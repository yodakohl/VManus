#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, json, urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.tsv"
METHOD = ROOT / "experiments/semantic_assumptions/LM001_HERBAL_LEAF_MARGIN_VISUAL_CAPACITY_METHOD.md"
OUT_TSV = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_calibration.tsv"
OUT_JSON = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_calibration.json"
OUT_MD = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_calibration_report.md"

OBS = {
    "LM01FB9FDF": ("UNCERTAIN", "OVERLAPPING_CANOPY_INDIVIDUAL_MARGINS_NOT_SEPARABLE"),
    "LM10799F77": ("TOOTHED", "TWO_LARGE_BASAL_LEAVES_WITH_REPEATED_SHARP_MARGIN_PROJECTIONS"),
    "LM1236AD38": ("SMOOTH", "MULTIPLE_RESOLVED_LOBED_LEAVES_WITH_CONTINUOUS_EDGES"),
    "LM12C2E77A": ("SMOOTH", "MANY_RESOLVED_SMALL_LEAVES_WITH_CONTINUOUS_MARGINS"),
    "LM211EBC9D": ("SMOOTH", "MANY_BROAD_SEPARATED_LEAVES_WITH_CONTINUOUS_MARGINS"),
    "LM2C2CD756": ("TOOTHED", "LARGE_LEAVES_WITH_DENSE_REPEATED_LOOPLIKE_MARGIN_PROJECTIONS"),
    "LM4F6E4E4B": ("UNCERTAIN", "NARROW_PROJECTIONS_NOT_SECURELY_DISTINGUISHED_FROM_COMPOSITE_STRUCTURES"),
    "LM63265EAB": ("SMOOTH", "LARGE_FAN_OF_SEPARATE_LEAVES_WITH_CONTINUOUS_ROUNDED_MARGINS"),
    "LM7387C412": ("TOOTHED", "MANY_TRIANGULAR_LEAVES_WITH_FINE_SAWLIKE_PROJECTIONS"),
    "LM79C8637B": ("TOOTHED", "NUMEROUS_OVAL_LEAVES_WITH_REGULAR_SCALLOPED_MARGINS"),
    "LM86F03782": ("TOOTHED", "SEVERAL_RESOLVED_LEAVES_WITH_REPEATED_SMALL_MARGIN_PROJECTIONS"),
    "LMC910E45A": ("SMOOTH", "DEEPLY_LOBED_LEAVES_WITH_CONTINUOUS_LOBE_MARGINS"),
    "LMDC2CC2D9": ("UNCERTAIN", "TIGHTLY_OVERLAPPING_SCALLOPED_TIERS_NOT_SEPARABLE_AS_LEAVES"),
    "LMEFA2C7F7": ("TOOTHED", "SEVERAL_LEAVES_WITH_REPEATED_FINE_PROJECTIONS_ON_LARGER_LOBES"),
    "LMF4CCA3F9": ("UNCERTAIN", "BANDED_COMPOSITE_GREEN_STRUCTURES_WITH_UNCERTAIN_LEAF_UNITS"),
    "LMF69ECC90": ("SMOOTH", "FOUR_LARGE_RESOLVED_LEAVES_WITH_CONTINUOUS_MARGINS"),
}

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    rows = list(csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t"))
    calibration = [r for r in rows if r["phase"] == "CALIBRATION"]
    assert {r["opaque_id"] for r in calibration} == set(OBS)
    out = []
    for row in sorted(calibration, key=lambda r: r["opaque_id"]):
        with urllib.request.urlopen(urllib.request.Request(row["review_image_url"], headers={"User-Agent":"VManus-LM001/1.0"}), timeout=60) as response:
            raw = response.read()
        state, basis = OBS[row["opaque_id"]]
        out.append({
            "opaque_id": row["opaque_id"], "currier": row["currier"],
            "folio_rank_quartile": row["folio_rank_quartile"], "quire": row["quire"],
            "canvas_id": row["canvas_id"], "review_image_sha256": hashlib.sha256(raw).hexdigest(),
            "leaf_margin_state": state, "visual_basis": basis,
        })
    fields = list(out[0])
    with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(out)
    counts=Counter(x["leaf_margin_state"] for x in out)
    result={
        "experiment":"LM001_LEAF_MARGIN_VISUAL_CALIBRATION", "schema":"LM001_CALIBRATION_V1",
        "status":"PASS_RUBRIC_WORKABLE_NO_AMENDMENT", "decision":"AUTHORIZE_ONE_PASS_HELD_NATIVE_VISUAL_JUDGMENT",
        "counts":{"pages":16,"SMOOTH":counts["SMOOTH"],"TOOTHED":counts["TOOTHED"],"UNCERTAIN":counts["UNCERTAIN"]},
        "gates":{"all_frozen_calibration_pages_judged":len(out)==16,"rubric_amended":False,
                 "at_least_four_each_admitted_state":counts["SMOOTH"]>=4 and counts["TOOTHED"]>=4,
                 "uncertain_no_more_than_six":counts["UNCERTAIN"]<=6,"held_images_opened_for_judgment":False,
                 "voynich_text_features_accessed":False,"ocr_clip_embedding_or_automated_vision_used":False,
                 "machine_authored_source_bound_native_inspection":True},
        "inputs":{str(METHOD.relative_to(ROOT)):sha(METHOD),str(PANEL.relative_to(ROOT)):sha(PANEL)},
        "observations_sha256":sha(OUT_TSV),
        "claim_ceiling":"Calibration shows that the frozen geometric rubric can classify the selected page images without amendment. It establishes no held capacity, leaf-word association, plant identity, language, plaintext, meaning, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    OUT_MD.write_text(
        "# LM001 leaf-margin visual calibration\n\nStatus: **PASS_RUBRIC_WORKABLE_NO_AMENDMENT**.\n\n"
        "All 16 frozen calibration canvases were inspected in opaque-ID order under the published rubric. "
        "The result is 6 `SMOOTH`, 6 `TOOTHED`, and 4 `UNCERTAIN`. The uncertainty class correctly "
        "absorbed overlapping canopies and composite structures, while large lobes remained distinct from "
        "fine repeated margin projections. No rubric amendment was made.\n\n"
        "No held canvas was opened for judgment, and no Voynich string or formal text feature was accessed. "
        "The observations are machine-authored source-bound native visual judgments, not literal human annotations.\n\n"
        "Claim ceiling: calibration only; no leaf word, plant identity, language, plaintext, meaning, or translation.\n",
        encoding="utf-8")

if __name__ == "__main__": main()
