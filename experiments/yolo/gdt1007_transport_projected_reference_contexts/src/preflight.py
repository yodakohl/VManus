from common import *
from run import primary_query
s,g=inputs();candidates=read(A/'CANDIDATE_PREDICTIONS.json');world=load(s['primary'],'world1003');ind=load(s['independent'],'independent1003');checks=[]
for shape in ['ONE_CARGO','TWO_CARGOS']:
    for c in candidates:
        kinds=['INITIAL','GOAL','SAFETY','CAPACITY','FERRY']+(['EXCLUDE','FERRY'] if shape=='TWO_CARGOS' else [])+['CONCLUSION']
        words=[];lex={};ferry_count=0
        for kind in kinds:
            pat=g['patterns'][kind]
            for j,t in enumerate(pat):
                if t=='@CARGO':value=c['values']['lchedy']
                elif t.startswith('@'):value=g['types'][t[1:]][0]
                else:value=t
                token='fixture_'+value
                if kind=='CAPACITY' and j==4:token='lchedy';value=c['values']['lchedy']
                if kind=='FERRY' and j==1:
                    token='chedy' if shape=='ONE_CARGO' or ferry_count==1 else 'lchedy';value=c['values'][token];ferry_count+=1
                if kind=='EXCLUDE' and j==1:token='lchedy';value=c['values']['lchedy']
                if token in lex:assert lex[token]==value
                lex[token]=value;words.append(token)
        p=dict(words=words);b=world.build([p],lex,g,5000);q=primary_query(b,c,world,s)
        solver,xs,num,other,there=ind.build([p],lex,g,5000);solver.add(other==int(c['variant']['other']=='FIRST'),there==int(c['variant']['there']=='CURRENT'));other_status=str(solver.check())
        expected='sat' if (c['chedy_class']=='REFERENCE')==(shape=='ONE_CARGO') else 'unsat'
        assert q['status']==other_status==expected,(shape,c['id'],q['status'],other_status,expected)
        if q['status']=='sat':assert replay(q['parse'],q['variant'],s,True)==q['replay']
        checks.append(dict(shape=shape,candidate=c['id'],groups=len(words),expected=expected,z3=q['status'],cvc5=other_status))
put('PREFLIGHT.json',dict(status='PASS',complete_synthetic_context_checks=len(checks),checks=checks,scope='Constructed semantic sensitivity and pinning check, no manuscript content or independent meaning.'))
print(json.dumps(dict(status='PASS',checks=len(checks))))
