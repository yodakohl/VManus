#!/usr/bin/env python3
"""Score the frozen GDT150 KOR/root-geometry visual transfer."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREDICTION = ROOT / "gdt150_prediction.json"
PREDICTION_VALIDATION = ROOT / "gdt150_prediction_validation.json"
TARGETS = ROOT / "gdt150_kor_root_targets.tsv"
OBSERVATIONS = ROOT / "gdt150_visual_observations.tsv"
SCORED = ROOT / "gdt150_scored_predictions.tsv"
REPORT = ROOT / "GDT150_KOR_ROOT_VISUAL_TRANSFER_REPORT.md"
RESULT = ROOT / "gdt150_result.json"


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
    targets = read(TARGETS)
    observations = read(OBSERVATIONS)
    assert prediction["status"] == "FROZEN_BEFORE_TARGET_IMAGE_ACCESS"
    assert len(targets) == len(observations) == 2
    assert {row["target_id"] for row in targets} == {row["target_id"] for row in observations}
    target_by_id = {row["target_id"]: row for row in targets}
    scored = []
    for row in observations:
        frozen = target_by_id[row["target_id"]]
        assert frozen["page"] == row["page"]
        assert frozen["frozen_prediction"] == row["frozen_prediction"] == "POSITIVE"
        assert row["observation_provenance"] == "AI_DIRECT_VISUAL_OBSERVATION"
        assert row["visual_call"] in {"POSITIVE", "NEGATIVE", "UNCERTAIN"}
        match = row["visual_call"] == row["frozen_prediction"]
        assert int(row["prediction_match"]) == int(match)
        scored.append({
            "target_id": row["target_id"], "page": row["page"], "physical_folio": row["physical_folio"],
            "kor_locus": frozen["kor_locus"], "frozen_prediction": row["frozen_prediction"],
            "visual_call": row["visual_call"], "prediction_match": int(match),
            "confidence": row["confidence"], "rule_basis": row["rule_basis"],
            "full_image_sha256": row["full_image_sha256"],
        })
    calls = [row["visual_call"] for row in observations]
    if "NEGATIVE" in calls:
        status = "KOR_ROOT_GEOMETRY_GLOSS_REJECTED"
    elif calls == ["POSITIVE", "POSITIVE"]:
        status = "KOR_ROOT_GEOMETRY_GLOSS_TRANSFERS"
    else:
        status = "KOR_ROOT_GEOMETRY_GLOSS_UNRESOLVED"
    assert status == "KOR_ROOT_GEOMETRY_GLOSS_REJECTED"
    write(SCORED, scored)
    REPORT.write_text(f"""# GDT150 — prospective KOR/root-geometry transfer

Status: **{status}**

The two image calls were made after the public freeze from exact official Yale
canvases and concern visible root geometry only. Both frozen `POSITIVE`
predictions failed:

- **f22r — NEGATIVE.** The visible root system fans into ordinary thin,
  tapering roots. The long parallel outlines immediately above it are part of
  the lower stem and do not form repeated root chambers.
- **f37r — NEGATIVE.** One rounded thickened central mass is visible, with
  looping/tapering roots around it. The frozen rule required a repeated
  chamber configuration or a serial telescoping root segment; a single
  thickening does not qualify.

Thus the exact provisional gloss `KOR = conspicuous thickened, segmented, or
bulb-like root architecture` is rejected **0/2**. The f37r thickening is
reported rather than erased because it shows how a looser post-hoc rule could
have manufactured a positive. No alternative KOR meaning is substituted.

The calls are `AI_DIRECT_VISUAL_OBSERVATION`, hypothesis-aware, and not human
confirmation. They do not reject KOR as a formal PAGE_HOST, HPR2, or the wider
record architecture. They establish no botanical identity, semantic role,
word, morpheme, POS, sound, language, plaintext, meaning, or translation.
f84r was not opened, queried, retained, joined, scored, or targeted.
""", encoding="utf-8")
    result = {
        "schema": "GDT150_KOR_ROOT_VISUAL_TRANSFER_RESULT_V1",
        "status": status,
        "hypothesis": prediction["hypothesis"],
        "prediction_summary": {"targets": 2, "positive_predictions": 2, "positive_calls": 0,
                               "negative_calls": 2, "uncertain_calls": 0, "exact_hits": 0},
        "review": {"provenance": "AI_DIRECT_VISUAL_OBSERVATION",
                   "condition": "HYPOTHESIS_AWARE_NO_HUMAN_CONFIRMATION",
                   "official_full_page_images": True, "automated_vision_used": False,
                   "ocr_used": False, "botanical_identity_assigned": False},
        "counterexample": "f37r has one thickened central root mass, but not the frozen repeated-chamber or serial-telescoping configuration.",
        "interpretation": "The exact prospective KOR root-geometry gloss failed on both mechanically selected targets; no alternative gloss was searched.",
        "claim_ceiling": "One rejected visible-root-geometry gloss only; no botanical identity, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("opened", "retained", "queried", "joined", "scored", "targeted", "assigned", "predicted")},
        "inputs": {PREDICTION.name: sha(PREDICTION), PREDICTION_VALIDATION.name: sha(PREDICTION_VALIDATION),
                   TARGETS.name: sha(TARGETS), OBSERVATIONS.name: sha(OBSERVATIONS)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {SCORED.name: sha(SCORED)},
        "documents": {REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "calls": calls, "hits": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
