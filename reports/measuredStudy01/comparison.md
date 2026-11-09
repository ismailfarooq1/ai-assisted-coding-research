# Memos: measured A/B comparison

Recorded coding runs: **24/24**. Complete study: **True**.

A was more reliable in this exploratory pilot: on four uncontested task clusters (two attempts per method), A achieved 8/8 verified completions and B 5/8. B was faster per attempt, but A used fewer observed coding tokens and less coding time per verified completion. The registered six-task scores and the two contract-conflict audits are retained below; this is not proof of general superiority.

A uses Memos’s native documentation. B adds a newly generated, source-reviewed context pack. The user delegated completion of review before coding; review is automated with coordinator source checks. The unfinished participant session is retained separately and does not establish comparative human labor savings.

Two task/evaluator contract issues affect colorAlpha and memoViewNames. The registered scores are retained below: the unstated alpha argument position and legacy memo-view UI fixture are audited separately, without replacing the primary endpoint. Genuine formatter and submitted-test failures remain recorded.

| Measurement | A | B |
|---|---:|---:|
| Verified completions | 8/12 | 5/12 |
| Unresolved evaluations | 0 | 0 |
| Coding input + output tokens | 4,726,354 | 3,713,641 |
| Coding input tokens | 4,704,633 | 3,694,081 |
| Cached input (included in input) | 4,404,736 | 3,394,304 |
| Uncached coding input (input − cached) | 299,897 | 299,777 |
| Coding output tokens | 21,721 | 19,560 |
| Coding wall seconds, sum | 1,628.66 | 1,206.00 |
| Coding wall seconds, median | 94.56 | 87.46 |
| Coding local CPU seconds | 1,520.21 | 1,014.45 |
| Maximum sampled coding memory, MiB | 1,716.50 | 1,871.47 |
| Additional preparation + review tokens | 0 | 179,156 |
| Additional preparation + review wall seconds | 0 | 95.65 |
| Two maintenance episodes + review tokens | 609,198 | 776,370 |
| Two maintenance episodes + review wall seconds | 229.67 | 210.09 |
| All measured automated method-stage tokens | 5,335,552 | 4,669,167 |
| All measured automated method-stage wall seconds | 1,858.33 | 1,511.73 |
| Independent evaluation wall seconds, sum (separate) | 3,275.85 | 3,277.06 |
| Interrupted agent verification commands | 6 | 6 |

A’s zero added-context preparation is defined within incremental adoption; the historical effort behind its native guidance is unknown. Model-token totals include cached input; cache and reasoning subsets are not counted again. Incomplete-turn usage, if any, is only reported usage. Actual billing, coordinator work and remote inference compute remain unavailable.

| Task | A verified / recorded | B verified / recorded | A mean coding seconds | B mean coding seconds | A mean reported tokens | B mean reported tokens |
|---|---:|---:|---:|---:|---:|---:|
| colorAlpha | 0/2 | 0/2 | 151.78 | 50.09 | 501,630.50 | 139,421 |
| legacyReleaseTag | 2/2 | 1/2 | 217.22 | 81.56 | 330,301.50 | 245,634.50 |
| unicodeSpaceTitles | 2/2 | 1/2 | 148.84 | 117.90 | 494,787 | 233,630.50 |
| retryMetadata | 2/2 | 2/2 | 172.71 | 96.87 | 616,102.50 | 194,232.50 |
| memoViewNames | 0/2 | 0/2 | 75.21 | 169.12 | 251,609.50 | 633,871.50 |
| safeTagCounts | 2/2 | 1/2 | 48.56 | 87.46 | 168,746 | 410,030.50 |

The two attempts are repeats within each of six task clusters. These are small file-local frontend tasks with the relevant source file identified; repository navigation, backend work and broader development tasks are untested. No pilot results are pooled.

The independent evaluator was repaired after TypeScript-Go hit its thread limit. Every candidate is checked under the same Linux-local source layout, GOMAXPROCS=2, 2 CPUs, 4 GB and 1,024-PID evaluator limit. Coding stayed at its original limits; the 24 patches and coding measurements were preserved. Initial evaluator records are retained separately as infrastructure evidence. See [evaluation amendment](../../sharedInputs/measuredStudy01/evaluationInfrastructureAmendment.json).

Completion requires hidden acceptance checks, independently passing candidate tests, pristine upstream regression tests, lint, build, permitted edits and successful agent exit within limits. An agent’s own claim or interrupted checks are not evidence of completion; independent gates determine the primary result.

Exploratory primary contrast: B − A completion fraction = -0.25; two-sided task-level exact sign-flip p = 0.25. This assumes within-pair label exchangeability and has low power with six curated tasks. A null result does not establish equivalence.

