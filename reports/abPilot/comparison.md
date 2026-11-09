# A/B frontend feasibility pilot

**This is one researcher-designed task and one coding attempt per method. It does not establish general superiority.** The registered score and an additional post-execution quality audit are reported separately.

## What ran

A used Memos's native instructions, source and documentation under the selected coding agent. This operational baseline is not an observation of how Memos maintainers themselves work. B retained those inputs and additionally read a frozen, source-verified context guide (536 words, 14 source references). The guide was prepared before the task was selected. Neither condition could access the evaluator, research, reports or the other condition's project. B's successful read event contains the guide in full; this establishes exposure, not attention or causation.

The task added single-line CEL raw-string literals to the frontend suggestion reader. Both runs used `gpt-6-luna` with `low` reasoning, Codex CLI `0.167.0`, the same pinned container image, a 600-second limit, 2 CPU quota and 4 GB memory. The frozen order was A then B. The source revision was `b40d8a7b573774c52b022c8d6537d6baf2129dc0`. These were actual fresh agent sessions, not coordinator-authored patches.

## Observations

| Measurement | A: existing workflow | B: prepared context |
|---|---:|---:|
| Registered completion gate | pass | pass |
| Independent acceptance | 10/10 | 10/10 |
| Focused regressions | 13/13 | 13/13 |
| Native candidate lint | pass | pass |
| Pristine native frontend tests | pass | pass |
| Frontend production build | pass | pass |
| Changed test file: supplementary audit | 1 failed \| 62 passed (63) | 66 passed (66) |
| Execution elapsed seconds | 110.896 | 78.990 |
| Input tokens | 185,769 | 350,595 |
| Cached input (included above) | 137,984 | 320,768 |
| Output tokens | 1,539 | 1,717 |
| Reasoning output (included above) | 0 | 0 |
| Total input + output tokens | 187,308 | 352,312 |
| Uncached input (input minus cached) | 47,785 | 29,827 |

Elapsed time includes container/dependency-volume startup and all agent activity. Independent evaluation time is excluded. B's observed execution was **28.8% shorter** and its reported input-plus-output total was **88.1% higher**. These are descriptive differences from this pair. Cached input is included in input totals and has a different accounting meaning from uncached input; total tokens do not establish monetary cost. No charges or pricing estimates are available. Context preparation and active human effort were not fully metered, so total-workflow savings cannot be computed. No maintenance episode was observed.

## Correctness finding and scoring limitation

The primary protocol checks independent functional acceptance, focused regressions, permitted changes, candidate lint, pristine upstream tests and a build. It requires a test change but explicitly does not independently grade the quality of agent-authored tests. The registered gate is retained without retrospective changes.

Inspection after both attempts found a suspect A assertion. A supplementary audit, planned before its execution and applied identically to both candidates, ran the changed test file while preserving each candidate's added tests. **A had one failing assertion; B's 66 tests passed.** A incorrectly expected a negated tag to appear among positive candidates in a Boolean disjunction. Its production change passes the focused functional checks, but its submitted test changes are not clean. The registered gate's pristine-test restoration masked this introduced test failure. A passing primary score therefore must not be presented as complete candidate quality.

A also claimed its checks passed while the captured stream lacks completion events for these started commands:

- `/bin/bash -lc 'pnpm test -- memo-suggestions.test.ts'`
- `/bin/bash -lc 'pnpm test -- memo-suggestions.test.ts'`

B used the explicit targeted Vitest invocation and has a successful completion event. These are process observations. One pair cannot establish that the context guide caused the difference. Neither candidate was manually repaired or rerun to improve its implementation result.

## What can be concluded

For this task, B's submission has stronger observed test evidence and shorter agent execution, with more reported total tokens. A's added test failure prevents describing its submission as fully verified. Both methods' registered functional-check results remain visible. There is no supported universal winner, no correctness equivalence claim, no statistical superiority test, and no organization-wide savings estimate.

The pilot validates the mechanics of isolated execution, token/time capture and independent functional checking. It also reveals a necessary improvement before confirmatory experiments: independently check the candidate's added tests and require actual command-completion evidence. Freeze that gate before collecting new held-out tasks. Do not reuse this task as unseen confirmatory evidence, or design C from these outcomes and evaluate it on this same task as if held out.

## Preparation, failures and preservation

The unchanged frontend baseline passed lint, all 1,616 tests across 192 files, and its production build. It failed all 10 new acceptance checks and passed all 13 focused regressions. A known positive control passed all 23 focused checks in the offline runtime. Backend/Go/database behavior was not validated by this frontend pilot.

An initial dependency-path error was fixed before coding attempts. Launch `rawStringPilot01` then failed in both conditions because Docker did not forward stdin; no model events were emitted. Both launch records, the old protocol and old runner are retained under `launchFailure01/`. After validating input forwarding, both conditions were repeated under the new frozen `rawStringPilot02` protocol. This was a shared infrastructure correction, not a selective retry following a coding failure. Setup/preflight usage is recorded separately and does not silently disappear into a claimed workflow saving.

All three original Memos source snapshots retain the pinned commit and tree. Agent edits exist only in run-specific copies and retained patches. C remains an undesigned shell. Shell egress was not technically restricted to provider domains; external-solution fetching was prohibited by the task prompt. Provider caching, one run order, stochastic variation, a single prepared artifact and the single chosen task limit interpretation.

## Evidence and reproduction

- [Frozen protocol](../../sharedInputs/pilotProtocol.json), [task](../../sharedInputs/tasks/rawStringPilot.md), [metrics](../../sharedInputs/metricsDefinition.md).
- [Machine-readable primary summary](pilotSummary.json), [supplementary audit](additionalAudit.json), [audit plan](additionalAuditPlan.json).
- [A execution](../../experiments/existingWorkflow/runs/rawStringPilot02/execution.json), [A patch](../../experiments/existingWorkflow/runs/rawStringPilot02/changes.patch), [A primary evaluation](../../experiments/existingWorkflow/runs/rawStringPilot02/evaluation.json), [A added-test audit](../../experiments/existingWorkflow/runs/rawStringPilot02/candidateTestAudit.log).
- [B execution](../../experiments/preparedContext/runs/rawStringPilot02/execution.json), [B patch](../../experiments/preparedContext/runs/rawStringPilot02/changes.patch), [B primary evaluation](../../experiments/preparedContext/runs/rawStringPilot02/evaluation.json), [B added-test audit](../../experiments/preparedContext/runs/rawStringPilot02/candidateTestAudit.log).
- [Frozen B context](../../experiments/preparedContext/strategy/contextPack/contextGuide.md), [source provenance](../../experiments/preparedContext/strategy/contextPack/sourceMap.json).
- [Baseline native log](baselineNative.log), [environment preparation](environment/preparation.json), [failed-launch classification](launchFailure01/status.json).

Raw `events.jsonl` and evaluator logs are beside each method's execution record. Regenerate this descriptive report with `python3 experiments/tools/comparePilot.py`. Verify snapshot/context integrity with `python3 experiments/tools/runPilot.py verify`. The execution runner refuses overwriting an existing attempt; reproductions require a separately frozen new attempt and retain their own stochastic outcomes. Runtime build commands and isolation limits are documented in [the shared tools](../../experiments/tools/readme.md). The CEL task follows [the language definition](https://github.com/cel-expr/cel-spec/blob/master/doc/langdef.md); the CLI event/accounting interface follows [official non-interactive documentation](https://learn.chatgpt.com/docs/non-interactive-mode).
