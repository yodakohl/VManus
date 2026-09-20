from common import *
import layout_solver,layout_independent
from evaluate import evaluate
s,g=inputs();original=read(A/'PANEL.json')[0];source=read(R/s['source_functional']);a=next(x for x in source['attempts'] if x['coherent_variants']);layouts=read(A/'LAYOUTS.json')
key=[{k:c[k] for k in ['start','end','kind']} for c in a['parse']]
same=next(x for x in layouts if x['layout']==key);other=next(x for x in layouts if x['layout']!=key)
checks=[]
for name,blocked,expected in [('PINNED_ORIGINAL',[], 'SAT'),('PINNED_OWN_LAYOUT_BLOCKED',[same['layout']],'UNSAT'),('PINNED_OTHER_LAYOUT_BLOCKED',[other['layout']],'SAT')]:
    one=layout_solver.solve([original],a['code'],g,timeout=10000,witness_limit=1,blocked_layouts=blocked)
    two=layout_independent.check([original],a['code'],g,timeout=10000,blocked_layouts=blocked)
    assert one['status']==expected and two['status']==expected.lower()
    checks.append(dict(name=name,primary=one['status'],independent=two['status']))
case=dict(id='FIXTURE',layout=same['id'],code=a['code'],parse=a['parse'],bijective=len(set(a['code'].values()))==47)
one=evaluate(case);two=evaluate(case,True);assert one==two and one['valid_variants']==a['coherent_variants']
put('PREFLIGHT.json',dict(status='PASS',checks=checks,known_source_meaning_variants=32,known_valid_variants=one['valid_variants'],free_original_coverage_query='NOT_RUN'))
print(json.dumps(dict(status='PASS',grammar_checks=3,meaning_settings=32)))

from worker import bounded
one=bounded('primary',dict(paragraphs=[original],lexicon=a['code']));two=bounded('independent',dict(paragraphs=[original],lexicon=a['code']))
assert one['status']=='SAT' and two['status']=='sat'
w=dict(aliases=a['code'],parses=[a['parse'],one['witnesses'][0]['parses'][0]])
m=bounded('meaning',dict(witness=w));mi=bounded('meaning',dict(witness=w,independent=True))
assert m['status']==mi['status']=='COMPLETE' and m['variants']==mi['variants']
assert any(v['status']=='COHERENT_COMMON_READING' for v in m['variants'])
r=read(A/'PREFLIGHT.json');r['extension_wrapper_checks']=dict(primary='SAT',independent='sat',meaning_settings=32,separate_meaning_equal=True);put('PREFLIGHT.json',r)
print(json.dumps(r['extension_wrapper_checks']))
