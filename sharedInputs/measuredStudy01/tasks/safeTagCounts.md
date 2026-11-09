# safeTagCounts

Make mergeTagCounts ignore counts that are not nonnegative safe integers (including negative values, fractions, nonfinite numbers, unsafe integers and runtime non-number values). Retain zero-valued tags. Saturate sums at Number.MAX_SAFE_INTEGER. Preserve own-key-only enumeration, null-prototype output, safe treatment of __proto__/constructor, undefined inputs and input immutability. Preserve all other exports.

Only change `web/src/lib/tag.ts` and relevant files in `web/tests/`. Add or update regression tests. Preserve unrelated behavior. Follow native project guidance and run appropriate checks. Do not use external solutions or access other runs. Do not change dependencies, generated files, test configuration or Git history. Report checks actually completed and any limitations.
