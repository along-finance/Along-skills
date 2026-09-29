# Exact calculation helper

Use [finance_checks.py](../scripts/finance_checks.py) for exact money conversion, receipt split checks, proportional allocation and dated cash projections. It is a local, standard-library Python 3.10+ helper: JSON on stdin, result on stdout, validation errors on stderr with exit code 2. Run `python3 <resolved-script-path> --help` for commands. The caller supplies the source meaning, currency exponent, scope and evidence; a successful calculation does not validate those facts.

| Command | JSON input |
|---|---|
| `minor` | `{"amount":"12.345","exponent":3}` returns integer `amount_minor`. Use decimal strings, not floats. |
| `split` | `{"total_minor":-10000,"parts_minor":[-4000,-6000]}` checks exact conservation. For evidenced mixed-sign discounts/returns, explicitly set `allow_mixed_sign:true`; the helper does not prove the adjustment's purpose. |
| `proportional` | `{"total_minor":-101,"weights":[1,1],"residual_index":1}` uses integer weights and discloses the signed residual assigned to a zero-based line. Explain the allocation convention to the user. |
| `cash` | `{"openings":[{"account_id":"checking","currency":"USD","exponent":2,"as_of":"2026-09-27","balance_minor":5000}],"events":[{"event_id":"bill-1","account_id":"checking","currency":"USD","exponent":2,"date":"2026-09-28","amount_minor":-6000}]}` returns separate account/currency event balances, closing and minimum amounts/dates. |

For cash input, remove transactions already reflected in the opening balance, bound events to the requested horizon, deduplicate repeated representations, and include each known obligation once. A date-only opening cannot itself distinguish earlier from later same-day activity. Use unique event IDs for each account leg, with shared transfer references maintained by the caller. Supply an integer `order` only when same-day ordering is established; otherwise the helper conservatively processes outflows first. Represent ranges as explicit bounded scenarios; unknown/unquantified events remain disclosed outside the numeric result.

The helper neither predicts counterpart transfers nor converts currencies. Its minimum is conditional on supplied events, not proof all bills are covered. Use the sequence to calculate headroom after a proposed spending date; the global minimum may be earlier. If execution is unavailable, an alternative exact calculation may support the answer, but do not claim this helper ran.

Synthetic behavior checks live in [test_finance_checks.py](../scripts/test_finance_checks.py). Run `python3 -B -m unittest discover -s <scripts-directory> -p 'test_*.py'` after changing the helper.
