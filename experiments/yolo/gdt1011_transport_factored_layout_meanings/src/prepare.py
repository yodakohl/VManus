from common import *
import collections,math
s,g=inputs();original=read(R/s['source_previous_panel'])[0];source=read(R/s['source_functional']);unique={}
for attempt in source['attempts']:
    layout=[{k:c[k] for k in ['start','end','kind']} for c in attempt['parse']]
    key=json.dumps(layout,sort_keys=True)
    if key not in unique:unique[key]=layout
layouts=[]
for i,(key,layout) in enumerate(sorted(unique.items())):
    domains={w:None for w in original['words']}
    for clause in layout:
        for word,t in zip(original['words'][clause['start']:clause['end']],g['patterns'][clause['kind']]):
            allowed=set(g['types'][t[1:]]) if t.startswith('@') else {t}
            domains[word]=allowed if domains[word] is None else domains[word]&allowed
    assert all(domains.values())
    domains={w:sorted(v) for w,v in sorted(domains.items())};count=math.prod(len(v) for v in domains.values())
    layouts.append(dict(id='L'+str(i).zfill(2),layout=layout,domains=domains,cartesian_maps=count))
assert len(layouts)==8 and all(x['cartesian_maps']==225 for x in layouts)
oldpanel=read(R/s['source_long_panel']);oldrows=read(R/s['source_long_rows']);v=read(R/s['source_long_validation'])
assert v['status']=='PASS'
keep=[x['paragraph_ids'][1] for x in oldrows if x['status']=='SAT'];assert len(keep)==4
panel=[original]+[p for p in oldpanel[1:] if p['id'] in keep]
for p in panel:assert not p['page'].startswith('f84') and p['page']!='f116v'
put('LAYOUTS.json',layouts);put('PANEL.json',panel)
put('PREDICTIONS.json',dict(layouts=8,maps_if_coverage_passes=1800,settings_per_map=32,extension_contexts=keep,extension_rule='EVERY_VALID_ORIGINAL_CODE_X_EVERY_CONTEXT',word_values='ALL47FREE_FUNCTIONAL; BIJECTIVE is subset',independent_meaning_capacity=0))
print(json.dumps(dict(layouts=8,map_bound=1800,long_contexts=len(panel)-1)))
