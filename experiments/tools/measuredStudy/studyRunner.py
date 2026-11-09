#!/usr/bin/env python3
"""Resumable, isolated measured A/B study. Never repeats a started coding attempt."""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import re
import shlex
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import runPilot

INPUT = ROOT / 'sharedInputs/measuredStudy01'
REPORT = ROOT / 'reports/measuredStudy01'
BASE = ROOT / 'experiments/existingWorkflow/memos'
PACK = ROOT / 'experiments/preparedContext/strategy/measuredStudy01/contextPack'
IMAGE = 'sha256:09eea9cc9b651793aabace5c6931c518f683e2857f8700c57c397e38e701b355'
METHODS = {'A': 'existingWorkflow', 'B': 'preparedContext'}

def now():
    return datetime.now(timezone.utc).isoformat()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')

def read(path):
    return json.loads(path.read_text())

def tasks():
    return read(INPUT / 'taskIndex.json')

def preflight():
    runPilot.verify_preparation()
    result = subprocess.check_output(['docker', 'image', 'inspect', IMAGE, '--format', '{{.Id}}'], text=True).strip()
    if result != IMAGE:
        raise RuntimeError('Runtime identity changed')
    active = subprocess.check_output(['docker', 'ps', '--filter', 'name=memos-measured-', '--format', '{{.Names}}'], text=True).strip()
    if active:
        raise RuntimeError('Study container already active: ' + active)
    probe = subprocess.run(['docker', 'run', '--rm', '--interactive', '--network', 'none', IMAGE, 'node', '-e', 'process.stdin.pipe(process.stdout)'], input='stdin-ok', text=True, capture_output=True, timeout=60, check=True)
    if probe.stdout != 'stdin-ok':
        raise RuntimeError('Prompt stdin transport failed')

def freeze():
    path = INPUT / 'designProtocol.json'
    if path.exists():
        raise RuntimeError('Design already frozen; refusing overwrite')
    preflight()
    order = [(task['id'], attempt) for task in tasks() for attempt in (1, 2)]
    random.Random(20261108).shuffle(order)
    schedule = [{'task': task, 'attempt': attempt, 'method': method} for task, attempt in order for method in (['A', 'B'] if attempt == 1 else ['B', 'A'])]
    sources = read(ROOT / 'experiments/preparedContext/strategy/contextPack/sourceMap.json')['sources']
    tracked = subprocess.check_output(['git', '-C', str(BASE), 'ls-files', '-z']).decode().split('\0')
    files = sorted([p for p in INPUT.rglob('*') if p.is_file()] + [p for p in HERE.glob('*') if p.is_file()])
    protocol = {
        'studyId': 'measuredStudy01', 'frozenAt': now(), 'snapshot': runPilot.SNAPSHOT['commit'], 'sourceTree': runPilot.SNAPSHOT['gitTree'],
        'image': IMAGE, 'model': 'gpt-6-luna', 'reasoningEffort': 'low', 'cliVersion': '0.167.0',
        'executionWallSeconds': 600, 'evaluationWallSeconds': 900, 'cpuLimit': 2, 'memoryLimit': '4g', 'pidLimit': 256,
        'tokenCap': None, 'codingRuns': 24, 'taskCount': 6, 'attemptsPerMethodPerTask': 2,
        'orderSeed': 20261108, 'schedule': schedule, 'methods': METHODS, 'preparationMaximumAttempts': 2,
        'preparationSources': sources,
        'sourceHashes': {name: digest(BASE / name) for name in tracked if name and (BASE / name).is_file()},
        'inputHashes': {str(p.relative_to(ROOT)): digest(p) for p in files},
        'primaryOutcome': 'Verified completion under all registered gates; task-level paired difference',
        'inference': 'Exploratory six-task convenience sample; no universal winner or equivalence claim',
        'humanReview': 'User agreed; actual participant-controlled intervals required before coding and for maintenance',
        'maintenanceEpisodes': ['renameLintScript', 'renameVitestConfig'],
        'limitations': ['No enforced provider-only shell egress', 'No hard token limit', 'Incomplete turns may have unreported usage', 'Historical native-documentation cost and coordinator/harness effort unavailable', 'Sampled local memory is not exact peak RSS; remote compute unobserved'],
    }
    write(path, protocol)
    print(json.dumps({'designFrozen': str(path.relative_to(ROOT)), 'codingRuns': 24}), flush=True)

