#!/usr/bin/env python3
"""Independently reconstruct the TGC001 score-blind capacity stop."""
from __future__ import annotations

import csv, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

B = Path(__file__).resolve().parent; ROOT = B.parents[1]; R = B / "results"
SOURCE = R / "source_sta_family_consensus_groups.tsv"
SOURCEV = R / "source_sta_family_consensus_validation.json"
IGR1 = R / "igr001_image_grounded_grapheme_selection.json"
METHOD = B / "TGC001_WHOLE_GROUP_TRACE_GRAPH_CAPACITY_METHOD.md"
BUILDER = B / "build_tgc001_whole_group_trace_capacity.py"
PANEL = R / "tgc001_whole_group_trace_capacity_panel.tsv"
RESULT = R / "tgc001_whole_group_trace_capacity.json"
REPORT = R / "tgc001_whole_group_trace_capacity_report.md"
OUT = R / "tgc001_whole_group_trace_capacity_validation.json"
OUTR = R / "tgc001_whole_group_trace_capacity_validation_report.md"
FIELDS = ["opaque_group_id","cell_index","physical_folio","page","locus","consensus_group_id","consensus_group_index","consensus_group_count","symbol_count","selection_rank_sha256"]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def folio(page): return re.match(r"^(f(?:Ros|[0-9]+))", page, re.I).group(1).lower()
def trip(r): return tuple(r[x] for x in ("zl_sta_codes","it_sta_codes","rf_sta_codes"))
def cell(r): return (r["family_surface"],r["currier"] or "BLANK",r["hand"] or "BLANK")
def rank(r): return hashlib.sha256(("TGC001_GROUP_V1|"+r["consensus_group_id"]).encode()).hexdigest()
def patterns(r):
    return [(f,z,i,q) for f,z,i,q in zip(r["family_surface"],r["zl_sta_codes"].split(),r["it_sta_codes"].split(),r["rf_sta_codes"].split()) if len({z,i,q})>1]

