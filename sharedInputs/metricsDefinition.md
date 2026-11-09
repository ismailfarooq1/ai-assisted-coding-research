# Metric definitions

Status: defined for the single-task feasibility pilot only. Confirmatory task counts, power, practical-effect margins and a third method remain undecided.

## Verified completion

An attempt succeeds only if it finishes within the common policy, returns successfully, changes only permitted files, includes a frontend test change, passes all 10 independent acceptance checks and 13 focused regressions, and passes native frontend lint, pristine upstream frontend tests and a frontend production build. Lint checks the candidate's tests before pristine tests are restored for independent regression evaluation. Agent-authored test quality is not independently graded beyond these checks. The evaluator runs after both agent sessions, in fresh offline containers. The baseline must pass native checks and focused regressions before execution; it must fail the new acceptance checks. A separate positive control verifies evaluator sensitivity.

Agent timeouts, invalid implementations and prohibited edits are failures. Infrastructure interruptions are recorded separately. There are no automatic best-of retries or manual implementation repairs. Unknown verdicts remain unknown. One task per condition supports a descriptive pilot result, not a success-rate estimate for general Memos work or a statistical superiority claim.

## Execution tokens

Preserve raw Codex JSONL events. Sum usage from distinct `turn.completed` events. Report input, cached input, cache-write input, output and reasoning output if observed. Total tokens are input plus output; cached input and reasoning output are overlapping subsets and are not added again. Missing usage remains null. Failed/incomplete turns can have unreported consumption; this limitation must be visible. No monetary estimate is made.

## Time and limits

Measure monotonic elapsed seconds from starting each Docker invocation until it exits. This includes container/dependency-volume startup and all agent activity. Each attempt has a 600-second wall limit, 2 CPU quota, 4 GB memory limit and 256-process limit. No token cap is enforced. Evaluation times are separate from agent-execution time. Model, reasoning setting, image ID, order and inputs are frozen in `pilotProtocol.json` before execution.

## Preparation, maintenance and human effort

Record the frozen B context, its source references and checksums. Complete token usage and active human effort for preparing it are unavailable and remain unknown. Shared environment/authentication checks are setup overhead, not A/B task usage. No maintenance episodes are part of this pilot. Do not compute whole-workflow savings or maintenance advantages from these observations.
