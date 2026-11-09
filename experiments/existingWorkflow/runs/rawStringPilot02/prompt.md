Follow the repository's native AGENTS.md. Do not read authentication files, change Git history, or delegate to other agents.

# Frontend CEL raw-string suggestions

This is a researcher-designed feasibility task on the pinned Memos snapshot,
not a sampled historical issue or a scored thesis task.

Memos's frontend suggestion reader supports ordinary quoted CEL strings, but
single-line raw strings are not recognized as string literals. Extend that
reader to recognize a lower-case `r` or upper-case `R` immediately before a
single- or double-quoted literal. The raw literal must be one token with its
literal content available to the existing suggestion machinery. Backslash
sequences such as `\n`, `\u5de5` and `\q` must remain literal text in raw
strings. Existing ordinary string escape decoding must continue to work.

Support raw literals in string lists and in Boolean expressions, including
negation and conjunction/disjunction, without interpreting operators or comment
markers inside a literal as syntax. Unclosed strings and existing malformed
Boolean expressions must remain rejected. This task covers single-line strings;
adding byte strings or multiline/triple-quoted strings is outside its scope.

Follow native project guidance and add appropriate regression tests. Keep
production edits confined to the frontend suggestion reader; test changes belong
under the existing frontend test directory. No dependencies, generated code,
backend/API behavior, release logic or documentation policy changes are needed.

Use the installed project tools. Do not fetch external solutions or use network
sources. Report the checks run and any checks that could not run. Work
independently; there are no previous attempts to consult in your environment.
