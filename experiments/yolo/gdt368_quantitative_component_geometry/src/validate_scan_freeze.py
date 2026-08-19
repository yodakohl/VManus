#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
P=ROOT/'experiments/yolo/gdt368_quantitative_component_geometry/artifacts/gdt368_scan_freeze.json'
def main():
 p=json.loads(P.read_text());q=dict(p);d=q.pop('content_hash');c=[p['target_count']==27,p['endpoints']==['MAJOR_BODY_COUNT','TERMINAL_ARM_COUNT','DOMINANT_HUE'],p['worlds']==4096,p['support_min']==p['absence_min']==4,p['folio_support_min_each_state']==2,p['formal_channel']=='CONTACT_GAP',not p['formal_access_before_freeze'],p['post_image_selection'],not p['f84_accessed'],all(sha256_file(ROOT/k)==v for k,v in p['inputs'].items()),all(sha256_file(ROOT/k)==v for k,v in p['implementation'].items()),hashlib.sha256(canonical_json_bytes(q)).hexdigest()==d];assert all(c);print(f'PASS {sum(c)}/{len(c)}')
if __name__=='__main__':main()
