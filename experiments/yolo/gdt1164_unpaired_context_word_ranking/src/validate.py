#!/usr/bin/env python3
"""Independent numerical definitions for GDT1164; source audit added after release.
No builder, fitter or scorer scientific functions are imported.
"""
import argparse
import csv
import gzip
import hashlib
import subprocess
import json
import math
from collections import Counter, defaultdict, OrderedDict
from pathlib import Path
from fractions import Fraction
import numpy as np
BASE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in BASE.parents if (p/'AGENTS.md').exists() and (p/'.git').exists())

def independent_geometry(records, nodes, top_context=1024):
    counts=Counter(t for r in records for t in r)
    contexts=sorted(counts,key=lambda t:(-counts[t],t))[:top_context]
    lookup={t:i for i,t in enumerate(contexts)}; width=len(contexts)+1
    offsets=(-5,-4,-3,-2,-1,1,2,3,4,5)
    cells=defaultdict(Counter); col=Counter(); row=Counter(); total=0
    for record in records:
        for center,word in enumerate(record):
            for oi,offset in enumerate(offsets):
                neighbor=center+offset
                if 0<=neighbor<len(record):
                    j=oi*width+lookup.get(record[neighbor],len(contexts))
                    cells[word][j]+=1;row[word]+=1;col[j]+=1;total+=1
    ppmi=np.zeros((len(nodes),10*width),dtype=np.float64)
    for i,word in enumerate(nodes):
        for j,c in cells[word].items():ppmi[i,j]=max(0.0,math.log(c*total/(row[word]*col[j])))
    norms=np.linalg.norm(ppmi,axis=1)
    if np.any(norms==0):return {'capacity':False,'reason':'zero_ppmi_norm','ppmi':ppmi,'counts':counts,'norms':norms}
    unit=ppmi/norms[:,None];d=np.clip(1-unit@unit.T,0,2);np.fill_diagonal(d,0)
    average=d.sum()/(len(nodes)*(len(nodes)-1))
    if not average>0:return {'capacity':False,'reason':'zero_offdiagonal_mean','ppmi':ppmi,'counts':counts,'norms':norms}
    d=d/average
    quantiles=np.array([np.quantile(np.delete(r,i),np.linspace(0,1,16),method='linear') for i,r in enumerate(d)])
    return {'capacity':True,'ppmi':ppmi,'distance':d,'fingerprints':quantiles,'counts':counts,'norms':norms,'context_types':contexts,'context_total':total}

def direct_objective(dw,de,coupling,p,q,cost=None):
    n,m=coupling.shape
    transport=sum((dw[i,k]-de[j,l])**2*coupling[i,j]*coupling[k,l] for i in range(n) for k in range(n) for j in range(m) for l in range(m)) if cost is None else float(np.sum(cost*coupling))
    cols=coupling.sum(axis=0)
    colkl=sum(x*math.log(x/y) for x,y in zip(cols,q) if x)
    joint=sum(coupling[i,j]*math.log(coupling[i,j]/(p[i]*q[j])) for i in range(n) for j in range(m) if coupling[i,j])
    return transport+colkl+.01*joint

def coupling_from_logits(z,p):
    shifted=z-z.max(axis=1,keepdims=True);exp=np.exp(shifted)
    return p[:,None]*exp/exp.sum(axis=1,keepdims=True)

def numerical_fixture():
    dw=np.array([[0.,1.],[1.,0.]])
    de=np.array([[0.,.4,1.3],[.4,0.,.8],[1.3,.8,0.]])
    p=np.array([.4,.6]);q=np.array([.2,.3,.5]);z=np.array([[.1,-.2,.3],[.4,.2,-.1]])
    g=coupling_from_logits(z,p);b=g.sum(axis=0)
    matrix=(p@(dw*dw)@p)+(b@(de*de)@b)-2*np.sum((dw@g@de.T)*g)
    col=sum(b*np.log(b/q));joint=np.sum(g*np.log(g/(p[:,None]*q[None,:])))
    direct=direct_objective(dw,de,g,p,q)
    gradients=np.empty_like(z);h=1e-6
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            plus=z.copy();minus=z.copy();plus[i,j]+=h;minus[i,j]-=h
            gradients[i,j]=(direct_objective(dw,de,coupling_from_logits(plus,p),p,q)-direct_objective(dw,de,coupling_from_logits(minus,p),p,q))/(2*h)
    _,analytic,_=independent_objective_gradient(z,{'Dw':dw,'De':de,'p':p,'q':q})
    gradient_error=float(abs(analytic-gradients).max())
    return {'direct':direct,'matrix':float(matrix+col+.01*joint),'row_mass_error':float(abs(g.sum(axis=1)-p).max()),'finite_difference_gradient':gradients.tolist(),'analytic_gradient_max_error':gradient_error,'agreement':bool(abs(direct-(matrix+col+.01*joint))<1e-12 and gradient_error<1e-8)}

