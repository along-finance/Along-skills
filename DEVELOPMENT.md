# Developing Along

The canonical plugin is in `plugins/along`. `build.py` builds the supported Codex package by default. Host-specific packaging stays separate from the shared workflows.

## Build

Requires Python 3.10 or later. From the repository root:

```bash
python3 build.py --output ./dist
```

Outputs:

- `dist/codex/along-codex-0.1.1.zip` — Codex plugin and local marketplace.
- Matching `.sha256` checksum files.

## Test

```bash
python3 -m unittest discover -s build-tests -p 'test_*.py'
python3 -m unittest discover -s release-tools -p 'test_*.py'
python3 release-tools/validate_release.py plugins/along \
  --fixtures fixtures \
  --host-build fixtures/host-builds/codex-desktop.json
```

The validator runs the finance-helper tests. See [release-tools](release-tools/README.md) for model scenario tests and evidence formats. Fixture metadata is not proof that a host can operate a live app.

## Release checks

- Verify installation and skill routing in each supported host. Setup must remain explicitly user-invoked.
- Test the actual browser/computer route separately from skill loading. Loading instructions is not evidence that an assistant can operate a finance app.
- Use disposable data for edit/recovery tests. Never infer live provider write support from a synthetic ledger test.
- Keep household data and private test logs out of the repository and archives.
- Update `SOURCE-MANIFEST.json` when source files change. Its `files` mapping contains SHA-256 hashes of tracked files other than the manifest itself.
- Retain immutable versioned ZIPs and checksums. Users can retain an older archive for rollback; keep one installed Along version to avoid duplicate routing.

Detailed test results and current limitations are in `VERIFICATION.md` attached to the [release](https://github.com/along-finance/Along-skills/releases/tag/v0.1.0).

## Adding a platform

Claude Desktop and Claude Code CLI support is deferred. Other assistants are welcome too. Before proposing a supported platform:

1. Add its packaging and installation instructions without duplicating the shared finance workflows.
2. Preserve explicit-only setup, permission boundaries, private storage, and recovery from uncertain saves.
3. Verify skill discovery, source reconciliation, and the actual computer/browser tools on that platform.
4. Demonstrate navigation and a scoped edit against disposable data, including reading the saved result and avoiding duplicate retries.
5. Document which live finance-app operations were tested and which remain unverified.

Earlier Claude packaging and fixtures remain as unsupported contributor scaffolding. To inspect the experimental bundle:

```bash
python3 build.py --output ./experimental-dist --include-experimental-claude
```

This is not a supported installation path. The old Claude assets on the 0.1.0 release are historical previews, not current support commitments.

## Host documentation

- [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [Claude Code plugins](https://code.claude.com/docs/en/plugins) (future work)
- [Claude Code computer use](https://code.claude.com/docs/en/computer-use) (future work)
