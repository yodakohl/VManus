from common import *
import itertools

def jobs():
    s=inputs();g=read(R/s['grammar']);variants=[dict(zip(g['variants'],v)) for v in itertools.product(*g['variants'].values())]
    originals=read(R/s['source_candidates']);byid={o['id']:o for o in originals}
    cases=read(R/s['source_cases']);p=read(R/s['source_saved_primary']);q=read(R/s['source_saved_independent'])
    out=[]
    for o in originals:
        for vi in o['valid_variants']:
            out.append(dict(id=o['id']+'_V'+str(vi),scope='original',original_id=o['id'],variant_index=vi,variant=variants[vi],parse=o['parse'],aliases=o['code']))
    assert len(out)==156
    witnesses=[]
    for case,one,two in zip(cases,p,q,strict=True):
        assert case['id']==one['id']==two['id']
        for engine,row in [('primary',one),('independent',two['independent'])]:
            if row['status']!='sat':continue
            w=row['witness'];wid=case['id']+'_'+engine
            witnesses.append(dict(id=wid,scope='saved',case=case['id'],context=case['context'],engine=engine,variant=case['variant'],parse=w['parse'],aliases=w['aliases']))
            for member in case['members']:
                for mi,rename in enumerate(member['original_to_canonical']):
                    inv={v:k for k,v in rename.items()}
                    parse=[dict(c,symbols=[inv.get(x,x) for x in c['symbols']]) for c in w['parse']]
                    alias={k:inv.get(v,v) for k,v in w['aliases'].items()}
                    o=byid[member['original_id']]
                    assert all(o['code'][k]==v for k,v in alias.items() if k in o['code'])
                    out.append(dict(id=wid+'_'+o['id']+'_M'+str(mi),scope='lift',witness=wid,original_id=o['id'],case=case['id'],context=case['context'],inverse_map=inv,variant_index=case['variant_index'],variant=case['variant'],parse=parse,aliases=alias))
    assert len(witnesses)==29
    assert len([x for x in out if x['scope']=='lift'])==492
    return out+witnesses
