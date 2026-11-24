<!-- factory-issue: 4 -->
# Fast path for small, low-risk jobs

A one-line calculator change runs the same chain as a risky change: triage, spec, build, gate, up to four reviewers, approve, then a docs handoff. That takes 4 to 6 minutes at best and much longer when reviewers ask for rework. Add a fast path for jobs that triage rates RISK low and that touch only `src/` and `tests/`: skip the separate spec step (triage's scope becomes the spec) and run a single reviewer (`code`). Anything touching the factory scripts, dashboard, playbooks or the job state machine keeps the full pipeline. Make the fast path configurable in `factory/config.json` so it can be turned off, and document it in AGENTS.md and the factory skill. Add focused tests for the routing decision.
