#!/usr/bin/env python3
"""Independent fixed-distance equality-run square and provenance validator."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re
import numpy as np

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n')


def squares(text,minimum=6):
    values=np.array([ord(c) for c in text],dtype=np.uint32);n=len(values);found=[]
    for period in range(minimum,n//2+1):
        equal=values[:-period]==values[period:]
        bad=np.flatnonzero(~equal)
        starts=np.concatenate((np.array([0]),bad+1))
        ends=np.concatenate((bad,np.array([len(equal)])))
        suitable=ends-starts>=period
        for start,end in zip(starts[suitable],ends[suitable]):
            found.extend((i,period) for i in range(int(start),int(end)-period+1))
    return sorted(found)


def brute(text,minimum):
    return sorted((i,p) for p in range(minimum,len(text)//2+1) for i in range(len(text)-2*p+1) if text[i:i+p]==text[i+p:i+2*p])


def normalize(text,positions,rule):
    letters=[];origins=[]
    for offset in positions:
        for char in text[offset].casefold():
            if char.isalpha():
                if rule=='UV_IJ':char={'v':'u','j':'i'}.get(char,char)
                else:assert rule=='CASEFOLD'
                letters.append(char);origins.append(offset)
    return ''.join(letters),origins


def controls():
    checked=0
    for n in range(11):
        for chars in itertools.product('ab',repeat=n):
            word=''.join(chars);assert squares(word,1)==brute(word,1);checked+=1
    for word in ('a'*12,'a'*18,'abcdefabcdef','xabcdefabcdefy','abcabcabcabc','abcdefabcdeg','abcdeabcde'):
        assert squares(word,6)==brute(word,6);checked+=1
    assert (0,6) in squares('a'*12,6) # nonprimitive blocks are required too
    source='V J ß [ab]';normal,offsets=normalize(source,range(len(source)),'UV_IJ')
    assert normal=='uissab' and offsets[2]==offsets[3]
    H={unit:unit*2 for unit in 'qokedy'};block=''.join(H[u] for u in 'qokedy')
    assert len(block)>=6 and (0,len(block)) in squares(block+block,6)
    assert not squares('abab',6) # erasing most units destroys the claimed6lower bound
    return {'status':'PASS_SOURCE_FREE_CONTROLS','binary_and_named_strings':checked,
            'all_starts_periods_vs_brute':True,'nonprimitive_blocks_retained':True,
            'casefold_expansion_origins_checked':True,'nonerasing_vs_null_limit':True,'source_access':False}


def projections(spec):
    source_path=ROOT/spec['source_path'];text=source_path.read_bytes().decode('utf-8')
    records=read(ROOT/spec['records_path']);assert records['source']['path']==spec['source_path']
    assert records['source']['sha256']==sha(source_path)
    lines=text.splitlines(keepends=True);assert len(lines)==records['source']['line_count']==404
    offsets=[];position=0
    for line in lines:offsets.append(position);position+=len(line)
    assert position==len(text)
    boundaries=records['all_header_boundaries'];baths=records['records']
    assert len(boundaries)==33 and len(baths)==32
    assert [int(r['record_id']) for r in baths]==list(range(1,31))+[32,33]
    headers={int(r['start_line'])-1:r for r in boundaries}
    assert len(headers)==33 and set(int(r['record_id']) for r in boundaries)==set(range(1,34))
    for line_index,record in headers.items():
        assert lines[line_index].rstrip('\r\n')==record['header_exact']
        assert 1<=int(record['start_line'])<=int(record['end_line'])<=len(lines)
    assert lines[0].startswith('[Prologus]')
    content_by_line=[]
    for index,line in enumerate(lines):
        cut=0
        if index==0 or index in headers:
            end=line.find(']');assert end>=0
            cut=end+1;separator=re.match(r'\s*-\s*',line[cut:])
            if separator:cut+=separator.end()
        content_by_line.append(list(range(offsets[index]+cut,offsets[index]+len(line))))
    bases={'PUBLISHED_ALL':list(range(len(text))),
           'ALL_CONTENT':[offset for part in content_by_line for offset in part]}
    bath_parts=[]
    for bath in baths:
        start,end=int(bath['start_line'])-1,int(bath['end_line'])
        assert bath==next(r for r in boundaries if r['record_id']==bath['record_id'])
        part=[offset for line_offsets in content_by_line[start:end] for offset in line_offsets]
        bath_parts.append((int(bath['record_id']),part))
    bases['BATH_CONTENT']=[offset for number,part in bath_parts for offset in part]
    for number,part in bath_parts:bases['BATH_BODY_'+str(number).zfill(2)]=part
    assert len(bases)==35
    output=[]
    for rule in spec['letter_rules']:
        for base,positions in bases.items():
            normalized,origins=normalize(text,positions,rule)
            assert len(normalized)==len(origins)
            output.append({'id':rule+':'+base,'base':base,'rule':rule,'text':normalized,
                           'source_offsets':origins,'characters':len(normalized)})
    return {'source_pin':{'path':spec['source_path'],'sha256':sha(source_path)},
            'record_pin':{'path':spec['records_path'],'sha256':sha(ROOT/spec['records_path'])},
            'projections':output}


def native_repeat(spec):
    worksheet=read(ROOT/spec['worksheet_path'])
    unit=worksheet['source_original_wrapper']['source_unit'];assert unit['edition']=='IT2a'
    assert unit['group_columns']==['source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']
    assert [line['metadata']['locus'] for line in unit['lines']]==['f75v.'+str(n) for n in range(43,50)]
    assert sum(len(line['groups']) for line in unit['lines'])==77
    line=next(line for line in unit['lines'] if line['metadata']['locus']=='f75v.46')
    pair=line['groups'][3:5];assert len(pair)==2
    assert [row[0] for row in pair]==['IT2a|f75v.46|G004','IT2a|f75v.46|G005']
    assert all(row[2]=='qokedy' for row in pair)
    assert int(pair[1][1])==int(pair[0][1])+1 and pair[0][4]==pair[1][3]=='DEFINITE_SPACE'
    return {'original_source':unit,'pair':pair,'required_word':'qokedy','required_units':list('qokedy'),
            'unit_count':6,'full_original_group_count':77}


def validate():
    lockpath=E/'LOCK.json';lock=read(lockpath)
    entries=lock.get('entries',lock.get('files',lock.get('hashes')))
    pins=entries if isinstance(entries,dict) else {entry['path']:entry['sha256'] for entry in entries}
    for path in (E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'METHOD.md'):
        relative=str(path.relative_to(ROOT));assert pins[relative]==sha(path),relative
    spec=read(E/'src/SPEC.json');assert spec['minimum_period']==6 and spec['letter_rules']==['CASEFOLD','UV_IJ']
    for field in ('source_path','records_path','worksheet_path'):assert pins[spec[field]]==sha(ROOT/spec[field])
    rebuilt=projections(spec);assert read(A/'PROJECTIONS.json')==rebuilt
    repeated=native_repeat(spec);assert read(A/'NATIVE_REPEAT.json')==repeated
    expected_cases=[]
    for projection in rebuilt['projections']:
        text=projection['text'];origins=projection['source_offsets'];found=squares(text,6)
        witnesses=[]
        for start,period in found:
            end=start+2*period;block=text[start:start+period]
            assert text[start+period:end]==block and period>=6
            witnesses.append({'start':start,'end':end,'period':period,'block':block,
                              'source_start_offset':origins[start],'source_last_offset':origins[end-1]})
        expected_cases.append({'projection_id':projection['id'],'characters':len(text),'square_count':len(found),
                               'squares':witnesses,'decision':'SQUARE_CAPACITY_ONLY' if found else 'NO_REQUIRED_SQUARE'})
    result=read(A/'RESULT.json')
    assert result['experiment_id']=='GDT1409' and result['status']=='COMPLETE_FIXED_SOURCE_SQUARE_CAPACITY'
    assert result['minimum_period']==6 and result['native_repeat']=='qokedy qokedy'
    assert result['cases']==expected_cases and len(expected_cases)==70
    assert result['word_meanings_assigned']==0 and result['claim_ceiling']==spec['claim_ceiling']
    receipt={'experiment_id':'GDT1409','status':'PASS_INDEPENDENT_VALIDATION',
             'method':'Constant-distance character equality runs; everyrunoflength>=period yields all squarestarts. No primary prefix-sum algorithm imported or read.',
             'source_free_controls':controls(),'projections_checked':70,'original_native_groups_preserved':77,
             'case_counts':{case['projection_id']:case['square_count'] for case in expected_cases},
             'pins':{'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(lockpath),
                     'projections_sha256':sha(A/'PROJECTIONS.json'),'native_repeat_sha256':sha(A/'NATIVE_REPEAT.json'),
                     'result_sha256':sha(A/'RESULT.json'),'source_sha256':sha(ROOT/spec['source_path']),
                     'audited_record_source_sha256':sha(ROOT/spec['records_path'])},
             'limits':['Fixed literal sourceprojections and nonerasing context-independent unit expansions only; no sourcebook or Latin-language ban.',
                       'Squares include nonprimitive blocks. Source boundaries, Unicodecasefold origins and explicitheaderremoval remain exactly as registered.',
                       'A source square gives necessary capacity only, not an encoding, word meaning or reading.',
                       'Null units, copying/dittography repairs, contextual expansions, paraphrase and changed sourcebooks are outside this test.']}
    target=A/'VALIDATION.json'
    if target.exists():assert read(target)==receipt
    else:save(target,receipt)
    print(json.dumps({'status':receipt['status'],'projections':70,'square_counts':receipt['case_counts']},sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--controls',action='store_true');mode.add_argument('--validate',action='store_true');args=parser.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
