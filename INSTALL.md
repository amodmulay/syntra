# Installing this factory into another project

You're a coding agent asked to bring this factory into someone else's
repository. Copy what's generic, adapt what depends on their project, verify
it actually works, and report back. Do all of this from that project's root.
Don't clone this factory's own repo into theirs — pull only the files named
below.

The source is wherever the user points you: a local path to a checkout of
this repo, or a git URL. If it's a URL, `git clone --depth 1 <url> /tmp/<tmp>`
into a scratch directory first and copy out of that; if it's a local path,
copy directly from it.

## 0. Check the target project first

Stop and tell the user if any of these aren't true:

- It's a git repository with at least one commit on its default branch (a
  job's worktree branches from that commit; `factory/checks.sh` gets
  verified against it in step 3).
- `claude --version` is recent enough to run a Fable subagent (triage runs on
  `model: fable`).
- `python3 --version` is 3.10 or later — the scripts use only the standard
  library, nothing else.
- None of the paths in step 1 already exist in the target. If one does, show
  the user the clash and ask before overwriting it.

## 1. Copy these files unchanged

```
.claude/skills/factory/SKILL.md
.claude/agents/triage.md
.claude/agents/spec-writer.md
.claude/agents/builder.md
.claude/agents/reviewer-code.md
.claude/agents/reviewer-security.md
.claude/agents/reviewer-ux.md
.claude/agents/reviewer-ui.md
.claude/agents/approver.md
factory/config.json
factory/checks.sh
factory/bin/job
factory/bin/gate
factory/bin/route
factory/bin/pull
factory/dashboard.html
factory/playbooks/_global.md
factory/playbooks/build.md
factory/playbooks/docs.md
```

```bash
chmod +x factory/checks.sh factory/bin/job factory/bin/gate factory/bin/route factory/bin/pull
mkdir -p factory/inbox
```

Leave this factory's own `README.md`, `DESIGN.md`, `INSTALL.md` and `LICENSE`
(if any) behind — they describe this reference, not the project you're
installing into. Don't overwrite the target's own `AGENTS.md`; you'll add to
it in step 2 instead of replacing it.

## 2. Adapt everything project-specific

**`factory/checks.sh`.** Replace the placeholder with this project's actual
checks: install dependencies if a fresh worktree needs them, then lint,
typecheck, test and build — whichever of those the project has. Find the
real commands in its `AGENTS.md`/`CLAUDE.md`, `package.json` scripts,
`Makefile`, or `pyproject.toml`. It must be non-interactive, must never
rewrite files (no `--fix`, no snapshot updates), and must exit non-zero on
any real failure. Keep `set -euo pipefail` at the top.

**`factory/playbooks/_global.md` and `factory/playbooks/<line>.md`.** These
ship as templates and are the single most important thing to get right —
everything downstream (triage's accept/reject call, what the builder
refuses to touch, what the approver always escalates) defers to them. Write
in a real sentence or two what this project actually is, then fill in:

- what's genuinely off-limits for every line, regardless of what a topic
  asks for (payments, auth, deploy config, production data — adjust to what
  this project actually has);
- what must always go to a human rather than land automatically, specific
  to this codebase (its real auth module, its real payment integration, its
  real data layer, not just the generic examples already in the template).

**`factory/config.json`.**

- `base_branch`: the project's actual default branch.
- `lines`: keep `build` and `docs`, add more only if the user asks for a
  different shape (e.g. a migration line, a design-review line) — each new
  line needs its own `checks` entry and its own `factory/playbooks/<line>.md`.
- `protected_paths`: keep the `factory/*` and `.claude/*` entries. Don't add
  the project's tests — real features legitimately change existing tests
  (a new required field touches every fixture), and a protected test would
  block a job with no way through. `reviewer-code.md` already catches a test
  that was weakened or special-cased instead of genuinely fixed.
