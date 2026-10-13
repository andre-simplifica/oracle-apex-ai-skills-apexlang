# SQLcl execution

Use the project's approved SQLcl launcher and named connection. On a configured Mac, honor its wrapper; never bypass it to invoke a private installation binary. Check `sql -version` and `/nolog -e 'help apex'` before version-sensitive work. [SQLcl 26.3 reference](sqlcl-26.3.md).

For a single non-interactive operation prefer repeatable `-e` arguments. For batch scripts use `whenever sqlerror exit failure rollback`, `whenever oserror exit failure rollback`, an explicit transaction contract and final `exit`; avoid interactive `accept`, `pause` and help prompts in scripts. `/nolog` is sufficient for offline APEXlang validation and CODESCAN.

Before connected work, confirm `USER`, `sys_context('USERENV','SERVICE_NAME')`, application/workspace and parsing schema in the same connection. Saved names are identifiers, not proof of the target. Do not pass or print credentials.

SQL/PLSQL, SQLcl commands and OS commands are distinct. `show errors`, `apex export`, `codescan` and `ddl` are SQLcl commands. Local help describes client support; the server version/privileges still apply.

For shared DEV compilation, audit and acquire the cooperative object lock, assert it immediately before compilation and inspect `USER_OBJECTS` plus `USER_ERRORS` afterwards. A `PACKAGE` lock covers specification and body. Table DDL/reviewed data corrections belong in the configured pending files; canonical package/view/trigger source does not.

An import or DDL can commit irreversibly. Keep recovery and authorization separate from client exit handling. Never run imports by trial and error or equate an exit code with runtime proof.
