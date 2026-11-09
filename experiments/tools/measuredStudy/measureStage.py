#!/usr/bin/env python3
"""Container-side stage timer; writes only resource and whitelisted usage metadata."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time

def read_cpu():
    try:
        return {k: int(v) for k, v in (line.split() for line in Path('/sys/fs/cgroup/cpu.stat').read_text().splitlines())}
    except (OSError, ValueError):
        return {}

def read_memory():
    try:
        return int(Path('/sys/fs/cgroup/memory.current').read_text())
    except (OSError, ValueError):
        return None

def rollout_usage(home):
    observations = []
    # Fresh private CLI home for this container; never inspect host sessions or copy transcripts.
    for path in (home / 'sessions').rglob('*.jsonl') if (home / 'sessions').exists() else []:
        for line in path.read_text(errors='replace').splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            payload = event.get('payload', {})
            if payload.get('type') != 'token_count':
                continue
            info = payload.get('info') or {}
            usage = info.get('total_token_usage') or {}
            clean = {key: value for key, value in usage.items() if key in (
                'input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens', 'total_tokens') and type(value) is int and value >= 0}
            if clean:
                observations.append(clean)
    return observations

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--timeout', type=float, required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command and args.command[0] == '--' else args.command
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cpu_before = read_cpu()
    memory_first = read_memory()
    samples = [memory_first] if memory_first is not None else []
    start = time.monotonic()
    timed_out = False
    with (out / 'events.jsonl').open('w') as stdout, (out / 'stderr.log').open('w') as stderr:
        process = subprocess.Popen(command, stdin=None, stdout=stdout, stderr=stderr, start_new_session=True)
        while process.poll() is None:
            memory = read_memory()
            if memory is not None:
                samples.append(memory)
            if time.monotonic() - start >= args.timeout:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                break
            time.sleep(0.1)
        process.wait()
        # Terminate orphaned checks left in the CLI process group before closing the boundary.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    cpu_after = read_cpu()
    elapsed = time.monotonic() - start
    cpu_delta = {k: cpu_after[k] - v for k, v in cpu_before.items() if k in cpu_after}
    record = {
        'exitCode': process.returncode, 'timedOut': timed_out, 'processWallSeconds': elapsed,
        'cpuUsageSeconds': cpu_delta.get('usage_usec', 0) / 1e6 if 'usage_usec' in cpu_delta else None,
        'cpuStatDelta': cpu_delta or None, 'initialMemoryBytes': memory_first,
        'sampledPeakMemoryBytes': max(samples) if samples else None, 'memorySamples': len(samples),
        'samplingIntervalSeconds': 0.1,
        'memoryDefinition': 'Observed maximum memory.current, including container cache/kernel; not exact peak or process RSS. Startup before wrapper is excluded.',
        'cpuDefinition': 'Container cgroup CPU delta during stage including local descendants and metering; remote inference compute unobserved.',
        'rolloutUsageObservations': rollout_usage(Path('/root/.codex')),
    }
    (out / 'resource.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'stageFinished': True, 'exitCode': process.returncode, 'timedOut': timed_out}), flush=True)

if __name__ == '__main__':
    main()
