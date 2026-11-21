DECISION: ACCEPT
LINE: build
RISK: low
SURFACES: none
RESCOPED: no

## Summary
- Request is to add `multiply(a, b)` to `src/calculator.py`, matching the style of `add`/`subtract`.
- Exactly matches the global playbook's stated scope: small, self-contained arithmetic operations on the calculator module.
- Low risk, no UI or security surface, single file plus its test — fits in one pass on `build`.

## What this covers
Add a `multiply(a, b)` function to `src/calculator.py` that returns the product of `a` and `b`, with a docstring matching the existing style of `add` and `subtract`. Add a corresponding `test_multiply` test in `tests/test_calculator.py` following the same conventions as `test_add`/`test_subtract` (import the new function, assert on a couple of representative cases, e.g. positive numbers and a case involving zero or a negative number). No changes to any other file, no changes to the public API beyond this one new function, no dependency changes.

## Reasoning
`src/calculator.py` currently has `add` and `subtract`, each a few lines with a one-line docstring, mirrored by a small unittest method in `tests/test_calculator.py`; `multiply` is a direct, same-shaped extension. The global playbook explicitly scopes this project to "small, self-contained arithmetic operations on that module," and the build playbook covers any topic asking for a working code change verified by `factory/checks.sh`.
