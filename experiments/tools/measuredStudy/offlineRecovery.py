#!/usr/bin/env python3
"""Common evaluator infrastructure repair. Never edits or reruns coding candidates."""
import concurrent.futures
import json
from pathlib import Path
import re
import shlex
import subprocess
import time

import studyRunner as s
import automatedStudy as a

AMENDMENT=s.INPUT/'evaluationInfrastructureAmendment.json'

def freeze():
    a.validate_execution()
    if AMENDMENT.exists():validate();return
    calibration=s.REPORT/'evaluatorCalibrationRecovered/resource.json'
    if s.read(calibration)['exitCode']!=0:raise RuntimeError('Baseline lint calibration failed')
    s.write(AMENDMENT,{'recordedAt':s.now(),'reason':'Initial evaluator TypeScript-Go runtime crashed with newosproc at the 256-thread/process cgroup cap; successful behavioral gates do not resolve lint. This is shared evaluator infrastructure, not candidate code failure.',
        'codingInputsAndRunsUnchanged':True,'all24CodingRunsSealed':True,'sourcePolicy':'Read-only candidates copied to Linux-local /project before running identical check commands.',
        'cpuLimit':2,'memoryLimit':'4g','pidLimit':1024,'compilerEnvironment':{'GOMAXPROCS':'2'},'network':'none','credentialsMounted':False,
        'evaluationConcurrency':2,'timeoutSeconds':900,'scoringCriteriaChanged':False,'selection':'Every one of the 24 candidates receives the common repaired evaluator, irrespective of method or prior status.',
        'retention':'Original initial evaluation JSON/logs/resources retained. Repaired verdicts use evaluationRecovered.json and independentEvaluationRecovered; no coding-agent replay or candidate repair.',
        'calibrationResourceSha256':s.digest(calibration),'implementationSha256':s.digest(Path(__file__).resolve()),'executionProtocolSha256':s.digest(s.INPUT/'executionProtocol.json')})

def validate():
    a.validate_execution()
    data=s.read(AMENDMENT)
    if s.digest(Path(__file__).resolve())!=data['implementationSha256'] or s.digest(s.INPUT/'executionProtocol.json')!=data['executionProtocolSha256']:
        raise RuntimeError('Evaluation repair seal changed')

def stage(output,project,acceptance,shell):
    if output.exists():raise RuntimeError('Recovered evaluator already started; inspect rather than overwrite')
    output.mkdir(parents=True)
    s.write(output/'started.json',{'startedAt':s.now(),'infrastructureAmendmentSha256':s.digest(AMENDMENT)})
    import hashlib
    name='memos-recovered-'+hashlib.sha256(str(output).encode()).hexdigest()[:12]
    args=['docker','run','--rm','--init','--name',name,'--network','none','--cpus','2','--memory','4g','--pids-limit','1024','--cap-drop','ALL','--security-opt','no-new-privileges','--env','GOMAXPROCS=2',
          '--mount',f'type=bind,source={project},target=/candidate,readonly',
          '--mount',f'type=bind,source={s.BASE/"web/tests"},target=/baselineTests,readonly',
          '--mount',f'type=bind,source={acceptance},target=/hiddenAcceptance,readonly',
          '--mount',f'type=bind,source={s.HERE/"measureStage.py"},target=/stage/measureStage.py,readonly',
          '--mount',f'type=bind,source={output},target=/measurement',s.IMAGE,'python3','/stage/measureStage.py','--out','/measurement','--timeout','900','--','bash','-lc',shell]
    start=time.monotonic()
    try:
        result=subprocess.run(args,text=True,capture_output=True,timeout=990)
        (output/'transport.log').write_text(result.stdout);(output/'transport.stderr').write_text(result.stderr)
        record={'hostWallSeconds':time.monotonic()-start,'dockerExitCode':result.returncode,'finishedAt':s.now()}
    except subprocess.TimeoutExpired:
        subprocess.run(['docker','kill',name],capture_output=True)
        record={'hostWallSeconds':time.monotonic()-start,'dockerExitCode':None,'infrastructureError':'Host evaluator deadline; no candidate or coding retry'}
    record['resources']=s.read(output/'resource.json')if(output/'resource.json').exists()else None
    s.write(output/'stage.json',record)
    return record

