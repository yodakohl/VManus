#!/usr/bin/env python3
"""Fixed post-exposure filter of already published whole figure keys."""
import csv,gzip,hashlib,itertools,json
from collections import defaultdict,Counter
from pathlib import Path
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[2]
OLD=ROOT/'experiments/yolo/gdt957_f66r_complete_geomantic_margin'
A=P/'artifacts'

def dump(name,obj):
    (A/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

def tab(name,rows):
    with (A/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)

def main():
    for rel,h in json.loads((P/'PREREG_LOCK.json').read_text()).items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
    src=json.loads((P/'src/SOURCE.json').read_text())
    target=json.loads((OLD/'artifacts/TARGET_RECORDS.json').read_text())
    cases=json.loads((OLD/'artifacts/ALL_CASES.json').read_text())
    names={x['value']:x['name'] for x in json.loads((OLD/'src/SOURCE.json').read_text())['figures']}
    records={ed:sorted([r for r in target if r['edition']==ed],key=lambda r:r['position_top_down']) for ed in ('ZL3b','IT2a','RF1b')}
    families={}
    for ed,rs in records.items():
        bins=defaultdict(list)
        for r in rs:
            if r['state']=='KNOWN' and len(r['raw'])>=2:
                assert r['raw'].isascii() and r['raw'].isalpha() and r['raw'].islower()
                bins[r['raw'][1:]].append({'position':r['position_top_down'],'raw':r['raw'],'initial':r['raw'][0]})
        families[ed]=[{'remainder':rem,'members':xs} for rem,xs in sorted(bins.items()) if len({x['initial'] for x in xs})>=2]
    dump('TARGET_RECORDS.json',target);dump('ALL_FAMILIES.json',families)
    with gzip.open(OLD/'artifacts/ALL_SURVIVING_CALCULATIONS.tsv.gz','rt') as f:
        charts={(r['case'],int(r['candidate_id'])):[int(r['figure_'+str(i)]) for i in range(1,16)] for r in csv.DictReader(f,delimiter='\t')}
    allrows=[];frows=[]
    for case in cases:
        ed=case['edition'];direction=case['direction']
        for cid in case['surviving_ids']:
            fig=charts[case['case'],cid]
            if direction=='BOTTOM_UP':fig=fig[::-1]
            for table,ts in src['tables'].items():
                elements=[ts['elements'][v] for v in fig]
                fs=[]
                for fam in families[ed]:
                    pos=[m['position'] for m in fam['members']]
                    vals=[fig[i-1] for i in pos]; es=[elements[i-1] for i in pos]
                    known={e for e in es if e is not None}
                    fs.append({'remainder':fam['remainder'],'positions':pos,'raw_forms':[m['raw'] for m in fam['members']],'figures':vals,'names':[names[v] for v in vals],'elements':es,'explicit_conflict':len(known)>1,'unknown_members':es.count(None)})
                lower=bool(fs) and all(not s['explicit_conflict'] and s['unknown_members']==0 for s in fs)
                completions=[]
                for completion in src['uncertainty']['upper_completions']:
                    if fs and all(len({completion if e is None else e for e in s['elements']})==1 for s in fs):completions.append(completion)
                upper=bool(completions)
                status='NO_CAPACITY' if not fs else 'COMPATIBLE_KNOWN_FAMILIES' if lower else 'UNKNOWN_ONLY' if upper else 'CONTRADICTED'
                row={'case':case['case'],'edition':ed,'direction':direction,'candidate_id':cid,'table':table,'figures':fig,'names':[names[v] for v in fig],'elements':elements,'lower':lower,'upper':upper,'status':status,'source_unknown_completions':completions if None in ts['elements'] else [],'family_results':fs,'unknown_target_labels':sum(r['state']!='KNOWN' for r in records[ed]),'physical_leaves':1,'independent_confirmation_leaves':0}
                allrows.append(row)
                for s in fs:
                    frows.append({'case':case['case'],'candidate_id':cid,'table':table,'remainder':s['remainder'],'positions':','.join(map(str,s['positions'])),'raw_forms':' | '.join(s['raw_forms']),'predicted_figure_names':' | '.join(s['names']),'predicted_elements':' | '.join(e or 'UNKNOWN' for e in s['elements']),'explicit_conflict':s['explicit_conflict'],'unknown_members':s['unknown_members'],'candidate_status':status})
    assert len(allrows)==1128
    dump('ALL_CANDIDATES.json',allrows);tab('ALL_FAMILY_CONSEQUENCES.tsv',frows)
    lookup={(r['edition'],r['direction'],r['candidate_id'],r['table']):r for r in allrows}
    robust=[]
    for r in allrows:
        if r['edition']!='IT2a':continue
        linked=[lookup.get((ed,r['direction'],r['candidate_id'],r['table'])) for ed in ('ZL3b','IT2a','RF1b')]
        robust.append({'direction':r['direction'],'candidate_id':r['candidate_id'],'table':r['table'],'all_editions_present':all(x is not None for x in linked),'lower':all(x is not None and x['lower'] for x in linked),'upper':all(x is not None and x['upper'] for x in linked),'edition_statuses':{ed:None if x is None else x['status'] for ed,x in zip(('ZL3b','IT2a','RF1b'),linked)},'figures':r['figures'],'names':r['names']})
    dump('COMPLETE_IT2A_CROSS_EDITION.json',robust)
    groups=defaultdict(list)
    for r in allrows:
        if r['upper']:
            groups[tuple(r['figures'])].append({'case':r['case'],'candidate_id':r['candidate_id'],'table':r['table'],'lower':r['lower'],'upper':r['upper']})
    dump('IDENTICAL_PHYSICAL_READINGS.json',[{'group_id':i+1,'figures':list(v),'names':[names[x] for x in v],'provenance':rs} for i,(v,rs) in enumerate(sorted(groups.items()))])
    marg=[]
    for population in ('IT2A_ONLY','CROSS_EDITION'):
        base=[r for r in allrows if r['edition']=='IT2a'] if population=='IT2A_ONLY' else robust
        for table in ('A','B','C','ANY_TABLE'):
            for bound in ('lower','upper'):
                selected=[r for r in base if (table=='ANY_TABLE' or r['table']==table) and r[bound]]
                readings={tuple(r['figures']) for r in selected}
                for i in range(15):
                    possible=sorted({x[i] for x in readings})
                    marg.append({'population':population,'table':table,'bound':bound,'physical_position':i+1,'distinct_complete_readings':len(readings),'possible_names':' | '.join(names[v] for v in possible),'number_of_names':len(possible)})
    tab('REMAINING_NAME_MARGINALS.tsv',marg)
    sums=[]
    for case in cases:
        for table in src['tables']:
            rs=[r for r in allrows if r['case']==case['case'] and r['table']==table]
            sums.append({'case':case['case'],'table':table,'candidates':len(rs),'lower':sum(r['lower'] for r in rs),'upper':sum(r['upper'] for r in rs),'contradicted':sum(r['status']=='CONTRADICTED' for r in rs),'unknown_only':sum(r['status']=='UNKNOWN_ONLY' for r in rs)})
    tab('SUMMARY.tsv',sums)
    result={'experiment_id':'GDT959','status':'POST_EXPOSURE_LOCAL_CLASS_HYPOTHESIS_UNIDENTIFIED','candidate_table_cases':len(allrows),'family_consequences':len(frows),'families':families,'summary':sums,'complete_cross_edition_lower':[{'direction':r['direction'],'candidate_id':r['candidate_id'],'table':r['table']} for r in robust if r['lower']],'complete_cross_edition_upper':[{'direction':r['direction'],'candidate_id':r['candidate_id'],'table':r['table']} for r in robust if r['upper']],'physical_leaves':1,'independent_confirmation_leaves':0,'confirmed_words':0,'significance':'NOT_ASSESSED_POST_SELECTED_SEARCH','no_candidate_key_changed':True}
    dump('RESULT.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('summary','families')},indent=2))
if __name__=='__main__':main()
