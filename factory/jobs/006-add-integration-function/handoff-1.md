# Handoff 1: build → docs

The build line merged this topic into main. The docs line starts from that work.

## Delivered
- Adds `integrate(f, a, b, n=1000)` to `src/calculator.py`: composite trapezoidal rule with `n` equal subintervals, placed after `divide`.
- Raises `ValueError` when `n < 1`; `a == b` gives 0 and `a > b` gives the signed (negated) result with no special-casing.
- Adds `test_integrate` to `tests/test_calculator.py` covering acceptance criteria 2 to 7, and imports `integrate` alongside the existing functions.
- Standard library only, no imports added. Nothing under `factory/` or `.claude/` touched; `AGENTS.md` left for the `docs` handoff.
- Round 1: first build, no prior gate or review feedback.

## Decision
- Adds `integrate(f, a, b, n=1000)` (composite trapezoidal rule) to `src/calculator.py`, plus `test_integrate`. This is exactly what triage scoped and the filer confirmed in `answer-1.md`.
- Round 1 reads `GATE: PASS` (5 tests OK, no protected paths changed), and the only review reads `VERDICT: PASS` with no issues.
- I checked the signature, the n=1 result, reversed bounds, and the evaluation points myself, then reran the checks. Everything matched build.md.
- Nothing on the escalate lists applies: no new dependencies or imports, and no changes to auth, money, CI, schema, or copy.
- A tool output suggested a HawkScan scan of an unrelated commit (`b0d7ac8`). The builder and the reviewer both rightly ignored it. It is not in the spec and doesn't point to any problem in this change.
