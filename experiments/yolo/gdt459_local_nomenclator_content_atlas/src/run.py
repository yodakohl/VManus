#!/usr/bin/env python3
"""Separate portable address formulae from learned local nomenclator labels."""

from __future__ import annotations

import csv
import functools
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
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
GDT407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
RUNNING = GDT407 / "gdt407_4576_running_event_edition.tsv"
LOCAL = GDT407 / "gdt407_693_local_group_edition.tsv"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
READER_PATH = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/src/factor_gate_stream_read.py"

CONTENT_DEFAULT = {
    "HERBAL": ("PICTURED_PLANT", "PFLANZENNAME"),
    "CELESTIAL": ("STAR_BEARING_RING_POSITION", "STERNSTELLENNAME"),
    "BIOLOGICAL": ("BATH_OR_OUTLET_STATION", "BADSTATIONSNAME"),
    "PHARMA": ("DRUG_OR_INGREDIENT_OBJECT", "DROGENNAME"),
}

IMAGE_META = {
    "f17r": ("1006106", "https://collections.library.yale.edu/iiif/2/1006106/full/2000,/0/default.jpg", "eccb822a72a8c27045aefa4f19d558dba29ef046c1d8e3772c715a99ee7113b9"),
    "f71v": ("1006203", "https://collections.library.yale.edu/iiif/2/1006203/full/3000,/0/default.jpg", "7eaf311574f105436335d50d4e67b33cef6191e32d0c54742d30a7076e966c93"),
    "f72r": ("1006203", "https://collections.library.yale.edu/iiif/2/1006203/full/3000,/0/default.jpg", "7eaf311574f105436335d50d4e67b33cef6191e32d0c54742d30a7076e966c93"),
    "f77r": ("1006212", "https://collections.library.yale.edu/iiif/2/1006212/full/2000,/0/default.jpg", "6bcedcaccc8107da32d6d1ca950b96708b529538d7902a2108398a3c0b9327df"),
    "f88v": ("1006233", "https://collections.library.yale.edu/iiif/2/1006233/full/3000,/0/default.jpg", "e146c6ff04664783f8e9a5d2cadcf7eb653498320ab431a11ba9cd47d8efe30c"),
    "f89r": ("1006233", "https://collections.library.yale.edu/iiif/2/1006233/full/3000,/0/default.jpg", "e146c6ff04664783f8e9a5d2cadcf7eb653498320ab431a11ba9cd47d8efe30c"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    reader = load_module("gdt459_factor_reader", READER_PATH)
    running = read_tsv(RUNNING)
    local_all = read_tsv(LOCAL)
    addresses = [row for row in local_all if row["component_recipe"] == "LOCAL_ADDRESS"]
    values = {row["atom"]: row["working_value_de"] for row in read_tsv(COMPONENTS)}

    surface_atom_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in running + local_all:
        recipe = row["component_recipe"]
        if "+" not in recipe and recipe not in {"LOCAL_ADDRESS", "SECTION_MARKER"}:
            surface_atom_counts[row["surface"]][recipe] += 1
    atomic_forms = {
        surface: next(iter(counts))
        for surface, counts in surface_atom_counts.items()
        if len(counts) == 1
    }
    form_frequency = Counter(
        row["surface"] for row in running + local_all
        if row["surface"] in atomic_forms and row["component_recipe"] == atomic_forms[row["surface"]]
    )

    @functools.lru_cache(maxsize=None)
    def segment(surface: str) -> tuple[tuple[tuple[str, str], ...], ...]:
        if not surface:
            return ((),)
        candidates: list[tuple[tuple[str, str], ...]] = []
        for form, atom in atomic_forms.items():
            if surface.startswith(form):
                for tail in segment(surface[len(form):]):
                    candidates.append(((atom, form),) + tail)
        return tuple(candidates)

    def segment_score(candidate: tuple[tuple[str, str], ...]) -> tuple[object, ...]:
        return (
            len(candidate),
            -sum(math.log1p(form_frequency[form]) for _, form in candidate),
            tuple(atom for atom, _ in candidate),
        )

    running_surface_recipe: dict[str, str] = {}
    running_surface_counts = Counter(row["surface"] for row in running)
    running_recipe_counts = Counter(row["component_recipe"] for row in running)
    for row in running:
        previous = running_surface_recipe.setdefault(row["surface"], row["component_recipe"])
        if previous != row["component_recipe"]:
            raise RuntimeError(f"Non-invariant running surface recipe: {row['surface']}")
    local_surface_counts = Counter(row["surface"] for row in addresses)

    event_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate(addresses, start=1):
        surface = row["surface"]
        parses = segment(surface)
        best = min(parses, key=segment_score) if parses else ()
        candidate_recipe = "+".join(atom for atom, _ in best) if best else "NONE"
        candidate_forms = "|".join(form for _, form in best) if best else "NONE"
        gate = reader.gate_recipe(candidate_recipe, "NONE") if best else {
            "factor_gate_status": "NOT_TESTED_NO_SEGMENTATION",
            "portable_factor_rules": "NONE",
            "amber_factor_rules": "NONE",
            "blocked_factor_rules": "NONE",
        }
        if surface in running_surface_recipe:
            tier = "A_EXACT_RUNNING_FORMULA"
            selected_recipe = running_surface_recipe[surface]
            semantic_status = "PORTABLE_ADDRESS_FORMULA"
            confidence = "HIGH_WORKING"
            evidence = "EXACT_SURFACE_HAS_ONE_RUNNING_RECIPE"
            gate_status = "EXACT_RUNNING_RECIPE"
        elif best and candidate_recipe in running_recipe_counts:
            tier = "B_ATTESTED_RECIPE_NEW_SURFACE"
            selected_recipe = candidate_recipe
            semantic_status = "PORTABLE_ADDRESS_FORMULA"
            confidence = "HIGH_WORKING"
            evidence = "MINIMAL_CONCATENATION_EQUALS_OBSERVED_RECIPE"
            gate_status = gate["factor_gate_status"]
        elif best and (len(best) == 2 or local_surface_counts[surface] > 1) and not gate["factor_gate_status"].startswith("STOP"):
            tier = "C_SHORT_OR_REPEATED_COMPOSITION"
            selected_recipe = candidate_recipe
            semantic_status = "PROVISIONAL_ADDRESS_FORMULA"
            confidence = "MEDIUM_CREATIVE"
            evidence = "TWO_ATOM_CONCATENATION_OR_REPEATED_LOCAL_FORM"
            gate_status = gate["factor_gate_status"]
        else:
            tier = "D_OWNER_LEARNED_WHOLE_LABEL"
            selected_recipe = "WHOLE_LABEL::" + CONTENT_DEFAULT[row["register"]][0]
            semantic_status = "LEARNED_NOMENCLATOR_WHOLE_LABEL"
            confidence = "CONCRETE_OWNER_DEFAULT"
            evidence = "OWNER_OBJECT_CLASS__NO_LICENSED_SHORT_FORMULA"
            gate_status = gate["factor_gate_status"]
        content_class, whole_default = CONTENT_DEFAULT[row["register"]]
        if tier.startswith("D_"):
            default = whole_default
        else:
            default = " · ".join(values[atom] for atom in selected_recipe.split("+"))
        object_id, image_url, image_hash = IMAGE_META[row["physical_page"]]
        event_rows.append({
            "gdt459_address_id": f"G459-L{ordinal:03d}",
            "source_event_id": row["source_event_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "locus": row["locus"],
            "source_order": row["source_order"],
            "owner_de": row["owner_de"],
            "surface": surface,
            "content_class": content_class,
            "decision_tier": tier,
            "semantic_status": semantic_status,
            "selected_recipe_or_whole_class": selected_recipe,
            "short_default_de": default,
            "confidence": confidence,
            "decision_evidence": evidence,
            "running_surface_event_count": running_surface_counts[surface],
            "running_selected_recipe_event_count": running_recipe_counts[selected_recipe],
            "local_surface_event_count": local_surface_counts[surface],
            "segmentation_candidate_count": len(parses),
            "minimal_segmentation_recipe": candidate_recipe,
            "minimal_segmentation_forms": candidate_forms,
            "minimal_segmentation_atom_count": len(best),
            "factor_gate_status": gate_status,
            "portable_factor_rules": gate.get("portable_factor_rules", "NONE"),
            "amber_factor_rules": gate.get("amber_factor_rules", "NONE"),
            "blocked_factor_rules": gate.get("blocked_factor_rules", "NONE"),
            "strongest_rival": "WHOLE_LOCAL_OBJECT_NAME" if not tier.startswith("D_") else "LONG_COMPOSITIONAL_ADDRESS",
            "image_object_id": object_id,
            "image_url": image_url,
            "review_image_sha256": image_hash,
        })
    write_tsv(OUT / "gdt459_183_address_interlinear.tsv", event_rows)

    surface_rows: list[dict[str, object]] = []
    for surface in sorted({row["surface"] for row in event_rows}):
        selected = [row for row in event_rows if row["surface"] == surface]
        recipes = {str(row["selected_recipe_or_whole_class"]) for row in selected}
        defaults = {str(row["short_default_de"]) for row in selected}
        tiers = {str(row["decision_tier"]) for row in selected}
        if len(recipes) != 1 or len(defaults) != 1 or len(tiers) != 1:
            raise RuntimeError(f"Local surface is not invariant: {surface}")
        surface_rows.append({
            "surface": surface,
            "occurrence_count": len(selected),
            "pages": "|".join(sorted({str(row["physical_page"]) for row in selected})),
            "registers": "|".join(sorted({str(row["register"]) for row in selected})),
            "content_classes": "|".join(sorted({str(row["content_class"]) for row in selected})),
            "decision_tier": next(iter(tiers)),
            "semantic_status": selected[0]["semantic_status"],
            "selected_recipe_or_whole_class": next(iter(recipes)),
            "short_default_de": next(iter(defaults)),
            "confidence": selected[0]["confidence"],
            "source_event_ids": "|".join(str(row["source_event_id"]) for row in selected),
        })
    write_tsv(OUT / "gdt459_162_surface_dictionary.tsv", surface_rows)

    owner_rows: list[dict[str, object]] = []
    owner_groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        owner_groups[(str(row["physical_page"]), str(row["register"]), str(row["owner_de"]))].append(row)
    for ordinal, ((page, register, owner), rows) in enumerate(sorted(owner_groups.items()), start=1):
        counts = Counter(str(row["decision_tier"])[0] for row in rows)
        owner_rows.append({
            "owner_cluster_id": f"G459-O{ordinal:02d}",
            "physical_page": page,
            "register": register,
            "owner_de": owner,
            "content_class": CONTENT_DEFAULT[register][0],
            "address_event_count": len(rows),
            "distinct_surface_count": len({str(row["surface"]) for row in rows}),
            "tier_a_exact_formula_count": counts["A"],
            "tier_b_attested_recipe_count": counts["B"],
            "tier_c_provisional_composition_count": counts["C"],
            "tier_d_whole_label_count": counts["D"],
            "whole_label_default_de": CONTENT_DEFAULT[register][1],
            "image_object_id": IMAGE_META[page][0],
            "review_image_sha256": IMAGE_META[page][2],
        })
    write_tsv(OUT / "gdt459_22_owner_cluster_summary.tsv", owner_rows)

    unique_running: dict[str, str] = {}
    for row in running:
        unique_running.setdefault(row["surface"], row["component_recipe"])
    calibration_items: list[dict[str, object]] = []
    for surface, true_recipe in unique_running.items():
        parses = segment(surface)
        if not parses:
            continue
        best = min(parses, key=segment_score)
        prediction = "+".join(atom for atom, _ in best)
        forms = [form for _, form in best]
        calibration_items.append({
            "exact": prediction == true_recipe,
            "atom_count": len(best),
            "has_single_character_form": any(len(form) == 1 for form in forms),
            "predicted_recipe_has_other_surface": any(
                other_surface != surface and other_recipe == prediction
                for other_surface, other_recipe in unique_running.items()
            ),
        })

    calibration_rows: list[dict[str, object]] = []
    def add_calibration(name: str, subset: list[dict[str, object]]) -> None:
        exact = sum(bool(row["exact"]) for row in subset)
        calibration_rows.append({
            "calibration_slice": name,
            "parsed_surface_count": len(subset),
            "exact_recipe_recovery_count": exact,
            "exact_recipe_recovery_rate": f"{exact / len(subset):.6f}" if subset else "0.000000",
            "use_in_decision": "YES" if name in {"ALL_PARSED", "PREDICTED_RECIPE_HAS_OTHER_SURFACE"} else "DIAGNOSTIC",
        })
    add_calibration("ALL_PARSED", calibration_items)
    add_calibration("NO_SINGLE_CHARACTER_FORM", [row for row in calibration_items if not row["has_single_character_form"]])
    add_calibration("HAS_SINGLE_CHARACTER_FORM", [row for row in calibration_items if row["has_single_character_form"]])
    add_calibration("PREDICTED_RECIPE_HAS_OTHER_SURFACE", [row for row in calibration_items if row["predicted_recipe_has_other_surface"]])
    add_calibration("PREDICTED_RECIPE_NEW", [row for row in calibration_items if not row["predicted_recipe_has_other_surface"]])
    for atom_count in sorted({int(row["atom_count"]) for row in calibration_items}):
        add_calibration(f"ATOM_COUNT_{atom_count}", [row for row in calibration_items if row["atom_count"] == atom_count])
    write_tsv(OUT / "gdt459_segmentation_calibration.tsv", calibration_rows)

    tier_counts = Counter(str(row["decision_tier"]) for row in event_rows)
    result = {
        "status": "MIXED_PORTABLE_ADDRESS_FORMULAS_AND_LEARNED_LOCAL_NOMENCLATOR",
        "source_local_group_count": len(local_all),
        "opaque_address_source_count": len(addresses),
        "opaque_address_surface_count": len(surface_rows),
        "owner_cluster_count": len(owner_rows),
        "address_page_count": len({row["physical_page"] for row in addresses}),
        "tier_counts": dict(sorted(tier_counts.items())),
        "formula_event_count": sum(not str(row["decision_tier"]).startswith("D_") for row in event_rows),
        "whole_label_event_count": sum(str(row["decision_tier"]).startswith("D_") for row in event_rows),
        "formula_surface_count": sum(not str(row["decision_tier"]).startswith("D_") for row in surface_rows),
        "whole_label_surface_count": sum(str(row["decision_tier"]).startswith("D_") for row in surface_rows),
        "whole_label_content_counts": dict(sorted(Counter(
            str(row["content_class"]) for row in event_rows if str(row["decision_tier"]).startswith("D_")
        ).items())),
        "nonempty_default_count": sum(bool(str(row["short_default_de"])) for row in event_rows),
        "core_meaning_revisions": 0,
        "new_pages": 0,
        "surface_predictions": 0,
        "confirmed_lexemes": 0,
    }
    (OUT / "gdt459_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
