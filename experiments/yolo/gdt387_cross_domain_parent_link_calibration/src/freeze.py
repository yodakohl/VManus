#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt387_cross_domain_parent_link_calibration";ART=BASE/"artifacts"
ENC=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit/artifacts/gdt382_voynichified_observation_layer.tsv.gz";P385=ROOT/"experiments/yolo/gdt385_corema_parent_link_consequence/artifacts/gdt385_result.json"
COMMIT="bf79d1c46e8ef983a7347b0664d0d80243f32831";BUNDLE="c90c1eabdb58bd1a41e9231c52612bc14cfa1c560d8cf357e1480384e873c714";LEX=["after","afore","before","ere","when","whan","whanne","whenne","until","untill","til","till","while","whil","whiles","whilst"]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bundle(paths,root):
 h=hashlib.sha256()
 for p in sorted(paths,key=lambda q:str(q.relative_to(root))):h.update(str(p.relative_to(root)).encode());h.update(b"\0");h.update(p.read_bytes());h.update(b"\0")
 return h.hexdigest()
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 env=os.environ.get("GDT387_PCEEC2_DIR");assert env,"set GDT387_PCEEC2_DIR";src=Path(env);files=list((src/"data/parsed").glob("*.psd"));assert len(files)==84
 assert subprocess.check_output(["git","-C",str(src),"rev-parse","HEAD"],text=True).strip()==COMMIT and bundle(files,src)==BUNDLE
 freeze={"schema":"GDT387_PRE_SCORE_FREEZE_V1","status":"FROZEN_BEFORE_SCORING","source":{"url":"https://github.com/beatrice57/pceec2","commit":COMMIT,"parsed_files":84,"bundle_sha256":BUNDLE},"sampling":{"maximum_records_per_file":12,"observation_pceec2_rows":27518,"hidden_role_pivots":110,"hidden_role_files":47},"hidden_role_forms":LEX,"head_rule_id":"GDT387_FIXED_CONSTITUENCY_HEAD_RULE_V1","distance_classes":["L_FAR"]+[f"L{i}" for i in range(13,0,-1)]+[f"R{i}" for i in range(1,14)]+["R_FAR"],"representations":["HOST_IDENTITY","COMPLETE_RENDERED_GROUP","CONSTRUCTION_STATE","COMPOSITE_JOINT_STATE","SHORT_CONSTRUCTION_SPAN","FREQUENCY_GRAMMAR_CHANNEL"],"fold":"WHOLE_PCEEC2_SOURCE_FILE","null":{"worlds":2048,"seed":3872048,"strata":"FILE_X_POSITION_X_BOUNDARY_X_FIELD_BIN_X_WITHIN_FIELD_BIN_X_RECORD_LENGTH_BIN_X_TRAINING_FREQUENCY_BIN","inclusive":True},"gate":{"minimum_role_pivots":100,"minimum_role_files":40,"minimum_role_auc":0.65,"role_gain_positive":True,"governor_gain_positive":True,"minimum_positive_files":42,"minimum_target_mrr_delta":0.0,"minimum_mobile_fraction":0.20,"maximum_p":0.05},"voynich_rows_authorized":0,"f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"inputs":{str(ENC.relative_to(ROOT)):sha(ENC),str(P385.relative_to(ROOT)):sha(P385)},"documents":{str((BASE/x).relative_to(ROOT)):sha(BASE/x) for x in ["README.md","METHOD.md","SOURCE_AUDIT.md"]},"implementation":{str((BASE/x).relative_to(ROOT)):sha(BASE/x) for x in ["src/freeze.py","src/validate_freeze.py","src/run.py","src/validate.py"]},"claim_ceiling":"CROSS_DOMAIN_COMPARATOR_RELATION_CALIBRATION_ONLY"};freeze["content_hash"]=content(freeze);(ART/"gdt387_pre_score_freeze.json").write_text(json.dumps(freeze,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":freeze["status"],"role_pivots":110,"role_files":47},sort_keys=True))
if __name__=="__main__":main()
