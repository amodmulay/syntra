# Syntra

**An Agentic Software Engineering Platform.**

Syntra is an AI-powered software factory designed to coordinate specialised agents across the software development lifecycle — from an initial idea or requirement to reviewed, tested and deliverable software.

It brings together engineering workflows, agent orchestration, project context, quality gates and human decision-making in one environment.

> **From intent to working software. One coordinated engineering system.**

## The Vision

Software engineering is moving from individual developers using AI assistants to teams of specialised agents collaborating on engineering work.

Syntra is being built around that shift.

A user should be able to describe a feature, change or problem in natural language. Syntra should interpret the request, break it into manageable work, assign the right responsibilities to agents, coordinate their execution, validate the output and keep a human in control of important decisions.

The objective is to build a coordinated engineering system with persistent context, explicit workflows, measurable quality and traceable outcomes.

## What Syntra Aims to Do

- **Translate intent into engineering work:** Turn requests, requirements and issues into structured specifications and actionable tasks.
- **Coordinate specialised agents:** Use dedicated roles for analysis, architecture, implementation, testing, security, review and documentation.
- **Orchestrate workflows:** Define repeatable engineering pipelines with configurable stages, dependencies, hand-offs and approval points.
- **Build and validate software:** Let agents work in isolated environments, run project checks and iterate on findings.
- **Keep humans in control:** Require explicit decisions for sensitive operations, high-risk changes and approval boundaries.
- **Preserve engineering context:** Maintain project knowledge, decisions, specifications, agent outputs and execution history.
- **Make execution observable:** Expose job status, agent activity, quality results, model usage, token consumption and cost.
- **Remain adaptable:** Support different models, agent runtimes, tools and deployment environments.

## A Software Factory, Not a Coding Assistant

Syntra is intended to cover the broader engineering lifecycle.

| Capability | Purpose |
|---|---|
| Request intake | Capture requirements, issues and change requests |
| Triage and planning | Assess scope, complexity, dependencies and risk |
| Specification | Produce clear, testable engineering requirements |
| Architecture | Identify components, interfaces and design decisions |
| Implementation | Delegate coding tasks to specialised builder agents |
| Testing and quality | Run deterministic checks and evaluate test coverage |
| Specialist reviews | Review code, security, UX, UI and architecture |
| Approval | Escalate decisions requiring human judgement |
| Documentation | Keep technical and user documentation aligned |
| Delivery | Prepare approved changes for integration and release |
| Operations | Extend into deployment, monitoring and incident response |

These are intended capability areas. Not all capabilities are available today.

## How It Works

At a high level, a request moves through a coordinated workflow:

