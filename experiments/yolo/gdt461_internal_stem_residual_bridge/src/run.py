#!/usr/bin/env python3
"""Calibrate internal functional stems and bridge the GDT460 residual labels."""

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
BASE = ROOT / "experiments/yolo/gdt461_internal_stem_residual_bridge"
OUT = BASE / "artifacts"
GDT407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
GDT413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
GDT459 = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts/gdt459_183_address_interlinear.tsv"
GDT460_LABELS = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas/artifacts/gdt460_107_hybrid_label_dictionary.tsv"
GDT460_FAMILIES = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas/artifacts/gdt460_17_owner_class_family_stems.tsv"

CLASS_DEFAULT = {
    "PICTURED_PLANT": ("PFLANZENNAME", "PFLANZENFAMILIE"),
    "STAR_BEARING_RING_POSITION": ("STERNSTELLENNAME", "STERNSTELLENFAMILIE"),
    "BATH_OR_OUTLET_STATION": ("BADSTATIONSNAME", "BADSTATIONSFAMILIE"),
    "DRUG_OR_INGREDIENT_OBJECT": ("DROGENNAME", "DROGENFAMILIE"),
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


def contains_atoms(needle: list[str], haystack: list[str]) -> bool:
    return any(haystack[index:index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1))


def strict_internal_positions(surface: str, stem: str) -> list[int]:
    return [
        index for index in range(1, len(surface) - len(stem))
        if surface.startswith(stem, index)
    ]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    running = read_tsv(GDT407)
    addresses = read_tsv(GDT459)
    labels = read_tsv(GDT460_LABELS)
    old_families = read_tsv(GDT460_FAMILIES)
    values = {row["atom"]: row["working_value_de"] for row in read_tsv(GDT413)}

    running_recipe: dict[str, str] = {}
    running_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in running:
        previous = running_recipe.setdefault(row["surface"], row["component_recipe"])
        if previous != row["component_recipe"]:
            raise RuntimeError(f"Non-invariant running surface: {row['surface']}")
        running_events[row["surface"]].append(row)

    def literal(recipe: str) -> str:
        return " · ".join(values[atom] for atom in recipe.split("+"))

    internal_candidates: list[dict[str, object]] = []
    for stem, recipe in running_recipe.items():
        if len(stem) < 2:
            continue
        extension_types = [
            (surface, candidate_recipe)
            for surface, candidate_recipe in running_recipe.items()
            if surface != stem and strict_internal_positions(surface, stem)
        ]
        if len(extension_types) < 4:
            continue
        atoms = recipe.split("+")
        matching_types = [
            (surface, candidate_recipe)
            for surface, candidate_recipe in extension_types
            if contains_atoms(atoms, candidate_recipe.split("+"))
        ]
        precision = len(matching_types) / len(extension_types)
        if precision < 0.90:
            continue
        label_hits: list[dict[str, str]] = []
        for label in labels:
            surface = label["surface"]
            prefix_length = 0 if label["prefix_stem"] == "NONE" else len(label["prefix_stem"])
            suffix_length = 0 if label["suffix_stem"] == "NONE" else len(label["suffix_stem"])
            center_end = len(surface) - suffix_length if suffix_length else len(surface)
            if any(
                position >= prefix_length and position + len(stem) <= center_end
                for position in strict_internal_positions(surface, stem)
            ):
                label_hits.append(label)
        if not label_hits:
            continue
        matching_surfaces = {surface for surface, _ in matching_types}
        internal_candidates.append({
            "surface_stem": stem,
            "component_recipe": recipe,
            "literal_working_value_de": literal(recipe),
            "running_internal_extension_type_count": len(extension_types),
            "running_matching_type_count": len(matching_types),
            "running_type_precision": f"{precision:.6f}",
            "running_matching_event_count": sum(len(running_events[surface]) for surface in matching_surfaces),
            "running_matching_pages": "|".join(sorted({row["physical_page"] for surface in matching_surfaces for row in running_events[surface]})),
            "target_label_count": len(label_hits),
            "target_pages": "|".join(sorted({row["physical_page"] for row in label_hits})),
            "target_surfaces": "|".join(sorted(row["surface"] for row in label_hits)),
        })
    internal_candidates.sort(key=lambda row: (-len(str(row["surface_stem"])), str(row["surface_stem"])))
    internal_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate(internal_candidates, start=1):
        internal_rows.append({
            "internal_stem_id": f"G461-I{ordinal:02d}",
            **row,
            "working_rule_de": "nur strikt binnen und innerhalb des noch gelernten Namenskerns lesen",
            "claim_status": "CALIBRATED_INTERNAL_FUNCTION__NOT_OBJECT_NAME",
        })
    write_tsv(OUT / "gdt461_9_calibrated_internal_stems.tsv", internal_rows)

    assignments_by_event: dict[str, list[dict[str, object]]] = defaultdict(list)
    occurrence_rows: list[dict[str, object]] = []
    occurrence_ordinal = 0
    for label in labels:
        surface = label["surface"]
        prefix_length = 0 if label["prefix_stem"] == "NONE" else len(label["prefix_stem"])
        suffix_length = 0 if label["suffix_stem"] == "NONE" else len(label["suffix_stem"])
        center_end = len(surface) - suffix_length if suffix_length else len(surface)
        candidates: list[dict[str, object]] = []
        for stem_row in internal_rows:
            stem = str(stem_row["surface_stem"])
            for position in strict_internal_positions(surface, stem):
                if position >= prefix_length and position + len(stem) <= center_end:
                    candidates.append({
                        "start": position,
                        "end": position + len(stem),
                        "stem": stem,
                        "recipe": stem_row["component_recipe"],
                        "value": stem_row["literal_working_value_de"],
                        "internal_stem_id": stem_row["internal_stem_id"],
                    })
        selected: list[dict[str, object]] = []
        for candidate in sorted(candidates, key=lambda item: (-len(str(item["stem"])), int(item["start"]), str(item["stem"]))):
            if not any(not (int(candidate["end"]) <= int(old["start"]) or int(candidate["start"]) >= int(old["end"])) for old in selected):
                selected.append(candidate)
        selected.sort(key=lambda item: (int(item["start"]), int(item["end"]), str(item["stem"])))
        assignments_by_event[label["source_event_id"]] = selected
        for candidate in selected:
            occurrence_ordinal += 1
            occurrence_rows.append({
                "internal_occurrence_id": f"G461-O{occurrence_ordinal:03d}",
                "source_event_id": label["source_event_id"],
                "physical_page": label["physical_page"],
                "surface": surface,
                "prior_hybrid_status": label["hybrid_status"],
                "internal_stem_id": candidate["internal_stem_id"],
                "internal_stem": candidate["stem"],
                "component_recipe": candidate["recipe"],
                "literal_working_value_de": candidate["value"],
                "character_start_zero_based": candidate["start"],
                "character_end_exclusive": candidate["end"],
                "left_surface": surface[:int(candidate["start"])] or "NONE",
                "right_surface": surface[int(candidate["end"]):] or "NONE",
                "selection_rule": "LONGEST_THEN_LEFTMOST_NONOVERLAPPING_INTERNAL_CHANNEL",
            })
    write_tsv(OUT / "gdt461_53_internal_occurrences.tsv", occurrence_rows)

    unique_addresses: dict[tuple[str, str], dict[str, str]] = {}
    for row in addresses:
        unique_addresses.setdefault((row["surface"], row["content_class"]), row)
    address_items = list(unique_addresses.values())
    substring_occurrences: dict[str, set[int]] = defaultdict(set)
    for index, row in enumerate(address_items):
        surface = row["surface"]
        for length in range(2, 6):
            for start in range(len(surface) - length + 1):
                substring_occurrences[surface[start:start + length]].add(index)
    raw_families: list[tuple[str, str, set[int]]] = []
    for stem, indexes in substring_occurrences.items():
        if len(indexes) < 3:
            continue
        classes = {address_items[index]["content_class"] for index in indexes}
        if len(classes) != 1:
            continue
        content_class = next(iter(classes))
        pages = {address_items[index]["physical_page"] for index in indexes}
        replicated = (
            content_class == "STAR_BEARING_RING_POSITION" and {"f71v", "f72r"}.issubset(pages)
        ) or (
            content_class == "DRUG_OR_INGREDIENT_OBJECT" and {"f88v", "f89r"}.issubset(pages)
        )
        if replicated:
            raw_families.append((stem, content_class, indexes))
    maximal_families = [
        candidate for candidate in raw_families
        if not any(
            len(other_stem) > len(candidate[0])
            and other_class == candidate[1]
            and other_indexes == candidate[2]
            for other_stem, other_class, other_indexes in raw_families
        )
    ]
    old_family_stems = {row["surface_substring"] for row in old_families}
    old_whole_surfaces = {
        row["surface"] for row in labels if row["hybrid_status"] == "WHOLE_LEARNED_LABEL"
    }
    new_residual_families = [
        candidate for candidate in maximal_families
        if candidate[0] not in old_family_stems
        and any(candidate[0] in surface for surface in old_whole_surfaces)
    ]
    new_residual_families.sort(key=lambda item: (item[1], -len(item[2]), -len(item[0]), item[0]))
    bridge_rows: list[dict[str, object]] = []
    for ordinal, (stem, content_class, indexes) in enumerate(new_residual_families, start=1):
        selected = [address_items[index] for index in sorted(indexes)]
        target_labels = [row for row in labels if stem in row["surface"]]
        bridge_rows.append({
            "residual_family_bridge_id": f"G461-F{ordinal:02d}",
            "surface_substring": stem,
            "working_family_value_de": CLASS_DEFAULT[content_class][1],
            "content_class": content_class,
            "unique_address_surface_count": len(selected),
            "pages": "|".join(sorted({row["physical_page"] for row in selected})),
            "address_surfaces": "|".join(sorted(row["surface"] for row in selected)),
            "gdt460_target_surfaces": "|".join(sorted(row["surface"] for row in target_labels)),
            "old_whole_target_surfaces": "|".join(sorted(row["surface"] for row in target_labels if row["hybrid_status"] == "WHOLE_LEARNED_LABEL")),
            "selection_rule": "COMPLETE_ADDRESS_DECK__3PLUS_UNIQUE_SURFACES__PURE_CLASS__BOTH_CLASS_PAGES__TOUCHES_OLD_WHOLE",
            "claim_status": "RESIDUAL_OWNER_FAMILY_BRIDGE__NOT_OBJECT_NAME",
        })
    write_tsv(OUT / "gdt461_residual_owner_family_bridge.tsv", bridge_rows)

    revised_rows: list[dict[str, object]] = []
    for ordinal, label in enumerate(labels, start=1):
        surface = label["surface"]
        selected = assignments_by_event[label["source_event_id"]]
        prefix_surface = "" if label["prefix_stem"] == "NONE" else label["prefix_stem"]
        suffix_surface = "" if label["suffix_stem"] == "NONE" else label["suffix_stem"]
        prefix_length = len(prefix_surface)
        suffix_length = len(suffix_surface)
        center_end = len(surface) - suffix_length if suffix_length else len(surface)
        new_family_hits = [row for row in bridge_rows if row["surface_substring"] in surface]
        family_parts = [] if label["owner_family_stem_trace"] == "NONE" else label["owner_family_stem_trace"].split("|")
        family_parts.extend(f"{row['surface_substring']}={row['working_family_value_de']}" for row in new_family_hits)
        family_trace = "|".join(dict.fromkeys(family_parts)) if family_parts else "NONE"
        default_name, _ = CLASS_DEFAULT[label["content_class"]]
        pieces: list[str] = []
        recipe_trace: list[str] = []
        if prefix_surface:
            pieces.append(label["prefix_value_de"])
            recipe_trace.append(label["prefix_recipe"])
        cursor = prefix_length
        for assignment in selected:
            start = int(assignment["start"])
            end = int(assignment["end"])
            if cursor < start:
                pieces.append(f"[{default_name}:{surface[cursor:start]}]")
            pieces.append(str(assignment["value"]))
            recipe_trace.append(str(assignment["recipe"]))
            cursor = end
        if cursor < center_end:
            pieces.append(f"[{default_name}:{surface[cursor:center_end]}]")
        if suffix_surface:
            pieces.append(label["suffix_value_de"])
            recipe_trace.append(label["suffix_recipe"])
        known_count = int(label["known_edge_character_count"]) + sum(int(item["end"]) - int(item["start"]) for item in selected)
        has_function = known_count > 0
        has_family = family_trace != "NONE"
        if known_count == len(surface):
            revised_status = "FULL_FUNCTION_FORMULA"
        elif has_function:
            revised_status = "FUNCTION_SHELL_PLUS_LEARNED_CORE"
        elif has_family:
            revised_status = "OWNER_FAMILY_STEM_ONLY"
            pieces = [family_trace.replace("=", ":"), f"[{default_name}:{surface}]"]
        else:
            revised_status = "WHOLE_LEARNED_LABEL"
            pieces = [f"[{default_name}:{surface}]"]
        revised_rows.append({
            "gdt461_label_id": f"G461-L{ordinal:03d}",
            "source_event_id": label["source_event_id"],
            "physical_page": label["physical_page"],
            "register": label["register"],
            "locus": label["locus"],
            "owner_de": label["owner_de"],
            "surface": surface,
            "content_class": label["content_class"],
            "prior_hybrid_status": label["hybrid_status"],
            "revised_hybrid_status": revised_status,
            "prefix_stem": label["prefix_stem"],
            "prefix_recipe": label["prefix_recipe"],
            "internal_occurrence_count": len(selected),
            "internal_stem_trace": "|".join(f"{item['start']}:{item['stem']}={item['recipe']}" for item in selected) or "NONE",
            "suffix_stem": label["suffix_stem"],
            "suffix_recipe": label["suffix_recipe"],
            "owner_family_stem_trace": family_trace,
            "known_function_character_count": known_count,
            "remaining_learned_character_count": len(surface) - known_count,
            "surface_character_count": len(surface),
            "known_function_fraction": f"{known_count / len(surface):.6f}",
            "ordered_function_recipe_trace": "+".join(recipe_trace) if recipe_trace else "NONE",
            "revised_short_default_de": " · ".join(pieces),
            "strongest_rival": "INTERNAL_RENDERER_COINCIDENCE" if selected else label["strongest_rival"],
            "image_object_id": label["image_object_id"],
            "review_image_sha256": label["review_image_sha256"],
        })
    write_tsv(OUT / "gdt461_107_revised_hybrid_dictionary.tsv", revised_rows)

    residual_rows: list[dict[str, object]] = []
    residual_sources = [row for row in revised_rows if row["prior_hybrid_status"] == "WHOLE_LEARNED_LABEL"]
    for row in residual_sources:
        residual_rows.append({
            "source_event_id": row["source_event_id"],
            "physical_page": row["physical_page"],
            "surface": row["surface"],
            "content_class": row["content_class"],
            "internal_stem_trace": row["internal_stem_trace"],
            "new_owner_family_bridge": "cheo=DROGENFAMILIE" if "cheo=DROGENFAMILIE" in str(row["owner_family_stem_trace"]) else "NONE",
            "revised_hybrid_status": row["revised_hybrid_status"],
            "revised_short_default_de": row["revised_short_default_de"],
        })
    write_tsv(OUT / "gdt461_19_residual_audit.tsv", residual_rows)

    page_rows: list[dict[str, object]] = []
    for page in sorted({row["physical_page"] for row in revised_rows}):
        selected = [row for row in revised_rows if row["physical_page"] == page]
        statuses = Counter(str(row["revised_hybrid_status"]) for row in selected)
        page_rows.append({
            "physical_page": page,
            "register": selected[0]["register"],
            "content_class": selected[0]["content_class"],
            "label_count": len(selected),
            "full_function_formula_count": statuses["FULL_FUNCTION_FORMULA"],
            "function_shell_plus_core_count": statuses["FUNCTION_SHELL_PLUS_LEARNED_CORE"],
            "owner_family_only_count": statuses["OWNER_FAMILY_STEM_ONLY"],
            "whole_learned_label_count": statuses["WHOLE_LEARNED_LABEL"],
            "labels_with_internal_stem": sum(int(row["internal_occurrence_count"]) > 0 for row in selected),
            "internal_occurrence_count": sum(int(row["internal_occurrence_count"]) for row in selected),
            "known_function_character_count": sum(int(row["known_function_character_count"]) for row in selected),
            "surface_character_count": sum(int(row["surface_character_count"]) for row in selected),
        })
    write_tsv(OUT / "gdt461_6_page_summary.tsv", page_rows)

    status_counts = Counter(str(row["revised_hybrid_status"]) for row in revised_rows)
    known_characters = sum(int(row["known_function_character_count"]) for row in revised_rows)
    total_characters = sum(int(row["surface_character_count"]) for row in revised_rows)
    result = {
        "status": "INTERNAL_FUNCTION_STEMS_REDUCE_WHOLE_LABEL_TAIL_TO_THIRTEEN",
        "source_label_count": len(labels),
        "calibrated_internal_stem_count": len(internal_rows),
        "labels_with_internal_stem_count": sum(int(row["internal_occurrence_count"]) > 0 for row in revised_rows),
        "internal_occurrence_count": len(occurrence_rows),
        "internal_assigned_character_count": sum(len(row["internal_stem"]) for row in occurrence_rows),
        "new_residual_owner_family_bridge_count": len(bridge_rows),
        "revised_hybrid_status_counts": dict(sorted(status_counts.items())),
        "labels_with_any_function_count": sum(int(row["known_function_character_count"]) > 0 for row in revised_rows),
        "labels_with_any_structure_count": sum(int(row["known_function_character_count"]) > 0 or row["owner_family_stem_trace"] != "NONE" for row in revised_rows),
        "known_function_character_count": known_characters,
        "surface_character_count": total_characters,
        "known_function_character_fraction": f"{known_characters / total_characters:.6f}",
        "old_whole_residual_count": len(residual_sources),
        "old_whole_residuals_with_internal_function": sum(row["internal_stem_trace"] != "NONE" for row in residual_sources),
        "old_whole_residuals_with_new_family_bridge": sum(row["new_owner_family_bridge"] != "NONE" for row in residual_rows),
        "remaining_whole_label_count": status_counts["WHOLE_LEARNED_LABEL"],
        "core_meaning_revisions": 0,
        "new_pages": 0,
        "surface_predictions": 0,
        "confirmed_lexemes": 0,
    }
    (OUT / "gdt461_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
