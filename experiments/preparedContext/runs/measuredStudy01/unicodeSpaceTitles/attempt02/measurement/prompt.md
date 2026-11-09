Follow the repository's native AGENTS.md. Do not read authentication files, change Git history, delegate, or access external solutions.
Before working, read .projectContext/contextGuide.md in full. Its source map is available for verification.

# unicodeSpaceTitles

Make getDuplicateSpaceTitles compare titles using Unicode NFC normalization. Return all original spellings whose normalized group occurs at least twice, retaining first-occurrence order of original spellings. Do not trim or case-fold, do not mutate inputs, and keep other exports unchanged. Exact duplicates still count; an original spelling occurs at most once in the returned set.

Only change `web/src/lib/space-display.ts` and relevant files in `web/tests/`. Add or update regression tests. Preserve unrelated behavior. Follow native project guidance and run appropriate checks. Do not use external solutions or access other runs. Do not change dependencies, generated files, test configuration or Git history. Report checks actually completed and any limitations.
