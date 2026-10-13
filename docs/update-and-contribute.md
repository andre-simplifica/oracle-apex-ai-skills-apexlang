# Update and contribute

A kit update, SQLcl update and APEX engine/source upgrade are different operations.

Fetch a clean candidate kit at an explicit tag/commit, validate it, then run `manage_project_installation.py check` and `update --dry-run` against the consuming repository. Apply only after reviewing the plan. The updater verifies old hashes and refuses conflicts; it preserves project-owned profiles, patterns, readiness, export policy and pending migrations. Existing templates need a reviewed manual merge. `--initialize-missing-project-files` creates only absent scaffolding.

See [installer contract](../skills/oracle-apex-ai-skills-apexlang/references/installation-and-updates.md), [APEX/source upgrades](../skills/oracle-apexlang-dev/references/versions-and-upgrades.md) and [SQLcl updates](../skills/oracle-apexlang-dev/references/sqlcl-26.3.md).

For the next APEX release, review the complete release-note changes and relevant APIs, vendor its matching Oracle inventory under a new pinned commit, add release-specific migration guidance and tests, and validate examples plus an authorized real application. Keep `runtime_verified_releases` honest; offline tests do not populate it.

Contributions belong in this reusable core only if they apply across applications. Preserve upstream Oracle bytes/license and put policy adaptations in local references. Run `bash scripts/validate_repo.sh`; see [contributing](../CONTRIBUTING.md).
