DECISION: ACCEPT
LINE: build
RISK: high
SURFACES: ui,security
RESCOPED: yes

## Summary

Accept a narrowed slice of topic 011: make a finished job's record durable by having `factory/bin/job` write a small summary to a tracked path `factory/records/<job-id>.json` when a job reaches `merged` (final line only, not a handoff) or `rejected`, and show a dashboard card with cost for any such record that has no local `factory/jobs/<job-id>/` folder. The GitHub issue status work (`factory-done` / `factory-rejected` labels, Project board Status, rejection comment, getting-started docs) is carved off and left unscoped.

## What this covers

- `factory/bin/job` writes `factory/records/<job-id>.json` on the final merge (`cmd_merge`, the branch that calls `advance(job, "merged")`) and on reject (`cmd_reject`, which moves the job to `rejected`). Fields: id, stage, line, pass, triage fields (DECISION, LINE, RISK, SURFACES, RESCOPED), started/ended, `cost_usd`, `models`. Records are written only by `factory/bin/job`.
- No record for handoff passes (`build` to `docs`) and none for jobs still in progress.
- Dashboard: list records that have no matching local job folder, render each as a card with its cost, marked "from record". Local jobs render as today.
- Focused unit tests: record contents on merge and on reject, no record for handoff or in-progress jobs, dashboard showing a record-only job, and no duplicate card when a job exists both locally and as a record.
- The ledger (`factory/usage/ledger.jsonl`) is not changed, and costs are never inferred from it.

## Reasoning

- RISK is high and SURFACES includes `security` because the change writes at the merge and reject transitions in `factory/bin/job`, which the build playbook treats as high impact. Security review should confirm the records contain no secrets, no absolute local paths, and no topic body, since they are meant to be committed.
- SURFACES includes `ui` because the dashboard gains a card type.
- LINE is `build`: the change is to factory scripts and dashboard code, not documentation. The global playbook allows `factory/bin/job` to be changed through a factory issue and the normal review pipeline.
- Protected-path note: CLAUDE.md says `factory/bin/job` is protected by the gate, but `factory/config.json` `protected_paths` lists only `factory/checks.sh`, and the global playbook explicitly allows `bin/job` changes via the factory. The mechanical gate only enforces `protected_paths`, so this does not block acceptance. It is a documentation inconsistency to fix in CLAUDE.md (and AGENTS.md, which must stay in sync), not an open escalation.
- Checked: `cmd_reject` exists and is the reject transition, so the reject path is accurate. `.gitignore` covers only `/factory/jobs/`, `/.worktrees/`, `/factory/.dashboard-id` and Python caches, so `factory/records/` is not ignored.
- Rescope: the topic bundles two independent changes. The durable record fixes the reported loss of data and cost, and the dashboard card is the minimum needed to see it. The GitHub label and Project board work touches external state (labels, board fields, outbound comments on real issues), depends on `gh` permissions and board setup, and is a separate concern. It should be its own topic after the record slice lands.
- Cost comes only from `job.json` (`cost_usd`, `models`), never from the ledger, which has no job id.
- Not a schema migration of existing data. Records are new files; existing finished jobs are not backfilled.

## Open questions

1. How the record becomes durable (decides whether the slice meets the goal). The topic says "committed" but not who commits or when, and nothing pushes today. Options: (a) on merge, write the record into the base branch as part of the landing, or as a follow-up commit on base; (b) on reject there is no merge, so something must commit the record on base or it stays an untracked file and the bug is unfixed; (c) reaching another device also needs a push, which the factory does not do. The spec must pick one. Recommended: a dedicated commit on base for each record, made by `factory/bin/job`, with pushing left to the operator.
2. Failure ordering and policy. `land()` fast-forwards base before the job is saved as `merged`. If the record write or its commit then fails, the job is left half-transitioned (base has the work, job.json says merging or needs-human). The spec must define the order (write record, then advance, then save) and what happens on failure. Recommended: report the failure clearly and do not roll back landed work. This is a state-transition concern and belongs in front of the security reviewer.
3. Backfill: should existing finished jobs get records? Left out of scope; it would need its own command and decision.
4. Privacy: confirm that committing triage fields, `models` and cost is acceptable for a repository that may be public.
5. Label and Project work: the carved-off GitHub status slice needs a separate topic. Adding labels and posting comments on real issues is outbound activity on a real repository, so a human should confirm it before it is filed as a factory job.
