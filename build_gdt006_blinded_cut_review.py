#!/usr/bin/env python3
"""Build the GDT006 localization-capacity result; no visual score was run."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_tsv(name: str):
    with (ROOT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def sha(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def main() -> None:
    selection = read_tsv("gdt005_matched_cut_selection.tsv")
    localizations = read_tsv("gdt006_cut_localizations.tsv")
    reviews = read_tsv("gdt006_blind_reviews.tsv")
    assert len(selection) == 9 and len(localizations) == 34 and not reviews
    assert len({(r["pair_id"], r["arm"], r["cut_ordinal"]) for r in localizations}) == 34
    assert all("f84" not in json.dumps(r) for r in localizations)

    expected = set()
    for row in selection:
        for arm in ("TARGET", "CONTROL"):
            prefix = "target" if arm == "TARGET" else "control"
            cuts = row[f"{prefix}_cut_offsets_1based"].split(";")
            for ordinal, offset in enumerate(cuts, 1):
                expected.add((row["pair_id"], arm, str(ordinal), row["locus"], row[f"{prefix}_group_index"], row[f"{prefix}_surface"], offset))
    actual = {(r["pair_id"], r["arm"], r["cut_ordinal"], r["locus"], r["group_index"], r["surface"], r["display_cut_offset"]) for r in localizations}
    assert actual == expected

    localized = [r for r in localizations if r["localization_state"] == "LOCALIZED"]
    unresolved = [r for r in localizations if r["localization_state"] == "LOCALIZATION_UNRESOLVED"]
    target = [r for r in localizations if r["arm"] == "TARGET"]
    control = [r for r in localizations if r["arm"] == "CONTROL"]
    intrinsic = [r for r in localizations if "falls inside single STA" in r["neutral_note"]]
    target_pair_state = {}
    for row in target:
        target_pair_state.setdefault(row["pair_id"], row["legacy_target_box_contains_registered_group"])
        assert target_pair_state[row["pair_id"]] == row["legacy_target_box_contains_registered_group"]

    inputs = [
        "GDT006_BLINDED_CUT_REVIEW_METHOD.md",
        "gdt005_matched_cut_selection.tsv",
        "gdt006_cut_localizations.tsv",
        "gdt006_blind_reviews.tsv",
        "gdt004_module_shape_selection.tsv",
        "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv",
        "prepare_gdt006_blind_cut_packet.py",
        "build_gdt006_blinded_cut_review.py",
    ]
    result = {
        "experiment": "GDT006_BLINDED_WITHIN_GROUP_CUT_REVIEW",
        "status": "STOP_LOCALIZATION_CAPACITY_3_OF_34_NO_BLIND_REVIEW",
        "exploratory": True,
        "registered": {"pairs": 9, "target_cuts": len(target), "control_cuts": len(control), "total_probes": len(localizations)},
        "localization": {
            "localized_target_cuts": sum(r["localization_state"] == "LOCALIZED" for r in target),
            "localized_control_cuts": sum(r["localization_state"] == "LOCALIZED" for r in control),
            "localized_total": len(localized),
            "unresolved_total": len(unresolved),
            "intrinsically_unmappable_display_cuts_inside_one_sta_sign": len(intrinsic),
            "other_unresolved": len(unresolved) - len(intrinsic),
            "legacy_target_boxes_confirmed": sum(v == "YES" for v in target_pair_state.values()),
            "legacy_target_boxes_wrong": sum(v == "NO" for v in target_pair_state.values()),
            "legacy_target_boxes_unresolved": sum(v == "UNRESOLVED" for v in target_pair_state.values()),
        },
        "blind_review": {
            "fresh_reviewer_instantiated": True,
            "valid_final_matched_packet_delivered": False,
            "review_rows": len(reviews),
            "score": "NOT_COMPUTED",
            "provisional_packet": "INVALIDATED_WITHDRAWN_AND_EXCLUDED",
        },
        "corrections": {
            "GDT004": "FORMER_NINE_TARGET_VISUAL_CLAIM_WITHDRAWN; TWO_TARGET_GROUPS_SECURE",
            "GDT005": "FORMER_0_OF_17_VS_0_OF_17_MATCHED_CLAIM_WITHDRAWN; ZERO_SECURE_CONTROL_CUTS",
        },
        "holdout": {"f84r_opened": False, "f84r_rows_retained_joined_or_scored": 0},
        "claim_ceiling": "Localization-capacity and provenance correction only; no spacing effect, grapheme boundary, morpheme, slot, language, meaning, semantic role, plaintext, or translation.",
        "inputs": {name: sha(name) for name in inputs},
    }
    (ROOT / "gdt006_blinded_cut_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
