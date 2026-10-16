#!/usr/bin/env python3
"""Independent freely-UD cube obstruction and unchanged-source verification."""
import argparse
from collections import Counter,defaultdict
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'


def read(path):
    raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n')


def parse(raw,signs):
    ways=[[] for _ in range(len(raw)+1)];ways[0]=[()]
    for i in range(len(raw)):
        for sign in signs:
            if ways[i] and raw.startswith(sign,i):
                j=i+len(sign);ways[j]=(ways[j]+[p+(sign,) for p in ways[i]])[:2]
    assert len(ways[-1])==1 and ways[-1][0]
    return list(ways[-1][0])


def collapse(word):return [unit for i,unit in enumerate(word) if i==0 or unit not in ('e','i') or word[i-1]!=unit]


def pattern(word):
    first=[next(j for j in range(i+1) if word[j]==word[i]) for i in range(len(word))]
    representatives=sorted(set(first))
    return tuple(representatives.index(j) for j in first)


def is_cube(word):
    return len(word)>=6 and len(word)%3==0 and word[:len(word)//3]*3==word


def is_ud(codes):
    C=set(codes);assert C and '' not in C
    residual={b[len(a):] for a in C for b in C if a!=b and b.startswith(a)}
    seen=set()
    while residual:
        if '' in residual or residual&C:return False
        signature=frozenset(residual)
        if signature in seen:return True
        seen.add(signature)
        following=set()
        for u in residual:
            for c in C:
                if c.startswith(u):following.add(c[len(u):])
                if u.startswith(c):following.add(u[len(c):])
        residual=following
    return True


def parses(word,codes):
    paths=[[] for _ in range(len(word)+1)];paths[0]=[()]
    for i in range(len(word)):
        for code in codes:
            if paths[i] and word.startswith(code,i):
                paths[i+len(code)].extend(path+(code,) for path in paths[i])
    return paths[-1]


def controls():
    codes={'d','y','a','ab','bba'}
    assert is_ud(codes)
    assert any(a!=b and b.startswith(a) for a in codes for b in codes)
    assert any(a!=b and b.endswith(a) for a in codes for b in codes)
    assert parses('dydydy',codes)==[('d','y','d','y','d','y')]
    assert not is_ud({'d','y','dy'})
    assert len(parses('dydydy',{'d','y','dy'}))>1
    blocks=[''.join(chars) for n in range(1,4) for chars in itertools.product('ab',repeat=n)]
    checked=0
    for U in blocks:
        for V in blocks:
            text=(U+V)*3
            assert is_cube(text) and is_cube(text[::-1]);checked+=1
    assert is_cube('aaaaaa') and is_cube('דידידי')
    assert not is_cube('aaa') and not is_cube('xabababx') and not is_cube('abababx')
    assert is_cube('AbAbAb') and not is_cube('AbAbab')
    # A fixed null expansion on another code cannot alter the six d/y tokens.
    expansion={'d':'a','y':'a','a':'','ab':'b','bba':''}
    assert ''.join(expansion[c] for c in parses('dydydy',codes)[0])=='aaaaaa'
    # Without the d/y standalone premises a null could invalidate the block-size claim.
    assert not is_cube((''+'a')*3)
    # Mixed character code: a two-unit nonlogogram containing >=2 letters must use2singletons.
    for lengths in itertools.product((1,2,3),repeat=2):
        if sum(lengths)==2:assert lengths==(1,1)
    for word in ['ababab','aaaaaa','AbAbAb','דידידי','xabababx']:
        p=pattern(word)
        structural=len(p)>=6 and len(p)%3==0 and p[:len(p)//3]*3==p
        assert structural==is_cube(word)
    assert collapse(list('dydydy'))==list('dydydy')
    return {'status':'PASS_SOURCE_FREE_CONTROLS','nonempty_U_V_pairs':checked,
            'UD_neither_prefix_nor_suffix_fixture':True,'noninjective_and_null_other_expansions':True,
            'wholeword_not_substring':True,'minimum_block_length2':True,
            'outside_wordbook_Hebrew_control_not_added_to_W':True,'native_access':False}


def actual_sources(spec):
    recipe=read(ROOT/spec['recipe_path']);deot=read(ROOT/spec['deot_path']);other=read(ROOT/spec['other_path'])
    words={name:[word for record in recipe[name] for word in record['words']] for name in ('b4','w1','bs1','gr1')}
    words['deot']=[word for section in deot['source_sections'] for word in section['words']]
    for name in ('OLD_ITALIAN_UD_CONTROL','LATIN_PROIEL_CONTROL','ANCIENT_GREEK_PROIEL_CONTROL'):
        words[name]=[entry['unit'] for entry in other[name]['PRIMARY']['units']]
        assert len(words[name])==8000
    assert set(words)==set(spec['source_names'])
    assert all(isinstance(word,str) and word for tokens in words.values() for word in tokens)
    return words


def actual_families(spec):
    rows=read(ROOT/spec['native_path']);families={}
    for reader in spec['readers']:
        byform=defaultdict(list)
        for row in rows[reader]:
            assert row['edition']==reader and row['kind']=='P'
            assert not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v')
            assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
            units=parse(row['ivtff_group_raw'],spec['signs']);assert units==row['units']
            byform[row['ivtff_group_raw']].append(row)
        out=[]
        for form,occurrences in sorted(byform.items()):
            units=parse(form,spec['signs'])
            out.append({'form':form,'units':units,'collapsed_units':collapse(units),
                        'count':len(occurrences),'leaves':sorted({re.match(r'f\d+',row['page']).group() for row in occurrences}),
                        'ids':sorted(row['id'] for row in occurrences)})
        families[reader]=out
    assert read(ROOT/spec['families_path'])=={'readers':families}
    return families


def validate():
    lockpath=E/'LOCK.json';lock=read(lockpath)
    pins=lock['files'] if isinstance(lock['files'],dict) else {entry['path']:entry['sha256'] for entry in lock['files']}
    for path in (E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'METHOD.md'):
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    spec=read(E/'src/SPEC.json')
    for entry in spec['inputs']:assert pins[entry['path']]==entry['sha256']==sha(ROOT/entry['path'])
    assert spec['experiment_id']=='GDT1406' and spec['readers']==['IT2a','RF1b','ZL3b']
    assert spec['panels']==['FULL','LEAF2'] and spec['models']==['PURE','MIXED']
    assert spec['forms']==['d','y','dy','yd','dydydy'] and spec['minimum_cube_block_codepoints']==2
    actual=actual_sources(spec);inherited=read(ROOT/spec['source_envelope_path'])['sources'];source={}
    assert set(actual)==set(inherited)
    for name in spec['source_names']:
        words=actual[name];W=sorted(set(words));old=inherited[name]
        assert old['tokens']==len(words) and old['word_types']==len(W)
        assert old['wordbook_sha256']==hashlib.sha256('\n'.join(W).encode('utf-8')).hexdigest()
        assert old['source_alphabet_size']==len(set(''.join(words)))
        found={}
        # Direct equality of three actual codepoint blocks, not a scan of pattern keys.
        for word in W:
            if not is_cube(word):continue
            pat=pattern(word);key='.'.join(map(str,pat))
            found.setdefault(key,{'pattern_key':key,'word':word,'block':word[:len(word)//3],
                                  'block_codepoints':len(word)//3})
        old_cube_patterns={key for key,cert in old['modes']['FWD'].items()
                           if len(cert['pattern'])>=6 and len(cert['pattern'])%3==0
                           and cert['pattern'][:len(cert['pattern'])//3]*3==cert['pattern']}
        assert set(found)==old_cube_patterns
        for key,item in found.items():
            representative=old['modes']['FWD'][key]
            assert representative['direction']=='FWD' and representative['word']==item['word']
            assert representative['word'] in W and is_cube(representative['word'])
            assert representative['pattern']==list(pattern(item['word']))
        source[name]={'word_types':len(W),'cube_pattern_count':len(found),
                      'cubes':[found[key] for key in sorted(found)],
                      'status':'NO_WHOLE_WORD_CUBE' if not found else 'CUBE_CAPACITY_ONLY'}
    assert read(A/'SOURCE_CUBES.json')=={'sources':source}
    families=actual_families(spec);cases=[]
    for reader in spec['readers']:
        for panel in spec['panels']:
            selected=[row for row in families[reader] if panel=='FULL' or len(row['leaves'])>=2]
            lookup={row['form']:row for row in selected};witnesses={}
            for form in spec['forms']:
                units=parse(form,spec['signs']);base=collapse(units)
                assert units==list(form) and base==units
                row=lookup.get(form)
                witnesses[form]={'present':row is not None,'count':row['count'] if row else 0,
                                  'leaves':row['leaves'] if row else [],'ids':row['ids'] if row else [],
                                  'units':units,'base_units':base}
            missing_pure=[form for form in ('d','y','dydydy') if not witnesses[form]['present']]
            mixed_forcing=[form for form in ('dy','yd') if witnesses[form]['present']]
            missing_mixed=[] if witnesses['dydydy']['present'] else ['dydydy']
            if not mixed_forcing:missing_mixed.append('dy_or_yd')
            models={}
            for model,missing,forcing in [('PURE',missing_pure,['d','y']),('MIXED',missing_mixed,mixed_forcing)]:
                ready=not missing
                models[model]={'ready':ready,'missing':missing,'forcing_forms':forcing,
                               'source_decisions':{name:'NO_NATIVE_BRIDGE' if not ready else 'EXCLUDED_FIXED_W_CONJUNCTION' if source[name]['cube_pattern_count']==0 else 'CUBE_CAPACITY_ONLY' for name in spec['source_names']}}
            cases.append({'reader':reader,'panel':panel,'groups':sum(row['count'] for row in selected),
                          'raw_types':len(selected),'witnesses':witnesses,'models':models})
    expected={'experiment_id':'GDT1406','status':'COMPLETE_UD_CUBE_NECESSARY_SCREEN','cases':cases,'claim_ceiling':spec['claim_ceiling']}
    assert read(A/'RESULT.json')==expected
    receipt={'experiment_id':'GDT1406','status':'PASS_INDEPENDENT_VALIDATION',
             'scientific_status':'COMPLETE_UD_CUBE_NECESSARY_SCREEN',
             'sources':{name:{'word_types':data['word_types'],'cube_pattern_count':data['cube_pattern_count']} for name,data in source.items()},
             'native_cases':[{'reader':case['reader'],'panel':case['panel'],'models':case['models']} for case in cases],
             'source_free_controls':controls(),
             'implementation':'Direct full-word codepoint cube checks on all eight actual unchanged W; independent positional patterns; raw1233segmentation/physical-leaf counts reconstructed and compared to1405FAMILIES. No primary import.',
             'proof_scope':['PURE uses fixed nonempty WRITTEN freelyUD codes. The d/y wholeword premises force positive expansions U,V, but other entries may be null and values may be noninjective.',
                            'MIXED uses a distinct mandatory one-character-sourceword singleton-logogram rule. A whole dy/yd forces two singleton CHARACTERcodes; native d/y logograms are not treated as letter seeds.',
                            'Both tests grant the generous whole-cube envelope with any blocklength>=2, including nonprimitive blocks and U=V. No stricter mixed predicate is introduced.',
                            'The Hebrew cube control is not added to any source W and is not a Voynich meaning.'],
             'pins':{'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(lockpath),
                     'result_sha256':sha(A/'RESULT.json'),'source_cubes_sha256':sha(A/'SOURCE_CUBES.json'),
                     'old_families_sha256':sha(ROOT/spec['families_path']),
                     'old_source_envelopes_sha256':sha(ROOT/spec['source_envelope_path'])},
             'limits':['No code inventory or length limit is imposed, but fixed entries, freeUD, complete word alignment and hypothetical run inversion remain premises.',
                       'Missing native premises stay NO_NATIVE_BRIDGE; a source cube would be necessary capacity only.',
                       'Finite wordbook absence never excludes a language; source codepoints/tokenization are unchanged.',
                       'No source key, letter identity, English word meaning, decoder or additional witness search.']}
    assert not (A/'VALIDATION.json').exists();save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'source_cube_pattern_counts':{name:data['cube_pattern_count'] for name,data in source.items()},'native_ready':{c['reader']+'_'+c['panel']:{m:v['ready'] for m,v in c['models'].items()} for c in cases}},sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--controls',action='store_true');args=parser.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
