from common import *
import copy,solver,independent
s,g=inputs();p=read(A/'PANEL.json')[0];source=read(R/s['source_original_candidates']);a=next(x for x in source['attempts'] if x['coherent_variants']);lex=a['code'];renamed=copy.deepcopy(p)
mapping={w:'fixture_'+str(i) for i,w in enumerate(sorted(set(p['words'])))};renamed['words']=[mapping[w] for w in p['words']];renamed_lex={**lex,**{mapping[w]:v for w,v in lex.items()}}
bad=copy.deepcopy(p);bad['words'][1]='chedain';checks=[]
for family in s['families']:
    fixtures=[('ORIGINAL',[p],lex,'SAT'),('DUPLICATE',[p,p],lex,'SAT'),('RENAMED_ALIASES',[p,renamed],renamed_lex,'SAT'),('FREE_BAD_HEADER',[p,bad],{},'UNSAT')]
    for name,ps,l,expected in fixtures:
        primary=solver.solve(ps,l,g,timeout=10000,witness_limit=1,family=family);other=independent.check(ps,l,g,timeout=10000,family=family)
        assert primary['status']==expected and other['status']==expected.lower(),(family,name,primary,other)
        checks.append(dict(family=family,fixture=name,primary=primary['status'],independent=other['status']))
put('PREFLIGHT.json',dict(status='PASS',checks=checks,scope='Pinned original, duplicate, new-form aliases and free known countercase; not independent manuscript meaning.'))
print(json.dumps(dict(status='PASS',checks=len(checks))))
