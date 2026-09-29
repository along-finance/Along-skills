# Budget period and allocation operations

Load this reference for period reviews, budget changes, rollover decisions and analytical household allocations. The entrypoint has already loaded the shared household, analysis and records contracts. For native app interpretation or edits, read [capabilities](../../along-sync-account/references/capabilities.md), applicable [Monarch knowledge](../../along-sync-account/references/monarch.md), and [changes](../../along-sync-account/references/changes.md); if a required app reference is missing, stop the dependent operation and report the incomplete installation.

## Resolve the period and version

1. Resolve the household timezone, exact period start and end, currency, native budget type, app workspace, group/category IDs, owner scope, allocation view and execution mode (`inspect`, `prepare` or `apply`). “This month” means the current calendar month in that timezone. Do not write when affected months or group/category identity is ambiguous.

2. Load the budget version applicable to the period. Preserve native IDs, group/category hierarchy, original monthly values, later adjustments, rollover setting, version timestamp and effective interval. A plan revision is a new version with its reason; never overwrite the original monthly value. If the first observation is mid-period and no historical version or evidence exists, mark the original monthly value unavailable; the current observed value is not automatically the original plan. If native semantics are undocumented or unobserved, preserve the value and mark its interpretation uncertain.

3. Gather compatible actuals for the same period: posted spending, evidenced refunds and reimbursements under the household basis, and any supported goal or transfer treatment. Keep pending activity separate. Card payments and internal transfers are cash movements, not purchase spending. An expected refund is not available budget or cash until observed.

## Show before and after effects

Compare the original plan, current version and actuals when useful. Show, using the app's observed rollover semantics:

- opening carry-in or rollover;
- original monthly plan and approved adjustments;
- eligible spending, refunds and reimbursements;
- closing carry-out or remaining amount; and
- effects on the parent group, affected categories and later periods.

Explain whether each variance comes from activity, a plan revision, rollover, goal treatment, a refund or missing evidence. Do not force a residual into a category. A native rollover toggle, debt-payment setting or goal-expense option requires capability inspection; unknown effects remain an explicit limitation.

## Household allocations

Keep transaction owner, account owner, review responsibility and cost share separate. A cost allocation distributes a shared household amount by an explicit preference; it does not filter the budget by owner or create a private account, private budget or privacy boundary. Preserve the household total and show analytical parts separately. For example, a 50/50 allocation of a $100 shared expense produces two $50 analytical shares while household spending and the household budget remain $100.

An allocation preference may be stored as a scoped household preference with its effective period and confirmation. It must conserve the shared amount, remain distinguishable from native owner fields, and never become authorization for a future app write.

## Budget-specific change details

Use the entrypoint's shared `inspect`, `prepare` and `apply` modes and [changes](../../along-sync-account/references/changes.md). A budget proposal must retain the exact period and native type, group/category or goal IDs, original and proposed monthly values, rollover assumptions, downstream period effects, evidence, uncertainty and excluded questions. Show household totals and the parent/group effects of the change.

Before applying, re-observe the affected budget, group/category, rollover and goal views and verify their after-values. If native semantics or side effects are unknown, leave the operation proposal-only. Native app allocations are metadata changes; the shared workflow never executes a bank transfer or bill payment.

Preserve superseded versions and unresolved cases. A later revision is a new operation against current state, not a replay of an old snapshot. Save budget versions, allocations, evidence and journal references under the selected private root according to [records](../../along-sync-account/references/records.md).
