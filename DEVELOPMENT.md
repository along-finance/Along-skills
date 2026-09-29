# Developing Along

The canonical plugin is in `plugins/along`. `build.py` packages the same skills for Codex and Claude, adding host-specific metadata.

## Build

Requires Python 3.10 or later. From the repository root:

```bash
python3 build.py --output ./dist
```

Outputs:

- `dist/codex/along-codex-0.1.0.zip` — Codex plugin and local marketplace.
- `dist/claude/along-claude-0.1.0.zip` — Claude plugin.
- Matching `.sha256` checksum files.

## Test

```bash
python3 -m unittest discover -s build-tests -p 'test_*.py'
python3 -m unittest discover -s release-tools -p 'test_*.py'
python3 release-tools/validate_release.py plugins/along \
  --fixtures fixtures \
  --host-build fixtures/host-builds/codex-desktop.json \
  --host-build fixtures/host-builds/claude-code-cli.json
```

The validator runs the finance-helper tests. See [release-tools](release-tools/README.md) for model scenario tests and evidence formats. Fixture metadata is not proof that a host can operate a live app.

## Release checks

- Verify installation and skill routing in each supported host. Setup must remain explicitly user-invoked.
- Test the actual browser/computer route separately from skill loading. Claude native computer use is interactive-only on the CLI and browsers are view-only; the Chrome extension is a separate route.
- Use disposable data for edit/recovery tests. Never infer live provider write support from a synthetic ledger test.
- Keep household data and private test logs out of the repository and archives.
- Update `SOURCE-MANIFEST.json` when source files change. Its `files` mapping contains SHA-256 hashes of tracked files other than the manifest itself.
- Retain immutable versioned ZIPs and checksums. Users can retain an older archive for rollback; keep one installed Along version to avoid duplicate routing.

Detailed test results and current limitations are in `VERIFICATION.md` attached to the [release](https://github.com/along-finance/Along-skills/releases/tag/v0.1.0).

## Host documentation

- [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [Claude Code plugins](https://code.claude.com/docs/en/plugins)
- [Claude Code native computer use](https://code.claude.com/docs/en/computer-use)
- [Claude Code Chrome integration](https://code.claude.com/docs/en/chrome)
