# Playbook: build

Read alongside `factory/playbooks/_global.md`, which takes precedence
wherever the two disagree. This is what defines the `build` line's scope for
triage, the boundary the builder treats as binding alongside
`protected_paths`, and the first place the approver looks for anything that
must escalate.

## What belongs on this line

<!-- Replace with the real shape of this project once there is one, e.g.:
     "Application code under src/, its tests, and the public API it exposes." -->

Any topic asking for a working code change: new behavior, a bug fix, a
refactor, performance work — anything that ends with the codebase doing
something it didn't do before, verified by `factory/checks.sh`.

## What doesn't belong here

- Documentation-only requests — those belong on the `docs` line; triage
  should route them there directly instead of accepting them onto `build`.
- Anything in "Never do this" in the global playbook.
- A topic that's really several unrelated changes bundled together. Triage
  should carve off the smallest useful slice and leave the rest unscoped.

## Always escalate (in addition to the global list)

<!-- Add anything specific to this project's codebase: its auth module, its
     payment integration, its data-access layer, wherever a mistake is
     expensive or hard to undo. -->

Nothing project-specific yet — tailor this once there's a real codebase to
reason about.
