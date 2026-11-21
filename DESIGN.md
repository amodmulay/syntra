# Design notes

Why this factory is put together the way it is. Read this alongside the
source itself — one skill, eight agent roles, three scripts, one config file.

## What a factory line actually does

Think of a line as an assembly line for one kind of work: a fixed sequence of
stations, each either mechanical (a script that runs the same way every time)
or judgment-based (an agent deciding something that can't be reduced to a
rule). The mechanical stations are where you want zero variance — running
tests, moving a job from one state to the next, fast-forwarding a branch.
The judgment stations are where variance is the point — is this worth doing,
what should get built, is the code actually right. Every station leaves
something behind: a file. That's what lets a person walk the line after the
fact and see exactly what happened and why, without having to re-run
anything or trust a summary.

## The moving parts

| Piece | Where | Does what |
|---|---|---|
| Inbox | `factory/inbox/*.md` | Holds the requests. One markdown file per topic; nothing more formal than that. |
| Orchestrator | `.claude/skills/factory/SKILL.md` | The session `/factory` runs in. Starts jobs, launches agents, calls the scripts. Writes nothing itself. |
| Agent roles | `.claude/agents/*.md` | One file per role. Reads what it needs, writes one output file, replies in one line. |
| Lines | `factory/config.json` → `lines` | Named stages with their own checks and an optional handoff to whatever comes next. |
| Playbooks | `factory/playbooks/` | Written policy: what the factory is for, what no line may ever do, what must always escalate. Read by agents, not enforced by a script. |
| Job state | `factory/jobs/<job-id>/` | `job.json` plus every file an agent wrote for that job. Gitignored, lives only on the machine running the factory. |
| Control scripts | `factory/bin/job`, `gate`, `route`, `pull` | Deterministic. `job` is the sole writer of `job.json`, and it refuses anything out of order. |
| Checks | one script per line | The project's real lint/test/typecheck/build commands, scoped to what that line produces. |
| Exit | the base branch | A pass ends either landed there or handed to the next line — never left half-finished. |

## How a pass flows

```
triage (fable)     → ACCEPT (scope maybe narrowed, line picked) | NEEDS-INFO | REJECT
route (script)     → reviewer set + models, from risk/surfaces, via config.json
worktree           → factory/<job-id>, branched off the base branch
spec-writer (opus) → spec.md
builder (opus)     → commits; writes build.md
gate (script)      → the line's checks; FAIL sends the log back to the builder, no reviewer runs
reviewers (routed) → run together, wait for every one; any CHANGES loops back through builder → gate → reviewers
approver (opus)    → APPROVE: resync with base, gate again, land (or hand off); ESCALATE: parked for a human
```

`stage` in `job.json` tracks one of: `triage`, `needs-info`, `spec`, `build`,
`gate`, `review`, `approve`, `merging`, `needs-human`, `merged`, `rejected`.
Which moves are legal from which stage lives in the `TRANSITIONS` table at
the top of `factory/bin/job` — nothing else decides that.

## Why it's built this way

**The queue is just files, and nothing fires on its own.** Dropping a
markdown file in `factory/inbox/` is the entire filing process — no external
service account, no label permissions, nothing to configure beyond having a
repo. And nothing runs unattended: `/factory run` is something you type, so
the factory only ever spends your own Claude usage when you've decided to
spend it. Keeping it local also means the worktrees, any dev server a
reviewer starts, and the dashboard are all sitting right next to each other
on one machine.

**GitHub issues feed the inbox; they don't replace it.** `factory/bin/pull`
turns every open, `factory`-labeled issue into a file in `factory/inbox/`,
marked with the issue number it came from, and leaves it alone from then on
— the issue can keep changing on GitHub without silently rewriting a topic
mid-flight. Once pulled, it's indistinguishable from a topic someone typed
by hand: triage, the lines, the playbooks, none of them know or care where a
topic came from. This keeps the inbox as the one queue the rest of the
factory has to understand, instead of teaching every downstream piece two
different ways to read a request. `pull` is also the only thing in the
factory that needs `gh` at all, and it's written to fail soft — no `gh`, no
auth, no problem, the run just continues on whatever's already filed
locally. The one place the loop closes back to GitHub is `job merge`, which
closes a pulled topic's originating issue, best-effort, once its job has
nothing left to run.

**One session runs the whole show.** Whoever runs `/factory run` becomes the
only orchestrator, starting up to `concurrency` jobs and launching every
agent each one needs as a background task. There's no second layer of
per-job coordinators to keep in sync. This keeps the orchestrator's own
context small, because every agent and every script hands back exactly one
line — the real substance lives in files the next step reads, not in
anything the orchestrator has to hold onto.

**Judgment happens once, at the front door.** Triage is the only step that
runs on Fable, and it runs exactly once per pass. It decides whether a topic
is worth the chain of work that follows, trims the scope if it's too broad,
picks which line should handle it, and asks a question when only the
original requester can answer it. That question gets asked before a spec
ever gets written, so nothing downstream sits around waiting on an answer
that was knowable up front.

**Lines are configuration, not hardcoded steps.** `factory/config.json`'s
`lines` table is what makes "spec → build → review → land" a pluggable unit
instead of the only possible shape. Each line names its own checks script and
can name a `handoff` to whatever comes after it — `build` finishing and
handing straight to `docs` is just one line's config pointing at another's
name. A job's folder keeps each line's pass in its own numbered subfolder
(`01-build/`, `02-docs/`, …), so a job that crosses three lines still reads
like three small, separately legible jobs instead of one tangled one. Adding
an entirely new line — a design-review line, a database-migration line —
means adding one entry to `config.json` and one new agent file; the rest of
the machinery doesn't change.

