"""Source-only automorphisms of complete ordered condition traces.

Block IDs and semantic atom names are not fixed colors. Positions within each
trace are fixed; all block permutations are allowed. Refinement is invariant
under every global atom renaming preserving the multiset of complete traces.
Exact enumeration within residual atom classes gives a complete result only
on exhaustion. Always-adjacent factors flag possible code-boundary ambiguity,
not an assertion that every prefix-free fitted code admits a deformation.
"""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from math import factorial
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parents[1]
SECONDS_PER_ORDER=30
PERMUTATION_CAP=100000

def colorize(signatures):
    unique={s:i for i,s in enumerate(sorted(set(signatures),key=repr))}
    return [unique[s] for s in signatures]

def refinement(words):
    atoms=sorted(set(itertools.chain.from_iterable(words)))
    ac={a:0 for a in atoms}; bc=colorize([len(w) for w in words]); rounds=0
    while True:
        rounds+=1
        bs=[(bc[i],tuple(ac[a] for a in w)) for i,w in enumerate(words)]
        nb=colorize(bs)
        occurrences={a:[] for a in atoms}
        for i,w in enumerate(words):
            for pos,a in enumerate(w):
                occurrences[a].append((nb[i],pos))
        na=dict(zip(atoms,colorize([(ac[a],tuple(sorted(occurrences[a]))) for a in atoms])))
        stable=len(set(na.values()))==len(set(ac.values())) and len(set(nb))==len(set(bc))
        ac,bc=na,nb
        if stable:
            break
    classes=defaultdict(list)
    for a,c in ac.items():
        classes[c].append(a)
    return atoms,list(classes.values()),bc,rounds

class Union:
    def __init__(self,items):
        self.parent={i:i for i in items}
    def find(self,x):
        while self.parent[x]!=x:
            x=self.parent[x]
        return x
    def join(self,a,b):
        self.parent[self.find(a)]=self.find(b)
    def classes(self):
        result=defaultdict(list)
        for x in self.parent:
            result[self.find(x)].append(x)
        return sorted((sorted(v) for v in result.values()),key=repr)

def adjacency(words):
    nxt=defaultdict(set); prev=defaultdict(set); counts=Counter()
    for w in words:
        for i,a in enumerate(w):
            counts[a]+=1
            prev[a].add(w[i-1] if i else None)
            nxt[a].add(w[i+1] if i+1<len(w) else None)
    pairs=[]
    for a,values in nxt.items():
        if len(values)==1:
            b=next(iter(values))
            if b is not None and prev[b]=={a}:
                pairs.append({'first':a,'second':b,'occurrences_each':counts[a],
                              'scope':'obligatory adjacency in these source traces only; possible boundary gauge'})
    return pairs

