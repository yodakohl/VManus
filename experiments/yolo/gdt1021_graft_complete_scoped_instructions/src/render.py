"""Post-result tables only; locked interpretation code is unchanged."""
from common import *
import ast
import csv

def table(name,rows):
    with (A/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

spec,source=inputs();results=read(A/'ROWS.json')
predictions=list(csv.DictReader((A/'PREDICTIONS.tsv').open(),delimiter='\t'))
scenarios=[];positions=[];candidates=[]
for r in results:
    for row in r['scenarios']:
        p=next(p for p in predictions if p['candidate']==r['candidate'] and p['season']==row['season']
               and p['method']==row['method'] and ast.literal_eval(p['refuses'])==row['refuses'])
        assert ast.literal_eval(p['predicted_license'])==row['instruction_licensed']
        assert ast.literal_eval(p['predicted_product_options'])==row['graft_product_options']
        assert ast.literal_eval(p['predicted_stock_product_options'])==row['stock_own_product_options']
        assert p['material']==row['material'] and p['origin']==row['origin']
        scenarios.append(dict(candidate=r['candidate'],**row,prediction_matches=True))
    for x in source['all_group_alignment']:
        clause=next(c['kind'] for c in r['graph']['clauses'] if c['start']<=x['index']-1<c['end'])
        positions.append(dict(candidate=r['candidate'],**x,lexical_type=spec['lexicon'][x['raw']],clause=clause,confirmed=False))
    candidates.append(dict(candidate=r['candidate'],prediction='Complete 23-group instruction account',
        observed=r['status'],groups=23,clauses=4,methods=3,scenario_rows=12,contradictions=0,
        unresolved='23 guessed singleton values; alternative scope; uncertain ZL; IT unbound',
        allowed_valuations=len(r['valuations']),independent_meaning_capacity=0))
table('SCENARIOS.tsv',scenarios);table('ALL_POSITIONS.tsv',positions);table('CANDIDATES.tsv',candidates)
print('All 24 frozen prediction rows matched; full 46 candidate-position rows disclosed.')
