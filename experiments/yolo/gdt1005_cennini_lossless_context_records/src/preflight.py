#!/usr/bin/env python3
import collections,itertools,json,sys
from pathlib import Path
from records import FIELDS,build,inverse,profile,prefix_bound,packing
from independent import decode,capacity,pack
from finite import solve
from reverse import replay
sys.setrecursionlimit(10000)
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def main():
    s=json.loads((E/'src/SPEC.json').read_text());source=json.loads((R/s['source_facts']).read_text());records=source['records']
    expected=[{k:r[k] for k in FIELDS} for r in records];assert len(records)==240
    assert {r['clause'] for r in records}=={'C%02d'%i for i in range(1,30)}
    allorders=list(itertools.permutations(FIELDS));full=[];inverse_checks=0
    for writer in s['writers']:
        for order in allorders:
            b=build(records,writer,order);assert inverse(b['atoms'],writer,order)==expected;inverse_checks+=1
        b=build(records,writer,FIELDS);code={}
        for typ in sorted(set(b['types'].values())):
            for i,a in enumerate(sorted(a for a,t in b['types'].items() if t==typ)):code[a]=chr(97+i//26)+chr(97+i%26)
        pieces=[];start=0
        for end in b['record_ends']:pieces.append(''.join(code[a] for a in b['atoms'][start:end]));start=end
        for count in (1,2):
            words=[''.join(pieces[i:i+count]) for i in range(0,len(pieces),count)]
            got,owners=decode(words,writer,FIELDS,code);assert got==expected and sum(map(len,owners))==240
            a=solve(b['atoms'],words,b['types'],pinned=code,record_ends=b['record_ends'],seconds=10)
            z=replay(b['atoms'],words,b['types'],pinned=code,record_ends=b['record_ends'],seconds=10)
            assert a['status']=='SAT' and a['exhaustive'] and a['codes']==[code],a
            assert z['status']=='SAT_REPLAY' and z['exhaustive'] and z['codes']==[code],z
            for cut in (1,2):
                bad=[words[0][:cut],words[0][cut:],*words[1:]]
                assert solve(b['atoms'],bad,b['types'],pinned=code,record_ends=b['record_ends'],seconds=10)['status']=='UNSAT_FINITE'
                assert replay(b['atoms'],bad,b['types'],pinned=code,record_ends=b['record_ends'],seconds=10)['status']=='UNSAT_REPLAY'
                try:decode(bad,writer,FIELDS,code)
                except AssertionError:pass
                else:raise AssertionError('bad word seam accepted')
            full.append(dict(writer=writer,records_per_word=count,pinned_full_roundtrip='PASS',broken_atom_and_record_seams='REJECTED'))
    # Small pinned equations versus the actual code-string inverse.
    fixtures=0
    toy=[dict(zip(FIELDS,x)) for x in [('x','x','y','x','y'),('x','x','y','y','x')]]
    for writer in s['writers']:
        b=build(toy,writer,FIELDS);atoms=b['atoms'];types=b['types'];keys=sorted(types)
        for vals in itertools.product(('a','b','aa','ab'),repeat=len(keys)):
            code=dict(zip(keys,vals))
            if any(types[a]==types[c] and (code[a].startswith(code[c]) or code[c].startswith(code[a])) for a,c in itertools.combinations(keys,2)):continue
            text=''.join(code[a] for a in atoms)
            end=sum(len(code[a]) for a in atoms[:b['record_ends'][0]])
            words=[text[:end],text[end:]]
            for cut in (end,max(1,end-1)):
                ws=[text[:cut],text[cut:]]
                a=solve(atoms,ws,types,pinned=code,record_ends=b['record_ends'])
                z=replay(atoms,ws,types,pinned=code,record_ends=b['record_ends'])
                try:got,_=decode(ws,writer,FIELDS,code);okay=got==toy
                except AssertionError:okay=False
                assert (a['status']=='SAT')==(z['status']=='SAT_REPLAY')==okay
                fixtures+=1
    # Namespace overlap is permitted; word seams, not disjoint alphabets, resolve it.
    bounds=0
    for D in (1,2,3,5,26):
        for n in range(1,9):
            fs={'VALUE':{str(i):i%3+1 for i in range(n)}}
            a=prefix_bound(fs,D);b=capacity(fs,D)
            assert a['possible']==(b is not None)
            if a['possible']:assert a['minimum_characters']==b
            bounds+=1
    # Exhaustive unpinned solver sets versus a direct two-variable code oracle.
    exhaustive_checks=0
    for text in map(''.join,itertools.product('ab',repeat=4)):
        for cut in (0,1,2,3):
            words=[text] if cut==0 else [text[:cut],text[cut:]]
            pieces={w[i:j] for w in words for i in range(len(w)) for j in range(i+1,len(w)+1)}
            for types in ({'A':'VALUE','B':'VALUE'},{'A':'MASK','B':'VALUE'}):
                expected_codes=[]
                for va,vb in itertools.product(pieces,repeat=2):
                    if types['A']==types['B'] and (va.startswith(vb) or vb.startswith(va)):continue
                    one=va+vb
                    if words==[one+one] or words==[one,one]:expected_codes.append({'A':va,'B':vb})
                a=solve(['A','B','A','B'],words,types,record_ends=[2,4],max_solutions=100)
                z=replay(['A','B','A','B'],words,types,record_ends=[2,4],max_solutions=100)
                encode=lambda cs:{json.dumps(c,sort_keys=True) for c in cs}
                assert a['exhaustive'] and z['exhaustive']
                assert encode(a.get('codes',[]))==encode(z['codes'])==encode(expected_codes)
                exhaustive_checks+=1
    kraft_checks=0
    for D in (2,3):
        for n in range(1,6):
            weights=[i%3+1 for i in range(n)]
            best=min(sum(w*l for w,l in zip(weights,lengths)) for lengths in itertools.product(range(1,max(2,n)),repeat=n) if sum(D**(-l) for l in lengths)<=1+1e-12)
            assert prefix_bound({'V':dict(enumerate(weights))},D)['minimum_characters']==best;kraft_checks+=1
    packchecks=0
    for minima in itertools.product((1,2,3),repeat=4):
        for lengths in itertools.product((1,3,5),repeat=3):
            brute=any(sum(counts)==4 and all(sum(minima[sum(counts[:i]):sum(counts[:i+1])])<=lengths[i] for i in range(3)) for counts in itertools.product((1,2),repeat=3))
            assert packing(minima,lengths)[0]==pack(minima,lengths)==brute;packchecks+=1
    out=dict(status='PASS',source_records=len(records),field_order_inverses=inverse_checks,full_source=full,small_seam_fixtures=fixtures,exhaustive_code_oracles=exhaustive_checks,kraft_bruteforce_checks=kraft_checks,prefix_capacity_crosschecks=bounds,packing_bruteforce_checks=packchecks,target_read=False,meaning_confirmation=False,profiles={w:profile(records,w) for w in s['writers']})
    (E/'artifacts/PREFLIGHT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='profiles'},indent=2))
if __name__=='__main__':main()
