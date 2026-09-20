from common import *
s,g=inputs();original=next(x for x in read(R/s['source_original']) if x['edition']=='ZL3b')
assert original['whole_paragraph_contract'] and len(original['words'])==63
panel=[dict(id='ZL3b|f83r|f83r.18-f83r.24',edition='ZL3b',page='f83r',leaf=83,words=original['words'],source_ids=original['source_ids'],groups=63,strict_anchor_eligible=original['strict_anchor_eligible'])]
source=read(R/s['source_contexts']);outcomes=read(R/s['source_context_results'])
keep=[r['paragraph'] for r in outcomes if any(q['candidate']!='UNPINNED' and q['status']=='sat' for q in r['rows'])]
assert keep==['ZL3b|f107r|f107r.4-f107r.7','IT2a|f108r|f108r.8-f108r.10']
for pid in keep:
    p=next(x for x in source if x['id']==pid);assert not p['page'].startswith('f84') and p['page']!='f116v'
    panel.append({k:p[k] for k in ['id','edition','page','leaf','words','source_ids','groups','strict_anchor_eligible']})
jobs=[]
for family in s['families']:
    for system in s['systems']:
        shared=sorted({w for i in system for w in panel[i]['words'] if sum(w in panel[j]['words'] for j in system)>1})
        jobs.append(dict(id=family+'_'+'-'.join(map(str,system)),family=family,system=system,paragraph_ids=[panel[i]['id'] for i in system],all_shared_words=shared,prediction='ONE_GLOBAL_UNFIXED_VALUE_PER_WHOLE_FORM_WITH_COMPLETE_SOURCE_COUNTS',independent_meaning_capacity=0))
occurrences=[(k,i) for k,p in g['patterns'].items() for i,t in enumerate(p) if 'CARGOS' in (g['types'][t[1:]] if t.startswith('@') else [t])]
assert occurrences==[('INITIAL',1)] and panel[1]['words'][1]=='chedain' and panel[0]['words'][1]!='chedain' and 'chedain' in panel[0]['words']
counter=dict(status='FIXED_ENDPOINT_COUNTERCASE',terminal='CARGOS',only_grammar_slot=['INITIAL',2],forced_context=panel[1]['id'],forced_form='chedain',original_positions=[i+1 for i,w in enumerate(panel[0]['words']) if w=='chedain'],consequence='No common grammar dictionary between original and f107r under either family, independent of meaning variant.')
put('PANEL.json',panel);put('PREDICTIONS.json',jobs);put('KNOWN_COUNTERCASE.json',counter)
print(json.dumps(dict(paragraphs=len(panel),system_family_cases=len(jobs),countercase=counter)))
