"""Separate set-based complete enumerator; imports no primary model."""
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]


def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def enumerate_sets(roles, atoms, deadline=float('inf')):
    factors = []
    support = {str(c['index']): 0 for role in roles for c in role}
    eligible_total = surviving_total = 0
    sets = {c['index']: {a: set(v) for a, v in c['domains'].items()} for role in roles for c in role}
    for prefix in itertools.product(*roles[:-1]):
        if time.monotonic() > deadline:
            raise TimeoutError('independent validation ceiling')
        eligible_indices = []
        surviving_indices = []
        if len({c['leaf'] for c in prefix}) == len(prefix):
            prefix_domains = {}
            for a in atoms:
                present = [sets[c['index']][a] for c in prefix if a in sets[c['index']]]
                prefix_domains[a] = set.intersection(*present) if present else None
            for j, last in enumerate(roles[-1]):
                if any(last['leaf'] == c['leaf'] for c in prefix):
                    continue
                eligible_indices.append(j)
                allowed = True
                for a in atoms:
                    first = prefix_domains[a]
                    final = sets[last['index']].get(a)
                    if first is None:
                        valid = final is None or bool(final)
                    elif final is None:
                        valid = bool(first)
                    else:
                        valid = not first.isdisjoint(final)
                    if not valid:
                        allowed = False
                        break
                if allowed:
                    surviving_indices.append(j)
                    for c in (*prefix, last):
                        support[str(c['index'])] += 1
        eligible_total += len(eligible_indices)
        surviving_total += len(surviving_indices)
        encode = lambda positions: format(sum(2**j for j in positions), 'x')
        factors.append([*[c['index'] for c in prefix], encode(eligible_indices), encode(surviving_indices)])
    return dict(factors=factors, case_support=support, distinct_leaf_tuples=eligible_total, surviving_tuples=surviving_total)


def main():
    started = time.monotonic()
    lock = read(E/'src/PREREG_LOCK.json')
    for path, expected in lock['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, path
    inp = read(E/'artifacts/INPUT_DOMAINS.json.gz')
    source = read(ROOT/'experiments/yolo/gdt963_dioscorides_complete_content_code/src/SOURCE.json')
    from collections import Counter
    counts = {r['id']: Counter(r['atoms']) for r in source['records']}
    atoms = sorted(a for a in set().union(*counts.values()) if sum(c[a] >= 2 for c in counts.values()) >= 2)
    assert inp['atoms'] == atoms and len(atoms) == 13
    old = read(ROOT/'experiments/yolo/gdt1096_dioscorides_finite_recurrent_domains/artifacts/CASES.json')
    cert = read(ROOT/'experiments/yolo/gdt1096_dioscorides_finite_recurrent_domains/artifacts/CERTIFICATES.json.gz')
    import re
    expected = []
    for record in counts:
        expected.append([dict(index=i, page=r['page'], leaf=re.match(r'f\d+',r['page']).group(),
                              domains={a: cert[str(i)]['final_domains'][a] for a in atoms if counts[record][a] >= 2})
                         for i,r in enumerate(old) if r['edition']=='IT2a' and r['record']==record and r['status']=='NECESSARY_DOMAINS_NONEMPTY'])
    assert inp['roles'] == expected
    result = enumerate_sets(expected, atoms, started + 120)
    saved = read(E/'artifacts/SUPPORT_FACTORS.json.gz')
    assert result == saved
    report = read(E/'artifacts/RESULT.json')
    assert report['distinct_leaf_tuples'] == result['distinct_leaf_tuples']
    assert report['surviving_tuples'] == result['surviving_tuples']
    assert report['retained_fraction'] == result['surviving_tuples']/result['distinct_leaf_tuples']
    rows = read(E/'artifacts/ALL_CASES.json.gz')
    assert len(rows) == len(old) == 1428
    for i, (new, original) in enumerate(zip(rows, old)):
        assert new['parent'] == original and new['index'] == i
        assert new['projected_tuple_support'] == result['case_support'].get(str(i))
    status = 'FINITE_SHARED_DOMAIN_CONJUNCTION_EMPTY' if not result['surviving_tuples'] else ('SHARED_DOMAIN_PROJECTION_WEAK' if report['retained_fraction'] >= .9 else 'SHARED_DOMAIN_CANDIDATES_REMAIN')
    assert report['status'] == status
    outcome = dict(status='PASS_FINITE_CONSEQUENCE_ONLY', checked_original_rows=1428,
                   checked_prefix_factors=len(result['factors']), checked_complete_tuple_universe=report['total_tuples'],
                   checked_shared_atoms=13, full_code_witnesses=0, confirmed_words=0,
                   wall_seconds=time.monotonic()-started)
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(outcome,indent=2)+'\n')
    print(json.dumps(outcome),flush=True)


if __name__ == '__main__':
    main()
