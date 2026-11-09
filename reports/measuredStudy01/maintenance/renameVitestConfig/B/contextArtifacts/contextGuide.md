# Prepared project context

Revision: `b40d8a7b573774c52b022c8d6537d6baf2129dc0`. Native source/configuration is authoritative; verify relevant details before changing code.

## c01: verification

Frontend checks are run from web/: `pnpm lint`, `pnpm test` (unit tests; invokes `vitest run --config vitest.project.config.mts`), and `pnpm build`. To run unit tests directly, use `cd web && pnpm test`; `test`, `test:watch`, and `test:coverage` explicitly select `vitest.project.config.mts`, which uses jsdom, setup file `./tests/setup.ts`, and tests `tests/**/*.test.{ts,tsx}`. Backend guidance includes `go test ./...`, `go test -v ./store/...`, and `golangci-lint run`.

Sources: `AGENTS.md`, `web/package.json`, `web/vitest.project.config.mts`.

## c02: code routing and layering

Route HTTP transport and thin handlers to `server/` and business rules to `core/`; store and migration behavior belongs in `store/`; markdown parsing/rendering and derived memo payload in `markdown/`; CEL filtering and SQL rendering in `filter/`. Import direction descends cmd → server → core → store → provider/markdown/filter → internal, with package-specific constraints enforced by depguard.

Sources: `AGENTS.md`, `markdown/doc.go`, `filter/doc.go`, `.golangci.yaml`.

## c03: frontend conventions

Frontend code uses `@/` absolute imports, strict TypeScript, and Biome formatting (2 spaces, double quotes, semicolons, 140-character line width). Put server data in React Query hooks under `web/src/hooks/`; keep UI-only state in contexts or component state. Memo display, editing, and composition use `MemoEditor`; reuse Base UI primitives and use Tailwind CSS v4 utilities, `cn()`, and CVA.

Sources: `AGENTS.md`, `web/tsconfig.json`, `web/src/components/MemoEditor/README.md`.

## c04: toolchain

The web package requires Node.js `>=24` and pins pnpm `11.0.1` in `web/package.json`; CI setup uses Node 24 and installs with `pnpm install --frozen-lockfile`. Go CI setup selects the version declared in `go.mod`; the repository guidance identifies Go 1.27.2. Tool versions belong in the shared setup actions rather than individual workflows.

Sources: `web/package.json`, `.github/actions/setup-web/action.yml`, `.github/actions/setup-go/action.yml`, `AGENTS.md`.

## c05: generated files and schema changes

Do not hand-edit generated proto outputs: change `.proto` sources and run `cd proto && buf generate`; generated outputs include Go/OpenAPI under `proto/gen/` and TypeScript under `web/src/types/proto/`. Database schema changes require SQLite, MySQL, and PostgreSQL migrations plus each driver's `LATEST.sql`; fresh-install SQL and incremental migrations must stay equivalent.

Sources: `AGENTS.md`.

## c06: documentation authority

For current behavior, use source code, tests, and package README.md/doc.go files rather than design documents. Design documents remain editable until release; after release their body is frozen and later changes go in a dated `## Amendments` section. If this repository guide conflicts with source files or CI configuration, trust the source/CI and update the guide.

Sources: `docs/design/README.md`, `AGENTS.md`.

## c07: store test prerequisites

The store test README says Docker must be running for MySQL, PostgreSQL, and released-binary upgrade tests. A single-driver test can be selected with `DRIVER=mysql go test -v ./store/test/...`; upgrade tests can be selected with `DRIVER=sqlite go test -v -count=1 -timeout 30m -run 'TestMigration|TestUpgrade|TestFreshInstall' ./store/test/...`.

Sources: `store/test/README.md`.

