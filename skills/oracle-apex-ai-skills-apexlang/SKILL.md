---
name: oracle-apex-ai-skills-apexlang
description: Adopt and develop Oracle APEX 26.2 applications with versioned APEXlang source, readiness checks, pinned Oracle references, project standards, and controlled SQLcl workflows. Use for this separate APEXlang kit, not the APEX 24.2 SQL-only kit.
---

# Oracle APEX AI Skills APEXlang

Start here for this four-skill kit. Minimum and currently reviewed APEX feature release: **26.2**. Require **SQLcl 26.3+** and **ORDS 26.3+**. Future APEX releases require a reviewed inventory and upgrade notes; do not silently reuse 26.2 grammar.

## Establish context

1. Inspect cwd, repository instructions, branch, dirty work and active work.
2. Read `.oracle-apexlang/project-profile.md`, `app-patterns.md`, `export-policy.json`, `installation-manifest.json`, `upstream-lock.json`, and `compatibility.json` when present. Carry forward useful `.oracle-apex-ai/` project standards explicitly; preserve the previous kit and its files.
3. Classify the request: inspect, prepare source, export/version a baseline, import into a named environment, or publish. Source edits and exports do not authorize imports or database changes. Prior explicit authorization remains valid for its scope.
4. Verify the saved connection, user/service, workspace, application, parsing schema, live APEX release, SQLcl, ORDS, database release/RU, and source `.apex/apexlang.json` `mmdVersion`. Repository evidence is not live evidence. Read [version gates](../oracle-apexlang-dev/references/versions-and-upgrades.md).
5. Load only the relevant skill and component references.

## Route

| Request | Route |
| --- | --- |
| Install/update/check this kit | [Installation](references/installation-and-updates.md) |
| Newly migrated application; first APEXlang baseline | `oracle-apexlang-export`, [readiness](../oracle-apexlang-export/references/readiness-and-first-baseline.md) |
| Edit `.apx`, add a page, fix a flow | `oracle-apexlang-dev`, [daily workflow](../oracle-apexlang-dev/references/daily-workflow.md) |
| SQL, PL/SQL, REST, security, debugging | `oracle-apexlang-dev` and its focused reference |
| Shared DEV database objects | `oracle-apexlang-object-lock` before compilation |
| Release, recovery SQL, schema source, pending migrations | `oracle-apexlang-export` |
| New APEX release or tool update | [Versions](../oracle-apexlang-dev/references/versions-and-upgrades.md), [SQLcl](../oracle-apexlang-dev/references/sqlcl-26.3.md) |
| Capability absent from APEXlang | [Public APIs and fallback](../oracle-apexlang-dev/references/public-apis-26.2.md) |

## Operating contract

- APEXlang is editable application source. Read the matching Oracle inventory and real application examples before generating syntax.
- Oracle references are pinned by commit and SHA-256. Read [reference policy](../oracle-apexlang-dev/references/oracle-reference-policy.md). Do not execute Oracle's deployment helper unchanged: it enables Supporting Objects and passes a connection string.
- Prefer Working Copies for application isolation. They still share schema objects. Git, application locks and cooperative database locks cover different resources.
- Selective file imports are for eligible development/test changes after drift comparison, full-tree validation, dependency review, recovery capture and scoped authorization. Production uses a complete tested application artifact.
- Exporting never implies theme refresh, Compatibility Mode changes, Upgrade Application actions, Supporting Objects execution or AI provider migration.
- During adoption, assess upgrading Compatibility Mode to the newest value supported by the verified engine. When explicitly authorized, carry out that upgrade with recovery and regression tests; do not preserve an older mode merely because the original task was an export. Follow [compatibility upgrades](../oracle-apexlang-dev/references/versions-and-upgrades.md#application-compatibility-mode).
- Keep confirmed application patterns in project-owned files. Optional reporting/ECharts companions remain independently installed; core operation does not require them.

## Closeout

Report source, version evidence, readiness stage, compiler/CODESCAN results, actual imports, runtime/authorization canaries, recovery and Git publication separately. `STRUCTURE_INSPECTED`, `COMPILER_VALIDATED`, `FILES_READY` and import success are not business-runtime proof.
