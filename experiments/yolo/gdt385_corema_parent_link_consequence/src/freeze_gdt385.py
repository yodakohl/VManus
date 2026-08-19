#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt385_corema_parent_link_consequence"
ART=BASE/"artifacts";ART.mkdir(exist_ok=True)
FILES=[
 BASE/"METHOD.md",BASE/"SOURCE_AUDIT.md",BASE/"gdt385_role_manifest.tsv",
 BASE/"experiment.json",
 ROOT/"gdt176_corema_role_oracle.tsv",
 ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit/artifacts/gdt382_voynichified_observation_layer.tsv.gz",
 ROOT/"experiments/yolo/gdt383_repaired_local_role_transfer/METHOD.md",
 ROOT/"experiments/yolo/gdt383_repaired_local_role_transfer/artifacts/gdt383_stage_a_result.json",
]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
out={
 "schema":"GDT385_PRE_SCORE_FREEZE_V1",
 "status":"FROZEN_BEFORE_PARENT_LINK_SCORING",
 "date":"2026-08-19",
 "routes":["CMP_PARENT_01","CMP_PARENT_02","CMP_PARENT_03","CMP_PARENT_04"],
 "role_auc_min":.60,"minimum_links":50,"minimum_link_collections":5,
 "minimum_positive_gain_collections":4,"minimum_mobile_fraction":.20,
 "null_worlds":2048,"joint_family_size":4,"joint_p_max":.05,
 "priority_route":"CMP_PARENT_01","minimum_routes_passing":3,
 "voynich_stage_authorized":False,"voynich_rows_read":0,
 "f84":{"authorized":False,"opened":False,"parsed":False,"retained":False,"scored":False},
 "files":{str(p.relative_to(ROOT)):sha(p) for p in FILES},
}
raw=json.dumps(out,sort_keys=True,separators=(",",":" )).encode();out["content_hash"]=hashlib.sha256(raw).hexdigest()
(ART/"gdt385_pre_score_freeze.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(out["content_hash"])
if __name__=="__main__":freeze=None
