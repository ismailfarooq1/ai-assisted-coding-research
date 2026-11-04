# Experiment 1: existing project workflow

Purpose: measure the workflow already available in Memos, including native agent instructions, domain terminology, documentation and ordinary repository tools.

## This project

- [project/](project/): independent Memos working copy at the shared candidate commit.
- [method.json](method.json): method definition; no additional context, no active agent execution.
- [Makefile](Makefile): setup, initial-state checks and application verification commands.
- `setup-manifest.json`: locally generated source/context identity and setup elapsed time; not a task execution result.

The initial application tree is unchanged. No native context files are removed, rewritten or withheld. This is an existing-workflow comparison rather than a no-context condition. How a chosen agent loads instructions must be observed when agent integration is designed.

## Commands

From this folder:

```sh
make setup
make check
make doctor
```

With the required Go and frontend dependencies available, `make backend-test` runs backend checks; `make frontend-install` installs pinned frontend dependencies and `make frontend-check` runs lint, tests and build. Store tests may require a working container environment. These checks have not yet been run successfully here.

`make check` audits the initial state. It will report changed files after development instead of silently resetting them. Preserve task work separately when the future run lifecycle is designed.

The model, tasks, budgets and independent evaluator are shared study decisions, not choices made independently by this method. Read [shared guidance](../../shared/README.md) and [protocol](../../protocol.md). Never give the future agent the parent research workspace, evaluator-only files or another method's outputs.