def validate_inputs():
    protocol = read(INPUT / 'designProtocol.json')
    for name, expected in protocol['inputHashes'].items():
        if digest(ROOT / name) != expected:
            raise RuntimeError('Frozen study input changed: ' + name)
    for name, expected in protocol['sourceHashes'].items():
        if digest(BASE / name) != expected:
            raise RuntimeError('Baseline source changed: ' + name)
    return protocol

def event_usage(output):
    result = runPilot.usage_from_events(output / 'events.jsonl')
    resource = read(output / 'resource.json') if (output / 'resource.json').exists() else {}
    samples = resource.get('rolloutUsageObservations', [])
    latest = max(samples, key=lambda item: item.get('total_tokens', item.get('input_tokens', 0) + item.get('output_tokens', 0)), default=None)
    result['sessionCumulativeUsage'] = latest
    if result['completedTurns'] == 0 and latest:
        for key, raw in [('inputTokens','input_tokens'), ('outputTokens','output_tokens'), ('cachedInputTokens','cached_input_tokens'), ('reasoningOutputTokens','reasoning_output_tokens')]:
            result[key] = latest.get(raw)
        result['totalTokens'] = result['inputTokens'] + result['outputTokens'] if result['inputTokens'] is not None and result['outputTokens'] is not None else None
    result['coverage'] = 'completed-turn-reported' if result['completedTurns'] and not resource.get('timedOut') and not result['failedTurnEvents'] else 'partial-or-unreported'
    result['source'] = 'CLI completed-turn events; cumulative session metadata fallback for incomplete turns'
    result['crossCheckMatches'] = (latest.get('input_tokens') == result['inputTokens'] and latest.get('output_tokens') == result['outputTokens']) if latest and result['completedTurns'] else None
    return result

def stage(output, project, prompt=None, *, shell=None, pack=None, timeout=600, mounts=()):
    if output.exists():
        raise RuntimeError('Stage already started; refusing to replay: ' + str(output))
    output.mkdir(parents=True)
    (output / 'started.json').write_text(json.dumps({'startedAt': now(), 'codingOrPreparation': prompt is not None}) + '\n')
    name = 'memos-measured-' + hashlib.sha256(str(output).encode()).hexdigest()[:12]
    args = ['docker', 'run', '--rm', '--interactive', '--init', '--name', name, '--cpus', '2', '--memory', '4g', '--pids-limit', '256', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
            '--mount', f'type=bind,source={project},target=/project', '--mount', 'type=volume,destination=/project/web/node_modules',
            '--mount', f'type=bind,source={HERE / "measureStage.py"},target=/stage/measureStage.py,readonly',
            '--mount', f'type=bind,source={output},target=/measurement']
    if prompt is not None:
        auth = Path.home() / '.codex/auth.json'
        if not auth.is_file():
            raise RuntimeError('Existing login unavailable; stage retained as infrastructure failure')
        args += ['--mount', f'type=bind,source={auth},target=/root/.codex/auth.json,readonly']
        (output / 'prompt.md').write_text(prompt)
    else:
        args += ['--network', 'none']
    if pack:
        args += ['--mount', f'type=bind,source={pack},target=/project/.projectContext,readonly']
    for source, target in mounts:
        args += ['--mount', f'type=bind,source={source},target={target},readonly']
    command = ['bash', '-lc', shell] if shell is not None else [
        'codex', 'exec', '--ignore-user-config', '--json', '--color', 'never', '--model', 'gpt-6-luna', '--sandbox', 'danger-full-access',
        '--disable', 'memories', '--disable', 'multi_agent', '--disable', 'apps', '-c', 'model_reasoning_effort="low"', '-c', 'web_search="disabled"',
        '--skip-git-repo-check', '--cd', '/project', '-']
    args += ['--workdir', '/project', IMAGE, 'python3', '/stage/measureStage.py', '--out', '/measurement', '--timeout', str(timeout), '--', *command]
    start = time.monotonic()
    try:
        completed = subprocess.run(args, input=prompt or '', text=True, capture_output=True, timeout=timeout + 90)
        (output / 'transport.log').write_text(completed.stdout)
        (output / 'transport.stderr').write_text(completed.stderr)
        host = {'dockerExitCode': completed.returncode, 'hostWallSeconds': time.monotonic() - start, 'finishedAt': now()}
    except subprocess.TimeoutExpired:
        subprocess.run(['docker', 'kill', name], capture_output=True)
        host = {'dockerExitCode': None, 'hostWallSeconds': time.monotonic() - start, 'finishedAt': now(), 'infrastructureError': 'Host transport deadline; no automatic replay'}
    write(output / 'transport.json', host)
    if (output / 'resource.json').exists():
        host['resources'] = read(output / 'resource.json')
    else:
        host['resources'] = None
        host['infrastructureError'] = host.get('infrastructureError', 'No finalized container measurement')
    if prompt is not None and (output / 'events.jsonl').exists():
        host['usage'] = event_usage(output)
        text = (output / 'events.jsonl').read_text(errors='replace') + (output / 'stderr.log').read_text(errors='replace')
        host['providerInfrastructureFailure'] = bool(re.search(r'rate.?limit|usage limit|quota exceeded|authentication failed|unauthorized|refresh token', text, re.I)) and not host['usage']['completedTurns']
    write(output / 'stage.json', host)
    print(json.dumps({'finishedStage': str(output.relative_to(ROOT)), 'seconds': round(host['hostWallSeconds'], 2), 'processExit': (host['resources'] or {}).get('exitCode')}), flush=True)
    return host

