#!/usr/bin/env python3
"""Execute the frozen simultaneous all-24 LRG004 manuscript target."""
from __future__ import annotations
import os
for variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[variable]="1"
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
from lrg004_core import coefficients,evaluate,fixed_labels,load_geometry
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];RES=HERE/"results";FREEZE=HERE/"LRG004_TARGET_FREEZE.json";CAPACITY=RES/"lrg001_label_register_capacity.tsv";GROUPS=RES/"source_sta_family_consensus_groups.tsv";OUT=RES/"lrg004_initial_family_target.json";REPORT=RES/"lrg004_initial_family_target_report.md";VALIDATION=RES/"lrg004_initial_family_target_validation.json";VALIDATION_REPORT=RES/"lrg004_initial_family_target_validation_report.md";OFFICIAL="ABCDEFGHJKLMNPQRSTUVWXYZ"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def table(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle,delimiter="\t"))
def atomic(path,text):
    if path.exists():raise RuntimeError("output exists")
    temporary=path.with_suffix(path.suffix+".tmp");temporary.write_text(text,encoding="utf-8",newline="\n");os.link(temporary,path);temporary.unlink()
def main():
    paths=(OUT,REPORT,VALIDATION,VALIDATION_REPORT)
    if any(path.exists() for path in paths):raise RuntimeError("target output exists")
    freeze=json.loads(FREEZE.read_text());
    if freeze["status"]!="FROZEN_LRG004_ALL_24_TARGET" or freeze["result_paths"]!=[str(path.relative_to(ROOT)) for path in paths]:raise RuntimeError("freeze contract")
    for relative,expected in freeze["frozen_files"].items():
        if sha(ROOT/relative)!=expected:raise RuntimeError(f"freeze drift {relative}")
    g=load_geometry(CAPACITY);y=fixed_labels(g);eligible=defaultdict(lambda:{"L":[],"P":[]})
    for row in table(GROUPS):
        if row["strict_zero_alternative"]!="1":continue
        kind="L" if row["kind"]=="L" else "P" if row["kind"]=="P" and row["grammar_scope"]=="CONFIRMED_PROSE" else None
        if kind:eligible[row["page"],int(row["symbol_count"])][kind].append(row)
    categories=[]
    for cell in [row for row in table(CAPACITY) if row["section"] in {"B","P"}]:
        key=cell["page"],int(cell["symbol_count"])
        for kind in ("L","P"):
            current=sorted(eligible[key][kind],key=lambda row:row["consensus_group_id"]);expected=int(cell["label_rows"] if kind=="L" else cell["prose_rows"])
            if len(current)!=expected:raise RuntimeError("target count drift")
            for row in current:
                surface=row["family_surface"]
                if len(surface)!=int(row["symbol_count"]) or any(value not in OFFICIAL for value in surface):raise RuntimeError("target family drift")
                categories.append(OFFICIAL.index(surface[0]))
    category_array=np.asarray(categories,dtype=np.int8)
    if len(category_array)!=2767:raise RuntimeError("target geometry")
    coefficient=coefficients(g);evaluation=evaluate(category_array,y,g,coefficient)
    for metric in evaluation["metrics"]:metric["family"]=OFFICIAL[metric["index"]]
    for item in evaluation["registered"]:item["family"]=OFFICIAL[item["index"]]
    registered=evaluation["registered"];status="CONFIRMED_STABLE_INITIAL_FAMILY_REGISTER" if registered else "FINAL_NO_STABLE_INITIAL_FAMILY";decision="AUTHORIZE_STRUCTURAL_FAMILY_TAGS_AFTER_VALIDATION" if registered else "CLOSE_EXACT_LRG004_DISCOVERY"
    result={"status":status,"decision":decision,"claim_ceiling":"Registered codes are only stable positive or negative manual-label-associated group-initial families, never prefixes classifiers morphemes words POS names identifiers sounds meanings plaintext or translation.","freeze_sha256":sha(FREEZE),"counts":{"rows":2767,"labels":288,"cells":101,"folios":13,"families_tested":24,"families_registered":len(registered)},"coefficient_sha256":hashlib.sha256(np.ascontiguousarray(coefficient).tobytes()).hexdigest(),"evaluation":evaluation,"source_sequences_emitted":False,"individual_rows_emitted":False,"form_rankings_emitted":False,"feature_weights_emitted":False}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n";names=", ".join(f"{item['family']} ({item['direction']})" for item in registered) if registered else "none";lines=["# LRG004 initial-family target","",f"Status: **{status}**.","",f"Registered families: **{names}**.","",f"All **24** families were tested simultaneously; **{len(registered)}** passed every frozen max-statistic, folio, section, parity, balance, deletion, and concentration gate.","",f"Decision: **{decision}**.","","These codes are structural family associations only, not prefixes, classifiers, morphemes, words, POS, names, identifiers, sounds, meanings, plaintext, or translation.",""];report="\n".join(lines)
    if any(path.exists() for path in paths):raise RuntimeError("concurrent output")
    atomic(OUT,text)
    try:atomic(REPORT,report)
    except Exception:OUT.unlink(missing_ok=True);raise
    print(text,end="")
if __name__=="__main__":main()
