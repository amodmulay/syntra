# Spec: durable job records (build line, rescoped slice of topic 011)

Job: 011-keep-finished-job-records-across-devices
Line: build. Risk: high. Surfaces: ui, security.
Source: topic.md (quoted data), triage.md (DECISION: ACCEPT, RESCOPED: yes).

## Goal

A finished job's cost and summary must survive outside the gitignored `factory/jobs/`
folder and be visible on every machine that has the repository. This slice:

1. `factory/bin/job` writes `factory/records/<job-id>.json` when a job reaches `merged`
   on its final line (not a handoff), and when a job is `rejected`.
2. The dashboard shows a card, with cost, for every record that has no local
   `factory/jobs/<job-id>/` folder, labelled "Recorded on another device".

Out of scope (see Exclusions): GitHub label/Project/comment work, backfill, ledger changes,
cost inference from the ledger, pushing.

## Decisions (binding; the builder has no open questions)

### D1. Who commits, and where

**Merge (final line): the record is committed on the job branch by `factory/bin/job`, inside
`land()`, so it reaches base in the same fast-forward that lands the work.** No merge commit is
created for it, no commit is made on base directly, and nothing is pushed. Concretely, base
receives one extra commit at the tip of the landed branch: the record commit, which touches only
`factory/records/<job-id>.json`.

**Reject: the record is written to the main checkout's working tree and is NOT committed.**
The reject path has no merge, the job branch is deleted by the reject transition, and committing
onto base from a command that may run on a dirty or non-base main checkout is unsafe. The command
prints the exact follow-up for the operator, as two separate commands, each with a pathspec and
no `&&`: `git -C <repo root> add -- factory/records/<job-id>.json` and
`git -C <repo root> commit -m "Record rejected job <job-id>" -- factory/records/<job-id>.json`.
Consequence to state plainly: a rejected job's record is not durable across devices until the
operator commits it. This is an accepted gap for this slice.

**Nothing pushes**, on either path. Pushing stays with the operator.

### D2. Ordering and failure handling

**Merge path.** Inside `land(job, record)` the order becomes:

1. `git merge --no-edit <BASE>` into the job branch (unchanged).
2. Gate with `--merge` (unchanged). The gate verdict covers the commit that exists at this point.
3. If `record` is true (final line only):
   a. `pre = rev-parse HEAD` in the job worktree.
   b. Write `factory/records/<job-id>.json` in the job worktree from `job_record(...)` (see D3).
      `ended` is the value the branch's record already holds (a re-run), else `now()`. The job's own
      `ended` is not used: `advance` clears it while a job is merging.
   c. `git add -- factory/records/<job-id>.json`.
   d. If `git diff --cached --quiet -- <that path>` reports no change (identical content on a
      re-run), skip the commit. Otherwise `git commit -m "Record job <job-id> (merged)" -- <that path>`.
      The pathspec form commits only that file, even if something else is staged.
   e. Any `OSError`, `Refused` or non-zero git exit in 3a-3d: undo only this attempt, then raise
      `Refused` with a message starting "couldn't write the job record". The undo (round 2, replaces
      `git reset --hard`, which could destroy uncommitted work): `update-ref HEAD <pre> <cur>` as a
      compare-and-swap, only when HEAD is `pre` or the commit directly on it; then `git reset -q --`
      the record path (or `git checkout <pre> --` it, if `pre` tracked it) and remove the file. The
      work tree keeps every other edit. The result is checked (HEAD back on `pre`, no record entry in
      `git status`); any problem is appended to the Refused message.
4. `tip = rev-parse HEAD`, then the existing fast-forward of `BASE` to `tip` (unchanged).
   If that fast-forward raises `Refused` and `record` is true, run the same undo as 3e before
   re-raising, so the branch carries no orphan record commit.

Failure in any step means base has not moved. `cmd_merge` already catches `Refused` from `land`,
calls `escalate`, and moves the job to `needs-human`. That existing path is reused unchanged. No
record is written for a job that ends in `needs-human`.

Known residual window, unchanged from today: if `save(sync(job))` fails after `land` has
fast-forwarded base, the job stays in `merging` while base holds the work. The record is already
on base at that point, so it is not lost. Re-running `job merge` is safe: `land` is idempotent and
rewrites the record.

**Reject path.** In `cmd_reject`, after `rejection.md` is written and before `advance`:

