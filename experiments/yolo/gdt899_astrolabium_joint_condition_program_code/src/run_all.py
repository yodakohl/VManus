#!/usr/bin/env python3
"""Run the six predeclared headers concurrently, with an outer timeout."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
BASE = Path(__file__).resolve().parents[1]
def main():
    p = argparse.ArgumentParser()
    p.add_argument('--engine', choices=['cvc5', 'z3'], required=True)
    p.add_argument('--budget-seconds', type=float, default=1200)
    p.add_argument('--output-dir', type=Path)
    a = p.parse_args()
    source = BASE / 'artifacts/SOURCE_PROGRAMS.json'
    target = BASE / 'artifacts/TARGET_INPUT.json'
    orders = json.loads(source.read_text())['header_orders']
    dest = a.output_dir or BASE / 'artifacts' / a.engine
    dest.mkdir(parents=True, exist_ok=True)
    script = BASE / 'src' / ('run.py' if a.engine == 'cvc5' else 'independent_z3.py')
    def one(item):
        i, order = item
        out = dest / f'case_{i:02}.json'
        assert not out.exists(), 'Do not overwrite a prior case'
        command = [sys.executable, str(script), '--source', str(source), '--target', str(target),
                   '--header-order', ','.join(order), '--output', str(out),
                   '--budget-seconds', str(a.budget_seconds)]
        started = time.monotonic()
        with tempfile.TemporaryFile() as errors:
            try:
                completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=errors,
                                           timeout=a.budget_seconds + 20)
                failure = 'ENGINE_ERROR' if completed.returncode else None
            except subprocess.TimeoutExpired:
                failure = 'EXTERNAL_TIMEOUT'
            if failure and not out.exists():
                errors.seek(0)
                result = {'schema': 'GDT899_EXTERNAL_EXECUTION_STATUS_V1', 'solver': a.engine,
                          'header_order': order, 'status': 'UNKNOWN_' + failure,
                          'elapsed_seconds': time.monotonic() - started,
                          'budget_seconds': a.budget_seconds,
                          'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                          'target_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                          'stderr_sha256': hashlib.sha256(errors.read()).hexdigest()}
                out.write_text(json.dumps(result, indent=2) + '\n')
        result = json.loads(out.read_text())
        print(a.engine, i, result.get('status', result.get('first_status')), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(one, enumerate(orders)))
if __name__ == '__main__':
    main()
