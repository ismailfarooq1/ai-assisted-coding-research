#!/usr/bin/env python3
"""Prepare and audit Memos experiment projects. Never launches an agent."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

STUDY = Path(__file__).resolve().parents[1]
WORKSPACE = STUDY.parents[1]
SOURCE = WORKSPACE / '.local' / 'memos-origin'
METHODS = ('existing-workflow', 'prepared-context', 'proposed-method')
CONTEXT_DIR = '.project-context'
CONTEXT_NOTICE = b'''\n\n## Additional project context\n\nBefore making changes, read [.project-context/README.md](.project-context/README.md)\nand the relevant linked context files. Verify current behavior against source\nand tests. Keep changes scoped to the assigned task.\n'''


def git(*args, cwd=None, binary=False):
    result = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null',
                             '-c', 'core.fsmonitor=false', *map(str, args)],
                            cwd=cwd, check=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return result.stdout if binary else result.stdout.decode().strip()


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def spec():
    return read_json(STUDY / 'shared' / 'study.json')


def method_path(method):
    if method not in METHODS:
        raise ValueError('Unknown method')
    return STUDY / 'methods' / method


def method_config(method):
    config = read_json(method_path(method) / 'method.json')
    if config['id'] != method:
        raise ValueError('Method configuration ID mismatch')
    return config


def ensure_enabled(method):
    if not method_config(method)['setup_enabled']:
        raise ValueError('proposed-method is a disabled shell; discuss its design before setup')


def source_info():
    config = spec()['project']
    commit = config['candidate_commit']
    git('cat-file', '-e', commit + '^{commit}', cwd=SOURCE)
    tree = git('rev-parse', commit + '^{tree}', cwd=SOURCE)
    if tree != config['git_tree']:
        raise ValueError('Source tree does not match study configuration')
    return commit, tree


def acquire_source():
    config = spec()['project']
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    if not SOURCE.exists():
        # Only publish the local source cache after a successful clone.
        with tempfile.TemporaryDirectory(dir=SOURCE.parent) as temporary:
            candidate = Path(temporary) / 'origin'
            git('clone', '--depth', '1', '--no-checkout', config['repository'], candidate)
            if not subprocess.run(['git', '-C', str(candidate), 'cat-file', '-e',
                                   config['candidate_commit'] + '^{commit}'],
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL).returncode == 0:
                git('fetch', '--depth', '1', 'origin', config['candidate_commit'], cwd=candidate)
            candidate.rename(SOURCE)
    # Never silently update or replace an existing cache.
    return source_info()


def inventory(project):
    """Tracked source plus untracked, nonignored files; no dependency caches or .git."""
    names = git('ls-files', '--cached', '--others', '--exclude-standard', '-z',
                cwd=project, binary=True).split(b'\0')
    records = {}
    for raw in sorted(set(names) - {b''}):
        name = os.fsdecode(raw)
        if Path(name).name == '.DS_Store':
            continue
        path = project / name
        if path.is_symlink():
            if not path.resolve().is_relative_to(project.resolve()):
                raise ValueError('Source symlink leaves project: ' + name)
            data, kind = os.fsencode(os.readlink(path)), 'symlink'
        else:
            data, kind = path.read_bytes(), 'file'
        records[name] = {'sha256': sha(data), 'kind': kind,
                         'executable': bool(path.lstat().st_mode & 0o111)}
    encoded = json.dumps(records, sort_keys=True, separators=(',', ':')).encode()
    return sha(encoded), records


def context_assets():
    folder = method_path('prepared-context') / 'context'
    return {p.name: p.read_bytes() for p in sorted(folder.glob('*.md'))}


def check(method):
    ensure_enabled(method)
    folder = method_path(method)
    project = folder / 'project'
    manifest = read_json(folder / 'setup-manifest.json')
    commit, tree = source_info()
    if manifest['method'] != method or manifest['source_commit'] != commit:
        raise ValueError('Manifest identity/source mismatch')
    if manifest['source_tree'] != tree:
        raise ValueError('Source tree mismatch')
    if manifest['method_config_sha256'] != sha((folder / 'method.json').read_bytes()):
        raise ValueError('Method definition changed; preserve existing project before re-preparing')
    if manifest['study_config_sha256'] != sha((STUDY / 'shared/study.json').read_bytes()):
        raise ValueError('Shared study configuration changed since preparation')
    if manifest['setup_tool_sha256'] != sha(Path(__file__).read_bytes()):
        raise ValueError('Setup tool changed since project preparation')
    if git('rev-parse', 'HEAD', cwd=project) != commit:
        raise ValueError('Project HEAD differs from pinned candidate')
    if git('remote', cwd=project):
        raise ValueError('Experiment project must have no Git remotes')
    if (project / '.git').is_symlink() or not (project / '.git').is_dir():
        raise ValueError('Project Git metadata must be a separate local directory')
    digest, records = inventory(project)
    if digest != manifest['starting_files_sha256']:
        raise ValueError('Starting files changed; refusing to overwrite or reset work')
    original = git('show', commit + ':AGENTS.md', cwd=SOURCE, binary=True)
    if method == 'existing-workflow':
        if git('diff', '--name-only', commit, cwd=project):
            raise ValueError('Existing workflow differs from source')
        if (project / CONTEXT_DIR).exists() or (project / 'AGENTS.md').read_bytes() != original:
            raise ValueError('Unexpected added context in existing workflow')
    else:
        assets = context_assets()
        if not assets:
            raise ValueError('Prepared context pack is empty')
        if (project / 'AGENTS.md').read_bytes() != original + CONTEXT_NOTICE:
            raise ValueError('Native instructions/context loading notice mismatch')
        for name, data in assets.items():
            if (project / CONTEXT_DIR / name).read_bytes() != data:
                raise ValueError('Prepared context differs: ' + name)
        actual = set(git('diff', '--name-only', commit, cwd=project).splitlines())
        if actual != {'AGENTS.md'}:
            raise ValueError('Prepared workflow unexpectedly changes tracked application files')
        if {n for n in records if n.startswith(CONTEXT_DIR + '/')} != {
                CONTEXT_DIR + '/' + n for n in assets}:
            raise ValueError('Unexpected prepared context file')
    return {'method': method, 'status': 'starting-files-verified',
            'source_commit': commit, 'files': len(records),
            'starting_files_sha256': digest, 'application_tests': 'not run',
            'agent_execution': 'not implemented'}


def setup(method):
    ensure_enabled(method)
    commit, tree = acquire_source()
    folder = method_path(method)
    project = folder / 'project'
    manifest_path = folder / 'setup-manifest.json'
    if project.exists() or manifest_path.exists():
        # Idempotent for intact setups, protective after any user edits.
        return check(method)
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='.preparing-', dir=folder) as temporary:
        candidate = Path(temporary) / 'project'
        git('clone', '--no-hardlinks', '--no-checkout', SOURCE, candidate)
        git('remote', 'remove', 'origin', cwd=candidate)
        git('config', 'core.hooksPath', '/dev/null', cwd=candidate)
        git('config', 'core.fsmonitor', 'false', cwd=candidate)
        git('checkout', '--detach', commit, cwd=candidate)
        context_hashes = {}
        if method == 'prepared-context':
            assets = context_assets()
            if not assets:
                raise ValueError('Prepared context pack is empty')
            context = candidate / CONTEXT_DIR
            context.mkdir(exist_ok=False)
            for name, data in assets.items():
                (context / name).write_bytes(data)
                context_hashes[CONTEXT_DIR + '/' + name] = sha(data)
            instructions = candidate / 'AGENTS.md'
            instructions.write_bytes(instructions.read_bytes() + CONTEXT_NOTICE)
        digest, records = inventory(candidate)
        manifest = {'schema_version': 1, 'method': method,
                    'prepared_at': datetime.now(timezone.utc).isoformat(),
                    'source_commit': commit, 'source_tree': tree,
                    'source_status': 'candidate; application environment unvalidated',
                    'method_config_sha256': sha((folder / 'method.json').read_bytes()),
                    'setup_tool_sha256': sha(Path(__file__).read_bytes()),
                    'study_config_sha256': sha((STUDY / 'shared/study.json').read_bytes()),
                    'starting_files_sha256': digest, 'file_count': len(records),
                    'added_context_files_sha256': context_hashes,
                    'setup_elapsed_seconds': round(time.perf_counter() - started, 6),
                    'context_authoring_tokens': None, 'human_authoring_minutes': None,
                    'missing_usage_reason': 'Context authoring was not instrumented; setup time measures only local materialization',
                    'application_tests': 'not run', 'agent_experiments': 'not run'}
        candidate.rename(project)
        write_json(manifest_path, manifest)
    return check(method)


def doctor():
    tools = {}
    for name, args in [('git', ['--version']), ('python3', ['--version']),
                       ('go', ['version']), ('node', ['--version']),
                       ('pnpm', ['--version']), ('docker', ['--version'])]:
        path = shutil.which(name)
        version = None
        if path:
            result = subprocess.run([path, *args], stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, timeout=15)
            version = result.stdout.strip()
        tools[name] = {'path': path, 'version': version}
    return {'required_by_pinned_source': spec()['runtime_requirements'],
            'installed_tools': tools, 'docker_daemon': 'not checked',
            'application_dependencies': 'not installed by setup',
            'application_environment': 'not validated', 'scored_execution': 'disabled'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['setup', 'check', 'doctor', 'status'])
    parser.add_argument('method', nargs='?', choices=[*METHODS, 'all'], default='all')
    args = parser.parse_args()
    try:
        if args.command == 'doctor':
            output = doctor()
        elif args.command == 'status':
            output = [{'method': m, 'setup_enabled': method_config(m)['setup_enabled'],
                       'project_present': (method_path(m) / 'project').exists(),
                       'execution_enabled': False} for m in METHODS]
        else:
            selected = [m for m in METHODS if method_config(m)['setup_enabled']] if args.method == 'all' else [args.method]
            output = [globals()[args.command](m) for m in selected]
        print(json.dumps(output, indent=2))
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        # Git stderr can include local paths but no credential-bearing repository URL is accepted from the CLI.
        print('Setup error: ' + str(error), file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr.decode(errors='replace'), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
