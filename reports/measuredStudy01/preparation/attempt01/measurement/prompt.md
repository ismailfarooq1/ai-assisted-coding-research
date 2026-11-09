Prepare concise additional project context from the native documentation and configuration supplied in this sparse Memos workspace. Read all supplied sources. No task descriptions, previous solutions or previous context packs are available. Do not access authentication, network sources or other projects, change source files, or delegate. Do not run application commands; dependencies/backend are not provided for preparation.
Write only contextOutput/claims.json as {"claims":[{"id":"c01","topic":"short topic","text":"one auditable factual claim or closely related instruction","sources":["relative/source/path"]}]}.
Use 1–12 claims and at most 650 words of claim text. Every claim must cite one or more supplied native source files. Cover verification commands, code routing, frontend conventions, actual toolchain requirements, generated-file rules and source authority where supported. Include exact actionable frontend unit-test invocation and the actual Vitest config location. Do not invent runtime validation, missing facts, results or task-specific advice. Preserve source authority when documentation conflicts. Return after writing valid JSON.
Allowed sources:
AGENTS.md
.golangci.yaml
core/memoexport/doc.go
markdown/doc.go
filter/doc.go
web/src/components/MemoEditor/README.md
web/package.json
.github/actions/setup-web/action.yml
web/vitest.config.mts
web/tsconfig.json
.github/actions/setup-go/action.yml
store/test/README.md
CONTEXT.md
docs/design/README.md