#!/usr/bin/env python3
"""Score the publicly frozen GDT128 f103r visual transfer."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREDICTION = ROOT / "gdt128_prediction.json"
PREDICTION_VALIDATION = ROOT / "gdt128_prediction_validation.json"
REVIEWS = ROOT / "gdt128_blind_visual_reviews.tsv"
SCORED = ROOT / "gdt128_scored_prediction.tsv"
REPORT = ROOT / "GDT128_Q20_QOKAL_SHEEDY_TRANSFER_REPORT.md"
RESULT = ROOT / "gdt128_result.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()


def read_tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, rows):
    fields = list(rows[0])
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def majority(values):
    counts = Counter(values)
    value, support = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    return value, support, counts


def main():
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    assert prediction["status"] == "FROZEN_BEFORE_F103R_STAR15_VISUAL_REVIEW"
    reviews = read_tsv(REVIEWS)
    assert len(reviews) == 3
    assert {row["reviewer_id"] for row in reviews} == {"GDT128_BLIND_A", "GDT128_BLIND_B", "GDT128_BLIND_C"}
    assert all(row["page"] == "f103r" and row["star_ordinal"] == "15" for row in reviews)
    assert len({row["image_sha256"] for row in reviews}) == 1

    ray_value, ray_support, ray_counts = majority([int(row["rays"]) for row in reviews])
    tail_value, tail_support, tail_counts = majority([int(row["tail"]) for row in reviews])
    frozen = prediction["target"]["prediction"]
    ray_hit = ray_value == int(frozen["rays"])
    tail_hit = tail_value == int(frozen["tail"])
    exact_hit = ray_hit and tail_hit
    status = "Q20_QOKAL_SHEEDY_RAY_TRANSFER_HIT_TAIL_TRANSFER_FAILED"

    scored = [{
        "target_id": prediction["target"]["target_id"],
        "page": "f103r",
        "star_ordinal": "15",
        "formal_field_locus": prediction["target"]["formal_field_locus"],
        "formal_tokens": "|".join(prediction["target"]["formal_tokens"]),
        "predicted_rays": str(frozen["rays"]),
        "reviewer_ray_counts": ",".join(row["rays"] for row in reviews),
        "consensus_rays": str(ray_value),
        "ray_consensus_support": f"{ray_support}/3",
        "ray_prediction_hit": str(int(ray_hit)),
        "predicted_tail": str(frozen["tail"]),
        "reviewer_tail_counts": ",".join(row["tail"] for row in reviews),
        "consensus_tail": str(tail_value),
        "tail_consensus_support": f"{tail_support}/3",
        "tail_prediction_hit": str(int(tail_hit)),
        "exact_joint_prediction_hit": str(int(exact_hit)),
        "color_prediction": frozen["color"],
        "review_protocol": "TWO_FRESH_BLIND_REVIEWS_PLUS_THIRD_AFTER_RAY_DISAGREEMENT",
        "interpretation": "RAY_CLASS_HIT_TAIL_AND_EXACT_STATE_FAILED_SINGLE_POSTSELECTED_TARGET",
    }]
    write_tsv(SCORED, scored)

    REPORT.write_text(f"""# GDT128 — f103r `qokal | sheedy` visual transfer

Status: **{status}**

The publicly committed prediction was **8 rays, 1 tail** for f103r star-record
15. Three fresh, source-free native-image reviewers counted rays as
**8, 7, 8** and tails as **0, 0, 0** on the same official Yale image hash.
The descriptive majority is therefore **8 rays (2/3)** and **0 tails (3/3)**.

The ray-class prediction hits, the tail prediction fails, and the exact joint
prediction fails. The third reviewer was requested only after the first two
reviewers disagreed on 7 versus 8 rays; majority adjudication was not part of
the original formal freeze and is reported transparently. No reviewer saw the
formal tokens or predicted values. Reviewer disagreement shows that even the
ray hit is visually less secure than a unanimous count.

This preserves a narrow YOLO lead: a q-routed two-field form ending in exact
`sheedy` again co-occurs with the coarse 8-ray class. It does **not** preserve
the proposed 1-tail state, does not establish a reusable visual code, and has
only one postselected prospective target. A second independently frozen target
would be required before treating the ray association as more than a risky
lead.

No star meaning, number, role, word, morpheme, POS, sound, language, plaintext,
meaning, or translation follows. f84r remained sealed and untouched.
""", encoding="utf-8")

    result = {
        "schema": "GDT128_Q20_QOKAL_SHEEDY_TRANSFER_RESULT_V1",
        "status": status,
        "target": prediction["target"],
        "review": {
            "reviewers": 3,
            "protocol": "TWO_FRESH_BLIND_REVIEWS_PLUS_THIRD_AFTER_RAY_DISAGREEMENT",
            "third_reviewer_trigger": "FIRST_TWO_DISAGREED_ON_RAYS",
            "ray_counts": dict(sorted((str(k), v) for k, v in ray_counts.items())),
            "ray_consensus": ray_value,
            "ray_consensus_support": ray_support,
            "tail_counts": dict(sorted((str(k), v) for k, v in tail_counts.items())),
            "tail_consensus": tail_value,
            "tail_consensus_support": tail_support,
            "same_image_hash": True,
            "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        },
        "score": {
            "ray_prediction_hit": ray_hit,
            "tail_prediction_hit": tail_hit,
            "exact_joint_prediction_hit": exact_hit,
            "statistical_inference": "NONE_SINGLE_POSTSELECTED_TARGET",
        },
        "interpretation": "One risky coarse ray-class hit accompanied by a unanimous tail failure and a failed exact joint state.",
        "claim_ceiling": "One provenance-qualified postselected visual lead only; no star meaning, number, role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("opened", "retained", "queried", "joined", "scored", "targeted", "assigned", "predicted")},
        "inputs": {
            PREDICTION.name: sha(PREDICTION),
            PREDICTION_VALIDATION.name: sha(PREDICTION_VALIDATION),
            REVIEWS.name: sha(REVIEWS),
            "gdt127_result.json": sha(ROOT / "gdt127_result.json"),
        },
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {SCORED.name: sha(SCORED)},
        "documents": {REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = content_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "rays": ray_value, "tail": tail_value, "ray_hit": ray_hit, "tail_hit": tail_hit}, sort_keys=True))


if __name__ == "__main__":
    main()
