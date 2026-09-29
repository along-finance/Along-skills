# Along release validation

Run the validator from this directory or pass the candidate plugin explicitly:

```bash
python3 validate_release.py \
  ../plugins/along \
  --fixtures ../fixtures \
  --host-build ../fixtures/host-builds/codex-desktop.json \
  --host-build ../fixtures/host-builds/claude-code-cli.json
```

The command writes one JSON evidence document to stdout and exits zero only when
all requested checks pass. It checks the eight-skill bundle shape, relative
Markdown references and anchors, symlink containment, private-path or
credential-like content, supplied host-build metadata, the bundled Python helper
tests, and the synthetic provided-source reconciliation fixtures. Host builds are
optional; each supplied build must identify a user-only setup invocation and all
six runtime capability records.

The fixtures are deliberately synthetic. The provided-source pair includes two
real same-amount purchases with distinct IDs, a source-only row, an unmatched app
row, a pending-to-posted replacement, and a split parent whose children conserve
the signed amount. Scenario prompts cover setup isolation and the choice between
an app-only check and Along-managed sync.

For a read-only model smoke run, use the installed Codex login from this
directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 run_scenarios.py --timeout 180
```

The runner copies the canonical skills into the private
`../tests/codex-scenarios/.agents/skills` workspace, stages only the two CSVs for
the independent reconciliation scenario, and keeps event logs and answers under
`../tests/codex-scenarios/runs`. Each session is ephemeral and uses a read-only
sandbox; no account, browser, connector, network, or financial write is
authorized by the prompts.
