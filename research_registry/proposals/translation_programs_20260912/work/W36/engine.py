"""W28: frozen W26 contract plus whole sal nominal role only."""
import ast,collections,copy,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(n,rr,cols=None):
 cols=[k for k in (cols or list(rr[0])) if k!='row_status']+['row_status']
 with (E/(RUN_ID+'_'+n)).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
def encode(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
S=read(E/'SPEC.json');S['variants']=['B','J','M'];assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')};rules=read(W/'W05/SPEC.json')
for w,o in rules['word_overrides'].items():D[w].update(o)
if SHOL_MODEL=='A':D['shol']={'role':'ACTION','hypothesis':'befeuchte'}
D.update(sheeody={'role':'MATERIAL','hypothesis':'Pulver'},qokeeo={'role':'ACTION','hypothesis':'rühre'})
D['sal']={'role':'MATERIAL','hypothesis':'Arzneimaterial'}
for nominal in NOMINALS:D[nominal]={'role':'MATERIAL','hypothesis':'trockene Krautzubereitung' if nominal=='chocthy' else 'Krautposten'}
ACT=set(rules['action_roles']);MAT=set(rules['material_roles']);MOD=set(rules['transparent_roles']);extracts={'cheor','okeeor','okeor','keeor','cheeor','sheeor'}
glosses={r['raw']:r['joint'] for r in rows(W/'W16/ALIGNMENT.tsv')}
if SHOL_MODEL=='A':glosses['shol']='befeuchte'
glosses['sal']='Arzneimaterial [Hypothese; Präparat/Salz offen]'
for nominal in NOMINALS:glosses[nominal]='trockene Krautzubereitung [Hypothese]' if nominal=='chocthy' else 'Krautposten [Wertachse offen; Hypothese]'
for folder,name in [('W05','base_arguments'),('W11','solve'),('W13','requal'),('W16','take'),('W14','replay')]:
 fn=next(n for n in ast.parse((W/folder/'build.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fn],type_ignores=[]),'frozen_'+folder+'_'+name,'exec'))
features=collections.defaultdict(list);standalone={}
for f in read(W/'W03/SPEC.json')['features']:
 if f['kind']=='STANDALONE':standalone[f['form']]=f
 else:features[f['form']].append(f)
if 'chocthy' in NOMINALS:features['chocthy'].append(dict(form='chocthy',axis='moisture',value='dry',kind='BARE_NOMINAL'))
opposed={'moisture':{frozenset(('wet','dry'))},'thermal':{frozenset(('cold','warm')),frozenset(('cold','hot'))}}
ns=dict(json=json,features=features,material_roles=MAT,opposed=opposed)
fns=[n for n in ast.parse((W/'W09/build.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in ['js','snapshots','execute']];exec(compile(ast.Module(body=fns,type_ignores=[]),'frozen_W09','exec'),ns)
effects=read(W/'W09/SPEC.json')['effects'];source=read(E/'SOURCE.json')['paragraphs']
if SHOL_MODEL=='A':effects['shol']={'axis':'moisture','value':'wet'}
flatout=[];args=[];quality=[];census=[];events=[];summary=[];targets=[];diff=[];takes=[]
for p in source:
 flat=[]
 for l in p['lines']:
  assert not l['locus'].startswith('f84')
  for i,w in enumerate(l['words'],1):flat.append(dict(id=l['locus']+':'+str(i),locus=l['locus'],index=i,form=w,role=D.get(w,{}).get('role','OPEN'),offset=len(flat)))
 flatout.extend(dict(paragraph=p['id'],**x) for x in flat);byid={x['id']:x for x in flat}
 for g,aa in solve(flat).items():
  args.extend(dict(paragraph=p['id'],grammar=g,**a) for a in aa);qq=[];shifts={}
  for x in flat:
   if x['form']=='ychor':takes.append(dict(paragraph=p['id'],grammar=g,target=x['id'],**take(flat,x,aa,g)))
   if x['role']!='STATE' or x['form'] not in standalone:continue
   f=standalone[x['form']];q=requal(dict(mention=x['id'],kind='STANDALONE',form=x['form'],axis=f['axis'],value=f['value'],scope='PHYSICAL'),flat,aa);qq.append(q);quality.append(dict(paragraph=p['id'],grammar=g,**q))
   m=byid.get(q['patient']);earlier=[a for a in aa if m and a['patient']==m['id'] and byid[a['operation']]['locus']==m['locus'] and byid[a['operation']]['offset']<m['offset']]
   eligible=bool(m and m['locus']==x['locus'] and m['offset']==x['offset']-1 and m['role'] in MAT and earlier)
   if eligible:shifts[x['id']]=m['offset']
   census.append(dict(paragraph=p['id'],grammar=g,mention=x['id'],form=x['form'],patient=q['patient'],input_eligible=eligible,earlier_actions=';'.join(a['operation'] for a in earlier)))
  traces={}
  for model,effect in S['models'].items():
   ns['S']={'effects':dict(effects,chol=effect)};base,_,_=ns['execute'](flat,aa,qq)
   for timing in S['timings']:
    trace=replay(base,shifts if timing=='I' else {});traces[model,timing]=trace
    for serial,(i,r) in enumerate(trace):
     if timing=='O':
      assert all(str(r[k])==str(base[i][k]) for k in ['status','before','after','state_origin','order'])
     events.append(dict(paragraph=p['id'],grammar=g,model=model,timing=timing,source_event=i,execution_index=serial,**r))
     if r['kind']=='ACTION' and r['form']=='chol':targets.append(dict(paragraph=p['id'],grammar=g,model=model,timing=timing,operation=r['location'],patient=r['patient'],patient_form=byid[r['patient']]['form'] if r['patient'] else '',object=r['object'],before=r['before'],after=r['after'],status=r['status'],debts=r['debts']))
    summary.append(dict(paragraph=p['id'],grammar=g,model=model,timing=timing,events=len(trace),input_shifts=len(shifts) if timing=='I' else 0,conflicts=sum(r['status']=='CONFLICT' for i,r in trace),unequal=sum(r['status']=='DIFFERENT_NOT_OPPOSED' for i,r in trace),missing_assertions=sum(r['status']=='MISSING_PATIENT' for i,r in trace),incomplete_actions=sum(r['kind']=='ACTION' and r['status']=='ARGUMENT_INCOMPLETE' for i,r in trace)))
  for timing in S['timings']:
   for (i,a),(j,b) in zip(traces['D',timing],traces['H',timing]):
    assert i==j and all(a[k]==b[k] for k in ['kind','location','form','patient','object','second_object','debts'])
    if any(a[k]!=b[k] for k in ['before','after','status','assertion','state_origin']):diff.append(dict(paragraph=p['id'],grammar=g,timing=timing,event=i,location=a['location'],kind=a['kind'],form=a['form'],object=a['object'],D_status=a['status'],H_status=b['status'],D_before=a['before'],H_before=b['before'],D_after=a['after'],H_after=b['after'],D_assertion=a['assertion'],H_assertion=b['assertion']))
for n,rr in [('SOURCE_FLAT',flatout),('ARGUMENTS',args),('QUALITY',quality),('INPUT_ELIGIBILITY',census),('EVENTS',events),('WORLD_SUMMARY',summary),('CHOL_TARGETS',targets),('DIFFERENCES',diff)]:table(n+'.tsv',rr)
table('TAKE_ARGUMENTS.tsv',takes,['paragraph','grammar','target','patient','patient_form','rule','debts'])
full=[dict(paragraph=r['paragraph'],locus=r['locus'],index=r['index'],raw=r['form'],role=r['role'],D='trockne' if r['form']=='chol' else glosses.get(r['form'],'[ungelesen: '+r['form']+']'),H='erhitze' if r['form']=='chol' else glosses.get(r['form'],'[ungelesen: '+r['form']+']'),status='ASSUMED' if r['form'] in glosses and not glosses[r['form']].startswith('[ungelesen') else 'UNREAD') for r in flatout];table('ALIGNMENT.tsv',full)
reader=['# W36 vollständige hypothetische Lesung '+RUN_ID+'','W28 plus registrierte unabhängige Ganzwortnomina chocthy/cthaiin; keine Bedeutungsbestätigung. Übernommen: shol Q=feucht / A=befeuchte, hier '+SHOL_MODEL+'. chol D=trockne/H=erhitze. Keine Übersetzungsbestätigung. GDT809s beschreibende Rivalen bleiben offen.']
for p in source:
 reader.append('\n## '+p['id'])
 for l in p['lines']:
  rr=[r for r in full if r['locus']==l['locus']];reader.append('\n'+l['locus']+'\n\n'+' · '.join(r['raw']+' ['+('D: trockne / H: erhitze' if r['raw']=='chol' else r['H'])+']' for r in rr))
(E/(RUN_ID+'_READING.md')).write_text('\n'.join(reader)+'\n')
result=dict(paragraphs=len(source),lines=sum(len(p['lines']) for p in source),groups=len(full),assumed=sum(r['status']=='ASSUMED' for r in full),unread=sum(r['status']=='UNREAD' for r in full),chol_positions=sum(r['raw']=='chol' for r in full),worlds=len(summary),events=len(events),models={m:{t:{k:sum(r[k] for r in summary if r['model']==m and r['timing']==t) for k in ['conflicts','unequal','missing_assertions','incomplete_actions','input_shifts']} for t in S['timings']} for m in S['models']},confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
(E/(RUN_ID+'_RESULT.json')).write_text(json.dumps(result,indent=2)+'\n');print(RUN_ID,json.dumps(result))
