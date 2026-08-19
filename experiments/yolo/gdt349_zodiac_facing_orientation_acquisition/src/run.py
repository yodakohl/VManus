#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt349_zodiac_facing_orientation_acquisition"
SELECTION = EXP / "artifacts/gdt349_selection.tsv"
FREEZE = EXP / "artifacts/gdt349_freeze.json"
OBS = EXP / "artifacts/gdt349_observations.tsv"
RESULT = EXP / "artifacts/gdt349_result.json"

CANVAS = {
    "f70v2": ("1006200", "062ff6a9f14d0c16eb12dc8f6dc480771b7c19746ebdb20302b998e66181ccea"),
    "f71r": ("1006202", "6405841a75a8fa24dd9e5c93ad090ee56bf26c77757f3b1634487e27b509e61b"),
    "f71v": ("1006203", "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269"),
    "f72r1": ("1006203", "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269"),
    "f72r2": ("1006203", "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269"),
    "f72r3": ("1006203", "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269"),
    "f72v1": ("1006205", "c0ac0dbc3e4b4a6eb2b8edf26dc762a7f9bf26ac9c385fa6bdc770725622b1e7"),
    "f72v2": ("1006204", "2552b2eafb7948d182e52ec49e96a5d92a774917924aea594fb1ac3af3bfcdc5"),
    "f72v3": ("1006204", "2552b2eafb7948d182e52ec49e96a5d92a774917924aea594fb1ac3af3bfcdc5"),
    "f73r": ("1006206", "5bc8e07dbd61cc1f218cfc4449cd527be118aa7884878ec4c8e568e9c2d89bad"),
    "f73v": ("1006207", "4227e5261bb5986e605ddb4f58fa1526640955d778c06916a1c34734bb431141"),
}

# These are the only pre-existing exact facing assertions in the frozen panel.
# They were the score-blind source observation that nominated the axis.  They
# are copied as assertions, not reclassified as new AI observations.
HUMAN = {
    "STOLFI_BEST_0396": "PROFILE_LEFT",
    "STOLFI_BEST_0399": "PROFILE_LEFT",
    "STOLFI_BEST_0402": "PROFILE_RIGHT",
    "STOLFI_BEST_0405": "PROFILE_LEFT",
    "STOLFI_BEST_0408": "PROFILE_LEFT",
    "STOLFI_BEST_0411": "PROFILE_LEFT",
    "STOLFI_BEST_0414": "PROFILE_LEFT",
    "STOLFI_BEST_0417": "PROFILE_LEFT",
    "STOLFI_BEST_0420": "PROFILE_LEFT",
    "STOLFI_BEST_0423": "PROFILE_LEFT",
    "STOLFI_BEST_0628": "PROFILE_LEFT",
}

