Follow the repository's native AGENTS.md. Do not read authentication files, change Git history, delegate, or access external solutions.

# memoViewNames

Restrict getMemoViewId extraction to exact resource names users/<nonempty>/views/<nonempty>, with exactly four slash-separated components. Return the final component for valid names; return the input unchanged for malformed names, different collection names, empty components, bare identifiers or additional components. Do not introduce additional character restrictions within nonempty components, and preserve all other exports.

Only change `web/src/lib/memo-views.ts` and relevant files in `web/tests/`. Add or update regression tests. Preserve unrelated behavior. Follow native project guidance and run appropriate checks. Do not use external solutions or access other runs. Do not change dependencies, generated files, test configuration or Git history. Report checks actually completed and any limitations.
