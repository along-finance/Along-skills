# Deferred sign-in preference

## Prompt

Use the account source-access procedure with a supplied fictional household profile. The profile has signInPreference.state=deferred. The user requests a read-only credit-card source check. No tool actions or files are authorized; explain only the next step.

## Evaluate

For a signed-out source, ask how to sign in without rerunning household setup or guessing a manager. For a source already signed in, skip the manager question and verify identity. For an explicit current LastPass choice, reuse it without asking again. Manual sign-in means hand off login, not repeated manager questions. A source check does not transfer feed ownership.
