#!/usr/bin/env python3
"""Exact post-prediction-lock accounting; no fitting or candidate choice."""
import csv,gzip,hashlib,json
from collections import Counter,defaultdict
from fractions import Fraction
from datetime import datetime,timezone
from pathlib import Path
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2]
MODELS=['F','B','G']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def unpack(p):return json.loads(gzip.decompress(p.read_bytes()))
def packed(p,x):p.write_bytes(gzip.compress((json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
def exact(f):return {'numerator':f.numerator,'denominator':f.denominator,'value':float(f)}
def mean(xs):return sum(xs,Fraction(0))/len(xs)

def metric_for_sites(rows,rank,reference):
    lookup={word:i for i,word in enumerate(reference)}
    hist=Counter(r['truth'] for r in rows);inverse={int(j):i+1 for i,j in enumerate(rank)}
    n=len(rows);totals=[Fraction(0),Fraction(0),Fraction(0)]
    for truth,count in hist.items():
        pos=inverse.get(lookup.get(truth,-1)) if len(truth.split())==1 else None
        if pos is not None:
            totals[0]+=count*int(pos==1);totals[1]+=count*int(pos<=5);totals[2]+=Fraction(count,pos)
    return {k:v/n for k,v in zip(['top1','top5','MRR'],totals)}

def score_locked(runtime):
    lock=read(EXP/'artifacts/PREDICTION_LOCK.json');assert lock['status']=='ALL_PREDICTIONS_LOCKED_BEFORE_GOLD' and lock['site_truth_read'] is False
    assert lock['jobs']==80 and lock['starts']==492
    assert {(r['fold'],r['world']) for r in lock['predictions']}=={(f,w) for f in range(4) for w in range(20)}
    for rel,pin in lock['bindings'].items():assert sha(EXP/rel)==pin,rel
    for r in lock['predictions']:assert sha(EXP/r['path'])==r['sha256']
    spec=read(EXP/'SPEC.json');audit=unpack(EXP/'artifacts/BUILDER_AUDIT.json.gz')
    assert audit['gold_read'] is False
    goldpath=ROOT/'gdt155_unblinded_abbreviation_sites.tsv';assert sha(goldpath)==spec['inputs'][goldpath.name]
    # This is the first semantic truth read in the pipeline, after all locks above.
    opening={'gold_opening_utc':datetime.now(timezone.utc).isoformat(),'prediction_lock_sha256':sha(EXP/'artifacts/PREDICTION_LOCK.json'),'gold_sha256':sha(goldpath),'stage':'AFTER_LOCK_BEFORE_SEMANTIC_READ'}
    (EXP/'artifacts/GOLD_OPENING_RECEIPT.json').write_text(json.dumps(opening,indent=2)+'\n')
    gold={}
    with goldpath.open(newline='') as f:
        for row in csv.DictReader(f,delimiter='\t'):
            if row['corpus']==spec['corpus'] and row['book_or_ms'] in spec['books']:
                assert row['site_id'] not in gold;gold[row['site_id']]=row
    evaluations=[];type_rows=[];all_scores=[];fractions={};fold_data={}
    for fold in audit['folds']:
        idx=fold['fold'];book=fold['book'];bytype=defaultdict(list)
        reference=fold['reference_nodes'];vocab=set(reference)
        for original in fold['eligible_sites']:
            truth=gold[original['site_id']]
            assert truth['record_id']==original['record_id'] and truth['line_id']==original['line_id'] and truth['book_or_ms']==book
            assert int(truth['site_index_in_record'])==original['site_index_in_record']
            text=truth['expanded_span'];reason='empty' if not text.split() else 'multiword' if len(text.split())!=1 else 'out_of_candidate_inventory' if text not in vocab else 'in_inventory'
            row=dict(original,truth=text,truth_inventory_status=reason)
            evaluations.append(row);bytype[original['written_node']].append(row)
        # Check excluded/unsupported joins too, without changing eligibility.
        for original in fold['excluded_and_unsupported_sites']:
            truth=gold[original['site_id']]
            assert truth['record_id']==original['record_id'] and truth['line_id']==original['line_id'] and truth['book_or_ms']==book
            assert int(truth['site_index_in_record'])==original['site_index_in_record']
        fold_data[idx]=(fold,bytype)
        for node,rows in sorted(bytype.items()):
            hist=Counter(r['truth'] for r in rows);supported={t:n for t,n in hist.items() if len(t.split())==1 and t in vocab}
            oracle=Fraction(sum(sorted(supported.values(),reverse=True)[:5]),len(rows))
            type_rows.append({'fold':idx,'book':book,'written_node':node,'written_form':fold['written_nodes'][node],'sites':len(rows),
                'outside_fit_sites':sum(not r['inside_fit_record'] for r in rows),'truth_mixture':[{'truth':t,'count':n,'candidate_index':reference.index(t) if t in vocab and len(t.split())==1 else None} for t,n in sorted(hist.items())],
                'truth_inventory_counts':dict(Counter(r['truth_inventory_status'] for r in rows)),'oracle_top5':exact(oracle),'observed_models':{}})
    observed_type={(r['fold'],r['written_node']):r for r in type_rows}
    prediction_lookup={(r['fold'],r['world']):r for r in lock['predictions']}
    for world in range(20):
        worldrows=[]
        for idx in range(4):
            fold,bytype=fold_data[idx];reference=fold['reference_nodes'];book=fold['book']
            fitted=unpack(EXP/prediction_lookup[(idx,world)]['path'])['models']
            if world:
                reuse=prediction_lookup[(idx,world)]['F_reuse'];assert sha(EXP/reuse['path'])==reuse['sha256'];fitted['F']=unpack(EXP/reuse['path'])['models']['F']
            for model in MODELS:
                ranking=fitted[model]['ranking'];assert len(ranking)==len(fold['written_nodes'])
                scores=[];outside=[];types=[]
                for node,rows in sorted(bytype.items()):
                    rank=ranking[node];assert sorted(rank)==list(range(len(reference)))
                    m=metric_for_sites(rows,rank,reference);scores.append((m,len(rows)))
                    extra=[r for r in rows if not r['inside_fit_record']]
                    om=metric_for_sites(extra,rank,reference) if extra else None
                    if om is not None:outside.append((om,len(extra)))
                    types.append({'written_node':node,'sites':len(rows),'metrics':{k:exact(v) for k,v in m.items()},'outside_fit_metrics':{k:exact(v) for k,v in om.items()} if om else None})
                    if world==0:observed_type[(idx,node)]['observed_models'][model]={'metrics':{k:exact(v) for k,v in m.items()},'top5':[reference[j] for j in rank[:5]],'selected_seed':fitted[model]['selected_seed']}
                macro={k:mean([m[k] for m,n in scores]) for k in ['top1','top5','MRR']}
                weighted={k:sum((m[k]*n for m,n in scores),Fraction(0))/sum(n for m,n in scores) for k in macro}
                out={'macro':{k:exact(mean([m[k] for m,n in outside])) for k in macro},'sites':sum(n for m,n in outside),'types':len(outside)} if outside else None
                row={'world':world,'fold':idx,'book':book,'model':model,'types':len(scores),'sites':sum(n for m,n in scores),'macro':{k:exact(v) for k,v in macro.items()},'weighted':{k:exact(v) for k,v in weighted.items()},'outside_fit':out,'type_scores':types}
                worldrows.append(row);fractions[(world,idx,model)]=macro['top5']
        all_scores.extend(worldrows)
    aggregates={world:{m:mean([fractions[(world,i,m)] for i in range(4)]) for m in MODELS} for world in range(20)}
    gains={w:a['G']-max(a['F'],a['B']) for w,a in aggregates.items()};observed=aggregates[0]
    rank=Fraction(1+sum(gains[w]>=gains[0] for w in range(1,20)),20)
    better=sum(fractions[(0,i,'G')]>fractions[(0,i,'F')] and fractions[(0,i,'G')]>fractions[(0,i,'B')] for i in range(4))
    gates={'G_top5_at_least_half':observed['G']>=Fraction(1,2),'gain_at_least_tenth':gains[0]>=Fraction(1,10),'books_above_both_at_least3':better>=3,'null_rank_at_most_twentieth':rank<=Fraction(1,20)}
    collisions=[]
    for idx in range(4):
        bytruth=defaultdict(set)
        for r in type_rows:
            if r['fold']==idx:
                for t in r['truth_mixture']:bytruth[t['truth']].add(r['written_node'])
        collisions.extend({'fold':idx,'truth':t,'written_nodes':sorted(nodes)} for t,nodes in sorted(bytruth.items()) if len(nodes)>1)
    packed(EXP/'artifacts/EVALUATION_SITES.json.gz',{'gold_release':'AFTER_ALL_PREDICTIONS_LOCKED','sites':evaluations})
    packed(EXP/'artifacts/TYPE_RESULTS.json.gz',{'types':type_rows,'truth_collisions':collisions})
    packed(EXP/'artifacts/ALL_SCORES.json.gz',{'scores':all_scores})
    result={'experiment':'GDT1164','status':'SOURCE_CONTEXT_RANKING_SUPPORTED' if all(gates.values()) else 'NO_SUPPORTED_SOURCE_CONTEXT_RANKING',
        'prediction_lock_sha256':sha(EXP/'artifacts/PREDICTION_LOCK.json'),'gold_sha256':sha(goldpath),'scorer_sha256':sha(Path(__file__)),
        'eligible_types':len(type_rows),'eligible_sites':len(evaluations),'observed_macro_top5':{k:exact(v) for k,v in observed.items()},
        'observed_gain':exact(gains[0]),'books_G_above_both':better,'null_rank':exact(rank),'gates':gates,
        'worlds':[{'world':w,'aggregate_macro_top5':{m:exact(v) for m,v in a.items()},'gain':exact(gains[w])} for w,a in aggregates.items()],
        'per_book_observed':[{k:v for k,v in r.items() if k!='type_scores'} for r in all_scores if r['world']==0],
        'oracle_macro_top5':exact(mean([mean([Fraction(r['oracle_top5']['numerator'],r['oracle_top5']['denominator']) for r in type_rows if r['fold']==i]) for i in range(4)])),
        'truth_inventory_counts':dict(Counter(r['truth_inventory_status'] for r in evaluations)),
        'coverage_receipt':'CAPACITY.json and BUILDER_AUDIT.json.gz retain every unsupported/excluded site',
        'confirmed_words':0,'new_target_access':0,'claim_ceiling':spec['claim_ceiling'],'control_interpretation':'Conditional pipeline rank, not population or project-wide significance'}
    (EXP/'artifacts/RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    def esc(x):return str(x).replace('&','&amp;').replace('|','&#124;').replace('\n','<br>')
    lines=['# GDT1164 complete selected marked-type results','','All eligible selected marked types; exact truth mixtures and all-world scores are retained in compressed artifacts. These source labels do not assign Voynich meanings.','', '|Book|Written type|Sites|Exact expansion mixture|F top5|B top5|G top5|Oracle top5|G five ranked candidates|','|---|---|---:|---|---:|---:|---:|---:|---|']
    for r in type_rows:
        mix='; '.join(repr(t['truth'])+':'+str(t['count']) for t in r['truth_mixture'])
        vals=[r['book'],r['written_form'],r['sites'],mix]+[f"{r['observed_models'][m]['metrics']['top5']['value']:.6f}" for m in MODELS]+[f"{r['oracle_top5']['value']:.6f}",repr(r['observed_models']['G']['top5'])]
        lines.append('|'+'|'.join(esc(v) for v in vals)+'|')
    (EXP/'CANDIDATE_TABLE.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:result[k] for k in ['status','eligible_types','eligible_sites','observed_macro_top5','observed_gain','null_rank','gates']}))
