---
name: oracle-apexlang-dev
description: Implement and debug Oracle APEX 26.2 by editing APEXlang source with the matching Oracle inventory, SQLcl validation, public API fallbacks and runtime checks. Includes SQL, PL/SQL, REST and application pattern learning.
---

# Oracle APEXlang Development

Use APEXlang as the authoring path after a validated baseline exists. For a newly upgraded application without source, start with `oracle-apexlang-export` readiness.

## Before editing

Read the project profile and patterns. Confirm live APEX 26.2, SQLcl 26.3+, ORDS 26.3+, source `mmdVersion` and target identity. Do not guess a version.

Compare a fresh export with the baseline before editing/importing. Preserve local and App Builder changes. A selected-file import replaces that file's components; it does not merge concurrent edits inside the file.

Read the relevant [Oracle inventory](references/oracle-reference-policy.md), properties, containment, theme and a real sibling page. Acquire cooperative locks for shared database objects; Working Copies do not isolate tables/packages.

## Implement and prove

Follow [daily workflow](references/daily-workflow.md): local diff → whole-tree compiler validation → CODESCAN triage → fresh drift check → authorized import → functional/security canaries → re-export/reconcile.

Resolve authorized work through APEXlang first, documented public APIs next, and verified internal APIs under the [internal API contract](references/apex-internal-apis.md) before requesting App Builder access. Consult [public APIs](references/public-apis-26.2.md). Builder is the last resort when these routes cannot safely complete the operation; report the concrete capability, privilege or validation blocker. Never invent a component-deletion command, Working Copy merge API or internal metadata call.

Distinguish stable component Static IDs from HTML DOM IDs. Keep generated artifacts and compiler metadata intact. Triage warnings; fix validation errors without deleting components merely to make a check pass.

## Focused references

| Task | Read |
| --- | --- |
| Syntax, themes, examples | [Oracle references](references/oracle-reference-policy.md) |
| Versions and upgrades | [Versions](references/versions-and-upgrades.md) |
| SQLcl/CODESCAN/Projects/MCP | [SQLcl 26.3](references/sqlcl-26.3.md), [execution](references/sqlcl.md) |
| New features and migration risks | [26.2 changes](references/release-notes-26.2.md) |
| Operations outside the language | [Public APIs](references/public-apis-26.2.md) |
| App standards | [Pattern learning](references/apex-pattern-learning.md), [profile](references/project-profile.md) |
| SQL/PLSQL | [Standards](references/sql-plsql-standards.md) |
| REST, debugging, jobs | [REST](references/rest-integrations.md), [debugging](references/apex-debugging.md), [jobs](references/background-jobs.md) |
| Dynamic Content | [RETURN CLOB](references/dynamic-content-regions.md) |
| Security and destructive actions | [Permissions](references/security-and-permissions.md), [destructive operations](references/destructive-operations.md) |
| Builder fallback | [Page Designer](references/page-designer.md), [Object Browser](references/object-browser.md) |
| Runtime and user help | [Validation](references/runtime-validation.md), [help](references/help-and-ux.md) |

After authorized PL/SQL compilation check object status and `USER_ERRORS`. Compiler validation does not execute business SQL, PL/SQL, integrations or browser JavaScript; test the affected flow and server-side authorization.
