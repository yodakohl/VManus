"""Finite Cartesian oracle checks; target-free and not a semantic null."""
import itertools,json
from pathlib import Path
from finite import solve
from reverse import replay,ground
E=Path(__file__).resolve().parents[1]

def oracle(atoms,words,types):
    pieces=sorted({w[i:j] for w in words for i in range(len(w)) for j in range(i+1,len(w)+1)});names=sorted(set(atoms));out=[]
    for vals in itertools.product(pieces,repeat=len(names)):
        code=dict(zip(names,vals))
        try:ground(atoms,words,types,code)
        except AssertionError:continue
        out.append(code)
    return out

def main():
    total=0;both_classes=0
    for n in range(1,5):
        for atoms0 in itertools.product('AB',repeat=n):
            atoms=list(atoms0);names=sorted(set(atoms))
            for same in (True,False):
                types={a:'T0' if same else 'T'+str(i) for i,a in enumerate(names)}
                for m in range(1,4):
                    for letters in itertools.product('ab',repeat=m):
                        text=''.join(letters)
                        for cuts in itertools.product((False,True),repeat=m-1):
                            ws=[];start=0
                            for i,cut in enumerate(cuts,1):
                                if cut:ws.append(text[start:i]);start=i
                            ws.append(text[start:]);expected=oracle(atoms,ws,types)
                            a=solve(atoms,ws,types,seconds=2,max_nodes=100000,max_solutions=2)
                            b=replay(atoms,ws,types,seconds=2,max_nodes=100000,max_solutions=2)
                            assert (a['status']=='SAT')==bool(expected),(atoms,ws,types,a,expected)
                            assert (b['status']=='SAT_REPLAY')==bool(expected)
                            for result in (a,b):
                                codes=result.get('codes',[]);assert len(codes)==min(2,len(expected));assert all(c in expected for c in codes)
                                if len(expected)<2:assert result['exhaustive']
                            total+=1;both_classes+=len(set(types.values()))>1
    # Former global forced-start pruning would wrongly reject this valid typed collision.
    atoms=['A','B','A'];words=['a','a','a'];types={'A':'OP','B':'ENTITY'}
    a=solve(atoms,words,types);assert a['status']=='SAT' and a['codes']==[{'A':'a','B':'a'}]
    assert solve(atoms,words,{'A':'OP','B':'OP'})['status']=='UNSAT_FINITE'
    output=dict(status='PASS',cartesian_cases=total,mixed_type_cases=both_classes,cross_type_identical_code_fixture=True,same_type_collision_rejected=True,scope='Exact small-code search and type-rule validation; no target access or full-search significance')
    (E/'artifacts/PREFLIGHT.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
if __name__=='__main__':main()
