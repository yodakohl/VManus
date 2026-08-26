#!/usr/bin/env python3
"""Find calibrated functional edge stems inside GDT459 learned labels."""

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
BASE = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas"
OUT = BASE / "artifacts"
GDT407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
GDT413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
GDT459 = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts/gdt459_183_address_interlinear.tsv"

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


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    running = read_tsv(GDT407)
    labels = [row for row in read_tsv(GDT459) if row["decision_tier"] == "D_OWNER_LEARNED_WHOLE_LABEL"]
    values = {row["atom"]: row["working_value_de"] for row in read_tsv(GDT413)}

    running_recipe: dict[str, str] = {}
    running_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in running:
        prior = running_recipe.setdefault(row["surface"], row["component_recipe"])
        if prior != row["component_recipe"]:
            raise RuntimeError(f"Non-invariant running surface: {row['surface']}")
        running_events[row["surface"]].append(row)

    def literal(recipe: str) -> str:
        return " · ".join(values[atom] for atom in recipe.split("+"))

    edge_candidates: list[dict[str, object]] = []
    for edge in ("PREFIX", "SUFFIX"):
        for stem, recipe in running_recipe.items():
            if len(stem) < 2:
                continue
            atoms = recipe.split("+")
            if edge == "PREFIX":
                extensions = [(surface, candidate) for surface, candidate in running_recipe.items() if surface != stem and surface.startswith(stem)]
                matches = [(surface, candidate) for surface, candidate in extensions if candidate.split("+")[:len(atoms)] == atoms]
                label_hits = [row for row in labels if row["surface"].startswith(stem)]
            else:
                extensions = [(surface, candidate) for surface, candidate in running_recipe.items() if surface != stem and surface.endswith(stem)]
                matches = [(surface, candidate) for surface, candidate in extensions if candidate.split("+")[-len(atoms):] == atoms]
                label_hits = [row for row in labels if row["surface"].endswith(stem)]
            if len(extensions) < 4 or not label_hits:
                continue
            precision = len(matches) / len(extensions)
            if precision < 0.90:
                continue
            matched_surfaces = {surface for surface, _ in matches}
            matched_event_count = sum(len(running_events[surface]) for surface in matched_surfaces)
            edge_candidates.append({
                "edge": edge,
                "surface_stem": stem,
                "component_recipe": recipe,
                "literal_working_value_de": literal(recipe),
                "running_extension_type_count": len(extensions),
                "running_matching_type_count": len(matches),
                "running_type_precision": f"{precision:.6f}",
                "running_matching_event_count": matched_event_count,
                "running_matching_pages": "|".join(sorted({row["physical_page"] for surface in matched_surfaces for row in running_events[surface]})),
                "learned_label_hit_count": len(label_hits),
                "learned_label_pages": "|".join(sorted({row["physical_page"] for row in label_hits})),
                "learned_label_surfaces": "|".join(sorted(row["surface"] for row in label_hits)),
            })
    edge_candidates.sort(key=lambda row: (str(row["edge"]), -len(str(row["surface_stem"])), str(row["surface_stem"])))
    edge_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate(edge_candidates, start=1):
        edge_rows.append({
            "edge_stem_id": f"G460-E{ordinal:02d}",
            **row,
            "working_rule_de": "linken Funktionsrand lesen; Rest als Namenskern behalten" if row["edge"] == "PREFIX" else "rechten Funktionsrand lesen; Rest als Namenskern behalten",
            "claim_status": "CALIBRATED_FUNCTION_EDGE__NOT_INDIVIDUAL_NAME",
        })
    write_tsv(OUT / "gdt460_27_calibrated_edge_stems.tsv", edge_rows)

    occurrence_sets: dict[str, set[int]] = defaultdict(set)
    for index, row in enumerate(labels):
        surface = row["surface"]
        for length in range(2, 6):
            for start in range(len(surface) - length + 1):
                occurrence_sets[surface[start:start + length]].add(index)
    raw_family: list[tuple[str, str, set[int]]] = []
    for stem, indexes in occurrence_sets.items():
        if len(indexes) < 3:
            continue
        classes = {labels[index]["content_class"] for index in indexes}
        if len(classes) != 1:
            continue
        content_class = next(iter(classes))
        pages = {labels[index]["physical_page"] for index in indexes}
        replicated = (
            content_class == "STAR_BEARING_RING_POSITION" and {"f71v", "f72r"}.issubset(pages)
        ) or (
            content_class == "DRUG_OR_INGREDIENT_OBJECT" and {"f88v", "f89r"}.issubset(pages)
        )
        if replicated:
            raw_family.append((stem, content_class, indexes))
    family_candidates = [
        candidate for candidate in raw_family
        if not any(
            len(other_stem) > len(candidate[0])
            and other_class == candidate[1]
            and other_indexes == candidate[2]
            for other_stem, other_class, other_indexes in raw_family
        )
    ]
    family_candidates.sort(key=lambda item: (item[1], -len(item[2]), -len(item[0]), item[0]))
    family_rows: list[dict[str, object]] = []
    for ordinal, (stem, content_class, indexes) in enumerate(family_candidates, start=1):
        selected = [labels[index] for index in sorted(indexes)]
        family_rows.append({
            "family_stem_id": f"G460-F{ordinal:02d}",
            "surface_substring": stem,
            "substring_length": len(stem),
            "working_family_value_de": CLASS_DEFAULT[content_class][1],
            "content_class": content_class,
            "label_count": len(selected),
            "pages": "|".join(sorted({row["physical_page"] for row in selected})),
            "page_counts": "|".join(f"{page}:{sum(row['physical_page'] == page for row in selected)}" for page in sorted({row["physical_page"] for row in selected})),
            "surfaces": "|".join(row["surface"] for row in selected),
            "source_event_ids": "|".join(row["source_event_id"] for row in selected),
            "selection_rule": "3PLUS_LABELS__ONE_CONTENT_CLASS__BOTH_CLASS_PAGES__MAXIMAL_EQUAL_OCCURRENCE_SET",
            "claim_status": "REPLICATED_OWNER_CLASS_FAMILY_MARKER__NOT_OBJECT_NAME",
        })
    write_tsv(OUT / "gdt460_17_owner_class_family_stems.tsv", family_rows)

    prefix_rows = [row for row in edge_rows if row["edge"] == "PREFIX"]
    suffix_rows = [row for row in edge_rows if row["edge"] == "SUFFIX"]
    label_rows: list[dict[str, object]] = []
    for ordinal, source in enumerate(labels, start=1):
        surface = source["surface"]
        prefix_options = sorted(
            (row for row in prefix_rows if surface.startswith(str(row["surface_stem"]))),
            key=lambda row: (-len(str(row["surface_stem"])), str(row["surface_stem"])),
        )
        prefix = prefix_options[0] if prefix_options else None
        prefix_surface = str(prefix["surface_stem"]) if prefix else ""
        suffix_options = sorted(
            (
                row for row in suffix_rows
                if surface.endswith(str(row["surface_stem"]))
                and len(prefix_surface) + len(str(row["surface_stem"])) <= len(surface)
            ),
            key=lambda row: (-len(str(row["surface_stem"])), str(row["surface_stem"])),
        )
        suffix = suffix_options[0] if suffix_options else None
        suffix_surface = str(suffix["surface_stem"]) if suffix else ""
        center_end = len(surface) - len(suffix_surface) if suffix_surface else len(surface)
        learned_center = surface[len(prefix_surface):center_end]
        family_hits = [row for row in family_rows if str(row["surface_substring"]) in surface]
        known_chars = len(prefix_surface) + len(suffix_surface)
        if known_chars == len(surface) and known_chars > 0:
            hybrid_status = "FULL_EDGE_FORMULA"
        elif known_chars > 0:
            hybrid_status = "FUNCTION_EDGE_PLUS_LEARNED_CORE"
        elif family_hits:
            hybrid_status = "OWNER_FAMILY_STEM_ONLY"
        else:
            hybrid_status = "WHOLE_LEARNED_LABEL"
        default_name, _ = CLASS_DEFAULT[source["content_class"]]
        pieces: list[str] = []
        recipe_parts: list[str] = []
        if prefix:
            pieces.append(str(prefix["literal_working_value_de"]))
            recipe_parts.append(str(prefix["component_recipe"]))
        if learned_center:
            pieces.append(f"[{default_name}:{learned_center}]")
        if suffix:
            pieces.append(str(suffix["literal_working_value_de"]))
            recipe_parts.append(str(suffix["component_recipe"]))
        if not pieces:
            pieces.append(default_name)
        family_trace = "|".join(f"{row['surface_substring']}={row['working_family_value_de']}" for row in family_hits) or "NONE"
        label_rows.append({
            "gdt460_label_id": f"G460-L{ordinal:03d}",
            "source_event_id": source["source_event_id"],
            "physical_page": source["physical_page"],
            "register": source["register"],
            "locus": source["locus"],
            "owner_de": source["owner_de"],
            "surface": surface,
            "content_class": source["content_class"],
            "hybrid_status": hybrid_status,
            "prefix_stem": prefix_surface or "NONE",
            "prefix_recipe": str(prefix["component_recipe"]) if prefix else "NONE",
            "prefix_value_de": str(prefix["literal_working_value_de"]) if prefix else "NONE",
            "learned_center_surface": learned_center or "NONE",
            "learned_center_default_de": default_name if learned_center else "NONE",
            "suffix_stem": suffix_surface or "NONE",
            "suffix_recipe": str(suffix["component_recipe"]) if suffix else "NONE",
            "suffix_value_de": str(suffix["literal_working_value_de"]) if suffix else "NONE",
            "known_edge_character_count": known_chars,
            "surface_character_count": len(surface),
            "known_edge_fraction": f"{known_chars / len(surface):.6f}",
            "edge_recipe_trace": "+".join(recipe_parts) if recipe_parts else "NONE",
            "owner_family_stem_trace": family_trace,
            "hybrid_short_default_de": " · ".join(pieces),
            "strongest_rival": "RENDERER_EDGE_WITHOUT_SEMANTIC_CONTRIBUTION" if known_chars else "UNANALYZED_WHOLE_NOMENCLATOR_ENTRY",
            "image_object_id": source["image_object_id"],
            "review_image_sha256": source["review_image_sha256"],
        })
    write_tsv(OUT / "gdt460_107_hybrid_label_dictionary.tsv", label_rows)

    page_rows: list[dict[str, object]] = []
    for page in sorted({row["physical_page"] for row in label_rows}):
        selected = [row for row in label_rows if row["physical_page"] == page]
        statuses = Counter(str(row["hybrid_status"]) for row in selected)
        page_rows.append({
            "physical_page": page,
            "register": selected[0]["register"],
            "content_class": selected[0]["content_class"],
            "label_count": len(selected),
            "full_edge_formula_count": statuses["FULL_EDGE_FORMULA"],
            "functional_edge_plus_core_count": statuses["FUNCTION_EDGE_PLUS_LEARNED_CORE"],
            "owner_family_only_count": statuses["OWNER_FAMILY_STEM_ONLY"],
            "whole_learned_label_count": statuses["WHOLE_LEARNED_LABEL"],
            "labels_with_any_known_edge": sum(int(row["known_edge_character_count"]) > 0 for row in selected),
            "labels_with_owner_family_stem": sum(row["owner_family_stem_trace"] != "NONE" for row in selected),
            "known_edge_character_count": sum(int(row["known_edge_character_count"]) for row in selected),
            "surface_character_count": sum(int(row["surface_character_count"]) for row in selected),
        })
    write_tsv(OUT / "gdt460_6_page_summary.tsv", page_rows)

    status_counts = Counter(str(row["hybrid_status"]) for row in label_rows)
    labels_with_edge = sum(int(row["known_edge_character_count"]) > 0 for row in label_rows)
    labels_with_family = sum(row["owner_family_stem_trace"] != "NONE" for row in label_rows)
    union_structured = sum(int(row["known_edge_character_count"]) > 0 or row["owner_family_stem_trace"] != "NONE" for row in label_rows)
    known_characters = sum(int(row["known_edge_character_count"]) for row in label_rows)
    total_characters = sum(int(row["surface_character_count"]) for row in label_rows)
    result = {
        "status": "HYBRID_FUNCTION_EDGES_AND_LEARNED_NAME_CORES",
        "source_learned_label_count": len(labels),
        "source_unique_surface_count": len({row["surface"] for row in labels}),
        "calibrated_edge_channel_count": len(edge_rows),
        "calibrated_prefix_stem_count": sum(row["edge"] == "PREFIX" for row in edge_rows),
        "calibrated_suffix_stem_count": sum(row["edge"] == "SUFFIX" for row in edge_rows),
        "hybrid_status_counts": dict(sorted(status_counts.items())),
        "labels_with_known_edge_count": labels_with_edge,
        "replicated_owner_family_stem_count": len(family_rows),
        "labels_with_owner_family_stem_count": labels_with_family,
        "labels_with_any_structure_count": union_structured,
        "fully_unstructured_whole_label_count": len(labels) - union_structured,
        "known_edge_character_count": known_characters,
        "surface_character_count": total_characters,
        "known_edge_character_fraction": f"{known_characters / total_characters:.6f}",
        "core_meaning_revisions": 0,
        "new_pages": 0,
        "surface_predictions": 0,
        "confirmed_lexemes": 0,
    }
    (OUT / "gdt460_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
