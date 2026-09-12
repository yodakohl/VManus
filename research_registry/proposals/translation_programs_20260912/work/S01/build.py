import csv,json,hashlib
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[4]
S=R/'research_registry/proposals/translation_programs_20260912/work/P12/PROSE.tsv'
def js(name,x):(H/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(name,rows):
 with (H/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
nouns={'shedy':'Gemisch','lchedy':'Rückstand','qokeey':'Flüssigkeit','shckhedy':'Teilportion'}
lex={**nouns,'qokeedy':'teile / entnimm eine Probe','chedy':'erwärme','sheey':'ist beobachtet klar','qokedy':'ist klar (Behauptung)'}
js('MODEL.json',{'lexicon':lex,'variants':['F first child sample','L last child sample','U no parent inference'],'semantic_status':'all whole-word hypotheses','identity':'same-form remention conditional; positions kept distinct'})
js('SOURCE.json',{'files':[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [S,H/'DECISION.md',H/'MODEL.json']],'sealed':['f84','f84r'],'independent_confirmation':0})
lines=list(csv.DictReader(S.open(),delimiter='\t'));g=[]
for line in lines:
 assert line['page']=='f83r'
 for n,w in enumerate(line['zl3b_line'].split(),1):g.append({'record':line['record_id'],'locus':line['locus'],'at':line['locus']+':'+str(n),'word':w})
assert len(g)==341 and len(lines)==51
def before(i):return [j for j in range(i) if g[j]['record']==g[i]['record']]
def left(i):return next((j for j in reversed(before(i)) if g[j]['word'] in nouns),None)
def right(i):
 out=[]
 for j in range(i+1,len(g)):
  if g[j]['record']!=g[i]['record'] or g[j]['word'] in {'qokeedy','qokedy'}:break
  if g[j]['word'] in nouns:out.append(j)
 return out
at=lambda i:g[i]['at'] if i is not None else 'NONE'
splits={};heats={};obs={};claims={}
for i,x in enumerate(g):
 if x['word']=='qokeedy':splits[i]=(left(i),right(i)[:2])
 if x['word']=='chedy':heats[i]=left(i)
 if x['word']=='sheey':obs[i]=left(i)
 if x['word']=='qokedy':claims[i]=next(iter(right(i)),None)
tab('SPLITS.tsv',[{'at':at(i),'record':g[i]['record'],'input':at(p),'children':','.join(at(c) for c in cs) or 'NONE','status':'COMPLETE' if p is not None and len(cs)==2 else 'MISSING_ROLES','mass':'m=m1+m2; m1>0,m2>0' if p is not None and len(cs)==2 else 'UNRESOLVED','row_status':'recorded'} for i,(p,cs) in splits.items()])
tab('HEATS.tsv',[{'at':at(i),'patient':at(p),'status':'BOUND' if p is not None else 'MISSING_MATERIAL','row_status':'recorded'} for i,p in heats.items()])
tab('INPUT.tsv',[dict(x,row_status='recorded') for x in g])
results={};all_checks=[]
for v in ['F','L','U']:
 observation_rows=[];evidence={}
 for i,patient in obs.items():
  candidates=[(s,p,cs) for s,(p,cs) in splits.items() if p is not None and len(cs)==2 and cs[-1]<i and patient in cs and g[s]['record']==g[i]['record']]
  licenses=[]
  for s,p,cs in candidates:
   sample=cs[0] if v=='F' else cs[1] if v=='L' else None
   if sample==patient and not any(patient==hp and sample<h<i for h,hp in heats.items()):licenses.append((s,p))
  evidence[i]=licenses
  observation_rows.append({'at':at(i),'patient':at(patient),'version':v,'sample_splits':','.join(at(s) for s,p in licenses) or 'NONE','parent_mentions':','.join(at(p) for s,p in licenses) or 'NONE','status':'MISSING_MATERIAL' if patient is None else 'SAMPLE_LICENSED' if licenses else 'DIRECT_ONLY','row_status':'recorded'})
 checks=[]
 for i,target in claims.items():
  direct=[];inferred=[];why=[]
  for o,patient in obs.items():
   if o>=i or g[o]['record']!=g[i]['record']:continue
   if target is None or patient is None:continue
   blocked=lambda p:any(o<h<i and hp in {p,patient} for h,hp in heats.items())
   if g[patient]['word']==g[target]['word'] and not blocked(patient):direct.append(o)
   for s,p in evidence[o]:
    if g[p]['word']==g[target]['word'] and not blocked(p):inferred.append((o,s,p))
  status='MISSING_TARGET' if target is None else 'SUPPORTED_DIRECT' if direct else 'SUPPORTED_SAMPLE' if inferred else 'UNSUPPORTED'
  row={'at':at(i),'record':g[i]['record'],'version':v,'target':at(target),'target_word':g[target]['word'] if target is not None else 'NONE','direct_observations':','.join(at(o) for o in direct) or 'NONE','sample_observations':','.join(at(o) for o,s,p in inferred) or 'NONE','sample_splits':','.join(at(s) for o,s,p in inferred) or 'NONE','parent_mentions':','.join(at(p) for o,s,p in inferred) or 'NONE','status':status,'row_status':'recorded'}
  checks.append(row)
 tab('OBSERVATIONS_'+v+'.tsv',observation_rows);tab('CLAIMS_'+v+'.tsv',checks);all_checks+=checks
 byclaim={x['at']:x for x in checks};byobs={x['at']:x for x in observation_rows};align=[]
 for i,x in enumerate(g):
  w=x['word'];render=lex.get(w,'['+w+' — offen]')
  if w=='qokeedy':
   p,cs=splits[i];render=('teile' if v=='U' else 'entnimm Probe, Ergebnis '+('1' if v=='F' else '2'))+' aus '+at(p)+'; zwei Teile: '+(','.join(at(c) for c in cs) or '?')
  elif w=='chedy':render='erwärme Material@'+at(heats[i])
  elif w=='sheey':render='beobachtet klar: Material@'+at(obs[i])+'; '+byobs[x['at']]['status']
  elif w=='qokedy':render='Material@'+at(claims[i])+' ist klar; '+byclaim[x['at']]['status']
  align.append(dict(x,version=v,render=render,read_status='HYPOTHESIS' if w in lex else 'OPEN',row_status='recorded'))
 tab('ALIGNMENT_'+v+'.tsv',align)
 text=['# S01 '+v+' — ganze Arbeitsseite; alle Bedeutungen hypothetisch','']
 for line in lines:text+=['**'+line['record_id']+' / '+line['locus']+'**','', ' · '.join(x['word']+' → '+x['render'] for x in align if x['locus']==line['locus']),'']
 (H/('READING_'+v+'.md')).write_text('\n'.join(text).rstrip()+'\n')
 results[v]={'claims':dict(Counter(x['status'] for x in checks)),'observations':dict(Counter(x['status'] for x in observation_rows))}
tab('ALL_CLAIMS.tsv',all_checks)
res={'status':'PARTIAL_SAMPLE_READING_ONE_ORIENTATION_DEPENDENT_PARENT_INFERENCE','groups':len(g),'hypothetical_positions':sum(x['word'] in lex for x in g),'open_positions':sum(x['word'] not in lex for x in g),'split_sites':len(splits),'complete_splits':sum(p is not None and len(cs)==2 for p,cs in splits.values()),'heat_sites':len(heats),'observation_sites':len(obs),'claim_sites':len(claims),'variants':results,'confirmed_meanings':0,'independent_confirmation_capacity':0,'limit':'local episodes, conditional same-form parent identity and representativeness; no global material balance or meaning proof'}
js('RESULT.json',res);print(json.dumps(res))
