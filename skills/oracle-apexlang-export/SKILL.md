---
name: oracle-apexlang-export
description: Assess a migrated APEX 26.2 application, establish its first versioned APEXlang baseline, and prepare complete releases or SQL recovery exports with project-owned database migration and retention policies.
---

# Oracle APEXlang Baseline and Release

Use for a newly migrated application, explicit APEXlang export/versioning, or an official release. An application request does not imply a schema snapshot.

## Modes

- `temporary-inspection`: export into a disposable candidate for investigation/drift comparison.
- `adopt-apexlang`: evaluate the upgraded application and create its complete APEXlang baseline, with SQL recovery and outstanding remediation recorded.
- `application-snapshot`: version the complete application source.
- `initial-baseline`: explicitly requested complete application and schema structural DDL.
- `release`: complete application plus the requested full/partial five-file database bundle and pending DDL/DML.

Start with [readiness and first baseline](references/readiness-and-first-baseline.md). For a migrated legacy application, also follow the [configuration review and scope choice](../oracle-apexlang-dev/references/application-migration-review.md); an export never authorizes the proposed adjustments. Read [deployment and recovery](references/deployment-and-recovery.md) before importing. Follow [version upgrades](../oracle-apexlang-dev/references/versions-and-upgrades.md) for a new language release.

## Source contract

1. Confirm target, versions, Git status and export policy.
2. Export the complete APEXlang tree into a new candidate directory. Preserve model metadata, application, pages, shared components, assets and generated artifacts.
3. Explicitly decide Supporting Objects, translations, subscriptions, credentials/remote servers, saved reports, ACL assignments and runtime instances. Exclude private runtime/user information by default. Keep restricted recovery separately from publishable source.
4. Reconcile application/page inventory and validate the whole tree with SQLcl 26.3+, then review CODESCAN. Keep diagnostics private; do not hand-edit generated translation SQL/model metadata.
5. Review diff and secrets/environment values, including checksum salts/deployment files. Preserve the original restricted recovery artifact. A sanitized source needs a tested deployment configuration.
6. Promote the complete candidate atomically, including intentional removals. Keep documentation outside exporter-owned directories.
7. Version/publish when requested. Export permission does not authorize import, refresh or compilation.

APEXlang is canonical application source. Store standard SQL recovery separately. `validate_apex_export.py` checks the split + monolithic SQL contract only; it does not validate APEXlang.

## Database practices

Use these inherited references only for the requested database scope:

- [Baseline](references/database-baseline.md): structural DDL; no user data/secrets.
- [Database release](references/database-release.md) and [five-file bundle](references/release-bundle.md): explicit full/partial scope and comparison base.
- [Pending migrations](references/pending-migrations.md): exactly two configured DDL/DML files; no APEX components or standalone object source.
- [Retention](references/export-retention.md): report before authorized cleanup.
- [Snapshot runtime](references/snapshot-runtime-contract.md): existing project exporter; no implicit runtime installation.
- [Coordinated exports](references/parallel-export.md): matching scope and the same confirmed snapshot/capture window.

## Exit criteria

Report `EXPORTED_NOT_VALIDATED`, `BASELINE_VALIDATED` or `READY_FOR_DEVELOPMENT` using the readiness reference. Include unresolved blockers, applied changes, actual canaries, recovery location, source identity and publication. A baseline can be committed with an explicit non-ready status; an instance upgrade alone does not make an application ready.
