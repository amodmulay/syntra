# Add multiply(a, b) to the calculator

> Job 002-add-a-multiply-function, pass 01-build

## Summary
- Add `multiply(a, b)` to `src/calculator.py`. It returns `a * b`.
- Copy the shape of the existing `add` and `subtract`: a short function with a one-line docstring.
- Add `test_multiply` to `tests/test_calculator.py`, following the pattern of `test_add` and `test_subtract`.
- Change only those two files. The `docs` line, which this job hands off to, updates the documentation.

## Background
- `src/calculator.py` starts with a one-line module docstring. It then defines two top-level functions, `add(a, b)` ("Return the sum of a and b.") and `subtract(a, b)` ("Return the difference of a and b."). Each has a one-line docstring and a single `return` statement, and two blank lines separate the top-level definitions.
- `tests/test_calculator.py` puts `src/` on `sys.path` and then runs `from calculator import add, subtract`. It defines one `unittest.TestCase` class, `TestCalculator`, with one method per function (`test_add`, `test_subtract`). Each method makes two `assertEqual` calls, one with an ordinary case and one with a negative number.
- Checks run through `factory/checks.sh`: `python3 -m py_compile src/*.py && python3 -m unittest discover -s tests -v`.
- `AGENTS.md` currently describes the module's functions as `add(a, b)` and `subtract(a, b)`. Triage limits this pass to the two files above. In `factory/config.json`, the `build` line's `handoff` is set to `docs`, so a later docs pass will update `AGENTS.md`.

## Must-haves
1. `src/calculator.py` defines a top-level `multiply(a, b)` after `subtract`. It returns `a * b` and has the one-line docstring `"""Return the product of a and b."""`, written in the same style as its neighbours. Two blank lines separate it from `subtract`.
2. `tests/test_calculator.py` imports `multiply` on the existing import line, so the line reads `from calculator import add, multiply, subtract` or `from calculator import add, subtract, multiply`.
3. `TestCalculator` gains a `test_multiply` method after `test_subtract`, with at least two `assertEqual` assertions:
   - one case with two positive numbers, e.g. `multiply(2, 3) == 6`
   - one case with zero or a negative number, e.g. `multiply(-2, 3) == -6` or `multiply(5, 0) == 0`
4. `add` and `subtract` and their tests stay exactly as they are.

## Acceptance criteria
1. From the worktree root, `python3 -c "import sys; sys.path.insert(0, 'src'); from calculator import multiply; print(multiply(2, 3), multiply(-2, 3), multiply(5, 0))"` prints `6 -6 0`.
2. `python3 -c "import sys; sys.path.insert(0, 'src'); import calculator; print(calculator.multiply.__doc__)"` prints `Return the product of a and b.`
3. `python3 -m unittest discover -s tests -v` lists `test_multiply (test_calculator.TestCalculator...) ... ok` along with `test_add` and `test_subtract`, and ends with `OK` (3 tests).
4. `git diff --name-only main...HEAD` lists only `src/calculator.py` and `tests/test_calculator.py`.
5. `git diff main...HEAD -- src/calculator.py` shows only lines added for `multiply` and no changed or removed lines in `add`, `subtract` or the module docstring.

## Explicitly excluded
- Changes to any file other than `src/calculator.py` and `tests/test_calculator.py`. That includes `AGENTS.md`, `README.md` and `DESIGN.md`, which the `docs` line handles after handoff.
- Any file under `factory/` or `.claude/` (these are `protected_paths`).
- Other operations, such as divide, power or modulo.
- Type checking, input validation, type hints, or special handling for non-numeric inputs, overflow or floats beyond what `a * b` already does.
- Refactoring or reformatting `add`, `subtract` or the existing tests.
- New dependencies, a test framework other than `unittest`, or CI or config changes.

## Judgment calls
- **Docstring wording "Return the product of a and b."**: mirrors "Return the sum of a and b." and "Return the difference of a and b." exactly.
- **No AGENTS.md update in this pass**: the usual rule is to fold doc updates into the spec, but triage restricts this pass to two files and the `build` line hands off to `docs`, which exists for exactly this.
- **Test cases**: two assertions to match the existing tests (an ordinary case plus a negative or zero case), rather than a bigger table of cases.
- **Placement**: append after `subtract` and `test_subtract` to keep the diff purely additive.
