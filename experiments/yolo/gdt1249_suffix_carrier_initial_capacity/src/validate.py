"""Independent raw-spelling branch census; imports no primary runner."""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json,re
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
S=json.loads((D/'src/SPEC.json').read_text())
lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
for p,h in lock['files'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
source=json.loads(gzip.decompress((ROOT/S['source']).read_bytes()))
R=json.loads((A/'RESULT.json').read_text())
pattern=re.compile('|'.join(sorted(S['signs'],key=len,reverse=True)))
checks={}
for ed in S['readers']:
 rows=source[ed]; parsed=[]; ids=set()
 for r in rows:
  assert r['id'] not in ids;ids.add(r['id'])
  u=pattern.findall(r['ivtff_group_raw'])
  assert ''.join(u)==r['ivtff_group_raw'] and u==r['units']
  assert not r['page'].startswith('f84') and r['page']!='f116v'
  parsed.append((r,u))
 frequencies=Counter(r['ivtff_group_raw'] for r in rows)
 got=R['readers'][ed]
 assert got['groups']==len(rows) and got['types']==len(frequencies)
 rebuilt=[]
 for head in S['signs']:
  relevant=[(r,u) for r,u in parsed if len(u)>1 and u[0]==head]
  followers=[tail for tail in S['signs'] if any(u[1]==tail for r,u in relevant)]
  nonself=[tail for tail in followers if tail!=head]
  witnesses=[]
  for tail in followers:
   matches=[r for r,u in relevant if u[1]==tail]
   row=sorted(matches,key=lambda r:(r['ivtff_group_raw'],r['id']))[0]
   witnesses.append(dict(follower=tail,id=row['id'],page=row['page'],locus=row['locus'],word=row['ivtff_group_raw'],units=pattern.findall(row['ivtff_group_raw']),whole_form_occurrences=frequencies[row['ivtff_group_raw']],branch_occurrences=len(matches)))
  rebuilt.append(dict(head=head,followers=followers,nonself_followers=nonself,initial_nonsingleton_occurrences=len(relevant),excluded=len(nonself)>=4,contradiction_followers=nonself[:4] if len(nonself)>=4 else [],witnesses=witnesses))
 assert rebuilt==got['heads']
 survivors=[h['head'] for h in rebuilt if not h['excluded']]
 assert got['survivors']==survivors
 assert got['status']==('ALL_RENAMINGS_EXCLUDED' if not survivors else 'NECESSARY_SURVIVORS_ONLY')
 q=next(h for h in rebuilt if h['head']=='q')
 assert got['literal_q_key_excluded']==bool(set(q['followers'])-set(['q','a','o','e']))
 checks[ed]={'groups':len(rows),'heads':len(rebuilt),'survivors':survivors,'all_witnesses_reconstructed':True}
status='ALL_RENAMINGS_EXCLUDED_ALL_READINGS' if all(not x['survivors'] for x in checks.values()) else 'READER_SPECIFIC_NECESSARY_SURVIVORS'
assert R['status']==status
out={'status':'PASS','readers':checks,'scientific_status':status,'scope':'Separate same-author code validates exact source/branch/certificate reconstruction, not independent manuscript or semantic confirmation.'}
(A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
