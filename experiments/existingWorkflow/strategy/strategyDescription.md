# Existing workflow

The agent uses Memos's code, native instructions, documentation and ordinary repository tools.

The `memos` copy remains the unchanged pinned source. Each execution uses a fresh run-specific copy in an isolated container. Native `AGENTS.md`, `CONTEXT.md`, package documentation and ordinary repository search remain available. There is no injected research context, task solution, evaluator or access to another condition's files.

For the first feasibility comparison, A and B receive the same task and execution policy from `sharedInputs/pilotProtocol.json`. The pilot uses one task and one coding attempt per method; it cannot establish general superiority. Execution logs, usage, final patches and independent evaluation records live under `runs/<pilotId>/`. Infrastructure-only failed launches are retained separately from task verdicts.