def audit_source(runtime,all_worlds=False):
    BOOKS=['Band2','Band3','Band4','Band5']
    records={b:OrderedDict() for b in BOOKS}; markers=defaultdict(list); line_counts=Counter()
    with (ROOT/'gdt155_blinded_diplomatic.tsv').open() as f:
     for row in csv.DictReader(f,delimiter='\t'):
      if row['corpus']!='NUREMBERG' or row['book_or_ms'] not in BOOKS:continue
      rid=row['record_id']; words=row['diplomatic_marked'].split(); records[row['book_or_ms']].setdefault(rid,[]).extend(words)
      n=sum(w.count('¤') for w in words);assert n==int(row['abbreviation_site_count'])
      for j,w in enumerate(words):
       for marker in range(w.count('¤')):markers[rid].append((row['line_id'],j,w))
      line_counts[rid]+=1
    sites=defaultdict(list)
    with (ROOT/'gdt155_blinded_abbreviation_sites.tsv').open() as f:
     for row in csv.DictReader(f,delimiter='\t'):
      if row['corpus']=='NUREMBERG':sites[row['record_id']].append(row)
    eligible={b:[] for b in BOOKS};exclusions=Counter();allsite={}
    for b,recs in records.items():
     for rid in recs:
      ms=markers[rid];ss=sites[rid];assert len(ms)==len(ss),(rid,len(ms),len(ss))
      for ordinal,((line,j,w),s) in enumerate(zip(ms,ss),1):
       assert int(s['site_index_in_record'])==ordinal and s['line_id']==line,(rid,ordinal,s)
       allsite[s['site_id']]={'line_id':line,'raw':w,'record_id':rid,'ordinal':ordinal,'marked_span':s['surface_span_marked']}
       if w.count('¤')!=1:exclusions['multiple_marker_group']+=1
       elif w!=s['surface_span_marked']:exclusions['not_whole_group']+=1
       else:eligible[b].append({'site_id':s['site_id'],'raw':w,'record_id':rid,'line_id':line,'group_index':j})
    def prefix(recs):
     out=[];n=0
     for rid,tokens in recs:
      if n+len(tokens)>32000:break
      out.append((rid,tokens));n+=len(tokens)
     return out
    out=[]
    for b in BOOKS:
     selected=prefix(records[b].items());cnt=Counter(t for rid,words in selected for t in words);vocab=sorted((t for t in cnt if cnt[t]>=20),key=lambda t:(-cnt[t],t))[:128]
     selectedsites=[e for e in eligible[b] if e['raw'] in vocab]
     out.append({'book':b,'written_records':len(selected),'written_tokens':sum(len(t) for _,t in selected),'written_supported_types':sum(v>=20 for v in cnt.values()),'written_selected_types':len(vocab),'selected_marked_types':len({e['raw'] for e in selectedsites}),'wholebook_selected_marked_sites':len(selectedsites),'all_eligible_sites':len(eligible[b]),'vocabulary':vocab,'panel_record_ids':[rid for rid,_ in selected]})
    for fold,b in enumerate(BOOKS):
     refs={book:OrderedDict() for book in BOOKS if book!=b}
     with (ROOT/'gdt155_unblinded_lines.tsv').open() as f:
      header=next(f).rstrip('\n').split('\t')
      for raw in f:
       # Inspect the corpus/book prefix before parsing any expanded payload.
       pos=raw.find('\t');pos2=raw.find('\t',pos+1)
       if raw[:pos]!='NUREMBERG' or raw[pos+1:pos2] not in refs:continue
       r=dict(zip(header,next(csv.reader([raw],delimiter='\t'))));refs[r['book_or_ms']].setdefault(r['record_id'],[]).extend(r['expanded_diplomatic'].split())
     queues={book:iter(recs.items()) for book,recs in refs.items()};pool=[]
     while queues:
      for book in list(queues):
       try:pool.append(next(queues[book]))
       except StopIteration:del queues[book]
     selected_ref=prefix(pool);rc=Counter(t for _,ts in selected_ref for t in ts);rv=sorted((w for w in rc if rc[w]>=20),key=lambda w:(-rc[w],w))[:256]
     wp=prefix(records[b].items());wv=out[fold]['vocabulary']
     wv=[wv[i] for i in np.random.default_rng(20261004+2*fold).permutation(len(wv))];rv=[rv[i] for i in np.random.default_rng(20261005+2*fold).permutation(len(rv))]
     wg=independent_geometry([ts for _,ts in wp],wv);rg=independent_geometry([ts for _,ts in selected_ref],rv)
     out[fold].update(reference_records=len(selected_ref),reference_tokens=sum(len(ts) for _,ts in selected_ref),reference_supported_types=sum(n>=20 for n in rc.values()),reference_selected_types=len(rv),written_geometry_capacity=wg['capacity'],reference_geometry_capacity=rg['capacity'],reference_record_ids=[rid for rid,_ in selected_ref],reference_vocabulary=rv,written_opaque_vocabulary=wv)
     checks=[]
     def check(name,ok):checks.append({'check':name,'pass':bool(ok)})
     published=json.load((BASE/'artifacts/CAPACITY.json').open())
     with gzip.open(BASE/'artifacts/BUILDER_AUDIT.json.gz','rt') as f:audit=json.load(f)
     selected_audit=audit['folds'][fold];published_fold=published['folds'][fold]
     check('written_panel_records',out[fold]['panel_record_ids']==published_fold['written_panel']['record_ids'])
     check('reference_panel_records',out[fold]['reference_record_ids']==published_fold['reference_panel']['record_ids'])
     check('written_opaque_nodes',selected_audit['written_nodes']==wv)
     check('reference_opaque_nodes',selected_audit['reference_nodes']==rv)
     relevant=[e for e in eligible[b] if e['raw'] in wv]
     check('all_selected_site_ids',[e['site_id'] for e in relevant]==[e['site_id'] for e in selected_audit['eligible_sites']])
     selected_ids={e['site_id'] for e in relevant};source_ids={site['site_id'] for rid in records[b] for site in sites[rid]}
     check('all_excluded_unsupported_ids',{e['site_id'] for e in selected_audit['excluded_and_unsupported_sites']}==source_ids-selected_ids)
     panelids={rid for rid,_ in wp}
     for item in selected_audit['eligible_sites']+selected_audit['excluded_and_unsupported_sites']:
      original=allsite[item['site_id']]
      assert item['raw_group']==original['raw'] and item['line_id']==original['line_id'] and item['record_id']==original['record_id'] and item['site_index_in_record']==original['ordinal'] and item['marked_span']==original['marked_span']
      reasons=[]
      if original['raw']!=original['marked_span']:reasons.append('marked_span_not_complete_whitespace_group')
      if original['raw'].count('¤')!=1:reasons.append('containing_group_marker_count_not_one')
      assert item['exclusion_reasons']==reasons
      if item['site_id'] in selected_ids:assert item['inside_fit_record']==(item['record_id'] in panelids) and item['written_node']==wv.index(original['raw'])
     check('every_site_identity_eligibility_and_join',True)
     check('capacity_gates',len(wv)==128 and len(rv)>=128 and len({e['raw'] for e in relevant})>=10 and len(relevant)>=200 and wg['capacity'] and rg['capacity'])
     arrays=np.load(runtime/f'fold_{fold}'/'world_00.npz')
     wc=np.array([wg['counts'][w] for w in wv]);rcount=np.array([rg['counts'][w] for w in rv])
     expected={'Dw':wg['distance'],'De':rg['distance'],'p':wc/wc.sum(),'q':rcount/rcount.sum(),'written_rates':wc/sum(len(ts) for _,ts in wp),'reference_rates':rcount/sum(len(ts) for _,ts in selected_ref)}
     errors={name:float(abs(arrays[name]-value).max()) for name,value in expected.items()}
     for name,error in errors.items():check('numerical_array:'+name,error<1e-12)
     out[fold]['checks']=checks;out[fold]['numerical_max_abs_errors']=errors
     if all_worlds:
      world_errors=[]
      for world in range(1,20):
       rebuilt=[]
       for side,panels,nodes in [(0,wp,wv),(1,selected_ref,rv)]:
        lengths=[len(ts) for _,ts in panels];flat=[t for _,ts in panels for t in ts]
        permutation=np.random.default_rng(20261100+100*fold+2*world+side).permutation(len(flat))
        shuffled=[flat[int(k)] for k in permutation];rr=[];offset=0
        for length in lengths:rr.append(shuffled[offset:offset+length]);offset+=length
        assert Counter(shuffled)==Counter(flat)
        geom=independent_geometry(rr,nodes)
        check('null_geometry_capacity:'+str(world)+':'+str(side),geom['capacity'])
        rebuilt.append(geom['distance'])
       payload=np.load(runtime/f'fold_{fold}'/f'world_{world:02d}.npz')
       error=max(float(abs(payload['Dw']-rebuilt[0]).max()),float(abs(payload['De']-rebuilt[1]).max()))
       check('null_geometry_exact:'+str(world),error<1e-12)
       check('null_frequency_invariance:'+str(world),all(np.array_equal(payload[k],expected[k]) for k in ['p','q','written_rates','reference_rates']))
       world_errors.append({'world':world,'max_abs_error':error})
      out[fold]['null_geometry']=world_errors

    return {'status':'PASS' if all(c['pass'] for f in out for c in f['checks']) else 'FAIL','folds':[{k:v for k,v in f.items() if 'vocabulary' not in k and 'record_ids' not in k} for f in out],'excluded_wholegroup_counts':dict(exclusions),'site_gold_read':False}

