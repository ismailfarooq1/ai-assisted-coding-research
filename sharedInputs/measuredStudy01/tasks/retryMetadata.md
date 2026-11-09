# retryMetadata

Harden only the client-side getRetryAfterSeconds metadata parser. Accept canonical positive base-10 safe-integer strings matching [1-9][0-9]* whose numeric value is <= Number.MAX_SAFE_INTEGER. Reject zero, signs, leading zeros, whitespace, fractions, exponents, junk and unsafe integers. Preserve RATE_LIMITED reason gating and existing error messages. This task does not change server-side rate limiting, authentication or token enforcement.

Only change `web/src/lib/error.ts` and relevant files in `web/tests/`. Add or update regression tests. Preserve unrelated behavior. Follow native project guidance and run appropriate checks. Do not use external solutions or access other runs. Do not change dependencies, generated files, test configuration or Git history. Report checks actually completed and any limitations.
