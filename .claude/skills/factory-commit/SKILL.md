---
name: factory-commit
description: Commit pending changes in the repository safely, as part of the Syntra factory. Use for work outside a factory job, such as dashboard edits, finished-job records and the usage ledger.
argument-hint: [message or scope]
disable-model-invocation: true
---

# Syntra factory commit

Commit pending work on the current branch of the main checkout. Jobs commit
inside their own `.worktrees/<id>` branch and land through
`factory/bin/job merge`; this skill never replaces that path. It is for
everything else: factory development done by hand, `factory/records/*.json`
that `job reject` leaves uncommitted, and the usage ledger.

Commit only. Never push, tag, amend, rebase, force anything, or skip hooks
(`--no-verify`). Pushing is always a separate, explicit request.

## Steps

1. **Look.** Run `git status --short` and `git diff --stat`. If the tree is
   clean, say so and stop. If the current branch is `factory/<id>` for a live
   job, stop: that branch belongs to the job's builder.
2. **Refresh usage.** If `factory/usage/` is among the changes, or this
   session did Claude Code work, run `python3 factory/bin/usage ingest` first
   so the ledger and `USAGE.md` are current. Never edit the ledger by hand.
3. **Never stage these.** `factory/jobs/`, `.worktrees/`, `factory/.dashboard-id`,
   `__pycache__/`, and anything that looks like a secret (`.env*`, keys,
   tokens, credentials, `.claude/settings.local.json`). Warn if one shows up
   as untracked and not ignored. `factory/jobs/` is gitignored; if it appears
   in status, stop and report it.
4. **Protected files.** `factory/bin/job` and `factory/checks.sh` are protected
   by the gate. Commit changes to them only if the user asked for that
   change in this conversation; otherwise list them and ask.
5. **Validate.** Run `python3 -m py_compile src/*.py && python3 -m unittest
   discover -s tests`. Do not commit on failure; report the output. A change
   that touches only Markdown, the dashboard HTML, records or the usage files
   may skip the test run, and the commit message must say nothing was run.
6. **Group.** Split into logical commits, one concern each:
   - code, scripts, prompts, playbooks or the dashboard
   - docs (`README.md`, `AGENTS.md`, `CLAUDE.md`, `INSTALL.md`, `DESIGN.md`,
     `GETTING_STARTED.md`)
   - `factory/records/<job-id>.json`, one commit per record
     (`Record rejected job <id>` or `Record merged job <id>`)
   - `factory/usage/ledger.jsonl` with `factory/usage/USAGE.md`
     (`Update usage ledger`)
   If `CLAUDE.md` or `AGENTS.md` changed, check the other one still agrees
   (they are kept in sync).
7. **Commit with explicit paths.** `git add -- <paths>` then
   `git commit -m <message> -- <paths>`. Never `git add -A` or `git add .`.
   Messages are an imperative summary line under 72 characters, a blank line
   and an optional short body saying why. End with the attribution trailer
   the session gives for commits, if there is one.
8. **Report.** Show `git log --oneline` for the new commits and `git status
   --short` for what was left out and why. State that nothing was pushed.

## Arguments

`/factory-commit <text>` uses the text as the message for a single-concern
change, or as the scope to commit ("records", "usage", "dashboard"). With no
argument, infer messages from the diff, and ask only if the grouping is
unclear.
