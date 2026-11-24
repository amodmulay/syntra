<!-- factory-issue: 10 -->
# Wire up or remove the builder gate hook

`factory/bin/gate --hook` is meant to run the checks when the builder stops, but nothing configures it: there is no `.claude/settings.json` hook and no hook in `.claude/agents/builder.md`. If it were wired it would crash, because it parses `Job: <id>.` from the prompt while the orchestrator sends `Job folder: <path>/`. Either wire it up as a SubagentStop hook for the builder with a prompt format both sides agree on (documented in the factory skill), or remove it. Add a test for the prompt parsing.
