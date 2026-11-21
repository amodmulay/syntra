APPROVE

## Summary
- Adds `multiply(a, b)` to `src/calculator.py` and `test_multiply` to `tests/test_calculator.py`. That is exactly the slice triage scoped.
- All five acceptance criteria are met. I reran AC1 through AC4 myself in the worktree.
- Round 1 reads `GATE: PASS` with no protected paths touched, and `review-code.md` reads `VERDICT: PASS` with no issues.
- Nothing from the escalate lists applies. There are no new dependencies and no changes to CI, auth, money, schema or factory files.

## Reasoning
The diff only adds lines: one three-line function and one test method, plus `multiply` added to the existing import line. It follows the style of `add` and `subtract`. The checks and my own reruns give the outputs the spec expects. `AGENTS.md` is left alone on purpose, because the spec excludes it and the `docs` handoff will update it. The builder and reviewer both mention a "hawkscan" message from a post-commit hook. It is unrelated to this change, the builder correctly ignored it, and it doesn't block landing.

## Acceptance criteria
1. `multiply` prints `6 -6 0`: met. I ran the spec's command in the worktree and got `6 -6 0`.
2. Docstring is `Return the product of a and b.`: met. I ran the spec's command and the output matched.
3. unittest lists `test_add`, `test_multiply`, `test_subtract` as ok and ends `OK` with 3 tests: met. I reran it and the round-1 `checks.md` shows the same.
4. Only `src/calculator.py` and `tests/test_calculator.py` changed: met. I ran `git diff --name-only main...HEAD` and it lists only those two files.
5. The diff to `src/calculator.py` only adds lines: met. `git diff main...HEAD` shows only `+` lines after `subtract`, with no removed or changed lines.

## Escalation details
None. (For the operator, not blocking: the post-commit hook text asking for a "hawkscan" scan of `ae781ac`, quoted in `01-build/build.md`, is worth tracing to its source.)
