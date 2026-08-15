#!/usr/bin/env python3
"""Corpus-wide O/OT PAGE_HOST retrieval sensitivity for GDT140 relations."""
import csv,hashlib,json,random
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;UNITS=R/'gdt112_o_ot_units.tsv';META=R/'gdt137_herbal_visual_feature_inventory.tsv';INV=R/'gdt140_herbal_relation_inventory.tsv';PARENT=R/'gdt140_result.json';NESTED=R/'gdt143_result.json';METHOD=R/'GDT144_CORPUS_WIDE_RELATION_RETRIEVAL_METHOD.md';REPORT=R/'GDT144_CORPUS_WIDE_RELATION_RETRIEVAL_REPORT.md';PAIR=R/'gdt144_pair_ranks.tsv';NULL=R/'gdt144_null_results.tsv';CAP=R/'gdt144_capacity.tsv';COUNTER=R/'gdt144_counterexamples.tsv';RESULT=R/'gdt144_result.json'
REPS=('HOST_SET','HOST_CHAR3_SET','FRAME_HOST_SET','FRAME_HOST_CHAR3_SET');WORLDS=100000;SEED=144140
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def clean(rows):return [{k:f'{v:.12g}' if isinstance(v,float) else v for k,v in x.items()} for x in rows]
def tri(s):
 s='^'+s+'$';return {s[i:i+3] for i in range(max(1,len(s)-2))}
def jac(a,b):return len(a&b)/len(a|b) if a|b else 0.

meta={x['page']:x for x in read(META)};units=read(UNITS);rels=read(INV)
assert not any(x['page'].startswith('f84r') for x in units) and not any(x['page'].startswith('f84r') for x in meta.values())
eligible0=sorted(p for p,x in meta.items() if x['currier']=='A' and x['hand']=='1')
by=defaultdict(list)
for x in units:
 if x['page'] in eligible0:by[x['page']].append(x)
eligible=sorted(p for p in eligible0 if p in by);covered=[x for x in rels if x['source_page'] in by and x['target_page'] in by];excluded=[x for x in rels if x not in covered]
assert len(eligible)==93 and len(covered)==4 and len(excluded)==1 and excluded[0]['relation_id']=='MHI002'
feat={}
for p in eligible:
 h={x['page_host'] for x in by[p]};hc=set().union(*(tri(x) for x in h));fh={x['frame']+'='+x['page_host'] for x in by[p]};fhc=set().union(*({x['frame']+'='+z for z in tri(x['page_host'])} for x in by[p]));feat[p]={'HOST_SET':h,'HOST_CHAR3_SET':hc,'FRAME_HOST_SET':fh,'FRAME_HOST_CHAR3_SET':fhc}
cands=[];zmat=[];rawmat=[];pair_rows=[]
for i,x in enumerate(covered):
 s=x['source_page'];t=x['target_page'];c=[p for p in eligible if p!=s and meta[p]['physical_folio']!=meta[s]['physical_folio']];cands.append(c);zr=[];rr=[]
 for rep in REPS:
  v=np.array([jac(feat[s][rep],feat[p][rep]) for p in c]);mu=float(v.mean());sd=float(v.std()) or 1.;z=(v-mu)/sd;score=jac(feat[s][rep],feat[t][rep]);rank=1+int(np.sum(v>score+1e-12));tail=float(np.mean(v>=score-1e-12));zr.append(dict(zip(c,z)));rr.append(dict(zip(c,v)))
  pair_rows.append({'relation_id':x['relation_id'],'source_page':s,'target_page':t,'representation':rep,'similarity':score,'candidate_pages':len(c),'true_target_rank':rank,'inclusive_candidate_tail':tail,'source_standardized_similarity':float((score-mu)/sd),'top_decile':int(rank<=max(1,int(np.ceil(.1*len(c))))),'top_three_candidates':'|'.join(p for _,p in sorted(zip(v,c),reverse=True)[:3])})
 zmat.append(zr);rawmat.append(rr)
obs=np.array([np.mean([zmat[i][k][covered[i]['target_page']] for i in range(4)]) for k in range(4)])
rng=random.Random(SEED);null=np.zeros((WORLDS,4))
for w in range(WORLDS):
 while True:
  draw=[rng.choice(cands[i]) for i in range(4)]
  if len(set(draw))==4:break
 for k in range(4):null[w,k]=np.mean([zmat[i][k][draw[i]] for i in range(4)])
