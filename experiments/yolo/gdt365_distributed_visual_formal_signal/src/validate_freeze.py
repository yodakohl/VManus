#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt365_distributed_visual_formal_signal';P=EXP/'artifacts/gdt365_freeze.json'
def main():
 p=json.loads(P.read_text());q=dict(p);d=q.pop('content_hash');checks=[p['dimensions']==[2,4,8],p['max_family']==6,p['null_worlds']==1024,p['postexposure'] is True,p['pharma_local_overlap_capacity']=={'contact_x_root_color':2,'flower_count_x_root_color':7,'model_run':False,'root_color_x_root_leaf':6},not p['access']['f84_accessed'],all(sha256_file(ROOT/k)==v for k,v in p['inputs'].items()),all(sha256_file(ROOT/k)==v for k,v in p['implementation'].items()),hashlib.sha256(canonical_json_bytes(q)).hexdigest()==d];assert all(checks);print(f'PASS {sum(checks)}/{len(checks)}')
if __name__=='__main__':main()
