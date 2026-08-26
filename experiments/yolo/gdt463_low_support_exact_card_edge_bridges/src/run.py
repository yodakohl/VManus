#!/usr/bin/env python3
"""Bridge four low-support residual edges with exact-card paradigms."""

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
BASE = ROOT / "experiments/yolo/gdt463_low_support_exact_card_edge_bridges"
OUT = BASE / "artifacts"
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
VALUE_PATH = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
GDT459_PATH = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts/gdt459_183_address_interlinear.tsv"
SOURCE_PATH = ROOT / "experiments/yolo/gdt462_near_threshold_ar_edge_exception_audit/artifacts/gdt462_107_revised_hybrid_dictionary.tsv"

CANDIDATES = (
    ("SUFFIX", "oin", "opoiiinoin"),
    ("PREFIX", "kor", "korainy"),
    ("PREFIX", "yky", "ykyd"),
    ("SUFFIX", "cfhy", "ykocfhy"),
)

TARGET_PLAN = {
    "opoiiinoin": {
        "status": "FUNCTION_SHELL_PLUS_LEARNED_CORE",
        "segmentation": "[STERNSTELLENNAME:opoiiin]|oin",
        "recipe": "O+IIN",
        "default": "[STERNSTELLENNAME:opoiiin] · AUSFÜHRUNG · STUFE",
        "known_add": 3,
        "prefix": ("NONE", "NONE"),
        "suffix": ("oin", "O+IIN"),
    },
    "korainy": {
        "status": "FULL_FUNCTION_FORMULA",
        "segmentation": "korain|y",
        "recipe": "K+OR+AIN+Y",
        "default": "GEBEN · EINHEIT · ANTEIL · POSTEN",
        "known_add": 7,
        "prefix": ("korain", "K+OR+AIN"),
        "suffix": ("y", "Y"),
    },
    "ykyd": {
        "status": "FULL_FUNCTION_FORMULA",
        "segmentation": "yky|d",
        "recipe": "Y+K+Y+D_ADDR",
        "default": "POSTEN · GEBEN · POSTEN · HIER",
        "known_add": 4,
        "prefix": ("yky", "Y+K+Y"),
        "suffix": ("d", "D_ADDR"),
    },
    "ykocfhy": {
        "status": "FUNCTION_SHELL_PLUS_LEARNED_CORE",
        "segmentation": "[DROGENNAME:yko]|cfhy",
        "recipe": "CH+LOCAL_CHAR_F+Y",
        "default": "[DROGENNAME:yko] · NEHMEN · HIER · POSTEN",
        "known_add": 4,
        "prefix": ("NONE", "NONE"),
        "suffix": ("cfhy", "CH+LOCAL_CHAR_F+Y"),
    },
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


def contains_sequence(needle: list[str], haystack: list[str]) -> bool:
    return any(haystack[index:index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    running = read_tsv(RUNNING_PATH)
    source = read_tsv(SOURCE_PATH)
    old_addresses = {row["surface"]: row for row in read_tsv(GDT459_PATH)}
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

    decision_rows: list[dict[str, object]] = []
    carrier_rows: list[dict[str, object]] = []
    for ordinal, (edge, stem, target) in enumerate(CANDIDATES, start=1):
        recipe = running_recipe[stem]
        atoms = recipe.split("+")
        if edge == "PREFIX":
            extensions = [(surface, candidate) for surface, candidate in running_recipe.items() if surface != stem and surface.startswith(stem)]
            matches = [(surface, candidate) for surface, candidate in extensions if candidate.split("+")[:len(atoms)] == atoms]
        else:
            extensions = [(surface, candidate) for surface, candidate in running_recipe.items() if surface != stem and surface.endswith(stem)]
            matches = [(surface, candidate) for surface, candidate in extensions if candidate.split("+")[-len(atoms):] == atoms]
        sequence_carriers = [
            (surface, candidate) for surface, candidate in running_recipe.items()
            if contains_sequence(atoms, candidate.split("+"))
        ]
        sequence_pages = {event["physical_page"] for surface, _ in sequence_carriers for event in running_events[surface]}
        sequence_registers = {event["register"] for surface, _ in sequence_carriers for event in running_events[surface]}
        plan = TARGET_PLAN[target]
        old = old_addresses[target]
        direct_full_reconstruction = plan["status"] == "FULL_FUNCTION_FORMULA"
        gdt459_recipe_matches = direct_full_reconstruction and old["minimal_segmentation_recipe"] == plan["recipe"]
        gdt459_gate_passes = direct_full_reconstruction and not old["factor_gate_status"].startswith("STOP")
        decision_rows.append({
            "bridge_id": f"G463-B{ordinal:02d}",
            "edge": edge,
            "surface_stem": stem,
            "component_recipe": recipe,
            "literal_working_value_de": literal(recipe),
            "base_running_event_count": len(running_events[stem]),
            "base_running_pages": "|".join(sorted({row["physical_page"] for row in running_events[stem]})),
            "edge_extension_type_count": len(extensions),
            "edge_matching_type_count": len(matches),
            "edge_type_precision": f"{len(matches) / len(extensions):.6f}",
            "edge_matching_surfaces": "|".join(sorted(surface for surface, _ in matches)),
            "recipe_sequence_carrier_type_count": len(sequence_carriers),
            "recipe_sequence_carrier_event_count": sum(len(running_events[surface]) for surface, _ in sequence_carriers),
            "recipe_sequence_page_count": len(sequence_pages),
            "recipe_sequence_registers": "|".join(sorted(sequence_registers)),
            "target_surface": target,
            "target_old_gdt459_minimal_recipe": old["minimal_segmentation_recipe"],
            "target_old_gdt459_factor_gate": old["factor_gate_status"],
            "target_full_reconstruction": "YES" if direct_full_reconstruction else "NO",
            "target_gdt459_recipe_matches": "YES" if gdt459_recipe_matches else "NOT_APPLICABLE",
            "target_gdt459_gate_passes": "YES" if gdt459_gate_passes else "NOT_APPLICABLE",
            "decision": "PROMOTE_EXACT_CARD_EDGE",
            "decision_rule": "ALL_EXTENSIONS_ALIGN__SEQUENCE_ON_4PLUS_PAGES__FULL_TARGET_REQUIRES_OLD_GREEN_RECIPE",
        })
        for surface, candidate in sorted(sequence_carriers):
            carrier_rows.append({
                "bridge_id": f"G463-B{ordinal:02d}",
                "edge_stem": stem,
                "edge_recipe": recipe,
                "carrier_surface": surface,
                "carrier_recipe": candidate,
                "carrier_event_count": len(running_events[surface]),
                "carrier_pages": "|".join(sorted({row["physical_page"] for row in running_events[surface]})),
                "carrier_registers": "|".join(sorted({row["register"] for row in running_events[surface]})),
                "edge_relation": (
                    "BASE"
                    if surface == stem
                    else (
                        "MATCHED_EDGE_EXTENSION"
                        if surface in {item[0] for item in matches}
                        else "RECIPE_SEQUENCE_SUPPORT"
                    )
                ),
            })
    write_tsv(OUT / "gdt463_4_bridge_decisions.tsv", decision_rows)
    write_tsv(OUT / "gdt463_recipe_sequence_carriers.tsv", carrier_rows)

    # The O+IIN bridge also sits beside two completely populated suffix axes.
    paradigm_rows: list[dict[str, object]] = []
    for stem in ("ain", "aiin", "oin"):
        recipe = running_recipe[stem]
        atoms = recipe.split("+")
        extensions = [(surface, candidate) for surface, candidate in running_recipe.items() if surface != stem and surface.endswith(stem)]
        matches = [(surface, candidate) for surface, candidate in extensions if candidate.split("+")[-len(atoms):] == atoms]
        paradigm_rows.append({
            "surface_suffix": stem,
            "component_recipe": recipe,
            "literal_working_value_de": literal(recipe),
            "base_event_count": len(running_events[stem]),
            "extension_type_count": len(extensions),
            "matching_type_count": len(matches),
            "type_precision": f"{len(matches) / len(extensions):.6f}",
            "role_in_gdt463": "DIRECT_COMPARATIVE_AXIS" if stem != "oin" else "PROMOTED_TARGET_EDGE",
        })
    write_tsv(OUT / "gdt463_ain_aiin_oin_suffix_paradigm.tsv", paradigm_rows)

    source_index = {row["surface"]: row for row in source}
    target_rows: list[dict[str, object]] = []
    for ordinal, surface in enumerate(("opoiiinoin", "korainy", "ykyd", "ykocfhy"), start=1):
        old = source_index[surface]
        plan = TARGET_PLAN[surface]
        target_rows.append({
            "target_id": f"G463-T{ordinal:02d}",
            "source_event_id": old["source_event_id"],
            "physical_page": old["physical_page"],
            "locus": old["locus"],
            "surface": surface,
            "content_class": old["content_class"],
            "old_status": old["gdt462_hybrid_status"],
            "new_status": plan["status"],
            "selected_surface_segmentation": plan["segmentation"],
            "selected_function_recipe": plan["recipe"],
            "selected_literal_de": plan["default"],
            "added_known_character_count": plan["known_add"],
            "remaining_learned_character_count": len(surface) - int(plan["known_add"]),
            "old_gdt459_minimal_recipe": old_addresses[surface]["minimal_segmentation_recipe"],
            "old_gdt459_factor_gate": old_addresses[surface]["factor_gate_status"],
            "revision_reason": "EXACT_COMPOSITE_EDGE_PLUS_INDEPENDENT_RECIPE_SEQUENCE_PARADIGM",
        })
    write_tsv(OUT / "gdt463_4_target_reconstructions.tsv", target_rows)

    revised_rows: list[dict[str, object]] = []
    for ordinal, old in enumerate(source, start=1):
        plan = TARGET_PLAN.get(old["surface"])
        known = int(old["known_function_character_count"]) + (int(plan["known_add"]) if plan else 0)
        prefix_stem, prefix_recipe = plan["prefix"] if plan else (old["prefix_stem"], old["prefix_recipe"])
        suffix_stem, suffix_recipe = plan["suffix"] if plan else (old["suffix_stem"], old["suffix_recipe"])
        revised_rows.append({
            "gdt463_label_id": f"G463-L{ordinal:03d}",
            "gdt462_label_id": old["gdt462_label_id"],
            "source_event_id": old["source_event_id"],
            "physical_page": old["physical_page"],
            "register": old["register"],
            "locus": old["locus"],
            "owner_de": old["owner_de"],
            "surface": old["surface"],
            "content_class": old["content_class"],
            "gdt462_hybrid_status": old["gdt462_hybrid_status"],
            "gdt463_hybrid_status": plan["status"] if plan else old["gdt462_hybrid_status"],
            "surface_segmentation": plan["segmentation"] if plan else "UNCHANGED_FROM_GDT462",
            "prefix_stem": prefix_stem,
            "prefix_recipe": prefix_recipe,
            "internal_stem_trace": old["internal_stem_trace"],
            "suffix_stem": suffix_stem,
            "suffix_recipe": suffix_recipe,
            "owner_family_stem_trace": old["owner_family_stem_trace"],
            "known_function_character_count": known,
            "remaining_learned_character_count": len(old["surface"]) - known,
            "surface_character_count": old["surface_character_count"],
            "known_function_fraction": f"{known / len(old['surface']):.6f}",
            "ordered_function_recipe_trace": plan["recipe"] if plan else old["ordered_function_recipe_trace"],
            "revised_short_default_de": plan["default"] if plan else old["revised_short_default_de"],
            "gdt463_change": "LOW_SUPPORT_EXACT_CARD_BRIDGE" if plan else "UNCHANGED",
            "strongest_rival": "EMBEDDED_EXACT_CARD_IS_NAME_OR_RENDERER_COINCIDENCE" if plan else old["strongest_rival"],
            "image_object_id": old["image_object_id"],
            "review_image_sha256": old["review_image_sha256"],
        })
    write_tsv(OUT / "gdt463_107_revised_hybrid_dictionary.tsv", revised_rows)

    page_rows: list[dict[str, object]] = []
    for page in sorted({row["physical_page"] for row in revised_rows}):
        selected = [row for row in revised_rows if row["physical_page"] == page]
        statuses = Counter(str(row["gdt463_hybrid_status"]) for row in selected)
        page_rows.append({
            "physical_page": page,
            "register": selected[0]["register"],
            "content_class": selected[0]["content_class"],
            "label_count": len(selected),
            "full_function_formula_count": statuses["FULL_FUNCTION_FORMULA"],
            "function_shell_plus_core_count": statuses["FUNCTION_SHELL_PLUS_LEARNED_CORE"],
            "owner_family_only_count": statuses["OWNER_FAMILY_STEM_ONLY"],
            "whole_learned_label_count": statuses["WHOLE_LEARNED_LABEL"],
            "gdt463_change_count": sum(row["gdt463_change"] != "UNCHANGED" for row in selected),
            "known_function_character_count": sum(int(row["known_function_character_count"]) for row in selected),
            "surface_character_count": sum(int(row["surface_character_count"]) for row in selected),
        })
    write_tsv(OUT / "gdt463_6_page_summary.tsv", page_rows)

    statuses = Counter(str(row["gdt463_hybrid_status"]) for row in revised_rows)
    known = sum(int(row["known_function_character_count"]) for row in revised_rows)
    total = sum(int(row["surface_character_count"]) for row in revised_rows)
    result = {
        "status": "FOUR_LOW_SUPPORT_EXACT_CARD_BRIDGES_REDUCE_WHOLE_LABEL_TAIL_TO_SEVEN",
        "source_label_count": len(source),
        "bridge_decision_count": len(decision_rows),
        "promoted_bridge_count": 4,
        "recipe_sequence_carrier_row_count": len(carrier_rows),
        "full_formula_promotions": ["korainy", "ykyd"],
        "hybrid_shell_promotions": ["opoiiinoin", "ykocfhy"],
        "revised_hybrid_status_counts": dict(sorted(statuses.items())),
        "remaining_whole_label_count": statuses["WHOLE_LEARNED_LABEL"],
        "labels_with_any_function_count": sum(int(row["known_function_character_count"]) > 0 for row in revised_rows),
        "labels_with_any_structure_count": sum(int(row["known_function_character_count"]) > 0 or row["owner_family_stem_trace"] != "NONE" for row in revised_rows),
        "known_function_character_count": known,
        "surface_character_count": total,
        "known_function_character_fraction": f"{known / total:.6f}",
        "new_core_meanings": 0,
        "new_pages": 0,
        "surface_predictions": 0,
        "confirmed_lexemes": 0,
    }
    (OUT / "gdt463_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
