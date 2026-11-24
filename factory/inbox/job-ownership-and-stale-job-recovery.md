<!-- factory-issue: 12 -->
# Record who is running a job and recover stale jobs

Nothing records which device or session is working on a job. After a pull, two machines can both resume the same job, and a session that dies mid-step leaves the job in build or review holding a concurrency slot forever while the dashboard shows it as live. Add a claim to the job (host, session, claimed-at, heartbeat updated on every `job` command), make `/factory run` refuse or ask before resuming a job claimed elsewhere, treat a claim with no heartbeat for a configurable time as stale, and add `job release <id>` to clear it. Show the owner and staleness on the dashboard.
