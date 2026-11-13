# Validation scope

`bash scripts/validate_repo.sh` runs offline behavioral tests for managed installation/update, preservation, compatibility gates, Oracle reference/catalog integrity, ranked search and bounded reads, structured diagnostics, source inspection, import-plan expiry and evidence binding, SQL recovery, pending migrations and release retention. It requires Python 3.10+, Bash, Git and ripgrep; install the pinned test dependencies with `python3 -m pip install -r requirements-dev.txt` in an isolated virtual environment. Installed CLI helpers use only the Python standard library. No database is required.

Set `SQLCL_BIN` to the approved SQLcl 26.3+ launcher to enable offline compiler integration tests on the pinned Oracle examples and a deliberately invalid application. CI does not download Oracle binaries or connect to Oracle. Syntax validation and CODESCAN results do not certify application runtime or security.

Live application adoption, Working Copy/import, theme refresh and business/security canaries remain to be performed in a specifically selected and authorized consuming project. The compatibility record therefore has no runtime-verified release entries.

## Development helper evidence — 2026-11-13

- Full local validation: **81 tests passed**, including the native SQLcl test, managed installation/update and rejection cases for changed sources, deployment configuration, scope, toolchain, drift and expired/inconsistent evidence.
- SQLcl build **26.3.1.301.1413** compiled both pinned Oracle example applications offline in temporary copies. A deliberately invalid `pageMode` produced structured location/property/allowed-value diagnostics and was rejected.
- Five catalog patterns are references into the complete example-1 context. Tracked compiler evidence binds that application's source hash and MMD to the pinned Oracle commit; runtime verification remains false.
- The changed development skill passed the skill-creator metadata validator. All **654** upstream files retain their pinned checksums and licenses.
- A temporary managed consumer successfully verified the catalog, searched in Portuguese and read example dependencies. Invalid example evidence prevented installation before any files were written.

This evidence covers local tooling and compiler behavior. No database connection, application import or business-runtime validation was performed.

## Initial release evidence — 2026-10-12

- Full local validation: **64 tests passed**, including schema/YAML contracts and native SQLcl integration.
- Approved local SQLcl launcher: build **26.3.0.260.1620**. Both pinned Oracle example applications compiled offline; a deliberately invalid application was rejected.
- All four skill entrypoints passed the skill-creator metadata validator.
- Oracle reference inventory: **654 files** verified against the pinned manifest (26.2 tree plus license).
- Independent skill forward-test followed the read-only adoption request without inventing a real application or authorizing an import. It identified build-reporting/provenance issues that were corrected and regression-tested.
- CODESCAN on Oracle example 1 analyzed **145 files** and reported **235 distinct warnings**. These are demonstration-source findings, not a clean security result or findings from a customer application.
- The original 24.2 kit's **93 tracked/untracked files** matched their initial hashes; its source was not changed.

GitHub CI runs the same offline suite without SQLcl; its native compiler test is explicitly skipped when `SQLCL_BIN` is absent. Actual run status is available in the repository's Actions tab. No live Oracle application, schema or runtime was changed by these tests.
