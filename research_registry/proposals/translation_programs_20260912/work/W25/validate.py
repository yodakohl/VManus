"""Separate source coverage, fixed binding replay and state-transition audit."""
import ast,collections,copy,csv,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
source=read(E/'SOURCE.json');blocks=re.findall(r'```text\n(.*?)```',(ROOT/source['source_report']).read_text(),re.S);raw=[]
assert len(blocks)==len(source['paragraphs'])==4
for block,p in zip(blocks,source['paragraphs']):
 assert len(block.strip().splitlines())==len(p['lines'])
 for text,l in zip(block.strip().splitlines(),p['lines']):
  loc,words=text.split(None,1);assert loc==l['locus'] and words.split()==l['words']
  raw.extend((loc,str(i),w) for i,w in enumerate(l['words'],1))
a=rows(E/'ALIGNMENT.tsv');assert len(raw)==len(a)==145 and raw==[(r['locus'],r['index'],r['raw']) for r in a]
D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')};rules=read(W/'W05/SPEC.json')
for w,o in rules['word_overrides'].items():D[w].update(o)
D.update(sheeody={'role':'MATERIAL','hypothesis':'Pulver'},qokeeo={'role':'ACTION','hypothesis':'rühre'})
ACT=set(rules['action_roles']);MAT=set(rules['material_roles']);MOD=set(rules['transparent_roles']);extracts={'cheor','okeeor','okeor','keeor','cheeor','sheeor'}
glosses={r['raw']:r['joint'] for r in rows(W/'W16/ALIGNMENT.tsv')}
for folder,name in [('W05','base_arguments'),('W11','solve'),('W13','requal')]:
 n=next(n for n in ast.parse((W/folder/'build.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[n],type_ignores=[]),'frozen_grammar','exec'))
argrows=rows(E/'ARGUMENTS.tsv');ix={(r['paragraph'],r['grammar'],r['operation']):r for r in argrows};qualrows=rows(E/'QUALITY.tsv');qix={(r['paragraph'],r['grammar'],r['mention']):r for r in qualrows}
features=read(W/'W03/SPEC.json')['features'];stand={f['form']:f for f in features if f['kind']=='STANDALONE'};checked=0;qchecked=0
for p in source['paragraphs']:
 flat=[]
 for l in p['lines']:
  for i,w in enumerate(l['words'],1):flat.append(dict(id=l['locus']+':'+str(i),locus=l['locus'],index=i,form=w,role=D.get(w,{}).get('role','OPEN'),offset=len(flat)))
 for g,aa in solve(flat).items():
  for ar in aa:assert all(ix[p['id'],g,ar['operation']][k]==v for k,v in ar.items());checked+=1
  for x in flat:
   if x['role']!='STATE' or x['form'] not in stand:continue
   f=stand[x['form']];q=requal(dict(mention=x['id'],kind='STANDALONE',form=x['form'],axis=f['axis'],value=f['value'],scope='PHYSICAL'),flat,aa)
   assert all(qix[p['id'],g,x['id']][k]==v for k,v in q.items());qchecked+=1
assert checked==len(ix)==len(argrows) and qchecked==len(qix)==len(qualrows)
events=rows(E/'EVENTS.tsv');worlds=collections.defaultdict(list)
for r in events:worlds[r['paragraph'],r['grammar'],r['model'],r['timing']].append(r)
assert len(worlds)==48 and len(events)==660
for key,rr in worlds.items():
 state={};origin={}
 for r in rr:
  oid=r['object'];before=state.get(oid,{}).copy();assert json.loads(r['before'])==before
  if r['kind']=='MATERIAL':state.setdefault(oid,{})
  elif r['kind']=='ACTION':
   effect=json.loads(r['assertion']) if r['assertion'] else None
   invalid=not oid or any(x in r['debts'].split(';') for x in ['EXTRACT_PATIENT_NOT_BOUND','MISSING_RELATION_PARTNER'])
   assert r['status']==('ARGUMENT_INCOMPLETE' if invalid else 'ASSUMED_EFFECT_APPLIED' if effect else 'NO_STATE_TRANSITION_MODELLED')
   if not invalid and effect:
    k='PHYSICAL:'+effect['axis'];state[oid][k]=effect['value'];origin[oid,k]=r['location']
  else:
   k,v=r['assertion'].split('=',1);old=before.get(k);opposed=k.endswith(':moisture') and {old,v}=={'wet','dry'} or k.endswith(':thermal') and ((old=='cold' and v in ['warm','hot']) or (v=='cold' and old in ['warm','hot']))
   expected='MISSING_PATIENT' if not oid else 'INITIAL_CONSTRAINT' if old is None else 'MATCH' if old==v else 'CONFLICT' if opposed else 'DIFFERENT_NOT_OPPOSED'
   assert r['status']==expected and r['state_origin']==origin.get((oid,k),'')
   if oid and old is None:state[oid][k]=v;origin[oid,k]=r['location']
  assert json.loads(r['after'])==state.get(oid,{})
# Both timing variants are retained; here no quality meets the fixed input rule.
assert not any(r['input_eligible']=='True' for r in rows(E/'INPUT_ELIGIBILITY.tsv'))
for (p,g,m,t),rr in worlds.items():
 if t=='I':assert [{k:v for k,v in r.items() if k!='timing'} for r in rr]==[{k:v for k,v in r.items() if k!='timing'} for r in worlds[p,g,m,'O']]
for r in rows(E/'WORLD_SUMMARY.tsv'):
 rr=worlds[r['paragraph'],r['grammar'],r['model'],r['timing']];assert int(r['events'])==len(rr)
 for k,status in [('conflicts','CONFLICT'),('unequal','DIFFERENT_NOT_OPPOSED'),('missing_assertions','MISSING_PATIENT')]:assert int(r[k])==sum(x['status']==status for x in rr)
for r in a:
 for m in ['D','H']:assert r[m]==({'D':'trockne','H':'erhitze'}[m] if r['raw']=='chol' else glosses.get(r['raw'],'[ungelesen: '+r['raw']+']'))
result=dict(status='PASS',bound_input_files=len(S['inputs']),source_groups=145,replayed_arguments=checked,replayed_qualities=qchecked,state_events=660,worlds=48,limits='Frozen grammar reused; new state transitions independently audited; no semantic validation')
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
