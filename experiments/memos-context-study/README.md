# Memos experiment projects

Three experiment projects share the same candidate Memos revision and evaluation protocol. The first two have independent application working copies. The third is a disabled shell for a later design discussion. No agent experiments have been executed.

## Open a project

| Project | Purpose | Current state |
| --- | --- | --- |
| [1. Existing workflow](methods/existing-workflow/README.md) | Memos with its native instructions and documentation | Complete source working copy; no added context |
| [2. Prepared context](methods/prepared-context/README.md) | Same source plus deliberately prepared context files | Complete source working copy and initial context pack |
| [3. Proposed method](methods/proposed-method/README.md) | Your alternative, to be discussed | Configuration and discussion shell only; setup/execution disabled |

## Folder map

```text
memos-context-study/
├── methods/
│   ├── existing-workflow/   # project/, method.json, Makefile, README
│   ├── prepared-context/   # project/, context/, method.json, Makefile, README
│   └── proposed-method/    # disabled configuration and discussion notes
├── shared/                 # common source/configuration, task and evaluator boundaries
├── tools/                  # source preparation, startup checks and scaffold tests
├── runs/                   # future attempt records; currently no runs
├── protocol.md             # common evaluation rules
└── Makefile                # setup, check, doctor, status, test
```

`project/` contains the actual Memos application. Its copies and generated setup manifests are ignored by the research repository and can be recreated from the pinned source. The shared local source cache lives at `.local/memos-origin` under the research workspace. It is used by preparation tooling only.

From this folder:

```sh
make setup    # prepare the first two projects; never resets existing work
make check    # verify their initial source/context against setup manifests
make doctor  # report installed tools and pinned application requirements
make status  # show all three project states
make test    # test preparation safeguards and the disabled third method
```

From a method folder, `make setup`, `make check` and `make doctor` operate on that project. `make backend-test`, `make frontend-install` and `make frontend-check` provide application verification commands for the first two methods, once dependencies are available. These commands do not run coding agents or hidden evaluation.

## What is ready and what remains

The pinned candidate is `b40d8a7b573774c52b022c8d6537d6baf2129dc0`. Preparation validates file identities, preserves native instructions and creates independent Git metadata without remotes or shared writable application files. The initial prepared pack is task-independent, source-linked and versioned in the research repository. Its loading notice is appended to the original `AGENTS.md` body only in method two.

The source is a setup candidate, not a validated experimental snapshot. Go and pnpm are missing from the current host; Memos dependency installation and baseline tests remain unvalidated. [Shared setup guidance](shared/README.md) records requirements and observation boundaries. Agent/model choices, tasks, budgets, repetitions and independent acceptance checks remain open. Scored execution is disabled for every method.

Separate copies do **not** enforce filesystem isolation against an unrestricted agent. Read [the isolation requirements](shared/isolation.md) before implementing execution. No agent launcher is included, and method three deliberately has no implementation.

See [protocol](protocol.md), [Memos provenance](../../benchmarks/memos/README.md), [open decisions](../../research/open-decisions.md), [recording templates](../../framework/README.md) and [analysis guidance](../../analysis/README.md).
