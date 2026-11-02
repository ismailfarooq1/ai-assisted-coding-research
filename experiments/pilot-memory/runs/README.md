# Raw run evidence

No runs have been collected. Create one folder per continuation:

`pilot-memory_T01_R01_structured-handover/`

Keep these files in each run folder:

- `manifest.json` — copied from `../templates/run-manifest.json` and completed.
- `prompt.md` — exact continuation prompt and references to shared instructions.
- `handover.md` — the supplied handover, where applicable.
- `transcript.jsonl` or the original exported agent log — prompts, tool calls, errors, and provider usage.
- `evaluation.json` plus raw test output — objective acceptance and architecture results.
- `changes.patch` — final changes relative to the checkpoint, with added files captured too.
- `notes.md` — deviations, evaluator decisions, infrastructure failures, and redactions.

Use `../preparation/<checkpoint-id>/` for initial-session evidence, checkpoint references, both frozen handovers, their audit, and preparation costs. Keep these records separate from continuation outcomes. Create that directory when preparing the first checkpoint.

Preserve unsuccessful and interrupted runs. Leave unknown values null/blank and explain them; never fill missing usage with zeros. Keep evaluator material and research logs inaccessible from experimental agent environments. Redact secrets before committing or sharing logs, and document redactions.
