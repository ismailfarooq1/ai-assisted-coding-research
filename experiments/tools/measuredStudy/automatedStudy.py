#!/usr/bin/env python3
"""Prospective user-directed replacement of unfinished human review by metered AI review."""
import argparse
import concurrent.futures
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys

import studyRunner as s

AMENDMENT = s.INPUT / 'automatedReviewAmendment.json'
REVIEW = s.REPORT / 'automatedReview/preparationB'
ORIGINAL_VALIDATE = s.validate_execution

def amendment():
    if AMENDMENT.exists():
        validate_amendment()
        return
    protocol = s.validate_inputs()
    if (s.INPUT / 'executionProtocol.json').exists() or any((s.run_path(item) / 'execution.json').exists() for item in protocol['schedule']):
        raise RuntimeError('Amendment must precede coding')
    s.write(AMENDMENT, {
        'recordedAt':s.now(), 'authority':'User: Decide for yourself',
        'originalDesignSha256':s.digest(s.INPUT / 'designProtocol.json'),
        'change':'Replace unfinished participant factual review with metered, source-grounded automated review for preparation and maintenance. Coordinator resolves review findings; no human completion is fabricated.',
        'preserved':'Frozen task set, acceptance controls, model/configuration, common limits, schedule, all 24 planned coding attempts and prior raw records.',
        'humanEffort':'Retain observed partial participant intervals separately; completed expert human review and associated human-effort comparison remain unavailable.',
        'reviewLimit':'One fresh automated review per preparation or maintenance packet; unresolved facts stop approval, without silently retrying or inventing evidence.',
        'evaluationConcurrency':2, 'evaluationNote':'Only offline independent evaluation may overlap after all coding attempts are sealed. Coding stays sequential. Evaluation time is separate research overhead.',
        'inputHashes':{str(Path(__file__).resolve().relative_to(s.ROOT)):s.digest(Path(__file__).resolve())},
        'inference':'Exploratory automated workflow comparison with partial human participation; not an experiment establishing human maintenance savings.',
    })

def validate_amendment():
    s.validate_inputs()
    data = s.read(AMENDMENT)
    if s.digest(s.INPUT / 'designProtocol.json') != data['originalDesignSha256']:
        raise RuntimeError('Original design changed')
    for name, expected in data['inputHashes'].items():
        if s.digest(s.ROOT / name) != expected:
            raise RuntimeError('Amendment implementation changed: ' + name)
    return data

def review_prompt(maintenance=False):
    return '''Review the supplied project-context claims against the supplied native source files. This is automated factual review, not a human review. Read contextInput/packet.json, then examine every cited source. No development tasks, test oracles, previous solutions or other workflows are available. Do not access authentication, external sources or delegate. Do not change supplied sources or run application suites. Write only contextOutput/review.json.
Output JSON: {"judgments":[{"id":"original claim id","decision":"supported|corrected|remove|unresolved","text":"complete final claim text","reason":"specific source-based reasoning","evidence":[{"path":"supplied source path","excerpt":"short exact contiguous source excerpt"}]}],"coverage":{"routing":"yes|no|unresolved","verification":"yes|no|unresolved","toolchain":"yes|no|unresolved","generated-file rules":"yes|no|unresolved","authority":"yes|no|unresolved"},"notes":"limitations"}.
Review every original claim exactly once. Supported means every factual assertion is backed by native source. Correct only factual errors/ambiguity; do not add new claims, task-specific guidance or optimize the context for undisclosed tasks. For corrected claims use at most 650 final claim-text words total and preserve the original source citations. Cite exact source excerpts as evidence. Mark unsupported content remove, and uncertainty unresolved. Do not claim any backend/runtime execution. A prose/source hash change by itself is not a stale factual assertion.
''' + ('''This is a maintenance review after a controlled configuration change. Also provide "beforeJudgments":{"original before-claim id":"supported|stale|unresolved"}, "requiredFacts":{"each fact key from packet metadata":"yes|no|unresolved"}, and "documentEdits":{"AGENTS.md":"full corrected document text"} ONLY if factual corrections to that supplied document are needed. Preserve unrelated text. A before-item is stale if any actionable instruction conflicts with the changed source; items can contain multiple assertions and are not directly comparable atomic claim counts across workflows. Check final guidance coverage against actual current configuration, and distinguish missing facts from false facts.\n''' if maintenance else '')

