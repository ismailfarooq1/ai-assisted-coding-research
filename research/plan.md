# Research plan

Status: draft · Created: 2026-10-19

## Overall question

Can a structured development environment help AI coding agents build and maintain large software projects more reliably, efficiently, and consistently than conventional environments?

The aim is to find out whether, when, and why a proposed framework helps. Null or negative findings are valid outcomes.

## Research questions

| ID | Question | Stage |
| --- | --- | --- |
| RQ1 — Memory | Does persistent structured project knowledge improve recovery after conversational context is reset? | First pilot |
| RQ2 — Architecture | Does explicit architectural knowledge reduce violations of software design constraints? | Later study |
| RQ3 — Efficiency | Does selective retrieval reduce tokens, cost, or time while preserving correctness? | Later study |
| RQ4 — Scalability | How does effectiveness change with repository size, dependency depth, and cross-module interactions? | Later study |

## First study

Compare interrupted-task recovery with no handover, a plain-text handover, and a structured handover. Hold ordinary repository instructions constant across these conditions. The incremental comparison of structured versus plain-text handover is the primary comparison; it tests whether organization adds value beyond providing a handover at all.

See `../experiments/pilot-memory/protocol.md` for controls, metrics, and unresolved design choices.

## Broader evaluation, after the pilot

The original proposal also compares a normal repository (A), a repository with AGENTS.md (B), and a full structured environment, provisionally called SADE (C). This is a separate design from the first pilot. Do not conflate the condition labels or infer full-framework benefits from a handover-only study.

Later studies may investigate selective retrieval, architectural feedback, individual component ablations, repository complexity, and generalization across applications or models. Preserve identical objective evaluation across conditions and explicitly control agent access to feedback.

## Milestones

- [x] Preserve the original outline and create the workspace.
- [ ] Verify starting literature and document the evidence gap.
- [ ] Choose one benchmark application and record a pinned source revision.
- [ ] Define five tasks, interruption checkpoints, acceptance tests, and architecture checks.
- [ ] Finalize handover construction rules, isolation, budgets, and scoring before scored runs.
- [ ] Build and smoke-test the two-session runner and evidence logger.
- [ ] Run the pilot and assess feasibility, variance, and measurement quality.
- [ ] Analyze outcomes, costs, memory errors, and failure cases.
- [ ] Write the pilot report and decide whether a larger evaluation is justified.

## Interpretation rules

The outline's suggested 45 pilot continuations and 300 main-evaluation runs are planning examples, not power calculations. Its improvement and cost thresholds are illustrative, not adopted acceptance criteria. Final claims must report effect sizes, uncertainty, limitations, and failures. A small pilot primarily establishes feasibility and informs the next study.
