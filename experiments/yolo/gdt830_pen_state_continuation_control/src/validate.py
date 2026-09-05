#!/usr/bin/env python3
"""Independent descriptor replay. Does not import the runner or pixel extractor.

Checks source hashes, row geometry, descriptor inventory, fitted statistics,
candidate selection and scores. Does not repeat manuscript pixel measurement.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

EXP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EXP.parents if (p / '.git').exists())
FIELDS = ['patch_id','page','row_id','source_ordinal','column','valid','reason','ink_json','nuisance_json','core_samples','patch_width','patch_height']
SCORES = ['query_id','page','candidate_id','is_true','is_same_row','primary_score','nuisance_score','constant_score','reverse_score']
NAMES = ['primary','nuisance','constant','reverse']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_tsv(path, fields=None):
    with Path(path).open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        if fields is not None:
            require(reader.fieldnames == fields, f'Unexpected fields: {Path(path).name}')
        return list(reader)


def geometry(spec, sources, raw_rows):
    pages = spec['pages']
    require(len(pages) == len(set(pages)) == 4, 'Expected four unique control pages')
    require(set(pages).isdisjoint(spec['sealed_data'] + spec['disputed_pages_not_scored']), 'Forbidden control page')
    sm = {s['page']: s for s in sources}
    require(len(sm) == len(sources) == 4 and set(sm) == set(pages), 'Source page mismatch')
    rows, grouped = {}, defaultdict(list)
    for raw in raw_rows:
        r = {k: v if k in ['page','row_id'] else int(v) for k,v in raw.items()}
        p = r['page']
        require(p in sm and not p.startswith('f84'), 'Unadmitted geometry page')
        require(r['row_id'] not in rows, 'Duplicate row')
        require(r['row_id'] == f"{p}:R{r['source_ordinal']:03d}", 'Wrong row identifier')
        require(0 <= r['x0'] < r['x1'] <= sm[p]['width'], 'Horizontal bounds')
        require(0 <= r['y0'] < r['y1'] <= sm[p]['height'], 'Vertical bounds')
        require(r['y0'] <= r['row_core_y'] < r['y1'], 'Row core bounds')
        rows[r['row_id']] = r
        grouped[p].append(r)
    require(set(grouped) == set(pages), 'Geometry page mismatch')
    for p, rr in grouped.items():
        rr.sort(key=lambda r:r['source_ordinal'])
        require([r['source_ordinal'] for r in rr] == list(range(1,len(rr)+1)), 'Nonconsecutive source rows')
        require(all(a['y1'] <= b['y0'] for a,b in zip(rr,rr[1:])), 'Overlapping registered rows')
    return rows


def features_from_file(path,spec,rows):
    features = {}
    for f in read_tsv(path,FIELDS):
        require(f['page'] in spec['pages'] and not f['page'].startswith('f84'), 'Unadmitted feature page')
        require(f['row_id'] in rows,'Unknown feature row')
        r = rows[f['row_id']]
        for k in ['source_ordinal','column','valid','core_samples','patch_width','patch_height']:
            f[k] = int(f[k])
        c,n = f['column'],spec['windows_per_row']
        require(f['page']==r['page'] and f['source_ordinal']==r['source_ordinal'],'Metadata mismatch')
        require(0 <= c < n,'Column bounds')
        require(f['patch_id']==f"{f['row_id']}:W{c:02d}" and f['patch_id'] not in features,'Patch identity mismatch')
        w = r['x1']-r['x0']
        require(f['patch_width']==((c+1)*w)//n-(c*w)//n and f['patch_height']==r['y1']-r['y0'],'Patch dimensions')
        require(0<=f['core_samples']<=f['patch_width']*f['patch_height'],'Core count bounds')
        require(f['valid'] in [0,1],'Invalid validity flag')
        require(f['reason'] == 'PASS' if f['valid'] else f['reason'] in ['INSUFFICIENT_VERTICAL_CORE','INSUFFICIENT_PAPER'],'Unexpected quality reason')
        for field,sz in [('ink',len(spec['ink_features'])),('nuisance',len(spec['nuisance_features']))]:
            vv = json.loads(f[field+'_json'])
            require(isinstance(vv,list) and len(vv)==(sz if f['valid'] else 0),'Descriptor size')
            require(json.dumps(vv,separators=(',',':'),allow_nan=False)==f[field+'_json'],'Noncanonical JSON')
            require(all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and abs(v-round(v,12))<1e-13 for v in vv),'Nonfinite/unrounded descriptor')
            f[field]=np.asarray(vv,float)
        if f['valid']:
            nu = dict(zip(spec['nuisance_features'],f['nuisance']))
            require(f['core_samples']>=spec['minimum_core_pixels'],'Insufficient valid core')
            require(0<=nu['ink_fraction']<=1-spec['minimum_paper_fraction']+1e-12,'Insufficient valid paper')
            require(abs(nu['log_core_count']-math.log1p(f['core_samples']))<1e-10,'Core descriptor mismatch')
            require(spec['horizontal_run_width'][0]<=nu['mean_run_width']<=spec['horizontal_run_width'][1],'Run width bounds')
            require(nu['sd_run_width']>=0 and 0<=nu['vertical_run_fraction']<=1,'Invalid width/persistence descriptor')
            require(0<=nu['x_normalized']<=1 and 0<=nu['y_normalized']<=1,'Position bounds')
            for channel in 'RGB':
                require(0<=nu['paper_'+channel]<=1 and 0<=nu['paper_sd_'+channel]<=1,'Background bounds')
                require(-1<=nu['paper_dx_'+channel]<=1 and -1<=nu['paper_dy_'+channel]<=1,'Background gradient bounds')
            require(np.all(f['ink']>=-math.log(256)) and np.all(f['ink']<=math.log(256)),'Ink bounds')
        features[f['patch_id']]=f
    require(len(features)==len(rows)*spec['windows_per_row'],'Incomplete feature inventory')
    return features


def fit(features,pages):
    cal=sorted([f for f in features.values() if f['valid'] and f['source_ordinal']%2],key=lambda f:f['patch_id'])
    nu=np.stack([f['nuisance'] for f in cal]); ink=np.stack([f['ink'] for f in cal])
    mean,sd=nu.mean(0),np.maximum(nu.std(0),1e-6)
    x=np.column_stack([(nu-mean)/sd,[[float(f['page']==p) for p in pages] for f in cal]])
    penalty=np.diag([1.]*nu.shape[1]+[0.]*len(pages))
    beta=np.linalg.solve(x.T@x+penalty,x.T@ink)
    rsd=np.maximum((ink-x@beta).std(0),1e-6)
    transformed={}
    for key,f in features.items():
        if not f['valid']: continue
        normalized=(f['nuisance']-mean)/sd
        xx=np.r_[normalized,[float(f['page']==p) for p in pages]]
        transformed[key]=(normalized,(f['ink']-xx@beta)/rsd)
    return {'nuisance_mean':mean,'nuisance_sd':sd,'coefficients':beta,'ink_residual_sd':rsd,
            'calibration_patch_ids':[f['patch_id'] for f in cal]},transformed


def top1(values):
    values=np.asarray(values,float)
    tied=values>=values.max()-1e-12
    return float(tied[0])/int(tied.sum())


def vector_scores(r2,r3,ink,nu3,nu):
    preds={'primary':r3+3*(r3-r2),'constant':r3,'reverse':r2+3*(r2-r3)}
    values={k:np.round(-np.mean((ink-v)**2,axis=1),12) for k,v in preds.items()}
    values['nuisance']=np.round(-np.mean((nu-nu3)**2,axis=1),12)
    return values


def metric_summary(queries):
    m={k+'_top1':float(np.mean([q[k] for q in queries])) for k in NAMES}
    m['same_row_top1']=float(np.mean([q['same_row'] for q in queries]))
    m.update({'gain_over_'+k:m['primary_top1']-m[k+'_top1'] for k in ['nuisance','constant','reverse']})
    return m


def reconstruct(spec,features):
    pages=spec['pages']; cap=spec['capacity_gate']
    cal=[f for f in features.values() if f['valid'] and f['source_ordinal']%2]
    caln={p:len({f['row_id'] for f in cal if f['page']==p}) for p in pages}
    result={'capacity':{'calibration_rows':sum(caln.values()),'calibration_rows_per_page':caln,
                        'queries':0,'queries_per_page':{p:0 for p in pages},'passed':False},
            'status':'CONTROL_CAPACITY_STOP','metrics':{},'by_page':{},'gates':{}}
    if sum(caln.values())<cap['minimum_calibration_rows'] or not all(caln[p]>=1 for p in pages):
        return result,[],None
    model,tf=fit(features,pages)
    byrow=defaultdict(dict)
    for f in features.values(): byrow[f['row_id']][f['column']]=f
    score_rows=[]; queries=[]
    need=spec['context_columns']+[spec['true_column']]+spec['same_row_decoy_columns']
    for rid in sorted(byrow):
        row=byrow[rid]; first=next(iter(row.values()))
        if first['source_ordinal']%2 or not all(c in row and row[c]['valid'] for c in need): continue
        target=row[spec['true_column']]
        others=[other[spec['true_column']] for oid,other in byrow.items() if oid!=rid
                and spec['true_column'] in other and other[spec['true_column']]['valid']
                and other[spec['true_column']]['source_ordinal']%2==0
                and other[spec['true_column']]['page']==first['page']]
        if len(others)<spec['other_row_decoys']: continue
        others.sort(key=lambda f:(float(np.mean((tf[f['patch_id']][0]-tf[target['patch_id']][0])**2)),f['patch_id']))
        cand=[target]+[row[c] for c in spec['same_row_decoy_columns']]+others[:spec['other_row_decoys']]
        nu2,r2=tf[row[spec['context_columns'][0]]['patch_id']]; nu3,r3=tf[row[spec['context_columns'][1]]['patch_id']]
        vals=vector_scores(r2,r3,np.stack([tf[f['patch_id']][1] for f in cand]),nu3,np.stack([tf[f['patch_id']][0] for f in cand]))
        queries.append({'page':first['page'],**{k:top1(vals[k]) for k in NAMES},'same_row':top1(vals['primary'][:3])})
        for i,f in enumerate(cand):
            score_rows.append({'query_id':rid,'page':first['page'],'candidate_id':f['patch_id'],'is_true':int(i==0),'is_same_row':int(i<3),**{k+'_score':float(vals[k][i]) for k in NAMES}})
    counts=Counter(q['page'] for q in queries)
    result['capacity'].update(queries=len(queries),queries_per_page={p:counts[p] for p in pages})
    passed=len(queries)>=cap['minimum_queries'] and len(counts)>=cap['minimum_pages'] and all(counts[p]>=cap['minimum_queries_per_page'] for p in pages)
    result['capacity']['passed']=passed
    if not passed: return result,[],model
    m=metric_summary(queries); per={p:metric_summary([q for q in queries if q['page']==p]) for p in pages}
    thresholds=spec['success_gates']
    gates={'top1':m['primary_top1']>=thresholds['top1_minimum'],
           'nuisance_gain':m['gain_over_nuisance']>=thresholds['top1_gain_over_nuisance_minimum'],
           'constant_gain':m['gain_over_constant']>=thresholds['top1_gain_over_constant_minimum'],
           'reverse_gain':m['gain_over_reverse']>=thresholds['top1_gain_over_reverse_minimum'],
           'same_row':m['same_row_top1']>=thresholds['same_row_threeway_top1_minimum'],
           'all_pages':all(per[p]['gain_over_nuisance']>0 for p in pages)}
    result.update(metrics=m,by_page=per,gates=gates,status='CONTROL_LOCAL_CONTINUATION_ONLY' if all(gates.values()) else 'CONTROL_NOT_SUPPORTED')
    return result,score_rows,model


def controls():
    checks={}
    r2=np.array([1.,2.,3.]);r3=2*r2
    vals=vector_scores(r2,r3,np.stack([5*r2,r3,-2*r2,9*r2,10*r2]),np.zeros(2),np.ones((5,2)))
    checks['planted_trajectory']=top1(vals['primary'])==1 and top1(vals['constant'])==0 and top1(vals['reverse'])==0
    checks['fractional_ties']=top1(np.zeros(5))==.2 and top1(np.zeros(3))==1/3
    checks['tie_tolerance']=top1([0,-5e-13,-2e-12])==.5
    vals=vector_scores(-10*np.ones(3),np.ones(3),np.array([[1]*3,[34]*3,[20]*3,[22]*3,[30]*3],float),np.zeros(2),np.array([[1,1],[0,0],[2,2],[3,3],[4,4]],float))
    checks['constant_beats_spurious_trajectory']=top1(vals['constant'])==1 and top1(vals['primary'])==0 and top1(vals['nuisance'])==0
    pp=['a','b','c','d']; ff={}
    for pi,p in enumerate(pp):
        for ordinal in range(1,13):
            for col in range(12):
                key=f'{p}:R{ordinal:03d}:W{col:02d}'
                ff[key]={'patch_id':key,'page':p,'row_id':f'{p}:R{ordinal:03d}','source_ordinal':ordinal,'column':col,'valid':1,
                         'nuisance':np.array([float(col),float(ordinal)]),'ink':np.array([col*.1+pi+math.sin(col),ordinal*.3+math.cos(col),col*.02+math.sin(ordinal)])}
    first,_=fit(ff,pp)
    test_spec={'pages':pp,'capacity_gate':{'minimum_calibration_rows':24,'minimum_queries':24,'minimum_pages':4,'minimum_queries_per_page':4},
               'context_columns':[2,3],'true_column':6,'same_row_decoy_columns':[8,10],'other_row_decoys':2,
               'success_gates':{'top1_minimum':.4,'top1_gain_over_nuisance_minimum':.1,'top1_gain_over_constant_minimum':.1,
                                'top1_gain_over_reverse_minimum':.05,'same_row_threeway_top1_minimum':.5}}
    reconstruction,ss,_=reconstruct(test_spec,ff)
    grouped=defaultdict(list)
    for s in ss: grouped[s['query_id']].append(s)
    checks['complete_candidate_control_inventory']=reconstruction['capacity']['passed'] and len(grouped)==24 and len(ss)==120
    checks['decoys_exclude_calibration_and_own_row']=all(
        len(rr)==5 and sum(r['is_true'] for r in rr)==1 and sum(r['is_same_row'] for r in rr)==3
        and all(ff[r['candidate_id']]['row_id']!=query and ff[r['candidate_id']]['source_ordinal']%2==0
                for r in rr if not r['is_same_row'])
        for query,rr in grouped.items())
    for f in ff.values():
        if f['source_ordinal']%2==0:
            f['ink']=f['ink']*1000+37;f['nuisance']=f['nuisance']*300+41
    changed,_=fit(ff,pp)
    checks['held_rows_excluded_from_all_fit_statistics']=all(np.array_equal(first[k],changed[k]) for k in ['nuisance_mean','nuisance_sd','coefficients','ink_residual_sd'])
    require(all(checks.values()),'Independent synthetic scorer control failed')
    return checks


def compare(actual,expected,trail='result'):
    if isinstance(expected,dict):
        require(isinstance(actual,dict),'Expected object at '+trail)
        for k,v in expected.items():
            require(k in actual,'Missing field '+trail+'.'+k)
            compare(actual[k],v,trail+'.'+k)
    elif isinstance(expected,np.ndarray):
        require(np.allclose(np.asarray(actual,float),expected,atol=1e-9,rtol=1e-8),'Model mismatch '+trail)
    elif isinstance(expected,float):
        require(isinstance(actual,(float,int)) and math.isclose(actual,expected,abs_tol=1e-10,rel_tol=1e-9),'Numerical mismatch '+trail)
    else: require(actual==expected,f'Mismatch {trail}: {actual!r} != {expected!r}')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--input-dir',type=Path,default=EXP/'artifacts')
    parser.add_argument('--image-dir','--cache-dir',dest='image_dir',type=Path,default=Path(os.environ.get('GDT830_IMAGE_CACHE',str(ROOT/'.cache/gdt830_native'))))
    args=parser.parse_args(); checks=controls()
    if args.self_test:
        print(json.dumps({'status':'SYNTHETIC_VALIDATOR_CONTROLS_PASS','checks':checks},sort_keys=True));return 0
    spec=json.loads((EXP/'src/SPEC.json').read_text());sources=json.loads((EXP/'src/SOURCES.json').read_text())
    rows=geometry(spec,sources,read_tsv(EXP/'src/ROWS.tsv'))
    lock=json.loads((EXP/'src/PREREG_LOCK.json').read_text())
    lockmap=lock.get('sha256',lock.get('files',lock))
    expected_lock_files={str((EXP/name).relative_to(ROOT)) for name in ['PREREGISTRATION.md','src/SPEC.json','src/ROWS.tsv','src/SOURCES.json']}
    require(set(lockmap)==expected_lock_files,'Incomplete or unexpected preregistration lock map')
    for rel,expected in lockmap.items():
        require(isinstance(rel,str) and not Path(rel).is_absolute(),'Nonrelative prereg lock')
        require(digest(ROOT/rel)==expected,'Preregistration hash mismatch: '+rel)
    from PIL import Image
    for s in sources:
        path=args.image_dir/s['filename']
        require(path.stat().st_size==s['bytes'] and digest(path)==s['sha256'],'Source image hash/size mismatch')
        with Image.open(path) as im: require(im.size==(s['width'],s['height']),'Image dimension mismatch')
    fp=args.input_dir/'FEATURES.tsv';before=digest(fp)
    ff=features_from_file(fp,spec,rows)
    expected,score_rows,model=reconstruct(spec,ff)
    aa=read_tsv(args.input_dir/'QUERY_SCORES.tsv',SCORES)
    amap={(r['query_id'],r['candidate_id']):r for r in aa};emap={(r['query_id'],r['candidate_id']):r for r in score_rows}
    require(len(amap)==len(aa) and set(amap)==set(emap),'Query/candidate inventory mismatch')
    for key,er in emap.items():
        ar=amap[key]
        for field in SCORES:
            value=float(ar[field]) if field.endswith('_score') else int(ar[field]) if field in ['is_true','is_same_row'] else ar[field]
            compare(value,er[field],f'scores.{key}.{field}')
    if model is not None: compare(json.loads((args.input_dir/'MODEL.json').read_text()),model,'model')
    expected.update(experiment_id='GDT830',source_images=len(sources),rows=len(rows),feature_windows=len(ff),valid_windows=sum(f['valid'] for f in ff.values()),
                    quality_reasons=dict(Counter(f['reason'] for f in ff.values())),prereg_hashes=lockmap,features_sha256=before,
                    pixel_measurement=True,artificial_cut_only=True,chronology_established=False,reading_order_established=False,disputed_blocks_scored=False,
                    semantic_claim=False,new_admissions=0,sealed_data=spec['sealed_data'],independent_trials=False)
    compare(json.loads((args.input_dir/'RESULT.json').read_text()),expected)
    require(digest(fp)==before,'Features changed during replay')
    validation={'status':'INDEPENDENT_DESCRIPTOR_REPLAY_PASS','experiment_id':'GDT830','independent_pixel_measurement':False,
                'feature_sha256':before,'source_geometry_sha256':digest(EXP/'src/ROWS.tsv'),'source_manifest_sha256':digest(EXP/'src/SOURCES.json'),
                'source_image_hash_size_dimensions_verified':len(sources),'synthetic_controls':checks,'features':len(ff),
                'candidate_scores_reconstructed':len(score_rows),'reconstructed_status':expected['status'],'reconstructed_capacity':expected['capacity'],
                'reconstructed_metrics':expected['metrics'],'reconstructed_gates':expected['gates'],
                'scope':'Independent descriptor/model/scoring replay; no independent pixel feature extraction, chronology or reading-order validation.'}
    (args.input_dir/'VALIDATION.json').write_text(json.dumps(validation,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':validation['status'],'control_status':expected['status'],'features':len(ff),'queries':expected['capacity']['queries']},sort_keys=True))
    return 0


if __name__=='__main__':raise SystemExit(main())
