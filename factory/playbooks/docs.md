# Playbook: docs

Read alongside `factory/playbooks/_global.md`, which takes precedence
wherever the two disagree. This line only ever starts as a handoff from
another line (see `handoff` in `factory/config.json`) — it keeps the written
record in step with work another line already landed.

## What belongs on this line

Updating `AGENTS.md`/`CLAUDE.md`, READMEs, and any other doc this project
keeps, so they describe the codebase as it now actually behaves after the
line that handed off here landed its change.

## What doesn't belong here

- Any change to application code, tests, or configuration. If a doc update
  can't be made without also touching code, that's a sign the triage line
  for the original topic was wrong — flag it rather than reaching outside
  docs to fix it.
- Rewriting documentation that has nothing to do with what was just landed.
  Scope this pass to the handoff it's responding to.

## Always escalate (in addition to the global list)

- A doc change that would alter a public commitment — a documented SLA, a
  pricing page, terms that read as a promise to users.

## Self-documentation

Syntra's docs can be updated through ordinary factory issues. Keep setup,
invocation, and project-specific behavior consistent across README.md,
INSTALL.md, AGENTS.md, and CLAUDE.md.
