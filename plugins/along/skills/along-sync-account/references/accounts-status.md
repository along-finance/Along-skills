# Account status mode

Default “status” to **saved status**: derive a compact view from the selected household's registry, observations, evidence index, reconciliation results and action history. Read [workflow](workflow.md) for identity, [records](records.md) for the status contract, and [capabilities](capabilities.md) when an app field or feed state needs interpretation. A status answer does not require an institutional login or a full evidence fetch.

## Saved and fresh status

1. For saved status, use the latest applicable observations and show their observation dates. Preserve independent timestamps: `lastLoginObservedAt`, `connectionTestedAt`, `appInspectedAt`, `balanceObservedAt` with balance type/as-of, `evidenceRetrievedAt` and `reconciledAt`. A fresh login, app inspection or balance does not refresh the other dimensions. Missing means unknown; it does not mean zero, healthy or complete.
2. A request for “current,” “refresh,” or “check now” authorizes a scoped read-only app inspection only for the named household/account set. It does not authorize signing into every bank, triggering connector refresh/import controls, opening email, repairing transactions or changing feed ownership. Read [authentication](authentication.md) before any live app inspection; source-institution access additionally needs the selected source-check or recovery scope.
3. Represent active, closed, manual, source-only and unresolved mappings without counting one physical account twice in household totals. Use exclusive inventory buckets: closed, Along-managed with verified handoff, app-managed, other manual, and unknown. Show feed errors and pending handoffs as labeled subsets; show confirmed source-only accounts separately from app inventory totals and suspected accounts outside confirmed totals. Deduplicate joint accounts and multiple app mappings explicitly.

## Lead with dimensions and exceptions

4. Show, for each relevant account, the smallest useful table: masked identity and owner, app mapping, `feedOwner` and handoff state, last observed connection health, evidence coverage/as-of, balance observation, verified sync coverage from sync checkpoints (or unknown), reconciliation basis/period/result, category-review state when available, and the smallest next action. Keep source access separate from app-reported feed health. A working login is not current evidence, and a matching balance is not verified transaction history.
5. If a fresh app inspection shows a stale/erroring feed, report the observed symptom, timestamp and affected account, then offer the relevant recovery action; only a requested recovery routes to [connection procedure](accounts-connections.md). The status run itself does not repeatedly refresh, reauthenticate, import, delete duplicates or add a manual replacement. Missing transaction details require [evidence](evidence.md) and `along-review-transactions`/`along-reconcile` within their scopes.
6. When action history is requested, derive a chronological view from private run journals: time, account, mode, requested scope, authorized/applied/verified counts (including legacy approved states), partial/unknown outcomes and links to proposal, journal and evidence. Distinguish read-only observations and recommendations from applied changes. Do not copy private artifacts into a public report.

## Save and finish

If the user asks to save status, write a timestamped derived snapshot with mode, scope, source references, independent observation dates, per-account dimensions, gaps and next actions. It is not a new verification of the referenced facts. Do not create empty evidence or “healthy” records for checks not performed.

Status is complete when every known in-scope account is represented or explicitly missing, counts reconcile, dates and evidence provenance are visible, and each material exception has a smallest next action. A stale feed can be a complete status result with an unresolved recovery action; do not hide the exception to make the status look healthy.
