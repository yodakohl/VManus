"""Presentation after the locked execution; no scientific changes."""
from common import *
import csv
def table(name,rows):
    with (A/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
check_lock();assert read(A/'VALIDATION.json')['status']=='PASS'
s=source();sp=spec();oldsp=read(OLD/'src/SPEC.json');positions=[]
for block,lines in [('NEW63',s['new_complete_clauses']),('OLD33',s['target']['old_complete_projection'])]:
    for l in lines:
        for i,w in enumerate(l['raw'].split(),l.get('groups',[1])[0]):
            meaning=s['frozen_parent']['all_24_meanings_exact'][w] if w in oldsp['lexicon'] else s['new_40_lexicon'][w]['meaning']
            positions.append(dict(position=len(positions)+1,block=block,locus=l['locus'],group=i,word=w,type=sp['lexicon'][w][0],value=sp['lexicon'][w][1],hypothetical_meaning=meaning,frozen_old=w in oldsp['lexicon'],confirmed=False))
rows=[];bindings=[]
for r in read(A/'ROWS.json'):
    for i,x in enumerate(r['readings'],1):
        j=x['joint'];rows.append(dict(pairing=r['pairing'],mode=r['mode'],parse=i,status=j['status'],new_weave_phase=j['new_habit_phase'],old_weave_phase=j['old_habit_phase'],habitual_frames=j['habitual_action_frames'],bounded_frames=j['bounded_action_frames'],errors=json.dumps(j['errors']),independent_meaning_capacity=0))
        bindings.extend(dict(pairing=r['pairing'],mode=r['mode'],parse=i,**b) for b in j['checks'])
assert [(r['locus'],r['group'],r['word']) for r in positions if r['block']=='NEW63']==[(l['locus'],i,w) for l in s['target']['new_complete_record']['lines'] for i,w in enumerate(l['words'],1)]
table('ALL_POSITIONS.tsv',positions);table('CANDIDATES.tsv',rows);table('ALL_BINDINGS.tsv',bindings)
reuse=[]
for w in sorted(set(x['word'] for x in positions if x['block']=='NEW63' and x['frozen_old'])):
    reuse.append(dict(word=w,meaning=s['frozen_parent']['all_24_meanings_exact'][w],new_positions=json.dumps([x['position'] for x in positions if x['block']=='NEW63' and x['word']==w]),old_positions=json.dumps([x['position'] for x in positions if x['block']=='OLD33' and x['word']==w]),confirmed=False))
table('REUSED_WORDS.tsv',reuse)
r=read(A/'RESULT.json');r.update(status='SUPPORTED_LIMITED_SHARED_DIRECT_REVERSED_CONTRADICTED',validation='PASS',separation_depends_on_shared_V_and_sole_phase=True,standalone_GDT1020_both_preserved=True,significance=False)
write(A/'RESULT.json',r)
print(json.dumps(r,indent=2))