def copy_project(destination, source=BASE):
    shutil.copytree(source, destination, symlinks=True, ignore=shutil.ignore_patterns('node_modules', '.DS_Store', '.projectContext'))

def validate_evaluators():
    validate_inputs()
    output = REPORT / 'evaluatorValidation'
    project = REPORT / 'validationWorkspace/project'
    if output.exists():
        raise RuntimeError('Evaluator validation already started; inspect record rather than overwrite')
    copy_project(project)
    commands = ['set +e', 'cd /project/web', 'pnpm lint > /measurement/baselineLint.log 2>&1; lintStatus=$?', 'pnpm test > /measurement/baselineTests.log 2>&1; regressionStatus=$?', 'pnpm build > /measurement/baselineBuild.log 2>&1; buildStatus=$?']
    for task in tasks():
        identifier = task['id']
        commands += [f'cp /hidden/{identifier}.test.ts tests/__studyAcceptance.test.ts', f'pnpm exec vitest run tests/__studyAcceptance.test.ts --reporter=json > /measurement/{identifier}Baseline.json 2> /measurement/{identifier}Baseline.stderr; baseline_{identifier}=$?',
                     f'cd /project; git apply /hidden/{identifier}.patch; apply_{identifier}=$?; cd /project/web', f'pnpm exec vitest run tests/__studyAcceptance.test.ts --reporter=json > /measurement/{identifier}Positive.json 2> /measurement/{identifier}Positive.stderr; positive_{identifier}=$?', 'rm tests/__studyAcceptance.test.ts']
    commands += ['printf "BASELINE_NATIVE %s %s %s\\n" "$lintStatus" "$regressionStatus" "$buildStatus"']
    for task in tasks():
        identifier = task['id']
        commands += [f'printf "SENSITIVITY {identifier} %s %s %s\\n" "$baseline_{identifier}" "$apply_{identifier}" "$positive_{identifier}"']
    result = stage(output, project, shell='; '.join(commands), timeout=900, mounts=[(INPUT / 'evaluation', '/hidden')])
    log = (output / 'events.jsonl').read_text()
    native = re.search(r'BASELINE_NATIVE (\d+) (\d+) (\d+)', log)
    sensitivity = re.findall(r'SENSITIVITY (\w+) (\d+) (\d+) (\d+)', log)
    details = {}
    for task in tasks():
        key = task['id']
        try:
            negative = read(output / (key + 'Baseline.json'))
            positive = read(output / (key + 'Positive.json'))
            details[key] = {'baselineTests': negative.get('numTotalTests'), 'baselineFailedTests': negative.get('numFailedTests'), 'positiveTests': positive.get('numTotalTests'), 'positiveSuccess': positive.get('success'),
                            'valid': negative.get('numTotalTests', 0) > 0 and negative.get('numFailedTests', 0) > 0 and positive.get('success') is True and positive.get('numTotalTests') == negative.get('numTotalTests')}
        except (OSError, ValueError):
            details[key] = {'valid': False}
    passed = bool(native and native.groups() == ('0', '0', '0') and len(sensitivity) == 6 and all(b != '0' and a == '0' and p == '0' for _, b, a, p in sensitivity) and all(v['valid'] for v in details.values()))
    write(output / 'validation.json', {'passed': passed, 'baselineNativeStatuses': native.groups() if native else None, 'sensitivity': sensitivity, 'details': details, 'stage': result})
    if not passed:
        raise RuntimeError('Evaluator validation failed; do not code until resolved and documented')

