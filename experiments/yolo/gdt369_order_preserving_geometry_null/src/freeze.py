#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,itertools,json,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt369_order_preserving_geometry_null';ART=EXP/'artifacts';G=ROOT/'experiments/yolo/gdt368_quantitative_component_geometry/artifacts';PANEL=G/'gdt368_formal_panel.tsv';FEATURES=G/'gdt368_feature_manifest.tsv';ATLAS=G/'gdt368_candidate_atlas.tsv';RESULT=G/'gdt368_result.json';OUT=ART/'gdt369_freeze.json'
def main():
 ART.mkdir(parents=True,exist_ok=True)
 with PANEL.open(newline='') as h:r=list(csv.DictReader(h,delimiter='\t'))
 orbits={}
 for e in ('major_body_count','terminal_arm_count','dominant_hue'):
  total=1
  for a in sorted({x['array_id'] for x in r}):
   y=[x[e] for x in r if x['array_id']==a];adj=sum(y[i]==y[i-1] for i in range(1,len(y)));q={p for p in itertools.permutations(y) if sum(p[i]==p[i-1] for i in range(1,len(p)))==adj};total*=len(q)
  orbits[e.upper()]=total
 assert orbits=={'MAJOR_BODY_COUNT':1040,'TERMINAL_ARM_COUNT':8640,'DOMINANT_HUE':120}
 p={'schema':'GDT369_FREEZE_V1','status':'POSTEXPOSURE_DIAGNOSTIC_FROZEN_BEFORE_RESCORING','panel_rows':27,'frozen_mask_count':27,'fixed_candidate':{'endpoint':'TERMINAL_ARM_COUNT','formal_feature':'FAMILY_3GRAM:ACA'},'adjacency_matched_exact_orbits':orbits,'global_sample_worlds':4096,'reversal_sensitivity':True,'feature_or_endpoint_reselection':False,'f84_accessed':False,'inputs':{str(x.relative_to(ROOT)):sha256_file(x) for x in (PANEL,FEATURES,ATLAS,RESULT,EXP/'METHOD.md')},'implementation':{str(Path(__file__).relative_to(ROOT)):sha256_file(Path(__file__))},'claim_ceiling':'ORDER_ROBUSTNESS_DIAGNOSTIC_OF_FIXED_GDT368_ASSOCIATION_ONLY'};p['content_hash']=hashlib.sha256(canonical_json_bytes(p)).hexdigest();OUT.write_bytes(canonical_json_bytes(p))
if __name__=='__main__':main()
