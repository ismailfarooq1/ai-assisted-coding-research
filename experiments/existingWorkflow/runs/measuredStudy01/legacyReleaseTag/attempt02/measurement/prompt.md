Follow the repository's native AGENTS.md. Do not read authentication files, change Git history, delegate, or access external solutions.

# legacyReleaseTag

Extend getReleaseTag to accept an already-prefixed lowercase legacy tag v0.x.y[-rc.K], returning it unchanged. Use the existing legacy numeric grammar (no leading zeroes except a single zero; positive rc number). Preserve bare legacy conversion and bare calendar releases. Continue rejecting prefixed calendar releases, uppercase V, double v, whitespace and malformed versions.

Only change `web/src/lib/release-version.ts` and relevant files in `web/tests/`. Add or update regression tests. Preserve unrelated behavior. Follow native project guidance and run appropriate checks. Do not use external solutions or access other runs. Do not change dependencies, generated files, test configuration or Git history. Report checks actually completed and any limitations.
