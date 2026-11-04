# Project-context workflows: focused reading guide

Updated 2026-11-03. Prioritize direct empirical evidence, distinguish publication status and avoid treating the absence of a common format as proof that no comparisons exist. This is not a systematic review or exhaustive novelty search.

## Central evidence

| Record | Role and publication status | Relevant boundary |
| --- | --- | --- |
| P06: [Mohsenimofidi et al.](https://doi.org/10.1145/3793302.3793350) | MSR 2026; inspected arXiv 2510.21413v4 | Observational context engineering, not a performance trial |
| P02: [Gloaguen et al.](https://arxiv.org/abs/2602.11988v3) | ICLR 2026 MemAgents workshop; later arXiv revision reviewed | Experimental evidence scoped to benchmark tasks and agents |
| P07: [Khatri](https://aclanthology.org/2026.realm-1.5/) | REALM 2026 workshop; reviewed arXiv v1 | Two agents; correctness and process measures, not maintenance labor |
| P08: [Chatlatanagulchai et al.](https://doi.org/10.1145/3840295) | TOSEM 2026; reviewed arXiv v2 | Repository content/evolution rather than causal effectiveness |

**MSR context engineering.** The study finds varied structures, writing styles and edits in project context files. It proposes investigation of how content and presentation affect agent behavior, as well as coevolution with code. This supports both questions, but does not demonstrate that standardization improves outcomes.

**AGENTS.md evaluation.** The revised experimental paper finds increased inference cost and no statistically significant success improvement against its no-file comparisons. Do not generalize this into a verdict that all project context is useless.

**Two-agent ablation.** The REALM study compares context delivery strategies. Its unequal selective corpora limit component attribution but remain relevant to whole-workflow comparisons. No maintenance labor estimate is supplied.

**Agent READMEs.** The study treats context files as evolving configuration-like artifacts. It informs maintenance observations rather than proving a return on authoring effort.

## Structural references for the white paper

- P09: [Esposito et al. (2024), Generative AI in Evidence-Based Software Engineering: A White Paper](https://arxiv.org/html/2407.17440v3). Use its problem, design, roadmap and limitations progression. Cite the verified arXiv version; the manuscript's journal-style header does not establish complete journal publication metadata.
- P10: [Hassan et al. (2026), Towards AI-Native Software Engineering](https://doi.org/10.1145/3807901). Publisher metadata confirms TOSEM 35(9), article 268, published 21 August 2026. Use its separation of motivation, vision and research challenges. It is a vision, not validation of this workflow.

Write original prose. These sources guide structure and framing without importing their architectures or promised effects.

## Review and artifact boundaries

The central experimental papers were reviewed for setup/results/limitations; the MSR paper for content/evolution/future work. Agent READMEs informs content characterization. No external experimental software, released datasets, analysis scripts or numerical outputs have been independently audited or reproduced here. In particular, Khatri's [released repository](https://github.com/codeprakhar25/context-files-coding-agents) remains unverified experimental material. Do not label an accessible artifact validated.

The bibliography distinguishes publication records from reviewed manuscript versions. See [metadata verification](metadata-verification.md) for primary evidence, including the newer workshop/journal records.

## Evaluation and context-use background

P03 [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/) is background on how models use supplied context. P05 [SWE-bench](https://www.swebench.com/original.html) is background for repository-task evaluation. Both remain primary-page checks only; no new full-method review or artifact validation is claimed. They are not evidence of Memos outcomes.

## Extraction questions

Use [the paper template](paper-template.md). Record information supplied, how it was created/loaded, tested tasks and models, evaluator independence, correctness/resources, uncertainty, maintenance observations and unavailable evidence. Keep author claims separate from our inference. Whole-workflow comparisons and component ablations answer different questions. A null result is not automatically equivalence.

A formal review would additionally require logged queries/dates, databases, inclusion/exclusion rules, deduplication and screening. No exhaustive review claim is made.
