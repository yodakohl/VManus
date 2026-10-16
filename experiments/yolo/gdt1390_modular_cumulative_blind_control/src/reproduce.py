#!/usr/bin/env python3
"""Post-result replay of frozen search; does not read TRUTH or change originals.

Example (fresh output directory, explicit 15-minute wall budget):
  python experiments/yolo/gdt1390_modular_cumulative_blind_control/src/reproduce.py \
    --output gdt1390-replay --seconds 900 --workers 32

This bypasses only run.py's historical calendar deadline. All 576 starts,
seeds, proposals and scoring remain in the hash-verified frozen engine.
Exact replay assumes the original C++ standard-library/compiler behavior;
scientific floating fields are compared at absolute tolerance 1e-7.
"""
import argparse
import concurrent.futures
import importlib.util
import json
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--seconds', type=float, required=True)
    p.add_argument('--workers', type=int, default=32)
    args = p.parse_args()
    assert args.seconds > 0 and 1 <= args.workers <= 32
    assert not args.output.exists(), 'Use a fresh output directory'
    spec = importlib.util.spec_from_file_location('frozen_driver', HERE / 'run.py')
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    driver.check_lock()
    lock = driver.read(driver.A / 'RECOVERY_LOCK.json')
    for item in lock['files']:
        assert driver.sha(driver.ROOT / item['path']) == item['sha256']
    recovery = driver.read(driver.A / 'RECOVERY.json')
    original = driver.read(driver.A / 'RESTARTS.json')['results']
    cases_path = driver.A / 'CASES.json'
    assert driver.sha(cases_path) == recovery['cases_sha256']
    cases = driver.read(cases_path)['cases']
    assert len(cases) == 18 and len(original) == 576
    started = time.monotonic()
    deadline = started + args.seconds
    args.output.mkdir(parents=True)
    driver.R = args.output.resolve()
    executable = driver.compile_engine()
    _, shape, tables = driver.public_models()
    driver.model_binary(shape, tables, driver.R / 'model.bin')
    driver.cases_binary(cases, driver.R / 'cases.bin')

    def run(pair):
        ci, ri = pair
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Explicit replay budget exhausted')
        out = subprocess.run([str(executable), '--start', str(driver.R / 'model.bin'),
                              str(driver.R / 'cases.bin'), str(ci), str(ri)],
                             check=True, capture_output=True, text=True, timeout=remaining)
        result = json.loads(out.stdout)
        result['status'] = 'COMPLETE'
        return result

    def compare(actual, expected):
        if isinstance(expected, dict):
            assert set(actual) == set(expected)
            for key in expected:
                if key not in ('wall_seconds', 'cpu_seconds'):
                    compare(actual[key], expected[key])
        elif isinstance(expected, list):
            assert len(actual) == len(expected)
            for a, b in zip(actual, expected):
                compare(a, b)
        elif isinstance(expected, float):
            assert abs(actual - expected) <= 1e-7, (actual, expected)
        else:
            assert actual == expected, (actual, expected)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(run, [(c, s) for c in range(18) for s in range(32)]))
    original.sort(key=lambda x: (x['case_index'], x['start_index']))
    compare(results, original)
    for ci, expected in enumerate(recovery['cases']):
        best = min(results[ci * 32:(ci + 1) * 32],
                   key=lambda r: (-r['winner']['score'], r['winner']['weights'], r['winner']['b']))
        actual = {'id': cases[ci]['id'], 'case_index': ci,
                  'message_length': len(cases[ci]['units']),
                  'winning_start_index': best['start_index'], **best['winner']}
        compare(actual, expected)
    driver.save(driver.R / 'REPLAY_RESTARTS.json', {'results': results})
    receipt = {'status': 'PASS_FROZEN_SEARCH_REPLAY', 'restarts': len(results),
               'absolute_float_tolerance': 1e-7, 'truth_access': False,
               'recovery_lock_sha256': driver.sha(driver.A / 'RECOVERY_LOCK.json'),
               'replay_script_sha256': driver.sha(Path(__file__)),
               'wall_seconds': time.monotonic() - started,
               'explicit_budget_seconds': args.seconds,
               'excluded_comparison_fields': ['wall_seconds', 'cpu_seconds']}
    driver.save(driver.R / 'REPLAY_VALIDATION.json', receipt)
    print(json.dumps(receipt, sort_keys=True))

if __name__ == '__main__':
    main()
