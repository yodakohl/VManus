"""Independent coverage and physical audit; frozen argument functions reused."""
import ast,copy,csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def read(p):return json.loads(p.read_text())
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
source=read(E/'SOURCE.json')['paragraphs'];expected=[{'id':t['hosts']['ZL3b'][0]['id'],'lines':t['hosts']['ZL3b'][0]['lines']} for t in read(W/'W02/SOURCE.json')['targets']]+read(W/'W25/SOURCE.json')['paragraphs'];assert source==expected and len(source)==17
raw=[(p['id'],l['locus'],str(i),w) for p in source for l in p['lines'] for i,w in enumerate(l['words'],1)];assert len(raw)==1045
rules=read(W/'W05/SPEC.json');ACT=set(rules['action_roles']);MAT=set(rules['material_roles']);MOD=set(rules['transparent_roles']);extracts={'cheor','okeeor','okeor','keeor','cheeor','sheeor'}
for folder,name in [('W05','base_arguments'),('W11','solve'),('W13','requal')]:
 n=next(n for n in ast.parse((W/folder/'build.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[n],type_ignores=[]),'frozen_grammar','exec'))
stand={f['form']:f for f in read(W/'W03/SPEC.json')['features'] if f['kind']=='STANDALONE'};countargs=0;countqualities=0;worlds={}
for sm in ['Q','A']:
 D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')}
 for w,o in rules['word_overrides'].items():D[w].update(o)
 D.update(sheeody={'role':'MATERIAL','hypothesis':'Pulver'},qokeeo={'role':'ACTION','hypothesis':'rühre'})
 glosses={r['raw']:r['joint'] for r in rows(W/'W16/ALIGNMENT.tsv')}
 if sm=='A':D['shol']={'role':'ACTION','hypothesis':'befeuchte'};glosses['shol']='befeuchte'
 aa=rows(E/(sm+'_ALIGNMENT.tsv'));assert [(r['paragraph'],r['locus'],r['index'],r['raw']) for r in aa]==raw
 for r in aa:
  for m in ['D','H']:assert r[m]==({'D':'trockne','H':'erhitze'}[m] if r['raw']=='chol' else glosses.get(r['raw'],'[ungelesen: '+r['raw']+']'))
 args=rows(E/(sm+'_ARGUMENTS.tsv'));ix={(r['paragraph'],r['grammar'],r['operation']):r for r in args};qq=rows(E/(sm+'_QUALITY.tsv'));qx={(r['paragraph'],r['grammar'],r['mention']):r for r in qq};seen=set();qseen=set()
 for p in source:
  ff=[]
  for l in p['lines']:
   for i,w in enumerate(l['words'],1):ff.append(dict(id=l['locus']+':'+str(i),locus=l['locus'],index=i,form=w,role=D.get(w,{}).get('role','OPEN'),offset=len(ff)))
  for g,ar in solve(ff).items():
   for a in ar:
    key=(p['id'],g,a['operation']);seen.add(key);assert all(ix[key][k]==v for k,v in a.items());countargs+=1
   for x in ff:
    if x['role']=='STATE' and x['form'] in stand:
     f=stand[x['form']];q=requal(dict(mention=x['id'],kind='STANDALONE',form=x['form'],axis=f['axis'],value=f['value'],scope='PHYSICAL'),ff,ar);key=(p['id'],g,x['id']);qseen.add(key);assert all(qx[key][k]==v for k,v in q.items());countqualities+=1
 assert seen==set(ix) and len(seen)==len(args) and qseen==set(qx) and len(qseen)==len(qq)
 events=rows(E/(sm+'_EVENTS.tsv'));ww=collections.defaultdict(list)
 for r in events:ww[r['paragraph'],r['grammar'],r['model'],r['timing']].append(r)
 worlds[sm]=ww
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
 assert len(ww)==204 and len(events)==5412
old=rows(W/'W25/EVENTS.tsv');herb={r['paragraph'] for r in old};assert [r for r in rows(E/'Q_EVENTS.tsv') if r['paragraph'] in herb]==old
assert rows(E/'Q_TAKE_ARGUMENTS.tsv')==rows(E/'A_TAKE_ARGUMENTS.tsv')
expected_futures=[];targetrows=rows(E/'SHOL_TARGETS.tsv');assert len(targetrows)==96
for t in targetrows:
 key=t['paragraph'],t['grammar'],t['chol'],t['timing']
 for sm in ['Q','A']:
  rr=worlds[sm][key];match=[r for r in rr if r['form']=='shol' and r['location']==t['target']];assert len(match)==1;target=match[0];assert target['patient']==t[sm+'_patient'] and target['object']==t[sm+'_object'] and target['status']==t[sm+'_status']
  for r in rr[rr.index(target)+1:]:
   if target['object'] and target['object']==r['object']:expected_futures.append((key,sm,t['target'],r['kind'],r['location'],r['object'],r['status']))
got=[((r['paragraph'],r['grammar'],r['chol'],r['timing']),r['shol_model'],r['target'],r['kind'],r['location'],r['object'],r['status']) for r in rows(E/'ALL_TARGET_FUTURES.tsv')];assert collections.Counter(got)==collections.Counter(expected_futures)
new_conflicts=[]
for key,rr in worlds['A'].items():
 old={(r['kind'],r['location']):r for r in worlds['Q'][key]}
 for r in rr:
  if r['status']=='CONFLICT' and old.get((r['kind'],r['location']),{}).get('status')!='CONFLICT':new_conflicts.append((key,r['location']))
result=dict(status='PASS',bound_files=len(S['inputs']),groups=1045,replayed_arguments=countargs,replayed_qualities=countqualities,state_events=10824,target_cases=96,target_future_rows=len(got),HERB4_Q_parity=True,take_parity=True,new_hard_conflicts=new_conflicts,limits='Old grammar reused, full new state and coverage audit; no independent semantic validation')
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
