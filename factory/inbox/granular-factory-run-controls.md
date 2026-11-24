<!-- factory-issue: 16 -->
# Granular control over factory runs

Today the only controls are `/factory run`, `run <topic>` and `run auto`. Add: stop or abandon a running job (not just reject a waiting one); pause and resume; run only up to a stage (for example `--until triage` or `--until spec`); re-run a single step or a single reviewer; a dry run that shows what a run would do; and a per-job override of the model and round limit. Add `job status <id>` that prints the stage, the next step and who should take it, so a new session can pick up without reading files. Put the state changes in `factory/bin/job` and document the options in the factory skill.
