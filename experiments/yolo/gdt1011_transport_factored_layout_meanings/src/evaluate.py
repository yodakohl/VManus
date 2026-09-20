from common import *
import itertools,collections

def maps():
    original=read(A/'PANEL.json')[0]
    for layout in read(A/'LAYOUTS.json'):
        names=list(layout['domains']);domains=[layout['domains'][w] for w in names]
        for i,values in enumerate(itertools.product(*domains)):
            code=dict(zip(names,values));parsed=[dict(c,symbols=[code[w] for w in original['words'][c['start']:c['end']]]) for c in layout['layout']]
            yield dict(id=layout['id']+'_'+str(i).zfill(3),layout=layout['id'],code=code,parse=parsed,bijective=len(set(code.values()))==len(code))

def compact(raw):
    if raw['status']=='BINDING_CONTRADICTION':return dict(status=raw['status'],error=raw['error'],source_valid=False)
    good=[p for p in raw['paths'] if p['consistent'] and len(p['trace'])==8]
    valid=len(raw['cargo'])==3 and len(raw['hazards'])==2 and bool(good)
    return dict(status='SOURCE_VALID' if valid else raw['status'],source_valid=valid,cargo=raw['cargo'],hazards=raw['hazards'],consistent_path_lengths=sorted(len(p['trace'])-1 for p in raw['paths'] if p['consistent']),physical_failure_paths=sum(not p['physical_complete'] for p in raw['paths']),assertion_failure_paths=sum(bool(p['assertions']) for p in raw['paths']),safety_failure_paths=sum(bool(p['safety_violations']) for p in raw['paths']),references=raw['references'])

def evaluate(candidate,independent=False):
    s,g=inputs();variants=[];full=[]
    for i,values in enumerate(itertools.product(*g['variants'].values())):
        variant=dict(zip(g['variants'],values));raw=replay(candidate['parse'],variant,s,independent)
        variants.append(dict(variant_index=i,variant=variant,**compact(raw)));full.append(raw)
    valid=[x['variant_index'] for x in variants if x['source_valid']]
    return dict(**candidate,variants=variants,valid_variants=valid,full_replays=full if valid else [])
