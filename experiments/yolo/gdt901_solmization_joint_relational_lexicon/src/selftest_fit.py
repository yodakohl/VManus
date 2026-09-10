#!/usr/bin/env python3
"""Constructed full witnesses, impossibility examples, and exhaustive tiny oracle."""
import itertools,json,random,time
from fit import ExactModel,replay

def source(sequences,forms=None):
    atoms=sorted(set().union(*(set(s) for s in sequences)))
    return {'atoms':atoms,'records':[{'id':str(i),'head_atom':s[0],'sequence':s} for i,s in enumerate(sequences)],
            'forms':forms or {a:{'family':None,'root':None,'roleclass':None} for a in atoms}}
def rows(words):return [{'words':w} for w in words]
def query(s,p,d):
    m=ExactModel(s,p,d);return m,m.query(time.monotonic()+10,1)
def brute(s,p,d):
    for values in itertools.product(*(d[a] for a in s['atoms'])):
        if len(set(values))<len(values):continue
        lex=dict(zip(s['atoms'],values));rev={v:k for k,v in lex.items()}
        for indices in itertools.permutations(range(len(p)),len(s['records'])):
            if all(p[j]['words'][0]==lex[r['head_atom']] and [rev[w] for w in p[j]['words'] if w in rev]==r['sequence'] for r,j in zip(s['records'],indices)):return True
    return False
def main():
    s=source([['H','A','B','A'],['J','B','A']]);s['forms']['A']={'family':'VOICE','root':'ut','roleclass':'VOICE:0'};s['forms']['B']={'family':'VOICE','root':'ut','roleclass':'VOICE:1'}
    d={'H':['head'],'J':['other'],'A':['pab'],'B':['tab']};p=rows([['head','pab','noise','tab','pab'],['other','tab','pab']])
    m,r=query(s,p,d);assert r['status']=='SAT';replay(s,p,r['witness'])
    bad=rows([['head','tab','pab','pab'],['other','tab','pab']]);m,r=query(s,bad,d);assert r['status']=='UNSAT' and m.cuts
    # Counts and order fit, but the two roleforms have no common nonempty root.
    d2={'H':['head'],'J':['other'],'A':['a'],'B':['b']};p2=rows([['head','a','b','a'],['other','b','a']]);_,r=query(s,p2,d2);assert r['status']=='UNSAT'
    # Global background forbids ignoring just one occurrence of an assigned type.
    _,r=query(s,rows([['head','pab','tab','pab','tab'],['other','tab','pab']]),d);assert r['status']=='UNSAT'
    ambiguous=source([['H','A'],['J','B']]);p3=rows([['h','a'],['j','b']]);d3={'H':['h','j'],'J':['h','j'],'A':['a','b'],'B':['a','b']}
    m,r=query(ambiguous,p3,d3);assert r['status']=='SAT';w=r['witness']
    for a,v in m.x.items():
        alt=m.query(time.monotonic()+10,1,(v,m.wid[w['lexicon'][a]]));assert alt['status']=='SAT' and alt['witness']['lexicon'][a]!=w['lexicon'][a]
    assert m.query(time.monotonic()-1,1)['status']=='UNKNOWN'
    rng=random.Random(901);s4=source([['A','B','A'],['B','A']]);d4={'A':['x','y','z'],'B':['x','y','z']}
    for _ in range(60):
        p4=rows([[rng.choice('xyzn') for _ in range(rng.randint(2,6))] for j in range(3)])
        expected=brute(s4,p4,d4);_,actual=query(s4,p4,d4)
        assert actual['status']==('SAT' if expected else 'UNSAT')
    print(json.dumps({'status':'PASS','checks':['full_shared_root_witness','order_only_impossibility_with_lazycuts','nonempty_shared_root_impossibility','global_background','unfrozen_alternative_queries','expired_budget_unknown'],'exhaustive_tiny_cases':60}))
if __name__=='__main__':main()