def render_pack(claims, destination, sources):
    allowed = {source['path'] for source in sources}
    if not isinstance(claims, dict) or not isinstance(claims.get('claims'), list) or not 1 <= len(claims['claims']) <= 12:
        raise ValueError('Expected 1–12 claims')
    seen = set()
    for claim in claims['claims']:
        if not all(isinstance(claim.get(key), str) and claim[key].strip() for key in ('id', 'topic', 'text')) or claim['id'] in seen:
            raise ValueError('Invalid or duplicate claim')
        if not isinstance(claim.get('sources'), list) or not claim['sources'] or any(s not in allowed for s in claim['sources']):
            raise ValueError('Invalid claim evidence')
        seen.add(claim['id'])
    if sum(len(c['text'].split()) for c in claims['claims']) > 650:
        raise ValueError('Pack exceeds 650 words')
    destination.mkdir(parents=True, exist_ok=True)
    write(destination / 'claims.json', claims)
    write(destination / 'sourceMap.json', {'snapshot': runPilot.SNAPSHOT['commit'], 'sources': sources})
    guide = '# Prepared project context\n\nRevision: `' + runPilot.SNAPSHOT['commit'] + '`. Native source/configuration is authoritative; verify relevant details before changing code.\n\n'
    for claim in claims['claims']:
        guide += f"## {claim['id']}: {claim['topic']}\n\n{claim['text']}\n\nSources: " + ', '.join('`' + s + '`' for s in claim['sources']) + '.\n\n'
    (destination / 'contextGuide.md').write_text(guide)

