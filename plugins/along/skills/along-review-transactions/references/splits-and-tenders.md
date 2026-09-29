# Splits, receipts and tenders

Use this reference only when a transaction needs receipt-backed allocation, a mixed tender, a partial receipt, a return or a credit. The transaction review skill owns the proposal and any approved native write.

## Resolve the parent

Identify one existing app transaction by its app/source identity and account mapping. Corroborate with signed amount, currency, posting status, date, merchant and original description. If the receipt covers several charges, map each charge to its own parent; never copy the whole receipt to every tender. A split parent and its allocation children count once for account totals.

Use [exact calculation checks](../../along-sync-account/references/calculations.md) for conversion, split conservation and proportional allocation. Use integer minor units and the currency exponent. Keep the app's signed direction. Require this exact conservation check:

```text
sum(split.amount_minor) == parent.amount_minor
```

For a receipt with several tenders, first identify the amount charged to the selected parent. Allocate only that amount. If an item cannot be assigned to a tender, ask for the household convention, use an explicitly requested proportional allocation, or leave the line unresolved. Do not invent another tender's ledger row.

For proportional allocation, compute truncated base shares, distribute the signed rounding residual to identified lines using a stated deterministic rule, and report that distribution. Verify `sum(base_shares) + total_residual == parent.amount_minor` before distribution and `sum(final_shares) == parent.amount_minor` after distribution; never add the residual a second time.

Taxes, tips, shipping, discounts, credits, returns and partial receipts are separate lines or explicitly explained adjustments. A mismatch from rounding, foreign exchange, a tip or a partial receipt remains unresolved until evidence or user context explains it.

## Preserve relationships

Keep original source identity, account, date and sign. Do not move dates or turn a transfer or card payment into spending to make a receipt balance. If the app represents a split as independent children, save the parent-to-child identity map and avoid counting both. If a native split changes review state, creates rows, changes exclusions or otherwise has a side effect, include it in the proposal and rely on [Monarch knowledge](../../along-sync-account/references/monarch.md) and live capability observation rather than an assumption.

## Proposal minimum

Include target account and transaction identity, original signed amount/currency/category, match basis, evidence references, each split line's signed minor-unit amount and category/item rationale, `supported` or `unresolved` state, the exact sum check, assumptions, questions, duplicate guard and expected app side effects. Report a proposal as complete only when the parent, evidence and arithmetic are clear; otherwise preserve the unresolved remainder and stop at `partial`.

