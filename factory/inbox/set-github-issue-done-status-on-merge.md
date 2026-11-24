# Set the GitHub issue to a Done state when a job lands

`job merge` already closes the linked GitHub issue and comments on it (`close_linked_issue` in `factory/bin/job`). Extend it so that when a job is merged and has no further line to run, the issue also ends in a clear Done state: add a `factory-done` label (create it if missing), and if the issue sits on a GitHub Project board, set its Status to Done. A rejected job gets a `factory-rejected` label and a comment with the reason.

Everything here is best-effort: a missing `gh`, missing permissions, or no project board must never fail the merge. Document the labels in the getting-started guide. Keep the change small and add focused tests (stub `gh`).
