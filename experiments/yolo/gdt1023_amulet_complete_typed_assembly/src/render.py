"""Post-result disclosure, not part of the locked scientific execution."""
from common import *
import csv
def table(name, rows):
    with (A/name).open('w', newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)
check_lock()
assert read(A/'VALIDATION.json')['status']=='PASS'
s=source(); rows=read(A/'ROWS.json')
pred=list(csv.DictReader((A/'PREDICTIONS.tsv').open(),delimiter='\t'))
out=[];traces=[];positions=[]
for r in rows:
    p=next(p for p in pred if p['branch']==r['branch'] and p['mode']==r['mode'])
    assert p['predicted_status']==r['status']
    e=r['execution'];st=e['final_state']
    out.append(dict(branch=r['branch'],model=r['mode'],predicted=p['predicted_status'],observed=r['status'],physical_status=e['physical_status'],attempted_steps=len(e['trace']),successful_steps=sum(not t['errors'] for t in e['trace']),unexecuted_tail=len(e['unexecuted_plan']),depiction=st['depicted_kind'],part_kind=r['graph']['part_kind'],enclosed=st['enclosed'],worn_by=st['worn_by'],attributed_claims=len(st['claims']),contradictions=';'.join(e['first_failure']),content_mismatches=';'.join(e['content_mismatches']),independent_meaning_capacity=0))
    for t in e['trace']:
        traces.append(dict(branch=r['branch'],model=r['mode'],step=t['index'],operation=json.dumps(t['operation']),before=json.dumps(t['before'],sort_keys=True),after=json.dumps(t['after'],sort_keys=True),errors=json.dumps(t['errors'])))
for c in s['complete_clauses']:
    for i,w in enumerate(c['raw'].split(),1):
        v=s['lexicon'][w]
        positions.append(dict(position=len(positions)+1,locus=c['locus'],group=i,raw_projection=w,clause=c['id'],production=c['production'],tag=v['tag'],hypothetical_meaning=v['meaning'],origin=v['status'],confirmed=False))
table('CANDIDATES.tsv',out);table('ALL_POSITIONS.tsv',positions);table('TRACE_STEPS.tsv',traces)
result=read(A/'RESULT.json');result.update(status='SUPPORTED_LIMITED_COMPLETE_PROJECTED_AMULET_ACCOUNT',validation='PASS',raw_forms_unbound=3,all_predictions_matched=True,significance=False)
write(A/'RESULT.json',result)
print(json.dumps(result,indent=2))
