# CLAUDE.md

This project is Syntra, a repository-local software factory. The
calculator module (`src/calculator.py`, `tests/test_calculator.py`) is only
a throwaway fixture for quick end-to-end tests of the factory; it is not the
product.

- **Setup:** nothing to install — stdlib only.
- **Validation:** `python3 -m py_compile src/*.py && python3 -m unittest
  discover -s tests -v` — matches `factory/checks.sh` exactly. Run this
  before calling anything done.
- **Scope:** factory work (workflow, prompts, playbooks, configuration,
  documentation, dashboard, `factory/bin/*`) is the real work. Calculator
  changes exist only to exercise the factory; keep them small and
  self-contained. `factory/bin/job` and `factory/checks.sh` are protected by
  the gate.
- **Token usage:** `factory/usage/ledger.jsonl` (append-only, tokens and
  API-equivalent dollars per call) and `factory/usage/USAGE.md` record usage
  per model. `factory/bin/job` ingests automatically on every save; run
  `python3 factory/bin/usage ingest` for work outside the factory. Commit
  the ledger so it persists; never edit it by hand. Per-job, per-step
  usage is in `job.json` (`models`) and never decreases on sync.

## The factory

`/factory run` works through topics filed in `factory/inbox/` (by hand,
or pulled from GitHub issues labeled `factory` via `factory/bin/pull`),
carrying each through triage → spec → build → gate → review → approve,
landing approved work on the base branch or handing it to another line
(`build` → `docs` by default).

- State: `factory/jobs/<job-id>/` (gitignored). Only `factory/bin/job`
  writes it. `factory/records/<job-id>.json` is a tracked, committed summary
  written by `factory/bin/job` at final merge (committed with the work) and at
  reject (written uncommitted; the operator must commit it by hand).
- Checks: `factory/checks.sh`.
- Boundaries: `factory/playbooks/_global.md` and one per line.
- Dashboard: `/factory run` starts it automatically (`factory/bin/dashboard`,
  localhost only, port from `dashboard.port` in `factory/config.json`) and
  prints the URL; run `python3 factory/bin/dashboard` to start it by hand.

Full detail lives in [AGENTS.md](AGENTS.md) (the file every factory agent
reads first — keep the two in sync if either changes), with the complete
picture in [README.md](README.md) and [DESIGN.md](DESIGN.md).
