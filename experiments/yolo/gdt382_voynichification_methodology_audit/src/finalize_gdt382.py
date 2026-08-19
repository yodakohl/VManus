#!/usr/bin/env python3
"""Finalize GDT382 decisions from frozen, already-scored aggregate tables."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/"experiments/yolo/gdt382_voynichification_methodology_audit";ART=BASE/"artifacts";G378=ROOT/"experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts"
ENDPOINTS=["FUNCTION_WORD","ALTERNATIVE_OR","POLARITY_EXCLUSION","UNTIL_STATE_GATE","COORDINATOR","REF_ANAPHORA"]
REPS=["SOURCE_TOKEN_EQUALITY","DOMAIN_LOCAL_OPAQUE_ID","HOST_IDENTITY","COMPOSITE_JOINT_STATE","COMPLETE_RENDERED_GROUP","FIELD_CONSTRUCTION_SPAN"]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def read(n):return list(csv.DictReader((ART/n).open(),delimiter="\t"))
def main():
 rep=read("gdt382_representation_recovery.tsv");over=read("gdt382_overcontrol_audit.tsv");controls=read("gdt382_bound_free_controls.tsv")
 best={e:max((x for x in rep if x["endpoint"]==e and x["regime"]=="LOCAL"),key=lambda x:float(x["macro_auc"])) for e in ENDPOINTS}
 comp_ok=sum(float(x["macro_auc"])>=.60 and float(x["gain_bits"])>0 for x in best.values())
 bound=[x for x in controls if x["regime"]=="LOCAL" and x["encoding_mode"]!="BASE_ORACLE_BLIND"];bound_ok=sum(float(x["macro_auc"])>=.80 for x in bound)
 losses=[]
 for e in ENDPOINTS:
  for v in sorted({x["variable"] for x in over}):
   g=next(x for x in over if x["endpoint"]==e and x["variable"]==v and x["treatment"]=="GRAMMAR_FEATURE");n=next(x for x in over if x["endpoint"]==e and x["variable"]==v and x["treatment"]=="CONDITIONED_NUISANCE");losses.append((float(g["gain_bits"])-float(n["gain_bits"]),e,v))
 strongest=max(losses)
 local_universal_gaps={e:max(float(x["macro_auc"]) for x in rep if x["endpoint"]==e and x["regime"]=="LOCAL")-max(float(x["macro_auc"]) for x in rep if x["endpoint"]==e and x["regime"]=="UNIVERSAL") for e in ENDPOINTS}
 dc=read("gdt382_discovery_confirmation.tsv");base=[x for x in dc if not x["representation"].startswith("PROSPECTIVE")];explore=sum(x["exploration_pass"]=="1" for x in base);confirm=sum(x["all_at_once_confirmation_pass"]=="1" for x in base)
 decisions={"CURRENT_PIPELINE_VALIDATED_FOR_COMPOSITE_ENCODING":comp_ok>=4,"JOINT_TUPLE_MAPPING_NOT_HOMOLOGOUS":sum(best[e]["representation"]!="COMPOSITE_JOINT_STATE" for e in ENDPOINTS)>=4,"OVERCONTROL_DESTROYS_FUNCTION_SIGNAL":strongest[0]>50,"UNIVERSAL_CROSS_DOMAIN_INVARIANCE_TOO_STRICT":sum(v>.10 for v in local_universal_gaps.values())>=3,"BOUND_FUNCTIONS_NOT_RECOVERABLE_BY_CURRENT_METHOD":bound_ok<len(bound)*2/3,"DISCOVERY_CORRECTION_UNDERPOWERED":explore>confirm+6}
 outnames=["gdt382_representation_recovery.tsv","gdt382_overcontrol_audit.tsv","gdt382_bound_free_controls.tsv","gdt382_discovery_confirmation.tsv","gdt382_ontology_audit.tsv","gdt382_counterexamples.tsv"]
 inputs=[ART/"gdt382_voynichified_observation_layer.tsv.gz",G378/"gdt378_hidden_oracle.tsv.gz",ART/"gdt382_encoder_freeze.json",ART/"gdt382_recovery_design_freeze.json"]
 result={"schema":"GDT382_RESULT_V1","status":"METHODOLOGY_AUDIT_COMPLETE","rows":133183,"records":3235,"domains":["COREMA","CURIOUS_CURES","HARLEIAN_COOKERY","PCEEC2","QUINTE_ESSENCE"],"endpoints":ENDPOINTS,"representations":REPS,"base_endpoints_exploration_recoverable":comp_ok,"bound_control_cells_auc_0_80":bound_ok,"bound_control_cells_total":len(bound),"strongest_overcontrol_loss":{"bits":strongest[0],"endpoint":strongest[1],"variable":strongest[2]},"local_minus_universal_best_auc":local_universal_gaps,"decision_matrix":decisions,"methodological_consequence":"REPAIR_INSTRUMENT_BEFORE_NEXT_VOYNICH_OPERATOR" if any([decisions["JOINT_TUPLE_MAPPING_NOT_HOMOLOGOUS"],decisions["OVERCONTROL_DESTROYS_FUNCTION_SIGNAL"],decisions["UNIVERSAL_CROSS_DOMAIN_INVARIANCE_TOO_STRICT"],decisions["BOUND_FUNCTIONS_NOT_RECOVERABLE_BY_CURRENT_METHOD"],not decisions["CURRENT_PIPELINE_VALIDATED_FOR_COMPOSITE_ENCODING"]]) else "EARLIER_NEGATIVES_MORE_INFORMATIVE","gdt381_outcome_used_to_tune":False,"voynich_rows_read":0,"voynich_scored":False,"f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"inputs":{str(p.relative_to(ROOT)):sha(p) for p in inputs},"outputs":{str((ART/n).relative_to(ROOT)):sha(ART/n) for n in outnames},"documents":{str((BASE/n).relative_to(ROOT)):sha(BASE/n) for n in ["METHOD.md","REPORT.md","README.md","experiment.json"]},"implementation":{str((BASE/'src/run_gdt382.py').relative_to(ROOT)):sha(BASE/'src/run_gdt382.py'),str((BASE/'src/finalize_gdt382.py').relative_to(ROOT)):sha(BASE/'src/finalize_gdt382.py')},"claim_ceiling":"COMPARATOR_POSITIVE_CONTROL_METHODOLOGY_CALIBRATION_ONLY"}
 result["content_hash"]=content(result);(ART/"gdt382_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"decisions":decisions,"content_hash":result["content_hash"]},sort_keys=True))
if __name__=="__main__":main()
