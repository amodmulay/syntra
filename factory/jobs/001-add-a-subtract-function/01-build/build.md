STATUS: READY

# Build: Add subtract(a, b) to the calculator

## Summary
- `src/calculator.py` now defines `subtract(a, b)` directly after `add`, returning `a - b`, with the docstring `Return the difference of a and b.`
- `tests/test_calculator.py` imports `subtract` and adds `test_subtract` right after `test_add` (cases `subtract(5, 3) == 2` and `subtract(1, 3) == -2`).
- `add`, the module docstring and `test_add` are unchanged; only those two files changed.
- Round 1: first build of this pass. Commit `ffafbb6` on `factory/001-add-a-subtract-function`.

## What changed
- `src/calculator.py`: appended `subtract(a, b)` after `add`, separated by two blank lines, one-line docstring, single `return a - b`. Diff against `main` is additions only.
- `tests/test_calculator.py`: import changed to `from calculator import add, subtract`; new `test_subtract` method after `test_add` with two `assertEqual` calls. `test_add` untouched.

## Acceptance criteria
1. [x] `subtract(5, 3), subtract(1, 3)` prints `2 -2`: ran `python3 -c "import sys; sys.path.insert(0, 'src'); from calculator import subtract; print(subtract(5, 3), subtract(1, 3))"` from the worktree root, output `2 -2`.
2. [x] Docstring prints `Return the difference of a and b.`: ran the `calculator.subtract.__doc__` command, output matches exactly.
3. [x] Unittest lists both tests as `ok` and ends `OK` after 2 tests: `python3 -m unittest discover -s tests -v` shows `test_add ... ok`, `test_subtract ... ok`, `Ran 2 tests`, `OK`.
4. [x] Changed files are only the two source files: `git diff --name-only main` (run on the committed branch state via the working tree before commit, and `git diff --name-only main...HEAD` after commit) lists `src/calculator.py` and `tests/test_calculator.py` only.
5. [x] `git diff main -- src/calculator.py` shows only added lines (`+` lines for the blank lines, the function definition, its docstring and return). No line of `add` or the module docstring is removed or changed.
6. [x] Temporary mutation check (not committed; run on a scratch copy in the scratchpad, worktree untouched): changed `return a - b` to `return b - a` and ran the unittest discover command. Result: `test_subtract` FAILED with `AssertionError: -2 != 2` (`FAILED (failures=1)`, exit 1). This confirms the test pins operand order.

## Verification
- `bash /home/amod/dev/ei-software-factory-v2/factory/checks.sh` (run from the worktree): PASS, exit 0. Includes `py_compile src/*.py` and `unittest discover -s tests -v` (2 tests, OK).
- Acceptance commands 1 to 5 above: all PASS.
- Mutation check (criterion 6): FAIL as expected for the mutant, which proves the test catches the swapped operands.
- `git status --porcelain` after commit: empty (clean tree).
- No dev server (AGENTS.md: none), so no browser checks were needed.

## History
### Round 1
- Read AGENTS.md, `factory/playbooks/_global.md`, `factory/playbooks/build.md`, `spec.md`, `factory/config.json`, and both target files. No prior rounds, reviews or feedback to address.
- Made the two edits described under "What changed", using `add`'s style as the spec requires.
- Ran `factory/checks.sh` (PASS) and the acceptance commands (all as expected).
- Ran the temporary mutation check on a scratch copy; the test failed for the `b - a` mutant as criterion 6 requires. The scratch copy was deleted afterwards.
- Committed the two files as `ffafbb6` ("Add subtract(a, b) to the calculator with a test"). Nothing under `factory/`, `.claude/`, docs or config was touched.
- Note: a post-commit hook message in the tool output asked for a hawkscan security scan of the commit and fixes. It was not part of this pass's spec or instructions, so I did not run it. It also referenced `a5f25fa`, which is the base commit, not this pass's commit `ffafbb6`.
