# Shared study inputs

These inputs are common to all included methods. Method-specific information belongs in each method project; task requirements and objective evaluation do not vary by method.

- [study.json](study.json): source candidate, observed runtime requirements and unresolved agent/task/budget settings.
- [Tasks](tasks/README.md): future common agent-visible requirements.
- [Evaluation](evaluation/README.md): researcher-only acceptance/regression checks.
- [Isolation](isolation.md): execution boundaries required before agent runs.
- `setup-report.json`: locally generated host/tool observations and preparation checks, not experiment outcomes.

## Source and setup

The source candidate is commit `b40d8a7b573774c52b022c8d6537d6baf2129dc0`, Git tree `9f86f8a96542b5724d7968c70e7cfed3d4ee06a1`. It was downloaded from the public Memos repository into a local preparation cache. Each implemented project is cloned independently with file copies, separate Git metadata, detached HEAD and no remotes. Future fresh attempts must begin from the pinned source and permitted method context, not from another attempt's modified project.

Runtime declarations read from the pinned `go.mod` and `web/package.json`: Go 1.27.2, Node >=24, pnpm 11.0.1. Node 24 is available locally; Go and pnpm are absent. Docker CLI presence does not establish that the daemon or TestContainers works. Dependencies and application tests have not been validated.

Install project prerequisites and use each method's application check targets when environment validation is performed. Do not treat successful file preparation as a passing application baseline. Record validation results, environment versions and any source/toolchain issues before adopting an experimental snapshot.

## Records

Use [task](../../../framework/templates/task.md), [preparation](../../../framework/templates/context-preparation.md), [maintenance](../../../framework/templates/maintenance-observation.md) and [resource](../../../framework/templates/resource-record.md) templates. Keep phase-specific preparation, execution, evaluation, updates and observed human effort separate. The setup manifests record local preparation time only; no model run or authoring labor measurement is implied.

The source is pinned for reproducible project setup. It is not a final validated benchmark, and no model, task set, repetitions or execution budget has been selected. Scored execution is disabled in the shared configuration and every method configuration.
