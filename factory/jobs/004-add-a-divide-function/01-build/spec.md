# Add divide(a, b) to the calculator

> Job 004-add-a-divide-function, pass 01-build

## Summary
- Add `divide(a, b)` to `src/calculator.py`, returning `a / b`, in the same one-line-docstring style as `add`, `subtract` and `multiply`.
- Division by zero raises Python's built-in `ZeroDivisionError`. Python already does this, so no guard code is needed.
- Add a `test_divide` method to `TestCalculator` in `tests/test_calculator.py`. It covers normal cases, a negative operand, and the zero-divisor error.
- AGENTS.md is not touched on this pass. The `docs` handoff updates the function list afterwards, the same way `multiply` was landed.

## Background
- `src/calculator.py` has three module-level functions: `add`, `subtract` and `multiply`. Each has a one-line docstring of the form `"""Return the <noun> of a and b."""` and a single `return a <op> b` line. There is no input validation and no type checking.
- `tests/test_calculator.py` puts `src/` on `sys.path` and imports the functions by name with `from calculator import add, multiply, subtract`. The names are in alphabetical order. The file has one `unittest.TestCase` class, `TestCalculator`, with one `test_<name>` method per function. Each method holds two `assertEqual` calls: one ordinary case and one with a negative operand or result.
- The repo's validation, and `factory/checks.sh`, both run `python3 -m py_compile src/*.py && python3 -m unittest discover -s tests -v`.
- The previous function landed in two steps: commit 438c158 changed the code and tests, then commit cf0cc93 updated AGENTS.md through the docs line. This pass is the build half of that pattern.

## Must-haves
1. `src/calculator.py` defines `divide(a, b)` after `multiply`, with the docstring `"""Return the quotient of a and b."""` and the body `return a / b`. It uses true division, not `//`.
2. `divide(a, 0)` raises `ZeroDivisionError`. Python's own `/` operator raises it, so the code has no explicit check, no try/except and no custom message.
3. The import line in `tests/test_calculator.py` becomes `from calculator import add, divide, multiply, subtract`, keeping alphabetical order.
4. `TestCalculator` gains a `test_divide` method, placed after `test_multiply`, that asserts:
   - `divide(6, 3) == 2`
   - `divide(-6, 3) == -2`
   - `divide(1, 0)` raises `ZeroDivisionError`, checked with `self.assertRaises(ZeroDivisionError)`
5. Only `src/calculator.py` and `tests/test_calculator.py` change.

## Acceptance criteria
1. Run `cd <worktree> && python3 -c "import sys; sys.path.insert(0,'src'); from calculator import divide; print(divide(6, 3), divide(-6, 3), divide(7, 2))"`. It prints `2.0 -2.0 3.5`.
2. Run `cd <worktree> && python3 -c "import sys; sys.path.insert(0,'src'); from calculator import divide; divide(1, 0)"`. It exits non-zero, and the last line of stderr starts with `ZeroDivisionError`.
3. Run `cd <worktree> && python3 -c "import sys; sys.path.insert(0,'src'); import calculator; print(calculator.divide.__doc__)"`. It prints `Return the quotient of a and b.`
4. Run `cd <worktree> && python3 -m unittest discover -s tests -v`. The output lists `test_divide (test_calculator.TestCalculator...) ... ok`, and the run ends with `OK` and 4 tests.
5. Read `tests/test_calculator.py`. `test_divide` contains `assertRaises(ZeroDivisionError)` around a `divide(..., 0)` call, and it has equality checks for one positive case and one negative-operand case.
6. Run `cd <worktree> && git diff --name-only main...HEAD`. It lists exactly `src/calculator.py` and `tests/test_calculator.py`.

## Explicitly excluded
- Any change to `AGENTS.md`, `README.md` or other docs. The `docs` line handoff owns that.
- Any explicit zero check, custom exception class, custom error message, or returning `None`, `inf` or `nan` for a zero divisor.
- Floor or integer division (`//`), rounding, a `Decimal` or `Fraction` result, or type validation or coercion of the inputs.
- Refactoring or changing `add`, `subtract`, `multiply` or their tests.
- Any other new operations, such as modulo or power.
- Any file under `factory/` or `.claude/` (protected paths), CI config, or dependencies.

## Judgment calls
- **Division by zero propagates Python's native `ZeroDivisionError`.** Triage called this the simplest consistent choice. It keeps `divide` a one-line function like its siblings, it is the error Python callers already expect, and it is easy to test with `assertRaises`.
- **True division (`/`), so results are floats.** The topic says "divide two numbers", and true division is the mathematically expected meaning. Tests compare with `==` against ints (`2 == 2.0`), so they stay consistent with the existing assertion style.
- **Docstring says "quotient"**, which matches the "sum", "difference" and "product" wording of the other functions.
