# Changelog

## 0.1.2 (unreleased)

- Clarify desktop and CLI support and repository installation.
- Require completed setup before every other Along workflow.
- During setup, install or enable available computer-use integration and verify read-only finance-app access before marking Along ready.
- Explain affiliation, local storage, cloud processing, and data removal.
- Add installation maintenance, verification status, linked skill examples, and a synthetic reconciliation walkthrough.

## 0.1.1

- Codex-only supported release; other hosts remain contributor experiments.
- Short setup intake with app, browser and sign-in choices.
- Optional household label and explained timezone, currency, storage and saved-record defaults.
- Deferred password-manager choices resolved only when sign-in is needed; existing sessions and explicit choices are reused.

## 0.1.0

- Bundle eight household-finance skills with shared references and calculation helpers.
- Keep household setup explicitly user-invoked on Codex and Claude.
- Separate Along-managed account updates from app-only and supplied-source reconciliation.
- Discover actual host capabilities before live account access; preserve file-based workflows when live access is unavailable.
- Keep private household state outside the installed plugin and public source.
- Generate Codex and Claude archives from one source with deterministic checksums.

Compatibility evidence and limitations are recorded in the README. A successful installation or read-only check does not establish live-write support for every finance app.
