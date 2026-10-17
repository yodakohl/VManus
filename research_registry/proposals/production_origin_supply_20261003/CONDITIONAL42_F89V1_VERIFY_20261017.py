#!/usr/bin/env python3
"""Independent source and positive-Horn bookkeeping, not a meaning test."""
import hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
PLAN=HERE/'CONDITIONAL42_F89V1_PLAN_20261017.json'
DERIVATION=HERE/'CONDITIONAL42_F89V1_DERIVATION_20261017.json'
OUT=HERE/'CONDITIONAL42_F89V1_VERIFICATION_20261017.json'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sid(r):return f"{r['edition']}|{r['locus']}|G{int(r['source_group_index']):03d}"
def opener(r):return r['ivtff_group_raw'].startswith('q') and len(r['ivtff_group_raw'])>1
def build(rows):
    # Partition into maximal equal-kind runs, rather than a per-token parser state.
    runs=[(q,list(v)) for q,v in itertools.groupby(rows,key=opener)]
    facts=[]; trace=[]; clauses=[]
    if runs and not runs[0][0]:
        _,initial=runs.pop(0);facts=[r['ivtff_group_raw'] for r in initial]
        trace.extend({'source':r,'id':sid(r),'role':'fact','clause':None,'predicate':r['ivtff_group_raw']} for r in initial)
    assert len(runs)%2==0,'Final antecedent run has no consequent'
    for j in range(0,len(runs),2):
        isq,heads=runs[j];isb,body=runs[j+1];assert isq and not isb
        n=len(clauses)+1
        clauses.append({'id':n,'antecedents':[r['ivtff_group_raw'][1:] for r in heads],'antecedent_ids':[sid(r) for r in heads],'body':[r['ivtff_group_raw'] for r in body],'body_ids':[sid(r) for r in body]})
        for role,rs in [('antecedent',heads),('consequent',body)]:
            trace.extend({'source':r,'id':sid(r),'role':role,'clause':n,'predicate':r['ivtff_group_raw'][1:] if role=='antecedent' else r['ivtff_group_raw']} for r in rs)
    return facts,trace,clauses

def closure(seed,clauses):
    # Finite bitsets with synchronous rounds: conjunction of antecedents is mandatory.
    labels=sorted(set(seed)|{v for c in clauses for k in ['antecedents','body'] for v in c[k]})
    ix={v:1<<i for i,v in enumerate(labels)}
    def mask(vs):
        m=0
        for v in vs:m|=ix[v]
        return m
    value=mask(seed);rules=[(mask(c['antecedents']),mask(c['body'])) for c in clauses]
    while True:
        new=value
        for left,right in rules:
            if value&left==left:new|=right
        if new==value:break
        value=new
    return {v for v in labels if value&ix[v]}

