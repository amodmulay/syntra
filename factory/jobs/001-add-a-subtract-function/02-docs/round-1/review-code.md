VERDICT: PASS

## Summary
- `AGENTS.md:4` now names both public functions, `add(a, b)` (sum) and `subtract(a, b)` (a - b), which matches `src/calculator.py` exactly.
- The branch has one commit, `fd77924`, and touches only `AGENTS.md` (1 insertion, 1 deletion). No code, test, config or `factory/*` file changed.
- The rest of the file is unchanged: the **Validation** bullet and the whole "About the factory" section are intact.
- The sentence makes no claims about types, errors or rounding, as the spec asks.
- Docs-only change, so no new tests are needed. The round-1 checks (`factory/checks.sh`, exit 0, 2 tests OK) cover the code already on `main`.

## Issues
None.

## Other observations
- `AGENTS.md:4` is one long line of about 115 characters, while the rest of the file wraps at about 76 columns. Re-wrapping the sentence onto two lines would match the file. This is cosmetic and does not change behavior, so it does not block.
- The `fd77924` commit message is one short line and carries the Co-Authored-By trailer, which is fine.
- `02-docs/build.md` records a post-commit hook message asking for a hawkscan security scan, which the pass correctly did not act on. That hook message is unrelated to this change; it is worth checking why it fires on this branch.
