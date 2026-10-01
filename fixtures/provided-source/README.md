# A reconciliation example with sample data

These small, synthetic files show what Along's reconciliation checks are intended to distinguish. You can read them before installing Along or signing into a finance app. This is a worked example, not a setup-free mode for running Along skills.

- [Bank transactions](bank_transactions.csv): six source rows.
- [App transactions](app_transactions.csv): seven app rows, including split children.
- [Expected reconciliation](expected-reconciliation.json): the machine-readable expected result used by validation.

The example concerns September 2026, account `checking-001`, in USD. Negative amounts are outflows.

| Case | Expected finding |
| --- | --- |
| Two Coffee House purchases of $12.34 | Both are real purchases with distinct IDs. Match each separately; do not remove one just because the amounts and dates agree. |
| Utility Co, $80 | Present in the bank data, missing from the app data. Flag for investigation. |
| Unknown Merchant, $22 | Present in the app data without a source match. Flag it; absence from these source rows alone does not justify deleting it. |
| Internet Co, $45 | A pending row was replaced by a posted row. Match the posted transaction and avoid counting the pending version again. |
| Home Store, $100 | The app splits this into $60 and $40. The children sum to the parent; do not count the parent and children together as $200 of spending. |

Expected totals: four source/app matched pairs, one source-only row, one unmatched app row, one pending replacement, and two split children. The observed dates span September 10–20; they do not establish complete coverage of September or prove balance agreement.

These are illustrative fixture expectations, not evidence of live finance-app compatibility. To use Along on your own records, follow the [normal setup flow](../../README.md#first-use).
