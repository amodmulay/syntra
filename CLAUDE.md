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
- **Token usage:** `factory/usage/ledger.jsonl` (append-only) and
  `factory/usage/USAGE.md` record tokens per model. Run
  `python3 factory/bin/usage ingest` before committing to capture new
  Claude Code transcripts; never edit the ledger by hand.

## The factory

`/factory run` works through topics filed in `factory/inbox/` (by hand,
or pulled from GitHub issues labeled `factory` via `factory/bin/pull`),
carrying each through triage → spec → build → gate → review → approve,
landing approved work on the base branch or handing it to another line
(`build` → `docs` by default).

- State: `factory/jobs/<job-id>/` (gitignored). Only `factory/bin/job`
  writes it.
- Checks: `factory/checks.sh`.
- Boundaries: `factory/playbooks/_global.md` and one per line.
- Dashboard: `cd factory && python3 -m http.server`, then
  `http://localhost:8000/dashboard.html`.

Full detail lives in [AGENTS.md](AGENTS.md) (the file every factory agent
reads first — keep the two in sync if either changes), with the complete
picture in [README.md](README.md) and [DESIGN.md](DESIGN.md).
