"""Disclosed post-result analytic checks; does not alter the registered result."""
from pathlib import Path
import json,gzip,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
S=json.loads((D/'src/SPEC.json').read_text());R=json.loads((A/'RESULT.json').read_text())
raw=(ROOT/S['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==S['source_sha256']
source=json.loads(gzip.decompress(raw))
def necessary_scan(u,h):
 i=0
 while i<len(u):
  if u[i]!=h:i+=1;continue
  if len(u)-i<3:return False,'reserved sign lacks its two escape digits'
  if u[i+1]==h:return False,'escape high digit cannot equal reserved sign'
  i+=3
 return True,'not excluded by this relaxed literal scan'
cases=[]
for ed,data in R['readers'].items():
 row=next(h for h in data['heads'] if h['head']=='a')
 for w in row['witnesses']:
  if w['follower'] not in ['i','n','m']:continue
  h=w['follower'];assert h in data['survivors'] and w['units'][0]!=h
  passed,reason=necessary_scan(w['units'],h)
  cases.append(dict(reader=ed,head=h,stage='nine_fixed_a_initial_witnesses',id=w['id'],word=w['word'],units=w['units'],excluded=not passed,reason=reason))
extra=[r for r in source['IT2a'] if r['id']=='IT2a|f108v.52|G009']
assert len(extra)==1 and extra[0]['ivtff_group_raw']=='daiin'
r=extra[0];passed,reason=necessary_scan(r['units'],'i')
cases.append(dict(reader='IT2a',head='i',stage='separately_named_GDT1204_witness',id=r['id'],word=r['ivtff_group_raw'],units=r['units'],excluded=not passed,reason=reason))
remaining={ed:[h for h in data['survivors'] if not any(c['reader']==ed and c['head']==h and c['excluded'] for c in cases)] for ed,data in R['readers'].items()}
out=dict(status='POST_RESULT_ALL_RENAMINGS_EXCLUDED' if all(not x for x in remaining.values()) else 'POST_RESULT_SURVIVORS_REMAIN',registered_initial_status=R['status'],cases=cases,remaining=remaining,scope='Disclosed post-result logical extension: original nine-witness check left IT/i open; one separately pre-named published GDT1204 occurrence closes it. No original gate replaced, no native meanings or general suffix-sharing exclusion.')
(A/'POST_RESULT_SURVIVOR_CHECK.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],remaining)
