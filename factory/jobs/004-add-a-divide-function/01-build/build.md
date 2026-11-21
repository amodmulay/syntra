STATUS: READY

# Build: Add divide(a, b) to the calculator

## Summary
- `src/calculator.py` gains `divide(a, b)` after `multiply`, returning `a / b` with the docstring `"""Return the quotient of a and b."""`.
- Division by zero propagates Python's native `ZeroDivisionError`; no guard code was added.
- `tests/test_calculator.py` imports `divide` and adds `test_divide` after `test_multiply`, covering `6/3`, `-6/3` and the zero-divisor error.
- Round 1: first build of this pass. Committed as `cde56cb`. Only the two files above changed; AGENTS.md is untouched (left for the `docs` handoff).

## What changed
- `src/calculator.py`: added `def divide(a, b)` with docstring and `return a / b` after `multiply`.
- `tests/test_calculator.py`: import line is now `from calculator import add, divide, multiply, subtract`; added `TestCalculator.test_divide` asserting `divide(6, 3) == 2`, `divide(-6, 3) == -2`, and `assertRaises(ZeroDivisionError)` around `divide(1, 0)`.

## Acceptance criteria
1. [x] `divide(6, 3), divide(-6, 3), divide(7, 2)` prints the expected values: ran `python3 -c "...from calculator import divide; print(divide(6, 3), divide(-6, 3), divide(7, 2))"`, output `2.0 -2.0 3.5`.
2. [x] `divide(1, 0)` exits non-zero with a `ZeroDivisionError` last line: exit status 1, final stderr line `ZeroDivisionError: division by zero`.
3. [x] Docstring: `calculator.divide.__doc__` printed `Return the quotient of a and b.`
4. [x] `python3 -m unittest discover -s tests -v`: lists `test_divide (test_calculator.TestCalculator.test_divide) ... ok`, `Ran 4 tests`, ends with `OK`.
5. [x] `tests/test_calculator.py` `test_divide` contains `with self.assertRaises(ZeroDivisionError): divide(1, 0)` plus equality checks for a positive case (`6, 3`) and a negative-operand case (`-6, 3`).
6. [x] `git diff --name-only main...HEAD` lists exactly `src/calculator.py` and `tests/test_calculator.py`.

## Verification
- `bash /home/amod/dev/ei-software-factory-v2/factory/checks.sh` (run from the worktree): exit 0, 4 tests OK.
- AC1, AC2, AC3 commands as listed above: all produced the expected output.
- `python3 -m unittest discover -s tests -v`: 4 tests, OK.
- `git diff --name-only main...HEAD`: `src/calculator.py`, `tests/test_calculator.py`.
- `git status --porcelain` after commit: empty.
- No dev server (none per AGENTS.md); no browser checks needed.

## History
### Round 1
- First build for this pass. Read AGENTS.md, both playbooks, spec, and the existing source and tests.
- Added `divide` and its test exactly as the spec describes, then ran checks and all six acceptance criteria. All passed on the first run.
- Committed the two files as `cde56cb` ("Add divide(a, b) to the calculator with a test").
- Note: a post-commit hook message in the Bash output asked for a hawkscan security scan of the commit. It is not part of this build spec, so I did not run it. It also named a different commit hash (`cf0cc93`) than the one created here.
