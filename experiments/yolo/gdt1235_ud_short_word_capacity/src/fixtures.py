"""Exhaustive binary UD-book control before any native capacity calculation."""
from pathlib import Path
from datetime import datetime,timezone
from itertools import product,combinations
import json
from engine import enumerate_cases,subcode,lower_bound,ud_certificate
from validate import independent_ud,verify_ud,check
D=Path(__file__).resolve().parents[1]


def parse(word,C):
    ways={0:[()]}
    for i in range(len(word)):
        for seq in ways.get(i,[]):
            for c in C:
                if word[i:i+len(c)]==c:ways.setdefault(i+len(c),[]).append(seq+(c,))
    answer=ways.get(len(word),[]);assert len(answer)<=1
    return answer[0]if answer else None


def run():
    U=[w for n in range(1,4)for w in product('ab',repeat=n)];books=[];checked=0
    for mask in range(1,1<<len(U)):
        C=tuple(U[i]for i in range(len(U))if mask>>i&1);valid,_=independent_ud(C)
        verify_ud(C,ud_certificate(C));checked+=1
        if valid:books.append((C,{w:parse(w,C)for w in U},{c[0]for c in C if len(c)==1}))
    sets=compatible=longchecks=0
    for n in range(1,4):
        for W in combinations(U,n):
            if {g for w in W for g in w}!=set('ab'):continue
            sets+=1;cert=enumerate_cases(W,'ab');check(W,'ab',cert)
            for C,parses,S in books:
                if any(parses[w]is None for w in W):continue
                compatible+=1
                if not any(len(c)>1 for w in W for c in parses[w]):continue
                longchecks+=1;rows=[r for r in cert['rows']if set(r['singletons'])==S];assert len(rows)==1;row=rows[0]
                B=subcode(S,{w for w in W if len(w)==2});assert set(B)<=set(C)
                assert row['ud']['status']=='UD'and row['bound']<=len(C)
    named=[]
    for W in [('a','ab'),('a','c','ab','bc'),('aa','b'),('aaa','b'),('aa','aaa'),('a','ab','bba')]:
        A=sorted({g for w in W for g in w});cert=enumerate_cases(W,A);check(W,A,cert);named.append({'W':W,'alphabet':A,'certificate':cert})
    assert independent_ud([tuple(w)for w in ('a','ab','bba')])[0]
    assert named[0]['certificate']['summary']['necessary_nontrivial_bound']==2
    assert named[1]['certificate']['summary']['decision']=='ONLY_IDENTITY'
    assert named[4]['certificate']['summary']['necessary_nontrivial_bound']==1
    assert sets==455
    return {'status':'PASS','checked_utc':datetime.now(timezone.utc).isoformat(),'all_binary_codebooks_checked':checked,'binary_ud_codebooks':len(books),'word_sets':sets,'compatible_book_word_pairs':compatible,'used_nontrivial_bound_checks':longchecks,'named':named,'extra_named_limit':'Unaryaa/aaa survives necessary bound1 with S empty, but has no actual unaryUDfull writer; do not treat bounds as existence.'}


if __name__=='__main__':
    r=run();(D/'artifacts/FIXTURES.json').write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items()if k!='named'})
