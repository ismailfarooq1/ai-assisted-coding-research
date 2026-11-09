#!/usr/bin/env python3
"""Post-execution sensitivity audit of a stale memo-view UI fixture, not primary rescoring."""
import argparse
from pathlib import Path
import json
import re

import studyRunner as s
import offlineRecovery as evaluator

DEFINITION=s.INPUT/'memoTaskValidityAudit.json'
FIXTURE=s.INPUT/'supplementalEvaluation/sidebarRowStateApiFixture.test.tsx'
ORIGINAL=s.BASE/'web/tests/sidebar-row-state.test.tsx'

def freeze():
    if DEFINITION.exists():raise RuntimeError('Memo fixture audit already defined')
    old=ORIGINAL.read_text()
    if old.count('users/1/memoViews/abc')!=1:raise RuntimeError('Unexpected original fixture')
    FIXTURE.write_text(old.replace('users/1/memoViews/abc','users/1/views/abc'))
    proto=s.BASE/'proto/api/user_service.proto'
    server=s.BASE/'server/api/user_service_memo_views.go'
    s.write(DEFINITION,{'recordedAt':s.now(),'classification':'Post-execution task/evaluator-validity sensitivity audit, discovered from registered regression failures; primary scores remain unchanged.',
        'reason':'The task requires exact users/<user>/views/<view> names and returning other collections unchanged. Pristine sidebar-row-state mocks users/1/memoViews/abc and expects the extracted abc. Actual proto/API builders use users/{user}/views/{view}. Restoring that fixture conflicts with the requested strict helper contract even if a candidate updates relevant fixtures.',
        'sourceEvidence':{'proto':{'path':str(proto.relative_to(s.BASE)),'sha256':s.digest(proto),'excerpt':'pattern: "users/{user}/views/{view}"'},'server':{'path':str(server.relative_to(s.BASE)),'sha256':s.digest(server),'excerpt':'return fmt.Sprintf("%s/views/%s", BuildUserName(username), memoViewID)'}},
        'originalFixtureSha256':s.digest(ORIGINAL),'correctedFixtureSha256':s.digest(FIXTURE),'runnerSha256':s.digest(Path(__file__).resolve()),
        'fixtureChange':'Only replace the single mock resource name. All test logic/assertions stay byte-for-byte otherwise unchanged.',
        'candidates':'Baseline plus all four memoViewNames candidates; no selection by result. No application patch edits or new coding calls.',
        'scope':'Targeted UI fixture sensitivity only, not a repeat of the entire regression suite or replacement primary endpoint. Genuine formatter or candidate-test failures remain failures.'})

def run():
    definition=s.read(DEFINITION)
    if s.digest(FIXTURE)!=definition['correctedFixtureSha256']or s.digest(Path(__file__).resolve())!=definition['runnerSha256']:raise RuntimeError('Memo audit definition changed')
    cases=[({'method':'baseline','task':'memoViewNames','attempt':0},s.BASE,s.REPORT/'memoFixtureAuditBaseline')]
    for item in s.validate_inputs()['schedule']:
        if item['task']=='memoViewNames':cases.append((item,s.run_path(item)/'project',s.run_path(item)/'supplementalMemoFixtureAudit'))
    rows=[]
    for item,project,target in cases:
        if(target/'audit.json').exists():rows.append(s.read(target/'audit.json'));continue
        shell='cp -a /candidate/. /project/ && cd /project/web && cp /hiddenAcceptance tests/sidebar-row-state.test.tsx && pnpm exec vitest run tests/sidebar-row-state.test.tsx --reporter=json > /measurement/acceptance.json 2> /measurement/acceptance.stderr'
        stage=evaluator.stage(target,project,FIXTURE,shell)
        result=s.read(target/'acceptance.json')if(target/'acceptance.json').exists()else{}
        row={'item':item,'passed':result.get('success')is True and result.get('numTotalTests',0)>0 and(stage.get('resources')or{}).get('exitCode')==0,'tests':result.get('numTotalTests'),'stage':stage,'definitionSha256':s.digest(DEFINITION),'classification':'Supplemental fixture sensitivity; original primary regression and formatting verdicts retained'}
        s.write(target/'audit.json',row);rows.append(row)
    s.write(s.REPORT/'memoTaskValidityAudit.json',{'definition':definition,'rows':rows,'passed':sum(v['passed']for v in rows),'audited':len(rows)})
    print(json.dumps({'memoFixtureChecks':len(rows),'passed':sum(v['passed']for v in rows)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','run']);freeze()if p.parse_args().action=='freeze'else run()
