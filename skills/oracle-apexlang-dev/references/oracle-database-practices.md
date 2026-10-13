# Related Oracle database practices

These are selected references from the same reviewed Oracle commit, not additional installed executors. Apply them only to the relevant database task and verify syntax against the actual database version.

| Reference | Useful contribution and local boundary |
| --- | --- |
| [Schema discovery](https://github.com/oracle/skills/blob/014cdb29f12dfa6a689bbe8a80ee1c5f0bf15be1/db/agent/schema-discovery.md) | Discover columns, keys and dependencies before generating SQL. Prefer scoped USER/ALL views; do not request DBA privileges simply to run an example. |
| [Safe DML](https://github.com/oracle/skills/blob/014cdb29f12dfa6a689bbe8a80ee1c5f0bf15be1/db/agent/safe-dml-patterns.md) | Preflight counts and bounded predicates are useful. Also require current-state predicates, expected-row-count assertions, explicit transaction control and postconditions. Review sample syntax; do not copy an immediate COMMIT or assume rollback makes trigger/external side effects harmless. |
| [Error handling](https://github.com/oracle/skills/blob/014cdb29f12dfa6a689bbe8a80ee1c5f0bf15be1/db/plsql/plsql-error-handling.md) | Preserve stack/backtrace and distinguish expected business exceptions from unexpected faults. Keep sensitive values out of logs and never silently absorb unexpected exceptions. |
| [Error catalog](https://github.com/oracle/skills/blob/014cdb29f12dfa6a689bbe8a80ee1c5f0bf15be1/db/agent/ora-error-catalog.md) | Use for diagnosis, then confirm the actual error, target state and documented remediation. An error number does not authorize a grant, recompilation or production change. |
| [SQLcl MCP](https://github.com/oracle/skills/blob/014cdb29f12dfa6a689bbe8a80ee1c5f0bf15be1/db/sqlcl/sqlcl-mcp-server.md) | Saved-connection and transport concepts help setup. Older runtime/default-restriction assumptions need the current changelog and local help; see [SQLcl 26.3](sqlcl-26.3.md). |

Preserve the project's existing PL/SQL standards and cooperative locks. The reusable core does not import customer-specific packages, tables, naming conventions or an automatic database repair agent from these references.
