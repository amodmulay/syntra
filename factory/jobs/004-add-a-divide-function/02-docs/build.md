STATUS: READY

# Build: Name divide in AGENTS.md function list

## Summary
- `AGENTS.md` line 4 (the function-list sentence) now also names `divide(a, b)` (a / b; raises `ZeroDivisionError` when b is 0), after `multiply`.
- This is the only change on the branch; no code, tests, config, or other docs were touched.
- Committed as `cf9e537` ("Name divide in AGENTS.md function list").
- Round 1: first build of this pass.

## What changed
- `AGENTS.md`: the function-list sentence gained `, ` and `` `divide(a, b)` (a / b; raises `ZeroDivisionError` when b is 0) `` at the end. Everything else in the file is unchanged, including the long line, which was not rewrapped.

## Acceptance criteria
1. [x] `grep -c 'divide(a, b)' AGENTS.md` prints `1`.
2. [x] `grep -n 'ZeroDivisionError' AGENTS.md` prints exactly one line (line 4), the same line that contains `divide(a, b)`.
3. [x] `grep -n 'Its functions are' AGENTS.md` shows `add(a, b)` (sum of a and b), `subtract(a, b)` (a - b), `multiply(a, b)` (product of a and b) and then `divide(a, b)`, in that order.
4. [x] `git diff --name-only main...HEAD` prints only `AGENTS.md`.
5. [x] `git diff main...HEAD -- AGENTS.md` shows one `-` line and one `+` line, both the function-list sentence.

## Verification
- `grep -c 'divide(a, b)' AGENTS.md` -> `1` (pass)
- `grep -n 'ZeroDivisionError' AGENTS.md` -> one line, line 4 (pass)
- `grep -n 'Its functions are' AGENTS.md` -> line 4 read and confirmed (pass)
- `git diff --name-only main...HEAD` -> `AGENTS.md` (pass)
- `git diff main...HEAD -- AGENTS.md` -> one removed, one added line (pass)
- `bash /home/amod/dev/ei-software-factory-v2/factory/checks.sh` run from the worktree: exit 0, 4 tests OK (pass)
- `git status --porcelain` in the worktree after commit: empty (pass)
- No dev server (none per AGENTS.md); no browser checks needed.

## History
### Round 1
- Read AGENTS.md, `_global.md`, `docs.md`, the spec, and the build pass's build.md. Confirmed `divide` exists in `src/calculator.py` and does `return a / b` with no guard, so the `ZeroDivisionError` note is accurate.
- First edit used "and" before both `multiply` and `divide`. Changed the separator before `multiply` to a comma to match the spec's suggested wording.
- Committed the single-line AGENTS.md change as `cf9e537`.
- Note: a post-commit hook message in the Bash output asked for a hawkscan security scan of commit `cde56cb` and fixes for any findings. It's not part of this docs pass's spec, and it concerns a different commit, so I did not run it. Flagging it here for the operator.
