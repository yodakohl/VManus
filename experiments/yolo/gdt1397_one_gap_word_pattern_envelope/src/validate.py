#!/usr/bin/env python3
"""Independent one-gap necessary equality-pattern capacity verification."""
import argparse
from collections import Counter,defaultdict
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
A=E/'artifacts'


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,obj):
    path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n')


def pattern(units):
    # Position-equality classes; deliberately no symbol->label mapping table.
    first=[next(j for j in range(i+1) if units[j]==units[i]) for i in range(len(units))]
    representatives=sorted(set(first))
    return tuple(representatives.index(j) for j in first)


def variants(word):
    yield word,None
    n=len(word)
    for prefix_length in range(1,n):
        for suffix_length in range(1,n-prefix_length):
            yield word[:prefix_length]+word[n-suffix_length:],(prefix_length,n-suffix_length)


def parse(raw,signs):
    paths=[[] for _ in range(len(raw)+1)];paths[0]=[()]
    for i in range(len(raw)):
        for sign in signs:
            if paths[i] and raw.startswith(sign,i):
                j=i+len(sign);paths[j]=(paths[j]+[p+(sign,) for p in paths[i]])[:2]
    return list(paths[-1][0]) if len(paths[-1])==1 and paths[-1][0] else None


def classify(units,supported,lengths):
    if units is None:return 'UNSCORABLE'
    if len(units) not in lengths:return 'LENGTH_UNSUPPORTED'
    return 'SUPPORTED' if pattern(units) in supported else 'PATTERN_UNSUPPORTED'


def controls():
    checked=0;letters='abc'
    for n in range(1,6):
        for symbols in itertools.product(letters,repeat=n):
            word=''.join(symbols)
            got={out for out,gap in variants(word)}
            expected={word}|{word[:i]+word[j:] for i in range(1,n) for j in range(i+1,n)}
            assert got==expected
            for out,gap in variants(word):
                assert out[0]==word[0] and out[-1]==word[-1]
                if gap is not None:assert len(out)>=2 and 1<=gap[0]<gap[1]<=n-1
                for perm in itertools.permutations(letters):
                    mapped=''.join(perm[letters.index(ch)] for ch in out)
                    assert pattern(mapped)==pattern(out)
                    assert pattern(mapped[::-1])==pattern(out[::-1])
                    checked+=1
    for n in range(1,4):
        words=list(itertools.product(letters,repeat=n))
        for x in words:
            for y in words:
                can_rename=any(tuple(perm[letters.index(ch)] for ch in x)==y for perm in itertools.permutations(letters))
                assert (pattern(x)==pattern(y))==can_rename
                checked+=1
    assert set(variants('aa'))=={('aa',None)}
    assert ('aa',(1,2)) in set(variants('aba'))
    assert 'ace' not in {out for out,gap in variants('abcde')}
    assert pattern(['ch','a','ch'])==(0,1,0)
    assert parse('ckhey',['ckh','e','y'])==['ckh','e','y']
    assert parse('c',['ch','a']) is None
    return {'status':'PASS_SOURCE_FREE_CONTROLS','cases_checked':checked,
            'equality_pattern_iff_bijection_checked':True,'one_contiguous_interior_gap_checked':True,
            'literal_equal_endpoints_and_nonletter_units_checked':True,'empirical_access':False}


def envelope(words):
    modes={'FWD':{},'BIDIR':{}}
    for word in sorted(set(words)):
        for retained,gap in variants(word):
            for direction,out in [('FWD',retained),('REV',retained[::-1])]:
                pat=pattern(out)
                key=(word,(-1,-1) if gap is None else gap,0 if direction=='FWD' else 1)
                witness={'pattern':list(pat),'word':word,'gap':None if gap is None else list(gap),
                         'direction':direction,'retained':retained,'output':out}
                for mode in ('FWD','BIDIR'):
                    if mode=='FWD' and direction!='FWD':continue
                    if pat not in modes[mode] or key<modes[mode][pat][0]:modes[mode][pat]=(key,witness)
    return {mode:{'.'.join(map(str,pat)):value[1] for pat,value in table.items()} for mode,table in modes.items()}


def memberships(units,modes,length_sets):
    if units is None:return {mode:'UNPARSEABLE' for mode in modes}
    pat=pattern(units);key='.'.join(map(str,pat))
    out={}
    for mode,table in modes.items():
        lengths=length_sets[mode]
        out[mode]='LENGTH_UNSUPPORTED' if len(units) not in lengths else 'SUPPORTED' if key in table else 'PATTERN_UNSUPPORTED'
    return out


