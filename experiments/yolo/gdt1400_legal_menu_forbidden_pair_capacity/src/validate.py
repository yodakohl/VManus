#!/usr/bin/env python3
"""Independent forbidden-block graph capacity verification; no solver/runner import."""
import argparse
from collections import Counter,defaultdict
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import re

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def parse(raw,signs):
    result=[[] for _ in range(len(raw)+1)];result[0]=[()]
    for i in range(len(raw)):
        for sign in signs:
            if result[i] and raw.startswith(sign,i):
                j=i+len(sign);result[j]=(result[j]+[p+(sign,) for p in result[i]])[:2]
    assert len(result[-1])==1 and result[-1][0]
    return tuple(result[-1][0])


def successors(state):
    out=[]
    for source in range(5):
        if state[source]:
            for dest in range(5):
                if source!=dest:
                    new=list(state);new[source]-=1;new[dest]+=1;out.append(tuple(new))
    return out+[state,(state[-1],)+state[:-1]]


def zero_predecessors(vertices,edges,B):
    return sorted(v for v in vertices if all((v,b) not in edges for b in B))


def extension_count(vertices,edges,B):
    Z=zero_predecessors(vertices,edges,B)
    return math.comb(len(Z)-2,2) if set(B)<=set(Z) and len(Z)>=4 else 0


def controls():
    states=firsts=second_checks=0
    for a in range(6):
        for b in range(6-a):
            for c in range(6-a-b):
                for d in range(6-a-b-c):
                    state=(a,b,c,d,5-a-b-c-d);states+=1
                    legal=successors(state)
                    assert len(legal)==4*sum(v>0 for v in state)+2
                    for rank in (16,17,18,19):
                        if rank>=len(legal):continue
                        nxt=legal[rank];firsts+=1
                        assert sum(v>0 for v in nxt)==4
                        for following in (18,19):
                            assert following>=len(successors(nxt));second_checks+=1
    assert states==126
    graph_checks=0
    for n in (4,5,6):
        vertices=list(range(n));all_edges=set(itertools.product(vertices,repeat=2))
        graphs=[set(),all_edges,{(v,v) for v in vertices},{(v,(v+1)%n) for v in vertices}]
        graphs.extend([{edge} for edge in sorted(all_edges)[:8]])
        graphs.append({(v,b) for v in vertices[4:] for b in vertices[:2]})
        for edges in graphs:
            for B in itertools.combinations(vertices,2):
                exact=sum(set(B)<=set(C) and not any((a,b) in edges for a in C for b in B)
                          for C in itertools.combinations(vertices,4))
                assert extension_count(vertices,edges,B)==exact;graph_checks+=1
    assert parse('qocheey',['q','o','ch','e','y'])==('q','o','ch','e','e','y')
    return {'status':'PASS_SOURCE_FREE_CONTROLS','states_checked':states,
            'legal_first_block_transitions':firsts,'forbidden_second_rank_checks':second_checks,
            'exhaustive_A_subset_graph_checks':graph_checks,'selfloops_absent_units_exact_four_Z_checked':True,
            'native_access':False}


