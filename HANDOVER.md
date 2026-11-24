Both pushes succeeded. On the other machine you can pick up job 011 with a `git pull`, a fetch of the job branch, and one manual worktree step.

**Pushed to `origin`:**
- **`main`** (68faa63 → 5d0cac0): one new commit, "Hand over job 011". It adds the two inbox topics and the job 011 state: `job.json`, `topic.md`, `triage.md`, the spec, the `build.md` and the round 1 reviews and checks. I force-added the job folder past the `/factory/jobs/` ignore rule, as jobs 001–010 already are. I left out `.lock` so a stale lock doesn't travel.
- **`factory/011-keep-finished-job-records-across-devices`**: the new branch, with `0b6bef5`, `960b915` and `409b777`. The round 2 commit `409b777` is unverified.

**Not pushed:**
- **Local-only changes:** the ledger and `USAGE.md` changes from my `usage ingest`, the `.lock` and `job.json` changes in the older jobs, and the untracked `screenshots/` folder.
- **Worktree:** it can't travel through git.

**On the other machine:**
1. `git pull` on `main`.
2. `git fetch origin factory/011-keep-finished-job-records-across-devices`.
3. Recreate the worktree: `git worktree add .worktrees/011-keep-finished-job-records-across-devices factory/011-keep-finished-job-records-across-devices`.
4. `job.json` still stores the other machine's absolute worktree path (`D:\repo\syntra\...`), but `factory/bin/job` and `factory/bin/gate` ignore it. Git steps run in `.worktrees/011-keep-finished-job-records-across-devices` in this machine's repo, which is the worktree from step 3. Do not edit `job.json`; no change is needed. If that worktree is missing, the step refuses and says so, so create it as in step 3 first.
5. Run `/factory run` to resume at `build` (round 2).

Before building, read `01-build/round-1/review-*.md` and run the checks on `409b777`. Round 2 was cut off before `build.md` or the checks were redone.