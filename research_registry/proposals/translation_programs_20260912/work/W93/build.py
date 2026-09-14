import csv,json,hashlib
from collections import Counter
from pathlib import Path
D=Path(__file__).resolve().parent;B=D.parent/'W92'
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rows,fields):
 with (D/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
for p,h in json.loads((D/'FROZEN_INPUTS.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
lex={x['name']:x for x in json.loads((B/'DEFINITIONS.json').read_text())}
pred={x['name']:x for x in json.loads((D/'PREDICTIONS.json').read_text())}
def expand(w):return sum((expand(v) for v in lex[w]['body']),[]) if w in lex else [w]
rows=list(csv.DictReader((D/'PROSE.tsv').open(),delimiter='\t'));assert {r['page'] for r in rows}=={'f77r','f82r'}
units=[];align=[];reading=['# W93 — alle vollständigen Arbeitsrecords','', 'qokedy und seine Bereiche werden ausschließlich nach dem unveränderten W92-Vertrag markiert. Jede Quellgruppe bleibt stehen. Nicht im festen Lexikon enthaltene Namen werden nicht neu gelernt.',''];seen=set()
for r in rows:
 if r['record_id'] not in seen:reading+=['## '+r['record_id'],''];seen.add(r['record_id'])
 words=r['zl3b_line'].split();start=0;roles={};render={}
 for i,w in enumerate(words):
  if w!='qokedy':continue
  body=words[start:i];name=words[i+1] if i+1<len(words) else ''
  name_at=r['locus']+':'+str(i+2) if name else ''
  status='EMPTY_BODY' if not body else 'MISSING_TARGET' if not name else 'MARKER_AS_NAME' if name=='qokedy' else 'OUTSIDE_FROZEN_NAMES' if name not in pred else 'APPLICABLE'
  observed=sum((expand(v) for v in body),[])
  expected=pred[name]['expected_expression'] if name in pred else []
  compared=status=='APPLICABLE'
  if compared:status='MATCH' if observed==expected else 'CONFLICT'
  first=next((k for k in range(max(len(observed),len(expected))) if (observed[k] if k<len(observed) else None)!=(expected[k] if k<len(expected) else None)),None) if compared else None
  u={'id':'U%02d'%(len(units)+1),'page':r['page'],'record':r['record_id'],'marker':r['locus']+':'+str(i+1),'name':name,'name_at':name_at,'body_loci':[r['locus']+':'+str(k+1) for k in range(start,i)],'literal_body':body,'expected_expression':expected,'observed_expression':observed,'status':status,'multiset_equal':Counter(observed)==Counter(expected) if compared else None,'first_difference_position':first+1 if first is not None else None,'raw_line':r['zl3b_line']};units.append(u)
  for k in range(start,i):roles[k]='PROPOSED_BODY'
  roles[i]='MARKER';render[i]='[qokedy: '+u['id']+'/'+status+']'
  if name:roles[i+1]='TARGET';render[i+1]='«'+name+'»'
  start=i+2
 reading += [r['locus']+' — `'+r['zl3b_line']+'`','', ' '.join(render.get(k,'⟦'+w+'⟧') for k,w in enumerate(words)),'']
 for k,w in enumerate(words):align.append({'page':r['page'],'record':r['record_id'],'at':r['locus']+':'+str(k+1),'word':w,'role':roles.get(k,'OTHER_TEXT'),'render':render.get(k,'⟦'+w+'⟧')})
dump('UNITS.json',units);tab('ALIGNMENT.tsv',align,list(align[0]))
(D/'READINGS.md').write_text('\n'.join(reading).rstrip()+'\n')
candidates=[]
for name,p in pred.items():
 us=[u for u in units if u['name']==name]
 nmatch=sum(u['status']=='MATCH' for u in us);nfail=sum(u['status']=='CONFLICT' for u in us)
 candidates.append({'name':name,'W92_definition':p['definition'],'expected_expression':' '.join(p['expected_expression']),'matched':nmatch,'contradicted':nfail,'unbound':sum(u['status'] not in {'MATCH','CONFLICT'} for u in us),'evaluated_markers':','.join(u['marker'] for u in us if u['status'] in {'MATCH','CONFLICT'}),'pages':','.join(sorted({u['page'] for u in us})),'all_source_occurrences':sum(t['word']==name for t in align),'verdict':'CONTRADICTED_EXTENSION' if nfail else 'MATCHED_UNCONFIRMED' if nmatch else 'NO_CAPACITY'})
tab('CANDIDATES.tsv',candidates,list(candidates[0]))
md=['# W93 — sämtliche qokedy-Stellen','', '| Stelle | Name | Ganzer vorgeschlagener Körper | Erwartete Auflösung | Beobachtete Auflösung | Ergebnis |','|---|---|---|---|---|---|']
for u in units:md.append('| '+u['marker']+' | '+u['name']+' | '+' '.join(u['literal_body'])+' | '+' '.join(u['expected_expression'])+' | '+' '.join(u['observed_expression'])+' | '+u['status']+' |')
(D/'COMPARISON.md').write_text('\n'.join(md)+'\n')
result={'status':'FIXED_W92_CROSS_PAGE_EXTENSION_REJECTED' if any(u['status']=='CONFLICT' for u in units) else 'NO_APPLICABLE_FIXED_NAME_STOP' if not any(u['status']=='MATCH' for u in units) else 'MATCHES_UNCONFIRMED','source_lines':len(rows),'source_groups':len(align),'records':len(seen),'pages':sorted({r['page'] for r in rows}),'physical_leaves':['f77','f82'],'marker_count':len(units),'unit_outcomes':dict(Counter(u['status'] for u in units)),'candidate_outcomes':dict(Counter(c['verdict'] for c in candidates)),'conflicts_not_explained_by_order':sum(u['status']=='CONFLICT' and not u['multiset_equal'] for u in units),'confirmed_meanings':0,'reserved_access':False,'independent_confirmation_capacity':0,'meaning_scope':'finite symbolic expansion only; unknown literal leaves are not confirmed distinct semantic concepts; ordinary paraphrase not tested','W92_changed':False}
dump('RESULT.json',result)
source=Path('research_registry/proposals/translation_programs_20260912/work/P28/PROSE.tsv')
dump('SOURCE.json',{'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'projection_sha256':hashlib.sha256((D/'PROSE.tsv').read_bytes()).hexdigest(),'selector':'page','allow':['f77r','f82r'],'columns':'page,panel_id,record_id,locus,zl3b_line','sealed':['f84','f84r'],'exposure':'previously exposed P28 development text; not held confirmation'})
print(json.dumps(result,indent=2));print((D/'COMPARISON.md').read_text())
