#!/usr/bin/env python3
"""Source-free fixtures for the two-phase cube and SPACE branch classification."""
from pathlib import Path
import argparse,hashlib,itertools,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(table,word,phase):
    out=[]
    for atom in word:
        out.append(table[(atom,phase)]);phase=1-phase
    return ''.join(out)
def cube(s):return len(s)>=6 and len(s)%3==0 and s[:len(s)//3]*3==s

def result():
    # These are synthetic outputs, not native letter or word assignments.
    strings=['','a','b','ab','é','אב'];checked=0;qualified=0
    for values in itertools.product(strings,repeat=4):
        table=dict(zip([('d',0),('d',1),('y',0),('y',1)],values))
        for phase in [0,1]:
            for word in ['dydydy','ydydyd']:
                block=table[(word[0],phase)]+table[(word[1],1-phase)]
                emitted=decode(table,word,phase)
                assert emitted==block*3
                if len(block)>=2:
                    assert cube(emitted) and cube(emitted[::-1]);qualified+=1
                checked+=1
    empty_table={('d',0):'a',('d',1):'a',('y',0):'b',('y',1):''}
    assert decode(empty_table,'dydydy',0)=='aaa' and not cube('aaa')
    branches={'WHOLE_WORD_CUBE':0,'THREE_IDENTICAL_ONE_LETTER_WORDS':0,'NO_LETTERS':0}
    for values in itertools.product(['a','b',' '],repeat=4):
        table=dict(zip([('d',0),('d',1),('y',0),('y',1)],values))
        for phase in [0,1]:
            block=table[('d',phase)]+table[('y',1-phase)]
            emitted=decode(table,'dydydy',phase);words=emitted.split()
            if ' ' not in block:
                assert len(words)==1 and cube(words[0]);branch='WHOLE_WORD_CUBE'
            elif block.count(' ')==1:
                assert len(words)==3 and len(set(words))==1 and len(words[0])==1
                branch='THREE_IDENTICAL_ONE_LETTER_WORDS'
            else:
                assert not words;branch='NO_LETTERS'
            branches[branch]+=1
    # Period3/4 are outside the theorem: named witnesses really break the cube.
    p3={('d',0):'a',('y',1):'b',('d',2):'c',('y',0):'d',('d',1):'e',('y',2):'f'}
    p4={('d',0):'a',('y',1):'b',('d',2):'c',('y',3):'d'}
    def periodic(t,n):return ''.join(t[(c,i%n)] for i,c in enumerate('dydydy'))
    assert periodic(p3,3)=='abcdef' and not cube(periodic(p3,3))
    assert periodic(p4,4)=='abcdab' and not cube(periodic(p4,4))
    planpath=HERE/'PERIOD2_CUBE_COROLLARY_PLAN_20261016.json'
    plan=json.loads(planpath.read_text())
    for pin in plan['pins']:assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']
    return {'idea':'IDEA001095','status':'PASS_SOURCE_FREE_FIXTURES_NOT_NATIVE_VALIDATION','synthetic_string_cases':checked,'blocklength_ge2_cases':qualified,'space_branch_fixture_counts':branches,'null_counterexample':'aaa is outside inherited blocklength>=2 predicate','period3_counterexample':'abcdef','period4_counterexample':'abcdab','plan_sha256':sha(planpath),'space_addendum_sha256':sha(HERE/'PERIOD2_SPACE_BRANCH_ADDENDUM_PLAN_20261016.json'),'checker_sha256':sha(Path(__file__)),'prior_source_pin_checks':'PASS','new_native_or_source_count':False,'word_values_assigned':0,'proof_ceiling':'Algebra establishes arbitrary strings; finite fixtures check implementation only. Fixed8Wabsence is inherited. LegacySPACE branches remain; boundary-free direction is outside whole-word corollary.'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    data=json.dumps(result(),ensure_ascii=False,indent=2,sort_keys=True)+'\n'
    output=HERE/'PERIOD2_CUBE_COROLLARY_CONTROLS_20261016.json'
    if args.check:assert output.read_text()==data
    else:
        assert not output.exists();output.write_text(data)
    print(data)
