# Getting started with Syntra

How to use the factory day to day: the idea, how to install it, how to give
it work, and how to see what it did. For the vision see
[README.md](README.md); for the design see [DESIGN.md](DESIGN.md); for the
rules agents follow see [AGENTS.md](AGENTS.md).

## The concept

Syntra is a software factory that runs inside your Git repository from
Claude Code. You file a request; the factory carries it through a fixed chain
of steps, each done by a small specialised agent, with scripts (not prompts)
making the decisions that must be reliable.

```
request → triage → spec → build → gate → review → approve → merged
```

| Step | Who | What happens |
|---|---|---|
| Triage | `triage` agent | Accepts, rejects, or asks a question. Picks the line, risk and surfaces (ui, security). |
| Spec | `spec-writer` agent | Writes a scoped, testable spec. |
| Build | `builder` agent | Implements it in its own Git worktree and commits. |
| Gate | `factory/bin/gate` script | Runs `factory/checks.sh`. A failure goes back to the builder; no reviewer runs. |
| Review | routed reviewers | Chosen by a script from risk and surface (code, ux, ui, security). All must pass. |
| Approve | `approver` agent | Lands the work on the base branch, or escalates to a human. |

Things worth knowing:

- **A job is one request.** Its state and evidence live in
  `factory/jobs/<id>/` (gitignored). Only `factory/bin/job` writes it.
- **Lines** are workflows. `build` changes code; `docs` changes documentation.
  `build` hands finished work to `docs` automatically.
- **Waiting is normal.** A job can stop at `needs-info` (triage has a
  question) or `needs-human` (the approver wants a person to decide).
- **Nothing is pushed.** Work lands on your local base branch only.
- **Runs are manual.** Filing a request does not start an agent.
- **Models** are set per agent in `.claude/agents/*.md` (`model:`) and per
  reviewer in `factory/config.json`. Everything currently runs on Haiku to
  keep token use low.

This repository's own calculator (`src/`, `tests/`) is only a throwaway
fixture for testing the factory.

## Install

