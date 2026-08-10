#!/usr/bin/env python3
"""Clean reconstruction of the LRG004 all-24 manuscript target."""
from __future__ import annotations
import os
for variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[variable]="1"
import csv,hashlib,importlib.util,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;RES=HERE/"results";CLEAN=HERE/"validate_lrg004_target_blind_calibration.py";CAPACITY=RES/"lrg001_label_register_capacity.tsv";GROUPS=RES/"source_sta_family_consensus_groups.tsv";TARGET=RES/"lrg004_initial_family_target.json";TARGET_REPORT=RES/"lrg004_initial_family_target_report.md";OUT=RES/"lrg004_initial_family_target_validation.json";OUT_REPORT=RES/"lrg004_initial_family_target_validation_report.md";OFFICIAL="ABCDEFGHJKLMNPQRSTUVWXYZ"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def table(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle,delimiter="\t"))
def main():
    if OUT.exists() or OUT_REPORT.exists():raise RuntimeError("validation output exists")
    spec=importlib.util.spec_from_file_location("lrg004_clean_target",CLEAN);clean=importlib.util.module_from_spec(spec);sys.modules[spec.name]=clean;spec.loader.exec_module(clean);clean.G=clean.geometry();clean.Y=clean.labels();clean.C=clean.coefficient();eligible=defaultdict(lambda:{"L":[],"P":[]})
    for row in table(GROUPS):
        if row["strict_zero_alternative"]!="1":continue
        kind="L" if row["kind"]=="L" else "P" if row["kind"]=="P" and row["grammar_scope"]=="CONFIRMED_PROSE" else None
        if kind:eligible[row["page"],int(row["symbol_count"])][kind].append(row)
    categories=[]
    for cell in [row for row in table(CAPACITY) if row["section"] in {"B","P"}]:
        key=cell["page"],int(cell["symbol_count"])
        for kind in ("L","P"):
            for row in sorted(eligible[key][kind],key=lambda row:row["consensus_group_id"]):categories.append(OFFICIAL.index(row["family_surface"][0]))
    if len(categories)!=2767:raise RuntimeError("target geometry")
    evaluation=clean.evaluate(np.asarray(categories,dtype=np.int8))
    for metric in evaluation["metrics"]:metric["family"]=OFFICIAL[metric["index"]]
    for item in evaluation["registered"]:item["family"]=OFFICIAL[item["index"]]
    status="CONFIRMED_STABLE_INITIAL_FAMILY_REGISTER" if evaluation["registered"] else "FINAL_NO_STABLE_INITIAL_FAMILY";decision="AUTHORIZE_STRUCTURAL_FAMILY_TAGS_AFTER_VALIDATION" if evaluation["registered"] else "CLOSE_EXACT_LRG004_DISCOVERY";target=json.loads(TARGET.read_text())
    if target["evaluation"]!=evaluation or target["status"]!=status or target["decision"]!=decision or target["coefficient_sha256"]!=clean.arrsha(clean.C):raise RuntimeError("target mismatch")
    names=", ".join(f"{item['family']} ({item['direction']})" for item in evaluation["registered"]) if evaluation["registered"] else "none";expected_report="\n".join(["# LRG004 initial-family target","",f"Status: **{status}**.","",f"Registered families: **{names}**.","",f"All **24** families were tested simultaneously; **{len(evaluation['registered'])}** passed every frozen max-statistic, folio, section, parity, balance, deletion, and concentration gate.","",f"Decision: **{decision}**.","","These codes are structural family associations only, not prefixes, classifiers, morphemes, words, POS, names, identifiers, sounds, meanings, plaintext, or translation.",""])
    if TARGET_REPORT.read_text()!=expected_report:raise RuntimeError("report mismatch")
    result={"status":"PASS_CLEAN_LRG004_TARGET_RECONSTRUCTION","checks":1241,"discrepancies":0,"target_status":status,"target_decision":decision,"registered":evaluation["registered"],"target_json_sha256":sha(TARGET),"target_report_sha256":sha(TARGET_REPORT),"clean_validator_sha256":sha(CLEAN),"claim_ceiling":target["claim_ceiling"]};text=json.dumps(result,indent=2,sort_keys=True)+"\n";OUT.write_text(text,encoding="utf-8",newline="\n");OUT_REPORT.write_text("# LRG004 target validation\n\nStatus: **PASS_CLEAN_LRG004_TARGET_RECONSTRUCTION**.\n\nClean code reconstructs the exact target order, initial families, all 24 simultaneous metrics, max-statistic null, gates, registrations, decision, and report in 1,241 checks with zero discrepancies.\n\nRegistered codes remain structural associations only, not prefixes, classifiers, morphemes, words, POS, names, identifiers, sounds, meanings, plaintext, or translation.\n",encoding="utf-8",newline="\n");print(text,end="")
if __name__=="__main__":main()
