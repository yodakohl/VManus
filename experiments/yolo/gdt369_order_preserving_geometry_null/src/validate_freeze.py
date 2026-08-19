#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
P=ROOT/'experiments/yolo/gdt369_order_preserving_geometry_null/artifacts/gdt369_freeze.json'
def main():
 p=json.loads(P.read_text());q=dict(p);d=q.pop('content_hash');c=[p['panel_rows']==p['frozen_mask_count']==27,p['fixed_candidate']=={'endpoint':'TERMINAL_ARM_COUNT','formal_feature':'FAMILY_3GRAM:ACA'},p['adjacency_matched_exact_orbits']=={'MAJOR_BODY_COUNT':1040,'TERMINAL_ARM_COUNT':8640,'DOMINANT_HUE':120},p['global_sample_worlds']==4096,p['reversal_sensitivity'],not p['feature_or_endpoint_reselection'],not p['f84_accessed'],all(sha256_file(ROOT/k)==v for k,v in p['inputs'].items()),all(sha256_file(ROOT/k)==v for k,v in p['implementation'].items()),hashlib.sha256(canonical_json_bytes(q)).hexdigest()==d];assert all(c);print(f'PASS {sum(c)}/{len(c)}')
if __name__=='__main__':main()