def native_projection(spec,modes):
    length_sets={mode:{len(item['pattern']) for item in table.values()} for mode,table in modes.items()}
    cache=read(ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz')
    native,results={},{}
    for reader in spec['readers']:
        grouped=defaultdict(list)
        for group in cache[reader]:
            assert group['edition']==reader and group['kind']=='P'
            assert not group['page'].startswith('f84') and group['page'] not in ('f1r','f116v')
            assert group['left_separator']==group['right_separator']=='DEFINITE_SPACE'
            units=parse(group['ivtff_group_raw'],spec['signs'])
            assert units==group['units'] and units is not None
            grouped[group['ivtff_group_raw']].append(group)
        forms=[]
        for raw,groups in sorted(grouped.items()):
            units=parse(raw,spec['signs']);pat=pattern(units)
            forms.append({'form':raw,'units':units,'pattern':list(pat),'pattern_key':'.'.join(map(str,pat)),
                          'count':len(groups),'ids':sorted(g['id'] for g in groups),
                          'pages':sorted({g['page'] for g in groups}),'status':memberships(units,modes,length_sets)})
        native[reader]=forms
        entry={'strict_groups':len(cache[reader]),'native_types':len(forms),
               'native_max_units':max(len(f['units']) for f in forms),'modes':{},'first_failures':{}}
        for mode in spec['modes']:
            tiers={}
            for tier,minimum in [('ALL',1),('GE2',2)]:
                selected=[f for f in forms if f['count']>=minimum]
                bad=[f for f in selected if f['status'][mode]!='SUPPORTED']
                tiers[tier]={'types':len(selected),'occurrences':sum(f['count'] for f in selected),
                             'unsupported_types':len(bad),'unsupported_occurrences':sum(f['count'] for f in bad),
                             'unsupported_leaves':sorted({re.match(r'f\d+',page).group() for f in bad for page in f['pages']}),
                             'length_failure_types':sum(f['status'][mode]=='LENGTH_UNSUPPORTED' for f in bad),
                             'pattern_failure_types':sum(f['status'][mode]=='PATTERN_UNSUPPORTED' for f in bad),
                             'status':'EXCLUDED' if bad else 'WORDWISE_SUPPORTED'}
            entry['modes'][mode]=tiers
            bad=sorted((f for f in forms if f['status'][mode]!='SUPPORTED'),key=lambda f:(-f['count'],f['form']))[:10]
            entry['first_failures'][mode]=[{'form':f['form'],'count':f['count'],'status':f['status'][mode],'first_id':f['ids'][0]} for f in bad]
        results[reader]=entry
    return native,results


def passage_projection(spec,modes):
    length_sets={mode:{len(item['pattern']) for item in table.values()} for mode,table in modes.items()}
    worksheet=read(ROOT/'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/LEXICAL_WORKSHEET_20261016.json')
    selected=[unit for unit in worksheet['units'] if unit['unit_id']==spec['passage_unit']]
    assert len(selected)==1 and spec['passage_unit']=='f75v_IT2a'
    lines=selected[0]['lines'];groups=[]
    assert [line['metadata']['locus'] for line in lines]==['f75v.'+str(n) for n in range(43,50)]
    assert str(lines[0]['metadata']['paragraph_start'])=='1' and str(lines[-1]['metadata']['paragraph_end'])=='1'
    for line in lines:
        metadata=line['metadata'];original=line['original_groups']
        assert metadata['edition']=='IT2a' and metadata['page']=='f75v' and metadata['kind']=='P'
        assert len(original)==int(metadata['source_group_count'])
        assert [int(row[1]) for row in original]==list(range(1,len(original)+1))
        for row in original:
            assert len(row)==5
            units=parse(row[2],spec['signs'])
            groups.append({'original':row,'page':metadata['page'],'locus':metadata['locus'],
                           'units':units,'pattern':None if units is None else list(pattern(units)),
                           'status':memberships(units,modes,length_sets)})
    assert len(groups)==spec['passage_expected_groups']==77
    badids=[g['original'][0] for g in groups if g['units'] is None]
    decisions={}
    for mode in spec['modes']:
        bad=sum(g['status'][mode] in ('LENGTH_UNSUPPORTED','PATTERN_UNSUPPORTED') for g in groups)
        decisions[mode]={'status':'UNSCORABLE' if badids else 'WHOLE_PASSAGE_EXCLUDED' if bad else 'WORDWISE_SUPPORTED_ONLY',
                         'unsupported_groups':bad}
    return {'unit_id':spec['passage_unit'],'reader':'IT2a','original_groups':77,
            'scorable_groups':77-len(badids),'unparseable_ids':badids,'modes':decisions,'groups':groups}


def validate():
    lockpath=E/'LOCK.json';lock=read(lockpath)
    pins={item['path']:item['sha256'] for item in lock['files']}
    for path in (E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'PREREGISTRATION.md',E/'METHOD.md'):
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    spec=read(E/'src/SPEC.json')
    for item in spec['inputs']:assert pins[item['path']]==item['sha256']==sha(ROOT/item['path'])
    assert spec['readers']==['IT2a','RF1b','ZL3b'] and spec['modes']==['FWD','BIDIR'] and spec['primary_mode']=='BIDIR'
    assert spec['recurrence_min']==2
    oldspec=read(ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/src/SPEC.json')
    assert spec['signs']==oldspec['signs']
    source=read(ROOT/'experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/SOURCE_PROJECTION.json')
    words=[word for section in source['source_sections'] for word in section['words']]
    assert all(word and set(word)<=set('אבגדהוזחטיכלמנסעפצקרשת') for word in words)
    W=sorted(set(words));assert len(W)==2411 and len(words)==source['tokens']==6288
    modes=envelope(W)
    assert read(A/'SOURCE_ENVELOPE.json')=={'modes':modes}
    native,readers=native_projection(spec,modes)
    nativepath=A/'NATIVE_SUPPORT.json.gz'
    assert nativepath.read_bytes()[4:8]==b'\x00\x00\x00\x00'
    assert read(nativepath)=={'readers':native}
    passage=passage_projection(spec,modes)
    source_summary={'wordbook_types':len(W),'tokens':len(words),'sections':len(source['source_sections']),
                    'alphabet_size':len(set(''.join(words))),'max_word_length':max(map(len,W)),
                    'wordbook_sha256':hashlib.sha256('\n'.join(W).encode('utf-8')).hexdigest(),
                    'modes':{mode:{'patterns':len(table),'lengths':sorted({len(row['pattern']) for row in table.values()})} for mode,table in modes.items()}}
    prior=read(ROOT/'experiments/yolo/gdt1396_inner_deletion_singleton_wordbook/artifacts/RESULT.json')
    assert source_summary['wordbook_sha256']==prior['source']['wordbook_sha256']
    assert source_summary['alphabet_size']==22 and source_summary['sections']==71
    excluded=[reader['modes']['BIDIR']['ALL']['status']=='EXCLUDED' for reader in readers.values()]
    status='FIXED_W_ONE_GAP_ENVELOPE_EXCLUDED_ALL_READERS' if all(excluded) else 'MIXED_WORD_ENVELOPE' if any(excluded) else 'NECESSARY_WORDWISE_SUPPORT_ONLY'
    expected={'status':status,'source':source_summary,'readers':readers,'passage':passage}
    assert read(A/'RESULT.json')==expected
    receipt={'experiment_id':'GDT1397','status':'PASS_INDEPENDENT_VALIDATION','scientific_status':status,
             'source_pattern_counts':{mode:len(table) for mode,table in modes.items()},
             'readers':{reader:{'strict_groups':entry['strict_groups'],'native_types':entry['native_types'],
                                'primary_mode_ALL':entry['modes']['BIDIR']['ALL']} for reader,entry in readers.items()},
             'passage':{key:value for key,value in passage.items() if key!='groups'},
             'source_free_controls':controls(),
             'implementation':'Independent retained-prefix/suffix enumeration; direct position-equality classes; dynamic raw-unit parsing; original77worksheetgroups only; no primary imports.',
             'pins':{'lock_sha256':sha(lockpath),'validator_sha256':sha(Path(__file__)),
                     'result_sha256':sha(A/'RESULT.json'),'source_envelope_sha256':sha(A/'SOURCE_ENVELOPE.json'),
                     'native_support_sha256':sha(nativepath)},
             'limits':['Only fixed W, literal/single-interior-gap and whole-group premises; no general source-language rejection.',
                       'Per-word pattern support is not a global key, valid unique contraction or meaning.',
                       'BIDIR permits even independently chosen orientations perword, a necessary superset.',
                       'GDT1396 singleton inventory collision and original validation failure remain separately recorded.']}
    assert not (A/'VALIDATION.json').exists()
    save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'scientific_status':status,'source_pattern_counts':receipt['source_pattern_counts']},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');args=p.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
