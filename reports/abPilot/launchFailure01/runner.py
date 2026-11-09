#!/usr/bin/env python3
"""Freeze and execute the single-task A/B feasibility pilot in isolated containers."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "sharedInputs/pilotProtocol.json"
PACK = ROOT / "experiments/preparedContext/strategy/contextPack"
METHODS = {"A": "existingWorkflow", "B": "preparedContext"}
SNAPSHOT = json.loads((ROOT / "sharedInputs/projectSnapshot.json").read_text())


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def command(args, **kwargs):
    return subprocess.check_output(args, text=True, **kwargs).strip()


def verify_preparation():
    checks = {}
    for relative in SNAPSHOT["projectCopies"]:
        project = ROOT / relative
        head = command(["git", "-C", str(project), "rev-parse", "HEAD"])
        tree = command(["git", "-C", str(project), "rev-parse", "HEAD^{tree}"])
        status = command(["git", "-C", str(project), "status", "--porcelain", "--untracked-files=all"])
        if head != SNAPSHOT["commit"] or tree != SNAPSHOT["gitTree"] or status:
            raise RuntimeError(f"Snapshot mismatch or uncommitted application edits: {relative}")
        checks[relative] = {"head": head, "tree": tree, "clean": True}
    pack = json.loads((PACK / "packManifest.json").read_text())
    for name, expected in pack["files"].items():
        if digest(PACK / name) != expected:
            raise RuntimeError(f"Prepared context changed after freezing: {name}")
    for source in json.loads((PACK / "sourceMap.json").read_text())["sources"]:
        for method in METHODS.values():
            if digest(ROOT / "experiments" / method / "memos" / source["path"]) != source["sha256"]:
                raise RuntimeError(f"Context source mismatch: {source['path']}")
    return checks


def freeze(args):
    if PROTOCOL.exists():
        raise RuntimeError("Protocol already exists; refusing to overwrite frozen inputs")
    checks = verify_preparation()
    baseline = Path(args.baseline_log)
    statuses = re.findall(r"PILOT_NATIVE_STATUS lint=(\d+) test=(\d+) build=(\d+)", baseline.read_text())
    if not statuses or statuses[-1] != ("0", "0", "0"):
        raise RuntimeError("Native frontend baseline is not healthy")
    image = command(["docker", "image", "inspect", args.image, "--format", "{{.Id}}"])
    order = ["A", "B"]
    random.Random(20261108).shuffle(order)
    inputs = ["sharedInputs/tasks/rawStringPilot.md", "sharedInputs/evaluation/rawStringPilot.mjs",
              "sharedInputs/evaluation/evaluatorValidation.json", "sharedInputs/metricsDefinition.md",
              "experiments/tools/pilotRuntime/Dockerfile", "experiments/tools/pilotRuntime/frontend.Dockerfile",
              "experiments/tools/runPilot.py", "experiments/preparedContext/strategy/contextPack/packManifest.json"]
    report = ROOT / "reports/abPilot"
    report.mkdir(exist_ok=True)
    shutil.copyfile(baseline, report / "baselineNative.log")
    data = {
        "pilotId": "rawStringPilot01", "status": "frozen-before-agent-execution", "frozenAt": now(),
        "purpose": "Feasibility only; researcher-designed task, one task and one attempt per method",
        "snapshot": SNAPSHOT["commit"], "sourceTree": SNAPSHOT["gitTree"], "snapshotChecks": checks,
        "image": image, "model": "gpt-6-luna", "modelSelection": "Existing user CLI default at preparation time",
        "reasoningEffort": "low", "cliVersion": "0.167.0", "methods": METHODS,
        "taskCount": 1, "attemptsPerMethod": 1, "methodOrder": order, "orderSeed": 20261108,
        "executionWallSeconds": 600, "cpuLimit": 2, "memoryLimit": "4g", "pidLimit": 256,
        "tokenCap": None, "tokenCapNote": "CLI does not enforce a registered token cap; actual usage is recorded",
        "requiredChecks": ["independent acceptance and focused regressions", "native frontend lint", "pristine native frontend tests", "frontend build", "permitted changes"],
        "permittedProductionChanges": ["web/src/lib/suggestion-expression.ts"],
        "permittedTestChangesPrefix": "web/tests/",
        "requireTestChanges": True,
        "inputHashes": {p: digest(ROOT / p) for p in inputs},
        "baselineLogSha256": digest(report / "baselineNative.log"),
        "isolation": "Fresh containers and project copies; only own project and B-only read-only context mounted. Evaluator, research, reports and other methods are not mounted. Fresh CLI homes; memories, delegation, apps and web search disabled.",
        "network": "Provider access available; external solutions prohibited in task prompt. Shell egress is not technically restricted to provider domains.",
        "evaluation": "Fresh offline containers; no agent credentials; pristine upstream test files restored; all candidate changes and original logs retained",
        "failurePolicy": "No best-of retries or manual code repair. Agent errors/timeouts count as task failure. Infrastructure interruption is reported separately; no selective rerun.",
        "missingPreparationUsage": "Coordinator token consumption and active human time unavailable; whole-workflow savings cannot be computed",
        "inference": "Descriptive one-task result only; no superiority test, confidence interval or general ranking",
    }
    write_json(PROTOCOL, data)
    print(json.dumps({"protocol": str(PROTOCOL.relative_to(ROOT)), "image": image, "order": order}))


def validate_frozen(protocol):
    verify_preparation()
    for name, expected in protocol["inputHashes"].items():
        if digest(ROOT / name) != expected:
            raise RuntimeError(f"Frozen input changed: {name}")


def usage_from_events(path):
    usage = []
    events = []
    for line in path.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.append(event)
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage.append(event["usage"])
    result = {"completedTurns": len(usage), "inputTokens": None, "outputTokens": None,
              "cachedInputTokens": None, "cacheWriteInputTokens": None,
              "reasoningOutputTokens": None, "totalTokens": None}
    if usage:
        for key, raw in (("inputTokens", "input_tokens"), ("outputTokens", "output_tokens"),
                         ("cachedInputTokens", "cached_input_tokens"), ("cacheWriteInputTokens", "cache_write_input_tokens"),
                         ("reasoningOutputTokens", "reasoning_output_tokens")):
            values = [item.get(raw) for item in usage]
            if all(type(value) is int and value >= 0 for value in values):
                result[key] = sum(values)
        if result["inputTokens"] is not None and result["outputTokens"] is not None:
            result["totalTokens"] = result["inputTokens"] + result["outputTokens"]
    result["failedTurnEvents"] = sum(event.get("type") in ("turn.failed", "error") for event in events)
    result["note"] = "Input includes cached input; output includes reported reasoning. Subsets are not added twice. Incomplete/failed turns may have unreported usage."
    return result


def capture_changes(project, output, protocol):
    baseline = ROOT / "experiments/existingWorkflow/memos"
    originals = set(subprocess.check_output(["git", "-C", str(baseline), "ls-files", "-z"]).decode().split("\0")) - {""}
    def local_file(name):
        candidate = project / name
        return candidate.is_file() and not candidate.is_symlink() and candidate.resolve().is_relative_to(project.resolve())

    tracked = [name for name in originals if not local_file(name)
               or digest(project / name) != digest(baseline / name)
               or ((project / name).stat().st_mode & 0o111) != ((baseline / name).stat().st_mode & 0o111)]
    extra = []
    for directory, directories, files in os.walk(project, followlinks=False):
        directories[:] = [name for name in directories if name not in (".git", "node_modules", ".projectContext")]
        for name in files:
            relative = str((Path(directory) / name).relative_to(project))
            if relative not in originals:
                extra.append(relative)
    # Use the trusted baseline ignore rules, never candidate Git metadata, to classify generated files.
    ignored = subprocess.run(["git", "-C", str(baseline), "check-ignore", "--no-index", "--stdin"],
                             input="\n".join(extra), capture_output=True, text=True)
    untracked = sorted(set(extra) - set(ignored.stdout.splitlines()))
    names = sorted(set(tracked + untracked))
    same_head = command(["git", "-C", str(project), "rev-parse", "HEAD"]) == protocol["snapshot"]
    allowed = same_head and all((name in protocol["permittedProductionChanges"] or name.startswith(protocol["permittedTestChangesPrefix"]))
                               and not (project / name).is_symlink() for name in names)
    patch = b""
    for name in names:
        before = baseline / name if name in originals else Path("/dev/null")
        after = project / name if (project / name).exists() or (project / name).is_symlink() else Path("/dev/null")
        addition = subprocess.run(["git", "diff", "--no-index", "--binary", str(before), str(after)], capture_output=True)
        patch += addition.stdout.replace(str(baseline).lstrip("/").encode() + b"/", b"").replace(str(project).lstrip("/").encode() + b"/", b"")
    (output / "changes.patch").write_bytes(patch)
    record = {"files": names, "permitted": allowed, "headUnchanged": same_head,
              "testFilesChanged": [name for name in names if name.startswith(protocol["permittedTestChangesPrefix"])],
              "fileHashes": {name: digest(project / name) if local_file(name) else None for name in names},
              "patchSha256": digest(output / "changes.patch")}
    write_json(output / "changes.json", record)
    return record


def execute(method, protocol, protocol_hash):
    slug = METHODS[method]
    output = ROOT / "experiments" / slug / "runs" / protocol["pilotId"]
    output.mkdir(parents=True, exist_ok=False)
    project = output / "project"
    shutil.copytree(ROOT / "experiments" / slug / "memos", project)
    prompt = (ROOT / "sharedInputs/tasks/rawStringPilot.md").read_text()
    common = "Follow the repository's native AGENTS.md. Do not read authentication files, change Git history, or delegate to other agents.\n"
    if method == "B":
        common += "Before working, read .projectContext/contextGuide.md in full. Its source map is available for verification.\n"
    prompt = common + "\n" + prompt
    (output / "prompt.md").write_text(prompt)
    name = f"memos-ab-{protocol['pilotId'].lower()}-{method.lower()}"
    auth = Path.home() / ".codex/auth.json"
    if not auth.is_file():
        raise RuntimeError("Existing Codex login unavailable")
    args = ["docker", "run", "--rm", "--init", "--name", name,
            "--cpus", str(protocol["cpuLimit"]), "--memory", protocol["memoryLimit"],
            "--pids-limit", str(protocol["pidLimit"]), "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges", "--mount", f"type=bind,source={project},target=/project",
            "--mount", "type=volume,destination=/project/web/node_modules",
            "--mount", f"type=bind,source={auth},target=/root/.codex/auth.json,readonly"]
    if method == "B":
        args += ["--mount", f"type=bind,source={PACK},target=/project/.projectContext,readonly"]
    args += ["--workdir", "/project", protocol["image"], "codex", "exec", "--ignore-user-config",
             "--ephemeral", "--json", "--color", "never", "--model", protocol["model"],
             "--sandbox", "danger-full-access", "--disable", "memories", "--disable", "multi_agent",
             "--disable", "apps", "-c", f'model_reasoning_effort="{protocol["reasoningEffort"]}"',
             "-c", 'web_search="disabled"', "--cd", "/project", "-"]
    started = now()
    start = time.monotonic()
    timed_out = False
    with (output / "events.jsonl").open("w") as stdout, (output / "stderr.log").open("w") as stderr:
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, text=True)
        try:
            process.communicate(prompt, timeout=protocol["executionWallSeconds"])
        except subprocess.TimeoutExpired:
            timed_out = True
            subprocess.run(["docker", "kill", name], capture_output=True)
            process.communicate(timeout=30)
    result = {"method": method, "strategy": slug, "startedAt": started, "finishedAt": now(),
              "elapsedSeconds": round(time.monotonic() - start, 3), "exitCode": process.returncode,
              "timedOut": timed_out, "protocolSha256": protocol_hash,
              "usage": usage_from_events(output / "events.jsonl")}
    result["changes"] = capture_changes(project, output, protocol)
    events = [json.loads(line) for line in (output / "events.jsonl").read_text().splitlines() if line.startswith("{")]
    result["contextReadCommands"] = [event["item"]["command"] for event in events
        if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "command_execution"
        and event["item"].get("exit_code") == 0 and "contextGuide.md" in event["item"].get("command", "")]
    write_json(output / "execution.json", result)
    print(json.dumps({"finished": method, "elapsedSeconds": result["elapsedSeconds"], "exitCode": result["exitCode"]}), flush=True)
    return result, output


def evaluate(result, output, protocol):
    project = output / "project"
    checks = {}
    grader = ROOT / "sharedInputs/evaluation/rawStringPilot.mjs"
    for label, shell in [
        ("independent", "node --experimental-strip-types /evaluation/rawStringPilot.mjs /candidate"),
        ("native", "cp -a /candidate/. /project/ && cd /project/web && pnpm lint; lintStatus=$?; rm -rf /project/web/tests && cp -a /baselineTests /project/web/tests; restoreStatus=$?; pnpm test; testStatus=$?; pnpm build; buildStatus=$?; printf '\\nPILOT_NATIVE_STATUS lint=%s test=%s build=%s\\n' \"$lintStatus\" \"$testStatus\" \"$buildStatus\"; test \"$lintStatus$restoreStatus$testStatus$buildStatus\" = 0000"),
    ]:
        container_name = f"memos-ab-eval-{result['method'].lower()}-{label}"
        args = ["docker", "run", "--rm", "--init", "--name", container_name, "--network", "none", "--cpus", str(protocol["cpuLimit"]),
                "--memory", protocol["memoryLimit"], "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                "--mount", f"type=bind,source={project},target=/candidate,readonly",
                "--mount", f"type=bind,source={grader},target=/evaluation/rawStringPilot.mjs,readonly",
                "--mount", f"type=bind,source={ROOT / 'experiments/existingWorkflow/memos/web/tests'},target=/baselineTests,readonly",
                protocol["image"], "bash", "-lc", shell]
        start = time.monotonic()
        try:
            completed = subprocess.run(args, capture_output=True, text=True, timeout=600)
            (output / f"{label}Evaluation.log").write_text(completed.stdout)
            (output / f"{label}Evaluation.stderr").write_text(completed.stderr)
            checks[label] = {"exitCode": completed.returncode, "passed": completed.returncode == 0,
                             "elapsedSeconds": round(time.monotonic() - start, 3)}
            if label == "independent":
                try:
                    checks[label]["details"] = json.loads(completed.stdout)
                except json.JSONDecodeError:
                    checks[label]["passed"] = False
            else:
                matches = re.findall(r"PILOT_NATIVE_STATUS lint=(\d+) test=(\d+) build=(\d+)", completed.stdout)
                checks[label]["statuses"] = dict(zip(("lint", "test", "build"), map(int, matches[-1]))) if matches else None
                checks[label]["passed"] = checks[label]["passed"] and bool(matches) and matches[-1] == ("0", "0", "0")
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "kill", container_name], capture_output=True)
            checks[label] = {"passed": False, "infrastructureError": "Independent evaluator timeout; verdict unresolved"}
    solved = (result["exitCode"] == 0 and not result["timedOut"] and result["changes"]["permitted"]
              and (not protocol["requireTestChanges"] or bool(result["changes"]["testFilesChanged"]))
              and all(item["passed"] for item in checks.values()))
    evaluation = {"method": result["method"], "verifiedCompletion": solved, "checks": checks,
                  "note": "Native tests restored from pristine snapshot. Agent-authored tests are retained in the patch; their quality is not independently graded."}
    write_json(output / "evaluation.json", evaluation)
    return evaluation


def run():
    protocol = json.loads(PROTOCOL.read_text())
    validate_frozen(protocol)
    protocol_hash = digest(PROTOCOL)
    for slug in METHODS.values():
        if (ROOT / "experiments" / slug / "runs" / protocol["pilotId"]).exists():
            raise RuntimeError("Pilot output already exists; refusing rerun or overwrite")
    records = [execute(method, protocol, protocol_hash) for method in protocol["methodOrder"]]
    # Evaluation starts after both independently prompted executions are finished.
    evaluations = {item[0]["method"]: evaluate(*item, protocol) for item in records}
    summary = {"pilotId": protocol["pilotId"], "completedAt": now(), "protocolSha256": protocol_hash,
               "executions": {result["method"]: result for result, _ in records}, "evaluations": evaluations,
               "conclusion": "Descriptive one-task pilot only. No supported general superiority claim.",
               "preparationUsage": None, "maintenanceObserved": False,
               "preservedSourceVerification": verify_preparation()}
    write_json(ROOT / "reports/abPilot/pilotSummary.json", summary)
    print(json.dumps({"report": "reports/abPilot/pilotSummary.json", "verifiedCompletion": {key: value["verifiedCompletion"] for key, value in evaluations.items()}}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("verify", "freeze", "run"))
    parser.add_argument("--baseline-log")
    parser.add_argument("--image", default="memos-ab-frontend:20261108")
    arguments = parser.parse_args()
    if arguments.action == "verify":
        print(json.dumps(verify_preparation(), indent=2))
    elif arguments.action == "freeze":
        if not arguments.baseline_log:
            parser.error("freeze requires --baseline-log")
        freeze(arguments)
    else:
        run()
