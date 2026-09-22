from common import *
from model import TAGS,compile_reading,evaluate,projection
from independent import compile_reverse,prediction,validate_output
# Only invented forms; no target paragraph is compiled here.
lex={f'INVENTED_{i}':dict(value=t) for i,t in enumerate(TAGS)}
lines=[dict(words=list(lex))];assert compile_reverse(lines,lex)=='COMPLETE_GRAPH'
rows=[]
for c in spec()['candidates']:
 g=compile_reading(lines,lex,c);assert g['status']=='COMPLETE_GRAPH'
 for f in cases():
  o=evaluate(g,f);validate_output(g,f,o);p=prediction(c,f['name']);assert projection(c,f['name'],o)==p,(c['id'],f['name'],projection(c,f['name'],o),p);rows.append(p)
for i in [0,7,8,13,16,18,23,26,32,35,36,38,39]:
 shortened=[dict(words=[w for j,w in enumerate(lex) if j!=i])]
 assert compile_reading(shortened,lex,spec()['candidates'][0])['status']=='UNBOUND_WHOLE_GRAMMAR'
table(A/'PREDICTIONS.tsv',rows)
write(A/'PREFLIGHT.json',dict(status='PASS',utc=now(),invented_forms_only=True,target_semantics_executed=False,complete_predictions=len(rows),omission_checks=13))
print('PASS invented preflight',len(rows))