def pair_costs(arrays):
    dw,de=arrays['Dw'],arrays['De']
    freq=abs(np.log(arrays['written_rates'])[:,None]-np.log(arrays['reference_rates'])[None,:])
    quant=lambda d:np.array([np.quantile(np.delete(row,i),np.linspace(0,1,16),method='linear') for i,row in enumerate(d)])
    w,e=quant(dw),quant(de)
    fingerprints=np.sum((w[:,None,:]-e[None,:,:])**2,axis=2)
    return {name:cost/cost.mean() if cost.mean()>0 else cost for name,cost in [('F',freq),('B',fingerprints)]}

def independent_objective_gradient(z,arrays,cost=None):
    p,q=arrays['p'],arrays['q'];dw,de=arrays['Dw'],arrays['De']
    g=coupling_from_logits(z,p);b=g.sum(axis=0)
    if cost is None:
        cross=dw@g@de.T
        data=float(p@(dw*dw)@p+b@(de*de)@b-2*np.sum(cross*g))
        derivative=2*((dw*dw)@p)[:,None]+2*((de*de)@b)[None,:]-4*cross
    else:
        data=float(np.sum(cost*g));derivative=cost.copy()
    column_log=np.log(b/q);joint_log=np.log(g/(p[:,None]*q[None,:]))
    loss=data+float(b@column_log)+.01*float(np.sum(g*joint_log))
    derivative=derivative+column_log[None,:]+1+.01*(joint_log+1)
    gradient=g*(derivative-np.sum(derivative*(g/p[:,None]),axis=1,keepdims=True))
    return loss,gradient,g

