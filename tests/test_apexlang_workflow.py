from __future__ import annotations
import argparse
import copy
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from apexlang_tools import (SourceError, inspect, import_plan, validate, sqlcl_version,
                            parse_compiler_diagnostics, verify_plan, digest_record, utc_now)
from oracle_reference import verify_vendor, verify_catalog, search_references, read_reference

ORACLE_ROOT = ROOT / 'vendor/oracle-skills'
EXAMPLES = ORACLE_ROOT / 'apex/apexlang/26.2/apexlang-example-applications/assets'
CATALOG = ROOT / 'skills/oracle-apexlang-dev/references/example-catalog.json'

# SQLcl 26.3.1 output captured from a deliberately invalid copy of Oracle example-1.
COMPILER_ERRORS = '''APEXlang Compile Errors:
File: pages/p00004-customer.apx
Line: 6
Column: 8
Type: LOV_NOT_FOUND
Error: Invalid LOV required parameter: appearance - pageMode (string)
Valid parameters are: modalDialog
-nonModalDialog
-normal

File: pages/p00004-customer.apx
Line: 7
Column: 8
Type: INVALID_PROPERTY
Error: Invalid property: dialogTemplate
'''


class ApexlangWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ('baseline', 'candidate', 'live'):
            app = self.root / name
            (app / '.apex').mkdir(parents=True)
            (app / 'deployments').mkdir()
            (app / 'pages').mkdir()
            (app / 'shared-components/lovs').mkdir(parents=True)
            (app / 'application.apx').write_text('app DEMO {\n}\n')
            (app / '.apex/apexlang.json').write_text(json.dumps({'mmdVersion':'26.2.0+3479'}))
            (app / 'deployments/default.json').write_text(json.dumps({'app':{'id':100}}))
            (app / 'pages/p00001-home.apx').write_text('page 1 {\n}\n')
            (app / 'shared-components/lovs/status.apx').write_text('lov status {\n}\n')
        self.candidate = self.root / 'candidate'
        self.args = argparse.Namespace(root=self.candidate, apex_version='26.2',
                sqlcl_version='26.3.0.260.1620', ords_version='26.3',
                baseline=self.root/'baseline', live=self.root/'live',
                environment='development', app_id=100, workspace='DEMO', schema='DEMO',
                deployment=None, allow_app_id_remap=False, files=['pages/p00001-home.apx'])

    def tearDown(self):
        self.temp.cleanup()

    def fake_sqlcl(self, output, version='26.3.0.260.1620', status=0):
        path=self.root/'sqlcl-fixture'
        # The fake client records invocation to prove /nolog and entire-tree input.
        path.write_text('#!'+sys.executable+'\nimport pathlib,sys\n'
            'if "-version" in sys.argv:\n'
            f' print("SQLcl: Release {version}")\n'
            'else:\n'
            f' pathlib.Path({str(self.root / "invocation")!r}).write_text(repr(sys.argv)+"\\n"+sys.stdin.read())\n'
            f' print({output!r})\n'
            f' sys.exit({status})\n')
        path.chmod(0o700)
        return str(path)

    def test_structure_does_not_claim_compiler_or_runtime(self):
        result=inspect(self.candidate,'26.2')
        self.assertFalse(result['compiler_validated'])
        self.assertFalse(result['runtime_verified'])
        self.assertEqual(result['source_mmd_version'],'26.2.0+3479')
        self.assertIn('.apex/apexlang.json',result['files'])

    def test_missing_model_and_unreviewed_release_are_blocked(self):
        for version in ('24.2','26.1','26.3','unknown'):
            with self.subTest(version=version), self.assertRaises(ValueError):
                inspect(self.candidate,version)
        (self.candidate/'.apex/apexlang.json').unlink()
        with self.assertRaises(SourceError): inspect(self.candidate,'26.2')

    def test_source_model_future_release_is_blocked(self):
        (self.candidate/'.apex/apexlang.json').write_text('{"mmdVersion":"26.3.0+1"}')
        with self.assertRaises(SourceError): inspect(self.candidate,'26.2')

    def test_symlinks_and_repository_root_are_rejected(self):
        target=self.candidate/'link';target.symlink_to(self.root/'live',target_is_directory=True)
        with self.assertRaises(SourceError): inspect(self.candidate,'26.2')
        target.unlink();(self.candidate/'.git').mkdir()
        (self.candidate/'.git/HEAD').write_text('ref: refs/heads/main')
        with self.assertRaises(SourceError): inspect(self.candidate,'26.2')

    def test_validate_requires_positive_success_and_no_error(self):
        for output in ('', 'Validation failed', 'Validation successful\nORA-00001: failed'):
            with self.subTest(output=output):
                result=validate(self.candidate,'26.2',self.fake_sqlcl(output))
                self.assertFalse(result['compiler_validated'])
                Path(result['diagnostic_log']).unlink()
        result=validate(self.candidate,'26.2',self.fake_sqlcl('Validation successful.'))
        self.assertTrue(result['compiler_validated'])
        self.assertFalse(result['runtime_verified'])
        self.assertEqual(result['sqlcl_version'],'26.3.0.260.1620')
        invocation=(self.root/'invocation').read_text()
        self.assertIn('/nolog',invocation)
        self.assertNotIn('-name',invocation)
        self.assertIn(str(self.candidate.resolve()),invocation)
        self.assertEqual(os.stat(result['diagnostic_log']).st_mode & 0o777,0o600)
        Path(result['diagnostic_log']).unlink()

    def test_validate_rejects_old_sqlcl_even_if_it_would_report_success(self):
        with self.assertRaises(ValueError):
            validate(self.candidate,'26.2',self.fake_sqlcl('Validation successful','26.2.2'))
        self.assertFalse((self.root/'invocation').exists())

    def test_actual_sqlcl_output_prefers_full_build_identity(self):
        binary=self.fake_sqlcl('Validation successful',
                               version='26.3.0.0 Production Build: 26.3.0.260.1620')
        self.assertEqual(sqlcl_version(binary),'26.3.0.260.1620')

    def test_nonzero_compiler_exit_is_failure(self):
        result=validate(self.candidate,'26.2',self.fake_sqlcl('Validation successful',status=1))
        self.assertFalse(result['compiler_validated'])
        Path(result['diagnostic_log']).unlink()

    def test_local_source_edit_produces_plan_only(self):
        (self.candidate/'pages/p00001-home.apx').write_text('page 1 {\n  title: New\n}\n')
        result=import_plan(self.args)
        self.assertEqual(result['status'],'PLAN_ONLY')
        self.assertFalse(result['executes_database_changes'])
        self.assertFalse(result['compiler_validated'])
        self.assertFalse(result['runtime_verified'])
        self.assertIn('-files "'+str((self.candidate/'pages/p00001-home.apx').resolve())+'"',result['command'])
        self.assertNotEqual(result['source_sha256'],result['live_sha256'])

    def test_live_drift_in_unselected_dependency_blocks_plan(self):
        (self.root/'live/shared-components/lovs/status.apx').write_text('changed by Builder')
        with self.assertRaisesRegex(SourceError,'Live changes'):
            import_plan(self.args)

    def test_production_requires_complete_import(self):
        self.args.environment='production'
        with self.assertRaises(SourceError): import_plan(self.args)
        self.args.files=None
        result=import_plan(self.args)
        self.assertEqual(result['mode'],'complete-application')
        self.assertNotIn(' -files ',result['command'])

    def test_selected_paths_cannot_escape_or_use_unsupported_components(self):
        for value in ('../outside.apx','/tmp/page.apx','pages/*.apx','application.apx',
                      'shared-components/themes/theme.apx','shared-components/plugins/plugin.apx',
                      'workspace/credentials.apx','pages/deleted.apx'):
            with self.subTest(value=value), self.assertRaises(SourceError):
                self.args.files=[value];import_plan(self.args)

    def test_command_arguments_reject_injection(self):
        for value in ('NAME\nexit','NAME"','NAME;host','NAME$(id)','NAME`id`','NAME\\path'):
            with self.subTest(value=value), self.assertRaises(SourceError):
                self.args.workspace=value;import_plan(self.args)

    def test_target_mapping_requires_deliberate_remap(self):
        self.args.app_id=101
        with self.assertRaisesRegex(SourceError,'app ID differs'): import_plan(self.args)
        self.args.allow_app_id_remap=True
        self.assertIn('-id 101',import_plan(self.args)['command'])

    def test_wrong_workspace_or_schema_is_blocked(self):
        deployment=self.root/'deployment.json';self.args.deployment=deployment
        for data in ({'workspace':{'name':'OTHER'}},{'app':{'databaseSession':{'parsingSchema':'OTHER'}}}):
            deployment.write_text(json.dumps(data))
            with self.assertRaises(SourceError):import_plan(self.args)

    def test_client_and_ords_minimums_are_enforced(self):
        self.args.sqlcl_version='26.2'
        with self.assertRaises(ValueError): import_plan(self.args)
        self.args.sqlcl_version='26.3';self.args.ords_version='26.2'
        with self.assertRaises(ValueError): import_plan(self.args)

    def test_compiler_diagnostics_preserve_location_property_and_allowed_values(self):
        result = validate(self.candidate, '26.2', self.fake_sqlcl(COMPILER_ERRORS))
        self.addCleanup(Path(result['diagnostic_log']).unlink)
        self.assertFalse(result['compiler_validated'])
        self.assertEqual(result['diagnostic_count'], 2)
        first, second = result['diagnostics']
        self.assertEqual((first['file'], first['line'], first['column']),
                         ('pages/p00004-customer.apx', 6, 8))
        self.assertEqual(first['valid_values'], ['modalDialog', 'nonModalDialog', 'normal'])
        self.assertEqual(first['property'], 'pageMode')
        self.assertEqual(first['reference_search'],
                         {'query': 'pageMode', 'kind': 'definition', 'apex_release': '26.2'})
        self.assertEqual(second['type'], 'INVALID_PROPERTY')

    def test_diagnostics_handle_adjacent_blocks_ansi_and_unknown_messages(self):
        output = COMPILER_ERRORS.replace('\n\nFile:', '\nFile:').replace('-normal', '- normal')
        output = '\x1b[31m' + output + '\x1b[0m'
        self.assertEqual(len(parse_compiler_diagnostics(output)), 2)
        output = output.replace('Invalid property: dialogTemplate', 'Unknown value: private-source-literal')
        output = output.replace('pages/p00004-customer.apx', '../outside.apx')
        result = parse_compiler_diagnostics(output)
        self.assertNotIn('private-source-literal', json.dumps(result))
        self.assertTrue(all(item['file'] is None for item in result))
        self.assertEqual(result[0]['valid_values'][-1], 'normal')

    def test_compiler_error_header_overrides_success_even_without_parseable_blocks(self):
        result = validate(self.candidate, '26.2', self.fake_sqlcl('Validation successful\nAPEXlang Compile Errors:\nunknown format'))
        self.addCleanup(Path(result['diagnostic_log']).unlink)
        self.assertFalse(result['compiler_validated'])

    def prepare_verified_plan(self):
        self.args.sqlcl = self.fake_sqlcl('Validation successful')
        report = validate(self.candidate, '26.2', self.args.sqlcl)
        self.addCleanup(Path(report['diagnostic_log']).unlink)
        self.args.validation = self.root / 'validation.json'
        self.args.validation.write_text(json.dumps(report))
        self.args.plan = self.root / 'plan.json'
        plan = import_plan(self.args)
        self.args.plan.write_text(json.dumps(plan))
        return plan, report

    def test_verified_plan_binds_complete_sources_and_allows_fresh_export_directory(self):
        self.prepare_verified_plan()
        fresh = self.root / 'fresh'
        shutil.copytree(self.args.live, fresh)
        self.args.live = fresh
        result = verify_plan(self.args)
        self.assertEqual(result['status'], 'PLAN_VERIFIED_OFFLINE')
        self.assertTrue(result['compiler_validated'])
        for key in ('executes_database_changes', 'live_identity_verified', 'authorization_checked', 'runtime_verified'):
            self.assertFalse(result[key])

    def test_plan_rejects_candidate_and_external_deployment_changes(self):
        self.args.deployment = self.root / 'target.json'
        self.args.deployment.write_text('{"app":{"id":100}}')
        self.prepare_verified_plan()
        for path in (self.candidate / 'shared-components/lovs/status.apx', self.args.deployment):
            with self.subTest(path=path):
                original = path.read_text()
                path.write_text(original + '\n')
                with self.assertRaisesRegex(SourceError, 'no longer matches'):
                    verify_plan(self.args)
                path.write_text(original)

    def test_plan_rejects_drift_even_when_outside_selected_page(self):
        self.prepare_verified_plan()
        (self.args.live / 'shared-components/lovs/status.apx').write_text('Builder change')
        with self.assertRaisesRegex(SourceError, 'Live changes'):
            verify_plan(self.args)

    def test_plan_rejects_changed_target_scope_and_toolchain(self):
        self.prepare_verified_plan()
        for field, value in (('workspace', 'OTHER'), ('schema', 'OTHER'), ('environment', 'test'),
                             ('files', ['shared-components/lovs/status.apx']), ('ords_version', '26.4'),
                             ('sqlcl_version', '26.3.1.301.1413')):
            with self.subTest(field=field):
                original = getattr(self.args, field)
                setattr(self.args, field, value)
                with self.assertRaises(SourceError):
                    verify_plan(self.args)
                setattr(self.args, field, original)

    def test_plan_probes_actual_sqlcl_build(self):
        self.prepare_verified_plan()
        self.args.sqlcl = self.fake_sqlcl('Validation successful', version='26.3.1.301.1413')
        with self.assertRaisesRegex(SourceError, 'Current SQLcl build'):
            verify_plan(self.args)

    def test_plan_expiry_future_creation_and_tampering_are_rejected(self):
        plan, _ = self.prepare_verified_plan()
        created = dt.datetime.fromisoformat(plan['created_at'])
        for now in (created - dt.timedelta(seconds=1), created + dt.timedelta(minutes=30)):
            with self.subTest(now=now), self.assertRaisesRegex(SourceError, 'validity window'):
                verify_plan(self.args, now)
        plan['command'] += ' unexpected'
        self.args.plan.write_text(json.dumps(plan))
        with self.assertRaisesRegex(SourceError, 'integrity'):
            verify_plan(self.args)

    def test_compiler_evidence_cannot_be_failed_stale_or_inconsistent(self):
        _, original = self.prepare_verified_plan()
        variants = [
            {'compiler_validated': False}, {'diagnostic_count': 1}, {'tree_sha256': '0' * 64},
            {'deployment_sha256': '0' * 64}, {'sqlcl_version': '26.3.1.301.1413'},
            {'target_apex_version': '26.3.0'}, {'source_root': str(self.args.live)},
            {'completed_at': (utc_now() + dt.timedelta(days=1)).isoformat()},
            {'started_at': (utc_now() + dt.timedelta(days=1)).isoformat()},
        ]
        for changes in variants:
            with self.subTest(changes=changes):
                evidence = {**original, **changes}
                evidence['report_sha256'] = digest_record(evidence, 'report_sha256')
                self.args.validation.write_text(json.dumps(evidence))
                with self.assertRaises(SourceError):
                    verify_plan(self.args)
        original['diagnostic_count'] = 1
        self.args.validation.write_text(json.dumps(original))
        with self.assertRaises(SourceError):
            verify_plan(self.args)

    def test_cli_writes_private_reports_and_refuses_overwrite_or_source_tree_output(self):
        binary = self.fake_sqlcl('Validation successful')
        command = [sys.executable, str(ROOT / 'scripts/apexlang_tools.py'), 'validate',
                   '--root', str(self.candidate), '--apex-version', '26.2', '--sqlcl', binary]
        output = self.root / 'report.json'
        result = subprocess.run([*command, '--output', str(output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(output.read_text())
        self.addCleanup(Path(report['diagnostic_log']).unlink)
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)
        original = output.read_bytes()
        for path in (output, self.candidate / 'report.json'):
            result = subprocess.run([*command, '--output', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(output.read_bytes(), original)
        self.assertFalse((self.candidate / 'report.json').exists())


class OracleReferenceTests(unittest.TestCase):
    def test_search_ranks_portuguese_examples_and_camel_case_properties(self):
        for query, expected in (('relatório formulário modal', 'report-modal-form'),
                                ('calendário', 'calendar'), ('filtro atualização', 'filter-refresh')):
            with self.subTest(query=query):
                result = search_references(ORACLE_ROOT, CATALOG, query, kind='example')
                self.assertEqual(result['matches'][0]['id'], 'example:26.2:' + expected)
                self.assertTrue(result['matches'][0]['compiler_validated'])
                self.assertFalse(result['matches'][0]['runtime_verified'])
        result = search_references(ORACLE_ROOT, CATALOG, 'pageItemsToSubmit', kind='definition')
        self.assertGreater(result['total_matches'], 0)
        self.assertTrue(all(hit['id'].startswith('oracle:26.2:') for hit in result['matches']))

    def test_search_and_read_are_bounded_and_reproducible(self):
        first = search_references(ORACLE_ROOT, CATALOG, 'region', limit=2)
        second = search_references(ORACLE_ROOT, CATALOG, 'region', limit=2, offset=first['next_offset'])
        self.assertEqual(len(first['matches']), 2)
        self.assertFalse({hit['id'] for hit in first['matches']} & {hit['id'] for hit in second['matches']})
        item = read_reference(ORACLE_ROOT, CATALOG, 'example:26.2:report-modal-form', max_chars=100)
        self.assertEqual(len(item['content']), 100)
        self.assertTrue(item['dependencies'])
        self.assertTrue(item['adaptation'])
        next_page = read_reference(ORACLE_ROOT, CATALOG, item['id'], offset=item['next_offset'], max_chars=100)
        source = Path(item['path']).read_text()
        self.assertEqual(item['content'] + next_page['content'], source[:200])
        form = read_reference(ORACLE_ROOT, CATALOG, item['id'], selected_file='pages/p00004-customer.apx')
        self.assertIn('pageMode: modalDialog', form['content'])
        with self.assertRaises(ValueError):
            read_reference(ORACLE_ROOT, CATALOG, item['id'], selected_file='../application.apx')

    def test_catalog_search_and_read_reject_other_releases_and_bad_bounds(self):
        for release in ('24.2', '26.1', '26.3', 'unknown'):
            with self.subTest(release=release):
                with self.assertRaises(ValueError):
                    search_references(ORACLE_ROOT, CATALOG, 'calendar', release)
                with self.assertRaises(ValueError):
                    read_reference(ORACLE_ROOT, CATALOG, 'example:26.2:calendar', release)
        for query, limit, offset in (('', 5, 0), ('with the', 5, 0), ('x' * 501, 5, 0), ('region', 21, 0), ('region', 5, -1)):
            with self.subTest(query=query[:20], limit=limit, offset=offset), self.assertRaises(ValueError):
                search_references(ORACLE_ROOT, CATALOG, query, limit=limit, offset=offset)

    def test_catalog_requires_bound_complete_application_compiler_evidence(self):
        self.assertEqual(verify_catalog(ORACLE_ROOT, CATALOG)['examples'], 5)
        with tempfile.TemporaryDirectory() as directory:
            catalog = Path(directory) / CATALOG.name
            evidence_path = catalog.with_name('example-validation.json')
            shutil.copy2(CATALOG, catalog)
            original = json.loads(CATALOG.with_name('example-validation.json').read_text())
            with self.assertRaises(ValueError):
                verify_catalog(ORACLE_ROOT, catalog)
            for field, value in (('source_tree_sha256', '0' * 64), ('source_mmd_version', '26.1.0'),
                                 ('scope', 'selected-files'), ('compiler_validated', False), ('runtime_verified', True)):
                with self.subTest(field=field):
                    evidence = copy.deepcopy(original)
                    evidence['applications']['example-1'][field] = value
                    evidence['evidence_sha256'] = digest_record(evidence, 'evidence_sha256')
                    evidence_path.write_text(json.dumps(evidence))
                    with self.assertRaises(ValueError):
                        verify_catalog(ORACLE_ROOT, catalog)

    def test_vendor_integrity_and_official_example_structures(self):
        result=verify_vendor(ORACLE_ROOT)
        self.assertGreater(result['files'],600)
        for name in ('example-1','example-2'):
            report=inspect(EXAMPLES/name,'26.2')
            self.assertGreater(len(report['pages']),0)
            self.assertFalse(report['runtime_verified'])

    def test_vendor_tampering_extra_files_and_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            vendor=Path(directory)/'oracle';shutil.copytree(ORACLE_ROOT,vendor)
            license=vendor/'LICENSE';original=license.read_bytes();license.write_bytes(b'changed')
            with self.assertRaises(ValueError):verify_vendor(vendor)
            license.write_bytes(original);extra=vendor/'unreviewed.txt';extra.write_text('new')
            with self.assertRaises(ValueError):verify_vendor(vendor)
            extra.unlink();extra.symlink_to(license)
            with self.assertRaises(ValueError):verify_vendor(vendor)


@unittest.skipUnless(os.environ.get('SQLCL_BIN'), 'Set SQLCL_BIN for offline Oracle compiler integration')
class NativeSQLclTests(unittest.TestCase):
    def test_official_examples_compile_and_invalid_candidate_fails(self):
        for name in ('example-1','example-2'):
            with tempfile.TemporaryDirectory() as directory:
                candidate = Path(directory) / name
                shutil.copytree(EXAMPLES/name, candidate)
                result=validate(candidate,'26.2',os.environ['SQLCL_BIN'])
            self.assertTrue(result['compiler_validated'],result['diagnostic_log'])
            Path(result['diagnostic_log']).unlink()
        with tempfile.TemporaryDirectory() as directory:
            candidate=Path(directory)/'invalid';shutil.copytree(EXAMPLES/'example-1',candidate)
            page = candidate/'pages/p00004-customer.apx'
            page.write_text(page.read_text().replace('pageMode: modalDialog', 'pageMode: invalidMode'))
            result=validate(candidate,'26.2',os.environ['SQLCL_BIN'])
            self.assertFalse(result['compiler_validated'],result['diagnostic_log'])
            self.assertEqual(result['diagnostics'][0]['property'], 'pageMode')
            self.assertIn('modalDialog', result['diagnostics'][0]['valid_values'])
            Path(result['diagnostic_log']).unlink()


if __name__=='__main__':unittest.main()
