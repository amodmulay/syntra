# Fix merge escalation on conflicts in the job state machine

## Problem

In factory/bin/job, cmd_merge calls land(job). If land() raises Refused (the branch conflicts with main, or the gate fails after syncing), it calls escalate() and then save(sync(advance(job, "needs-human"))).

advance() from "merging" runs the merging ancestor check: the branch must already be an ancestor of main. Before landing, it never is, so advance() dies with "<branch> isn't on main yet". The job stays at merging and never reaches needs-human.

Result: a job that conflicts with main cannot be rejected. reject() only accepts needs-info or needs-human, and advance(merging -> needs-human) is refused. Jobs 007 and 009 are stuck at merging for this reason.

## Expected

A merge refusal moves the job to needs-human with the reason recorded, so the user can reject it or send it back to build.

## Scope

Fix the transition so merging -> needs-human is allowed after a refused land, without weakening the ancestor check for the merging -> spec and merging -> merged transitions. Keep the change minimal.

## Validation

- A test that a conflicting merge leaves the job at needs-human with the escalation recorded.
- A test that merging -> spec and merging -> merged still require the branch on main.
- The existing ledger and transition tests still pass.

## Worktree path on another machine

job.json records each job's worktree as an absolute path. Jobs created on another machine (for example Windows, `D:\repo\syntra\.worktrees\<id>`) carry that path, and every git-backed step runs in `job["worktree"]`. Here that path doesn't exist, so gate, review and merge fail for those jobs. Job 011 (keep-finished-job-records-across-devices) is blocked this way.

Expected: when the stored worktree path isn't a local directory, resolve it to `REPO/.worktrees/<job-id>` (the path `cmd_create` uses). Keep the stored value unchanged in job.json, and keep the fallback read-only (no state writes from the path resolution).

Validation: a test where job.json holds a foreign absolute path and the local `.worktrees/<id>` exists, showing git steps run in the local worktree; and a test that a local, existing stored path is used unchanged.

## Security

Job state transitions are high impact. This needs focused validation and security review. Do not edit job.json directly; only factory/bin/job writes job state.
