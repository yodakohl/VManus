from copy import deepcopy
from common import *
from model import NEW_TAGS,PM,compile_pair,evaluate,projection
from independent import compile_reverse,prediction,validate_graph,validate_output
assert not (A/'RESULT.json').exists()
s=source();cfg=spec();fs=cases()
# Invented forms follow the stated tag productions; no target strings are compiled.
alltags=sorted(set(NEW_TAGS+[v for rule in PM.RULES for v in rule]));lex={f'FIXTURE_{i}':dict(value=v) for i,v in enumerate(alltags)}
inv={x['value']:w for w,x in lex.items()}
old=[dict(words=[inv[v] for v in rule]) for rule in PM.RULES];new=[dict(words=[inv[v] for v in NEW_TAGS])]
pred=[]
for c in cfg['candidates']:
    g=compile_pair(old,new,lex,c);assert g['status']=='COMPLETE_POSITION_GRAPH';validate_graph(g,s)
    assert compile_reverse(old,new,lex,s)=='COMPLETE_POSITION_GRAPH'
    for f in fs if c['kind']=='SEMANTIC' else [dict(name='STATIC_WHOLE_GRAPH')]:
        o=evaluate(g,f);validate_output(g,f,o)
        expected=prediction(c,f['name']);assert projection(c,f['name'],o)==expected,(c,f)
        pred.append(expected)
for pos in [1,18,21,24,26,31,37,43,45,46]:
    changed=deepcopy(new);changed[0]['words'].pop(pos-1)
    assert compile_pair(old,changed,lex,cfg['candidates'][0])['status']=='NEW_GRAMMAR_GAP'
bad=deepcopy(fs[0]);bad['ordinary_soft']=False
try:evaluate(compile_pair(old,new,lex,cfg['candidates'][0]),bad)
except AssertionError as e:assert 'INVALID_FIXTURE' in str(e)
else:raise AssertionError('invalid proper/ordinary input was accepted')
assert len(pred)==87
table(A/'PREDICTIONS.tsv',pred)
write(A/'PREFLIGHT.json',dict(status='PASS',utc=now(),synthetic_case_checks=87,omission_checks=10,invalid_softness_fixture_rejected=1,target_executed=False,meaning_evidence=False))
print(json.dumps(read(A/'PREFLIGHT.json')))
