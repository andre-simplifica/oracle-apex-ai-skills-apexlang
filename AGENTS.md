# AGENTS.md

This is the separate Oracle APEX AI Skills APEXlang repository.

## Context

- Repository: `andre-simplifica/oracle-apex-ai-skills-apexlang`
- Audience: Oracle APEX developers, PL/SQL developers, Oracle OCI users, and AI-assisted development practitioners
- Minimum baseline: Oracle APEX 26.2. Only explicitly reviewed feature releases are enabled.
- Core purpose: provide reusable skills, templates, scripts, and documentation that help AI agents work safely with Oracle APEX projects.

## Working Rules

- Work directly on `main` for this repository.
- When a change is finished, commit and push to `origin main` unless the user explicitly asks not to publish.
- Keep this repository generic and reusable. Do not add company-specific, customer-specific, or application-specific rules to the core.
- Do not include private schema names, workspace names, hostnames, internal URLs, credentials, production payloads, or customer data.
- Do not invent APEX, SQLcl, PL/SQL, OCI, Codex, Claude Code, or GitHub behavior. Verify current files before changing instructions.
- Maintain APEXlang-first workflows with version-matched Oracle references. Do not modify the separate 24.2 kit.
- Preserve Oracle upstream files byte-for-byte with their license and pinned checksums. Apply policy adaptations in this kit, not inside the vendor tree.
- Installing or updating skills never connects to Oracle, runs supporting objects, imports an application, or changes production.
- Prefer small, explicit, production-friendly guidance over broad abstractions.
- Keep documentation and skill content in English, except `README.pt-BR.md`, which is the Portuguese onboarding document.

## Source Boundaries

- Main routing and project-managed installation guidance belongs in `skills/oracle-apex-ai-skills-apexlang/`.
- General APEX development guidance belongs in `skills/oracle-apexlang-dev/`.
- Cooperative shared-DEV object-lock guidance and runtime assets belong in `skills/oracle-apexlang-object-lock/`.
- General baseline, export, snapshot, and release guidance belongs in `skills/oracle-apexlang-export/`.
- Human-facing guides belong in `docs/`.
- Reusable project-profile scaffolding belongs in `templates/`.
- Installer, updater, and validation logic belongs in `scripts/`.
- Application-specific project standards belong in the consuming project's `.oracle-apexlang/` profile, not in this reusable core.

## Validation

Before committing, run:

```bash
bash scripts/validate_repo.sh
```

If the validation cannot run locally, state the blocker clearly in the final response.

## Publication Flow

For Codex work:

1. Inspect `git status --short --branch`.
2. Keep edits scoped to the requested improvement.
3. Run `bash scripts/validate_repo.sh`.
4. Commit the scoped change.
5. Push to `origin main`.
