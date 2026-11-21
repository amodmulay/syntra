# AGENTS.md

This repository is Syntra, a software factory. The minimal calculator sample is only a throwaway fixture for quick end-to-end tests of the factory, not the product. Syntra issues may update the factory itself through the same reviewed workflow. The calculator's functions are `add(a, b)` (sum of a and b), `subtract(a, b)` (a - b), `multiply(a, b)` (product of a and b), `divide(a, b)` (a / b; raises `ZeroDivisionError` when b is 0), and `integrate(f, a, b, n=1000)` (approximates the integral of f from a to b with the trapezoidal rule over n subintervals; raises `ValueError` when n < 1).

- **Setup**: nothing to install. `src/calculator.py` and
  `tests/test_calculator.py` use only the standard library.
- **Dev server**: none — there's no app to serve.
- **Validation**: `python3 -m py_compile src/*.py && python3 -m unittest
  discover -s tests -v` — matches `factory/checks.sh` exactly.

## About the factory

`/factory run` works through whatever's filed in `factory/inbox/`, one job
per topic, carrying each through triage → spec → build → gate → review →
approve and landing approved work on the base branch. Issues may update Syntra itself; `factory/checks.sh` remains gate-protected. A line's `handoff`
setting (in `factory/config.json`) can pass a finished job on to another line
— `build` handing to `docs`, for instance — before it's actually done.

- State lives in `factory/jobs/<job-id>/` (gitignored).
- `factory/bin/job` is the only thing allowed to write that state.
- `factory/bin/pull` pulls open GitHub issues labeled `factory` into the
  inbox before each run — optional, and harmless if `gh` isn't set up.
- Token usage: `factory/usage/ledger.jsonl` is an append-only record of
  tokens and API-equivalent dollars per call, per model. `factory/bin/job`
  ingests automatically on every save; `python3 factory/bin/usage ingest`
  does it by hand and regenerates `factory/usage/USAGE.md`. Never edit the
  ledger by hand.
- Checks: `factory/checks.sh` (plus whatever script other lines point to).
- Dashboard: `cd factory && python3 -m http.server`, then open
  `http://localhost:8000/dashboard.html`.

Every job gets its own git worktree — a full checkout at
`.worktrees/<job-id>` (gitignored). Any tool you run from the repo root that
doesn't respect `.gitignore` will also see those copies, so exclude
`.worktrees/` in its own config if that matters.

See [README.md](README.md) for the full picture and day-to-day usage, and
[DESIGN.md](DESIGN.md) for the reasoning behind how it's built.
