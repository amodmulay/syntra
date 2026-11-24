<!-- factory-issue: 11 -->
# Keep a per-job event log

`job.json` holds only the current stage, so there is no record of how a job got there. Have `factory/bin/job` append one line per transition and per command (advance, merge, answer, feedback, reject, gate result) to `factory/jobs/<id>/events.jsonl`: timestamp, from and to stage, round, command, commit, host name and Claude session id when known. Copy a compact form of it into the job record at merge and reject so the history travels with the record. Show it in the dashboard drawer. Never let a failed log write block a transition.
