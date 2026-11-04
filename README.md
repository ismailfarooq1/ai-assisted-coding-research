# AI-assisted coding research

**Current study: Memos project-context workflows. Research design and project setup, 2026-11-03; no Memos experiments executed.**

We investigate (1) the benefits and resource costs of project-context methods for development tasks, and (2) the effort to keep context accurate and consistent as code changes. Compare complete workflows, accounting for preparation, execution and maintenance. Methods may supply different information; inventory that difference and its costs.

Memos is selected because it already maintains agent instructions and project documentation. The inspected documentation commit is provenance, not an experimentally validated snapshot. The reference methods are the existing project workflow and deliberately prepared context files. Three experiment slots are set up: existing workflow, prepared context files, and a disabled shell for the proposed alternative. Its architecture remains for later discussion; retrieval is not required.

## Start here

1. [Research plan](research/plan.md) and [open decisions](research/open-decisions.md).
2. [Memos selection and provenance](benchmarks/memos/README.md).
3. [The three experiment projects](experiments/memos-context-study/README.md), [shared protocol](experiments/memos-context-study/protocol.md) and [templates](framework/README.md).
4. [Literature guide](research/literature/reading-guide.md).
5. [White paper and build instructions](reports/memos-context-white-paper/README.md).

## Workspace map

| Folder | Purpose |
| --- | --- |
| `research/` | Current questions, literature and unresolved decisions |
| `framework/` | Workflow definitions and recording templates |
| `benchmarks/` | Application provenance and rationale |
| `experiments/` | Three method projects, shared configuration, setup tools and draft protocol |
| `analysis/` | Analysis rules and future derived evidence |
| `reports/` | Research-design paper, sources and build instructions |
| `notes/` | Dated decisions and verification records |

## Working conventions

- Preserve primary evidence; keep interpretations and derived data separate.
- Freeze project, task, context and evaluator inputs before scored execution. Keep hidden tests and reference solutions outside agent and preparer access.
- Isolate workspaces, conversations, caches and writable state. Do not expose another method's outputs or conclusions.
- Record failed attempts, missing measurements and deviations. Unobserved human effort and unavailable monetary costs are unknown, not zero.
- Distinguish source preparation, validated application setup and measured outcomes. Two source working copies are prepared; Memos builds/tests and agent experiments remain unvalidated.
- Keep credentials and sensitive data out of source control. No commits or publication are included in this revision.
