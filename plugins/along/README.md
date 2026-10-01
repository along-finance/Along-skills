# Along skills

Along has skills to help manage household finance work in your personal finance app, such as Quicken Simplifi or Monarch Money.

Review transactions, reconcile accounts, plan bills, manage budgets, and understand your spending—all through your AI assistant.

## Supported platforms

- **Desktop:** Codex desktop app, or Codex in the ChatGPT desktop app.
- **Terminal:** Codex CLI with computer use enabled.

Along needs computer-use access to your chosen browser or finance app. Setup checks that access and helps you install or enable the required capability if it is missing.

## Install

Ask your desktop assistant or Codex CLI:

> Install Along from https://github.com/along-finance/Along-skills. Use the repository's installation instructions, and computer use if needed.

Or run these commands yourself:

```bash
codex plugin marketplace add along-finance/Along-skills
codex plugin add along@along
```

For a local copy, download or clone this repository, then replace `along-finance/Along-skills` in the first command with the path to its folder. The marketplace is at `.agents/plugins/marketplace.json`; the plugin is at `plugins/along`.

Start a new chat after installation. The desktop app also supports installing through its plugin directory; see [OpenAI's plugin installation guide](https://developers.openai.com/plugins/build/plugins).

## Start using Along

Run **`$along-setup`** first. Setup asks for your finance app, browser, sign-in preference, and private records folder. It then checks computer use and reads your app's account list to confirm access. You handle any sign-in or permission prompts that need you.

**Other Along skills wait until setup is complete.** Setup runs only when you ask for it. If access is missing, Along saves your progress and explains the next step. Installing a skill alone does not grant computer access.

After setup, ask naturally—your assistant chooses the relevant skill.

**Sync brings transactions into your app. Reconcile checks whether records agree.** Household setup does not connect banks or take over syncing. Along asks before taking over an account's sync.

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

See [DEVELOPMENT.md](https://github.com/along-finance/Along-skills/blob/main/DEVELOPMENT.md) for contributor instructions.

[MIT license](LICENSE).
