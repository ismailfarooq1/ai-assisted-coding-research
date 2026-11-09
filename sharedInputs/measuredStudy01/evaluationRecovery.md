# Common evaluator recovery

All 24 coding attempts completed before this repair. Their prompts, context, patches, source snapshots and measured coding resources remain unchanged.

The first offline evaluations hit TypeScript-Go's `newosproc` failure at the evaluator's 256-PID cap. This compiler runtime crash is infrastructure evidence, not a source-level type error. The original evaluation logs and JSON are retained; initial infrastructure failures do not become task failures or passes by assumption.

The [infrastructure amendment](evaluationInfrastructureAmendment.json) binds a replacement evaluator for **every candidate**. It uses the same immutable image and check commands, 2 CPUs and 4 GB, with Linux-local source copies, explicit `GOMAXPROCS=2`, a 1,024-PID evaluator cap and no network or credentials. The baseline lint check passed this environment before candidate evaluation. The coding actors retain their original 256-PID conditions; no additional coding attempt or patch repair is permitted.

Original verdicts remain in `evaluation.json` where recorded. Common repaired verdicts are separate `evaluationRecovered.json` files, with raw logs/resources in `independentEvaluationRecovered/`. The report selects the repaired evaluator consistently for all 24 candidates and retains initial records as infrastructure overhead. It does not choose the best result from alternative evaluators. Suspicious test changes remain flagged for explicit adjudication.

The original coordinator was stopped after its active containers finished, preventing further use of the invalid evaluator. Its incomplete host transport records are retained; missing overhead is unknown rather than zero.

Current commands after the 24 coding attempts:

```sh
python3 experiments/tools/measuredStudy/offlineRecovery.py run
python3 experiments/tools/measuredStudy/automatedStudy.py maintain
python3 experiments/tools/measuredStudy/finishReport.py
```

Already finished recovered evaluations are skipped. Already started partial evaluations are never overwritten. `maintain` performs only the prescribed documentation-maintenance stages and reviews; it does not rerun coding. A review schema/evidence failure requires a recorded source-based coordinator adjudication, not a hidden new model attempt. `finishReport.py` keeps the registered task-level primary calculation and measurement definitions, selecting the common repaired verdicts.
