# Verification by changed surface

Source: [`AGENTS.md`, Commands, Change Routing and Verification Policy](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/AGENTS.md), commit `b40d8a7b573774c52b022c8d6537d6baf2129dc0`.

Run the narrowest relevant checks while iterating, then the checks appropriate to the changed surface. Commands are documented by Memos; installation and successful baseline execution still require validation.

| Change | Documented check |
| --- | --- |
| Backend service/business behavior | `go test -v -race ./server/... ./core/...` |
| Storage and migrations | `go test -v ./store/...`; these include TestContainers-based driver tests |
| Markdown, filters, providers | `go test -v -race ./markdown/... ./filter/... ./provider/...` |
| Private plumbing | `go test -v -race ./internal/...` |
| Frontend behavior | From `web/`: `pnpm lint` and `pnpm test` |
| Frontend production output | From `web/`: `pnpm build` |
| Proto changes | From `proto/`: `buf generate` and `buf lint` |
| Documentation-only edits | `git diff --check`, plus runnable examples where relevant |

The repository also documents `go test ./...`. Report any check that could not run and its reason. Passing developer-visible checks is separate from independent task evaluation.
