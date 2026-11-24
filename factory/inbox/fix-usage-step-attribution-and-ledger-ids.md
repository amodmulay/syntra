<!-- factory-issue: 14 -->
# Fix per-step cost attribution and tag ledger entries

Job records and job.json put nearly every call under step `other` (job 011: 145 calls, job 1000: all of them), so per-step costs on the dashboard are meaningless; `step_of` in `factory/bin/job` is not recognising the steps. Fix the attribution, for example by having the orchestrator put `Step: <name>` in each agent prompt next to `Job folder:`. Also add the job id (when known) and a host id to each ledger entry so costs can be traced across devices, and make `ledger.jsonl` and `USAGE.md` merge cleanly when two devices both append (for example a union merge attribute for the ledger and regenerating USAGE.md instead of merging it).
