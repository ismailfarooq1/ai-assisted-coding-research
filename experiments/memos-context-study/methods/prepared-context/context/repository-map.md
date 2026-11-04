# Repository map

Source: [`AGENTS.md`, Repository Layout and Change Routing](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/AGENTS.md), commit `b40d8a7b573774c52b022c8d6537d6baf2129dc0`.

| Surface | Responsibility and starting location |
| --- | --- |
| Startup/CLI | `cmd/memos/` |
| HTTP and transports | `server/`; API handlers in `server/api/` |
| Business rules | `core/`, without HTTP or SQL |
| Storage and migrations | `store/`, with SQLite, MySQL and PostgreSQL driver implementations |
| Markdown/filter/provider behavior | `markdown/`, `filter/`, `provider/` |
| Generic private plumbing | `internal/`; avoid introducing project-domain concepts here |
| API definitions | `proto/api/`, `proto/store/`; generated outputs under `proto/gen/` and `web/src/types/proto/` |
| Frontend | `web/src/`: React components, hooks and contexts |

Import direction documented by the project: `cmd` → `server` → `core` → `store` → `provider`/`markdown`/`filter` → `internal`. Inspect local package instructions and surrounding code before deciding where to implement a change.

Do not hand-edit generated protocol outputs. Edit proto sources and regenerate with the documented tooling. Schema changes need migrations and fresh-install SQL updates for every supported database driver. Keep API compatibility unless the task explicitly permits a break.
