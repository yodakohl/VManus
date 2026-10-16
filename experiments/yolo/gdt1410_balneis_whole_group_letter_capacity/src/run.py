#!/usr/bin/env python3
"""Necessary fixed whole-group character support in literal source windows."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'


def read(path):return json.loads(path.read_text())
def save(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def pairs(groups):
    first={};constraints=[]
    for index,group in enumerate(groups):
        if group in first:constraints.append([first[group],index])
        else:first[group]=index
    return constraints


def windows(text,width,constraints):
    count=max(0,len(text)-width+1)
    alive=np.ones(count,dtype=bool)
    values=np.array([ord(c) for c in text],dtype=np.uint32)
    survivors=[count];removed=[]
    for left,right in constraints:
        equal=values[left:left+count]==values[right:right+count]
        alive &= equal
        survivors.append(int(alive.sum()));removed.append(survivors[-2]-survivors[-1])
    return [int(i) for i in np.flatnonzero(alive)],survivors,removed


def patterns(length):
    def build(prefix):
        if len(prefix)==length:yield tuple(prefix);return
        for value in range(max(prefix,default=-1)+2):yield from build(prefix+[value])
    yield from build([])


def oracle(text,groups):
    alphabet=tuple(sorted(set(text)))
    keys=tuple(sorted(set(groups)));found=set()
    for outputs in itertools.product(alphabet,repeat=len(keys)):
        mapping=dict(zip(keys,outputs));decoded=''.join(mapping[g] for g in groups)
        for start in range(max(0,len(text)-len(groups)+1)):
            if text[start:start+len(groups)]==decoded:found.add(start)
    return sorted(found)


def controls():
    checked=0
    for length in range(1,5):
        for group_pattern in patterns(length):
            for source_length in range(8):
                for chars in itertools.product('ab',repeat=source_length):
                    text=''.join(chars)
                    starts,counts,rejections=windows(text,length,pairs(group_pattern))
                    assert starts==oracle(text,group_pattern)
                    assert counts[-1]==len(starts) and sum(rejections)==counts[0]-len(starts)
                    checked+=1
    assert windows('aaa',3,[[0,2]])[0]==[0]
    assert not windows('abc',3,[[0,2]])[0]
    assert not windows('ab',3,[[0,2]])[0]
    assert windows('aab',3,[[0,1]])[0]==[0]
    assert not windows('aab',3,[[2,1]])[0]
    receipt={'status':'PASS_SOURCE_FREE_CONTROLS','exhaustive_pattern_source_pairs':checked,
             'oracle':'Enumerate all fixed maps from pattern classes to source alphabet, with collisions permitted.',
             'samegroup_only_not_injective':True,'whole_reverse_checked':True,'too_short_checked':True,
             'native_source_access':False}
    save(A/'CONTROLS.json',receipt);return receipt


def run():
    assert read(A/'CONTROLS.json')['status']=='PASS_SOURCE_FREE_CONTROLS'
    lock=read(E/'LOCK.json')
    for name,digest in lock['files'].items():assert sha(ROOT/name)==digest,name
    spec=read(E/'src/SPEC.json')
    assert spec['directions']==['FWD','REVERSE'] and spec['required_native_groups']==77
    projections=read(ROOT/spec['projections_path'])
    for pin in (projections['source_pin'],projections['record_pin']):
        assert sha(ROOT/pin['path'])==pin['sha256']
    assert len(projections['projections'])==70
    native=read(ROOT/spec['native_path'])['original_source']
    worksheet=read(ROOT/spec['worksheet_path'])['source_original_wrapper']['source_unit']
    assert native==worksheet and native['edition']==spec['required_native_edition']
    assert [line['metadata']['locus'] for line in native['lines']]==spec['required_loci']
    rows=[row for line in native['lines'] for row in line['groups']]
    assert len(rows)==77 and native['group_columns'][2]=='ivtff_group_raw'
    groups=[row[2] for row in rows];constraints=pairs(groups);width=len(groups)
    assert len(constraints)==len(groups)-len(set(groups))
    cases=[]
    for projection in projections['projections']:
        text=projection['text'];origins=projection['source_offsets']
        assert len(text)==len(origins)==projection['characters']
        for direction in spec['directions']:
            comparisons=constraints if direction=='FWD' else [[width-1-a,width-1-b] for a,b in constraints]
            starts,counts,rejections=windows(text,width,comparisons)
            witnesses=[{'start':i,'end':i+width,'text':text[i:i+width],
                        'source_start_offset':origins[i],'source_last_offset':origins[i+width-1]}
                       for i in starts[:spec['witness_limit_per_case']]]
            cases.append({'projection_id':projection['id'],'direction':direction,'characters':len(text),
                          'candidate_windows':max(0,len(text)-width+1),'matches':len(starts),
                          'survivor_counts':counts,'first_rejections':rejections,'witnesses':witnesses,
                          'decision':'EQUALITY_CAPACITY_ONLY' if starts else 'NO_FIXED_GROUP_LETTER_WINDOW'})
    result={'experiment_id':'GDT1410','status':'COMPLETE_FIXED_SOURCE_EQUALITY_CAPACITY',
            'native_group_count':width,'distinct_native_forms':len(set(groups)),
            'equality_constraints':constraints,'cases':cases,'word_meanings_assigned':0,
            'claim_ceiling':spec['claim_ceiling']}
    save(A/'RESULT.json',result)
    print(json.dumps({'status':result['status'],'cases':len(cases),'surviving_cases':sum(c['matches']>0 for c in cases),
                      'matches':sum(c['matches'] for c in cases),'groups':width,'constraints':len(constraints)}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--controls',action='store_true');args=parser.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:run()
