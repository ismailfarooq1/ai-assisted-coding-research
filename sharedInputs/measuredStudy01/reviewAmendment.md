# Active review amendment

The 24 coding attempts are complete. For current evaluation and maintenance continuation, use [evaluationRecovery.md](evaluationRecovery.md); the original evaluator hit a compiler thread-limit failure. The commands below document the original automated-review transition and are not a request to replay coding.

The user delegated the review decision to the assistant before any of the 24 coding attempts started. [automatedReviewAmendment.json](automatedReviewAmendment.json) preserves the original frozen design hash and records the prospective change. The original design, measurement plan, human-review drafts and partial timed observations remain intact.

Preparation and maintenance factual review now use fresh, metered AI sessions with only the relevant native sources and the workflow's own context. Reviewers receive no task specifications, hidden tests, other workflow's outcomes or previous solutions. Claim decisions include exact source excerpts, reasons and coverage judgments. The coordinator inspects findings; this is automated source-grounded review, not independent expert human review. Unresolved or unsupported evidence prevents sealing. No human completion file is fabricated.

The partial human review is retained separately; it is neither zero nor a completed review or total adoption-effort measurement. No comparative human labor savings can be established in this amended round. Automated review consumes tokens and time that are recorded separately from preparation, coding, maintenance and independent evaluation. Coordinator review/engineering tokens and effort remain unavailable.

All task definitions, primary checks, model/image/configuration, per-stage limits and the 24-run schedule remain frozen. Coding is sequential. After candidates are sealed, two independent offline evaluator containers may run concurrently on the four-CPU Docker runtime; evaluation resources are separate research overhead and do not affect recorded coding latency. Test flags are adjudicated explicitly, never silently removed.

Use the amended adapter from the repository root:

```sh
python3 experiments/tools/measuredStudy/automatedStudy.py review
python3 experiments/tools/measuredStudy/automatedStudy.py seal
python3 experiments/tools/measuredStudy/automatedStudy.py run
```

Preparation review and sealing are one-time operations; already-started model calls are not replayed. `run` resumes only unstarted coding calls, then evaluates and performs controlled maintenance and its automated reviews. Use `evaluate`, `maintain`, or `report` for those stages independently if necessary. Raw records and all failures are retained. The original `studyRunner.py` remains frozen, and its human-only seal command does not represent the active review mode.