def replay_selected(arrays,model,seed):
    costs=pair_costs(arrays);cost=costs.get(model)
    shape=(len(arrays['p']),len(arrays['q']))
    z=np.log(arrays['q'])[None,:]+np.random.default_rng(seed).normal(0,.1,shape)
    m=np.zeros(shape);v=np.zeros(shape)
    for step in range(1,201):
        _,gradient,_=independent_objective_gradient(z,arrays,cost)
        m=.9*m+.1*gradient;v=.999*v+.001*gradient**2
        z-=.05*(m/(1-.9**step))/(np.sqrt(v/(1-.999**step))+1e-8)
    loss,_,g=independent_objective_gradient(z,arrays,cost)
    return loss,g/arrays['p'][:,None]

def audit_fits(runtime):
    lock=json.loads((BASE/'artifacts/PREDICTION_LOCK.json').read_text());checks=[];replays=[];largest_objective_error=0.0
    def check(name,ok):checks.append({'check':name,'pass':bool(ok)})
    def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    def adigest(a):return hashlib.sha256(np.ascontiguousarray(a,dtype=np.float64).tobytes()).hexdigest()
    check('complete_prediction_lock',lock['jobs']==80 and lock['starts']==492 and lock['site_truth_read'] is False)
    for path,h in lock['bindings'].items():check('locked_file:'+path,digest(BASE/path)==h)
    check('original_capacity_receipt_preserved',digest(BASE/'artifacts/CAPACITY_VALIDATION.json')=='13f8d8fc074a506813c99f938a77d7d21e26c4a1652ec1eab4d57938301283d2')
    check('all_fold_worlds',[(x['fold'],x['world']) for x in lock['predictions']]==[(f,w) for f in range(4) for w in range(20)])
    observed={}
    for item in lock['predictions']:
        fold,world=item['fold'],item['world'];path=BASE/item['path'];payload_path=runtime/f'fold_{fold}'/f'world_{world:02d}.npz'
        check('prediction_and_payload_hash:'+str((fold,world)),digest(path)==item['sha256'] and digest(payload_path)==item['payload_sha256'])
        with gzip.open(path,'rt') as f:pred=json.load(f)
        with np.load(payload_path) as z:arrays={k:z[k] for k in z.files}
        check('anonymous_input_hash:'+str((fold,world)),all(pred['input_sha256'][k]==adigest(v) for k,v in arrays.items()))
        check('model_inventory:'+str((fold,world)),set(pred['models'])==({'F','B','G'} if world==0 else {'B','G'}))
        if world==0:observed[fold]=(arrays,item)
        else:
            base_arrays,base_item=observed[fold]
            check('F_reuse:'+str((fold,world)),all(np.array_equal(arrays[k],base_arrays[k]) for k in ['p','q','written_rates','reference_rates']) and item['F_reuse']['path']==base_item['path'] and item['F_reuse']['sha256']==base_item['sha256'])
        costs=pair_costs(arrays);p,q=arrays['p'],arrays['q'];dw,de=arrays['Dw'],arrays['De']
        for model,data in pred['models'].items():
            tag=f'{fold}:{world}:{model}';rr=np.asarray(data['normalized_rows']);plan=p[:,None]*rr;columns=plan.sum(axis=0)
            check('plan_masses:'+tag,np.isfinite(rr).all() and (rr>=0).all() and np.max(abs(rr.sum(axis=1)-1))<1e-12 and np.max(abs(columns-np.asarray(data['column_masses'])))<1e-12)
            cost=costs.get(model)
            transport=float(p@(dw*dw)@p+columns@(de*de)@columns-2*np.sum((dw@plan@de.T)*plan)) if cost is None else float(np.sum(cost*plan))
            obj=transport+float(np.sum(columns*np.log(columns/q)))+.01*float(np.sum(plan*np.log(rr/q[None,:])))
            error=abs(obj-data['selected_objective']);largest_objective_error=max(largest_objective_error,error)
            check('selected_objective:'+tag,error<1e-10)
            check('full_ranking:'+tag,np.argsort(-rr,axis=1,kind='stable').tolist()==data['ranking'])
            restarts=data['restarts'];winner=min(restarts,key=lambda x:x['objective_after_step200'])
            check('restart_selection:'+tag,[r['seed'] for r in restarts]==[0,1,2] and all(r['steps']==200 for r in restarts) and data['selected_seed']==winner['seed'] and data['selected_objective']==winner['objective_after_step200'] and data['ranking']==winner['ranking'])
            for restart in restarts:
                initial=np.log(q)[None,:]+np.random.default_rng(restart['seed']).normal(0,.1,(len(p),len(q)))
                comp=restart['components'];restart_obj=comp['data_cost']+comp['column_kl']+.01*comp['joint_kl']
                check('restart_record:'+tag+':'+str(restart['seed']),adigest(initial)==restart['initial_logits_sha256'] and math.isfinite(restart['objective_after_step200']) and abs(restart_obj-restart['objective_after_step200'])<1e-10 and all(sorted(r)==list(range(len(q))) for r in restart['ranking']))
            if world==0:
                independent_loss,independent_rows=replay_selected(arrays,model,data['selected_seed'])
                maxrow=float(abs(independent_rows-rr).max());ranking=np.argsort(-independent_rows,axis=1,kind='stable')
                mismatches=int(np.sum(ranking!=np.asarray(data['ranking'])))
                check('independent_200step_Adam:'+tag,abs(independent_loss-data['selected_objective'])<1e-9 and maxrow<1e-8 and mismatches==0)
                replays.append({'fold':fold,'model':model,'seed':data['selected_seed'],'objective_error':abs(independent_loss-data['selected_objective']),'row_max_abs_error':maxrow,'ranking_mismatches':mismatches})
    return {'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','checks':checks,'independent_Adam_replays':replays,'largest_selected_objective_error':largest_objective_error,'prediction_lock_sha256':digest(BASE/'artifacts/PREDICTION_LOCK.json'),'site_gold_read':False,'limit':'All164 selected plans/objectives/rankings and492 restart records audited; full Adam independently replayed only12 observed selected starts, not all492 trajectories.'}

