"""Independent reverse-scan scope reconstruction and complete candidate audit."""
import csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;B=W/'W28';ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def read(p):return json.loads(p.read_text())
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for x in S['inputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
source=read(B/'SOURCE.json')['paragraphs'];assert len(source)==17 and sum(len(l['words']) for p in source for l in p['lines'])==1045
expected={};by_model={};old_by_model={}
for sm in ['Q','A']:
 ff=rows(B/(sm+'_SOURCE_FLAT.tsv'));by_model[sm]={r['id']:r for r in ff};events=rows(B/(sm+'_EVENTS.tsv'));old_by_model[sm]=events
 acts={r['location'] for r in events if r['kind']=='ACTION' and r['form']!='chey'};quals={r['location'] for r in events if r['kind']=='QUALITY'}
 for p in source:
  ts=[r for r in ff if r['paragraph']==p['id']]
  for contract in ['P16_LITERAL','TRANSFER']:
   nextidx=None;barrier='PARAGRAPH_END';end=len(ts)
   for i in range(len(ts)-1,-1,-1):
    x=ts[i]
    if x['form']=='chey':
     target=ts[nextidx] if nextidx is not None else None;gap=ts[i+1:nextidx if nextidx is not None else end]
     expected[sm,x['id'],contract]=dict(target=target['id'] if target else '',target_form=target['form'] if target else '',target_kind=('ACTION' if target['id'] in acts else 'QUALITY' if target['id'] in quals else 'NOT_CURRENT_PREDICATE') if target else '',stop='TARGET' if target else barrier,interval=';'.join(y['id']+'='+y['form'] for y in gap),open_interval=';'.join(y['id']+'='+y['form'] for y in gap if y['role']=='OPEN'))
    if x['form'] in S['scope_barriers']:nextidx=None;barrier=x['id'];end=i
    elif (x['form'] in S['literal_P16_predicates'] if contract=='P16_LITERAL' else x['id'] in acts|quals):nextidx=i
actual=rows(E/'SCOPES.tsv');assert len(actual)==len(expected)==32
for r in actual:
 ex=expected[r['shol'],r['chey'],r['contract']];assert all(r[k]==v for k,v in ex.items())
 assert r['parity']==(str(sum(v['target']==ex['target'] for (sm,loc,c),v in expected.items() if sm==r['shol'] and c==r['contract'])%2) if ex['target'] else '')
assert all(not r['target'] for r in actual if r['contract']=='P16_LITERAL')
c=rows(E/'CANDIDATES.tsv');assert len(c)==192
keys=set()
for r in c:
 key=tuple(r[k] for k in ['shol','chey','grammar','model','timing']);assert key not in keys;keys.add(key)
 events=[a for a in old_by_model[r['shol']] if (a['paragraph'],a['grammar'],a['model'],a['timing'])==tuple(r[k] for k in ['paragraph','grammar','model','timing'])]
 check=next(a for a in events if a['location']==r['chey'] and a['kind']=='ACTION');t=expected[r['shol'],r['chey'],'TRANSFER'];target=next(a for a in events if a['location']==t['target'] and a['kind'] in ['ACTION','QUALITY'])
 assert r['C_patient']==check['patient'] and r['N_patient']==target['patient'] and r['N_target']==t['target'] and r['N_kind']==target['kind'] and r['debts']==target['debts'] and r['baseline_before']==target['before'] and r['baseline_target_status']==target['status']
 assert r['physical_result']=='NOT_REPLAYED_STATE_TARGET_CAPACITY'
full=rows(E/'CONTEXT_ALIGNMENT.tsv');old=rows(B/'A_ALIGNMENT.tsv');pars={r['paragraph'] for r in actual};expected_full=[r for r in old if r['paragraph'] in pars];assert len(full)==len(expected_full)==606
text=(E/'READINGS.md').read_text()
for r,b in zip(full,expected_full):assert all(r[k]==v for k,v in b.items())
for loc in dict.fromkeys(r['locus'] for r in full):assert text.count('`'+' '.join(r['raw'] for r in full if r['locus']==loc)+'`')==1
res=read(E/'RESULT.json');assert res['replayed_worlds']==0 and res['constraint_discriminators'] is None and res['new_conflicts'] is None
for sm in ['Q','A']:
 ss=[r for r in actual if r['shol']==sm and r['contract']=='TRANSFER'];assert len(ss)==8 and sum(r['target_kind']=='QUALITY' for r in ss)==1
out=dict(status='PASS',bound_files=len(S['inputs']),scope_rows=32,candidate_rows=len(c),complete_context_groups=len(full),whole_source_groups=1045,physical_model_execution='NOT_PERFORMED',limits='Verifies scope and conditional wording/bindings, not a negative-state simulation or word meanings')
(E/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
