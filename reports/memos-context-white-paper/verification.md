# Verification record

Completed 2026-11-03. Research-design deliverable only; no Memos agent runs, application changes, runner adaptation, commits or publication.

## Document build and layout

- Built with TeX Live 2026, pdfTeX 1.40.29, BibTeX and latexmk 4.88; rasterized with Ghostscript 10.07.0.
- Five Letter portrait pages; MediaBox `[0 0 612 792]` verified through Ghostscript's PDF interpreter. Body is 11-point, two-column; title/abstract span the page. Figure is vector TikZ; no raster assets are required.
- Seven citations match seven bibliography entries; alphabetical author–date references. No unresolved citations/references, bibliography warnings or overflowing boxes in the final logs.
- All five final pages rendered at 150 dpi and visually inspected. Checked title/abstract, column flow, figure arrows/labels, table wrapping, black headings, references and page numbers. The final bibliography keeps individual entries together.
- A forced TeX rebuild under the Makefile's fixed date environment produced an identical PDF. Reproducible bytes require the same TeX/font toolchain.
- PDF SHA-256: `1318b94baf7451f4be6bae6ad973034d4b882d5d0db368b0c718372031daa520`.
- The log has a benign epstopdf warning because shell escape is disabled. No EPS files or external conversion are used.

## Evidence and consistency

- Primary publication/author/publisher records checked; see [metadata verification](../../research/literature/metadata-verification.md). Publication status, reviewed manuscript version and unaudited experimental artifacts are distinguished.
- Pinned Memos instructions, README, terminology, design-document lifecycle and license inspected through GitHub; commit and blob hashes are in [provenance](../../benchmarks/memos/README.md). This is documentation evidence, not environment validation.
- Active questions and workflow definitions checked against the paper. Proposed architecture, tasks, models, repetitions, budgets and targets are not invented; unresolved decisions are internal.
- Paper checked for unsupported results and placeholders; none included.
- Current Markdown links and citation coverage checked.

## Workspace cleanup

On 2026-11-03, superseded experiments, legacy implementation, old planning sources/archives, obsolete templates and generated build files were removed at the user's request. Navigation and literature guidance were updated for the current Memos study. The delivered PDF, LaTeX source, bibliography and Makefile are unchanged by cleanup. Generated build files can be recreated using the build instructions.
