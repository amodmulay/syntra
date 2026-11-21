DECISION: ACCEPT
LINE: build
RISK: low
SURFACES: none
RESCOPED: no

## Summary
- Request adds `divide(a, b)` to `src/calculator.py`, matching the existing style of `add`, `subtract`, and `multiply`.
- Small, self-contained arithmetic function on a module built exactly for this kind of exercise — squarely in scope per the global playbook.
- Topic leaves division-by-zero handling to the builder's judgment; spec/build should pick a sensible, well-tested behavior (e.g. raise `ZeroDivisionError` naturally, or a deliberate explicit check with a clear error message) and cover it with a test.
- No security or UI surfaces involved; risk is low and easily verified by `factory/checks.sh`.

## What this covers
Add a `divide(a, b)` function to `src/calculator.py` with a docstring consistent with the other three functions, plus corresponding tests in `tests/test_calculator.py` following the existing `TestCalculator` pattern (normal division cases, including a case with a negative operand). The builder should decide and document how division by zero is handled (letting Python's natural `ZeroDivisionError` propagate is the simplest consistent choice, but an explicit guard is also acceptable) and add a test asserting that behavior. No changes to `AGENTS.md` are needed on this pass — the `docs` line handoff will update the function list afterward, matching how `multiply` was previously landed.

## Reasoning
This mirrors the three prior accepted/built functions (`add`, `subtract`, `multiply` in `src/calculator.py` and `tests/test_calculator.py`), is explicitly the kind of small arithmetic operation the global playbook calls in-scope, and requires no changes outside `src/` and `tests/`. Division by zero is a minor implementation decision, not a blocking ambiguity, so no NEEDS-INFO is warranted.
