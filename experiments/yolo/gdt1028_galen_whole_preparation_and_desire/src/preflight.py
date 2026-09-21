from copy import deepcopy
from common import *
from model import RULES,compile_reading,evaluate
from independent import compile_reverse,predict,observe,validate_output

assert not (A/'RESULT.json').exists()
cfg=spec();fs=cases();assert [f['name'] for f in fs]==cfg['case_names']
# Invented whole forms only: no target words are read or compiled here.
tags=sorted(set(v for rule in RULES for v in rule))
lex={f'FIXTURE_{n}':dict(value=v) for n,v in enumerate(tags)}
inverse={e['value']:w for w,e in lex.items()}
lines=[dict(words=[inverse[v] for v in rule]) for rule in RULES]
productions=[dict(production=' '.join(rule)) for rule in RULES]
pred=[];count=0
for c in cfg['candidates']:
    g=compile_reading(lines,lex,c);assert g['status']=='COMPLETE_GRAPH'
    assert compile_reverse(lines,lex,productions)=='COMPLETE_GRAPH'
    names=fs if c['syntax']=='QUOTED_FOOD_TRANSFER' else [dict(name='STATIC_WHOLE_GRAPH')]
    for f in names:
        p=predict(c,f['name']);o=evaluate(g,f)
        assert observe(c,f['name'],o)==p,(c,f,p,o)
        validate_output(c,f,g,o);pred.append(p);count+=1
for i in range(5):
    omitted=lines[:i]+lines[i+1:]
    assert compile_reading(omitted,lex,cfg['candidates'][0])['status']=='GRAMMAR_CONTRADICTION'
    changed=deepcopy(lines);changed[i]['words'][0]='FIXTURE_UNKNOWN'
    assert compile_reading(changed,lex,cfg['candidates'][0])['status']=='UNBOUND_FORMS'
assert count==228
table(A/'PREDICTIONS.tsv',pred)
write(A/'PREFLIGHT.json',dict(status='PASS',utc=now(),invented_form_case_checks=count,whole_clause_omissions_rejected=5,unknown_form_mutations_rejected=5,target_execution=False,meaning_evidence=False))
print(json.dumps(read(A/'PREFLIGHT.json')))
