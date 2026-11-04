# Experiment 2: deliberately prepared context files

Purpose: compare existing Memos practice plus an explicitly authored project-context pack, accounting for its preparation, consumption and maintenance.

## This project

- [project/](project/): independent Memos working copy from the same candidate as experiment one.
- [context/README.md](context/README.md): editable source of the initial task-independent pack.
- [method.json](method.json): method definition and delivery behavior.
- [Makefile](Makefile): setup, initial-state audit and application checks.
- `setup-manifest.json`: locally generated file/context hashes and setup elapsed time.

Preparation copies the four Markdown context files into `project/.project-context/`. The original native `AGENTS.md` body is retained, with a short appended instruction to read the context index and relevant files. No tracked application code changes. The added instructions are intentionally part of this method's context treatment.

The pack organizes repository responsibilities, relevant verification commands and context maintenance rules from pinned Memos documentation. It contains no selected task, solution, hidden tests, retrieval implementation or architecture for experiment three. This is v0.1 for setup and review, not an experimentally validated or finalized optimal context design.

## Commands

```sh
make setup
make check
make doctor
```

After prerequisites are installed, the same `backend-test`, `frontend-install` and `frontend-check` targets are available as in experiment one. No successful Memos test result is asserted.

Context file availability and a loading notice do not prove that an agent actually consumed the pack. Record that during future execution integration. Available information may differ between methods, but correctness/evaluation inputs must be shared.

Authoring tokens and human effort were not instrumented during this scaffold creation and remain unknown. Setup elapsed time measures only local source/context materialization. See [preparation record](preparation.md), [shared guidance](../../shared/README.md), and [protocol](../../protocol.md).

`make check` refuses to reset changes. If you edit the pack or a project, preserve that work before preparing a new initial state; do not silently replace it or relabel old observations.
