# Along shared workflow

Along supplements the selected finance app through on-demand work. Choose the smallest workflow that can finish the user's request; source reconciliation is not a prerequisite for categorization, reporting, or a dated forecast.

## Explicit setup and account actions

Every Along workflow requires completed household setup. Before doing finance work, read the selected household profile and its setup verification. A usable setup has `setupState: complete` and evidence that computer use could read the selected finance-app workspace. A profile's existence or an installed tool alone is insufficient. For older profiles, accept equivalent dated setup evidence without rewriting history; if that evidence is absent, ask the user to resume setup.

If setup is missing or partial, preserve the requested task and say “Run $along-setup first so Along can check access to your finance app.” Stop the workflow before accessing accounts, analyzing files, or changing records. This applies to all seven non-setup skills, including status and supplied-file work. Explaining this prerequisite is allowed. Only an explicit user request invokes setup; never run it automatically.

Completed setup is a household prerequisite, not a permanent permission grant. After setup, saved-data/file work can proceed without a live session; live operations still require the fresh access check below. A changed finance-app workspace requires the user to update setup. A changed host/browser or expired permission requires fresh live verification, not repeated household intake.

Use clear action language: **set up Along** establishes household configuration; **set up Along sync for an account** establishes source access, app mapping and exclusive update responsibility; **sync** imports source activity; **reconcile** checks records on a stated evidence basis. “Connect” alone does not choose between these actions. A request to sync an account not onboarded for Along offers app-only checking versus Along sync onboarding followed by source reconciliation, unless the user already made that choice. A one-off source/statement comparison never implies ongoing sync.

## Identity and access

Resolve the household and app workspace from explicit context or `work/along-local.json` (`householdId`, `dataRoot`, optional `legacyProfileRef`). Never infer the household from the computer username. Use established account storage paths. Multiple matching households or unresolved account identity require selection before dependent access or writes. After the setup prerequisite passes, supplied-file outputs may use the task workspace without creating another household profile.

Before live access read [authentication](authentication.md) and [runtime adapters](runtime-adapters.md). Select the host branch from the actual current tool inventory. Initialize the exposed native browser/native-app surface or configured supported connector according to its returned documentation. In a new session or after a browser/profile, workspace, tool, or permission change, obtain a fresh readable account-list/detail view and verify the intended workspace. Record tool/adapter discovery, capability results and app access separately, with timestamp and evidence. A listed tool or prior successful login is not current verification. If the selected live route is unavailable, continue supplied-file/saved-data work with its limits; do not substitute shell-driven UI or private endpoints. A supported connector may be used only if actually available, authorized for the selected target, and its semantics are known.

Before interpreting unfamiliar app fields or operations, read [capabilities](capabilities.md) and the applicable app reference; for Monarch read [Monarch behavior](monarch.md). Before saving private records read [records](records.md); before any app mutation read [changes](changes.md). If a required dependency is missing, stop only the dependent operation.

## Scope and routing

| User's job | Owner and completion |
|---|---|
| Explicit household setup | Explicit Along setup command, user-invoked only; household/app/storage context and inventory, no account sync |
| Use Along to update an account, onboard Along sync or recover it | `along-sync-account`; verified source-to-app updates and separate reconciliation coverage |
| Status and pending work | `along-status`; dated saved state or requested live app inspection |
| Fetch a statement for a task | Shared [evidence](evidence.md) procedure; no onboarding or sync implied |
| Categorize, split, review purchases, resolve refunds, assign questions, repair rules | `along-review-transactions`; handled items and unresolved cases are distinguishable |
| Check app records, compare a statement, reconcile an Along-synced account or household period | `along-reconcile`; app-only, supplied/one-off-source, or Along-source basis stated, with only supported checks claimed |
| Explain historical spending, cash changes or comparisons | `along-report-money`; answer on a disclosed evidence/budget basis |
| Cover bills through a date, maintain recurring obligations | `along-plan-cash`; dated per-account projection or requested obligation updates |
| Adjust budgets/rollovers, manage goal allocations or close a budget month | `along-manage-budget`; period-specific allocation changes and remaining decisions |

Evidence acquisition and scoped email access are procedures in [evidence](evidence.md) and [email](email.md), not extra workflow gates. The workflow doing the work owns its write execution through the shared protocol; categorization need not hand off to reconciliation just to save.

Honor explicit dates. For transaction review use the saved cursor plus unresolved cases; without one, state a latest-seven-days scope. For reconciliation prefer the selected statement period or resume after the last verified coverage checkpoint; otherwise state the latest complete calendar month. A checkpoint bounds discovery, not proof old rows cannot change: include requested historical checks and known replacement/repair cases. Historical reports default to the latest complete month; cash projections to 30 days. Use the household timezone, exact dates, and boundary context without silently expanding scope. A budget change with ambiguous affected months needs a decision before writes.

## Feed responsibility and allowed operations

Keep `feedOwner` (`app`, `along`, `manual`, `unknown`) separate from operation authorization. A login is source access; it does not change the producer of routine imported data. A verified handoff is required when Along becomes that producer, with competing feeds inactive. A targeted correction on a connected or user-maintained account does not require takeover.

| Operation | Required boundary |
|---|---|
| Read, compare, prepare | Requested scope and authorized access; inspection remains read-only |
| Categories, notes, tags, review status, review assignment, merchant/owner metadata | Known target, exact task authorization and observed effects; disclose material cascades |
| Splits, rules, exclusions, goal links, recurring definitions, budget/goal allocations | Concrete affected scope and side effects; obtain approval for choices inferred beyond the request |
| Create/delete records, alter amount/date/account, import or repair history/balances | Source-backed proposal, scoped authorization, duplicate/drift checks, recovery plan and verification |
| Feed/account creation, provider switch or takeover | Preview effects on history, pending activity and sibling accounts; verify the selected transition |

Unknown identity or unknown operation effects block that write, not independent work. Check every affected account and counterpart. Preserve source provenance and supported parent/child relationships rather than demanding identical app row IDs after a native split. A split may change review state or transaction counts; include those effects explicitly. One-off manual repairs create follow-up cases for later synced duplicates.

## Continuity and delivery

Reuse scoped preferences, evidence and open cases under [records](records.md). An observation is dated evidence, a preference is a household choice, and authorization permits a particular action; none implies the others. Ask only questions that affect a decision, grouped by transaction/case; allow deferral and continue independent work. One explanation of a merchant is not permission for a merchant-wide rule.

For a household check-in, summarize existing open cases, fresh-enough cash/budget findings and the smallest next actions. Run additional workflows only within the request. Preserve member visibility limits; native ownership labels are not access controls. Messages to a partner/support, schedules, bill payments, bank transfers, and subscription cancellations require their own explicit authorization and supported tools. A local case or planned next date does not establish a running monitor.

Lead with the result, scope and unresolved decisions. Keep evidence coverage, balance match, categorization, native links, feed health and applied-change verification independent. Saved status and reports are derived views. Visuals are optional and stay private; plain Markdown is complete delivery. Claim completion only for performed checks and verified changes.
