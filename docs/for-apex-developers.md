# For APEX developers

This kit connects your existing project conventions to source-based APEX development. Start with [first application](first-application.md), then use [daily workflow](../skills/oracle-apexlang-dev/references/daily-workflow.md).

The agent learns from real pages, modifies `.apx`, validates the entire app and uses scoped imports when suitable. App Builder remains available for supported operations that lack a source/public-API route. Re-export after Builder changes to keep Git synchronized.

Theme refresh, Compatibility Mode and database changes are separate decisions. Compiler success does not run business logic; demonstrate the affected user flow after import.
