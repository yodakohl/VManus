#!/usr/bin/env python3
"""Integrity and arithmetic validator for GDT230."""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(n):
    with (ROOT/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def main():
    result=json.loads((ROOT/'gdt230_result.json').read_text()); atlas=read('gdt230_content_host_atlas.tsv'); source=read('gdt229_q13_semantic_role_lattice.tsv'); checks=[]
    groups=sum(len(r['page_hosts'].split('|')) for r in source)
    checks += [('groups_1896',groups==result['group_occurrences']==1896),('eligible_count',len(atlas)==result['eligible_hosts'])]
    checks.append(('eligibility',all(int(r['occurrences'])>=5 and int(r['folios'])>=3 for r in atlas)))
    checks.append(('no_f84',all(not r['page'].startswith('f84') and not r['locus'].startswith('f84') for r in source)))
    checks.append(('no_gloss',all(r['claim_state']=='OPAQUE_ADDRESS_CANDIDATE_NO_GLOSS' for r in atlas)))
    counts=Counter(r['priority_status'] for r in atlas); checks.append(('status_counts',dict(sorted(counts.items()))==result['status_counts']))
    top=[r for r in atlas if r['priority_status'] in {'EXTERNAL_CONTENT_TEST_PRIORITY','PLACEMENT_STABLE_NUISANCE_EXPLAINED'}]
    checks.append(('top_ids',[r['page_host'] for r in top]==result['top_stable_hosts']))
    checks.append(('all_top_nonpositive',all(float(r['host_increment'])<=0 for r in top)))
    for kind in ('inputs','outputs','documents','implementation'):
        for name,digest in result[kind].items():checks.append((f'hash:{name}',sha(name)==digest))
    clean=dict(result);stored=clean.pop('content_hash'); checks.append(('content_hash',stored==hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
    checks += [(f'f84_{k}_false',v is False) for k,v in result['f84'].items()]
    failed=[n for n,ok in checks if not ok]; out={'experiment':result['experiment'],'status':'PASS' if not failed else 'FAIL','checks_passed':sum(ok for _,ok in checks),'checks_total':len(checks),'failed':failed,'result_sha256':sha('gdt230_result.json')}
    (ROOT/'gdt230_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    if failed:raise SystemExit('FAIL '+','.join(failed))
    print(f"PASS {out['checks_passed']}/{out['checks_total']}")
if __name__=='__main__':main()
