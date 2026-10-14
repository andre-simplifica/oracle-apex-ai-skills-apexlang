# Universal Theme and style upgrades

A request to upgrade an application includes assessing and, within the authorized target and scope, refreshing Universal Theme and adopting the intended current style. Do not stop at the engine, Compatibility Mode or APEXlang export. For a full upgrade to APEX 26.2, include UT 26.2 and Iris in the proposed scope. If branding, custom templates, style choice or production authority is unclear, inspect first and ask a focused question. An export-only request or a focused page fix does not implicitly authorize a theme migration.

A theme migration also needs the [application configuration review](application-migration-review.md): inspect definition/security/UI, substitutions, themes/assets, Component Settings and New Features. Offer the full review and automatic adjustments if not already decided; carry out only the agreed scope.

## Preflight and recovery

1. Verify connection, schema/service, workspace, application, installed release, theme number, **theme component ID**, subscription master/status, current style and static ID. Theme number 42, the application's theme component ID and the upstream reference ID are different identifiers.
2. Inspect custom templates, Theme Roller settings, custom CSS/JS, plugins, session/user style overrides and translated applications. Preserve brand choices; do not silently replace a custom theme. Vita and Iris share Theme Roller variable names, but visual compatibility still needs testing; Redwood Light uses a different variable scheme.
3. Capture a private complete SQL recovery export without automatic Supporting Objects execution, the current APEXlang tree, export options and a guarded restore procedure. Coordinate edits and check drift immediately before mutation. A rollback statement alone is not recovery from an operation that may commit internally. Do not execute restore merely to test it against the live application; record whether restoration was rehearsed.

## Programmatic route

Inspect version-matched APEXlang theme properties first. The pinned 26.2 inventory represents `baseTheme: ut-26.2` and `style.currentThemeStyle` (the verified export used `@/iris`; preserve the exported reference casing). Changing those text values alone is not evidence that subscribed templates were refreshed. Prefer the public refresh operation when refreshing a live subscription, followed by a fresh export.

`APEX_SHARED_COMPONENT.REFRESH` supports themes starting with APEX 26.1. Verify the installed public synonym, specification, arguments and permissions; the installed package documents availability in a full APEX installation, not runtime-only deployment. On reviewed 26.2 the contract is:

```sql
apex_util.set_workspace(p_workspace => l_verified_workspace);
apex_shared_component.refresh(
    p_component_type => apex_shared_component.c_theme,
    p_component_id   => l_verified_theme_component_id);
```

Resolve exactly one subscribed theme belonging to the authorized application. Do not iterate over every subscribed component or use `PUBLISH`, which is a different operation. Guard the previous theme version, subscription identity, current style and application target. Verify the refreshed version before selecting the style.

Query `APEX_APPLICATION_THEME_STYLES` for the exact application/theme and intended style. Use the returned numeric `THEME_STYLE_ID`, converted to character, for the persistent current-style API:

```sql
apex_theme.set_current_style(
    p_application_id => l_verified_application_id,
    p_theme_number   => l_verified_theme_number,
    p_id             => to_char(l_verified_style_id));
```

Do not confuse this with session-only style overrides. The public specification documents a Runtime API Usage prerequisite; verify it in the actual execution context and never broaden security permissions just to make a call succeed. Wrap the operation in current-state guards, error handling and an explicit transaction contract, then verify metadata before commit where supported. If a public route is blocked, follow the [internal API contract](apex-internal-apis.md) before requesting Builder access.

## Acceptance

- Query the live theme version, current style, file prefix and subscription state. Compare the complete before/after APEXlang trees; investigate changes outside expected theme/style metadata rather than assuming the refresh was scoped.
- Run whole-tree SQLcl compiler validation and triage relevant CODESCAN findings against the baseline. A clean diff outside the theme does not resolve existing security findings.
- In Browser, test fresh login, Home, navigation, representative reports, filters/AJAX refresh, custom CSS/JS, desktop and mobile overflow. Inspect actual loaded theme CSS paths; metadata alone does not prove the session uses Iris. Test relevant authorization boundaries separately and report any untested paths.
- Reconcile the final export into canonical source and record recovery location, mutation evidence and canary results privately. Publish only generic lessons in this kit. Separate live application state from Git/PR publication state.

References: [26.1 public theme refresh support](https://docs.oracle.com/en/database/oracle/apex/26.1/htmrn/new-features.html), [26.2 enhancements](https://docs.oracle.com/en/database/oracle/apex/26.2/htmrn/new-features.html), [Theme Roller](https://docs.oracle.com/en/database/oracle/apex/26.2/htmdb/using-theme-roller.html). Exact API calls must also be checked against the installed public specification.