\`\`\`mermaid
flowchart TD
    A[Request / Requirement / Issue] --> B[Intake and Triage]
    B --> C{Accepted?}
    C -- No --> D[Clarification or Rejection]
    C -- Yes --> E[Specification]
    E --> F[Architecture and Planning]
    F --> G[Agent Orchestration]
    G --> H[Implementation]
    H --> I[Automated Quality Gates]
    I -- Failed --> H
    I -- Passed --> J[Specialist Reviews]
    J -- Changes Required --> H
    J -- Passed --> K[Human Approval]
    K -- Approved --> L[Integration / Delivery]
    K -- Changes Required --> H
    L --> M[Documentation and Traceability]
\`\`\`

The workflow is configurable. Different work types may use different agent roles, stages, review policies and quality gates.

## Core Design Principles

### 1. Orchestration Before Autonomy

Agents should have clearly defined responsibilities, inputs, outputs and boundaries. Syntra coordinates their work and controls transitions between stages. Agents should not independently bypass the workflow.

### 2. Deterministic Controls Around Probabilistic Agents

Use AI for interpretation, reasoning and generation. Use conventional software for state transitions, permissions, validation, policy enforcement, budgets and other controls that must behave predictably.

### 3. Human Oversight by Design

Human approval should be configurable according to risk. High-impact actions, such as production changes, security-sensitive modifications, data migrations and releases, must have explicit approval boundaries.

### 4. Persistent Context and Traceability

Every job should leave behind useful evidence: the original request, specification, decisions, generated changes, test results, review findings, approvals and execution metadata.

### 5. Model and Runtime Flexibility

Avoid coupling workflow definitions to one model provider or agent runtime. Model selection should be configurable by task, capability, cost, latency and policy.

### 6. Cost and Resource Awareness

Track token usage, model costs, execution time and retries. Apply budgets and routing policies so expensive models are used where they add value.

### 7. Isolation and Least Privilege

Agents should work in scoped environments with only the tools, repositories and permissions required for their tasks. Separate agent execution from privileged integration and release operations.

## Conceptual Architecture

Syntra is intended to evolve around these logical components:

| Component | Responsibility |
|---|---|
| Workspace and UI | User interaction, projects, requests, jobs and operational visibility |
| Workflow engine | Workflow definitions, orchestration, state management, retries and hand-offs |
| Agent runtime | Agent lifecycle, execution, tool access and communication |
| Agent catalogue | Reusable role definitions, capabilities and configurations |
| Model gateway | Provider abstraction, model routing, quotas, budgets and usage tracking |
| Project context | Repository context, engineering standards, knowledge and decisions |
| Tool integrations | Git, issue trackers, CI/CD, cloud platforms and engineering tools |
| Quality and policy engine | Automated checks, approvals, risk policies and guardrails |
| Observability | Job timelines, agent execution, logs, traces, metrics and cost reporting |
| Knowledge and skills | Reusable engineering patterns, playbooks, templates and domain knowledge |

This is a logical target architecture, not a claim that all components are already implemented.

## Agent Roles

Agent roles should be modular and reusable.

| Role | Responsibility |
|---|---|
| Triage agent | Understand and classify incoming work |
| Product analyst | Refine requirements and acceptance criteria |
| Architect agent | Propose architecture and technical design |
| Specification agent | Produce structured implementation specifications |
| Builder agent | Implement engineering tasks |
| Test agent | Create and execute tests |
| Code reviewer | Assess correctness, maintainability and scope |
| Security reviewer | Identify security risks and weaknesses |
| UX/UI reviewers | Assess usability and interface consistency |
| Documentation agent | Maintain technical and user documentation |
| Release agent | Prepare controlled delivery activities |
| Operations agent | Analyse incidents and support remediation |

A role is a reusable definition, not necessarily a separate model. Multiple roles may use the same model, and one role may use different models depending on task requirements.

## Workflows and Factory Lines

A workflow is a configurable sequence of activities. Each activity can be performed by an agent, a deterministic tool or a human.

Examples:

- **Feature development:** Triage → Specification → Architecture → Build → Test → Review → Approval.
- **Bug fixing:** Triage → Reproduce → Diagnose → Fix → Regression Test → Review.
- **Documentation:** Analyse Changes → Update Documentation → Validate → Review.
- **Security remediation:** Assess Finding → Prioritise → Plan → Implement → Security Review → Approval.
- **Incident response:** Ingest Incident → Investigate → Correlate Evidence → Propose Remediation → Human Approval → Execute Authorised Actions.

Workflows should support conditional routing, parallel activities, retries, explicit hand-offs and human checkpoints.

## Technology Direction

Syntra is intended to remain technology- and model-agnostic where practical.

Potential integration areas include:

- **Models:** Hosted LLM APIs and locally hosted models.
- **Agent execution:** Coding agents, tool-using agents and custom agent runtimes.
- **Development environments:** Git repositories, isolated worktrees or containers.
- **Engineering systems:** Issue trackers, source control, CI/CD, test frameworks and observability platforms.
- **Knowledge sources:** Source code, architecture documents, standards, runbooks and project documentation.
- **Infrastructure:** Local development, self-hosted deployments and cloud environments.

Specific technology choices will be documented as the implementation takes shape.

## Current Foundation

Syntra builds on ideas and practical experimentation from an earlier software-factory prototype:

[ei-software-factory-v2](https://github.com/amodmulay-ltts/ei-software-factory-v2)

That prototype explores a manually triggered, repository-local engineering pipeline. Requests enter an inbox, an agent triages them, and accepted work moves through specification, implementation, deterministic checks, specialist reviews and approval.

It uses configurable factory lines, local job state, Git worktrees, GitHub issue intake and a lightweight dashboard.

Syntra takes this foundation as a starting point for a broader platform. The direction is to move from a repository-level workflow into a reusable system for managing projects, agents, workflows, context, tools and execution across the engineering lifecycle.

## Development Status

**Early-stage project — actively evolving.**

The current focus is to establish the platform foundations and validate the orchestration model before expanding the feature set.

Planned development themes:

1. Establish the core workflow and job lifecycle.
2. Define agent contracts, execution boundaries and reusable roles.
3. Build persistent project and job context.
4. Add model-provider abstraction and usage metering.
5. Introduce a workspace for managing projects and observing execution.
6. Expand integrations, reusable skills and workflow templates.
7. Strengthen security, permissions, auditability and deployment options.

Features will be marked as implemented only when they are available and verified in the codebase.

## Guiding Idea

**Syntra is where software engineering work gets organised, executed and verified by coordinated AI agents — with engineers setting the direction and retaining control.**

## Name

**Syntra** — inspired by synthesis: bringing specialised capabilities, tools and intelligence together into one coordinated system.
