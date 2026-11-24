STATUS: READY

# Build: durable job records (topic 011, rescoped slice), round 2

Branch: `factory/011-keep-finished-job-records-across-devices`
Round-1 commits: `0b6bef5`, `960b915`. Round-2 commit: `409b777 Harden finished-job record handling (round 2 review fixes)`.
Worktree: `D:/repo/syntra/.worktrees/011-keep-finished-job-records-across-devices`

## Round-1 review items, and what changed

1. Reject ordering (`cmd_reject`, `factory/bin/job`). Order is now: build and write the record to `RECORDS`, then write `rejection.md`, then `advance`. If the record write fails, the job stays waiting with its worktree and no `rejection.md`. If `rejection.md` fails, the record is removed. Both die messages say the job is unchanged and to fix the cause and re-run `job reject <id>` with the reason on stdin. Test: `test_reject_record_failure_keeps_job_waiting` (also checks no rejection.md, then re-runs successfully). `test_reject_removes_record_when_rejection_file_fails`.
2. Undo without `reset --hard` (`undo_record`). The undo moves the branch with `update-ref HEAD <pre> <cur>` (compare-and-swap, only when HEAD is `pre` or the commit directly on it). Then it runs `git reset -q -- <rel>`, or `git checkout <pre> -- <rel>` if `pre` tracked the file, and removes the record file. It checks the result (HEAD back on pre, no status entry for the record). Any problem is added to the Refused text (`record_refusal`). Test: `test_failed_fast_forward_resets_branch_and_keeps_edits`. It makes the real ff of base fail after a real record commit, with a modified tracked file and an untracked file in the worktree, and asserts both survive, the branch tip is back at pre, and the status shows only those two entries.
3. Privacy. `title` is removed from `job_record` and from the record keys. The dashboard record card label is the id slug (numeric prefix dropped, hyphens to spaces). Record cards show "record only" (for rejected: "rejected · record only"). The `title` requirement in `loadRecords` is removed. Test: `RECORD_KEYS` has no title. Dashboard static test updated.
4. Symlinks. `write_record` refuses when the records dir or its parent is a symlink (`Refused`). Test: `test_write_record_refuses_symlinked_records_dir`. On this Windows machine `os.symlink` needs a privilege, so the test is SKIPPED here. It has not been exercised.
5. `ended` pin. `record_ended(job)` takes `ended` from the record the branch already holds at `HEAD:factory/records/<id>.json`, else `now()`. `job["ended"]` is not used, because `advance` clears it while merging (per the advisor). Reject keeps `now()`. Tests: `test_rerun_land_adds_no_second_record_commit` (calls `land(job, record=True)` twice with `now` returning a new value on each call; main and the branch tip are unchanged after the second call) and `test_commit_record_skips_identical_content`.
6. Tests added: merging to needs-human is refused without ESCALATE and allowed with it (`test_merging_to_needs_human_requires_escalate`); ff failure resets to pre (above); invalid job id on the merge path goes to needs-human (`test_invalid_job_id_on_merge_path_goes_to_needs_human`, id `001-new+topic`). Also fixed: `advance` set `outcome = "merged"` for a failed land too. It now sets it only for `stage == "merged"`. The guard deviation is noted in spec.md (see below).
7. Output. The reject follow-up is two lines: `git -C "<repo root>" add -- <rel>` and `git -C "<repo root>" commit -m "Record rejected job <id>" -- <rel>`, with no `&&`. The merge success output adds a line: "record factory/records/<id>.json was committed with the work; nothing was pushed." The failed-record message begins "couldn't write the job record: base is unchanged; fix the cause and re-run `job merge <id>`, or reject the job with `job reject <id>`", then "Cause: ...". The advance() error text no longer says "escalate first".
8. Dashboard (`factory/dashboard.html`).
   - `.flag.record` is neutral (`--muted`). The visible text is "record only".
   - `.card.record` has `cursor: default` and no hover lift.
   - Done cards are no longer faded in dark (`opacity` removed). `.card.done .feature` and `.card.done .links` use `--muted` in both themes. Contrast: dark `--muted` on `--card` is 4.68:1. Done cards also keep `--card` on hover (`.card.done:hover`), because `--muted` on `--card-hover` measured 4.33:1. Light `--muted` on `--card` is 6.74:1. `--faint` (2.54:1 in dark) is no longer used for Done text.
   - The `<topic>.md` link line is dropped from record cards.
   - `elapsed()` returns "—" when `started` is missing or invalid.
   - Done cards (local and record) are sorted by `ended` (ascending sort, then the existing reverse). Other columns are unchanged. Records carry `ended` as a string, or "" if absent.
   - `.meta` wraps (`flex-wrap: wrap`).
   Node check on the extracted script: OK.
9. Docs.
   - CLAUDE.md is REVERTED to the base version (`68faa63`) on this branch. The records sentence is not in CLAUDE.md. Reason: CLAUDE.md edits need human confirmation, and the round-1 sentence contradicted itself. See "Needs the operator" below.
   - AGENTS.md: the State line is split. The records note is its own bullet: it is committed with the work at merge, and at reject it is written but not committed, so the operator commits it by hand and nothing is pushed.
   - GETTING_STARTED.md: a short paragraph after the reject sentence says the reject writes the record, nothing commits or pushes it, and the operator commits it by hand using the printed command.

## spec.md

The spec was edited to match (`factory/jobs/011-.../01-build/spec.md`, as this round requested): D1 (printed follow-up), D2 (merge undo, `ended`, reject order), D3 (no title, symlink refusal), D6 (label, "record only", no topic line, Done interleave, no `title` requirement), D7 test list (`record only`), AC9, the security note on title, and D8 (CLAUDE.md not changed). A new section "Round 2 deviations and additions" lists the guard deviation, the `ended` pin, the reject ordering, and the new tests.

## Checks

- `bash factory/checks.sh` from the worktree: exit 0. Ran 25 tests, OK, 1 skipped (the symlink test, see item 4).
- `python3 -m py_compile src/*.py` and `python3 -m py_compile factory/bin/job factory/bin/dashboard`: OK.
- `node --check` on the extracted dashboard script: OK (`/d/node/node`).
- `factory/checks.sh`, `factory/config.json`, `factory/usage/ledger.jsonl`, `src/`, `tests/test_calculator.py`: unchanged versus `68faa63`.

## Needs the operator

- MANUAL DASHBOARD CHECK IS STILL NOT RUN. It is required by spec D7 and is not covered by unittest. Still to do, in a scratch copy of `factory/` (not the real one): put `records/<id>.json` for an id with no local job, and a second record for an id that has a local job. Serve with `python -m http.server` from that copy's `factory/` and open `dashboard.html`. Check: the record-only card is in Done with its cost and a "record only" tag; the duplicate id shows once (the local card); clicking a record card does not open the drawer and shows no error; with no `records/` folder the board is unchanged; the listing hrefs are bare file names. The browser check was not run this round either.
- CLAUDE.md: add the records bullet by hand after the State bullet, using the AGENTS.md wording, if you want CLAUDE.md in step with AGENTS.md (spec D8). It was reverted here, not edited.
- Privacy confirmation (spec security notes) is still open for the operator. Records now carry `topic` (the inbox slug), triage fields, models and cost. `title` is removed.

## Known limits (unchanged from the spec)

- Rejected records are not durable until the operator commits them.
- A topic that finished on another machine can still be started again by `/factory run` (spec Exclusions).
- The dashboard record cache is keyed by file name. A rewritten record shows its old contents until reload.
- Records are not backfilled.
- Nothing is pushed on any path.
