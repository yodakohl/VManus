import json,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('fe',P/'FE_RUN.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r,c,x=m.build();checks=0
for f,obj in [('FE_RESULT.json',r),('FE_CASES.json',c),('FE_CONTEXTS.json',x)]:assert json.loads((P/f).read_text())==obj;checks+=1
assert len(c)==4 and len(x)==3;checks+=2
assert r['outside_construction_candidates']==r['conditional_reverse_candidates']==r['actual_fixed_graph_conflicts']==0;checks+=3
assert all(z['physical_leaf']==113 for z in c);checks+=1
assert r['eligible_primary_candidates']==2;checks+=1
v={'status':'COVERAGE_REPLAY_PASS','checks':checks,'semantic_validation':False,'scope':'4exactwindows/fullmatchingcontexts; no universalpatternobligation or wordmeaningtest'}
(P/'FE_VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
