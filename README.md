# AI-assisted coding research

We are planning a comparison of project-context strategies for coding agents using Memos. Metrics, tasks and execution details will be decided together.

```text
research/                    Buildable LaTeX thesis project
experiments/
    existingWorkflow/
        memos/               First Memos copy
        strategy/            Existing-workflow description
        runs/                Future raw execution records
    preparedContext/
        memos/               Second Memos copy
        strategy/            Prepared-context strategy description
        runs/                Future raw execution records
    proposedStrategy/
        memos/               Third Memos copy
        strategy/            Shell for our later design discussion
        runs/                Future raw execution records
    tools/                   Shared preparation, measurement and comparison tools
reports/                     Experiment reports and comparisons
sharedInputs/                Common snapshot reference, tasks, evaluation and metrics
```

All three Memos copies start at the same pinned revision. Their source files are initially identical; strategy descriptions live outside the application copies. The third strategy remains undesigned. No experiments have run and no metrics have been selected.

Our folders and files use lower camelCase. Memos retains its upstream filenames. The application copies are local working directories ignored by the research repository; their revision is recorded in [projectSnapshot.json](sharedInputs/projectSnapshot.json).

Start with the strategy descriptions: [existing workflow](experiments/existingWorkflow/strategy/strategyDescription.md), [prepared context](experiments/preparedContext/strategy/strategyDescription.md), and [proposed strategy](experiments/proposedStrategy/strategy/strategyDescription.md).

## Generate the research PDF

The main LaTeX file is [thesis.tex](research/thesis.tex). It includes [literatureReview.tex](research/literatureReview.tex) and [methodology.tex](research/methodology.tex).

From the project root, run:

```sh
make -C research
```

The PDF is generated at `research/build/thesis.pdf` and copied to `research/thesis.pdf` for convenient viewing. Running the build keeps both copies in sync. Temporary compilation files stay in `research/build/`, which is ignored by Git. Edit the `.tex` files and run the same command to update the PDF.

To remove generated files, run `make -C research clean`. Building requires a LaTeX installation with `latexmk` and pdfLaTeX, such as MacTeX or TeX Live. Both tools are available on this computer. The document is an initial thesis scaffold; metrics and experiment results have not been filled in.
