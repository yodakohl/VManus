"""Finite brute-force controls before any native result."""
from pathlib import Path
from itertools import product, combinations
from datetime import datetime,timezone
import json
from engine import solve
D=Path(__file__).resolve().parents[1]

def brute(words):
    alphabet=('a','b')
    choices={g:[(g,)+tail for n in range(3) for tail in product(alphabet,repeat=n)] for g in alphabet}
    for ca,cb in product(choices['a'],choices['b']):
        table={'a':ca,'b':cb};used=set();valid=True
        for word in words:
            p=0
            while p<len(word):
                g=word[p];code=table[g]
                if tuple(word[p:p+len(code)]) != code:
                    valid=False;break
                used.add(g);p+=len(code)
            if not valid:break
        if valid and any(len(table[g])>1 for g in used):return True
    return False

def main():
    vocab=[''.join(s) for n in range(1,4) for s in product('ab',repeat=n)]
    cases=0;positive=0
    for size in range(1,4):
        for ws in combinations(vocab,size):
            expected=brute(ws)
            r=solve([(str(i),tuple(w))for i,w in enumerate(ws)],list('ab'),10)
            assert r['status']!='UNKNOWN'
            assert (r['status']=='NONTRIVIAL')==expected,(ws,expected,r)
            cases+=1;positive+=expected
    named={}
    for name,ws in [('positive',['ab','abab','bb']),('parity',['aa','aaa','b'])]:
        r=solve([(str(i),tuple(w))for i,w in enumerate(ws)],list('ab'),10)
        assert r['status']==('NONTRIVIAL'if name=='positive'else'ALL_USED_CODES_SINGLETON')
        named[name]=r
    out={'status':'PASS','checked_utc':datetime.now(timezone.utc).isoformat(),'binary_word_sets':cases,'all_binary_codebooks_per_set':49,'positive_sets':positive,'negative_sets':cases-positive,'named':named,'native_data_read':False}
    (D/'artifacts/FIXTURES.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items()if k!='named'},indent=2))
if __name__=='__main__':main()
