---
name: along-manage-budget
description: Review, version and change household budgets, rollovers, allocations and goal funding for an exact period. Use for budget maintenance and month close; recurring cash belongs to along-plan-cash.
---

# Manage budgets and goals

Use this skill for period-specific household budget work: compare planned and actual amounts, maintain rollover decisions, prepare supported budget or goal allocation changes, reconcile goal funding and refunds, and run a scoped month-close review. It owns budget and allocation versions and goal cases. It does not own recurring bills or expected cash events; those belong to [along-plan-cash](../along-plan-cash/SKILL.md).

Read [workflow](../along-sync-account/references/workflow.md), [analysis basis](../along-sync-account/references/analysis.md), and [records](../along-sync-account/references/records.md). For source gaps, read the shared [evidence procedure](../along-sync-account/references/evidence.md). Load [budget operations](references/budget-operations.md) for period, rollover and allocation work, or [goals and close](references/goals-and-close.md) for goal funding, refunds and month close. Those references identify the required capability, Monarch-knowledge and write-contract dependencies; a missing dependency blocks its app-specific operation.

Budget means the shared household plan unless the current capability map proves another native model. A household cost allocation or member spending view distributes shared amounts analytically; it is not an owner filter, private account, private budget or privacy boundary. Native budget or goal allocation metadata may be changed when the exact operation is supported and authorized. This skill never executes a bank transfer or bill payment.

## Choose the mode and scope

- **Review period:** inspect one exact period's plan, actuals, rollover and goal state; read [budget operations](references/budget-operations.md).
- **Prepare changes:** build a versioned proposal for budget amounts, groups/categories, rollover treatment, allocation preferences or goal links; read [budget operations](references/budget-operations.md).
- **Goal funding:** reconcile planned allocation, evidenced funding, goal-linked use and refunds; read [goals and close](references/goals-and-close.md).
- **Month close:** orchestrate only the requested checks and proposals for one exact period; read [goals and close](references/goals-and-close.md).

Use the shared execution modes **inspect**, **prepare** and **apply**. “This month” means the current calendar month in the selected household timezone; state its start and end dates. Otherwise resolve an exact period, currency, native budget type, app workspace, group/category or goal IDs, owner scope, allocation view and as-of time before doing dependent work. Ambiguous affected months or identities block a write. Historical “why” questions belong to `along-report-money`; future cash questions belong to `along-plan-cash`.

## Shared execution rules

1. In `inspect`, calculate and report the requested effect without changing the app. Use the selected period and compatible actuals; do not turn an inspection into a broad reconciliation.

2. In `prepare`, record stable change IDs, exact period and native type, targets, current and proposed values, original monthly values, rollover assumptions, downstream effects, evidence, uncertainty and excluded questions. Show a concise before/after view and household totals.

3. In `apply`, follow [changes](../along-sync-account/references/changes.md). An exact user instruction naming the records, values and intended effects can authorize that exact operation; broad requests or agent-chosen allocations require a concrete proposal and approval. Do not ask for redundant approval when the exact request already supplies authorization. Re-observe the workspace and before-values, stop on drift, apply only supported metadata changes, and verify affected budget, group/category, rollover and goal views.

4. Unsupported or unknown native operations remain proposal-only. A local analytical allocation can be saved as a scoped household preference when explicitly chosen, but it must remain labeled local. Preserve superseded versions and open cases; do not create a second bills registry or replay an old proposal against changed state.

## Completion

- **Inspect:** the exact period, budget scope, basis, version, rollover and goal state are stated, with supported results and explicit gaps.
- **Prepare:** every requested change has stable identity, before/after values, original monthly values, impact, evidence and unresolved choices.
- **Apply:** only exact, supported, authorized changes were made and their after-values and effects were verified; unsupported operations remain proposals.
- **Month close:** the period version and coverage are preserved, the next-period decision or explicit no-change result is recorded, and unresolved cases are carried forward with owner, evidence, status and next action.

Save budget versions, allocation preferences and goal/refund cases under the selected private root according to [records](../along-sync-account/references/records.md) when storage is established or the user requests a saved result. An inline supplied-file inspection can finish without creating private storage. No completion state authorizes a bank transfer or bill payment.
