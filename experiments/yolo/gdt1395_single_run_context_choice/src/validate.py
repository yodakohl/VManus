#!/usr/bin/env python3
"""Independent run/context projection and conditional-permutation validator."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import re
import numpy as np

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
A = E/'artifacts'


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')


def parse(raw, signs):
    paths = [[] for _ in range(len(raw)+1)]
    paths[0] = [()]
    for i in range(len(raw)):
        for sign in signs:
            if paths[i] and raw.startswith(sign,i):
                j = i+len(sign)
                paths[j] = (paths[j]+[p+(sign,) for p in paths[i]])[:2]
    assert len(paths[-1]) == 1, ('Nonunique working-unit parse',raw)
    return list(paths[-1][0])


def collapse(units):
    reduced, runs = [], []
    i = 0
    while i < len(units):
        sign = units[i]
        end = i+1
        if sign in ('e','i'):
            while end < len(units) and units[end] == sign:
                end += 1
            runs.append((sign,len(reduced),end-i))
        reduced.append(sign)
        i = end
    return reduced, runs


def bigrams(units):
    padded = ['<BOS>']+list(units)+['<EOS>']
    return set(zip(padded[:-1],padded[1:]))


def kernel(contexts):
    sides = [(bigrams(left),bigrams(right)) for left,right in contexts]
    n = len(sides)
    K = np.empty((n,n),dtype=float)
    for i in range(n):
        for j in range(n):
            K[i,j] = sum(len(sides[i][side]&sides[j][side])/math.sqrt(len(sides[i][side])*len(sides[j][side])) for side in (0,1))/2
    assert np.max(np.abs(np.diag(K)-1)) < 1e-12
    return K


def centered_kernel(K):
    return K-K.mean(axis=0)[None,:]-K.mean(axis=1)[:,None]+K.mean()


def statistic(Kc, labels):
    labels = np.asarray(labels)
    n = len(labels)
    counts = Counter(map(int,labels))
    denominator = n-sum(v*v for v in counts.values())/n
    assert denominator > 0
    same = labels[:,None] == labels[None,:]
    return float(Kc[same].sum()/denominator)


def mobility(Kc, labels):
    observed = statistic(Kc,labels)
    for i in range(len(labels)):
        for j in range(i+1,len(labels)):
            if labels[i] == labels[j]:
                continue
            altered = list(labels)
            altered[i],altered[j] = altered[j],altered[i]
            value = statistic(Kc,altered)
            if abs(value-observed)>1e-9:
                return {'i':i,'j':j,'observed':observed,'swapped':value}
    return None


def controls():
    fixtures = [
        ([(['a'],['a']),(['a'],['a']),(['b'],['b'])],[1,1,2]),
        ([(['a'],['b']),(['b'],['a'])],[1,2]),
        ([(['a'],['a']),(['b'],['b']),(['a','b'],['b','a'])],[1,2,3]),
        ([(['a'],['a']),(['a'],['b']),(['b'],['b']),(['b'],['a'])],[1,1,2,2])]
    checked = 0
    for contexts,labels in fixtures:
        K = kernel(contexts); Kc = centered_kernel(K)
        scores=[]
        assignments=Counter()
        category_probability={c:Fraction(j+1,sum(range(1,len(set(labels))+1))) for j,c in enumerate(sorted(set(labels)))}
        probabilities=set()
        for order in itertools.permutations(range(len(labels))):
            perm = [labels[i] for i in order]
            assignments[tuple(perm)]+=1
            probabilities.add(math.prod(category_probability[c] for c in perm))
            categories = sorted(set(perm))
            Z = np.array([[int(v==c) for c in categories] for v in perm],dtype=float)
            Z -= Z.mean(axis=0)
            reference = float(np.trace(Z.T@K@Z)/np.trace(Z.T@Z))
            score = statistic(Kc,perm)
            assert abs(score-reference)<1e-12
            scores.append(score);checked+=1
        assert len(set(assignments.values()))==1 and len(probabilities)==1
        assert len(assignments)==math.factorial(len(labels))//math.prod(math.factorial(v) for v in Counter(labels).values())
        assert abs(sum(scores)/len(scores)-np.trace(Kc)/(len(labels)-1))<1e-12
        if len(set(labels))==len(labels):
            assert max(scores)-min(scores)<1e-12 and mobility(Kc,labels) is None
        elif contexts==fixtures[0][0]:
            assert mobility(Kc,labels) is not None
    for count in (1,2,5):
        assert collapse(['q']+['e']*count+['d','y'])[0] == ['q','e','d','y']
        assert collapse(['i']*count+['e']*count)[0] == ['i','e']
    assert len(collapse(['q','e','d','e','y'])[1])==2
    assert parse('qocheey',['q','o','ch','e','y'])==['q','o','ch','e','e','y']
    return {'status':'PASS_SOURCE_FREE_CONTROLS','permutations_checked':checked,
            'independent_trace_identity_checked':True,'unique_label_and_n2_invariance_checked':True,
            'neighbor_collapse_invariance_checked':True,'native_access':False}


def project(spec):
    old1233=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion'
    old915=ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
    source=read(old1233/'artifacts/GROUPS.json.gz')
    assert spec['signs']==read(old1233/'src/SPEC.json')['signs']
    allowed=set(spec['allowed'])
    assert len(allowed)==179 and not any(p.startswith('f84') or p in ('f116v','f1r') for p in allowed)
    output,counts={},{}
    for reader in spec['readers']:
        strict={g['id']:g for g in source[reader]}
        assert len(strict)==len(source[reader])
        for g in strict.values():
            assert g['edition']==reader and g['page'] in allowed and g['kind']=='P'
            assert g['left_separator']==g['right_separator']=='DEFINITE_SPACE'
            assert parse(g['ivtff_group_raw'],spec['signs'])==g['units']
        positions={}
        for phase in ('DISCOVERY','EVALUATION'):
            doc=read(old915/'artifacts'/('SOURCE_'+phase+'_'+reader+'.json'))
            assert doc['group_columns']==['source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']
            for line in doc['lines']:
                meta=line['metadata']
                assert meta['page'] in allowed and meta['edition']==reader
                groups=[dict(zip(doc['group_columns'],row)) for row in line['groups']]
                N=int(meta['source_group_count'])
                assert len(groups)==N
                assert [int(g['source_group_index']) for g in groups]==list(range(1,N+1))
                for index,g in enumerate(groups,1):
                    gid=g['source_group_id']
                    assert gid not in positions
                    if gid in strict:
                        cached=strict[gid]
                        assert cached['page']==meta['page'] and cached['locus']==meta['locus']
                        assert cached['kind']==meta['kind']
                        assert int(cached['source_group_index'])==index
                        for key in ('left_separator','right_separator','ivtff_group_raw'):
                            assert cached[key]==g[key]
                    positions[gid]=(meta,groups,index)
        assert set(strict)<=set(positions)
        buckets=defaultdict(list)
        three=single=0
        for gid,g in strict.items():
            meta,line,index=positions[gid]
            N=len(line)
            if index<=1 or index>=N:
                continue
            left_id=line[index-2]['source_group_id'];right_id=line[index]['source_group_id']
            if left_id not in strict or right_id not in strict:
                continue
            three+=1
            collapsed,runs=collapse(g['units'])
            if len(runs)!=1:
                continue
            single+=1
            third=min(2,3*(index-1)//N)
            left,right=strict[left_id],strict[right_id]
            left_source=collapse(left['units'])[0];right_source=collapse(right['units'])[0]
            event={'id':gid,'raw':g['ivtff_group_raw'],'length':runs[0][2],
                   'left_id':left_id,'left_raw':left['ivtff_group_raw'],'left_source':left_source,
                   'right_id':right_id,'right_raw':right['ivtff_group_raw'],'right_source':right_source,
                   'line_groups':N,'index':index}
            buckets[(g['page'],tuple(collapsed),third)].append(event)
        cells=[]
        for (page,collapsed,third),events in sorted(buckets.items()):
            events.sort(key=lambda e:e['id'])
            if len(events)<3 or len({e['length'] for e in events})<2:
                continue
            contexts=[(e['left_source'],e['right_source']) for e in events]
            Kc=centered_kernel(kernel(contexts));labels=[e['length'] for e in events]
            witness=mobility(Kc,labels)
            cells.append({'page':page,'leaf':re.match(r'f\d+',page).group(),'source':list(collapsed),
                          'third':third,'events':events,'score':statistic(Kc,labels),
                          'witness':None if witness is None else {'i':witness['i'],'j':witness['j'],'swapped_score':witness['swapped']}})
        output[reader]=cells
        witnessed=[c for c in cells if c['witness'] is not None]
        counts[reader]={'strict_groups':len(strict),'three_strict_positions':three,'single_run_positions':single,
                        'candidate_cells':len(cells),'witnessed_cells':len(witnessed),
                        'witnessed_occurrences':sum(len(c['events']) for c in witnessed),
                        'witnessed_leaves':len({c['leaf'] for c in witnessed}),
                        'score_leaves':len({c['leaf'] for c in cells})}
    return output,counts


def compare_tree(actual,expected,tolerance=1e-9):
    if isinstance(expected,dict):
        assert set(actual)==set(expected),(set(actual),set(expected))
        for key in expected:compare_tree(actual[key],expected[key],tolerance)
    elif isinstance(expected,list):
        assert len(actual)==len(expected)
        for a,b in zip(actual,expected):compare_tree(a,b,tolerance)
    elif isinstance(expected,float):
        assert math.isfinite(actual) and abs(actual-expected)<=tolerance,(actual,expected)
    else:assert actual==expected,(actual,expected)


def evaluate(cells,counts,spec,reader_index):
    leaves=Counter(c['leaf'] for c in cells)
    weights=[1/(len(leaves)*leaves[c['leaf']]) for c in cells]
    observed=math.fsum(c['score']*weight for c,weight in zip(cells,weights))
    entry={'counts':counts,'observed':observed}
    capacity=counts['witnessed_cells']>=20 and counts['witnessed_occurrences']>=100 and counts['witnessed_leaves']>=10
    if not capacity:
        entry['status']='CAPACITY_STOP'
        return entry,[]
    rng=random.Random(1395+reader_index)
    draws=1999
    null=np.zeros(draws)
    leaf_scores={leaf:np.zeros(draws) for leaf in leaves}
    leaf_obs={leaf:0.0 for leaf in leaves}
    for cell,weight in zip(cells,weights):
        labels=np.array([e['length'] for e in cell['events']],dtype=int)
        n=len(labels)
        Kc=centered_kernel(kernel([(e['left_source'],e['right_source']) for e in cell['events']]))
        permutations=[]
        # Stratum outer, draw inner, fresh identity indices each time.
        for draw in range(draws):
            indices=list(range(n));rng.shuffle(indices);permutations.append(indices)
        changed=labels[np.asarray(permutations,dtype=int)]
        sizes=Counter(map(int,labels))
        den=n-sum(v*v for v in sizes.values())/n
        values=np.zeros(draws)
        # Separate class-indicator quadratic forms of centered K; no feature matrix.
        for start in range(0,draws,128):
            end=min(start+128,draws)
            for category in sorted(sizes):
                indicator=(changed[start:end]==category).astype(float)
                values[start:end]+=np.sum((indicator@Kc)*indicator,axis=1)/den
        null+=weight*values
        leaf_scores[cell['leaf']]+=values/leaves[cell['leaf']]
        leaf_obs[cell['leaf']]+=cell['score']/leaves[cell['leaf']]
    null_list=list(map(float,null))
    mean=math.fsum(null_list)/draws
    sd=math.sqrt(math.fsum((value-mean)**2 for value in null_list)/(draws-1))
    p=(1+sum(value>=observed-1e-12 for value in null_list))/(draws+1)
    gain=(observed-mean)/mean if mean>0 else None
    summaries=[{'leaf':leaf,'observed':leaf_obs[leaf],
                'null_mean':math.fsum(map(float,leaf_scores[leaf]))/draws} for leaf in sorted(leaves)]
    direction=sum(leaf['observed']>leaf['null_mean']+1e-12 for leaf in summaries)
    rejected=p<=.005 and gain is not None and gain>=.10 and 3*direction>=2*len(leaves)
    entry.update(status='REJECTED' if rejected else 'NOT_REJECTED',
                 statistics={'null_mean':mean,'null_sd':sd,'p_upper':p,'relative_gain':gain,
                             'direction_leaves':direction,'leaves':len(leaves)},leaf_summaries=summaries)
    return entry,null_list


def validate():
    lock_path=E/'LOCK.json';lock=read(lock_path)
    pins={item['path']:item['sha256'] for item in lock['files']}
    required=[E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'PREREGISTRATION.md',E/'METHOD.md']
    for path in required:
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    spec=read(E/'src/SPEC.json')
    for item in spec['inputs']:
        assert pins[item['path']]==item['sha256']==sha(ROOT/item['path'])
    assert spec['readers']==['IT2a','ZL3b'] and spec['draws']==1999 and spec['seed']==1395
    assert spec['min_witnessed_cells']==20 and spec['min_witnessed_occurrences']==100 and spec['min_witnessed_leaves']==10
    assert spec['swap_tolerance']==1e-9 and spec['p_max']==.005 and spec['relative_gain_min']==.1
    assert spec['leaf_direction_fraction']==[2,3]
    cells,counts=project(spec)
    primary_data=read(A/'DATA.json');primary_result=read(A/'RESULT.json');primary_null=read(A/'NULLS.json')
    compare_tree(primary_data,{'readers':cells})
    result={'readers':{}};nulls={};max_errors={}
    for index,reader in enumerate(spec['readers']):
        value,null=evaluate(cells[reader],counts[reader],spec,index)
        result['readers'][reader]=value;nulls[reader]=null
        compare_tree(primary_result['readers'][reader],value)
        compare_tree(primary_null['readers'][reader],null)
        max_errors[reader]=max((abs(a-b) for a,b in zip(primary_null['readers'][reader],null)),default=0.0)
    statuses=[r['status'] for r in result['readers'].values()]
    result['status']='CONTEXT_INDEPENDENT_RUN_CHOICE_REJECTED' if all(s=='REJECTED' for s in statuses) else 'CAPACITY_STOP' if 'CAPACITY_STOP' in statuses else 'NOT_REJECTED'
    compare_tree(primary_result,result)
    compare_tree(primary_null,{'readers':nulls})
    receipt={'experiment_id':'GDT1395','status':'PASS_INDEPENDENT_VALIDATION','scientific_status':result['status'],
             'readers':{reader:{'status':result['readers'][reader]['status'],'counts':counts[reader],
                                'permutations_checked':len(nulls[reader]),'max_null_score_error':max_errors[reader]} for reader in spec['readers']},
             'implementation':'Independent dynamic segmentation and original915joins; normalized bigram-set intersections; centered-kernel label-block quadratic forms; no primary imports.',
             'mobility':'All eligible varying strata retained; first unequal-label swap witness independently checked; no-witness not interpreted as invariant.',
             'permutation_order':'Reader IT2a,ZL3b; stratum outer,1999draws inner; persistent reader RNG; fresh identity indices perdraw.',
             'source_free_controls':controls(),
             'pins':{'code_lock_sha256':sha(lock_path),'validator_sha256':sha(Path(__file__)),
                     'spec_sha256':sha(E/'src/SPEC.json'),'data_sha256':sha(A/'DATA.json'),
                     'result_sha256':sha(A/'RESULT.json'),'nulls_sha256':sha(A/'NULLS.json')},
             'limits':['Exposed conditional writer test; no semantic translation or synonym assignment.',
                       'Reader results are alternate transcriptions, not independent manuscripts.',
                       'Exchangeability requires the fixed line scaffold and length-invariant eligibility assumptions.']}
    assert not (A/'VALIDATION.json').exists()
    save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'scientific_status':result['status'],'readers':receipt['readers']},sort_keys=True))


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--controls',action='store_true');args=parser.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