def prepare():
    protocol = validate_inputs()
    preflight()
    if not read(REPORT / 'evaluatorValidation/validation.json')['passed']:
        raise RuntimeError('Evaluator validation required')
    if PACK.exists():
        raise RuntimeError('Prepared pack exists; use review rather than regenerate')
    for attempt in range(1, protocol['preparationMaximumAttempts'] + 1):
        parent = REPORT / 'preparation' / f'attempt{attempt:02}'
        if (parent / 'measurement').exists():
            if (parent / 'packValidation.json').exists() and read(parent / 'packValidation.json')['valid']:
                return
            continue
        project = parent / 'sourceWorkspace'
        project.mkdir(parents=True)
        for source in protocol['preparationSources']:
            target = project / source['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(BASE / source['path'], target)
        (project / 'contextOutput').mkdir()
        prompt = '''Prepare concise additional project context from the native documentation and configuration supplied in this sparse Memos workspace. Read all supplied sources. No task descriptions, previous solutions or previous context packs are available. Do not access authentication, network sources or other projects, change source files, or delegate. Do not run application commands; dependencies/backend are not provided for preparation.
Write only contextOutput/claims.json as {"claims":[{"id":"c01","topic":"short topic","text":"one auditable factual claim or closely related instruction","sources":["relative/source/path"]}]}.
Use 1–12 claims and at most 650 words of claim text. Every claim must cite one or more supplied native source files. Cover verification commands, code routing, frontend conventions, actual toolchain requirements, generated-file rules and source authority where supported. Include exact actionable frontend unit-test invocation and the actual Vitest config location. Do not invent runtime validation, missing facts, results or task-specific advice. Preserve source authority when documentation conflicts. Return after writing valid JSON.\n'''
        prompt += 'Allowed sources:\n' + '\n'.join(s['path'] for s in protocol['preparationSources'])
        result = stage(parent / 'measurement', project, prompt)
        if result.get('providerInfrastructureFailure') or result.get('infrastructureError'):
            raise RuntimeError('Preparation infrastructure failed; record retained, investigate before further calls')
        try:
            if not result.get('resources') or result['resources']['exitCode'] != 0 or result['resources']['timedOut']:
                raise ValueError('Preparation did not finish')
            for source in protocol['preparationSources']:
                if digest(project / source['path']) != source['sha256']:
                    raise ValueError('Preparation modified native source')
            claims = read(project / 'contextOutput/claims.json')
            # Validate in a temporary destination before marking this version reviewable.
            render_pack(claims, parent / 'validatedPack', protocol['preparationSources'])
            shutil.copytree(parent / 'validatedPack', PACK)
            write(parent / 'packValidation.json', {'valid': True, 'validatedAt': now(), 'reviewRequired': True})
            create_review_packet('preparationB', claims, BASE, PACK, {'stage': str((parent / 'measurement').relative_to(ROOT)), 'purpose': 'Review prepared context before coding'})
            print(json.dumps({'preparedPack': str(PACK.relative_to(ROOT)), 'next': 'Timed human review required; no coding launched'}), flush=True)
            return
        except (ValueError, OSError, KeyError) as error:
            write(parent / 'packValidation.json', {'valid': False, 'reason': str(error)})
    raise RuntimeError('Preparation attempt limit reached; retain failures, no coding')

def create_review_packet(identifier, claims, project, target, metadata):
    sources = sorted({source for claim in claims['claims'] for source in claim['sources']})
    packet = {'id': identifier, 'claims': claims['claims'], 'sourceTexts': {source: (project / source).read_text() for source in sources},
              'target': str(target.relative_to(ROOT)), 'createdAt': now(), 'metadata': metadata,
              'coverageTopics': ['routing', 'verification', 'toolchain', 'generated-file rules', 'authority'], 'beforeHashes': {p.name: digest(p) for p in target.glob('*') if p.is_file()}}
    write(REPORT / 'humanReview' / identifier / 'packet.json', packet)

def seal_execution():
    protocol = validate_inputs()
    path = INPUT / 'executionProtocol.json'
    if path.exists():
        validate_execution()
        return
    review = REPORT / 'humanReview/preparationB/completion.json'
    if not review.exists() or not read(review).get('completed'):
        raise RuntimeError('Actual timed human preparation review is pending')
    if not read(REPORT / 'evaluatorValidation/validation.json')['passed']:
        raise RuntimeError('Evaluator validation not passed')
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in PACK.glob('*') if p.is_file()}
    write(path, {'sealedAt': now(), 'designSha256': digest(INPUT / 'designProtocol.json'), 'packHashes': hashes, 'humanReviewSha256': digest(review), 'humanReviewPath': str(review.relative_to(ROOT)), 'codingRuns': protocol['codingRuns']})

def validate_execution():
    validate_inputs()
    execution = read(INPUT / 'executionProtocol.json')
    if digest(INPUT / 'designProtocol.json') != execution['designSha256'] or digest(ROOT / execution['humanReviewPath']) != execution['humanReviewSha256']:
        raise RuntimeError('Execution seal changed')
    for path, expected in execution['packHashes'].items():
        if digest(ROOT / path) != expected:
            raise RuntimeError('Reviewed context changed: ' + path)

