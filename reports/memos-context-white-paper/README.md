# Evaluating Project Context Workflows for AI Assisted Software Development

Research-design white paper, 3 November 2026. No Memos experiments or company savings are reported. The proposed alternative architecture remains outside this paper.

- [PDF](paper.pdf)
- [Editable LaTeX](paper.tex)
- [BibTeX bibliography](references.bib)
- [Build file](Makefile)
- [Verification record](verification.md)

The paper uses Harvard author–date citations with an alphabetical reference list. It has Letter portrait pages, 11-point body text, two columns, a full-width title/abstract, a vector TikZ flow figure and compact tables. No invented authorship or affiliation is supplied.

## Reproducible build

Install TeX Live or MacTeX with `latexmk`, pdfLaTeX and BibTeX. Required packages: geometry, newtx, microtype, natbib, harvard (`agsm.bst`), booktabs, tabularx, pgf/TikZ, titlesec, caption, xurl and hyperref. They are included in a full TeX Live distribution. No network calls or application checkout are needed to compile.

From the workspace root:

```sh
cd reports/memos-context-white-paper
make
make render
```

`make` runs pdfLaTeX and BibTeX as needed until references converge, then copies the built document to `paper.pdf`. Intermediate files stay in ignored `build/`. The Makefile sets `SOURCE_DATE_EPOCH=1793664000` and `FORCE_SOURCE_DATE=1` for stable PDF dates; an identical TeX/font toolchain is required for identical bytes. If the delivered PDF is newer than the sources, use `make -B` for a complete rebuild.

`make render` requires Ghostscript (`gs`) and creates a PNG for every page under `build/preview/`. Inspect every page after changing prose, tables, figure placement or references. Compilation alone does not verify layout.

Manual equivalent (from this directory):

```sh
mkdir -p build
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -output-directory=build paper.tex
bibtex build/paper
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -output-directory=build paper.tex
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -output-directory=build paper.tex
cp build/paper.pdf paper.pdf
```

Inspect `build/paper.log` and `build/paper.blg` for unresolved citations/references, bibliography errors and overflow before delivery. The manual commands do not set the stable-date environment variables unless exported separately.

## Evidence and scope

The related work distinguishes the MSR conference paper, the AGENTS.md workshop record and later preprint revision, the REALM workshop study, the Agent READMEs journal record, and structural/vision references. Paper review does not establish experimental artifact validation. Source status details and primary links are in the [literature index](../../research/literature/README.md).

The inspected Memos documentation commit is provenance, not a validated benchmark snapshot. See [selection evidence](../../benchmarks/memos/README.md), [current protocol](../../experiments/memos-context-study/protocol.md), and [internal open decisions](../../research/open-decisions.md). The paper reports no Memos measurements and does not select models, tasks, budgets or a proposed method architecture.
