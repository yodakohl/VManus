import csv, json, hashlib, itertools
from pathlib import Path
D=Path(__file__).resolve().parent
M=json.loads((D/'MODEL.json').read_text()); atoms=M['atoms']; conn={M['conditional'],M['inference_marker']}
rows=list(csv.DictReader((D/'PROSE.tsv').open(),delimiter='\t'))
assert {r['page'] for r in rows}=={'f83r'}
records={}
for r in rows:
 records.setdefault(r['record_id'],[]).extend({'at':r['locus']+':'+str(i),'word':w,'line':r['locus']} for i,w in enumerate(r['zl3b_line'].split(),1))
def dump(n,x): (D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def table(n,rs,fields):
 with (D/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs)
def formula_text(f):return f[1] if f[0]=='atom' else f[1]+' -> '+f[2]
def holds(f,v):return v[f[1]] if f[0]=='atom' else (not v[f[1]] or v[f[2]])
worlds=[dict(zip('PQR',v)) for v in itertools.product([False,True],repeat=3)]
all_ops=[]; proof=[]; align=[]; readings=['# W91 — vollständiger Text und zwei hypothetische logische Lesungen','', 'P/Q/R sind unübersetzte Aussagenplatzhalter. Eckige Rohformen sind offen, keine weglassbaren Füllwörter. A prüft einen Folgerungsanspruch; U behauptet denselben Schlusssatz zusätzlich. Keine natürliche Gesamtübersetzung.','']; trace=[]; rec_summary=[]
for rid,ts in records.items():
 ops=[];owned={};errors=[]
 for i,t in enumerate(ts):
  if t['word'] not in conn:continue
  ends={}
  for direction in ([-1,1] if t['word']==M['conditional'] else [1]):
   j=i+direction
   while 0<=j<len(ts):
    if ts[j]['word'] in conn:break
    if ts[j]['word'] in atoms:ends['left' if direction<0 else 'right']=j;break
    j+=direction
  need={'left','right'} if t['word']==M['conditional'] else {'right'}
  status='BOUND' if need<=ends.keys() else 'UNBOUND'
  span={k:[x['at'] for x in ts[min(i,j)+1:max(i,j)]] for k,j in ends.items()}
  o={'record':rid,'at':t['at'],'index':i,'word':t['word'],'ends':ends,'status':status,'intervening':span}
  if status=='BOUND':
   for j in ends.values():
    if j in owned:errors.append((t['at'],ts[j]['at']))
    owned[j]=o
  ops.append(o)
 assert not errors,errors
 events=[]
 for i,t in enumerate(ts):
  if t['word'] in atoms and i not in owned:events.append((i,'bare',['atom',atoms[t['word']]],t['at']))
 for o in ops:
  if o['status']=='BOUND' and o['word']==M['conditional']:
   l,r=o['ends']['left'],o['ends']['right'];events.append((r,'conditional',['implies',atoms[ts[l]['word']],atoms[ts[r]['word']]],o['at']))
  if o['word']==M['inference_marker']:events.append((o['ends'].get('right',o['index']),'conclusion',o,o['at']))
 events.sort(key=lambda x:x[0]); A=[];U=[];pa=[];asserted=set();local=[]
 for i,kind,f,at in events:
  if kind!='conclusion':
   A.append(f);U.append(f);pa.append(at)
   if kind=='bare':asserted.add(f[1])
   trace.append({'record':rid,'at':at,'kind':kind,'formula':formula_text(f),'available_after':ts[i]['at']})
   continue
  o=f;pr={'record':rid,'marker':at,'target':ts[i]['at'] if o['status']=='BOUND' else '', 'atom':atoms[ts[i]['word']] if o['status']=='BOUND' else '', 'premises':[formula_text(x) for x in A],'premise_loci':pa.copy(), 'premise_models':[], 'countermodels':[], 'status':'UNBOUND'}
  if o['status']=='BOUND':
   goal=['atom',pr['atom']]; sat=[v for v in worlds if all(holds(x,v) for x in A)];bad=[v for v in sat if not holds(goal,v)]
   pr['premise_models']=sat;pr['countermodels']=bad
   pr['status']='INCONSISTENT_PREMISES' if not sat else 'NOT_ENTAILED' if bad else 'ENTAILED_ALREADY_ASSERTED' if pr['atom'] in asserted else 'ENTAILED_NEW'
   if sat and not bad:A.append(goal);pa.append(at);asserted.add(pr['atom'])
   U.append(goal)
  local.append(pr);proof.append(pr)
 satA=[v for v in worlds if all(holds(x,v) for x in A)];satU=[v for v in worlds if all(holds(x,v) for x in U)]
 rec_summary.append({'record':rid,'groups':len(ts),'hypothesis_positions':sum(t['word'] in atoms or t['word'] in conn for t in ts),'operators':len(ops),'bound_conditionals':sum(o['word']==M['conditional'] and o['status']=='BOUND' for o in ops),'sol':len(local),'proved_new':sum(p['status']=='ENTAILED_NEW' for p in local),'A_prefix_survivor_models':satA,'U_full_assertion_models':satU})
 readings+=['## '+rid,'']
 for line in dict.fromkeys(t['line'] for t in ts):
  line_ts=[t for t in ts if t['line']==line];readings += [line+' — `'+' '.join(t['word'] for t in line_ts)+'`','']
  for mode in ['A','U']:
   rendered=[]
   for t in line_ts:
    if t['word'] in atoms:r=atoms[t['word']]
    elif t['word']==M['conditional']:r='[wenn … dann …?]'
    elif t['word']==M['inference_marker']:r='[folglich?]' if mode=='A' else '[ferner gilt?]'
    else:r='⟦'+t['word']+'⟧'
    rendered.append(r);align.append({'record':rid,'at':t['at'],'word':t['word'],'mode':mode,'reading':r})
   readings += [mode+': '+' '.join(rendered),'']
 for o in ops:
  all_ops.append({'record':rid,'at':o['at'],'word':o['word'],'status':o['status'],'left':ts[o['ends']['left']]['at'] if 'left'in o['ends'] else '', 'right':ts[o['ends']['right']]['at'] if 'right'in o['ends'] else '', 'left_atom':atoms[ts[o['ends']['left']]['word']] if 'left'in o['ends'] else '', 'right_atom':atoms[ts[o['ends']['right']]['word']] if 'right'in o['ends'] else '', 'intervening':json.dumps(o['intervening'],ensure_ascii=False)})
(D/'READINGS.md').write_text('\n'.join(readings).rstrip()+'\n')
table('ALIGNMENT.tsv',align,['record','at','word','mode','reading'])
table('OPERATORS.tsv',all_ops,['record','at','word','status','left','right','left_atom','right_atom','intervening'])
table('ASSERTIONS.tsv',trace,['record','at','kind','formula','available_after'])
dump('PROOF_CASES.json',proof)
dump('RESULT.json',{'status':'FIXED_ARGUMENT_SKELETON_NOT_SUPPORTED_NO_CONNECTIVE_SELECTED','hypothesis_positions':43,'open_positions':298,'decision':'Do not adopt sol=therefore or qokeey=if-then; broad IDEA000127 not exhausted','records':rec_summary,'source_groups':sum(len(t) for t in records.values()),'source_lines':len(rows),'operator_count':len(all_ops),'proof_status_counts':{s:sum(p['status']==s for p in proof) for s in sorted({p['status'] for p in proof})},'confirmed_meanings':0,'independent_semantic_confirmation':False,'reserved_access':False,'categorical_syllogisms_reconstructed':0})
paths=['DECISION.md','MODEL.json','PROSE.tsv']
dump('SOURCE.json',{'original':'research_registry/proposals/translation_programs_20260912/work/P12/PROSE.tsv','guard':'./vmanus-exp query-tsv SOURCE --selector page --allow f83r --columns page,panel_id,record_id,locus,zl3b_line','original_sha256':'147f2e10c7cca6c3b93f9358498e01089efc28eb11ecba786f335103c928beb8','local_hashes':{p:hashlib.sha256((D/p).read_bytes()).hexdigest() for p in paths},'exposure':'previously exposed entire source; exploratory model selected after rereading','sealed':['f84','f84r']})
print(json.dumps(json.loads((D/'RESULT.json').read_text()),indent=2))
print(json.dumps(proof,indent=2))
