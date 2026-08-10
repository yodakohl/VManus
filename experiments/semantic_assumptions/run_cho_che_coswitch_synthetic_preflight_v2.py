#!/usr/bin/env python3
"""Run the blockwise-intersection v2 co-switch synthetic preflight."""

from __future__ import annotations
import hashlib,json,os,tempfile
from pathlib import Path
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";RUNNER=Path(__file__).resolve()
PANEL=RESULTS/"cho_che_coswitch_masked_panel.tsv";V1=RESULTS/"cho_che_coswitch_synthetic_preflight.json";V1_REPORT=RESULTS/"cho_che_coswitch_synthetic_preflight_report.md"
AMENDMENT=BASE/"CHO_CHE_COSWITCH_SYNTHETIC_PREFLIGHT_V2_AMENDMENT.md";CORE1=BASE/"cho_che_coswitch_core.py";CORE2=BASE/"cho_che_coswitch_core_v2.py";FIXTURE=BASE/"cho_che_coswitch_fixture.py"
OUT=RESULTS/"cho_che_coswitch_synthetic_preflight_v2.json";REPORT=RESULTS/"cho_che_coswitch_synthetic_preflight_v2_report.md"
TARGETS=(RESULTS/"cho_che_coswitch_target.json",RESULTS/"cho_che_coswitch_target_report.md",RESULTS/"cho_che_coswitch_target_validation.json",RESULTS/"cho_che_coswitch_target_validation_report.md")
EXPECTED={PANEL:"25ae579c3f122f188089edc8fd2e0f617194bf6240cb20570d9aff881f80e003",V1:"d82a6a2cc0ac10c6f5eab3bc3b425ee30cd0759c4277e74b86a49373bd8f7f9e",V1_REPORT:"e89af1897fd624ff6b1bee0819ecfec101c04ea75140607ef078f0e7e5da0397",AMENDMENT:"a306f3342b80a57f6f8ccbb11e3caebd54f708b36f188a5ec46228e265995acf",CORE1:"a1f246f7c25318eb7c54c393425d939f4ef5755df066732716322aa1b214602d",CORE2:"34e53d843c70e1f4fe68b9d9ec8cd1c1da1433a501b5f554b526b77be513dae5",FIXTURE:"3b79e60770d67cee7e43506fef00a9d95de1abf24d0a1f79bf4c81ad80b06ce4"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def install(a,b):
 if OUT.exists() or REPORT.exists():raise FileExistsError('v2 exists')
 with tempfile.TemporaryDirectory(prefix='cho_che_coswitch_v2_',dir=RESULTS) as d:
  x,y=Path(d)/'j',Path(d)/'m';x.write_bytes(a);y.write_bytes(b)
  if OUT.exists() or REPORT.exists():raise FileExistsError('v2 appeared')
  os.link(x,OUT)
  try:os.link(y,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 absent_before={p.name:not p.exists() for p in TARGETS}
 if not all(absent_before.values()):raise SystemExit('target exists')
 for p,h in EXPECTED.items():
  if sha(p)!=h:raise SystemExit(f'hash {p.name}')
 old=json.loads(V1.read_text())
 if old['status']!='STOP_CHO_CHE_COSWITCH_PREFLIGHT' or old['pass_counts']['ONE_BLOCK']!=2:raise ValueError('v1 binding')
 import numpy as np
 from cho_che_coswitch_fixture import FAMILIES,geometry,make_world
 from cho_che_coswitch_core_v2 import compact,score
 scale,shared,side_rows=geometry(PANEL);records={};counts={};base_matches=0
 for family,(count,strength) in FAMILIES.items():
  values=[]
  for world in range(count):
   record={'world':world,**compact(score(make_world(scale,family,world,strength)))};values.append(record)
   prior=dict(record);prior['passes']=prior.pop('v1_passes')
   for key in ('block_primary','block_p_value','exact_block_passes'):prior.pop(key)
   if prior!=old['worlds'][family][world]:raise ValueError(f'v1 world mismatch {family} {world}')
   base_matches+=1
  records[family]=values;counts[family]=sum(v['passes'] for v in values)
 fixture=make_world(scale,'DISTRIBUTED_THREE_BLOCK',0,.75);a=compact(score(fixture));b=compact(score(tuple(-x for x in fixture)))
 mutations={}
 for name,fn in {'wrong_count':lambda:score(fixture[:2]),'wrong_shape':lambda:score((fixture[0][:,:7],fixture[1],fixture[2])),'zero':lambda:score((np.zeros_like(fixture[0]),fixture[1],fixture[2])),'nan':lambda:score((np.full_like(fixture[0],np.nan),fixture[1],fixture[2]))}.items():
  try:fn()
  except (ValueError,IndexError,FloatingPointError):mutations[name]=True
  else:mutations[name]=False
 absent_after={p.name:not p.exists() for p in TARGETS}
 adversarial=[x for x in FAMILIES if x not in {'NULL','DISTRIBUTED_THREE_BLOCK','DISTRIBUTED_TWO_BLOCK'}]
 gates={'v1_all_136_worlds_exactly_reconstructed':base_matches==136,'null_at_most_one_of_64':counts['NULL']<=1,'three_block_power_at_least_seven_of_eight':counts['DISTRIBUTED_THREE_BLOCK']>=7,'two_block_power_at_least_seven_of_eight':counts['DISTRIBUTED_TWO_BLOCK']>=7,'all_adversarial_controls_zero':all(counts[x]==0 for x in adversarial),'one_block_exactly_zero_of_eight':counts['ONE_BLOCK']==0,'complement_invariance':a==b,'all_mutations_rejected':all(mutations.values()),'geometry_exact':len(shared)==24 and sum(map(len,shared.values()))==272 and sum(side_rows.values())==2730 and min(side_rows.values())==9,'finite':all(np.isfinite(v[k]).all() for vv in records.values() for v in vv for k in ('primary','p_value','reading_alignment','min_deletion','orientation_cross','domain_cross','reading_agreement','max_concentration','block_primary','block_p_value')),'target_absent_before':all(absent_before.values()),'target_absent_after':all(absent_after.values()),'target_sequences_accessed_zero':True,'english_glosses_zero':True}
 passed=all(gates.values());status='PASS_TARGET_FREE_CHO_CHE_COSWITCH_PREFLIGHT_V2' if passed else 'STOP_CHO_CHE_COSWITCH_PREFLIGHT_V2';decision='AUTHORIZE_ONE_FROZEN_COSWITCH_TARGET' if passed else 'TARGET_FORBIDDEN_CLOSE_COSWITCH_ROUTE'
 result={'experiment':'CHO_CHE_COSWITCH_SYNTHETIC_PREFLIGHT_V2','status':status,'decision':decision,'inputs':{p.name:sha(p) for p in (*EXPECTED,RUNNER)},'pass_counts':counts,'worlds':records,'controls':{'v1_worlds_reconstructed':base_matches,'complement_invariant':a==b,'mutation_rejections':mutations},'geometry':{'shared_nuisance_cells':sum(map(len,shared.values())),'retained_group_rows':sum(side_rows.values()),'minimum_leaf_side_rows':min(side_rows.values()),'noise_scale_sha256':hashlib.sha256(np.asarray(scale,dtype='<f8').tobytes()).hexdigest()},'gates':gates,'target_absence_before':absent_before,'target_absence_after':absent_after,'target_family_sequences_accessed':0,'target_associations_computed':0,'english_glosses':0,'claim_ceiling':'A pass validates only a blockwise-intersection synthetic scorer on the frozen eight-leaf geometry. It supplies no manuscript co-switch result meaning sound wordhood language cipher plaintext or translation.'}
 report=f'''# `cho/che` independent co-switch synthetic preflight v2\n\nStatus: **{status}**\n\nThe stricter blockwise-intersection scorer exactly reconstructs all **{base_matches}** v1 worlds. Pass counts are null **{counts['NULL']}/64**, distributed three-block **{counts['DISTRIBUTED_THREE_BLOCK']}/8**, distributed two-block **{counts['DISTRIBUTED_TWO_BLOCK']}/8**, and one-block **{counts['ONE_BLOCK']}/8**. All other adversarial controls total **{sum(counts[x] for x in adversarial if x!='ONE_BLOCK')}** passes.\n\nDecision: **{decision}**. No target family sequence or manuscript feature/state association was opened. This supplies no co-switch result, meaning, sound, wordhood, language, cipher, plaintext, or translation.\n'''
 install((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),report.encode());print(json.dumps({'status':status,'decision':decision,'pass_counts':counts,'gates':gates},sort_keys=True))
 if not passed:raise SystemExit(2)
if __name__=='__main__':main()
