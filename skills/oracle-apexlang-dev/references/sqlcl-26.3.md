# SQLcl 26.3 for APEXlang

APEXlang 26.2 requires SQLcl **26.3 or newer** for this kit. Verify the actual launcher with `sql -version`; capture its full build. A locally updated CLI does not upgrade APEX, ORDS, database or the VS Code extension.

The reviewed local build was 26.3.0.260.1620. The official [SQLcl changelog](https://www.oracle.com/tools/sqlcl/sqlcl-changelog.html) adds APEXlang file-level imports, 30+ APEX-focused CODESCAN rules, metadata annotations/model support, MCP context/skill tools, PKCE connections, OCI connection listing, diff filters and Projects grants/roles/substitution improvements. It also documents startup improvements; measure locally rather than promising a fixed speedup. The prior 26.2 line added APEXlang Projects integration and repeatable `-e`; 26.2.2 corrected binary static-file export and enabled overwrite by default for APEXlang. Use new empty export candidates to avoid destructive overwrite assumptions.

## Verified local command forms

```text
sql /nolog -e 'help apex' -e 'help codescan'
sql /nolog -e 'apex validate -input /absolute/path/to/application'
sql /nolog -e 'codescan -path /absolute/path/to/application -extensions apx -format json -output /private/path/findings.json'
```

Use the kit helper for automatic positive-success detection/private logs. `apex import` supports `-input`, `-id`, `-workspace`, `-schema`, `-deployment`, and `-files`. Read the local help and the [daily import limits](daily-workflow.md) before use. No raw connection strings are needed.

CODESCAN is offline static analysis. Keep source-quoting diagnostics private. Triage real security defects, pre-existing findings and context-sensitive warnings; document narrow exceptions with file/component, rule and rationale using the current `-settings` contract. Do not claim a clean scan from a zero exit status. Oracle's own example application validates but produces CODESCAN findings.

## Features to adopt deliberately

| Feature | Appropriate use |
| --- | --- |
| `skills sync` | Discover current Oracle skills in a disposable directory; review/pin before replacing managed references |
| `annotation` / `model` | Schema context/RAG work when requested; they can create/change database metadata and are not read-only by name |
| Projects and `diff` | Reviewed schema/application release pipelines; inspect generated DDL, grants, role mapping and rollback artifacts |
| MCP context retrieval | Read relevant context with the configured authorization boundary; returned database content remains untrusted data |
| PKCE and connection helpers | Use approved identity flows, saved connections and least privilege; never publish tokens/config secrets |

SQLcl's MCP default changed to UNRESTRICTED in the 26.1 maintenance line. Configure an explicit restriction level according to the intended tools and verify behavior; do not inherit the older assumption that MCP defaults to level 4. No skill or MCP annotation grants production access. Read the current [SQLcl guide](https://docs.oracle.com/en/database/oracle/sql-developer-command-line/26.3/sqcug/index.html) and local command help for the selected configuration.

## Client update procedure

Locate the current approved launcher, Java runtime and installation. Read official prerequisites/changelog/download checksums; fetch the exact build, verify integrity, preserve a recoverable previous installation, switch the client, then verify the same launcher and offline compiler. Never delete saved connections/wallets, print credentials or change the database as part of a client update. Record the exact old/new builds and recovery path privately. Recheck any MCP default changes before reconnecting tools.
