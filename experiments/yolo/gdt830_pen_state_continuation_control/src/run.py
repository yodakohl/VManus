#!/usr/bin/env python3
"""GDT830: one fixed artificial-cut control, never a split-block order solver."""
import argparse
import csv
import hashlib
import io
import json
import os
from collections import Counter
from pathlib import Path

import numpy as np
from measure import COLUMNS, canon, check, extract, load_sources

EXP=Path(__file__).resolve().parent.parent
ROOT=EXP.parents[2]
SCORE_COLUMNS=['query_id','page','candidate_id','is_true','is_same_row','primary_score','nuisance_score','constant_score','reverse_score']


def read_tsv(path):
    with path.open() as f:return list(csv.DictReader(f,delimiter='\t'))


def table(rows,columns):
    out=io.StringIO(); w=csv.DictWriter(out,fieldnames=columns,delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(rows);return out.getvalue()


def topcredit(rows,key):
    best=max(r[key] for r in rows)
    winners=[r for r in rows if abs(r[key]-best)<=1e-12]
    return sum(r['is_true'] for r in winners)/len(winners)


def summarize(queries):
    if not queries:return {}
    values={name:float(np.mean([topcredit(q,col) for q in queries])) for name,col in [('primary_top1','primary_score'),('nuisance_top1','nuisance_score'),('constant_top1','constant_score'),('reverse_top1','reverse_score')]}
    values['same_row_top1']=float(np.mean([topcredit([r for r in q if r['is_same_row']],'primary_score') for q in queries]))
    for key in ['nuisance','constant','reverse']:
        values['gain_over_'+key]=values['primary_top1']-values[key+'_top1']
    return {k:float(np.round(v,12)) for k,v in values.items()}


def evaluate(features,spec):
    valid=[r for r in features if int(r['valid'])]
    cal=[r for r in valid if int(r['source_ordinal'])%2==1]
    cal_rows={r['row_id']:r['page'] for r in cal}
    percal={p:sum(page==p for page in cal_rows.values()) for p in spec['pages']}
    cap=dict(calibration_rows=len(cal_rows),calibration_rows_per_page=percal,queries=0,queries_per_page={p:0 for p in spec['pages']},passed=False)
    empty=dict(status='CONTROL_CAPACITY_STOP',capacity=cap,metrics={},by_page={},gates={})
    if len(cal_rows)<spec['capacity_gate']['minimum_calibration_rows'] or min(percal.values())<1:
        return [],empty,{}
    nu=np.array([json.loads(r['nuisance_json']) for r in cal]); ink=np.array([json.loads(r['ink_json']) for r in cal])
    mean=nu.mean(axis=0); sd=np.maximum(nu.std(axis=0),1e-6)
    def design(rows):
        z=(np.array([json.loads(r['nuisance_json']) for r in rows])-mean)/sd
        page=np.array([[int(r['page']==p) for p in spec['pages']] for r in rows])
        return z,np.c_[z,page]
    z,x=design(cal); penalty=np.diag([1.]*nu.shape[1]+[0.]*len(spec['pages']))
    coef=np.linalg.solve(x.T@x+penalty,x.T@ink)
    residual_sd=np.maximum((ink-x@coef).std(axis=0),1e-6)
    zv,xv=design(valid);rv=(np.array([json.loads(r['ink_json']) for r in valid])-xv@coef)/residual_sd
    lookup={r['patch_id']:(r,zv[i],rv[i]) for i,r in enumerate(valid)}
    held=sorted({r['row_id'] for r in valid if int(r['source_ordinal'])%2==0})
    querylists=[]
    for row_id in held:
        names={col:row_id+f':W{col:02d}' for col in [2,3,6,8,10]}
        if not all(name in lookup for name in names.values()):continue
        target,tnu,_=lookup[names[6]]
        others=[r for r in valid if r['row_id']!=row_id and r['page']==target['page'] and int(r['source_ordinal'])%2==0 and int(r['column'])==6]
        if len(others)<2:continue
        others.sort(key=lambda r:(float(np.mean((lookup[r['patch_id']][1]-tnu)**2)),r['patch_id']))
        candidate_ids=[names[6],names[8],names[10],others[0]['patch_id'],others[1]['patch_id']]
        left2,nu2,r2=lookup[names[2]];left3,nu3,r3=lookup[names[3]]
        pred=r3+3*(r3-r2);reverse=r2+3*(r2-r3)
        query=[]
        for name in sorted(candidate_ids):
            candidate,nuc,rc=lookup[name]
            scores=[-float(np.mean((rc-pred)**2)),-float(np.mean((nuc-nu3)**2)),-float(np.mean((rc-r3)**2)),-float(np.mean((rc-reverse)**2))]
            query.append(dict(query_id=row_id,page=target['page'],candidate_id=name,is_true=int(name==names[6]),is_same_row=int(candidate['row_id']==row_id),**dict(zip(['primary_score','nuisance_score','constant_score','reverse_score'],[float(np.round(v,12)) for v in scores]))))
        querylists.append(query)
    cap['queries']=len(querylists)
    cap['queries_per_page']={p:sum(q[0]['page']==p for q in querylists) for p in spec['pages']}
    cap['passed']=cap['queries']>=spec['capacity_gate']['minimum_queries'] and min(cap['queries_per_page'].values())>=spec['capacity_gate']['minimum_queries_per_page']
    model=dict(nuisance_mean=mean.tolist(),nuisance_sd=sd.tolist(),coefficients=coef.tolist(),ink_residual_sd=residual_sd.tolist(),calibration_patch_ids=[r['patch_id'] for r in cal])
    # Capacity precedes reporting any retrieval performance.
    if not cap['passed']:
        return [],empty,model
    metrics=summarize(querylists)
    bypage={p:summarize([q for q in querylists if q[0]['page']==p]) for p in spec['pages']}
    gate=spec['success_gates']
    gates=dict(top1=metrics['primary_top1']>=gate['top1_minimum'],nuisance_gain=metrics['gain_over_nuisance']>=gate['top1_gain_over_nuisance_minimum'],constant_gain=metrics['gain_over_constant']>=gate['top1_gain_over_constant_minimum'],reverse_gain=metrics['gain_over_reverse']>=gate['top1_gain_over_reverse_minimum'],same_row=metrics['same_row_top1']>=gate['same_row_threeway_top1_minimum'],all_pages=all(m['gain_over_nuisance']>0 for m in bypage.values()))
    result=dict(status='CONTROL_LOCAL_CONTINUATION_ONLY' if all(gates.values()) else 'CONTROL_NOT_SUPPORTED',capacity=cap,metrics=metrics,by_page=bypage,gates=gates)
    return [r for q in querylists for r in q],result,model


def output(path,content,checking):
    if checking:check(path.read_text()==content,'Replay differs: '+path.name)
    else:path.write_text(content)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--fetch',action='store_true');p.add_argument('--cache-dir',type=Path,default=Path(os.environ.get('GDT830_IMAGE_CACHE',str(ROOT/'.cache/gdt830_native'))));args=p.parse_args()
    spec=json.loads((EXP/'src/SPEC.json').read_text());sources=json.loads((EXP/'src/SOURCES.json').read_text());rows=read_tsv(EXP/'src/ROWS.tsv')
    locks=json.loads((EXP/'src/PREREG_LOCK.json').read_text())
    for path,expected in locks.items():check(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,'Preregistration drift')
    check({r['page'] for r in rows}==set(spec['pages'])=={r['page'] for r in sources},'Scope')
    images=load_sources(sources,args.cache_dir,args.fetch)
    features=extract(images,rows,spec)
    featuretext=table(features,COLUMNS)
    output(EXP/'artifacts/FEATURES.tsv',featuretext,args.check)
    scores,result,model=evaluate(features,spec)
    result.update(experiment_id='GDT830',source_images=len(sources),rows=len(rows),feature_windows=len(features),valid_windows=sum(int(r['valid']) for r in features),quality_reasons=dict(sorted(Counter(r['reason'] for r in features).items())),prereg_hashes=locks,features_sha256=hashlib.sha256(featuretext.encode()).hexdigest(),pixel_measurement=True,artificial_cut_only=True,chronology_established=False,reading_order_established=False,disputed_blocks_scored=False,semantic_claim=False,new_admissions=0,sealed_data=spec['sealed_data'],independent_trials=False)
    output(EXP/'artifacts/QUERY_SCORES.tsv',table(scores,SCORE_COLUMNS),args.check)
    output(EXP/'artifacts/MODEL.json',json.dumps(model,sort_keys=True,indent=2)+'\n',args.check)
    output(EXP/'artifacts/RESULT.json',json.dumps(result,sort_keys=True,indent=2)+'\n',args.check)
    print(canon({k:result[k] for k in ['status','feature_windows','valid_windows','quality_reasons','capacity','metrics','gates']}))


if __name__=='__main__':main()