def derive(reader,panel,rows,signs):
    leaves=defaultdict(set)
    for row in rows:
        leaves[row['ivtff_group_raw']].add(int(re.fullmatch(r'f(\d+)[rv].*',row['page']).group(1)))
    chosen=rows if panel=='FULL' else [row for row in rows if len(leaves[row['ivtff_group_raw']])>=2]
    counts=Counter();witnesses={}
    for row in chosen:
        units=parse(row['ivtff_group_raw'],signs)
        assert list(units)==row['units']
        for position in range(len(units)-1):
            pair=(units[position],units[position+1]);counts[pair]+=1
            witness={'id':row['id'],'position':position,'raw':row['ivtff_group_raw'],
                     'source_group_index':row['source_group_index']}
            old=witnesses.get(pair)
            if old is None or (witness['id'],position)<(old['id'],old['position']):witnesses[pair]=witness
    edges=[{'from':pair[0],'to':pair[1],'count':count,'witness':witnesses[pair]} for pair,count in sorted(counts.items())]
    adjacency=set(counts);cards=[]
    for B in itertools.combinations(sorted(signs),2):
        Z=zero_predecessors(signs,adjacency,B)
        possible=set(B)<=set(Z) and len(Z)>=4
        cards.append({'B':list(B),'Z':Z,'compatible':possible,
                      'A_extensions':math.comb(len(Z)-2,2) if possible else 0})
    assert len(cards)==231
    compatible=sum(card['compatible'] for card in cards)
    case={'reader':reader,'panel':panel,'groups':len(chosen),
          'types':len({row['ivtff_group_raw'] for row in chosen}),
          'adjacent_slots':sum(counts.values()),'distinct_edges':len(edges),
          'B_sets_tested':231,'surviving_B_sets':compatible,
          'admissible_A_B_patterns':sum(card['A_extensions'] for card in cards),
          'status':'ALL_KEYS_EXCLUDED_BY_LOCAL_BLOCK' if compatible==0 else 'LOCAL_BLOCK_CAPACITY_NOT_EXCLUDED'}
    return case,{'edges':edges,'cards':cards}


def validate():
    lockpath=E/'LOCK.json';lock=read(lockpath)
    pins=lock['files'] if isinstance(lock['files'],dict) else {p['path']:p['sha256'] for p in lock['files']}
    for path in (E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'METHOD.md'):
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    spec=read(E/'src/SPEC.json')
    assert spec['experiment']=='GDT1400' and spec['readers']==['IT2a','RF1b','ZL3b']
    assert spec['panels']==['FULL','GE2'] and len(spec['signs'])==len(set(spec['signs']))==22
    assert spec['rank_A']==[16,17,18,19] and spec['rank_B']==[18,19]
    for key in ('source','plan','proposal'):assert pins[spec[key]]==sha(ROOT/spec[key])
    cache=read(ROOT/spec['source']);cases={};evidence={}
    for reader in spec['readers']:
        rows=cache[reader];assert len({row['id'] for row in rows})==len(rows)
        for row in rows:
            assert row['edition']==reader and row['kind']=='P'
            assert not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v')
            assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
            assert type(row['source_group_index']) is str and int(row['source_group_index'])>=1
            assert list(parse(row['ivtff_group_raw'],spec['signs']))==row['units']
        for panel in spec['panels']:
            key=reader+'_'+panel
            cases[key],evidence[key]=derive(reader,panel,rows,spec['signs'])
    status='ALL_FULL_READERS_EXCLUDED' if all(cases[r+'_FULL']['surviving_B_sets']==0 for r in spec['readers']) else 'LOCAL_CAPACITY_REMAINS'
    expected={'experiment':'GDT1400','cases':cases,'status':status}
    assert read(A/'RESULT.json')==expected
    evidence_path=A/'EVIDENCE.json.gz'
    assert read(evidence_path)==evidence
    assert evidence_path.read_bytes()[4:8]==b'\x00\x00\x00\x00'
    receipt={'experiment':'GDT1400','status':'PASS_INDEPENDENT_VALIDATION','scientific_status':status,
             'cases':cases,'source_free_controls':controls(),
             'implementation':'Independent raw working-unit segmentation, physical-leaf filtering, positional edge census and exactB/Z/A extension enumeration; no primary import.',
             'pins':{'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(lockpath),
                     'result_sha256':sha(A/'RESULT.json'),'evidence_sha256':sha(evidence_path),
                     'source_sha256':sha(ROOT/spec['source'])},
             'limits':['All-state necessary forbidden-block capacity only; surviving placements are not complete keys or legal source traces.',
                       'Within-group adjacency only; no cross-word or line edge was added.',
                       'GE2 is repeated physical-leaf support, not independent confirmation or permission to drop FULL countercases.',
                       'GDT1399 computational stop and its absent native test remain unchanged.',
                       'The fixed22-unit atomization, global rank bijection and no reset inside a group remain premises.']}
    assert not (A/'VALIDATION.json').exists()
    save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'scientific_status':status,
                      'surviving_B_sets':{name:case['surviving_B_sets'] for name,case in cases.items()}},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');args=p.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
