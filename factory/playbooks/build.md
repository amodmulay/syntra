# Playbook: build

Read alongside `factory/playbooks/_global.md`, which takes precedence
wherever the two disagree. This is what defines the `build` line's scope for
triage, the boundary the builder treats as binding alongside
`protected_paths`, and the first place the approver looks for anything that
must escalate.

## What belongs on this line

Working changes to Syntra's factory scripts, configuration, dashboard,
playbooks and Claude Code agents, plus changes to the calculator sample in
`src/` and `tests/`. Keep each topic scoped to one behavior and verify it
with `factory/checks.sh`.

## What doesn't belong here

- Documentation-only requests — those belong on the `docs` line; triage
  should route them there directly instead of accepting them onto `build`.
- Anything in "Never do this" in the global playbook.
- A topic that's really several unrelated changes bundled together. Triage
  should carve off the smallest useful slice and leave the rest unscoped.

## Always escalate (in addition to the global list)

Changes to job state transitions are high impact: include focused validation
and request security review. Never edit runtime state files under
`factory/jobs/` directly.
