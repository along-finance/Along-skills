# Provided-source reconciliation

## Prompt

> Reconcile the synthetic provided-source files at
> `inputs/provided-source-csv-only/` for the checking account and report findings
> only. That private test directory contains only `bank_transactions.csv` and
> `app_transactions.csv`; do not open or rely on `expected-reconciliation.json`
> or any other fixture. Do not sign in, use a browser, import anything, edit an
> app record, or create a persistent household profile. Match the two CSVs by
> stable IDs and the supplied fields. Treat a same-account, same-group pending
> row followed by a posted row with the same merchant and amount as a possible
> source supersession; decide from the CSVs whether it should be counted once.
> Report the four matched pairs, the source-only `$80.00` row, the app-only
> `$22.00` row, the pending-to-posted replacement, and the `$100.00` split parent
> with its conserving children. The requested interval is 2026-09-01 through
> 2026-09-30, and the declared source interval supplied with this request is
> also 2026-09-01 through 2026-09-30; report those separately from observed row
> spans and do not infer full source completeness from the minimum and maximum
> dates present in the rows.

## Expected observation

The response should identify the supplied-file route as `provided-source`, keep
source completeness separate from app-only findings, preserve the two identical
coffee amounts as distinct transactions, and explain the split parent/children
without double-counting the children. It should distinguish the requested and
declared interval from the observed 2026-09-10 through 2026-09-20 row span rather
than treating row dates as proof of coverage. No sync or app mutation is implied.