def audit(words,ids,seconds=SECONDS_PER_ORDER,cap=PERMUTATION_CAP):
    words=[tuple(w) for w in words]
    assert len(ids)==len(words) and len(set(ids))==len(ids)
    assert all(w and all(type(a) is str for a in w) for w in words)
    atoms,classes,blockcolors,rounds=refinement(words)
    residual=1
    for group in classes:
        residual*=factorial(len(group))
    source=Counter(words); byword=defaultdict(list)
    for bid,w in zip(ids,words):
        byword[w].append(bid)
    atomorbits=Union(atoms); blockorbits=Union(ids)
    # Duplicate complete traces allow address permutations with the identity key.
    duplicate_factor=1
    for group in byword.values():
        duplicate_factor*=factorial(len(group))
        for bid in group[1:]:
            blockorbits.join(group[0],bid)
    start=time.monotonic(); tried=0; found=0; witnesses=[]; mapping={}
    unknown=False
    def visit(level):
        nonlocal tried,found,unknown
        if time.monotonic()-start>=seconds or tried>=cap:
            unknown=True; return
        if level<len(classes):
            group=classes[level]
            for permutation in itertools.permutations(group):
                mapping.update(zip(group,permutation)); visit(level+1)
                if unknown:
                    return
            return
        tried+=1
        transformed=[tuple(mapping[a] for a in w) for w in words]
        if Counter(transformed)!=source:
            return
        found+=1; changed=False
        for a,b in mapping.items():
            if atomorbits.find(a)!=atomorbits.find(b):
                changed=True; atomorbits.join(a,b)
        for bid,w in zip(ids,transformed):
            for dest in byword[w]:
                if blockorbits.find(bid)!=blockorbits.find(dest):
                    changed=True; blockorbits.join(bid,dest)
        if changed:
            witnesses.append({'renamed_atoms':{a:b for a,b in mapping.items() if a!=b},
                              'block_images':{bid:byword[w] for bid,w in zip(ids,transformed)}})
    visit(0)
    # Reaching the cap on the final permutation still exhausts the domain.
    complete=tried==residual
    return {'status':'COMPLETE' if complete else 'UNKNOWN_BUDGET',
            'refinement_rounds':rounds,'atom_count':len(atoms),'atom_color_classes':classes,
            'single_occurrence_atoms':sorted(a for a,n in Counter(itertools.chain.from_iterable(words)).items() if n==1),
            'residual_permutations':residual,'permutations_examined':tried,
            'atom_automorphisms_found':found,'identical_trace_block_permutation_factor':duplicate_factor,
            'combined_automorphism_count':found*duplicate_factor if complete else None,
            'atom_orbits':atomorbits.classes(),'block_orbits':blockorbits.classes(),
            'orbit_scope':'complete' if complete else 'lower bounds from found automorphisms only',
            'nontrivial_orbit_witnesses':witnesses,'obligatory_adjacent_pairs':adjacency(words),
            'seconds':time.monotonic()-start}

def selftest():
    r=audit([['A','X'],['B','X']],['1','2'])
    assert r['status']=='COMPLETE' and r['atom_automorphisms_found']==2
    assert ['1','2'] in r['block_orbits']
    r=audit([['A','X'],['A','X']],['1','2'])
    assert r['combined_automorphism_count']==2
    assert r['obligatory_adjacent_pairs'][0]['first']=='A'
    r=audit([['A','X'],['B','X'],['A','A']],['1','2','3'])
    assert r['combined_automorphism_count']==1
    assert audit([['A'],['B']],['1','2'],seconds=0)['status']=='UNKNOWN_BUDGET'
    return {'status':'PASS','scope':'invented source-language automorphism and cutoff fixtures'}

def main():
    import sys
    if sys.argv[1:]==['--selftest']:
        print(json.dumps(selftest())); return
    import source
    path=ROOT/'artifacts/SOURCE_PROGRAMS.json';raw=path.read_bytes();packet=json.loads(raw)
    programs=packet['programs'];orders=packet['header_orders']
    assert len(programs)==24 and len(orders)==6
    results=[]
    for order in orders:
        words=[source.compile_program(p,order) for p in programs]
        result=audit(words,[p['id'] for p in programs]);result['header_order']=order
        results.append(result)
    record={'schema':'GDT899_SOURCE_SYMMETRY_V1','status':'COMPLETE' if all(r['status']=='COMPLETE' for r in results) else 'UNKNOWN_BUDGET',
            'completion_scope':'Within each fixed header order only; not a fitted-code uniqueness result',
            'source_programs_sha256':hashlib.sha256(raw).hexdigest(),
            'compiler_sha256':hashlib.sha256((ROOT/'src/source.py').read_bytes()).hexdigest(),
            'auditor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'seconds_per_order':SECONDS_PER_ORDER,'permutation_cap_per_order':PERMUTATION_CAP,
            'orders':results,'limits':['No target read or fitted-key claim.','Header orders audited separately; equivalences between different orders are not exhausted.','Adjacency is a possible code-boundary ambiguity, not a proof for every prefix-free key.','Literal prognosis payloads omitted by the compiler cannot break condition-trace symmetries.']}
    (ROOT/'artifacts/SOURCE_SYMMETRY.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'status':record['status'],'orders':len(results),'counts':[r['combined_automorphism_count'] for r in results]}))

if __name__=='__main__':
    main()
