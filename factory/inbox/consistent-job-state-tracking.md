<!-- factory-issue: 13 -->
# Make job state tracking consistent

`.gitignore` ignores `factory/jobs/` and AGENTS.md says it is gitignored, yet jobs 001 to 011 are tracked, including their `.lock` files. Every save dirties tracked files, and whether a job travels to another device depends on how it was created. Decide one rule and apply it: either track job folders except `.lock` (and say so in the docs), or untrack them all and rely on `factory/records/` plus the event log. Remove the tracked `.lock` files either way, and update AGENTS.md, CLAUDE.md and README.md to match.
