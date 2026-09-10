#!/usr/bin/env python3
"""Finite exhaustive oracle checks for the exact equation enumerator."""
import itertools,time
from run import solve_words,compatible,reject,constraints,Budget

def main():
    a,b=('a',),('b',)
    examples=[([((a,b),'xyx'),((a,a),'xx')],1),([((a,),'x'),((b,),'xy')],0),
              ([((a,b),'abcd')],3),([((a,a),'xy'),((b,),'z')],0),
              ([((a,b,a),'xyx'),((b,a,b),'yxy')],1)]
    for equations,n in examples:
        actual=list(solve_words(equations,time.monotonic()+5))
        pool={word[i:j] for _,word in equations for i in range(len(word)) for j in range(i+1,len(word)+1)}
        brute=[]
        for va,vb in itertools.product(pool,repeat=2):
            key={a:va,b:vb}
            if not compatible({a:va},vb):continue
            if all(''.join(key[u] for u in seq)==word for seq,word in equations):brute.append(key)
        canon=lambda keys:{tuple(sorted(k.items())) for k in keys}
        assert canon(actual)==canon(brute) and len(actual)==n
    alphabet=[('a',),('b',),('c',)]
    pattern=tuple(list(itertools.product(alphabet,repeat=1))+list(itertools.product(alphabet,repeat=2))+list(itertools.product(alphabet,repeat=3))[:6])
    assert len(pattern)==18
    for code in [{alphabet[0]:'a',alphabet[1]:'bb',alphabet[2]:'bc'},
                 {alphabet[0]:'xy',alphabet[1]:'xz',alphabet[2]:'z'}]:
        words=[''.join(code[u] for u in seq) for seq in pattern]
        assert reject(pattern,words,constraints(pattern)) is None
    try:list(solve_words(examples[0][0],time.monotonic()-1))
    except Budget:pass
    else:raise AssertionError('Expired budget must be unresolved')
    print('PASS exact finite oracle, all partitions, shared code, prefix gates, timeout')
if __name__=='__main__':main()
