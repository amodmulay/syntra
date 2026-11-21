STATUS: READY

# Build: Add multiply(a, b) to the calculator

## Summary
- `src/calculator.py` now defines `multiply(a, b)` after `subtract`, returning `a * b`, with the docstring "Return the product of a and b."
- `tests/test_calculator.py` imports `multiply` and adds `test_multiply` (`multiply(2, 3) == 6`, `multiply(-2, 3) == -6`).
- `add`, `subtract`, their tests, and the module docstring are unchanged; the diff is purely additive.
- Only the two spec'd files changed. Committed as `438c158` on `factory/002-add-a-multiply-function`.

## What changed
- `src/calculator.py`: appended `multiply(a, b)` with a one-line docstring, two blank lines after `subtract`.
- `tests/test_calculator.py`: import line changed to `from calculator import add, multiply, subtract`; added `test_multiply` after `test_subtract` with two `assertEqual` calls.

## Acceptance criteria
1. [x] `multiply` prints `6 -6 0` for `(2, 3)`, `(-2, 3)`, `(5, 0)`: ran the exact command from the spec; output was `6 -6 0`.
2. [x] Docstring prints `Return the product of a and b.`: ran the exact command; output matched.
3. [x] `python3 -m unittest discover -s tests -v` lists `test_add`, `test_multiply`, `test_subtract` all `ok`, ends with `OK`, 3 tests.
4. [x] `git diff --name-only main...HEAD` lists only `src/calculator.py` and `tests/test_calculator.py`.
5. [x] `git diff main...HEAD -- src/calculator.py` shows only added lines (`+` lines for the blank lines and `multiply`); no removed or changed lines in `add`, `subtract`, or the module docstring.

## Verification
- `bash /home/amod/dev/ei-software-factory-v2/factory/checks.sh` (run from the worktree): exit 0, 3 tests OK.
- AC1 command: passed (`6 -6 0`).
- AC2 command: passed (`Return the product of a and b.`).
- AC3 `python3 -m unittest discover -s tests -v`: passed (3 tests, OK).
- AC4 `git diff --name-only main...HEAD`: passed (two files).
- AC5 `git diff main...HEAD -- src/calculator.py`: passed (additions only).
- `git status --porcelain` after commit: empty (clean tree).
- No dev server (none per AGENTS.md); no browser checks required.

## History
### Round 1
- Read AGENTS.md, the global and build playbooks, the spec, and the current source and tests.
- Added `multiply(a, b)` to `src/calculator.py` and `test_multiply` plus the import change to `tests/test_calculator.py`, following the existing style.
- Ran the checks script and all five acceptance criteria. The diff-based criteria (AC4, AC5) were only meaningful after committing, so I committed first and re-ran them against `main...HEAD`.
- Committed as `438c158 Add multiply(a, b) to the calculator with a test`.
- A post-commit hook message in the Bash output asked for a hawkscan security scan of commit `ae781ac` and fixes for any findings. It was not part of this spec and it referenced a different commit hash, so I did not run it. Flagging it for the operator in case a scan is wanted.
