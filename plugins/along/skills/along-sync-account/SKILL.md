---
name: along-sync-account
description: Use Along to bring bank transactions into a finance-app account, onboard routine updates or recover a sync. Use for sync requests; setup is the explicit user-invoked command.
---

# Sync an account with Along

**Before starting:** Apply the [setup prerequisite](references/workflow.md#explicit-setup-and-account-actions). If setup is missing or partial, ask the user to run `$along-setup` and stop this workflow.

The user action is **read this account's source and bring its activity into the finance app using Along**. Say the named source, destination and period before acting. “Connect” is ambiguous: resolve whether the user wants Along-managed updates or a one-off check. For “refresh/reconnect” requests that may refer to the app’s own connector, clarify “Refresh the app’s existing connection, or use Along to supply updates?” using the actual selected app name. App-feed recovery preserves app ownership and follows the recovery reference without Along onboarding. Model selection of this skill grants no new account access or write authority.

Read [workflow](references/workflow.md) for scope and setup boundaries, [records](references/records.md) for existing state, and [connections](references/accounts-connections.md) when inspecting access, onboarding or recovering a feed. Before source retrieval read [evidence](references/evidence.md) and [authentication](references/authentication.md); before import/write read [changes](references/changes.md), [capabilities](references/capabilities.md), and [Monarch behavior](references/monarch.md) when applicable.

## Choose the action from observed account state

- **Already synced by Along:** reuse a verified source mapping and feed handoff, then run the sync below. Stale access follows the recovery procedure; unknown ownership blocks imports.
- **Not onboarded for Along sync:** for a bare “sync/update/connect this account” request, ask: “Along does not sync this account yet. Should I check what's already in [app], or set it up so Along reads the bank and updates [app]?” Replace `[app]` with the observed app name, or say “this finance app” until the app is observed. Offer **Check [app] only** and **Set up Along sync, then reconcile**, using the same observed app label. Explain that the first does not fetch bank activity or sync anything; the second makes Along responsible for future updates when run and requires stopping the app’s competing feed for that account, subject to a concrete transition preview. Honor a choice already explicit in the request rather than asking again.
- **Check app only chosen:** hand the named account/period to [reconcile](../along-reconcile/SKILL.md) in app-only mode. State that no sync was performed. A supplied statement can support a one-off source comparison without account onboarding.
- **Along sync chosen:** reuse an existing compatible household profile, including profiles from earlier Along versions. New household profile creation belongs only to the explicit Along setup command. If absent, tell the user to invoke that command and retain the selected account/action as pending context. Do not invoke household setup automatically. With a profile, follow the selected-account onboarding/handoff in [connections](references/accounts-connections.md), then sync and reconcile within the selected scope.

Account onboarding means verified source access, an unambiguous app mapping, a recorded initial baseline/cutoff and exclusive update responsibility. A saved login or mapping alone is insufficient. An app/manual account with unknown handoff is not already onboarded.

## Run a bounded sync

1. Confirm source, destination, currency, verified feed ownership and the requested interval. On later runs resume the last verified import coverage with enough overlap to detect replacements or late rows. On the first run choose and disclose the initial period/baseline; no automatic all-history import. Fetch only the needed source evidence.
2. Inspect destination rows and prior operation journals before calculating additions or updates. Reuse [reconcile](../along-reconcile/SKILL.md)'s source comparison to detect existing, pending/replaced, split, changed and ambiguous rows. Keep source IDs or reliable fingerprints; date cutoff alone is not a duplicate guard.
3. Prepare the exact import/update batch, app import mode, count and balance effects. Apply the [changes](references/changes.md) authorization rule: a previously approved bounded import policy may cover deterministic additions only within its recorded source/account/operation scope. “Sync” or a cadence alone does not authorize choosing destructive replacement, deletions, history rewrites or new inferred category rules. Without applicable authorization, show the concrete batch for approval. Never silently use a replacing CSV mode.
4. Execute through the supported path with a single writer and journal, then reread affected app rows and balances. Advance the sync checkpoint only for verified coverage; retain failures and uncertain saves as pending without blind retry.
5. Reconcile the imported interval against the source evidence. Report **updated through [date]**, verified additions/changes, **checked against [source/period]**, and remaining discrepancies separately. Successful import does not establish all-history reconciliation; failed verification is a partial sync.

## Finish clearly

Distinguish **ready for Along sync** (onboarding), **synced through a date** (verified update), and **reconciled for a period** (comparison). Source login alone proves none of these. Along runs on demand unless the user separately requests scheduling and a real scheduler confirms it. Store cadence intent separately from active scheduling.

For feed recovery or returning updates to the app, use [connections](references/accounts-connections.md). For status use [along-status](../along-status/SKILL.md). Household setup, ordinary transaction review, and a supplied-file comparison do not become a sync operation.
