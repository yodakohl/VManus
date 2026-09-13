"""Separate consequence audit against frozen source events, without importing build."""
import csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent; W=E.parent; ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
S=json.loads((E/'SPEC.json').read_text())
for f in S['inputs']: assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
old=rows(W/'W18/EVENTS.tsv');new=rows(E/'EVENTS.tsv');assert len(old)==3528 and len(new)==7056
keys=lambda r:(r['model'],r['world'],r['source_event'])
index={keys(r):r for r in old}; assert len(index)==3528
worlds=collections.defaultdict(list)
for r in new:
 o=index[keys(r)]
 if r['verb']=='X':assert all(r[k]==v for k,v in o.items())
 else:
  mutable={'before','after','status','state_origin','debts'}
  assert all(r[k]==v for k,v in o.items() if k not in mutable)
  expected=';'.join(x for x in o['debts'].split(';') if x and x!='EXTRACT_PATIENT_NOT_BOUND') if r['form']=='qokeor' and r['kind']=='ACTION' else o['debts']
  assert r['debts']==expected
 worlds[r['verb'],r['model'],r['world']].append(r)
repindex={(r['verb'],r['model'],r['world'],r['target']):r for r in rows(E/'REPEAT_TARGETS.tsv')};assert len(repindex)==90
witness=rows(E/'REPEAT_WITNESSES.tsv');pairs=0
for key,rr in worlds.items():
 states={};origins={};prior=[]
 for r in rr:
  oid=r['object'];before=states.get(oid,{}).copy();assert json.loads(r['before'])==before
  if r['kind']=='MATERIAL':
   if oid:states.setdefault(oid,{})
  elif r['kind']=='ACTION':
   effect=json.loads(r['assertion']) if r['assertion'] else None
   invalid=not oid or any(x in r['debts'].split(';') for x in ['EXTRACT_PATIENT_NOT_BOUND','MISSING_RELATION_PARTNER']) or (r['second'] and not r['second_object'])
   assert r['status']==('ARGUMENT_INCOMPLETE' if invalid else 'ASSUMED_EFFECT_APPLIED' if effect else 'NO_STATE_TRANSITION_MODELLED')
   if not invalid and effect:
    k='PHYSICAL:'+effect['axis'];states[oid][k]=effect['value'];origins[oid,k]=r['location']
   if r['form'] in ['ykeey','yteey']:
    eligible=[p for p in prior if oid and p['object']==oid and p['kind']=='ACTION' and p['status']=='ASSUMED_EFFECT_APPLIED']; pairs+=len(prior)
    exact=[p for p in eligible if json.loads(p['assertion'])==effect]
    rec=repindex[(*key,r['location'])];assert int(rec['exact_effect_witnesses'])==len(exact)
    got=[p['witness'] for p in witness if (p['verb'],p['model'],p['world'],p['target'])==(*key,r['location']) and p['kind']=='REP_EXACT']
    assert got==[p['location'] for p in exact]
  else:
   k,v=r['assertion'].split('=',1);p=before.get(k)
   opposition=(k.endswith(':thermal') and p=='cold' and v in ['hot','warm']) or (k.endswith(':thermal') and v=='cold' and p in ['hot','warm']) or (k.endswith(':moisture') and {p,v}=={'wet','dry'})
   expected='MISSING_PATIENT' if not oid else 'INITIAL_CONSTRAINT' if p is None else 'MATCH' if p==v else 'CONFLICT' if opposition else 'DIFFERENT_NOT_OPPOSED'
   assert r['status']==expected and r['state_origin']==origins.get((oid,k),'')
   if oid and p is None:states[oid][k]=v;origins[oid,k]=r['location']
  assert json.loads(r['after'])==states.get(oid,{})
  prior.append(r)
a=rows(W/'W17/ALIGNMENT.tsv');b=rows(E/'ALIGNMENT.tsv');assert len(a)==len(b)==900
for x,y in zip(a,b):
 assert all(y[k]==v for k,v in x.items());assert y['X']==x['joint'];assert y['G']==('erhitze' if x['raw']=='qokeor' else x['joint'])
args=rows(E/'ARGUMENTS.tsv');source=[r for r in rows(W/'W17/ACTION_CONSEQUENCES.tsv') if r['form']=='qokeor'];assert len(args)==2*len(source)==162
for i,r in enumerate(source):
 for a in args[2*i:2*i+2]:assert all(a[k]==v for k,v in r.items())
result={'status':'PASS','frozen_files':len(S['inputs']),'replayed_events':len(new),'repeat_targets':len(repindex),'prior_event_pairs_checked':pairs,'raw_groups':900,'source_X_exact':True,'reserved_access':False}
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
