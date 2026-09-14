"""Reconstruct attachment/events separately; verify truth consequences via set models."""
import csv,hashlib,json,itertools
from pathlib import Path
D=Path(__file__).resolve().parent
j=lambda n:json.loads((D/n).read_text())
m=j('MODEL.json'); src=j('SOURCE.json'); result=j('RESULT.json'); cases=j('PROOF_CASES.json')
for f,h in src['local_hashes'].items():assert hashlib.sha256((D/f).read_bytes()).hexdigest()==h
assert hashlib.sha256(Path(src['original']).read_bytes()).hexdigest()==src['original_sha256']
rows=list(csv.DictReader((D/'PROSE.tsv').open(),delimiter='\t'))
assert len(rows)==51 and {r['page'] for r in rows}=={'f83r'}
seq={}
for r in rows:
 seq.setdefault(r['record_id'],[]).extend((r['locus']+':'+str(i),w) for i,w in enumerate(r['zl3b_line'].split(),1))
assert len(seq)==7 and sum(map(len,seq.values()))==341
alignment=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'))
for mode in ['A','U']:
 assert [(r['record'],r['at'],r['word']) for r in alignment if r['mode']==mode]==[(rid,a,w) for rid,ts in seq.items() for a,w in ts]
operators=list(csv.DictReader((D/'OPERATORS.tsv').open(),delimiter='\t'))
worlds=[dict(zip('PQR',b)) for b in itertools.product([False,True],repeat=3)]
truth={a:{i for i,v in enumerate(worlds) if v[a]} for a in 'PQR'}
for a,b in itertools.product('PQR',repeat=2):truth[a+' -> '+b]=set(range(8))-truth[a]|truth[b]
checks=0
for rid,ts in seq.items():
 # Each delimiter bounds the operand search. Segment edges derived once.
 delimiters=[i for i,(_,w) in enumerate(ts) if w in {'sol','qokeey'}]
 compound={}; goals={}; owners=set();expected=[]
 for n,i in enumerate(delimiters):
  at,word=ts[i];leftedge=delimiters[n-1]+1 if n else 0;rightedge=delimiters[n+1] if n+1<len(delimiters) else len(ts)
  ls=[k for k in range(leftedge,i) if ts[k][1] in m['atoms']]
  rs=[k for k in range(i+1,rightedge) if ts[k][1] in m['atoms']]
  left=ls[-1] if word=='qokeey' and ls else None;right=rs[0] if rs else None
  bound=right is not None and (word=='sol' or left is not None)
  o=next(o for o in operators if o['record']==rid and o['at']==at)
  assert o['status']==('BOUND' if bound else 'UNBOUND')
  assert o['left']==(ts[left][0] if left is not None else '') and o['right']==(ts[right][0] if right is not None else '')
  if word=='sol':goals[right if bound else i]=(at,m['atoms'][ts[right][1]] if bound else None)
  elif bound:compound[right]=(at,m['atoms'][ts[left][1]]+' -> '+m['atoms'][ts[right][1]])
  if bound:
   ends={right}|({left} if word=='qokeey' else set());assert not owners&ends;owners|=ends
  checks+=1
 premise=[];loci=[];accepted=set();U=[]
 for i,(at,w) in enumerate(ts):
  if i in compound:
   ca,form=compound[i];premise.append(form);loci.append(ca);U.append(form)
  elif w in m['atoms'] and i not in owners:
   form=m['atoms'][w];premise.append(form);loci.append(at);U.append(form);accepted.add(form)
  if i in goals:
   marker,goal=goals[i];c=next(c for c in cases if c['record']==rid and c['marker']==marker)
   assert c['premises']==premise and c['premise_loci']==loci
   if goal is None:assert c['status']=='UNBOUND';continue
   sat=set(range(8))
   for p in premise:sat &= truth[p]
   bad=sat-truth[goal]
   state='INCONSISTENT_PREMISES' if not sat else 'NOT_ENTAILED' if bad else 'ENTAILED_ALREADY_ASSERTED' if goal in accepted else 'ENTAILED_NEW'
   assert state==c['status']
   assert c['premise_models']==[worlds[k] for k in sorted(sat)] and c['countermodels']==[worlds[k] for k in sorted(bad)]
   if sat and not bad:premise.append(goal);loci.append(marker);accepted.add(goal)
   U.append(goal);checks+=1
 def models(fs):
  s=set(range(8))
  for f in fs:s &= truth[f]
  return [worlds[k] for k in sorted(s)]
 rr=next(r for r in result['records'] if r['record']==rid)
 assert rr['A_prefix_survivor_models']==models(premise)
 assert rr['U_full_assertion_models']==models(U)
 assert rr['hypothesis_positions']==sum(w in m['atoms'] or w in {'sol','qokeey'} for a,w in ts)
# Semantic fixtures: valid nonvacuous modus ponens and invalid converse, plus inconsistency guard.
assert truth['P']&truth['P -> Q'] <= truth['Q']
assert not truth['Q']&truth['P -> Q'] <= truth['P']
assert set(range(8))-truth['P'] & truth['P']==set()
assert result['proof_status_counts']=={'NOT_ENTAILED':5,'UNBOUND':2}
assert sum(r['hypothesis_positions'] for r in result['records'])==43
out={'status':'PASS','scope':'local source hashes; full 682-position dual alignment; independently reconstructed attachments, event order and 8-world truth consequences; no independent meaning validation','operators_replayed':len(operators),'sol_cases':len(cases),'source_groups':341,'hypothesis_positions':43,'open_positions':298,'external_validator':False}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
