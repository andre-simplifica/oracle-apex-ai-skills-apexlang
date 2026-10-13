# Architecture

Four short skill entrypoints route to focused references. The inherited database safety, project learning and publication practices remain, while APEXlang becomes canonical application source.

| Layer | Owner |
| --- | --- |
| `skills/` and installed `.agents/skills/` | Versioned kit |
| `vendor/oracle-skills/` and installed `.oracle-apexlang/vendor/` | Unmodified pinned Oracle reference |
| `scripts/` and installed `Util/apexlang/` | Deterministic offline helpers |
| `.oracle-apexlang/project-profile.md`, patterns, readiness, policy | Consuming project |
| Application `.apx`, deployment configuration, database migrations | Consuming project with its own publication/authorization rules |

The installation manifest records managed file hashes; the kit upstream lock records kit origin; the Oracle vendor lock records a separate upstream commit. Neither proves runtime readiness. Skills install without Oracle access. Source validation uses `/nolog`; import planning produces commands but never executes them.

Application Working Copies and database locks are complementary. Production authority remains explicit. Read [technical overview](technical-overview.md) and [source boundaries](../AGENTS.md).
