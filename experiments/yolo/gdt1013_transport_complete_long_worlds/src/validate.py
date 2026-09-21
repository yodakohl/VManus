from common import *
from worker import bounded
from run import check_witness
import itertools,concurrent.futures,collections,csv

def grammar_check(p,code,parsed,g):
    assert set(p['words'])<=code.keys();cursor=0;kinds=[]
    for cl in parsed:
        pat=g['patterns'][cl['kind']];assert cl['start']==cursor and cl['end']==cursor+len(pat);cursor=cl['end'];kinds.append(cl['kind'])
        assert cl['symbols']==[code[w] for w in p['words'][cl['start']:cl['end']]]
        for slot,sym in zip(pat,cl['symbols']):assert sym in (g['types'][slot[1:]] if slot.startswith('@') else [slot])
    assert cursor==len(p['words']) and kinds[0]=='INITIAL' and kinds[-1]=='CONCLUSION'
    for k in ['INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION']:assert kinds.count(k)==1

def independent_job(args):
    case,primary=args;s,g=inputs();p=read(A/'PANEL.json')[case['context_index']]
    other=bounded('independent',dict(paragraph=p,lexicon=case['canonical_lexicon'],variant=case['variant']))
    assert {primary['status'],other['status']}!={'sat','unsat'},case['id']
    if other['status']=='sat':other['witness_check']=check_witness(other['witness'])
    for r in [primary,other]:
        if r['status']=='sat':
            w=r['witness'];assert all(w['aliases'][k]==v for k,v in case['canonical_lexicon'].items()) and w['variant']==case['variant']
            grammar_check(p,w['aliases'],w['parse'],g)
    status='VERIFIED_SAT' if any(r['status']=='sat' and r['witness_check']['verified'] for r in [primary,other]) else 'VERIFIED_UNSAT' if primary['status']==other['status']=='unsat' else 'UNKNOWN'
    return dict(id=case['id'],primary_status=primary['status'],independent=other,status=status)

def lift_job(j):
    s,g=inputs();panel=read(A/'PANEL.json');case=j['case'];original=j['original'];w=j['witness'];inverse=j['inverse']
    renamed={k:inverse.get(v,v) for k,v in w['aliases'].items()};code={**original['code'],**renamed}
    assert all(code[k]==v for k,v in original['code'].items())
    parsed=[dict(c,symbols=[inverse.get(v,v) for v in c['symbols']]) for c in w['parse']]
    grammar_check(panel[0],code,original['parse'],g);grammar_check(panel[case['context_index']],code,parsed,g)
    results=[]
    for parse in [original['parse'],parsed]:
        a=bounded('replay',dict(parse=parse,variant=case['variant']));b=bounded('replay',dict(parse=parse,variant=case['variant'],independent=True))
        if a['status']==b['status']=='COMPLETE':
            assert a['result']==b['result'] and a['result']['status']=='COHERENT'
            result=a['result'];paths=[p for p in result['paths'] if p['consistent']]
            results.append(dict(status='VERIFIED_COHERENT',cargo=result['cargo'],hazards=result['hazards'],consistent_paths=len(paths),voyage_counts=sorted({len(p['trace'])-1 for p in paths}),example_trace=paths[0]['trace']))
        else:results.append(dict(status='UNKNOWN_REPLAY',primary=a['status'],independent=b['status']))
    if results[0]['status']=='VERIFIED_COHERENT':assert len(results[0]['cargo'])==3 and len(results[0]['hazards'])==2 and 7 in results[0]['voyage_counts']
    return dict(case=case['id'],engine=j['engine'],original_id=original['id'],context_index=case['context_index'],variant_index=case['variant_index'],canonical_to_original=inverse,code_sha256=hashlib.sha256(json.dumps(code,sort_keys=True).encode()).hexdigest(),status='VERIFIED_SHARED_READING' if all(r['status']=='VERIFIED_COHERENT' for r in results) else 'UNKNOWN_REPLAY',worlds=results)

