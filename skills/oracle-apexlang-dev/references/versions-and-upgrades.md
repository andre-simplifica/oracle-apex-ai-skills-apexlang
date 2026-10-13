# Version gates and upgrades

Minimum APEX: 26.2. Reviewed feature releases: 26.2 only. Patch versions of that release are accepted but still need current known-issue review. A future feature release returns `REVIEW_REQUIRED`; changing a numeric minimum alone does not qualify it.

APEX 26.2 prerequisites include ORDS 26.3+, SQLcl 26.3+ for APEXlang workflows, and supported Database 19c RU 19.18+ or Oracle AI Database 26ai (23.26.0+). Verify the actual service; do not infer database capabilities from branding. Deep Data Security has additional database prerequisites. [Oracle release requirements](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/about-release-notes.html).

## Evidence

```text
sql -version
sql /nolog -e 'help apex'
```

Use the approved launcher from PATH or the private project profile; do not bypass its wrapper to call an installation binary directly.

In the confirmed saved connection:

```sql
select user, sys_context('USERENV','SERVICE_NAME') as service_name from dual;
select version_no from apex_release;
```

Inspect public metadata to confirm workspace/application/parsing schema. Obtain database full release/RU and ORDS version from authorized administration/host evidence; if inaccessible, record the missing prerequisite, not an assumed version. App Compatibility Mode and `mmdVersion` are separate from live engine version.

```bash
python3 Util/apexlang/validate_oracle_apex_compatibility.py \
  --apex-version 26.2 --sqlcl-version 26.3 --ords-version 26.3 --require apexlang
```

The helper validates supplied facts offline. Doctor without versions verifies installed files only; it never connects or proves runtime readiness.

## First adoption versus source upgrade

### Application Compatibility Mode

Treat engine version, source `mmdVersion` and application Compatibility Mode as separate facts. For adoption, recommend the newest mode supported by the verified engine after reviewing cumulative changed behavior. If the user authorizes the application compatibility upgrade, prepare recovery, apply it through a supported route, and test the affected runtime flows. Retaining an older mode must be an explicit decision with a reason, not an automatic consequence of starting from an export.

The pinned APEX 26.2 inventory defines the newest `runtime.compatibilityMode` value as `26.1`, displayed as **26.1 to 26.2**. Do not set an invented `26.2` token or copy the engine version into this property. Verify the release-matched inventory and Builder options when upgrading to another reviewed release.

This setting affects the whole application. A page-only import does not apply an `application.apx` change. Follow the programmatic-first [internal API contract](apex-internal-apis.md), including its verified compatibility setter example, before requesting App Builder's Application Definition. Do not silently broaden a page-only import into a full import or treat a historical API's existence as current support. Preserve the application's exact target and current-state guards. If no safe route can be established, report the concrete blocker before requesting Builder access.

Preserve the previous mode and source for reversal; re-export to prove the exact change and run fresh login, navigation, affected components and authorization canaries. Report untested paths separately: setting the mode or passing the compiler is not a guarantee of runtime compatibility.

See [Oracle's application upgrade guide](https://docs.oracle.com/en/database/oracle/apex/26.2/htmdb/upgrading-apex-applications.html) and the pinned `apexlang-inventory/assets/app/app.md` property definition. Theme refresh, authentication changes and database-object changes remain separately scoped.

### Source workflow

If the live application was just upgraded and no canonical APEXlang exists, export it directly and perform [readiness](../../oracle-apexlang-export/references/readiness-and-first-baseline.md). Do not import an old SQL snapshot over its current state.

If Git is already authoritative, prepare a dedicated upgrade branch. Back up both live and uncommitted source; reconcile Builder drift. In an authorized isolated DEV target, import the approved old source with the version's supported upgrade path, re-export under the new engine, validate the complete new structure and test behavior. Keep the structural upgrade in its own commit/PR and rebase downstream work. [Oracle source-upgrade process](https://docs.oracle.com/en/database/oracle/apex/26.2/apxdc/upgrading-apexlang-source-with-new-apex-release.html).

Oracle documents `-force` for replacing the exporter-owned alias directory; it deletes that directory. Prefer exporting into a new empty candidate then replacing the reviewed application tree, including removed files. Never run `-force` in a mixed source directory. Keep project docs, hand-written SQL and reports outside exporter-owned trees.

## Qualifying the next release

1. Read new/changed/deprecated/desupported features, fixed/known bugs, API changes, all relevant announcement links, and tool prerequisites. Record URLs/review date.
2. Inspect the matching Oracle inventory, grammar, examples and license. Pin a full commit and verify hashes; do not choose an inventory based on marketing names.
3. Assess model metadata, file-layout and import/deployment changes, JS/CSS/API removals, security defaults and database prerequisites.
4. Add a release-specific reference and explicit gate, update schema/template/installer contracts and tests. Never mark an untested runtime as verified.
5. Validate official examples offline and perform an authorized real-app round trip in a consuming project. Record which evidence was actually obtained.
6. Release the kit. Update projects through the manifest-aware updater, preserving project profiles/patterns/pending migrations and the old kit's files.
