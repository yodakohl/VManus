#!/usr/bin/env python3
"""Independent compact validation of the NVA001 route-worth stop."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
RESULT = RES / "nva001_native_visual_next_route_worth.json"
REPORT = RES / "nva001_native_visual_next_route_worth_report.md"
OUT = RES / "nva001_native_visual_next_route_worth_validation.json"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["canonical_result"] = RESULT.read_bytes() == canonical(result)
    checks["result_and_report_bound"] = sha(RESULT) != sha(REPORT)

    ledger = {row["experiment"]: row["status"] for row in rows(BASE / "ACTIVE_EXPERIMENT_LEDGER.tsv")}
    expected_statuses = {
        "attached_label_v2_final": "FINAL_VALIDATED_NARROW_NONCONFIRMATION",
        "LM001Y_final_residual_leaf_margin_census_result": "PASS_COMBINED_VISUAL_CAPACITY_ALL_ORIGINAL_GATES",
        "LM002_synthetic_calibration": "STOP_SYNTHETIC_INSTRUMENT_FAILED",
        "SME003_independent_full_calibration_validation": "PASS_402_CASE_TARGET_FREE_RECONSTRUCTION_FAIL_CLOSE_CONFIRMED",
        "f66r_border_permitted_evidence_audit": "PASS_PHYSICAL_HIERARCHY_FUNCTION_UNKNOWN",
        "RFH001_f73v_retracer_hook": "PASS_ONE_VISIBLE_HOOK_BEARING_UNDERSTROKE_AND_HOOKLESS_RETRACING",
        "RBR002_complete_outer_ring_underlayer_capacity": "STOP_INSUFFICIENT_COMPLETE_UNDERLAYER_RECOVERY_CAPACITY",
        "DRI002_discordant_cell_role_capacity_result": "STOP_ONE_OF_TWO_CELLS_LACKS_REPLICATED_ROLE_MOBILITY",
    }
    checks["completed_route_statuses"] = (
        result["prerequisite_route_statuses"] == expected_statuses
        and {key: ledger[key] for key in expected_statuses} == expected_statuses
    )

    annotations = rows(RES / "existing_human_exact_locus_annotations.tsv")
    names = ("REL_EXPLICIT_ATTACHMENT", "REL_ENCLOSURE", "REL_OVERLAP_OR_CONTACT")
    counts = {}
    per_unit = defaultdict(set)
    for name in names:
        picked = []
        for row in annotations:
            tags = set(filter(None, row["local_relation_tags"].split(";")))
            if row["certainty"] == "UNHEDGED" and row["relation_scope"] == "EXACT_LOCAL_COMMENT" and name in tags:
                picked.append(row)
                per_unit[(row["page"], row["unit"])].add(name)
        counts[name] = (len(picked), len({(row["page"], row["unit"]) for row in picked}))
    checks["strong_relation_counts"] = counts == {
        "REL_EXPLICIT_ATTACHMENT": (51, 6),
        "REL_ENCLOSURE": (48, 10),
        "REL_OVERLAP_OR_CONTACT": (8, 6),
    }
    checks["zero_mixed_strong_units"] = not any(len(value) >= 2 for value in per_unit.values())

    retracing = [row for row in annotations if re.search(r"\bretrac", row["local_comment"], re.I)]
    strict = [row for row in retracing if re.search(r"original hook.*retracer did not", row["local_comment"], re.I)]
    checks["retracing_census"] = len(retracing) == 9 and [(row["page"], row["locus"]) for row in strict] == [("f73v", "f73v.15")]

    page_rows: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for row in rows(RES / "existing_human_locus_roles.tsv"):
        page_rows.setdefault(row["page"], []).append(row)
    cell_pages = []
    for page, items in page_rows.items():
        template = "".join(kind for kind, _ in itertools.groupby(item["kind"] for item in items))
        if (items[0]["section"], template) == ("T", "P"):
            cell_pages.append(page)
    checks["text_cell_complete"] = cell_pages == ["f1r", "f85r1", "f86v6", "f86v5"]
    dri = json.loads((RES / "dri001_paired_document_role_inventory_result.json").read_text())
    cell = next(item for item in dri["cells"] if item["cell_id"] == "DRC13")
    public = {row["page"]: row for row in rows(RES / "public_voynich_nu_page_annotations_v2.tsv")}
    f1r = " ".join((public["f1r"]["general_description"], public["f1r"]["text_description"])).lower()
    checks["text_cell_role_ceiling"] = (
        cell["calibration_role"] == cell["diagnostic_role"] == "PROSE_DOMINANT"
        and "text-only page" in f1r and "four paragraphs" in f1r and "fill the entire page" in f1r
    )

    registry = rows(RES / "translation_anchor_acquisition_registry_v1.tsv")
    checks["zero_of_eleven_admissible_anchors"] = len(registry) == 11 and sum(row["admissible"] == "1" for row in registry) == 0
    checks["seven_stops_and_no_access"] = (
        len(result["candidate_checks"]) == 7
        and all(not item["new_image_access_authorized"] for item in result["candidate_checks"].values())
        and not any(result["access"].values())
    )
    checks["decision_and_ceiling"] = (
        result["status"] == "STOP_NO_GENUINELY_NEW_CAPACITY_QUALIFIED_NATIVE_VISUAL_ROUTE"
        and result["decision"] == "REQUIRE_NEW_READABLE_OR_PHYSICAL_LAYER_EVIDENCE"
        and "no word" in result["claim_ceiling"].lower()
        and "translation" in result["claim_ceiling"].lower()
    )
    expected_inputs = {key: sha(ROOT / key) for key in result["inputs"]}
    checks["all_input_hashes"] = expected_inputs == result["inputs"]
    if not all(checks.values()):
        raise SystemExit({key: value for key, value in checks.items() if not value})
    payload = {
        "experiment": "NVA001_NATIVE_VISUAL_NEXT_ROUTE_WORTH_VALIDATION",
        "status": "PASS_12_CHECK_INDEPENDENT_ROUTE_STOP_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "source_result_sha256": sha(RESULT),
        "source_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms the route-worth stop and opens no image, filler, word, meaning, plaintext, or translation.",
    }
    OUT.write_bytes(canonical(payload))
    print(json.dumps({"status": payload["status"], "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
