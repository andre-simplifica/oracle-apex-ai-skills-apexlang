# Daily APEXlang workflow

1. Load project rules, version/toolchain evidence and the task's application/Working Copy. Read the canonical baseline, target page and its dependencies; use [Oracle inventory](oracle-reference-policy.md) for actual grammar.
2. Export the target to a separate fresh directory and compare it to the last reconciled baseline. Merge concurrent Builder changes explicitly before proceeding. Keep unrelated local edits. Use consistent export options and exclude volatile export timestamps; never suppress an unexplained difference automatically.
3. Edit the minimum set of `.apx` files. Preserve stable component identifiers, parent containment, theme/template references, authorization and bind variables. Do not regenerate the whole app from a prompt for a focused change.
4. Validate the complete candidate with `apexlang_tools.py validate` and the same deployment JSON intended for import. A single page is not a standalone application. Save the evidence outside all application trees; report paths must be new files. Run CODESCAN and review changed findings according to project rules. Execute proportionate SQL/browser tests where relevant.

```bash
python3 Util/apexlang/apexlang_tools.py validate \
  --root <candidate-app> --apex-version 26.2 \
  --deployment <reviewed-deployment.json> --output <private-validation.json>
```

Read `diagnostics` for file, line, column, error type, recognized property and allowed values. `reference_search` identifies a query for the matching Oracle inventory. Unknown source-bearing messages are omitted from JSON; the private diagnostic log retains compiler output. Treat that log as sensitive local evidence, never public documentation. A successful exit alone is insufficient: validation also requires the compiler's positive success marker and no error diagnostics. The report binds the complete tree, deployment bytes, MMD, APEX release and detected SQLcl build; concurrent source changes invalidate it.

5. Review the entire diff and dependency closure. Capture SQL recovery. Prepare the plan with the actual target identity and fresh live export. Use the exact `sqlcl_version` from the validation report, including its build:

```bash
python3 Util/apexlang/apexlang_tools.py plan-import \
  --root <candidate-app> --baseline <last-reconciled-app> --live <fresh-live-app> \
  --apex-version 26.2 --sqlcl-version <verified-full-build> --ords-version <verified-version> \
  --environment development --app-id <confirmed-id> \
  --workspace <confirmed-workspace> --schema <confirmed-schema> \
  --deployment <reviewed-deployment.json> --files pages/<actual-page-file>.apx \
  --output <private-plan.json>
```

Before executing an authorized import, obtain another fresh export from the confirmed target and verify the plan with the current scope and configuration:

```bash
python3 Util/apexlang/apexlang_tools.py verify-plan \
  --plan <private-plan.json> --validation <private-validation.json> \
  --root <candidate-app> --baseline <last-reconciled-app> --live <new-fresh-live-app> \
  --apex-version 26.2 --sqlcl-version <verified-full-build> --ords-version <verified-version> \
  --environment development --app-id <confirmed-id> \
  --workspace <confirmed-workspace> --schema <confirmed-schema> \
  --deployment <reviewed-deployment.json> --files pages/<actual-page-file>.apx
```

`verify-plan` probes the local SQLcl version, compares full-tree hashes and compiler evidence, and rejects expired plans, target/scope/configuration/toolchain changes, or drift anywhere in the live snapshot. Plans expire after 30 minutes; changes require a new validation/plan as applicable. A fresh export may use a different directory but its contents must match the reconciled baseline. Use `--sqlcl` or `SQLCL_BIN` when the approved launcher is not `sql` on PATH. Use `--allow-app-id-remap` consistently only for a reviewed application/Working Copy mapping.

The result is `PLAN_VERIFIED_OFFLINE`: local consistency only. Hashes detect accidental changes; they are not signatures or approval. The helper cannot prove the origin/freshness of a supplied export, the actual ORDS version, live service/connection identity, dependency closure, recovery readiness or authorization. Confirm these in the executing session. No helper connects to a database or executes the planned import.

6. If the task already authorizes the exact import, execute through the saved connection after same-session identity checks and coordination. Otherwise present the concrete plan/diff for authorization. Continue independent local work without repeated permission requests.
7. Inspect all diagnostics, verify affected metadata and run functional plus negative authorization canaries. Refresh browser/session state as appropriate. Re-export to a new directory and reconcile with the candidate; explain normalization and unexpected changes before updating the canonical source.
8. Commit only intended source and project learning after successful validation, per project publication rules. Release owned locks. Report source, import and runtime separately.

## Selective import boundaries

Oracle 26.2 supports `apex import -input <whole-app> -files <file> ...` using SQLcl/VS Code. Paths are absolute or relative to SQLcl's working directory; the helper emits absolute explicit files. The target application must exist and source must be exported from 26.2+. Use eligible page/shared-component files with their dependencies. Theme/template/plugin and workspace components need a different supported workflow/full application import; SQLcl glob examples do not override APEX limitations. Production always receives a full application import. [Oracle file-import guide](https://blogs.oracle.com/apex/introducing-file-level-import-with-apexlang-in-oracle-apex).

Importing a file replaces its represented definition. Removing a local file is not a supported selective deletion request. File renames, component movement, shared dependencies, new plugins and themes require explicit scope analysis. Use a full reviewed import or Builder for deletion when the selected-file contract cannot represent it. Do not use wildcards to hide an unknown scope.

Keep database object changes and pending migrations separate from application files. A Working Copy does not isolate underlying data; follow cooperative locking for PL/SQL objects.
