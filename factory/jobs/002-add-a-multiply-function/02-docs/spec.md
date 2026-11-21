# Name multiply in AGENTS.md

> Job 002-add-a-multiply-function, pass 02-docs

## Summary
- The build pass (handoff-1) landed `multiply(a, b)` in `src/calculator.py`, with a test.
- `AGENTS.md` line 4 still lists only `add(a, b)` and `subtract(a, b)` as the module's functions, so it is now out of date.
- This pass adds `multiply(a, b)` to that sentence, in the same style. Nothing else changes.
- No other doc in the repo lists the calculator's functions, so no other doc needs updating.

## Background
- `src/calculator.py` defines `add`, `subtract` and `multiply`. `multiply` returns `a * b` and has the docstring "Return the product of a and b." It landed in commit `438c158`.
- `AGENTS.md` (repo root), lines 3-4, currently reads:
  "This project is a minimal calculator module, used mainly to exercise the
  software factory below end to end. Its functions are `add(a, b)` (sum of a and b) and `subtract(a, b)` (a - b)."
- The established pattern comes from commit `fd77924` ("Name the calculator's add and subtract in AGENTS.md"). Each function is named in backticks with its signature, followed by a short parenthetical saying what it returns.
- Searching `README.md`, `DESIGN.md` and `INSTALL.md` for `add(`, `subtract` and `calculator.py` finds no list of the calculator's functions. `factory/playbooks/_global.md` mentions the module but is a protected path (`factory/*`), and it does not list the functions anyway.

## Must-haves
1. In `AGENTS.md`, the sentence listing the calculator's functions also names `multiply(a, b)` in backticks, with a parenthetical in the existing style: `(a * b)` or `(product of a and b)`. The list reads naturally, for example: "Its functions are `add(a, b)` (sum of a and b), `subtract(a, b)` (a - b) and `multiply(a, b)` (product of a and b)."
2. The `add` and `subtract` entries keep their current wording, apart from the punctuation and conjunction changes needed to make a three-item list.
3. `AGENTS.md` is the only file changed on the branch in this pass.

## Acceptance criteria
1. Run `cd .worktrees/002-add-a-multiply-function && grep -c 'multiply(a, b)' AGENTS.md`. It prints `1` or more.
2. Run `grep -n 'Its functions are' AGENTS.md`. It prints one line that contains `` `add(a, b)` ``, `` `subtract(a, b)` `` and `` `multiply(a, b)` ``, each followed by a parenthetical description.
3. Run `git diff --name-only 438c158..HEAD`. It prints exactly `AGENTS.md`.
4. Run `git diff 438c158..HEAD -- AGENTS.md`. It shows only the lines of the function-list sentence (lines 3-4, plus any rewrap of them). No other section of `AGENTS.md` changes.

## Explicitly excluded
- Any change to `src/`, `tests/`, configuration, or anything under `factory/` or `.claude/`, which are protected paths. The docs playbook forbids code, test and config changes.
- Adding function lists or API docs to `README.md`, `DESIGN.md` or `INSTALL.md`. They don't document the functions today, and the docs playbook says this pass covers only the handoff.
- Rewording or restructuring other parts of `AGENTS.md`, such as the validation command or the factory section.
- Adding docstrings, examples or usage snippets beyond the one sentence.
- New dependencies, CI changes, or any other item on the global playbook's never-do list.

## Judgment calls
- **Only `AGENTS.md` is updated.** It is the only doc that lists the calculator's functions. Adding the list to other docs would widen the scope past the handoff.
- **Parenthetical wording.** The two existing entries use different styles ("sum of a and b" and "a - b"), so either `(a * b)` or `(product of a and b)` is acceptable. The second matches the new docstring.
