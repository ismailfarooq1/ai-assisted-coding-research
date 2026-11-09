#!/usr/bin/env python3
"""Run one explicitly requested B repetition without changing the original pilot."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import time

import runPilot

ROOT = runPilot.ROOT
REPORT = ROOT / "reports/bRepeat01"
PRIOR = ROOT / "experiments/preparedContext/runs/rawStringPilot02"
RUN_ID = "bRepeat01"
DRIVER = Path(__file__).resolve()


def expected_prompt():
    return ("Follow the repository's native AGENTS.md. Do not read authentication files, change Git history, or delegate to other agents.\n"
            "Before working, read .projectContext/contextGuide.md in full. Its source map is available for verification.\n\n"
            + (ROOT / "sharedInputs/tasks/rawStringPilot.md").read_text())


def preflight():
    original = json.loads(runPilot.PROTOCOL.read_text())
    runPilot.validate_frozen(original)
    expected = expected_prompt()
    if expected != (PRIOR / "prompt.md").read_text():
        raise RuntimeError("Prompt differs from original B; refusing execution")
    if not (Path.home() / ".codex/auth.json").is_file():
        raise RuntimeError("Existing Codex authentication unavailable")
    image = runPilot.command(["docker", "image", "inspect", original["image"], "--format", "{{.Id}}"])
    if image != original["image"]:
        raise RuntimeError("Runtime image identity mismatch")
    active = runPilot.command(["docker", "ps", "--filter", "name=memos-ab", "--format", "{{.Names}}"])
    if active:
        raise RuntimeError("Another pilot/evaluator container is still running")
    # Exercise the exact stdin transport that was missing in the historical failed launches.
    probe = subprocess.run(["docker", "run", "--rm", "--interactive", "--network", "none", original["image"],
                            "node", "-e", "process.stdin.pipe(process.stdout)"],
                           input="b-repeat-stdin-ok", text=True, capture_output=True, timeout=60, check=True)
    if probe.stdout != "b-repeat-stdin-ok":
        raise RuntimeError("Docker stdin forwarding check failed")
    return original


def freeze():
    if REPORT.exists() or (ROOT / "experiments/preparedContext/runs" / RUN_ID).exists():
        raise RuntimeError("Repetition output already exists; refusing overwrite")
    original = preflight()
    protocol = deepcopy(original)
    protocol.update({
        "pilotId": RUN_ID, "frozenAt": runPilot.now(), "methods": {"B": "preparedContext"},
        "methodOrder": ["B"], "orderSeed": None, "repetitionOf": "rawStringPilot02/B",
        "purpose": "One user-requested additional B attempt on the identical task with identical prepared context; not a replacement or best-of retry",
        "parentProtocolSha256": runPilot.digest(runPilot.PROTOCOL),
        "priorPromptSha256": runPilot.digest(PRIOR / "prompt.md"),
        "contextReuse": "Same frozen pack bytes; fresh source checkout and conversation; no previous patch, logs, evaluator or research mounted",
        "candidateTestValidation": "Prespecified before this repetition: independently run all changed/new frontend test files against this candidate, in addition to the original registered gate",
        "failurePolicy": "One coding attempt, no manual repair or best-of selection; retain errors/timeouts and report them; do not overwrite original B",
        "inference": "Descriptive B-to-B repetition only. No new A run and no general superiority or context-reuse causality claim",
    })
    protocol["inputHashes"][str(DRIVER.relative_to(ROOT))] = runPilot.digest(DRIVER)
    protocol["inputHashes"]["sharedInputs/pilotProtocol.json"] = runPilot.digest(runPilot.PROTOCOL)
    REPORT.mkdir(parents=True)
    runPilot.write_json(REPORT / "protocol.json", protocol)
    print(json.dumps({"frozen": str((REPORT / "protocol.json").relative_to(ROOT)),
                      "promptIdentical": True, "stdinTransportVerified": True}), flush=True)


def candidate_test_audit(execution, output, protocol):
    files = [name for name in execution["changes"]["testFilesChanged"] if re.fullmatch(r"web/tests/.*\.test\.(?:ts|tsx)", name)]
    if not files:
        audit = {"passed": False, "reason": "No changed or new frontend test file to validate", "testFiles": []}
        runPilot.write_json(output / "candidateTestAudit.json", audit)
        return audit
    name = "memos-b-repeat-candidate-tests"
    targets = [str(Path(path).relative_to("web")) for path in files]
    shell = "set -e; cp -a /candidate/. /project/; cd /project/web; " + shlex.join(["pnpm", "exec", "vitest", "run", *targets])
    args = ["docker", "run", "--rm", "--init", "--name", name, "--network", "none",
            "--cpus", str(protocol["cpuLimit"]), "--memory", protocol["memoryLimit"],
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
            "--mount", f"type=bind,source={output / 'project'},target=/candidate,readonly",
            protocol["image"], "bash", "-lc", shell]
    started = time.monotonic()
    try:
        completed = subprocess.run(args, capture_output=True, text=True, timeout=600)
        (output / "candidateTestAudit.log").write_text(completed.stdout)
        (output / "candidateTestAudit.stderr").write_text(completed.stderr)
        clean = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", completed.stdout)
        counts = re.findall(r"^\s*Tests\s+([^\n]+)", clean, flags=re.MULTILINE)
        audit = {"passed": completed.returncode == 0, "exitCode": completed.returncode,
                 "elapsedSeconds": round(time.monotonic() - started, 3), "testFiles": files,
                 "summary": counts[-1].strip() if counts else None,
                 "classification": "Candidate-added/changed-test validation specified before this repetition"}
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "kill", name], capture_output=True)
        audit = {"passed": False, "verdictUnresolved": True, "reason": "Candidate test evaluator timeout", "testFiles": files}
    runPilot.write_json(output / "candidateTestAudit.json", audit)
    return audit


def run():
    protocol = json.loads((REPORT / "protocol.json").read_text())
    runPilot.validate_frozen(protocol)
    preflight()
    output = ROOT / "experiments/preparedContext/runs" / RUN_ID
    if output.exists():
        raise RuntimeError("Repetition already started; refusing a second coding attempt")
    prior_hashes = {name: runPilot.digest(PRIOR / name) for name in ("execution.json", "events.jsonl", "changes.patch", "evaluation.json", "prompt.md")}
    execution, output = runPilot.execute("B", protocol, runPilot.digest(REPORT / "protocol.json"))
    if runPilot.digest(output / "prompt.md") != protocol["priorPromptSha256"]:
        raise RuntimeError("Executed prompt differs from prior B; preserve record and investigate")
    print(json.dumps({"phase": "independent evaluation", "codingAttemptFinished": True}), flush=True)
    evaluation = runPilot.evaluate(execution, output, protocol)
    audit = candidate_test_audit(execution, output, protocol)
    guide = (runPilot.PACK / "contextGuide.md").read_text().strip()
    exposure = False
    for line in (output / "events.jsonl").read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if event.get("type") == "item.completed" and item.get("type") == "command_execution" and item.get("exit_code") == 0:
            exposure = exposure or (guide in item.get("aggregated_output", ""))
    artifacts_unchanged = all(runPilot.digest(output / "project" / name) == expected for name, expected in execution["changes"]["fileHashes"].items() if expected is not None)
    prior_unchanged = all(runPilot.digest(PRIOR / name) == expected for name, expected in prior_hashes.items())
    runPilot.validate_frozen(protocol)
    summary = {"runId": RUN_ID, "completedAt": runPilot.now(), "protocolSha256": runPilot.digest(REPORT / "protocol.json"),
               "execution": execution, "evaluation": evaluation, "candidateTestAudit": audit,
               "fullGuideExposureObserved": exposure, "sealedArtifactsUnchanged": artifacts_unchanged,
               "originalBRecordsUnchanged": prior_unchanged,
               "candidateFullyValidated": bool(evaluation["verifiedCompletion"] and audit["passed"] and artifacts_unchanged),
               "methodBCompletedAsSpecified": bool(evaluation["verifiedCompletion"] and audit["passed"] and artifacts_unchanged and exposure),
               "previousBExecution": json.loads((PRIOR / "execution.json").read_text()),
               "snapshotVerification": runPilot.verify_preparation(),
               "interpretation": "Both attempts used the same prepared context. Differences describe repeated execution, not an effect of adding or reusing context."}
    runPilot.write_json(REPORT / "summary.json", summary)
    write_report(summary)
    print(json.dumps({"report": "reports/bRepeat01/comparison.md", "candidateFullyValidated": summary["candidateFullyValidated"]}), flush=True)


def write_report(summary):
    previous = summary["previousBExecution"]
    current = summary["execution"]
    audit = summary["candidateTestAudit"]
    independent = summary["evaluation"]["checks"]["independent"].get("details", {}).get("outcomes", [])
    focused = f"{sum(item['passed'] for item in independent)}/{len(independent)}" if independent else "unresolved"
    native = summary["evaluation"]["checks"]["native"].get("statuses")
    rows = [
        ("Agent execution seconds", previous["elapsedSeconds"], current["elapsedSeconds"]),
        *[(label, previous["usage"].get(key), current["usage"].get(key)) for label, key in (
            ("Input tokens", "inputTokens"), ("Cached input (included in input)", "cachedInputTokens"),
            ("Output tokens", "outputTokens"), ("Total input + output tokens", "totalTokens"))],
        ("Independent acceptance and focused regressions", "23/23", focused),
        ("Legacy registered completion gate", "pass", "pass" if summary["evaluation"]["verifiedCompletion"] else "fail or unresolved"),
        ("Candidate test-file audit", "66 passed", audit.get("summary") or audit.get("reason")),
    ]
    def cell(value):
        return ("unknown" if value is None else f"{value:,}" if type(value) is int else str(value)).replace("|", "\\|")
    table = "\n".join(f"| {cell(label)} | {cell(left)} | {cell(right)} |" for label, left, right in rows)
    seconds = current["elapsedSeconds"] - previous["elapsedSeconds"]
    percent = seconds / previous["elapsedSeconds"] * 100
    note = f"The repeat took {abs(seconds):.3f} seconds ({abs(percent):.1f}%) {'longer' if seconds >= 0 else 'less time'} than the previous B attempt."
    report = f'''# B repetition with unchanged prepared context

One additional B coding attempt was requested and performed. The original A/B results and context files are preserved. This repeats the same task from the same clean Memos snapshot; it does not resume the solved project or the previous agent conversation.

The existing context guide/source map, task, prompt, model (`gpt-6-luna`, low reasoning), CLI 0.167.0, image ID and 600-second/2-CPU/4-GB limits match the previous B attempt. The context was reused byte-for-byte; prior patches, logs and hidden evaluation were not mounted in the coding-agent container. Docker stdin transport, input hashes, source snapshots and runtime identity were checked before launching. Exactly one new coding attempt was made, without manual repair or selecting a preferred outcome.

| Measurement | Previous B | B repeat |
|---|---:|---:|
{table}

{note} Execution time uses the same monotonic wall-clock definition as before: Docker invocation through agent exit, including container/dependency-volume startup, excluding independent evaluation. Provider caching and stochastic behavior can vary. Token totals include cached input; cached and reasoning subsets are not added again. These observations do not establish monetary cost or general performance differences.

The repeat's native evaluator statuses are `{native}` (zero means success). Candidate-added/changed test-file validation was specified before this repeat and runs in a separate offline evaluator with those tests retained. The old registered gate is also reported unchanged. Full guide text was observed in a successful read event: **{summary['fullGuideExposureObserved']}**. The candidate passes both the original gate and the additional test validation: **{summary['candidateFullyValidated']}**.

Both B attempts already used the same prepared context. A timing difference therefore measures repeat variability; it cannot show that context reuse caused an improvement. A was not rerun, so this is not another paired A/B comparison. Preparation and active human effort remain unmetered; no context was regenerated and no maintenance episode was observed.

Evidence: [repeat protocol](protocol.json), [machine-readable summary](summary.json), [execution](../../experiments/preparedContext/runs/{RUN_ID}/execution.json), [patch](../../experiments/preparedContext/runs/{RUN_ID}/changes.patch), [original-gate evaluation](../../experiments/preparedContext/runs/{RUN_ID}/evaluation.json), [candidate test audit](../../experiments/preparedContext/runs/{RUN_ID}/candidateTestAudit.json), [raw events](../../experiments/preparedContext/runs/{RUN_ID}/events.jsonl), [original B](../abPilot/comparison.md). Original snapshots, prepared context and earlier results are not overwritten.
'''
    (REPORT / "comparison.md").write_text(report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("freeze", "run"))
    args = parser.parse_args()
    freeze() if args.action == "freeze" else run()
