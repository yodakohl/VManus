#!/usr/bin/env python3
"""Independent inherited-run reconstruction and exact fixed-vocabulary bound."""
import argparse
import collections
import csv
import hashlib
import itertools
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
ART=EXP/'artifacts'

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def wordhash(words): return hashlib.sha256(('\n'.join(sorted(words))+('\n' if words else '')).encode()).hexdigest()
def parse(word,signs):
    ways=[[] for _ in range(len(word)+1)]; ways[0]=[[]]
    for i in range(len(word)):
        for s in signs:
            if word.startswith(s,i):
                for old in ways[i]:
                    if len(ways[i+len(s)])<2: ways[i+len(s)].append(old+[s])
    return ways[-1][0] if len(ways[-1])==1 else None

def runs(rows):
    out=[]; chunks=[]; block=[]
    for row in rows:
        good=re.fullmatch('[a-z]+',row['ivtff_group_raw']) is not None
        linked=bool(block) and block[-1]['ivtff_group_raw']==row['ivtff_group_raw'] and block[-1]['right_separator']==row['left_separator']=='DEFINITE_SPACE'
        if not linked and block:
            chunks.append(block); block=[]
        if good: block.append(row)
    if block: chunks.append(block)
    for chunk in chunks:
        if len(chunk)>=3:
            first=chunk[0]
            old={'edition':first['edition'],'locus':first['locus'],'start':int(first['source_group_index']),'word':first['ivtff_group_raw'],'length':len(chunk)}
            out.append((old,chunk))
    return out

def longest(word,letter):
    best=current=0
    for c in word:
        current=current+1 if c==letter else 0
        best=max(best,current)
    return best

def controls():
    count=0
    for h,b,previous,r in itertools.product(range(7),range(7),range(7),range(3,7)):
        states=[previous]+[h]*r
        outputs=[(states[i+1]-states[i]+b)%7 for i in range(r)]
        assert outputs[1:]==[b]*(r-1)
        count+=1
    # Reset or contextual states violate the stipulated invariant, not its proof.
    assert [(4-0+2)%7]*3 != [(4-0+2)%7,2,2]
    assert [(x-y+2)%7 for x,y in zip([1,3,6],[0,1,3])][1:] != [2,2]
    for words in itertools.product(['a','aa','aba','bbb'],repeat=3):
        text=' '.join(words)
        assert '  ' not in text
        for c in 'ab': assert longest(text,c)==max(longest(w,c) for w in words)
        count+=1
    assert '  ' in 'a  b'  # Outside canonical source grammar.
    assert ''.join(['b','','b']) != 'bbb'  # Erasure destroys r-to-r output premise.
    assert parse('chch',['c','h','ch']) is None
    assert parse('chch',['ch','a'])==['ch','ch']
    return {'status':'PASS','algebra_and_word_join_checks':count,'negative_contract_checks':4,'parser_checks':2}

