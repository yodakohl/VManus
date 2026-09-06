"""Bounded, reviewed conditional priorities; no automatic research permission."""
import hashlib
import json
from tools import research_registry as registry

DATA='research_registry/semantic_priority_decisions.jsonl'

def latest(rows):
    result={};seen=set()
    for row in rows:
        key=row['decision_key'];expected=result[key]['id'] if key in result else None
        if row['id'] in seen or row.get('previous_revision')!=expected:
            raise ValueError('broken priority/dossier revision chain')
        seen.add(row['id']);result[key]=row
    return result

def get_page(root,query='',limit=8,offset=0,semantic_id=None):
    from tools import semantic_ideas as ideas,semantic_identity as identity
    if not 1<=limit<=20 or offset<0:raise ValueError('limit1..20 and offset>=0 required')
    rows=sorted(latest(registry.read_jsonl(root/DATA)).values(),key=lambda x:(x['rank'],x['id']))
    if semantic_id:rows=[r for r in rows if semantic_id in r['sem_ids']]
    if query.strip():rows=[r for r in rows if all(t.casefold() in registry.canonical(r).casefold() for t in query.split())]
    selected=rows[offset:offset+limit];dossiers=latest(registry.read_jsonl(root/ideas.FAILURES));con=ideas.connect(root)
    try:
        for row in selected:
            if row.get('scientific_test_ready') is not False:raise ValueError('this conditional shortlist cannot approve execution')
            if set(row['card_basis'])!=set(row['sem_ids']) or set(row['effective_basis'])!=set(row['sem_ids']):raise ValueError('incomplete priority binding')
            if set(row['dossier_keys'])!=set(row['dossier_basis']):raise ValueError('incomplete priority dossier binding')
            for key,sha in row['dossier_basis'].items():
                if key not in dossiers or hashlib.sha256(registry.canonical(dossiers[key]).encode()).hexdigest()!=sha:raise ValueError('stale priority dossier')
                dossier=dossiers[key]
                identity._evidence(root,dossier.get('evidence'))
                if set(dossier['targets'])!=set(dossier['card_basis']) or set(dossier['targets'])!=set(dossier['effective_basis']):raise ValueError('incomplete bound dossier targets')
                for target in dossier['targets']:
                    hit=con.execute('SELECT payload FROM ideas WHERE id=?',(target,)).fetchone()
                    if not hit:raise ValueError('priority dossier target no longer active')
                    card=json.loads(hit[0])
                    if ideas.card_basis(card)!=dossier['card_basis'][target] or identity.effective_basis(card)!=dossier['effective_basis'][target]:raise ValueError('stale priority dossier target')
            for target in row['sem_ids']:
                hit=con.execute('SELECT payload FROM ideas WHERE id=?',(target,)).fetchone()
                if not hit:raise ValueError('priority card no longer active')
                card=json.loads(hit[0])
                if ideas.card_basis(card)!=row['card_basis'][target] or identity.effective_basis(card)!=row['effective_basis'][target]:raise ValueError('stale priority proposition')
            identity._evidence(root,row.get('evidence'))
        compact=[registry.bounded_view({k:r[k] for k in ('id','rank','question','readiness','scientific_test_ready','sem_ids','next_work_object','outcome_decisions','smallest_adequate_check','blockers','changed_inputs','budget_minutes','scope')}) for r in selected]
        return {'results':compact,'matched':len(rows),'next_offset':offset+len(selected) if offset+len(selected)<len(rows) else None,'scope':'Conditional question priorities in the explicitly reviewed subset. Ranking is neither support for a meaning nor evidence that a new qualifying observation exists.'}
    finally:con.close()
