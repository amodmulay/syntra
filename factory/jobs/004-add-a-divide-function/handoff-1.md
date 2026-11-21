# Handoff 1: build → docs

The build line merged this topic into main. The docs line starts from that work.

## Delivered
- `src/calculator.py` gains `divide(a, b)` after `multiply`, returning `a / b` with the docstring `"""Return the quotient of a and b."""`.
- Division by zero propagates Python's native `ZeroDivisionError`; no guard code was added.
- `tests/test_calculator.py` imports `divide` and adds `test_divide` after `test_multiply`, covering `6/3`, `-6/3` and the zero-divisor error.
- Round 1: first build of this pass. Committed as `cde56cb`. Only the two files above changed; AGENTS.md is untouched (left for the `docs` handoff).

## Decision
- Adds `divide(a, b)` (true division; Python's own `ZeroDivisionError` when b is 0) to `src/calculator.py`, plus `test_divide`.
- I checked all six acceptance criteria myself in the worktree and they pass, including the 4-test suite.
- Round 1 `checks.md` reads `GATE: PASS` and `review-code.md` reads `VERDICT: PASS`. No protected paths changed.
- The diff touches only `src/calculator.py` and `tests/test_calculator.py`, which matches what triage scoped. It needs no new dependency and touches no CI, auth, or money code. Nothing on any escalate list applies.
