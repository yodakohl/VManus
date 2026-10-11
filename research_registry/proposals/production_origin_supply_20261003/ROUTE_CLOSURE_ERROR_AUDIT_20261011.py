"""Bounded source-free spot check of the existing GDT892 CSP engine.

No native payloads, gold, images, reserves, or file outputs. This does not replay
GDT906's complete native enumeration or validate its linguistic assumptions.
Run from repository root with PYTHONDONTWRITEBYTECODE=1 python <this path>.
"""
import importlib.util
import itertools
import random
import sys
from pathlib import Path

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[3]
path = root / 'experiments/yolo/gdt892_joint_abugida_paradigm_reconstruction/src/csp.py'
spec = importlib.util.spec_from_file_location('audit_csp', path)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
rng = random.Random(11102026)
cases = 0
for nvars in range(6):
    for trial in range(40):
        nvalues = 5
        tables = []
        for _ in range(rng.randrange(1, 5)):
            scope = sorted(rng.sample(range(nvars), rng.randrange(min(nvars, 3) + 1)))
            rows = [row for row in itertools.product(range(nvalues), repeat=len(scope))
                    if rng.random() < .25]
            tables.append({'vars': scope, 'rows': rows})
        expected = set()
        for assignment in itertools.permutations(range(nvalues), nvars):
            if all(tuple(assignment[i] for i in table['vars']) in table['rows']
                   for table in tables):
                expected.add(assignment)
        actual = engine.solve_tables(tables, nvars, nvalues, float('inf'))
        assert actual['status'] == 'COMPLETE'
        assert set(actual['solutions']) == expected, (nvars, trial)
        cases += 1
print({'audited_csp_small_cases': cases, 'exact_exhaustive_match': True,
       'native_data_read': False, 'files_written': False})
