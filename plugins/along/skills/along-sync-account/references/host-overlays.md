# Host overlay instructions

The production bundle is host-neutral. Keep invocation syntax and host-specific tool wiring in the build or deployment overlay, not in the canonical skill instructions. The overlay describes how the current host exposes the skills and records the generated invocation without changing the workflow's financial rules.

## Generated setup invocation

Use the canonical phrase **explicit Along setup command** in skill text. During packaging, generate the host's invocation for the `along-setup` skill and record it in host metadata:

- Codex desktop or Codex CLI may expose the skill through the `$along-setup` form when that host's skill loader supports it.
- Claude desktop/Cowork and Claude Code CLI should use the invocation form supplied by their installed skill loader or deployment adapter. Do not assume Codex token syntax is available there.

The generated overlay must preserve that setup is user-only. It must not cause sync, status, reconciliation or analysis skills to invoke setup automatically, and it must not turn a missing profile into permission for source login, connector changes or imports. If the host cannot represent an explicit skill invocation, state the required user-facing command in the host setup documentation instead of adding a hidden automatic trigger.

## Generated runtime mapping

For each host, record the actual adapter/tool names and capability results for `file_read`, `ui_read`, `ui_write`, `connector_read`, `python3_10` and `scheduler`. Record `unknown` when a capability was not tested. A discovered tool is not an active browser or signed-in account. The overlay must not invent browser, computer-use, connector, scheduler or MCP APIs; it may only map to capabilities the host actually exposes.

Keep the overlay's paths relative to the installed bundle, keep private data paths outside the immutable plugin cache, and omit secrets, cookies, account identifiers and authentication URLs. Updating an overlay does not rewrite household records or imply that a live capability passed.
