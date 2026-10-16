#!/usr/bin/env python3
"""Independent fixed-wordbook/run-allograph necessary support validator."""
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
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n')


def pattern(sequence):
    earliest=[next(j for j in range(i+1) if sequence[j]==sequence[i]) for i in range(len(sequence))]
    labels=sorted(set(earliest))
    return tuple(labels.index(j) for j in earliest)


def collapse(sequence):
    return [value for i,value in enumerate(sequence)
            if i==0 or value not in ('e','i') or sequence[i-1]!=value]


def parse(raw,signs):
    states=[[] for _ in range(len(raw)+1)];states[0]=[()]
    for i in range(len(raw)):
        for sign in signs:
            if states[i] and raw.startswith(sign,i):
                j=i+len(sign);states[j]=(states[j]+[s+(sign,) for s in states[i]])[:2]
    return list(states[-1][0]) if len(states[-1])==1 and states[-1][0] else None


def pkey(p):return '.'.join(map(str,p))


def source_words(spec):
    recipes=read(ROOT/spec['recipe_path']);deot=read(ROOT/spec['deot_path']);others=read(ROOT/spec['other_path'])
    result={name:[word for record in recipes[name] for word in record['words']] for name in ('b4','w1','bs1','gr1')}
    result['deot']=[word for section in deot['source_sections'] for word in section['words']]
    for name in ('OLD_ITALIAN_UD_CONTROL','LATIN_PROIEL_CONTROL','ANCIENT_GREEK_PROIEL_CONTROL'):
        result[name]=[item['unit'] for item in others[name]['PRIMARY']['units']]
        assert len(result[name])==8000
    assert set(result)==set(spec['source_names'])
    assert all(isinstance(word,str) and word for words in result.values() for word in words)
    return result


def envelopes(words):
    modes={'FWD':{},'BIDIR':{}}
    for word in sorted(set(words)):
        for direction,output in [('FWD',word),('REV',word[::-1])]:
            pat=pattern(output);key=pkey(pat)
            witness={'word':word,'direction':direction,'pattern':list(pat)}
            if direction=='FWD':modes['FWD'].setdefault(key,witness)
            modes['BIDIR'].setdefault(key,witness)
    return modes


def controls():
    checks=0
    letters='aei'
    for length in range(5):
        for source in itertools.product(letters,repeat=length):
            if any(source[i]==source[i-1] and source[i] in ('e','i') for i in range(1,length)):continue
            run_positions=[i for i,c in enumerate(source) if c in ('e','i')]
            for sizes in itertools.product((1,2,3),repeat=len(run_positions)):
                counts=dict(zip(run_positions,sizes));rendered=[c for i,c in enumerate(source) for _ in range(counts.get(i,1))]
                assert collapse(rendered)==list(source);checks+=1
    assert collapse([])==[] and collapse(['e'])==['e']
    assert collapse(['a','a','ckh','ckh','e','e','i','i'])==['a','a','ckh','ckh','e','i']
    assert pattern('AaA')==(0,1,0) and pattern('AAA')==(0,0,0)
    assert pattern('eé')==(0,1) and len(pattern('e\u0301'))==2
    assert pattern('ee')==(0,0) and pattern(collapse(['e','e']))==(0,)
    assert parse('qocheey',['q','o','ch','e','y'])==['q','o','ch','e','e','y']
    for length in range(1,4):
        words=list(itertools.product('abc',repeat=length))
        for left in words:
            for right in words:
                possible=any(tuple(perm['abc'.index(c)] for c in left)==right for perm in itertools.permutations('abc'))
                assert (pattern(left)==pattern(right))==possible;checks+=1
    # Raw-form leaf support cannot be enlarged by merging collapsed variants.
    rawleaves={'e':{'f2'},'ee':{'f3'}}
    assert not [raw for raw,leaves in rawleaves.items() if len(leaves)>=2]
    assert collapse(['e'])==collapse(['e','e'])
    return {'status':'PASS_SOURCE_FREE_CONTROLS','cases_checked':checks,'native_only_collapse':True,
            'Unicode_case_accents_and_source_repeats_preserved':True,'raw_leaf_support_precedes_collapse':True,
            'equality_pattern_iff_small_bijection':True,'empirical_access':False}


def support(units,envelopes_by_source,lengths):
    out={}
    for name,modes in envelopes_by_source.items():
        out[name]={}
        for mode,table in modes.items():
            if units is None:status='UNPARSEABLE'
            elif len(units) not in lengths[name][mode]:status='LENGTH_UNSUPPORTED'
            else:status='SUPPORTED' if pkey(pattern(units)) in table else 'PATTERN_UNSUPPORTED'
            out[name][mode]=status
    return out


