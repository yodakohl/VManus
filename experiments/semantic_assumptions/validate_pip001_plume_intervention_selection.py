#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RESULTS = BASE / "results"
METHOD = BASE / "PIP001_PLUME_INTERVENTION_PANEL_METHOD.md"
SOURCE = ROOT / "transcription/sources/Stolfi_text25e1-52.evt"
SELECTION = RESULTS / "pip001_plume_intervention_selection.json"
OUT = RESULTS / "pip001_plume_intervention_selection_validation.json"
REPORT = RESULTS / "pip001_plume_intervention_selection_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    stored = json.loads(SELECTION.read_text(encoding="utf-8"))
    lines = SOURCE.read_text(encoding="latin-1").splitlines()
    found = []
    for i, line in enumerate(lines):
        low = line.lower()
        if line.startswith("# ") and "plume" in low and any(word in low for word in ("correct", "added", "darker ink")):
            target = next(candidate for candidate in lines[i + 1 :] if candidate.startswith("<f"))
            found.append(re.match(r"<([^;>]+);U>", target).group(1))
    targets = stored["targets"]
    checks = {
        "canonical_selection": SELECTION.read_bytes() == (json.dumps(stored, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "complete_comment_census": found == ["f26r.1", "f31r.7", "f37v.22", "f81v.13", "f81v.19"] == [target["locus"] for target in targets],
        "exact_four_folio_scope": len({target["page"] for target in targets}) == 4,
        "exposure_and_prior_outcomes": [target["previously_exposed_for_plume_intervention_question"] for target in targets] == [True, True, False, False, False] and [target["fixed_prior_outcome"] for target in targets[:2]] == ["VISIBLE_PLUME_CHRONOLOGY_UNRESOLVED", "SECURE_VISIBLE_SEPARABLE_PLUME_INTERVENTION"],
        "official_canvases": [(target["page"], target["canvas_id"], target["official_dimensions"]) for target in targets] == [("f26r", "1006124", [2727, 3743]), ("f31r", "1006134", [2717, 3743]), ("f37v", "1006147", [2882, 3769]), ("f81v", "1006221", [2835, 3705]), ("f81v", "1006221", [2835, 3705])],
        "new_regions_sealed": all(not target["target_region_opened_for_pip001"] for target in targets[2:]) and stored["access"]["new_target_image_bodies_opened"] is False,
        "input_hashes": stored["inputs"] == {str(METHOD.relative_to(ROOT)): sha(METHOD), str(SOURCE.relative_to(ROOT)): sha(SOURCE), "sia001_result_sha256": sha(RESULTS / "sia001_supralinear_addition_result.json"), "processed_correction_screen_sha256": sha(RESULTS / "processed_correction_pair_worth_screen.json"), "yale_manifest_2002046_sha256": "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"},
        "frozen_thresholds_and_ceiling": stored["panel_gates"] == {"minimum_total_positives": 3, "minimum_new_target_positives": 2, "minimum_positive_physical_folios": 3} and stored["access"]["ocr_clip_embeddings_or_automated_vision_used"] is False and stored["access"]["formal_or_meaning_fields_used"] is False,
    }
    if not all(checks.values()):
        raise SystemExit("validation failed: " + ", ".join(k for k, value in checks.items() if not value))
    result = {"experiment": "PIP001_SELECTION_VALIDATION", "status": "PASS_8_CHECK_SOURCE_ONLY_RECONSTRUCTION", "source_selection_sha256": sha(SELECTION), "check_count": len(checks), "checks": checks, "scope_note": "This reconstructs the source census, exposure accounting, bindings, and frozen decision before any new target pixels are opened.", "claim_ceiling": stored["claim_ceiling"]}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text("# PIP001 selection validation\n\nStatus: **PASS_8_CHECK_SOURCE_ONLY_RECONSTRUCTION**\n\nIndependent compact code reconstructs the five-comment census, four-folio scope, two fixed prior outcomes, three sealed new targets, official canvas bindings, input hashes, thresholds, and zero-semantic-access ceiling.\n\nThis authorizes three source-native inspections only and supplies no glyph value, word, meaning, plaintext, or translation.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
