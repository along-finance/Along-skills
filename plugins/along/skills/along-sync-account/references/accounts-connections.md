# Account sync onboarding, recovery and handoff

Use this mode for a selected institution/account source check, source-to-app mapping, stale or erroring feed diagnosis, supported provider recovery, or a deliberate change in routine feed ownership. Read [workflow](workflow.md) for feed responsibility and runtime, [authentication](authentication.md) before access, [capabilities](capabilities.md) for supported controls, and [records](records.md) before saving. Read [changes](changes.md) before a feed or ledger mutation. Use [evidence](evidence.md) for a requested history/statement bundle and [email](email.md) only for a separately authorized receipt or MFA lookup; [analysis](analysis.md) is not a substitute for connection evidence. For Monarch-specific semantics, read [Monarch](monarch.md).

This is a procedure for a selected action, not a standalone “connect” command. The parent [sync skill](../SKILL.md) resolves the app-only versus Along-sync choice before onboarding. Household setup is user-invoked only; missing household configuration routes back to that explicit command. Existing requested one-off source checks can use the identity/access steps without creating an ongoing sync connection.

## Keep three decisions separate

Track these independently for each selected account:

- **Source access:** whether the official institution route is readable for the selected owner/account and what data routes are available.
- **App mapping:** whether that source identity is mapped to the intended finance-app account/workspace, with evidence beyond a masked suffix.
- **Feed responsibility:** whether the app connector, Along, manual entry or an unknown/pending handoff supplies routine updates.

A successful bank login does not establish an app mapping or make Along the feed owner. A mapped app account does not establish fresh source evidence. A verified handoff does not establish a reconciled transaction history.

## Source check and mapping

1. Resolve the user-selected institution, owner, account, finance-app workspace and requested operation. Reuse the existing registry and connection route; do not broaden a selected account into every account behind a shared login. Preserve joint ownership and ambiguous identities.
2. Verify the official route and displayed owner, then the selected masked account, type, currency and other stable attributes. Record access method, MFA observation, available transaction/statement/export routes and capability states. Use the live runtime in [workflow](workflow.md); if access is blocked, keep the connection partial and state the human action needed.
3. Inspect the app inventory and compare identity evidence before mapping. If the app account is absent, prepare a new-account proposal with intended type, currency, opening baseline and feed responsibility. Do not create it during a read-only connection check. Unresolved identity or mapping stays partial and is not ready for imports or repairs.
4. Do not fetch all history during connection testing. If the user requested a period, pass the exact scope to [evidence](evidence.md); if the purpose is categorization or completeness, hand the resulting evidence to `along-review-transactions` or `along-reconcile`. Connection completion records access and mapping, not balances or reconciliation.

## Diagnose and recover a feed

5. Start from an observed stale/error state and classify the smallest likely cause: app-side latency, expired authorization, provider outage or maintenance, changed institution route, wrong account mapping, unsupported account type, filtered/excluded rows, or a possible missing/duplicate transaction. Preserve the observation and do not call an old complaint a current defect without current evidence.
6. For a user-requested recovery of the selected feed, follow the provider's supported route: scoped reauthentication (the user completes MFA), then one read-only reinspection. If the provider reports an outage or unsupported route, record it and use the documented recovery path; do not loop logins or broaden scope. [capabilities](capabilities.md) and [Monarch](monarch.md) define what the app claims and what remains unverified.
7. If reauthentication fails and an alternate provider is supported, prepare the selected switch under [changes](changes.md): preserve account identity/history and user metadata, disclose sibling-account effects and overlap/reimport risks, snapshot the before-state, and verify the resulting mapping and producer before reconciling. Do not silently create a duplicate account or delete history. After access or provider recovery, compare the app's current account state with the existing evidence/checkpoint. A missing or duplicate transaction is a reconciliation finding, not proof that the feed should be taken over. Route the exact period to [evidence](evidence.md) and `along-reconcile`; use a manual repair only with source evidence, duplicate checks, a concrete proposal and a later duplicate recheck. Preserve app feed ownership for a one-off repair.

## Deliberate handoff

8. Consider a handoff only when the user chooses **routine Along-managed ingestion**. Source verification, a stale-feed diagnosis, categorization, or a one-off missing-transaction repair does not authorize it. Explain before preparing it: the app connector must stop updating the selected account, Along will update it through the supported manual/import path when run, and running both can duplicate or overwrite activity. Handoff may affect sibling accounts, existing history, balances or pending transactions.
9. Prepare a concrete preview before any connector change: source and app identity, exact account/connector scope, current feed owner, last known imported transaction/cutoff, pending/in-flight activity, expected effects on history/balances/sibling accounts, duplicate risks, return-to-app plan and any user-requested Along run cadence. Record the initial baseline/cutoff; do not treat the selected cadence as an active schedule. Read [changes](changes.md) and obtain approval for the exact connector/account operation. A generic setup preference is not standing approval.
10. Before applying, save an available app export or focused before-state snapshot, establish one writer, reobserve identity and feed state, and stop if they drift. Apply only through supported controls. Verify that the connector is actually inactive for the selected account, the mapping remains correct, no competing writer is active, and the destination state is readable. Set `feedOwner=along` and `handoff=verified` only after those observations; otherwise retain the prior owner and mark the handoff pending or blocked. Keep routine Along imports blocked while ingestion ownership is unknown; targeted repairs use the separate shared operation policy.
11. To return an account to app-managed updates, suspend Along writes first, preserve an overlap checkpoint, assess the app's documented import/re-download and duplicate behavior, then perform the approved reconnection and reinspection. Mark app ownership only after observed completion; preserve history and do not delete records to make the transition appear clean.

## Save and finish

Save a connection profile with source identity, app mapping evidence, access/capability states, feed owner, handoff state, observation times, evidence references, affected sibling scope and remaining work. Journal any approved connector mutation through [changes](changes.md) and verify it after the write. Report **source access**, **app mapping**, **feed responsibility**, **recovery outcome** and **transaction/evidence coverage** as separate results.

The onboarding/recovery procedure is complete when the selected operation has an observed or explicitly blocked result and its next action is clear. A verified handoff returns to the parent sync skill to perform the already requested bounded sync and reconciliation; do not stop at “connected” when the user requested a sync. A source-check-only request does not initiate historical imports, repairs or takeover. When a provider or tool remains unavailable, preserve the partial record and continue any independent saved-file or status work.