- `ports`: move `base` if the project already uses ports 5100–5199.
- `github.issue_label`: only matters if the project wants issues labeled
  `factory` pulled into the inbox automatically (`factory/bin/pull`). Leave
  it as `factory` unless that label already means something else here; this
  whole feature is optional and `gh` doesn't need to be installed for the
  rest of the factory to work.
- Leave `concurrency`, `max_rounds`, `routing`, `surface_reviewers` and
  `prices_usd_per_mtok` as shipped unless the user asks otherwise.

**The reviewer agents.** Keep their structure, file names, and the exact
`VERDICT:`/first-line reply format untouched; only tailor the content:

- `reviewer-security.md`: this project's actual exposure — its auth, its
  data-access rules, its payment and webhook paths, anywhere user input
  reaches a query or HTML.
- `reviewer-ui.md`: where this project keeps its design tokens, theme and
  shared components.
- `reviewer-ux.md`: the kind of users this project actually has.

**`AGENTS.md`** (or `CLAUDE.md` — whichever the project already uses; create
`AGENTS.md` if it has neither). Every agent reads this first, so make sure
it covers:

- how to get a fresh checkout working (installing dependencies, env files
  to copy);
- how to start the dev server, on what port, if the project has one;
- the real validation commands, matching `factory/checks.sh` exactly.

Then append:

```markdown
## Software factory

`/factory run` works through topics filed in `factory/inbox/`, carrying each
through triage → spec → build → gate → review → approve, landing approved
work on the base branch (or handing it to another line, per a line's
`handoff`). State: `factory/jobs/` (gitignored). The only writer of that
state: `factory/bin/job`. Checks: `factory/checks.sh`. Boundaries: start at
`factory/playbooks/_global.md`. Dashboard:
`cd factory && python3 -m http.server`, then
http://localhost:8000/dashboard.html.

Each job works in its own git worktree, a full checkout at
`.worktrees/<job-id>` (gitignored). A tool run from the repo root that
doesn't read `.gitignore` will also see those copies — exclude
`.worktrees/` in its own config if that matters.
```

**`.gitignore`.** Append:

```gitignore
/factory/jobs/
/.worktrees/
```

Everything else you copied in step 1 is meant to be committed: the skill,
the agents, and the rest of `factory/` (including `factory/playbooks/` and
`factory/inbox/`) are part of the project now.

## 3. Verify it before handing it back

1. From the project root, on its current branch: `bash factory/checks.sh`
   exits 0. If it doesn't, the factory can never pass a single job — fix the
   script (not the project) or tell the user exactly what's broken.
2. `factory/bin/job queue` runs without an error (an empty inbox is fine —
   it should just print nothing).
3. Every file under `.claude/agents/` has only these frontmatter keys:
   `name`, `description`, `tools`, `model`, and `hooks` on `builder.md`
   alone. Claude Code silently ignores an unknown key, so a typo there would
   change behavior with no warning.
4. `python3 -m json.tool factory/config.json` succeeds.
5. `git check-ignore factory/jobs/x .worktrees/x` prints both paths back,
   and `git status --porcelain --untracked-files=all` lists every file you
   copied or edited as something that can be committed.

## 4. Hand it back to the user

Stay on whatever branch they're already on — don't create or switch to a
new one. Commit the install there with a short, one-line message, and show
them the diff. Ask before pushing: every job branches from this branch's
tip on the remote, so the install needs to already be there before the
first real run.

Then tell them, briefly:

- File one or two small topics in `factory/inbox/`, then run `/factory run`
  from the project root in Claude Code.
- A finished job either lands on the base branch directly, or (if its line
  has a `handoff`) moves on to the next line automatically.
- Anything the approver isn't sure about waits as `needs-human` — read
  `factory/jobs/<id>/<pass>/decision.md`, then reply with feedback or a
  rejection through `/factory <anything>`.
- Triage runs on Fable once per pass; depending on their plan, that can bill
  against usage credits rather than plan-included usage.
- Start with `concurrency: 1` in `factory/config.json` and read what a few
  jobs actually produce before raising it.
