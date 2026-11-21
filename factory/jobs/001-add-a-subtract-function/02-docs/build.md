STATUS: READY

# Build: Document the calculator's add and subtract functions in AGENTS.md

## Summary
- `AGENTS.md` opening paragraph now names the module's two public functions: `add(a, b)` (sum of a and b) and `subtract(a, b)` (a - b).
- Docs only: this is the only file changed in this pass.
- Branch commit `fd77924` sits on top of the build pass commit `ffafbb6`.

## What changed
- `AGENTS.md`: appended one sentence to the existing opening paragraph (line 4): "Its functions are `add(a, b)` (sum of a and b) and `subtract(a, b)` (a - b)." Nothing else in the file was touched.

## Acceptance criteria
1. [x] `grep -n 'subtract(a, b)' AGENTS.md` prints exactly one line (line 4), and that line also contains `add(a, b)` (checked with `grep -c 'add(a, b)'` on that output, count 1).
2. [x] `grep -n 'subtract' AGENTS.md` returns only line 4, inside the first 10 lines and in the intro paragraph, not the factory section.
3. [x] `git diff --name-only main...HEAD` lists only `AGENTS.md`. `git diff --name-only ffafbb6..HEAD` lists exactly `AGENTS.md`. (`main` already contains `ffafbb6`, confirmed with `git merge-base --is-ancestor`.)
4. [x] `git diff ffafbb6..HEAD -- AGENTS.md` shows a single changed line, the intro paragraph's line 4 (the old line is replaced by the same text plus the new sentence). No line from "## About the factory" onward, and no **Validation** line, changed.
5. [x] The sentence matches `src/calculator.py`: `add` returns `a + b` (sum), `subtract` returns `a - b`. It names no other function and makes no claims about types, errors or rounding.

## Verification
- `bash /home/amod/dev/ei-software-factory-v2/factory/checks.sh` (run from the worktree): PASS, exit 0 (`py_compile` plus `unittest discover`, 2 tests OK).
- Acceptance commands 1 to 4 above: all as expected.
- `git status --porcelain` after commit: empty (clean tree).
- No dev server (AGENTS.md: none), so no browser checks were needed.

## History
### Round 1
- Handed off from the build line (pass 01-build, commit `ffafbb6`). Read the docs spec, `factory/playbooks/docs.md`, and the worktree's `AGENTS.md`. The worktree was still present on `factory/001-add-a-subtract-function` at `ffafbb6` with a clean tree, so I used it as-is.
- Added the one-sentence functions note to the opening paragraph of `AGENTS.md`, as the spec's must-haves allow.
- Ran the acceptance checks and `factory/checks.sh`, all passing. Committed as `fd77924` ("Name the calculator's add and subtract in AGENTS.md").
- Note: a post-commit hook message again asked for a hawkscan security scan. It is not part of this docs pass, so I did not run it; it also referenced `ffafbb6`, the previous commit.
