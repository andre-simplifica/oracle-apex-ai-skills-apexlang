# Oracle references and syntax discovery

The kit carries the complete Oracle APEXlang **26.2** directory from `oracle/skills`, unmodified, with its UPL license. `vendor/oracle-skills/upstream-lock.json` pins commit, paths and SHA-256 hashes. In a managed project it is installed at `.oracle-apexlang/vendor/oracle-skills/`. A personal symlink installation resolves references from the source checkout; do not expect vendored files inside the individual skill directory.

```bash
python3 Util/apexlang/oracle_reference.py verify
python3 Util/apexlang/oracle_reference.py search --query 'interactive-grid'
```

In the kit itself use `scripts/oracle_reference.py`. Search reports candidate document paths; then read only those needed. Do not load all inventory files into model context.

## Four upstream skills

| Oracle directory | Use |
| --- | --- |
| `apexlang-inventory` | Read `SKILL.md`, index and the component document for syntax, required identifiers, containment, `filePath`, properties, allowed enum values, `appliesWhen` and references |
| `apexlang-example-applications` | Inspect the closest page and its complete app context; copy patterns, not example app IDs, credentials or business logic |
| `apexlang-compile` | Understand offline compilation and diagnostics; this kit's helper verifies SQLcl and validation success |
| `apexlang-deploy` | Reference command behavior only; use this kit's controlled deployment workflow instead of its sample script |

The 26.2 set has no separate generation skill. Do not fall back to 26.1 guidance because a file name is missing.

APEXlang is not YAML. Follow its actual grammar: properties occupy their own lines; property groups and complex values have different colon rules. Required identifiers, enum tokens and references come from the component inventory. Examples show flat `pages/pNNNNN-name.apx`, `.apex/apexlang.json`, `application.apx` and `deployments/default.json`. Preserve the existing application's layout where the matching exporter differs. Do not invent abbreviated syntax or infer component properties from Builder labels.

Theme references are versioned dependencies. Use the application's exported/subscribed theme; Oracle example central-theme IDs are not a portable license to replace it. Validate application/template references together.

## Authority and upstream differences

The live release and matching public documentation control supported behavior. Oracle sample scripts do not grant mutation authority. In particular, the deployment sample sets automatic Supporting Objects installation and uses a connection-string variable; do not execute it unchanged. Inventory guidance suggesting automatic installation is subject to the project's explicit Supporting Objects decision. An upstream generic version router may guess a release; this kit blocks unknown versions instead.

New upstream code is not auto-trusted. Review the exact diff, license, inventory model/version, sample scripts and dependency changes; update the lock, revalidate examples, then release a kit version. `skills sync` can help discovery in a scratch directory but must not overwrite reviewed managed references or project standards.

## Other Oracle material worth consulting

The same repository includes SQL/PLSQL, schema discovery, safe DML, error analysis and SQLcl/MCP material. See the [selected database practices](oracle-database-practices.md). Use narrow references when the task needs them and verify live schema/public APIs; do not bulk-install unrelated skills. SQLcl MCP restrictions changed over time, so old examples are not a current permission contract. See [SQLcl 26.3](sqlcl-26.3.md) and the [pinned upstream repository](https://github.com/oracle/skills/tree/014cdb29f12dfa6a689bbe8a80ee1c5f0bf15be1).
