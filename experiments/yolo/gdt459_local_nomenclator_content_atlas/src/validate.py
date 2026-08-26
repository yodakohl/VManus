#!/usr/bin/env python3
"""Validate the GDT459 mixed address-formula / nomenclator release."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas"
OUT = BASE / "artifacts"
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
LOCAL_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_693_local_group_edition.tsv"
RUN_SCRIPT = BASE / "src/run.py"

EVENT_PATH = OUT / "gdt459_183_address_interlinear.tsv"
SURFACE_PATH = OUT / "gdt459_162_surface_dictionary.tsv"
OWNER_PATH = OUT / "gdt459_22_owner_cluster_summary.tsv"
CALIBRATION_PATH = OUT / "gdt459_segmentation_calibration.tsv"
RESULT_PATH = OUT / "gdt459_result.json"
VALIDATION_PATH = OUT / "gdt459_validation.json"

EXPECTED_TIERS = {
    "A_EXACT_RUNNING_FORMULA": 61,
    "B_ATTESTED_RECIPE_NEW_SURFACE": 7,
    "C_SHORT_OR_REPEATED_COMPOSITION": 8,
    "D_OWNER_LEARNED_WHOLE_LABEL": 107,
}
EXPECTED_CONTENT = {
    "BATH_OR_OUTLET_STATION": 6,
    "DRUG_OR_INGREDIENT_OBJECT": 35,
    "PICTURED_PLANT": 2,
    "STAR_BEARING_RING_POSITION": 64,
}
EXPECTED_IMAGES = {
    "f17r": ("1006106", "eccb822a72a8c27045aefa4f19d558dba29ef046c1d8e3772c715a99ee7113b9"),
    "f71v": ("1006203", "7eaf311574f105436335d50d4e67b33cef6191e32d0c54742d30a7076e966c93"),
    "f72r": ("1006203", "7eaf311574f105436335d50d4e67b33cef6191e32d0c54742d30a7076e966c93"),
    "f77r": ("1006212", "6bcedcaccc8107da32d6d1ca950b96708b529538d7902a2108398a3c0b9327df"),
    "f88v": ("1006233", "e146c6ff04664783f8e9a5d2cadcf7eb653498320ab431a11ba9cd47d8efe30c"),
    "f89r": ("1006233", "e146c6ff04664783f8e9a5d2cadcf7eb653498320ab431a11ba9cd47d8efe30c"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    running = read_tsv(RUNNING_PATH)
    local = read_tsv(LOCAL_PATH)
    source_addresses = [row for row in local if row["component_recipe"] == "LOCAL_ADDRESS"]
    events = read_tsv(EVENT_PATH)
    surfaces = read_tsv(SURFACE_PATH)
    owners = read_tsv(OWNER_PATH)
    calibration = read_tsv(CALIBRATION_PATH)
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    check("source_running_count", len(running) == 4576, f"observed={len(running)} expected=4576")
    check("source_local_count", len(local) == 693, f"observed={len(local)} expected=693")
    check("source_address_count", len(source_addresses) == 183, f"observed={len(source_addresses)} expected=183")
    check("event_output_count", len(events) == 183, f"observed={len(events)} expected=183")
    check("surface_output_count", len(surfaces) == 162, f"observed={len(surfaces)} expected=162")
    check("owner_output_count", len(owners) == 22, f"observed={len(owners)} expected=22")
    check("event_ids_unique", len({row["gdt459_address_id"] for row in events}) == 183, "183 unique GDT459 IDs")
    check("source_event_ids_unique", len({row["source_event_id"] for row in events}) == 183, "183 unique source IDs")
    check(
        "source_order_exact",
        [row["source_event_id"] for row in events] == [row["source_event_id"] for row in source_addresses],
        "output preserves every LOCAL_ADDRESS in source order",
    )
    check(
        "source_surface_exact",
        [row["surface"] for row in events] == [row["surface"] for row in source_addresses],
        "output surface sequence equals source",
    )
    check(
        "source_context_exact",
        all(
            tuple(event[key] for key in ("physical_page", "register", "locus", "source_order", "owner_de"))
            == tuple(source[key] for key in ("physical_page", "register", "locus", "source_order", "owner_de"))
            for event, source in zip(events, source_addresses)
        ),
        "page/register/locus/order/owner retained",
    )

    tier_counts = Counter(row["decision_tier"] for row in events)
    check("tier_counts", dict(tier_counts) == EXPECTED_TIERS, f"observed={dict(tier_counts)}")
    check("formula_event_count", sum(not row["decision_tier"].startswith("D_") for row in events) == 76, "76 formula events")
    check("whole_event_count", sum(row["decision_tier"].startswith("D_") for row in events) == 107, "107 learned whole-label events")
    check("formula_surface_count", sum(not row["decision_tier"].startswith("D_") for row in surfaces) == 55, "55 formula surfaces")
    check("whole_surface_count", sum(row["decision_tier"].startswith("D_") for row in surfaces) == 107, "107 learned whole-label surfaces")
    whole_content = Counter(row["content_class"] for row in events if row["decision_tier"].startswith("D_"))
    check("whole_content_counts", dict(whole_content) == EXPECTED_CONTENT, f"observed={dict(whole_content)}")
    check(
        "whole_labels_are_singletons",
        all(row["local_surface_event_count"] == "1" for row in events if row["decision_tier"].startswith("D_")),
        "all 107 retained whole labels occur once in the selected address set",
    )

    running_by_surface: dict[str, set[str]] = {}
    running_recipe_counts = Counter(row["component_recipe"] for row in running)
    for row in running:
        running_by_surface.setdefault(row["surface"], set()).add(row["component_recipe"])
    check(
        "tier_a_exact_running",
        all(
            row["surface"] in running_by_surface
            and running_by_surface[row["surface"]] == {row["selected_recipe_or_whole_class"]}
            and row["decision_evidence"] == "EXACT_SURFACE_HAS_ONE_RUNNING_RECIPE"
            for row in events if row["decision_tier"].startswith("A_")
        ),
        "every A row has one invariant running recipe",
    )
    check(
        "tier_b_attested_recipe",
        all(
            row["surface"] not in running_by_surface
            and row["selected_recipe_or_whole_class"] == row["minimal_segmentation_recipe"]
            and running_recipe_counts[row["selected_recipe_or_whole_class"]] > 0
            for row in events if row["decision_tier"].startswith("B_")
        ),
        "every B recipe occurs in running prose under another surface",
    )
    check(
        "tier_c_bounded",
        all(
            row["surface"] not in running_by_surface
            and row["selected_recipe_or_whole_class"] == row["minimal_segmentation_recipe"]
            and (row["minimal_segmentation_atom_count"] == "2" or int(row["local_surface_event_count"]) > 1)
            and not row["factor_gate_status"].startswith("STOP")
            for row in events if row["decision_tier"].startswith("C_")
        ),
        "every C row is a short or repeated non-stop composition",
    )
    check(
        "tier_d_is_complement",
        all(
            row["selected_recipe_or_whole_class"].startswith("WHOLE_LABEL::")
            and row["semantic_status"] == "LEARNED_NOMENCLATOR_WHOLE_LABEL"
            for row in events if row["decision_tier"].startswith("D_")
        ),
        "D rows remain owner-bound learned labels",
    )

    per_surface: dict[str, list[dict[str, str]]] = {}
    for row in events:
        per_surface.setdefault(row["surface"], []).append(row)
    surface_index = {row["surface"]: row for row in surfaces}
    check("surface_dictionary_keyset", set(surface_index) == set(per_surface), "surface dictionary covers exactly the 162 event surfaces")
    check(
        "surface_dictionary_invariant",
        all(
            int(surface_index[surface]["occurrence_count"]) == len(rows)
            and len({row["decision_tier"] for row in rows}) == 1
            and len({row["selected_recipe_or_whole_class"] for row in rows}) == 1
            and len({row["short_default_de"] for row in rows}) == 1
            and surface_index[surface]["decision_tier"] == rows[0]["decision_tier"]
            and surface_index[surface]["selected_recipe_or_whole_class"] == rows[0]["selected_recipe_or_whole_class"]
            and surface_index[surface]["short_default_de"] == rows[0]["short_default_de"]
            for surface, rows in per_surface.items()
        ),
        "one tier, recipe/class and short default per surface",
    )
    check(
        "owner_totals",
        sum(int(row["address_event_count"]) for row in owners) == 183
        and sum(int(row["tier_a_exact_formula_count"]) for row in owners) == 61
        and sum(int(row["tier_b_attested_recipe_count"]) for row in owners) == 7
        and sum(int(row["tier_c_provisional_composition_count"]) for row in owners) == 8
        and sum(int(row["tier_d_whole_label_count"]) for row in owners) == 107,
        "owner clusters reconcile to event totals",
    )
    check("allowed_pages_exact", set(row["physical_page"] for row in events) == set(EXPECTED_IMAGES), "exact six already admitted pages")
    check(
        "image_bindings_exact",
        all((row["image_object_id"], row["review_image_sha256"]) == EXPECTED_IMAGES[row["physical_page"]] for row in events),
        "official image object IDs and reviewed hashes match page bindings",
    )
    check(
        "defaults_concrete_nonempty",
        all(row["short_default_de"].strip() and not any(term in row["short_default_de"].upper() for term in ("UNKNOWN", "EXEMPLAR", "FORMAL")) for row in events),
        "183/183 short defaults are nonempty and concrete",
    )
    check(
        "calibration_anchor",
        any(row["calibration_slice"] == "ALL_PARSED" and row["parsed_surface_count"] == "761" and row["exact_recipe_recovery_count"] == "442" and row["exact_recipe_recovery_rate"] == "0.580815" for row in calibration)
        and any(row["calibration_slice"] == "PREDICTED_RECIPE_HAS_OTHER_SURFACE" and row["parsed_surface_count"] == "253" and row["exact_recipe_recovery_count"] == "185" and row["exact_recipe_recovery_rate"] == "0.731225" for row in calibration),
        "segmenter calibration anchors retained",
    )
    check("result_status", result["status"] == "MIXED_PORTABLE_ADDRESS_FORMULAS_AND_LEARNED_LOCAL_NOMENCLATOR", result["status"])
    check(
        "result_counts",
        result["source_local_group_count"] == 693
        and result["opaque_address_source_count"] == 183
        and result["opaque_address_surface_count"] == 162
        and result["owner_cluster_count"] == 22
        and result["tier_counts"] == EXPECTED_TIERS
        and result["formula_event_count"] == 76
        and result["whole_label_event_count"] == 107
        and result["formula_surface_count"] == 55
        and result["whole_label_surface_count"] == 107
        and result["whole_label_content_counts"] == EXPECTED_CONTENT,
        "result JSON reconciles with release tables",
    )
    check(
        "claim_ceiling_zeroes",
        all(result[key] == 0 for key in ("core_meaning_revisions", "new_pages", "surface_predictions", "confirmed_lexemes")),
        "no core revision, new page, surface prediction, or confirmed lexeme",
    )
    serialized = "\n".join(path.read_text(encoding="utf-8") for path in (EVENT_PATH, SURFACE_PATH, OWNER_PATH, CALIBRATION_PATH, RESULT_PATH))
    check("sealed_pages_absent", "f84" not in serialized.lower(), "no sealed folio token in release artifacts")
    check(
        "artifact_size_gate",
        all(path.stat().st_size < 5_000_000 for path in (EVENT_PATH, SURFACE_PATH, OWNER_PATH, CALIBRATION_PATH, RESULT_PATH)),
        "all release artifacts are below 5 MB",
    )

    generated = (EVENT_PATH, SURFACE_PATH, OWNER_PATH, CALIBRATION_PATH, RESULT_PATH)
    before = {path: path.read_bytes() for path in generated}
    completed = subprocess.run([sys.executable, str(RUN_SCRIPT)], cwd=ROOT, check=False, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in generated}
    check("deterministic_rebuild_exit", completed.returncode == 0, f"returncode={completed.returncode}")
    check("deterministic_rebuild_bytes", before == after, "all five generated artifacts are byte-identical after rebuild")

    passed = sum(bool(row["passed"]) for row in checks)
    validation = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
    }
    VALIDATION_PATH.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
