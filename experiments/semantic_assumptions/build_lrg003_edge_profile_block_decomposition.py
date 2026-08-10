#!/usr/bin/env python3
"""Decompose the confirmed LRG002 edge profile into four frozen blocks."""

from __future__ import annotations
import os
for variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[variable]="1"
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
import lrg001_core as l1
import lrg002_core as l2

HERE=Path(__file__).resolve().parent;RES=HERE/"results";CAP1=RES/"lrg001_label_register_capacity.tsv";CAP2=RES/"lrg002_prose_slot_capacity.tsv";GROUPS=RES/"source_sta_family_consensus_groups.tsv";TARGET=RES/"lrg002_prose_slot_target.json";OUT=RES/"lrg003_edge_profile_block_decomposition.json";REPORT=RES/"lrg003_edge_profile_block_decomposition_report.md";OFFICIAL="ABCDEFGHJKLMNPQRSTUVWXYZ";BLOCKS=("FAMILY_INVENTORY","INITIAL_FAMILY","FINAL_FAMILY","ADJACENT_PAIR");SLICES=((0,24),(24,48),(48,72),(72,648))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def table(path):
    with path.open(encoding="utf-8",newline="") as handle:return list(csv.DictReader(handle,delimiter="\t"))
def profiles(source):
    g=l1.load_geometry(CAP1);eligible=defaultdict(lambda:{"L":[],"P":[]})
    for row in source:
        if row["strict_zero_alternative"]!="1":continue
        kind="L" if row["kind"]=="L" else "P" if row["kind"]=="P" and row["grammar_scope"]=="CONFIRMED_PROSE" else None
        if kind:eligible[row["page"],int(row["symbol_count"])][kind].append(row)
    sequences=[];labels=[]
    for cell in [row for row in table(CAP1) if row["section"] in {"B","P"}]:
        key=cell["page"],int(cell["symbol_count"])
        for kind,value in (("L",1),("P",0)):
            current=sorted(eligible[key][kind],key=lambda row:row["consensus_group_id"]);sequences.extend(row["family_surface"] for row in current);labels.extend([value]*len(current))
    matrix=l1.feature_matrix(sequences,g.lengths);y=np.asarray(labels,dtype=np.int8);numbers=np.asarray([int(value[1:]) for value in g.folios]);odd=numbers%2==1
    return l1.learn_profile(matrix,y,g,odd),l1.learn_profile(matrix,y,g,~odd)
def center(values,g):
    output=values.copy();cells=defaultdict(list)
    for index,key in enumerate(zip(g.pages,g.lengths,strict=True)):cells[(str(key[0]),int(key[1]))].append(index)
    for members in cells.values():indices=np.asarray(members,dtype=np.int64);output[indices]-=values[indices].mean()
    return output
def vectors(values,g):
    folios={}
    for folio in g.folio_names:
        current=g.primary&(g.folios==folio);means={position:float(values[current&(g.positions==position)].mean()) for position in ("FIRST","LAST","CORE")};folios[folio]=np.asarray((means["FIRST"]-means["CORE"],means["LAST"]-means["CORE"]))
    matrix=np.stack([folios[folio] for folio in g.folio_names]);sections={section:matrix[np.asarray([str(g.sections[np.flatnonzero(g.folios==folio)[0]])==section for folio in g.folio_names])].mean(0) for section in ("B","P")};parities={parity:matrix[np.asarray([str(g.parities[np.flatnonzero(g.folios==folio)[0]])==parity for folio in g.folio_names])].mean(0) for parity in ("ODD","EVEN")}
    return {"overall":matrix.mean(0),"folios":folios,"sections":sections,"parities":parities}
def serial(value):
    return {"overall_vector":[float(x) for x in value["overall"]],"folio_vectors":{k:[float(x) for x in v] for k,v in value["folios"].items()},"section_vectors":{k:[float(x) for x in v] for k,v in value["sections"].items()},"parity_vectors":{k:[float(x) for x in v] for k,v in value["parities"].items()}}
