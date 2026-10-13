# Oracle APEX AI Skills APEXlang

A reusable skill kit for **Oracle APEX 26.2**, with APEXlang as editable, versioned application source. It helps an agent assess a newly upgraded application, create the first complete baseline, then edit, validate, import and verify changes through a controlled development loop.

[Português do Brasil](README.pt-BR.md) · [First application](docs/first-application.md) · [Install](docs/install-codex.md) · [Release review](skills/oracle-apexlang-dev/references/release-notes-26.2.md)

This is a separate project derived from [Oracle APEX AI Skills](https://github.com/andre-simplifica/oracle-apex-ai-skills). The original kit remains the SQL-based path for APEX 24.2. Skill names, profiles and installed tools here use separate paths so the two kits can coexist.

## Compatibility

| Component | Requirement |
| --- | --- |
| APEX | Minimum 26.2; reviewed release 26.2 |
| SQLcl | 26.3+; local build 26.3.0.260.1620 tested |
| ORDS | 26.3+; verify the actual server |
| Database | Supported 19c RU 19.18+ or Oracle AI Database 26ai 23.26.0+ |
| Future APEX releases | Blocked until their inventory, APIs and migration workflow are reviewed |

A file installation can run without a database. Connected work requires verified environment identity and version evidence. Compiler success is not runtime or production validation.

## What is included

- Four coordinated skills: routing/install, APEXlang development, baseline/release and cooperative database-object locks.
- The complete Oracle-maintained APEXlang 26.2 reference set, pinned at commit `014cdb29f12dfa6a689bbe8a80ee1c5f0bf15be1`, with SHA-256 inventory and UPL license.
- First-adoption checks for theme/subscriptions, Compatibility Mode, legacy metadata, translations, Supporting Objects, integrations and security.
- SQLcl offline validation, explicit import plans, whole-tree drift detection and deployment identity checks. Plans never execute imports.
- Version-specific API guidance, release-note coverage and SQLcl 26.3 practices, including CODESCAN.
- A manifest-aware project installer/updater preserving local profiles, patterns, migrations and the previous kit.
- Inherited PL/SQL, REST, runtime, schema baseline, pending migration and five-file database release practices.

## Start in a consuming project

Ask your agent:

```text
Install Oracle APEX AI Skills APEXlang in this project from
https://github.com/andre-simplifica/oracle-apex-ai-skills-apexlang.
Preserve the existing project standards and the previous kit. Pin the source
commit, inspect the installation plan, then install and run status/doctor.
Do not connect to or change Oracle as part of file installation.
```

For a reproducible CLI installation from a clean source checkout:

```bash
python3 scripts/manage_project_installation.py install \
  --project-root /path/to/project --source-ref <tag-or-commit> --dry-run
```

Review the plan and repeat without `--dry-run`. Run the copied manager:

```bash
python3 Util/apexlang/manage_oracle_apexlang_skills.py status --project-root .
python3 Util/apexlang/manage_oracle_apexlang_skills.py doctor --project-root .
```

Use `$oracle-apex-ai-skills-apexlang` as the main skill. Read [Codex installation](docs/install-codex.md) or [Claude Code installation](docs/install-claude-code.md). Personal installation is optional; a managed project is preferred for teams.

## The first application

```mermaid
flowchart LR
    A[Confirm target and versions] --> B[Inspect upgraded application]
    B --> C[Export fresh APEXlang and SQL recovery]
    C --> D[Validate and assess remediation]
    D --> E[Commit first complete baseline]
    E --> F[Authorized DEV round trip and canaries]
    F --> G[Source based development]
```

An export request does not authorize theme refresh, imports or schema changes. A theme refresh is assessed and tested when appropriate; it is not blindly required before every export. Read the [first baseline workflow](skills/oracle-apexlang-export/references/readiness-and-first-baseline.md).

Typical next request:

```text
Assess this application, recently upgraded to APEX 26.2, and export/version
its first complete APEXlang baseline. Report readiness, diagnostics and any
proposed remediation before applying database or application changes.
```

## Daily development

Edit the smallest source diff using the matching Oracle inventory. Validate the whole application, review CODESCAN, compare a fresh live export, and prepare the exact import scope. Eligible development/test updates can use selected files. Production receives a complete tested application artifact. After an authorized import, exercise runtime/authorization canaries and re-export to reconcile the actual state.

```bash
python3 Util/apexlang/apexlang_tools.py validate \
  --root apex/my-app --apex-version 26.2
python3 Util/apexlang/oracle_reference.py search --query 'interactive-grid'
```

Read [daily workflow](skills/oracle-apexlang-dev/references/daily-workflow.md), [deployment/recovery](skills/oracle-apexlang-export/references/deployment-and-recovery.md) and [public APIs](skills/oracle-apexlang-dev/references/public-apis-26.2.md). Working Copies isolate application metadata, while database objects/data remain shared.

## Updating and verification

[Update instructions](docs/update-and-contribute.md) distinguish kit updates, SQLcl updates and APEX/source upgrades. New engine releases are never enabled by changing only a version number.

```bash
python3 -m venv .tmp/validation-env
source .tmp/validation-env/bin/activate
python3 -m pip install -r requirements-dev.txt
bash scripts/validate_repo.sh
```

CI runs offline installation, integrity, version, source-plan, retention and migration tests. SQLcl integration tests are opt-in through `SQLCL_BIN`; see [validation evidence](docs/validation.md). No live application import, schema compilation or production test is implied by the kit release.

## License and provenance

Core: MIT. Oracle reference files: UPL 1.0, preserved unmodified. See [third-party notices](THIRD_PARTY_NOTICES.md), [source catalog](docs/research-sources.json), [security](SECURITY.md) and [contributing](CONTRIBUTING.md).
