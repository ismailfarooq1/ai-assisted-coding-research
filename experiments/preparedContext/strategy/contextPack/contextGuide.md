# Prepared project context: Memos

Scope: pinned revision b40d8a7b573774c52b022c8d6537d6baf2129dc0. This is a navigation and verification aid derived from project sources. Read native AGENTS.md first. Source and tests take precedence over this guide. No experiment task, solution, evaluator output or another method's result was used to author it.

## Find the owning layer

- HTTP/RPC transport belongs in server; application rules belong in core. Storage operations and migrations belong in store. Pure Markdown and CEL-filter engines are separate root packages. internal is reserved for application-independent plumbing. Import restrictions are enforced in .golangci.yaml, not just described in AGENTS.md. [S1, S2]
- core/memoexport owns the export ZIP and JSON format and its reader/writer, while transports supply data and interpret records; it does not decide how records map to an instance. [S3]
- markdown owns parsing, AST, syntax extensions, rendering and derived payload. filter compiles CEL to an IR and per-driver SQL, including filterable-field schemas. Check each package's doc.go before extending it. [S4, S5]
- MemoEditor is the memo-aware integration point for showing, editing and composing. Its README maps view and edit subdirectories, draft lifecycle and relevant tests. Tests mounting an editing session preloadMemoEditing first. [S6]

## Verify changes using the project's harness

- Frontend CI uses Node 24 and pnpm from web/package.json (11.0.1 here), then pnpm install --frozen-lockfile. Run frontend commands from web. Test, lint and build are distinct scripts; passing one does not establish the others. [S7, S8]
- The frontend Vitest configuration is web/vitest.config.mts, separate from Vite's build configuration. It uses jsdom, tests/setup.ts, tests/**/*.test.{ts,tsx}, and the @/ alias to src. Existing tests are under web/tests, rather than beside every source file. Mock reset and spy restoration are configured for each test. [S9]
- TypeScript checks include both src and tests, with strict and unused-variable checks. Generated proto TypeScript is kept out of manual rewrites. [S1, S10]
- Backend CI obtains Go from go.mod (1.27.2 here). Store tests can involve Docker/TestContainers and released binaries. Do not mistake Docker or toolchain failures for an implementation failure; report the exact command and cause. [S8, S11, S12]
- Native guidance calls for narrow checks while iterating and checks matching the changed surface before finishing. Report checks that could not run; do not claim they passed. [S1]

## Check terminology and evidence

- CONTEXT.md distinguishes stable internal IDs, public UIDs and resource names. Space is a collaboration boundary, not an application-wide authorization role. Use the source glossary when naming fields or describing a change. [S13]
- Design documents record rationale and may describe a historical state. Unreleased designs remain editable; released bodies are frozen and later changes go into dated amendments. Current behavior must be checked in source and tests. [S1, S14]
- Avoid broad cleanup, dependency churn, manual generated-file edits and new generic helper packages. Schema changes affect all three database drivers; API changes may require regeneration and compatibility review. Native rules continue to apply. [S1]

## Evidence and limitations

sourceMap.json binds each source identifier to a path and SHA-256 at the pinned snapshot. These are inspected-source facts. Commands listed above have not, by their presence in this pack, been validated in the execution environment. This pack is task-independent and may duplicate native guidance; whether it helps is an experimental question.
