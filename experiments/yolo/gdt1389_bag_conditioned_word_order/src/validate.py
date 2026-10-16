#!/usr/bin/env python3
"""Independent forward count-state DP and conditional-mixture verification."""
import argparse
import gzip
import hashlib
import itertools
import json
import math
import random
import time
import multiprocessing
from collections import Counter,defaultdict
from fractions import Fraction
from pathlib import Path

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
READERS=['ZL3b','IT2a','RF1b']
SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def bag(word):return tuple(sorted(Counter(word).items()))


def forward_mass(multiset, transition, state_limit=2000000, deadline=None):
    symbols=tuple(s for s,n in multiset)
    target=tuple(n for s,n in multiset)
    size=sum(target)
    assert size and all(n>0 for n in target)
    frontier={(tuple(0 for _ in target),'^'):1}
    visited=1
    for position in range(size):
        after={}
        for (used,previous),mass in frontier.items():
            for j,symbol in enumerate(symbols):
                if used[j]==target[j]:continue
                increment=list(used);increment[j]+=1
                key=(tuple(increment),symbol)
                value=mass*transition(position,previous,symbol)
                if key not in after:
                    visited+=1
                    if visited>state_limit:raise RuntimeError('INDEPENDENT_STATE_BUDGET_STOP')
                    after[key]=value
                else:after[key]+=value
            if deadline is not None and time.monotonic()>deadline:
                raise RuntimeError('INDEPENDENT_WALL_BUDGET_STOP')
        frontier=after
    return sum(frontier.values()),visited


def word_mass(word,transition):
    value=1
    for i,s in enumerate(word):value*=transition(i,word[i-1] if i else '^',s)
    return value


def cdf_pick(categories,u):
    cumulative=0.0
    for category in categories:
        cumulative+=category['probability']
        if u<cumulative:return category['score']
    assert 1-cumulative<=1e-10
    return categories[-1]['score']


def controls():
    alphabet=('a','b','c');bags_checked=words_checked=0
    for n in range(1,7):
        def transition(i,previous,s):
            weights=[1+((i+1)*(j+2)+(0 if previous=='^' else alphabet.index(previous)+1))%5 for j in range(3)]
            return Fraction(weights[alphabet.index(s)],sum(weights))
        groups=defaultdict(list)
        for word in itertools.product(alphabet,repeat=n):groups[bag(word)].append(word)
        total=Fraction(0)
        for b,words in groups.items():
            expected=sum(word_mass(w,transition) for w in words)
            actual,_=forward_mass(b,transition)
            assert actual==expected
            total+=actual;bags_checked+=1;words_checked+=len(words)
        assert total==1
    uniform=lambda i,p,s:Fraction(1,3)
    assert forward_mass((('a',2),('b',1)),uniform)[0]==Fraction(1,9)
    words=[('a','a','b'),('a','b','a'),('b','a','a')]
    p=Fraction(1,27);pb=Fraction(1,9);qb=Fraction(1)
    scores=[]
    for i,w in enumerate(words):
        q=Fraction(1) if i==0 else Fraction(0)
        residual=math.log1p(float(q/p))-math.log1p(float(qb/pb))
        massgain=math.log1p(float(qb/pb))-math.log(2)
        raw=math.log(float((p+q)/(2*p)))
        assert abs(raw-massgain-residual)<1e-12
        scores.append(residual)
    assert sum(scores)/3<=0
    assert abs(sum(math.exp(r) for r in scores)/3-1)<1e-12
    flat_q=Fraction(1,3)
    assert abs(math.log1p(float(flat_q/p))-math.log1p(float(qb/pb)))<1e-12
    categories=[{'probability':1/3,'score':scores[0]},{'probability':2/3,'score':scores[1]}]
    assert cdf_pick(categories,0)==scores[0] and cdf_pick(categories,.5)==scores[1]
    assert math.log1p(0)-math.log1p(0)==0
    try:forward_mass((('a',2),('b',1)),uniform,state_limit=1)
    except RuntimeError:pass
    else:raise AssertionError('state limit did not stop')
    return {'status':'PASS_SOURCE_FREE_ONLY','exhaustively_checked_words':words_checked,'bags':bags_checked,
            'duplicate_count_no_multiplicity':True,'raw_mass_order_decomposition':True,'conditional_expected_log_ratio_nonpositive':True}


