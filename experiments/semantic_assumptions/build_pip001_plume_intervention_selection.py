#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RESULTS = BASE / "results"
METHOD = BASE / "PIP001_PLUME_INTERVENTION_PANEL_METHOD.md"
SOURCE = ROOT / "transcription/sources/Stolfi_text25e1-52.evt"
OUT_JSON = RESULTS / "pip001_plume_intervention_selection.json"
OUT_MD = RESULTS / "pip001_plume_intervention_selection_report.md"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA256 = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
EXPECTED = {
    "f26r.1": ("26r", "1006124", True, "VISIBLE_PLUME_CHRONOLOGY_UNRESOLVED", "PROCESSED_CORRECTION_PAIR"),
    "f31r.7": ("31r", "1006134", True, "SECURE_VISIBLE_SEPARABLE_PLUME_INTERVENTION", "SIA001"),
    "f37v.22": ("37v", "1006147", False, None, None),
    "f81v.13": ("81v", "1006221", False, None, None),
    "f81v.19": ("81v", "1006221", False, None, None),
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def select_comments(raw: str) -> list[dict[str, str]]:
    lines = raw.splitlines()
    hits = []
    for i, line in enumerate(lines):
        low = line.lower()
        if not line.startswith("# ") or "plume" not in low or not any(word in low for word in ("correct", "added", "darker ink")):
            continue
        target = next((candidate for candidate in lines[i + 1 :] if candidate.startswith("<f")), None)
        assert target is not None
        match = re.match(r"<([^;>]+);U>", target)
        assert match
        hits.append({"locus": match.group(1), "comment": line[2:]})
    return hits


def main() -> None:
    if OUT_JSON.exists() or OUT_MD.exists():
        raise SystemExit("refusing overwrite")
    hits = select_comments(SOURCE.read_text(encoding="latin-1"))
    assert [hit["locus"] for hit in hits] == list(EXPECTED)
    request = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "VManus-PIP001/1.0"})
    manifest_raw = urllib.request.urlopen(request, timeout=60).read()
    assert sha_bytes(manifest_raw) == MANIFEST_SHA256
    manifest = json.loads(manifest_raw.decode())
    canvases = {}
    for canvas in manifest["items"]:
        label = canvas["label"].get("none", [""])[0]
        body = canvas["items"][0]["items"][0]["body"]
        canvases[label] = {
            "canvas_id": canvas["id"].rsplit("/", 1)[-1],
            "width": body["width"],
            "height": body["height"],
            "service": body["service"][0]["@id"],
        }
    targets = []
    for hit in hits:
        label, canvas_id, exposed, fixed, prior = EXPECTED[hit["locus"]]
        canvas = canvases[label]
        assert canvas["canvas_id"] == canvas_id
        targets.append({
            **hit,
            "page": "f" + label,
            "canvas_id": canvas_id,
            "official_dimensions": [canvas["width"], canvas["height"]],
            "official_full_image_url": canvas["service"] + "/full/full/0/default.jpg",
            "previously_exposed_for_plume_intervention_question": exposed,
            "fixed_prior_outcome": fixed,
            "prior_experiment": prior,
            "target_region_opened_for_pip001": False,
        })
    result = {
        "experiment": "PIP001_COMPLETE_PLUME_INTERVENTION_SELECTION",
        "schema": "PIP001_SELECTION_V1",
        "status": "FROZEN_COMPLETE_FIVE_LOCUS_PANEL_THREE_NEW_REGIONS_UNOPENED",
        "decision": "AUTHORIZE_ONE_SOURCE_NATIVE_INSPECTION_PER_THREE_NEW_TARGETS",
        "counts": {"comments": 5, "physical_loci": 5, "physical_folios": 4, "previously_exposed": 2, "new_targets": 3},
        "targets": targets,
        "panel_gates": {"minimum_total_positives": 3, "minimum_new_target_positives": 2, "minimum_positive_physical_folios": 3},
        "gates": {
            "complete_literal_comment_rule": len(targets) == 5,
            "exact_expected_loci": [target["locus"] for target in targets] == list(EXPECTED),
            "exact_exposure_pattern": [target["previously_exposed_for_plume_intervention_question"] for target in targets] == [True, True, False, False, False],
            "fixed_prior_outcomes_preserved": [target["fixed_prior_outcome"] for target in targets[:2]] == ["VISIBLE_PLUME_CHRONOLOGY_UNRESOLVED", "SECURE_VISIBLE_SEPARABLE_PLUME_INTERVENTION"],
            "three_new_regions_unopened": all(not target["target_region_opened_for_pip001"] for target in targets[2:]),
            "official_manifest_canvas_bindings": True,
            "outcomes_physical_gates_and_panel_thresholds_frozen": True,
        },
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(SOURCE.relative_to(ROOT)): sha(SOURCE),
            "sia001_result_sha256": sha(RESULTS / "sia001_supralinear_addition_result.json"),
            "processed_correction_screen_sha256": sha(RESULTS / "processed_correction_pair_worth_screen.json"),
            "yale_manifest_2002046_sha256": MANIFEST_SHA256,
        },
        "access": {"new_target_image_bodies_opened": False, "ocr_clip_embeddings_or_automated_vision_used": False, "formal_or_meaning_fields_used": False},
        "claim_ceiling": "A pass can establish only majority visible separable plume intervention in this complete human-comment panel. It supplies no correct glyph identity, correction intent, sound, word, language, cipher, plaintext, meaning, or translation.",
    }
    assert all(result["gates"].values())
    OUT_JSON.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# PIP001 plume-intervention selection\n\n"
        "Status: **FROZEN_COMPLETE_FIVE_LOCUS_PANEL_THREE_NEW_REGIONS_UNOPENED**.\n\n"
        "The complete literal source-comment rule selects five plume-intervention claims on four folios. "
        "Two prior outcomes are fixed: f26r.1 unresolved and f31r.7 secure. The target regions at f37v.22, "
        "f81v.13, and f81v.19 remain unopened for PIP001. Official canvases, five physical gates, and thresholds "
        "of at least 3/5 total, 2/3 new, and three positive folios are frozen.\n\n"
        "This authorizes three source-native inspections only and supplies no glyph value, word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
