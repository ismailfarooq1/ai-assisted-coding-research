# First literature review: memory and continuity in coding agents

Created: 2026-10-19
Status: scoped reading guide, not a completed literature review.

## Recommended review question

What evidence shows that persistent project knowledge helps coding agents resume interrupted tasks, and how do the content, structure, and freshness of that knowledge affect correctness and recovery cost?

A literature review compares existing methods, evidence, disagreements, and limitations to identify a defensible next experiment. Individual paper summaries are inputs to that comparison.

## Four useful themes

| Theme | Question to investigate | Connection to our study |
| --- | --- | --- |
| Memory and handovers | What must survive a reset, and how is it reconstructed? | Primary focus for the first pilot |
| Repository instructions | When do static instructions help or add overhead? | Establish a realistic baseline |
| Context selection | Which evidence should be provided, retrieved, or omitted? | Inform later retrieval experiments |
| Evaluation | How are correctness, recovery, cost, and leakage measured? | Make experimental results credible |

Architecture preservation and repository scalability can be reviewed next, after narrowing the first study.

## Starting papers, in suggested reading order

### 1. Handoff Debt — Dipesh KC and Anjila Budathoki (2026)

[Handoff Debt: The Rediscovery Cost When Coding Agents Take Over Interrupted Tasks](https://arxiv.org/abs/2606.02875v2)

The abstract describes deterministic interruptions and successor agents receiving repository state only, raw traces, summary notes, or structured notes. It reports consistent efficiency gains from context-bearing handoffs, with smaller, model-dependent effects on solving tasks.

Read for: interruption rules, checkpoint construction, summary-versus-structure comparisons, cost accounting, and whether handovers contain equivalent information. Inspect the actual comparisons before attributing an effect to structure.

This directly overlaps our draft pilot. We cannot claim that testing handover-based interrupted-task recovery is itself new. Potential extensions such as equal-information comparisons, stale decisions, or architectural constraints must first be checked against the full paper and its related work.

### 2. Evaluating AGENTS.md — Gloaguen et al. (2026)

[Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?](https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd)

The authors' publication page reports no overall task-success improvement and increased inference cost in their tested settings. This concerns repository context files, not a universal verdict on all memory or handover methods.

Read for: generated versus developer-written instructions, model/task differences, unnecessary requirements, and baseline construction.

### 3. Lost in the Middle — Liu et al. (2024)

[Lost in the Middle: How Language Models Use Long Contexts](https://aclanthology.org/2024.tacl-1.9/)

The abstract reports that relevant information's position affects performance on multi-document question answering and key-value retrieval.

Read for: experimental controls, context positions, and why information availability does not guarantee effective use. These are not coding-recovery experiments, so relevance to our setting is a hypothesis to test.

### 4. MemTrace — Xu et al. (2026)

[MemTrace: State-Consistent Memory for Long-Horizon Coding Agents](https://arxiv.org/abs/2610.04838v3)

The abstract proposes memory tied to execution evidence and repository state, checking whether historical information remains valid before reuse.

Read for: stale evidence detection, source tracking, state reconstruction, baselines, and component ablations. Consider whether benefits arise from representation, retrieval, or additional validation.

### 5. SWE-bench — Jimenez et al. (ICLR 2024; preprint 2023)

[SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://www.swebench.com/original.html)

The official project page describes repository-level tasks drawn from GitHub issues and pull requests, reproducible execution environments, and tests that fail before the fix and pass afterward.

Read for: task construction, executable evaluation, preservation of existing behavior, and the limits of issue-resolution benchmarks for interrupted development.

## How to review each paper

Use `paper-template.md`. Start with the abstract, introduction, experimental setup, main results, and limitations. Record:

1. The exact question and what the authors actually tested.
2. What information the agent could access and how memory was created.
3. Models, tasks, baselines, budgets, and evaluation controls.
4. Correctness, resource costs, failures, and uncertainty.
5. What the results do not establish.
6. The resulting decision or unanswered question for our experiment.

Then synthesize across papers: compare methods, explain disagreements, and state which gaps remain supported after reading the full texts. Do not assume that a gap exists because an abstract omits a detail.

For a manageable first pass, review these five papers and follow their references and later citing papers to find additional directly relevant work. This is a focused exploratory review. A systematic review would additionally require a predefined search strategy, databases, inclusion criteria, deduplication, and a documented screening process.

## Search phrases

- coding agent interrupted task handover evaluation
- coding agent persistent memory context reset
- repository instructions context files empirical evaluation
- coding agent stale memory repository state
- software engineering agent recovery cost benchmark

Record search dates, queries, selected papers, and exclusions if the review will support a formal publication.

## Verification boundary

On 2026-10-19, titles and bibliographic details were checked against primary-source abstract, publisher, project, or author publication pages. The descriptions above are based on those pages; full methods, results tables, artifacts, and reproducibility have not been reviewed. Handoff Debt and MemTrace are linked to specific arXiv versions; no peer-review status is inferred from arXiv hosting.
