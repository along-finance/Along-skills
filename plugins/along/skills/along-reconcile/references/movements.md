# Checks by movement type

| Flow | Compare | Correct accounting and exceptions |
|---|---|---|
| Paycheck | Paystub employer/pay date/net pay and deposit allocations against bank deposits; account suffixes and settlement dates | Net pay equals the sum of actual direct deposits, including split routing. Gross less taxes and deductions must reconcile to net; deductions are not missing bank deposits. Employer is an external source, not a household cash account needing an invented counterpart. Keep reimbursements, bonuses and equity proceeds separate. Without a stub, label only the bank deposit observed. |
| Payroll benefits | Employee and employer contributions on stubs against retirement/HSA/ESPP cash or contribution records | Separate employer match, employee deductions, vesting, fees and market movement. A portfolio balance change does not prove a contribution. Avoid recording the same salary once as net deposits and again as gross income unless a complete, approved payroll representation supports it. |
| Internal bank transfer | Withdrawal and receipt across owned accounts, currency, source reference and settlement interval | Transfer principal is neither household income nor spending. Fees, if present, are separately evidenced expenses. Check both report and spending-plan settings without assuming the CSV's one exclusion field captures both. |
| Wallet transfer | Wallet cash-out/funding record and bank receipt/withdrawal; trace funding source | Separate wallet purchases/reimbursements from cash-outs. A bank-funded wallet purchase may not change wallet balance; inspect the source model before creating two cash movements. Gross cash-out = net bank receipt + fee when documented. Preserve dates; keep a local match if the app link changes them. |
| Card payment | Bank debit and card payment credit; card identity, reversals, retry attempts and posting dates | A card purchase records spending; paying the card transfers cash/reduces debt. Do not categorize both as expenses. A single card ledger credit must not satisfy two bank debits. Investigate unmatched payments outside the period before calling them missing. |
| Amortizing car/student loan | Bank cash paid and lender receipt, allocated principal/interest/fees, plus principal ledger | Cash paid = principal + interest + fees, with extra principal/credits supported by lender evidence. Principal-only receiver equals the bank principal split, not full cash payment. Beginning principal + new borrowing/capitalized amounts − principal reductions = ending principal. Keep accrued interest and payoff separate. Balance-only source updates do not prove receipt or allocation. |
| Lease | Bank payment and lessor statement/payment receipt; lease obligation representation | A remaining-rent snapshot is not amortizing loan principal or payoff. State whether rent is expensed or a lease-liability model is used. Historical receipt creation against a current snapshot would double-reduce the obligation; reconstruct a source-backed baseline before any approved backfill. |
| Brokerage cash transfer | Bank side and brokerage cash ledger | Contributions/withdrawals differ from trades, dividends and market gains. Read the investment ledger even if the general export omits it. Account valuation changes are insufficient evidence. |
| Refund | Actual receiving account and original purchase/order allocation | Use the original spending category for posted cash/card refunds. Honor household exclusions for store-credit activity; do not invent a bank refund when money returns to store credit. |

For installment financing, verify whether the original purchase and refund already enter expenses before judging payment exclusions. Existing notes describing an installment model may be stale after historical purchase reconstruction. Report double-counting risk when both purchase and repayment remain included, even if native links are correct.

A source-backed adjustment can make a balance current while payment-side accounting remains incomplete. Expose that distinction instead of declaring the whole account reconciled.

## Behavioral acceptance cases

Review the draft against these cases before changing its scope:
- Two identical transfers on adjacent days: no reused receiver; unresolved identity is shown rather than arbitrary pairing.
- Month-end bank debit and next-month receipt: match with disclosed boundary context, without changing either date.
- $928.12 cash payment and $840.60 loan principal: require $87.52 source-supported interest, then reconcile the principal leg.
- Loan principal adjustments exist while full bank payments are expenses: flag the accounting model and propose a reviewed conversion; do not add duplicate principal rows.
- Current lease snapshot and earlier payments: preserve snapshot until an opening baseline and historical model are approved.
- Paystub with two direct-deposit destinations and retirement deduction: reconcile net deposit routing separately from retirement contributions.
- Native link would synchronize dates or create a counterpart: local match stays valid; unsupported link stays unapplied.
- Existing counterpart already linked: verify it, do not repeat the mutation.
- A user-selected store-credit exclusion: the named account scope is honored; store-balance movements are not imported.
