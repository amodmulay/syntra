DECISION: REJECT
LINE: build
RISK: low
SURFACES: none
RESCOPED: no

## Summary
- Topic asks to add an addition function to the calculator.
- `add(a, b)` already exists in `src/calculator.py`, is documented in `AGENTS.md`, and has passing tests in `tests/test_calculator.py`.
- Work is already done; nothing left to build.

## What this covers
N/A — rejected.

## Reasoning
`src/calculator.py` already defines `add(a, b)` returning `a + b`, `tests/test_calculator.py` has `test_add` covering it, and `AGENTS.md` already lists `add(a, b)` in the function list. The request is already fully satisfied in the base branch, so there is no remaining work for a build pass.

## Open questions
None.