1. Build the record from `dict(sync(job), stage="rejected", ended=now())` in memory, and write
   `RECORDS/<job-id>.json` in the main checkout (no git operation). Round 2: `ended` stays `now()`
   here, because a waiting job's `ended` is when it started waiting, not when it was rejected.
2. Write `rejection.md`. If that fails, remove the record just written and die. Round 2 order,
   so a failed record leaves no rejection marker behind.
3. Only then `save(sync(advance(sync(job), "rejected")))`, as today. `advance` drops the worktree,
   so the record must be written before it.

If step 2 fails (`OSError`), call `die(...)` with a message saying the record could not be
written and the job is still waiting. The job stays in `needs-human` or `needs-info`, the worktree
is intact, and the operator can re-run `job reject`. If step 3's save fails after step 2 succeeded,
the record exists while job.json still says waiting; re-running `job reject` overwrites the record.

### D3. Record contents (allowlist; nothing else)

`job_record(job)` returns exactly these keys, JSON-encoded with `indent=2, sort_keys=True` and a
trailing newline:

```
{
  "id":       job["id"],                 # e.g. "011-keep-finished-job-records-across-devices"
  "topic":    job["topic"],              # the inbox slug, a filename stem
  "stage":    "merged" | "rejected",
  "line":     job["line"],               # the final line
  "pass":     job["pass"],               # int
  "triage":   {"decision", "line", "risk", "surfaces"},   # from job["triage"], same keys
  "started":  job["started"],            # ISO UTC, "Z"
  "ended":    <now() when the record is built>,
  "cost_usd": job["cost_usd"],           # float, from sync
  "models":   job["models"]              # list of {step, model, calls, tokens, cost}, as synced
}
```

Forbidden in the record: the topic body, any part of `topic.md`, `worktree`, `branch`, `passes`,
`handoff_to`, `agents`, `reviews`, `interventions`, any absolute path, any environment value, any
transcript text. `triage.surfaces` is a list of strings; `triage` values that are None are written
as null. `ended` may differ by about a second from the job.json `ended` that `advance` sets; that
is accepted.

The id must match `[0-9A-Za-z][0-9A-Za-z._-]*` before it is used in a filename. If not, raise
`Refused` (merge path: needs-human; reject path: die). This blocks path traversal.

Round 2: `title` is dropped from the allowlist (privacy: the title is user-authored and would be
committed to base). The dashboard labels a record from its id slug instead. Also round 2: the
records directory and its parent must not be symlinks; a write through one is refused.

`RECORDS = FACTORY / "records"`. The file is `RECORDS/<id>.json` in the main checkout for reject,
and `<worktree>/factory/records/<id>.json` for merge.

No ledger reads. `cost_usd` and `models` come only from the job's own synced values.

### D4. Which transitions write a record

- `merged` via `cmd_merge` when `LINES[job["line"]].get("handoff")` is falsy: writes (D2 merge).
- `merged` via a handoff (`handoff` set): no record. The `spec` transition to the next line is
  not terminal.
- `rejected` via `cmd_reject`: writes (D2 reject).
- `rejected` via any other path: none exists today; none is added.
- Every other stage (including `needs-info`, `needs-human`, and all in-progress stages): no record.

`cmd_merge` computes `final = not LINES[job["line"]].get("handoff")` before calling `land`, and
passes it as `land(job, record=final)`.

### D5. Ids and numbering (small addition, required by this slice)

`cmd_create` picks the next number from the local `JOBS` folders only. A record from another
device could then share a number with a new local job. Change the numbering so it also considers
`RECORDS/*.json` (`p.stem[:3]`). The next id is `max(numbers) + 1`, as today. Records do not
otherwise affect `cmd_create`, `cmd_queue`, `cmd_summary` or `resolve`.

### D6. Dashboard discovery (`factory/dashboard.html`)

The dashboard is served by `python -m http.server` with root `factory/` (see `factory/bin/dashboard`),
so `records/` is reachable at `records/` relative to `dashboard.html`.

- Listing: `fetchText('records/')` parsed with `DOMParser`, the same way `loadJobs` reads `jobs/`.
  Take anchors whose href ends in `.json`. A 404 (no `records/` folder yet) means no records, not an error.
- Fetch each `records/<name>.json` with `fetchText`, parse, and skip anything that fails to parse or
  lacks `id` or `stage` (round 2: `title` is no longer a record field). Cache parsed records in a `Map` keyed by file name, so the poll
  loop (every 2 s) does not refetch unchanged files; the listing itself is re-read each poll.
