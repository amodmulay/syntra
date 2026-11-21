# Handoff 1: build → docs

The build line merged this topic into main. The docs line starts from that work.

## Delivered
- `src/calculator.py` now defines `subtract(a, b)` directly after `add`, returning `a - b`, with the docstring `Return the difference of a and b.`
- `tests/test_calculator.py` imports `subtract` and adds `test_subtract` right after `test_add` (cases `subtract(5, 3) == 2` and `subtract(1, 3) == -2`).
- `add`, the module docstring and `test_add` are unchanged; only those two files changed.
- Round 1: first build of this pass. Commit `ffafbb6` on `factory/001-add-a-subtract-function`.

## Decision
- Adds `subtract(a, b)` to `src/calculator.py` and `test_subtract` to `tests/test_calculator.py`, which is exactly what triage scoped.
- All six acceptance criteria are met. I reran 1 to 4 and the mutation check (6) myself and got the expected results.
- Round 1 checks read `GATE: PASS` at the commit under review (`ffafbb6`). The single code review reads `VERDICT: PASS` with no issues.
- Nothing in the global, build or generic escalate lists applies: no money, auth, CI, dependencies, migrations or product calls.
