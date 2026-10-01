# Verification status

Along is a preview. Packaging and synthetic-data checks do not certify live financial operations.

## Versions and evidence

- **Development source: 0.1.2, unreleased.** The plugin manifest and build version agree. The changelog describes the pending changes. Installing from the repository can include changes newer than the published archives.
- **Latest published preview: [0.1.1](https://github.com/along-finance/Along-skills/releases/tag/v0.1.1).** Its release notes report build, validator, finance-helper, and read-only setup-preview checks. They explicitly do not certify bank syncing or finance-app edits.
- **Historical evidence: [0.1.0](https://github.com/along-finance/Along-skills/releases/tag/v0.1.0).** The attached verification file and experimental Claude packages describe that release only. They are not current Claude support claims.

## What has and has not been established

| Area | Evidence and boundary |
| --- | --- |
| Bundle structure and Python helpers | Automated checks cover packaging, references, helper calculations, and synthetic reconciliation. See the [validation workflow](.github/workflows/check.yml) and [validation guide](release-tools/README.md). |
| Codex installation | Historical 0.1.0 evidence reports native install/remove checks. Current installation command syntax was checked with CLI 0.158.0. This does not establish every desktop/CLI/OS combination. |
| Setup | 0.1.1 reports a read-only setup preview. Current setup additionally requires saved computer-use/app-access evidence before other skills proceed. |
| Quicken Simplifi | Intended use case; current published evidence does not certify live navigation, bank sync, transaction edits, or budget changes. |
| Monarch Money | Intended use case with product references; current published evidence does not certify live navigation, bank sync, transaction edits, or budget changes. |
| Other finance apps | Unverified; inspect the exact app and operation before use. |
| Unattended scheduling | Unverified. A saved future date is not a scheduled task. |
| Claude and other hosts | Unsupported today. Experimental assets and fixtures are contributor scaffolding. |

The host fixture's capability fields are test inputs, not an end-to-end test report. Skills enforce setup and scope through instructions and saved evidence, not a separate technical lock on the host's tools.

When publishing a new release, update this page with the exact version, host/OS/browser, tested operation, date, result, and evidence. Keep read-only access, calculation checks, and successful live edits separate. Use disposable data for write testing.
