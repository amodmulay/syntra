# Add subtract(a, b) to the calculator

> Job 001-add-a-subtract-function, pass 01-build

## Summary
- Add a `subtract(a, b)` function to `src/calculator.py` that returns `a - b`.
- Copy the existing `add` function's style: same signature shape, a one-line docstring, a single return.
- Add a `test_subtract` method to `TestCalculator` in `tests/test_calculator.py`, right after `test_add`.
- Change only those two files. Nothing in docs or the factory changes.

## Background
- `src/calculator.py` has a module docstring and a single function:
  ```python
  def add(a, b):
      """Return the sum of a and b."""
      return a + b
  ```
  Top-level definitions are separated by two blank lines (PEP 8). The file ends with a newline.
- `tests/test_calculator.py` puts `src/` on `sys.path`, then runs `from calculator import add`. It defines `class TestCalculator(unittest.TestCase)` with one method, `test_add`. That method makes two `assertEqual` calls: `add(2, 3) == 5` and `add(-1, 1) == 0`.
- Checks (`factory/checks.sh`, also listed in `AGENTS.md` under Validation): `python3 -m py_compile src/*.py && python3 -m unittest discover -s tests -v`. Everything uses the standard library only.
- No docs (`AGENTS.md`, `README.md`, `DESIGN.md`, `INSTALL.md`) list the calculator's functions, so this change needs no doc updates.

## Must-haves
1. `src/calculator.py` defines `subtract(a, b)` directly after `add`, with two blank lines between them. It returns `a - b`.
2. `subtract` has a one-line docstring that follows the `add` pattern: `"""Return the difference of a and b."""`.
3. `add`, the module docstring and everything else already in `src/calculator.py` stay exactly as they are.
4. In `tests/test_calculator.py`, the import becomes `from calculator import add, subtract`.
5. `TestCalculator` gets a new `test_subtract` method directly after `test_add`, written in the same style: two `assertEqual` calls with representative cases. One of them must produce a negative result, which proves the operand order is `a - b`. Suggested cases: `subtract(5, 3) == 2` and `subtract(1, 3) == -2`.
6. `test_add` stays exactly as it is.

## Acceptance criteria
1. Run `python3 -c "import sys; sys.path.insert(0, 'src'); from calculator import subtract; print(subtract(5, 3), subtract(1, 3))"` from the worktree root. It prints `2 -2`.
2. Run `python3 -c "import sys; sys.path.insert(0, 'src'); import calculator; print(calculator.subtract.__doc__)"`. It prints `Return the difference of a and b.`
3. Run `python3 -m unittest discover -s tests -v`. The output lists `test_add` and `test_subtract`, both `ok`, and ends with `OK` after 2 tests.
4. Run `git diff --name-only main...HEAD`. It lists only `src/calculator.py` and `tests/test_calculator.py`.
5. Run `git diff main...HEAD -- src/calculator.py`. It shows only added lines: no line of `add` or the module docstring is removed or changed.
6. Temporary manual check (do not commit): change `subtract` to return `b - a` and run the tests. `test_subtract` must fail. This confirms the test actually pins the operand order.

## Explicitly excluded
- No other operations (multiply, divide, etc.), and no input validation, type hints or type checks that `add` doesn't have.
- No changes to the module docstring, to `add` or to `test_add`.
- No new files, and no changes to any doc (`README.md`, `AGENTS.md`, `DESIGN.md`, `INSTALL.md`). Any doc follow-up belongs to the `docs` line's handoff pass.
- No changes to anything under `factory/` or `.claude/` (these are protected paths), including `factory/checks.sh`.
- No dependencies, no test framework change (stay on `unittest`), no CI config.

## Judgment calls
- **Docstring wording: "Return the difference of a and b."** This is the closest parallel to `add`'s "Return the sum of a and b." The `a - b` order is already pinned by the code and the tests, so the docstring doesn't need to spell it out.
- **One test case must give a negative result.** Without it, swapped operands could still pass for symmetric inputs. The negative case makes the test enforce `a - b` while still matching `test_add`'s two-assertion shape.
- **No doc updates in this pass.** No current doc lists the calculator's functions. The configured `docs` handoff can decide whether anything needs mentioning.
