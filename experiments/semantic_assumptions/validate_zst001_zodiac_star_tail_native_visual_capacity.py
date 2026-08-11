#!/usr/bin/env python3
"""Independent reconstruction of the ZST001 unscored capacity stop."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
PROJECTION = RESULTS / "zst001_zodiac_star_tail_state_projection.tsv"
RESULT = RESULTS / "zst001_zodiac_star_tail_native_visual_capacity.json"
REPORT = RESULTS / "zst001_zodiac_star_tail_native_visual_capacity_report.md"
OUT = RESULTS / "zst001_zodiac_star_tail_native_visual_capacity_validation.json"
OUT_MD = RESULTS / "zst001_zodiac_star_tail_native_visual_capacity_validation.md"

RING_SPECS = [
    ("f72r3", "x", "f72", "INNER", 7, {5, 6, 7}, "f72r3.S3", "266c96a38063766cc6053915b72200432823c16c2670859c61580194b5385299"),
    ("f72r3", "y", "f72", "MIDDLE", 11, {1, 2, 5, 8, 9, 10}, "f72r3.S2", "a1dd0e98c81791950ecd951c62d60d1a97d14e1c50a52a6d249603e3a32910e7"),
    ("f72r3", "z", "f72", "OUTER", 12, {1, 2, 3, 6, 7, 8, 9, 10, 12}, "f72r3.S1", "b98ceb38cb8351bae8c743948b3f7d0004c8e7bb4daea2a95a04fe5938eed6ca"),
    ("f73r", "x", "f73", "INNER", 10, {3}, "f73r.S2", "f22341fdd6cd3de0a22e33c3f1e7d707047b2b82afc72b95b39de56f44df623a"),
    ("f73r", "y", "f73", "OUTER", 16, {4, 6}, "f73r.S1", "127f26916640014f7bae7e0d3728be86ca7d469868aba063609df390c69779d3"),
]
EXPLICIT_NO = {("f73r", "x", 8), ("f73r", "x", 9)}
CONFLICTS = {"STOLFI_BEST_0748", "STOLFI_BEST_0749"}
URL = "https://www.ic.unicamp.br/~stolfi/EXPORT/voynich/Notes/060/L16%2BH-eva/UNITS/"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def projection_bytes(crosswalk_rows: list[dict[str, str]]) -> bytes:
    lookup = {
        (row["source_page"], row["source_unit"], int(row["source_item"])): row
        for row in crosswalk_rows
        if row["source_item"].isdigit()
    }
    fields = [
        "source_record_id", "page", "physical_folio", "source_unit", "ring", "grove_number",
        "tail_state", "grade_source", "grade_confidence", "catalogue_star_tail_conflict",
        "source_note_url", "source_note_sha256", "native_image_id", "native_image_sha256", "visual_basis",
    ]
    lines = ["\t".join(fields)]
    for page, unit, folio, ring, count, tails, note, note_sha in RING_SPECS:
        for number in range(1, count + 1):
            source = lookup[(page, unit, number)]
            state = "TAIL" if number in tails else "NO_TAIL"
            key = (page, unit, number)
            if state == "TAIL":
                grade = "HUMAN_EXPLICIT_TAIL"; basis = "public unit note explicitly says star with tail"
            elif key in EXPLICIT_NO:
                grade = "HUMAN_EXPLICIT_NO_TAIL_CORRECTION"; basis = "public unit note explicitly rejects tail and distinguishes the arm"
            else:
                grade = "NATIVE_CLEAR_NO_TAIL"; basis = "complete held-star contour visible with no independent continuation beyond the holding arm"
            values = {
                "source_record_id": source["source_record_id"], "page": page, "physical_folio": folio,
                "source_unit": unit, "ring": ring, "grove_number": str(number), "tail_state": state,
                "grade_source": grade, "grade_confidence": "HIGH",
                "catalogue_star_tail_conflict": "1" if source["source_record_id"] in CONFLICTS else "0",
                "source_note_url": URL + note, "source_note_sha256": note_sha,
                "native_image_id": "YALE_1006203" if folio == "f72" else "YALE_1006206",
                "native_image_sha256": "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269" if folio == "f72" else "5bc8e07dbd61cc1f218cfc4449cd527be118aa7884878ec4c8e568e9c2d89bad",
                "visual_basis": basis,
            }
            lines.append("\t".join(values[field] for field in fields))
    return ("\n".join(lines) + "\n").encode()


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise SystemExit("refusing overwrite")
    checks = []
    def check(name: str, value: bool) -> None:
        checks.append({"name": name, "pass": bool(value)})
        if not value:
            raise SystemExit(f"validation failure: {name}")

    check("crosswalk_sha", sha(CROSSWALK) == "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc")
    check("groups_sha", sha(GROUPS) == "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225")
    crosswalk_rows = read(CROSSWALK)
    check("projection_exact_bytes", PROJECTION.read_bytes() == projection_bytes(crosswalk_rows))
    projection = read(PROJECTION)
    check("projection_count", len(projection) == 56)
    check("catalogue_corrections", {r["source_record_id"] for r in projection if r["catalogue_star_tail_conflict"] == "1"} == CONFLICTS)
    crosswalk = {row["source_record_id"]: row for row in crosswalk_rows}
    group_lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read(GROUPS): group_lookup[row["locus"]].append(row)
    strict_rows=[]; exclusions={}
    for row in projection:
        source=crosswalk[row["source_record_id"]]; expected=f"{row['ring']}:GROVE_{row['grove_number']}"
        ok=source["primary_eligible"]=="1" and bool(source["current_locus"]) and source["current_page"]==row["page"] and source["position_key"]==expected
        gs=sorted(group_lookup.get(source["current_locus"],()), key=lambda v:int(v["consensus_group_index"])) if ok else []
        reason="NONE"
        if not ok: reason="CROSSWALK_NOT_STRICT"
        elif not gs: reason="NO_CONSENSUS"
        elif any(v["page"]!=row["page"] or v["kind"]!="L" or v["grammar_scope"]!="DIAGNOSTIC_NONPROSE" or v["strict_zero_alternative"]!="1" or not v["family_surface"] for v in gs): reason="NONSTRICT_CONSENSUS"
        elif [int(v["consensus_group_index"]) for v in gs]!=list(range(1,len(gs)+1)): reason="NONCONTIGUOUS_CONSENSUS"
        elif {int(v["consensus_group_count"]) for v in gs}!={len(gs)}: reason="INCONSISTENT_CONSENSUS_COUNT"
        if reason=="NONE": strict_rows.append(row)
        else: exclusions[row["source_record_id"]]=reason
    strata=defaultdict(list)
    for row in strict_rows: strata[f"{row['page']}|{row['ring']}"].append(row)
    mixed={k:v for k,v in strata.items() if {r["tail_state"] for r in v}=={"TAIL","NO_TAIL"}}
    selected=[r for values in mixed.values() for r in values]
    folios={f:dict(sorted(Counter(r["tail_state"] for r in selected if r["physical_folio"]==f).items())) for f in sorted({r["physical_folio"] for r in selected})}
    check("strict_count", len(strict_rows)==39)
    check("mixed_strata", sorted(mixed)==["f72r3|INNER","f72r3|MIDDLE","f72r3|OUTER","f73r|OUTER"])
    check("selected_count", len(selected)==33 and Counter(r["tail_state"] for r in selected)==Counter({"NO_TAIL":17,"TAIL":16}))
    check("folio_counts", folios=={"f72":{"NO_TAIL":7,"TAIL":15},"f73":{"NO_TAIL":10,"TAIL":1}})
    check("cyclic_worlds", math.prod(len(v) for v in mixed.values())==4158)
    f70=crosswalk["STOLFI_BEST_0425"]
    check("f70_no_strict_rescue", f70["primary_eligible"]=="0" and f70["position_key"]=="")
    result=json.loads(RESULT.read_text(encoding="utf-8"))
    check("result_status", result["status"]=="STOP_UNSCORED_SINGLE_POSITIVE_SECOND_FOLIO")
    check("failed_replication_gate", result["gates"]["at_least_two_strict_examples_of_each_state_per_physical_folio"] is False)
    check("zero_features_and_scores", result["counts"]["formal_features_constructed"]==0 and result["counts"]["formal_associations_scored"]==0)
    check("result_projection_binding", result["inputs"]["results/zst001_zodiac_star_tail_state_projection.tsv"]==sha(PROJECTION))
    check("report_status", "STOP_UNSCORED_SINGLE_POSITIVE_SECOND_FOLIO" in REPORT.read_text(encoding="utf-8"))
    validation={
        "experiment":"ZST001_ZODIAC_STAR_TAIL_NATIVE_VISUAL_CAPACITY_VALIDATION",
        "status":"PASS_INDEPENDENT_RECONSTRUCTION",
        "validated_status":result["status"],
        "check_count":len(checks),
        "checks":checks,
        "source_result_sha256":sha(RESULT),
        "source_report_sha256":sha(REPORT),
        "claim_ceiling":result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    OUT_MD.write_text(
        "# ZST001 star-tail capacity validation\n\n"
        f"Status: **PASS_INDEPENDENT_RECONSTRUCTION** ({len(checks)} checks).\n\n"
        "The source correction, strict joins, four mixed strata, f73 singleton-positive stop, f70 exclusion, and zero-score contract reconstruct exactly.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
