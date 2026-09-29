# Along skills

Along has skills to help manage household finance work in your personal finance app, such as Quicken Simplifi or Monarch Money.

Review transactions, reconcile accounts, plan bills, manage budgets, and understand your spending—all through your AI assistant.

## Supported platforms

| Platform | Support |
| --- | --- |
| **Codex Desktop** | Along skills and computer use. Recommended for working in your finance app. |
| **Claude Desktop · Cowork** | Along skills, statement/export analysis, and assisted viewing of your finance app. Full app interaction is not yet verified. |
| **Claude Code · CLI** | Along skills load. Interactive computer use is available on macOS; live finance-app workflows are not yet verified. |
| **Codex CLI** | Along skills. Our computer-use test used the Codex Desktop integration; standalone computer use is not verified. |

**To work directly in your finance app, your assistant needs browser/computer access.** Installing Along adds the workflows, not that access. You can also use supplied statements and exports without computer use.

Claude's native computer use can only view browsers. Clicking, navigating, or editing a web app needs its separate browser tools, such as [Claude in Chrome](https://code.claude.com/docs/en/chrome). Full live syncing and finance-app edits are still in preview.

## Install

Download the bundle for your assistant from [Releases](https://github.com/along-finance/Along-skills/releases).

### Codex

1. Download and extract `along-codex-0.1.0.zip`.
2. Open a terminal in the extracted `along` folder and run:

   ```bash
   codex plugin marketplace add .
   codex plugin add along@along
   ```

3. Start a new Codex chat.

### Claude Desktop

1. Download `along-claude-0.1.0.zip`.
2. In **Cowork → Customize → Plugins → Add plugin → Upload plugin**, select the ZIP.
3. Start a new Cowork task.

### Claude Code CLI

Download and extract `along-claude-0.1.0.zip`, then launch Claude with the extracted folder:

```bash
claude --plugin-dir /path/to/along
```

This loads Along for that session. For browser interaction, set up [Claude in Chrome](https://code.claude.com/docs/en/chrome) and add `--chrome`. Native [computer use](https://code.claude.com/docs/en/computer-use) is enabled separately through `/mcp → computer-use` in an interactive macOS session; it is unavailable with `claude -p`.

## Start using Along

Run **`$along-setup` in Codex** or **`/along:along-setup` in Claude** when you want to save your household profile. Setup does not connect or sync accounts.

After that, ask naturally—your assistant chooses the relevant skill. You can also reconcile a supplied statement without setup.

**Sync brings transactions into your app. Reconcile checks whether records agree.** Along asks before taking over an account's sync.

## Skills

| Skill | What it helps you do |
| --- | --- |
| `along-setup` | Set up your household profile. You invoke this yourself. |
| `along-sync-account` | Use Along to bring bank transactions into your finance app. |
| `along-status` | See account status and unfinished work. |
| `along-reconcile` | Check app records against statements or saved source records. |
| `along-review-transactions` | Categorize, split, and review transactions. |
| `along-report-money` | Explain spending, income, and changes over time. |
| `along-plan-cash` | Plan bills and check cash through your next payday. |
| `along-manage-budget` | Manage budgets, rollovers, and goal funding. |

## Example requests

- After selecting `along-setup`: “Set up my household profile and finance app. Do not connect bank sources yet.”
- “Use Along to sync my checking account into my finance app.”
- “Reconcile checking against this September statement.”
- “Review new transactions since the last checkpoint.”
- “Can checking cover bills through next payday?”
- “Explain last month’s spending.”

## Your data

Install the full bundle—the skills work together. Keep household records in a separate private folder, not in this repository or the plugin. Never store passwords in Along files.

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for building, testing, and release checks.

[MIT license](LICENSE).