def close(a,b,tol=1e-9):
    assert math.isfinite(a) and math.isfinite(b)
    assert abs(a-b)<=tol,(a,b)


def log1pexp(x):
    return max(x,0.0)+math.log1p(math.exp(-abs(x)))


def model_tables(models):
    transitions={};whole={}
    for reader,model in models.items():
        transitions[reader]={tuple(row['context']):row['counts'] for row in model['m1']}
        whole[reader]={tuple(row['cell']):{tuple(w['units']):w['count'] for w in row['counts']} for row in model['whole']}
    return transitions,whole


def tprob(t,c,n,i,prev,symbol):
    counts=t.get((c,n,i,prev),{})
    return (counts.get(symbol,0)+.5)/(sum(counts.values())+11)


def log_word(t,c,u):
    return math.fsum(math.log(tprob(t,c,len(u),i,u[i-1] if i else '^',s)) for i,s in enumerate(u))


WORK_T=None
WORK_Q=None

def init_worker(transitions,whole):
    global WORK_T,WORK_Q
    WORK_T=transitions;WORK_Q=whole


def calculate_bag(task):
    key,reader,c,n,counts,deadline=task
    t=WORK_T[reader];all_q=WORK_Q[reader].get((c,n),{})
    symbols=[s for s,k in zip(SIGNS,counts) if k]
    target=tuple(k for k in counts if k)
    frontier={(tuple(0 for _ in target),'^'):1.0};logpb=0.0;visited=1
    probabilities={(i,prev):[tprob(t,c,n,i,prev,s) for s in symbols] for i in range(n) for prev in (['^'] if i==0 else symbols)}
    for position in range(n):
        after={}
        for (used,previous),mass in frontier.items():
            local=probabilities[(position,previous)]
            for j,symbol in enumerate(symbols):
                if used[j]>=target[j]:continue
                inc=list(used);inc[j]+=1;state=(tuple(inc),symbol)
                amount=mass*local[j]
                if state not in after:
                    visited+=1
                    if visited>2000000:raise RuntimeError('INDEPENDENT_STATE_BUDGET_STOP:'+key)
                    after[state]=amount
                else:after[state]+=amount
            if time.monotonic()>deadline:raise RuntimeError('INDEPENDENT_WALL_BUDGET_STOP')
        scale=math.fsum(after.values());assert scale>0
        logpb+=math.log(scale)
        frontier={state:value/scale for state,value in after.items()}
    pb=math.exp(logpb)
    if not pb:raise RuntimeError('INDEPENDENT_MASS_UNDERFLOW_STOP')
    train_n=sum(all_q.values())
    qwords=sorted(w for w in all_q if tuple(w.count(s) for s in SIGNS)==tuple(counts))
    qb=math.fsum(all_q[w]/train_n for w in qwords) if train_n else 0.0
    z=log1pexp(math.log(qb)-logpb) if qb else 0.0
    support=[];categories=[]
    for w in qwords:
        logp=log_word(t,c,w);p=math.exp(logp);q=all_q[w]/train_n
        mass=math.exp(logp-logpb)
        score=log1pexp(math.log(q)-logp)-z
        support.append({'units':list(w),'count':all_q[w],'p':p,'q':q,'mass':mass,'R':score})
        categories.append({'kind':'TRAIN','units':list(w),'mass':mass,'R':score})
    residual=1-math.fsum(v['mass'] for v in categories)
    assert residual>=-1e-10
    residual=max(0.0,residual)
    categories.append({'kind':'RESIDUAL','units':None,'mass':residual,'R':-z})
    mean=math.fsum(a['mass']*a['R'] for a in categories)
    second=math.fsum(a['mass']*a['R']**2 for a in categories)
    rawvar=second-mean*mean
    assert rawvar>=-1e-12
    var=math.fsum(a['mass']*(a['R']-mean)**2 for a in categories)
    close(var,max(0.0,rawvar),1e-9)
    norm=math.fsum(a['mass']*math.exp(a['R']) for a in categories)
    close(norm,1.0)
    assert mean<=1e-10
    return key,{'P_B':pb,'log_P_B':logpb,'Q_B':qb,'cell_train_N':train_n,'train_support':support,'categories':categories,'mean_R':mean,'variance_R':var,'mobile':var>1e-12,'conditional_normalization':norm,'normalizer':z,'visited_states':visited}


