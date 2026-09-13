"""Audit every published transition as a local constraint; no builder import."""
import csv,json,hashlib
from pathlib import Path
from collections import defaultdict,Counter
D=Path(__file__).parent
S=json.loads((D/'SPEC.json').read_text())
for p,h in S['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
raw=[]
for r in csv.DictReader(Path(S['source']).open(),delimiter='\t'):
 assert r['page']=='f83r' and r['record_id'] in S['records']
 raw.extend((r['record_id'],r['locus']+':'+str(i),w) for i,w in enumerate(r['zl3b_line'].split(),1))
assert len(raw)==341
als=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'))
es=list(csv.DictReader((D/'EVENTS.tsv').open(),delimiter='\t'))
refs={(r['model'],r['mention']):r for r in csv.DictReader(Path(S['references']).open(),delimiter='\t') if r['identity']=='REUSE' and r['model'] in S['reference_models']}
chains=list(csv.DictReader((D/'CHAINS.tsv').open(),delimiter='\t'))
checks=0
for ref in S['reference_models']:
 for mode in S['models']:
  world=ref+'_'+mode
  rows=[r for r in als if r['world']==world]
  assert [(r['record'],r['at'],r['word']) for r in rows]==raw
  events={e['at']:e for e in es if e['world']==world}
  assert len(events)==27
  for rid in S['records']:
   rr=[r for r in rows if r['record']==rid];past=[];problems=[]
   state=dict(actor=rid+':A0',recipient='MISSING',owners={},origins={})
   for r in rr:
    before=json.loads(r['before']);after=json.loads(r['after']);assert before==state
    want=json.loads(json.dumps(before));w=r['word'];e=events.get(r['at'])
    if w=='qokaiin':want['recipient']=rid+':B'
    if w=='qoky' and mode=='H1':want['actor']=before['recipient']
    if w in ['chedy','qokeedy']:
     materials=[x for x in past if x['word'] in ['shedy','lchedy']]
     m=(materials[-1] if ref=='L1' else materials[0]) if materials else None
     dests=[x for x in past if x['word']=='qokaiin']
     p=rid+':'+{'shedy':'A','lchedy':'C'}[m['word']] if m else 'MISSING'
     dst=rid+':B' if dests else 'MISSING'
     old=refs[(ref,r['at'])];assert (p,dst)==(old['patient'],old['destination'])==(e['patient'],e['destination'])
     assert old['patient_trigger']==(m['at'] if m else 'MISSING')
     owner=before['owners'].get(p,'UNKNOWN');actor=before['actor'];issues=[]
     if p=='MISSING':issues.append('MISSING_PATIENT')
     if w=='qokeedy' and dst=='MISSING':issues.append('MISSING_DESTINATION')
     if mode!='V':
      if actor=='MISSING':issues.append('MISSING_ACTOR')
      if w=='qokeedy' and actor!='MISSING' and dst!='MISSING' and actor==dst:issues.append('SELF_TRANSFER')
      if p!='MISSING' and actor!='MISSING' and owner!='UNKNOWN' and owner!=actor:issues.append('ACCESS_CONFLICT')
      if not issues:
       if owner=='UNKNOWN':want['owners'][p]=actor;want['origins'][p]=r['at']
       if w=='qokeedy':want['owners'][p]=dst;want['origins'][p]=r['at']
      status=('CONFLICT' if set(issues)&{'SELF_TRANSFER','ACCESS_CONFLICT'} else 'UNBOUND') if issues else ('INITIAL_REQUIREMENT' if owner=='UNKNOWN' else 'ACCESS_MATCH')
     else:status='UNBOUND' if issues else 'BOUND_NO_CUSTODY_TEST'
     assert e['status']==status
     assert e['owner_before']==owner and e['owner_after']==want['owners'].get(p,'UNKNOWN')
    elif w=='qoky':
     issues=['MISSING_RECIPIENT'] if mode=='H1' and before['recipient']=='MISSING' else []
     status='OPEN' if mode!='H1' else ('UNBOUND' if issues else ('ROLE_REPEATED' if before['actor']==before['recipient'] else 'ACTOR_CHANGED'))
     assert e['status']==status
    else:assert e is None
    assert after==want,(world,r['at'])
    if e:
     assert e['issues']==(','.join(issues) or 'NONE')
     assert json.loads(e['before'])==before and json.loads(e['after'])==after
     assert (e['actor_before'],e['actor_after'])==(before['actor'],after['actor'])
     assert e['prior_problem']==(','.join(problems) or 'NONE')
     if issues:problems.append(r['at'])
     checks+=1
    state=after;past.append(r)
# Enumerate all marker witnesses between successful custody transfer and heat.
expected=[]
for world in {r['world'] for r in es}:
 ev=[r for r in es if r['world']==world]
 for j,h in enumerate(ev):
  if h['kind']!='HEAT' or h['status']!='ACCESS_MATCH':continue
  before=json.loads(h['before']);origin=before['origins'].get(h['patient'])
  prior=[r for r in ev[:j] if r['at']==origin and r['record']==h['record'] and r['kind']=='TRANSFER' and r['issues']=='NONE']
  if not prior:continue
  tr=prior[0];i=ev.index(tr)
  for marker in ev[i+1:j]:
   if marker['record']==h['record'] and marker['kind']=='MARKER' and marker['status'] in ['ACTOR_CHANGED','ROLE_REPEATED'] and marker['actor_after']==h['actor_before']:
    expected.append((world,tr['at'],marker['at'],h['at'],h['patient']))
actual=[(c['world'],c['transfer'],c['marker'],c['later_action'],c['patient']) for c in chains]
assert sorted(actual)==sorted(expected)
text=(D/'READING.md').read_text()
for row in csv.DictReader(Path(S['source']).open(),delimiter='\t'):assert row['locus']+': `'+row['zl3b_line']+'`' in text
result=dict(status='PASS',source_hashes=len(S['hashes']),groups=341,full_alignment_rows=len(als),event_checks=checks,original_action_bindings=40,marker_witnesses=len(chains),distinct_transfer_action_pairs=len({(c['world'],c['transfer'],c['later_action']) for c in chains}),independent_meaning_validation=False)
(D/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
