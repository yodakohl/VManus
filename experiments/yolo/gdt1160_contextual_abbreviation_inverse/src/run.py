#!/usr/bin/env python3
"""GDT1160 frozen source-only contextual abbreviation calibration.

prepare/selftest do not fit the real panel. fit requires a public registration
lock and writes no held gold. score is separate and requires prediction locks.
"""
from __future__ import annotations
import argparse, collections, csv, gzip, hashlib, io, json, math, os
from pathlib import Path
import time
import tempfile

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
ART = EXP / 'artifacts'
SPEC_PATH = EXP / 'SPEC.json'

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def read(path):
    with open(path,encoding='utf-8',newline='') as f:yield from csv.DictReader(f,delimiter='\t')
def spec():
    s=json.loads(SPEC_PATH.read_text())
    for name,digest in s['source_inputs'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Source hash mismatch: '+name)
    return s

def observed(s):
    """All eligibility and contexts are functions of blinded source fields."""
    lines=[r for r in read(ROOT/'gdt155_blinded_diplomatic.tsv') if r['corpus']=='NUREMBERG']
    records=collections.defaultdict(list)
    for r in lines:records[r['record_id']].append(r)
    sites=collections.defaultdict(list)
    for r in read(ROOT/'gdt155_blinded_abbreviation_sites.tsv'):
        if r['corpus']=='NUREMBERG':sites[r['line_id']].append(r)
    rows=[]
    for rid,rr in records.items():
        rr.sort(key=lambda r:int(r['line_index']))
        nlines=int(rr[0]['record_line_count'])
        assert [int(r['line_index']) for r in rr]==list(range(1,nlines+1))
        allgroups=[t for r in rr for t in r['diplomatic_marked'].split()]
        base=0
        for line in rr:
            tokens=line['diplomatic_marked'].split()
            assignments=[(i,t) for i,t in enumerate(tokens) for _ in range(t.count('¤'))]
            ss=sorted(sites[line['line_id']],key=lambda r:int(r['site_index_in_record']))
            assert len(ss)==len(assignments)
            for r,(i,t) in zip(ss,assignments):
                if not (t.count('¤')==1 and t==r['surface_span_marked']):continue
                pos=base+i
                window=tuple(allgroups[pos+d] if 0<=pos+d<len(allgroups) else None for d in range(-8,9) if d)
                layout=[0.]*10
                layout[int(line['record_position_quartile'])]=1.
                layout[4+min(3,4*i//len(tokens))]=1.
                layout[8]=float(int(line['line_index'])==1)
                layout[9]=float(int(line['line_index'])==nlines)
                rows.append(dict(site_id=r['site_id'],book=line['book_or_ms'],page=line['page_id'],record_id=rid,line_id=line['line_id'],group_index=i,marked=t,layout=layout,window=window))
            base+=len(tokens)
    assert len(rows)==s['expected_source_eligible_sites'],len(rows)
    assert len({r['site_id'] for r in rows})==len(rows)
    return rows

def expansions(books):
    # Only retained training books enter the map. Held labels are not inputs.
    return {r['site_id']:r['expanded_span'] for r in read(ROOT/'gdt155_unblinded_abbreviation_sites.tsv') if r['corpus']=='NUREMBERG' and r['book_or_ms'] in books}

def fold_data(rows,s,fi):
    held=s['books'][fi];gold=expansions(set(s['books'])-{held})
    counts=collections.defaultdict(collections.Counter);pages=collections.defaultdict(set)
    for r in rows:
        if r['book']==held:continue
        e=gold[r['site_id']];counts[r['marked']][e]+=1;pages[r['marked'],e].add((r['book'],r['page']))
    support=s['training_type_support']
    families=sorted(k for k,v in counts.items() if sum(n>=support['minimum_sites_per_supported_expansion'] and len(pages[k,e])>=support['minimum_pages_per_supported_expansion'] for e,n in v.items())>=support['minimum_expansions'])
    famset=set(families)
    train=sorted((r for r in rows if r['book']!=held and r['marked'] in famset),key=lambda r:r['site_id'])
    test=[r for r in rows if r['book']==held and r['marked'] in famset]
    assert len(test)==s['expected_held_sites'][fi],(held,len(test))
    domains={k:sorted(counts[k]) for k in families}
    mn=[]
    for k in families:
        ok={e for e,n in counts[k].items() if n>=5 and len(pages[k,e])>=3}
        if any(e.endswith('m') and e[:-1]+'n' in ok for e in ok):mn.append(k)
    windows={(r['marked'],r['window']) for r in train}
    meta=dict(book=held,fold_index=fi,training_sites=len(train),held_sites=len(test),families=families,candidate_domains=domains,training_counts={k:dict(counts[k]) for k in families},mn_marked_types=mn,held_site_ids_sha256=hashlib.sha256(('\n'.join(sorted(r['site_id'] for r in test))+'\n').encode()).hexdigest())
    return train,test,gold,meta,windows

def hashed_context(window):
    counts=collections.Counter()
    for d,word in zip([d for d in range(-8,9) if d],window):
        if word is None:continue
        for n in (2,3,4):
            for i in range(len(word)-n+1):
                key=(str(d)+':'+word[i:i+n]).encode('utf-8')
                counts[int.from_bytes(hashlib.sha256(key).digest()[:8],'big')%4096]+=1
    den=math.sqrt(sum(v*v for v in counts.values()))
    return [(k,v/den) for k,v in sorted(counts.items())] if den else []

def build_features(rows,families,context_cache):
    import numpy as np
    fm={k:i for i,k in enumerate(families)};base=len(families)+10
    x=np.zeros((len(rows),base+4096),dtype=np.float32);fids=np.empty(len(rows),dtype=np.int64)
    for i,r in enumerate(rows):
        f=fm[r['marked']];fids[i]=f;x[i,f]=1.;x[i,len(families):base]=r['layout']
        w=r['window']
        if w not in context_cache:context_cache[w]=hashed_context(w)
        for j,v in context_cache[w]:x[i,base+j]=v
    return x,fids,base

def configuration_hashes():
    return {'SPEC.json':sha(SPEC_PATH),'src/run.py':sha(Path(__file__))}

def prepare():
    s=spec();rows=observed(s)
    payload={'status':'SOURCE_CAPACITY_ONLY_NO_MODEL_FIT','source_sha256':s['source_inputs'],'configuration_sha256':configuration_hashes(),'source_eligible_sites':len(rows),'folds':[]}
    for fi in range(4):payload['folds'].append(fold_data(rows,s,fi)[3])
    save(ART/'PREPARATION.json',payload)
    print(json.dumps({'status':payload['status'],'held_sites':[f['held_sites'] for f in payload['folds']]}))

def write_gzip_rows(path,rows):
    with open(path,'wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as zipped:
            for r in rows:zipped.write((json.dumps(r,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode())

def fit(fi,work_dir):
    import numpy as np
    import torch
    lock=ART/'REGISTRATION_LOCK.json'
    if not lock.exists():raise RuntimeError('Public preregistration lock absent; real fitting forbidden')
    registration=json.loads(lock.read_text())
    if registration.get('configuration_sha256')!=configuration_hashes():raise RuntimeError('Registered configuration hashes do not match current files')
    if not registration.get('commit'):raise RuntimeError('Registration lacks public commit binding')
    s=spec();torch.set_num_threads(s['training']['threads_per_fit']);torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True)
    target=ART/f'PREDICTIONS_{s["books"][fi]}.jsonl.gz'
    if target.exists():raise RuntimeError('Refusing to overwrite frozen predictions')
    rows=observed(s);train,test,gold,meta,windows=fold_data(rows,s,fi)
    cache={};xn,fn,base=build_features(train,meta['families'],cache);xtn,ftn,_=build_features(test,meta['families'],cache);del cache,rows
    x=torch.from_numpy(xn);xt=torch.from_numpy(xtn);f=torch.from_numpy(fn);ft=torch.from_numpy(ftn)
    outputs=sorted({e for es in meta['candidate_domains'].values() for e in es});out_index={e:i for i,e in enumerate(outputs)}
    y=torch.tensor([out_index[gold[r['site_id']]] for r in train],dtype=torch.long)
    nf=len(meta['families']);nout=len(outputs)
    prior=torch.full((nf,nout),-float('inf'),dtype=torch.float32)
    domain_indices=[];fp=[]
    for kidx,k in enumerate(meta['families']):
        counts=meta['training_counts'][k];total=sum(counts.values());ix=[out_index[e] for e in meta['candidate_domains'][k]];domain_indices.append(ix)
        probs=[counts[e]/total for e in meta['candidate_domains'][k]];fp.append(probs)
        prior[kidx,ix]=torch.tensor([math.log(p) for p in probs],dtype=torch.float32)
    seed_predictions={a:[] for a in ('L','C','N')};curves=[];weights=[]
    work_dir.mkdir(parents=True,exist_ok=True)
    for arm in ('L','C','N'):
        width=base if arm=='L' else x.shape[1]
        for rawseed in s['training']['seeds']:
            seed=rawseed+100*fi;torch.manual_seed(seed)
            model=torch.nn.Linear(width,nout) if arm!='N' else torch.nn.Sequential(torch.nn.Linear(width,64),torch.nn.ReLU(),torch.nn.Linear(64,nout))
            opt=torch.optim.AdamW(model.parameters(),lr=s['training']['learning_rate'],weight_decay=s['training']['weight_decay'])
            generator=torch.Generator().manual_seed(seed)
            epoch_losses=[];start=time.monotonic();model.train()
            for epoch in range(s['training']['epochs']):
                permutation=torch.randperm(len(train),generator=generator);total_loss=0.
                for ix in permutation.split(s['training']['batch_size']):
                    opt.zero_grad(set_to_none=True)
                    logits=model(x[ix,:width])+prior[f[ix]]
                    loss=torch.nn.functional.cross_entropy(logits,y[ix]);loss.backward();opt.step()
                    total_loss+=float(loss.detach())*len(ix)
                epoch_losses.append(total_loss/len(train))
                if (epoch+1)%5==0:print(f'{meta["book"]} {arm} seed{seed} epoch{epoch+1} loss{epoch_losses[-1]:.6f}',flush=True)
            model.eval();pred=[]
            with torch.no_grad():
                for startidx in range(0,len(test),256):
                    probs=torch.softmax(model(xt[startidx:startidx+256,:width])+prior[ft[startidx:startidx+256]],dim=1).cpu().numpy()
                    for j,p in enumerate(probs):pred.append([float(p[z]) for z in domain_indices[int(ftn[startidx+j])]])
            seed_predictions[arm].append(pred)
            weightfile=work_dir/f'{meta["book"]}_{arm}_{seed}.npz'
            np.savez_compressed(weightfile,**{k:v.detach().numpy() for k,v in model.state_dict().items()})
            weights.append(dict(arm=arm,seed=seed,local_working_basename=weightfile.name,sha256=sha(weightfile),published=False))
            curves.append(dict(arm=arm,seed=seed,epoch_mean_online_batch_cross_entropy=epoch_losses,loss_note='Sample-weighted online pre-update batch CE; not a full post-epoch reevaluation; AdamW decoupled weight decay is not added to the displayed CE.',elapsed_seconds=time.monotonic()-start))
            del model,opt
    predrows=[]
    for i,r in enumerate(test):
        k=r['marked'];fid=int(ftn[i]);candidates=meta['candidate_domains'][k]
        scores={'F':fp[fid]};seedp={}
        for arm in ('L','C','N'):
            seedp[arm]=[seed_predictions[arm][ss][i] for ss in range(2)]
            scores[arm]=[(a+b)/2 for a,b in zip(*seedp[arm])]
        chosen={arm:candidates[max(range(len(candidates)),key=lambda j:probs[j])] for arm,probs in scores.items()}
        predrows.append(dict(site_id=r['site_id'],book=r['book'],record_id=r['record_id'],line_id=r['line_id'],marked_group=k,candidates=candidates,probabilities=scores,seed_probabilities=seedp,predictions=chosen,novel_exact_context=(k,r['window']) not in windows,mn_training_type=k in meta['mn_marked_types']))
    write_gzip_rows(target,predrows)
    fitmeta=dict(status='PREDICTIONS_FROZEN_NO_HELD_GOLD_SCORED',fold=meta,configuration_sha256=configuration_hashes(),source_sha256=s['source_inputs'],registration_lock_sha256=sha(lock),torch_version=torch.__version__,numpy_version=np.__version__,output_vocabulary=outputs,train_curves=curves,weights_local_only=weights,prediction_file=target.name,prediction_sha256=sha(target))
    save(ART/f'FIT_{meta["book"]}.json',fitmeta)
    print(json.dumps({'book':meta['book'],'held_predictions':len(predrows),'prediction_sha256':sha(target)}),flush=True)

def freeze_predictions():
    s=spec();files={}
    for book in s['books']:
        for name in [f'PREDICTIONS_{book}.jsonl.gz',f'FIT_{book}.json']:
            p=ART/name
            if not p.exists():raise RuntimeError('Incomplete fit panel: '+name)
            files[name]=sha(p)
        f=json.loads((ART/f'FIT_{book}.json').read_text())
        if f['configuration_sha256']!=configuration_hashes():raise RuntimeError('Fit configuration changed')
        if f['prediction_sha256']!=files[f'PREDICTIONS_{book}.jsonl.gz']:raise RuntimeError('Prediction hash mismatch')
    path=ART/'PREDICTION_LOCK.json'
    if path.exists():raise RuntimeError('Prediction lock already exists')
    save(path,dict(status='ALL_FOUR_FOLDS_FROZEN_BEFORE_SCORING',configuration_sha256=configuration_hashes(),files=files))
    print('Prediction lock written')

def accuracy(rows,arm):return sum(r['correct'][arm] for r in rows)/len(rows) if rows else None

def metrics(rows,arm):
    types=collections.defaultdict(list);records=collections.defaultdict(list)
    for r in rows:types[r['marked_group']].append(r);records[r['record_id']].append(r)
    return dict(sites=len(rows),types=len(types),token_accuracy=accuracy(rows,arm),macro_type_accuracy=sum(accuracy(rr,arm) for rr in types.values())/len(types) if types else None,records=len(records),all_ambiguous_sites_correct_record_accuracy=sum(all(r['correct'][arm] for r in rr) for rr in records.values())/len(records) if records else None)

def score():
    s=spec();lock=json.loads((ART/'PREDICTION_LOCK.json').read_text())
    assert lock['configuration_sha256']==configuration_hashes()
    for name,digest in lock['files'].items():assert sha(ART/name)==digest
    gold=expansions(set(s['books']));folds=[];allrows=[];typerows=[]
    for book in s['books']:
        with gzip.open(ART/f'PREDICTIONS_{book}.jsonl.gz','rt',encoding='utf-8') as f:pr=[json.loads(line) for line in f]
        rs=[]
        for p in pr:
            truth=gold[p['site_id']]
            rr={k:p[k] for k in ['site_id','book','record_id','line_id','marked_group','novel_exact_context','mn_training_type','predictions']}
            rr.update(truth=truth,truth_in_candidates=truth in p['candidates'],correct={a:p['predictions'][a]==truth for a in ('F','L','C','N')})
            rs.append(rr)
        arms={a:metrics(rs,a) for a in ('F','L','C','N')}
        second={name:{a:metrics([r for r in rs if r[field]],a) for a in ('F','L','C','N')} for name,field in [('novel_context','novel_exact_context'),('terminal_m_n','mn_training_type')]}
        folds.append(dict(book=book,arms=arms,secondary=second,oov_truths=sum(not r['truth_in_candidates'] for r in rs)))
        bytype=collections.defaultdict(list)
        for r in rs:bytype[r['marked_group']].append(r)
        for k,rr in sorted(bytype.items()):typerows.append(dict(book=book,marked_group=k,sites=len(rr),oov_truths=sum(not r['truth_in_candidates'] for r in rr),accuracy={a:accuracy(rr,a) for a in ('F','L','C','N')}))
        allrows.extend(rs)
    macro={a:sum(f['arms'][a]['macro_type_accuracy'] for f in folds)/4 for a in ('F','L','C','N')}
    gains={a:[f['arms'][a]['macro_type_accuracy']-max(f['arms']['F']['macro_type_accuracy'],f['arms']['L']['macro_type_accuracy']) for f in folds] for a in ('C','N')}
    mean_context_gains={a:macro[a]-max(macro['F'],macro['L']) for a in ('C','N')}
    context_gates={a:mean_context_gains[a]>=.03 and sum(x>0 for x in v)>=3 for a,v in gains.items()}
    nc=[f['arms']['N']['macro_type_accuracy']-f['arms']['C']['macro_type_accuracy'] for f in folds]
    neural=context_gates['N'] and sum(nc)/4>=.01 and sum(x>0 for x in nc)>=3
    result=dict(status=('CONTEXT_AND_NEURAL_INCREMENT' if context_gates['C'] and neural else 'NEURAL_CONTEXT_ONLY' if neural else 'CONTEXT_INCREMENT_ONLY' if context_gates['C'] else 'NO_PROMOTED_CONTEXT_MODEL'),scope='SUPERVISED_SOURCE_CALIBRATION_ONLY',sites=len(allrows),folds=folds,equal_fold_macro_type_accuracy=macro,context_gains_over_fold_max_F_L=gains,context_mean_gains_over_max_mean_F_L=mean_context_gains,context_gate_pass=context_gates,neural_gains_over_C=nc,neural_gate_pass=neural,prediction_lock_sha256=sha(ART/'PREDICTION_LOCK.json'))
    save(ART/'RESULT.json',result);save(ART/'TYPE_RESULTS.json',typerows);write_gzip_rows(ART/'SITE_RESULTS.jsonl.gz',allrows)
    print(json.dumps({k:v for k,v in result.items() if k!='folds'},ensure_ascii=False))

def selftest():
    # Invented fixtures only: hash identity, signed order, missing slots, masks.
    assert hashed_context((None,)*16)==[]
    w=[None]*16;w[0]='Ab¤';x=hashed_context(tuple(w));assert abs(sum(v*v for k,v in x)-1)<1e-12
    w2=[None]*16;w2[-1]='Ab¤';assert x!=hashed_context(tuple(w2))
    import torch
    z=torch.tensor([[0.,-float('inf'),math.log(3.)]])
    p=torch.softmax(z,dim=1);assert p[0,1].item()==0 and abs(p[0,2].item()-.75)<1e-6
    assert ['aa','bb'][max(range(2),key=lambda i:[.5,.5][i])]=='aa'
    print('SELFTEST_PASS invented-only')

def main():
    a=argparse.ArgumentParser();a.add_argument('command',choices=['prepare','selftest','fit','freeze','score']);a.add_argument('--fold',type=int,choices=range(4));a.add_argument('--work-dir',type=Path,default=Path(tempfile.gettempdir())/'gdt1160_weights');args=a.parse_args()
    if args.command=='prepare':prepare()
    elif args.command=='selftest':selftest()
    elif args.command=='fit':
        if args.fold is None:a.error('fit needs --fold')
        fit(args.fold,args.work_dir)
    elif args.command=='freeze':freeze_predictions()
    else:score()
if __name__=='__main__':main()
