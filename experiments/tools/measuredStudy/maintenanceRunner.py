#!/usr/bin/env python3
"""Two controlled maintenance episodes; isolated derivatives, original sources untouched."""
import argparse
import json
import re
import shutil

import studyRunner as study

EPISODES = ('renameLintScript', 'renameVitestConfig')

def apply_change(project, episode):
    package_file = project / 'web/package.json'
    package = study.read(package_file)
    if episode == 'renameLintScript':
        package['scripts']['check'] = package['scripts'].pop('lint')
        path = project / '.github/workflows/frontend-tests.yml'
        path.write_text(path.read_text().replace('pnpm lint', 'pnpm check'))
    elif episode == 'renameVitestConfig':
        (project / 'web/vitest.config.mts').rename(project / 'web/vitest.project.config.mts')
        for key in ('test','test:watch','test:coverage'):
            package['scripts'][key] += ' --config vitest.project.config.mts'
    else:
        raise ValueError(episode)
    study.write(package_file, package)

def facts(project, episode):
    package = study.read(project / 'web/package.json')
    return {
        'frontendCheckCommand': 'cd web && pnpm check' if episode == 'renameLintScript' else 'cd web && pnpm lint',
        'unitTestCommand': 'cd web && pnpm test',
        'vitestConfig': 'web/vitest.project.config.mts' if episode == 'renameVitestConfig' else 'web/vitest.config.mts',
        'nodeEngine': package['engines']['node'], 'pnpm': package['packageManager'],
        'generatedTypeScript': 'web/src/types/proto/; do not hand-edit',
    }

def claims_for_native(project):
    text = (project / 'AGENTS.md').read_text()
    excerpts = []
    for label, start, end in [('commands','# Frontend','# Protocol Buffers'), ('verification','## Verification Policy','## CI Reference'), ('ci','- Workflows install toolchains',None), ('generatedFiles','## Database And Proto Rules','## Verification Policy')]:
        begin = text.find(start)
        stop = text.find(end, begin + len(start)) if end else len(text)
        if begin >= 0:
            excerpts.append({'id': 'native' + str(len(excerpts)+1), 'topic': label, 'text':text[begin:stop].strip(), 'sources':['AGENTS.md']})
    return {'claims': excerpts}

def run():
    protocol = study.validate_inputs()
    study.validate_execution()
    if sum((study.run_path(item) / 'execution.json').exists() for item in protocol['schedule']) != 24:
        raise RuntimeError('Complete/seal all 24 coding attempts before maintenance')
    study.preflight()
    for index, episode in enumerate(EPISODES):
        for method in (('A','B') if index == 0 else ('B','A')):
            parent = study.REPORT / 'maintenance' / episode / method
            if (parent / 'observation.json').exists():
                continue
            if (parent / 'measurement').exists():
                raise RuntimeError('Partially started maintenance; do not replay ' + str(parent))
            project = parent / 'project'
            study.copy_project(project)
            apply_change(project, episode)
            if method == 'B':
                shutil.copytree(study.PACK, project / 'contextPack')
            initial = {str(p.relative_to(project)):study.digest(p) for p in project.rglob('*') if p.is_file() and '.git' not in p.parts}
            study.write(parent / 'introducedFacts.json', facts(project, episode))
            message = ('The frontend lint package script was renamed to check; CI has been updated to use pnpm check.' if episode == 'renameLintScript' else 'The Vitest configuration was renamed to web/vitest.project.config.mts; test, test:watch and test:coverage scripts now explicitly select it.')
            prompt = 'Perform documentation maintenance after this controlled project change: ' + message + '\nInspect actual configuration and native guidance. Update only AGENTS.md' + (' and contextPack/claims.json' if method == 'B' else '') + '. Preserve unrelated guidance. Do not change code, dependencies, workflows, Git history, other files, authentication or network sources. Do not delegate. Do not run full test/build suites; verify documentation against actual supplied configuration. '
            if method == 'B':
                prompt += 'Read the existing contextPack/contextGuide.md. Preserve the claims JSON schema, update affected claims and source paths; the coordinator will regenerate the guide/source map mechanically. '
            result = study.stage(parent / 'measurement', project, prompt)
            if result.get('providerInfrastructureFailure') or result.get('infrastructureError'):
                raise RuntimeError('Maintenance infrastructure failed; preserve records and stop')
            changed = [name for name, expected in initial.items() if not (project / name).is_file() or study.digest(project / name) != expected]
            added = [str(p.relative_to(project)) for p in project.rglob('*') if p.is_file() and '.git' not in p.parts and 'node_modules' not in p.parts and str(p.relative_to(project)) not in initial]
            allowed = all(name == 'AGENTS.md' or (method == 'B' and name == 'contextPack/claims.json') for name in changed + added)
            claims = study.read(project / 'contextPack/claims.json') if method == 'B' else claims_for_native(project)
            if method == 'B':
                sources = study.read(project / 'contextPack/sourceMap.json')['sources']
                for source in sources:
                    if source['path'] == 'web/vitest.config.mts' and episode == 'renameVitestConfig':
                        source['path'] = 'web/vitest.project.config.mts'
                    source['sha256'] = study.digest(project / source['path'])
                study.render_pack(claims, project / 'contextPack', sources)
            guide_text = (project / 'AGENTS.md').read_text() + ((project / 'contextPack/contextGuide.md').read_text() if method == 'B' else '')
            alerts = []
            if episode == 'renameLintScript' and re.search(r'pnpm lint\b', guide_text):
                alerts.append('Potential obsolete pnpm lint instruction; human must distinguish historical mention from actionable claim')
            if episode == 'renameVitestConfig' and 'vitest.config.mts' in guide_text:
                alerts.append('Potential obsolete Vitest config path; human factual judgment required')
            observation = {'episode':episode,'method':method,'controlledChange':message,'stage':result,'changedFiles':changed,'addedFiles':added,'allowedScope':allowed,'reviewAlerts':alerts,'staleClaimsBefore':None,'staleClaimsAfter':None,'humanReviewRequired':True,'note':'Source hash changes are review triggers, not stale-claim labels. Human judgments determine factual errors and common-fact coverage.'}
            study.write(parent / 'observation.json', observation)
            identifier = episode + method
            study.create_review_packet(identifier, claims, project, project, {'method':method, 'episode':episode, 'facts':facts(project,episode), 'alerts':alerts})
            packet_path = study.REPORT / 'humanReview' / identifier / 'packet.json'
            packet = study.read(packet_path)
            packet['editableDocuments'] = {'AGENTS.md':(project / 'AGENTS.md').read_text()}
            # Compare actual before and after prose, not only assertions that survived maintenance.
            packet['metadata']['nativeBefore'] = (study.BASE / 'AGENTS.md').read_text()
            packet['metadata']['additionalContextBefore'] = (study.PACK / 'contextGuide.md').read_text() if method == 'B' else None
            if method == 'B':
                packet['beforeClaims'] = study.read(study.PACK / 'claims.json')['claims']
            else:
                packet['beforeClaims'] = claims_for_native(study.BASE)['claims']
            study.write(packet_path, packet)
    print(json.dumps({'maintenanceAutomatedStages':4, 'requiredHumanReviewOrder':['renameLintScriptA','renameLintScriptB','renameVitestConfigB','renameVitestConfigA']}), flush=True)
    study.analyze()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    run()
