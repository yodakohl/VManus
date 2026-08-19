#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
P=ROOT/'experiments/yolo/gdt366_matched_reproductive_delta/artifacts/gdt366_freeze.json'
def main():
 p=json.loads(P.read_text());q=dict(p);d=q.pop('content_hash');c=[p['feature_manifest_count']==227,[x['physical_folio'] for x in p['primary_pairs']]==['f4','f17'],p['secondary_unscored_contrast']['physical_folio']=='f8',p['postexposure'],not p['access']['f84_accessed'],all(sha256_file(ROOT/k)==v for k,v in p['inputs'].items()),all(sha256_file(ROOT/k)==v for k,v in p['implementation'].items()),hashlib.sha256(canonical_json_bytes(q)).hexdigest()==d];assert all(c);print(f'PASS {sum(c)}/{len(c)}')
if __name__=='__main__':main()
