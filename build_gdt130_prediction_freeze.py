#!/usr/bin/env python3
"""Build the GDT130 f116r near-minimal visual prediction before image access."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
CATALOGUE = ROOT / "experiments/semantic_assumptions/cache/public_voynich_nu_catalogue/q20.html"
PREDICTION_TSV = ROOT / "gdt130_frozen_prediction.tsv"
METHOD = ROOT / "GDT130_QOKAL_SHEDY_RAY_TRANSFER_METHOD.md"
OUT = ROOT / "gdt130_prediction.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def main():
    groups = {}
    paragraph_starts = []
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] != "f116r":
                continue
            if row["edition"] == "ZL3b" and row["source_group_index"] == "1" and row["paragraph_start"] == "1":
                paragraph_starts.append(row["locus"])
            if row["locus"] == "f116r.23" and row["source_group_index"] in {"5", "6"}:
                groups[(row["edition"], int(row["source_group_index"]))] = row["ivtff_group_raw"]
    assert groups[("ZL3b", 5)] == groups[("IT2a", 5)] == groups[("RF1b", 5)] == "qokal"
    assert groups[("ZL3b", 6)] == groups[("IT2a", 6)] == "shedy"
    assert groups[("RF1b", 6)] == "she@152;y"
    assert paragraph_starts[5] == "f116r.18"
    assert int("f116r.18".split(".")[1]) <= 23 < int(paragraph_starts[6].split(".")[1])
    catalogue = CATALOGUE.read_text(encoding="latin-1")
    assert 'ID="f116r"' in catalogue and "child_oid=1006276" in catalogue
    frozen = list(csv.DictReader(PREDICTION_TSV.open(encoding="utf-8"), delimiter="\t"))
    assert len(frozen) == 1 and frozen[0]["predicted_rays"] == "7"
    assert frozen[0]["star_ordinal"] == "UNRESOLVED_BEFORE_LOCALIZATION"
    result = {
        "schema": "GDT130_QOKAL_SHEDY_RAY_TRANSFER_PREDICTION_V1",
        "status": "CORRECTED_FROZEN_BEFORE_F116R_LINE_TO_STAR_LOCALIZATION",
        "target": {
            "target_id": "GDT130_F116R_LINE23_NEAREST_STAR", "page": "f116r", "physical_folio": "f116",
            "star_ordinal": "UNRESOLVED_BEFORE_LOCALIZATION", "formal_locus": "f116r.23", "formal_group_indices": [5, 6],
            "visual_binding": "MARGINAL_STAR_VERTICAL_CENTER_NEAREST_SIXTH_LINE_OF_LONG_SIXTH_PARAGRAPH",
            "readings": {"ZL3b": ["qokal", "shedy"], "IT2a": ["qokal", "shedy"], "RF1b": ["qokal", "she@152;y"]},
            "reading_state": "ZL_IT_EXACT_RF_UNCERTAIN",
            "prediction": {"rays": 7, "tail": "UNPREDICTED", "color": "UNPREDICTED"},
            "canvas_id": "1006276",
            "image_url": "https://collections.library.yale.edu/iiif/2/1006276/full/full/0/default.jpg",
        },
        "near_minimal_pair": {
            "reference_target": "GDT128_F103R_STAR15", "reference_form": "qokal|sheedy",
            "reference_consensus_rays": 8, "target_form_primary": "qokal|shedy",
            "formal_difference": "SECOND_GROUP_PAGE_HOST_EE_TO_E_IN_PRIMARY_READINGS",
        },
        "postselection": {"gdt128_target_used": True, "gdt129_local_rule_used": True, "pristine_blind": False},
        "correction": {
            "invalidated_binding": "PARAGRAPH_ORDINAL_6_EQUALS_STAR_ORDINAL_6",
            "reason": "TEN_STARS_BUT_EIGHT_PARAGRAPHS_AND_MULTIPLE_STARS_ALONG_LONG_PARAGRAPH",
            "invalid_ordinal6_prediction_scored": False,
        },
        "target_access": {
            "canvas_opened_by_two_reviewers_under_invalid_instruction": True,
            "invalid_reviewer_a_completed_count": False,
            "invalid_reviewer_b_tentative_unfinalized_count": 8,
            "correct_line23_owned_star_localized_at_freeze": False,
            "correct_target_ray_state_reviewed_at_freeze": False,
        },
        "claim_ceiling": "One postselected near-minimal visual transfer only; no number, star meaning, role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("opened", "retained", "queried", "joined", "scored", "targeted", "predicted")},
        "inputs": {str(SOURCE.relative_to(ROOT)): sha(SOURCE), str(CATALOGUE.relative_to(ROOT)): sha(CATALOGUE), "gdt128_result.json": sha(ROOT / "gdt128_result.json"), "gdt129_result.json": sha(ROOT / "gdt129_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {PREDICTION_TSV.name: sha(PREDICTION_TSV)},
        "documents": {METHOD.name: sha(METHOD)},
    }
    result["prediction_content_sha256"] = csha(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "target": result["target"]}, sort_keys=True))


if __name__ == "__main__":
    main()
