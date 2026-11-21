VERDICT: PASS

## Summary
- The branch has one commit (`cf9e537`) that changes only the function-list sentence on AGENTS.md line 4, which is what the spec's must-have 1 asks for.
- The new sentence names `add`, `subtract`, `multiply` and `divide` in source order, uses the existing "`name(a, b)` (description)" form, and says `ZeroDivisionError` is raised when b is 0. That matches the build's `return a / b` with no guard in `src/calculator.py`.
- Protected paths and code are untouched: `git diff --name-only main...HEAD` lists only `AGENTS.md`, and the diff has exactly one removed and one added line.
- The checks passed on this commit (4 tests OK), and the line is not rewrapped, as the spec excludes.

## Issues
None.

## Other observations
- `build.md` reports that a post-commit hook message asked for a hawkscan security scan of commit `cde56cb`. The build correctly ignored it as out of scope. The operator may still want to look at that hook output, since it arrived through tool output and not through the spec.
- The AGENTS.md sentence is now long. The spec explicitly excludes rewrapping, so I left it alone.
