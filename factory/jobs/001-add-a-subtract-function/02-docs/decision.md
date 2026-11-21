APPROVE

## Summary
- Docs-only pass. One sentence added to the opening paragraph of `AGENTS.md` names `add(a, b)` and `subtract(a, b)`, and the sentence matches `src/calculator.py`.
- All five acceptance criteria are met. I reran criteria 1 to 3 and compared the sentence against the code (criterion 5) myself.
- Round 1 checks read `GATE: PASS` at `fd77924`, which is HEAD. The single code review reads `VERDICT: PASS` with no issues.
- The change stays within the docs line's scope and touches no code, config or protected paths. Nothing on the global, docs or generic escalate lists applies.

## Reasoning
The diff is one changed line in `AGENTS.md`'s intro paragraph, and it describes exactly what the landed code does. Gate and review both passed at the current HEAD. The only note is cosmetic: the new line is about 115 characters, while the rest of the file wraps at about 76. That isn't a real problem and doesn't justify asking a person to look.

## Acceptance criteria
1. Exactly one line contains `subtract(a, b)`, and it also contains `add(a, b)`: met. I ran `grep -n subtract AGENTS.md` and got only line 4, which holds both.
2. `subtract` appears only in the first 10 lines: met. Line 4 is the only match.
3. Only `AGENTS.md` changed: met. Both `git diff --name-only main...HEAD` and `git diff --name-only ffafbb6..HEAD` list only `AGENTS.md`.
4. Only intro or Setup lines changed, with Validation and the factory section untouched: met. The diff is a single-line change at line 4.
5. The sentence matches the code and makes no extra claims: met. `add` returns `a + b` and `subtract` returns `a - b` in `src/calculator.py`. The sentence names no other function and says nothing about types, errors or rounding.