def validate():
    lock=read(EXP/'LOCK.json')
    for p,h in lock['files'].items():
        assert not Path(p).is_absolute() and sha(ROOT/p)==h,p
    for p in [Path(__file__),EXP/'src/run.py',EXP/'src/SPEC.json',EXP/'reproduce.py']:
        assert p.relative_to(ROOT).as_posix() in lock['files']
    spec=read(EXP/'src/SPEC.json')
    guard=read(ROOT/spec['native_guard_path'])
    oldspec=read(ROOT/spec['native_spec_path'])
    cache=ROOT/spec['native_cache_path']
    assert sha(cache)==guard['sha256']
    by=collections.defaultdict(list)
    with cache.open(encoding='utf-8',newline='') as stream:
        for row in csv.DictReader(stream,delimiter='\t'):
            assert row['page'] in oldspec['allowed'] and not row['page'].startswith('f84')
            by[row['edition'],row['locus']].append(row)
    assert sum(map(len,by.values()))==guard['stats']['selected']
    allruns=[]
    for key,rows in sorted(by.items()):
        if rows[0]['kind']!='P': continue
        rows.sort(key=lambda x:int(x['source_group_index']))
        assert all(r['kind']=='P' for r in rows)
        assert len(rows)==int(rows[0]['source_group_count'])
        assert [int(r['source_group_index']) for r in rows]==list(range(1,len(rows)+1))
        allruns.extend(runs(rows))
    oldruns=read(ROOT/spec['native_runs_path'])
    assert [old for old,rows in allruns]==oldruns
    signs=read(ROOT/spec['signs_path'])['signs']
    panel={'guard_sha256':sha(ROOT/spec['native_guard_path']),'cache_sha256':sha(cache),'old_runs_sha256':sha(ROOT/spec['native_runs_path']),'readers':{}}
    for ed in spec['editions']:
        retained=[]; unparsed=[]
        for original,rows in allruns:
            if original['edition']!=ed: continue
            units=parse(original['word'],signs)
            if units is None:
                unparsed.append({'original':original,'reason':'NO_UNIQUE_22_UNIT_PARSE','source_rows':rows})
            else:
                retained.append({'original':original,'working_units':units,'source_rows':rows})
        maximum=max(x['original']['length'] for x in retained)
        panel['readers'][ed]={'retained_runs':retained,'unparsed_runs':unparsed,'max_native_run':maximum,'required_source_run':maximum-1,'maximum_run_witnesses':[x['original'] for x in retained if x['original']['length']==maximum]}
    assert read(ART/'NATIVE_PANEL.json')==panel
    manifest=read(ROOT/spec['vocabulary_pins_path'])
    old_source_pins={x['path']:x['sha256'] for x in manifest['inputs']}
    catalogs={}; vocabularies={}
    for pack in spec['source_packs']:
        path=Path(spec['source_directory'])/(pack+'.txt')
        assert sha(ROOT/path)==old_source_pins[path.as_posix()]
        text=(ROOT/path).read_text(encoding='utf-8')
        words=sorted(set(text.split()))
        assert all(re.fullmatch('[a-z]+',w) for w in words)
        assert len(words)==manifest['vocabularies'][pack]['size']
        assert wordhash(words)==manifest['vocabularies'][pack]['sha256']
        letters={}
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            maximum=max(longest(w,letter) for w in words)
            example=next((w for w in words if longest(w,letter)==maximum),None) if maximum else None
            letters[letter]={'max_run':maximum,'longest_example':example}
        catalogs[pack]={'path':path.as_posix(),'source_sha256':sha(ROOT/path),'vocabulary_size':len(words),'vocabulary_sha256':wordhash(words),'letters':letters}
        vocabularies[pack]=words
    assert read(ART/'VOCABULARY_RUNS.json')=={'packs':catalogs}
    cases=[]
    for ed in spec['editions']:
        r=panel['readers'][ed]['max_native_run']
        for pack in spec['source_packs']:
            options=[]
            for letter in spec['candidate_letters']:
                matching=[] if letter==' ' else [w for w in vocabularies[pack] if letter*(r-1) in w]
                maximum=1 if letter==' ' else catalogs[pack]['letters'][letter]['max_run']
                options.append({'character':'SPACE' if letter==' ' else letter,'max_source_run':maximum,'eligible':maximum>=r-1,'word_count':len(matching),'words_sha256':None if letter==' ' else wordhash(matching),'examples':matching[:spec['examples_per_letter']]})
            survivors=[x['character'] for x in options if x['eligible']]
            cases.append({'edition':ed,'pack':pack,'max_native_run':r,'required_source_run':r-1,'beta_options':options,'surviving_beta':survivors,'decision':'RUN_BOUND_CAPACITY_ONLY' if survivors else 'FIXED_WORDSTAR_CONSTANT_DIAGONAL_EXCLUDED'})
    expected={'experiment_id':'GDT1412','status':'COMPLETE_FIXED_WORDSTAR_REPEAT_BOUND','cases':cases,'word_meanings_assigned':0,'claim_ceiling':spec['claim_ceiling']}
    assert read(ART/'RESULT.json')==expected
    receipt={'experiment_id':'GDT1412','status':'PASS_INDEPENDENT_RECONSTRUCTION','controls':controls(),'lock_sha256':sha(EXP/'LOCK.json'),'pins':lock['files'],'outputs':{n:sha(ART/n) for n in ['NATIVE_PANEL.json','VOCABULARY_RUNS.json','RESULT.json']},'cases':len(cases),'scope':'Inherited selected native runs and fixed six ASCII word inventories only; no meanings, full-support source rejection or independent manuscript samples.'}
    target=ART/'VALIDATION.json'
    if target.exists(): assert read(target)==receipt
    else: target.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':receipt['status'],'cases':len(cases)}))
if __name__=='__main__':
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--controls',action='store_true');g.add_argument('--validate',action='store_true');a=p.parse_args()
    if a.controls: print(json.dumps(controls(),sort_keys=True))
    else: validate()