def main():
    if OUT.exists() or OUTR.exists(): raise SystemExit("refusing overwrite")
    checks={}
    checks["upstream_pass"]=json.loads(SOURCEV.read_text())["status"].startswith("PASS_")
    src=list(csv.DictReader(SOURCE.open(newline=""),delimiter="\t"))
    base=[r for r in src if r["strict_zero_alternative"]=="1" and r["grammar_scope"]=="CONFIRMED_PROSE" and 1<=int(r["symbol_count"])<=8]
    dis=[r for r in base if len(set(trip(r)))>1]
    checks["base_counts"]=(len(base),len({folio(r["page"]) for r in base}))==(21841,94)
    checks["disagreement_counts"]=(len(dis),sum(int(r["symbol_count"]) for r in dis),sum(len(patterns(r)) for r in dis),len({folio(r["page"]) for r in dis}))==(2997,13679,3184,93)
    shell=defaultdict(set); trf=defaultdict(set)
    for r in dis:
        shell[r["family_surface"]].add(folio(r["page"]));trf[(r["family_surface"],*trip(r))].add(folio(r["page"]))
    checks["raw_recurrence"]=(len(shell),sum(len(v)>=5 for v in shell.values()),sum(len(shell[r["family_surface"]])>=5 for r in dis),len(trf),sum(len(v)>=5 for v in trf.values()),sum(len(trf[(r["family_surface"],*trip(r))])>=5 for r in dis))==(923,102,1857,1759,61,958)
    igr=json.loads(IGR1.read_text());closed={(t["family"],t["zl_code"],t["it_code"],t["rf_code"]) for t in igr["targets"]}
    checks["closed_registry"] = len(closed)==8 and ("B","B1","B1","Ba") in closed
    nd=[r for r in dis if all(p not in closed for p in patterns(r))]
    checks["nonduplicate_counts"]=(len(nd),len({folio(r["page"]) for r in nd}))==(676,91)
    cells=defaultdict(list)
    for r in nd: cells[cell(r)].append(r)
    qualified=[(k,rs,{folio(r["page"]) for r in rs}) for k,rs in cells.items() if len({folio(r["page"]) for r in rs})>=6]
    qualified.sort(key=lambda x:(-len(x[2]),-len(x[1]),tuple(v.encode() for v in x[0])))
    checks["controlled_capacity"] = len(qualified)==5 and sum(len(x[1]) for x in qualified)==32 and len({folio(r["page"]) for x in qualified for r in x[1]})==28
    expected=[];meta=[]
    for idx,(key,rs,fols) in enumerate(qualified,1):
        chosen=[];used=set()
        for r in sorted(rs,key=rank):
            pf=folio(r["page"])
            if pf in used: continue
            used.add(pf);chosen.append(r)
            if len(chosen)==6:break
        meta.append({"cell_index":idx,"family_surface":key[0],"currier":key[1],"hand":key[2],"groups":len(rs),"folios":len(fols),"triplet_variants":len({trip(r) for r in rs})})
        for r in chosen:
            expected.append({"opaque_group_id":"TGC"+hashlib.sha256(("TGC001_OPAQUE_V1|"+r["consensus_group_id"]).encode()).hexdigest()[:16].upper(),"cell_index":str(idx),"physical_folio":folio(r["page"]),"page":r["page"],"locus":r["locus"],"consensus_group_id":r["consensus_group_id"],"consensus_group_index":r["consensus_group_index"],"consensus_group_count":r["consensus_group_count"],"symbol_count":r["symbol_count"],"selection_rank_sha256":rank(r)})
    with PANEL.open(newline="") as h:
        rd=csv.DictReader(h,delimiter="\t");checks["panel_header"]=rd.fieldnames==FIELDS;observed=list(rd)
    checks["panel_exact"] = observed==expected and len(observed)==30 and Counter(x["cell_index"] for x in observed)=={str(i):6 for i in range(1,6)} and len({x["physical_folio"] for x in observed})==28
    result=json.loads(RESULT.read_text())
    checks["result_cells"] = result["private_controlled_cell_metadata"]==meta
    checks["result_hold"] = result["status"]=="HOLD_5_CELL_30_GROUP_GEOMETRY_PENDING_TARGET_FREE_CALIBRATION" and result["decision"]=="AUTHORIZE_TARGET_FREE_SYNTHETIC_GEOMETRY_CALIBRATION_ONLY_PUBLISHED_ROWS_IMAGE_INELIGIBLE" and result["published_panel_image_eligibility"]=="PERMANENTLY_INELIGIBLE_FUTURE_IMAGE_PANEL_MUST_EXCLUDE_ALL_30_ROWS" and result["calibration_required"]=={"geometry_cells":5,"folios_per_cell":6,"null_worlds":128,"distributed_plant_worlds":100,"minimum_plant_recovery_rate":0.9,"maximum_null_full_passes":1}
    expected_counts={"base_groups":21841,"base_folios":94,"disagreement_groups":2997,"symbol_positions_in_disagreement_groups":13679,"disagreeing_symbol_positions":3184,"disagreement_folios":93,"family_shells":923,"family_shells_five_folios":102,"groups_in_five_folio_shells":1857,"ordered_triplet_types":1759,"ordered_triplet_types_five_folios":61,"groups_in_five_folio_triplets":958,"nonduplicate_disagreement_groups":676,"nonduplicate_disagreement_folios":91,"qualifying_controlled_cells":5,"groups_in_qualifying_cells":32,"folios_in_qualifying_cells":28,"retained_cells":5,"maximum_selected_groups":30,"selected_physical_folios":28}
    checks["result_counts"] = result["counts"]==expected_counts
    checks["bindings"] = result["inputs"]=={str(p.relative_to(ROOT)):sha(p) for p in (SOURCE,SOURCEV,IGR1,METHOD,BUILDER)} and result["outputs"]=={str(PANEL.relative_to(ROOT)):sha(PANEL)}
    checks["access_ceiling"] = result["access"]=={"image_bodies_opened":False,"manual_internal_symbol_target_selected":False,"trace_graphs_created":False,"zl_it_rf_target_score_opened":False} and all(x in result["claim_ceiling"] for x in ("preferred reading","plaintext","meaning","translation"))
    checks["canonical"] = RESULT.read_bytes()==(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n").encode()
    expected_report=f"# TGC001 whole-group trace-graph capacity\n\nStatus: **{result['status']}**.\n\nThe source-only universe contains 2,997 short confirmed-prose disagreement groups on 93 physical folios. After deleting every group containing any of the eight IGR001-selected types carried into IGR002, 676 groups remain. Five exact family/Currier/hand cells reach six folios, yielding a 30-group geometry on 28 physical folios.\n\nThis geometry now requires target-free synthetic power calibration; it is not yet authorized for image access. No manuscript image, trace graph, internal-symbol box, preferred reading, glyph identity, sound, language, plaintext, meaning, or translation was opened.\n"
    checks["report"] = REPORT.read_text()==expected_report
    fail=[k for k,v in checks.items() if not v]
    if fail: raise SystemExit(fail)
    out={"check_count":len(checks),"checks":list(checks),"claim_ceiling":"Score-blind nonduplicate geometry for target-free calibration only; no image trace preferred reading glyph identity sound language plaintext meaning or translation.","experiment":"TGC001_WHOLE_GROUP_TRACE_CAPACITY_VALIDATION","panel_sha256":sha(PANEL),"result_sha256":sha(RESULT),"status":f"PASS_{len(checks)}_CHECK_INDEPENDENT_GEOMETRY_RECONSTRUCTION"}
    OUT.write_text(json.dumps(out,sort_keys=True,separators=(",",":"))+"\n")
    OUTR.write_text(f"# TGC001 geometry validation\n\nStatus: **{out['status']}**.\n\nIndependent code reconstructs the 2,997 raw disagreement groups, excludes every group containing any of the eight IGR001-selected types carried into IGR002, and reproduces five controlled cells and the 30-group geometry. Only target-free synthetic calibration is authorized before image access.\n\nNo preferred reading, glyph identity, sound, language, plaintext, meaning, or translation follows.\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":main()