def run_review(identifier, packet, source_project, target, source_map, maintenance=False):
    parent = s.REPORT / 'automatedReview' / identifier
    finalized = parent / 'review.json'
    if finalized.exists():
        return s.read(finalized)
    if (parent / 'measurement').exists():
        raise RuntimeError('Review already started; inspect rather than replay ' + identifier)
    project = parent / 'project'
    project.mkdir(parents=True)
    for source in source_map:
        name = source['path']
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_project / name, path)
    (project / 'contextInput').mkdir()
    (project / 'contextOutput').mkdir()
    s.write(project / 'contextInput/packet.json', packet)
    before_sources = {source['path']:s.digest(project / source['path']) for source in source_map}
    result = s.stage(parent / 'measurement', project, review_prompt(maintenance))
    resources = result.get('resources') or {}
    if result.get('infrastructureError') or result.get('providerInfrastructureFailure') or resources.get('exitCode') != 0 or resources.get('timedOut'):
        raise RuntimeError('Automated review failed; retain records, no approval')
    if any(s.digest(project / name) != sha for name, sha in before_sources.items()):
        raise RuntimeError('Reviewer altered supplied evidence')
    review = s.read(project / 'contextOutput/review.json')
    originals = {claim['id']:claim for claim in packet['claims']}
    judgments = review.get('judgments',[])
    if len(judgments) != len(originals) or {j.get('id') for j in judgments} != set(originals):
        raise RuntimeError('Incomplete review coverage')
    allowed = set(before_sources)
    for judgment in judgments:
        if judgment.get('decision') not in ('supported','corrected','remove'):
            raise RuntimeError('Unresolved review finding; coordinator must inspect')
        if not isinstance(judgment.get('text'),str) or not judgment.get('reason') or not judgment.get('evidence'):
            raise RuntimeError('Review missing reasoning/evidence')
        for evidence in judgment['evidence']:
            if evidence.get('path') not in allowed or not evidence.get('excerpt') or evidence['excerpt'] not in (project / evidence['path']).read_text():
                raise RuntimeError('Review evidence does not match supplied source')
    if any(review.get('coverage',{}).get(topic) not in ('yes','no') for topic in ('routing','verification','toolchain','generated-file rules','authority')):
        raise RuntimeError('Unresolved review coverage')
    before_hashes = {str(p.relative_to(target)):s.digest(p) for p in target.rglob('*') if p.is_file() and '.git' not in p.parts and 'node_modules' not in p.parts}
    if maintenance:
        for name, text in review.get('documentEdits',{}).items():
            if name != 'AGENTS.md' or not isinstance(text,str):
                raise RuntimeError('Review requested out-of-scope document edit')
            (target / name).write_text(text)
        if set(review.get('beforeJudgments',{})) != {c['id'] for c in packet['beforeClaims']} or any(v not in ('supported','stale','unresolved') for v in review['beforeJudgments'].values()):
            raise RuntimeError('Missing before-state judgments')
        if set(review.get('requiredFacts',{})) != set(packet['metadata']['facts']) or any(v not in ('yes','no','unresolved') for v in review['requiredFacts'].values()):
            raise RuntimeError('Missing required-fact judgments')
    pack_target = target / 'contextPack' if maintenance and packet['metadata']['method'] == 'B' else target
    if not maintenance or packet['metadata']['method'] == 'B':
        final_claims = {'claims':[{**originals[j['id']], 'text':j['text']} for j in judgments if j['decision'] != 'remove']}
        s.render_pack(final_claims, pack_target, s.read(pack_target / 'sourceMap.json')['sources'])
    review.update({'completed':True,'reviewType':'automated','completedAt':s.now(),'stage':result,'humanActiveSeconds':None,'beforeHashes':before_hashes,
                   'afterHashes':{str(p.relative_to(target)):s.digest(p) for p in target.rglob('*') if p.is_file() and '.git' not in p.parts and 'node_modules' not in p.parts},
                   'limitation':'Same model family as author/coder, fresh conversation; source-grounded AI judgments are not independent expert human judgments.'})
    s.write(finalized,review)
    return review

def preparation_review():
    validate_amendment()
    s.preflight()
    packet = s.read(s.REPORT / 'humanReview/preparationB/packet.json')
    return run_review('preparationB',packet,s.BASE,s.PACK,s.read(s.PACK / 'sourceMap.json')['sources'])

def seal():
    data = validate_amendment()
    path = s.INPUT / 'executionProtocol.json'
    if path.exists():
        validate_execution()
        return
    review = REVIEW / 'review.json'
    if not review.exists() or s.read(review).get('reviewType') != 'automated' or not s.read(review).get('completed'):
        raise RuntimeError('Automated review not completed')
    s.write(path, {'sealedAt':s.now(),'designSha256':s.digest(s.INPUT / 'designProtocol.json'), 'amendmentSha256':s.digest(AMENDMENT),
                  'packHashes':{str(p.relative_to(s.ROOT)):s.digest(p) for p in s.PACK.glob('*') if p.is_file()},
                  'reviewType':'automated', 'reviewPath':str(review.relative_to(s.ROOT)), 'reviewSha256':s.digest(review), 'codingRuns':24,
                  'completedHumanReview':False,'humanEffortComparisonAvailable':False})

