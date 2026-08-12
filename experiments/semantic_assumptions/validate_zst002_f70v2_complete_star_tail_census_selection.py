#!/usr/bin/env python3
"""Independently validate the ZST002 source-only complete selection."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "ZST002_F70V2_COMPLETE_STAR_TAIL_CENSUS_METHOD.md"
CROSSWALK = RES / "existing_human_current_locus_crosswalk.tsv"
GROUPS = RES / "source_sta_family_consensus_groups.tsv"
ZST001 = RES / "zst001_zodiac_star_tail_native_visual_capacity.json"
PRODUCER = BASE / "build_zst002_f70v2_complete_star_tail_census_selection.py"
RESULT = RES / "zst002_f70v2_complete_star_tail_census_selection.json"
REPORT = RES / "zst002_f70v2_complete_star_tail_census_selection_report.md"
OUT = RES / "zst002_f70v2_complete_star_tail_census_selection_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text())
    cross = [r for r in tsv(CROSSWALK) if r["source_page"] == "f70v2" and r["source_unit"] in {"s1", "s2"}]
    groups = defaultdict(list)
    for row in tsv(GROUPS):
        groups[row["locus"]].append(row)
    strict = {}
    reasons = {}
    for row in cross:
        ring = "OUTER" if row["source_unit"] == "s1" else "INNER"
        values = sorted(groups.get(row["current_locus"], []), key=lambda x: int(x["consensus_group_index"]))
        if row["primary_eligible"] != "1" or not re.fullmatch(ring + r":GROVE_[1-9][0-9]*", row["position_key"]):
            ok, reason = False, "CROSSWALK_NOT_STRICT"
        elif not values:
            ok, reason = False, "NO_CONSENSUS"
        elif any(x["page"] != "f70v2" or x["kind"] != "L" or x["grammar_scope"] != "DIAGNOSTIC_NONPROSE" or x["strict_zero_alternative"] != "1" or not x["family_surface"] for x in values):
            ok, reason = False, "NONSTRICT_CONSENSUS"
        elif [int(x["consensus_group_index"]) for x in values] != list(range(1, len(values) + 1)) or {int(x["consensus_group_count"]) for x in values} != {len(values)}:
            ok, reason = False, "NONCONTIGUOUS_CONSENSUS"
        else:
            ok, reason = True, "NONE"
        strict[row["source_record_id"]] = ok
        if not ok:
            reasons[row["source_record_id"]] = reason
    observed = result["rows"]
    checks = {
        "canonical_result": RESULT.read_bytes() == (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "exact_complete_29_slot_order": [(r["source_unit"], r["source_item"]) for r in cross] == [("s1", str(i)) for i in range(1, 20)] + [("s2", str(i)) for i in range(1, 11)],
        "row_ids_and_order_reconstructed": [r["source_record_id"] for r in observed] == [r["source_record_id"] for r in cross],
        "cyclic_position_keys_preserved": [r["grove_number"] for r in observed] == [str(i) for i in range(2, 20)] + ["1", "9", "10"] + [str(i) for i in range(1, 9)],
        "strict_mask_reconstructed": {r["source_record_id"]: r["strict_eligible"] for r in observed} == strict,
        "strict_counts_25_16_9": result["counts"]["strict_slots"] == 25 and result["counts"]["strict_by_ring"] == {"INNER": 9, "OUTER": 16},
        "four_exact_exclusions": result["counts"]["strict_exclusions"] == reasons and len(reasons) == 4,
        "exact_canvas_and_complete_rule": result["canvas"]["canvas_id"] == "1006200" and result["canvas"]["official_dimensions"] == [3945, 3772] and result["counts"]["selected_slots"] == 29,
        "all_inputs_bound": result["inputs"] == {str(p.relative_to(ROOT)): sha(p) for p in (METHOD, CROSSWALK, GROUPS, ZST001)},
        "visual_and_formal_targets_sealed": result["access"]["selected_image_body_opened_by_builder"] is False and result["access"]["surface_family_member_root_parser_role_or_formal_association_serialized"] is False,
        "fixed_gate_and_ceiling": result["capacity_gate"].startswith("AT_LEAST_ONE_MIXED") and "translation" in result["claim_ceiling"],
        "report_present": REPORT.is_file() and "25 are strict-capacity eligible" in REPORT.read_text(),
    }
    if not all(checks.values()):
        raise SystemExit({k: v for k, v in checks.items() if not v})
    output = {
        "experiment": "ZST002_F70V2_COMPLETE_STAR_TAIL_CENSUS_SELECTION_VALIDATION",
        "schema": "ZST002_SELECTION_VALIDATION_V1",
        "status": "PASS_11_CHECK_INDEPENDENT_COMPLETE_SELECTION_RECONSTRUCTION",
        "check_count": len(checks), "checks": list(checks),
        "producer_sha256": sha(PRODUCER), "validated_result_sha256": sha(RESULT),
        "reconstructed": {"slots": 29, "strict": 25, "strict_by_ring": {"OUTER": 16, "INNER": 9}, "exclusions": reasons},
        "claim_ceiling": "Validation authorizes only complete f70v2 native-visual grading and supplies no word meaning plaintext or translation.",
    }
    OUT.write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
