# CLAUDE.md

This project is a minimal calculator module (`src/calculator.py`:
`add`, `subtract`, `multiply`, `divide`, `integrate`), used mainly to
exercise the software factory below end to end.

- **Setup:** nothing to install — stdlib only.
- **Validation:** `python3 -m py_compile src/*.py && python3 -m unittest
  discover -s tests -v` — matches `factory/checks.sh` exactly. Run this
  before calling anything done.
- **Scope:** keep changes to `src/` and `tests/` small and self-contained,
  matching the existing functions' style. Treat `factory/*` and
  `.claude/*` as off-limits unless the task is explicitly about the
  factory itself.

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
