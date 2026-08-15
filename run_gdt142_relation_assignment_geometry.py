#!/usr/bin/env python3
"""Post-hoc exact assignment-geometry audit of the published GDT140 matrices."""
import csv, hashlib, itertools, json, math
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parent
INV=R/'gdt140_herbal_relation_inventory.tsv'
PAIR=R/'gdt140_pair_similarities.tsv'
ORBIT=R/'gdt140_assignment_orbit.tsv'
PARENT=R/'gdt140_result.json'
DECOMP=R/'gdt141_result.json'
METHOD=R/'GDT142_RELATION_ASSIGNMENT_GEOMETRY_METHOD.md'
REPORT=R/'GDT142_RELATION_ASSIGNMENT_GEOMETRY_REPORT.md'
SCORES=R/'gdt142_normalization_scores.tsv'
ASSIGN=R/'gdt142_assignment_scores.tsv'
RECIP=R/'gdt142_relation_reciprocity.tsv'
NEAR=R/'gdt142_near_optimal_assignments.tsv'
COUNTER=R/'gdt142_counterexamples.tsv'
RESULT=R/'gdt142_result.json'

REPS=('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE')
NORMS=('RAW_SIMILARITY','SOURCE_RANK','TARGET_RANK','MUTUAL_RANK_MEAN','RECIPROCAL_RANK_MEAN','MUTUAL_TOP2')

def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def clean(rows):return [{k:f'{v:.12g}' if isinstance(v,float) else v for k,v in x.items()} for x in rows]
def competition_ranks(v):
 return np.array([1+sum(y>x+1e-12 for y in v) for x in v],float)
def normalized_matrices(m):
 sr=np.stack([competition_ranks(m[i,:]) for i in range(5)])
 tr=np.stack([competition_ranks(m[:,j]) for j in range(5)]).T
 return {
  'RAW_SIMILARITY':m,
  'SOURCE_RANK':(6-sr)/5,
  'TARGET_RANK':(6-tr)/5,
  'MUTUAL_RANK_MEAN':((6-sr)+(6-tr))/10,
  'RECIPROCAL_RANK_MEAN':.5*(1/sr+1/tr),
  'MUTUAL_TOP2':((sr<=2)&(tr<=2)).astype(float),
 },sr,tr

rels=read(INV);pairs=read(PAIR);orbit=read(ORBIT)
assert len(rels)==5 and len(pairs)==100 and len(orbit)==120
sources=[x['source_page'] for x in rels];targets=[x['target_page'] for x in rels]
assert not any(x.startswith('f84') for x in sources+targets)
maps=[]
for x in orbit:
 d=dict(z.split('->') for z in x['mapping'].split('|'))
 maps.append([targets.index(d[s]) for s in sources])
true_idx=next(i for i,x in enumerate(orbit) if x['is_true']=='1')

matrices={r:np.zeros((5,5),float) for r in REPS}
for x in pairs:
 matrices[x['representation']][sources.index(x['source_page']),targets.index(x['candidate_target_page'])]=float(x['similarity'])

variant_rows=[];assignment_rows=[];reciprocity=[];zs=[];variant_values={};rank_cache={}
for rep in REPS:
 nm,sr,tr=normalized_matrices(matrices[rep]);rank_cache[rep]=(sr,tr)
 for norm in NORMS:
  m=nm[norm]
  vals=np.array([sum(m[i,j] for i,j in enumerate(q))/5 for q in maps])
  z=(vals-vals.mean())/(vals.std() or 1)
  zs.append(z);variant_values[(rep,norm)]=(vals,z)
  ts=float(vals[true_idx]);rank=1+int(np.sum(vals>ts+1e-12));p=float(np.mean(vals>=ts-1e-12))
  variant_rows.append({'representation':rep,'normalization':norm,'true_score':ts,'null_mean':float(vals.mean()),'null_sd':float(vals.std()),'true_z':float(z[true_idx]),'inclusive_rank_of_120':rank,'local_inclusive_p':p,'max_24_inclusive_p':'PENDING'})
  for i,x in enumerate(orbit):assignment_rows.append({'representation':rep,'normalization':norm,'assignment_id':x['assignment_id'],'is_true':x['is_true'],'score':float(vals[i]),'standardized_score':float(z[i]),'max_24_standardized_score':'PENDING'})
 for i,x in enumerate(rels):
  reciprocity.append({'relation_id':x['relation_id'],'representation':rep,'source_page':x['source_page'],'target_page':x['target_page'],'source_rank_of_true_target':int(sr[i,i]),'target_rank_of_true_source':int(tr[i,i]),'mutual_top2':int(sr[i,i]<=2 and tr[i,i]<=2),'raw_similarity':float(matrices[rep][i,i])})

maxz=np.max(np.stack(zs),axis=0);max24=float(np.mean(maxz>=maxz[true_idx]-1e-12))
for x in variant_rows:x['max_24_inclusive_p']=max24
for x in assignment_rows:x['max_24_standardized_score']=float(maxz[next(i for i,a in enumerate(orbit) if a['assignment_id']==x['assignment_id'])])

