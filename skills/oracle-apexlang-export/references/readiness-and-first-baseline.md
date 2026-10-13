# Readiness and the first APEXlang baseline

Use when a live application was upgraded to 26.2 and has no versioned APEXlang source. The initial activity is read-only inspection/export. An import, theme refresh or repair needs authorization for the concrete target; existing authorization remains sufficient within its scope.

## 1. Identify and capture

Confirm repository/branch/dirty work and the application's main/Working Copy identity. Read existing project standards before adopting `.oracle-apexlang/`. Record evidence time, named connection, `USER`, service, workspace, app ID/alias, parsing schema, live APEX patch, SQLcl, ORDS and database release/RU. Use [version checks](../../oracle-apexlang-dev/references/versions-and-upgrades.md). Do not derive live version from Compatibility Mode or an old export.

Use the same documented export options for baseline and drift captures, including `-skipExportDate` to reduce volatile export metadata. Record the current Git base, application/page inventory, theme and subscription state, Compatibility Mode, authentication/authorization, translations, integrations, plugins, Supporting Objects and relevant business canaries. Use public metadata after inspecting its actual columns. Establish who may edit the app during capture. A multi-command export is not automatically one transactionally consistent snapshot: freeze/coordinate edits or compare captures and retry on drift.

Export into separate new directories (replace placeholders after target confirmation, not literally):

```text
sql -name <confirmed-connection>
SQL> apex export -applicationid <app-id> -exptype APEXLANG -dir <fresh-apexlang-parent> -expSupportingObjects N -skipExportDate
SQL> apex export -applicationid <app-id> -exptype APPLICATION_SOURCE -dir <fresh-sql-recovery-parent> -expSupportingObjects N -skipExportDate
SQL> exit
```

These examples explicitly omit Supporting Objects. Decide the application-specific policy before running: including source differs from executing it, and `I` can enable automatic installation. Use local `help apex export`; do not copy switches from an older tool. App Builder 26.2 includes existing Supporting Objects; use SQLcl or `APEX_EXPORT.GET_APPLICATION` for explicit exclusion. Include translation repository data when applicable; SQLcl exposes `-expTranslations`. Preserve `generated-artifacts/translations.sql` unchanged. See [export API](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/GET_APPLICATION_Function.html) and [changed behavior](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/changed-behavior.html).

Retain the complete original recovery privately, including any necessary sensitive configuration. Public Git source must exclude secrets, salts, customer/runtime data and private deployment identities. Review binary static files as well as text. Record required externally provisioned credentials, ACL users, subscriptions, remote servers and data; application source is not a database/data backup. Preserve the export-generated app alias directory; do not assume it is `f<id>`.

## 2. Inspect and diagnose without changing the app

```bash
python3 Util/apexlang/apexlang_tools.py inspect --root <app-directory> --apex-version 26.2
python3 Util/apexlang/apexlang_tools.py validate --root <app-directory> --apex-version 26.2
```

The second command verifies local SQLcl >=26.3 and uses `/nolog`. It requires a positive compiler success marker, not merely exit code zero. Read its private diagnostic log. Match all exported pages/assets to live inventory. The structural helper cannot prove export completeness without this reconciliation.

APEXlang validation can expose old metadata inconsistencies even when runtime works. Investigate each diagnostic by file, line and component; use Builder for context. Choose the smallest correction and preserve recoverability. Errors block import; warnings need classification but do not inherently block it. Repair in Builder and re-export, or in source and revalidate within the authorized scope. Never remove unfamiliar metadata automatically. [Oracle diagnostic guidance](https://docs.oracle.com/en/database/oracle/apex/26.2/htmdb/creating-an-application-with-APEXlang.html).

Run CODESCAN on the candidate. Separate existing findings from introduced findings; review security issues according to actual server-side controls. A successful compiler and a large warning count can coexist. Do not blanket-ignore warnings or claim a clean security audit.

## 3. Classify remediation

| Finding | Treatment |
| --- | --- |
| Unknown/wrong target; APEX below 26.2; unreviewed future release | Stop connected APEXlang work and resolve evidence/version gate |
| Missing files, model mismatch, compiler errors, unresolved drift | Block candidate promotion/import until understood |
| Legacy Calendar; missing/invalid plugin, template or subscription references | Inspect replacement/refresh options, prepare a targeted repair |
| Old Universal Theme subscription/custom template deltas | Assess refresh in isolated DEV, compare appearance and interactions |
| Old Compatibility Mode or Upgrade Application suggestions | Review cumulative behavior changes; select and test changes separately |
| OAuth token/scope customization, AI provider migration, custom JS/DOM references | Run focused integration/security/browser regression tests |
| Warning, optional new styling, new provider capability | Record severity/decision; no automatic feature adoption |

A theme refresh is recommended maintenance, not proof of readiness nor a universal prerequisite to export. Oracle supports UT 26.2/26.1 in this release. Do not replace a custom theme or force Iris. Review Upgrade Application suggestions individually and keep theme/style/Compatibility Mode changes separate from the first export. [Application upgrade guide](https://docs.oracle.com/en/database/oracle/apex/26.2/htmdb/upgrading-apex-applications.html), [prerequisites](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/about-release-notes.html).

## 4. Establish source and prove the development loop

Preserve the original baseline before remediation. Promote the complete reviewed tree into the canonical application directory; include `.apex/` hidden metadata, deployment JSON, translations and static assets. Record source hash, version, recovery location and readiness report outside that directory. Commit the first baseline separately from behavioral changes; publish according to the consuming repository's rules.

When a DEV test is authorized, create/use a Working Copy or isolated app, import with reviewed deployment overrides, exercise login, a representative read/write flow, negative authorization and relevant integrations. Then make a small reversible source change, validate, import eligible files, verify runtime and re-export to prove reconciliation. Working Copies share database objects and do not copy Supporting Objects.

For every round trip, compare baseline/local/fresh-live, capture recovery, inspect import errors, and reconcile normalized source. Do not repeatedly import to discover a command's behavior. If no DEV target/import is authorized, finish the read-only baseline and report runtime validation pending.

## Readiness record

Use the project-owned `.oracle-apexlang/readiness.md` initialized from `templates/readiness-report.md`: target/time/version evidence; original source/recovery identity; inventory; diagnostics with severity/owner; theme/Compatibility Mode decisions; authorized mutations; tests; final status.

- `EXPORTED_NOT_VALIDATED`: capture exists; compiler/inventory checks incomplete or failed.
- `BASELINE_VALIDATED`: inventory reconciled and full-tree compiler passed; runtime/import loop may remain untested.
- `READY_FOR_DEVELOPMENT`: baseline plus authorized round trip and agreed runtime/security canaries passed, with remaining accepted warnings listed.

None of these means production deployment. Report Git publication and any deployed environment separately.
