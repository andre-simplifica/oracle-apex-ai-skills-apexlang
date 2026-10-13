# Coordinated application and database export

Use concurrent lanes only when explicitly requested/authorized and the project has a known resource/session cap. A focused application export does not need multiple agents or a schema snapshot.

Establish one application/source identity and the same confirmed snapshot or coordinated capture window. Export APEXlang into a fresh candidate, SQL recovery into a different restricted candidate, and the requested database source into its own lane. Detect concurrent edits and retry/reconcile rather than combining incompatible captures.

The coordinator reviews inventory, validation, lineage and diagnostics before promoting output. If any required lane fails, keep partial artifacts labeled incomplete; do not replace the last good published snapshot. Record elapsed time when performance is relevant. Do not reuse an unrelated saved snapshot just because it is faster.

Use [readiness](readiness-and-first-baseline.md), [release bundle](release-bundle.md) and [snapshot runtime](snapshot-runtime-contract.md) for their respective scope. Parallelism changes scheduling, not authority or evidence requirements.
