#!/usr/bin/env python3
"""Frozen finite semantic consequence filter; no key search."""
import csv, hashlib, itertools, json
from collections import defaultdict, Counter
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];A=P/'artifacts'
OLD=ROOT/'experiments/yolo/gdt959_geomantic_element_remainder'
ELEMENTS=['AIR','EARTH','FIRE','WATER']
def dump(name,obj): (A/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def tab(name,rows):
    with (A/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
def records():return json.loads((OLD/'artifacts/TARGET_RECORDS.json').read_text())
def oldcases():return json.loads((OLD/'artifacts/ALL_CANDIDATES.json').read_text())
def predict():
    rs={(r['edition'],r['position_top_down']):r for r in records()};out=[]
    for c in oldcases():
        for i,(v,n,e) in enumerate(zip(c['figures'],c['names'],c['elements']),1):
            r=rs[c['edition'],i]
            out.append(dict(case=c['case'],candidate_id=c['candidate_id'],table=c['table'],position=i,raw=r['raw'],raw_state=r['state'],figure=v,predicted_name=n,predicted_element=e or 'UNKNOWN',old959_status=c['status']))
    assert len(out)==16920;tab('PREDICTIONS.tsv',out)
def run():
    for p,h in json.loads((P/'PREREG_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    target=records();pairs=[];edges=defaultdict(list)
    for ed in ('ZL3b','IT2a','RF1b'):
        rs=sorted([r for r in target if r['edition']==ed],key=lambda r:r['position_top_down'])
        assert len(rs)==15
        for x,y in itertools.combinations(rs,2):
            a,b=x['raw'],y['raw'];diff=[]
            if x['state']!='KNOWN' or y['state']!='KNOWN':state='UNKNOWN_TARGET'
            else:
                assert a and b and all('a'<=c<='z' for c in a+b)
                diff=[i+1 for i,(u,v) in enumerate(zip(a,b)) if u!=v]
                state='EDGE' if len(a)==len(b) and len(diff)==1 else 'NOT_EDGE'
            q=dict(edition=ed,position1=x['position_top_down'],position2=y['position_top_down'],raw1=a,raw2=b,status=state,changed_position=diff[0] if state=='EDGE' else None)
            pairs.append(q)
            if state=='EDGE':edges[ed].append(q)
    dump('ALL_PAIRS.json',pairs);allrows=[];consequences=[]
    for c in oldcases():
        er=[]
        for e in edges[c['edition']]:
            i,j=e['position1']-1,e['position2']-1;vs=[c['elements'][i],c['elements'][j]]
            d=dict(e,names=[c['names'][i],c['names'][j]],elements=vs,conflict=None not in vs and vs[0]!=vs[1],unknown_source=None in vs)
            er.append(d);consequences.append(dict(case=c['case'],candidate_id=c['candidate_id'],table=c['table'],position1=i+1,position2=j+1,raw1=e['raw1'],raw2=e['raw2'],changed_position=e['changed_position'],name1=d['names'][0],name2=d['names'][1],element1=vs[0] or 'UNKNOWN',element2=vs[1] or 'UNKNOWN',explicit_conflict=d['conflict']))
        ok=[v for v in ELEMENTS if er and all(len({v if x is None else x for x in e['elements']})==1 for e in er)]
        lower=bool(er) and all(not e['unknown_source'] and not e['conflict'] for e in er)
        allrows.append(dict(case=c['case'],edition=c['edition'],direction=c['direction'],candidate_id=c['candidate_id'],table=c['table'],figures=c['figures'],names=c['names'],elements=c['elements'],old959_status=c['status'],edges=er,lower=lower,upper=bool(ok),allowed_source_completions=ok,status='NO_CAPACITY' if not er else 'COMPATIBLE_KNOWN_EDGES' if lower else 'UNKNOWN_ONLY' if ok else 'CONTRADICTED',unknown_target_labels=c['unknown_target_labels'],independent_confirmation_leaves=0))
    assert len(allrows)==1128
    dump('ALL_CANDIDATES.json',allrows);tab('EDGE_CONSEQUENCES.tsv',consequences)
    tab('CANDIDATE_TABLE.tsv',[dict(case=r['case'],candidate_id=r['candidate_id'],table=r['table'],old959_status=r['old959_status'],new_status=r['status'],edge_count=len(r['edges']),explicit_conflicts=sum(e['conflict'] for e in r['edges']),source_completions=' | '.join(r['allowed_source_completions']),predicted_names=' | '.join(r['names']),predicted_elements=' | '.join(x or 'UNKNOWN' for x in r['elements']),independent_confirmation_leaves=0) for r in allrows])
    lookup={(r['edition'],r['direction'],r['candidate_id'],r['table']):r for r in allrows};cross=[]
    for r in allrows:
        if r['edition']!='IT2a':continue
        linked=[lookup.get((ed,r['direction'],r['candidate_id'],r['table'])) for ed in ('ZL3b','IT2a','RF1b')]
        common=set(ELEMENTS)
        for x in linked:common&=set(x['allowed_source_completions']) if x else set()
        cross.append(dict(direction=r['direction'],candidate_id=r['candidate_id'],table=r['table'],names=r['names'],figures=r['figures'],all_editions_present=all(x is not None for x in linked),lower=all(x and x['lower'] for x in linked),upper=bool(common),common_source_completions=sorted(common),edition_statuses={ed:x['status'] if x else 'MISSING_KEY' for ed,x in zip(('ZL3b','IT2a','RF1b'),linked)}))
    dump('COMPLETE_IT2A_CROSS_EDITION.json',cross)
    oldcross=json.loads((OLD/'artifacts/COMPLETE_IT2A_CROSS_EDITION.json').read_text());old7={(r['direction'],r['candidate_id'],r['table']) for r in oldcross if r['upper']}
    dump('PREVIOUS_SEVEN.json',[r for r in cross if (r['direction'],r['candidate_id'],r['table']) in old7])
    for kind in ('physical','observed'):
        groups=defaultdict(list)
        for r in allrows:
            key=tuple(r['names']) if kind=='physical' else (r['edition'],tuple((e['position1'],e['position2'],*e['elements']) for e in r['edges']))
            groups[repr(key)].append(dict(case=r['case'],candidate_id=r['candidate_id'],table=r['table'],status=r['status']))
        dump('IDENTICAL_'+kind.upper()+'_PREDICTIONS.json',[dict(prediction=k,provenance=v) for k,v in sorted(groups.items())])
    sums=[]
    for case,table in sorted({(r['case'],r['table']) for r in allrows}):
        rs=[r for r in allrows if r['case']==case and r['table']==table]
        sums.append(dict(case=case,table=table,candidates=len(rs),lower=sum(r['lower'] for r in rs),upper=sum(r['upper'] for r in rs),contradicted=sum(r['status']=='CONTRADICTED' for r in rs)))
    tab('SUMMARY.tsv',sums)
    result=dict(status='POST_EXPOSURE_FIXED_CLASS_EXTENSION_EVALUATED',candidate_table_cases=len(allrows),pair_cases=len(pairs),edge_counts={ed:len(es) for ed,es in edges.items()},edge_consequences=len(consequences),statuses=dict(Counter(r['status'] for r in allrows)),complete_cross_edition_lower=[{k:r[k] for k in ('direction','candidate_id','table')} for r in cross if r['lower']],complete_cross_edition_upper=[{k:r[k] for k in ('direction','candidate_id','table')} for r in cross if r['upper']],confirmed_words=0,independent_confirmation_leaves=0,significance_claim=False)
    dump('RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':
    import sys
    predict() if '--predict-only' in sys.argv else run()
