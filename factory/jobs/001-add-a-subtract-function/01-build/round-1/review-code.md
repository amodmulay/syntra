VERDICT: PASS

## Summary
- `subtract(a, b)` is added directly after `add` with two blank lines between them, returns `a - b`, and has the spec's docstring `Return the difference of a and b.`
- `add`, the module docstring and `test_add` are untouched; the `src/calculator.py` diff against `main` is additions only.
- `test_subtract` sits right after `test_add`, uses the two suggested cases (`subtract(5, 3) == 2`, `subtract(1, 3) == -2`), and the negative case pins the `a - b` operand order.
- Only `src/calculator.py` and `tests/test_calculator.py` changed; nothing under `factory/`, `.claude/` or the docs was touched, and the working tree is clean.
- Round-1 checks (`factory/checks.sh`, exit 0, 2 tests OK) cover the change; I did not rerun them.

## Issues
None.

## Other observations
- `01-build/build.md` (History, Round 1) records a post-commit hook message asking for a hawkscan security scan, which the pass correctly did not act on. Worth a look at why that hook fires on this branch, since it also cited the base commit `a5f25fa` rather than `ffafbb6`. This does not affect the code.
- `build.md` acceptance item 4 is worded awkwardly ("run on the committed branch state via the working tree before commit"). The outcome is correct; no change needed.