def run_path(item):
    return ROOT / 'experiments' / METHODS[item['method']] / 'runs/measuredStudy01' / item['task'] / f"attempt{item['attempt']:02}"

def coding():
    protocol = validate_inputs()
    seal_execution()
    preflight()
    task_map = {t['id']: t for t in tasks()}
    for item in protocol['schedule']:
        validate_execution()
        output = run_path(item)
        if (output / 'execution.json').exists():
            prior = read(output / 'execution.json')
            if prior.get('stage', {}).get('providerInfrastructureFailure'):
                raise RuntimeError('Prior provider failure requires explicit diagnostic disposition before resume')
            continue
        if output.exists():
            raise RuntimeError('Partially started attempt; never replay. Inspect ' + str(output))
        output.mkdir(parents=True)
        project = output / 'project'
        copy_project(project)
        task = task_map[item['task']]
        prompt = "Follow the repository's native AGENTS.md. Do not read authentication files, change Git history, delegate, or access external solutions.\n"
        if item['method'] == 'B':
            prompt += 'Before working, read .projectContext/contextGuide.md in full. Its source map is available for verification.\n'
        prompt += '\n' + (INPUT / task['taskFile']).read_text()
        result = stage(output / 'measurement', project, prompt, pack=PACK if item['method'] == 'B' else None)
        scope = {'snapshot': protocol['snapshot'], 'permittedProductionChanges': [task['productionFile']], 'permittedTestChangesPrefix': 'web/tests/'}
        changes = runPilot.capture_changes(project, output, scope)
        record = {'item': item, 'stage': result, 'changes': changes, 'executionProtocolSha256': digest(INPUT / 'executionProtocol.json')}
        if item['method'] == 'B':
            guide = (PACK / 'contextGuide.md').read_text().strip()
            record['fullGuideExposureObserved'] = any(guide in event.get('item', {}).get('aggregated_output', '') and event.get('item', {}).get('exit_code') == 0 for event in load_events(output / 'measurement/events.jsonl'))
        write(output / 'execution.json', record)
        if result.get('providerInfrastructureFailure') or result.get('infrastructureError'):
            raise RuntimeError('Infrastructure failure; all records preserved, further coding stopped')
    evaluate_all()
    analyze()

def load_events(path):
    result = []
    for line in path.read_text(errors='replace').splitlines():
        try:
            result.append(json.loads(line))
        except ValueError:
            pass
    return result