mu=null.mean(0);sd=null.std(0);zobs=(obs-mu)/sd;znull=(null-mu)/sd;mx=znull.max(1);max4=float(np.mean(mx>=zobs.max()-1e-12));null_rows=[]
for k,rep in enumerate(REPS):null_rows.append({'representation':rep,'true_mean_source_z':float(obs[k]),'null_mean':float(mu[k]),'null_sd':float(sd[k]),'true_null_standardized_z':float(zobs[k]),'local_monte_carlo_p':float(np.mean(null[:,k]>=obs[k]-1e-12)),'max_four_monte_carlo_p':max4,'worlds':WORLDS,'seed':SEED})
top_decile=max(sum(int(q['top_decile']) for q in pair_rows if q['representation']==rep) for rep in REPS);gates={'at_least_three_of_four_top_decile_in_one_fixed_representation':top_decile>=3,'max_four_p_le_0_05':max4<=.05};status='O_OT_PAGE_HOST_CORPUS_WIDE_RELATION_RETRIEVAL_SUPPORTED' if all(gates.values()) else 'O_OT_PAGE_HOST_CORPUS_WIDE_RELATION_RETRIEVAL_NOT_SUPPORTED'
cap=[{'state':'ELIGIBLE_HERBAL_A_HAND1_PAGES','count':len(eligible),'detail':'Pages with at least one unique O/OT PAGE_HOST unit.'},{'state':'COVERED_RELATIONS','count':len(covered),'detail':'MHI003/MHI004/MHI006/MHI007.'},{'state':'EXCLUDED_NO_TARGET_O_OT_CAPACITY','count':len(excluded),'detail':'MHI002 f17v to f96v; f96v has no O/OT unit.'}]
counter=[{'type':'CORPUS_WIDE_RANK_FAILURE','item':q['relation_id'],'representation':q['representation'],'value':q['true_target_rank'],'detail':f"True target ranks {q['true_target_rank']}/{q['candidate_pages']}."} for q in pair_rows if q['representation']=='HOST_CHAR3_SET' and not int(q['top_decile'])]+[{'type':'PARTIAL_REPRESENTATION','item':'GDT112_O_OT_UNIQUE_SETS','representation':'ALL','value':'NA','detail':'Frequency and non-O/OT PAGE_HOSTs are absent; this does not refute full PAGE_HOST retrieval.'},{'type':'POSTHOC_EXPOSED','item':'GDT140','representation':'ALL','value':'NA','detail':'Designed after the five-target relation lead was known.'}]
write(PAIR,clean(pair_rows));write(NULL,clean(null_rows));write(CAP,cap);write(COUNTER,counter)
char=[q for q in pair_rows if q['representation']=='HOST_CHAR3_SET']
REPORT.write_text(f"""# GDT144 — corpus-wide relation retrieval

## Outcome

**{status}**

The partial O/OT PAGE_HOST representation covers 93 comparable Herbal A/hand-1 pages and four of five GDT140 relations. Under PAGE_HOST character-trigram sets, true targets rank {', '.join(str(q['true_target_rank'])+'/'+str(q['candidate_pages']) for q in char)}. Only MHI004 (the f6r→f51r leaves relation) is near the top, at rank {next(q['true_target_rank'] for q in char if q['relation_id']=='MHI004')}; the other three are ordinary or poor retrievals. Across four fixed representations and 100,000 distinct-target worlds, the maximum-over-four tail is p={max4:.5f}; the best aggregate z is only {float(zobs.max()):+.3f}.

This sharply limits GDT140/GDT143: their PAGE_HOST relation structure distinguishes the five frozen target pages, but this O/OT-only view does not retrieve three of four partners from the wider comparable Herbal corpus. MHI002 is unscored because f96v has no O/OT unit. The result is a partial-set sensitivity, not a test of full PAGE_HOST frequency profiles.

Both inputs are already published f84r-free derived tables; no global source or image was opened. No botanical truth, identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation follows.
""",encoding='utf8')
result={'schema':'GDT144_CORPUS_WIDE_RELATION_RETRIEVAL_RESULT_V1','status':status,'eligible_pages':len(eligible),'covered_relations':[x['relation_id'] for x in covered],'capacity_exclusions':[x['relation_id'] for x in excluded],'representations':list(REPS),'worlds':WORLDS,'seed':SEED,'null_results':null_rows,'best_top_decile_relation_count':top_decile,'gates':gates,'interpretation':'Partial O/OT PAGE_HOST sets do not retrieve most GDT140 targets corpus-wide.','claim_ceiling':'Partial-representation corpus retrieval only; no full PAGE_HOST refutation, botanical truth, identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84':{'all_actual_inputs_have_zero_f84r_rows':True,'global_source_or_image_opened':False,'new_f84r_access':False},'inputs':{p.name:sha(p) for p in (UNITS,META,INV,PARENT,NESTED)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (PAIR,NULL,CAP,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'eligible':len(eligible),'covered':len(covered),'char3_ranks':[q['true_target_rank'] for q in char],'max4_p':max4},sort_keys=True))
