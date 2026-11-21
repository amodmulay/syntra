# Handoff 1: build → docs

The build line merged this topic into main. The docs line starts from that work.

## Delivered
- `src/calculator.py` now defines `multiply(a, b)` after `subtract`, returning `a * b`, with the docstring "Return the product of a and b."
- `tests/test_calculator.py` imports `multiply` and adds `test_multiply` (`multiply(2, 3) == 6`, `multiply(-2, 3) == -6`).
- `add`, `subtract`, their tests, and the module docstring are unchanged; the diff is purely additive.
- Only the two spec'd files changed. Committed as `438c158` on `factory/002-add-a-multiply-function`.

## Decision
- Adds `multiply(a, b)` to `src/calculator.py` and `test_multiply` to `tests/test_calculator.py`. That is exactly the slice triage scoped.
- All five acceptance criteria are met. I reran AC1 through AC4 myself in the worktree.
- Round 1 reads `GATE: PASS` with no protected paths touched, and `review-code.md` reads `VERDICT: PASS` with no issues.
- Nothing from the escalate lists applies. There are no new dependencies and no changes to CI, auth, money, schema or factory files.