- Dedupe: a record whose `id` equals the `id` of a local job is not shown. The local job wins.
- Keep records in a separate array (`records`), not in `jobs`. `renderStats`, `refreshDrawer`,
  `autonomy` and `roundVerdicts` keep operating on local jobs only.
- Render: each record becomes a card in the "Done" column (its stages are `merged` or `rejected`),
  using the same card markup as local cards. It shows: id, a label taken from the id slug (numeric
  prefix dropped, hyphens replaced by spaces; round 2, no title), stage (rejected is struck through as
  today), line and pass, risk from `triage.risk`, models chip, `$cost_usd` with two decimals, and
  elapsed time from `started` to `ended`. Rejected records keep the same `<span class="flag wait">rejected</span>`
  flag as local rejected jobs. Every record also carries a separate visible line, "Recorded on another
  device", with a `title` tooltip "This summary was saved from another machine. This machine has no
  job folder, so there is no detail view.". Round 2: no `<topic>.md` link line. Done cards, local and record, are interleaved
  by `ended`, newest first.
- Record cards have no `data-job` attribute, so clicking them does not open the drawer (there is no
  folder to read). They are not focusable as job cards.
- Footer totals: `$` total includes the record costs; the running count does not change.
- Task statistics table and "Not picked up" view: local jobs only. Record-only jobs are not added.
- Every value from a record is passed through the existing `esc()`. The id is also checked against
  `/^[0-9A-Za-z][0-9A-Za-z._-]*$/` before it is used in any attribute.

### D7. Tests

Add `tests/test_job_records.py` (picked up by `unittest discover -s tests`, so it runs in the gate).
It loads `factory/bin/job` by path, since the file has no `.py` suffix:

```python
import importlib.machinery, importlib.util
loader = importlib.machinery.SourceFileLoader("job_bin", str(REAL_REPO / "factory" / "bin" / "job"))
spec = importlib.util.spec_from_loader("job_bin", loader)
job = importlib.util.module_from_spec(spec); loader.exec_module(job)
```

Test isolation requirements (the builder must follow these or tests will touch the real repo):

- Patch module globals per test: `JOBS`, `INBOX`, `RECORDS`, `REPO`, `FACTORY`, `BIN`.
  `BIN` points to a temp dir holding a fake `gate` script. It exits 0, or 1 in the gate-failure test.
- `run()` has `cwd=REPO` bound as a default argument at definition time, and `land()` and
  `drop_worktree()` call `run` without `cwd`. Patching `REPO` does NOT redirect them. Replace the
  module attribute: `real_run = job.run; job.run = lambda cmd, cwd=None, check=True: real_run(cmd, cwd=cwd or TMP_REPO, check=check)`.
- `job.ingest_usage` is replaced with a no-op (otherwise save writes the real ledger).
- `job.usage_by_step` is replaced to return `[]` (otherwise sync reads the real transcripts).
- Temp git repo: `git init -b main`, set local `user.name` and `user.email`, make one commit on main.
  Job worktree is under the temp dir, not `REPO/.worktrees`. Create the job branch and worktree
  with `git worktree add -b`, commit a change in the worktree, set `job["stage"] = "merging"`,
  `job["line"] = "build"` (or `"docs"` for the no-handoff case), `job["pass"] = 1`,
  `job["round"] = 1`, `job["agents"] = {"reviewers": {}}`, and write `job.json` with `save`.
- Topic: write `INBOX/<topic>.md` with a `# Title` line.

Exact tests (round 2 adds the tests listed under "Round 2 test additions" below):

1. `test_record_has_only_allowlisted_fields`: `job_record(job)` keys equal exactly
   `{id, topic, stage, line, pass, triage, started, ended, cost_usd, models}`; `triage` keys
   equal `{decision, line, risk, surfaces}`; the JSON text contains neither the temp repo path nor the
   worktree path nor the topic body.
2. `test_record_id_rejects_traversal`: `write_record` (or the id check) rejects `"../x"` and `"a/b"`.
3. `test_merge_final_line_commits_record_to_base`: `cmd_merge(job)` on a `docs`-type final line (no handoff);
   assert `main` tip's commit touches only `factory/records/<id>.json` (use
   `git show --name-only --format= main`); the file's JSON has `stage == "merged"`, `cost_usd`,
   `models`; `job.json` stage is `merged`; the job branch no longer exists.
