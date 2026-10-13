# Export modes

Use the mode definitions in [the export skill](../SKILL.md). APEXlang is canonical application source; complete source export is distinct from an application-plus-schema initial baseline or a full/partial database release.

Temporary inspection and drift exports belong in separate scratch candidates. SQL recovery belongs in a restricted separate directory and is captured before mutation. Only an explicitly requested release includes the database five-file bundle and pending DDL/DML. Never create a full schema snapshot as a side effect of a page edit.

See [first baseline](readiness-and-first-baseline.md), [database baseline](database-baseline.md) and [release bundle](release-bundle.md).
