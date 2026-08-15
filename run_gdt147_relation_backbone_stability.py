#!/usr/bin/env python3
"""Post-hoc edge-stability localization of the exposed GDT140 5x5 lead."""
import csv, hashlib, json
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parent
INV=R/'gdt140_herbal_relation_inventory.tsv';PAIR=R/'gdt140_pair_similarities.tsv';ORBIT=R/'gdt140_assignment_orbit.tsv'
P140=R/'gdt140_result.json';P142=R/'gdt142_result.json';P144=R/'gdt144_result.json';P145=R/'gdt145_result.json'
METHOD=R/'GDT147_RELATION_BACKBONE_STABILITY_METHOD.md';REPORT=R/'GDT147_RELATION_BACKBONE_STABILITY_REPORT.md'
EDGES=R/'gdt147_edge_stability.tsv';BEST=R/'gdt147_best_assignments.tsv';SWAP=R/'gdt147_swap_diagnostics.tsv';COUNTER=R/'gdt147_counterexamples.tsv';RESULT=R/'gdt147_result.json'
NORMS=('RAW_SIMILARITY','SOURCE_RANK','TARGET_RANK','MUTUAL_RANK_MEAN','RECIPROCAL_RANK_MEAN','MUTUAL_TOP2')

def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def fmt(x):return f'{x:.12g}' if isinstance(x,float) else x
def clean(rows):return [{k:fmt(v) for k,v in x.items()} for x in rows]
def ranks(v):return np.array([1+sum(y>x+1e-12 for y in v) for x in v],float)

rels=read(INV);pairs=read(PAIR);orbit=read(ORBIT)
assert len(rels)==5 and len(orbit)==120
sources=[x['source_page'] for x in rels];targets=[x['target_page'] for x in rels]
assert not any(x.startswith('f84') for x in sources+targets)
maps=[]
for x in orbit:
 d=dict(z.split('->') for z in x['mapping'].split('|'));maps.append([targets.index(d[s]) for s in sources])
true_i=next(i for i,x in enumerate(orbit) if x['is_true']=='1')
swap_i=next(i for i,q in enumerate(maps) if q==[0,1,4,3,2])

m=np.zeros((5,5),float)
for x in pairs:
 if x['representation']=='PAGE_HOST_CHAR3':m[sources.index(x['source_page']),targets.index(x['candidate_target_page'])]=float(x['similarity'])
sr=np.stack([ranks(m[i,:]) for i in range(5)]);tr=np.stack([ranks(m[:,j]) for j in range(5)]).T
nm={'RAW_SIMILARITY':m,'SOURCE_RANK':(6-sr)/5,'TARGET_RANK':(6-tr)/5,'MUTUAL_RANK_MEAN':((6-sr)+(6-tr))/10,'RECIPROCAL_RANK_MEAN':.5*(1/sr+1/tr),'MUTUAL_TOP2':((sr<=2)&(tr<=2)).astype(float)}

best_rows=[];swap_rows=[];best_mass=np.zeros(5);top5_mass=np.zeros(5);any_best=np.zeros(5,int);all_best=np.zeros(5,int)
for norm in NORMS:
 vals=np.array([sum(nm[norm][i,j] for i,j in enumerate(q))/5 for q in maps])
 mx=float(vals.max());best_ids=[i for i,v in enumerate(vals) if abs(v-mx)<=1e-12]
 order=sorted(range(120),key=lambda i:(-vals[i],orbit[i]['assignment_id']));top5=order[:5]
 for i in range(5):
  mass=sum(maps[k][i]==i for k in best_ids)/len(best_ids);tm=sum(maps[k][i]==i for k in top5)/5
  best_mass[i]+=mass/6;top5_mass[i]+=tm/6;any_best[i]+=int(mass>0);all_best[i]+=int(mass==1)
 best_rows.append({'normalization':norm,'best_score':mx,'tied_best_count':len(best_ids),'best_assignment_ids':'|'.join(orbit[i]['assignment_id'] for i in best_ids),'best_mappings':' || '.join(orbit[i]['mapping'] for i in best_ids),'true_assignment_score':float(vals[true_i]),'true_rank_of_120':1+int(np.sum(vals>vals[true_i]+1e-12)),'true_score_gap_from_best':mx-float(vals[true_i]),'top5_assignment_ids':'|'.join(orbit[i]['assignment_id'] for i in top5)})
 delta=float(vals[true_i]-vals[swap_i])
 swap_rows.append({'normalization':norm,'true_assignment_id':orbit[true_i]['assignment_id'],'swapped_assignment_id':orbit[swap_i]['assignment_id'],'true_score':float(vals[true_i]),'swapped_score':float(vals[swap_i]),'true_minus_swapped':delta,'winner':'TRUE' if delta>1e-12 else 'SWAPPED' if delta < -1e-12 else 'TIE'})

edge_rows=[]
for i,x in enumerate(rels):
 stable=best_mass[i]>=.75 and top5_mass[i]>=.60
 edge_rows.append({'relation_id':x['relation_id'],'source_page':x['source_page'],'target_page':x['target_page'],'relation_class':x['relation_class'],'component':x['component'],'best_assignment_inclusion_mass':float(best_mass[i]),'top5_inclusion_mass':float(top5_mass[i]),'normalizations_with_any_best_inclusion':int(any_best[i]),'normalizations_with_all_best_inclusion':int(all_best[i]),'descriptive_class':'STABLE_BACKBONE_EDGE' if stable else 'EXCHANGEABLE_OR_UNSTABLE_EDGE'})

