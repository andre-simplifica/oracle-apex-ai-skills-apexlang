# Deployment and recovery

Application import is a database mutation even when only one `.apx` file changes. Require exact target/scope authorization and current same-session identity. A generated plan is not executable approval and does not prove a saved connection, privileges, locks, rollback or runtime.

Before execution, hold the project's owned application/Working Copy coordination and applicable database-object locks. Capture a fresh SQL recovery export and preserve the last reconciled APEXlang tree. Review complete-tree validation, CODESCAN findings, fresh drift comparison, target mapping and dependency closure. Never unlock another developer's application to continue.

## Deployment JSON

Use `deployments/default.json` from the export and an explicitly reviewed target configuration passed with `-deployment`. Supported 26.2 groups include `app` identity/runtime/databaseSession/availability/staticFiles/proxy/sessionStateProtection, `workspace`, `subscription.masterApps` and theme file-prefix configuration. Check the exact property in the current guide. Do not infer JSON keys for settings mentioned only in release announcements. [Deployment files](https://docs.oracle.com/en/database/oracle/apex/26.2/apxdc/understanding-apexlang-deployment-files.html).

Confirm application ID, workspace and parsing schema against both command options and JSON; conflicting mappings block the plan. Check subscribed parent application mappings and theme availability in the destination. Keep checksum salts, credentials and private endpoints out of public source. Use a private deployment file populated by the approved secret/configuration mechanism; do not replace a salt with a placeholder and claim the artifact is deployable.

Supporting Objects, automations, subscriptions and security defaults can have side effects beyond page metadata. Inspect `autoInstall` and Supporting Objects scripts in source. Record whether they are absent, retained without execution or explicitly approved to execute. Do not pass `-expSupportingObjects I` or call `set_auto_install_sup_obj(true)` as an incidental convenience. If installation is explicitly selected, query `APEX_APPLICATION_ADMIN.GET_SUPPORTING_OBJECTS_ERRORS`: the install API can return normally despite errors. [Supporting Objects API](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_APPLICATION_ADMIN.INSTALL_SUPPORTING_OBJECTS-Procedure.html).

## Execution and postconditions

Use the generated SQLcl command through the confirmed saved connection after `USER`/service/app checks. Set fail-safe SQL/OS behavior and explicit exit in batch scripts. Inspect tool diagnostics as well as exit code; do not assume `whenever sqlerror` detects every client-side failure. Imports, DDL and Supporting Objects are not a rollback-safe transaction merely because a wrapper ends in `rollback`.

For a file import, verify the selected components and dependencies. For a full import, verify application identity/build status, authentication, authorization, translations, assets, subscriptions, integrations, automation state and schema object validity as relevant. Run business canaries, including at least one denied cross-scope access. Re-export and review the actual metadata diff before claiming success.

Recovery is an authorized re-import of the known-good application plus separately planned database/data recovery for side effects. Preserve exact Git revision, deployment configuration identity, export provenance and private logs. Releasing a lock is not rollback. If a postcondition fails, stop further promotion, preserve evidence and execute only the agreed recovery scope.
