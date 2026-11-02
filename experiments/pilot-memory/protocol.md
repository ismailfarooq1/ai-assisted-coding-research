# Pilot: recovery after a conversation reset

Status: draft — not ready for scored execution

## Question and hypothesis

Does structured persistent project knowledge improve interrupted-task completion compared with ordinary repository instructions and simple handover notes?

The primary contrast is structured handover versus plain-text handover. The no-handover condition measures the effect of providing continuation information at all. Benefits, harms, and no detectable difference are all possible outcomes.

## Conditions

| ID | Continuation context |
| --- | --- |
| `no-handover` | Task description, checkpoint repository, and shared repository instructions |
| `plain-handover` | The same context plus a simple prose handover |
| `structured-handover` | The same context plus a handover using the frozen framework template |

Ordinary repository instructions, including any AGENTS.md, stay identical across conditions. Plain and structured handovers must encode the same facts from the same allowed evidence, with a predefined comparable information/token budget. Record both the construction procedure and any content mismatch. Organization is the intended changing factor.

## Proposed pilot size

Five tasks × three conditions × three repetitions = **45 continuation runs**, subject to feasibility review. This is not a statistically justified sample size. Preparation sessions and handover construction are additional work and must be recorded separately.

## Execution unit and pairing

For each task and repetition, run an initial session to a predefined interruption rule. Save its repository state, task description, allowed evidence, and initial-session logs. Produce a paired set of plain and structured handovers from that same evidence, then freeze and audit them before any continuation outcomes are observed.

Clone that checkpoint into three isolated continuation environments, one per condition. Reset conversation history and any agent caches or external memory; retain the intended repository state. Run order should be randomized and recorded. The three continuations share a checkpoint, so analysis must retain this pairing and account for task-level dependence.

For an initial study of representation, prepare and audit handovers outside the continuation agent. This does not test autonomous memory generation; that would require a separate experiment. Record preparation labor and model costs.

## Controls

- Pin model identifier, agent version, runtime, dependencies, and starting/checkpoint revisions. Record provider settings and any unavailable version guarantees.
- Use the same task prompt, execution budget, tools, network policy, and repository instructions across conditions.
- Apply identical hidden acceptance tests and architecture checks to all outputs.
- Control separately whether agents can see validation feedback. No condition gets extra feedback implicitly.
- Keep hidden tests, reference solutions, research plans, and other runs outside agent access.
- Freeze scoring rules, timeouts, retry policy, and exclusions before scored runs. Preserve failures and deviations.
- Evaluate artifacts blind to condition labels where practical. Record manual decisions and their reasons.

## Outcomes

**Primary outcome:** task success, a binary result requiring every mandatory hidden acceptance test and architectural constraint to pass within the execution budget. Distinguish an unsuccessful task from an infrastructure failure using predefined rules.

Secondary measurements:

- Acceptance tests passed/total and architecture violation counts.
- Input/output tokens, cached input where available, tool calls, and elapsed time.
- Continuation inference cost and total cost including preparation and handover construction. Record price source/date; do not turn unavailable values into zero.
- Time/tokens until a predefined meaningful resumption action; define that action per task before runs.
- Rework to previously correct code and violations of prior decisions, using predefined labels.
- Missing, stale, or incorrect handover statements, with supporting evidence.

Keep raw provider usage and test outputs. Any metric not available should be null/blank with an explanation. Never compare incompatible token counters without qualification.

## Evidence and analysis

Use `templates/run-manifest.json` for metadata, `runs/` for raw evidence, and `metrics.csv` for one summary row per continuation. Raw run artifacts are authoritative; summaries must be traceable to them.

Report counts and task-level outcomes before aggregate differences. Estimate structured-minus-plain success differences and cost trade-offs while preserving task/checkpoint pairing. Choose an uncertainty method suitable for clustered data before analysis. With five tasks, treat estimates as exploratory and avoid broad generalization.

## Decisions required before scored runs

- [ ] Benchmark repository, license, commit, and runtime.
- [ ] Five task definitions with objective acceptance and architecture checks.
- [ ] Interruption rule and checkpoint capture/restore procedure.
- [ ] Model/agent configuration, budgets, timeout, retry, and failure policies.
- [ ] Handovers' shared evidence, construction method, budgets, and content audit.
- [ ] Agent-visible validation feedback and tool/network access.
- [ ] Run-order randomization and recorded seed/procedure.
- [ ] Operational definitions for recovery, rework, and memory errors.
- [ ] Scoring, exclusions, uncertainty method, and cost accounting.
- [ ] Protocol version and freeze timestamp recorded before scored runs.

## Deviations

None recorded; no runs have occurred. Log amendments with date, rationale, affected runs, and whether outcomes had already been viewed.