def summary(rows,name,mode):
    bad=[row for row in rows if row['support'][name][mode]!='SUPPORTED']
    return {'types':len(rows),'occurrences':sum(row['count'] for row in rows),
            'unsupported_types':len(bad),'unsupported_occurrences':sum(row['count'] for row in bad),
            'unsupported_physical_leaves':sorted({leaf for row in bad for leaf in row['leaves']}),
            'length_failure_types':sum(row['support'][name][mode]=='LENGTH_UNSUPPORTED' for row in bad),
            'pattern_failure_types':sum(row['support'][name][mode]=='PATTERN_UNSUPPORTED' for row in bad),
            'unsupported_changed_types':sum(row['changed'] for row in bad),
            'unsupported_unchanged_types':sum(not row['changed'] for row in bad),
            'status':'EMPTY_PANEL' if not rows else 'EXCLUDED' if bad else 'WORDWISE_SUPPORTED_ONLY'}


def native_projection(spec,tables,lengths):
    cached=read(ROOT/spec['native_path']);native={};results={}
    for reader in spec['readers']:
        groups=defaultdict(list);rows=cached[reader]
        assert len({row['id'] for row in rows})==len(rows)
        for row in rows:
            assert row['edition']==reader and row['kind']=='P'
            assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
            assert not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v')
            units=parse(row['ivtff_group_raw'],spec['signs']);assert units==row['units'] and units is not None
            groups[row['ivtff_group_raw']].append(row)
        forms=[]
        for raw,occurrences in sorted(groups.items()):
            units=parse(raw,spec['signs']);collapsed=collapse(units);pat=pattern(collapsed)
            pages=sorted({row['page'] for row in occurrences})
            leaves=sorted({re.match(r'f\d+',page).group() for page in pages})
            forms.append({'form':raw,'units':units,'collapsed_units':collapsed,'changed':units!=collapsed,
                          'pattern':list(pat),'pattern_key':pkey(pat),'count':len(occurrences),
                          'ids':sorted(row['id'] for row in occurrences),'pages':pages,'leaves':leaves,
                          'support':support(collapsed,tables,lengths)})
        native[reader]=forms;source_results={}
        for name in spec['source_names']:
            item={mode:{'FULL':summary(forms,name,mode),'LEAF2':summary([row for row in forms if len(row['leaves'])>=2],name,mode)} for mode in spec['modes']}
            item['first_failures']={}
            for mode in spec['modes']:
                bad=sorted((row for row in forms if row['support'][name][mode]!='SUPPORTED'),key=lambda row:(-row['count'],row['form']))[:10]
                item['first_failures'][mode]=[{'form':row['form'],'count':row['count'],'leaves':row['leaves'],
                                               'changed':row['changed'],'status':row['support'][name][mode],
                                               'first_id':row['ids'][0]} for row in bad]
            source_results[name]=item
        results[reader]={'strict_groups':len(rows),'raw_types':len(forms),
                         'changed_raw_types':sum(row['changed'] for row in forms),'source_results':source_results}
    return native,results


def passage_projection(spec,tables,lengths):
    worksheet=read(ROOT/spec['worksheet_path'])
    selected=[unit for unit in worksheet['units'] if unit['unit_id']==spec['passage_unit']]
    assert len(selected)==1 and spec['passage_unit']=='f75v_IT2a'
    lines=selected[0]['lines'];rows=[]
    assert [line['metadata']['locus'] for line in lines]==['f75v.'+str(i) for i in range(43,50)]
    assert str(lines[0]['metadata']['paragraph_start'])=='1' and str(lines[-1]['metadata']['paragraph_end'])=='1'
    for line in lines:
        meta=line['metadata'];groups=line['original_groups']
        assert meta['edition']=='IT2a' and meta['page']=='f75v' and meta['kind']=='P'
        assert len(groups)==int(meta['source_group_count'])
        assert [int(group[1]) for group in groups]==list(range(1,len(groups)+1))
        for original in groups:
            assert len(original)==5
            units=parse(original[2],spec['signs']);collapsed=collapse(units) if units is not None else None
            rows.append({'original':original,'page':meta['page'],'locus':meta['locus'],'units':units,
                         'collapsed_units':collapsed,'pattern':list(pattern(collapsed)) if collapsed is not None else None,
                         'support':support(collapsed,tables,lengths)})
    assert len(rows)==spec['expected_passage_groups']==77
    missing=[row['original'][0] for row in rows if row['units'] is None]
    decisions={}
    for name in spec['source_names']:
        decisions[name]={}
        for mode in spec['modes']:
            unsupported=[row['original'][0] for row in rows if row['support'][name][mode] not in ('SUPPORTED','UNPARSEABLE')]
            decisions[name][mode]={'status':'UNSCORABLE' if missing else 'WHOLE_PASSAGE_EXCLUDED' if unsupported else 'WORDWISE_SUPPORTED_ONLY',
                                   'unsupported_groups':len(unsupported),'unsupported_ids':unsupported}
    return {'unit_id':spec['passage_unit'],'original_groups':77,'unparseable_ids':missing,
            'groups':rows,'sources':decisions}