4. `test_merge_handoff_writes_no_record`: a `build` line (handoff `docs`). Assert no `RECORDS` file and
   no `factory/records` path in `git log --name-only main`; the job is in `spec` (next pass).
5. `test_gate_failure_writes_no_record`: fake gate exits 1. Assert base sha unchanged, no record
   file in the worktree or on base, job stage `needs-human`.
6. `test_record_commit_failure_leaves_base_untouched`: monkeypatch the function that writes and
   commits the record so it raises `OSError`. Assert base sha unchanged, the job branch tip equals
   its pre-record commit (no orphan record commit), job stage `needs-human`.
7. `test_reject_writes_uncommitted_record`: a job in `needs-human` with a worktree. `cmd_reject(job, "reason")`.
   Assert `RECORDS/<id>.json` exists with `stage == "rejected"`; `git status --porcelain` in the main
   checkout lists it as untracked (`??`); base sha unchanged; job stage `rejected`; worktree and
   branch removed.
8. `test_reject_record_failure_keeps_job_waiting`: make `RECORDS` a path whose parent is a regular
   file, so `mkdir` fails. Call `cmd_reject`; expect `SystemExit`; job.json stage still `needs-human`;
   worktree still present.
9. `test_create_numbering_skips_recorded_ids`: `RECORDS` contains `005-old-topic.json`, `JOBS` is empty;
   `cmd_create("new-topic")` yields `006-new-topic`.
10. `test_no_record_for_in_progress_stages`: after `cmd_create` and `advance` to `spec`, `RECORDS` is not
    created.
11. `test_dashboard_reads_records_and_dedupes`: read `factory/dashboard.html` as text and assert it
    contains `fetchText('records/')` (or the literal `'records/'`), the string `Recorded on another device`
    (round 3: replaces `record only`/`from record` as the visible label), and the
    dedupe on job id (the record filter that checks `jobIds`). Static check only; behaviour is verified
    manually (below).

Manual dashboard check (required, since the JS is not covered by unittest): in a scratch copy of
`factory/` (not the real one), add `records/<id>.json` for an id that has no local job, plus a second
record for an id that does have a local job. Serve it with `python -m http.server` from that copy's
`factory/`, open `dashboard.html`, and confirm: the record-only card appears in Done with its cost and
"Recorded on another device"; the duplicate id shows once (the local card); clicking a record card does not open the
drawer or show an error; with no `records/` folder the board is unchanged. Record the result in the
builder's report.

### D8. Documentation

Keep AGENTS.md and CLAUDE.md in step (CLAUDE.md requires it): one sentence each under the
State description, saying that `factory/records/<job-id>.json` is a tracked, committed summary written
by `factory/bin/job` at final merge and at reject, and that reject records must be committed by hand.
Do not change the protected-paths wording (see Exclusions).

Round 2: AGENTS.md carries this note as its own bullet. CLAUDE.md is NOT changed on this branch: the
round-1 sentence was self-contradictory, and CLAUDE.md edits need human confirmation. The operator adds
the same bullet to CLAUDE.md (see build.md). GETTING_STARTED.md gets a short note on reject records.

## Round 2 deviations and additions (fixes for round-1 review)

- Deviation, merging to needs-human: a refused land goes through `refuse_land(job, why)` only, which
  `cmd_merge` calls from its `except Refused` block. It writes `decision.md` (starting `ESCALATE`),
  sets `stage` to `needs-human` and `ended`, and does not check the branch against base, because the
  branch is not on base by definition. `advance()` has no needs-human special case and no `decision.md`
  test: its ancestor check runs unconditionally for every `merging` exit, so `advance(merging ->
  needs-human)` is refused when the branch is not on base. `refuse_land` leaves `passes[-1]["outcome"]`
  unset.
