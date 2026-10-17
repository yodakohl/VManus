#!/usr/bin/env python3
"""One invariant-core gate; reuse the unchanged previously validated solver."""
import argparse,hashlib,importlib.util,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def kept(g):return bool(g) and g[-2:]!=['d','y'] and not any(a==b and a in ('e','i') for a,b in zip(g,g[1:]))
def predicate_controls():
    examples=[([],False),(['e'],True),(['i'],True),(list('ee'),False),(list('ii'),False),(list('dy'),False),(list('dya'),True),(list('ady'),False),(list('dydy'),False),(list('dyad'),True),(list('aa'),True),(list('ei'),True),(list('ie'),True),(list('eea'),False),(list('aii'),False),(['ch','e','y'],True)]
    for group,expected in examples:assert kept(group)==expected
    return dict(status='PASS',checks=len(examples),scope='New eligibility predicate only; old solver controls inherited unchanged.')
def library(path):
    spec=importlib.util.spec_from_file_location('unchanged_primary',ROOT/path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
    ap=argparse.ArgumentParser();p=ap.add_mutually_exclusive_group(required=True);p.add_argument('--gate',action='store_true');p.add_argument('--native',action='store_true');args=ap.parse_args()
    lock=read(E/'LOCK.json')
    for name,digest in lock['files'].items():assert sha(ROOT/name)==digest,name
    s=read(E/'src/SPEC.json');old=library(s['primary_library_path']);W=old.sources(s)
    if args.gate:
        control=read(ROOT/s['old_control_path']);ids=[i for i,g in enumerate(control['encoded_groups']) if kept(g)];groups=[control['encoded_groups'][i] for i in ids]
        planted=control['planted_key']
        assert all(''.join(planted[u] for u in g)==control['source_words'][i] for i,g in zip(ids,groups))
        result=old.solve(groups,W['deot'],s['signs'],'BIDIR',s) if len(groups)>=2 and len(set(map(tuple,groups)))>=2 else dict(status='UNKNOWN',reason='insufficient_control_subset')
        save('CONTROL_SUBSET.json',dict(experiment_id='GDT1417',source='deot',old_control_sha256=sha(ROOT/s['old_control_path']),selected_indices=ids,groups=groups,result=result,candidate_scope='ANYordinarykey control subset only',predicate_controls=predicate_controls()));print(json.dumps(dict(control_status=result['status'],positions=len(groups))));return
    assert read(A/'GATE_VALIDATION.json')['status']=='PASS'
    worksheet=read(ROOT/s['worksheet_path']);units=[u for u in worksheet['units'] if u['unit_id']==s['passage_unit']];assert len(units)==1
    rx=re.compile('|'.join(re.escape(u) for u in sorted(s['signs'],key=lambda u:(-len(u),u))));original=[];parsed=[]
    for line in units[0]['lines']:
        assert line['metadata']['edition']=='IT2a' and line['metadata']['page']=='f75v'
        for row in line['original_groups']:
            g=rx.findall(row[2]);assert ''.join(g)==row[2];original.append(row);parsed.append(g)
    assert len(parsed)==77
    ids=[i for i,g in enumerate(parsed) if kept(g)];groups=[parsed[i] for i in ids];cases=[]
    for name in s['source_names']:
        for mode in s['modes']:
            result=old.solve(groups,W[name],s['signs'],mode,s);cases.append(dict(source=name,mode=mode,result=result));print(json.dumps(dict(source=name,mode=mode,status=result['status'])),flush=True)
    save('RESULT.json',dict(experiment_id='GDT1417',status='JOINT_UNCHANGED_CORE_CAPACITY',original_groups=original,original_units=parsed,positions_zero_based=ids,freed_positions=[i for i in range(77) if i not in ids],groups=groups,cases=cases,claim_ceiling=s['claim_ceiling']))
if __name__=='__main__':main()