def main():
    assert DERIVATION.exists(),'Await primary derivation; no result created'
    plan=json.loads(PLAN.read_text());source=ROOT/plan['source']['path'];assert digest(source)==plan['source']['sha256']
    raw=json.loads(source.read_text())['query']['rows'];result=json.loads(DERIVATION.read_text());assert result['source_sha256']==digest(source);assert result['primary_edition']=='IT2a'
    readers=sorted({r['edition'] for r in raw});assert set(result['readers'])==set(readers)
    summaries={};own={};expected={}
    for ed in readers:
        rows=[r for r in raw if r['edition']==ed]
        assert set(r['locus'] for r in rows)==set(plan['rules']['window'])
        assert len({sid(r) for r in rows})==len(rows)
        facts,trace,clauses=build(rows);expected[ed]=(facts,trace,clauses)
        got=result['readers'][ed]
        assert got['trace']==trace,ed+' exact trace mismatch'
        assert got['facts']==facts,ed+' facts mismatch'
        assert len(got['clauses'])==len(clauses)
        for actual,want in zip(got['clauses'],clauses):
            for key,value in want.items():assert actual[key]==value,(ed,key)
        flags={}
        for r in rows:
            flags.setdefault(r['locus'],[r['paragraph_start'],r['paragraph_end']]);assert flags[r['locus']]==[r['paragraph_start'],r['paragraph_end']]
        assert got['own_paragraph_flags']==[{'locus':loc,'start':[v[0]],'end':[v[1]]} for loc,v in flags.items()],ed+' serialized own flags mismatch'
        own[ed]=flags
        summaries[ed]={'groups':len(rows),'facts':len(facts),'clauses':len(clauses),'q_occurrences':sum(opener(r) for r in rows),'q_types':len({r['ivtff_group_raw'] for r in rows if opener(r)}),'body_counts':[len(c['body']) for c in clauses],'own_start_flags':sum(v[0]=='1' for v in flags.values()),'own_end_flags':sum(v[1]=='1' for v in flags.values())}
    f,t,c=expected['IT2a'];p=result['primary'];sm=summaries['IT2a']
    for key in ['groups','facts','clauses','q_types','body_counts']:assert p[key]==sm[key],key
    assert sm['groups']==78 and sm['facts']==6 and sm['clauses']==7 and sm['q_occurrences']==7 and sm['q_types']==6
    assert sm['body_counts']==[24,1,17,1,3,7,12]
    labels={r['predicate'] for r in t};assert p['predicate_types']==len(labels)
    for seed,claimed in p['conditional_closures'].items():assert set(claimed)==closure(f+[seed],c),seed
    assert set(p['fact_closure'])==closure(f,c)
    wanted=plan['rules']['expected_paths'];actualpaths={tuple(z['symbols']):z for z in p['paths']}
    byid={z['id']:z for z in c}
    for path in wanted:
        assert tuple(path) in actualpaths,path
        assert path[-1] in closure([path[0]],c)
    for path in p['paths']:
        ss=path['symbols'];cs=path['clauses'];assert len(cs)==len(ss)-1
        for left,right,ci in zip(ss,ss[1:],cs):
            rule=byid[ci];assert rule['antecedents']==[left] and right in rule['body']
    # No conditional antecedent is promoted to an actual unconditional fact.
    assert set(p['fact_closure'])==set(f)
    assert 'ockhy' not in closure(['ykchol'],c)
    assert 'otchy' not in closure(['cheol'],c)
    # Independent conjunction and non-entailment controls.
    demo=[{'antecedents':['a','b'],'body':['c']},{'antecedents':['c'],'body':['d']}]
    assert closure(['a'],demo)=={'a'} and closure(['a','b'],demo)=={'a','b','c','d'}
    assert 'a' not in closure(['d'],demo)
    report={'status':'PASS_INDEPENDENT_SOURCE_AND_CONDITIONAL_LOGIC_ONLY','source_sha256':digest(source),'derivation_sha256':digest(DERIVATION),'plan_sha256':digest(PLAN),'validator_sha256':digest(Path(__file__)),'reader_accounting':summaries,'conditional_closure_seed':'six unconditional facts plus one stated antecedent; no other antecedent assumed','validator_preoutput_correction':'Initial checker expected antecedent-only closure; producer includes unconditional facts. Initial mismatch was exactly the six facts. Corrected checker uses full-theory closure; no producer or scientific rule changed.','own_source_flags':own,'verified_primary_paths':wanted,'primary_fact_closure':sorted(closure(f,c)),'checks':['Every source row including all separators, annotations, own flags and original order preserved','Maximal consecutive q runs independently grouped; no clause crosses a reader window','All scope assignments, all clause arguments and all consequence multiplicities reconstructed','Positive Horn closure computed with independent synchronous bitsets','Every serialized path checked against actual source-bound clause edges','No reverse implications inferred and no condition promoted to an actual fact','IT/ZL own flags and RF raw flags retained without pooling'],'limits':['This verifies bookkeeping under unproved unary-predicate, same-subject and literal-q scope assumptions; no lexical meaning or global grammar selected.','Positive Horn consistency is automatic, not semantic confirmation. Repeated predicates remain in source although closure is set-valued.','RF is only the corresponding exposed window: its zero own boundary flags cannot authenticate paragraph scope.','No new source, image, statistical test, reserved data or primary-code import.']}
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':report['status'],'reader_accounting':summaries}))
if __name__=='__main__':main()
