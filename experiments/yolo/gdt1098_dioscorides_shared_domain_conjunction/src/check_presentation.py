"""Disclosed post-result accounting/illustration checks; no scientific rerun."""
import csv
import gzip
import json
import math
from collections import Counter
from pathlib import Path

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
P=E/'artifacts'


def read(name):
    b=(P/name).read_bytes()
    return json.loads(gzip.decompress(b) if name.endswith('.gz') else b)


def main():
    inp=read('INPUT_DOMAINS.json.gz');fact=read('SUPPORT_FACTORS.json.gz');r=read('RESULT.json');cases=read('ALL_CASES.json.gz')
    assert math.prod(map(len,inp['roles']))==r['total_tuples']
    assert r['same_leaf_tuples']==r['total_tuples']-r['distinct_leaf_tuples']
    assert r['empty_common_domain_tuples']==r['distinct_leaf_tuples']-r['surviving_tuples']
    assert len(fact['factors'])==math.prod(map(len,inp['roles'][:-1]))
    assert r['source_shared_occurrences']==sum(sum(v.values()) for v in inp['participation'].values())==175
    assert all(sum(fact['case_support'][str(c['index'])] for c in role)==r['surviving_tuples'] for role in inp['roles'])
    solver=json.loads(gzip.decompress((ROOT/'experiments/yolo/gdt1097_dioscorides_complete_interval_code/artifacts/SOLVER_RESULTS.json.gz').read_bytes()))
    counts=Counter()
    for c in inp['roles'][0]:counts[solver[str(c['index'])]['status']]+=fact['case_support'][str(c['index'])]
    assert dict(counts)==r['surviving_tuples_by_inherited_iris_solver_status']
    for c in cases:assert c['inherited_iris_solver_status']==(solver[str(c['index'])]['status'] if str(c['index']) in solver else None)
    with (P/'CANDIDATES.tsv').open() as stream:
        table=list(csv.DictReader(stream,delimiter='\t'))
    assert len(table)==len(cases)==1428
    for t,c in zip(table,cases):
        d=c['parent']
        assert t==dict(zip(t.keys(),map(str,(c['index'],d['edition'],d['page'],d['record'],d['status'],c['projected_tuple_support'],c['inherited_iris_solver_status']))))
    byid={c['index']:c for role in inp['roles'] for c in role}
    for ex in read('ILLUSTRATIONS.json')['examples'].values():
        chosen=[byid[i] for i in ex['indices']]
        domains={a:sorted(set.intersection(*(set(c['domains'][a]) for c in chosen if a in c['domains']))) for a in inp['atoms']}
        assert domains==ex['common_domains']
        assert [a for a,v in domains.items() if not v]==ex['empty_atoms']
    print(json.dumps(dict(status='PASS_PRESENTATION_AND_ILLUSTRATIONS',case_rows=1428,prefix_factors=len(fact['factors']),full_tuple_universe=r['total_tuples'])))


if __name__=='__main__':
    main()
