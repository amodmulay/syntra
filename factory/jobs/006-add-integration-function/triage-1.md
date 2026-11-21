DECISION: NEEDS-INFO
LINE: build
RISK: low
SURFACES: none

## Summary
- Topic asks to "add integration function to the calculator" but gives no detail on what kind of integration or what inputs/outputs it should have.
- Every existing function (`add`, `subtract`, `multiply`, `divide`) takes two plain numbers and returns a number; a calculus-style integral needs a function to integrate plus bounds (and a choice of numerical method), which is a different shape of API than anything in this module.
- The global playbook scopes this project to "small, self-contained arithmetic operations" on the calculator — accepting a vague "integration" request risks building the wrong thing or over-scoping a single pass.
- Rather than guess at a design (numerical method, step count/tolerance, how the function-to-integrate is passed in), asking one clarifying question keeps this to a single, well-scoped build pass.

## Reasoning
`src/calculator.py` only has `add(a, b)`, `subtract(a, b)`, `multiply(a, b)`, `divide(a, b)` — all two-number arithmetic ops (see `tests/test_calculator.py` for the matching test shape). "Integration" most plausibly means a numerical definite-integral helper, but that requires design decisions (what gets passed in: a callable plus bounds? which numerical method — trapezoidal, Simpson's? how many steps/what tolerance?) that the one-line topic doesn't settle and that the code gives no precedent for, so this isn't a case where "the obvious reading" is clear enough to just pick.

## Open questions
1. By "integration function," do you mean a numerical definite integral — i.e. a function like `integrate(f, a, b)` that approximates ∫ f(x) dx from a to b — and if so, is a simple trapezoidal-rule approximation with a reasonable default step count acceptable?
