# Shared basis for plans and reports

Use this reference for cash forecasts, historical reports, and budget/goal impact calculations. Follow [workflow](workflow.md) for household identity, runtime and permissions, and [records](records.md) for private storage, provenance, currencies and versioning. These calculations derive answers; they do not change feed ownership or confer financial-write permission. Requested obligation or budget edits separately follow the shared changes contract.

## Evidence and access

Resolve the selected household/account identity and source scope before combining records. Load its `appKnowledgeRef` when available. Supplied-file work can proceed with explicit file/account labels and coverage without live setup; use existing household storage for persistent records or the task workspace for standalone output; missing household configuration follows the workflow’s explicit setup boundary. Missing live access blocks only dependent live work, not analysis of adequate saved or supplied evidence. Before live access, read [authentication](authentication.md), follow the workflow's runtime check, and inspect the relevant [capabilities](capabilities.md). A report request does not authorize unrelated bank logins, feed refresh/import controls, or mailbox searches.

Use source IDs or supported fingerprints with duplicate ordinals and provenance to resolve export overlaps. Retain genuinely separate equal-value purchases; uncertainty about identity remains a gap. Label source-verified, app-observed and user-provided inputs separately. A reconciled historical period does not make a current balance fresh. Timestamp and scope inherited verification rather than upgrading it.

For exact money conversion and dated cash arithmetic, use [calculation checks](calculations.md).

## Accounting basis

- **Purchase spending / income:** use the household's supported expense/income treatment, normally posted purchases and income, with refunds offsetting the evidenced original expense category. Card repayments and internal transfers are not new spending/income. An external payment is not internal merely because its label says transfer; unresolved cases remain visible. Separate evidence-backed principal, interest and fees where the question needs that breakdown.
- **Cash movement:** define the selected cash-account boundary. Count actual or planned cash inflows/outflows on their cash dates, including card and loan payments. Transfers between two selected cash accounts cancel in the aggregate but affect each account; transfers to savings/investments outside the boundary affect selected cash without becoming household spending. Missing counterpart evidence remains unresolved rather than a fabricated matching row.
- **Spending surplus:** selected income minus selected expenses under the stated basis. It is not a bank balance or proof of increased cash/net worth. Name a savings-rate numerator/denominator explicitly; transfers, employer contributions and market gains do not silently become take-home income or spending.

Use one sign convention per measure, preserve raw signs/directions, and calculate in integer currency minor units with the actual currency exponent. For category detail, use allocation children instead of the split parent; for account totals, count the source transaction once. Keep reported pending items separate from posted activity; an initial forecast need not model pending transactions, but disclose omitted items or unclear balance holds when they limit coverage. Never claim complete cash availability from an unexplained balance definition.

Compare balances only at aligned dates and with compatible definitions. A change in investment valuation is not reconstructible from deposits/withdrawals alone. A cash bridge residual stays unexplained until evidenced; do not force it into income, spending or a balancing adjustment. Separate native app presentation from an analytical view when they differ.

Keep currencies in separate totals by default. If conversion is requested and supportable, retain original amounts, rate source/date, valuation policy, rounding and converted values; distinguish historical transaction conversion from point-in-time balance valuation. Missing exchange evidence limits the converted result, not the valid per-currency report.

## Saved analysis

Use established private household storage; never store runtime financial records inside skill folders. Add directories only when saving an actual run, without migrating existing records:

- `plans/cash/<runId>/`: `plan.json`, `SUMMARY.md`, `verification.json` and an optional private presentation.
- `reports/money/<runId>/`: `report.json`, `SUMMARY.md`, `verification.json` and an optional private presentation.

Each structured result includes the operational fields in [records](records.md): schemaVersion, runId, household/account IDs, scope/period/as-of, observation times, outcome, evidence references and remaining work. Add `basis`, input coverage/provenance, assumptions, calculation references and optional `supersedesRef`. Preserve prior snapshots and reference source records rather than copying them into a competing ledger. Save calculations with row/event IDs so totals can be reproduced; verification records actual checks, not a generic “passed.”

A cash plan additionally stores opening balance definitions/cutoffs, dated event IDs with state and evidence, reserve, projections/scenarios and unresolved obligations. A money report additionally stores query/filter semantics, selected measures/periods, included/excluded/unresolved record references, budget-version references when used, results and residuals. Preserve household purchase spending separately from native budget actuals: goal-funded spending may be excluded from Monarch budgets while still being an actual purchase. Goal adjustments and allocations are not automatically income, spending or bank movements. Household cost allocations must conserve the household total; owner filters are not cost-share calculations. These are derived run snapshots, not standing authorizations or a master transaction ledger. Reference the versioned obligations, occurrences, cases and budget records in [records](records.md); cash planning owns obligation maintenance and budget management owns allocations.

If no private root is established and the user only needs an inline answer, provide it with evidence labels and limitations; do not require onboarding or create persistent household records merely to answer. Save private artifacts only in the selected storage and share them only as authorized. A visualization is optional; plain text or Markdown remains a complete delivery format.
