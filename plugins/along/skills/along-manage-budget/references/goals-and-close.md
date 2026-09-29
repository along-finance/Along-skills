# Goal funding and scoped month close

Load this reference for goal allocation, funding reconciliation, refunds or a month-close request. The entrypoint has already loaded the shared household, analysis and records contracts. For native app interpretation or edits, read [capabilities](../../along-sync-account/references/capabilities.md), applicable [Monarch knowledge](../../along-sync-account/references/monarch.md), and [changes](../../along-sync-account/references/changes.md); if a required app reference is missing, stop the dependent operation and report the incomplete installation.

## Reconcile a goal without collapsing distinct facts

Track these separately:

1. **Planned allocation:** the budget amount or household preference assigned to the goal for a period.
2. **Observed funding:** an evidenced posted transfer or other supported funding event, with source account, date, amount and currency. A planned transfer is not funding.
3. **Goal-linked use:** the purchase or expense relationship, budget period and app treatment. A transfer is not spending; a goal expense may be presented differently from ordinary budget actuals. For Monarch, consult the dated goal behavior in `monarch.md` and the household capability observation before interpreting the native view.
4. **Refund or reimbursement:** the actual return, original purchase or allocation, partial amount and period. Preserve the original expense and relationship; an expected refund does not restore a goal or budget amount until observed and supported by the household policy.

Match each side once using stable app/source IDs or documented fingerprints plus account, date and amount evidence. Keep cross-period relationships visible. If native goal linking creates counterpart rows, changes dates or review state, or has another effect outside the permitted scope, retain the local evidence-backed relationship and leave the native operation proposal-only. Never manufacture a funding or refund transaction to make a goal balance.

Native goal allocation metadata can be changed when the exact operation is supported and authorized. It does not execute a bank transfer. A request to move money between accounts or pay a goal is outside this workflow and must remain unexecuted.

## Run a scoped month close

Month close is orchestration for one exact period, not a blanket audit and not a claim that the app has a native close-books operation.

1. Preserve the final observed budget version, actual coverage, rollover state and goal/refund cases for the period. Record what is posted, pending, missing or provisional.
2. Review only the requested variances. Mark which are explained, need a handoff to `along-review-transactions` or `along-reconcile`, or need a budget/goal proposal. Do not close an unresolved case merely because the period ended.
3. Prepare the next period's budget version with explicit changes, original values and rollover effects. Carry open cases forward with owner, evidence, status and next action. Do not create duplicate recurring obligations; `along-plan-cash` owns those records.
4. Apply only exact, supported, authorized app changes through the shared protocol and verify them. If no supported native close operation exists, save a local close record and state that the native period remains unchanged.

Save the period version, goal/refund cases, next-period decision or explicit no-change result, and remaining work under the selected private root. A close is complete only when the period scope and evidence coverage are stated, unresolved cases are carried forward, and any applied native changes are verified.
