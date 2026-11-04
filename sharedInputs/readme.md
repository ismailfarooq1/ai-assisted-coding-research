# Shared inputs

All three experiments use the same source revision, task requirements and evaluation rules.

- [projectSnapshot.json](projectSnapshot.json) records the common Memos source revision.
- `tasks/` is reserved for common task definitions.
- `evaluation/` is reserved for independent checks, outside agent-visible application folders.
- [metricsDefinition.md](metricsDefinition.md) will hold the metrics we agree to measure.

Source copies have been checked for consistency. Application dependencies, builds, tests and agent execution have not been validated. Folder separation alone does not enforce agent access restrictions; execution isolation will be designed before experiments run.
