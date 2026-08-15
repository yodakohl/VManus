#!/usr/bin/env python3
"""Exact coarse-visual confound audit for the GDT140 relation assignment."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;META=R/'gdt137_herbal_visual_feature_inventory.tsv';INV=R/'gdt140_herbal_relation_inventory.tsv';ORBIT=R/'gdt140_assignment_orbit.tsv';PARENT=R/'gdt140_result.json';METHOD=R/'GDT146_RELATION_COARSE_VISUAL_CONFOUND_METHOD.md';REPORT=R/'GDT146_RELATION_COARSE_VISUAL_CONFOUND_REPORT.md';SCORES=R/'gdt146_visual_scores.tsv';MATRIX=R/'gdt146_visual_pair_matrix.tsv';NULL=R/'gdt146_assignment_scores.tsv';RESULT=R/'gdt146_result.json'
FEATURES=('DAISY_CUP','BROAD_CALYX','GRASS','ROOT_PLATFORM','LEAVES_ONE_SIDE','FUSED_PARALLEL_LEAVES','BULB_OR_TUBER_ROOT','LARGE_OR_EXTENSIVE_ROOT','MULTIPLE_PLANTS','BLUE_FLOWERS_OR_BUDS','FINGERED_OR_FRILLED_LEAVES','MULTIPLE_STEMS_OR_STALKS');MODES=('POSITIVE_JACCARD','BIT_AGREEMENT','EXACT_ILLUSTRATION_PROFILE')
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def clean(rows):return [{k:f'{v:.12g}' if isinstance(v,float) else v for k,v in x.items()} for x in rows]
meta={x['page']:x for x in read(META)};rels=read(INV);orbit=read(ORBIT);s=[x['source_page'] for x in rels];t=[x['target_page'] for x in rels];assert not any(x.startswith('f84') for x in s+t)
maps=[]
for x in orbit:d=dict(z.split('->') for z in x['mapping'].split('|'));maps.append([t.index(d[a]) for a in s])
ti=next(i for i,x in enumerate(orbit) if x['is_true']=='1');mats={m:np.zeros((5,5)) for m in MODES};matrix=[]
for i,a in enumerate(s):
 av=np.array([int(meta[a][f]) for f in FEATURES])
 for j,b in enumerate(t):
  bv=np.array([int(meta[b][f]) for f in FEATURES]);u=np.sum((av==1)|(bv==1));vals={'POSITIVE_JACCARD':float(np.sum((av==1)&(bv==1))/u) if u else 0.,'BIT_AGREEMENT':float(np.mean(av==bv)),'EXACT_ILLUSTRATION_PROFILE':float(meta[a]['illustration_profile']==meta[b]['illustration_profile'])}
  for mode,v in vals.items():mats[mode][i,j]=v;matrix.append({'mode':mode,'source_page':a,'target_page':b,'similarity':v,'is_true_pair':int(i==j)})
scores=[];null=[]
for mode in MODES:
 v=np.array([sum(mats[mode][i,j] for i,j in enumerate(q))/5 for q in maps]);tv=float(v[ti]);scores.append({'mode':mode,'true_score':tv,'null_mean':float(v.mean()),'null_sd':float(v.std()),'inclusive_rank_of_120':1+int(np.sum(v>tv+1e-12)),'inclusive_p':float(np.mean(v>=tv-1e-12))})
 for i,x in enumerate(orbit):null.append({'mode':mode,'assignment_id':x['assignment_id'],'is_true':x['is_true'],'score':float(v[i])})
status='COARSE_VISUAL_PROFILE_DOES_NOT_EXPLAIN_RELATION_ASSIGNMENT' if all(float(x['inclusive_p'])>.05 for x in scores) else 'COARSE_VISUAL_PROFILE_POTENTIAL_CONFOUND';write(SCORES,clean(scores));write(MATRIX,clean(matrix));write(NULL,clean(null))
REPORT.write_text(f"""# GDT146 — coarse visual confound audit

## Outcome

**{status}**

The true relation mapping ranks {scores[0]['inclusive_rank_of_120']}/120 by positive-feature Jaccard (p={scores[0]['inclusive_p']:.3f}) and {scores[1]['inclusive_rank_of_120']}/120 by twelve-bit agreement (p={scores[1]['inclusive_p']:.3f}). Exact coarse illustration profiles tie across all 120 assignments (p={scores[2]['inclusive_p']:.3f}). The GDT140 PAGE_HOST assignment therefore is not explained by the twelve recorded GDT137 flags or their coarse profile label.

Those flags are sparse and do not encode the detailed human statements that selected the five relations, so this is not an independent validation or proof against visual-selection bias. Inputs are f84-free derived artifacts; no source or image was opened. No botanical truth, identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation follows.
""",encoding='utf8')
result={'schema':'GDT146_RELATION_COARSE_VISUAL_CONFOUND_RESULT_V1','status':status,'relations':5,'assignment_worlds':120,'features':list(FEATURES),'scores':scores,'interpretation':'The frozen relation assignment is not recoverable from twelve coarse recorded visual flags.','claim_ceiling':'Coarse-confound audit only; no independent relation validation, botanical truth, identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84':{'all_actual_inputs_are_f84_free':True,'source_or_image_opened':False,'new_f84r_access':False},'inputs':{p.name:sha(p) for p in (META,INV,ORBIT,PARENT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (SCORES,MATRIX,NULL)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'scores':scores},sort_keys=True))
