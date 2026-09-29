# Along skills

Along has skills to help manage household finance work in your personal finance app, such as Quicken Simplifi or Monarch Money.

Review transactions, reconcile accounts, plan bills, manage budgets, and understand your spending—all through your AI assistant.

## Supported platform

**Along currently supports Codex only.** Use Codex Desktop for working in your finance app. Codex CLI can load the skills, but standalone computer use has not been verified.

Codex needs browser/computer access to work directly in your finance app. Installing Along adds the workflows, not that access. You can also use supplied statements and exports without computer use. Live syncing and finance-app edits are still in preview.

## Install

Download the Codex bundle from [Releases](https://github.com/along-finance/Along-skills/releases).

1. Download and extract `along-codex-0.1.0.zip`.
2. Open a terminal in the extracted `along` folder and run:

   ```bash
   codex plugin marketplace add .
   codex plugin add along@along
   ```

3. Start a new Codex chat.

## Start using Along

Run **`$along-setup` in Codex** when you want to save your household profile. Setup does not connect or sync accounts.

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

## Future platforms

Claude Desktop, Claude Code CLI, and other assistants are future contributor opportunities, not supported options today. Contributions are welcome—see [Adding a platform](https://github.com/along-finance/Along-skills/blob/main/DEVELOPMENT.md#adding-a-platform). The workflows are kept separate from host-specific packaging so support can grow over time.

## Development

See [DEVELOPMENT.md](https://github.com/along-finance/Along-skills/blob/main/DEVELOPMENT.md) for building, testing, and release checks.

[MIT license](LICENSE).