- Deviation, `ended` in merge records: pinned to the value an earlier attempt committed on the branch.
- Deviation, reject ordering: record, then rejection.md, then advance (see D2 reject).
- Round 2 test additions (in `tests/test_job_records.py`): reject-record failure leaves no rejection.md and
  a retry works; a rejection.md failure removes the record; a symlinked records dir is refused (skipped
  where symlinks are unavailable, e.g. Windows without the privilege); a re-run of `land` adds no second
  record commit; `commit_record` skips identical content; a failed fast-forward resets to pre and keeps
  uncommitted edits; an invalid job id on the merge path goes to needs-human; `test_merging_to_needs_human_keeps_ancestor_check`
  (replacing the old ESCALATE-guard test): with ESCALATE on disk, `advance(merging -> needs-human)` still
  raises `Refused` and the stage stays `merging`, and `refuse_land` then moves the job to `needs-human`
  with the outcome unset; the merge output says nothing was pushed.
- The manual dashboard check (D7) is still NOT run.

## Acceptance criteria

- AC1: After `job merge` of a final-line job, base contains `factory/records/<job-id>.json` in the
  same fast-forward as the work. There is no second commit on base from the record path, and no push.
- AC2: After `job merge` of a job with a handoff, no record file is written and no record commit exists.
- AC3: After `job reject`, `factory/records/<job-id>.json` exists in the main checkout, is uncommitted,
  and contains `stage: rejected`.
- AC4: A failure while writing or committing the merge record leaves base at its prior sha and the
  job in `needs-human`, with the job branch tip equal to its pre-record commit.
- AC5: A failure while writing the reject record leaves the job in its prior waiting stage with its
  worktree intact.
- AC6: Record contents match the D3 allowlist exactly; no topic body, absolute path or secret appears.
- AC7: Ids that would escape `factory/records/` are refused.
- AC8: `cmd_create` never reuses an id that exists as a record.
- AC9: The dashboard shows each record-only job as a Done card with its cost and a "Recorded on another device" label,
  and does not show a record whose id matches a local job.
- AC10: Record cards do not open the drawer. Local jobs render as before.
- AC11: `python3 -m py_compile src/*.py && python3 -m unittest discover -s tests -v` passes, including
  the eleven tests in D7 (run from the repo root).
- AC12: `factory/checks.sh` and `factory/config.json` are byte-identical to before the change.
- AC13: `factory/usage/ledger.jsonl` is not modified by the tests or the implementation.
- AC14: The ledger is not read by any new code.

## Exclusions

- GitHub issue status work: `factory-done` and `factory-rejected` labels, Project board Status, rejection
  comments, getting-started docs. Carved off (separate topic, needs human confirmation).
- Backfill of existing finished jobs into `factory/records/`.
- Changes to `factory/usage/ledger.jsonl`, or any cost inference from it.
- Pushing, or any `git push`, on any path.
- Committing reject records automatically (D1 makes this an operator step).
- Changes to `factory/checks.sh` (protected) or to `protected_paths`.
- The CLAUDE.md/AGENTS.md mismatch about whether `factory/bin/job` is protected. Config lists only
  `factory/checks.sh`. Flag for a separate docs fix; do not change it here.
- `cmd_queue` and `cmd_create` do not treat a recorded-but-absent topic specially. On a machine whose
  inbox still holds a topic that finished elsewhere, `/factory run` would start it again. Known gap,
  separate decision.
- Task statistics and "Not picked up" views for record-only jobs.
- Any new dependency. Stdlib only.
- Changes to `src/` or `tests/test_calculator.py`.
- Record schema versioning and migration.

## Security notes for the reviewer

- Records are committed and may be public. Contents are limited to D3. Triage fields, models and cost are
  accepted for this repository per the topic. Round 2: `title` is removed from records, since it is
  user-authored and the merge record commit goes to base after the gate with no review. `topic` (the
  inbox slug) and the triage fields remain. Human confirmation of privacy remains an open question for the operator.
- The record commit is an extra commit on the job branch after the gate. It adds one new, non-protected
  file, so `gate.protected_changes` is unaffected.
- The state change is inside `land()`, before any base mutation, so a failure cannot half-transition base.
- Path traversal is blocked by the id regex (D3).
- The reset in D2 uses the pre-record commit recorded in the same call, never a relative `HEAD~1`.

## Checks (what the builder must run)

1. `python3 -m py_compile src/*.py` and `python3 -m unittest discover -s tests -v` from the repo root.
2. `python3 -m py_compile factory/bin/job factory/bin/dashboard`.
3. Manual dashboard check in D7.
4. `git status` shows only: `factory/bin/job`, `factory/dashboard.html`, `tests/test_job_records.py`,
   `AGENTS.md`, `CLAUDE.md`, and (new) `factory/records/` is not created in the repo by the tests.
