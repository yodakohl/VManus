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
for run in ['P_Q','P_A','K_Q','K_A','PK_Q','PK_A']:
 candidate,sm=run.split('_');nominals={'P':['chocthy'],'K':['cthaiin'],'PK':['chocthy','cthaiin']}[candidate]
 D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')}
 for w,o in rules['word_overrides'].items():D[w].update(o)
 D.update(sheeody={'role':'MATERIAL','hypothesis':'Pulver'},qokeeo={'role':'ACTION','hypothesis':'rühre'})
 D['sal']={'role':'MATERIAL','hypothesis':'Arzneimaterial'}
 glosses={r['raw']:r['joint'] for r in rows(W/'W16/ALIGNMENT.tsv')}
 glosses['sal']='Arzneimaterial [Hypothese; Präparat/Salz offen]'
 for nominal in nominals:
  D[nominal]={'role':'MATERIAL','hypothesis':'trockene Krautzubereitung' if nominal=='chocthy' else 'Krautposten'}
  glosses[nominal]='trockene Krautzubereitung [Hypothese]' if nominal=='chocthy' else 'Krautposten [Wertachse offen; Hypothese]'
 if sm=='A':D['shol']={'role':'ACTION','hypothesis':'befeuchte'};glosses['shol']='befeuchte'
 aa=rows(E/(run+'_ALIGNMENT.tsv'));assert [(r['paragraph'],r['locus'],r['index'],r['raw']) for r in aa]==raw
 for r in aa:
  for m in ['D','H']:assert r[m]==({'D':'trockne','H':'erhitze'}[m] if r['raw']=='chol' else glosses.get(r['raw'],'[ungelesen: '+r['raw']+']'))
 args=rows(E/(run+'_ARGUMENTS.tsv'));ix={(r['paragraph'],r['grammar'],r['operation']):r for r in args};qq=rows(E/(run+'_QUALITY.tsv'));qx={(r['paragraph'],r['grammar'],r['mention']):r for r in qq};seen=set();qseen=set()
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
    if x['role']=='STATE' and x['form'] in stand:
     f=stand[x['form']];q=requal(dict(mention=x['id'],kind='STANDALONE',form=x['form'],axis=f['axis'],value=f['value'],scope='PHYSICAL'),ff,ar);key=(p['id'],g,x['id']);qseen.add(key);assert all(qx[key][k]==v for k,v in q.items());countqualities+=1
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
 assert len(ww)==204 and len(events)==5436+12*sum((2 if r['raw']=='chocthy' else 1) for r in aa if r['raw'] in nominals)

# Whole nominal types, not physical drying or numerical dose inference.
for run,ww in worlds.items():
 for trace in ww.values():
  for r in trace:
   if r['form']=='chocthy' and r['kind']!='MATERIAL' and r['location'].endswith((':3',':4')) and r['kind']!='ACTION':
    assert r['kind']=='BARE_NOMINAL' and r['assertion']=='CONSTITUTION:moisture=dry'
   if r['form']=='cthaiin':assert r['kind']=='MATERIAL'
for sm in ['Q','A']:
 for c in ['P','K','PK']:
  a=rows(E/(c+'_'+sm+'_ARGUMENTS.tsv'))
  f=[r for r in a if r['operation']=='f32v.9:1'];assert len(f)==3
  for r in f:
   assert r['patient']==('f32v.9:6' if c=='K' else 'f32v.9:4')
   assert r['coingredient']==('f32v.9:6' if c=='PK' else '')
   assert ('MISSING_RELATION_PARTNER' in r['debts'])==(c!='PK')
  if c!='K':
   for r in [r for r in a if r['operation']=='f22v.15:4']:assert (r['patient'],r['coingredient'])==('f22v.15:3','f22v.15:2')
result=dict(status='PASS',bound_files=len(S['inputs']),source_groups=1045,new_runs=6,replayed_arguments=countargs,replayed_qualities=countqualities,independent_state_events=sum(len(rr) for ww in worlds.values() for rr in ww.values()),registered_f32_pair_prediction=True,registered_f22_displacement=True,take_independently_reapplied=True,limits='Frozen grammar reused; independent state audit, no meaning confirmation')
# Every nominal target and its direct/displaced-object continuation, including baseline C.
for sm in ['Q','A']:
 ww=collections.defaultdict(list)
 for r in rows(W/'W28'/(sm+'_EVENTS.tsv')):ww[r['paragraph'],r['grammar'],r['model'],r['timing']].append(r)
 worlds['C_'+sm]=ww