def audit_scores():
    def loadgzip(name):
        with gzip.open(BASE/'artifacts'/name,'rt') as f:return json.load(f)
    def frac(x):return Fraction(x['numerator'],x['denominator'])
    def mean(xs):return sum(xs,Fraction())/len(xs)
    checks=[]
    def check(name,ok):checks.append({'check':name,'pass':bool(ok)})
    lock=json.loads((BASE/'artifacts/PREDICTION_LOCK.json').read_text())
    assert lock['status']=='ALL_PREDICTIONS_LOCKED_BEFORE_GOLD' and lock['jobs']==80
    audit=loadgzip('BUILDER_AUDIT.json.gz');published=loadgzip('ALL_SCORES.json.gz');types=loadgzip('TYPE_RESULTS.json.gz');evaluation=loadgzip('EVALUATION_SITES.json.gz')
    reported=json.loads((BASE/'artifacts/RESULT.json').read_text());opening=json.loads((BASE/'artifacts/GOLD_OPENING_RECEIPT.json').read_text())
    check('gold_after_lock',opening['gold_opening_utc']>lock['locked_utc'] and opening['prediction_lock_sha256']==hashlib.sha256((BASE/'artifacts/PREDICTION_LOCK.json').read_bytes()).hexdigest())
    gold={}
    with (ROOT/'gdt155_unblinded_abbreviation_sites.tsv').open() as f:
        for r in csv.DictReader(f,delimiter='\t'):
            if r['corpus']=='NUREMBERG' and r['book_or_ms'] in ['Band2','Band3','Band4','Band5']:
                assert r['site_id'] not in gold;gold[r['site_id']]=r
    rows_by_fold={};inventory=Counter();expected_eval={};oracle_by_fold=[];type_lookup={(t['fold'],t['written_node']):t for t in types['types']};collision_expected=[]
    for fold in audit['folds']:
        f=fold['fold'];groups=defaultdict(list);reference=fold['reference_nodes'];vocabulary=set(reference)
        for row in fold['eligible_sites']+fold['excluded_and_unsupported_sites']:
            truth=gold[row['site_id']]
            assert truth['record_id']==row['record_id'] and truth['line_id']==row['line_id'] and truth['book_or_ms']==fold['book'] and int(truth['site_index_in_record'])==row['site_index_in_record']
        for row in fold['eligible_sites']:
            text=gold[row['site_id']]['expanded_span'];reason='empty' if not text.split() else ('multiword' if len(text.split())!=1 else ('in_inventory' if text in vocabulary else 'out_of_candidate_inventory'))
            inventory[reason]+=1;groups[row['written_node']].append((text,row['inside_fit_record']))
            expected_eval[row['site_id']]=dict(row,truth=text,truth_inventory_status=reason)
        rows_by_fold[f]=groups;oracles=[];bytruth=defaultdict(set)
        for node,events in groups.items():
            hist=Counter(t for t,_ in events);tr=type_lookup[(f,node)]
            for t in hist:bytruth[t].add(node)
            candidate_hist={t:n for t,n in hist.items() if len(t.split())==1 and t in vocabulary}
            oracle=Fraction(sum(sorted(candidate_hist.values(),reverse=True)[:5]),len(events));oracles.append(oracle)
            expected_mixture=[{'truth':t,'count':n,'candidate_index':reference.index(t) if t in candidate_hist else None} for t,n in sorted(hist.items())]
            check('type_mixture:'+str((f,node)),tr['sites']==len(events) and tr['written_form']==fold['written_nodes'][node] and tr['truth_mixture']==expected_mixture and frac(tr['oracle_top5'])==oracle and tr['outside_fit_sites']==sum(not inside for _,inside in events))
        oracle_by_fold.append(mean(oracles))
        collision_expected.extend({'fold':f,'truth':t,'written_nodes':sorted(ns)} for t,ns in sorted(bytruth.items()) if len(ns)>1)
    check('every_evaluation_site',len(evaluation['sites'])==len(expected_eval) and all(expected_eval.get(r['site_id'])==r for r in evaluation['sites']))
    check('all_truth_collisions',types['truth_collisions']==collision_expected)
    scorelookup={(r['world'],r['fold'],r['model']):r for r in published['scores']};prediction_lookup={(r['fold'],r['world']):r for r in lock['predictions']};foldscores={};allmetrics={};replay_count=0
    for world in range(20):
        for f in range(4):
            fold=audit['folds'][f];reference=fold['reference_nodes'];groups=rows_by_fold[f]
            with gzip.open(BASE/prediction_lookup[(f,world)]['path'],'rt') as stream:models=json.load(stream)['models']
            if world:
                with gzip.open(BASE/prediction_lookup[(f,0)]['path'],'rt') as stream:models['F']=json.load(stream)['models']['F']
            for model in ['F','B','G']:
                rec=scorelookup[(world,f,model)];pertype=[];outside=[];weighted=defaultdict(Fraction);alln=0
                reported_types={r['written_node']:r for r in rec['type_scores']}
                for node,events in sorted(groups.items()):
                    ranks={reference[j]:rank for rank,j in enumerate(models[model]['ranking'][node],1)}
                    def metrics(ev):
                        numerator=[Fraction(),Fraction(),Fraction()]
                        for truth,n in Counter(t for t,_ in ev).items():
                            rank=ranks.get(truth) if len(truth.split())==1 else None
                            if rank is not None:
                                numerator[0]+=n*(rank==1);numerator[1]+=n*(rank<=5);numerator[2]+=Fraction(n,rank)
                        return {k:v/len(ev) for k,v in zip(['top1','top5','MRR'],numerator)}
                    values=metrics(events);extra=[event for event in events if not event[1]];extra_values=metrics(extra) if extra else None
                    t=reported_types[node]
                    check('all_world_type:'+str((world,f,model,node)),t['sites']==len(events) and all(frac(t['metrics'][k])==v for k,v in values.items()) and ((t['outside_fit_metrics'] is None and extra_values is None) or (extra_values is not None and all(frac(t['outside_fit_metrics'][k])==v for k,v in extra_values.items()))))
                    pertype.append(values);alln+=len(events)
                    for k,v in values.items():weighted[k]+=v*len(events)
                    if extra:outside.append((extra_values,len(extra)))
                    if world==0:
                        rt=type_lookup[(f,node)]['observed_models'][model]
                        check('observed_candidate_row:'+str((f,model,node)),all(frac(rt['metrics'][k])==v for k,v in values.items()) and rt['top5']==[reference[j] for j in models[model]['ranking'][node][:5]] and rt['selected_seed']==models[model]['selected_seed'])
                macro={k:mean([v[k] for v in pertype]) for k in ['top1','top5','MRR']}
                check('all_world_macro:'+str((world,f,model)),rec['types']==len(groups) and rec['sites']==alln and all(frac(rec['macro'][k])==v and frac(rec['weighted'][k])==weighted[k]/alln for k,v in macro.items()))
                if outside:check('all_world_outside_macro:'+str((world,f,model)),rec['outside_fit']['types']==len(outside) and rec['outside_fit']['sites']==sum(n for _,n in outside) and all(frac(rec['outside_fit']['macro'][k])==mean([v[k] for v,_ in outside]) for k in macro))
                foldscores[(world,f,model)]=macro['top5'];allmetrics[(world,f,model)]=macro;replay_count+=1
    aggregates={w:{m:mean([foldscores[(w,f,m)] for f in range(4)]) for m in ['F','B','G']} for w in range(20)}
    gains={w:a['G']-max(a['F'],a['B']) for w,a in aggregates.items()};rank=Fraction(1+sum(gains[w]>=gains[0] for w in range(1,20)),20)
    good=sum(foldscores[(0,f,'G')]>max(foldscores[(0,f,'F')],foldscores[(0,f,'B')]) for f in range(4))
    gates={'G_top5_at_least_half':aggregates[0]['G']>=Fraction(1,2),'gain_at_least_tenth':gains[0]>=Fraction(1,10),'books_above_both_at_least3':good>=3,'null_rank_at_most_twentieth':rank<=Fraction(1,20)}
    check('all240_fold_model_scores',replay_count==len(published['scores'])==240)
    check('observed_exact_aggregate',all(frac(reported['observed_macro_top5'][m])==v for m,v in aggregates[0].items()) and frac(reported['observed_gain'])==gains[0])
    check('every_null_aggregate',len(reported['worlds'])==20 and all(r['world']==w and frac(r['gain'])==gains[w] and all(frac(r['aggregate_macro_top5'][m])==v for m,v in aggregates[w].items()) for w,r in enumerate(reported['worlds'])))
    check('rank_gates_status',frac(reported['null_rank'])==rank and reported['books_G_above_both']==good and reported['gates']==gates and reported['status']==('SOURCE_CONTEXT_RANKING_SUPPORTED' if all(gates.values()) else 'NO_SUPPORTED_SOURCE_CONTEXT_RANKING'))
    check('coverage_oracle',reported['eligible_sites']==len(expected_eval) and reported['eligible_types']==len(type_lookup) and reported['truth_inventory_counts']==dict(inventory) and frac(reported['oracle_macro_top5'])==mean(oracle_by_fold))
    return {'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','checks':checks,'reconstructed_fold_model_scores':replay_count,'selected_sites':len(expected_eval),'selected_types':len(type_lookup),'independent_observed_top5':{m:str(v) for m,v in aggregates[0].items()},'independent_gain':str(gains[0]),'independent_null_rank':str(rank),'independent_gates':gates,'meaning_confirmation':False}