stable=[x['relation_id'] for x in edge_rows if x['descriptive_class']=='STABLE_BACKBONE_EDGE']
unstable=[x['relation_id'] for x in edge_rows if x['descriptive_class']!='STABLE_BACKBONE_EDGE']
counter=[
 {'type':'EXPOSED_POSTHOC_LOCALIZATION','item':'GDT140_5X5','value':'NA','detail':'The edge-stability statistic and threshold were chosen after inspecting the published assignment geometry; they are descriptive.'},
 {'type':'TWO_TARGET_SWAP_PREFERRED','item':'MHI004_MHI007','value':sum(x['winner']=='SWAPPED' for x in swap_rows),'detail':'The assignment swapping the leaf and bulb targets beats the human mapping under five of six normalizations and ties under one.'},
 {'type':'CORPUS_WIDE_RETRIEVAL_FAILURE','item':'GDT144','value':'MAX4_P_0.36544','detail':'The partial O/OT PAGE_HOST view did not retrieve four covered targets manuscript-wide.'},
 {'type':'UBIQUITOUS_HOST_COUNTEREXAMPLE','item':'MHI004','value':'L_ON_84_OF_93_PAGES','detail':'The only apparent corpus-wide MHI004 lead was explained by the ubiquitous one-character host l in GDT145.'},
 {'type':'NO_ALTERNATE_READING_REPLICATION','item':'GDT062_DERIVED_VIEW','value':'NA','detail':'PAGE_HOST bags come from one derived source-display view; no ZL/IT/RF replication is claimed.'},
]
write(EDGES,clean(edge_rows));write(BEST,clean(best_rows));write(SWAP,clean(swap_rows));write(COUNTER,counter)
status='PAGE_HOST_CHAR3_THREE_EDGE_BACKBONE_TWO_TARGETS_EXCHANGEABLE' if stable==['MHI002','MHI003','MHI006'] and unstable==['MHI004','MHI007'] else 'PAGE_HOST_CHAR3_EDGE_STABILITY_DIFFUSE'
REPORT.write_text(f"""# GDT147 — relation-backbone stability

## Outcome

**{status}**

The five-pair PAGE_HOST-character-trigram assignment does not behave as five equally supported edges. Three human-paired relations form a stable descriptive backbone across the six already-published GDT142 normalizations: `{'`, `'.join(stable)}`. Their best-assignment inclusion masses are {', '.join(f'{x["best_assignment_inclusion_mass"]:.3f}' for x in edge_rows if x['relation_id'] in stable)}.

`MHI004` and `MHI007` are exchangeable. The assignment that keeps the other three edges and swaps only their targets beats the human mapping under five normalizations and ties it under one. Their best-assignment inclusion masses are each {edge_rows[2]['best_assignment_inclusion_mass']:.3f}; the matrix therefore does not support interpreting the leaf and bulb edges individually. The raw-similarity score difference is only {abs(float(swap_rows[0]['true_minus_swapped'])):.6f}, but the direction is consistent across the rank-based variants.

This sharpens rather than extends GDT140: the candidate-pool signal is concentrated in the whole-plant pairs MHI002/MHI003 and the flower pair MHI006, while two component pairings remain unresolved. It remains wholly post-hoc and conditional on the five exposed targets. GDT144 still shows that a partial O/OT host view does not retrieve these partners corpus-wide, and GDT145 explains the sole apparent top-decile exception by an ubiquitous one-character host.

No transcription source or image was opened, and f84r remains untouched. This result establishes no botanical truth, plant/component identity, semantic role, gloss, word, morpheme, part of speech, sound, language, plaintext, meaning, or translation.
""",encoding='utf8')

result={'schema':'GDT147_RELATION_BACKBONE_STABILITY_RESULT_V1','status':status,'relations':5,'normalizations':list(NORMS),'assignment_worlds':120,'stable_backbone_edges':stable,'exchangeable_or_unstable_edges':unstable,'true_vs_swap':{'true_assignment_id':orbit[true_i]['assignment_id'],'swapped_assignment_id':orbit[swap_i]['assignment_id'],'swapped_wins':sum(x['winner']=='SWAPPED' for x in swap_rows),'ties':sum(x['winner']=='TIE' for x in swap_rows),'true_wins':sum(x['winner']=='TRUE' for x in swap_rows)},'edge_stability':edge_rows,'interpretation':'Post-hoc localization of the exposed PAGE_HOST-character-trigram assignment into a three-edge backbone and two exchangeable targets.','claim_ceiling':'Exposed five-target edge stability only; no botanical truth, identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84':{'published_derived_inputs_have_zero_f84_pages':True,'source_or_image_opened':False,'new_f84r_access':False},'inputs':{p.name:sha(p) for p in (INV,PAIR,ORBIT,P140,P142,P144,P145)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (EDGES,BEST,SWAP,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
print(json.dumps({'status':status,'stable':stable,'swapped_wins':result['true_vs_swap']['swapped_wins']},sort_keys=True))
