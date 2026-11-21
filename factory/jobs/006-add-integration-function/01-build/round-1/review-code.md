VERDICT: PASS

## Summary
- `integrate(f, a, b, n=1000)` in `src/calculator.py` matches the spec: composite trapezoidal rule, `h = (b - a) / n`, `f` evaluated at `a`, `b` and the interior points, `ValueError` for `n < 1`, and no special-casing for `a == b` or `a > b`.
- The docstring follows the "Return the ..." style of the neighbouring functions, and no imports were added.
- `test_integrate` covers the spec's acceptance criteria 2 to 7 with tolerances in line with the spec. The existing four tests are untouched.
- The diff touches only `src/calculator.py` and `tests/test_calculator.py`. The commit is a single line, the worktree is clean, and the checks log shows 5 tests passing.
- Nothing blocking. The remaining points are minor and noted below.

## Issues
None.

## Other observations
- `tests/test_calculator.py`: must-have 2 says `f` is called at exactly the `n + 1` points. The build verified this by hand, but no test asserts it. A small recording-lambda test would lock it in. Optional, since the spec's acceptance criteria do not require it.
- `src/calculator.py`: with `n` a float such as `2.5`, the `n < 1` guard passes and `range(1, n)` raises `TypeError`. The spec accepts this, so no change is needed.
- `factory/jobs/006-add-integration-function/01-build/build.md` (History, Round 1) says a tool result asked for a HawkScan scan of commit `b0d7ac8`. The builder did not run it, and this review does not act on it either. It is not part of the spec, and the reviewer or user should decide whether they want such a scan.
