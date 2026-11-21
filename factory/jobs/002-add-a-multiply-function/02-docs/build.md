STATUS: READY

# Build: Name multiply in AGENTS.md

## Summary
- `AGENTS.md` line 4 now lists `multiply(a, b)` (product of a and b) alongside `add(a, b)` and `subtract(a, b)`.
- The `add` and `subtract` entries keep their wording; only the punctuation and conjunction changed to make a three-item list.
- `AGENTS.md` is the only file changed on the branch since `438c158`. No code, test, config or `factory/` files were touched.
- Checks pass (`factory/checks.sh` exit 0, 3 tests OK).

## What changed
- `AGENTS.md` (commit `cf0cc93`, "Name multiply in AGENTS.md function list"): the sentence on line 4 that lists the module's functions. It was changed from
  "Its functions are `add(a, b)` (sum of a and b) and `subtract(a, b)` (a - b)."
  to
  "Its functions are `add(a, b)` (sum of a and b), `subtract(a, b)` (a - b) and `multiply(a, b)` (product of a and b)."
  The line was not rewrapped; the rest of the file is unchanged.

## Acceptance criteria
1. [x] `grep -c 'multiply(a, b)' AGENTS.md` prints `1 or more`: ran in the worktree, printed `1`.
2. [x] `grep -n 'Its functions are' AGENTS.md` prints one line containing `add(a, b)`, `subtract(a, b)` and `multiply(a, b)`, each with a parenthetical: printed `4:software factory below end to end. Its functions are `add(a, b)` (sum of a and b), `subtract(a, b)` (a - b) and `multiply(a, b)` (product of a and b).`
3. [x] `git diff --name-only 438c158..HEAD` prints exactly `AGENTS.md`: confirmed.
4. [x] `git diff 438c158..HEAD -- AGENTS.md` shows only the function-list sentence: the diff is a single `-`/`+` pair on line 4 (`git diff --stat`: 1 insertion, 1 deletion). No other section changed.

## Verification
- `bash /home/amod/dev/ei-software-factory-v2/factory/checks.sh` (run from the worktree): PASS, exit 0. `py_compile` succeeded; `unittest` ran 3 tests (`test_add`, `test_multiply`, `test_subtract`), all ok.
- `grep -c 'multiply(a, b)' AGENTS.md`: `1`.
- `grep -n 'Its functions are' AGENTS.md`: one matching line, as above.
- `git diff --name-only 438c158..HEAD`: `AGENTS.md`.
- `git diff 438c158..HEAD -- AGENTS.md`: one changed sentence on line 4.
- `git status --porcelain`: empty after commit.
- No dev server (AGENTS.md: none), so no browser checks were needed.

## History
### Round 1
- Read AGENTS.md, `factory/playbooks/_global.md`, `factory/playbooks/docs.md`, the pass spec, and `handoff-1.md`. Confirmed the worktree is on `factory/002-add-a-multiply-function` and that `src/calculator.py` already defines `multiply`, per the build handoff.
- Edited the function-list sentence in `AGENTS.md` to add `multiply(a, b)` (product of a and b), using the parenthetical wording from the spec's example.
- Ran the checks script (PASS) and walked all four acceptance criteria, recording the results above.
- Committed the single change as `cf0cc93`. Worktree is clean.
- Note: a post-commit hook message appeared after the commit, asking for a hawkscan security scan of commit `438c158` (a commit that is not part of this pass). It was not part of this docs task and I did not act on it. Nothing was scanned or changed because of it.
