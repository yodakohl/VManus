#!/usr/bin/env python3
"""Necessary OR streak bound; not a nominal parser."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'vmanus-work').is_file())
BASE = Path(__file__).resolve().parents[1]
COLS = ['source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def streaks(groups, columns, expansion):
    c = {name:i for i,name in enumerate(columns)}
    output, pending = [], []
    def flush():
        if pending:
            output.append(list(pending))
            pending.clear()
    for i,g in enumerate(groups):
        if i and not (groups[i-1][c['right_separator']]=='DEFINITE_SPACE' and
                      g[c['left_separator']]=='DEFINITE_SPACE'):
            flush()
        for j,symbol in enumerate(expansion.get(g[c['ivtff_group_raw']], ['OTHER'])):
            if symbol=='OR':
                pending.append({'source_group_id':g[c['source_group_id']], 'component_index':j})
            else:
                flush()
    flush()
    return output

def controls(expansion):
    ds='DEFINITE_SPACE'
    tests=[
        ('two_bound_endpoints',['dalor','orar'],[ds],[2]),
        ('three_mixed_marks',['dalor','or','oraiin'],[ds,ds],[3]),
        ('three_free_marks',['or','or','or'],[ds,ds],[3]),
        ('written_ar_breaks_run',['orar','or'],[ds],[1,1]),
        ('two_written_links',['dal','or','ar','or','aiin'],[ds]*4,[1,1]),
        ('drawing_break',['or','or'],['DRAWING_INTERRUPTION'],[1,1]),
        ('uncertain_break',['or','or'],['UNCERTAIN_SMALL_SPACE'],[1,1]),
        ('physical_line_break',['or','or'],['LINE_END'],[1,1]),
        ('dor_is_not_split',['dor','or'],[ds],[1]),
        ('oror_is_not_split',['oror'],[],[]),
        ('single_bound_mark',['oraiin'],[],[1])]
    cases=[]
    for name,raw,seams,expected in tests:
        gs=[[f'CONTROL|{name}|{i+1}',str(i+1),w,
             seams[i-1] if i else 'LINE_START',
             seams[i] if i<len(seams) else 'LINE_END'] for i,w in enumerate(raw)]
        actual=[len(x) for x in streaks(gs,COLS,expansion)]
        cases.append(dict(name=name,raw_groups=raw,seams=seams,
            expected_run_lengths=expected,actual_run_lengths=actual,**{'pass':actual==expected}))
    assert all(x['pass'] for x in cases)
    return dict(experiment_id='GDT1384',cases=cases,all_pass=True)

def main():
    cp=BASE/'src/CONTRACT.json';cfg=json.loads(cp.read_text())
    assert cfg['maximum_or_run']==2
    assert cfg['sealed_data']=={'f84':'FORBIDDEN','f84r':'FORBIDDEN'}
    assert digest(ROOT/cfg['candidate_file'])==cfg['candidate_sha256']
    expansion=cfg['finite_expansion'];control_result=controls(expansion)
    stats={};seen=set()
    for item in cfg['inputs']:
        path=ROOT/item['path'];assert digest(path)==item['sha256'],item['path']
        source=json.loads(path.read_text());reader=item['reader']
        d=stats.setdefault(reader,dict(prose_lines=0,raw_groups=0,or_components=0,
            run_lengths=Counter(),max_run=0,violating_runs=0,multiple_runs=[]))
        c={name:i for i,name in enumerate(source['group_columns'])}
        for line in source['lines']:
            m=line['metadata'];assert not m['page'].startswith('f84')
            assert m['edition']==reader
            if m['kind']!=cfg['kind']:continue
            gs=line['groups']
            for g in gs:
                gid=g[c['source_group_id']];assert gid not in seen,gid;seen.add(gid)
            d['prose_lines']+=1;d['raw_groups']+=len(gs)
            for run in streaks(gs,source['group_columns'],expansion):
                n=len(run);d['or_components']+=n;d['run_lengths'][str(n)]+=1
                d['max_run']=max(d['max_run'],n);d['violating_runs']+=n>2
                if n>=2:d['multiple_runs'].append(dict(page=m['page'],locus=m['locus'],
                    source=item['path'],length=n,components=run,
                    raw_line=[g[c['ivtff_group_raw']] for g in gs],
                    group_ids=[g[c['source_group_id']] for g in gs],
                    separators=[[g[c['left_separator']],g[c['right_separator']]] for g in gs]))
    for d in stats.values():
        d['run_lengths']=dict(sorted(d['run_lengths'].items(),key=lambda x:int(x[0])))
        d['multiple_runs'].sort(key=lambda x:(x['page'],x['locus'],
            x['components'][0]['source_group_id'],x['components'][0]['component_index']))
    status='CAP_VIOLATION' if any(d['violating_runs'] for d in stats.values()) else 'NO_CAP_VIOLATION_IN_FIXED_SAME_LINE_SCOPE'
    result=dict(schema_version=1,experiment_id='GDT1384',status=status,
        contract_sha256=digest(cp),scope=cfg['scope'],by_reader=stats,
        claim_ceiling='Necessary finite-realization bound only; no meaning, endpoint ownership or complete grammar.')
    (BASE/'artifacts/RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (BASE/'artifacts/CONTROLS.json').write_text(json.dumps(control_result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(status=status,by_reader={r:{k:v for k,v in d.items() if k!='multiple_runs'} for r,d in stats.items()}),indent=2))

if __name__=='__main__':
    main()
