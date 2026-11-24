<!-- factory-issue: 17 -->
# Honour the routed reviewer models

`factory/bin/route` records a model for each reviewer from `config.json` routing (medium and high risk now map to sonnet), but every agent file in `.claude/agents/` still says `model: haiku` and the factory skill never tells the orchestrator to pass the routed model. Make the skill pass the routed model when it launches each reviewer (and decide how the builder, spec-writer and approver models are chosen), and record the model actually used in the review file header so it can be checked.
