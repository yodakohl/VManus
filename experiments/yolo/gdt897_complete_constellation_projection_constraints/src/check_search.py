"""Complete tiny permutation oracle checks pruning and compiled search logic."""
import itertools
import json
import random
import tempfile
from pathlib import Path
import prepare
import run

def oracle(case,g):
    n=case['n'];k=3 if case['mode']=='gnomonic' else 4
    tuples=list(itertools.combinations(range(n),k))
    for p in itertools.permutations(range(n)):
        if all((prepare.flip(case['source_masks'][prepare.flat(t,n)]) if g<0 else case['source_masks'][prepare.flat(t,n)]) & case['target_masks'][prepare.flat(tuple(p[i] for i in t),n)] for t in tuples):return True
    return False
def main():
    rng=random.Random(897);count=0
    with tempfile.TemporaryDirectory(prefix='gdt897_synthetic_') as directory:
        binary=run.compile_solver(directory)
        for mode,k in [('gnomonic',3),('stereographic',4)]:
            for trial in range(20):
                n=5 if k==3 else 6
                s=prepare.tensor(n,k,lambda _:rng.choice([1,2,3,4,5,6,7]))
                t=prepare.tensor(n,k,lambda _:rng.choice([1,2,3,4,5,6,7]))
                if trial==0:t=s[:]
                if trial==1:s=prepare.tensor(n,k,lambda _:1);t=prepare.tensor(n,k,lambda _:2)
                c={'case_id':str(count),'mode':mode,'n':n,'source_masks':s,'target_masks':t}
                r=run.solve_case(c,binary,10)
                for o in r['orientations']:
                    expected=oracle(c,o['g']);assert (o['status']=='INVARIANT_COMPATIBLE')==expected,(c['case_id'],o,expected)
                    assert o['status']!='UNKNOWN_BUDGET'
                count+=1
    out={'status':'PASS','complete_small_tensor_cases':count,'orientations_per_case':2,'scope':'Search and pruning logic on invented complete tensors, not manuscript evidence.'}
    (Path(__file__).resolve().parents[1]/'artifacts/SEARCH_PREPARATION.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
