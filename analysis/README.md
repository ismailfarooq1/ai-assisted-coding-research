# Analysis guidance: Memos context workflows

Status: planned analysis, no Memos observations. Freeze primary contrasts and statistical choices with the eventual protocol before scored runs.

## Task outcomes and resources (RQ1)

Report acceptance correctness and original regressions separately, with task/attempt counts and denominators. Keep paired starting states and task grouping; repetitions are not independent new tasks. Distinguish failed implementation, timeout and infrastructure failure, retain exclusions/retries and show their resource costs. Report uncertainty appropriate to the sample rather than claiming equivalence from a nonsignificant result.

Compare total workflow resources as well as execution alone: preparation, execution, evaluation, maintenance and observed human review. Preserve raw token categories and provider semantics; cached input and reasoning can be subsets. Separate initial/reused preparation from recurring costs and state shared-cost allocation. Show all-attempt consumption, including failures, alongside correctness; any cost per successful task requires explicit numerator/denominator and is undefined if none succeeds. Elapsed runtime is not human labor. Monetary conversion requires actual charges or dated rates, not token totals alone.

## Maintenance (RQ2)

Group observations by common source change and workflow-specific context history. Report audit scope and inspected claim counts, stale/contradictory findings, unresolved defects, observed detection/update latency and active update/review effort. Record reviewer disagreement and uncertainty. More edited lines do not alone imply more effort or improved accuracy. Separate policy documentation from observed maintenance behavior.

## Interpretation and traceability

Complete workflows may contain unequal information. Explain content, delivery and resource differences; do not attribute a whole-workflow effect to one component without an additional ablation. Preserve raw evidence under experiments and derived outputs here with reproducible transformations and run/episode IDs. Report missingness, versions, deviations and exploratory analyses explicitly. Limit conclusions to observed tasks, models and environment; do not project corporate savings.
