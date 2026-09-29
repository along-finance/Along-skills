# Refunds and reimbursements

Keep merchant refunds, card reversals, rewards, store credit and household reimbursements as distinct cases. Amount similarity alone does not establish a relationship.

## Model the relationship

Represent relationships by references to existing purchase and credit records. A purchase may have many partial refunds; one refund may allocate across several purchase lines; one household reimbursement may repay several purchases; and one purchase may be reimbursed by more than one payer. Record each allocation in integer minor units with the source account, signed amount, date, evidence and confidence. A row may participate in one relationship map without sharing a source row ID with its parent.

For each posted credit, require:

```text
credit.amount_minor == sum(allocated_offsets) + unallocated_remainder
```

The remainder must be visible and explained. For a purchase with multiple credits, compare the cumulative allocation with the evidenced refundable amount and identify return fees, shipping, tax differences or over-refund exceptions. Do not offset a category twice. For a reimbursement across purchases, allocate the payer's exact amount once and preserve any unapplied remainder as a question; do not create a synthetic purchase or receiving account.

Refunds normally offset the evidenced original spending category, including its split allocations. A reimbursement follows the household's recorded treatment and payer context; it is not automatically a merchant refund or income. A card reversal, cashback reward or store-credit return follows its own documented treatment. A credit that returns to store credit is not a bank inflow.

## Track expected money

Keep an expected refund or reimbursement separate from posted cash. Use case states `expected → partial → resolved` when receipt is complete; `disputed` remains open and `abandoned` requires explicit user disposition. Record basis, related purchase references, payer or merchant, expected amount, expected and observed dates, received amount, evidence and next action. Never include an expected credit in available cash until supported by the observed receiving balance/activity cutoff. A supported expected date/amount may enter an explicitly conditional forecast, not current available cash.

An original purchase outside the requested period may be read to identify a refund relationship, but that context does not authorize editing the older row. A posted credit can be categorized in transaction review; a missing expected credit or an unexplained extra credit belongs in [along-reconcile](../../along-reconcile/SKILL.md) when source completeness is in question.

