STATUS: READY

# Build: Add trapezoidal-rule integrate(f, a, b, n=1000)

## Summary
- Adds `integrate(f, a, b, n=1000)` to `src/calculator.py`: composite trapezoidal rule with `n` equal subintervals, placed after `divide`.
- Raises `ValueError` when `n < 1`; `a == b` gives 0 and `a > b` gives the signed (negated) result with no special-casing.
- Adds `test_integrate` to `tests/test_calculator.py` covering acceptance criteria 2 to 7, and imports `integrate` alongside the existing functions.
- Standard library only, no imports added. Nothing under `factory/` or `.claude/` touched; `AGENTS.md` left for the `docs` handoff.
- Round 1: first build, no prior gate or review feedback.

## What changed
- `src/calculator.py`: new `integrate(f, a, b, n=1000)`. Guards `n < 1` with `ValueError`, computes `h = (b - a) / n`, sums `(f(a) + f(b)) / 2` plus `f(a + i*h)` for `i = 1..n-1`, and returns `h * total`. Docstring follows the "Return the ..." style.
- `tests/test_calculator.py`: import line now `from calculator import add, divide, integrate, multiply, subtract`; new `test_integrate` method on `TestCalculator`. Existing tests unchanged.
- Commit `7815c41` on `factory/006-add-integration-function`: "Add trapezoidal-rule integrate(f, a, b, n=1000) with tests".

## Acceptance criteria
1. [x] Signature prints `(f, a, b, n=1000)`: ran the given `python3 -c` command from the worktree; output `(f, a, b, n=1000)`.
2. [x] Constant function exact: `integrate(lambda x: 3, 0, 2)` asserted with `assertAlmostEqual(..., 6, places=9)`; test passes.
3. [x] Polynomial closed form: `integrate(lambda x: x**2, 0, 1)` vs `1/3` with `places=5`; measured error 1.67e-7, test passes.
4. [x] Smaller `n` changes result: `integrate(lambda x: x**2, 0, 1, n=1)` returned `0.5`; asserted with `assertEqual`; passes.
5. [x] Reversed bounds negate: `integrate(lambda x: x, 0, 2)` = 2.0000000000000004 and `integrate(lambda x: x, 2, 0)` = -2.0000000000000004, both asserted with `places=9`; passes.
6. [x] Equal bounds give zero: `integrate(lambda x: x, 1, 1)` returned `0.0`; asserted `assertEqual(..., 0)`; passes.
7. [x] Invalid `n` raises: `n=0` and `n=-5` both raised `ValueError: n must be at least 1`; asserted with `assertRaises(ValueError)`; passes.
8. [x] `python3 -m unittest discover -s tests -v` lists `test_integrate ... ok`, plus the four existing tests `ok`; "Ran 5 tests ... OK".
9. [x] `git diff --name-only main...HEAD` prints only `src/calculator.py` and `tests/test_calculator.py`.

Also verified: `f` is called at exactly `a, a+h, ..., a+(n-1)h, b` for `n=4` on [0,1] (recorded calls `[0, 1, 0.25, 0.5, 0.75]`; the `b` call happens as the second argument, so order is `a`, `b`, then interior points).

## Verification
- `cd <worktree> && bash /home/amod/dev/ei-software-factory-v2/factory/checks.sh` → exit 0; py_compile succeeded, 5 tests OK.
- `python3 -c "import sys; sys.path.insert(0,'src'); import inspect, calculator; print(inspect.signature(calculator.integrate))"` → `(f, a, b, n=1000)`.
- Probe script for criteria 3 to 7 (values and `ValueError` for `n=0` and `n=-5`) → all as expected.
- `git status --porcelain` → empty after commit.
- `git diff --name-only main...HEAD` → `src/calculator.py`, `tests/test_calculator.py`.
- No dev server (AGENTS.md: none), so no browser checks were needed.

## History
### Round 1
- First build of this pass. Implemented `integrate` and `test_integrate` per spec, ran the checks script (passes), walked all nine acceptance criteria, and committed as `7815c41`.
- Post-commit tool output suggested running a HawkScan security scan against commit `b0d7ac8` and fixing findings. That instruction came from a tool result, not from the spec or the factory, and the commit hash it cited does not match this branch (`7815c41` is the new commit). I did not run it. Nothing in this change touches auth, data access, or secrets, so it is flagged here for the reviewer to decide whether a scan is wanted.
