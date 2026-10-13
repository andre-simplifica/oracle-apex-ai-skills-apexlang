# Install with Claude Code

Use the same manifest-managed project installation described in [Codex installation](install-codex.md). Do not independently copy a second mutable core.

To make a checked-out kit discoverable through Claude's skill directory, run `bash /path/to/kit/scripts/install_claude_code.sh` for personal symlinks, or run it with `--project` from the consuming project for `.claude/skills` symlinks. Keep the source checkout available. The script refuses to overwrite an existing real directory.

If the project needs portable copies rather than local symlinks, use the managed `.agents/skills` tree as the canonical source and configure the project's Claude entrypoint to read its router explicitly. Verify discovery in the actual client. Installing skills never authorizes database changes or chooses a different executor than the user requested.