def evaluate_all():
    protocol = validate_inputs()
    task_map = {t['id']: t for t in tasks()}
    for item in protocol['schedule']:
        output = run_path(item)
        if not (output / 'execution.json').exists() or (output / 'evaluation.json').exists():
            continue
        record = read(output / 'execution.json')
        target = output / 'independentEvaluation'
        if target.exists():
            raise RuntimeError('Partial evaluator stage retained; inspect before resuming ' + str(target))
        eval_project = output / 'evaluationWorkspace/project'
        copy_project(eval_project, output / 'project')
        changed_tests = [name for name in record['changes']['testFilesChanged'] if re.fullmatch(r'web/tests/.*\.test\.(ts|tsx)', name) and (eval_project / name).is_file()]
        # Static suspicious-test flags are unresolved until human adjudication, never a silent pass.
        suspicious = []
        for name in record['changes']['testFilesChanged']:
            file = eval_project / name
            if not file.is_file():
                suspicious.append(name + ': deleted test/support file')
            elif re.search(r'\b(?:it|test|describe)\s*\.\s*(?:skip|only|todo)\b', file.read_text(errors='replace')):
                suspicious.append(name + ': skip/only/todo registration')
            if (BASE / name).exists():
                diff = subprocess.run(['git', 'diff', '--no-index', str(BASE / name), str(file)], capture_output=True, text=True).stdout
                if any(line.startswith('-') and not line.startswith('---') and ('expect(' in line or re.search(r'\b(?:it|test)\(', line)) for line in diff.splitlines()):
                    suspicious.append(name + ': removed or rewritten upstream test assertion')
        candidate = shlex.join(['pnpm', 'exec', 'vitest', 'run', *[str(Path(p).relative_to('web')) for p in changed_tests]]) if changed_tests else 'false'
        commands = ['set +e', 'cd /project/web', 'pnpm lint > /measurement/lint.log 2>&1; lintStatus=$?', candidate + ' > /measurement/candidateTests.log 2>&1; candidateStatus=$?',
                    'cp /hiddenAcceptance tests/__studyAcceptance.test.ts', 'pnpm exec vitest run tests/__studyAcceptance.test.ts --reporter=json > /measurement/acceptance.json 2> /measurement/acceptance.stderr; acceptanceStatus=$?',
                    'rm -rf /project/web/tests', 'cp -a /baselineTests /project/web/tests; restoreStatus=$?', 'pnpm test > /measurement/regression.log 2>&1; regressionStatus=$?', 'pnpm build > /measurement/build.log 2>&1; buildStatus=$?',
                    'printf "GATES %s %s %s %s %s %s\\n" "$lintStatus" "$candidateStatus" "$acceptanceStatus" "$restoreStatus" "$regressionStatus" "$buildStatus"']
        result = stage(target, eval_project, shell='; '.join(commands), timeout=protocol['evaluationWallSeconds'], mounts=[(INPUT / task_map[item['task']]['acceptanceFile'], '/hiddenAcceptance'), (BASE / 'web/tests', '/baselineTests')])
        log = (target / 'events.jsonl').read_text()
        match = re.search(r'GATES (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)', log)
        statuses = dict(zip(['lint','candidateTests','acceptance','restorePristineTests','regression','build'], map(int, match.groups()))) if match else None
        resources = record['stage'].get('resources') or {}
        artifact_ok = all((output / 'project' / p).is_file() and digest(output / 'project' / p) == value if value is not None else not (output / 'project' / p).exists() for p, value in record['changes']['fileHashes'].items())
        fully_passed = bool(resources.get('exitCode') == 0 and not resources.get('timedOut') and record['changes']['permitted'] and changed_tests and statuses and all(v == 0 for v in statuses.values()) and artifact_ok)
        write(output / 'evaluation.json', {'gates': statuses, 'automatedGatesPass': fully_passed, 'verifiedCompletion': fully_passed if not suspicious and statuses is not None else None,
              'humanAdjudicationRequired': suspicious, 'evaluationUnresolved': statuses is None, 'candidateArtifactsUnchanged': artifact_ok,
              'bContextExposureObserved': record.get('fullGuideExposureObserved'), 'evaluationStage': result})
        shutil.rmtree(eval_project.parent)

