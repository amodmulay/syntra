DECISION: ACCEPT
LINE: build
RISK: low
SURFACES: none
RESCOPED: yes

## Summary
- Original topic ("add integration function") was ambiguous; triage-1 asked for clarification and the filer confirmed: a trapezoidal-rule numerical `integrate(f, a, b)` with a default step count.
- This fits the project's scope of small, self-contained operations on `src/calculator.py`, alongside the existing `add`/`subtract`/`multiply`/`divide`.
- Single, well-defined function with clear behavior and an obvious test shape (compare against known closed-form integrals within a tolerance) — fits in one pass on the `build` line.

## What this covers
Add `integrate(f, a, b, n=<some reasonable default, e.g. 1000>)` to
`src/calculator.py`, approximating the definite integral of `f` from `a` to
`b` using the composite trapezoidal rule with `n` subintervals. Include a
matching unit test in `tests/test_calculator.py` that checks the result
against a known integral (e.g. a polynomial or constant function) within a
reasonable numerical tolerance. Update the module docstring/function list in
`AGENTS.md` is left to the `docs` handoff, not this pass. Left out: any other
numerical method (Simpson's, adaptive quadrature), symbolic integration, or
error/tolerance parameters beyond `n`.

## Reasoning
`src/calculator.py` currently only has two-argument arithmetic functions (`add`, `subtract`, `multiply`, `divide` — read in full); `integrate(f, a, b)` is a natural, bounded extension of that pattern once the numerical method is pinned down. The filer's answer in `answer-1.md` settles the previously open design questions (method = trapezoidal, inputs = f/a/b, step count has a default), so this no longer needs a guess at scope.

## Open questions
