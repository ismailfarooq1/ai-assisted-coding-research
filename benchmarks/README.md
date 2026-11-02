# Benchmark applications

No benchmark application has been selected.

Choose one moderately complex application with several interacting modules, repeatable local setup, runnable tests, and realistic interrupted-development tasks. Record its license and provenance.

For each application, create `<benchmark-id>/README.md` containing:

- Source URL or local origin, license, and exact commit.
- Language/runtime, dependency lockfiles, setup and test commands.
- Module responsibilities, relevant architectural constraints, and complexity measurements.
- Task starting commits and interruption checkpoints.
- How hidden acceptance tests are kept outside agent access.
- How clean, isolated run workspaces are created and network access is controlled.

Keep executable benchmark checkouts separate from this research workspace and expose only the materials allowed by each condition. Record reproducible references and sanitized evidence here. Do not copy evaluator files into agent-visible repositories.
