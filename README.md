# AI-assisted coding research

A local workspace for investigating whether structured project knowledge helps AI coding agents complete software engineering tasks reliably and efficiently.

**Status:** research setup, 2026-10-19. No experiments have been run and no results have been collected. The first study focuses on recovery after a conversation reset.

## Workspace map

| Folder | What belongs here |
| --- | --- |
| `sources/` | Original material, preserved separately from our interpretation |
| `research/` | Research questions, scope, and literature reviews |
| `framework/` | Proposed knowledge structure and handover templates |
| `benchmarks/` | Benchmark application specifications and repository provenance |
| `experiments/` | Protocols, task definitions, run records, and raw evidence |
| `analysis/` | Analysis scripts, derived tables, and figures |
| `reports/` | Pilot reports, papers, and presentation material |
| `notes/` | Dated working notes and decisions |

## Start here

1. Read [the research plan](research/plan.md).
2. Review [the draft pilot protocol](experiments/pilot-memory/protocol.md).
3. Select a benchmark application using [these requirements](benchmarks/README.md).
4. Define five interrupted-development tasks using [the task template](experiments/pilot-memory/tasks/task-template.md).
5. Verify the literature and finalize the protocol before collecting scored runs.

## Working conventions

- Keep primary evidence unchanged; put interpretations and derived data in separate files.
- Use Markdown for documents, CSV for tables, and JSON for machine-readable metadata.
- Use IDs such as `T01` for tasks and `pilot-memory_T01_R01_structured-handover` for runs.
- Record dates as `YYYY-MM-DD`; include a timezone in timestamps.
- Mark documents as draft until their decisions are settled. Log protocol changes and deviations.
- Never treat the outline's example numbers as measurements or its references as verified citations.
- Keep this research workspace outside agent-visible benchmark checkouts. Hidden tests, reference solutions, and research notes must not leak into experimental context.
- Store data locally here. Do not commit credentials, private prompts, or sensitive logs; keep sanitized evidence and document any redactions.

This scaffold provides storage and study templates. The benchmark application, agent runner, tests, and analysis code still need to be built or selected.
