# Name divide in AGENTS.md function list

> Job 004-add-a-divide-function, pass 02-docs

## Summary
- The build line landed `divide(a, b)` in `src/calculator.py` (commit `cde56cb`); AGENTS.md still lists only add, subtract and multiply.
- This pass adds `divide(a, b)` to the one-sentence function list in AGENTS.md, and notes that dividing by zero raises `ZeroDivisionError`.
- It follows the same pattern as the earlier multiply docs pass (commit `cf0cc93`), which changed one line of AGENTS.md.
- Only documentation changes. Nothing else in the repo describes the calculator's functions.

## Background
- `src/calculator.py` now defines `add`, `subtract`, `multiply` and `divide`. `divide(a, b)` returns `a / b` (true division). When `b` is 0, Python's own `ZeroDivisionError` propagates, and the module has no guard for it (handoff-1.md). `tests/test_calculator.py` covers this in `test_divide`.
- `AGENTS.md` line 4 currently reads:
  `software factory below end to end. Its functions are `add(a, b)` (sum of a and b), `subtract(a, b)` (a - b) and `multiply(a, b)` (product of a and b).`
- Precedent: commit `cf0cc93` ("Name multiply in AGENTS.md function list") changed only that sentence, adding the new function in the same "`name(a, b)` (short description)" form.
- `README.md`, `DESIGN.md` and `INSTALL.md` never mention the calculator's functions (a grep for `calculator`, `add(`, `subtract`, `multiply` and `divide` finds nothing), so they need no update. There is no `CLAUDE.md`.

## Must-haves
1. In `AGENTS.md`, the function-list sentence names all four functions in source order, using the existing "`name(a, b)` (short description)" form. `divide(a, b)` comes last, with a parenthetical that says it gives a / b and raises `ZeroDivisionError` when b is 0. Suggested wording:
   `Its functions are `add(a, b)` (sum of a and b), `subtract(a, b)` (a - b), `multiply(a, b)` (product of a and b) and `divide(a, b)` (a / b; raises `ZeroDivisionError` when b is 0).`
2. No other line of `AGENTS.md` changes, and no other file changes.

## Acceptance criteria
1. `grep -c 'divide(a, b)' AGENTS.md` prints `1`.
2. `grep -n 'ZeroDivisionError' AGENTS.md` prints exactly one line, and it is the same line that contains `divide(a, b)`.
3. That line still contains `add(a, b)`, `subtract(a, b)` and `multiply(a, b)`, in that order, before `divide(a, b)`. To check, run `grep -n 'Its functions are' AGENTS.md` and read the line.
4. `git diff --name-only main...HEAD` (run in the worktree) lists only `AGENTS.md`.
5. `git diff main...HEAD -- AGENTS.md` shows one line removed and one line added: the function-list sentence.

## Explicitly excluded
- Any change to `src/calculator.py`, `tests/test_calculator.py`, or other code, tests or configuration (docs playbook).
- Any change under `factory/` or `.claude/` (protected paths).
- Rewording, reflowing or restructuring other parts of AGENTS.md, README.md, DESIGN.md or INSTALL.md. That includes the "About the factory" section and rewrapping the long function-list line.
- Adding a new API or functions section, usage examples or docstring changes anywhere.
- Documenting anything about multiply, add or subtract beyond keeping their existing entries as they are.

## Judgment calls
- **Mention ZeroDivisionError in the entry.** The topic asked for a deliberate choice about division by zero, and the build line chose to let `ZeroDivisionError` propagate. Saying so in one short clause tells readers what to expect and adds nothing beyond the sentence's existing form.
- **Only AGENTS.md.** The other docs never list the calculator's functions, so updating only AGENTS.md matches the multiply precedent and the docs playbook's "scope this pass to the handoff" rule.
- **Describe it as "a / b" rather than "quotient of a and b".** This matches the terse operator style already used for `subtract` ("a - b") and makes clear that it is true division. The docstring's "quotient" wording would also be acceptable if the builder prefers it.