candidates=rows(E/'CANDIDATES.tsv');got_later=rows(E/'ALL_LATER_REQUIREMENTS.tsv');expected_later=[];seen=set()
for t in candidates:
 run=t['candidate']+'_'+t['shol'];key=t['paragraph'],t['grammar'],t['model'],t['timing'];trace=worlds[run][key];old=worlds['C_'+t['shol']][key];identity=run,key,t['target'];assert identity not in seen;seen.add(identity)
 mat=next((r for r in trace if r['kind']=='MATERIAL' and r['location']==t['target']),None);assert t['material']==str(bool(mat)) and t['object']==(mat['object'] if mat else '')
 direct=[r for r in trace if r['kind'] in ['ACTION','QUALITY'] and (r['patient']==t['target'] or r.get('second')==t['target'])];assert t['direct_actions']==';'.join(r['location'] for r in direct if r['kind']=='ACTION') and t['direct_qualities']==';'.join(r['location'] for r in direct if r['kind']=='QUALITY')
 if not mat:continue
 index=lambda r:(r['kind'],r['location'],r['assertion']);oi={index(r):r for r in old};ni={index(r):r for r in trace}
 displaced={oi[index(r)][f] for r in direct if index(r) in oi for f in ['object','second_object'] if oi[index(r)][f]!=r[f]}-{''};assert t['displaced_objects']==';'.join(sorted(displaced));objects=displaced|{mat['object']}
 # Offset remains source-bound; material event order is exactly the written offset.
 selected=set()
 for rr in [old,trace]:
  for r in rr:
   if int(r['order'])>=int(mat['order']) and r['kind']!='MATERIAL' and (r['object'] in objects or r['second_object'] in objects):selected.add(index(r))
 for k in selected:
  a=oi.get(k);b=ni.get(k);expected_later.append((identity,k[0],k[1],a['status'] if a else 'ABSENT',b['status'] if b else 'ABSENT',a['before'] if a else '',b['before'] if b else '',a['after'] if a else '',b['after'] if b else ''))
got=[((r['candidate']+'_'+r['shol'],tuple(r[k] for k in ['paragraph','grammar','model','timing']),r['target']),r['kind'],r['location'],r['C_status'],r['N_status'],r['C_before'],r['N_before'],r['C_after'],r['N_after']) for r in got_later];assert collections.Counter(got)==collections.Counter(expected_later)
assert len(candidates)==288 and len(got_later)==240
result.update(candidate_rows=288,all_later_requirements=240)
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
assert not rows(E/'ALL_LATER_TAKE.tsv')
print(json.dumps(result))

reader=(E/'READING.md').read_text()
for p in source:
 for l in p['lines']:assert reader.count('`'+' '.join(l['words'])+'`')==1
for r in rows(E/'BINDING_GAPS.tsv'):
 folder=W/'W28' if r['candidate']=='C' else E;pre=r['shol'] if r['candidate']=='C' else r['candidate']+'_'+r['shol'];ff=rows(folder/(pre+'_SOURCE_FLAT.tsv'));byid={x['id']:x for x in ff}
 ids=[r[k] for k in ['operation','patient','second'] if r[k]];a,b=min(int(byid[x]['offset']) for x in ids),max(int(byid[x]['offset']) for x in ids)
 gap=[x for x in ff if x['paragraph']==r['paragraph'] and a<int(x['offset'])<b and x['role']=='OPEN']
 assert r['diagnostic_open_ids']==';'.join(x['id'] for x in gap) and r['diagnostic_open_forms']==';'.join(x['form'] for x in gap)
 if r['candidate']=='PK' and r['operation']=='f32v.9:1':assert r['diagnostic_open_forms']=='cfhy;skey' and r['engine_debts']==''
result.update(full_reader_groups=1045,gap_diagnostics=len(rows(E/'BINDING_GAPS.tsv')))
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
