#!/usr/bin/env python3
"""Direct ground-witness and complete case-accounting checks, no model import."""
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
PARENT=ROOT/'experiments/yolo/gdt963_dioscorides_complete_content_code'
DOMAINS=ROOT/'experiments/yolo/gdt1096_dioscorides_finite_recurrent_domains'


def read(path):
    b=path.read_bytes()
    return json.loads(gzip.decompress(b) if path.suffix=='.gz' else b)


def ground(atoms,text,code,alignment,domains):
    assert set(code)==set(atoms) and all(isinstance(v,str) and v for v in code.values())
    assert len(set(code.values()))==len(code)
    for a,u in code.items():
        for b,v in code.items():
            assert a==b or not u.startswith(v)
    assert ''.join(code[a] for a in atoms)==text
    assert len(alignment)==len(atoms)
    position=0
    for i,(atom,row) in enumerate(zip(atoms,alignment)):
        assert row==dict(index=i,atom=atom,start=position,end=position+len(code[atom]),code=code[atom])
        position+=len(code[atom])
    assert position==len(text)
    for atom,values in domains.items():
        assert code[atom] in values
    return {'atoms':len(atoms),'types':len(code),'target_characters':len(text),
            'singleton_characters':sum(len(code[a]) for a,n in Counter(atoms).items() if n==1)}


def main():
    lock=read(E/'src/PREREG_LOCK.json')
    for path,expected in lock['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
    original=read(DOMAINS/'artifacts/CASES.json')
    cases=read(E/'artifacts/ALL_CASES.json.gz')
    results=read(E/'artifacts/SOLVER_RESULTS.json.gz')
    domains=read(DOMAINS/'artifacts/CERTIFICATES.json.gz')
    spec=read(E/'src/SPEC.json')
    frames={r['id']:r for r in read(PARENT/'artifacts/TARGET_FRAMES.json.gz')}
    atoms=next(r['atoms'] for r in read(PARENT/'src/SOURCE.json')['records'] if r['id']=='I.1')
    selected=[i for i,r in enumerate(original) if r['edition']=='IT2a' and r['record']=='I.1'
              and r['status']=='NECESSARY_DOMAINS_NONEMPTY']
    assert selected==spec['all_selected_case_indices']
    assert set(results)==set(map(str,selected)) and len(cases)==len(original)==1428
    ground_results={}
    for i,(old,new) in enumerate(zip(original,cases)):
        assert new['index']==i and new['parent_domain_status']==old['status']
        assert all(new[k]==v for k,v in old.items() if k!='status')
        if i not in selected:
            assert new['status']=='INHERITED_NOT_RETESTED'
            continue
        result=results[str(i)]
        assert new['status']==result['status']
        frame=frames[old['target_id']]
        assert frame['eligible'] and not frame['page'].startswith('f84') and frame['page']!='f116v'
        if result['status'] in ('OPTIMAL','FEASIBLE'):
            ground_results[str(i)]=ground(atoms,frame['text'],result['full_code'],result['alignment'],
                                          domains[str(i)]['final_domains'])
        elif result['status']=='INFEASIBLE':
            assert result['full_code'] is None and 'status: INFEASIBLE' in result['response_stats']
        else:
            assert result.get('full_code') is None
    table=list(csv.DictReader((E/'artifacts/CANDIDATES.tsv').open(),delimiter='\t'))
    assert len(table)==len(cases)
    for row,case in zip(table,cases):
        assert all(row[k]==str(case[k]) for k in row)
    summary=read(E/'artifacts/RESULT.json')
    counts=Counter(r['status'] for r in results.values())
    assert dict(counts)==summary['statuses'] and summary['newly_tested']==7
    assert summary['full_local_witnesses']==len(ground_results)
    assert summary['it_literal_conjunction']==('SOLVER_INFEASIBLE' if counts['INFEASIBLE']==7 else 'UNRESOLVED')
    assert summary['source_unknown_cases_inherited']==1016
    receipt=read(E/'artifacts/EXECUTION_RECEIPT.json')
    assert receipt['target_runs']==1 and receipt['maximum_solver_workers']==28
    report=dict(status='PASS',lock_files=len(lock['files']),all_cases_checked=len(cases),
                selected_cases_checked=len(selected),ground_witnesses=ground_results,
                solver_infeasible_reports_checked=counts['INFEASIBLE'],
                independent_unsat_certificates=0,independent_meaning_confirmation=False,
                ceiling='Ground SAT and accounting validation; negative solver claims are not independently proved.')
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':
    main()
