# Maintain recurring obligations

Load this reference for requests to add, revise, dismiss, settle or investigate a recurring bill or other user-owned future cash obligation. The entrypoint has already loaded the shared household, analysis and records contracts. For native app interpretation or edits, read [capabilities](../../along-sync-account/references/capabilities.md), applicable [Monarch knowledge](../../along-sync-account/references/monarch.md), and [changes](../../along-sync-account/references/changes.md); if a required app reference is missing, stop the dependent operation and report the incomplete installation.

An obligation is a user-owned expectation about a future cash event. It is not proof that a payment happened, that a native recurring item exists, or that money is available. Cash planning owns these records. Budget categories, allocations and goal funding belong to `along-manage-budget` and must not create a second bills registry.

## Maintain the record

1. Resolve the household, account, currency, timezone and obligation identity. Reuse a stable `obligationId`; a changed merchant description, source transaction ID or expected date does not by itself create a new obligation. Preserve explicit dismissals, cancellations and “do not suggest again” decisions with their scope, confirmation and date. Dismissing a suggestion or removing a native recurring item does not cancel the real bill; keep suppression preferences separate from the obligation's evidenced active/canceled state.

2. Read the current obligation version and record the fields needed for a forecast: payee or purpose, paying or receiving account, native recurring ID when present, cadence or one-off basis, due date, expected cash date, amount or lower/likely/upper range, currency, evidence, confidence, user confirmation, and active/canceled state. Keep due date and expected withdrawal date distinct. Variable bills remain variable; do not replace a range with a falsely precise average. If no defensible bound exists, keep the obligation visible as unknown and exclude it from a guaranteed minimum.

3. Create or revise the obligation version in the selected private root according to [records](../../along-sync-account/references/records.md). Preserve prior values, effective dates, reasons, evidence and supersession. A changed amount, account, date rule or cadence affects future forecasts; show that effect. Do not silently learn a permanent merchant-wide rule from one changed payment.

## Match expected and actual settlement

1. For each occurrence, preserve the expected amount/date bounds and link any observed posted or settled activity by source ID or a documented fingerprint plus account, date and amount evidence. Match an actual settlement once. Do not overwrite the expected date or amount.

2. Record early, late, partial, over, under, settled, missed, duplicate, changed, canceled or unresolved disposition. A partial payment leaves the remainder open. A native missed marker or absent match is a finding to investigate, not proof that the bill was unpaid. A canceled obligation that still settles becomes an open exception; do not delete history.

3. If a follow-up is needed to detect a later synced row, create a `manual-repair-watch` or related case with evidence and next action. A local case is not an unattended reminder and does not authorize a future deletion or duplicate cleanup.

## Native recurring edits

Inspect the operation and its side effects before any app write. A user instruction that names the exact recurring item, fields, account and intended result can authorize that exact operation under [changes](../../along-sync-account/references/changes.md); record the before/after plan and user-message reference without asking for redundant approval. A broad request or an inferred change requires a concrete proposal before applying.

Apply only supported, known effects through the shared inspect → prepare → apply protocol and verify the saved item. If native behavior is unsupported or unknown, keep the native edit proposal-only. Save confirmed real-world bill changes or explicitly chosen local expectations separately from proposed app values; a failed app edit must not appear as observed native state. Never execute the underlying bill payment, bank transfer or connector change. Native recurring representation does not prove settlement.

## Finish

Report the current obligation version, expected-versus-actual occurrence dispositions, changed or unresolved items, and effect on the next forecast. Save immutable versions and occurrence references under the selected private root; do not store household facts in the skill folder or create a second ledger. Completion means every requested record has a stable identity, current fields and a settlement disposition or explicit gap, and any native edit is verified or clearly left as a proposal.
