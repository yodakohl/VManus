#!/usr/bin/env python3
"""Score the corrected frozen GDT130 target after source-aware localization."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREDICTION = ROOT / "gdt130_prediction.json"
LOCALIZATION = ROOT / "gdt130_localization.json"
REVIEWS = ROOT / "gdt130_blind_crop_reviews.tsv"
SCORED = ROOT / "gdt130_scored_prediction.tsv"
REPORT = ROOT / "GDT130_QOKAL_SHEDY_RAY_TRANSFER_REPORT.md"
RESULT = ROOT / "gdt130_result.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    localization = json.loads(LOCALIZATION.read_text(encoding="utf-8"))
    reviews = read(REVIEWS)
    assert prediction["status"] == "CORRECTED_FROZEN_BEFORE_F116R_LINE_TO_STAR_LOCALIZATION"
    assert localization["status"] == "SECURE_LINE23_TO_STAR09_LOCALIZATION"
    assert localization["selected_star_ordinal"] == 9
    assert len(reviews) == 2 and {int(row["rays"]) for row in reviews} == {8, 9}
    assert all(row["target_id"] == prediction["target"]["target_id"] for row in reviews)
    assert all(row["crop_sha256"] == localization["image"]["crop_sha256"] for row in reviews)
    predicted = int(prediction["target"]["prediction"]["rays"])
    reviewer_counts = [int(row["rays"]) for row in reviews]
    hit_by_reviewer = [value == predicted for value in reviewer_counts]
    assert not any(hit_by_reviewer)
    status = "QOKAL_SHEDY_SEVEN_RAY_TRANSFER_FAILED_VISUAL_COUNT_8_OR9"
    scored = [{
        "target_id": prediction["target"]["target_id"], "page": "f116r", "formal_locus": "f116r.23",
        "selected_star_ordinal": localization["selected_star_ordinal"], "formal_primary": "qokal|shedy",
        "formal_reference": "qokal|sheedy", "predicted_rays": predicted,
        "reviewer_ray_counts": ",".join(map(str, reviewer_counts)), "visual_consensus": "UNRESOLVED_8_OR_9",
        "prediction_supported_by_any_reviewer": int(any(hit_by_reviewer)),
        "prediction_rejected_by_all_reviewers": int(not any(hit_by_reviewer)),
        "decision": "FAILED_INVARIANT_TO_8_VS_9_ADJUDICATION",
    }]
    write(SCORED, scored)
    REPORT.write_text(f"""# GDT130 — corrected `qokal | shedy` ray transfer

Status: **{status}**

The invalid paragraph-6 → star-6 binding was discarded before scoring. The
publicly corrected nearest-line rule securely localized f116r.23 to marginal
star **9**, and two fresh crop-only reviewers then counted **9** and **8**
rays on the same hashed crop. They disagree on the exact visible count, but
neither sees the frozen **7 rays**. The prediction therefore fails regardless
of adjudication; a third reviewer could not change that decision.

This is a useful falsifier. The exact primary-view near-minimal contrast
`qokal | sheedy` → 8 versus `qokal | shedy` → 7 does not transfer to f116r.
The GDT129 `q* | sheedy` 8-ray pattern remains a small post-reveal descriptive
lead, but the proposed `e/ee` visual-class interpretation is rejected. RF1b's
uncertain target reading was already frozen and further weakens the contrast.

Two earlier reviewers opened the full canvas under the invalid star-6 request;
one made no count and one formed an unfinalized tentative count. Those reviews
are excluded and do not enter this result. No number, star meaning, role, word,
morpheme, POS, sound, language, plaintext, meaning, or translation follows.
f84r remained sealed and untouched.
""", encoding="utf-8")
    result = {
        "schema": "GDT130_QOKAL_SHEDY_RAY_TRANSFER_RESULT_V1", "status": status,
        "target": {"target_id": prediction["target"]["target_id"], "page": "f116r", "formal_locus": "f116r.23",
                   "selected_star_ordinal": 9, "predicted_rays": predicted, "formal_primary": "qokal|shedy",
                   "formal_reference": "qokal|sheedy", "reading_state": prediction["target"]["reading_state"]},
        "review": {"eligible_reviewers": 2, "reviewer_counts": reviewer_counts,
                   "visual_consensus": "UNRESOLVED_8_OR_9", "prediction_supported_by_any_reviewer": any(hit_by_reviewer),
                   "prediction_rejected_by_all_reviewers": not any(hit_by_reviewer),
                   "invalid_star06_reviewers_excluded": 2, "third_review_needed": False,
                   "third_review_reason": "DECISION_INVARIANT_TO_8_VS_9_ADJUDICATION"},
        "interpretation": "The postselected qokal sheedy/shedy near-minimal ray-class rule failed on the corrected target.",
        "claim_ceiling": "One failed postselected visual transfer; no number, star meaning, role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("opened", "retained", "queried", "joined", "scored", "targeted", "assigned", "predicted")},
        "inputs": {PREDICTION.name: sha(PREDICTION), "gdt130_prediction_validation.json": sha(ROOT / "gdt130_prediction_validation.json"),
                   LOCALIZATION.name: sha(LOCALIZATION), "gdt130_localization_validation.json": sha(ROOT / "gdt130_localization_validation.json"),
                   REVIEWS.name: sha(REVIEWS), "gdt129_result.json": sha(ROOT / "gdt129_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {SCORED.name: sha(SCORED)}, "documents": {REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "predicted": predicted, "reviewers": reviewer_counts}, sort_keys=True))


if __name__ == "__main__":
    main()
