"""Post-result tables; does not alter the registered model."""
from common import *
import csv
def table(name,rows):
    with (A/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
check_lock();assert read(A/'VALIDATION.json')['status']=='PASS'
s=source();p=read(R/s['frozen_parent']['path']);lex={**p['lexicon'],**s['new_18_lexical_entries']};positions=[];out=[]
for block,clauses in [('NEW33',s['complete_new_block_clauses']),('OLD62',p['whole_paragraph_clauses'])]:
    for c in clauses:
        for i,w in enumerate(c['raw'].split(),1):
            positions.append(dict(position=len(positions)+1,block=block,locus=c['locus'],group=i,word=w,clause=c['id'],tag=lex[w]['tag'],hypothetical_meaning=lex[w]['meaning'],frozen_old_entry=w in p['lexicon'],confirmed=False))
for row in read(A/'ROWS.json'):
    out.append(dict(n=row['n'],branch=row['branch'],model=row['mode'],observed=row['status'],errors=json.dumps(row['errors']),full_bound_original_intervals=row['complete_trace_events'],new_semantic_observations=0,independent_meaning_capacity=0))
table('ALL_POSITIONS.tsv',positions);table('CANDIDATES.tsv',out)
reuse=[]
for w,receipt in s['shared_word_receipt'].items():
    reuse.append(dict(word=w,meaning=p['lexicon'][w]['meaning'],old_locations=json.dumps([x['locus']+':'+str(x['group']) for x in positions if x['block']=='OLD62' and x['word']==w]),new_locations=json.dumps([x['locus']+':'+str(x['group']) for x in positions if x['block']=='NEW33' and x['word']==w]),meaning_unchanged=True,confirmed=False))
table('REUSED_WORDS.tsv',reuse)
r=read(A/'RESULT.json');r.update(status='SUPPORTED_LIMITED_TWO_PROJECTED_PARAGRAPHS_FIXED53',validation='PASS',raw_ZL_unbound=4,complete_IT_reading=False,all_60_predictions_matched=True,significance=False)
write(A/'RESULT.json',r)
print(json.dumps(r,indent=2))
