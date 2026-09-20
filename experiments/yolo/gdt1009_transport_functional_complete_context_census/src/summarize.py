from common import *
import csv,collections
s,g=inputs();rows=read(A/'ROWS.json');v=read(A/'VALIDATION.json');panel=read(A/'PANEL.json');inherited=read(A/'INHERITED.json')
assert v['status']=='PASS' and not v['independent_unknowns'] and not v['unverified_negatives']
checks={x['id']:x for x in v['checks']};new={x['paragraph_ids'][1]:x for x in rows};old={x['paragraph']:x for x in inherited}
allrows=[]
for p in panel[1:]:
    if p['id'] in new:
        r=new[p['id']];c=checks[r['id']]
        status=r['status'];certificate='GDT1009:'+r['id'];secondary=c['independent']
    else:
        r=old[p['id']];status=r['status'];certificate='GDT1008:'+r['row'];secondary=r['independent']
    assert status=='UNSAT' and secondary=='unsat'
    allrows.append(dict(paragraph=p['id'],edition=p['edition'],physical_leaf=p['leaf'],groups=p['groups'],strict_source=p['strict_anchor_eligible'],prediction='Complete joint grammar under one free global dictionary; aliases allowed',observed=status,independent=secondary,certificate=certificate,remaining_common_readings=0,independent_meaning_capacity=0))
assert len(allrows)==120
with (A/'CONTEXT_CLOSURE.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(allrows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(allrows)
out=dict(status='ALL_120_COMPLETE_FUNCTIONAL_CONTEXTS_EXCLUDED',new_queries=118,inherited_negatives=2,contexts=120,strict_source_contexts=sum(p['strict_anchor_eligible'] for p in panel[1:]),conditional_source_contexts=sum(not p['strict_anchor_eligible'] for p in panel[1:]),other_physical_leaves=len({p['leaf'] for p in panel[1:]}),dependency='GDT1009 independent grammar negatives plus two GDT1008 independent grammar negatives; no GDT1006 projection exhaustion required',bijection='Also excluded as a subset of FUNCTIONAL',original_local_worlds='RETAINED',original_functional_enumeration='UNCHANGED_INCOMPLETE; not needed for this closure',unknowns=0,confirmed_words=0,independent_meaning_capacity=0,significance=False)
put('CLOSURE.json',out);print(json.dumps(out,indent=2))
