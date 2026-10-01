# Along skills

Review transactions, reconcile accounts, plan bills, manage budgets, and understand spending in your personal finance app through Codex.

> **Independent project:** Along is not affiliated with, endorsed by, or sponsored by Quicken, Monarch Money, or any bank or finance-app provider mentioned here.
>
> **Privacy:** Along saves household records in a folder you choose, but information your assistant reads can be sent to its cloud model provider. Local storage does not mean local-only processing. See [Your data](#your-data).

**Preview:** Codex is the supported host. Live bank syncing and finance-app edits are not yet certified by the published releases. Read the [verification status](https://github.com/along-finance/Along-skills/blob/main/VERIFICATION.md) before using real accounts.

## Requirements

- **Desktop:** Codex or ChatGPT desktop app with plugin support.
- **Terminal:** Codex CLI with plugin support and computer use enabled.
- Computer-use access to your chosen browser or finance app. Along does not bundle that capability; setup checks whether it is available.
- Access to your finance app and a separate private folder for household records. You handle sign-in and permission prompts that need you.
- Python 3.10 or later when running the bundled finance-check helpers. Building from source also requires Python 3.10 or later.

An assistant subscription or usage allowance and any finance-app subscription are separate from Along. Operating-system and browser compatibility depend on your host's computer-use tools; Along has not verified every combination.

## Install

Ask your desktop assistant or Codex CLI:

> Install Along from https://github.com/along-finance/Along-skills. Use the repository's installation instructions, and computer use if needed.

Or run:

```bash
codex plugin marketplace add along-finance/Along-skills
codex plugin add along@along
```

Install the full bundle: its eight skills share references and helpers. Start a new chat after installation.

The repository command follows the development source. For a versioned download, use a Codex ZIP from [Releases](https://github.com/along-finance/Along-skills/releases), extract it, and run the following from the extracted `along` folder:

```bash
codex plugin marketplace add .
codex plugin add along@along
```

The same commands work from the root of a local repository copy. Keep only one Along installation to avoid duplicate skills. See [installation, updates, and troubleshooting](https://github.com/along-finance/Along-skills/blob/main/INSTALLATION.md) for details.

## First use

1. In a new chat, open the skill picker and check that `along-setup` is available. Skill discovery confirms installation, not finance-app access.
2. Select **`$along-setup`** and ask: “Set up my household profile and finance app. Do not connect bank sources yet.” Setup asks for your app, browser, sign-in preference, and private records folder, then checks access and reads the app's account list.
3. Once setup is complete, try: “Show my saved Along status and unfinished work. Do not refresh feeds or change app data.” Expect a dated summary of what is known and what remains unverified; a new setup has no sync history yet.

Other Along skills wait until setup is complete. If access is missing, setup saves a partial result and explains the next step. It runs only when you ask; installing Along does not grant computer access or connect banks.

Want to see a reconciliation result before setting up? Browse the optional [worked example with synthetic data](https://github.com/along-finance/Along-skills/blob/main/fixtures/provided-source/README.md). Reading it requires no installation or account access.

## Skills

After setup, ask naturally; your assistant selects the relevant skill. Read-only app work can still save local reports or evidence.

| Skill | Example request and result | Can change finance-app data? |
| --- | --- | --- |
| [`along-setup`](https://github.com/along-finance/Along-skills/blob/main/plugins/along/skills/along-setup/SKILL.md) | “Set up Along.” Saves a household profile and visible account inventory. Explicit invocation only. | No |
| [`along-sync-account`](https://github.com/along-finance/Along-skills/blob/main/plugins/along/skills/along-sync-account/SKILL.md) | “Sync checking.” Brings source transactions into the mapped app account and reports verified coverage. | Yes, within the requested scope |
| [`along-status`](https://github.com/along-finance/Along-skills/blob/main/plugins/along/skills/along-status/SKILL.md) | “Show Along status.” Summarizes saved coverage and unfinished work. | No |
| [`along-reconcile`](https://github.com/along-finance/Along-skills/blob/main/plugins/along/skills/along-reconcile/SKILL.md) | “Compare checking with this statement.” Reports matches, gaps, and proposed repairs. | Only when repairs are authorized |
| [`along-review-transactions`](https://github.com/along-finance/Along-skills/blob/main/plugins/along/skills/along-review-transactions/SKILL.md) | “Review new transactions.” Categorizes, splits, or marks selected transactions reviewed. | Yes, within the requested scope |
| [`along-report-money`](https://github.com/along-finance/Along-skills/blob/main/plugins/along/skills/along-report-money/SKILL.md) | “Explain last month's spending.” Produces a report for the requested period. | No |
| [`along-plan-cash`](https://github.com/along-finance/Along-skills/blob/main/plugins/along/skills/along-plan-cash/SKILL.md) | “Can checking cover bills until payday?” Projects cash using balances and obligations. | When requested recurring-item changes are supported |
| [`along-manage-budget`](https://github.com/along-finance/Along-skills/blob/main/plugins/along/skills/along-manage-budget/SKILL.md) | “Update next month's grocery budget.” Previews and applies scoped budget changes. | Yes, within the requested scope |

Sync brings transactions into the app; reconciliation checks whether records agree. Setup does neither. Along asks before taking over an account's sync.

## Compatibility

Quicken Simplifi and Monarch Money are intended finance-app use cases, not blanket compatibility certifications. For both, live navigation, syncing, transaction edits, and budget changes need operation-specific verification. Other finance apps are unverified. See [current evidence and limitations](https://github.com/along-finance/Along-skills/blob/main/VERIFICATION.md).

Claude Desktop, Claude Code CLI, and other assistants are not supported today. Historical experimental packages do not establish current support.

## Your data

**Saved locally:** In a local Codex session, Along's instructions direct the assistant to keep household profiles, account mappings, source evidence, checkpoints, and reports in your chosen private folder, outside the repository and plugin. Some outputs may also be saved in the task workspace. A folder synced by iCloud, Dropbox, or another service may also be copied to that service. Along does not add encryption or access controls to these files.

**Sent to the cloud model:** With a cloud-backed assistant, prompts and the information returned by tools are processed by the model provider. This can include transaction rows, balances, merchant names, account identifiers, statement contents, reports, and browser screenshots or page text. A read-only task can still disclose this information to the provider. Along does not automatically anonymize it or make the assistant run offline.

**Other services:** Your finance app, banks, and any browser, connector, or password-manager integrations continue to process data under their own policies. This repository contains skills and local helpers; it does not include an Along-hosted data service or telemetry client. Your assistant and its integrations may retain their own chat history, logs, or screenshots. Their retention and model-training rules depend on your product, account, and settings; Along does not control them.

Never put passwords, recovery codes, or access tokens in Along records or chat. Handle sign-in through the app or your chosen credential tool. Share only the accounts and files needed for the task, and review your assistant's data controls before using real financial records.

**Removal:** Uninstalling Along removes the plugin, not your household folder, finance-app records, or provider-held chat history. Delete local records and synced copies separately when you no longer need them; manage chat history and connected-service access with the relevant provider. Removing local files does not erase copies already sent to a service.

## Development and license

See [DEVELOPMENT.md](https://github.com/along-finance/Along-skills/blob/main/DEVELOPMENT.md) for existing build and validation instructions, and the [changelog](https://github.com/along-finance/Along-skills/blob/main/plugins/along/CHANGELOG.md) for version history.

[MIT license](LICENSE). Product names belong to their respective owners and are used only to identify the apps discussed.
