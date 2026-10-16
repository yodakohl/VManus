"""Frozen whole-form score conditional on complete symbol bags."""
from pathlib import Path
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError as FutureTimeout
from itertools import permutations
import argparse, bisect, gzip, hashlib, json, math, random, time

BASE=Path(__file__).resolve().parents[1]; ROOT=BASE.parents[2]; ART=BASE/'artifacts'
SPEC=BASE/'src/SPEC.json'; LOCK=BASE/'src/REGISTRATION_LOCK.json'


def read(p):
    raw=Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def save(name,value):
    raw=(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
    (ART/name).write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Stop(Exception):pass


def transition_table(rows,c,n,signs):
    inventory={tuple(r['context']):r['counts'] for r in rows}
    table=[]
    for position in range(n):
        layer=[]
        for previous in list(signs)+['^']:
            counts=inventory.get((c,n,position,previous),{})
            denom=sum(counts.values())+.5*len(signs)
            layer.append([math.log((counts.get(s,0)+.5)/denom) for s in signs])
        table.append(layer)
    return table


def word_log_probability(units,table,signs):
    ids={s:i for i,s in enumerate(signs)};prev=len(signs);terms=[]
    for i,s in enumerate(units):
        j=ids[s];terms.append(table[i][prev][j]);prev=j
    return math.fsum(terms)


def cell_masses(job):
    started=time.monotonic();signs=job['signs'];n=job['n'];table=transition_table(job['rows'],job['c'],n,signs)
    width=max(1,n.bit_length());mask=(1<<width)-1;shifts=[width*j for j in range(len(signs))];memo={}
    def mass(code,previous,left):
        if not code:return 0.0
        key=(code,previous)
        if key in memo:return memo[key]
        if len(memo)>=job['max_states']:raise Stop('CELL_STATE_LIMIT')
        if len(memo)%256==0 and time.monotonic()>job['deadline']:raise Stop('NORMALIZER_WALL_LIMIT')
        position=n-left;values=[]
        for j,shift in enumerate(shifts):
            if (code>>shift)&mask:
                values.append(table[position][previous][j]+mass(code-(1<<shift),j,left-1))
        largest=max(values);answer=largest+math.log(math.fsum(math.exp(v-largest) for v in values))
        if len(memo)>=job['max_states']:raise Stop('CELL_STATE_LIMIT')
        memo[key]=answer;return answer
    output=[]
    for counts in job['bags']:
        code=sum(v<<shift for v,shift in zip(counts,shifts))
        output.append(dict(counts=counts,log_P_B=mass(code,len(signs),n)))
    return dict(cell=job['cell'],masses=output,states=len(memo),seconds=time.monotonic()-started)


def category_certificate(support,log_pb,qb,tol):
    offset=math.log1p(qb/math.exp(log_pb));cats=[];clamps=[]
    for item in support:
        item['mass']=math.exp(math.log(item['p'])-log_pb)
        item['R']=math.log1p(item['q']/item['p'])-offset
        cats.append(dict(kind='TRAIN',units=item['units'],mass=item['mass'],R=item['R']))
    remainder=1-math.fsum(x['mass'] for x in cats)
    if remainder<0:
        if remainder < -tol:raise Stop('NEGATIVE_RESIDUAL_MASS')
        clamps.append(dict(quantity='residual_mass',before=remainder,after=0.0));remainder=0.0
    cats.append(dict(kind='RESIDUAL',units=None,mass=remainder,R=-offset))
    mean=math.fsum(x['mass']*x['R'] for x in cats)
    variance=math.fsum(x['mass']*(x['R']-mean)**2 for x in cats)
    norm=math.fsum(x['mass']*math.exp(x['R']) for x in cats)
    if abs(norm-1)>tol or abs(math.fsum(x['mass'] for x in cats)-1)>tol:raise Stop('CONDITIONAL_NORMALIZATION')
    if mean>tol:raise Stop('POSITIVE_NULL_EXPECTED_LOG_LR')
    return cats,mean,variance,norm,clamps


def controls():
    signs=['a','b'];checked=0
    for n in [3,4]:
        rows=[dict(context=['C',n,i,p],counts={'a':1+i+(p=='a'),'b':2+(p=='b')})
              for i in range(n) for p in signs+['^']]
        bags=[[n,0],[n-1,1],[1,n-1],[n//2,n-n//2]]
        job=dict(signs=signs,n=n,c='C',rows=rows,bags=bags,cell=['toy','C',n],max_states=10000,deadline=time.monotonic()+10)
        result=cell_masses(job);table=transition_table(rows,'C',n,signs)
        for bag,answer in zip(bags,result['masses']):
            words=sorted(set(permutations('a'*bag[0]+'b'*bag[1])))
            ps=[math.exp(word_log_probability(w,table,signs)) for w in words];pb=math.fsum(ps)
            assert abs(math.exp(answer['log_P_B'])-pb)<1e-12
            for mode in ['zero','one','equal_conditional']:
                selected=[] if mode=='zero' else list(zip(words,ps))[:1] if mode=='one' else list(zip(words,ps))
                qb=0 if not selected else .2
                support=[dict(units=list(w),count=1,p=p,q=qb*p/math.fsum(t[1] for t in selected)) for w,p in selected]
                cats,mean,var,norm,clamps=category_certificate(support,math.log(pb),qb,1e-10)
                assert mean<=1e-10 and abs(norm-1)<1e-10
                if mode in ['zero','equal_conditional']:assert var<1e-12
                checked+=1
    return dict(status='PASS',enumerated_bag_masses=8,categorical_controls=checked,
                no_multiplicity_factor=True,unknown_word_residual=True,native_access=False)


def key(reader,c,n,counts):return reader+'|'+c+'|'+str(n)+'|'+','.join(map(str,counts))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');args=ap.parse_args()
    if args.controls:
        outcome=controls();save('CONTROLS.json',outcome);print(json.dumps(outcome));return
    spec,lock=read(SPEC),read(LOCK)
    hashes=lock.get('hashes') or {x['path']:x['sha256'] for x in lock['files']}
    required={str(p.relative_to(ROOT)) for p in [SPEC,Path(__file__).resolve(),BASE/'src/validate.py',BASE/'METHOD.md',BASE/'PREREGISTRATION.md']}
    required.update(x['path'] for x in spec['inputs']);assert required<=hashes.keys()
    for p,h in hashes.items():assert sha(ROOT/p)==h,p
    for x in spec['inputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
    model,events,parent=read(ROOT/spec['model']),read(ROOT/spec['events']),read(ROOT/spec['parent_result'])
    assert read(ROOT/spec['model_lock'])['sha256']==sha(ROOT/spec['model'])
    signs,readers=spec['signs'],spec['readers'];assert len(signs)==22
    started=time.monotonic();deadline=started+spec['execution']['primary_normalizer_wall_seconds']
    bags={};cells=defaultdict(list);totals={};wordmaps={};trainbags=defaultdict(list);tables={}
    for reader in readers:
        wordmaps[reader]={tuple(x['cell']):{tuple(w['units']):w['count'] for w in x['counts']} for x in model[reader]['whole']}
        for cell,counts in wordmaps[reader].items():
            c,n=cell;totals[reader,c,n]=sum(counts.values())
            for u,count in sorted(counts.items()):
                vector=tuple(u.count(s) for s in signs)
                trainbags[key(reader,c,n,vector)].append((u,count))
    for e in events:
        reader,c=e['reader'],e['c'];u=e['units'];n=len(u)
        assert reader in readers and n>=4 and e['leaf']%2==0 and set(u)<=set(signs)
        vector=tuple(u.count(s) for s in signs);bk=key(reader,c,n,vector)
        if bk not in bags:
            bags[bk]=dict(key=bk,reader=reader,c=c,n=n,counts=list(vector),held_occurrences=0,held_leaves=[])
            cells[reader,c,n].append(bk)
        bags[bk]['held_occurrences']+=1;bags[bk]['held_leaves'].append(e['leaf'])
    jobs=[]
    for cell,bks in sorted(cells.items()):
        reader,c,n=cell;rows=[x for x in model[reader]['m1'] if tuple(x['context'][:2])==(c,n)]
        tables[cell]=transition_table(rows,c,n,signs)
        jobs.append(dict(cell=list(cell),signs=signs,c=c,n=n,rows=rows,
            bags=[bags[bk]['counts'] for bk in sorted(bks)],max_states=spec['execution']['primary_max_states_per_cell'],deadline=deadline))
    pool=ProcessPoolExecutor(max_workers=spec['execution']['max_workers']);futures={pool.submit(cell_masses,j):j for j in jobs};completed=[]
    try:
        for f in as_completed(futures,timeout=max(.01,deadline-time.monotonic())):completed.append(f.result())
    except Exception as exc:
        processes=list(getattr(pool,'_processes',{}).values());pool.shutdown(wait=False,cancel_futures=True)
        for process in processes:
            if process.is_alive():process.terminate()
        for process in processes:process.join(timeout=1)
        reason=str(exc) if isinstance(exc,Stop) else type(exc).__name__
        save('DP_STATUS.json',dict(status='COMPUTATIONAL_STOP',reason=reason,completed_cells=[x['cell'] for x in completed],required_cells=len(jobs)))
        save('RESULT.json',dict(status='COMPUTATIONAL_STOP',reason=reason,scientific_scope_complete=False));return
    else:pool.shutdown()
    if time.monotonic()>deadline:
        save('RESULT.json',dict(status='COMPUTATIONAL_STOP',reason='NORMALIZER_WALL_LIMIT',scientific_scope_complete=False));return
    tol=spec['numeric']['probability_tolerance'];scoretol=spec['numeric']['score_absolute_tolerance']
    for item in completed:
        reader,c,n=item['cell']
        for mass in item['masses']:bags[key(reader,c,n,mass['counts'])]['log_P_B']=mass['log_P_B']
    save('DP_STATUS.json',dict(status='COMPLETE',cells=[{k:v for k,v in x.items() if k!='masses'} for x in sorted(completed,key=lambda x:x['cell'])],seconds=time.monotonic()-started))
    try:
        for bk,bag in sorted(bags.items()):
            cell=(bag['reader'],bag['c'],bag['n']);N=totals.get(cell,0);pb=math.exp(bag['log_P_B'])
            if pb<=0 or not math.isfinite(pb):raise Stop('BAG_MASS_UNDERFLOW')
            if pb>1+tol:raise Stop('BAG_MASS_ABOVE_ONE')
            support=[]
            for u,count in trainbags.get(bk,[]):
                p=math.exp(word_log_probability(u,tables[cell],signs))
                if p<=0:raise Stop('SUPPORT_MASS_UNDERFLOW')
                support.append(dict(units=list(u),count=count,p=p,q=count/N))
            qb=sum(x['count'] for x in support)/N if N else 0.0
            cats,mean,var,norm,clamps=category_certificate(support,bag['log_P_B'],qb,tol)
            bag.update(P_B=pb,Q_B=qb,cell_train_N=N,train_support=support,categories=cats,mean_R=mean,
                variance_R=var,mobile=var>1e-12,conditional_normalization=norm,clamps=clamps,
                held_leaves=sorted(set(bag['held_leaves'])))
        scored=[]
        for e in events:
            u=e['units'];cell=(e['reader'],e['c'],len(u));bk=key(*cell,tuple(u.count(s) for s in signs));bag=bags[bk]
            p=math.exp(word_log_probability(u,tables[cell],signs));N=totals.get(cell,0)
            q=wordmaps[e['reader']].get((e['c'],len(u)),{}).get(tuple(u),0)/N if N else 0.0
            if abs(p/e['p']-1)>tol or abs(q-e['q'])>tol or N!=e['cell_train_N']:raise Stop('FROZEN_EVENT_MISMATCH')
            raw=math.log1p(q/p)-math.log(2) if N else 0.0
            if abs(raw-e['gain'])>scoretol:raise Stop('FROZEN_GAIN_MISMATCH')
            if e['p']>bag['P_B']*(1+tol) or e['q']>bag['Q_B']+tol:raise Stop('BAG_MASS_BELOW_MEMBER')
            R=math.log1p(e['q']/e['p'])-math.log1p(bag['Q_B']/bag['P_B'])
            scored.append(dict(e,bag_key=bk,conditional_gain=R,bag_gain=e['gain']-R,mobile=bag['mobile']))
        summaries={}
        for ri,reader in enumerate(readers):
            selected=[e for e in scored if e['reader']==reader];leaves=defaultdict(list)
            for e in selected:leaves[e['leaf']].append(e)
            assert len(leaves)==46
            per_leaf={str(k):dict(words=len(v),raw_gain=math.fsum(x['gain'] for x in v)/len(v),
                conditional_gain=math.fsum(x['conditional_gain'] for x in v)/len(v),
                bag_gain=math.fsum(x['bag_gain'] for x in v)/len(v),mobile_words=sum(x['mobile'] for x in v)) for k,v in sorted(leaves.items())}
            mean=lambda field:math.fsum(v[field] for v in per_leaf.values())/len(per_leaf)
            mobile=[e for e in selected if e['mobile']];mobile_leaves=len({e['leaf'] for e in mobile})
            capacity=len(mobile)>=spec['primary']['capacity_mobile_occurrences'] and mobile_leaves>=spec['primary']['capacity_mobile_physical_leaves']
            observed=mean('conditional_gain');null=[];cdf={}
            for e in selected:
                bk=e['bag_key']
                if bk not in cdf:
                    cumulative=[];total=0.0
                    for cat in bags[bk]['categories']:total+=cat['mass'];cumulative.append(min(1.0,total))
                    cumulative[-1]=1.0;cdf[bk]=(cumulative,[x['R'] for x in bags[bk]['categories']])
            rng=random.Random(spec['randomization']['seed_base']+spec['randomization']['reader_seed_stride']*ri)
            if capacity:
                for _ in range(spec['randomization']['draws']):
                    sums={k:[] for k in leaves}
                    for e in selected:
                        cumulative,values=cdf[e['bag_key']];j=bisect.bisect_right(cumulative,rng.random())
                        sums[e['leaf']].append(values[j])
                    null.append(math.fsum(math.fsum(v)/len(v) for v in sums.values())/len(sums))
            tail=(1+sum(x>=observed-1e-12 for x in null))/(len(null)+1) if capacity else None
            positive=sum(v['conditional_gain']>0 for v in per_leaf.values())
            passed=capacity and observed>=spec['primary']['minimum_gain_nats_per_word'] and 3*positive>=2*len(leaves) and tail<=spec['randomization']['corrected_threshold']
            summaries[reader]=dict(words=len(selected),leaves=len(leaves),mobile_words=len(mobile),mobile_leaves=mobile_leaves,
                mean_raw_gain=mean('raw_gain'),mean_conditional_gain=observed,mean_bag_gain=mean('bag_gain'),positive_leaves=positive,
                capacity=capacity,status='CONDITIONAL_ORDER_GAIN_RETAINED' if passed else 'NO_RETAINED_CONDITIONAL_ORDER_GAIN' if capacity else 'NO_CAPACITY',
                per_leaf=per_leaf,null_scores=null,p_or_null=tail,mean_null=math.fsum(null)/len(null) if null else None,
                min_null=min(null) if null else None,max_null=max(null) if null else None)
            old=parent['readers'][reader]['cohorts']['ALL']
            if abs(summaries[reader]['mean_raw_gain']-old['equal_leaf_gain'])>scoretol:raise Stop('PARENT_AGGREGATE_MISMATCH')
    except (Stop,OverflowError,ZeroDivisionError) as exc:
        save('RESULT.json',dict(status='COMPUTATIONAL_STOP',reason=str(exc),scientific_scope_complete=False));return
    save('BAGS.json.gz',dict(status='EXACT_BAG_MASS_ACCOUNTING',signs=signs,bags=[bags[k] for k in sorted(bags)]))
    save('EVENTS_SCORES.json.gz',scored)
    save('RESULT.json',dict(status='BAG_CONDITIONAL_WORD_ORDER',readers=summaries,
        joint_retained=all(x['status']=='CONDITIONAL_ORDER_GAIN_RETAINED' for x in summaries.values())))
    print(json.dumps({k:{f:v[f] for f in ('status','mean_conditional_gain','p_or_null','mobile_words')} for k,v in summaries.items()}))


if __name__=='__main__':main()
