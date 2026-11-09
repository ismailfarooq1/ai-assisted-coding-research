# Experiment reports

Completed experiment reports and comparisons belong here. Raw execution records belong in each experiment's `runs` folder.

Start with [the A/B pilot comparison](abPilot/comparison.md). Both registered functional gates passed; a separate audit caught one failing added test in A, while B's changed test file passed. The report preserves that scoring distinction and includes execution tokens/time, native-baseline evidence, environment preparation and infrastructure-failure history.

Raw coding-agent events, patches and evaluation logs live in each method's `runs/rawStringPilot02/` directory. `abPilot/pilotSummary.json` holds the primary machine-readable record; `abPilot/additionalAudit.json` holds the separately labelled audit. Neither source snapshot was changed.

One task is a feasibility observation and cannot support a general method ranking. Context preparation resources and maintenance effort are not fully observed in this pilot.
