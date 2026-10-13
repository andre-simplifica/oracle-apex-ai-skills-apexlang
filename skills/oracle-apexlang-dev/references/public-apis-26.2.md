# Public APIs in APEX 26.2

Use this decision index before falling back from APEXlang. Verify the live public signature, overload, privileges, workspace/session context and prerequisites. A public API is supported functionality, not automatic authorization. Resolve public synonyms to their actual owner/package before querying `ALL_ARGUMENTS`; searching only for `APEX_*` in package names can miss the underlying package.

```sql
select owner, synonym_name, table_owner, table_name
  from all_synonyms
 where synonym_name = :public_package
   and owner in (user, 'PUBLIC');

select overload, argument_name, position, data_type, in_out, defaulted
  from all_arguments
 where owner = :resolved_owner
   and package_name = :resolved_package
   and object_name = :public_member
 order by overload, sequence;
```

Resolve synonym chains if present. Check the installed public specification when dictionary access is limited. If no suitable public operation exists, investigate the [internal API contract](apex-internal-apis.md) before requesting UI access; an internal call is not a public API substitute without that review.

## Application operations

| API | Contract and use |
| --- | --- |
| `APEX_APPLICATION_ADMIN.LOCK_APPLICATION` | `p_application_id`, `p_lock_as_user`, `p_lock_comment`; owner must be an existing workspace developer/admin. Same-owner requests update the comment; another owner fails. [Signature](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_APPLICATION_ADMIN.LOCK_APPLICATION-Procedure.html) |
| `UNLOCK_APPLICATION` | Always pass the owned `p_unlock_as_user` with `p_application_id`. Null removes the owner filter and is inappropriate for routine cleanup. [Signature](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_APPLICATION_ADMIN.UNLOCK_APPLICATION-Procedure.html) |
| `CREATE_WORKING_COPY` | Function returning the new app ID; parameters `p_application_id`, `p_working_copy_name`, optional `p_working_copy_description`. Supporting Objects are not copied. Shared schema/data remain shared. Use Builder's supported merge/refresh workflow; no merge API is inferred. [Signature](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_APPLICATION_ADMIN.CREATE_WORKING_COPY-Function.html) |
| `INSTALL_SUPPORTING_OBJECTS` / `GET_SUPPORTING_OBJECTS_ERRORS` | Installation can complete its API call despite execution errors. Query errors explicitly and verify expected objects/data. Separate approval from application import. [Install](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_APPLICATION_ADMIN.INSTALL_SUPPORTING_OBJECTS-Procedure.html), [errors](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_APPLICATION_ADMIN.GET_SUPPORTING_OBJECTS_ERRORS-Function.html) |
| `DEINSTALL_SUPPORTING_OBJECTS` | Destructive operation; inspect deinstallation scripts and data impact, obtain the exact authorized scope and recovery plan. [Reference](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_APPLICATION_ADMIN.DEINSTALL_SUPPORTING_OBJECTS-Procedure.html) |
| `APEX_EXPORT.GET_APPLICATION` | Use `p_type => 'APEXLANG'` for source or `'SQL'` for recovery; check `p_with_supporting_objects`, translations and runtime/private options. Handle returned file BLOB content as documented. [Signature](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/GET_APPLICATION_Function.html) |

## Security

- `APEX_APPLICATION_ADMIN` and `APEX_APPLICATION_INSTALL` expose `SET_DEEP_SEC`, `DEEP_SEC_IS_ENABLED`, `GET_DEEP_SEC_DB_RESOURCE_SCOPE`, `GET_DEEP_SEC_APPLICATION_SCOPE`. With `p_enabled => true`, both scopes are required; disabling requires null scopes. Installation null behavior can inherit exported settings. Verify DB26ai capability and database policy before changing them. [Application settings](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_APPLICATION_ADMIN.SET_DEEP_SEC-Procedure.html), [installation](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_APPLICATION_INSTALL.SET_DEEP_SEC-Procedure.html).
- `APEX_SESSION.ENABLE_DEEP_SEC_DATA_ROLES(p_data_roles, p_current_request_only)` controls roles for the request/session; the latter defaults true. Apply least privilege and test denied data access. [Signature](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_SESSION.ENABLE_DEEP_SEC_DATA_ROLES-Procedure.html).
- `APEX_EXEC.SUSPEND_DEEP_SEC` / `RESUME_DEEP_SEC` need explicit security justification; never use suspension to make a failing access check succeed. [Reference](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_EXEC.SUSPEND_DEEP_SEC-Procedure.html).
- `APEX_AUTHENTICATION.GROUPS_FROM_TOKEN` is a **function**, returning `apex_t_varchar2` with `p_group_names_path_expr`. Release notes loosely call it a procedure. Use the signature and test provider token shape; do not copy the documentation's malformed debug example. Dynamic groups still need application authorization rules. [Signature](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_AUTHENTICATION.GROUPS_FROM_TOKEN-Function.html).

## Workflow, tasks and AI

- `APEX_HUMAN_TASK.SET_TASK_OUTCOME`: set a valid action-task outcome using the documented `p_outcome`, not the inconsistent example's `p_priority`. Confirm task state, actor and allowed outcome; test branching. [Signature](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_HUMAN_TASK.SET_TASK_OUTCOME-Procedure.html).
- `APEX_WORKFLOW.MIGRATE_INSTANCE` accepts instance, variable/parameter values, resume activity and `p_continue_workflow` (default false). Prepare mapping against the new version, handle required parameters and inspect suspended state. It is a runtime migration, not a source edit. [Signature](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_WORKFLOW.MIGRATE_INSTANCE-Procedure.html).
- `APEX_AI.CHAT` and `APEX_AI.GENERATE` overloads accept `p_reasoning_effort`. Verify the overload, provider API/model support and latency/cost before setting a value. [CHAT](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_AI.CHAT-Function-Signature-1.html), [GENERATE](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/APEX_AI.GENERATE-Function-Signature-1.html).
- `APEX_APPLICATION_INSTALL.SET_REMOTE_SERVER` can override OCI service settings during installation. Follow the current signature and approved target configuration; do not embed provider credentials.

## JavaScript

`apex.region.multipleRefresh` can combine refreshes for Cards, Charts, Interactive Grid and Template Components; unsupported regions make their own requests. The new `ForegroundTimer` and `chartRegion` API support visibility-aware refresh control. `apex.util.applyTemplate` adds the `%assigned` operator. Inspect the current [JavaScript reference](https://docs.oracle.com/en/database/oracle/apex/26.2/aexjs/index.html) before writing exact calls; test hidden regions, dialogs and reduced-motion behavior.

## Fallback order

Use matching APEXlang for represented source, then a documented public API, then a verified internal API within the authorized project policy. Investigate these programmatic routes before requesting Builder/SQL Developer UI access. Internal APIs remain version-specific implementation details: follow the [internal API contract](apex-internal-apis.md), preserve recovery, and re-export after an authorized change. Request UI access only for the concrete operation still blocked; do not confuse lack of public documentation with proof that no safe programmatic route exists.

Prior 26.1 capabilities are indexed in [the inherited API reference](apex-26-1-public-apis.md); recheck signatures on 26.2. `APEX_LANG` translation APIs are not the APEXlang source language. Complete package discovery: [API contents](https://docs.oracle.com/en/database/oracle/apex/26.2/aeapi/toc.htm) and [APEX Diff](https://oracleapex.com/apexdiff).
