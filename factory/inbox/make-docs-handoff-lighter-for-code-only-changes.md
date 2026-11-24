<!-- factory-issue: 7 -->
# Make the docs handoff lighter for code-only changes

A merged `build` job hands off to the `docs` line, which runs a second full pipeline of triage, spec, build, gate and review. For job 011 the docs pass took four rounds even though the code change was small. Make the handoff proportionate. Skip the docs line when the build diff touches no user-facing behaviour (for example tests-only or internal refactors), and when it does run, give it a single reviewer and a round limit of 1 or 2 with the previous pass's diff and summary supplied up front. Decide the rule from the build line's own files, not from an agent's judgement alone, so it is auditable. Keep it configurable in `factory/config.json`, document it in AGENTS.md, and add focused tests.
