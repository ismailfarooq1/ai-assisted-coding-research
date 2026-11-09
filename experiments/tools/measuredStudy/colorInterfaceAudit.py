#!/usr/bin/env python3
"""Explicit post-execution sensitivity check for an underspecified API contract."""
import json
import re
from pathlib import Path

import studyRunner as s
import offlineRecovery as evaluator

DEFINITION=s.INPUT/'colorTaskValidityAudit.json'
TEST=s.INPUT/'supplementalEvaluation/colorAlphaInterface.test.ts'

def freeze():
    if DEFINITION.exists():raise RuntimeError('Audit already defined')
    s.write(DEFINITION,{'recordedAt':s.now(),'classification':'Post-execution task-validity audit, discovered after seeing failed registered color acceptances; not a predeclared primary endpoint.',
        'reason':'The frozen task says add optional alpha to colorToHex but never specifies property versus second argument. Both preserve existing calls and can satisfy the described behavior. The registered oracle assumes object.alpha without stating that API in the task.',
        'registeredScoresPreserved':True,'codingCallsAdded':0,'candidates':'All four colorAlpha candidates, including any passing registered tests; no selection by method or result.',
        'audit':'Require all stated behavior through one consistently applied interface, either object.alpha or second argument. Do not choose an interface per test case.',
        'inference':'Report registered oracle scores and this audit separately. Do not interpret an unstated API choice as evidence of method inferiority. Show the five unambiguous tasks separately as a labeled sensitivity subset.',
        'taskSha256':s.digest(s.INPUT/'tasks/colorAlpha.md'),'registeredOracleSha256':s.digest(s.INPUT/'evaluation/colorAlpha.test.ts'),'supplementalOracleSha256':s.digest(TEST),'runnerSha256':s.digest(Path(__file__).resolve())})

def run():
    definition=s.read(DEFINITION)
    if s.digest(TEST)!=definition['supplementalOracleSha256'] or s.digest(Path(__file__).resolve())!=definition['runnerSha256']:raise RuntimeError('Audit changed')
    rows=[]
    for item in s.validate_inputs()['schedule']:
        if item['task']!='colorAlpha':continue
        candidate=s.run_path(item)
        target=candidate/'supplementalColorInterfaceAudit'
        if (target/'audit.json').exists():rows.append(s.read(target/'audit.json'));continue
        shell='cp -a /candidate/. /project/ && cd /project/web && cp /hiddenAcceptance tests/__studyAcceptance.test.ts && pnpm exec vitest run tests/__studyAcceptance.test.ts --reporter=json > /measurement/acceptance.json 2> /measurement/acceptance.stderr'
        stage=evaluator.stage(target,candidate/'project',TEST,shell)
        test=s.read(target/'acceptance.json')if(target/'acceptance.json').exists()else{}
        result={'item':item,'passed':test.get('success')is True and test.get('numTotalTests')==1 and (stage.get('resources')or{}).get('exitCode')==0,'stage':stage,'definitionSha256':s.digest(DEFINITION),'classification':'Post-execution interface-validity sensitivity audit; registered primary result unchanged'}
        s.write(target/'audit.json',result);rows.append(result)
    s.write(s.REPORT/'colorTaskValidityAudit.json',{'definition':definition,'rows':rows,'passed':sum(v['passed']for v in rows),'audited':len(rows)})
    print(json.dumps({'auditedColorCandidates':len(rows),'interfaceAuditPassed':sum(v['passed']for v in rows)}))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','run']);freeze()if p.parse_args().action=='freeze'else run()
