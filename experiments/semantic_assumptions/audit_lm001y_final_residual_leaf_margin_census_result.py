#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METHOD = ROOT / "experiments/semantic_assumptions/LM001Y_FINAL_RESIDUAL_LEAF_MARGIN_CENSUS_METHOD.md"
PANEL = ROOT / "experiments/semantic_assumptions/results/lm001y_final_residual_leaf_margin_census_selection.tsv"
OLD_HELD = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_held.tsv"
OLD_EXTENSION = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_result.tsv"
OUT_TSV = ROOT / "experiments/semantic_assumptions/results/lm001y_final_residual_leaf_margin_census_result.tsv"
OUT_JSON = ROOT / "experiments/semantic_assumptions/results/lm001y_final_residual_leaf_margin_census_result.json"
OUT_MD = ROOT / "experiments/semantic_assumptions/results/lm001y_final_residual_leaf_margin_census_result_report.md"

OBS = {
    "LY3362A195": ("TOOTHED", "MULTIPLE_RESOLVED_LEAVES_WITH_REPEATED_FINE_SCALLOPS_ON_OUTER_MARGINS"),
    "LY3EF27319": ("UNCERTAIN", "ONLY_ONE_CLEARLY_RESOLVED_GIANT_LEAF_SO_NEITHER_TWO_LEAF_STATE_CRITERION_IS_MET"),
    "LY4DCF82C2": ("TOOTHED", "MULTIPLE_LANCEOLATE_LEAVES_WITH_REPEATED_FINE_SERRATIONS_OR_SCALLOPS"),
    "LY64E57EC5": ("SMOOTH", "MANY_LARGE_LOBED_LEAVES_WITH_CONTINUOUS_LOBE_EDGES"),
    "LY82D0DF56": ("SMOOTH", "MULTIPLE_RESOLVED_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LYD11C7D19": ("SMOOTH", "MULTIPLE_LONG_NARROW_LEAVES_WITH_LARGELY_UNINTERRUPTED_MARGINS"),
    "LYD541DBB2": ("TOOTHED", "MANY_RESOLVED_LEAVES_WITH_CLEARLY_REPEATED_SCALLOPED_OR_SERRATED_EDGES"),
    "LYD6D791C8": ("SMOOTH", "MANY_DEEPLY_LOBED_CURVED_LEAVES_WITH_CONTINUOUS_LOBE_EDGES"),
    "LYF21DAF2A": ("SMOOTH", "FINE_HAIRLIKE_MARGIN_MARKS_EXCLUDED_BY_RUBRIC_AND_OVAL_LEAF_EDGES_OTHERWISE_CONTINUOUS"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(rows: list[dict[str, str]]) -> tuple[Counter, dict, dict, dict, dict, dict]:
    states = ("SMOOTH", "TOOTHED", "UNCERTAIN")
    counts = Counter(row["leaf_margin_state"] for row in rows)
    by_currier = {state: dict(sorted(Counter(row["currier"] for row in rows if row["leaf_margin_state"] == state).items())) for state in states}
    by_quartile = {state: dict(sorted(Counter(row["folio_rank_quartile"] for row in rows if row["leaf_margin_state"] == state).items())) for state in states}
    by_quire = {state: dict(sorted(Counter(row["quire"] for row in rows if row["leaf_margin_state"] == state).items())) for state in states}
    shares = {state: max(by_quire[state].values()) / counts[state] for state in ("SMOOTH", "TOOTHED")}
    gates = {
        "at_least_six_each_admitted_state": counts["SMOOTH"] >= 6 and counts["TOOTHED"] >= 6,
        "both_states_at_least_three_in_each_currier": all(by_currier[state].get(currier, 0) >= 3 for state in ("SMOOTH", "TOOTHED") for currier in ("A", "B")),
        "both_states_in_at_least_three_quartiles": all(len(by_quartile[state]) >= 3 for state in ("SMOOTH", "TOOTHED")),
        "uncertain_no_more_than_four": counts["UNCERTAIN"] <= 4,
        "max_quire_share_no_more_than_point25": all(value <= 0.25 for value in shares.values()),
    }
    return counts, by_currier, by_quartile, by_quire, shares, gates


def main() -> None:
    panel = list(csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t"))
    assert {row["opaque_id"] for row in panel} == set(OBS)
    extension = []
    for row in sorted(panel, key=lambda item: item["opaque_id"]):
        request = urllib.request.Request(row["review_image_url"], headers={"User-Agent": "VManus-LM001Y-result/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
        state, basis = OBS[row["opaque_id"]]
        extension.append({
            "opaque_id": row["opaque_id"], "currier": row["currier"],
            "folio_rank_quartile": row["folio_rank_quartile"], "quire": row["quire"],
            "canvas_id": row["canvas_id"], "review_image_sha256": hashlib.sha256(raw).hexdigest(),
            "leaf_margin_state": state, "visual_basis": basis,
        })
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(extension[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(extension)

    old = list(csv.DictReader(OLD_HELD.open(encoding="utf-8"), delimiter="\t"))
    old += list(csv.DictReader(OLD_EXTENSION.open(encoding="utf-8"), delimiter="\t"))
    combined = old + extension
    counts, by_currier, by_quartile, by_quire, shares, gates = summarize(combined)
    result = {
        "experiment": "LM001Y_FINAL_RESIDUAL_LEAF_MARGIN_CENSUS_RESULT",
        "schema": "LM001Y_RESULT_V1",
        "status": "PASS_COMBINED_VISUAL_CAPACITY_ALL_ORIGINAL_GATES",
        "decision": "AUTHORIZE_SEPARATE_TEXT_BLIND_PREREGISTRATION_ONLY",
        "extension_counts": {state: Counter(row["leaf_margin_state"] for row in extension)[state] for state in ("SMOOTH", "TOOTHED", "UNCERTAIN")},
        "combined_counts": {"pages": len(combined), **{state: counts[state] for state in ("SMOOTH", "TOOTHED", "UNCERTAIN")}},
        "combined_by_currier": by_currier,
        "combined_by_quartile": by_quartile,
        "combined_by_quire": by_quire,
        "combined_max_quire_share": shares,
        "gates": gates,
        "failed_gates": [name for name, value in gates.items() if not value],
        "access": {
            "extension_images_judged_once": True,
            "voynich_text_features_accessed": False,
            "ocr_clip_embedding_or_automated_vision_used": False,
            "machine_authored_source_bound_native_inspection": True,
        },
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(PANEL.relative_to(ROOT)): sha(PANEL),
            str(OLD_HELD.relative_to(ROOT)): sha(OLD_HELD),
            str(OLD_EXTENSION.relative_to(ROOT)): sha(OLD_EXTENSION),
        },
        "observations_sha256": sha(OUT_TSV),
        "claim_ceiling": "The complete final source-only census makes the combined 44-folio visual panel satisfy every original LM001 capacity gate. This licenses only a separately frozen formal-text design; it does not establish a text association, plant identity, leaf word, language, plaintext, meaning, or translation.",
    }
    assert result["extension_counts"] == {"SMOOTH": 5, "TOOTHED": 3, "UNCERTAIN": 1}
    assert result["combined_counts"] == {"pages": 44, "SMOOTH": 29, "TOOTHED": 13, "UNCERTAIN": 2}
    assert result["combined_by_currier"]["TOOTHED"] == {"A": 9, "B": 4}
    assert result["combined_by_quire"]["TOOTHED"] == {"q01": 1, "q02": 3, "q03": 2, "q05": 3, "q06": 3, "q07": 1}
    assert result["combined_max_quire_share"]["TOOTHED"] == 3 / 13
    assert all(gates.values()) and result["failed_gates"] == []
    OUT_JSON.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# LM001Y final residual leaf-margin census result\n\n"
        "Status: **PASS_COMBINED_VISUAL_CAPACITY_ALL_ORIGINAL_GATES**.\n\n"
        "The complete nine-folio residual contains 5 `SMOOTH`, 3 `TOOTHED`, and 1 `UNCERTAIN` judgment. "
        "Combined unchanged with LM001 and LM001X, the totals are 29 smooth, 13 toothed, and 2 uncertain on 44 physical folios. "
        "Both admitted states exceed six pages, reach at least three pages in each Currier system, and span at least three folio-rank quartiles. "
        "The uncertainty count is two. The largest toothed quire contributions are q02, q05, and q06 at 3/13 each (23.1%), while the largest smooth contribution is q03 at 6/29 (20.7%). Every original visual-capacity gate passes.\n\n"
        "This result authorizes only a separately frozen formal-text design. No Voynich text was opened during selection or judgment, and this capacity pass supplies no association, plant identity, leaf word, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