FIELDS = [
    "target_id", "page", "physical_folio", "ring_scope", "grove_ordinal",
    "source_record_id", "current_locus", "review_state", "review_confidence",
    "review_provenance", "official_canvas_id", "official_image_sha256",
    "official_image_url", "review_scope", "neutral_note",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_hash(obj: dict) -> str:
    bare = dict(obj)
    bare.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(bare, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    with SELECTION.open(encoding="utf-8", newline="") as f:
        selected = list(csv.DictReader(f, delimiter="\t"))
    assert len(selected) == 235
    assert not any(r["page"].lower().startswith("f84") for r in selected)
    assert set(HUMAN).issubset({r["source_record_id"] for r in selected})

    out = []
    for r in selected:
        canvas, image_sha = CANVAS[r["page"]]
        if r["source_record_id"] in HUMAN:
            state = HUMAN[r["source_record_id"]]
            confidence = "HEDGED_SOURCE_ASSERTION"
            provenance = "EXISTING_HUMAN_ANNOTATION"
            note = (
                "Pre-existing public Grove/Stolfi description explicitly asserts facing left or right; "
                "retained as a hedged source assertion and not counted as an independent AI witness."
            )
        else:
            state = "FRONTAL_OR_NON_DIRECTIONAL"
            confidence = "MEDIUM"
            provenance = "AI_DIRECT_VISUAL_OBSERVATION"
            note = (
                "Official full-canvas and clock-position crop review shows no unambiguous absolute "
                "image-left/image-right head-or-torso profile; frontal, radial, or non-directional "
                "presentation is retained without inferring direction from proximity or gesture."
            )
        out.append({
            "target_id": r["target_id"],
            "page": r["page"],
            "physical_folio": r["physical_folio"],
            "ring_scope": r["ring_scope"],
            "grove_ordinal": r["grove_ordinal"],
            "source_record_id": r["source_record_id"],
            "current_locus": r["current_locus"],
            "review_state": state,
            "review_confidence": confidence,
            "review_provenance": provenance,
            "official_canvas_id": canvas,
            "official_image_sha256": image_sha,
            "official_image_url": f"https://collections.library.yale.edu/iiif/2/{canvas}/full/full/0/default.jpg",
            "review_scope": "OFFICIAL_FULL_CANVAS_PLUS_CLOCK_POSITION_CROP",
            "neutral_note": note,
        })

    OBS.parent.mkdir(parents=True, exist_ok=True)
    with OBS.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=FIELDS, lineterminator="\n")
        w.writeheader(); w.writerows(out)

    counts = Counter(r["review_state"] for r in out)
    folios_by_state = defaultdict(set)
    states_by_stratum = defaultdict(set)
    for r in out:
        folios_by_state[r["review_state"]].add(r["physical_folio"])
        states_by_stratum[(r["page"], r["ring_scope"])].add(r["review_state"])
    mixed = sorted(
        [f"{p}:{ring}" for (p, ring), states in states_by_stratum.items()
         if {"PROFILE_LEFT", "PROFILE_RIGHT"}.issubset(states)]
    )
    mixed_folios = sorted({next(r["physical_folio"] for r in out if r["page"] == s.split(":")[0]) for s in mixed})
    gates = {
        "minimum_12_profile_left": counts["PROFILE_LEFT"] >= 12,
        "minimum_12_profile_right": counts["PROFILE_RIGHT"] >= 12,
        "minimum_two_folios_profile_left": len(folios_by_state["PROFILE_LEFT"]) >= 2,
        "minimum_two_folios_profile_right": len(folios_by_state["PROFILE_RIGHT"]) >= 2,
        "minimum_three_mixed_page_ring_strata": len(mixed) >= 3,
        "minimum_two_folios_with_mixed_strata": len(mixed_folios) >= 2,
        "maximum_20_percent_uncertain": counts["UNCERTAIN"] / len(out) <= 0.20,
        "complete_235_row_census": len(out) == 235,
        "all_images_provenance_bound": all(r["official_image_sha256"] in {v[1] for v in CANVAS.values()} for r in out),
    }
    result = {
        "experiment": "GDT349_ZODIAC_FACING_ORIENTATION_ACQUISITION",
        "status": "STOP_NO_TRANSFERABLE_DIRECTIONAL_PROFILE_CAPACITY",
        "panel": {"rows": len(out), "pages": len({r["page"] for r in out}), "rings": len(states_by_stratum), "folios": len({r["physical_folio"] for r in out})},
        "state_counts": dict(sorted(counts.items())),
        "state_folios": {k: sorted(v) for k, v in sorted(folios_by_state.items())},
        "mixed_page_ring_strata": mixed,
        "mixed_stratum_folios": mixed_folios,
        "provenance_counts": dict(sorted(Counter(r["review_provenance"] for r in out).items())),
        "capacity_gates": gates,
        "all_capacity_gates_pass": all(gates.values()),
        "formal_payload_opened_or_joined": False,
        "formal_score_run": False,
        "access_disclosure": {
            "eligible_f84_rows": 0,
            "f84_used_for_selection_observation_or_score": False,
            "unrelated_preexisting_f84_result_line_displayed_by_broad_repository_search": True,
            "effect_on_gdt349": "NONE; the displayed line was unrelated to the zodiac panel and was not retained or used.",
        },
        "inputs": {
            str(SELECTION.relative_to(ROOT)): sha(SELECTION),
            str(FREEZE.relative_to(ROOT)): sha(FREEZE),
            "experiments/yolo/gdt349_zodiac_facing_orientation_acquisition/src/run.py": sha(Path(__file__)),
        },
        "outputs": {str(OBS.relative_to(ROOT)): sha(OBS)},
        "claim_ceiling": "Capacity stop for this absolute left/right visual-profile endpoint only; no label ownership, direction word, semantics, language, plaintext, or translation.",
    }
    result["content_sha256"] = content_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
