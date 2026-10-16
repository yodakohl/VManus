#!/usr/bin/env python3
"""Independent exact written-producer/reference accounting; no native glosses."""
import argparse
from collections import Counter,defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')


def adjacent_argument(groups,index):
    if index+1>=len(groups):return None,'NO_RIGHT_GROUP'
    head,arg=groups[index],groups[index+1]
    if int(arg['source_group_index'])!=int(head['source_group_index'])+1:return None,'NONCONSECUTIVE_INDEX'
    if head['right_separator']!='DEFINITE_SPACE' or arg['left_separator']!='DEFINITE_SPACE':return None,'NONDEFINITE_SEAM'
    return arg,None


def select_anchor(producers,page,argument,start):
    eligible=[p for p in producers if p['page']==page and p['argument']==argument and p['end']<start]
    return max(eligible,key=lambda p:p['end']) if eligible else None


def abstract_events(lines,head='R',reference='LR'):
    producers=[];targets=[]
    for line in sorted(lines,key=lambda l:(l['page'],int(l['row']))):
        groups=sorted(line['groups'],key=lambda g:int(g['source_group_index']))
        for i,group in enumerate(groups):
            if group['ivtff_group_raw'] not in (head,reference):continue
            arg,reason=adjacent_argument(groups,i)
            start=(int(line['row']),int(group['source_group_index']))
            if group['ivtff_group_raw']==head:
                if arg is not None:
                    producers.append({'page':line['page'],'argument':arg['ivtff_group_raw'],
                                      'start':start,'end':(int(line['row']),int(arg['source_group_index'])),
                                      'payload':{'head':head,'argument':arg['ivtff_group_raw'],
                                                 'ids':[group['source_group_id'],arg['source_group_id']]}})
            else:
                selected=select_anchor(producers,line['page'],arg['ivtff_group_raw'],start) if arg is not None else None
                targets.append({'id':group['source_group_id'],'argument':None if arg is None else arg['ivtff_group_raw'],
                                'reason':reason,'status':'UNRESOLVED_ARGUMENT' if arg is None else 'MATCHED' if selected else 'MISSING_ANCHOR',
                                'selected':selected})
    return producers,targets


def fixture_line(words,row=1,page='p'):
    return {'page':page,'row':row,'groups':[{'source_group_id':page+':'+str(row)+':'+str(i+1),
        'source_group_index':str(i+1),'ivtff_group_raw':word,
        'left_separator':'LINE_START' if i==0 else 'DEFINITE_SPACE',
        'right_separator':'LINE_END' if i==len(words)-1 else 'DEFINITE_SPACE'} for i,word in enumerate(words)]}


def controls():
    line=fixture_line(['R','A','R','B','LR','A'])
    producers,targets=abstract_events([line]);assert len(producers)==2 and targets[0]['status']=='MATCHED'
    assert targets[0]['selected']['payload']['argument']=='A' and targets[0]['selected']['payload']['ids']==['p:1:1','p:1:2']
    _,twice=abstract_events([fixture_line(['R','A','R','A','LR','A'])]);assert twice[0]['selected']['payload']['ids']==['p:1:3','p:1:4']
    for words in (['R','B','LR','A'],['LR','A','R','A']):assert abstract_events([fixture_line(words)])[1][0]['status']=='MISSING_ANCHOR'
    assert abstract_events([fixture_line(['R','A'],page='p'),fixture_line(['LR','A'],page='q')])[1][0]['status']=='MISSING_ANCHOR'
    for field,position in [('right_separator',0),('left_separator',1)]:
        bad=fixture_line(['R','A','LR','A']);bad['groups'][position][field]='UNCERTAIN_SMALL_SPACE'
        assert abstract_events([bad])[1][0]['status']=='MISSING_ANCHOR'
    bad=fixture_line(['R','A','LR','A']);bad['groups'][1]['source_group_index']='9'
    assert abstract_events([bad])[1][0]['status']=='MISSING_ANCHOR'
    uncertain_target=fixture_line(['R','A','LR','A']);uncertain_target['groups'][2]['right_separator']='UNCERTAIN_SMALL_SPACE'
    assert abstract_events([uncertain_target])[1][0]['status']=='UNRESOLVED_ARGUMENT'
    assert abstract_events([fixture_line(['LR'])])[1][0]['status']=='UNRESOLVED_ARGUMENT'
    assert abstract_events([fixture_line(['R','A'])])[1]==[]
    overlap=fixture_line(['R','LR','LR'])
    assert abstract_events([overlap])[1][0]['status']=='MISSING_ANCHOR'
    _,numeric=abstract_events([fixture_line(['LR','A'],row=10),fixture_line(['R','A'],row=2)])
    assert numeric[0]['status']=='MATCHED'
    producers,_=abstract_events([line]);chosen=select_anchor(producers,'p','A',(1,5));old=deepcopy(chosen['payload'])
    chosen['payload']['intervention']='changed'
    assert select_anchor(producers,'p','A',(1,5))['payload']!=old
    chosen['argument']='C';assert select_anchor(producers,'p','A',(1,5)) is None
    return {'status':'PASS_SOURCE_FREE_CONTROLS','latest_matching_key_not_latest_record':True,
            'future_crosspage_overlap_and_bad_seams_rejected':True,'numeric_order_checked':True,
            'no_argument_and_no_target_distinct':True,'stored_payload_intervention_changes_return':True,
            'producer_key_intervention_removes_match':True,'native_access':False}


