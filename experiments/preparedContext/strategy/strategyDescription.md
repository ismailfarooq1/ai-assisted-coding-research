# Prepared context

This strategy adds deliberately prepared project context to the existing Memos workflow.

The `memos` copy remains the unchanged pinned source. The additional pack lives in `contextPack/`: a concise `contextGuide.md`, a source map with 14 pinned-source references, and a checksum manifest. It was frozen before selecting the pilot task. It contains navigation, test-harness, terminology and maintenance guidance, with no task-specific answer or experimental result.

Each execution receives a fresh run-specific project copy and a read-only mount of this pack at `.projectContext/`. The prompt explicitly requires reading its guide before working. Native `AGENTS.md` and project documentation remain available. Successful read commands are recorded as exposure evidence; they do not establish how attentively an agent used the material.

Everything else follows the same frozen pilot protocol as A. Preparation usage and active human effort were not fully metered in the coordinating conversation and remain unknown; no total-workflow savings claim is supported. The pack may duplicate native information. Whether its additional preparation helps is what the comparison tests.

The first pilot has one task and one coding attempt per method. Logs, usage, final patches and independent evaluation live under `runs/<pilotId>/`; infrastructure-only failed launches are retained separately. This is feasibility evidence rather than a general ranking.