**Requirements:** Git (with at least one commit), Claude Code, Python 3.10+,
and Bash (Git Bash or WSL on Windows). The GitHub CLI `gh` (signed in) is what
fetches GitHub issues, the default intake; see [Give it work](#give-it-work).
Without it you can still use the factory through files in the inbox.

- **Use this repository as is:** clone it, open it in Claude Code, and you are
  ready. Nothing to install; everything is standard library.
- **Add the factory to another project:** open that project in Claude Code
  (from its root) and paste the prompt below. The agent follows
  [INSTALL.md](INSTALL.md): it copies the generic files, then adapts
  `factory/checks.sh`, `factory/config.json`, the playbooks and the project
  instructions to your codebase, and verifies the result.

  ```text
  Install the Syntra software factory into this project.

  Source: https://github.com/amodmulay/syntra.git
  (or a local checkout at <path to your Syntra clone>; use whichever I have
  given you).

  1. Fetch INSTALL.md from the source (clone it with --depth 1 into a scratch
     directory outside this project if it is a URL) and follow it exactly,
     starting with its section 0 checks. Stop and tell me if any check fails
     or if a path it would create already exists.
  2. Copy only the files INSTALL.md lists. Do not copy the source repository's
     own history, jobs, usage ledger, or its calculator sample (src/, tests/).
  3. Adapt everything project-specific: factory/checks.sh to this project's
     real lint/test/build commands, factory/config.json (base branch, lines,
     models), the playbooks, the .gitignore entries, and this project's
     CLAUDE.md or AGENTS.md.
  4. Verify it as INSTALL.md section 3 describes (checks script passes,
     `factory/bin/job queue` runs, agent frontmatter and config.json are
     valid, ignore rules work).
  5. Hand it back as INSTALL.md section 4 describes: stay on my current
     branch, commit the install with a one-line message, show me the diff,
     and ask before pushing. Do not change anything outside what INSTALL.md
     describes. Report what you copied, what you changed, and what you
     verified.
  ```

  Afterwards, file a small topic in `factory/inbox/` and run `/factory run`.
  Each agent's cost is set by the `model:` line in `.claude/agents/*.md` and
  by the reviewer routing in `factory/config.json`; start with
  `concurrency: 1` until you have seen what a few jobs produce.

## Give it work

One topic becomes one job. Topics live in `factory/inbox/`, and there are two
ways to fill it.

### GitHub issues (the default)

Every `/factory run` starts by fetching your open GitHub issues that carry the
`factory` label and writing each one into `factory/inbox/`. File issues with
the *Factory request* form, which adds the label for you. An issue you edit
later is updated in place.

This needs one-time setup on your machine. If it is missing, `/factory run`
tells you exactly what to do and carries on with whatever is already in the
inbox:

1. Install the GitHub CLI: <https://cli.github.com/>
2. Sign in: `gh auth login`
3. Make sure the project has a GitHub remote: `git remote -v` should list one
   (otherwise `git remote add origin https://github.com/<owner>/<repo>.git`).
4. Create the label once: `gh label create factory`

Jira and other trackers are not supported yet; they are planned as a later
addition. Until then you can copy their tickets into the inbox as files (next
section).

### A task list in the inbox (no GitHub needed)

You can use the factory without any tracker. Make one Markdown file per task
in `factory/inbox/`. The first heading is the title and the body is the
request, so a task list is simply a folder of small files:

```
factory/inbox/
  add-divide-function.md
  fix-rounding-in-integrate.md
  document-the-dashboard.md
```

```markdown
# Add a divide function

Add divide(a, b) next to add and subtract. Raise ZeroDivisionError when b is 0
and add tests in the same style.
```

`/factory run` asks you to confirm when several topics are waiting: run up to
`concurrency` of them in parallel, or pick which ones by hand. Anything not
chosen stays queued for the next run. Local
files and GitHub issues can be mixed freely.

Be specific. "Add a divide function that raises on zero" gets built;
"Add a Fourier function" gets a question back.

## Run it

In Claude Code, from the project root:

```
/factory run
```

It imports issues, creates jobs for new topics (up to `concurrency` in
`factory/config.json`), and moves each as far as it can. It reports every
job's final stage and where the evidence is.

To answer a waiting job, describe the answer or feedback in plain language,
for example `/factory the Fourier function should be a DFT of a list`. The
operator routes it to the right job: `needs-info` goes back to triage,
`needs-human` goes back to build, and you can also reject a waiting job.

## View the runs

**Dashboard** (a board with a column per stage, live every 2 seconds):

It starts by itself the first time you run `/factory run`, keeps running in
the background, and the run prints its address, normally
<http://localhost:8000/dashboard.html>. It only listens on your own machine.
If port 8000 is taken it uses the next free one (the printed URL is the
truth), and `dashboard.port` in `factory/config.json` changes where it
starts looking. To start it yourself, or to find the address again:

```
python3 factory/bin/dashboard
```

Each card shows the verdict of
every round, the models used, cost and elapsed time. Click a card to read the
job's files (topic, triage, spec, build notes, check logs, reviews, decision)
and a table of model, calls, tokens and cost per step.

The header has a **Light** or **Dark** button next to the status line. It names the theme a click switches to, so it reads "Light" while the dark theme is showing. With no saved choice, the dashboard follows your browser or OS light or dark setting, including changes made while the page is open. A click saves your choice in this browser's local storage for the dashboard's address (scheme, host and port), and a saved choice then wins over the OS setting. If the browser blocks local storage, the choice lasts only until the page is reloaded. The dashboard has no reset control: to follow the OS again, clear the site data for that address or delete the `syntra-factory-theme` key in the browser's developer tools. A saved choice applies to one address only, so the same dashboard on another port, or on `127.0.0.1` instead of `localhost`, keeps its own choice.

The header also has two other views next to **Board**:

- **Not picked up** lists topics in `factory/inbox/` that have no job yet
  (the badge shows how many), why each is waiting, and the jobs that are
  parked waiting for your answer or decision.
- **Task stats** has one row per job: model, tokens, cost, elapsed time, how
  many times a person had to step in, and whether it ran **100% autonomous**,
  needed you, or is waiting on you now. A "human step" is an answer to a
  triage question, feedback after an escalation, an approval from
  `needs-human`, or a rejection. Cost is API-equivalent dollars, elapsed time
  includes time spent waiting for you, and tokens count cached input.

**Terminal summary:**

```
python3 factory/bin/job summary
```

**Files**, per job in `factory/jobs/<id>/`:

| File | Contents |
|---|---|
| `topic.md`, `triage.md` | The request and triage's decision |
| `NN-<line>/spec.md`, `build.md`, `decision.md` | Spec, builder notes, approver's verdict |
| `NN-<line>/round-N/` | Gate result and each reviewer's verdict |
| `job.json` | Stage, verdicts, routed reviewers, per-step models, cost |

Stages: `triage`, `needs-info`, `spec`, `build`, `gate`, `review`, `approve`,
`merging`, `needs-human`, `merged`, `rejected`.

## Tokens and cost

- **Per job:** `cost_usd` and `models` in `job.json` and on the dashboard.
  These are API-equivalent dollars worked out from Claude Code's transcripts,
  not an actual bill, and they never go down on a re-sync.
- **Everything, permanently:** `factory/usage/ledger.jsonl` records every API
  call with model, tokens and dollars, and `factory/usage/USAGE.md` summarises
  it by model and day. The factory adds to it whenever a job is saved. For
  other Claude Code work run `python3 factory/bin/usage ingest`. Commit the
  ledger to keep it. Only Claude Code usage is captured.

## When something looks wrong

- **Job is `needs-info` or `needs-human`:** read `triage.md` or
  `<pass>/decision.md`, then answer through `/factory`.
- **Gate keeps failing:** read `<pass>/round-N/checks.log`. The job stops
  after `max_rounds` (3) and waits for a human.
- **Dashboard is empty:** it must be served from the `factory/` folder, and
  `factory/jobs/` only exists after the first job is created.
- **No GitHub issues arrive:** `gh` is missing or not signed in. Local inbox
  topics still work.
- **Rules the factory will not break:** see
  [factory/playbooks/_global.md](factory/playbooks/_global.md). It never
  deploys, pushes, or edits protected paths such as `factory/checks.sh`.
