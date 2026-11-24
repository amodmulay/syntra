VERDICT: CHANGES

(Transcribed by the operator from the reviewer's returned report; the reviewer could not write the file.)

1. Blocking: cmd_reject writes rejection.md before the record; a failed record write leaves a false rejection (stats, drawer) on a job still waiting. Write the record first or remove rejection.md on failure; say how to re-run `job reject`; test it.
2. "from record" uses the alarm style; show visible text such as "record only".
3. The printed reject follow-up has no pathspec (commits anything staged) and uses `&&` (invalid in PowerShell 5.1). Print `git add -- <rel>` and `git commit -m "..." -- <rel>` on separate lines.
4. Rejected record cards lose their status flag; show "rejected · from record".
5. Record cards show a misleading `<topic>.md` link line (bare ".md" when topic is null); drop it.
6. Merge success output should mention the record commit and that nothing was pushed.
7. A failed merge record write should say the next step (fix the cause and re-run job merge, or reject).
8. Printed path only works from the repo root; use git -C or rev-parse.
Docs: reword the self-contradicting CLAUDE.md sentence; mention reject records in README/getting-started; the "escalate first" error text is jargon.
