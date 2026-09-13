"""Independent adjacency-matrix capacity audit, no builder import."""
from pathlib import Path
import csv,json,hashlib,collections
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
S=json.loads((E/'SPEC.json').read_text());assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for x in S['inputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
keys=['lexicon','shol','paragraph','grammar','chol','timing','mix','relation']
def key(r):return tuple(r[k] for k in keys)
R=rows(E/'RELATIONS.tsv');A=rows(E/'THERMAL_ACTIONS.tsv');C=rows(E/'CANDIDATES.tsv');F=rows(E/'ALL_RECIPIENT_FUTURES.tsv');worlds=rows(E/'WORLDS.tsv')
rr={key(r)+(int(r['index']),):r for r in R};aa={key(r)+(int(r['index']),):r for r in A};cc={(key(r),r['action'],r['recipient']):r for r in C}
assert len(rr)==len(R) and len(aa)==len(A) and len(cc)==len(C)
traces={}
for l in S['lexicons']:
 for s in S['shol']:
  B=W/('W28' if l=='C' else 'W33');pre=s if l=='C' else 'O_'+s
  for r in rows(B/(pre+'_EVENTS.tsv')):traces.setdefault((l,s,r['paragraph'],r['grammar'],r['model'],r['timing']),[]).append(r)
expected_worlds={k+(m,r) for k in traces for m in S['mix_models'] for r in S['relation_models']};assert {key(r) for r in worlds}==expected_worlds
seenR=[];seenA=[];seenC=[];expectedF=[]
for world in worlds:
 k=key(world);trace=traces[k[:6]];neighbors=collections.defaultdict(set);potential=0
 for i,e in enumerate(trace):
  assert not e['location'].startswith('f84')
  if e['kind']!='ACTION':continue
  a,b=e['object'],e['second_object']
  if e['form'] in S['mix_forms']+['qotchy']:
   r=rr[k+(i,)];seenR.append(k+(i,));old=sorted((x,y) for x,ys in neighbors.items() for y in ys if x<y)
   operation=('JOIN' if k[6]=='D' else 'UNCHANGED') if e['form'] in S['mix_forms'] else ('JOIN' if k[7]=='V' else 'REMOVE_PAIR')
   status='UNARY_NO_EDGE' if operation=='UNCHANGED' else 'MISSING_PARTICIPANT' if not a or not b else 'SAME_OBJECT' if a==b else 'APPLIED'
   assert r['contract']==operation and r['status']==status and json.loads(r['before'])==[list(x) for x in old]
   if status=='APPLIED':
    if operation=='JOIN':neighbors[a].add(b);neighbors[b].add(a)
    else:neighbors[a].discard(b);neighbors[b].discard(a)
   new=sorted((x,y) for x,ys in neighbors.items() for y in ys if x<y)
   assert json.loads(r['after'])==[list(x) for x in new]
   assert all(r[f]==e[f] for f in ['form','patient','second','object','second_object','debts'])
  effect=json.loads(e['assertion']) if e['assertion'] else {}
  if e['status']!='ASSUMED_EFFECT_APPLIED' or effect.get('axis')!='thermal':continue
  ar=aa[k+(i,)];seenA.append(k+(i,));reach={a}
  for _ in range(len(neighbors)+1):reach |= {y for x in list(reach) for y in neighbors[x]}
  assert json.loads(ar['members'])==sorted(reach) and int(ar['recipient_count'])==len(reach)-1 and ar['value']==effect['value']
  for other in reach-{a}:
   potential+=1;ck=(k,e['location'],other);c=cc[ck];seenC.append(ck)
   assert c['H_prediction']==effect['value'] and c['acting_object']==a
   later=[(j,x) for j,x in enumerate(trace) if j>i and (x['object']==other or x['second_object']==other)]
   assert int(c['later_events'])==len(later)
   # Actual corpus outcome: no later mention/action/assertion at all on recipient.
   assert not later and c['status']=='NO_LATER_THERMAL_EVENT' and not c['first_thermal_event'] and not c['written_value']
   assert c['independent_confirmation_capacity']=='0'
   for j,x in later:expectedF.append((ck,j))
 assert int(world['potential_transfers'])==potential and int(world['events'])==len(trace)
 assert json.loads(world['final_edges'])==[list(x) for x in sorted((x,y) for x,ys in neighbors.items() for y in ys if x<y)]
assert set(seenR)==set(rr) and set(seenA)==set(aa) and set(seenC)==set(cc) and len(seenC)==len(C)
assert not F and not expectedF
res=json.loads((E/'RESULT.json').read_text());assert res['worlds']==len(worlds)==3264 and res['relation_cases']==len(R)==1920 and res['thermal_action_cases']==len(A)==8352 and res['potential_transfers']==len(C)==96 and res['differing_checkable_predictions']==0
assert {(r['action'],r['recipient']) for r in C}=={('f93r.30:2','f93r.13:3')}
out=dict(status='PASS',bound_files=len(S['inputs']),worlds=len(worlds),relation_cases=len(R),thermal_actions=len(A),all_potential_transfers=len(C),recipient_futures=0,limits='Independent graph and complete future capacity audit; not independent meaning validation')
(E/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
