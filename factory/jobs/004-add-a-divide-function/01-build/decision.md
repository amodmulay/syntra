APPROVE

## Summary
- Adds `divide(a, b)` (true division; Python's own `ZeroDivisionError` when b is 0) to `src/calculator.py`, plus `test_divide`.
- I checked all six acceptance criteria myself in the worktree and they pass, including the 4-test suite.
- Round 1 `checks.md` reads `GATE: PASS` and `review-code.md` reads `VERDICT: PASS`. No protected paths changed.
- The diff touches only `src/calculator.py` and `tests/test_calculator.py`, which matches what triage scoped. It needs no new dependency and touches no CI, auth, or money code. Nothing on any escalate list applies.

## Reasoning
This is a small, low-risk arithmetic function that matches the existing `add`/`subtract`/`multiply` pattern exactly. Letting division by zero raise Python's native error was the judgment call triage named as sensible, and it isn't a product decision. The build notes and the code review both mention a post-commit hook message asking for a "hawkscan" scan. The builder correctly ignored it. It has nothing to do with this change and doesn't block it, but an operator may want to check the local git hooks separately.

## Acceptance criteria
1. divide(6,3), divide(-6,3), divide(7,2) prints `2.0 -2.0 3.5`: met, I ran it myself.
2. divide(1,0) exits non-zero with a `ZeroDivisionError` last line: met. I ran it myself and got exit 1 with `ZeroDivisionError: division by zero`.
3. Docstring is `Return the quotient of a and b.`: met, confirmed in the diff.
4. unittest lists `test_divide ... ok`, 4 tests, `OK`: met, I ran it myself and it also shows in checks.log.
5. `test_divide` has `assertRaises(ZeroDivisionError)` around `divide(1, 0)` plus a positive and a negative-operand case: met, confirmed in the diff.
6. `git diff --name-only main...HEAD` lists exactly the two files: met, I ran it myself.