def validate_native():
    started=time.monotonic();deadline=started+900
    lockpath=E/'src/REGISTRATION_LOCK.json';lock=read(lockpath)
    pins={r['path']:r['sha256'] for r in lock['files']}
    for path,digest in pins.items():assert sha(ROOT/path)==digest,path
    for name in ['src/run.py','src/validate.py','src/SPEC.json','METHOD.md']:
        assert str((E/name).relative_to(ROOT)) in pins
    spec=read(E/'src/SPEC.json')
    assert spec['readers']==READERS and spec['signs']==SIGNS
    assert spec['execution']['independent_max_states_per_bag']==2000000
    assert spec['execution']['independent_normalizer_wall_seconds']==900
    assert spec['randomization']['draws']==199 and spec['randomization']['seed_base']==1389000 and spec['randomization']['reader_seed_stride']==1000
    for r in spec['inputs']:assert sha(ROOT/r['path'])==r['sha256']
    base=ROOT/'experiments/yolo/gdt1308_whole_form_prediction/artifacts'
    assert sha(base/'MODEL.json')==read(base/'MODEL_LOCK.json')['sha256']
    models=read(base/'MODEL.json');transitions,whole=model_tables(models)
    parent_result=read(base/'RESULT.json')
    original=json.loads(gzip.decompress((base/'EVENTS.json.gz').read_bytes()))
    assert len(original)==23496
    result=read(E/'artifacts/RESULT.json')
    if result['status']=='COMPUTATIONAL_STOP':
        receipt={'status':'COMPUTATIONAL_STOP_RETAINED_NO_SCIENTIFIC_VALIDATION','lock_sha256':sha(lockpath),'result_sha256':sha(E/'artifacts/RESULT.json')}
        (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));return
    assert result['status']=='BAG_CONDITIONAL_WORD_ORDER'
    saved_bags=json.loads(gzip.decompress((E/'artifacts/BAGS.json.gz').read_bytes()))
    assert saved_bags['status']=='EXACT_BAG_MASS_ACCOUNTING' and saved_bags['signs']==SIGNS
    saved_scores=json.loads(gzip.decompress((E/'artifacts/EVENTS_SCORES.json.gz').read_bytes()))
    assert len(saved_scores)==len(original)
    bags={};event_keys=[];counts_by_leaf={}
    for old,new in zip(original,saved_scores):
        assert all(new.get(k)==v for k,v in old.items())
        reader,c,u=old['reader'],old['c'],old['units'];n=len(u)
        assert reader in READERS and n>=4 and old['leaf']%2==0 and set(u)<=set(SIGNS)
        assert not old['id'].split('|')[1].startswith(('f84','f116v','f1r.'))
        p=math.exp(log_word(transitions[reader],c,u))
        qcounts=whole[reader].get((c,n),{});train_n=sum(qcounts.values())
        q=qcounts.get(tuple(u),0)/train_n if train_n else 0.0
        mix=(p+q)/2 if train_n else p
        close(old['p'],p,1e-11);close(old['q'],q,1e-11);close(old['mix'],mix,1e-11)
        close(old['gain'],math.log(mix/p),1e-10);assert old['cell_train_N']==train_n
        counts=tuple(u.count(s) for s in SIGNS)
        key=reader+'|'+c+'|'+str(n)+'|'+','.join(map(str,counts))
        event_keys.append(key)
        if key not in bags:bags[key]={'reader':reader,'c':c,'n':n,'counts':counts,'events':[]}
        bags[key]['events'].append(old)
    saved_index={b['key']:b for b in saved_bags['bags']}
    assert len(saved_index)==len(saved_bags['bags']) and set(saved_index)==set(bags)
    tasks=[(key,b['reader'],b['c'],b['n'],b['counts'],deadline) for key,b in bags.items()]
    calculated={}
    try:
        with multiprocessing.Pool(processes=min(16,len(tasks)),initializer=init_worker,initargs=(transitions,whole)) as pool:
            iterator=pool.imap_unordered(calculate_bag,tasks,chunksize=1)
            for _ in tasks:
                key,value=iterator.next(timeout=max(.001,deadline-time.monotonic()))
                calculated[key]=value
    except (RuntimeError,multiprocessing.TimeoutError) as exc:
        receipt={'status':'COMPUTATIONAL_STOP_INDEPENDENT_VALIDATION','reason':str(exc),'complete_bags':len(calculated),'required_bags':len(bags),'scientific_claim_validated':False}
        (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));return
    for key,b in bags.items():
        expected=calculated[key];actual=saved_index[key]
        assert actual['reader']==b['reader'] and actual['c']==b['c'] and actual['n']==b['n'] and actual['counts']==list(b['counts'])
        assert actual['held_occurrences']==len(b['events']) and actual['held_leaves']==sorted({e['leaf'] for e in b['events']})
        assert actual['cell_train_N']==expected['cell_train_N'] and actual['mobile']==expected['mobile']
        for field in ['P_B','Q_B','conditional_normalization']:close(actual[field],expected[field],1e-10)
        for field in ['log_P_B','mean_R','variance_R']:close(actual[field],expected[field],1e-9)
        assert actual['P_B']>0
        close(math.log(actual['P_B']),actual['log_P_B'])
        assert actual['mean_R']<=1e-10 and actual['variance_R']>=0
        assert isinstance(actual['clamps'],list)
        for clamp in actual['clamps']:
            assert clamp['quantity']=='residual_mass' and -1e-10<=clamp['before']<0 and clamp['after']==0.0
            assert actual['categories'][-1]['mass']==0.0
        for field in ['train_support','categories']:
            assert len(actual[field])==len(expected[field])
            for av,ev in zip(actual[field],expected[field]):
                for name,value in ev.items():
                    if isinstance(value,float):close(av[name],value)
                    else:assert av[name]==value
    reconstructed=defaultdict(list)
    for old,new,key in zip(original,saved_scores,event_keys):
        b=calculated[key]
        z=b['normalizer']
        r=(log1pexp(math.log(old['q'])-math.log(old['p'])) if old['q'] else 0)-z
        massgain=z-math.log(2) if old['cell_train_N'] else 0.0
        close(old['gain'],r+massgain)
        assert new['bag_key']==key and new['mobile']==b['mobile']
        close(new['conditional_gain'],r);close(new['bag_gain'],massgain)
        reconstructed[old['reader']].append(dict(old,conditional_gain=r,bag_gain=massgain,mobile=b['mobile'],bag_key=key))
    summary=[]
    for ri,reader in enumerate(READERS):
        es=reconstructed[reader];r=result['readers'][reader]
        leaves=defaultdict(list)
        for e in es:leaves[e['leaf']].append(e)
        perleaf={}
        for leaf,events in sorted(leaves.items()):
            perleaf[str(leaf)]={'words':len(events),'raw_gain':math.fsum(e['gain'] for e in events)/len(events),
                                'conditional_gain':math.fsum(e['conditional_gain'] for e in events)/len(events),
                                'bag_gain':math.fsum(e['bag_gain'] for e in events)/len(events),'mobile_words':sum(e['mobile'] for e in events)}
        assert set(r['per_leaf'])==set(perleaf)
        for leaf,data in perleaf.items():
            for k,v in data.items():
                if isinstance(v,float):close(r['per_leaf'][leaf][k],v)
                else:assert r['per_leaf'][leaf][k]==v
        L=len(leaves)
        assert L==46 and parent_result['readers'][reader]['cohorts']['ALL']['words']==len(es)
        close(parent_result['readers'][reader]['cohorts']['ALL']['equal_leaf_gain'],math.fsum(v['raw_gain'] for v in perleaf.values())/L)
        mobile=[e for e in es if e['mobile']];mobileleaves=len({e['leaf'] for e in mobile})
        capacity=len(mobile)>=100 and mobileleaves>=10
        observed=math.fsum(v['conditional_gain'] for v in perleaf.values())/L
        rawmean=math.fsum(v['raw_gain'] for v in perleaf.values())/L
        bagmean=math.fsum(v['bag_gain'] for v in perleaf.values())/L
        positive=sum(v['conditional_gain']>0 for v in perleaf.values())
        assert r['words']==len(es) and r['leaves']==L and r['mobile_words']==len(mobile) and r['mobile_leaves']==mobileleaves
        assert r['capacity']==capacity and r['positive_leaves']==positive
        close(r['mean_conditional_gain'],observed);close(r['mean_raw_gain'],rawmean);close(r['mean_bag_gain'],bagmean)
        scores=[]
        if capacity:
            rng=random.Random(1389000+1000*ri)
            for rep in range(199):
                byleaf=defaultdict(float)
                for e in es:
                    categories=calculated[e['bag_key']]['categories']
                    u=rng.random();acc=0.0;score=categories[-1]['R']
                    for category in categories:
                        acc+=category['mass']
                        if u<acc:score=category['R'];break
                    byleaf[e['leaf']]+=score
                scores.append(math.fsum(byleaf[f]/len(leaves[f]) for f in sorted(leaves))/L)
                if time.monotonic()>deadline:raise RuntimeError('INDEPENDENT_WALL_BUDGET_STOP_DURING_NULL')
            p=(1+sum(s>=observed-1e-12 for s in scores))/200
            assert len(r['null_scores'])==199
            for a,b in zip(r['null_scores'],scores):close(a,b)
            close(r['p_or_null'],p);close(r['mean_null'],math.fsum(scores)/199);close(r['min_null'],min(scores));close(r['max_null'],max(scores))
        else:
            p=None;assert r['null_scores']==[]
            for k in ['p_or_null','mean_null','min_null','max_null']:assert r[k] is None
        passed=capacity and observed>=.01 and positive*3>=2*L and p<=.05/3
        expected_status='NO_CAPACITY' if not capacity else 'CONDITIONAL_ORDER_GAIN_RETAINED' if passed else 'NO_RETAINED_CONDITIONAL_ORDER_GAIN'
        assert r['status']==expected_status
        summary.append({'reader':reader,'all_words':len(es),'all_leaves':L,'mobile_words':len(mobile),'mobile_leaves':mobileleaves,'mean_conditional_gain':observed,'joint_gate':bool(passed),'reported_status':r['status']})
    assert result['joint_retained']==all(s['joint_gate'] for s in summary)
    receipt={'status':'PASS_SOURCE_BAG_MASS_AND_CONDITIONAL_ACCOUNTING','lock_sha256':sha(lockpath),'result_sha256':sha(E/'artifacts/RESULT.json'),
             'events':len(original),'bags':len(bags),'readers':summary,'method':'Forward used-count/lastsign DP with per-layer scaling; explicit all-permutation controls; full independent occurrence null replay; no primary imports.',
             'limits':['Conditional fixed-model accounting only, not language or word meaning.','No per-bag omission; independent limits two million visited count/last states per bag and900seconds overall.','All original leaf denominators retained; model normalization uses all permutations, not only observed words.']}
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,sort_keys=True))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--controls','--controls-only',action='store_true');args=parser.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True));return
    try:
        validate_native()
    except RuntimeError as exc:
        if 'BUDGET_STOP' not in str(exc):raise
        receipt={'status':'COMPUTATIONAL_STOP_INDEPENDENT_VALIDATION','reason':str(exc),'scientific_claim_validated':False}
        (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt))


if __name__=='__main__':main()
