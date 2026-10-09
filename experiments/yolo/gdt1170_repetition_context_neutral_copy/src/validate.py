#!/usr/bin/env python3
"""Independent guarded-artifact, Gram-kernel and permutation audit; no runner import."""
from pathlib import Path
import collections,csv,hashlib,itertools,json,math,re
import numpy as np
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def link(a,b):return a['right_separator']=='DEFINITE_SPACE'==b['left_separator']
def extract(ed,loc,rows):
    n=len(rows);segments=[];seg=[];runs=[];longer=[]
    for i,r in enumerate(rows):
        if re.fullmatch('[a-z]+',r['ivtff_group_raw']) is None:
            if seg:segments.append(seg)
            seg=[];continue
        if seg and not link(rows[seg[-1]],r):segments.append(seg);seg=[]
        seg.append(i)
    if seg:segments.append(seg)
    for seg in segments:
        blocks=[list(v) for _,v in itertools.groupby(seg,key=lambda i:rows[i]['ivtff_group_raw'])]
        for k,b in enumerate(blocks):
            start=b[0];length=len(b);word=rows[start]['ivtff_group_raw']
            if length>2:longer.append(dict(edition=ed,locus=loc,start=start+1,word=word,length=length))
            if k in (0,len(blocks)-1) or length not in (1,2):continue
            page=rows[start]['page']
            runs.append(dict(edition=ed,page=page,leaf=re.match(r'f\d+',page)[0],locus=loc,start=start+1,
                length=length,position_bin=min(2,(6*start+3*(length-1))//(2*n)),word=word,
                left=rows[start-1]['ivtff_group_raw'],right=rows[b[-1]+1]['ivtff_group_raw']))
    return runs,longer
def gram(words):
    sets=[]
    for w in words:
        marked='^'+w+'$';sets.append(set(zip(marked[:-1],marked[1:])))
    return np.array([[len(a&b)/math.sqrt(len(a)*len(b)) for b in sets] for a in sets])
def close(a,b):return bool(np.allclose(a,b,rtol=1e-10,atol=1e-9))
def fixtures():
    def rows(words,broken=None):
        r=[dict(ivtff_group_raw=w,page='f2r',left_separator='DEFINITE_SPACE',right_separator='DEFINITE_SPACE') for w in words]
        r[0]['left_separator']='LINE_START';r[-1]['right_separator']='LINE_END'
        if broken is not None:r[broken]['right_separator']='UNCERTAIN_SPACE';r[broken+1]['left_separator']='UNCERTAIN_SPACE'
        return r
    a,l=extract('IT2a','fixture',rows(['a','x','x','b']))
    assert len(a)==1 and a[0]['length']==2 and (a[0]['left'],a[0]['right'])==('a','b')
    assert not extract('IT2a','fixture',rows(['a','x','x','b'],1))[0]
    assert not extract('IT2a','fixture',rows(['a','x','@221;','b']))[0]
    a,l=extract('IT2a','fixture',rows(['a','x','x','x','b']));assert not a and l[0]['length']==3
    assert not extract('IT2a','fixture',rows(['x','x','b']))[0]
    k=gram(['a','b']);z=np.array([-.5,.5]);assert close(z@k@z,(-z)@k@(-z))
    return 6

def main():
    checks=[]
    def check(name,ok):checks.append(dict(check=name,passed=bool(ok)))
    s=load(E/'src/SPEC.json');lock=load(E/'artifacts/REGISTRATION_LOCK.json');g=load(E/'artifacts/GUARD.json');result=load(E/'artifacts/RESULT.json')
    check('registered_bytes',all(sha(E/p)==h for p,h in lock['files'].items()))
    check('allowlist_pin',sha(ROOT/s['allowlist'])==s['allowlist_sha256'])
    check('guarded_pin',sha(E/'artifacts/GUARDED.tsv')==g['sha256']==result['source_sha256'])
    check('recorded_chronology',s['registered_utc']==lock['registered_utc']==result['registered_utc'] and s['registered_utc']<g['intake_utc']<=result['completed_utc'])
    source=list(csv.DictReader((E/'artifacts/GUARDED.tsv').open(),delimiter='\t'))
    check('guard_scope_columns',len(source)==g['stats']['selected'] and list(source[0])==s['columns'] and all(r['page'] in s['allowed'] and not r['page'].startswith(('f84','f116v')) and r['edition'] in s['editions'] for r in source))
    command=['./vmanus-exp','query-tsv',s['source'],'--selector','page']
    for p in s['allowed']:command.extend(['--allow',p])
    command.extend(['--columns',','.join(s['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r'])
    check('guard_command',command==g['command'])
    by=collections.defaultdict(list)
    for row in source:by[row['edition'],row['locus']].append(row)
    runs=[];longer=[];counts=collections.defaultdict(collections.Counter);indexes_ok=True
    for (ed,loc),rows in sorted(by.items()):
        rows.sort(key=lambda r:int(r['source_group_index']));n=len(rows)
        indexes_ok &= ([int(r['source_group_index']) for r in rows]==list(range(1,n+1)) and all(int(r['source_group_count'])==n for r in rows) and len({(r['page'],r['kind']) for r in rows})==1)
        if rows[0]['kind']!='P':continue
        counts[ed]['prose_lines']+=1;a,l=extract(ed,loc,rows);runs.extend(a);longer.extend(l)
        for row in a:counts[ed]['eligible_'+str(row['length'])]+=1
    check('complete_source_loci',indexes_ok)
    actual=list(csv.DictReader((E/'artifacts/RUNS.tsv').open(),delimiter='\t'))
    check('every_eligible_run_exact',actual==[{k:str(v) for k,v in r.items()} for r in runs])
    check('every_longer_run_exact',load(E/'artifacts/LONGER_RUNS.json')==longer)
    check('independent_fixtures',fixtures()==6)
    audit={};fractions={}
    for ed in s['editions']:
        allgroups=collections.defaultdict(list)
        for r in runs:
            if r['edition']==ed:allgroups[r['word'],r['leaf'],r['position_bin']].append(r)
        groups={k:v for k,v in allgroups.items() if len({r['length'] for r in v})==2}
        rr=[r for v in groups.values() for r in v];ds=sum(r['length']==2 for r in rr)
        cap=dict(strata=len(groups),matched_runs=len(rr),double_runs=ds,leaves=len({r['leaf'] for r in rr}),words=len({r['word'] for r in rr}))
        entry=result['editions'][ed]
        check(ed+'_counts_capacity',dict(counts[ed])==entry['counts'] and cap==entry['capacity'] and sum(r['edition']==ed for r in longer)==entry['longer_runs'])
        passing=ds>=s['minimum_doubles'] and cap['leaves']>=s['minimum_leaves']
        check(ed+'_capacity_status',entry['status']==('EVALUATED' if passing else 'INSUFFICIENT_MATCHED_CAPACITY'))
        n=s['permutations']+1;values=np.zeros((n,2));rng=np.random.default_rng(s['seed']);info=[set(),set(),set()];info_d=[0,0,0]
        for key,group in sorted(groups.items()):
            count=len(group);d=sum(r['length']==2 for r in group);denom=d*(count-d)/count
            z=np.array([float(r['length']==2)-d/count for r in group])
            labels=np.stack([z]+[rng.permutation(z) for _ in range(s['permutations'])])
            matrices=[gram([r[side] for r in group]) for side in ('left','right')]
            for side,k in enumerate(matrices):values[:,side]+=np.einsum('bi,ij,bj->b',labels,k,labels,optimize=True)/denom
            assert math.comb(count,d)<=20000,'unexpected large power enumeration'
            probe=[]
            for inds in itertools.combinations(range(count),d):
                v=np.full(count,-d/count);v[list(inds)]+=1
                t=[float(v@k@v/denom) for k in matrices];probe.append(t+[t[1]-t[0]])
            variation=np.ptp(np.array(probe),axis=0)
            for side in range(3):
                if variation[side]>1e-10:info[side].add(key);info_d[side]+=d
        audit[ed]=dict(nominal_strata=len(groups),balanced_two_run_invariant_strata=sum(len(v)==2 for v in groups.values()),
            permutation_informative_strata=dict(zip(s['statistics'],map(len,info))),doubles_in_informative_strata=dict(zip(s['statistics'],info_d)),
            union_informative_strata=len(set.union(*info)),power_audit='All legal fixed-count assignments enumerated per stratum; variation tolerance1e-10.')
        if not passing:continue
        values=np.column_stack([values,values[:,1]-values[:,0]])
        saved=list(csv.DictReader((E/'artifacts'/('NULL_'+ed+'.tsv')).open(),delimiter='\t'))
        draws=np.array([[float(r[k]) for k in s['statistics']] for r in saved])
        check(ed+'_every_shuffle_score',len(saved)==n and [int(r['draw']) for r in saved]==list(range(n)) and close(values,draws))
        means=draws[1:].mean(axis=0);sd=draws[1:].std(axis=0,ddof=1);standard=(draws-means)/np.where(sd>0,sd,1);maximum=standard[1:].max(axis=1)
        fractions[ed]={}
        for j,name in enumerate(s['statistics']):
            frac=(1+int(np.count_nonzero(maximum>=standard[0,j])))/n;fractions[ed][name]=frac;t=entry['statistics'][name]
            check(ed+'_'+name+'_score_calibration',close(values[0,j],t['observed']) and close(means[j],t['null_mean']) and close(sd[j],t['null_sd']) and close(standard[0,j],t['standardized']) and frac==t['max_calibrated_upper_fraction'])
    retained=[stat for stat in s['statistics'] if all(ed in fractions and fractions[ed][stat]<=.01 for ed in ('IT2a','ZL3b'))]
    status='EXPLORATORY_CONTEXT_SIGNAL' if retained else ('INSUFFICIENT_PRIMARY_CAPACITY' if any(ed not in fractions for ed in ('IT2a','ZL3b')) else 'NO_RETAINED_CONTEXT_SIGNAL')
    check('joint_gate_status',retained==result['retained_statistics'] and status==result['status'])
    check('meaning_confirmation_ceiling',result['confirmed_words']==result['independent_confirmation_leaves']==0)
    paths=['artifacts/GUARDED.tsv','artifacts/RUNS.tsv','artifacts/LONGER_RUNS.json','artifacts/RESULT.json']+[f'artifacts/NULL_{ed}.tsv' for ed in s['editions']]
    out=dict(status='PASS' if all(c['passed'] for c in checks) else 'FAIL',independent_of_runner=True,checks=checks,source_rows=len(source),eligible_runs=len(runs),power=audit,result_status=result['status'],
        limits=['Conditional exchangeability on exposed alternate readings, not translation or a general copying-mechanism test.',
        'Nominal capacity includes permutation-invariant strata; informative counts reported separately.',
        'Recorded chronology and guarded artifact audited without a new source query.',
        'NumPy fixed-count permutations independently replayed; not independent manuscript witnesses.',
        'Upper-tail right-minus-left tests only the registered direction, not every possible asymmetry.'],validator_sha256=sha(Path(__file__)),audited_artifact_sha256={p:sha(E/p) for p in paths})
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(status=out['status'],checks=len(checks),failures=[c['check'] for c in checks if not c['passed']],power=audit),indent=2))
    return 0 if out['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
