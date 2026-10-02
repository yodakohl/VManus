"""Account for frozen human-readable observations; never infer visual truth."""
import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compute():
 s=read(E/'src/SOURCE.json');lock=read(E/'src/PREREG_LOCK.json')
 for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
 assert sha(ROOT/s['cache'])==s['sha256']
 assert sha(E/'artifacts/ROOT.json')==read(E/'artifacts/ROOT_FREEZE.json')['sha256']
 records=[read(E/'artifacts'/f'{n}.json') for n in ['ROOT','OBSERVER']]
 maps=[]
 for r in records:
  assert r['source_sha256']==s['sha256'] and r['utc']>=lock['utc']
  assert len(r['observations'])==8
  d={(x['panel'],x['item']):x for x in r['observations']}
  assert set(d)=={(p,i) for p in s['panels'] for i in s['items']}
  for x in d.values():assert x['status'] in ['PRESENT','ABSENT_AT_SUPPLIED_SCALE','UNRESOLVED'] and x['location'] and x['description']
  maps.append(d)
 cells=[]
 for p in s['panels']:
  for i in s['items']:
   a,b=[m[p,i]['status'] for m in maps]
   cells.append({'panel':p,'item':i,'root':a,'observer':b,'joint':a if a==b else 'UNRESOLVED'})
 # Any jointly positive capacity requires an explicit same-connection review;
 # do not make agreement in category a substitute for ownership identity.
 candidates=[]
 for p in s['panels']:
  joint={c['item']:c['joint'] for c in cells if c['panel']==p}
  if all(joint[i]=='PRESENT' for i in ['M1','M2','M4']) or all(joint[i]=='PRESENT' for i in ['M3','M4']): candidates.append(p)
 status='LOCATION_REVIEW_REQUIRED' if candidates else 'NO_OWNED_CONSTRUCTION_CAPACITY_IN_FIXED_CANVAS'
 return {'status':status,'cells':cells,'candidate_panels_requiring_same_connection_review':candidates,'source_sha256':s['sha256'],'confirmed_words':0,'independent_meaning_confirmation_capacity':0,'claim_ceiling':'Recorded local visible prerequisites only; no semantic refutation or scored inscription edges'}
if __name__=='__main__':
 r=compute();(E/'artifacts/RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
