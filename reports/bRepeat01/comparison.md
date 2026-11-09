# B repetition with unchanged prepared context

One additional B coding attempt was requested and performed. The original A/B results and context files are preserved. This repeats the same task from the same clean Memos snapshot; it does not resume the solved project or the previous agent conversation.

The existing context guide/source map, task, prompt, model (`gpt-6-luna`, low reasoning), CLI 0.167.0, image ID and 600-second/2-CPU/4-GB limits match the previous B attempt. The context was reused byte-for-byte; prior patches, logs and hidden evaluation were not mounted in the coding-agent container. Docker stdin transport, input hashes, source snapshots and runtime identity were checked before launching. Exactly one new coding attempt was made, without manual repair or selecting a preferred outcome.

| Measurement | Previous B | B repeat |
|---|---:|---:|
| Agent execution seconds | 78.99 | 110.869 |
| Input tokens | 350,595 | 347,529 |
| Cached input (included in input) | 320,768 | 308,608 |
| Output tokens | 1,717 | 1,639 |
| Total input + output tokens | 352,312 | 349,168 |
| Independent acceptance and focused regressions | 23/23 | 23/23 |
| Legacy registered completion gate | pass | pass |
| Candidate test-file audit | 66 passed | 65 passed (65) |

The repeat took 31.879 seconds (40.4%) longer than the previous B attempt. Execution time uses the same monotonic wall-clock definition as before: Docker invocation through agent exit, including container/dependency-volume startup, excluding independent evaluation. Provider caching and stochastic behavior can vary. Token totals include cached input; cached and reasoning subsets are not added again. These observations do not establish monetary cost or general performance differences.

The repeat's native evaluator statuses are `{'lint': 0, 'test': 0, 'build': 0}` (zero means success). Candidate-added/changed test-file validation was specified before this repeat and runs in a separate offline evaluator with those tests retained. The old registered gate is also reported unchanged. Full guide text was observed in a successful read event: **True**. The candidate passes both the original gate and the additional test validation: **True**.

Both B attempts already used the same prepared context. A timing difference therefore measures repeat variability; it cannot show that context reuse caused an improvement. A was not rerun, so this is not another paired A/B comparison. Preparation and active human effort remain unmetered; no context was regenerated and no maintenance episode was observed.

Evidence: [repeat protocol](protocol.json), [machine-readable summary](summary.json), [execution](../../experiments/preparedContext/runs/bRepeat01/execution.json), [patch](../../experiments/preparedContext/runs/bRepeat01/changes.patch), [original-gate evaluation](../../experiments/preparedContext/runs/bRepeat01/evaluation.json), [candidate test audit](../../experiments/preparedContext/runs/bRepeat01/candidateTestAudit.json), [raw events](../../experiments/preparedContext/runs/bRepeat01/events.jsonl), [original B](../abPilot/comparison.md). Original snapshots, prepared context and earlier results are not overwritten.
