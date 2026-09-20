"""Source-only synthetic tests, no manuscript strings or target selection."""
import datetime,json
from pathlib import Path
from core import endpoints,relaxed_path,shared_path
from validate import independent_endpoints,backward,sat_shared,witness_check
E=Path(__file__).resolve().parents[1];R=E.parents[2]
cfg=json.loads((E/'src/SPEC.json').read_text());g=json.loads((R/cfg['grammar']).read_text())
names=['INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'];syms=[]
for k in names:
 for x in g['patterns'][k]:syms.append(g['types'][x[1:]][0] if x.startswith('@') else x)
lex={s:s for s in syms};fixtures=[]
def check(label,words,endpoint,relaxed,shared):
 a=endpoints(words,lex,g);assert a==independent_endpoints(words,lex,g) and a['pass_']==endpoint
 b,_=relaxed_path(words,lex,g);assert b['feasible']==backward(words,lex,g)==relaxed
 c=shared_path(words,lex,g,100000,5);assert c['status']==shared
 d=sat_shared(words,lex,g,10000);assert d==('sat' if shared=='SHARED_SAT' else 'unsat')
 if shared=='SHARED_SAT':witness_check(words,lex,g,c)
 fixtures.append(dict(name=label,endpoint=endpoint,relaxed=relaxed,shared=shared,independent=d))
check('complete_minimal_scope',syms,True,True,'SHARED_SAT')
x=syms.copy();x[0]=x[1]='alias_conflict';check('contradictory_shared_endpoints',x,False,True,'SHARED_UNSAT')
x=syms.copy();x[5]=x[6]='alias_conflict';check('interior_same_spelling_two_roles',x,True,True,'SHARED_UNSAT')
x=syms.copy();x[9]='M';check('known_value_blocks_required_clause',x,True,False,'SHARED_UNSAT')
x=syms[:5]+syms[9:];check('missing_required_clause',x,False,False,'SHARED_UNSAT')
x=syms[:9]+syms[5:9]+syms[9:];check('duplicate_required_clause',x,True,False,'SHARED_UNSAT')
x=syms.copy()
for i in (14,17):
 assert x[i]=='M';x[i]='shared_agent_alias'
check('repeated_consistent_unknown',x,True,True,'SHARED_SAT')
out=dict(status='PASS',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),fixtures=fixtures,manuscript_data_read=False)
(E/'artifacts/PRE_RUN_FIXTURES.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
