# Resolve foreign worktree paths in job.json to the local worktree

## Problem

job.json records each job's worktree as an absolute path. Jobs created on another machine (for example Windows, `D:\repo\syntra\.worktrees\<id>`) carry that path. factory/bin/job runs every git-backed step in job["worktree"], so on any other machine gate, review and merge fail for those jobs. Job 011 (keep-finished-job-records-across-devices) is blocked this way.

## Expected

When the stored worktree path is not a local directory, resolve it to REPO/.worktrees/<job-id> (the path cmd_create uses). Keep the stored value unchanged in job.json. Keep the fallback read-only: path resolution must not write job state.

## Scope

Only the path resolution used by git-backed steps. Do not change the merge escalation transition (topic fix-merge-escalation-on-conflicts covers that).

## Validation

- A test where job.json holds a foreign absolute path and REPO/.worktrees/<id> exists: git steps run in the local worktree.
- A test that a local, existing stored path is used unchanged.
- The stored job.json value is not rewritten by the resolution.

## Security

Job state is high impact. This needs focused validation and security review. Do not edit job.json directly; only factory/bin/job writes job state.
