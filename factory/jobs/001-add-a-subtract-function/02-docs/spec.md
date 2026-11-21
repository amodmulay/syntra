# Document the calculator's add and subtract functions in AGENTS.md

> Job 001-add-a-subtract-function, pass 02-docs

## Summary
- The build pass (handoff-1) added `subtract(a, b)` to `src/calculator.py` and `test_subtract` to `tests/test_calculator.py`, merged as `ffafbb6`.
- No doc in the repo names the calculator's functions today, so nothing is currently wrong. But nothing records what the module provides either.
- This pass adds one short sentence to `AGENTS.md` naming the module's two public functions, `add(a, b)` and `subtract(a, b)`, so the doc an agent reads first matches what shipped.
- Docs only: no code, test, config or factory file changes.

## Background
- `src/calculator.py` (on this branch, at `ffafbb6`) defines `add(a, b)` ("Return the sum of a and b.") and, directly after it, `subtract(a, b)` ("Return the difference of a and b."). `tests/test_calculator.py` covers both with `test_add` and `test_subtract`.
- `AGENTS.md` opens with "This project is a minimal calculator module, used mainly to exercise the software factory below end to end." Its **Setup** bullet names `src/calculator.py` and `tests/test_calculator.py` but doesn't list any function.
- `README.md`, `INSTALL.md` and `DESIGN.md` describe the factory, not the calculator. A search for `subtract`/`add(` across the repo's markdown finds no reference to the calculator's functions. None of these three files needs to change.
- `factory/playbooks/_global.md` also describes the calculator, but it matches `factory/*` in `protected_paths` and must not be touched. It doesn't list functions anyway, so it's still accurate.
- `CLAUDE.md` does not exist in this repo.

## Must-haves
1. `AGENTS.md` names both public functions of `src/calculator.py`, `add(a, b)` and `subtract(a, b)`, in one short sentence. Put it either in the opening paragraph that describes the calculator module or in the **Setup** bullet that already mentions `src/calculator.py`.
2. The sentence describes only what the code does today: `add` returns the sum of `a` and `b`, and `subtract` returns the difference `a - b`.
3. Everything else in `AGENTS.md` stays as it is, including the **Validation** command and the whole "About the factory" section.
4. `AGENTS.md` is the only file changed on the branch in this pass.

## Acceptance criteria
1. `cd .worktrees/001-add-a-subtract-function && grep -n 'subtract(a, b)' AGENTS.md` prints exactly one line, and that line (or the sentence it belongs to) also contains `add(a, b)`.
2. `grep -n 'subtract' AGENTS.md` returns matches only within the first 10 lines of the file, meaning the intro paragraph or the Setup bullet, not the factory section.
3. `git diff --name-only main...HEAD` lists only `AGENTS.md`, plus the build pass's `src/calculator.py` and `tests/test_calculator.py` if `main` doesn't already contain `ffafbb6`. `git diff --name-only ffafbb6..HEAD` lists exactly `AGENTS.md`.
4. `git diff ffafbb6..HEAD -- AGENTS.md` shows only added or changed lines in the intro paragraph or the Setup bullet. No line from "## About the factory" onward, and no line of the **Validation** bullet, is added, removed or changed.
5. Reading the new sentence next to `src/calculator.py` shows it matches the code: `add` gives the sum, `subtract` gives `a - b`. The sentence names no other function and makes no claims about behavior such as types, errors or rounding.

## Explicitly excluded
- Any change to `src/calculator.py`, `tests/test_calculator.py` or any other code or test file (docs playbook: no code, tests or config on this line).
- Any change to `factory/*` or `.claude/*`, including `factory/playbooks/_global.md` and `factory/checks.sh` (`protected_paths`).
- Edits to `README.md`, `INSTALL.md` or `DESIGN.md`. They describe the factory, not the calculator, and rewriting unrelated docs is ruled out by the docs playbook.
- Creating `CLAUDE.md`, a calculator README, a docs folder or any other new file.
- A full API reference, usage examples, a changelog entry, or descriptions of functions that don't exist (multiply, divide and so on).
- Rewording or restructuring any other part of `AGENTS.md`.

## Judgment calls
- **Make a small doc change instead of declaring "nothing to do".** No doc is wrong today, but a docs pass that changes nothing leaves no record and no clear way to check it. Naming the module's functions in `AGENTS.md`, the file every agent reads first, is the smallest addition that keeps the written record in step with the landed work.
- **Put the sentence in `AGENTS.md`, not `README.md`.** `README.md` is about the factory and never mentions the calculator's contents. `AGENTS.md` is where the project describes the calculator module.
- **List `add` as well as `subtract`.** Naming only the new function would read as if it were the module's only one. Listing both describes the module as it actually is now.
