#!/usr/bin/env python3
"""Independent endpoint-retaining wordbook singleton-capacity certificate."""
import argparse
from collections import Counter,defaultdict
import gzip
import hashlib
import itertools
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
A=E/'artifacts'
ALPHABET='אבגדהוזחטיכלמנסעפצקרשת'


def read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix=='.gz' else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n')


def parse(raw,signs):
    states=[[] for _ in range(len(raw)+1)];states[0]=[()]
    for start in range(len(raw)):
        for sign in signs:
            if states[start] and raw.startswith(sign,start):
                end=start+len(sign)
                states[end]=(states[end]+[p+(sign,) for p in states[start]])[:2]
    assert len(states[-1])==1
    return list(states[-1][0])


def controls():
    checked=0
    letters='abc'
    for mapped in itertools.permutations('xyz'):
        rename=dict(zip(letters,mapped))
        singleton_outputs=set()
        for n in range(1,6):
            for word in itertools.product(letters,repeat=n):
                interior=range(1,n-1)
                for bits in itertools.product((False,True),repeat=max(0,n-2)):
                    remove={i for i,bit in zip(interior,bits) if bit}
                    remaining=[ch for i,ch in enumerate(word) if i not in remove]
                    output=''.join(rename[ch] for ch in remaining)
                    assert len(output)==len(remaining)
                    assert n==1 or len(output)>=2
                    if len(output)==1:
                        assert n==1
                        singleton_outputs.add(output)
                    checked+=1
        assert singleton_outputs==set(mapped)
        assert rename['a']+rename['a']!=rename['a']
        for allowed_singletons in (set(),{'a'},{'a','b'},set(letters)):
            W=allowed_singletons|{'aa','ab','bc','cab'}
            possible={rename[word] for word in W if len(word)==1}
            assert len(possible)==len(allowed_singletons)
        # A purported one-letter logogram for 'ab' cannot be produced by the writer.
        assert len('ab')>=2 and len(rename['a']+rename['b'])==2
    return {'status':'PASS_SOURCE_FREE_CONTROLS','endpoint_deletion_bijection_cases':checked,
            'length1_length2_and_equal_endpoints_checked':True,
            'long_word_single_letter_logogram_outside_contract':True,'empirical_access':False}


def source_certificate():
    projection=read(ROOT/'experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/SOURCE_PROJECTION.json')
    assert len(ALPHABET)==len(set(ALPHABET))==22
    sections=projection['source_sections'];words=[];ones=[]
    for section in sections:
        assert isinstance(section['ref'],str)
        for index,word in enumerate(section['words']):
            assert isinstance(word,str) and word and set(word)<=set(ALPHABET)
            words.append(word)
            if len(word)==1:ones.append({'ref':section['ref'],'index':index+1,'word':word})
    W=sorted(set(words))
    return projection,words,W,ones


