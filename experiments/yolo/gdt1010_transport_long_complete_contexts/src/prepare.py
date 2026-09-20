from common import *
s,g=inputs();original=read(R/s['source_previous_panel'])[0];census=read(R/s['source_census'])
required=[x['id'] for x in census if x['scope_status']=='ABOVE_SCOPE'];panel=[original]
for ed,paragraphs in read(R/s['source_paragraphs']).items():
    for p in paragraphs:
        assert not p['page'].startswith('f84') and p['page']!='f116v'
        pid=ed+'|'+p['id']
        if pid not in required:continue
        words=[w for line in p['lines'] for w in line['words']]
        assert p['leaf']!=83 and 'chedy' in words and len(words)>37
        panel.append(dict(id=pid,edition=ed,page=p['page'],leaf=p['leaf'],words=words,source_ids=[v for line in p['lines'] for v in line['source_ids']],groups=len(words),strict_anchor_eligible=all(line['anchor_eligible'] for line in p['lines'])))
assert [p['id'] for p in panel[1:]]==required and len(required)==282
jobs=[]
for i,p in enumerate(panel[1:],1):
    jobs.append(dict(id='LONG_'+str(i).zfill(3),family='FUNCTIONAL',system=[0,i],paragraph_ids=[original['id'],p['id']],all_shared_words=sorted(set(original['words'])&set(p['words'])),prediction='FULL_ORIGINAL_PLUS_COMPLETE_LONG_CONTEXT_ONE_FREE_GLOBAL_DICTIONARY',independent_meaning_capacity=0))
put('PANEL.json',panel);put('PREDICTIONS.json',jobs)
put('KNOWN_COUNTERCASE.json',dict(source='GDT1008',word='chedain',forced='CARGOS in initial second slot of f107r',conflict='Original noninitial occurrence cannot have CARGOS; this already excluded short case is not in long panel.'))
print(json.dumps(dict(original_groups=63,long_contexts=282,other_leaves=len({p['leaf'] for p in panel[1:]}),maximum_groups=max(p['groups'] for p in panel))))
