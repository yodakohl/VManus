#!/usr/bin/env python3
"""Freeze the untouched five-by-five Herbal relation assignment panel."""
import csv,hashlib,itertools,json
from pathlib import Path
R=Path(__file__).resolve().parent;SRC=R/'experiments/semantic_assumptions/cache/existing_human_annotations/manual_herbal_internal_relations.tsv';METHOD=R/'GDT140_HERBAL_RELATION_PAGE_HOST_TRANSFER_METHOD.md';INV=R/'gdt140_herbal_relation_inventory.tsv';ASSIGN=R/'gdt140_assignment_orbit.tsv';PRED=R/'gdt140_prediction.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
rows=list(csv.DictReader(SRC.open(encoding='utf8'),delimiter='\t'));selected={}
for x in rows:
 if x['panel_class']=='CLEAN_HA_HAND1_5X5':selected.setdefault(x['relation_id'],x)
assert sorted(selected)==['MHI002','MHI003','MHI004','MHI006','MHI007']
out=[]
for rid,x in sorted(selected.items()):
 assert x['page_a_section']==x['page_b_section']=='H' and x['page_a_currier']==x['page_b_currier']=='A' and x['page_a_hand']==x['page_b_hand']=='1'
 out.append({'relation_id':rid,'source_page':x['page_a'],'target_page':x['page_b'],'relation_class':x['relation_class'],'component':x['component'],'strength':x['strength'],'panel_class':x['panel_class'],'source_statement_sha256':hashlib.sha256(x['source_statement'].encode()).hexdigest(),'provenance':'EXISTING_HUMAN_ANNOTATION','semantic_role':'UNASSIGNED'})
assert len({x['source_page'] for x in out})==len({x['target_page'] for x in out})==5 and len({x[k] for x in out for k in ('source_page','target_page')})==10 and not any(x[k].startswith('f84') for x in out for k in ('source_page','target_page'))
with INV.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(out[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(out)
targets=[x['target_page'] for x in out];orbit=[]
for i,p in enumerate(itertools.permutations(targets)):
 orbit.append({'assignment_id':f'A{i:03d}','mapping':'|'.join(f"{out[j]['source_page']}->{p[j]}" for j in range(5)),'is_true':int(all(p[j]==out[j]['target_page'] for j in range(5)))})
assert len(orbit)==120 and sum(x['is_true'] for x in orbit)==1
with ASSIGN.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(orbit[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(orbit)
p={'schema':'GDT140_HERBAL_RELATION_PAGE_HOST_TRANSFER_PREDICTION_V1','status':'FROZEN_UNTOUCHED_5X5_RELATION_ASSIGNMENT_BEFORE_FORMAL_SCORING','relations':len(out),'source_pages':len({x['source_page'] for x in out}),'target_pages':len({x['target_page'] for x in out}),'assignment_worlds':len(orbit),'representations':['PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE'],'similarity':'WEIGHTED_JACCARD','primary_family':['PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3'],'gates':{'page_host_inclusive_rank_le_6_of_120':True,'page_host_beats_raw_and_compiler':True,'at_least_4_of_5_true_partner_ranks_le_2':True,'leave_one_pair_score_positive_at_least_4_of_5':True},'chronology':'The human relations and eligibility labels were archived before GDT140; the exact five relations, 120 assignments, representations and score were frozen before relation-conditioned formal similarities were computed.','prior_route_distinction':'FPR/S99 tested pharmaceutical-label roots against Herbal prose; GDT140 tests complete formal page-bag similarity within five disjoint Herbal-Herbal relations.','f84':{'all_f84_rows_rejected_before_retention':True,'new_f84r_access':False},'claim_ceiling':'Anonymous formal content preservation only; no botanical truth, plant/component identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','inputs':{str(x.relative_to(R)):sha(x) for x in (SRC,METHOD,R/'gdt062_result.json',R/'gdt139_result.json')},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{INV.name:sha(INV),ASSIGN.name:sha(ASSIGN)}};p['prediction_content_sha256']=csha(p);PRED.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':p['status'],'relations':p['relations'],'worlds':p['assignment_worlds']},sort_keys=True))
