from common import *
s,g=inputs();original=read(R/s['source_previous_panel'])[0]
contexts=read(R/s['source_contexts']);assert len(contexts)==120
assert original['leaf']==83 and original['groups']==63
prior=read(R/s['source_previous_rows']);validation=read(R/s['source_previous_validation'])
assert validation['status']=='PASS'
inherited=[]
for row in prior:
    if row['family']=='FUNCTIONAL' and len(row['system'])==2:
        check=next(x for x in validation['checks'] if x['id']==row['id'])
        assert row['status']=='UNSAT' and check['independent']=='unsat'
        inherited.append(dict(paragraph=row['paragraph_ids'][1],status='UNSAT',certificate='GDT1008',row=row['id'],independent='unsat'))
assert len(inherited)==2
panel=[original]+[{k:p[k] for k in original} for p in contexts]
assert len({p['id'] for p in panel})==121
jobs=[]
for i,p in enumerate(panel[1:],1):
    assert p['leaf']!=83 and not p['page'].startswith('f84') and p['page']!='f116v'
    assert 26<=p['groups']<=37 and 'chedy' in p['words']
    if p['id'] in {x['paragraph'] for x in inherited}:continue
    shared=sorted(set(original['words'])&set(p['words']))
    jobs.append(dict(id='FUNCTIONAL_'+str(i).zfill(3),family='FUNCTIONAL',system=[0,i],paragraph_ids=[original['id'],p['id']],all_shared_words=shared,prediction='ONE_GLOBAL_UNFIXED_VALUE_PER_WHOLE_FORM_WITH_COMPLETE_SOURCE_COUNTS',independent_meaning_capacity=0))
assert len(jobs)==118
put('PANEL.json',panel);put('PREDICTIONS.json',jobs);put('INHERITED.json',inherited)
put('KNOWN_COUNTERCASE.json',dict(status='INHERITED_ALREADY_EXCLUDED_NOT_RETRIED',source='GDT1008',terminal='CARGOS',only_slot=['INITIAL',2],word='chedain',scope='Original plus ZL3b f107r.4-7; both whole-dictionary families.'))
print(json.dumps(dict(paragraphs=len(panel),new_systems=len(jobs),inherited=len(inherited))))
