from __future__ import annotations
import argparse
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
from apexlang_tools import SourceError, inspect, import_plan, validate, sqlcl_version
from oracle_reference import verify_vendor

ORACLE_ROOT = ROOT / 'vendor/oracle-skills'
EXAMPLES = ORACLE_ROOT / 'apex/apexlang/26.2/apexlang-example-applications/assets'


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


class OracleReferenceTests(unittest.TestCase):
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
            result=validate(EXAMPLES/name,'26.2',os.environ['SQLCL_BIN'])
            self.assertTrue(result['compiler_validated'],result['diagnostic_log'])
            Path(result['diagnostic_log']).unlink()
        with tempfile.TemporaryDirectory() as directory:
            candidate=Path(directory)/'invalid';shutil.copytree(EXAMPLES/'example-1',candidate)
            (candidate/'application.apx').write_text('this is deliberately invalid apexlang\n')
            result=validate(candidate,'26.2',os.environ['SQLCL_BIN'])
            self.assertFalse(result['compiler_validated'],result['diagnostic_log'])
            Path(result['diagnostic_log']).unlink()


if __name__=='__main__':unittest.main()
