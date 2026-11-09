# Shared inputs

Scored conditions use the same source revision, task requirements and independent evaluation rules. The first registered comparison is A/B; C is a shell.

- [projectSnapshot.json](projectSnapshot.json) records the common Memos source revision.
- `tasks/rawStringPilot.md` defines the researcher-designed frontend feasibility task.
- `evaluation/` contains independent checks and evaluator-validation evidence. It is never mounted in the coding-agent containers. Its positive control is evaluator-only material.
- [metricsDefinition.md](metricsDefinition.md) defines pilot correctness, token/time accounting, limits and unavailable measurements.
- [pilotProtocol.json](pilotProtocol.json) freezes the current pilot's task, metrics, evaluator, runner, context and runtime hashes before coding-agent execution. Do not edit a frozen protocol to match outcomes.

All source copies were checked against the recorded commit/tree. The unchanged frontend passed lint, 1,616 tests and its production build in the pilot runtime. This does not validate backend/Go/database behavior. Each execution receives a fresh project/container; neither research nor hidden evaluation nor another condition's artifacts are mounted. The independent evaluator runs separately, offline, after both attempts. See the experiment tools documentation for isolation boundaries and limitations.
