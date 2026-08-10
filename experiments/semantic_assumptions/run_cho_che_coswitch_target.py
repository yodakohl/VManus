#!/usr/bin/env python3
"""Execute the single frozen cho/che independent co-switch target."""
from __future__ import annotations
import csv,hashlib,json,os,tempfile
from collections import Counter,defaultdict
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
B=Path(__file__).resolve().parent;R=B/'results';RUNNER=Path(__file__).resolve();PANEL=R/'cho_che_coswitch_masked_panel.tsv';SOURCE=R/'source_sta_group_alignment.tsv';SOURCE_VALIDATION=R/'source_sta_group_alignment_validation.json';SPEC=B/'CHO_CHE_COSWITCH_TARGET_SPEC.md';METHOD=B/'CHO_CHE_COSWITCH_SYNTHETIC_PREFLIGHT_SPEC.md';CORE1=B/'cho_che_coswitch_core.py';CORE2=B/'cho_che_coswitch_core_v2.py';CAP=R/'cho_che_coswitch_capacity_v2.json';CAPV=R/'cho_che_coswitch_capacity_validation.json';PRE=R/'cho_che_coswitch_synthetic_preflight_v2.json';PREV=R/'cho_che_coswitch_synthetic_preflight_v2_validation.json';OUT=R/'cho_che_coswitch_target.json';REPORT=R/'cho_che_coswitch_target_report.md'
EXPECTED={PANEL:'25ae579c3f122f188089edc8fd2e0f617194bf6240cb20570d9aff881f80e003',SOURCE:'f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840',SOURCE_VALIDATION:'cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd',SPEC:'d834e5049a4dcba5d49e3b6c391ea3335a586e50436e18e525b86502b2c4ba13',METHOD:'aa75c979b7a7d4d6a1ed86973ce47101cdcc4d73ff1595af5c2fd84f7a810186',CORE1:'a1f246f7c25318eb7c54c393425d939f4ef5755df066732716322aa1b214602d',CORE2:'34e53d843c70e1f4fe68b9d9ec8cd1c1da1433a501b5f554b526b77be513dae5',CAP:'c32a6dc5456a59f469de1f8d47d95fba8e6384d60ecccd678adb678c0382b775',CAPV:'68bf07fa2fcaf5437fd5240ac394b4c20add24d4867eb3b3ac846378b0809d73',PRE:'d7906941588b8f8b8792a2809e64a3288db578eb272c9803cc0930190c011d37',PREV:'925f9e5adc17ab7173f35412bc62c13f99e75652d453a54ac72d2b7dbcfbd19b'}
NU=('section','currier','hand','kind','grammar_scope','primary_sta_symbol_count','page_position_quartile','group_position_class');ALPH=tuple('ABCDEFGHJKLMNPQRSTUVWXYZ')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def install(a,b):
 if OUT.exists() or REPORT.exists():raise FileExistsError('target exists')
 with tempfile.TemporaryDirectory(prefix='ccswtarget_',dir=R) as d:
  x,y=Path(d)/'j',Path(d)/'m';x.write_bytes(a);y.write_bytes(b)
  if OUT.exists() or REPORT.exists():raise FileExistsError('target appeared')
  os.link(x,OUT)
  try:os.link(y,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing second target')
 for p,h in EXPECTED.items():
  if sha(p)!=h:raise SystemExit(f'hash {p.name}')
 if json.loads(SOURCE_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_SOURCE_STA_ALIGNMENT_RECONSTRUCTION':raise SystemExit('source validation')
 if json.loads(CAPV.read_text())['status']!='PASS_INDEPENDENT_SCORE_BLIND_COSWITCH_CAPACITY_RECONSTRUCTION':raise SystemExit('capacity validation')
 pre=json.loads(PRE.read_text());pv=json.loads(PREV.read_text())
 if pre['status']!='PASS_TARGET_FREE_CHO_CHE_COSWITCH_PREFLIGHT_V2' or not all(pre['gates'].values()) or pv['status']!='PASS_INDEPENDENT_136_WORLD_BLOCKWISE_RECONSTRUCTION':raise SystemExit('preflight')
 import numpy as np
 from cho_che_coswitch_core import BLOCKS,BLOCK_DIMS,LEAVES,READINGS
 from cho_che_coswitch_core_v2 import compact,score
 rows=list(csv.DictReader(PANEL.open(),delimiter='\t'))
 if len(rows)!=5012 or len({r['source_group_id'] for r in rows})!=len(rows):raise ValueError('panel')
 wanted={r['source_group_id'] for r in rows};seq={};alts={};lengths={};source_rows=0
 with SOURCE.open(encoding='utf-8',newline='') as h:
  rd=csv.DictReader(h,delimiter='\t')
  for r in rd:
   source_rows+=1;uid=r['source_group_id']
   if uid in wanted:
    if uid in seq:raise ValueError('duplicate source')
    seq[uid]=r['primary_sta_families'];alts[uid]=int(r['alternative_site_count']);lengths[uid]=int(r['primary_sta_symbol_count'])
 if set(seq)!=wanted or any(alts.values()):raise ValueError('join')
 index={x:i for i,x in enumerate(ALPH)};grouped=defaultdict(list)
 for r in rows:
  s=seq[r['source_group_id']]
  if len(s)!=lengths[r['source_group_id']] or len(s)!=int(r['primary_sta_symbol_count']) or any(x not in index for x in s):raise ValueError('sequence')
  cell=tuple(r[k] for k in NU);grouped[r['edition'],r['physical_folio'],r['side'],cell].append((r,s))
 def features(s,block):
  if block==0:
   z=np.zeros(24);np.add.at(z,[index[x] for x in s],1);return z/len(s)
  if block==1:
   z=np.zeros(48);z[index[s[0]]]=1;z[24+index[s[-1]]]=1;return z
  z=np.zeros(576)
  for a,b in zip(s,s[1:]):z[index[a]*24+index[b]]+=1
  return z/(len(s)-1)
 vectors=[];used_cells={};used_rows=Counter()
 for bi,dim in enumerate(BLOCK_DIMS):
  block=np.zeros((3,8,dim))
  for ei,e in enumerate(READINGS):
   for li,l in enumerate(LEAVES):
    a={k[3] for k,v in grouped.items() if k[:3]==(e,l,'r') and len(v)>=2};b={k[3] for k,v in grouped.items() if k[:3]==(e,l,'v') and len(v)>=2};cells=sorted(a&b)
    if bi==2:cells=[c for c in cells if int(c[5])>=2]
    diffs=[]
    for c in cells:
     bystate=defaultdict(list)
     for side in 'rv':
      for r,s in grouped[e,l,side,c]:bystate[int(r['page_state'])].append(features(s,bi));used_rows[bi,e,l,side]+=1
     if set(bystate)!={0,1}:raise ValueError('state cell')
     diffs.append(np.mean(bystate[1],axis=0)-np.mean(bystate[0],axis=0))
    if not diffs:raise ValueError('empty block cells')
    block[ei,li]=np.mean(diffs,axis=0);used_cells[BLOCKS[bi],e,l]=len(cells)
  vectors.append(block)
 value=compact(score(tuple(vectors)));passed=value['passes'];status='CONFIRM_DISTRIBUTED_OFFSITE_CHO_CHE_SYSTEM_STATE' if passed else 'NONCONFIRM_DISTRIBUTED_OFFSITE_CHO_CHE_SYSTEM_STATE';decision='RETAIN_BROADER_FORMAL_PAGE_SIDE_SYSTEM_STATE' if passed else 'REJECT_BROAD_COSWITCH_AUTHORIZE_CANONICALIZED_FORM_TEST'
 vector_hashes={BLOCKS[bi]:{READINGS[e]:hashlib.sha256(np.asarray(vectors[bi][e],dtype='<f8').tobytes()).hexdigest() for e in range(3)} for bi in range(3)}
 gates={'exact_115470_source_rows':source_rows==115470,'exact_5012_join':len(seq)==5012,'zero_alternatives':not any(alts.values()),'exact_272_family_endpoint_cells':sum(v for (b,e,l),v in used_cells.items() if b=='FAMILY_RATE')==272 and sum(v for (b,e,l),v in used_cells.items() if b=='ENDPOINT_RATE')==272,'finite_vectors':all(np.isfinite(x).all() for x in vectors),'target_gate':passed,'event_sequences_stored_zero':True,'english_glosses_zero':True}
 result={'experiment':'CHO_CHE_COSWITCH_TARGET','status':status,'decision':decision,'inputs':{p.name:sha(p) for p in (*EXPECTED,RUNNER)},'source_rows_accessed':source_rows,'joined_groups':len(seq),'score':value,'vector_hashes':vector_hashes,'used_cell_counts':{b:{e:{l:used_cells[b,e,l] for l in LEAVES} for e in READINGS} for b in BLOCKS},'gates':gates,'target_source_opened':True,'target_family_sequences_accessed':len(seq),'target_associations_computed':1,'event_level_sequences_stored':0,'event_level_vectors_stored':0,'english_glosses':0,'claim_ceiling':'A pass establishes only a distributed held-leaf direction in at least two off-site formal feature blocks beyond the defining cho/che construction. A failure rejects only that broad model and permits a canonicalized-form test. Neither result supplies meaning sound wordhood language cipher plaintext or translation.'}
 report=f'''# `cho/che` independent co-switch target\n\nStatus: **{status}**\n\nThe single frozen run joined **{len(seq):,}** strict off-site source groups. Minimum-reading combined alignment is **{value['primary']:+.6f}**, exact synchronous p **{value['p_value']:.6f}**, and exact independently passing feature blocks **{value['exact_block_passes']}/3**. Held-leaf positives by reading are **{value['positive_held']}**; cross-orientation cosines are **{[round(x,6) for x in value['orientation_cross']]}** and prose/diagnostic cross-cosines **{[round(x,6) for x in value['domain_cross']]}**.\n\nDecision: **{decision}**. No event sequence or vector is stored. This supplies no meaning, sound, wordhood, language, cipher, plaintext, or translation.\n'''
 install((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),report.encode());print(json.dumps({'status':status,'decision':decision,'score':value,'gates':gates},sort_keys=True))
if __name__=='__main__':main()
