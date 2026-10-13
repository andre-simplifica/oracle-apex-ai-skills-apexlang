# APEX 26.2 release review

Reviewed 2026-10-12. This is an implementation index, not a copy of Oracle's manuals. See the [source catalog](https://github.com/andre-simplifica/oracle-apex-ai-skills-apexlang/blob/main/docs/research-sources.json) for reviewed pages and capture hashes. Refresh current known issues before a real adoption/deployment.

## Capability map

| Area | Decision for this kit |
| --- | --- |
| APEXlang | Deployment JSON, file-level import and source-upgrade workflow; see daily/deployment references |
| AI | Provider API selection, reasoning effort, OCI dedicated fields and authorized navigation; test provider/model compatibility |
| Reports | Local search phrases, natural-language computed columns and translated default report metadata; test saved reports/reset behavior |
| Workflow/tasks | Draft modeling, custom action outcomes, failure actions, diagram export and instance migration; runtime migration needs its own plan |
| Security | Deep Data Security, Resource Principal authentication and schema-level network ACL option; verify actual database/provider prerequisites |
| Charts/UI | Lazy loading, coalesced refresh, foreground timers, reduced motion, UT refinements and utility CSS; test visibility/custom styling |
| Administration | Mail-queue diagnostics, service-limit requests and new public APIs |
| Dependencies | Bundled JS upgrades require plugin/custom-JS regression checks |

The full feature inventory and exact library versions remain in [new features](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/new-features.html).

## Announcement details

The [file-import article](https://blogs.oracle.com/apex/introducing-file-level-import-with-apexlang-in-oracle-apex) informs the selected-file limitations and workflow. The [AI article](https://blogs.oracle.com/apex/working-with-generative-ai-provider-apis-and-reasoning-effort) explains Provider API/model compatibility: Responses/Interactions are new defaults for eligible providers; legacy settings remain available, and automatic migration depends on custom attributes/headers. Test existing integrations before requesting new reasoning levels. The [report article](https://blogs.oracle.com/apex/whats-new-in-interactive-reports-and-ai-interactive-reports) covers deterministic search phrases versus LLM requests and editable computed columns. Verify generated formulas and user permissions.

AI-generated navigation requires Show AI Assistant, an AI Agent and an application AI Request Handler. Define allowed destinations and parameter validation server-side; never treat a generated link as authorization.

## Upgrade behavior requiring inspection

[Changed behavior](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/changed-behavior.html) affects Supporting Objects export defaults, generated translation SQL, report resets/substitutions, raw JSON report queries, tab characters in Static IDs, REST enablement and stricter OAuth token-scope matching. Prefer declarative OAuth over custom token reuse. Compatibility Mode changes are cumulative; do not set a mode only to match the engine's release number.

For an application upgraded from 24.2, also review [26.1 behavior](https://docs.oracle.com/en/database/oracle/apex/26.1/htmrn/changed-behavior.html): external component Static IDs and HTML DOM IDs serve different roles; outdated internal metadata/JavaScript assumptions need targeted remediation. Existing legacy Calendars cannot simply be carried into the APEXlang authoring path. Inspect their replacement before baseline acceptance.

## Deprecations and removals

[Current deprecations](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/deprecated-features.html): Advisor, Data Generator and the legacy Oracle Application Server SSO authentication scheme. Use SQLcl CODESCAN for static code checks; it does not replace runtime tests. [Earlier deprecations](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/deprecated-previous-releases.html) remain an adoption checklist for old calendars, legacy APIs/components and old attribute access.

[Current removals](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/desupported-features.html): the Export Repository, Query Builder and APEX REST Workshop. Existing ORDS services/data remain; use supported ORDS/SQL Developer tools. Also review [prior removals](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/desupported-previous-releases.html). Do not reinstall removed tooling or assume compatibility mode restores it.

## Remaining release-note sections

- [Requirements/about](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/about-release-notes.html): database/toolchain and supported-theme evidence.
- [Fixed bugs](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/fixed-bugs.html): match affected components; a listed fix does not prove your patch/runtime.
- [Open bugs](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/open-bugs-known-issues.html): check affected translation, browser, REST/export and bot-protection paths; some features require a later ORDS capability.
- [Ideas](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/ideas-app.html): discovery only; do not infer undocumented API/JSON keys. The What's New Ideas link pointed at 26.1 during review; use this version-specific chapter.
- [Privacy](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/privacy-notice.html): inspect telemetry/runtime-data handling relevant to deployment; no customer data belongs in public examples.
- [Preface](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/preface.html) and [index](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/index.html): documentation scope and navigation.

The linked rolling known-issues page returned no extractable content during capture. Do not interpret that as no issues; check it interactively before a live rollout. Instance patches, database settings, theme refresh and feature enablement remain separate authorized operations.
