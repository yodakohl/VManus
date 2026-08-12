#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METHOD = ROOT / "experiments/semantic_assumptions/LM001X_CURRIER_A_LEAF_MARGIN_EXTENSION_METHOD.md"
PANEL = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_selection.tsv"
OLD_OBS = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_held.tsv"
OLD_RESULT = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_held.json"
OUT_TSV = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_result.tsv"
OUT_JSON = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_result.json"
OUT_MD = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_result_report.md"

OBS = {
    "LX04270557": ("TOOTHED", "MANY_RESOLVED_LEAVES_WITH_REPEATED_FINE_FRINGELIKE_MARGIN_PROJECTIONS"),
    "LX13E439B5": ("SMOOTH", "DEEP_POINTED_LOBES_EXCLUDED_AS_TEETH_AND_LOBE_MARGINS_UNINTERRUPTED"),
    "LX16DE17EC": ("TOOTHED", "SEVERAL_BROAD_LEAVES_WITH_REPEATED_FINE_SECONDARY_SERRATIONS"),
    "LX1DEE719D": ("SMOOTH", "MANY_RESOLVED_OVAL_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LX2459DE79": ("SMOOTH", "TERMINAL_CURLS_AND_LOBES_WITHOUT_REPEATED_SECONDARY_MARGIN_TEETH"),
    "LX25B2BBA8": ("SMOOTH", "MANY_RESOLVED_POINTED_LEAVES_WITH_OTHERWISE_UNINTERRUPTED_EDGES"),
    "LX2E609C0A": ("TOOTHED", "MANY_RESOLVED_LEAVES_WITH_REPEATED_SHARP_MARGIN_PROJECTIONS"),
    "LX392B8776": ("TOOTHED", "MULTIPLE_LOBED_LEAVES_WITH_REPEATED_SMALL_SECONDARY_SCALLOPS"),
    "LX449DB51B": ("SMOOTH", "REPEATED_HAIRLIKE_FRINGE_EXCLUDED_BY_RUBRIC"),
    "LX47C213BA": ("SMOOTH", "LARGE_POINTED_LOBES_WITHOUT_SECONDARY_MARGIN_TEETH"),
    "LX605028AC": ("SMOOTH", "MANY_RESOLVED_OVAL_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LX69592034": ("SMOOTH", "MANY_RESOLVED_OVAL_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LX71B507A7": ("SMOOTH", "MANY_SMALL_RESOLVED_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LX8C602775": ("SMOOTH", "DEEP_SEPARATE_LOBES_WITH_CONTINUOUS_LOBE_EDGES"),
    "LX927CDC89": ("SMOOTH", "MANY_RESOLVED_LANCEOLATE_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LXC164AE70": ("SMOOTH", "LARGE_CURVED_RESOLVED_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LXCB52589D": ("SMOOTH", "MULTIPLE_RESOLVED_LANCEOLATE_LEAVES_WITH_UNINTERRUPTED_MARGINS"),
    "LXEA1B71E7": ("SMOOTH", "RADIATING_NARROW_LOBES_WITH_CONTINUOUS_EDGES"),
    "LXF93AFBB6": ("TOOTHED", "MANY_RESOLVED_LEAVES_WITH_REPEATED_SCALLOPED_MARGIN_PROJECTIONS"),
}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    panel = list(csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t"))
    assert {row["opaque_id"] for row in panel} == set(OBS)
    extension = []
    for row in sorted(panel, key=lambda item: item["opaque_id"]):
        request = urllib.request.Request(row["review_image_url"], headers={"User-Agent": "VManus-LM001X-result/1.0"})
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
        writer.writeheader(); writer.writerows(extension)

    old = list(csv.DictReader(OLD_OBS.open(encoding="utf-8"), delimiter="\t"))
    combined = old + extension
    counts = Counter(row["leaf_margin_state"] for row in combined)
    by_currier = {state: dict(Counter(row["currier"] for row in combined if row["leaf_margin_state"] == state)) for state in ("SMOOTH", "TOOTHED", "UNCERTAIN")}
    by_quartile = {state: dict(sorted(Counter(row["folio_rank_quartile"] for row in combined if row["leaf_margin_state"] == state).items())) for state in ("SMOOTH", "TOOTHED", "UNCERTAIN")}
    by_quire = {state: dict(sorted(Counter(row["quire"] for row in combined if row["leaf_margin_state"] == state).items())) for state in ("SMOOTH", "TOOTHED", "UNCERTAIN")}
    shares = {state: max(by_quire[state].values()) / counts[state] for state in ("SMOOTH", "TOOTHED")}
    gates = {
        "at_least_six_each_admitted_state": counts["SMOOTH"] >= 6 and counts["TOOTHED"] >= 6,
        "both_states_at_least_three_in_each_currier": all(by_currier[state].get(currier, 0) >= 3 for state in ("SMOOTH", "TOOTHED") for currier in ("A", "B")),
        "both_states_in_at_least_three_quartiles": all(len(by_quartile[state]) >= 3 for state in ("SMOOTH", "TOOTHED")),
        "uncertain_no_more_than_four": counts["UNCERTAIN"] <= 4,
        "max_quire_share_no_more_than_point25": all(value <= 0.25 for value in shares.values()),
    }
    result = {
        "experiment": "LM001X_CURRIER_A_LEAF_MARGIN_EXTENSION_RESULT",
        "schema": "LM001X_RESULT_V1", "status": "STOP_COMBINED_QUIRE_CONCENTRATION_FAILED",
        "decision": "STOP_BEFORE_ALL_VOYNICH_TEXT_FEATURES",
        "extension_counts": dict(Counter(row["leaf_margin_state"] for row in extension)),
        "combined_counts": {"pages": len(combined), **{state: counts[state] for state in ("SMOOTH", "TOOTHED", "UNCERTAIN")}},
        "combined_by_currier": by_currier, "combined_by_quartile": by_quartile,
        "combined_by_quire": by_quire, "combined_max_quire_share": shares,
        "gates": gates, "failed_gates": [name for name, value in gates.items() if not value],
        "access": {"extension_images_judged_once": True, "voynich_text_features_accessed": False,
                   "ocr_clip_embedding_or_automated_vision_used": False,
                   "machine_authored_source_bound_native_inspection": True},
        "inputs": {str(METHOD.relative_to(ROOT)): file_sha(METHOD), str(PANEL.relative_to(ROOT)): file_sha(PANEL),
                   str(OLD_OBS.relative_to(ROOT)): file_sha(OLD_OBS), str(OLD_RESULT.relative_to(ROOT)): file_sha(OLD_RESULT)},
        "observations_sha256": file_sha(OUT_TSV),
        "claim_ceiling": "The 19-page extension adds source-native Currier-A observations but the combined panel still fails the original 25% maximum-quire gate. No Voynich text was opened and no plant identity, leaf word, language, plaintext, meaning, or translation follows.",
    }
    assert result["extension_counts"] == {"SMOOTH": 14, "TOOTHED": 5}
    assert result["combined_counts"] == {"pages": 35, "SMOOTH": 24, "TOOTHED": 10, "UNCERTAIN": 1}
    assert result["failed_gates"] == ["max_quire_share_no_more_than_point25"]
    OUT_JSON.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# LM001X Currier-A leaf-margin extension result\n\nStatus: **STOP_COMBINED_QUIRE_CONCENTRATION_FAILED**.\n\n"
        "The 19 extension pages contain 14 `SMOOTH`, 5 `TOOTHED`, and no `UNCERTAIN` judgments. "
        "Combined unchanged with the original held panel, the totals are 24 smooth, 10 toothed, and "
        "1 uncertain on 35 folios. Minimum state counts, Currier support, quartile support, and uncertainty "
        "all pass. The sole failure is quire concentration: q05 still supplies 3/10 toothed pages, or 30%, "
        "above the frozen 25% ceiling.\n\nNo Voynich string or formal text feature was opened. The route stops before association testing and supplies no plant identity, leaf word, plaintext, meaning, or translation.\n",
        encoding="utf-8")


if __name__ == "__main__": main()
