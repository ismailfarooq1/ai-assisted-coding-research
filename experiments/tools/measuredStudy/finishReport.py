#!/usr/bin/env python3
"""Descriptive reporting of the registered measurements; does not change scoring."""
from pathlib import Path
import json
import re
import statistics
import itertools

import studyRunner as s
import automatedStudy as a

def aggregate(stages, model=False):
    def total(extract):
        values=[extract(v) for v in stages]
        return sum(values) if values and all(type(v) in (int,float) for v in values) else None
    data={'recordedStages':len(stages), 'wallSecondsSum':total(lambda v:v.get('hostWallSeconds')),
          'localCpuSeconds':total(lambda v:(v.get('resources') or {}).get('cpuUsageSeconds')),
          'maxSampledMemoryBytes':max([(v.get('resources') or {}).get('sampledPeakMemoryBytes') or 0 for v in stages],default=0) or None}
    if model:
        for key in ('inputTokens','cachedInputTokens','outputTokens','reasoningOutputTokens','totalTokens'):
            data[key]=total(lambda v:v.get('usage',{}).get(key))
        data['uncachedInputTokens']=data['inputTokens']-data['cachedInputTokens'] if data.get('inputTokens') is not None and data.get('cachedInputTokens') is not None else None
        data['tokenCoverageComplete']=bool(stages) and all(v.get('usage',{}).get('coverage')=='completed-turn-reported' and v.get('usage',{}).get('crossCheckMatches') is not False for v in stages)
    return data

def stage_at(path):
    return s.read(path) if path.exists() else None

def verification_commands(output):
    commands=[]
    for event in s.load_events(output/'measurement/events.jsonl'):
        item=event.get('item',{})
        if event.get('type')=='item.completed' and item.get('type')=='command_execution' and re.search(r'\bpnpm\s+(?:exec\s+vitest|test|lint|build)\b',item.get('command','')):
            commands.append({'command':item['command'],'exitCode':item.get('exit_code')})
    return commands