def source_packet(spec):
    columns=['source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']
    selected={reader:[] for reader in spec['editions']}
    for pin in spec['sources']:
        document=read(ROOT/pin['path']);assert document['group_columns']==columns
        for line in document['lines']:
            metadata=line['metadata']
            if metadata['page'] not in spec['pages'] or metadata['kind']!='P':continue
            assert metadata['edition'] in selected
            rows=line['groups'];assert len(rows)==int(metadata['source_group_count'])
            assert all(len(row)==len(columns) for row in rows)
            assert [int(row[1]) for row in rows]==list(range(1,len(rows)+1))
            selected[metadata['edition']].append(line)
    for reader,lines in selected.items():
        assert {line['metadata']['page'] for line in lines}==set(spec['pages'])
        assert len({line['metadata']['locus'] for line in lines})==len(lines)
        assert len({int(line['metadata']['source_row_index']) for line in lines})==len(lines)
        lines.sort(key=lambda line:int(line['metadata']['source_row_index']))
        ids=[row[0] for line in lines for row in line['groups']]
        assert len(ids)==len(set(ids))
    return {'source_pins':spec['sources'],'group_columns':columns,'readers':selected}


def panel(lines,columns,spec):
    producers=[];references=[]
    # Construct the complete licensed producer inventory first; temporal filtering is explicit.
    for line in lines:
        metadata=line['metadata'];rows=[dict(zip(columns,row)) for row in line['groups']]
        row_order=int(metadata['source_row_index'])
        for index,head in enumerate(rows):
            raw=head['ivtff_group_raw']
            if raw not in (spec['head'],spec['reference_head']):continue
            argument,problem=adjacent_argument(rows,index)
            span=[head['source_group_id']]+([argument['source_group_id']] if argument is not None else [])
            if raw==spec['head']:
                if argument is not None:
                    producers.append({'page':metadata['page'],'locus':metadata['locus'],'span':span,
                                      'key':argument['ivtff_group_raw'],
                                      'end_order':[row_order,int(argument['source_group_index'])],
                                      'payload':{'head':spec['head'],'argument':argument['ivtff_group_raw'],'producer_span':span}})
            else:references.append((metadata,head,argument,problem,span))
    cases=[]
    for metadata,head,argument,problem,span in references:
        start=(int(metadata['source_row_index']),int(head['source_group_index']))
        prior=[producer for producer in producers if producer['page']==metadata['page'] and tuple(producer['end_order'])<start]
        matching=[] if argument is None else [producer for producer in prior if producer['key']==argument['ivtff_group_raw']]
        chosen=max(matching,key=lambda producer:tuple(producer['end_order'])) if matching else None
        cases.append({'reference_id':head['source_group_id'],'page':metadata['page'],'locus':metadata['locus'],
                      'argument':None if argument is None else argument['ivtff_group_raw'],
                      'reference_span':span,'status':'UNRESOLVED_ARGUMENT' if argument is None else 'MATCH' if chosen else 'NO_ANCHOR',
                      'argument_problem':problem,'prior_producer_spans':[p['span'] for p in prior],
                      'matching_prior_spans':[p['span'] for p in matching],
                      'selected_producer_span':None if chosen is None else chosen['span'],
                      'returned':None if chosen is None else deepcopy(chosen['payload'])})
    counts=Counter(case['status'] for case in cases)
    return {'producer_records':producers,'cases':cases,'target_count':len(cases),
            'matched':counts['MATCH'],'missing':counts['NO_ANCHOR'],'unresolved':counts['UNRESOLVED_ARGUMENT']}


