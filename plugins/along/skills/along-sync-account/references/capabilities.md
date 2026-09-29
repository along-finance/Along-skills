# Observe app behavior

Record app/edition/version when visible, workspace, relevant settings, observation time/method and evidence. Tools must actually be available. Quicken Desktop, Simplifi, Monarch and other apps have separate semantics; an app-neutral workflow is not a compatibility claim. User-supplied exports can support comparison without live access.

## Public knowledge versus private observations

For Monarch start with [dated product knowledge](monarch.md). For another app, search and open its official documentation for the operation in scope. Use public product terms without household details. Record URL/title, retrieval date and available update date, applicable edition/account type/settings, rule, implication and unresolved questions. A search snippet or community guess is not product documentation.

Use the selected household's saved `appKnowledgeRef` for settings and live observations. Documentation is `documented-unverified` until the needed behavior is corroborated; store contradictions separately. Recheck official pages when the operation/version/settings change, a source conflicts, or current behavior is uncertain. Preserve earlier observations. A documentation refresh does not refresh balances or feed health. Inspect only topics relevant to the current job; setup need not research every future feature before becoming useful.

## Inspect the operation's effects

Classify the capabilities needed now as `observed`, `documented-unverified`, `unsupported`, or `unknown`. Inspect controls without saving; an unapproved live mutation is not a capability test. Product support does not authorize an operation. Before writes, identify:

- Exact targets, editable fields, native IDs and source identity; any parent/child transformation or recreated rows.
- Amount/date/account/currency effects, count changes, balances, category totals and pending/posted behavior.
- Review-state, owner, notes/tags, rule, merchant/recurring, exclusion and goal-budget side effects.
- Counterpart creation/deletion, date synchronization or cascades beyond the selected account.
- Confirmation/asynchronous completion, reliable post-save reads, export/backup and actual recovery limits.

The write protocol evaluates the complete operation. Supported native splits may change row IDs and review state; preserve source correspondence and totals rather than assume unchanged IDs/counts. Retain local evidence relationships when native links are unavailable or exceed scope. A limitation in one operation need not block another.

## Evidence and balance models

Determine whether connected balances are bank-reported or computed from transactions; distinguish current/available/statement balances, pending holds, opening adjustments and source as-of dates. A matching bank-reported balance does not prove complete transaction history. Compare compatible date/currency/sign/definition only. Cash, card debt, loan principal/accrued interest/payoff and investment valuation require different equations.

Inspect export coverage, filters, date meanings, identifiers, split/hidden rows, separate investment views and source lookback limits. Identify pending-to-posted replacement and deleted/re-added records. A full-looking export or a successful refresh need not recover old missing history. Backfill against an already-current opening adjustment requires baseline reconstruction to avoid double-counting.

For imports record supported file schema, exact mode, scope/overlap behavior, ID matching, balance effects, expected rows and verification. In particular distinguish update-by-ID from replacement-by-date-range and append/import-all. The reviewed file must represent the complete intended effect, not just desired new rows.

## Connection recovery and ingestion ownership

Inspect official refresh/reauthentication/recovery options for the selected feed. A refresh that can ingest transactions is an operation, not saved-status inspection; use only within a requested recovery/update scope. Diagnose filters, sync lag and history limits before recommending connector replacement.

For provider switches or takeover, establish account-level versus sibling-connector effects, history retention, duplicate/re-import windows, pending items and baseline behavior. A disconnected UI session is not evidence the feed is inactive. Routine Along ingestion requires verified identity/mapping and no competing producer. Keep source-access success, native feed state and verified handoff independent.
