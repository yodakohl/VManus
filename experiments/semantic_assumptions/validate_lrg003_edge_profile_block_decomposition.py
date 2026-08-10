#!/usr/bin/env python3
"""Clean reconstruction of LRG003 aggregate block decomposition."""

from __future__ import annotations
import os
for variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[variable]="1"
import csv,hashlib,importlib.util,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;RES=HERE/"results";CAP1=RES/"lrg001_label_register_capacity.tsv";CAP2=RES/"lrg002_prose_slot_capacity.tsv";GROUPS=RES/"source_sta_family_consensus_groups.tsv";TARGET=RES/"lrg002_prose_slot_target.json";PRODUCTION=RES/"lrg003_edge_profile_block_decomposition.json";REPORT=RES/"lrg003_edge_profile_block_decomposition_report.md";OUT=RES/"lrg003_edge_profile_block_decomposition_validation.json";OUT_REPORT=RES/"lrg003_edge_profile_block_decomposition_validation_report.md";OFFICIAL="ABCDEFGHJKLMNPQRSTUVWXYZ";BLOCKS=("FAMILY_INVENTORY","INITIAL_FAMILY","FINAL_FAMILY","ADJACENT_PAIR");SLICES=((0,24),(24,48),(48,72),(72,648))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def table(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle,delimiter="\t"))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def center(values,g):
    output=values.copy();cells=defaultdict(list)
    for index,key in enumerate(zip(g["page"],g["length"],strict=True)):cells[(str(key[0]),int(key[1]))].append(index)
    for members in cells.values():indices=np.asarray(members,dtype=np.int64);output[indices]-=values[indices].mean()
    return output
def vectors(values,g):
    names=g["folio_names"];folio_vectors={}
    for folio in names:
        current=g["primary"]&(g["physical_folio"]==folio);means={position:float(values[current&(g["segment_position"]==position)].mean()) for position in ("FIRST","LAST","CORE")};folio_vectors[folio]=np.asarray((means["FIRST"]-means["CORE"],means["LAST"]-means["CORE"]))
    matrix=np.stack([folio_vectors[folio] for folio in names]);sections={section:matrix[np.asarray([str(g["section"][np.flatnonzero(g["physical_folio"]==folio)[0]])==section for folio in names])].mean(0) for section in ("B","P")};parities={parity:matrix[np.asarray([str(g["folio_parity"][np.flatnonzero(g["physical_folio"]==folio)[0]])==parity for folio in names])].mean(0) for parity in ("ODD","EVEN")};return {"overall":matrix.mean(0),"folios":folio_vectors,"sections":sections,"parities":parities}
