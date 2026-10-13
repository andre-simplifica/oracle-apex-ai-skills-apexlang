# Technical overview

[Compatibility](../templates/compatibility.json) records minimum APEX 26.2, reviewed releases, toolchain prerequisites and no claimed live runtime verification. `apex_version.py` rejects older and unreviewed future feature releases.

`apexlang_tools.py inspect` inventories source and hashes. `validate` invokes SQLcl offline and requires positive compiler evidence. `plan-import` compares the full baseline with a fresh export, checks explicit target mappings and rejects unsupported selected paths/production partial imports. It does not parse the complete language, resolve dependency closure, authenticate a target or execute a plan.

`oracle_reference.py` verifies pinned Oracle inventory hashes and searches component documents. The project installer copies the reference tree along with tools and verifies managed-file integrity on updates.

The SQL recovery validator, pending migration checker, retention reporter and five-file release validator remain distinct. No command here silently upgrades a database runtime or imports an application.

See [validation](validation.md), [APIs](../skills/oracle-apexlang-dev/references/public-apis-26.2.md) and [release review](../skills/oracle-apexlang-dev/references/release-notes-26.2.md).
