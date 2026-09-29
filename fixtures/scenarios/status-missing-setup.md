# Status with no setup profile

## Prompt

> Show the current Along status for the synthetic household `household-demo`.
> There is no saved Along household profile in the task workspace. Do not create
> one, do not open a browser or connector, do not inspect private account pages,
> and do not change files. Tell me the smallest next action and what can still be
> reported from the missing setup state.

## Expected observation

The status request remains read-only and does not initialize setup. The response
should say that a persistent status view is unavailable until the user invokes the
explicit Along setup command, while keeping that request separate from sync or
reconciliation. It may explain that no account health or feed coverage can be
claimed from an absent profile.