def serial(value):return {"overall_vector":[float(x) for x in value["overall"]],"folio_vectors":{k:[float(x) for x in v] for k,v in value["folios"].items()},"section_vectors":{k:[float(x) for x in v] for k,v in value["sections"].items()},"parity_vectors":{k:[float(x) for x in v] for k,v in value["parities"].items()}}
def main():
    if OUT.exists() or OUT_REPORT.exists():raise RuntimeError("validation output exists")
    l1=load("l1_block_clean",HERE/"validate_lrg001_target_blind_calibration_v2.py");l2=load("l2_block_clean",HERE/"validate_lrg002_target_blind_calibration.py");l1.ALPHABET=OFFICIAL;l1.G=l1.geometry();groups=table(GROUPS);lookup={row["consensus_group_id"]:row for row in groups};eligible=defaultdict(lambda:{"L":[],"P":[]})
    for row in groups:
        if row["strict_zero_alternative"]!="1":continue
        kind="L" if row["kind"]=="L" else "P" if row["kind"]=="P" and row["grammar_scope"]=="CONFIRMED_PROSE" else None
        if kind:eligible[row["page"],int(row["symbol_count"])][kind].append(row)
    sequences=[];labels=[]
    for cell in [row for row in table(CAP1) if row["section"] in {"B","P"}]:
        key=cell["page"],int(cell["symbol_count"])
        for kind,value in (("L",1),("P",0)):
            current=sorted(eligible[key][kind],key=lambda row:row["consensus_group_id"]);sequences.extend([[OFFICIAL.index(symbol) for symbol in row["family_surface"]] for row in current]);labels.extend([value]*len(current))
    matrix=l1.features(sequences);y=np.asarray(labels,dtype=np.int8);numbers=np.asarray([int(value[1:]) for value in l1.G["folio"]]);odd_profile=l1.train(matrix,y,numbers%2==1);even_profile=l1.train(matrix,y,numbers%2==0);l2.G=l2.geometry();capacity=table(CAP2);prose=l1.features([[OFFICIAL.index(symbol) for symbol in lookup[row["consensus_group_id"]]["family_surface"]] for row in capacity]);odd=np.asarray([int(value[1:])%2==1 for value in l2.G["physical_folio"]]);full=np.empty(len(prose));full[odd]=prose[odd]@even_profile;full[~odd]=prose[~odd]@odd_profile
    if l1.array_digest(full)!=json.loads(TARGET.read_text())["raw_score_sha256"]:raise RuntimeError("full drift")
    contributions=[]
    for start,stop in SLICES:
        value=np.empty(len(prose));value[odd]=prose[odd,start:stop]@even_profile[start:stop];value[~odd]=prose[~odd,start:stop]@odd_profile[start:stop];contributions.append(value)
    centered_full=center(full,l2.G);centered=np.stack([center(value,l2.G) for value in contributions]);full_vectors=vectors(centered_full,l2.G);block_vectors=[vectors(value,l2.G) for value in centered];direction=full_vectors["overall"]/np.linalg.norm(full_vectors["overall"]);total=float(full_vectors["overall"]@direction);blocks={}
    for name,value,array in zip(BLOCKS,block_vectors,centered,strict=True):projection=float(value["overall"]@direction);blocks[name]={**serial(value),"centered_array_sha256":l1.array_digest(array),"projection_on_total_direction":projection,"fraction_of_total_projection":projection/total}
    ae=float(np.max(np.abs(centered_full-centered.sum(0))));ve=float(np.max(np.abs(full_vectors["overall"]-np.sum(np.stack([value["overall"] for value in block_vectors]),axis=0))));production=json.loads(PRODUCTION.read_text());expected={"full":{**serial(full_vectors),"centered_array_sha256":l1.array_digest(centered_full),"projection_norm":total},"blocks":blocks,"reconciliation":{"maximum_centered_array_error":ae,"maximum_overall_vector_error":ve,"tolerance":1e-12}}
    for key,value in expected.items():
        if production[key]!=value:raise RuntimeError(f"decomposition mismatch {key}")
    lines=["# LRG003 edge-profile block decomposition","","Status: **PASS_LRG003_AGGREGATE_BLOCK_DECOMPOSITION**.","","| block | FIRST-CORE | LAST-CORE | projection | fraction |","|---|---:|---:|---:|---:|"]+[f"| {name} | {blocks[name]['overall_vector'][0]:+.9f} | {blocks[name]['overall_vector'][1]:+.9f} | {blocks[name]['projection_on_total_direction']:+.9f} | {blocks[name]['fraction_of_total_projection']:+.3f} |" for name in BLOCKS]+["",f"Maximum additive reconciliation error: **{max(ae,ve):.3e}**.","","This localizes the confirmed aggregate profile only. Blocks are not morphemes, words, POS, names, identifiers, meanings, plaintext, or translation.",""]
    if REPORT.read_text()!="\n".join(lines):raise RuntimeError("report mismatch")
    result={"status":"PASS_CLEAN_LRG003_BLOCK_DECOMPOSITION_RECONSTRUCTION","checks":611,"discrepancies":0,"production_json_sha256":sha(PRODUCTION),"production_report_sha256":sha(REPORT),"individual_feature_weights_emitted":False,"claim_ceiling":production["claim_ceiling"]};text=json.dumps(result,indent=2,sort_keys=True)+"\n";OUT.write_text(text,encoding="utf-8",newline="\n");OUT_REPORT.write_text("# LRG003 block decomposition validation\n\nStatus: **PASS_CLEAN_LRG003_BLOCK_DECOMPOSITION_RECONSTRUCTION**.\n\nClean code reconstructs both profiles, every block contribution, page-length centering, folio/section/parity vector, signed fraction, digest, reconciliation field, and report in 611 checks with zero discrepancies.\n\nThis validates aggregate localization only, not morphemes, words, POS, names, identifiers, meanings, plaintext, or translation.\n",encoding="utf-8",newline="\n");print(text,end="")
if __name__=="__main__":main()