def native_certificate(signs,readers):
    cache=read(ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz')
    old=read(ROOT/'experiments/yolo/gdt1227_relation_path_one_sign_capacity/artifacts/RESULT.json')
    output={}
    for reader in readers:
        counts=Counter();pages=defaultdict(set);rows={}
        for group in cache[reader]:
            assert group['edition']==reader and group['kind']=='P'
            assert not group['page'].startswith('f84') and group['page'] not in ('f116v','f1r')
            assert group['left_separator']==group['right_separator']=='DEFINITE_SPACE'
            units=parse(group['ivtff_group_raw'],signs)
            assert units==group['units']
            if len(units)==1:
                unit=units[0];counts[unit]+=1;pages[unit].add(group['page']);rows[group['id']]=group
        retained=old['readings'][reader]
        assert dict(counts)==retained['counts']
        assert len(counts)==retained['types'] and sum(counts.values())==retained['tokens']
        for unit in counts:
            assert sorted(pages[unit])==retained['pages'][unit]
            witness=retained['witnesses'][unit]
            group=rows[witness['id']]
            expected={'id':group['id'],'word':group['ivtff_group_raw'],'page':group['page'],
                      'locus':group['locus'],'source_group_index':group['source_group_index'],
                      'left_separator':group['left_separator'],'right_separator':group['right_separator']}
            assert witness==expected and group['units']==[unit]
        output[reader]=retained
    return output


def validate():
    lock_path=E/'LOCK.json';lock=read(lock_path)
    pins={item['path']:item['sha256'] for item in lock['files']}
    required=[E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'PREREGISTRATION.md',E/'METHOD.md']
    for path in required:
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    spec=read(E/'src/SPEC.json')
    for item in spec['inputs']:
        assert pins[item['path']]==item['sha256']==sha(ROOT/item['path'])
    assert spec['experiment_id']=='GDT1396' and spec['readers']==['IT2a','RF1b','ZL3b']
    assert spec['common6']==['a','d','o','r','s','y']
    projection,words,W,ones=source_certificate()
    assert len(projection['source_sections'])==spec['source_expected_sections']==71
    assert len(words)==projection['tokens']==spec['source_expected_tokens']==6288
    alphabet=sorted(set(''.join(words)))
    assert len(alphabet)==spec['source_expected_alphabet']==22 and set(alphabet)==set(ALPHABET)
    groups=defaultdict(list)
    for item in ones:
        groups[item['word']].append({'ref':item['ref'],'index':item['index']})
    singletons=[{'word':word,'token_count':len(groups[word]),'occurrences':groups[word]} for word in sorted(groups)]
    source={'sections':71,'tokens':6288,'alphabet':alphabet,'wordbook_types':len(W),
            'wordbook_sha256':hashlib.sha256('\n'.join(W).encode('utf-8')).hexdigest(),
            'single_word_types':len(groups),'singletons':singletons}
    signs=read(ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/src/SPEC.json')['signs']
    retained=native_certificate(signs,spec['readers'])
    readers={}
    for reader in spec['readers']:
        counts=retained[reader]['counts']
        assert len(counts)==spec['native_expected_types'][reader]
        assert all(counts.get(sign,0)>0 for sign in spec['common6'])
        forms={'ALL':sorted(counts),'GE2':sorted(sign for sign,count in counts.items() if count>=2),'COMMON6':spec['common6']}
        tiers={tier:{'forms':values,'types':len(values),'status':'EXCLUDED' if len(values)>len(groups) else 'NOT_EXCLUDED'} for tier,values in forms.items()}
        readers[reader]={'counts':counts,'inherited_tokens':retained[reader]['tokens'],'tiers':tiers}
    excluded=[r['tiers']['ALL']['status']=='EXCLUDED' for r in readers.values()]
    status='FIXED_W_DOMAIN_EXCLUDED_ALL_READERS' if all(excluded) else 'SOME_READERS_EXCLUDED' if any(excluded) else 'NECESSARY_CAPACITY_ONLY'
    expected={'experiment_id':'GDT1396','status':status,'source':source,'readers':readers}
    assert read(A/'RESULT.json')==expected
    receipt={'experiment_id':'GDT1396','status':'PASS_INDEPENDENT_VALIDATION','scientific_status':status,
             'source_single_word_types':len(groups),'source_occurrences_verified':len(ones),
             'readers':{reader:{'singleton_types':len(retained[reader]['counts']),
                                'singleton_tokens':retained[reader]['tokens'],
                                'all_counts_pages_and_original_witnesses_verified':True} for reader in spec['readers']},
             'source_free_controls':controls(),
             'implementation':'Independent Unicode wordbook reconstruction and exact occurrence indexing; dynamic working-unit segmentation; source-free exhaustive endpoint-retaining deletions under bijections; no primary imports.',
             'pins':{'lock_sha256':sha(lock_path),'spec_sha256':sha(E/'src/SPEC.json'),
                     'validator_sha256':sha(Path(__file__)),'result_sha256':sha(A/'RESULT.json')},
             'limits':['Fixed W domain and literal endpoint retention only; no general1069exclusion.',
                       'W is a control vocabulary, not a nominated manuscript plaintext or source language.',
                       'Working units and strict group boundaries are inherited; readers are alternative transcriptions.']}
    assert not (A/'VALIDATION.json').exists()
    save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'scientific_status':status,'source_single_word_types':len(groups)},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');args=p.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
