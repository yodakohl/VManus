#!/usr/bin/env python3
"""Independent record-integrity validator for the GDT002 contact/gap result."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xywh(value: str) -> tuple[int, int, int, int]:
    values = tuple(map(int, value.split(",")))
    if len(values) != 4:
        raise ValueError(value)
    return values


selection = rows("gdt002_contact_gap_selection.tsv")
localizations = rows("gdt002_contact_gap_localizations.tsv")
observations = rows("gdt002_contact_gap_observations.tsv")
result = json.loads((ROOT / "gdt002_contact_gap_result.json").read_text())
checks: dict[str, bool] = {}

checks["cardinality_12"] = len(selection) == len(localizations) == len(observations) == 12
checks["target_order_exact"] = [r["target_id"] for r in selection] == [r["target_id"] for r in localizations] == [r["target_id"] for r in observations]
checks["selection_fields_preserved"] = all(
    all(loc[key] == sel[key] for key in sel) for sel, loc in zip(selection, localizations)
)
checks["full_hashes_canvas_consistent"] = {
    (r["canvas_id"], r["full_image_sha256"]) for r in localizations
} == {
    ("1006233", "3b553c70d0c068cb39a276d391127165c5d9d868ec08e7f5eb2e73b32bb95d1e"),
    ("1006247", "111f6dfc34b8ecb9230cb5a0d144afef4cbd788048ddda2f440108941c91d5e5"),
    ("1006248", "6dcf72a0d7eac14da2232987c9cc1521e6d70c9f0f92d3eb39b55fc075520429"),
}
checks["coordinates_positive_in_bounds"] = all(
    all(v >= 0 for v in xywh(r[field])[:2])
    and xywh(r[field])[2] > 0 and xywh(r[field])[3] > 0
    and xywh(r[field])[0] + xywh(r[field])[2] <= int(r["width"])
    and xywh(r[field])[1] + xywh(r[field])[3] <= int(r["height"])
    for r in localizations for field in ("context_xywh", "target_xywh")
)
checks["target_inside_context"] = all(
    (lambda c, t: c[0] <= t[0] and c[1] <= t[1] and t[0] + t[2] <= c[0] + c[2] and t[1] + t[3] <= c[1] + c[3])(
        xywh(r["context_xywh"]), xywh(r["target_xywh"])
    ) for r in localizations
)
checks["region_urls_exact"] = all(
    r["context_region_url"] == f'https://collections.library.yale.edu/iiif/2/{r["canvas_id"]}/{r["context_xywh"]}/full/0/default.jpg'
    and r["target_region_url"] == f'https://collections.library.yale.edu/iiif/2/{r["canvas_id"]}/{r["target_xywh"]}/full/0/default.jpg'
    for r in localizations
)
checks["crop_hash_format"] = all(
    len(r[key]) == 64 and set(r[key]) <= set("0123456789abcdef")
    for r in localizations for key in ("context_sha256", "target_sha256")
)
checks["localizer_role_sealed"] = all(r["localizer_judgment_excluded"] == "CONTACT_GAP_NOT_JUDGED" for r in localizations)
checks["review_provenance_exact"] = all(
    r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION"
    and r["review_input"] == "RANDOMIZED_CONTEXT_AND_TARGET_CROPS_ONLY"
    and r["source_metadata_available_to_reviewer"] == "0"
    for r in observations
)
checks["review_state_vocab"] = {r["review_state"] for r in observations} <= {"CONTACT", "CLEAR_GAP", "UNCERTAIN"}
checks["review_notes_present"] = all(r["review_confidence"] and r["review_note"] for r in observations)

sel_by_id = {r["target_id"]: r for r in selection}
counts: dict[str, Counter[str]] = defaultdict(Counter)
for row in observations:
    counts[sel_by_id[row["target_id"]]["physical_folio"]][row["review_state"]] += 1
expected_counts = {
    folio: {state: count[state] for state in ("CONTACT", "CLEAR_GAP", "UNCERTAIN")}
    for folio, count in sorted(counts.items())
}
expected_gate = {
    folio: count["CONTACT"] >= 1 and count["CLEAR_GAP"] >= 2 and count["UNCERTAIN"] == 0
    for folio, count in expected_counts.items()
}
checks["counts_independent"] = result["counts_by_physical_folio"] == expected_counts == {
    "f100": {"CONTACT": 1, "CLEAR_GAP": 4, "UNCERTAIN": 0},
    "f89": {"CONTACT": 2, "CLEAR_GAP": 0, "UNCERTAIN": 1},
    "f99": {"CONTACT": 1, "CLEAR_GAP": 3, "UNCERTAIN": 0},
}
checks["gate_independent"] = result["capacity_gate_by_physical_folio"] == expected_gate == {"f89": False, "f99": True, "f100": True}
checks["overall_stop_independent"] = not result["capacity_gate_passed"] and result["status"] == "STOP_CAPACITY_GATE_FAILED_NO_FORMAL_COMPARISON"
checks["access_ceiling_exact"] = result["access"] == {
    "f100_formal_payload_used_to_tune_visual_calls": False,
    "formal_data_supplied_to_crop_reviewer": False,
    "formal_visual_join_or_role_solver_run": False,
    "ocr_or_automated_vision_used": False,
    "official_images_opened_after_registration": True,
    "source_aware_localizer_saw_transcription_and_formal_tables_after_registration": True,
}
checks["input_hashes"] = all(sha(ROOT / name) == digest for name, digest in result["inputs"].items())
checks["output_hashes"] = all(sha(ROOT / name) == digest for name, digest in result["outputs"].items())
checks["no_formal_payload_in_visual_rows"] = all(
    not ({"family_surface", "family_sequence", "sta_codes", "transcription"} & set(row))
    for row in localizations + observations
)

failed = [name for name, passed in checks.items() if not passed]
validation = {
    "artifact": "GDT002_CONTACT_GAP_RESULT_VALIDATION_V1",
    "status": "PASS" if not failed else "FAIL",
    "checks": checks,
    "passed": sum(checks.values()), "total": len(checks), "failed": failed,
    "result_sha256": sha(ROOT / "gdt002_contact_gap_result.json"),
    "scope": "Independent table, provenance, coordinate, arithmetic, gate, and hash validation. Visual judgments and remote crop bytes are recorded, not independently re-inspected or downloaded by this validator.",
}
(ROOT / "gdt002_contact_gap_result_validation.json").write_text(
    json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps({"status": validation["status"], "passed": validation["passed"], "total": validation["total"], "failed": failed}))
sys.exit(1 if failed else 0)
