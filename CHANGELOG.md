# Changelog

## Unreleased

- Added structured SQLcl compiler diagnostics and full-tree/deployment validation evidence.
- Added ranked, paginated Oracle 26.2 reference search with Portuguese aliases and five compiler-validated example patterns, preserving upstream files and licenses.
- Added offline import-plan verification with a 30-minute lifetime, source/configuration/scope checks, current SQLcl build verification and explicit live-identity/authorization limits.
- Included example catalog/evidence integrity checks in managed project installation. Search now defaults to five ranked matches; callers needing all results must paginate with `next_offset`.
- Fixed object-lock compilation by evaluating private byte-truncation helpers in PL/SQL before SQL DML.
- Accepted Oracle's UTC expression for the expiry timestamp index in audit and strict validation, preserving runtime API version 1.1.0.

## 0.1.0 - 2026-10-12

Initial separate APEXlang kit, derived from the MIT-licensed Oracle APEX AI Skills at `e105a7ca1271cb5a218ad363099537e0a4eb720e` without modifying that project.

- Minimum/reviewed APEX 26.2, SQLcl/ORDS 26.3 prerequisite and blocked unreviewed releases.
- Complete pinned Oracle 26.2 component inventory, grammar, examples, compile/deploy references and UPL provenance.
- Readiness and first versioned baseline workflow for freshly upgraded applications.
- Source editing, whole-tree validation, CODESCAN triage, drift-aware import plans, target configuration and recovery.
- 26.2 feature/API review, SQLcl update guidance and future-release qualification process.
- Independent skill/profile/tool names, manifest-managed installation/update and preserved project-owned files.
- Retained cooperative database locks, PL/SQL practices, pending migrations and scoped baseline/release tooling.

No live consuming application has been imported or certified by this initial release. See `docs/validation.md`.