def trace77(source,panels):
    constructors={gid for producer in panels['IT2a']['producer_records'] for gid in producer['span']}
    references={gid for case in panels['IT2a']['cases'] for gid in case['reference_span']}
    selected=[line for line in source['readers']['IT2a'] if line['metadata']['locus'] in {'f75v.'+str(n) for n in range(43,50)}]
    assert [line['metadata']['locus'] for line in selected]==['f75v.'+str(n) for n in range(43,50)]
    assert sum(len(line['groups']) for line in selected)==77
    result=[]
    for line in selected:
        groups=[]
        for original in line['groups']:
            gid=original[0]
            label='CONSTRUCTOR_SPAN' if gid in constructors else 'REFERENCE_SPAN' if gid in references else 'UNKNOWN_CONTRIBUTION'
            groups.append({'original_group':original,'structural_annotation':label,'meaning':'UNASSIGNED'})
        result.append({'metadata':line['metadata'],'groups':groups})
    return result


def validate():
    lockpath=E/'LOCK.json';lock=read(lockpath);pins={item['path']:item['sha256'] for item in lock['entries']}
    for path in (E/'src/run.py',Path(__file__),E/'src/SPEC.json'):
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    spec=read(E/'src/SPEC.json')
    assert spec['pages']==['f75v','f80v'] and spec['editions']==['IT2a','ZL3b','RF1b']
    assert spec['head']=='sheckhy' and spec['reference_head']=='lsheckhy'
    assert pins[spec['plan']]==spec['plan_sha256']==sha(ROOT/spec['plan'])
    for entry in spec['sources']:assert pins[entry['path']]==entry['sha256']==sha(ROOT/entry['path'])
    plan=read(ROOT/spec['plan'])
    source=source_packet(spec);assert read(A/'SOURCE.json')==source
    panels={reader:panel(source['readers'][reader],source['group_columns'],spec) for reader in spec['editions']}
    assert {reader:data['target_count'] for reader,data in panels.items()}=={'IT2a':2,'ZL3b':2,'RF1b':1}
    primary=panels['IT2a']
    status='NO_PRIMARY_TARGET_CAPACITY' if primary['target_count']==0 else 'FIXED_OVERT_CONSTRUCTION_MISSING_ANCHOR' if primary['missing'] else 'UNRESOLVED_SOURCE_OR_ARGUMENT' if primary['unresolved'] else 'ALL_PRIMARY_TARGETS_HAVE_OVERT_ANCHORS_SCOPED'
    expected={'status':status,'primary_reader':'IT2a','panels':panels,'meaning_selection':'NONE',
              'unknowns_are_noops':False,'scope':plan['claim_ceiling']}
    assert read(A/'RESULT.json')==expected
    trace=read(A/'TRACE_77.json');assert trace['lines']==trace77(source,panels)
    assert isinstance(trace['scope'],str) and trace['scope']
    receipt={'experiment':'GDT1407','status':'PASS_INDEPENDENT_VALIDATION','scientific_status':status,
             'panels':{reader:{field:data[field] for field in ('target_count','matched','missing','unresolved')} for reader,data in panels.items()},
             'original_IT_f75v_groups_preserved':77,'source_free_controls':record_controls(),
             'implementation':'Independent six-cache source reconstruction, complete producer inventory then strict end-before-start same-page exact-key selection; no primary imports.',
             'pins':{'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(lockpath),
                     'source_sha256':sha(A/'SOURCE.json'),'result_sha256':sha(A/'RESULT.json'),
                     'trace77_sha256':sha(A/'TRACE_77.json'),'plan_sha256':sha(ROOT/spec['plan'])},
             'limits':['Exact authored overt-producer/right-argument/page-scope contract only; unknown groups are not asserted to be no-ops.',
                       'Missing licensed anchors do not exclude other unrecognized producers or other possible native semantics.',
                       'Payload intervention proves the authored software return depends on its stored record, not that this is a native reference.',
                       'Alternate readings and absence of an RF target are not independent confirmation or success.',
                       'No general l-prefix meaning, action/object assignment, language or English gloss selected.']}
    target=A/'VALIDATION.json'
    if target.exists():assert read(target)==receipt
    else:save(target,receipt)
    print(json.dumps({'status':receipt['status'],'scientific_status':status,'panels':receipt['panels']},sort_keys=True))


def record_controls():
    result=controls();path=A/'INDEPENDENT_CONTROLS.json'
    if path.exists():assert read(path)==result
    else:save(path,result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--controls','--controls-only',dest='controls',action='store_true');args=p.parse_args()
    if args.controls:print(json.dumps(record_controls(),sort_keys=True))
    else:validate()