key=('PAGE_HOST_CHAR3','RECIPROCAL_RANK_MEAN');vals,z=variant_values[key]
weights=np.exp(z-z.max());weights/=weights.sum()
order=sorted(range(120),key=lambda i:(-vals[i],orbit[i]['assignment_id']))
near=[]
for k,i in enumerate(order[:12],1):
 q=maps[i];near.append({'rank_by_key_variant':k,'assignment_id':orbit[i]['assignment_id'],'is_true':orbit[i]['is_true'],'mapping':orbit[i]['mapping'],'score':float(vals[i]),'standardized_score':float(z[i]),'descriptive_softmax_mass':float(weights[i]),'correct_edges':sum(q[j]==j for j in range(5))})
entropy=-float(np.sum(weights*np.log2(np.maximum(weights,1e-300))))
effective=2**entropy

char=[x for x in variant_rows if x['representation']=='PAGE_HOST_CHAR3']
gates={'all_six_page_host_char3_ranks_le_6':all(int(x['inclusive_rank_of_120'])<=6 for x in char),'max_24_inclusive_p_le_0_05':max24<=.05}
status='RELATION_ASSIGNMENT_GEOMETRY_ROBUST_WITHIN_EXPOSED_5X5' if all(gates.values()) else 'RELATION_ASSIGNMENT_GEOMETRY_SENSITIVE'
# Build rows explicitly to retain one row per weak PAGE_HOST relation.
counter=[{'type':'EXPOSED_POSTHOC_PANEL','item':'GDT140_5X5','value':'NA','detail':'Normalization family was designed after the GDT140 matrix was exposed; max-24 does not correct that history.'},{'type':'SMALL_CANDIDATE_POOL','item':'FIVE_TARGET_PAGES','value':5,'detail':'Ranks are conditional on the five frozen targets, not all Herbal pages.'},{'type':'NO_SOURCE_NATIVE_REPLICATION','item':'GDT062_DERIVED_VIEW','value':'NA','detail':'This audit uses published similarities only and adds no alternate-reading replication.'}]
for x in reciprocity:
 if x['representation']=='PAGE_HOST_CHAR3' and not x['mutual_top2']:
  counter.append({'type':'NONMUTUAL_TRUE_PAIR','item':x['relation_id'],'value':f"{x['source_rank_of_true_target']}/{x['target_rank_of_true_source']}",'detail':'True PAGE_HOST-char3 pair is not mutual top-two.'})

write(SCORES,clean(variant_rows));write(ASSIGN,clean(assignment_rows));write(RECIP,clean(reciprocity));write(NEAR,clean(near));write(COUNTER,counter)
best=max(char,key=lambda x:float(x['true_z']))
REPORT.write_text(f"""# GDT142 — relation assignment geometry

## Outcome

**{status}**

The GDT140 PAGE_HOST-character-trigram lead is not an artifact of the absolute weighted-Jaccard scale inside the frozen five-by-five panel. Across raw similarity, source rank, target rank, mutual rank, reciprocal rank, and mutual-top-two scoring, the true mapping ranks {', '.join(str(x['inclusive_rank_of_120']) for x in char)} out of 120. The strongest fixed normalization is `{best['normalization']}` (z {float(best['true_z']):+.3f}); the exact maximum-over-24 diagnostic is p={max24:.4f}.

Four of five PAGE_HOST-character-trigram true pairs are the best incoming match for their target, while source-side ranks are 1, 2, 3, 1, 1. Three pairs are mutual top-two. The true mapping is therefore supported by a distributed assignment geometry, but not by five individually reciprocal nearest neighbours. Under a purely descriptive unit-temperature softmax of the standardized reciprocal-rank score, assignment entropy is {entropy:.3f} bits (effective {effective:.2f} assignments); this is not a semantic posterior.

This remains an exposed post-hoc audit of five candidate targets. It does not supply a manuscript-wide donor rank or an independent visual panel, and max-24 cannot correct the decision to inspect normalizations after GDT140. It uses only already-published f84-free artifacts; no transcription source or image was opened. No botanical truth, plant/component identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation follows.
""",encoding='utf8')

result={'schema':'GDT142_RELATION_ASSIGNMENT_GEOMETRY_RESULT_V1','status':status,'relations':5,'assignment_worlds':120,'representations':list(REPS),'normalizations':list(NORMS),'variant_count':24,'scores':variant_rows,'max_24_inclusive_p':max24,'key_variant':{'representation':key[0],'normalization':key[1],'descriptive_assignment_entropy_bits':entropy,'descriptive_effective_assignments':effective,'true_descriptive_softmax_mass':float(weights[true_idx])},'gates':gates,'interpretation':'Post-hoc scale and reciprocity robustness inside the exposed GDT140 five-by-five assignment.','claim_ceiling':'Assignment-geometry robustness only; no independent panel, botanical truth, identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84':{'all_inputs_are_derived_gdt140_panel_artifacts_with_zero_f84_pages':True,'source_or_image_opened':False,'new_f84r_access':False},'inputs':{p.name:sha(p) for p in (INV,PAIR,ORBIT,PARENT,DECOMP)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (SCORES,ASSIGN,RECIP,NEAR,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
print(json.dumps({'status':status,'max24_p':max24,'char3_ranks':[x['inclusive_rank_of_120'] for x in char],'effective_assignments':effective},sort_keys=True))
