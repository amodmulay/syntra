STATUS: READY

# Build: job 011 round 3 (last round) fixes for the four round-2 reviews

Branch: `factory/011-keep-finished-job-records-across-devices`
Commit: `34c1980 Harden job record writes and fix record card layout (job 011, round 3)`
Worktree: `/home/amod/dev-private/syntra/.worktrees/011-keep-finished-job-records-across-devices`
Base for the change: `40487c5`

Files changed: `factory/bin/job`, `factory/dashboard.html`, `tests/test_job_records.py`. Nothing else was committed. `factory/checks.sh` and `factory/config.json` were not touched. The `.pyc` files were not committed.

## Open item for the spec owner (item 4)

`spec.md` was NOT edited. It sits in the main checkout's `factory/jobs/` as an agent output, and the build rules forbid editing agent outputs. The corrected text below is ready to apply. Until someone does, `spec.md` still describes the removed ESCALATE guard, so the item-4 reviewer finding stays open. Replace the two "Deviation, merging to needs-human" bullets (spec lines ~260-263) and the test sentence (spec lines ~270-271) with:

- Merging to needs-human: a refused land goes through `refuse_land(job, why)` only, which `cmd_merge` calls from its `except Refused` block. It writes `decision.md` (starting `ESCALATE`), sets `stage` to `needs-human` and `ended`, and does not check the branch against base, because the branch is not on base by definition. `advance()` has no needs-human special case and no `decision.md` test: its ancestor check runs unconditionally for every `merging` exit, so `advance(merging -> needs-human)` is refused when the branch is not on base. `refuse_land` leaves `passes[-1]["outcome"]` unset.
- Test: `test_merging_to_needs_human_keeps_ancestor_check` (tests/test_job_records.py). With ESCALATE on disk, `advance(merging -> needs-human)` raises `Refused` and the stage stays `merging`; `refuse_land` then moves the job to `needs-human` with the outcome unset. This replaces the ESCALATE-guard test named in the old text.

Also in spec.md, replace the visible tag wording "record only" / "from record" with "Recorded on another device" (lines ~15, ~165-167, ~234-235, ~243, ~288-289). Tooltip and tag text are in the code now.

## Item by item

1. HIGH, stored `job["worktree"]` in record writes and undo. Fixed. `commit_record` now writes under `worktree_path(job)`, and `undo_record`'s unlink uses `worktree_path(job)` too, the same root as `commit_record`. The stored value is not read anywhere in the record path. Test: `test_record_ignores_foreign_stored_worktree` sets `job["worktree"]` to a directory outside `.worktrees/`, runs `cmd_merge`, and checks the directory is never created and the record lands on base.

2. MEDIUM, symlink check on the record file. Fixed. `write_record` refuses when `root/<id>.json` is a symlink, before `write_text` (which would follow it). Test: `test_write_record_refuses_symlinked_record_file` links the record path to an outside file and checks the file is unchanged.

3. MEDIUM, non-Refused exceptions from `job_record`. Fixed by making `job_record` raise `Refused`. A non-object `triage`, a non-numeric `cost_usd`, and a `models` value that is not a list of objects are each checked and raised as `Refused`. `land()`'s existing `except (OSError, Refused)` then runs `record_refusal`, and `cmd_merge` sends the job to needs-human. Test: `test_job_record_refuses_bad_synced_fields_as_refused`. I first tried a `cmd_merge`-level test, but `sync()` fails on a bad `cost_usd` before `land()` runs. That is pre-existing and outside the record path (see residual notes), so the test calls `job_record` directly.

4. CODE, stale spec text. Content resolved in the block above. `spec.md` itself is not edited (see the open item).

5. UX, hover on Done cards. Fixed. `.card.done:hover` no longer removes the background. The rule is now `.card.done:not(.record):hover { background: var(--card-hover) }` plus `.card.done:not(.record):hover .feature/.links { color: var(--text) }`. Local Done cards keep a hover state and the drawer still opens. The text goes to `--text` on hover because `--muted` on `--card-hover` is 4.33:1. Record cards keep `.card.record:hover { background: var(--card); transform: none }`, so they stay non-interactive. Test: the dashboard static test asserts the `:not(.record):hover` rule exists.

6. UX, duplicate id and jargon. Fixed. The header shows only the number (e.g. `011`). The title is the slug spaced out. A visible line reads "Recorded on another device", with a plain-language tooltip ("This summary was saved from another machine. This machine has no job folder, so there is no detail view."). The old "from record" / "no job folder" tooltip text is gone. The dashboard test now asserts "Recorded on another device".

7. UX, `pass` rendering "null"/"undefined". Fixed. The pass segment renders only when `r.pass != null`, so a missing pass leaves just the line. Checked in the screenshot with a merged fixture that has no `pass`.

8. UX, `elapsed()` growing for a record with no `ended`. Fixed in `recordCard`: the elapsed value is `r.ended ? elapsed(r) : '—'`. `loadRecords` sets a missing `ended` to `''`, so the card shows `—` and does not start a live timer. `elapsed()` itself is unchanged for local jobs, which still run live.

9. UI, header squeeze and overflow at 1600, 1280, 640. Fixed. The flag is now only `rejected` (short) and the record-only text moved to its own wrapping line (`.origin`, with `overflow-wrap: anywhere`). The number has `flex-shrink: 0`, and the long title wraps. Verified with headless Chrome (google-chrome --headless) against a scratch copy of the dashboard in the scratchpad (not the real factory), with a rejected record (011) and a merged record with no pass and no ended (002). Screenshots at 1600 and 1280 show the id intact, the rejected flag inside the border, and `—` for the missing end time. The 640 screenshot shows the card stacked and inside its border.

## Checks

- `python3 -m py_compile src/*.py && python3 -m unittest discover -s tests -v`: 48 tests, OK. The 22 `test_job_records` tests include the new ones.
- `bash factory/checks.sh`: exit 0, 48 tests OK.
- `git status` after the commit: clean. Only the three intended files were committed.

## Residual notes (not fixed in this round)

- `sync()` (factory/bin/job, around line 441) computes `max(job.get("cost_usd") or 0.0, ...)` and raises `TypeError` on a non-numeric `cost_usd` before `land()` runs. This is pre-existing and affects any job field, not just records. The record path is covered by item 3. A job with a non-numeric `cost_usd` still gets a traceback at `sync`, not needs-human. Out of scope for this record fix.
- `advance()`'s merging branch uses `else: outcome = "merged"` (main's code), so `advance(merging -> needs-human)` on a branch that is on base would set the outcome to "merged". No caller in the job script does this; `refuse_land` is the only path to needs-human from merging. Changing the branch would make the code diverge from main, so it is noted, not changed.
- Local Done card hover was checked from CSS only; the screenshots show record cards, not a hover state.
- A post-commit hook prompted a hawkscan run. It was not run, per the instruction for this round.
