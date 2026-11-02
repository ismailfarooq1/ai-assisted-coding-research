# TXX — <task name>

Status: draft

- Benchmark ID and source commit:
- Related research question:
- Protocol version:

## Exact prompt given to both sessions

## Starting state and setup

Commands, runtime/dependency versions, and baseline checks.

## Initial session and interruption rule

Define the cutoff before execution; specify how the checkpoint, uncommitted changes, and allowed evidence are preserved.

## Decisions and completed work to preserve

Identify the observable decisions/constraints used in recovery scoring. Separate evaluator-only notes from agent-visible facts.

## Handover evidence and preparation

Shared factual content, allowed sources, template version, token budget, and equivalence audit.

## Objective evaluation (evaluator only)

- Mandatory acceptance tests and evaluator artifact location:
- Architecture checks and scoring rules:
- Definition of correct completion:
- Definition of meaningful resumption:
- Rework / memory-error labeling rules:
- Timeout and infrastructure failure handling:

## Execution controls

Model, agent, budget, tools, validation feedback, and network policy; reference the frozen protocol and record any exceptions.

## Risks and confounders

## Readiness checklist

- [ ] Starting state and checkpoint can be reproduced.
- [ ] Tests distinguish correct and deliberately faulty implementations.
- [ ] All conditions share identical code/checkpoints and evaluation.
- [ ] Hidden material is inaccessible to the agent.
- [ ] Handovers contain equivalent facts and no reference-solution leakage.
- [ ] Task and scoring rules were frozen before scored runs.
