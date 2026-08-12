#!/usr/bin/env python3
"""Record the frozen SRE001 native-visual capacity census."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
METHOD = BASE / "SRE001_SPECIAL_CIRCLE_STAR_RAY_EXTENSION_METHOD.md"
SELECTION = BASE / "results/sre001_special_circle_star_ray_extension_selection.json"
SELECTION_VALIDATION = BASE / "results/sre001_special_circle_star_ray_extension_selection_validation.json"
OUT_TSV = BASE / "results/sre001_special_circle_star_ray_extension_result.tsv"
OUT = BASE / "results/sre001_special_circle_star_ray_extension_result.json"
REPORT = BASE / "results/sre001_special_circle_star_ray_extension_result_report.md"
IMAGE_SHA = {
    "1006198": "b830e74480830c0d5e8f7b56025473e051743f9ec50685b6fe316ecd493f0f01",
    "1006203": "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269",
    "1006206": "5bc8e07dbd61cc1f218cfc4449cd527be118aa7884878ec4c8e568e9c2d89bad",
    "1006207": "4227e5261bb5986e605ddb4f58fa1526640955d778c06916a1c34734bb431141",
}
FIELDS = ("opaque_id", "page", "physical_folio", "locus", "unit", "canvas_id", "outcome", "ray_count", "visible_basis")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def classify(row: dict) -> tuple[str, str, str]:
    if row["page"] == "f69r" and row["unit"] == "K1":
        return (
            "NON_STAR_OBJECT",
            "",
            "The inscription occupies one central disk sector between two painted star arms; the visible owner is the sector, not one star.",
        )
    if row["page"] in {"f72r1", "f72r2", "f73r", "f73v"}:
        return (
            "SLOT_OR_GROUP_ONLY",
            "",
            "The inscription occupies a repeated combined human-figure-plus-star slot with no leader, enclosure, or separation assigning it uniquely to the star rather than the figure/pair.",
        )
    raise AssertionError(row)


def report_text(result: dict) -> str:
    return (
        "# SRE001 special-circle star-ray extension result\n\n"
        f"Status: **{result['status']}**.\n\n"
        "The complete frozen 24-target census yields **0** singular star-owned countable labels. "
        "All six f69 targets are central-sector inscriptions between star arms and are therefore "
        "`NON_STAR_OBJECT`. The ten f72 and eight f73 targets occupy combined figure-plus-star "
        "slots without a leader, enclosure, or separate writing cell assigning the inscription "
        "uniquely to the star; all eighteen are `SLOT_OR_GROUP_ONLY`.\n\n"
        "Every capacity gate fails before Voynich label identity or formal-feature access. The new "
        "census does not satisfy the published second-folio reopen condition for the f68 ray-count "
        "association route.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n"
    )


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT, REPORT)):
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    rows = []
    for target in selection["targets"]:
        outcome, ray_count, basis = classify(target)
        rows.append({key: str(target.get(key, "")) for key in FIELDS})
        rows[-1].update({"outcome": outcome, "ray_count": ray_count, "visible_basis": basis})
    with OUT_TSV.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    outcomes = Counter(row["outcome"] for row in rows)
    by_folio: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        by_folio[row["physical_folio"]][row["outcome"]] += 1
    qualifying = Counter(row["physical_folio"] for row in rows if row["outcome"] == "SINGULAR_STAR_OWNED_RAY_COUNTABLE")
    gates = {
        "one_new_folio_has_at_least_eight_countable_singular_star_owners": any(value >= 8 for value in qualifying.values()),
        "one_qualifying_folio_has_two_ray_counts": False,
        "two_ray_counts_each_have_three_examples": False,
        "maximum_one_page_share_at_most_point_75": False,
    }
    result = {
        "experiment": "SRE001_SPECIAL_CIRCLE_STAR_RAY_EXTENSION_RESULT",
        "schema": "SRE001_RESULT_V1",
        "status": "STOP_ZERO_SINGULAR_STAR_OWNED_TARGETS",
        "decision": "KEEP_DIRECT_STAR_LABEL_RAY_COUNT_ROUTE_CLOSED",
        "counts": {
            "targets": len(rows),
            "outcomes": dict(sorted(outcomes.items())),
            "by_folio": {folio: dict(sorted(count.items())) for folio, count in sorted(by_folio.items())},
            "countable_singular_star_owned": sum(qualifying.values()),
            "label_surfaces_opened": 0,
            "formal_features_opened": 0,
            "associations_scored": 0,
        },
        "gates": gates,
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(SELECTION.relative_to(ROOT)): sha(SELECTION),
            str(SELECTION_VALIDATION.relative_to(ROOT)): sha(SELECTION_VALIDATION),
            "official_image_sha256": IMAGE_SHA,
        },
        "result_tsv_sha256": sha(OUT_TSV),
        "access": {
            "all_twenty_four_target_positions_inspected": True,
            "voynich_label_surfaces_opened": False,
            "formal_features_opened": False,
            "ocr_clip_embedding_or_automated_vision_used": False,
            "machine_authored_source_bound_native_visual_judgments": True,
        },
        "claim_ceiling": (
            "This closes only the current second-folio star-ray ownership extension. It establishes no "
            "ray-count encoding, number, star name, word, sound, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_bytes(canonical(result))
    REPORT.write_text(report_text(result), encoding="utf-8")


if __name__ == "__main__":
    main()
