# Resource-record template

Status: unfilled aid. One record per observed phase/attempt; retain raw usage evidence.

| Field | Rule |
| --- | --- |
| Identity | Task/episode/method/attempt IDs, artifact and configuration hashes |
| Phase | Preparation, execution, evaluation, maintenance or human review; identify shared costs |
| Outcome | Completed, failed, timeout, infrastructure error or cancelled; evidence link |
| Usage | Raw input, cached input, output, reasoning; provider definitions and overlaps |
| Totals | Derivation without double counting; cached input may be input subset and reasoning may be output subset |
| Time | Start/end with timezone, elapsed seconds, setup/queue/tool time if observed |
| Human effort | Observed active minutes, role and activity; unknown if not collected, never inferred from runtime |
| Context | Artifact size, source revision, preparation/update procedure and reuse scope |
| Money | Actual charges or dated rates and category mapping; otherwise unknown, not zero |
| Missingness | Unavailable fields, reason, redactions and any estimation procedure |
| Evidence | Raw usage, logs, patch, evaluation and related records |

Include failed attempts and retries. Keep initial preparation, recurring execution, maintenance and evaluator overhead separate. Available context tokens are not automatically billed input. Report shared-cost allocation explicitly rather than charging it to every task invisibly.
