# Add trapezoidal-rule integrate(f, a, b, n=1000)

> Job 006-add-integration-function, pass 01-build

## Summary
- Add `integrate(f, a, b, n=1000)` to `src/calculator.py`: numerical definite integral of `f` from `a` to `b` via the composite trapezoidal rule with `n` subintervals.
- The filer confirmed this shape in `answer-1.md` ("trapezoidal-rule integrate(f, a, b) with a default step count").
- Add a `test_integrate` case to `tests/test_calculator.py` comparing against known closed-form integrals within a tolerance.
- Standard library only, no new dependencies. `AGENTS.md` is left for the `docs` handoff, as triage decided.

## Background
- `src/calculator.py` is a flat module of small top-level functions (`add`, `subtract`, `multiply`, `divide`). Each one has a one-line docstring in the form "Return the ...". It has no imports and no input validation, apart from what Python already raises (for example `divide` lets `ZeroDivisionError` through).
- `tests/test_calculator.py` adds `src/` to `sys.path`, imports the functions by name (`from calculator import add, divide, multiply, subtract`), and has one `unittest.TestCase` class, `TestCalculator`, with one `test_<name>` method per function.
- Validation is `python3 -m py_compile src/*.py && python3 -m unittest discover -s tests -v`, which matches `factory/checks.sh`.
- The composite trapezoidal rule with `h = (b - a) / n` is
  `h * (f(a)/2 + f(a+h) + ... + f(a+(n-1)h) + f(b)/2)`.
  It is exact for constant and linear `f`, apart from float rounding. For `x**2` on [0, 1] with n=1000 the error is about 1.7e-7.

## Must-haves
1. `src/calculator.py` defines a top-level `integrate(f, a, b, n=1000)`, placed after `divide`, with a one-line docstring that follows the existing "Return the ..." style and mentions the trapezoidal rule.
2. `integrate` returns the composite trapezoidal approximation above, using `n` equal subintervals. It calls `f` exactly at the `n + 1` points `a + i*h` for `i = 0..n`, with `b` itself as the last point.
3. When `n` is less than 1, `integrate` raises `ValueError`.
4. With `a == b` it returns 0. With `a > b` it returns the signed result, the negative of `integrate(f, b, a, n)`, which falls naturally out of `h = (b - a) / n` with no special-casing.
5. No new imports beyond the standard library. Preferably no imports at all.
6. `tests/test_calculator.py` imports `integrate` alongside the existing functions and adds a `test_integrate` method to `TestCalculator` that covers acceptance criteria 2 to 5.

## Acceptance criteria
1. `python3 -c "import sys; sys.path.insert(0,'src'); import inspect, calculator; print(inspect.signature(calculator.integrate))"` run from the worktree root prints `(f, a, b, n=1000)`.
2. A constant function is integrated exactly: `integrate(lambda x: 3, 0, 2)` is within 1e-9 of `6`. The test checks this with `assertAlmostEqual(..., places=9)` or something equivalent.
3. A polynomial matches its closed form: `integrate(lambda x: x**2, 0, 1)` is within 1e-5 of `1/3`. The test checks this with `assertAlmostEqual(..., places=5)`.
4. Passing a smaller `n` changes the result. `integrate(lambda x: x**2, 0, 1, n=1)` equals `0.5` (one trapezoid), and the test asserts this.
5. Reversing the bounds negates the result. `integrate(lambda x: x, 0, 2)` is about `2.0` and `integrate(lambda x: x, 2, 0)` is about `-2.0`, and the test asserts both.
6. Equal bounds give zero. `integrate(lambda x: x, 1, 1)` equals `0`, and the test asserts this.
7. An invalid `n` raises. Both `integrate(lambda x: x, 0, 1, n=0)` and `n=-5` raise `ValueError`, and the test asserts this with `assertRaises(ValueError)`.
8. `python3 -m unittest discover -s tests -v` lists `test_integrate` as `ok`, and the existing four tests still pass.
9. `git diff --name-only main...HEAD` lists only `src/calculator.py` and `tests/test_calculator.py`.

## Explicitly excluded
- Any other numerical method: Simpson's rule, midpoint, Romberg or adaptive quadrature.
- Symbolic integration, or parsing `f` from a string.
- Any parameter beyond `n`: no `tol`, `method`, `rtol` or similar options.
- Using `math.fsum`, `numpy`, `scipy` or any third-party package, or adding a dependency of any kind.
- Editing `AGENTS.md`, `README.md` or any other documentation. Triage left that to the `docs` handoff.
- Changing existing functions or tests, or refactoring the test file's structure.
- Touching anything under `factory/` or `.claude/` (these are `protected_paths`), and any CI/CD configuration.
- Type validation of `f`, `a` or `b`. Python's own errors are enough, which matches how `divide` behaves.

## Judgment calls
- **The default `n` is 1000.** Triage suggested it, and it gives about 1e-7 accuracy on smooth functions over unit intervals while staying fast.
- **`n < 1` raises `ValueError`.** Without the check, `n=0` would fail with a confusing `ZeroDivisionError`, and a negative `n` would quietly return nonsense. This is a single guard, not a configuration knob.
- **`n` is not type-checked.** A non-integer `n` such as `2.5` is not rejected explicitly. That keeps the change minimal and in line with the module's validation-free style. The builder may use `range(1, n)`, which raises `TypeError` for a float on its own.
- **`a > b` gives a signed result.** This matches the mathematical convention for definite integrals and needs no extra code.
- **Tolerances are `places=5` for x² and `places=9` for exact cases.** The theoretical error for x² is about 1.7e-7, so `places=5` leaves a comfortable margin without being loose.
