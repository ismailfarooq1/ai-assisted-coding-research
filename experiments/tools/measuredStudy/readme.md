# Measured A/B study tools

Study inputs and measurement boundaries: [measurementPlan.md](../../../sharedInputs/measuredStudy01/measurementPlan.md). Historical pilot files are preserved. C remains a shell. All new application edits occur in per-run derivatives; the three original copies stay unchanged.

From the repository root, using Python 3 and the already installed Docker runtime:

```sh
python3 experiments/tools/measuredStudy/studyTests.py
python3 experiments/tools/measuredStudy/studyRunner.py status
python3 experiments/tools/measuredStudy/studyRunner.py freeze
python3 experiments/tools/measuredStudy/studyRunner.py validate
python3 experiments/tools/measuredStudy/studyRunner.py prepare
python3 experiments/tools/measuredStudy/reviewServer.py --packet preparationB
```

Freeze, validation and preparation are one-time operations. Do not rerun them to seek a better result. The review server prints a private localhost URL. Open it, start the timer, check/correct the claims against their source excerpts, judge coverage and complete. It pauses when the tab is hidden or heartbeats stop. It records participation intervals, not verified attention. Restarting the server retains already observed intervals; the new URL changes. Stop with Ctrl-C once completed. It does not launch any agent automatically.

After actual preparation review:

```sh
python3 experiments/tools/measuredStudy/studyRunner.py seal
python3 experiments/tools/measuredStudy/studyRunner.py run
python3 experiments/tools/measuredStudy/maintenanceRunner.py
```

`run` executes only unstarted coding attempts in the frozen order, then independently evaluates them and writes the analysis. Started partial attempts are never silently replayed. Infrastructure/provider failures stop subsequent calls. No manual rescue or best-of retry. `evaluate` can finish evaluations that have not started; partial evaluations require investigation, not destructive cleanup. The primary correctness gate includes the agent's changed/new tests, addressing the gap in the historical pilot. Suspicious skips/deleted upstream assertions remain unresolved until adjudicated; do not convert them to a pass.

Maintenance yields four review packets. Review in order: `renameLintScriptA`, `renameLintScriptB`, `renameVitestConfigB`, `renameVitestConfigA`, using `reviewServer.py --packet <id>`. Record stale assertions and remaining errors in review notes, and common-fact coverage in the form; the before prose and introduced facts remain in packet metadata. A new source hash alone does not demonstrate stale context. Same-reviewer carry-over is disclosed. The two episodes are controlled stress cases, not natural workload frequencies.

```sh
python3 experiments/tools/measuredStudy/studyRunner.py analyze
```

Output: `reports/measuredStudy01/summary.json` and `comparison.md`, plus raw per-attempt logs/patches under each method's `runs/measuredStudy01`. Human records are separate from agent timing. Missing measurements are null; no API-price estimate is presented as an actual account charge. Complete maintenance and all human adjudications before drawing whole-workflow conclusions. Source/harness/coordinator work outside the metered stages is not retroactively reconstructed.
