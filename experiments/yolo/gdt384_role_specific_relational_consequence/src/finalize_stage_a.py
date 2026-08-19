#!/usr/bin/env python3
"""Finalize the sequentially stopped GDT384 comparator result."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt384_role_specific_relational_consequence";ART=BASE/"artifacts"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def read(n):return list(csv.DictReader((ART/n).open(),delimiter="\t"))
def main():
 priority=json.loads((ART/"gdt384_priority_result.json").read_text());row=read("gdt384_priority_coordinator.tsv")[0];build=json.loads((ART/"gdt384_relation_oracle_build.json").read_text())
 failed=float(row["source_overlap_auc"])>.65 or float(row["deterministic_overlap_auc"])>.65 or float(row["auc_increment"])<.02 or float(row["relation_gain_bits"])<=0 or int(row["positive_held_collections"])<4
 assert failed and priority["status"]=="PRIORITY_RELATION_FAILED_STOP_BEFORE_OTHER_ROLES" and row["pre_null_gate_pass"]=="0"
 outs=["gdt384_hidden_relational_oracle.tsv.gz","gdt384_relation_capacity.tsv","gdt384_relation_oracle_build.json","gdt384_priority_coordinator.tsv","gdt384_priority_coordinator_folds.tsv","gdt384_priority_predictions.tsv.gz","gdt384_priority_result.json","gdt384_output_audit_extension.json"]
 docs=["METHOD.md","SOURCE_AUDIT.md","REPORT.md","gdt384_relation_manifest.tsv","README.md","experiment.json"]
 impl=["src/build_relational_oracle.py","src/run_priority_coordinator.py","src/finalize_stage_a.py","src/validate_stage_a.py"]
 result={"schema":"GDT384_RESULT_V1","status":"PRIORITY_RELATION_UNIDENTIFIABLE_SOURCE_OVERLAP_STOP_BEFORE_VOYNICH","priority_role":"COORDINATOR","priority":{k:(float(v) if k in {"role_auc","role_gain_bits","source_overlap_auc","deterministic_overlap_auc","source_relation_auc","role_plus_relation_auc","auc_increment","relation_gain_bits"} else int(v) if k in {"n","role_positives","relation_positives","positive_held_collections","held_collections","pre_null_gate_pass"} else v) for k,v in row.items()},"relation_oracle_rows":build["rows"],"other_roles_scored":False,"null_run":False,"stage_a_pass":False,"voynich_stage_b_authorized":False,"voynich_stage_b_created":False,"voynich_rows_read":0,"voynich_scored":False,"gdt381_target_artifacts_read":False,"semantic_state":"UNASSIGNED","interpretation":"ROLE_RECOVERY_STRONG_BUT_RELATION_ENDPOINT_SOURCE_OVERLAPPED","next_route":"COMPARATOR_ONLY_EXTERNAL_EDGE_OR_AUTHORIAL_RELATION_CALIBRATION","f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"inputs":priority["inputs"],"outputs":{str((ART/n).relative_to(ROOT)):sha(ART/n) for n in outs},"documents":{str((BASE/n).relative_to(ROOT)):sha(BASE/n) for n in docs},"implementation":{str((BASE/n).relative_to(ROOT)):sha(BASE/n) for n in impl},"claim_ceiling":"COMPARATOR_ROLE_RELATION_INSTRUMENT_FAILURE_ONLY"};result["content_hash"]=content(result);(ART/"gdt384_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"source_overlap_auc":result["priority"]["source_overlap_auc"],"auc_increment":result["priority"]["auc_increment"]},sort_keys=True))
if __name__=="__main__":main()
