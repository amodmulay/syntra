DECISION: REJECT
LINE: build
RISK: low
SURFACES: none

## Summary
- Topic asks for a sleek static graphical explainer of the "EI Software factory" concept itself, for presenting to teams/customers.
- This project's scope is a minimal calculator module (`src/calculator.py`), used only to exercise the factory end to end.
- The global playbook explicitly states topics should ask for small, self-contained arithmetic operations on that module, and that anything structural to the factory itself is out of scope for a `build` or `docs` job.
- This isn't a documentation update reflecting a merged build change either — it's a net-new marketing/explainer artifact about the factory concept, unrelated to the calculator's behavior.
- No rescoped slice of this request fits either line's mandate, so this is rejected outright rather than narrowed.

## Reasoning
`AGENTS.md` and `factory/playbooks/_global.md` both describe this repo's sole purpose as a minimal calculator module for exercising the factory, with factory-structural work explicitly carved out as something to be done via direct edit, not a topic. A "graphical view explaining the EI Software factory concept" is squarely about the factory's own concept/structure, not about `add`/`subtract` (or similar) behavior in `src/calculator.py`, so it falls outside both the `build` and `docs` lines' legitimate work.

## Open questions
None — this is rejected on scope grounds, not missing information.
