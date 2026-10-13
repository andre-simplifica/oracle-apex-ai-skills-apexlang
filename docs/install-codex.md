# Install with Codex

Use a clean checkout of an immutable tag/commit from `https://github.com/andre-simplifica/oracle-apex-ai-skills-apexlang`. Prepare the isolated test environment in the README and run `bash scripts/validate_repo.sh` first. Confirm the requested ref resolves to the checked-out HEAD.

```bash
python3 scripts/manage_project_installation.py install \
  --project-root /path/to/project --source-ref <tag-or-commit> --dry-run
```

Review the file plan and run without `--dry-run`. The installer copies the four skills, tools and pinned Oracle references, initializes missing project-owned templates, and records checksums/source identity. It does not change Git or connect to Oracle. Follow [the installation contract](../skills/oracle-apex-ai-skills-apexlang/references/installation-and-updates.md).

The existing `.oracle-apex-ai/` kit uses different names and paths. Preserve it; explicitly route 26.2 APEXlang work to `$oracle-apex-ai-skills-apexlang` and merge useful project standards into the new profile. When rules conflict, the consuming project's explicit routing/instructions must select the intended kit; co-installation alone does not resolve contradictory old instructions.

Run the copied manager's `status` and `doctor`. With confirmed versions, provide `--apex-version`, `--sqlcl-version` and `--ords-version`; this is an offline compatibility check. Audit/install database locking separately only if relevant and authorized.

Optional personal installation: `bash scripts/install_codex.sh` creates symlinks under the user's `.agents/skills`. Keep the source checkout available because references resolve there. Existing real skill directories require an intentional backed-up replacement with `--replace-existing`. This command does not install the kit into a consuming repository.
