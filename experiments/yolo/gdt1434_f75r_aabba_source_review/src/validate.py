#!/usr/bin/env python3
"""Independent source/chronology/category check; never validates perception."""
from pathlib import Path
import datetime,hashlib,json
from PIL import Image
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def t(v):
 x=datetime.datetime.fromisoformat(v.replace('Z','+00:00'));assert x.tzinfo is not None;return x
l=read(E/'src/PROTOCOL_LOCK.json');s=read(E/'src/SPEC.json')
for p,h in l['pins'].items():
 q=Path(p);assert not q.is_absolute() and '..' not in q.parts;assert sha(R/q)==h,p
assert s['canvas_id']=='1006208' and s['label']=='75r' and s['overview_dimensions']==[2852,3759]
assert s['sealed_data']=={'f84':'FORBIDDEN','f84r':'FORBIDDEN'} and s['confirmed_words']==0
base='https://collections.library.yale.edu/iiif/2/1006208/'
def source(k,url,dims):
 v=read(A/(k+'_SOURCE.json'));p=R/v['path'];assert p.parent.resolve()==A.resolve() and '..' not in Path(v['path']).parts and not Path(v['path']).is_absolute()
 assert v['url']==url and [v['width'],v['height']]==dims and sha(p)==v['sha256'] and p.stat().st_size==v['bytes']
 with Image.open(p) as im:assert im.format=='JPEG' and list(im.size)==dims
 return v
v=source('OVERVIEW',base+'full/full/0/default.jpg',[2852,3759]);assert v['sha256']==s['overview_sha256'];assert t(l['locked_at'])<=t(v['acquired_at'])
o=read(A/'OBSERVATION.json');z=read(A/'RESULT.json');assert o['observer']=='root informed AI' and o['localization'].strip() and o['limits'];assert t(v['acquired_at'])<=t(o['observed_at'])
if o['status']=='OBSERVED':
 c=read(A/'CROP_SCOPE.json');x,y,w,h=c['region'];assert all(type(n) is int for n in (x,y,w,h)) and x>=0 and y>=0 and w>0 and h>0 and x+w<=2852 and y+h<=3759
 assert c['overview_sha256']==v['sha256'] and c['localization'].strip();d=source('DETAIL',base+','.join(map(str,c['region']))+'/full/0/default.jpg',[w,h]);assert t(v['acquired_at'])<=t(c['locked_at'])<t(d['acquired_at'])<=t(o['observed_at'])
 assert o['oneoverview_onecrop'] is True
 assert [a['id'] for a in o['gaps']]==['g1_g2','g2_g3','g3_g4','g4_g5','g5_g6'];assert [a['id'] for a in o['pairs']]==['g1_g2','g1_g5','g3_g4','g1_g3']
 assert all(a['category'] in {'SPACE_LIKE','INTERNAL_LIKE','UNRESOLVED'} and a['reason'].strip() for a in o['gaps']);assert all(a['category'] in {'SIMILAR','DIFFERENT','UNRESOLVED'} and a['reason'].strip() for a in o['pairs'])
 ok=all(a['category']=='SPACE_LIKE' for a in o['gaps']) and [a['category'] for a in o['pairs']]==['SIMILAR','SIMILAR','SIMILAR','DIFFERENT'];decision='LOCAL_REPEAT_AND_CONTRAST_SUPPORT' if ok else 'MIXED_OR_UNRESOLVED';expected={'original_f75r.jpg','native_detail.jpg'}
else:
 assert o['status']=='TARGET_LOCALIZATION_STOP' and not o['gaps'] and not o['pairs'] and not (A/'DETAIL_SOURCE.json').exists();decision='TARGET_LOCALIZATION_STOP';expected={'original_f75r.jpg'}
assert {p.name for p in A.iterdir() if p.suffix.lower() in {'.jpg','.png','.jpeg','.tif'}}==expected
assert z['observation']==o and z['status']==decision and z['observation_sha256']==sha(A/'OBSERVATION.json') and z['protocol_lock_sha256']==sha(E/'src/PROTOCOL_LOCK.json') and z['confirmed_words']==0
out={'status':'PASS_NOT_PERCEPTION','experiment_id':'GDT1434','decision':decision,'judgments_checked':len(o['gaps'])+len(o['pairs']),'validator_sha256':sha(Path(__file__)),'result_sha256':sha(A/'RESULT.json'),'limits':['Validates saved bytes, declared categories and recordedchronology, not externallyattestedviewbehavior','Cannot independently verify targetlocalization, cropsemantics, exactalphabetidentity or visualjudgments','No meaning, independenthistoricalsample or oldfailurerescue']}
p=A/'VALIDATION.json'
if p.exists():assert read(p)==out
else:p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out))
