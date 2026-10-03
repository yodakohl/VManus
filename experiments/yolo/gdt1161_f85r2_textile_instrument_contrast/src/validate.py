#!/usr/bin/env python3
"""Separate direct accounting; does not import the runner or certify vision."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1]; R=B.parents[2]
s=json.loads((B/'SPEC.json').read_text()); r=json.loads((B/'artifacts/RESULT.json').read_text())
p=[json.loads((B/'artifacts'/('OBSERVER_'+x+'.json')).read_text()) for x in ('ROOT','B')]
checks=[]
def check(name,value):
    checks.append({'check':name,'pass':bool(value)})
for path,h in r['bindings'].items():
    check('hash:'+path,hashlib.sha256((R/path).read_bytes()).hexdigest()==h)
for i in json.loads((B/'src/IMAGE_SOURCES.json').read_text())['images']:
    check('image:'+i['path'],hashlib.sha256((R/i['path']).read_bytes()).hexdigest()==i['sha256'])
for obs in p:
    check('complete:'+obs['observer'],set(obs['features'])==set(s['features']))
    for k,v in obs['features'].items():
        check(obs['observer']+':'+k,v['value'] in s['values'] and bool(v['visible']) and bool(v['uncertain']) and (v['value']!='ABSENT' or v['usable_entire_object_area']))
for row in r['features']:
    k=row['feature']; a=p[0]['features'][k]['value']; b=p[1]['features'][k]['value']
    check('row:'+k,row=={'feature':k,'ROOT':a,'B':b,'agree':a==b})
yes=True
for obs in p:
    for k in s['textile_required']:
        yes = yes and obs['features'][k]['value']=='PRESENT'
no=True
for obs in p:
    f=obs['features']; no=no and f['E_vessel']['value']=='PRESENT' and f['E_frame']['value']=='ABSENT' and f['E_frame']['usable_entire_object_area']
expected='TEXTILE_JOINT_SUPPORTED' if yes else 'TEXTILE_JOINT_CONTRADICTED' if no else 'NO_DISTINCTIVE_TEXTILE_SUPPORT_OR_CAPACITY'
check('exclusive',not(yes and no));check('decision',r['status']==expected)
check('no_semantic_export',r['confirmed_words']==r['independent_confirmation_leaves']==r['new_target_admissions']==0)
v={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','checks':checks,'scope':'Manual-record completeness, source hashes and decision arithmetic, not image truth.'}
(B/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n'); print(v['status'],len(checks));assert v['status']=='PASS'
