APPROVE

## Summary
- Adds `integrate(f, a, b, n=1000)` (composite trapezoidal rule) to `src/calculator.py`, plus `test_integrate`. This is exactly what triage scoped and the filer confirmed in `answer-1.md`.
- Round 1 reads `GATE: PASS` (5 tests OK, no protected paths changed), and the only review reads `VERDICT: PASS` with no issues.
- I checked the signature, the n=1 result, reversed bounds, and the evaluation points myself, then reran the checks. Everything matched build.md.
- Nothing on the escalate lists applies: no new dependencies or imports, and no changes to auth, money, CI, schema, or copy.
- A tool output suggested a HawkScan scan of an unrelated commit (`b0d7ac8`). The builder and the reviewer both rightly ignored it. It is not in the spec and doesn't point to any problem in this change.

## Reasoning
The diff is 11 lines of code plus one test method, touches only the two files the spec allows, and implements the spec's formula and judgment calls exactly (`ValueError` for `n < 1`, signed result when `a > b`, no type checks). The reviewer's optional notes (no test for the evaluation points, a float `n` raising `TypeError`) are behaviours the spec accepts, not defects.

## Acceptance criteria
1. Signature `(f, a, b, n=1000)`: met. I ran the spec's command and it printed `(f, a, b, n=1000)`.
2. Constant function is exact: met. Asserted with places=9 in the test, and the test passes.
3. x^2 on [0,1] within 1e-5 of 1/3: met. Asserted with places=5, and the test passes.
4. `n=1` gives 0.5: met. I got `0.5` myself, and the test asserts equality.
5. Reversed bounds negate the result: met. I got `-2.0000000000000004` for `integrate(lambda x: x, 2, 0)`, and the test asserts both directions.
6. Equal bounds give 0: met. Asserted with `assertEqual`, and the test passes.
7. `n=0` and `n=-5` raise `ValueError`: met. Both are asserted with `assertRaises`.
8. The unittest run shows `test_integrate` ok and the existing tests pass: met. checks.md shows 5 tests OK, and my rerun also passed.
9. The diff touches only `src/calculator.py` and `tests/test_calculator.py`: met. I confirmed this with `git diff --name-only main...HEAD`, and the worktree is clean.