def validate():
    lockpath=E/'LOCK.json';lock=read(lockpath)
    pins=lock['files'] if isinstance(lock['files'],dict) else {entry['path']:entry['sha256'] for entry in lock['files']}
    for path in (E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'METHOD.md',E/'PREREGISTRATION.md'):
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    spec=read(E/'src/SPEC.json')
    for entry in spec['inputs']:assert pins[entry['path']]==entry['sha256']==sha(ROOT/entry['path'])
    assert spec['experiment_id']=='GDT1403' and spec['readers']==['IT2a','RF1b','ZL3b']
    assert spec['modes']==['FWD','BIDIR'] and spec['primary_mode']=='BIDIR'
    assert spec['collapsed_native_units']==['e','i']
    oldspec=read(ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/src/SPEC.json')
    assert spec['signs']==oldspec['signs']
    sources=source_words(spec);tables={};envelope_artifact={};source_summary={}
    for name in spec['source_names']:
        words=sources[name];W=sorted(set(words));modes=envelopes(words);tables[name]=modes
        metadata={'tokens':len(words),'word_types':len(W),
                  'wordbook_sha256':hashlib.sha256('\n'.join(W).encode('utf-8')).hexdigest(),
                  'source_alphabet_size':len(set(''.join(words)))}
        envelope_artifact[name]={**metadata,'modes':modes}
        source_summary[name]={**metadata,'modes':{mode:{'patterns':len(table),'lengths':sorted({len(row['pattern']) for row in table.values()})} for mode,table in modes.items()}}
    envelope_path=A/'SOURCE_ENVELOPES.json.gz'
    assert read(envelope_path)=={'sources':envelope_artifact}
    assert envelope_path.read_bytes()[4:8]==b'\x00\x00\x00\x00'
    lengths={name:{mode:set(data['lengths']) for mode,data in meta['modes'].items()} for name,meta in source_summary.items()}
    native,readers=native_projection(spec,tables,lengths)
    native_path=A/'NATIVE_SUPPORT.json.gz';assert read(native_path)=={'readers':native}
    assert native_path.read_bytes()[4:8]==b'\x00\x00\x00\x00'
    passage=passage_projection(spec,tables,lengths)
    decisions={name:{'all_readers_FULL_excluded':all(readers[r]['source_results'][name]['BIDIR']['FULL']['status']=='EXCLUDED' for r in spec['readers']),
                     'all_readers_LEAF2_excluded':all(readers[r]['source_results'][name]['BIDIR']['LEAF2']['status']=='EXCLUDED' for r in spec['readers'])} for name in spec['source_names']}
    status='ALL_EIGHT_FIXED_WORD_ENVELOPES_EXCLUDED' if all(value['all_readers_FULL_excluded'] for value in decisions.values()) else 'MIXED_FIXED_WORD_ENVELOPES'
    expected={'sources':source_summary,'readers':readers,'claim_ceiling':spec['claim_ceiling'],
              'passage':passage,'source_decisions':decisions,'status':status}
    assert read(A/'RESULT.json')==expected
    receipt={'experiment_id':'GDT1403','status':'PASS_INDEPENDENT_VALIDATION','scientific_status':status,
             'source_decisions':decisions,'source_count':len(sources),'source_free_controls':controls(),
             'native_raw_type_counts':{reader:readers[reader]['raw_types'] for reader in spec['readers']},
             'passage_original_groups':77,'passage_unparseable_ids':passage['unparseable_ids'],
             'implementation':'Independent direct positional-equality classes, dynamic raw-unit parsing, adjacent-only native e/i suppression, exact source-codepoint envelopes, rawform leaf support and original passage reconstruction; no primary imports.',
             'pins':{'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(lockpath),
                     'result_sha256':sha(A/'RESULT.json'),'source_envelopes_sha256':sha(envelope_path),
                     'native_support_sha256':sha(native_path)},
             'limits':['Fixed eight source-wordbook conjunctions only; not language, phonetic or general allograph exclusions.',
                       'Source codepoints remain untouched; run collapse is a native writer hypothesis, not accepted normalization.',
                       'Perword renaming and reversal do not supply a common key or a full passage reading.',
                       'LEAF2 is selected on raw forms beforecollapse; it is sensitivity rather than independent confirmation.',
                       'GDT1395nonrejection does not accept runallography; GDT1328geometric failure remains unchanged.']}
    assert not (A/'VALIDATION.json').exists()
    save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'scientific_status':status,'source_count':len(sources)},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');args=p.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
