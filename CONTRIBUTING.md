# Contributing

Keep the core generic and English; only `README.pt-BR.md` is Portuguese onboarding. Preserve application-specific rules in consuming-project profiles. Never publish credentials, private targets, logs or customer data.

Follow [source boundaries](AGENTS.md). Do not modify the separate APEX 24.2 kit. Keep Oracle vendor files byte-identical; change local policy references instead. New release support requires a matching inventory, migration/API review and explicit tests, not a minimum-version edit.

Preserve installed project profiles, patterns, readiness, pending migrations and untracked work. Database/runtime installation and application import remain separate from file installation. Use meaningful behavioral tests for scripts and `bash scripts/validate_repo.sh` before committing.
