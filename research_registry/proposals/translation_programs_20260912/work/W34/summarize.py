import csv,json,collections,hashlib
from pathlib import Path
E=Path(__file__).resolve().parent
K=['lexicon','shol','paragraph','grammar','chol','timing','target']
def rows(n):return list(csv.DictReader((E/n).open(),delimiter='\t'))
def key(r):return tuple(r[k] for k in K)
def table(n,rr):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0])+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
ts={key(r):r for r in rows('TARGETS.tsv')};ls=collections.defaultdict(list);ev=collections.defaultdict(list);tk=collections.defaultdict(list)
for r in rows('ALL_LATER_REQUIREMENTS.tsv'):ls[key(r)].append(r)
for r in rows('EVENTS.tsv'):ev[key(r)].append(r)
for r in rows('TAKE_REFERENCES.tsv'):tk[key(r)].append(r)
res=[];groups={}
for r in rows('ELIGIBILITY.tsv'):
 k=key(r);t=ts.get(k);future=ls[k];payload=[{a:b for a,b in x.items() if a not in K+['row_status']} for x in ev[k]]
 # Include take references: identical state traces alone cannot hide different take bindings.
 sig=hashlib.sha256(json.dumps([payload,[{a:b for a,b in x.items() if a not in K+['row_status']} for x in tk[k]]],sort_keys=True).encode()).hexdigest() if t else 'UNAVAILABLE'
 if sig not in groups:groups[sig]='G'+str(len(groups)+1)
 res.append(dict(**{a:r[a] for a in K},form=r['form'],eligibility=r['status'],parent=r['parent'],parent_form=t['antecedent_form'] if t else '',R_entry_state=t['R_state'] if t else '',E_prediction='separate portion; warm asserted at name',R_prediction='inherit complete nearest-material state before name assertion' if t else 'unavailable',observed_requirements=json.dumps([{a:x[a] for a in ['location','form','kind','E_status','R_status','R_before','R_after','debts']} for x in future],ensure_ascii=False),new_conflicts=sum(x['R_status']=='CONFLICT' and x['E_status']!='CONFLICT' for x in future),later_actions=sum(x['kind']=='ACTION' for x in future),prediction_group=groups[sig],prediction_sha256=sig,remaining_ambiguity='conditional identity rejected in fixed model' if any(x['R_status']=='CONFLICT' and x['E_status']!='CONFLICT' for x in future) else 'external versus same portion unresolved',independent_confirmation_capacity=0))
table('CANDIDATES.tsv',res)
out=[]
for sig,g in groups.items():
 cases=[r for r in res if r['prediction_group']==g]
 out.append(dict(group=g,sha256=sig,cases=len(cases),members=json.dumps([{k:r[k] for k in K} for r in cases]),limit='Same full event/take predictions do not independently confirm meanings; unavailable group has no R prediction' ))
table('PREDICTION_GROUPS.tsv',out)
print(json.dumps({'candidate_rows':len(res),'groups_including_unavailable':len(out)}))
