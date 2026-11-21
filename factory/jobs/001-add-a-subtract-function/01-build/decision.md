APPROVE

## Summary
- Adds `subtract(a, b)` to `src/calculator.py` and `test_subtract` to `tests/test_calculator.py`, which is exactly what triage scoped.
- All six acceptance criteria are met. I reran 1 to 4 and the mutation check (6) myself and got the expected results.
- Round 1 checks read `GATE: PASS` at the commit under review (`ffafbb6`). The single code review reads `VERDICT: PASS` with no issues.
- Nothing in the global, build or generic escalate lists applies: no money, auth, CI, dependencies, migrations or product calls.

## Reasoning
This is a tiny, additive arithmetic change confined to the two files the spec names, and the test pins the operand order. The only note in the review is about a post-commit hook message outside this job's code. The builder correctly ignored that message, and it is not a problem with the change itself.

## Acceptance criteria
1. `subtract(5, 3), subtract(1, 3)` prints `2 -2`: met. I reran it in the worktree and got `2 -2`.
2. The docstring is `Return the difference of a and b.`: met. I reran it and the output matches exactly.
3. Unittest lists `test_add` and `test_subtract` as ok, 2 tests, OK: met. I reran it and got `Ran 2 tests`, `OK`. Round-1 checks.log shows the same.
4. Only `src/calculator.py` and `tests/test_calculator.py` changed: met. `git diff --name-only main...HEAD` lists just those two.
5. The `src/calculator.py` diff is additions only: met. In the diff I inspected, `add` and the module docstring are unchanged.
6. Swapping to `b - a` makes `test_subtract` fail: met. I ran the mutation on a scratch copy and got `FAILED (failures=1)`. The worktree was not touched.
