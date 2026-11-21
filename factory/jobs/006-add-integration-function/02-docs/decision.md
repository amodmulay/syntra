APPROVE

## Summary
- The branch changes one line of `AGENTS.md`: the function list now names `integrate(f, a, b, n=1000)` last, after `divide`, with the trapezoidal-rule description and the `ValueError` when n < 1.
- Round 2's `checks.md` reads `GATE: PASS` (5 tests OK, no protected paths changed). The round-2 review reads `VERDICT: PASS` with no issues. The only round-1 issue, the stray "and" before `divide`, is fixed.
- I checked the diff myself: only `AGENTS.md` changed (1 insertion, 1 deletion). `and `divide(a, b)`` has count 0 and `and `integrate(...)`` has count 1. The entry matches `src/calculator.py`.
- Nothing on the global or docs escalate lists applies. There is no code, config, dependency, public commitment or product-copy change.

## Reasoning
This is a docs-only one-line edit that brings `AGENTS.md` in line with the `integrate` function the build line already landed. It follows the convention used for `multiply` and `divide` and stays inside the scope set by the spec and the docs playbook. The hawkscan post-commit hook message noted in build.md and the reviews is tool output unrelated to this change. It was rightly ignored and doesn't block landing.

## Acceptance criteria
1. `integrate(f, a, b, n=1000)` count is 1: met. It is visible in the diff.
2. `trapezoidal` is on the function-list line: met. The diff shows it on line 4 with `add(a, b)`.
3. `ValueError` is on the same line: met. The diff shows it.
4. `and `integrate(...)`` = 1 and `and `divide(a, b)`` = 0: met. I reran the greps and got 1 and 0.
5. The `divide`, `add`, `subtract` and `multiply` parentheticals are unchanged: met. The diff shows they are word for word the same apart from the comma before `divide`.
6. Only `AGENTS.md` changed, and only the function-list sentence: met. I checked `git diff --stat main...HEAD`.
