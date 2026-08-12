#!/usr/bin/env python3
"""Efficient exact real-panel scorer for a passed RTA001 calibration."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; R=HERE/'results'
sys.path.insert(0,str(HERE))
from build_rta001_edge_programs import exact_alignment, canonical_dsl, atom_counts
from rta001_model import (ABSTRACT_ORDER,K_GRID,SCALE,EdgeMeta,FeatureData,baseline_training_and_test,
                          build_feature_data,categorical_test_costs,fit_model,score_model,stable_seed,
                          training_projection)

CAL=R/'rta001_synthetic_calibration.json'; PROGRAM_META=R/'rta001_edge_programs.json'
OUT=R/'rta001_result.json'; REPORT=R/'rta001_result_report.md'; HELD=R/'rta001_heldout_panel_results.tsv'
CODEBOOK=R/'rta001_operator_codebook.json'; ATLAS=R/'rta001_operator_atlas.md'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write_json(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def select_fold(folio):
    full={rep:build_feature_data(R,rep) for rep in ABSTRACT_ORDER}; candidates=[]; prepared={}
    for rep in ABSTRACT_ORDER:
        data=full[rep]; tr=[i for i,e in enumerate(data.edges) if e.physical_folio!=folio]; te=[i for i,e in enumerate(data.edges) if e.physical_folio==folio]
        train,test=training_projection(data,tr,te); prepared[rep]=(train,test)
        for k in K_GRID:
            if k<=len(train.edges):
                model=fit_model(train,k,f'REAL|{folio}|{rep}|K{k}',16,None)
                candidates.append((model.total_bits_scaled,ABSTRACT_ORDER.index(rep),k,model,train,test))
    winner=min(candidates,key=lambda x:(x[0],x[1],x[2],x[3].medoid_indices))
    best_by_rep={}
    for rep in ABSTRACT_ORDER:
        best_by_rep[rep]=min((x for x in candidates if x[3].representation==rep),key=lambda x:(x[0],x[2],x[3].medoid_indices))
    return folio,winner,best_by_rep

def sequence_maps(rep):
    seq={}
    for x in rows(R/f'rta001_edge_programs_{rep}.tsv'):
        if x['status']!='EXACT_PROGRAM':continue
        seq[(x['edition'],x['source_locus'])]=json.loads(x['source_sequence_json'])
        seq[(x['edition'],x['target_locus'])]=json.loads(x['target_sequence_json'])
    return seq

def pair_vector(rep,source_locus,target_locus,feature_names,sequences):
    index={name:i for i,name in enumerate(feature_names)}; vectors=[]
    for edition in ('ZL3b','IT2a','RF1b'):
        source=sequences.get((edition,source_locus));target=sequences.get((edition,target_locus))
        if source is None or target is None:continue
        _,_,primitive=exact_alignment(source,target);program=canonical_dsl(source,target,primitive,rep)
        vector=np.zeros(len(feature_names),dtype=np.int32)
        for atom,count in atom_counts(program).items():
            name='ATOM:'+atom
            if name in index:vector[index[name]]+=count
        unseen=index['DELTA:UNSEEN_LITERAL']
        for token,sign in [(t,-1) for t in source]+[(t,1) for t in target]:vector[index.get('DELTA:'+token,unseen)]+=sign
        vector[index['SOURCE_LENGTH']]=len(source);vector[index['TARGET_LENGTH']]=len(target)
        vector[index['BOUNDARY_EDITS']]=sum(v for k,v in atom_counts(program).items() if 'BOUNDARY' in k)
        vectors.append(vector)
    if len(vectors) not in (2,3):raise ValueError((rep,source_locus,target_locus,len(vectors)))
    return (np.sum(vectors,axis=0,dtype=np.int32)*(SCALE//len(vectors))).astype(np.int16)

def row_signature(edge):
    a=re.search(r':R(\d+)$',edge.source_node);b=re.search(r':R(\d+)$',edge.target_node)
    return (edge.panel_id,edge.relation_type,a.group(1) if a else '',b.group(1) if b else '')

def groups_for(test):
    groups=defaultdict(list)
    for i,e in enumerate(test.edges):
        key=(e.panel_id,'CYCLE') if e.relation_type=='CYCLIC_SUCCESSOR' else row_signature(e)
        groups[key].append(i)
    return {k:v for k,v in sorted(groups.items(),key=lambda x:str(x[0]))}

def score_baseline(train,test,name):
    if name=='edge_independent':return categorical_test_costs(train.vectors,np.zeros(len(train.edges),dtype=np.int32),1,test.vectors)[1]
    costs=np.zeros(len(test.edges),dtype=np.int64)
    for i,e in enumerate(test.edges):
        candidates=[j for j,x in enumerate(train.edges) if x.relation_type==e.relation_type]
        if name=='source_target_length_matched':
            exact=[j for j in candidates if int(train.vectors[j,-3])==int(test.vectors[i,-3]) and int(train.vectors[j,-2])==int(test.vectors[i,-2])]
            if exact:candidates=exact
        if not candidates:candidates=list(range(len(train.edges)))
        _,value=categorical_test_costs(train.vectors[candidates],np.zeros(len(candidates),dtype=np.int32),1,test.vectors[i:i+1]);costs[i]=value[0]
    return costs

def panel_mean(edges,values):
    d=defaultdict(list)
    for e,v in zip(edges,values):d[e.panel_id].append(float(v))
    return {k:float(np.mean(v)) for k,v in sorted(d.items())}

def null_mapping(test,world):
    mapping={}; rng=np.random.default_rng(stable_seed('RTA001_NULL',world,test.edges[0].physical_folio))
    for key,indices in groups_for(test).items():
        targets=[test.edges[i].target_locus for i in indices];n=len(indices)
        if n<2:
            for i,t in zip(indices,targets):mapping[i]=t
        elif key[1]=='CYCLE':
            shift=int(rng.integers(1,n)); order=np.roll(np.arange(n),shift)
            if int(rng.integers(0,2)):order=order[::-1]
            for i,j in zip(indices,order):mapping[i]=targets[int(j)]
        else:
            order=rng.permutation(n)
            if np.array_equal(order,np.arange(n)):order=np.roll(order,1)
            for i,j in zip(indices,order):mapping[i]=targets[int(j)]
    return mapping

def candidate_costs(train,test,model,baseline):
    seq=sequence_maps(test.representation); pair_rows=[]; pair_keys=[]
    for _,indices in groups_for(test).items():
        targets=sorted({test.edges[i].target_locus for i in indices})
        for i in indices:
            for target in targets:
                pair_keys.append((i,target));pair_rows.append(pair_vector(test.representation,test.edges[i].source_locus,target,test.feature_names,seq))
    matrix=np.stack(pair_rows); meta=tuple(test.edges[i] for i,_ in pair_keys)
    candidates=FeatureData(test.representation,test.vocabulary,test.feature_names,matrix,test.weights,np.zeros(len(matrix),dtype=np.int64),meta,tuple('' for _ in meta))
    _,mc=score_model(train,model,candidates);bc=score_baseline(train,candidates,baseline)
    return {key:(int(m),int(b)) for key,m,b in zip(pair_keys,mc,bc)}

def main():
    calibration=json.loads(CAL.read_text())
    if calibration['status']!='PASS':raise SystemExit('calibration not PASS')
    for name,digest in calibration['inputs'].items():
        candidates=[HERE/name,R/name]
        path=next((p for p in candidates if p.exists()),None)
        if path is None or sha(path)!=digest:raise SystemExit(f'calibration input drift: {name}')
    full_surface=build_feature_data(R,'surface');folios=sorted({e.physical_folio for e in full_surface.edges})
    with ProcessPoolExecutor(max_workers=min(9,os.cpu_count() or 1)) as pool: fitted=list(pool.map(select_fold,folios))
    folds={folio:(winner,best) for folio,winner,best in fitted}; fold_rows=[];fold_json=[];codebooks=[];folio_gains=[];null_cache={};rep_gains=defaultdict(list)
    for folio in folios:
        winner,best=folds[folio];_,_,_,model,train,test=winner
        assignments,mc=score_model(train,model,test);bases=baseline_training_and_test(train,test);baseline=min(bases,key=lambda n:(bases[n]['training_total_scaled'],n));bc=bases[baseline]['test_costs_scaled']
        mp=panel_mean(test.edges,mc);bp=panel_mean(test.edges,bc);pg={p:(bp[p]-mp[p])/SCALE for p in mp};gain=float(np.mean(list(pg.values())));folio_gains.append(gain)
        costs=candidate_costs(train,test,model,baseline);null_cache[folio]=(test,costs)
        per_rep={}
        for rep,item in best.items():
            _,_,_,rm,rt,rv=item;_,rmc=score_model(rt,rm,rv);rb=baseline_training_and_test(rt,rv);rn=min(rb,key=lambda n:(rb[n]['training_total_scaled'],n));rbc=rb[rn]['test_costs_scaled'];g=float(np.mean(list({p:(panel_mean(rv.edges,rbc)[p]-panel_mean(rv.edges,rmc)[p])/SCALE for p in panel_mean(rv.edges,rmc)}.values())));per_rep[rep]=g;rep_gains[rep].append(g)
        for panel in mp:
            fold_rows.append({'physical_folio':folio,'panel_id':panel,'heldout_edges':str(sum(e.panel_id==panel for e in test.edges)),'selected_representation':model.representation,'selected_k':str(model.k),'strongest_admissible_baseline':baseline,'operator_bits_per_edge':f'{mp[panel]/SCALE:.6f}','baseline_bits_per_edge':f'{bp[panel]/SCALE:.6f}','gain_bits_per_edge':f'{pg[panel]:.6f}','composition_residual_bits':f'{model.composition_bits_scaled/SCALE:.6f}','cycle_residual_bits':f'{model.cycle_bits_scaled/SCALE:.6f}','rectangle_residual_bits':'0.000000'})
        operators=[]
        for c,medoid in enumerate(model.medoid_indices):
            members=[i for i,a in enumerate(model.assignments) if a==c];held=[i for i,a in enumerate(assignments) if int(a)==c]
            examples=[train.edges[i].relation_instance for i in members[:3]];counter=[train.edges[i].relation_instance for i in members if model.assignment_costs_scaled[i]>0][:3]
            operators.append({'operator_id':f'OP{c+1:02d}','dsl_program':train.medoid_programs[medoid],'supporting_relation_types':sorted({train.edges[i].relation_type for i in members}),'training_folios':sorted({train.edges[i].physical_folio for i in members}),'training_support':len(members),'heldout_support':len(held),'representative_examples':examples,'counterexamples':counter,'residual_bits':sum(model.assignment_costs_scaled[i] for i in members)/SCALE,'composition_residual_bits':model.composition_bits_scaled/SCALE,'cycle_residual_bits':model.cycle_bits_scaled/SCALE,'survives_literal_surface_removal':model.representation in {'family','root','construction'}})
        codebooks.append({'holdout_folio':folio,'representation':model.representation,'k':model.k,'operators':operators})
        fold_json.append({'physical_folio':folio,'selected_representation':model.representation,'selected_k':model.k,'strongest_admissible_baseline':baseline,'folio_gain_bits_per_edge':gain,'positive':gain>0,'representation_gains_bits_per_edge':per_rep,'model':asdict(model),'heldout_assignment_sha256':hashlib.sha256(np.array(assignments,dtype='<i4').tobytes()).hexdigest()})
    observed=float(np.mean(folio_gains));null=[]
    for world in range(4096):
        fg=[]
        for folio in folios:
            test,costs=null_cache[folio];mapping=null_mapping(test,world);pm=[];pb=[]
            for i,e in enumerate(test.edges):m,b=costs[(i,mapping[i])];pm.append(m);pb.append(b)
            a=panel_mean(test.edges,np.array(pm));b=panel_mean(test.edges,np.array(pb));fg.append(float(np.mean([(b[p]-a[p])/SCALE for p in a])))
        null.append(float(np.mean(fg)))
    p=sum(x>=observed for x in null)/4096
    recurring=sum(any(len(op['training_folios'])>=3 and op['heldout_support']>0 for op in fold['operators']) for fold in codebooks)
    robustness={'positive_folios_at_least_7_of_9':sum(x>0 for x in folio_gains)>=7,'operator_recurs_on_3_folios_and_is_used_heldout':recurring>0,'abstract_representation_positive_without_exact_identity':any(np.mean(rep_gains[r])>0 for r in ('construction','root','family'))}
    status='PASS' if observed>0 and p<=.01 and all(robustness.values()) else 'FAIL'
    result={'experiment':'RTA001_GRAPH_TO_TEXT_OPERATOR_INDUCTION','schema_version':'RTA001_RESULT_V1','status':status,'decision':'ANONYMOUS_RELATIONAL_OPERATORS_TRANSFER' if status=='PASS' else 'NO_TRANSFER_AT_REGISTERED_RESOLUTION','primary':{'statistic':'equal-folio held-out description-length gain over strongest admissible baseline','gain_bits_per_edge':observed,'null_worlds':4096,'inclusive_p_value':p,'positive_folios':sum(x>0 for x in folio_gains),'physical_folios':9},'robustness':robustness,'secondary':{'recurring_operator_fold_instances':recurring,'representation_mean_gains_bits_per_edge':{r:float(np.mean(v)) for r,v in rep_gains.items()},'representation_selection_counts':dict(Counter(x['selected_representation'] for x in fold_json)),'mean_composition_residual_bits':float(np.mean([x[0][3].composition_bits_scaled/SCALE for x in folds.values()])),'mean_cycle_residual_bits':float(np.mean([x[0][3].cycle_bits_scaled/SCALE for x in folds.values()])),'rectangle_residual_bits':0.0},'folds':fold_json,'null':{'gains_bits_per_edge':null,'gain_sha256':hashlib.sha256(np.array(null,dtype='<f8').tobytes()).hexdigest(),'minimum':min(null),'median':float(np.median(null)),'maximum':max(null)},'inputs':{'synthetic_calibration_sha256':sha(CAL),'edge_program_metadata_sha256':sha(PROGRAM_META),'runner_sha256':sha(Path(__file__))},'claim_ceiling':'At most, anonymous formal transformations correspond to author-visible relations and predict held-out panels; no meaning, language, cipher, plaintext, or translation is assigned.'}
    fields=list(fold_rows[0]);
    with HELD.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(fold_rows)
    codebook={'experiment':'RTA001_OPERATOR_CODEBOOK','schema_version':'RTA001_OPERATOR_CODEBOOK_V1','status':status,'fold_codebooks':codebooks,'claim_ceiling':result['claim_ceiling']};write_json(CODEBOOK,codebook)
    lines=['# RTA001 anonymous operator atlas','',f'Overall result: **{status}**.','', 'Operators are fold-local anonymous medoids. IDs carry no meaning.','']
    for fold in codebooks:
        lines += [f"## Holdout {fold['holdout_folio']} — {fold['representation']}, K={fold['k']}",'']
        for op in fold['operators']:
            lines += [f"### {op['operator_id']}",'',f"- Explicit DSL: `{op['dsl_program']}`",f"- Relation types: {', '.join(op['supporting_relation_types'])}",f"- Training folios: {', '.join(op['training_folios'])}",f"- Training/held-out support: {op['training_support']}/{op['heldout_support']}",f"- Examples: {', '.join(op['representative_examples']) or 'none'}",f"- Counterexamples: {', '.join(op['counterexamples']) or 'none'}",f"- Residual: {op['residual_bits']:.3f} bits; composition {op['composition_residual_bits']:.3f}; cycle {op['cycle_residual_bits']:.3f}",f"- Survives removal of literal surface identity: {op['survives_literal_surface_removal']}",'']
    lines+=['## Ceiling','',result['claim_ceiling'],''];ATLAS.write_text('\n'.join(lines),encoding='utf-8')
    result['artifacts']={HELD.name:sha(HELD),CODEBOOK.name:sha(CODEBOOK),ATLAS.name:sha(ATLAS)};write_json(OUT,result)
    report=['# RTA001 result','',f"Status: **{status}** — `{result['decision']}`.",'',f"Held-out gain: **{observed:.6f} bits/edge**; exact 4,096-world CPU p = **{p:.6f}**.",'',f"Positive folios: {result['primary']['positive_folios']}/9.",'','## Robustness','']+[f"- `{k}`: **{'PASS' if v else 'FAIL'}**" for k,v in robustness.items()]+['','## Interpretation','',result['claim_ceiling'],'']
    report += ['Next: RTA002 may test these anonymous operators in prose beyond adjacency.' if status=='PASS' else 'Next: latent grapheme/transcription-channel reconstruction; do not return to visual binary attributes or exact-label mining.',''];REPORT.write_text('\n'.join(report),encoding='utf-8')
    print(json.dumps({'status':status,**result['primary']},sort_keys=True))
if __name__=='__main__':main()
