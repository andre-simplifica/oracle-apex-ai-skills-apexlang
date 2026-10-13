# Programmatic fallback and internal APEX APIs

Resolve an authorized operation in this order: matching APEXlang source, documented public API, verified internal API, then App Builder as the last resort. Investigate the programmatic routes before asking for Builder access. A user may require this order even when Builder is available. Internal `WWV_FLOW_*` APIs remain unsupported implementation details; discovery is not permission to mutate, and compiler errors are not a reason to bypass validation.

## Before calling an internal API

- Confirm operation/target authorization and the consuming project's internal-API policy. Existing explicit authorization remains valid; do not ask again merely because a verified implementation uses an internal setter. A local prohibition still needs a user override.
- Resolve synonyms and inspect the exact installed package specification and `ALL_ARGUMENTS`, including overloads and defaults. Use a fresh SQL export from the same APEX release to establish wrappers, identifiers and context where applicable. Do not extrapolate signatures or valid values from older releases.
- Choose the narrowest operation. Verify application/workspace/schema/service, expected current value and one unambiguous target; abort on mismatch. Preserve component identities and concurrent edits. Never directly update APEX dictionary tables.
- Capture recovery before mutation and prepare the inverse operation. Establish commit behavior; a trailing rollback does not undo an APEX import or an internally committed operation. Use fail-safe error handling and explicit transaction control where applicable.
- Verify the immediate postcondition, re-export the complete APEXlang tree, explain every difference and run affected runtime/security canaries. Record the installed version and internal route in private project evidence, without claiming public API support or portability.

If scope, privileges, side effects or recovery cannot be established, stop that mutation. Complete independent authorized work and report the precise unresolved operation before requesting Builder access. Do not install helper packages or broaden into a full import merely to avoid the UI.

## Compatibility Mode: verified 26.2 setter

In an APEX 26.2.0 installation, the `WWV_FLOW_IMP` synonym resolved to the current APEX owner's package, whose specification exposed:

```sql
procedure set_compatibility_mode (
    p_flow_id            in number default wwv_flow.g_flow_id,
    p_compatibility_mode in varchar2 );
```

The installed specification describes this as the implementation of `APEX_UTIL.SET_COMPATIBILITY_MODE`. Historical public documentation for that utility is not proof of its current supported values. Recheck the installed signature and synonym on every target; use an explicit application ID, not the default session flow ID.

A verified approach is to establish the confirmed workspace context with `APEX_UTIL.SET_SECURITY_GROUP_ID`, then invoke `WWV_FLOW_IMP.SET_COMPATIBILITY_MODE` inside a guarded script with the exact application ID and expected previous mode. Verify `APEX_APPLICATIONS.COMPATIBILITY_MODE` before committing and re-export afterward. Do not run an unguarded generic example against an unknown application.

For the pinned 26.2 model the newest value is `26.1` (label **26.1 to 26.2**). A fresh export may omit `runtime.compatibilityMode` when it equals that default; corroborate the omission with live metadata and the version-matched inventory. A page-only import cannot apply this application-level setting. This setter provides a narrow alternative without replacing the application; it does not authorize a theme, authentication or schema change.

APEX 26.1 also changed external Static IDs versus HTML DOM IDs. Preserve their distinction when investigating other metadata APIs. [Changed behavior](https://docs.oracle.com/en/database/oracle/apex/26.1/htmrn/changed-behavior.html).