def validate_execution():
    validate_amendment()
    execution = s.read(s.INPUT / 'executionProtocol.json')
    if s.digest(AMENDMENT) != execution['amendmentSha256'] or s.digest(s.INPUT / 'designProtocol.json') != execution['designSha256'] or s.digest(s.ROOT / execution['reviewPath']) != execution['reviewSha256']:
        raise RuntimeError('Execution seal changed')
    for name, expected in execution['packHashes'].items():
        if s.digest(s.ROOT / name) != expected:
            raise RuntimeError('Reviewed context changed: ' + name)

def evaluate_one(item):
    validate_execution()
    original = s.validate_inputs
    s.validate_inputs = lambda: {**original(), 'schedule':[item]}
    s.evaluate_all()
    return item

def evaluations():
    validate_execution()
    items = s.validate_inputs()['schedule']
    # Separate OS processes, no LLM calls or cross-candidate mounts. Limits remain 2 CPU / 4 GB each.
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(evaluate_one,item) for item in items]
        for future in concurrent.futures.as_completed(futures):
            print(json.dumps({'evaluationFinished':future.result()}),flush=True)

def maintenance():
    import maintenanceRunner
    maintenanceRunner.study.validate_execution = validate_execution
    maintenanceRunner.run()
    for identifier in ('renameLintScriptA','renameLintScriptB','renameVitestConfigB','renameVitestConfigA'):
        packet = s.read(s.REPORT / 'humanReview' / identifier / 'packet.json')
        target = s.ROOT / packet['target']
        sources = deepcopy(s.read(s.PACK / 'sourceMap.json')['sources'])
        if packet['metadata']['episode'] == 'renameVitestConfig':
            for source in sources:
                if source['path'] == 'web/vitest.config.mts':
                    source['path'] = 'web/vitest.project.config.mts'
        for source in sources:
            source['sha256'] = s.digest(target / source['path'])
        run_review(identifier,packet,target,target,sources,maintenance=True)
    report()

def report():
    s.analyze()
    path = s.REPORT / 'summary.json'
    data = s.read(path)
    data['reviewMode'] = 'automated, user-directed amendment before coding'
    data['humanEffortComparisonAvailable'] = False
    timer = s.REPORT / 'humanReview/preparationB/timerState.json'
    data['partialHumanParticipation'] = {'record':s.read(timer) if timer.exists() else None, 'completed':False, 'note':'Retained partial observation; not an expert-review completion or total adoption effort'}
    data['automatedReviews'] = {str(p.parent.relative_to(s.ROOT)):s.read(p) for p in (s.REPORT / 'automatedReview').rglob('review.json')}
    data['remaining']['maintenance'] = 'Automated maintenance and factual review; human labor comparison unavailable'
    s.write(path,data)
    table = '| Metric | A | B |\n|---|---:|---:|\n'
    for label,key in [('Recorded attempts','codingAttempts'),('Verified completions','verifiedCompletions'),('Coding input + output tokens','codingTotalTokens'),('Coding wall seconds','codingWallSeconds'),('Coding local CPU seconds','codingLocalCpuSeconds')]:
        table += '| ' + label + ' | ' + ' | '.join(str(data['stageCosts'][m][key]) for m in ('A','B')) + ' |\n'
    text = '# Measured A/B study\n\n' + f"Recorded coding runs: {data['recordedCodingRuns']}/24.\n\n" + table
    text += '\nReview was changed prospectively to automated source checking at the user\u2019s instruction. The partial human session is retained separately; no completed human review, human labor saving or monetary saving is claimed. Preparation, automated review, maintenance and evaluation are separate from coding costs in [summary.json](summary.json).\n\n'
    text += 'Primary completion requires acceptance, candidate-authored test validation, pristine regressions, lint, build and permitted edits. Failed attempts remain in denominators; unresolved evaluations are not passes. Six curated frontend tasks support exploratory conclusions within this snapshot, not general superiority or equivalence.\n'
    if 'exploratoryPrimaryContrast' in data:
        text += '\nExploratory primary contrast: `' + json.dumps(data['exploratoryPrimaryContrast']) + '`.\n'
    (s.REPORT / 'comparison.md').write_text(text)

def run():
    validate_execution()
    s.seal_execution = seal
    s.validate_execution = validate_execution
    original_evaluate = s.evaluate_all
    # Coding remains in the frozen original driver. Defer its evaluator until every candidate is sealed.
    s.evaluate_all = lambda: None
    s.coding()
    s.evaluate_all = original_evaluate
    evaluations()
    maintenance()
    report()

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['amend','review','seal','run','evaluate','maintain','report'])
    action=parser.parse_args().action
    {'amend':amendment,'review':preparation_review,'seal':seal,'run':run,'evaluate':evaluations,'maintain':maintenance,'report':report}[action]()
