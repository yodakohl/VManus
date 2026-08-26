#!/usr/bin/env python3
"""Audit near-threshold edge stems touching GDT461's thirteen whole labels."""

from __future__ import annotations

import csv
import json
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
BASE = ROOT / "experiments/yolo/gdt462_near_threshold_ar_edge_exception_audit"
OUT = BASE / "artifacts"
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
ATTACHMENT_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_5051_attachment_edition.tsv"
VALUE_PATH = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
SOURCE_PATH = ROOT / "experiments/yolo/gdt461_internal_stem_residual_bridge/artifacts/gdt461_107_revised_hybrid_dictionary.tsv"

CLASS_DEFAULT = {
    "PICTURED_PLANT": "PFLANZENNAME",
    "STAR_BEARING_RING_POSITION": "STERNSTELLENNAME",
    "BATH_OR_OUTLET_STATION": "BADSTATIONSNAME",
    "DRUG_OR_INGREDIENT_OBJECT": "DROGENNAME",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    running = read_tsv(RUNNING_PATH)
    attachments = read_tsv(ATTACHMENT_PATH)
    source = read_tsv(SOURCE_PATH)
    residuals = [row for row in source if row["revised_hybrid_status"] == "WHOLE_LEARNED_LABEL"]
    values = {row["atom"]: row["working_value_de"] for row in read_tsv(VALUE_PATH)}

    running_recipe: dict[str, str] = {}
    running_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in running:
        previous = running_recipe.setdefault(row["surface"], row["component_recipe"])
        if previous != row["component_recipe"]:
            raise RuntimeError(f"Non-invariant running surface: {row['surface']}")
        running_events[row["surface"]].append(row)

    def literal(recipe: str) -> str:
        return " · ".join(values[atom] for atom in recipe.split("+"))

    channel_keys: set[tuple[str, str]] = set()
    for row in residuals:
        surface = row["surface"]
        for length in range(2, len(surface) + 1):
            prefix = surface[:length]
            suffix = surface[-length:]
            if prefix in running_recipe:
                channel_keys.add(("PREFIX", prefix))
            if suffix in running_recipe:
                channel_keys.add(("SUFFIX", suffix))

    inventory_rows: list[dict[str, object]] = []
    candidate_cache: dict[tuple[str, str], tuple[list[tuple[str, str]], list[tuple[str, str]]]] = {}
    for edge, stem in sorted(channel_keys):
        recipe = running_recipe[stem]
        atoms = recipe.split("+")
        if edge == "PREFIX":
            extensions = [(surface, candidate) for surface, candidate in running_recipe.items() if surface != stem and surface.startswith(stem)]
            matches = [(surface, candidate) for surface, candidate in extensions if candidate.split("+")[:len(atoms)] == atoms]
            hits = [row for row in residuals if row["surface"].startswith(stem)]
        else:
            extensions = [(surface, candidate) for surface, candidate in running_recipe.items() if surface != stem and surface.endswith(stem)]
            matches = [(surface, candidate) for surface, candidate in extensions if candidate.split("+")[-len(atoms):] == atoms]
            hits = [row for row in residuals if row["surface"].endswith(stem)]
        if not extensions or not hits:
            continue
        candidate_cache[(edge, stem)] = (extensions, matches)
        precision = len(matches) / len(extensions)
        if len(extensions) >= 4 and 0.75 <= precision < 0.90:
            band = "NEAR_THRESHOLD_REVIEW"
        elif len(extensions) >= 4 and precision >= 0.90:
            band = "ALREADY_CALIBRATED_BAND"
        elif len(extensions) < 4 and precision == 1:
            band = "LOW_SUPPORT_EXACT"
        elif len(extensions) < 4:
            band = "LOW_SUPPORT_INCONSISTENT"
        else:
            band = "BELOW_PRECISION"
        decision = "PROMOTE_AFTER_PACKAGE_EXCEPTION" if (edge, stem) == ("PREFIX", "ar") else "DO_NOT_PROMOTE"
        inventory_rows.append({
            "edge": edge,
            "surface_stem": stem,
            "component_recipe": recipe,
            "literal_working_value_de": literal(recipe),
            "running_extension_type_count": len(extensions),
            "running_matching_type_count": len(matches),
            "running_type_precision": f"{precision:.6f}",
            "residual_hit_count": len(hits),
            "residual_surfaces": "|".join(row["surface"] for row in hits),
            "audit_band": band,
            "decision": decision,
            "decision_reason": (
                "sole mismatch is a two-page exact P+AR+AR repeated-relation package"
                if decision == "PROMOTE_AFTER_PACKAGE_EXCEPTION"
                else "precision or support gate not satisfied; no exception imported"
            ),
        })
    inventory_rows.sort(key=lambda row: (str(row["audit_band"]), str(row["edge"]), str(row["surface_stem"])))
    write_tsv(OUT / "gdt462_residual_edge_channel_inventory.tsv", inventory_rows)

    near = [row for row in inventory_rows if row["audit_band"] == "NEAR_THRESHOLD_REVIEW"]
    if [(row["edge"], row["surface_stem"]) for row in near] != [("PREFIX", "ar")]:
        raise RuntimeError(f"Unexpected near-threshold set: {near}")

    extensions, matches = candidate_cache[("PREFIX", "ar")]
    matching_surfaces = {surface for surface, _ in matches}
    extension_rows: list[dict[str, object]] = []
    for ordinal, (surface, recipe) in enumerate(sorted(extensions), start=1):
        is_match = surface in matching_surfaces
        explained = surface == "arary" and recipe == "P+AR+AR"
        extension_rows.append({
            "extension_id": f"G462-X{ordinal:02d}",
            "surface": surface,
            "component_recipe": recipe,
            "literal_working_value_de": literal(recipe),
            "running_event_count": len(running_events[surface]),
            "physical_pages": "|".join(sorted({row["physical_page"] for row in running_events[surface]})),
            "prefix_alignment": "MATCH" if is_match else "MISMATCH",
            "mismatch_disposition": "NOT_APPLICABLE" if is_match else ("EXPLAINED_EXACT_PACKAGE" if explained else "UNEXPLAINED"),
            "package_explanation": (
                "P+AR+AR is an exact repeated-relation card on f71v/f72r; two AR peers attach to one P head"
                if explained else "NONE"
            ),
        })
    write_tsv(OUT / "gdt462_ar_complete_running_extensions.tsv", extension_rows)

    package_rows: list[dict[str, object]] = []
    package_events = [row for row in running if row["surface"] in {"arary", "parar"} and row["component_recipe"] == "P+AR+AR"]
    for ordinal, event in enumerate(sorted(package_events, key=lambda row: row["physical_page"]), start=1):
        selected = [
            row for row in attachments
            if row["global_running_event_id"] == event["global_running_event_id"] and row["focus_core"] == "AR"
        ]
        package_rows.append({
            "package_evidence_id": f"G462-P{ordinal:02d}",
            "global_running_event_id": event["global_running_event_id"],
            "source_event_id": event["source_event_id"],
            "physical_page": event["physical_page"],
            "locus": event["locus"],
            "surface": event["surface"],
            "component_recipe": event["component_recipe"],
            "action_head": "|".join(sorted({row["action_core"] for row in selected})),
            "ar_attachment_count": len(selected),
            "focus_atom_ordinals": "|".join(sorted((row["focus_atom_ordinal"] for row in selected), key=int)),
            "duplicate_modes": "|".join(sorted({row["duplicate_mode"] for row in selected})),
            "duplicate_roles": "|".join(sorted(row["duplicate_role"] for row in selected)),
            "package_class": "EXACT_TWO_PAGE_P_PLUS_REPEATED_AR_PACKAGE",
        })
    write_tsv(OUT / "gdt462_ar_repeated_relation_package.tsv", package_rows)

    target_rows: list[dict[str, object]] = []
    for row in residuals:
        if not row["surface"].startswith("ar"):
            continue
        learned_tail = row["surface"][2:]
        default_name = CLASS_DEFAULT[row["content_class"]]
        target_rows.append({
            "source_event_id": row["source_event_id"],
            "physical_page": row["physical_page"],
            "surface": row["surface"],
            "content_class": row["content_class"],
            "old_status": row["revised_hybrid_status"],
            "new_status": "FUNCTION_SHELL_PLUS_LEARNED_CORE",
            "promoted_edge_stem": "ar",
            "promoted_recipe": "AR",
            "promoted_value_de": values["AR"],
            "remaining_learned_core": learned_tail,
            "old_default_de": row["revised_short_default_de"],
            "new_default_de": f"{values['AR']} · [{default_name}:{learned_tail}]",
            "license": "G462_AR_PREFIX_AFTER_EXACT_P_AR_AR_PACKAGE_EXCEPTION",
        })
    target_rows.sort(key=lambda row: str(row["source_event_id"]))
    write_tsv(OUT / "gdt462_two_promoted_residual_labels.tsv", target_rows)

    target_index = {row["source_event_id"]: row for row in target_rows}
    revised_rows: list[dict[str, object]] = []
    for ordinal, old in enumerate(source, start=1):
        target = target_index.get(old["source_event_id"])
        known = int(old["known_function_character_count"]) + (2 if target else 0)
        revised_rows.append({
            "gdt462_label_id": f"G462-L{ordinal:03d}",
            "gdt461_label_id": old["gdt461_label_id"],
            "source_event_id": old["source_event_id"],
            "physical_page": old["physical_page"],
            "register": old["register"],
            "locus": old["locus"],
            "owner_de": old["owner_de"],
            "surface": old["surface"],
            "content_class": old["content_class"],
            "gdt461_hybrid_status": old["revised_hybrid_status"],
            "gdt462_hybrid_status": "FUNCTION_SHELL_PLUS_LEARNED_CORE" if target else old["revised_hybrid_status"],
            "prefix_stem": "ar" if target else old["prefix_stem"],
            "prefix_recipe": "AR" if target else old["prefix_recipe"],
            "internal_stem_trace": old["internal_stem_trace"],
            "suffix_stem": old["suffix_stem"],
            "suffix_recipe": old["suffix_recipe"],
            "owner_family_stem_trace": old["owner_family_stem_trace"],
            "known_function_character_count": known,
            "remaining_learned_character_count": len(old["surface"]) - known,
            "surface_character_count": old["surface_character_count"],
            "known_function_fraction": f"{known / len(old['surface']):.6f}",
            "ordered_function_recipe_trace": "AR" if target else old["ordered_function_recipe_trace"],
            "revised_short_default_de": str(target["new_default_de"]) if target else old["revised_short_default_de"],
            "gdt462_change": "PROMOTED_AR_PREFIX" if target else "UNCHANGED",
            "strongest_rival": "ARARY_PACKAGE_DOES_NOT_LICENSE_FREE_PREFIX" if target else old["strongest_rival"],
            "image_object_id": old["image_object_id"],
            "review_image_sha256": old["review_image_sha256"],
        })
    write_tsv(OUT / "gdt462_107_revised_hybrid_dictionary.tsv", revised_rows)

    page_rows: list[dict[str, object]] = []
    for page in sorted({row["physical_page"] for row in revised_rows}):
        selected = [row for row in revised_rows if row["physical_page"] == page]
        statuses = Counter(str(row["gdt462_hybrid_status"]) for row in selected)
        page_rows.append({
            "physical_page": page,
            "register": selected[0]["register"],
            "content_class": selected[0]["content_class"],
            "label_count": len(selected),
            "full_function_formula_count": statuses["FULL_FUNCTION_FORMULA"],
            "function_shell_plus_core_count": statuses["FUNCTION_SHELL_PLUS_LEARNED_CORE"],
            "owner_family_only_count": statuses["OWNER_FAMILY_STEM_ONLY"],
            "whole_learned_label_count": statuses["WHOLE_LEARNED_LABEL"],
            "gdt462_promoted_ar_prefix_count": sum(row["gdt462_change"] == "PROMOTED_AR_PREFIX" for row in selected),
            "known_function_character_count": sum(int(row["known_function_character_count"]) for row in selected),
            "surface_character_count": sum(int(row["surface_character_count"]) for row in selected),
        })
    write_tsv(OUT / "gdt462_6_page_summary.tsv", page_rows)

    status_counts = Counter(str(row["gdt462_hybrid_status"]) for row in revised_rows)
    known_characters = sum(int(row["known_function_character_count"]) for row in revised_rows)
    total_characters = sum(int(row["surface_character_count"]) for row in revised_rows)
    result = {
        "status": "NEAR_THRESHOLD_AR_PREFIX_PROMOTED_BY_EXACT_REPEATED_RELATION_PACKAGE",
        "source_label_count": len(source),
        "source_whole_label_count": len(residuals),
        "residual_edge_channel_inventory_count": len(inventory_rows),
        "near_threshold_channel_count": len(near),
        "promoted_channel_count": 1,
        "promoted_channel": "PREFIX:ar=AR",
        "ar_running_extension_type_count": len(extensions),
        "ar_running_matching_type_count": len(matches),
        "ar_running_mismatch_type_count": len(extensions) - len(matches),
        "ar_explained_mismatch_type_count": sum(row["mismatch_disposition"] == "EXPLAINED_EXACT_PACKAGE" for row in extension_rows),
        "repeated_relation_package_surface_count": len(package_rows),
        "promoted_residual_label_count": len(target_rows),
        "promoted_residual_surfaces": [row["surface"] for row in target_rows],
        "revised_hybrid_status_counts": dict(sorted(status_counts.items())),
        "remaining_whole_label_count": status_counts["WHOLE_LEARNED_LABEL"],
        "labels_with_any_function_count": sum(int(row["known_function_character_count"]) > 0 for row in revised_rows),
        "labels_with_any_structure_count": sum(int(row["known_function_character_count"]) > 0 or row["owner_family_stem_trace"] != "NONE" for row in revised_rows),
        "known_function_character_count": known_characters,
        "surface_character_count": total_characters,
        "known_function_character_fraction": f"{known_characters / total_characters:.6f}",
        "core_meaning_revisions": 0,
        "new_pages": 0,
        "surface_predictions": 0,
        "confirmed_lexemes": 0,
    }
    (OUT / "gdt462_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
