# Research plan: project-context workflows in Memos

Status: research design and experiment scaffolding, revised 2026-11-03. No Memos experiments executed.

## Research questions

| ID | Question |
| --- | --- |
| RQ1 | What benefits and resource costs do project-context methods produce when coding agents perform development tasks? |
| RQ2 | How much effort is required to keep that context accurate and consistent as the project changes? |

Compare complete workflows, including context creation and upkeep. Information may differ; account for its content, delivery and costs rather than imposing equal-information controls. This comparison cannot by itself attribute an effect to formatting, retrieval or extra information alone.

Memos is selected; see [provenance](../benchmarks/memos/README.md). Commit `b40d8a7b573774c52b022c8d6537d6baf2129dc0` identifies inspected documentation, not a validated executable benchmark.

## Reference workflows

- **Existing project workflow:** retain native instructions, documentation and ordinary repository tools. Record what the selected agent automatically loads and discovers. This is not a no-context condition.
- **Deliberately prepared context files:** retain the existing workflow and add prepared, versioned project context. Record allowed sources, construction, review, exposure, size and resources. The preparation rules must be selected and frozen before scored runs.

Three experiment slots are now created: existing workflow, prepared context files, and a disabled proposed-method shell. The first two have independent Memos working copies and setup checks. The prepared-file workflow has an initial task-independent pack for review; its final construction rules must still be frozen before scored work. The third method's knowledge schema, retrieval architecture and implementation remain undecided. No method is presumed superior. See [experiment projects](../experiments/memos-context-study/README.md).

## Shared evaluation flow

Pinned project and task inputs → sealed method context → fresh isolated executions → independent evaluation → resource-linked comparison. See the [draft protocol](../experiments/memos-context-study/protocol.md).

Each execution starts from the same source state and task requirements. All methods receive the same evaluation, tool policy and execution limits once selected. Preparation can differ but must be auditable. Separate workspaces, conversations, caches and writable storage prevent cross-method learning. Hidden tests and reference patches remain unavailable to agents and context preparers. The evaluator receives final artifacts after execution ends.

For RQ2, observe common project changes and each workflow's own context updates as paired maintenance episodes. Keep these separate from independent task executions. Carry forward only the workflow's intended context history. Track stale claims, contradictions, repairs and review effort. Agent runtime is not a proxy for human labor.

## Measures and analysis

Record task correctness, original regressions, token categories, elapsed time, preparation, maintenance and human effort where observed. Include failed attempts and timeouts. Keep raw usage semantics; cached input and reasoning may overlap other categories and must not be counted twice. Tokens are not monetary costs. Separate initial and recurring resources. See [analysis guidance](../analysis/README.md).

Use task-level paired comparisons, denominators and uncertainty appropriate to the eventual sample. Repeated attempts are not independent tasks. Models, tasks, sample sizes, budgets and thresholds remain open in the [internal decision register](open-decisions.md). A small project study does not establish corporate savings or general productivity effects.

## Milestones

- [x] Select Memos and document existing context and testing guidance.
- [x] Reframe current plans and prepare a research-design white paper.
- [x] Materialize two independent Memos projects and create the disabled third-method shell.
- [ ] Validate the candidate application environment and adopt an executable benchmark revision.
- [ ] Select development tasks and independent evaluators.
- [ ] Review/finalize the initial context pack and design the proposed third method.
- [ ] Choose models, repetitions, budgets and analysis before scored execution.
- [ ] Specify observable maintenance episodes and effort collection.
- [ ] Implement and validate orchestration in a later implementation stage.
