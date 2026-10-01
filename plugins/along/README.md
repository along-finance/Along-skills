# Along skills

Bring transactions and balances from accounts your personal finance app doesn’t support—or struggles to keep connected—into apps like Quicken Simplifi and Monarch Money.

Along gives your AI assistant workflows to access those accounts through your browser, bring transactions into your finance app, and reconcile the results. It also helps review transactions, manage budgets, plan bills, and explain spending.

## Install

Works with the Codex or ChatGPT desktop app, or Codex CLI, with computer use enabled.

Ask your assistant:

> Install Along from [https://github.com/along-finance/Along-skills](https://github.com/along-finance/Along-skills) using the repository’s installation instructions.

Or run:

```bash
codex plugin marketplace add along-finance/Along-skills
codex plugin add along@along
```

Install the full bundle—the skills work together. Start a new chat after installation.

## Get started

Run `$along-setup` to choose your finance app, browser, and private records folder. Setup checks access; it doesn’t connect bank sources or start syncing.

Then try:

- “My finance app doesn’t support this account. Help me bring its transactions in.”
- “Use Along to sync my checking account.”
- “Check whether these transactions match my statement.”
- “Review new transactions and help categorize them.”
- “Can checking cover my bills until payday?”

## Included skills

| Skill | What it does |
| --- | --- |
| `along-setup` | Set up your finance app and preferences. |
| `along-sync-account` | Bring account transactions into your finance app. |
| `along-status` | Show sync coverage and unfinished work. |
| `along-reconcile` | Find missing transactions and differences. |
| `along-review-transactions` | Categorize, split, and review transactions. |
| `along-report-money` | Explain spending and income. |
| `along-plan-cash` | Plan bills and upcoming cash needs. |
| `along-manage-budget` | Update budgets, rollovers, and goals. |

Account access depends on what your assistant can operate in your browser. Along checks the available route for your account and app.

## Privacy and affiliation

Along saves household records in a private folder you choose. Information your assistant reads—including transactions, statements, and browser content—may be sent to its cloud model provider under that provider’s data policies.

Along is an independent project, not affiliated with Quicken, Monarch Money, or the banks and finance apps mentioned here.

[Development](https://github.com/along-finance/Along-skills/blob/main/DEVELOPMENT.md) · [MIT license](https://github.com/along-finance/Along-skills/blob/main/LICENSE)
