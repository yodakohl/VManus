#!/usr/bin/env python3
"""Finalize GDT383 Stage A from the retained frozen-scoring tables."""
import csv,hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/"experiments/yolo/gdt383_repaired_local_role_transfer"
ART=BASE/"artifacts"
ENDPOINTS=["FUNCTION_WORD","ALTERNATIVE_OR","POLARITY_EXCLUSION","UNTIL_STATE_GATE","COORDINATOR","REF_ANAPHORA"]
OUTPUTS=["gdt383_role_recovery.tsv","gdt383_resolution_diagnostics.tsv","gdt383_channel_treatments.tsv","gdt383_realization_controls.tsv","gdt383_outcome_overlap.tsv","gdt383_downstream_transfer.tsv","gdt383_null_worlds.tsv"]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):
 q=dict(d);q.pop("content_hash",None)
 return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def read(name): return list(csv.DictReader((ART/name).open(),delimiter="\t"))

def main():
 old=json.loads((ART/"gdt383_stage_a_result.json").read_text())
 freeze=json.loads((ART/"gdt383_stage_a_freeze.json").read_text())
 role=read("gdt383_role_recovery.tsv");controls=read("gdt383_realization_controls.tsv")
 down=read("gdt383_downstream_transfer.tsv");overlap=read("gdt383_outcome_overlap.tsv")
 role_gate={}
 for endpoint in ENDPOINTS:
  h=next(x for x in role if x["endpoint"]==endpoint and x["model"]=="HIERARCHICAL_EVIDENCE")
  j=next(x for x in role if x["endpoint"]==endpoint and x["model"]=="EXACT_JOINT_ONLY")
  u=next(x for x in role if x["endpoint"]==endpoint and x["model"]=="STRICT_UNIVERSAL")
  role_gate[endpoint]=(float(h["macro_auc"])>=.80 and float(h["gain_bits"])>0 and int(h["positive_domains"])>=3 and float(h["macro_auc"])-float(j["macro_auc"])>=.02 and float(h["macro_auc"])-float(u["macro_auc"])>=.10 and float(h["max_family_p"])<=.05)
 control_pass=len(controls)==42 and all(float(x["macro_auc"])>=.90 and float(x["gain_bits"])>0 for x in controls)
 downstream_gate={}
 for endpoint in ENDPOINTS:
  x=next(x for x in down if x["endpoint"]==endpoint and x["selected_on_development"]=="1")
  conf=[float(q["source_only_auc"]) for q in overlap if q["outcome"]==x["outcome"] and q["domain"] in freeze["confirmation_domains"] and q["source_only_auc"]!="NA"]
  downstream_gate[endpoint]=(len(conf)==2 and sum(conf)/2<=freeze["leakage_ceiling_source_only_auc"] and float(x["confirmation_harleian_gain_bits"])>0 and float(x["confirmation_quinte_gain_bits"])>0 and float(x["confirmation_max_family_p"])<=freeze["downstream_gate"]["max_family_p"])
 stage_a=all(role_gate.values()) and control_pass and sum(downstream_gate.values())>=freeze["downstream_gate"]["minimum_roles"] and downstream_gate["COORDINATOR"]
 assert role_gate==old["role_gates"] and downstream_gate==old["downstream_gates"] and stage_a==old["stage_a_pass"]
 docs=["METHOD.md","REPORT.md","README.md","experiment.json"]
 impl=["src/run_stage_a.py","src/finalize_stage_a.py","src/validate_stage_a.py"]
 result={
  "schema":"GDT383_STAGE_A_RESULT_V1",
  "status":"STAGE_A_PASS_TARGET_FREEZE_AUTHORIZED" if stage_a else "STAGE_A_FAILED_STOP_BEFORE_VOYNICH",
  "rows":old["rows"],"records":old["records"],"pivots":old["pivots"],
  "role_gates":role_gate,"roles_passing":sum(role_gate.values()),
  "realization_gate_pass":control_pass,"realization_cells_passing":sum(float(x["macro_auc"])>=.90 and float(x["gain_bits"])>0 for x in controls),
  "downstream_gates":downstream_gate,"downstream_roles_passing":sum(downstream_gate.values()),"priority_coordinator_pass":downstream_gate["COORDINATOR"],
  "stage_a_pass":stage_a,"voynich_stage_b_authorized":stage_a,"voynich_stage_b_created":False,"voynich_rows_read":0,"voynich_scored":False,
  "gdt381_target_artifacts_read":False,"semantic_state":"UNASSIGNED",
  "interpretation":"REPAIRED_LOCAL_ROLE_RECOVERY_PARTIAL_BUT_DISJOINT_TRANSFORMATION_NOT_VALIDATED",
  "next_route":"COMPARATOR_ONLY_AUTHORIAL_DOWNSTREAM_EVENT_GRAPH_CALIBRATION",
  "f84":{"opened":False,"parsed":False,"retained":False,"scored":False},
  "inputs":old["inputs"],
  "outputs":{str((ART/n).relative_to(ROOT)):sha(ART/n) for n in OUTPUTS},
  "documents":{str((BASE/n).relative_to(ROOT)):sha(BASE/n) for n in docs},
  "implementation":{str((BASE/n).relative_to(ROOT)):sha(BASE/n) for n in impl},
  "claim_ceiling":"COMPARATOR_POSITIVE_CONTROL_REPAIRED_INSTRUMENT_ONLY"
 }
 result["content_hash"]=content(result)
 (ART/"gdt383_stage_a_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":result["status"],"role_gates":role_gate,"downstream_gates":downstream_gate,"content_hash":result["content_hash"]},sort_keys=True))

if __name__=="__main__": main()
