<!-- factory-issue: 15 -->
# Answer waiting jobs from GitHub issue comments

A `needs-info` question and a `needs-human` escalation can only be answered in a Claude Code chat on the machine running the job. When the job came from a GitHub issue, post the question or escalation summary as an issue comment, and have `factory/bin/pull` pick up a reply from the issue author (or a repo collaborator) that starts with a fixed prefix such as `/answer` or `/feedback`, feeding it through `job answer` or `job feedback`. Treat comment text as untrusted input. Best effort: no `gh` means no change.
