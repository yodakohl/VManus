from common import *
s,g=inputs();source=read(R/s['source_candidates']);v=read(R/s['source_validation'])
assert source['exhaustive_projection'] and next(x for x in v['families'] if x['family']=='BIJECTIVE')['final_blocked_cvc5']=='unsat'
candidates=[]
for t in source['positive_tuples']:
    attempt=source['attempts'][t['attempt']];variant=attempt['replays'][t['variant_index']]['variant']
    assert variant['exclude']=='EXCLUDING' and variant['first']=='FIRST' and variant['copy']=='FIRST'
    candidates.append(dict(id='B'+str(t['tuple']).zfill(2),original_tuple=t['tuple'],original_attempt=t['attempt'],values=t['values'],variant_index=t['variant_index'],variant=variant,chedy_class='REFERENCE' if t['values']['chedy']=='FIRST_CARGO' else 'NAME'))
assert len(candidates)==36 and len(base_roles(candidates))==8
put('CANDIDATE_PREDICTIONS.json',candidates)
panel=[];census=[]
for edition,paragraphs in read(R/s['source_paragraphs']).items():
    for p in paragraphs:
        assert not p['page'].startswith('f84') and p['page']!='f116v'
        words=[w for line in p['lines'] for w in line['words']];ids=[i for line in p['lines'] for i in line['source_ids']]
        assert len(words)==len(ids)==p['groups']
        status='ORIGINAL_LEAF' if p['leaf']==83 else 'NO_EXACT_CHEDY' if 'chedy' not in words else 'BELOW_SCOPE' if len(words)<26 else 'ABOVE_SCOPE' if len(words)>37 else 'QUERY'
        row=dict(id=edition+'|'+p['id'],edition=edition,paragraph=p['id'],page=p['page'],leaf=p['leaf'],groups=len(words),chedy_occurrences=words.count('chedy'),scope_status=status,strict_anchor_eligible=all(l['anchor_eligible'] for l in p['lines']),independent_meaning_capacity=0)
        census.append(row)
        if status=='QUERY':panel.append(dict(**row,words=words,source_ids=ids))
assert len(census)==1349
put('CENSUS.json',census);put('PANEL.json',panel)
put('PREDICTIONS.json',dict(scope_rows=1349,query_paragraphs=len(panel),candidate_queries=len(panel)*36,baseline_queries=len(panel),required_first=g['patterns']['INITIAL'],required_last=g['patterns']['CONCLUSION'],required_once=['INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'],fixed_roles_per_candidate=11,nonprojected_original_roles='UNBOUND_NECESSARY_SCREEN',all_candidate_ids=[c['id'] for c in candidates],all_paragraph_ids=[p['id'] for p in panel],source_contract='CONDITIONAL_WHEN_NOT_STRICT',reserved_confirmation=False))
print(json.dumps(dict(census_rows=len(census),eligible_complete_contexts=len(panel),queries=len(panel)*37)))
