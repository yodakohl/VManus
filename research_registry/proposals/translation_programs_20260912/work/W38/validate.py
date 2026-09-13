"""Independent coverage and physical audit; frozen argument functions reused."""
import ast,copy,csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def read(p):return json.loads(p.read_text())
S=read(E/'SPEC.json');S['variants']=['B','J','M'];assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
source=read(E/'SOURCE.json')['paragraphs'];expected=[{'id':t['hosts']['ZL3b'][0]['id'],'lines':t['hosts']['ZL3b'][0]['lines']} for t in read(W/'W02/SOURCE.json')['targets']]+read(W/'W25/SOURCE.json')['paragraphs'];assert source==expected and len(source)==17
raw=[(p['id'],l['locus'],str(i),w) for p in source for l in p['lines'] for i,w in enumerate(l['words'],1)];assert len(raw)==1045
rules=read(W/'W05/SPEC.json');ACT=set(rules['action_roles']);MAT=set(rules['material_roles']);MOD=set(rules['transparent_roles']);extracts={'cheor','okeeor','okeor','keeor','cheeor','sheeor'}
for folder,name in [('W05','base_arguments'),('W11','solve'),('W13','requal'),('W16','take')]:
 n=next(n for n in ast.parse((W/folder/'build.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[n],type_ignores=[]),'frozen_grammar','exec'))
stand={f['form']:f for f in read(W/'W03/SPEC.json')['features'] if f['kind']=='STANDALONE'};countargs=0;countqualities=0;worlds={}
for run in ['P_Q','P_A','C_Q','C_A']:
 candidate,sm=run.split('_');nominals=['chocthy','cthaiin'];quality_scope={'P':'PHYSICAL','C':'CONSTITUTION'}[candidate]
 D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')}
 for w,o in rules['word_overrides'].items():D[w].update(o)
 D.update(sheeody={'role':'MATERIAL','hypothesis':'Pulver'},qokeeo={'role':'ACTION','hypothesis':'rühre'})
 D['sal']={'role':'MATERIAL','hypothesis':'Arzneimaterial'}
 glosses={r['raw']:r['joint'] for r in rows(W/'W16/ALIGNMENT.tsv')}
 glosses['sal']='Arzneimaterial [Hypothese; Präparat/Salz offen]'
 for nominal in nominals:
  D[nominal]={'role':'MATERIAL','hypothesis':'trockene Krautzubereitung' if nominal=='chocthy' else 'Krautposten'}
  glosses[nominal]='trockene Krautzubereitung [Hypothese]' if nominal=='chocthy' else 'Krautposten [Wertachse offen; Hypothese]'
 D['cfhy']={'role':'LINK','hypothesis':'Untereintrag'};glosses['cfhy']='Untereintrag [Strukturhypothese]'
 D['chkaiin']={'role':'STATE','hypothesis':'heiß-trocken [Wertklasse offen]'};glosses['chkaiin']='heiß-trocken [Hypothese; '+quality_scope+'; Wertklasse offen]'
 if sm=='A':D['shol']={'role':'ACTION','hypothesis':'befeuchte'};glosses['shol']='befeuchte'
 aa=rows(E/(run+'_ALIGNMENT.tsv'));assert [(r['paragraph'],r['locus'],r['index'],r['raw']) for r in aa]==raw
 for r in aa:
  for m in ['D','H']:assert r[m]==({'D':'trockne','H':'erhitze'}[m] if r['raw']=='chol' else glosses.get(r['raw'],'[ungelesen: '+r['raw']+']'))
 args=rows(E/(run+'_ARGUMENTS.tsv'));ix={(r['paragraph'],r['grammar'],r['operation']):r for r in args};qq=rows(E/(run+'_QUALITY.tsv'));qx={(r['paragraph'],r['grammar'],r['mention'],r['axis']):r for r in qq};seen=set();qseen=set()
 take_rows=rows(E/(run+'_TAKE_ARGUMENTS.tsv'));take_index={(r['paragraph'],r['grammar'],r['target']):r for r in take_rows};take_seen=set()
 for p in source:
  ff=[]
  for l in p['lines']:
   for i,w in enumerate(l['words'],1):ff.append(dict(id=l['locus']+':'+str(i),locus=l['locus'],index=i,form=w,role=D.get(w,{}).get('role','OPEN'),offset=len(ff)))
  for g,ar in solve(ff).items():
   for x in ff:
    if x['form']=='ychor':
     key=(p['id'],g,x['id']);take_seen.add(key);assert all(take_index[key][k]==v for k,v in take(ff,x,ar,g).items())
   for a in ar:
    key=(p['id'],g,a['operation']);seen.add(key);assert all(ix[key][k]==v for k,v in a.items());countargs+=1
   for x in ff:
    if x['role']=='STATE' and (x['form'] in stand or x['form']=='chkaiin'):
     fs=[dict(axis='thermal',value='hot',scope=quality_scope),dict(axis='moisture',value='dry',scope=quality_scope)] if x['form']=='chkaiin' else [dict(stand[x['form']],scope='PHYSICAL')]
     for f in fs:
      q=requal(dict(mention=x['id'],kind='STANDALONE',form=x['form'],axis=f['axis'],value=f['value'],scope=f['scope']),ff,ar);key=(p['id'],g,x['id'],f['axis']);qseen.add(key);assert all(qx[key][k]==v for k,v in q.items());countqualities+=1
 assert take_seen==set(take_index)
 assert seen==set(ix) and len(seen)==len(args) and qseen==set(qx) and len(qseen)==len(qq)
 events=rows(E/(run+'_EVENTS.tsv'));ww=collections.defaultdict(list)
 for r in events:ww[r['paragraph'],r['grammar'],r['model'],r['timing']].append(r)
 worlds[run]=ww
 for key,rr in ww.items():
  state={};origin={};effects=read(W/'W09/SPEC.json')['effects'];effects['chol']=S['models'][key[2]]
  if sm=='A':effects['shol']={'axis':'moisture','value':'wet'}
  for r in rr:
   oid=r['object'];before=state.get(oid,{}).copy();assert json.loads(r['before'])==before
   if r['kind']=='MATERIAL':state.setdefault(oid,{})
   elif r['kind']=='ACTION':
    effect=json.loads(r['assertion']) if r['assertion'] else None;assert effect==effects.get(r['form'])
    invalid=not oid or any(x in r['debts'].split(';') for x in ['EXTRACT_PATIENT_NOT_BOUND','MISSING_RELATION_PARTNER'])
    assert r['status']==('ARGUMENT_INCOMPLETE' if invalid else 'ASSUMED_EFFECT_APPLIED' if effect else 'NO_STATE_TRANSITION_MODELLED')
    if not invalid and effect:k='PHYSICAL:'+effect['axis'];state[oid][k]=effect['value'];origin[oid,k]=r['location']
   else:
    k,v=r['assertion'].split('=',1);prior=before.get(k);opp=k.endswith(':moisture') and {prior,v}=={'wet','dry'} or k.endswith(':thermal') and ((prior=='cold' and v in ['hot','warm']) or (v=='cold' and prior in ['hot','warm']))
    status='MISSING_PATIENT' if not oid else 'INITIAL_CONSTRAINT' if prior is None else 'MATCH' if prior==v else 'CONFLICT' if opp else 'DIFFERENT_NOT_OPPOSED'
    assert r['status']==status and r['state_origin']==origin.get((oid,k),'')
    if oid and prior is None:state[oid][k]=v;origin[oid,k]=r['location']
   assert json.loads(r['after'])==state.get(oid,{})
 assert len(ww)==204 and len(events)==5568


T=rows(E/'CANDIDATES.tsv');H=rows(E/'ALL_PRIOR_CARRIER_EVENTS.tsv');F=rows(E/'ALL_LATER_CARRIER_EVENTS.tsv');assert len(T)==144 and not F
meta=['scope','shol','paragraph','grammar','model','timing','target'];expected_history=[];seen=set()
for c in T:
 run=c['scope']+'_'+c['shol'];key=tuple(c[k] for k in ['paragraph','grammar','model','timing']);trace=worlds[run][key];ident=tuple(c[k] for k in meta);assert ident not in seen;seen.add(ident)
 tt=[r for r in trace if r['location']==c['target'] and r['form']=='chkaiin'];assert len(tt)==2
 assert c['patient']=={'f9v.12:1':'','f21r.9:4':'f21r.9:2','f21r.12:8':'f21r.12:5'}[c['target']]
 for axis in ['thermal','moisture']:
  r=next(r for r in tt if ':'+axis+'=' in r['assertion']);assert c[axis+'_status']==r['status'] and c[axis+'_before']==r['before'] and c[axis+'_origin']==r['state_origin']
  assert r['assertion']=={'P':'PHYSICAL','C':'CONSTITUTION'}[c['scope']]+':'+axis+'='+{'thermal':'hot','moisture':'dry'}[axis]
  if c['target']=='f9v.12:1':assert r['status']=='MISSING_PATIENT'
  elif c['scope']=='C' or c['target']=='f21r.9:4':assert r['status']=='INITIAL_CONSTRAINT'
  elif c['model']=='H':assert r['status']==('MATCH' if axis=='thermal' else 'CONFLICT')
  else:assert r['status']==('DIFFERENT_NOT_OPPOSED' if axis=='thermal' else 'MATCH')
 oid=c['object'];a=min(int(r['execution_index']) for r in tt);b=max(int(r['execution_index']) for r in tt)
 if oid:
  for r in trace:
   if r['object']==oid or r['second_object']==oid:
    if int(r['execution_index'])<a:expected_history.append((ident,r['location'],r['kind'],r['assertion'],r['before'],r['after']))
    assert int(r['execution_index'])<=b
assert collections.Counter(expected_history)==collections.Counter((tuple(r[k] for k in meta),r['location'],r['kind'],r['assertion'],r['before'],r['after']) for r in H)
for sm in ['Q','A']:
 for scope in ['P','C']:
  for name in ['ARGUMENTS','TAKE_ARGUMENTS']:
   assert rows(E/(scope+'_'+sm+'_'+name+'.tsv'))==rows(W/'W37'/('S_'+sm+'_'+name+'.tsv'))
result=dict(status='PASS',bound_files=len(S['inputs']),source_groups=1045,replayed_arguments=countargs,replayed_qualities=countqualities,independent_state_events=sum(len(r) for ww in worlds.values() for r in ww.values()),target_cases=len(T),prior_carrier_events=len(H),later_carrier_events=0,scope_predictions_verified=True,limits='Fixed grammar reapplied; independent state and complete carrier-history audit, no independent meaning validation')
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
