# Name integrate in AGENTS.md function list

> Job 006-add-integration-function, pass 02-docs

## Summary
- The build pass (handoff-1) landed `integrate(f, a, b, n=1000)` in `src/calculator.py`, but `AGENTS.md` still lists only `add`, `subtract`, `multiply` and `divide`.
- This pass adds `integrate` to that one-sentence function list so the doc matches the code.
- This is a one-line edit to `AGENTS.md` only, following the same pattern as earlier commits `cf0cc93` (multiply) and `cf9e537` (divide).
- No code, tests, or other docs change.

## Background
- `AGENTS.md` line 4 (worktree root) is the project's only list of calculator functions. It currently reads: "Its functions are `add(a, b)` (sum of a and b), `subtract(a, b)` (a - b), `multiply(a, b)` (product of a and b) and `divide(a, b)` (a / b; raises `ZeroDivisionError` when b is 0)."
- The established convention, set by commits `cf0cc93` and `cf9e537`, is one entry per function: the backticked signature followed by a short parenthetical saying what it returns and, where relevant, what it raises. The last entry is joined with "and".
- `src/calculator.py` now defines `integrate(f, a, b, n=1000)` after `divide`. It approximates the definite integral of `f` from `a` to `b` using the composite trapezoidal rule with `n` equal subintervals, and raises `ValueError` when `n < 1`.
- No other doc mentions the function list: `README.md` and `DESIGN.md` don't name individual calculator functions. A grep for `multiply`/`divide` across `*.md` (excluding `factory/`) only matches `AGENTS.md`.

## Must-haves
1. `AGENTS.md`'s function-list sentence names `integrate(f, a, b, n=1000)` as the last entry, after `divide`. The parenthetical says it approximates the integral of f from a to b with the trapezoidal rule over n subintervals, and that it raises `ValueError` when n < 1.
2. The sentence's joining is fixed so it reads as a single list: `divide` becomes a comma-separated entry, and "and" moves to just before `integrate`.
3. The existing entries for `add`, `subtract`, `multiply` and `divide` keep their current wording.
4. No other line of `AGENTS.md`, and no other file, changes.

## Acceptance criteria
1. `cd <worktree> && grep -c 'integrate(f, a, b, n=1000)' AGENTS.md` prints `1`.
2. `cd <worktree> && grep -n 'trapezoidal' AGENTS.md` matches the function-list sentence (the same line as `add(a, b)`).
3. `cd <worktree> && grep -n 'ValueError' AGENTS.md` matches that same line.
4. `cd <worktree> && grep -c 'and `integrate(f, a, b, n=1000)`' AGENTS.md` prints `1`, and `grep -c 'and `divide(a, b)`' AGENTS.md` prints `0`.
5. The text `(a / b; raises `ZeroDivisionError` when b is 0)` is still present in `AGENTS.md`, along with the existing parentheticals for `add`, `subtract` and `multiply`.
6. `cd <worktree> && git diff --stat main...HEAD -- . ':!src' ':!tests'` lists only `AGENTS.md`, and `git diff main...HEAD -- AGENTS.md` shows changes to the function-list sentence only.

## Explicitly excluded
- Any change to `src/calculator.py`, `tests/test_calculator.py`, or any other code, test or config (docs playbook).
- Any file under `factory/` or `.claude/` (`protected_paths`), including `factory/inbox/` and the playbooks.
- Edits to `README.md`, `DESIGN.md`, or anything else that doesn't list the calculator functions.
- Rewording or restructuring other parts of `AGENTS.md`, such as the Setup, Validation or factory sections.
- Documenting methods the build didn't add (Simpson's rule, adaptive quadrature, symbolic integration) or tolerance and error parameters beyond `n`.
- Converting the function list into a bullet list or table.
- Changing the module docstring in `src/calculator.py`. Triage's mention of a "module docstring" refers to the `AGENTS.md` function list, and the docs line may not touch code anyway.

## Judgment calls
- **`AGENTS.md` only**: triage's "module docstring/function list" note could be read as including `src/calculator.py`'s docstring. The docs playbook forbids code changes, and the existing module docstring doesn't list functions, so only `AGENTS.md` is in scope.
- **Mention the `ValueError`**: this follows the `divide` entry, which documents its `ZeroDivisionError`. The failure condition is part of the function's contract.
- **Show the default `n=1000` in the signature**: it's the real signature, and the default step count was an explicit part of the filer's request (answer-1).
- **No mention of reversed bounds or `a == b`**: these fall out of the formula naturally, and covering them would make this entry far longer than its neighbours.
