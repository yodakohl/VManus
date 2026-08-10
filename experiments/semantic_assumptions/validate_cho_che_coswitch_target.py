#!/usr/bin/env python3
"""Production-free reconstruction of the single co-switch target."""
from __future__ import annotations
import csv,hashlib,json,os,tempfile
from collections import defaultdict
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import numpy as np
from validate_cho_che_coswitch_synthetic_preflight_v2 import evaluate
B=Path(__file__).resolve().parent;R=B/'results';SELF=Path(__file__).resolve();P=R/'cho_che_coswitch_masked_panel.tsv';S=R/'source_sta_group_alignment.tsv';T=R/'cho_che_coswitch_target.json';TR=R/'cho_che_coswitch_target_report.md';OUT=R/'cho_che_coswitch_target_validation.json';REPORT=R/'cho_che_coswitch_target_validation_report.md'
HASH={P:'25ae579c3f122f188089edc8fd2e0f617194bf6240cb20570d9aff881f80e003',S:'f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840',T:'c8b1fe3ed6644e2063e4c4d2c4e72f272b5e98dc7ddca09fe3aaded5e0a72914',TR:'85e98d728e262cd0fd948ef1899bf915be27983043ac24ae4405aa9df3434c26',B/'run_cho_che_coswitch_target.py':'6088a73912e8ad888f56ffa0663ad9500c662b1fc7d6917f040c0278d9ba1f9d',B/'CHO_CHE_COSWITCH_TARGET_SPEC.md':'d834e5049a4dcba5d49e3b6c391ea3335a586e50436e18e525b86502b2c4ba13',B/'validate_cho_che_coswitch_synthetic_preflight_v2.py':'010cb7f6da3af88f879c441482121d562b948a100910bfabc825036870e6270e'}
E=('ZL3b','IT2a','RF1b');L=('f39','f55','f68','f73','f87','f89','f90','f96');BLOCK=('FAMILY_RATE','ENDPOINT_RATE','BIGRAM_RATE');DIM=(24,48,576);A=tuple('ABCDEFGHJKLMNPQRSTUVWXYZ');NU=('section','currier','hand','kind','grammar_scope','primary_sta_symbol_count','page_position_quartile','group_position_class')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def feat(s,b,idx):
 if b==0:
  z=np.zeros(24);np.add.at(z,[idx[x] for x in s],1);return z/len(s)
 if b==1:
  z=np.zeros(48);z[idx[s[0]]]=1;z[24+idx[s[-1]]]=1;return z
 z=np.zeros(576)
 for x,y in zip(s,s[1:]):z[idx[x]*24+idx[y]]+=1
 return z/(len(s)-1)
def install(a,b):
 if OUT.exists() or REPORT.exists():raise FileExistsError
 with tempfile.TemporaryDirectory(prefix='ccswtval_',dir=R) as d:
  x,y=Path(d)/'j',Path(d)/'m';x.write_bytes(a);y.write_bytes(b);os.link(x,OUT)
  try:os.link(y,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 checks=[]
 for p,h in HASH.items():
  if sha(p)!=h:raise AssertionError('hash '+p.name)
  checks.append('hash:'+p.name)
 actual=json.loads(T.read_text());rows=list(csv.DictReader(P.open(),delimiter='\t'));wanted={r['source_group_id'] for r in rows};seq={};length={};alt={};n=0
 with S.open(encoding='utf-8',newline='') as h:
  for r in csv.DictReader(h,delimiter='\t'):
   n+=1
   if r['source_group_id'] in wanted:seq[r['source_group_id']]=r['primary_sta_families'];length[r['source_group_id']]=int(r['primary_sta_symbol_count']);alt[r['source_group_id']]=int(r['alternative_site_count'])
 if n!=115470 or set(seq)!=wanted or len(seq)!=5012 or any(alt.values()):raise AssertionError('join')
 checks+=['source_rows','join','zero_alternatives'];idx={x:i for i,x in enumerate(A)};g=defaultdict(list)
 for r in rows:
  s=seq[r['source_group_id']]
  if len(s)!=length[r['source_group_id']] or len(s)!=int(r['primary_sta_symbol_count']):raise AssertionError('length')
  g[r['edition'],r['physical_folio'],r['side'],tuple(r[k] for k in NU)].append((r,s))
 vectors=[];cells={}
 for bi,d in enumerate(DIM):
  z=np.zeros((3,8,d))
  for ei,e in enumerate(E):
   for li,l in enumerate(L):
    rset={k[3] for k,v in g.items() if k[:3]==(e,l,'r') and len(v)>=2};vset={k[3] for k,v in g.items() if k[:3]==(e,l,'v') and len(v)>=2};common=sorted(rset&vset)
    if bi==2:common=[c for c in common if int(c[5])>=2]
    dif=[]
    for c in common:
     q=defaultdict(list)
     for side in 'rv':
      for r,s in g[e,l,side,c]:q[int(r['page_state'])].append(feat(s,bi,idx))
     dif.append(np.mean(q[1],0)-np.mean(q[0],0))
    z[ei,li]=np.mean(dif,0);cells[BLOCK[bi],e,l]=len(common)
  vectors.append(z)
 score=evaluate(tuple(vectors));score['v1_passes']=score.pop('v1_passes')
 if score!=actual['score']:raise AssertionError('score')
 checks.append('score')
 hashes={BLOCK[bi]:{E[ei]:hashlib.sha256(np.asarray(vectors[bi][ei],dtype='<f8').tobytes()).hexdigest() for ei in range(3)} for bi in range(3)}
 if hashes!=actual['vector_hashes']:raise AssertionError('vector hashes')
 if {b:{e:{l:cells[b,e,l] for l in L} for e in E} for b in BLOCK}!=actual['used_cell_counts']:raise AssertionError('cells')
 checks+=['vector_hashes','cell_counts']
 if actual['status']!='NONCONFIRM_DISTRIBUTED_OFFSITE_CHO_CHE_SYSTEM_STATE' or actual['decision']!='REJECT_BROAD_COSWITCH_AUTHORIZE_CANONICALIZED_FORM_TEST' or actual['score']['passes']:raise AssertionError('decision')
 checks.append('decision')
 result={'experiment':'CHO_CHE_COSWITCH_TARGET_VALIDATION','status':'PASS_PRODUCTION_FREE_COSWITCH_NONCONFIRMATION_RECONSTRUCTION','checks_passed':len(checks),'inputs':{p.name:sha(p) for p in (*HASH,SELF)},'source_rows':n,'joined_groups':len(seq),'score':score,'vector_hashes':hashes,'decision':actual['decision'],'event_sequences_stored':0,'english_glosses':0,'claim_ceiling':'Validation confirms only the broad off-site co-switch nonconfirmation and supplies no meaning sound wordhood language cipher plaintext or translation.'}
 report=f"# `cho/che` independent co-switch target validation\n\n**PASS**: {len(checks)} checks reconstruct all 5,012 joins, three feature blocks, vector hashes, exact score, and the broad-system nonconfirmation without importing the target runner or scoring cores.\n";install((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),report.encode());print(json.dumps({'status':result['status'],'checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
