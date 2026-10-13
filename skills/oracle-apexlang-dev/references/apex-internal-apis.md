# Internal APEX API exceptions

Normal work uses APEXlang, documented public APIs or App Builder. Internal `WWV_FLOW_*` metadata APIs are unsupported implementation details and are not a fallback to try when the compiler reports an error.

For an explicitly approved legacy project exception, first inspect a fresh standard SQL export from the exact target release and actual package signature. Preserve wrappers, component identities, parent scope and application/workspace context. Require one unambiguous match, current-state checks, recovery and proportional postconditions. Never extrapolate a parameter from an older release or mutate APEX dictionary tables directly.

APEX 26.1 changed the distinction between external Static IDs and HTML DOM IDs; metadata call names/parameters and wrapper behavior can differ. Regenerate evidence on 26.2. [Prior changed behavior](https://docs.oracle.com/en/database/oracle/apex/26.1/htmrn/changed-behavior.html).

If no supported or reviewed operation exists, explain the exact missing capability and prepare the supported Builder procedure. Do not silently broaden authority or install arbitrary metadata packages. After an authorized change, re-export and reconcile APEXlang, then run the affected flow/security checks.
