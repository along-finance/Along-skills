# Along

Along is a coordinated set of eight skills for household finance work:

- **along-setup** — create the household profile, app inventory, access choices, and private-storage pointer.
- **along-sync-account** — onboard or update an account through Along, or recover an existing Along sync.
- **along-status** — show feed ownership, sync coverage, reconciliation coverage, and open work.
- **along-reconcile** — compare app records with saved or supplied source evidence, or inspect app-only consistency.
- **along-review-transactions** — classify, split, assign, review, and prepare scoped transaction rules.
- **along-report-money** — explain historical spending, income, cash changes, and budget or goal outcomes.
- **along-plan-cash** — forecast future cash coverage and maintain recurring obligations.
- **along-manage-budget** — review and change budgets, rollovers, allocations, and goal funding.

## Setup and routing

Household setup is an explicit user action. Invoke `$along-setup` in Codex, or
the installed host's `/along-setup` command in Claude surfaces that display
that form. The generated Claude Code adapter documents its host-specific alias;
use the command shown by the installed host after verifying its routing. Ordinary
status, sync, review, report, cash-plan, and reconciliation requests must not
initialize setup. Setup also does not sign into an institution, connect a feed,
import transactions, reconcile records, or change finance-app data.

`along-sync-account` handles source activity brought into the finance app,
account onboarding for Along, and Along sync recovery. If an account is not onboarded and a
request only says “sync” or “update,” it offers two choices: inspect what is
already in the app, or let Along take responsibility for reading the source and updating this account.

`along-reconcile` checks records. With no verified Along handoff or supplied
source, it may inspect the app ledger only and must say that bank completeness
is unknown. A supplied statement/export supports a scoped comparison without
onboarding. Reconciliation does not silently take over a feed or run a routine
import.

## Example requests

- After selecting `along-setup`: “Set up my household profile and finance app. Do not connect bank sources yet.”
- “Use Along to sync my checking account into my finance app.”
- “Reconcile checking against this September statement without taking over its feed.”
- “Review new transactions since the last checkpoint.”
- “Can checking cover bills through next payday?”
- “Explain last month’s spending.”

## Package and private state

Install the complete bundle. The skills share references and scripts under
`along-sync-account`; copying an individual skill breaks those links and its
workflow contract. The bundle contains instructions, references, and a
calculation helper. Keep the household's selected private data root outside
this package and outside source control. Do not put credentials, tokens, or
household records in the plugin directory.

The skills prepare or apply app changes only when the host exposes the needed
app/browser tools and the request satisfies Along's authorization, journaling,
single-writer, and read-after-write rules. Live write support depends on the app and exact operation; read-only smoke tests do not validate writes. Along makes no promise of unattended scheduling.

## Install in Codex

Install the complete Along plugin through Codex's plugin manager. The Codex ZIP
includes a local marketplace containing the plugin. Extract it, then from the
extracted `along` folder, run:

```bash
codex plugin marketplace add .
codex plugin add along@along
```

Start a new Codex chat after installation. Keep one installed Along version;
remove older loose Along skill copies after backing them up to avoid duplicate
routing. Household records stay outside the plugin and are not migrated by an
update. Pin a release version, and retain its archive if you need to roll back.

## Build and local test

For contributors with the source checkout, run from its root:

```bash
python3 build.py --output ./dist
```

The build materializes both host trees and deterministic archives. With the
current version in `build.py`, the outputs are:

```text
dist/codex/along-codex-0.1.0.zip
dist/codex/along-codex-0.1.0.zip.sha256
dist/claude/along-claude-0.1.0.zip
dist/claude/along-claude-0.1.0.zip.sha256
```

The Codex archive includes its native marketplace wrapper and the complete plugin. For
a one-session Claude Code test, load `dist/claude/along/` with
`--plugin-dir`:

```bash
claude --plugin-dir ./dist/claude/along
```

In Claude Desktop, choose **Customize → Plugins → Add plugin → Upload plugin** and upload `along-claude-0.1.0.zip`. Start a new Cowork task after installing or updating.

For marketplace installation, follow the host's documented plugin flow and
verify that all eight skills appear after installation. The generated Claude
bundle has uploaded successfully to the current Claude Desktop installation
and all eight skills are listed and enabled. A fresh Cowork check loads seven
skills for model invocation and excludes setup as intended; shared-reference
resolution passed for all 18 links in the loaded status instructions.

Validate the source bundle and synthetic fixtures before distribution:

```bash
python3 -m unittest discover -s build-tests -p 'test_*.py'
python3 release-tools/validate_release.py plugins/along \
  --fixtures fixtures \
  --host-build fixtures/host-builds/codex-desktop.json \
  --host-build fixtures/host-builds/claude-code-cli.json
```

## Observed compatibility

These are smoke-test observations, not a production-readiness claim. They used
public example content and did not validate finance-app writes. No account
values are included here.

| Surface | Observed result |
| --- | --- |
| Codex desktop | Native Chrome read of a public page and a read-only selected finance-app view succeeded in the current desktop installation; no writes were attempted. |
| Codex CLI 0.158 | Native Chrome read of a public page succeeded through this desktop integration; this is not an independent clean-CLI result. |
| Claude Desktop 1.52386.3 | Cowork's built-in browser read a public page. The generated bundle uploaded and listed all eight skills; a fresh Cowork check loaded seven model-invocable skills and excluded setup as intended. |
| Claude CLI 2.1.227 | File tools are available; `--chrome` is discoverable, but its browser extension is disconnected. Further extension testing is deferred. |

The package is MIT licensed; see [LICENSE](LICENSE).

Host references: [Codex plugin packaging and local marketplaces](https://developers.openai.com/plugins/build/plugins) and [Claude Code plugin installation](https://code.claude.com/docs/en/plugins/install).
