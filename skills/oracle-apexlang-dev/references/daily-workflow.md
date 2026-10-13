# Daily APEXlang workflow

1. Load project rules, version/toolchain evidence and the task's application/Working Copy. Read the canonical baseline, target page and its dependencies; use [Oracle inventory](oracle-reference-policy.md) for actual grammar.
2. Export the target to a separate fresh directory and compare it to the last reconciled baseline. Merge concurrent Builder changes explicitly before proceeding. Keep unrelated local edits. Use consistent export options and exclude volatile export timestamps; never suppress an unexplained difference automatically.
3. Edit the minimum set of `.apx` files. Preserve stable component identifiers, parent containment, theme/template references, authorization and bind variables. Do not regenerate the whole app from a prompt for a focused change.
4. Validate the complete candidate with `apexlang_tools.py validate`. A single page is not a standalone application. Run CODESCAN and review changed findings. Execute proportionate SQL/browser tests where relevant.
5. Review the entire diff and dependency closure. Capture SQL recovery. Prepare the plan with the actual target identity and fresh live export:

```bash
python3 Util/apexlang/apexlang_tools.py plan-import \
  --root <candidate-app> --baseline <last-reconciled-app> --live <fresh-live-app> \
  --apex-version 26.2 --sqlcl-version 26.3 --ords-version 26.3 \
  --environment development --app-id <confirmed-id> \
  --workspace <confirmed-workspace> --schema <confirmed-schema> \
  --deployment <reviewed-deployment.json> --files pages/<actual-page-file>.apx
```

This helper prepares a command only. It does not connect, verify claimed live evidence, resolve dependencies or grant approval. Review hashes, source lineage, target identity and deployment contents; recheck immediately before execution. Use `--allow-app-id-remap` only for a reviewed application/Working Copy mapping.

6. If the task already authorizes the exact import, execute through the saved connection after same-session identity checks and coordination. Otherwise present the concrete plan/diff for authorization. Continue independent local work without repeated permission requests.
7. Inspect all diagnostics, verify affected metadata and run functional plus negative authorization canaries. Refresh browser/session state as appropriate. Re-export to a new directory and reconcile with the candidate; explain normalization and unexpected changes before updating the canonical source.
8. Commit only intended source and project learning after successful validation, per project publication rules. Release owned locks. Report source, import and runtime separately.

## Selective import boundaries

Oracle 26.2 supports `apex import -input <whole-app> -files <file> ...` using SQLcl/VS Code. Paths are absolute or relative to SQLcl's working directory; the helper emits absolute explicit files. The target application must exist and source must be exported from 26.2+. Use eligible page/shared-component files with their dependencies. Theme/template/plugin and workspace components need a different supported workflow/full application import; SQLcl glob examples do not override APEX limitations. Production always receives a full application import. [Oracle file-import guide](https://blogs.oracle.com/apex/introducing-file-level-import-with-apexlang-in-oracle-apex).

Importing a file replaces its represented definition. Removing a local file is not a supported selective deletion request. File renames, component movement, shared dependencies, new plugins and themes require explicit scope analysis. Use a full reviewed import or Builder for deletion when the selected-file contract cannot represent it. Do not use wildcards to hide an unknown scope.

Keep database object changes and pending migrations separate from application files. A Working Copy does not isolate underlying data; follow cooperative locking for PL/SQL objects.
