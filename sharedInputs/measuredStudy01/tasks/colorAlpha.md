# colorAlpha

Add optional alpha to colorToHex. With alpha omitted or undefined keep the current six-digit RGB output. With alpha explicitly provided append two lowercase hex digits: clamp finite alpha to [0,1], round alpha*255; non-finite alpha defaults to 1. Explicit alpha=1 therefore appends ff. Preserve existing RGB clamping, rounding, missing-color behavior and call compatibility.

Only change `web/src/lib/color.ts` and relevant files in `web/tests/`. Add or update regression tests. Preserve unrelated behavior. Follow native project guidance and run appropriate checks. Do not use external solutions or access other runs. Do not change dependencies, generated files, test configuration or Git history. Report checks actually completed and any limitations.