def analyze():
    protocol = validate_inputs()
    rows = []
    for item in protocol['schedule']:
        output = run_path(item)
        if (output / 'execution.json').exists():
            rows.append({'item': item, 'execution': read(output / 'execution.json'), 'evaluation': read(output / 'evaluation.json') if (output / 'evaluation.json').exists() else None})
    summary = {'generatedAt': now(), 'plannedCodingRuns': 24, 'recordedCodingRuns': len(rows), 'rows': rows, 'perTask': [], 'stageCosts': {}, 'interpretation': 'Exploratory, curated six-task comparison. No universal or company-level superiority conclusion.'}
    for task in tasks():
        values = {}
        for method in METHODS:
            selected = [r for r in rows if r['item']['task'] == task['id'] and r['item']['method'] == method]
            verdicts = [r['evaluation'].get('verifiedCompletion') if r['evaluation'] else None for r in selected]
            values[method] = sum(v is True for v in verdicts) / 2 if len(verdicts) == 2 and all(v is not None for v in verdicts) else None
        summary['perTask'].append({'task': task['id'], **values, 'differenceBminusA': values['B'] - values['A'] if all(v is not None for v in values.values()) else None})
    differences = [r['differenceBminusA'] for r in summary['perTask']]
    if all(value is not None for value in differences):
        observed = sum(differences) / 6
        permutations = [sum(s * d for s, d in zip(signs, differences)) / 6 for signs in itertools.product([-1,1], repeat=6)]
        summary['exploratoryPrimaryContrast'] = {'meanCompletionDifferenceBminusA': observed, 'twoSidedExactSignFlipP': sum(abs(v) >= abs(observed) - 1e-12 for v in permutations) / 64, 'taskClusters': 6, 'labelSwaps': 64, 'assumption': 'Within-pair label exchangeability; convenience sample does not support population-wide claims'}
    for method in METHODS:
        selected = [r for r in rows if r['item']['method'] == method]
        def total(extract):
            values = [extract(r) for r in selected]
            return sum(values) if values and all(type(v) in (float, int) for v in values) else None
        successes = sum(r['evaluation'] is not None and r['evaluation'].get('verifiedCompletion') is True for r in selected)
        tokens = total(lambda r: r['execution']['stage'].get('usage', {}).get('totalTokens'))
        summary['stageCosts'][method] = {'codingAttempts': len(selected), 'verifiedCompletions': successes, 'codingTotalTokens': tokens,
            'codingWallSeconds': total(lambda r: r['execution']['stage'].get('hostWallSeconds')),
            'codingLocalCpuSeconds': total(lambda r: (r['execution']['stage'].get('resources') or {}).get('cpuUsageSeconds')),
            'tokensPerVerifiedCompletion': tokens / successes if tokens is not None and successes else None,
            'actualMoney': None, 'note': 'Coding only; preparation, human review, maintenance and evaluation separately itemized below, including failed attempts.'}
    summary['otherStages'] = {str(p.parent.relative_to(ROOT)): read(p) for p in REPORT.rglob('stage.json')}
    summary['humanReviews'] = {str(p.parent.relative_to(ROOT)): read(p) for p in (REPORT / 'humanReview').rglob('completion.json')} if (REPORT / 'humanReview').exists() else {}
    summary['remaining'] = {'codingRuns': 24 - len(rows), 'unevaluatedOrUnresolved': sum(not r['evaluation'] or r['evaluation'].get('verifiedCompletion') is None for r in rows), 'maintenance': 'See maintenance records; two controlled episodes and timed human reviews are required before whole-workflow conclusion'}
    write(REPORT / 'summary.json', summary)
    table = '| Task | A completion fraction | B completion fraction |\n|---|---:|---:|\n' + '\n'.join(f"| {r['task']} | {r['A'] if r['A'] is not None else 'pending'} | {r['B'] if r['B'] is not None else 'pending'} |" for r in summary['perTask'])
    (REPORT / 'comparison.md').write_text('# Measured study status\n\nRecorded coding runs: ' + str(len(rows)) + '/24. Unknown or pending observations are not zero.\n\n' + table + '\n\n' + summary['interpretation'] + '\n\nFull records: [summary.json](summary.json). Costs, failures, missing measurements and human intervals remain separately visible. A final ranking is withheld until gates and required maintenance/review observations are complete.\n')
    print(json.dumps({'recordedCodingRuns': len(rows), 'report': 'reports/measuredStudy01/comparison.md'}), flush=True)

def status():
    print(json.dumps({'designFrozen': (INPUT / 'designProtocol.json').exists(), 'evaluatorsValidated': read(REPORT / 'evaluatorValidation/validation.json')['passed'] if (REPORT / 'evaluatorValidation/validation.json').exists() else False, 'contextPrepared': PACK.exists(), 'humanPreparationReviewComplete': (REPORT / 'humanReview/preparationB/completion.json').exists(), 'executionSealed': (INPUT / 'executionProtocol.json').exists(), 'codingRunsRecorded': sum((run_path(item) / 'execution.json').exists() for item in read(INPUT / 'designProtocol.json')['schedule']) if (INPUT / 'designProtocol.json').exists() else 0}, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['freeze', 'validate', 'prepare', 'seal', 'run', 'evaluate', 'analyze', 'status'])
    action = parser.parse_args().action
    {'freeze': freeze, 'validate': validate_evaluators, 'prepare': prepare, 'seal': seal_execution, 'run': coding, 'evaluate': evaluate_all, 'analyze': analyze, 'status': status}[action]()
