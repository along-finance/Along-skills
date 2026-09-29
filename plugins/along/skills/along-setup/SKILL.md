---
name: along-setup
description: Set up Along's household profile, app/workspace, private storage, access preferences and app inventory. User invocation only; routine sync, status, analysis and one-off file work do not invoke it.
---

# Set up Along

This is the explicit Along setup command. Run it only after the user invokes this command or directly asks to create or change the household setup. Read [setup](references/setup.md) and complete only the requested setup scope.

Setup establishes the household, selected finance app/workspace, private storage, timezone/currency and access preferences, then inventories accounts visible in that app. It does not sign into source institutions, connect or recover feeds, import or sync transactions, reconcile records, repair ledger rows, or change app data. Keep those as separate user-requested workflows.

If another Along workflow is missing a persistent setup profile, it must preserve the user's original request and tell the user to invoke the explicit Along setup command; it must not silently invoke this skill or reproduce the full household setup. A one-off file or live task may resolve only the minimum account identity it needs when its own workflow allows it.

Finish with a saved setup profile and app inventory, or a clearly partial result with the exact missing user action. Do not imply source onboarding or reconciliation has occurred.