def final_summary():
    names=['CAPACITY_VALIDATION.json','GEOMETRY_VALIDATION.json','FIT_VALIDATION.json','SCORE_VALIDATION.json']
    records={name:json.loads((BASE/'artifacts'/name).read_text()) for name in names}
    statuses={name:r['status'] for name,r in records.items()}
    hashes={name:hashlib.sha256((BASE/'artifacts'/name).read_bytes()).hexdigest() for name in names+['PREDICTION_LOCK.json','RESULT.json']}
    geometrychecks=sum(len(f['checks']) for f in records['GEOMETRY_VALIDATION.json']['folds'])
    count=geometrychecks+len(records['FIT_VALIDATION.json']['checks'])+len(records['SCORE_VALIDATION.json']['checks'])
    return {'status':'PASS' if all(v=='PASS' for v in statuses.values()) else 'FAIL','phase_statuses':statuses,'checks_excluding_duplicated_observed_capacity':count,'geometry_checks':geometrychecks,'fit_checks':len(records['FIT_VALIDATION.json']['checks']),'score_checks':len(records['SCORE_VALIDATION.json']['checks']),'receipt_sha256':hashes,'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'independent_numerical_fixture':numerical_fixture(),'initial_capacity_validator_sha256':'af4cd72241a7dd3e17bc991e42095dc300b734a5c96c8fbbd906ba3f31e73c9a','initial_capacity_receipt_preserved':hashes['CAPACITY_VALIDATION.json']=='13f8d8fc074a506813c99f938a77d7d21e26c4a1652ec1eab4d57938301283d2','independence':'No builder/fitter/scorer imports. Original source/panel/site/geometry reconstruction, separate NumPy analytic-gradient Adam, and separate Fraction scoring. Serialization and fitter implementation inspected after independent equations were written.','scope':['All80 observed/null geometries and token-count-preserving seed constructions','All164 selected transport plans, objectives and complete rankings','All492 restart record initialization hashes, finite objective/component records and minimum selection; not independent replay of all492 trajectories','Twelve complete observed selected-start Adam replays with identical rankings','All240 fold/world/model score records, all156 selected marked types and47342 selected sites, exact null arithmetic'], 'limits':['Prospective local validation plan was not part of initial public registration commit.','Capacity receipt predates extended validator code and remains unchanged; original hash retained.','Source expansion labels are editorial representation truth, not Voynich meanings.','Nonconvex fixed optimizer was checked, not certified globally optimal.','Source negative result does not reject every context representation; no unregistered baseline promotion or tuning follows.']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fixture-only',action='store_true');parser.add_argument('--runtime',type=Path);parser.add_argument('--all-worlds',action='store_true');parser.add_argument('--fits',action='store_true');parser.add_argument('--scores',action='store_true');parser.add_argument('--release-gold',action='store_true');parser.add_argument('--summary',action='store_true');args=parser.parse_args()
    if args.summary:
        result=final_summary()
        (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'status':result['status'],'checks':result['checks_excluding_duplicated_observed_capacity']}))
        return int(result['status']!='PASS')
    if args.fixture_only:
        result=numerical_fixture();print(json.dumps(result,indent=2));return int(not result['agreement'])
    if args.runtime is None:raise SystemExit('--runtime required for released source validation')
    for name in ['METHOD.md','SPEC.json']:
        path=BASE/name
        assert subprocess.check_output(['git','show','ca1d9ec93:'+str(path.relative_to(ROOT))],cwd=ROOT)==path.read_bytes()
    spec=json.loads((BASE/'SPEC.json').read_text())
    for name,h in spec['inputs'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
    if args.scores:
        assert args.release_gold,'Explicit post-lock root gold release required'
        result=audit_scores()
        (BASE/'artifacts/SCORE_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'status':result['status'],'checks':len(result['checks']),'failures':[c for c in result['checks'] if not c['pass']],'gain':result['independent_gain'],'null_rank':result['independent_null_rank']}))
        return int(result['status']!='PASS')
    if args.fits:
        result=audit_fits(args.runtime)
        (BASE/'artifacts/FIT_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'status':result['status'],'checks':len(result['checks']),'failures':[c for c in result['checks'] if not c['pass']],'replays':result['independent_Adam_replays']}))
        return int(result['status']!='PASS')
    result=audit_source(args.runtime,args.all_worlds);result['fixture']=numerical_fixture()
    result['plan_timing']='Prospective local plan before source access; plan was not included in initial public registration commit.'
    result['independence']='No builder/fitter/scorer imports. Independent original-table token/site/panel/geometry reconstruction.'
    (BASE/'artifacts'/('GEOMETRY_VALIDATION.json' if args.all_worlds else 'CAPACITY_REPLAY.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'folds':len(result['folds']),'fixture_pass':result['fixture']['agreement']}))
    return int(result['status']!='PASS' or not result['fixture']['agreement'])
if __name__=='__main__':raise SystemExit(main())
