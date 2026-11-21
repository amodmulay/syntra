DECISION: ACCEPT
LINE: build
RISK: low
SURFACES: none
RESCOPED: no

## Summary
- Small, well-scoped request: add `subtract(a, b)` to `src/calculator.py` plus a matching test, mirroring the existing `add` function.
- Matches the project's stated purpose exactly — a minimal arithmetic operation on the calculator module used to exercise the factory.
- No protected paths, dependencies, auth, money, or migrations involved.
- Clear acceptance criteria already implied by the existing `add`/`test_add` pattern.

## What this covers
Add a `subtract(a, b)` function to `src/calculator.py`, following the same
style and one-line docstring convention as the existing `add` function
(`"""Return the sum of a and b."""` style), returning `a - b`. Add a
corresponding `test_subtract` method in `tests/test_calculator.py`, alongside
`test_add`, importing `subtract` and asserting correct behavior (e.g. a
couple of representative cases mirroring `test_add`'s style). Nothing else
changes — no changes to the module docstring, no new files, no changes to
`factory/checks.sh` or any other factory file.

## Reasoning
The request is a tiny, self-contained arithmetic operation on
`src/calculator.py`/`tests/test_calculator.py`, which is precisely what
`factory/playbooks/_global.md` describes as in scope for this project, and it
fits the `build` line per `factory/playbooks/build.md` (a code change
verified by `factory/checks.sh`). The existing `add`/`test_add` pair in
`src/calculator.py` and `tests/test_calculator.py` gives an unambiguous
template to mirror, so there's nothing to clarify.