def main():
    if OUT.exists() or REPORT.exists():raise RuntimeError("LRG003 output exists")
    target=json.loads(TARGET.read_text());
    if target["status"]!="CONFIRMED_DISTRIBUTED_LABEL_PROFILE_SLOT":raise RuntimeError("LRG002 confirmation absent")
    l1.ALPHABET=OFFICIAL;l1.INDEX={value:index for index,value in enumerate(OFFICIAL)};source=table(GROUPS);lookup={row["consensus_group_id"]:row for row in source};capacity=table(CAP2);g=l2.load_geometry(CAP2);odd_profile,even_profile=profiles(source);surfaces=[lookup[row["consensus_group_id"]]["family_surface"] for row in capacity];matrix=l1.feature_matrix(surfaces,g.lengths);odd=np.asarray([int(value[1:])%2==1 for value in g.folios])
    full=np.empty(len(matrix));full[odd]=matrix[odd]@even_profile;full[~odd]=matrix[~odd]@odd_profile
    if l1.sha256_array(full)!=target["raw_score_sha256"]:raise RuntimeError("full score drift")
    contributions=[]
    for start,stop in SLICES:
        current=np.empty(len(matrix));current[odd]=matrix[odd,start:stop]@even_profile[start:stop];current[~odd]=matrix[~odd,start:stop]@odd_profile[start:stop];contributions.append(current)
    centered_full=center(full,g);centered=np.stack([center(value,g) for value in contributions]);summed=centered.sum(axis=0);array_error=float(np.max(np.abs(centered_full-summed)));full_vectors=vectors(centered_full,g);block_vectors=[vectors(value,g) for value in centered];vector_error=float(np.max(np.abs(full_vectors["overall"]-np.sum(np.stack([value["overall"] for value in block_vectors]),axis=0))));direction=full_vectors["overall"]/np.linalg.norm(full_vectors["overall"]);total_projection=float(full_vectors["overall"]@direction)
    block_results={}
    for name,value,array in zip(BLOCKS,block_vectors,centered,strict=True):
        projection=float(value["overall"]@direction);block_results[name]={**serial(value),"centered_array_sha256":l1.sha256_array(array),"projection_on_total_direction":projection,"fraction_of_total_projection":projection/total_projection}
    if max(array_error,vector_error)>1e-12:raise RuntimeError("block reconciliation")
    result={"status":"PASS_LRG003_AGGREGATE_BLOCK_DECOMPOSITION","counts":{"rows":5824,"primary_rows":5769,"segments":705,"folios":16,"blocks":4},"full":{**serial(full_vectors),"centered_array_sha256":l1.sha256_array(centered_full),"projection_norm":total_projection},"blocks":block_results,"reconciliation":{"maximum_centered_array_error":array_error,"maximum_overall_vector_error":vector_error,"tolerance":1e-12},"inputs":{path.name:sha(path) for path in (CAP1,CAP2,GROUPS,TARGET,HERE/"LRG003_EDGE_PROFILE_BLOCK_DECOMPOSITION_SPEC.md",Path(__file__))},"individual_feature_weights_emitted":False,"individual_forms_emitted":False,"english_glosses":0,"claim_ceiling":"Aggregate additive block localization only; feature blocks are not morphemes words POS names identifiers meanings plaintext or translation."}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n";OUT.write_text(text,encoding="utf-8",newline="\n");lines=["# LRG003 edge-profile block decomposition","","Status: **PASS_LRG003_AGGREGATE_BLOCK_DECOMPOSITION**.","","| block | FIRST-CORE | LAST-CORE | projection | fraction |","|---|---:|---:|---:|---:|"]+[f"| {name} | {block_results[name]['overall_vector'][0]:+.9f} | {block_results[name]['overall_vector'][1]:+.9f} | {block_results[name]['projection_on_total_direction']:+.9f} | {block_results[name]['fraction_of_total_projection']:+.3f} |" for name in BLOCKS]+["",f"Maximum additive reconciliation error: **{max(array_error,vector_error):.3e}**.","","This localizes the confirmed aggregate profile only. Blocks are not morphemes, words, POS, names, identifiers, meanings, plaintext, or translation.",""];REPORT.write_text("\n".join(lines),encoding="utf-8",newline="\n");print(text,end="")
if __name__=="__main__":main()
