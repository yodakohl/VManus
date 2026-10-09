import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def read(p):return json.loads(p.read_text())
lock=read(P/'src/REGISTRATION_LOCK.json')
for f,h in lock['sha256'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h
oldpath='experiments/yolo/gdt1250_cache_reset_doublet_conflict/artifacts/WITNESSES.json'
old=read(ROOT/oldpath);manifest=read(ROOT/'experiments/yolo/gdt1250_cache_reset_doublet_conflict/experiment.json')
entry=next(e for e in manifest['outputs'] if e['path']==oldpath);assert hashlib.sha256((ROOT/oldpath).read_bytes()).hexdigest()==entry['sha256']
r=read(P/'artifacts/RESULT.json');assert len(r['cases'])==3
for c in r['cases']:
    o=next(x for x in old if x['edition']==c['reader'] and x['form']==c['form'])
    assert c['complete_line']==sorted(o['doublet_line'],key=lambda x:int(x['source_group_index']))
    index=o['doublet']['index'];by={int(x['source_group_index']):x for x in o['doublet_line']}
    assert c['first_group_index']==index and c['locus']==o['doublet']['locus']
    assert by[index]['ivtff_group_raw']==by[index+1]['ivtff_group_raw']=='qokeedy'
    for i in [index-1,index,index+1]:assert by[i]['right_separator']=='DEFINITE_SPACE' and by[i+1]['left_separator']=='DEFINITE_SPACE'
    assert all(x['kind']=='P' and x['locus']==c['locus'] for x in by.values())
    expected=('q','o','k','e','e','d','y');assert tuple(c['working_units'])==expected
    assert c['width']==c['lower_bound_r']==7
assert r['necessary_reference_width']==7 and r['excluded_maxima']==[0,1,2,3,4,5,6]
assert r['status']=='REFERENCE_WIDTH_AT_LEAST_SEVEN_UNDER_STRICT_SAVING_POLICY'
v={'status':'PASS','reader_witnesses':3,'scope':'Independent source-index/seam/hash and reduction check; sameauthor, no paleographic, semantic or probability validation. General proof separately reviewed.'}
(P/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
