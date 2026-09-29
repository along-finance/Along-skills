---
name: along-plan-cash
description: Project cash coverage and maintain recurring obligations. Use for bills, paydays and account liquidity; historical explanations go to along-report-money, budget/goal changes to along-manage-budget.
---

# Plan upcoming cash

Use this skill for two related future-cash jobs:

- **Forecast:** determine whether selected accounts cover listed bills and other cash events through a date.
- **Maintain obligations:** create or revise user-owned recurring obligations, compare expected and actual settlement, and carry the result into later forecasts.

Read [workflow](../along-sync-account/references/workflow.md) and [analysis basis](../along-sync-account/references/analysis.md). Read [records](../along-sync-account/references/records.md) before saving. For source gaps, read the shared [evidence procedure](../along-sync-account/references/evidence.md). For obligation maintenance, load [obligations](references/obligations.md), which names the additional required capability, app-knowledge and write-contract references.

Forecast mode is read-only and does not pay bills, send transfers, change connectors or schedule unattended checks. A full account reconciliation is not required when the opening balance and in-scope events are adequate for the requested scenario. Native recurring maintenance and its write boundary are defined in [obligations](references/obligations.md).

Budget amounts, category allocations, goal funding and month close belong to [along-manage-budget](../along-manage-budget/SKILL.md). Historical spending or cash explanations belong to [along-report-money](../along-report-money/SKILL.md). Account corrections and completeness work belong to [along-reconcile](../along-reconcile/SKILL.md).

## Choose the mode

- Use **forecast** for “Can this account cover the bills?”, “How low will checking get?”, or “How much room is left before payday?”
- Route **maintain obligations** requests such as “Add this bill,” “This recurring amount changed,” “Mark this bill paid,” “Stop suggesting this subscription,” or “Why did the expected bill not match?” to [obligations](references/obligations.md).
- If both modes are requested, complete the obligation review first, then forecast from the resulting version while preserving the previous version for comparison.
- A category budget or goal allocation belongs to `along-manage-budget`; it is not an obligation update or a cash event.

## Forecast cash coverage

1. Resolve the household, selected cash account(s), currency, timezone, starting as-of, and horizon. Reuse established choices. “Until payday” means through the next confirmed payday, with pre-payday and payday effects shown separately; ask for the date if it is unknown. For an otherwise unspecified horizon, state a 30-day default. Ask only for missing choices that materially affect the result, such as account selection or the reserve to retain.

2. Establish each opening balance's identity, amount, definition, source and timestamp. Reuse evidence only when it fits this as-of; perform live access only under the shared runtime and authentication contract. Align the opening cutoff with later events so transactions already reflected in it are not replayed. If available balance includes holds or the cutoff is unclear, resolve the overlap or label the scenario provisional. An old or uncertain balance supports an explicitly dated scenario, not a current assurance.

3. Assemble only relevant future cash events: net deposits, maintained obligations, bills, credit-card payments, loan payments, known spending allowances and user-planned transfers. For each event, record account, amount or defensible range, currency, expected cash date, due date when different, evidence or user context, and state (`confirmed`, `estimated`, `unknown`, or `settled`). When a card or loan payment could be the minimum, statement, installment or another amount, record the user's choice when it changes the outcome; a statement balance is not automatically the amount due in cash. A payday or planned transfer is a cash event, not a budget allocation. Historical repetition can suggest an estimate or a question; it does not confirm a bill, payday, amount or recurrence. An unconfirmed incoming transfer is not guaranteed cash. Keep unquantified obligations visible outside the numeric subtotal.

4. Match repeated representations of the same event before calculating. A statement, calendar entry, obligation and expected payment may describe one cash event. On a revised run, match settled activity to the obligation and the new opening balance before removing or retaining it. Preserve prior plan versions. Represent a planned transfer on each affected account with one shared reference; do not count a card purchase as another checking withdrawal when its card payment is already included.

5. Calculate in integer currency minor units, separately per account and currency. For each event, `projected_balance = preceding_balance + signed_cash_event`; derive the closing balance and the lowest balance across the whole horizon, including the opening balance. A loan event uses the full expected cash withdrawal even when principal and interest are analyzed separately. Where same-day ordering is unknown, show the conservative low with outflows before inflows. Use stated amount/date bounds for scenarios; uncertainty without a defensible bound cannot produce a guaranteed minimum.

6. Lead with coverage through the selected date, the lowest projected balance and date, and any shortfalls. Show a compact dated event/balance table and the decisive assumptions. Compare the minimum with the user's reserve. If additional spending is requested, compute headroom from the minimum after that spending date, less the reserve, and label it conditional on the listed events and assumptions. Unknown obligations or an unknown reserve preclude a definite spendable amount; report the known-event projection and the focused missing question instead. Negative headroom is a shortfall.

## Save and finish

Use the private records contract in [analysis basis](../along-sync-account/references/analysis.md#saved-analysis) and [records](../along-sync-account/references/records.md). Save an immutable cash-plan snapshot with opening balances, event and obligation IDs, evidence, cutoffs, deduplication choices, reserve, ordered projections, scenarios, assumptions and unresolved items.

Forecast completion means the requested accounts and horizon are represented, each in-scope event is included once or explicitly unresolved, calculations are checked, and limitations are clear. A finished scenario is not verification of all future finances. Keep recurring record completion with [obligations](references/obligations.md), budgets and goals with `along-manage-budget`, and historical actuals with `along-report-money`.
