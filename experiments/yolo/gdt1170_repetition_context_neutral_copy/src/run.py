#!/usr/bin/env python3
import argparse,collections,csv,datetime,hashlib,io,json,re,subprocess
from pathlib import Path
import numpy as np
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x): (E/'artifacts'/n).write_text(json.dumps(x,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cached',action='store_true');a=ap.parse_args()
    s=json.loads((E/'src/SPEC.json').read_text());lock=json.loads((E/'artifacts/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items(): assert sha(E/p)==h
    assert sha(ROOT/s['allowlist'])==s['allowlist_sha256']
    source=E/'artifacts/GUARDED.tsv'
    if not a.cached:
        cmd=['./vmanus-exp','query-tsv',s['source'],'--selector','page']
        for p in s['allowed']:cmd+=['--allow',p]
        cmd+=['--columns',','.join(s['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']
        result=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
        guards=[json.loads(x.removeprefix('GUARD_STATS ')) for x in result.stderr.splitlines() if x.startswith('GUARD_STATS ')]
        assert len(guards)==1
        source.write_text(result.stdout)
        save('GUARD.json',{'command':cmd,'stats':guards[0],'sha256':sha(source),'intake_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    guard=json.loads((E/'artifacts/GUARD.json').read_text());assert sha(source)==guard['sha256']
    by=collections.defaultdict(list)
    for row in csv.DictReader(source.open(),delimiter='\t'):
        assert row['page'] in s['allowed'] and not row['page'].startswith('f84')
        by[row['edition'],row['locus']].append(row)
    assert sum(map(len,by.values()))==guard['stats']['selected']
    runs=[];excluded=[];counts=collections.defaultdict(collections.Counter)
    for (ed,loc),rows in sorted(by.items()):
        if rows[0]['kind']!='P':continue
        rows.sort(key=lambda r:int(r['source_group_index']));n=len(rows)
        assert n==int(rows[0]['source_group_count'])
        assert [int(r['source_group_index']) for r in rows]==list(range(1,n+1))
        counts[ed]['prose_lines']+=1
        def linked(a,b):return a['right_separator']==b['left_separator']=='DEFINITE_SPACE'
        i=0
        while i<n:
            if not re.fullmatch('[a-z]+',rows[i]['ivtff_group_raw']): i+=1;continue
            j=i+1
            while j<n and linked(rows[j-1],rows[j]) and rows[j]['ivtff_group_raw']==rows[i]['ivtff_group_raw']:j+=1
            length=j-i;word=rows[i]['ivtff_group_raw']
            if length>2:excluded.append({'edition':ed,'locus':loc,'start':i+1,'word':word,'length':length})
            if length in (1,2) and i>0 and j<n and linked(rows[i-1],rows[i]) and linked(rows[j-1],rows[j]) and all(re.fullmatch('[a-z]+',rows[k]['ivtff_group_raw']) for k in (i-1,j)):
                # Maximality inside a definite-space segment was determined above.
                page=rows[i]['page'];leaf=re.match(r'f[0-9]+',page)[0];pos=min(2,int(3*(i+(length-1)/2)/n))
                runs.append({'edition':ed,'page':page,'leaf':leaf,'locus':loc,'start':i+1,'length':length,'position_bin':pos,'word':word,'left':rows[i-1]['ivtff_group_raw'],'right':rows[j]['ivtff_group_raw']})
                counts[ed]['eligible_'+str(length)]+=1
            i=j
    columns=['edition','page','leaf','locus','start','length','position_bin','word','left','right']
    with (E/'artifacts/RUNS.tsv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=columns,delimiter='\t');w.writeheader();w.writerows(runs)
    save('LONGER_RUNS.json',excluded)
    output={'registered_utc':s['registered_utc'],'source_sha256':sha(source),'editions':{},'independent_confirmation_leaves':0,'confirmed_words':0,'claim_ceiling':'Conditional exchangeability diagnostic only; no translation, general error mechanism exclusion, or search-wide significance.'}
    for ed in s['editions']:
        strata=collections.defaultdict(list)
        for r in runs:
            if r['edition']==ed:strata[r['word'],r['leaf'],r['position_bin']].append(r)
        strata={k:v for k,v in strata.items() if {r['length'] for r in v}=={1,2}}
        rr=[r for v in strata.values() for r in v];doubles=[r for r in rr if r['length']==2]
        capacity={'strata':len(strata),'matched_runs':len(rr),'double_runs':len(doubles),'leaves':len({r['leaf'] for r in rr}),'words':len({r['word'] for r in rr})}
        entry={'counts':dict(counts[ed]),'capacity':capacity,'longer_runs':sum(r['edition']==ed for r in excluded)};output['editions'][ed]=entry
        if len(doubles)<s['minimum_doubles'] or capacity['leaves']<s['minimum_leaves']:
            entry['status']='INSUFFICIENT_MATCHED_CAPACITY';continue
        rng=np.random.default_rng(s['seed']);scores=np.zeros((s['permutations']+1,2))
        for key,group in sorted(strata.items()):
            y=np.array([r['length']==2 for r in group],dtype=float);z=y-y.mean();denom=z@z
            Z=np.empty((s['permutations']+1,len(y)));Z[0]=z
            for b in range(1,len(Z)):Z[b]=rng.permutation(z)
            for side_idx,side in enumerate(('left','right')):
                features=[{('^'+r[side]+'$')[i:i+2] for i in range(len(r[side])+1)} for r in group]
                vocab={g:i for i,g in enumerate(sorted(set.union(*features)))}
                F=np.zeros((len(y),len(vocab)))
                for i,fs in enumerate(features):
                    for g in fs:F[i,vocab[g]]=1/np.sqrt(len(fs))
                U=Z@F;scores[:,side_idx]+=np.einsum('ij,ij->i',U,U)/denom
        scores=np.column_stack((scores,scores[:,1]-scores[:,0]));mu=scores[1:].mean(axis=0);sd=scores[1:].std(axis=0,ddof=1)
        standard=(scores-mu)/np.where(sd>0,sd,1);mx=standard.max(axis=1)
        stats={}
        for j,name in enumerate(s['statistics']):
            stats[name]={'observed':float(scores[0,j]),'null_mean':float(mu[j]),'null_sd':float(sd[j]),'standardized':float(standard[0,j]),'max_calibrated_upper_fraction':float((1+np.sum(mx[1:]>=standard[0,j]))/len(mx))}
        entry.update(status='EVALUATED',statistics=stats)
        with (E/'artifacts'/('NULL_'+ed+'.tsv')).open('w') as f:
            f.write('draw\tleft\tright\tright_minus_left\n')
            for i,row in enumerate(scores):f.write(str(i)+'\t'+'\t'.join(format(x,'.15g') for x in row)+'\n')
    qualifying=[]
    for stat in s['statistics']:
        if all(output['editions'][ed]['status']=='EVALUATED' and output['editions'][ed]['statistics'][stat]['max_calibrated_upper_fraction']<=.01 for ed in ('IT2a','ZL3b')):qualifying.append(stat)
    output['retained_statistics']=qualifying
    output['status']='EXPLORATORY_CONTEXT_SIGNAL' if qualifying else ('INSUFFICIENT_PRIMARY_CAPACITY' if any(output['editions'][e]['status']!='EVALUATED' for e in ('IT2a','ZL3b')) else 'NO_RETAINED_CONTEXT_SIGNAL')
    output['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('RESULT.json',output);print(json.dumps(output,indent=2))
if __name__=='__main__':main()