The color task did not state alpha argument position; its oracle assumed object.alpha. The memo-view task matches the actual API views collection, but the restored UI fixture uses memoViews. These two conflicts limit interpretation of registered primary completion scores. Supplemental audits are post-execution checks and do not replace registered results.

| Uncontested task sensitivity (four tasks, two attempts each) | A | B |
|---|---:|---:|
| Verified / planned attempts | 8/8 | 5/8 |
| Pending verdicts | 0 | 0 |
| Reported coding input + output tokens | 3,219,874 | 2,167,056 |
| Coding wall seconds, sum | 1,174.69 | 767.57 |

This subset was defined after contract conflicts were found; it is descriptive and cannot substitute for a preregistered confirmatory comparison. Both the full registered sample and the sensitivity subset remain visible.

Maintenance is assessed after two designed changes: lint-script rename and Vitest-config rename. Review items differ in granularity across workflows; compare common required-fact coverage alongside errors and measured upkeep resources. Changed hashes alone do not demonstrate stale content. Source-grounded automated judgments are not expert human judgments.

Wall seconds above sum actual stage durations; overlapping offline evaluation is separate research overhead. Memory is a 100-ms sampled container maximum including cache, not exact peak RSS. Reuse occurred across 12 attempts on six distinct tasks; no company workload, future reuse rate or monetary savings are inferred.

Full evidence: [resource comparison](resourceComparison.json), [original scoring summary](summary.json), [review amendment](../../sharedInputs/measuredStudy01/reviewAmendment.md), per-run raw events/patches and offline logs linked by those records. Historical pilots, original source copies and research files are preserved.

A performed better on this pilot’s primary completion criterion. The registered result is 8/12 for A and 5/12 for B. The color API assumption and memo-view fixture conflict limit the meaning of those absolute rates. On the separately labelled four-task sensitivity subset, A completed 8/8 attempts and B 5/8. The three B failures there were an incorrect tag-count assertion, a Unicode-ordering defect and malformed release-tag acceptance. All failed attempts remain in the resource totals.

B’s faster average attempt did not translate into a better observed coding cost per verified completion on that subset: A used 402,484.25 reported tokens and 146.84 seconds per verified completion; B used 433,411.20 tokens and 153.51 seconds. These figures are coding-only, include failed attempts, and describe the observed subset; setup and upkeep are reported separately above.

A’s and B’s uncached coding inputs were 299,897 and 299,777 tokens respectively. Most of the full-sample total-token difference is cached input, so it is not evidence of the same percentage reduction in actual spending. B’s added preparation plus automated review consumed 179,156 reported tokens and 95.65 seconds. Native documentation creation is historical and unknown; it is not treated as free.

Across the two controlled maintenance edits, A took 53.85 seconds and B 75.58 seconds. Including the recorded automated review calls, maintenance consumed 609,198 tokens / 229.67 seconds for A and 776,370 tokens / 210.09 seconds for B. Review scope, missing reviewer inputs, exact-quote corrections and one recovered output-file delivery required coordinator adjudication. Coordinator effort is unavailable, so these recorded stage costs cannot establish total maintenance labor savings.

The source consistency audit found no remaining obsolete command or config-path mentions for the introduced changes. B’s source-map hashes and claim-source links match both maintained derivatives. The Vitest-config filename was missing from A’s guide in the lint-rename episode (5/6 common coverage items); all other final episode/workflow cases covered 6/6. Missing detail is not counted as a false claim. Changes were supplied explicitly, so autonomous staleness discovery and natural maintenance frequency were not measured.

Both diagnostic audits passed: all four color candidates satisfy the written alpha behavior through a consistent reasonable interface; baseline plus all four memo-view candidates pass the targeted UI fixture checks after changing only the mock resource name. Those audits do not alter primary scores. All four submitted memo-view fixtures were unchanged, so the diagnostic fixture edit does not repair their submitted CI failures.

The justified claim is bounded: the existing Memos workflow was more reliable and used fewer observed coding resources per verified completion in this pilot; the prepared guide reduced average attempt time but did not improve completion. Six curated tasks, two attempts, two contract conflicts and the exploratory primary p=0.25 do not establish general superiority or equivalence. No company savings, completed human-review cost, backend result or performance for the undecided third method is inferred.

Additional audits: [maintenance consistency](maintenanceConsistencyAudit.json), [context exposure](contextExposureAudit.json), [color interface](colorTaskValidityAudit.json), [memo-view fixture](memoTaskValidityAudit.json), [preservation verification](preservationVerification.json).
