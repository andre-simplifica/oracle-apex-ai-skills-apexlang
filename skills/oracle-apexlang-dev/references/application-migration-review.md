# Application migration configuration review

Read this for legacy application migrations, engine/Compatibility Mode upgrades,
theme changes, and first APEXlang adoption. A successful engine upgrade, theme
refresh or export does not establish that the application's configuration is current.

## Agree the review scope

Inspect the confirmed target and existing authorization first. Prepare a short,
read-only inventory of configuration findings, dependencies and proposed changes.
If the user has not already chosen this scope, ask one focused question offering:

- **Review and apply:** review the whole application and automatically apply the
  proposed adjustments within the explicitly authorized target and scope.
- **Review only:** document findings and proposed adjustments without applying them.
- **Requested migration only:** complete the agreed migration and record deferred
  configuration findings without expanding it.

For example: "This older application still has unused theme assets and legacy
application settings. Would you like a full configuration review with automatic
adjustments in the confirmed target, a review only, or just the requested migration?"
Adapt the question to the actual findings and the user's language. Do not invent
findings to justify a review. An export-only request remains read-only.

A migration request alone does not authorize unrelated configuration remediation.
If the user already requested the full review and adjustments, proceed without
asking again. Keep their opt-out and earlier authorization across turns. Continue
independent, already authorized work while waiting; silence or elapsed time is
not consent for additional live changes. Record the agreed mode and target in
the project profile/readiness record.

## Review the entire application

Inspect Application Definition and Shared Components, including the following
areas. Record observed state, dependencies, proposed action, validation and any
reason to preserve/defer. Do not apply a uniform set of switches to every app.

| Area | Checks and decision criteria |
| --- | --- |
| Definition | Name/alias/version, Compatibility Mode, Friendly URLs, availability/build status, logging/debug, feedback, accessible read-only items, process limits, global notification and error handling |
| Substitution strings | Search pages, shared components, templates, static assets, SQL/PLSQL and print documents before removal; check obsolete branding and names that shadow built-in substitutions |
| Security | Authentication/authorization, public pages, session-state/checksum protection, exact substitutions, cache, frames, escaping, referrer, bots, Runtime API Usage, session timeout/rejoin and password-item session storage |
| Database Session | Parsing schema, MLE, initialization/cleanup and existing dependencies; preserve business transaction semantics |
| Globalization | Language, direction, masks, comparison/NLS, time zone and native messages; distinguish display cleanup from business behavior |
| User Interface | Native icons/favicon/PWA assets, logo/text, navigation/menu/bar, JavaScript/CSS, concatenated files, external scripts, custom paths and deprecated libraries |
| PWA | HTTPS/Friendly URL prerequisites, enabled/installable settings, name/description/colors, manifest/icons and service worker; enable when included in the agreed scope |
| Themes | Active theme, subscription/master/version, style, overrides, templates/options and used assets; distinguish local themes from centrally inherited template references |
| Component Settings | Native defaults, labels/values, calendar behavior, report features and plugins; review remote debug and external configuration without exposing private values |
| New Features / Upgrade Application | Review each category and actual candidates in the installed release; classify applied, preserved or deferred with a reason |
| AI/workflows/integrations | Inspect existing settings and dependencies; provider changes, credentials, external costs and outbound notifications require their own explicit scope |

Do not disable or strengthen a setting solely because it is old: understand the
application's dependencies and validate the result. Never weaken protection or
broaden Runtime API permissions to make a tooling call succeed. Changing the
identity provider, widening user access, executing business DML, database DDL,
jobs/grants or production changes requires specific existing authorization.

## Prepare and apply the agreed adjustments

- Preserve a complete private SQL recovery export and current APEXlang source,
  including the real target's deployment configuration. Keep checksum salts,
  credentials and runtime/user information out of published artifacts. Check drift
  before import and follow [deployment/recovery](../../oracle-apexlang-export/references/deployment-and-recovery.md).
- Use APEXlang first, documented public APIs next, then verified internal APIs
  under the [fallback contract](apex-internal-apis.md). When no safe route completes
  the change, check for an existing authorized Builder session before asking the
  user for access. Request access only for the concrete remaining task.
- Delete inactive themes/styles/assets/substitutions only after proving they are
  unused, including inherited references and external print/template consumers.
  Age, an unfamiliar name or a similar theme number is not proof of disuse.
- Apply New Features individually. Preserve calendar masks/time/ranges/month and
  year selectors; preserve button requests, validation, conditions, authorization
  and database actions when replacing JavaScript confirmations. Do not execute
  destructive actions merely to test a dialog.
- Keep plugin APEXlang identifiers unique across component types and verify their
  native static IDs and consumer references. Compiler success alone may not detect
  an incorrect cross-type binding. Read exported defaults from the matching
  inventory and verify effective live metadata rather than treating omitted
  properties as disabled.
- Defer form/grid conversions and other changes needing separate business-flow
  validation. Do not use Upgrade All as a substitute for reviewing the candidates.

## Acceptance and project record

Validate the entire source tree, triage CodeScan findings and verify effective
configuration after the authorized application changes. Test valid and invalid
login, selection/context changes, authorization failures, navigation, representative
reports/calendars/filters/AJAX, relevant custom scripts, and desktop/mobile layout.
Check loaded assets, native icons, manifest and service worker. PWA configuration
does not prove operating-system installation or offline business functionality.

After an authorized migration, re-export the complete application to a new
candidate directory, reconcile intentional removals and validate again. Inspect
the actual artifact format: a download named ZIP can contain an HTML error page.
Publish the complete reviewed source when requested, following the project export
policy; do not generate a schema/release snapshot as an incidental side effect.

Keep application-specific results and the agreed review mode in the consuming
project, not this reusable kit. Report configuration applied, source/publication,
actual runtime tests and production state separately. If a critical login or
business canary fails, record the exact blocker and do not declare readiness.