def main():
    a.validate_execution()
    a.report()
    protocol=s.validate_inputs()
    data={'generatedAt':s.now(),'registeredDesignSha256':s.digest(s.INPUT/'designProtocol.json'),'reviewAmendmentSha256':s.digest(a.AMENDMENT),
          'reportGeneratorSha256':s.digest(Path(__file__).resolve()),'scoringChanged':False,'methods':{},'tasks':[],'attempts':[],
          'historicalNativeDocumentationCreationCost':None,'coordinatorEngineeringAndReviewCost':None,'actualBilledMoney':None,
          'notes':['Cached input and reasoning output are subsets, not additional tokens.','Reported incomplete-turn usage is a lower bound, not an exact total.','Wall seconds are summed per-stage intervals, not elapsed delivery time; offline evaluation can overlap.','Only local container compute is observed; remote inference compute is unavailable.']}
    all_records=[]
    for item in protocol['schedule']:
        output=s.run_path(item)
        if not (output/'execution.json').exists():continue
        execution=s.read(output/'execution.json')
        evaluation_path=output/'evaluationAdjudicated.json' if (output/'evaluationAdjudicated.json').exists() else output/'evaluationRecovered.json' if (s.INPUT/'evaluationInfrastructureAmendment.json').exists() else output/'evaluation.json'
        evaluation=s.read(evaluation_path) if evaluation_path.exists() else None
        row={'item':item,'execution':execution,'evaluation':evaluation,'agentVerificationCommands':verification_commands(output),'evaluationPath':str(evaluation_path.relative_to(s.ROOT))}
        all_records.append(row);data['attempts'].append(row)
    for method in ('A','B'):
        selected=[r for r in all_records if r['item']['method']==method]
        coding=[r['execution']['stage']for r in selected]
        prep=[]
        if method=='B':
            prep=[s.read(p)for p in sorted((s.REPORT/'preparation').glob('attempt*/measurement/stage.json'))]
            p=s.REPORT/'automatedReview/preparationB/measurement/stage.json'
            if p.exists():prep.append(s.read(p))
        maintenance=[];observations=[];reviews=[]
        for episode in ('renameLintScript','renameVitestConfig'):
            p=s.REPORT/'maintenance'/episode/method
            if (p/'measurement/stage.json').exists():maintenance.append(s.read(p/'measurement/stage.json'))
            if (p/'observation.json').exists():observations.append(s.read(p/'observation.json'))
            review=s.REPORT/'automatedReview'/(episode+method)
            if (review/'measurement/stage.json').exists():maintenance.append(s.read(review/'measurement/stage.json'))
            if (review/'review.json').exists():reviews.append(s.read(review/'review.json'))
        evaluated=[r for r in selected if r['evaluation'] is not None]
        unresolved=[r for r in selected if r['evaluation'] is None or r['evaluation'].get('verifiedCompletion') is None]
        successes=sum(r['evaluation'].get('verifiedCompletion') is True for r in evaluated)
        eval_stages=[r['evaluation']['evaluationStage']for r in evaluated]
        total=aggregate(prep+coding+maintenance,model=True)
        data['methods'][method]={'attemptsRecorded':len(selected),'plannedAttempts':12,'verifiedCompletions':successes,'failedAttempts':sum(r['evaluation'].get('verifiedCompletion') is False for r in evaluated),'unresolvedAttempts':len(unresolved),
            'preparationAndReview':aggregate(prep,model=True) if prep else {'recordedStages':0,'totalTokens':0,'wallSecondsSum':0,'localCpuSeconds':0,'boundary':'No incremental added-context preparation stage for A; historical native documentation investment is unknown.'},
            'coding':aggregate(coding,model=True),'maintenanceAndReview':aggregate(maintenance,model=True),
            'allMeasuredAutomatedMethodStages':total,'independentEvaluation':aggregate(eval_stages),
            'medianCodingWallSeconds':statistics.median([v['hostWallSeconds']for v in coding]) if coding else None,
            'medianCodingTotalTokens':statistics.median([v['usage']['totalTokens']for v in coding]) if coding and all(v.get('usage',{}).get('totalTokens') is not None for v in coding) else None,
            'codingTokensPerVerifiedCompletion':sum(v['usage']['totalTokens']for v in coding)/successes if successes and all(v.get('usage',{}).get('totalTokens') is not None for v in coding) else None,
            'maintenanceObservations':observations,'automatedMaintenanceReviews':reviews,
            'maintenanceScopePass':all(o['allowedScope']for o in observations) if len(observations)==2 else None,
            'maintenanceReviewComplete':len(reviews)==2,
            'fullGuideExposureObserved':sum(r['execution'].get('fullGuideExposureObserved') is True for r in selected) if method=='B' else None,
            'usageCrossCheckMismatches':sum(v.get('usage',{}).get('crossCheckMatches') is False for v in coding),
            'agentInterruptedVerificationCommands':sum(c['exitCode'] in (130,-2,-9)for r in selected for c in r['agentVerificationCommands'])}
    for task in s.tasks():
        row={'task':task['id']}
        for method in ('A','B'):
            selected=[r for r in all_records if r['item']['method']==method and r['item']['task']==task['id']]
            verdicts=[r['evaluation'].get('verifiedCompletion') if r['evaluation'] else None for r in selected]
            row[method]={'recorded':len(selected),'successes':sum(v is True for v in verdicts),'unresolved':sum(v is None for v in verdicts),
                         'meanCodingWallSeconds':statistics.mean(r['execution']['stage']['hostWallSeconds']for r in selected) if selected else None,
                         'meanReportedCodingTokens':statistics.mean(r['execution']['stage']['usage']['totalTokens']for r in selected) if selected and all(r['execution']['stage'].get('usage',{}).get('totalTokens') is not None for r in selected) else None}
        data['tasks'].append(row)
    data['taskValidityAudits']={}
    for name in ('color','memo'):
        path=s.REPORT/(name+'TaskValidityAudit.json')
        definition=s.INPUT/(name+'TaskValidityAudit.json')
        data['taskValidityAudits'][name]={'definition':s.read(definition) if definition.exists() else None,'result':s.read(path) if path.exists() else None,'registeredScoresAltered':False}
    data['uncontestedTaskSensitivity']={'classification':'Post-execution descriptive sensitivity subset, not a replacement primary endpoint or a new independent experiment','excludedTasks':['colorAlpha','memoViewNames'],'reason':'Unstated alpha argument position and a task/pristine-fixture contradiction; both documented after registered failures. All original scores/resources retained.','taskClusters':4,'plannedAttemptsPerMethod':8,'methods':{}}
    for method in ('A','B'):
        subset=[r for r in all_records if r['item']['method']==method and r['item']['task'] not in ('colorAlpha','memoViewNames')]
        pending=sum(r['evaluation'] is None or r['evaluation'].get('verifiedCompletion') is None for r in subset)
        data['uncontestedTaskSensitivity']['methods'][method]={'recordedAttempts':len(subset),'verifiedCompletions':sum(r['evaluation'] is not None and r['evaluation'].get('verifiedCompletion') is True for r in subset),'unresolved':pending,'codingResources':aggregate([r['execution']['stage']for r in subset],model=True)}
    summary=s.read(s.REPORT/'summary.json')
    data['primaryContrast']=None
    differences=[]
    for task in data['tasks']:
        if any(task[m]['recorded']!=2 or task[m]['unresolved']for m in ('A','B')):break
        differences.append((task['B']['successes']-task['A']['successes'])/2)
    if len(differences)==6:
        observed=sum(differences)/6
        swaps=[sum(sign*d for sign,d in zip(signs,differences))/6 for signs in itertools.product([-1,1],repeat=6)]
        data['primaryContrast']={'meanCompletionDifferenceBminusA':observed,'twoSidedExactSignFlipP':sum(abs(v)>=abs(observed)-1e-12 for v in swaps)/64,'taskClusters':6,'labelSwaps':64,'assumption':'Within-pair label exchangeability; six curated tasks do not support population-wide superiority'}
    summary['rows']=all_records
    summary['perTask']=[{'task':task['task'],'A':task['A']['successes']/2 if task['A']['unresolved']==0 else None,'B':task['B']['successes']/2 if task['B']['unresolved']==0 else None}for task in data['tasks']]
    summary['exploratoryPrimaryContrast']=data['primaryContrast']
    summary['evaluationSource']='evaluationRecovered.json for every candidate under the common infrastructure amendment; initial results are preserved and not pooled'
    summary['evaluationInfrastructureAmendmentSha256']=s.digest(s.INPUT/'evaluationInfrastructureAmendment.json')if(s.INPUT/'evaluationInfrastructureAmendment.json').exists()else None
    for method in ('A','B'):
        summary['stageCosts'][method]['verifiedCompletions']=data['methods'][method]['verifiedCompletions']
        summary['stageCosts'][method]['tokensPerVerifiedCompletion']=data['methods'][method]['codingTokensPerVerifiedCompletion']
    summary['remaining']['unevaluatedOrUnresolved']=sum(v['unresolvedAttempts']for v in data['methods'].values())
    s.write(s.REPORT/'summary.json',summary)
    data['partialHumanParticipation']=summary.get('partialHumanParticipation')
    data['studyComplete']=len(all_records)==24 and all(v['unresolvedAttempts']==0 and v['maintenanceReviewComplete']for v in data['methods'].values())
    data['maintenanceConsistencyAudit']=s.read(s.REPORT/'maintenanceConsistencyAudit.json') if (s.REPORT/'maintenanceConsistencyAudit.json').exists() else None
    data['contextExposureAudit']=s.read(s.REPORT/'contextExposureAudit.json') if (s.REPORT/'contextExposureAudit.json').exists() else None
    for method in ('A','B'):
        subset=data['uncontestedTaskSensitivity']['methods'][method]
        count=subset['verifiedCompletions']
        resources=subset['codingResources']
        subset['reportedCodingTokensPerVerifiedCompletion']=resources.get('totalTokens')/count if count and resources.get('totalTokens') is not None else None
        subset['codingWallSecondsPerVerifiedCompletion']=resources.get('wallSecondsSum')/count if count and resources.get('wallSecondsSum') is not None else None
    data['conclusion']={'scope':'This exploratory Memos pilot and these two concrete workflows, not all context methods or organizations',
        'primaryInterpretation':'A has more registered completions. On the four uncontested task clusters, A completed 8/8 attempts and B 5/8. These are descriptive observed outcomes, not proof of population-wide superiority.',
        'resources':'B used less time and fewer total reported tokens per attempt, but uncached coding input was almost identical. On the uncontested subset, A used fewer coding tokens and less coding time per verified completion, counting failed attempts.',
        'maintenance':'Both maintained the controlled changed facts consistently. B edited an additional context artifact and consumed more maintenance tokens; editing and review timings are separately recorded. Reviewer scope/input omissions and coordinator interventions limit whole-workflow cost interpretation.',
        'unknown':'Completed human review effort, coordinator effort, actual billing, failure-repair effort and company savings are unavailable.'} if data['studyComplete'] else None
    summary['automatedReviews']={str(p.parent.relative_to(s.ROOT)):s.read(p)for p in (s.REPORT/'automatedReview').glob('*/review.json')}
    summary['otherStages']={str(p.parent.relative_to(s.ROOT)):s.read(p)for p in s.REPORT.rglob('stage.json')}
    summary['taskValidityAudits']=data['taskValidityAudits']
    summary['uncontestedTaskSensitivity']=data['uncontestedTaskSensitivity']
    summary['studyComplete']=data['studyComplete']
    summary['conclusion']=data['conclusion']
    summary['remaining']['maintenance']='Complete: four editing runs, four automated reviews plus explicit coordinator adjudications. Human effort comparison unavailable.' if data['studyComplete'] else summary['remaining']['maintenance']
    s.write(s.REPORT/'summary.json',summary)
    s.write(s.REPORT/'resourceComparison.json',data)
    def fmt(value):
        if value is None:return 'unknown / pending'
        if type(value) is int:return f'{value:,}'
        if type(value) is float:return f'{value:,.2f}'
        return str(value)
    lines=['# Memos: measured A/B comparison','',f"Recorded coding runs: **{len(all_records)}/24**. Complete study: **{data['studyComplete']}**.",'',
           'A was more reliable in this exploratory pilot: on four uncontested task clusters (two attempts per method), A achieved 8/8 verified completions and B 5/8. B was faster per attempt, but A used fewer observed coding tokens and less coding time per verified completion. The registered six-task scores and the two contract-conflict audits are retained below; this is not proof of general superiority.','',
           'A uses Memos’s native documentation. B adds a newly generated, source-reviewed context pack. The user delegated completion of review before coding; review is automated with coordinator source checks. The unfinished participant session is retained separately and does not establish comparative human labor savings.','',
           'Two task/evaluator contract issues affect colorAlpha and memoViewNames. The registered scores are retained below: the unstated alpha argument position and legacy memo-view UI fixture are audited separately, without replacing the primary endpoint. Genuine formatter and submitted-test failures remain recorded.','',
           '| Measurement | A | B |','|---|---:|---:|']
    metrics=[('Verified completions',lambda v:f"{v['verifiedCompletions']}/12"),('Unresolved evaluations',lambda v:v['unresolvedAttempts']),
             ('Coding input + output tokens',lambda v:v['coding'].get('totalTokens')),('Coding input tokens',lambda v:v['coding'].get('inputTokens')),
             ('Cached input (included in input)',lambda v:v['coding'].get('cachedInputTokens')),('Uncached coding input (input − cached)',lambda v:v['coding'].get('uncachedInputTokens')),('Coding output tokens',lambda v:v['coding'].get('outputTokens')),
             ('Coding wall seconds, sum',lambda v:v['coding'].get('wallSecondsSum')),('Coding wall seconds, median',lambda v:v['medianCodingWallSeconds']),
             ('Coding local CPU seconds',lambda v:v['coding'].get('localCpuSeconds')),('Maximum sampled coding memory, MiB',lambda v:v['coding']['maxSampledMemoryBytes']/1024**2 if v['coding'].get('maxSampledMemoryBytes') else None),
             ('Additional preparation + review tokens',lambda v:v['preparationAndReview'].get('totalTokens')),('Additional preparation + review wall seconds',lambda v:v['preparationAndReview'].get('wallSecondsSum')),
             ('Two maintenance episodes + review tokens',lambda v:v['maintenanceAndReview'].get('totalTokens')),('Two maintenance episodes + review wall seconds',lambda v:v['maintenanceAndReview'].get('wallSecondsSum')),
             ('All measured automated method-stage tokens',lambda v:v['allMeasuredAutomatedMethodStages'].get('totalTokens')),('All measured automated method-stage wall seconds',lambda v:v['allMeasuredAutomatedMethodStages'].get('wallSecondsSum')),
             ('Independent evaluation wall seconds, sum (separate)',lambda v:v['independentEvaluation'].get('wallSecondsSum')),
             ('Interrupted agent verification commands',lambda v:v['agentInterruptedVerificationCommands'])]
    for label,extract in metrics:lines.append('| '+label+' | '+' | '.join(fmt(extract(data['methods'][m]))for m in ('A','B'))+' |')
    lines+=['','A’s zero added-context preparation is defined within incremental adoption; the historical effort behind its native guidance is unknown. Model-token totals include cached input; cache and reasoning subsets are not counted again. Incomplete-turn usage, if any, is only reported usage. Actual billing, coordinator work and remote inference compute remain unavailable.','',
            '| Task | A verified / recorded | B verified / recorded | A mean coding seconds | B mean coding seconds | A mean reported tokens | B mean reported tokens |','|---|---:|---:|---:|---:|---:|---:|']
    for task in data['tasks']:
        lines.append('| '+task['task']+' | '+' | '.join(f"{task[m]['successes']}/{task[m]['recorded']}"for m in ('A','B'))+' | '+' | '.join(fmt(task[m][key])for key in ('meanCodingWallSeconds','meanReportedCodingTokens')for m in ('A','B'))+' |')
    lines+=['','The two attempts are repeats within each of six task clusters. These are small file-local frontend tasks with the relevant source file identified; repository navigation, backend work and broader development tasks are untested. No pilot results are pooled.','',
            'The independent evaluator was repaired after TypeScript-Go hit its thread limit. Every candidate is checked under the same Linux-local source layout, GOMAXPROCS=2, 2 CPUs, 4 GB and 1,024-PID evaluator limit. Coding stayed at its original limits; the 24 patches and coding measurements were preserved. Initial evaluator records are retained separately as infrastructure evidence. See [evaluation amendment](../../sharedInputs/measuredStudy01/evaluationInfrastructureAmendment.json).','',
            'Completion requires hidden acceptance checks, independently passing candidate tests, pristine upstream regression tests, lint, build, permitted edits and successful agent exit within limits. An agent’s own claim or interrupted checks are not evidence of completion; independent gates determine the primary result.','']
    if data['primaryContrast']:
        lines.append('Exploratory primary contrast: B − A completion fraction = '+fmt(data['primaryContrast']['meanCompletionDifferenceBminusA'])+'; two-sided task-level exact sign-flip p = '+str(data['primaryContrast']['twoSidedExactSignFlipP'])+'. This assumes within-pair label exchangeability and has low power with six curated tasks. A null result does not establish equivalence.\n')
    lines+=['The color task did not state alpha argument position; its oracle assumed object.alpha. The memo-view task matches the actual API views collection, but the restored UI fixture uses memoViews. These two conflicts limit interpretation of registered primary completion scores. Supplemental audits are post-execution checks and do not replace registered results.','', '| Uncontested task sensitivity (four tasks, two attempts each) | A | B |','|---|---:|---:|']
    sensitivity=data['uncontestedTaskSensitivity']['methods']
    lines.append('| Verified / planned attempts | '+' | '.join(str(sensitivity[m]['verifiedCompletions'])+'/8'for m in ('A','B'))+' |')
    lines.append('| Pending verdicts | '+' | '.join(str(sensitivity[m]['unresolved'])for m in ('A','B'))+' |')
    lines.append('| Reported coding input + output tokens | '+' | '.join(fmt(sensitivity[m]['codingResources'].get('totalTokens'))for m in ('A','B'))+' |')
    lines.append('| Coding wall seconds, sum | '+' | '.join(fmt(sensitivity[m]['codingResources'].get('wallSecondsSum'))for m in ('A','B'))+' |')
    lines+=['','This subset was defined after contract conflicts were found; it is descriptive and cannot substitute for a preregistered confirmatory comparison. Both the full registered sample and the sensitivity subset remain visible.','']
    lines+=['Maintenance is assessed after two designed changes: lint-script rename and Vitest-config rename. Review items differ in granularity across workflows; compare common required-fact coverage alongside errors and measured upkeep resources. Changed hashes alone do not demonstrate stale content. Source-grounded automated judgments are not expert human judgments.','',
            'Wall seconds above sum actual stage durations; overlapping offline evaluation is separate research overhead. Memory is a 100-ms sampled container maximum including cache, not exact peak RSS. Reuse occurred across 12 attempts on six distinct tasks; no company workload, future reuse rate or monetary savings are inferred.','',
            'Full evidence: [resource comparison](resourceComparison.json), [original scoring summary](summary.json), [review amendment](../../sharedInputs/measuredStudy01/reviewAmendment.md), per-run raw events/patches and offline logs linked by those records. Historical pilots, original source copies and research files are preserved.']
    if data['studyComplete']:
        sensitivity=data['uncontestedTaskSensitivity']['methods']
        lines+=['','A performed better on this pilot’s primary completion criterion. The registered result is 8/12 for A and 5/12 for B. The color API assumption and memo-view fixture conflict limit the meaning of those absolute rates. On the separately labelled four-task sensitivity subset, A completed 8/8 attempts and B 5/8. The three B failures there were an incorrect tag-count assertion, a Unicode-ordering defect and malformed release-tag acceptance. All failed attempts remain in the resource totals.','',
          'B’s faster average attempt did not translate into a better observed coding cost per verified completion on that subset: A used '+fmt(sensitivity['A']['reportedCodingTokensPerVerifiedCompletion'])+' reported tokens and '+fmt(sensitivity['A']['codingWallSecondsPerVerifiedCompletion'])+' seconds per verified completion; B used '+fmt(sensitivity['B']['reportedCodingTokensPerVerifiedCompletion'])+' tokens and '+fmt(sensitivity['B']['codingWallSecondsPerVerifiedCompletion'])+' seconds. These figures are coding-only, include failed attempts, and describe the observed subset; setup and upkeep are reported separately above.','',
          'A’s and B’s uncached coding inputs were 299,897 and 299,777 tokens respectively. Most of the full-sample total-token difference is cached input, so it is not evidence of the same percentage reduction in actual spending. B’s added preparation plus automated review consumed 179,156 reported tokens and 95.65 seconds. Native documentation creation is historical and unknown; it is not treated as free.','',
          'Across the two controlled maintenance edits, A took 53.85 seconds and B 75.58 seconds. Including the recorded automated review calls, maintenance consumed 609,198 tokens / 229.67 seconds for A and 776,370 tokens / 210.09 seconds for B. Review scope, missing reviewer inputs, exact-quote corrections and one recovered output-file delivery required coordinator adjudication. Coordinator effort is unavailable, so these recorded stage costs cannot establish total maintenance labor savings.','',
          'The source consistency audit found no remaining obsolete command or config-path mentions for the introduced changes. B’s source-map hashes and claim-source links match both maintained derivatives. The Vitest-config filename was missing from A’s guide in the lint-rename episode (5/6 common coverage items); all other final episode/workflow cases covered 6/6. Missing detail is not counted as a false claim. Changes were supplied explicitly, so autonomous staleness discovery and natural maintenance frequency were not measured.','',
          'Both diagnostic audits passed: all four color candidates satisfy the written alpha behavior through a consistent reasonable interface; baseline plus all four memo-view candidates pass the targeted UI fixture checks after changing only the mock resource name. Those audits do not alter primary scores. All four submitted memo-view fixtures were unchanged, so the diagnostic fixture edit does not repair their submitted CI failures.','',
          'The justified claim is bounded: the existing Memos workflow was more reliable and used fewer observed coding resources per verified completion in this pilot; the prepared guide reduced average attempt time but did not improve completion. Six curated tasks, two attempts, two contract conflicts and the exploratory primary p=0.25 do not establish general superiority or equivalence. No company savings, completed human-review cost, backend result or performance for the undecided third method is inferred.','',
          'Additional audits: [maintenance consistency](maintenanceConsistencyAudit.json), [context exposure](contextExposureAudit.json), [color interface](colorTaskValidityAudit.json), [memo-view fixture](memoTaskValidityAudit.json), [preservation verification](preservationVerification.json).']
    (s.REPORT/'comparison.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'studyComplete':data['studyComplete'],'recordedCodingRuns':len(all_records),'report':'reports/measuredStudy01/comparison.md'}))

if __name__=='__main__':main()