def evaluate(item):
    validate()
    output=s.run_path(item)
    verdict=output/'evaluationRecovered.json'
    if verdict.exists():return {'item':item,'alreadyEvaluated':True}
    execution=s.read(output/'execution.json');project=output/'project'
    task=next(t for t in s.tasks()if t['id']==item['task'])
    changed=[name for name in execution['changes']['testFilesChanged']if re.fullmatch(r'web/tests/.*\.test\.(ts|tsx)',name)and(project/name).is_file()]
    flags=[]
    for name in execution['changes']['testFilesChanged']:
        file=project/name
        if not file.is_file():flags.append(name+': deleted test/support file')
        elif re.search(r'\b(?:it|test|describe)\s*\.\s*(?:skip|only|todo)\b',file.read_text(errors='replace')):flags.append(name+': skip/only/todo registration')
        if(s.BASE/name).exists():
            diff=subprocess.run(['git','diff','--no-index',str(s.BASE/name),str(file)],capture_output=True,text=True).stdout
            if any(line.startswith('-')and not line.startswith('---')and('expect('in line or re.search(r'\b(?:it|test)\(',line))for line in diff.splitlines()):flags.append(name+': removed or rewritten upstream test assertion')
    target=output/'independentEvaluationRecovered'
    candidate=shlex.join(['pnpm','exec','vitest','run',*[str(Path(name).relative_to('web'))for name in changed]])if changed else 'false'
    commands=['set +e','cp -a /candidate/. /project/; copyStatus=$?','cd /project/web','pnpm lint > /measurement/lint.log 2>&1; lintStatus=$?',candidate+' > /measurement/candidateTests.log 2>&1; candidateStatus=$?',
              'cp /hiddenAcceptance tests/__studyAcceptance.test.ts','pnpm exec vitest run tests/__studyAcceptance.test.ts --reporter=json > /measurement/acceptance.json 2> /measurement/acceptance.stderr; acceptanceStatus=$?',
              'rm -rf /project/web/tests','cp -a /baselineTests /project/web/tests; restoreStatus=$?','pnpm test > /measurement/regression.log 2>&1; regressionStatus=$?','pnpm build > /measurement/build.log 2>&1; buildStatus=$?',
              'printf "COPY %s\\nGATES %s %s %s %s %s %s\\n" "$copyStatus" "$lintStatus" "$candidateStatus" "$acceptanceStatus" "$restoreStatus" "$regressionStatus" "$buildStatus"']
    result=stage(target,project,s.INPUT/task['acceptanceFile'],'; '.join(commands))
    text=(target/'events.jsonl').read_text()if(target/'events.jsonl').exists()else''
    match=re.search(r'GATES (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)',text)
    copy=re.search(r'COPY (\d+)',text)
    gates=dict(zip(('lint','candidateTests','acceptance','restorePristineTests','regression','build'),map(int,match.groups())))if match else None
    source_unchanged=all((project/name).is_file()and s.digest(project/name)==sha if sha is not None else not(project/name).exists()for name,sha in execution['changes']['fileHashes'].items())
    native_resource=execution['stage'].get('resources')or{}
    passed=bool(native_resource.get('exitCode')==0 and not native_resource.get('timedOut') and execution['changes']['permitted']and changed and copy and copy.group(1)=='0' and gates and all(v==0 for v in gates.values())and source_unchanged)
    infra=not match or not copy or copy.group(1)!='0' or bool(re.search('newosproc|failed to create new OS thread',(target/'lint.log').read_text(errors='replace')if(target/'lint.log').exists()else''))
    value={'gates':gates,'automatedGatesPass':passed,'verifiedCompletion':passed if not flags and not infra else None,'humanAdjudicationRequired':flags,'evaluationUnresolved':infra,'candidateArtifactsUnchanged':source_unchanged,
           'bContextExposureObserved':execution.get('fullGuideExposureObserved'),'evaluationStage':result,'evaluationRevision':'common infrastructure recovery','infrastructureAmendmentSha256':s.digest(AMENDMENT),'initialEvaluationRetained':(output/'evaluation.json').exists()}
    s.write(verdict,value)
    return {'item':item,'verifiedCompletion':value['verifiedCompletion'],'gates':gates,'flags':flags,'infra':infra}

def main():
    validate()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
        futures=[pool.submit(evaluate,item)for item in s.validate_inputs()['schedule']]
        for future in concurrent.futures.as_completed(futures):print(json.dumps(future.result()),flush=True)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['freeze','run']);action=parser.parse_args().action
    freeze()if action=='freeze'else main()
