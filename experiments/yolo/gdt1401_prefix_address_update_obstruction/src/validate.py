#!/usr/bin/env python3
"""Independent active-frontier proof fixtures and old source-line witness replay."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def parse(raw,signs):
    ways=[[] for _ in range(len(raw)+1)];ways[0]=[()]
    for i in range(len(raw)):
        for sign in signs:
            if ways[i] and raw.startswith(sign,i):
                j=i+len(sign);ways[j]=(ways[j]+[p+(sign,) for p in ways[i]])[:2]
    assert len(ways[-1])==1 and ways[-1][0]
    return list(ways[-1][0])


def frontiers(branches,depth):
    if depth==0:return [frozenset({()})]
    result=[frozenset({()})]
    below=frontiers(branches,depth-1)
    for children in itertools.product(below,repeat=branches):
        result.append(frozenset((i,)+path for i,frontier in enumerate(children) for path in frontier))
    assert len(result)==len(set(result))
    return result


def update(frontier,address,branches,depth):
    if len(address)>=depth:return None
    children=frozenset(address+(i,) for i in range(branches))
    assert children
    if address in frontier:return (frontier-{address})|children
    if children<=frontier:return (frontier-children)|{address}
    return None


def valid(frontier,branches,depth):
    if any(u!=v and len(u)<=len(v) and v[:len(u)]==u for u in frontier for v in frontier):return False
    return all(sum(leaf[:len(node)]==node for node in frontier)==1
               for leaf in itertools.product(range(branches),repeat=depth))


def controls():
    records=[]
    for branches,depth,expected in [(2,3,26),(3,2,9)]:
        states=frontiers(branches,depth);assert len(states)==expected
        nodes=[node for n in range(depth+1) for node in itertools.product(range(branches),repeat=n)]
        enabled=forbidden=0
        for frontier in states:
            assert valid(frontier,branches,depth)
            for U in nodes:
                changed=update(frontier,U,branches,depth)
                if changed is None:continue
                assert valid(changed,branches,depth);enabled+=1
                for V in nodes:
                    if len(V)>=len(U)+2 and V[:len(U)]==U:
                        assert update(changed,V,branches,depth) is None;forbidden+=1
        records.append({'branching':branches,'depth':depth,'frontiers':len(states),
                        'enabled_updates':enabled,'forbidden_descendant_checks':forbidden})
    initial=frozenset({()});state=initial
    for address in [(),(0,),(0,),()]:
        state=update(state,address,2,3);assert state is not None
    assert state==initial
    first=update(initial,(),2,3)
    assert update(first,(0,),2,3) is not None
    assert update(first,(0,0),2,3) is None
    assert update(frozenset({(0,0,0)}),(0,0,0),2,3) is None
    return {'status':'PASS_SOURCE_FREE_FRONTIER_CONTROLS','cases':records,
            'immediate_child_allowed':True,'parent_child_child_parent_undo':True,
            'empty_child_merge_forbidden':True,'native_access':False,
            'general_proof':'After split only immediate children are active below U; after merge only U is active there. A distance>=2descendant is neither active nor has active immediate children.'}


def reconstruct(spec):
    lines=read(ROOT/spec['source_lines'])
    pair_table=read(ROOT/spec['pairs'])
    cases=[]
    for reader in spec['readers']:
        for chosen in spec['witnesses']:
            locus=chosen['locus'];base=chosen['base'];extended=chosen['extended']
            relevant=[line for line in lines if line['edition']==reader and line['locus']==locus]
            assert len(relevant)==1
            line=relevant[0];assert line['page']==locus.split('.')[0]
            assert not line['page'].startswith('f84') and line['page'] not in ('f1r','f116v')
            groups=line['groups']
            assert len({group['source_group_id'] for group in groups})==len(groups)
            assert [int(group['source_group_index']) for group in groups]==list(range(1,len(groups)+1))
            for group in groups:
                assert group['edition']==reader and group['page']==line['page'] and group['locus']==locus
                if 'source_group_count' in group:assert int(group['source_group_count'])==len(groups)
            matches=[]
            for i in range(len(groups)-1):
                left,right=groups[i],groups[i+1]
                if left['ivtff_group_raw']==base and right['ivtff_group_raw']==extended:
                    matches.append((left,right))
            assert len(matches)==1
            left,right=matches[0]
            assert left['kind']==right['kind']=='P'
            assert int(right['source_group_index'])==int(left['source_group_index'])+1
            assert left['right_separator']==right['left_separator']=='DEFINITE_SPACE'
            # Exact original dictionaries survive unchanged; only arithmetic casts ordinals.
            stored=[pair for pair in pair_table[reader][base]
                    if pair['left']['locus']==locus and pair['right']['locus']==locus
                    and pair['left']['ivtff_group_raw']==base and pair['right']['ivtff_group_raw']==extended]
            assert len(stored)==1 and stored[0]['left']==left and stored[0]['right']==right
            lu,ru=parse(base,spec['signs']),parse(extended,spec['signs'])
            assert ru[:len(lu)]==lu and ru[len(lu):]==['d','y']
            cases.append({'reader':reader,'locus':locus,'base':base,'extended':extended,
                          'left':left,'right':right,'left_units':lu,'right_units':ru,
                          'extension_units':['d','y'],'minimum_path_distance':2,
                          'status':'FORBIDDEN_UNDER_DECLARED_ADDRESS_CONTRACT'})
    return cases


def validate():
    lockpath=E/'LOCK.json';lock=read(lockpath)
    pins=lock['files'] if isinstance(lock['files'],dict) else {item['path']:item['sha256'] for item in lock['files']}
    for path in (E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'METHOD.md'):
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    spec=read(E/'src/SPEC.json')
    assert spec['experiment']=='GDT1401' and spec['readers']==['ZL3b','IT2a','RF1b']
    expected=[('cho','chody','f42r.11'),('okal','okaldy','f58v.10'),('or','ordy','f39r.4'),('sheo','sheody','f88v.16')]
    assert [(w['base'],w['extended'],w['locus']) for w in spec['witnesses']]==expected
    for key in ('pairs','source_lines','old_validation','proposal','plan'):
        assert pins[spec[key]]==sha(ROOT/spec[key])
    cases=reconstruct(spec)
    result=read(A/'RESULT.json')
    assert result['experiment']=='GDT1401' and result['status']=='PREFIX_FAITHFUL_SINGLE_UPDATE_FAMILY_EXCLUDED'
    assert result['case_count']==len(cases)==12 and result['physical_sites']==4
    assert len({case['locus'] for case in cases})==4
    assert result['cases']==cases
    assert result['new_native_census'] is False and result['word_meanings_assigned']==0
    assert isinstance(result['selection'],str) and result['selection']
    receipt={'experiment':'GDT1401','status':'PASS_INDEPENDENT_VALIDATION',
             'scientific_status':'PREFIX_FAITHFUL_SINGLE_UPDATE_FAMILY_EXCLUDED',
             'original_source_line_pairs_verified':12,'physical_sites':4,
             'readers':spec['readers'],'source_free_controls':controls(),
             'implementation':'Independent complete source-line adjacency reconstruction and exact original-row comparison; dynamic22unit parsing; independently generated active-frontier controls. No primary import.',
             'general_argument':['After SPLIT(U), the only active leaves below U are its immediate children; a distance>=2descendant and its children are inactive.',
                                 'After MERGE(U), U is the active leaf and all proper descendants are inactive.',
                                 'Therefore no one-update trace contains U immediately followed by a distance>=2descendant, under the declared nonempty-child frontier rules.',
                                 'The candidate positive-step prefix law turns each existing B/Bdy pair into that forbidden address relation; it is a hypothesis, not an inferred meaning.'],
             'pins':{'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(lockpath),
                     'result_sha256':sha(A/'RESULT.json'),'old_pairs_sha256':sha(ROOT/spec['pairs']),
                     'old_source_lines_sha256':sha(ROOT/spec['source_lines'])},
             'limits':['Post-observation logical application to named old witnesses; no statistical or blind-confirmation claim.',
                       'Finite controls illustrate the general local proof and do not prove it merely by sampling.',
                       'Wholewords,22working units, same-root prefix-faithful addresses and one explicit update perword are premises.',
                       'Immediate-child moves and repeated inverse updates remain legal; arbitrary hierarchy, nonprefix names and macros are not excluded.',
                       'No native addresses, glyph values, English word meanings or translated passage assigned.']}
    assert not (A/'VALIDATION.json').exists()
    save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'scientific_status':receipt['scientific_status'],'verified_pairs':12},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');args=p.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
