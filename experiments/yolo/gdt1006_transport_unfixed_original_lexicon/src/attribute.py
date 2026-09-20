"""Deterministic domain attribution under the documented coverage theorem."""
from common import *
import csv
checklock();s=read(E/'src/SPEC.json');pred=read(A/'PREDICTIONS.json');validation=read(A/'VALIDATION.json');rows=[];counts=[]
for family in s['families']:
    r=read(A/('FAMILY_'+family+'.json'));v=next(x for x in validation['families'] if x['family']==family)
    complete=r['exhaustive_projection'] and v['final_blocked_cvc5']=='unsat'
    keys={tuple(a['code'][w] for w in pred['projection_words']) for a in r['attempts']}
    counts.append(dict(family=family,syntax_word_tuples_seen=len(keys),syntax_role_variant_tuples=len(keys)*32,world_role_variant_tuples=len(r['positive_tuples']),complete=complete))
    for word in pred['projection_words']:
        syntax=sorted({a['code'][word] for a in r['attempts']});world=sorted({p['values'][word] for p in r['positive_tuples']})
        assert set(world)<=set(syntax)
        rows.append(dict(family=family,word=word,syntax_values=syntax,world_values=world,world_exclusions=sorted(set(syntax)-set(world)) if complete else None,syntax_singleton=len(syntax)==1 if complete else None,world_singleton=len(world)==1 if complete else None,complete=complete,independent_meaning_capacity=0))
put('ATTRIBUTION.json',dict(coverage=counts,domains=rows,scope='Conditional source-template domain attribution, no word meaning confirmation.'))
with (A/'SYNTAX_VS_WORLD.tsv').open('w',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['family','word','syntax_values','world_values','world_exclusions','complete','independent_meaning_capacity'])
    for r in rows:w.writerow([r['family'],r['word'],','.join(r['syntax_values']),','.join(r['world_values']),','.join(r['world_exclusions']) if r['world_exclusions'] is not None else 'UNKNOWN',r['complete'],0])
print(json.dumps(counts,indent=2))
