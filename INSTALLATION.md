# Install and maintain Along

Install all eight skills together. Copying an individual skill can break shared references. The command syntax below was checked against Codex CLI 0.158.0; this is not a claimed minimum version or a live finance-app certification. For host-specific plugin behavior, see [OpenAI's plugin documentation](https://developers.openai.com/plugins/build/plugins).

## Choose a source

Choose the repository install for current development changes. Choose a versioned Codex ZIP from [Releases](https://github.com/along-finance/Along-skills/releases) for a fixed preview you can retain and reinstall. See [verification status](VERIFICATION.md) for the distinction between source and published versions.

Repository install:

```bash
codex plugin marketplace add along-finance/Along-skills
codex plugin add along@along
```

For a downloaded ZIP, extract it and run the following from its `along` folder. For a clone, run them from the repository root. The chosen directory must contain `.agents/plugins/marketplace.json` and `plugins/along`.

```bash
codex plugin marketplace add .
codex plugin add along@along
```

A desktop user can ask the assistant to follow these instructions. A plugin directory in the host does not mean Along is listed in it.

## Verify installation

Start a new chat and check that the skill picker includes `along-setup`. In the terminal, `codex plugin list` also lets you inspect the marketplace listing and installation state. Then explicitly invoke `$along-setup` as described in the [README](README.md#first-use).

Seeing a skill proves that its instructions can load. Only a completed setup with saved app-access evidence establishes readiness for that household. A partial setup must explain what is missing.

## Update

For a Git-backed marketplace:

```bash
codex plugin marketplace upgrade along
codex plugin add along@along
```

For a local source, first update your checkout or extract the newer release. Register that local root with `codex plugin marketplace add .`, then run `codex plugin add along@along`. Local directories are not refreshed by the Git marketplace upgrade command.

Start a new chat and check the installed version. Keep household records outside the plugin so replacing it does not replace those records. If the old version still loads, inspect the configured source with `codex plugin marketplace list` and follow the duplicate/stale installation guidance below.

To return to an earlier preview, remove the current plugin, register the retained release's extracted folder, and install again. This changes the skill version; it does not undo finance-app edits or revert household records.

## Uninstall

```bash
codex plugin remove along@along
codex plugin marketplace remove along
```

The second command removes the marketplace registration. Start a new chat. Your household folder and finance-app data remain; see the README's [data removal guidance](README.md#your-data) for other copies.

## Troubleshooting

| Symptom | Next step |
| --- | --- |
| `codex` is missing or `plugin` is unknown | Install or update Codex using its official instructions. The desktop app's bundled command may differ from the terminal command. |
| Along is missing from the skill picker | Confirm installation, then start a new chat. Inspect `codex plugin list` and `codex plugin marketplace list`. |
| Old or duplicate Along skills appear | Check for a legacy manually copied Along skill set as well as the plugin. Retain one source; remove only the duplicate Along installation. If needed, remove and reinstall the plugin from the chosen source. |
| Setup cannot read the app | Enable the host's computer/browser tools, complete its permission prompts, and sign in to the selected app. Ask setup to resume. Reinstalling skills does not grant browser access. |
| A workflow asks for setup | Invoke `$along-setup` explicitly. A profile with partial setup is not ready yet. |
| A calculation helper cannot run | Check that Python 3.10 or later is available to the assistant's execution environment. |
| An import or edit has an uncertain result | Inspect the saved result before retrying; repeating an uncertain action can create duplicate changes. |

Do not include statements, credentials, or private household logs in public troubleshooting reports.