def main():
    checklock();s,g=inputs();panel=read(A/'PANEL.json');cases=read(A/'PREDICTIONS.json');primary=read(A/'ROWS.json');originals=read(A/'ORIGINAL_CANDIDATES.json');assert panel==read(R/s['source_panel']) and cases==read(R/s['source_cases']) and originals==read(R/s['source_candidates'])
    original={r['id']:r for r in originals};membership=[];settings=[dict(zip(g['variants'],v)) for v in itertools.product(*g['variants'].values())]
    assert len(cases)==20 and len(primary)==20 and [r['id'] for r in primary]==[r['id'] for r in cases]
    for case in cases:
        assert case['variant']==settings[case['variant_index']]
        for m in case['members']:
            row=original[m['original_id']];shared={w:row['code'][w] for w in set(row['code'])&set(panel[case['context_index']]['words'])};assert set(shared)==set(case['canonical_lexicon'])
            matches=[dict(zip(('C','G','W'),v)) for v in itertools.permutations(('C','G','W')) if {w:dict(zip(('C','G','W'),v)).get(x,x) for w,x in shared.items()}==case['canonical_lexicon']]
            assert matches==m['original_to_canonical'] and case['variant_index'] in row['valid_variants'];membership.append((row['id'],case['context_index'],case['variant_index']))
    expected=[(r['id'],pi,vi) for r in originals for pi in (2,4) for vi in r['valid_variants']]
    assert collections.Counter(membership)==collections.Counter(expected) and len(membership)==312
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:checks=list(pool.map(independent_job,zip(cases,primary)))
    put('INDEPENDENT.json',checks)
    jobs=[]
    for case,p,check in zip(cases,primary,checks):
        for engine,r in [('primary',p),('independent',check['independent'])]:
            if r['status']=='sat' and r['witness_check']['verified']:
                for m in case['members']:
                    for rename in m['original_to_canonical']:jobs.append(dict(case=case,engine=engine,witness=r['witness'],original=original[m['original_id']],inverse={v:k for k,v in rename.items()}))
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:lifts=list(pool.map(lift_job,jobs))
    put('LIFT_CHECKS.json',lifts)
    with (A/'CANONICAL_RESULTS.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['case','context_index','class','variant','original_members','primary','independent','decision','independent_meaning_capacity'])
        for c,p,x in zip(cases,primary,checks):w.writerow([c['id'],c['context_index'],c['class_name'],c['variant_index'],len(c['members']),p['status'],x['independent']['status'],x['status'],0])
    candidate_rows=[]
    for case,check in zip(cases,checks):
        for m in case['members']:
            my=[r for r in lifts if r['case']==case['id'] and r['original_id']==m['original_id']]
            verdict='VERIFIED_SHARED_READING' if any(r['status']=='VERIFIED_SHARED_READING' for r in my) else 'VERIFIED_UNSAT' if check['status']=='VERIFIED_UNSAT' else 'UNKNOWN'
            candidate_rows.append(dict(original=m['original_id'],context_index=case['context_index'],variant=case['variant_index'],case=case['id'],decision=verdict,lifted_witnesses=len(my),independent_meaning_capacity=0))
    assert len(candidate_rows)==312
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(candidate_rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(candidate_rows)
    result=dict(experiment='GDT1013',status='FULL_CONTENT_CASES_CHECKED',canonical_cases=20,canonical_decisions=dict(collections.Counter(r['status'] for r in checks)),original_setting_context_cases=312,candidate_decisions=dict(collections.Counter(r['decision'] for r in candidate_rows)),lifted_witnesses=len(lifts),verified_lifts=sum(r['status']=='VERIFIED_SHARED_READING' for r in lifts),unknown_lifts=sum(r['status']!='VERIFIED_SHARED_READING' for r in lifts),confirmed_words=0,independent_meaning_capacity=0,significance=False)
    put('RESULT.json',result);put('VALIDATION.json',dict(status='PASS',complete_population_checked=True,original_setting_cases=312,canonical_queries=20,counts=dict(collections.Counter(r['status'] for r in checks)),opposite_solver_answers=0,verified_lifts=result['verified_lifts'],unknown_lifts=result['unknown_lifts'],completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),confirmed_words=0))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
