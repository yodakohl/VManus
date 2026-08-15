#!/usr/bin/env python3
"""Freeze GDT150 targets and predictions before image access."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;OCC=R/'gdt149_candidate_host_occurrences.tsv';VIS=R/'gdt137_herbal_visual_feature_inventory.tsv';P149=R/'gdt149_result.json';METHOD=R/'GDT150_KOR_ROOT_VISUAL_TRANSFER_METHOD.md';INV=R/'gdt150_kor_root_targets.tsv';PRED=R/'gdt150_prediction.json'
FEATURES=('DAISY_CUP','BROAD_CALYX','GRASS','ROOT_PLATFORM','LEAVES_ONE_SIDE','FUSED_PARALLEL_LEAVES','BULB_OR_TUBER_ROOT','LARGE_OR_EXTENSIVE_ROOT','MULTIPLE_PLANTS','BLUE_FLOWERS_OR_BUDS','FINGERED_OR_FRILLED_LEAVES','MULTIPLE_STEMS_OR_STALKS')
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
vis={x['page']:x for x in read(VIS)};occ=read(OCC);pages=sorted({x['page'] for x in occ if x['page_host']=='kor' and x['page'] not in {'f90r1','f3v'} and all(vis[x['page']][f]=='0' for f in FEATURES)})
assert pages==['f22r','f37r'] and not any(p.startswith('f84') for p in pages)
rows=[]
for p in pages:
 q=[x for x in occ if x['page_host']=='kor' and x['page']==p];assert len(q)==1
 rows.append({'target_id':'GDT150_'+p.upper(),'page':p,'physical_folio':q[0]['physical_folio'],'kor_locus':q[0]['locus'],'kor_surface':q[0]['surface_token'],'selection_rule':'EXACT_KOR_NON_MHI007_ZERO_OF_12_GDT137_FEATURES','frozen_prediction':'POSITIVE','visual_endpoint':'CONSPICUOUS_THICKENED_SEGMENTED_OR_BULB_LIKE_ROOT_ARCHITECTURE','image_access_before_freeze':'NO','visual_call':'SEALED_NOT_REVIEWED','provenance':'SOURCE_SELECTED_PROSPECTIVE_AI_VISUAL_TEST','semantic_role':'UNASSIGNED'})
write(INV,rows)
pred={'schema':'GDT150_KOR_ROOT_VISUAL_TRANSFER_PREDICTION_V1','status':'FROZEN_BEFORE_TARGET_IMAGE_ACCESS','hypothesis':'Exact PAGE_HOST KOR predicts conspicuous thickened, segmented, or bulb-like root architecture.','targets':rows,'positive_rule':'At least one repeated rounded/thickened/tuber-like chamber or serial telescoping root segment clearly distinct from thin tapering roots and central stem.','negative_rule':'Visible and judgeable root system contains only ordinary thin/tapering or unsegmented root strokes.','uncertain_rule':'Damage, crop, paint, or geometry prevents the distinction.','decision':{'both_positive':'KOR_ROOT_GEOMETRY_GLOSS_TRANSFERS','any_negative':'KOR_ROOT_GEOMETRY_GLOSS_REJECTED','otherwise':'KOR_ROOT_GEOMETRY_GLOSS_UNRESOLVED'},'reviewer_provenance':'AI_DIRECT_VISUAL_OBSERVATION;HYPOTHESIS_AWARE;NO_HUMAN_CONFIRMATION','claim_ceiling':'One prospective visible-root-geometry gloss test only; no plant identity, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84':{'targeted':False,'opened':False,'queried':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (OCC,VIS,P149)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{INV.name:sha(INV)},'documents':{METHOD.name:sha(METHOD)}};pred['prediction_content_sha256']=csha(pred);PRED.write_text(json.dumps(pred,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':pred['status'],'pages':pages},sort_keys=True))
