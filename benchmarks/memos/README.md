# Memos: selected study application

Status: documentation inspected and two source working copies prepared on 2026-11-03; application build/tests and experiments have not been validated.

- Repository: https://github.com/usememos/memos
- Inspected documentation revision: `b40d8a7b573774c52b022c8d6537d6baf2129dc0`.
- [Pinned tree](https://github.com/usememos/memos/tree/b40d8a7b573774c52b022c8d6537d6baf2129dc0). This is **not an experimentally validated snapshot** and does not freeze the future benchmark revision.
- [License](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/LICENSE): MIT.

## Selection rationale and evidence

Memos is an open-source, self-hosted note-taking application with a Go backend and React/TypeScript frontend. It already has substantial agent-facing guidance. This allows an incremental comparison with a team-maintained workflow rather than an artificially undocumented repository. Selection does not establish representativeness or proven local test feasibility.

| Inspected file | What it documents | Git blob SHA |
| --- | --- | --- |
| [README.md](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/README.md) | Application purpose, installation and documentation links | `69210e53c4d2b84435362adae94997ca3c6db0a0` |
| [AGENTS.md](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/AGENTS.md) | Agent rules, layer responsibilities, change routing, Go/frontend/proto tests and maintenance instructions | `5716713e3d9d81e688901e980f218cf8ca51d8dc` |
| [CONTEXT.md](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/CONTEXT.md) | Domain terminology and distinctions | `32b4341a1b3cb9b910a4bedbf089f2bf62f1a0e5` |
| [docs/design/README.md](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/docs/design/README.md) | Editable unreleased designs, frozen released bodies and dated amendments | `98ec6f3cc36a1a06d2496f1dfdf68c44c687ae45` |
| [LICENSE](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/LICENSE) | MIT terms | `ad324eef282c58316ff9dfc8ed5086d120a2311c` |

AGENTS.md refers developers to package-local README/doc.go files, asks that contributor guidance stay current with relevant code changes, and says source and tests determine current behavior. These are documented policies; compliance has not been measured. The design lifecycle distinguishes historical rationale from current behavior, which matters when auditing stale context.

## Testing guidance, not executed checks

The inspected instructions list `go test ./...`, targeted backend tests, store tests using TestContainers, and frontend `pnpm lint`, `pnpm test` and `pnpm build` from `web/`. Proto checks are documented separately. These commands have **not** been run here; dependencies, runtime versions, containers and baseline behavior require validation before adopting an executable snapshot. No current task, patch or acceptance suite is selected.

## Experimental boundary

Retain native context in the existing-workflow reference. Inventory what the chosen agent actually loads. Added preparation must cite permitted project sources and exclude hidden evaluator material. Pin a validated revision, task inputs, environment, evaluator and method context before scored execution. See [open decisions](../../research/open-decisions.md). The same candidate source has been copied into the [first two experiment projects](../../experiments/memos-context-study/README.md). Application code is unchanged; method two appends a context-loading notice to the retained native `AGENTS.md` body and adds a prepared context pack. The third method has no application copy or implementation yet.