**Risk decides who reviews, and a script makes that call — not a prompt.**
Triage scores risk (`low`/`medium`/`high`) and the surfaces involved
(`ui`/`security`). `factory/bin/route` looks both up in `config.json`:

| | code reviewer | ux reviewer | ui reviewer | security reviewer |
|---|---|---|---|---|
| low risk | Haiku | | | |
| medium risk | Sonnet | | | |
| high risk | Sonnet | | | |
| touches `ui` | | Sonnet | Haiku | |
| touches `security` | | | | Opus |

The builder is always Opus regardless of risk. A small, low-risk, UI-free
change gets exactly one Haiku reviewer. Changing who reviews what, or which
model they run on, means editing one JSON file — never a prompt.

**Policy, judgment and enforcement are three different files, on purpose.**
It would be easy to let "what's in scope" and "what must always escalate"
live only inside an agent's own prompt — but then changing policy means
editing an agent, and there's no single place to read what the rules
actually are. Playbooks split that out: `factory/playbooks/_global.md` holds
boundaries that apply no matter which line a job is on, and
`factory/playbooks/<line>.md` holds what's specific to one line. Triage
reads both before it can ACCEPT anything; the builder treats their "never
do this" items as binding, the same way it already treats `protected_paths`;
the approver's escalate list starts from them before anything
project-specific. None of this is mechanically enforced the way the gate
is — a playbook is something an agent has to actually read and comply with,
not a rule a script checks. That's the tradeoff: softer than a gate, but
editable by anyone who can write a markdown file, without touching a single
agent's instructions.

**A script is the referee on whether the code works; agents judge what a
script can't.** The gate runs the line's checks before any reviewer sees the
diff, and again right before landing, because another job might have landed
something in between. It always runs the main checkout's copy of the checks
script — a branch editing its own checks doesn't change what it's graded
against. It also fails any branch that touches a file matching
`protected_paths` (the factory's own scripts and config stay off-limits;
tests don't, since real features legitimately change them — the code
reviewer is what catches a test that got weakened instead of fixed). The
builder also gets a `SubagentStop` hook that runs the checks as an early
warning before it even finishes, but that's just a nudge — the gate is still
what actually decides PASS or FAIL. Reviewers, in turn, never rerun the
checks themselves; their job is reading the diff for things a check can't
catch — correctness, scope creep, security holes, a confusing flow, a UI
that doesn't match the rest of the app.

**Landing means fast-forwarding a local branch, not opening anything on a
remote.** Every job works inside its own worktree and branch
(`.worktrees/<job-id>`, `factory/<job-id>`). When a pass is approved, landing
it means: resync that branch with the base branch, rerun the gate, then
fast-forward the base branch onto it — all through `factory/bin/job merge`,
which is the only thing allowed to touch the base branch. The user's main
checkout is never dirtied while a job is running, and nothing but that one
script ever moves it.

**A human is a conversation partner, not someone who has to click merge
somewhere.** Since there's no hosted pull request to approve by merging,
approval instead means responding: the approver's reasoning lands in
`decision.md`, and `/factory <anything>` is how an operator replies — send
the builder feedback and get another round, or reject the pass outright. A
parked job keeps its worktree alive until someone responds to it.

**Everything the orchestrator needs survives in files, so a dead session
costs nothing.** All of a run's state sits under `factory/jobs/`. If the
session running it dies, gets compacted, or just gets closed, a new
`/factory run` reads the inbox and every job's saved state and continues
exactly where things left off — no job silently falls through.

**Cost gets tracked per job, from the raw transcripts.** Claude Code logs
every subagent's messages — including per-message token counts and which
model handled them — under
`~/.claude/projects/<project>/<session>/subagents/`. Since every factory
prompt opens with that job's folder path, `factory/bin/job` can scan for
transcripts naming a given job and price them using `prices_usd_per_mtok`.
What comes out is the API-equivalent cost of that job's agents — useful as a
relative number on a subscription plan, not a literal bill. The
orchestrator's own token usage isn't counted toward any job. Since the
transcript layout isn't a published, stable format, a future Claude Code
release could change it out from under this.

## Boundaries that don't bend

- A topic's text only ever reaches an agent as quoted material inside
  `topic.md` — never folded into a prompt. Triage, which reads it first, has
  no shell access at all.
- Every agent works only inside its own job's worktree and branch. The base
  branch moves only through `factory/bin/job merge`. Nothing the factory
  does ever deploys anywhere.
- One branch per job (a new one each time a handoff starts a fresh line),
  and at most `max_rounds` build-review rounds per pass before a human gets
  pulled in.

## Where this design came from

The shape of this pipeline — triage, then route, then spec, build, gate,
review, approve, with files as the only state and small scripts as the only
things allowed to mutate it — started from studying ZazenCodes'
[software-factory-claude-code-v2](https://github.com/zazencodes/zazencodes-season-3/tree/main/src/software-factory-claude-code-v2)
as a reference for what a Claude-Code-driven software factory can look like.
This implementation reworks that shape around a different queue (a local
inbox instead of GitHub issues) and a different exit (landing straight on a
branch instead of opening and merging a hosted pull request), and generalizes
the single build pipeline into a configurable chain of lines that can hand
work from one to the next.
