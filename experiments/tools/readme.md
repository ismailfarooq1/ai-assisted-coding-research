# Shared experiment tools

Shared preparation, measurement, comparison and reporting tools belong here.

## A/B feasibility pilot

- `pilotRuntime/Dockerfile`: Node 24, Codex CLI 0.167.0 and pnpm 11.0.1.
- `pilotRuntime/frontend.Dockerfile`: dependencies installed from Memos's frozen frontend lockfile.
- `runPilot.py verify`: checks all three source snapshots, B's frozen context and its source references.
- `runPilot.py freeze --baseline-log PATH --pilot-id ID`: freezes task, evaluator, metrics, runner, context and image provenance after a healthy native baseline. It refuses to overwrite a protocol.
- `runPilot.py run`: runs A and B sequentially in fresh containers, retains raw events and patches, then evaluates them in fresh offline containers. It refuses to overwrite existing attempt records.
- `runPilotTests.py`: validates usage accounting, unknown-versus-zero handling and independent detection of prohibited source changes.
- `comparePilot.py`: regenerates the descriptive Markdown comparison from the retained primary records and separately labelled supplementary audit.

Build the runtime from the project root:

```sh
docker build -t memos-ab-pilot:20261108 -f experiments/tools/pilotRuntime/Dockerfile experiments/tools/pilotRuntime
docker build -t memos-ab-frontend:20261108 -f experiments/tools/pilotRuntime/frontend.Dockerfile experiments/existingWorkflow/memos/web
```

The recorded runtime used Node 24.22.2 on Linux aarch64. Its local image ID is frozen in the protocol. The resolved Node base digest is `sha256:8fa96264f302f58bbb13aa7339c541547b56975766ce956c875da149452a3e40`; use that digest rather than the moving Node tag when reconstructing the historical environment. Package/lock files and the original build logs are retained. An image ID identifies the actual local image; it is not a published registry image.

Run from the project root with Python 3 and a working Docker daemon. Agent execution uses the existing local Codex login through a read-only credential mount. Credentials are not copied into project files or reports. The agent container uses full tool access within its container; it has no host Docker socket or mounts of the evaluator, reports, research, or another method. Its only application mount is its own disposable copy. B additionally receives its read-only context pack. CLI memory, delegation, apps and web search are disabled. Shell egress is not restricted to provider domains; fetching external solutions is prohibited by the task prompt.

The source copies in each method's `memos/` directory remain unchanged. Working project copies live under `runs/<pilotId>/project/` and are ignored by the outer Git repository. Keep raw logs, hashes, patches and evaluation records alongside them. Do not rerun or edit a frozen attempt to obtain a preferred outcome.

The first launch (`rawStringPilot01`) failed for both methods because Docker did not forward stdin. Neither produced model events. Its protocol, runner and classification are retained in `reports/abPilot/launchFailure01/`. Input forwarding was validated before freezing `rawStringPilot02`; both conditions are repeated together with unchanged task/context/model/limits.

This runner is deliberately scoped to the registered single-task pilot. A confirmatory study needs a new task set, power analysis and protocol. The third method remains unimplemented.
