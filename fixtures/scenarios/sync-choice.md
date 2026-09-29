# Sync choice scenario

## Prompt

> Connect `checking-001` and bring in the last statement period. I am not sure
> whether I want Along to own future updates or only to check what is already in
> Monarch. What are my choices?

## Expected route

The assistant asks the user to choose between **Check Monarch only** and **Set up
Along sync, then reconcile**. The first route inspects the app or compares a
supplied statement without source retrieval or import. The second route previews
source access, app mapping, feed ownership, initial cutoff, competing-feed effects
and duplicate risks before any handoff or import. The word “connect” alone does
not authorize a connector change, takeover or routine sync.

## Isolation checks

- The account and requested statement period are carried into the pending choice.
- Setup is not invoked automatically because a sync profile is missing.
- A selected Along sync still requires verified source access, an unambiguous app
  mapping, an agreed baseline and a single update owner before import.
- A selected app-only check reports source coverage as unknown and does not claim
  that the bank was reconciled.
