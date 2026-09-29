# Runtime adapters

Use this reference before any live finance-app or institution UI work. It keeps the financial workflow independent from the host that supplies browser, native-app, connector, file and Python capabilities. A skill installation does not create a browser session, grant OS permissions, authenticate an account, or make a connector available.

## Capability checks

Inspect the actual current session and record the host, adapter/tool names, target, authorization state and observation time. Use these semantic capability names in the run record:

- `file_read`: the selected local evidence or task files can be read.
- `ui_read`: an approved native browser or native-app surface is exposed, initialized according to its current host documentation, and can show the selected app or institution.
- `ui_write`: the same surface exposes the approved write control for the exact requested operation. Discovery alone never grants write permission.
- `connector_read`: a configured, authorized connector for the selected target is exposed and its account/operation semantics are known.
- `python3_10`: Python is available at version 3.10 or newer when a bundled helper or check is requested.
- `scheduler`: a real host scheduler returns a completion handle when a user explicitly requests future work. A saved date or case is not a scheduler.

Mark each capability `passed`, `blocked`, or `unknown` independently. A tool name in an inventory means only that the tool is discoverable. It does not prove that a browser is open, that the user is signed in, that the selected workspace is visible, or that a target account is authorized.

For `ui_read`, initialize the exposed adapter with its returned documentation, obtain a fresh readable view, and verify the displayed app/institution, workspace/profile and selected masked account. Only then is the UI route usable. For `connector_read`, verify the configured connector, target workspace, selected account and supported operation before treating it as usable. Keep source access, app mapping, feed ownership and write authorization separate.

## Host branches

- **Codex desktop:** Use the computer-use surface actually exposed by the desktop host and follow its returned initialization documentation. In the current Codex desktop environment this may be the `mcp__cua_repl` adapter; treat that as a conditional observed tool, never as a portable assumption. A fresh browser or native-app view is still required.
- **Codex CLI:** Inspect the CLI session's actual tool inventory. Use a currently exposed native browser/computer surface or a configured supported connector when its target and semantics are verified. Shell and file tools alone provide no UI capability.
- **Claude desktop/Cowork:** Use the connected native browser/computer surface or configured supported connector exposed by the current host, following that host's documentation. Do not assume that Claude desktop or Cowork has a browser, a finance-app session or a connector merely because the bundle is installed.
- **Claude Code CLI:** Use an actually configured supported connector or browser/computer surface present in the current session. A terminal, HTTP client, or local file tool cannot substitute for an approved UI route.
- **Other hosts:** Continue file-backed, saved-status and other independent work when possible. Mark live UI or connector work unavailable until a supported adapter is exposed and verified.

The allowed live routes are a verified native browser/native-app surface or a configured supported connector with known semantics. Do not use shell-driven UI automation, private endpoints, guessed APIs, direct HTTP requests to authenticated services, or an unverified browser workaround. If no live route passes, stop only the dependent live step and report the exact capability gap; do not block supplied-file parsing, saved evidence analysis or other independent read-only work.

## Host overlays and private data

Canonical skills use the phrase **explicit Along setup command** so they can run on Codex and Claude hosts. Read [host overlays](host-overlays.md) when packaging a host-specific invocation. The overlay may map that phrase to the host's generated skill command, but it must not change authorization, feed ownership, recovery rules or the requirement for a fresh target view. Keep credentials, statements, receipts, runtime records and other household data in the selected private data root or task workspace, outside this immutable plugin cache.

When a helper script is requested, check `python3_10` first and run it only against the selected private/task data. If Python is missing or too old, report the helper-specific gap and continue any work that does not depend on it. Do not install packages into the plugin cache or claim that Python availability proves UI access.
