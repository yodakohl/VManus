#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RESULTS = BASE / "results"
METHOD = BASE / "PVO001_PHARMA_VISIBLE_OWNERSHIP_CENSUS_METHOD.md"
PANEL = RESULTS / "pvo001_pharma_visible_ownership_selection.tsv"
OUT_TSV = RESULTS / "pvo001_pharma_visible_ownership_result.tsv"
OUT_JSON = RESULTS / "pvo001_pharma_visible_ownership_result.json"
OUT_MD = RESULTS / "pvo001_pharma_visible_ownership_result_report.md"

OBS = {
    "PV0B664D19": ("OWNER_ABSENT", 0, "LABELS_NEAR_MULTIPLE_FRAGMENTS_WITHOUT_CONNECTOR_ENCLOSURE_OR_INSIDE_BODY_PLACEMENT"),
    "PV1BA00478": ("OWNER_ABSENT", 0, "COMBINED_CANVAS_HAS_NEARBY_LABELS_AND_PROSE_BUT_NO_SINGULAR_VISIBLE_OWNERSHIP_DEVICE"),
    "PV5FBEFAA6": ("OWNER_ABSENT", 0, "MANY_SHORT_LABELS_ADJACENT_TO_FRAGMENTS_WITHOUT_CONNECTOR_CELL_OR_INSIDE_BODY_PLACEMENT"),
    "PV6348C446": ("OWNER_ABSENT", 0, "SHORT_LABELS_OCCUPY_WHITESPACE_BETWEEN_FRAGMENTS_WITHOUT_SINGULAR_VISIBLE_DEVICE"),
    "PV7958C95C": ("OWNER_ABSENT", 0, "LABELS_NEAR_ROOT_FORMS_WITHOUT_CONNECTOR_ENCLOSURE_OR_INSIDE_BODY_PLACEMENT"),
    "PV90337007": ("OWNER_ABSENT", 0, "SPARSE_ROOT_FRAGMENTS_AND_TEXT_REMAIN_UNCONNECTED_AND_UNENCLOSED"),
    "PVA1D1B3C5": ("OWNER_ABSENT", 0, "THREE_PAGE_SPREAD_USES_PROSE_AND_WHITESPACE_PROXIMITY_WITHOUT_SINGULAR_VISIBLE_DEVICE"),
    "PVAD2C8158": ("OWNER_ABSENT", 0, "MULTIPLE_FRAGMENT_ROWS_HAVE_NEARBY_LABELS_BUT_NO_CONNECTOR_CELL_OR_INSIDE_BODY_PLACEMENT"),
    "PVB0038D21": ("OWNER_ABSENT", 0, "LABELS_ABOVE_AND_BETWEEN_ROOT_FORMS_WITHOUT_AUTHOR_VISIBLE_SINGULAR_JOIN"),
    "PVBF6CD577": ("OWNER_PRESENT", 1, "ONE_MULTILINE_INSCRIPTION_IS_VISIBLY_PLACED_WITHIN_THE_SINGLE_LARGE_GREEN_FOLDED_PLANT_BODY_AT_BOTTOM"),
    "PVD339FB60": ("OWNER_ABSENT", 0, "ROOT_FORM_LABELS_AND_PROSE_HAVE_NO_CONNECTOR_ENCLOSURE_OR_INSIDE_BODY_PLACEMENT"),
    "PVE7B0A3F3": ("OWNER_ABSENT", 0, "PLANT_FRAGMENTS_AND_PROSE_ARE_SEPARATE_WITHOUT_SINGULAR_VISIBLE_JOIN"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    panel = list(csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t"))
    assert {row["opaque_id"] for row in panel} == set(OBS)
    rows = []
    for source in sorted(panel, key=lambda row: row["opaque_id"]):
        request = urllib.request.Request(source["review_image_url"], headers={"User-Agent": "VManus-PVO001-result/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response: raw = response.read()
        state, count, basis = OBS[source["opaque_id"]]
        rows.append({"opaque_id": source["opaque_id"], "canvas_id": source["canvas_id"], "quire": source["quire"], "outside_prior_mixed_folios": source["outside_prior_mixed_folios"], "review_image_sha256": hashlib.sha256(raw).hexdigest(), "visible_owner_state": state, "visible_owner_device_count": count, "visual_basis": basis})
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    counts = Counter(row["visible_owner_state"] for row in rows)
    present = [row for row in rows if row["visible_owner_state"] == "OWNER_PRESENT"]
    devices = sum(int(row["visible_owner_device_count"]) for row in rows)
    gates = {
        "at_least_four_owner_present_canvases": len(present) >= 4,
        "both_q15_and_q19_have_owner_present": {row["quire"] for row in present} == {"q15", "q19"},
        "owner_present_outside_prior_mixed_folios": any(row["outside_prior_mixed_folios"] == "1" for row in present),
        "at_least_six_visible_owner_devices": devices >= 6,
        "at_most_two_uncertain": counts["UNCERTAIN"] <= 2,
    }
    result = {"experiment": "PVO001_PHARMA_VISIBLE_OWNERSHIP_RESULT", "schema": "PVO001_RESULT_V1", "status": "STOP_COMPLETE_CENSUS_ONLY_ONE_VISIBLE_OWNER_CANVAS", "decision": "CLOSE_BEFORE_OBJECT_STATE_MAPPING_OR_TRANSCRIPTION", "counts": {"canvases": len(rows), "OWNER_PRESENT": counts["OWNER_PRESENT"], "OWNER_ABSENT": counts["OWNER_ABSENT"], "UNCERTAIN": counts["UNCERTAIN"], "visible_owner_devices": devices, "owner_present_quires": sorted({row["quire"] for row in present}), "owner_present_outside_prior_mixed_folios": sum(row["outside_prior_mixed_folios"] == "1" for row in present)}, "gates": gates, "failed_gates": [name for name, passed in gates.items() if not passed], "access": {"canvases_inspected_once": True, "voynich_transcription_opened": False, "label_identity_or_formal_feature_opened": False, "ocr_clip_embedding_or_automated_vision_used": False, "machine_authored_source_bound_native_inspection": True}, "inputs": {str(METHOD.relative_to(ROOT)): sha(METHOD), str(PANEL.relative_to(ROOT)): sha(PANEL)}, "observations_sha256": sha(OUT_TSV), "claim_ceiling": "One of twelve official pharmaceutical canvases contains one strict author-visible singular owner device. This is far below the frozen capacity gate and licenses no object-state mapping or transcription access. It supplies no label meaning, ROOT or LEAF word, plant identity, plaintext, or translation."}
    assert result["counts"] == {"canvases": 12, "OWNER_PRESENT": 1, "OWNER_ABSENT": 11, "UNCERTAIN": 0, "visible_owner_devices": 1, "owner_present_quires": ["q19"], "owner_present_outside_prior_mixed_folios": 1}
    assert result["failed_gates"] == ["at_least_four_owner_present_canvases", "both_q15_and_q19_have_owner_present", "at_least_six_visible_owner_devices"]
    OUT_JSON.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_MD.write_text("# PVO001 pharmaceutical visible-ownership result\n\nStatus: **STOP_COMPLETE_CENSUS_ONLY_ONE_VISIBLE_OWNER_CANVAS**.\n\nDirect inspection of all 12 frozen official canvases yields 1 `OWNER_PRESENT`, 11 `OWNER_ABSENT`, and 0 `UNCERTAIN`, with one qualifying device total. The sole positive is q19 canvas `PVBF6CD577`: a multi-line inscription is visibly placed within a single large green folded plant body at the bottom. It lies outside the already mixed PLC001 folios, so that one gate passes; however q15 has no positive canvas, only one rather than four canvases qualifies, and one rather than six devices exists.\n\nThe census therefore stops before object-state mapping, transcription, or label/formal-feature access. Whitespace proximity remains inadmissible. This supplies no label meaning, ROOT or LEAF word, plant identity, plaintext, meaning, or translation.\n", encoding="utf-8")


if __name__ == "__main__": main()
