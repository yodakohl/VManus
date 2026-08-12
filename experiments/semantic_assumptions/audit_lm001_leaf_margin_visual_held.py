#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.tsv"
METHOD = ROOT / "experiments/semantic_assumptions/LM001_HERBAL_LEAF_MARGIN_VISUAL_CAPACITY_METHOD.md"
CALIBRATION = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_calibration.json"
OUT_TSV = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_held.tsv"
OUT_JSON = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_held.json"
OUT_MD = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_held_report.md"

OBS = {
    "LM0D77BF50": ("SMOOTH", "LARGE_LOBES_EXCLUDED_AS_TEETH_AND_MULTIPLE_MARGINS_UNINTERRUPTED"),
    "LM16839C2C": ("SMOOTH", "MULTIPLE_RESOLVED_OVAL_AND_LANCEOLATE_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LM1A73FE1E": ("SMOOTH", "DEEPLY_LOBED_LEAVES_WITH_CONTINUOUS_LOBE_MARGINS"),
    "LM213247BB": ("TOOTHED", "ONE_EXCEPTIONALLY_CLEAR_LARGE_BLADE_WITH_MANY_REPEATED_SHARP_MARGIN_PROJECTIONS"),
    "LM2B184143": ("SMOOTH", "MULTIPLE_RESOLVED_BROAD_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LM3800E5EB": ("TOOTHED", "MULTIPLE_DIVIDED_LEAVES_WITH_REPEATED_SMALL_SECONDARY_MARGIN_PROJECTIONS"),
    "LM4A01EBCD": ("UNCERTAIN", "PROMINENT_RADIAL_STRUCTURES_NOT_SECURELY_IDENTIFIABLE_AS_LEAVES"),
    "LM4BDB2124": ("SMOOTH", "MULTIPLE_LARGE_REPEATED_LOBES_WITH_UNINTERRUPTED_LOBE_MARGINS"),
    "LM56823A90": ("SMOOTH", "OVERLAPPING_BUT_INDIVIDUALLY_OUTLINED_LANCEOLATE_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LM7201FAD9": ("SMOOTH", "MANY_REPEATED_CURVED_STRAPLIKE_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LM7D3410B1": ("SMOOTH", "MULTIPLE_NARROW_RESOLVED_BLADES_WITH_UNINTERRUPTED_MARGINS"),
    "LM8DD0010A": ("SMOOTH", "LARGE_AND_SMALLER_RESOLVED_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LMAE19D35F": ("TOOTHED", "MULTIPLE_BROAD_LEAVES_WITH_REPEATED_FINE_SHARP_MARGIN_PROJECTIONS"),
    "LME24EBA42": ("TOOTHED", "MANY_RESOLVED_LEAVES_WITH_REPEATED_SMALL_MARGIN_PROJECTIONS"),
    "LME32F24F5": ("SMOOTH", "MULTIPLE_LARGE_RESOLVED_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LMFCAA8CDD": ("TOOTHED", "MULTIPLE_BROAD_LEAVES_WITH_REPEATED_SHARP_MARGIN_PROJECTIONS"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rows = list(csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t"))
    held = [row for row in rows if row["phase"] == "HELD"]
    assert {row["opaque_id"] for row in held} == set(OBS)
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    assert calibration["status"] == "PASS_RUBRIC_WORKABLE_NO_AMENDMENT"

    out = []
    for row in sorted(held, key=lambda item: item["opaque_id"]):
        request = urllib.request.Request(
            row["review_image_url"], headers={"User-Agent": "VManus-LM001-held/1.0"}
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
        state, basis = OBS[row["opaque_id"]]
        out.append(
            {
                "opaque_id": row["opaque_id"],
                "currier": row["currier"],
                "folio_rank_quartile": row["folio_rank_quartile"],
                "quire": row["quire"],
                "canvas_id": row["canvas_id"],
                "review_image_sha256": hashlib.sha256(raw).hexdigest(),
                "leaf_margin_state": state,
                "visual_basis": basis,
            }
        )

    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(out[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(out)

    counts = Counter(row["leaf_margin_state"] for row in out)
    by_currier = {
        state: dict(Counter(row["currier"] for row in out if row["leaf_margin_state"] == state))
        for state in ("SMOOTH", "TOOTHED", "UNCERTAIN")
    }
    by_quartile = {
        state: dict(
            sorted(
                Counter(
                    row["folio_rank_quartile"]
                    for row in out
                    if row["leaf_margin_state"] == state
                ).items()
            )
        )
        for state in ("SMOOTH", "TOOTHED", "UNCERTAIN")
    }
    by_quire = {
        state: dict(
            sorted(
                Counter(row["quire"] for row in out if row["leaf_margin_state"] == state).items()
            )
        )
        for state in ("SMOOTH", "TOOTHED", "UNCERTAIN")
    }
    max_quire_share = {
        state: max(by_quire[state].values()) / counts[state] for state in ("SMOOTH", "TOOTHED")
    }
    gates = {
        "at_least_six_each_admitted_state": counts["SMOOTH"] >= 6 and counts["TOOTHED"] >= 6,
        "both_states_at_least_three_in_each_currier": all(
            by_currier[state].get(currier, 0) >= 3
            for state in ("SMOOTH", "TOOTHED")
            for currier in ("A", "B")
        ),
        "both_states_in_at_least_three_quartiles": all(
            len(by_quartile[state]) >= 3 for state in ("SMOOTH", "TOOTHED")
        ),
        "uncertain_no_more_than_four": counts["UNCERTAIN"] <= 4,
        "max_quire_share_no_more_than_point25": all(
            value <= 0.25 for value in max_quire_share.values()
        ),
    }
    result = {
        "experiment": "LM001_LEAF_MARGIN_VISUAL_HELD_CAPACITY",
        "schema": "LM001_HELD_V1",
        "status": "STOP_HELD_VISUAL_CAPACITY_FAILED",
        "decision": "STOP_BEFORE_ALL_VOYNICH_TEXT_FEATURES",
        "counts": {
            "pages": len(out),
            "SMOOTH": counts["SMOOTH"],
            "TOOTHED": counts["TOOTHED"],
            "UNCERTAIN": counts["UNCERTAIN"],
        },
        "by_currier": by_currier,
        "by_quartile": by_quartile,
        "by_quire": by_quire,
        "max_quire_share": max_quire_share,
        "gates": gates,
        "failed_gates": [name for name, passed in gates.items() if not passed],
        "access": {
            "held_images_judged_once": True,
            "voynich_text_features_accessed": False,
            "ocr_clip_embedding_or_automated_vision_used": False,
            "machine_authored_source_bound_native_inspection": True,
        },
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(PANEL.relative_to(ROOT)): sha(PANEL),
            str(CALIBRATION.relative_to(ROOT)): sha(CALIBRATION),
        },
        "observations_sha256": sha(OUT_TSV),
        "claim_ceiling": "The frozen held visual panel lacks the preregistered balance and independence needed for any leaf-margin/text association test. No Voynich text was opened, and no plant identity, leaf word, language, plaintext, meaning, or translation follows.",
    }
    assert not all(gates.values())
    OUT_JSON.write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(
        "# LM001 held leaf-margin visual capacity\n\n"
        "Status: **STOP_HELD_VISUAL_CAPACITY_FAILED**.\n\n"
        "The unchanged rubric classified the 16 frozen held canvases as 10 `SMOOTH`, "
        "5 `TOOTHED`, and 1 `UNCERTAIN`. The held panel fails three preregistered gates: "
        "six toothed pages are not available; toothed support is only 1 Currier-A versus "
        "4 Currier-B pages; and three of the five toothed pages lie in q05, a 60% maximum "
        "quire share. Both states do span at least three quartiles, and uncertainty is low.\n\n"
        "No Voynich string or formal text feature was opened. The route stops before association "
        "testing and supplies no plant identity, leaf word, language, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
