"""Single publicly registered finite domain conjunction."""
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
from model import compute

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def save(name, value):
    data = (json.dumps(value, ensure_ascii=False, separators=(',', ':'))+'\n').encode()
    (E/'artifacts'/name).write_bytes(gzip.compress(data, mtime=0) if name.endswith('.gz') else data)


def main():
    lock = read(E/'src/PREREG_LOCK.json')
    for path, expected in lock['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, path
    assert not (E/'artifacts/RESULT.json').exists(), 'one target conjunction only'
    inp = read(E/'artifacts/INPUT_DOMAINS.json.gz')
    old = read(ROOT/'experiments/yolo/gdt1096_dioscorides_finite_recurrent_domains/artifacts/CASES.json')
    solver = read(ROOT/'experiments/yolo/gdt1097_dioscorides_complete_interval_code/artifacts/SOLVER_RESULTS.json.gz')
    start_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    result = compute(inp['roles'], inp['atoms'], started + 120)
    save('SUPPORT_FACTORS.json.gz', result)
    total = math.prod(len(role) for role in inp['roles'])
    remaining = result['surviving_tuples']
    fraction = remaining / result['distinct_leaf_tuples']
    counts = Counter()
    for c in inp['roles'][0]:
        counts[solver[str(c['index'])]['status']] += result['case_support'][str(c['index'])]
    status = 'FINITE_SHARED_DOMAIN_CONJUNCTION_EMPTY' if not remaining else ('SHARED_DOMAIN_PROJECTION_WEAK' if fraction >= .9 else 'SHARED_DOMAIN_CANDIDATES_REMAIN')
    summary = dict(status=status, source_shared_atoms=len(inp['atoms']), source_shared_occurrences=inp['shared_recurrent_occurrences'],
                   original_cases=len(old), role_case_counts=[len(role) for role in inp['roles']],
                   total_tuples=total, distinct_leaf_tuples=result['distinct_leaf_tuples'],
                   same_leaf_tuples=total-result['distinct_leaf_tuples'], surviving_tuples=remaining,
                   empty_common_domain_tuples=result['distinct_leaf_tuples']-remaining, retained_fraction=fraction,
                   surviving_tuples_by_inherited_iris_solver_status=dict(counts),
                   full_code_witnesses=0, confirmed_words=0, independent_confirmation_leaves=0,
                   meaning_test=False, significance_claim=False, wall_seconds=time.monotonic()-started)
    save('RESULT.json',summary)
    rows = [dict(index=i,parent=r,projected_tuple_support=result['case_support'].get(str(i)),
                 inherited_iris_solver_status=solver[str(i)]['status'] if str(i) in solver else None)
            for i,r in enumerate(old)]
    save('ALL_CASES.json.gz',rows)
    header = ['index','edition','page','record','parent_status','projected_tuple_support','inherited_iris_solver_status']
    table = ['\t'.join(header)]
    for row in rows:
        r=row['parent'];table.append('\t'.join(str(v) for v in (row['index'],r['edition'],r['page'],r['record'],r['status'],row['projected_tuple_support'],row['inherited_iris_solver_status'])))
    (E/'artifacts/CANDIDATES.tsv').write_text('\n'.join(table)+'\n')
    save('EXECUTION_RECEIPT.json',dict(started_utc=start_utc,finished_utc=datetime.now(timezone.utc).isoformat(),
         registration_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         lock_sha256=hashlib.sha256((E/'src/PREREG_LOCK.json').read_bytes()).hexdigest(), target_conjunction_runs=1))
    print(json.dumps(summary),flush=True)


if __name__ == '__main__':
    main()
