# AI-assisted coding research

We are comparing project-context workflows for coding agents using Memos. The first A/B feasibility pilot compares native project practice with a frozen prepared-context pack. The third strategy remains open. Confirmatory tasks, sample sizes and practical-effect margins are still to be decided.

```text
research/                    Buildable LaTeX thesis project
experiments/
    existingWorkflow/
        memos/               First Memos copy
        strategy/            Existing-workflow description
        runs/                Raw execution records, patches and evaluation
    preparedContext/
        memos/               Second Memos copy
        strategy/            Prepared-context strategy description
        runs/                Raw execution records, patches and evaluation
    proposedStrategy/
        memos/               Third Memos copy
        strategy/            Shell for our later design discussion
        runs/                Future raw execution records
    tools/                   Shared preparation, measurement and comparison tools
reports/                     Experiment reports and comparisons
sharedInputs/                Common snapshot reference, tasks, evaluation and metrics
```

All three `memos/` copies retain the same unchanged pinned revision. Agent edits happen in independent per-run copies under `runs/<pilotId>/project/`. Strategy descriptions and B's context pack live outside the source snapshots. The A/B task, evaluator, limits and accounting definitions are in `sharedInputs/`; records and comparisons belong in `reports/abPilot/`. The third strategy remains undesigned.

Our folders and files use lower camelCase. Memos retains its upstream filenames. The application copies are local working directories ignored by the research repository; their revision is recorded in [projectSnapshot.json](sharedInputs/projectSnapshot.json).

Start with the strategy descriptions: [existing workflow](experiments/existingWorkflow/strategy/strategyDescription.md), [prepared context](experiments/preparedContext/strategy/strategyDescription.md), and [proposed strategy](experiments/proposedStrategy/strategy/strategyDescription.md).

## Generate the research PDF

The main LaTeX file is [thesis.tex](research/thesis.tex). It includes the literature review, research position, evaluation methodology, comparison framework and references. It describes the research design; pilot observations are recorded separately in `reports/abPilot/`.

From the project root, run:

```sh
make -C research
```

The PDF is generated at `research/build/thesis.pdf` and copied to `research/thesis.pdf` for convenient viewing. Running the build keeps both copies in sync. Temporary compilation files stay in `research/build/`, which is ignored by Git. Edit the `.tex` files and run the same command to update the PDF.

To remove generated files, run `make -C research clean`. Building requires a LaTeX installation with `latexmk` and pdfLaTeX, such as MacTeX or TeX Live. Both tools are available on this computer.
# Current measured study

The six-task A/B study is separate from the historical raw-string pilot. It compares the native Memos workflow with a newly metered preparation of additional context, using two attempts per method per task (24 coding runs). It includes metered automated factual review and two controlled maintenance episodes. Partial human participation is retained separately; the user delegated completion of the review to the assistant. C remains a shell.

Read the original [measurement plan](sharedInputs/measuredStudy01/measurementPlan.md) together with the active [review amendment](sharedInputs/measuredStudy01/reviewAmendment.md), and inspect [study status/results](reports/measuredStudy01/comparison.md). The amended adapter is `experiments/tools/measuredStudy/automatedStudy.py`; it preserves the original frozen driver and uses a separate seal for automated review. No general winner or comparative human labor saving is presumed.

