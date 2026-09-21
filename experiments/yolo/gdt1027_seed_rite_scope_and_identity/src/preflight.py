from copy import deepcopy
from common import *
from model import RULES,compile_reading,execute
from independent import compile_reverse,fact_violations,validate_trace,independent_worlds

# Invented forms only, no source/target loading or source-dependent result.
tags=sum(RULES,[])
lex={f'invented_{tag}':dict(tag=tag) for tag in set(tags)}
lines=[dict(words=[f'invented_{tag}' for tag in tags])]
checks=[]
for c in spec()['candidates']:
    g=compile_reading(lines,lex,c); assert g['status']=='COMPLETE'
    assert compile_reverse(lines,lex,c)=='COMPLETE'
    for mode in ['NONE']+spec()['countercases']:
        w=good_world(); out=execute(g,[4],w,mode,True)
        assert out['coherent']==(mode=='NONE')
        assert out['coherent']==(not fact_violations(c,[4],w,mode))
        validate_trace(c,[4],w,out,mode)
        checks.append(dict(candidate=c['id'],case=mode,status='PASS'))
    selfworld=dict(id='SYNTHETIC_SELF',actor='A',recipient='A',knowledge={'A':dict(P_rite=False,P_attach=True,P_purpose=False)},purity={'A':True})
    for ns in [[],[4],[2,2],[4,4],[3,3]]:
        out=execute(g,ns,selfworld,store_trace=True)
        assert out['coherent']==(not fact_violations(c,ns,selfworld))
        validate_trace(c,ns,selfworld,out)
        checks.append(dict(candidate=c['id'],case=f'self{ns}',status='PASS'))
omissions=[];cursor=0
for i,rule in enumerate(RULES):
    ts=tags[:cursor]+tags[cursor+len(rule):]; ls=[dict(words=[f'invented_{t}' for t in ts])]
    assert compile_reading(ls,lex,spec()['candidates'][0])['status']=='GRAMMAR_CONTRADICTION'
    assert compile_reverse(ls,lex,spec()['candidates'][0])=='GRAMMAR_CONTRADICTION'
    omissions.append(f'C{i+1:02}'); cursor+=len(rule)
mutations=[]
for position,replacement in [(4,'CLOTH'),(8,'RECIPIENT'),(18,'PURE'),(21,'NOT'),(29,'KNOWS')]:
    ls=deepcopy(lines);ls[0]['words'][position]='invented_'+replacement
    assert compile_reading(ls,lex,spec()['candidates'][0])['status']=='GRAMMAR_CONTRADICTION'
    assert compile_reverse(ls,lex,spec()['candidates'][0])=='GRAMMAR_CONTRADICTION'
    mutations.append(dict(position=position+1,replacement=replacement))
assert worlds()==independent_worlds()
write(A/'PREFLIGHT.json',dict(status='PASS',utc=now(),target_executed=False,synthetic_cases=checks,omitted_clauses=omissions,wrong_types=mutations,independent_world_generation=272))
rows=[]
for c in spec()['candidates']:
    expected={('TOTAL','SAME_OBJECT'):96,('EACH','SAME_OBJECT'):64,('TOTAL','DIFFERENT_OBJECTS'):102,('EACH','DIFFERENT_OBJECTS'):68}[c['quantity'],c['knowledge']]
    rows.append(dict(candidate=c['id'],complete_rows=1904,predicted_coherent=expected,predicted_self_coherent=0 if c['knowledge']=='SAME_OBJECT' else (6 if c['quantity']=='TOTAL' else 4),predicted_extra_countercase_contradictions=6,independent_meaning_capacity=0))
table(A/'PREDICTIONS.tsv',rows)
print('PASS:96 synthetic cases,5 omitted clauses,5 type mutations; actual target not executed.')
