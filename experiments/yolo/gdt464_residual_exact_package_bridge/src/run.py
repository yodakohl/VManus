#!/usr/bin/env python3
"""Close six of seven GDT463 residual labels with bounded existing packages."""

from __future__ import annotations

import csv
import importlib.util
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
BASE = ROOT / "experiments/yolo/gdt464_residual_exact_package_bridge"
OUT = BASE / "artifacts"
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
VALUE_PATH = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
ADDRESS_PATH = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts/gdt459_183_address_interlinear.tsv"
SOURCE_PATH = ROOT / "experiments/yolo/gdt463_low_support_exact_card_edge_bridges/artifacts/gdt463_107_revised_hybrid_dictionary.tsv"
READER_PATH = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/src/factor_gate_stream_read.py"

RESIDUALS = ("oiil", "ofaom", "chdaiirdainy", "ofchdamy", "opoeey", "of", "yddy")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        if not rows:
            raise ValueError(f"Refusing to infer fields for empty table: {path}")
        fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contains_atoms(needle: list[str], haystack: list[str]) -> bool:
    return any(haystack[index:index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    running = read_tsv(RUNNING_PATH)
    addresses = read_tsv(ADDRESS_PATH)
    source = read_tsv(SOURCE_PATH)
    values = {row["atom"]: row["working_value_de"] for row in read_tsv(VALUE_PATH)}
    factor_reader = load_module("gdt464_factor_reader", READER_PATH)

    running_recipe: dict[str, str] = {}
    running_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in running:
        previous = running_recipe.setdefault(row["surface"], row["component_recipe"])
        if previous != row["component_recipe"]:
            raise RuntimeError(f"Non-invariant running surface: {row['surface']}")
        running_events[row["surface"]].append(row)

    def literal(recipe: str) -> str:
        return " · ".join(values[atom] for atom in recipe.split("+"))

    def recipe_surfaces(sequence: str) -> list[str]:
        atoms = sequence.split("+")
        return sorted(
            surface for surface, recipe in running_recipe.items()
            if contains_atoms(atoms, recipe.split("+"))
        )

    def pages_for(surfaces: list[str]) -> set[str]:
        return {
            row["physical_page"]
            for surface in surfaces
            for row in running_events[surface]
        }

    # q is already a renderer channel, while bare of- extensions are six for
    # six O+LOCAL_CHAR_F. The six labels receive the same complete left card.
    of_extensions = sorted(surface for surface in running_recipe if surface.startswith("of"))
    of_matches = [
        surface for surface in of_extensions
        if running_recipe[surface].split("+")[:2] == ["O", "LOCAL_CHAR_F"]
    ]
    if running_recipe.get("qof") != "O+LOCAL_CHAR_F":
        raise RuntimeError("qof base card changed")

    # -ain is a completely filled suffix channel; ain and y are exact cards.
    ain_extensions = sorted(
        surface for surface in running_recipe
        if surface != "ain" and surface.endswith("ain")
    )
    ain_matches = [
        surface for surface in ain_extensions
        if running_recipe[surface].split("+")[-1:] == ["AIN"]
    ]
    if running_recipe.get("ain") != "AIN" or running_recipe.get("y") != "Y":
        raise RuntimeError("ain/y exact cards changed")

    # Terminal eey is kept separate from both lower-precision ey and longer
    # eeey. Only sorcheey is a learned exact-card exception.
    eey_candidates = sorted(
        surface for surface in running_recipe
        if surface.endswith("eey") and not surface.endswith("eeey")
    )
    eey_matches = [
        surface for surface in eey_candidates
        if running_recipe[surface].split("+")[-2:] == ["EE", "Y"]
    ]
    eey_mismatches = sorted(set(eey_candidates) - set(eey_matches))

    # y|d|dy is three exact cards. Its two overlapping directed arms are
    # independently populated across the running deck.
    exact_yddy_cards = {surface: running_recipe.get(surface) for surface in ("y", "d", "dy")}
    expected_yddy_cards = {"y": "Y", "d": "D_ADDR", "dy": "Y"}
    if exact_yddy_cards != expected_yddy_cards:
        raise RuntimeError(f"yddy card inventory changed: {exact_yddy_cards}")
    ydy_left = recipe_surfaces("Y+D_ADDR")
    ydy_right = recipe_surfaces("D_ADDR+Y")

    source_index = {row["surface"]: row for row in source}
    address_index = {row["surface"]: row for row in addresses}
    if set(RESIDUALS) - set(source_index):
        raise RuntimeError("Missing residual source rows")
    if source_index["korainy"]["gdt463_hybrid_status"] != "FULL_FUNCTION_FORMULA":
        raise RuntimeError("korainy anchor is no longer a full formula")

    decisions = [
        {
            "bridge_id": "G464-B01", "channel": "PREFIX_of",
            "channel_kind": "Q_STRIPPED_EXACT_CARD_PLUS_PERFECT_PREFIX_EXTENSIONS",
            "selected_recipe": "O+LOCAL_CHAR_F", "literal_working_value_de": literal("O+LOCAL_CHAR_F"),
            "calibration_candidate_type_count": len(of_extensions), "calibration_matching_type_count": len(of_matches),
            "calibration_precision": f"{len(of_matches) / len(of_extensions):.6f}",
            "matching_event_count": sum(len(running_events[s]) for s in of_matches),
            "matching_page_count": len(pages_for(of_matches)), "left_arm_type_count": 0, "right_arm_type_count": 0,
            "exact_card_bases": "qof=O+LOCAL_CHAR_F", "address_anchor": "NONE",
            "target_surfaces": "ofaom|ofaralar|ofchdamy|ofsholdy|of|ofakal", "target_count": 6,
            "exception": "NONE", "factor_gate_status": factor_reader.gate_recipe("O+LOCAL_CHAR_F", "NONE")["factor_gate_status"],
            "decision": "PROMOTE_FUNCTION_CHANNEL",
        },
        {
            "bridge_id": "G464-B02", "channel": "SUFFIX_ainy",
            "channel_kind": "TWO_EXACT_CARDS_PLUS_HELD_ADDRESS_ANCHOR",
            "selected_recipe": "AIN+Y", "literal_working_value_de": literal("AIN+Y"),
            "calibration_candidate_type_count": len(ain_extensions), "calibration_matching_type_count": len(ain_matches),
            "calibration_precision": f"{len(ain_matches) / len(ain_extensions):.6f}",
            "matching_event_count": sum(len(running_events[s]) for s in ain_matches),
            "matching_page_count": len(pages_for(ain_matches)), "left_arm_type_count": 0, "right_arm_type_count": 0,
            "exact_card_bases": "ain=AIN|y=Y", "address_anchor": "korainy=K+OR+AIN+Y",
            "target_surfaces": "chdaiirdainy|otainy", "target_count": 2, "exception": "NONE",
            "factor_gate_status": factor_reader.gate_recipe("AIN+Y", "NONE")["factor_gate_status"],
            "decision": "PROMOTE_EXACT_CARD_PACKAGE",
        },
        {
            "bridge_id": "G464-B03", "channel": "SUFFIX_eey",
            "channel_kind": "GRADE_BOUNDARY_SUFFIX_DISTINCT_FROM_EY_AND_EEEY",
            "selected_recipe": "EE+Y", "literal_working_value_de": literal("EE+Y"),
            "calibration_candidate_type_count": len(eey_candidates), "calibration_matching_type_count": len(eey_matches),
            "calibration_precision": f"{len(eey_matches) / len(eey_candidates):.6f}",
            "matching_event_count": sum(len(running_events[s]) for s in eey_matches),
            "matching_page_count": len(pages_for(eey_matches)), "left_arm_type_count": 0, "right_arm_type_count": 0,
            "exact_card_bases": "qoeey=O+EE+Y", "address_anchor": "NONE",
            "target_surfaces": "opoeey", "target_count": 1,
            "exception": "|".join(eey_mismatches) or "NONE",
            "factor_gate_status": factor_reader.gate_recipe("EE+Y", "NONE")["factor_gate_status"],
            "decision": "PROMOTE_GRADE_BOUNDARY_CHANNEL",
        },
        {
            "bridge_id": "G464-B04", "channel": "FULL_yddy",
            "channel_kind": "THREE_EXACT_CARDS_WITH_TWO_POPULATED_OVERLAPPING_ARMS",
            "selected_recipe": "Y+D_ADDR+Y", "literal_working_value_de": literal("Y+D_ADDR+Y"),
            "calibration_candidate_type_count": len(ydy_left) + len(ydy_right),
            "calibration_matching_type_count": len(ydy_left) + len(ydy_right), "calibration_precision": "1.000000",
            "matching_event_count": sum(len(running_events[s]) for s in ydy_left) + sum(len(running_events[s]) for s in ydy_right),
            "matching_page_count": len(pages_for(sorted(set(ydy_left) | set(ydy_right)))),
            "left_arm_type_count": len(ydy_left), "right_arm_type_count": len(ydy_right),
            "exact_card_bases": "y=Y|d=D_ADDR|dy=Y",
            "address_anchor": "GDT459:Y+D_ADDR+Y:y|d|dy:FACTOR_GREEN_CROSS_PAGE",
            "target_surfaces": "yddy", "target_count": 1, "exception": "NONE",
            "factor_gate_status": factor_reader.gate_recipe("Y+D_ADDR+Y", "NONE")["factor_gate_status"],
            "decision": "PROMOTE_OVERLAPPING_TWO_ARM_PACKAGE",
        },
    ]
    write_tsv(OUT / "gdt464_4_bridge_decisions.tsv", decisions)

    support_rows: list[dict[str, object]] = []

    def add_running_support(bridge: str, role: str, surface: str, status: str) -> None:
        events = running_events[surface]
        support_rows.append({
            "bridge_id": bridge, "support_role": role, "source_layer": "GDT407_RUNNING",
            "surface": surface, "component_recipe": running_recipe[surface], "event_count": len(events),
            "pages": "|".join(sorted({row["physical_page"] for row in events})),
            "registers": "|".join(sorted({row["register"] for row in events})), "support_status": status,
        })

    add_running_support("G464-B01", "Q_STRIPPED_BASE", "qof", "MATCH")
    for surface in of_extensions:
        add_running_support("G464-B01", "PREFIX_EXTENSION", surface, "MATCH" if surface in of_matches else "MISMATCH")
    add_running_support("G464-B02", "EXACT_CARD_BASE", "ain", "MATCH")
    add_running_support("G464-B02", "EXACT_CARD_BASE", "y", "MATCH")
    for surface in ain_extensions:
        add_running_support("G464-B02", "AIN_SUFFIX_EXTENSION", surface, "MATCH" if surface in ain_matches else "MISMATCH")
    anchor = source_index["korainy"]
    support_rows.append({
        "bridge_id": "G464-B02", "support_role": "HELD_ADDRESS_ANCHOR", "source_layer": "GDT463_ADDRESS",
        "surface": "korainy", "component_recipe": "K+OR+AIN+Y", "event_count": 1,
        "pages": anchor["physical_page"], "registers": anchor["register"], "support_status": "MATCH",
    })
    for surface in eey_candidates:
        add_running_support("G464-B03", "EXACT_EEY_BOUNDARY", surface, "MATCH" if surface in eey_matches else "EXACT_WHOLE_CARD_EXCEPTION")
    for surface in ("y", "d", "dy"):
        add_running_support("G464-B04", "EXACT_CARD_BASE", surface, "MATCH")
    for surface in ydy_left:
        add_running_support("G464-B04", "LEFT_ARM_Y_D_ADDR", surface, "MATCH")
    for surface in ydy_right:
        add_running_support("G464-B04", "RIGHT_ARM_D_ADDR_Y", surface, "MATCH")
    write_tsv(OUT / "gdt464_191_supporting_surfaces.tsv", support_rows)

    # Repeat the strict owner-family search separately. Mixed-class of is a
    # functional card, never assigned an object-family meaning.
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
            len(other_stem) > len(candidate[0]) and other_class == candidate[1] and other_indexes == candidate[2]
            for other_stem, other_class, other_indexes in raw_families
        )
    ]
    touching_families = [
        candidate for candidate in maximal_families
        if any(candidate[0] in residual for residual in RESIDUALS)
    ]
    write_tsv(OUT / "gdt464_owner_family_audit.tsv", [{
        "unique_address_surface_class_pair_count": len(address_items),
        "raw_replicated_owner_family_count": len(raw_families),
        "maximal_replicated_owner_family_count": len(maximal_families),
        "residual_surface_count": len(RESIDUALS),
        "residual_touching_strict_family_count": len(touching_families),
        "decision": "NO_NEW_STRICT_OWNER_FAMILY__USE_ONLY_FUNCTION_OR_EXACT_PACKAGE_BRIDGES",
    }])

    plans = {
        "ofaom": ("FUNCTION_SHELL_PLUS_LEARNED_CORE", "of|[STERNSTELLENNAME:aom]", "O+LOCAL_CHAR_F", "AUSFÜHRUNG · HIER · [STERNSTELLENNAME:aom]", 2, ("of", "O+LOCAL_CHAR_F"), ("NONE", "NONE"), "NONE", "OF_FUNCTION_CHANNEL"),
        "ofaralar": ("FULL_FUNCTION_FORMULA", "of|ar|al|ar", "O+LOCAL_CHAR_F+AR+AL+AR", "AUSFÜHRUNG · HIER · AUSGANG · ZIELORT · AUSGANG", 8, ("of", "O+LOCAL_CHAR_F"), ("ar", "AR"), "2:ar=AR|4:al=AL", "OF_FUNCTION_CHANNEL"),
        "ofchdamy": ("FUNCTION_SHELL_PLUS_LEARNED_CORE", "of|[STERNSTELLENNAME:chdamy]", "O+LOCAL_CHAR_F", "AUSFÜHRUNG · HIER · [STERNSTELLENNAME:chdamy]", 2, ("of", "O+LOCAL_CHAR_F"), ("NONE", "NONE"), "NONE", "OF_FUNCTION_CHANNEL"),
        "ofsholdy": ("FUNCTION_SHELL_PLUS_LEARNED_CORE", "of|sh|ol|[STERNSTELLENNAME:dy]", "O+LOCAL_CHAR_F+SH+OL", "AUSFÜHRUNG · HIER · HALTEN · FORTSETZEN · [STERNSTELLENNAME:dy]", 6, ("of", "O+LOCAL_CHAR_F"), ("NONE", "NONE"), "2:sh=SH|4:ol=OL", "OF_FUNCTION_CHANNEL"),
        "of": ("FULL_FUNCTION_FORMULA", "of", "O+LOCAL_CHAR_F", "AUSFÜHRUNG · HIER", 2, ("of", "O+LOCAL_CHAR_F"), ("NONE", "NONE"), "NONE", "OF_FUNCTION_CHANNEL"),
        "ofakal": ("FUNCTION_SHELL_PLUS_LEARNED_CORE", "of|[DROGENNAME:ak]|al", "O+LOCAL_CHAR_F+AL", "AUSFÜHRUNG · HIER · [DROGENNAME:ak] · ZIELORT", 4, ("of", "O+LOCAL_CHAR_F"), ("al", "AL"), "NONE", "OF_FUNCTION_CHANNEL"),
        "chdaiirdainy": ("FUNCTION_SHELL_PLUS_LEARNED_CORE", "[STERNSTELLENNAME:chdaiird]|ain|y", "AIN+Y", "[STERNSTELLENNAME:chdaiird] · ANTEIL · POSTEN", 4, ("NONE", "NONE"), ("ainy", "AIN+Y"), "NONE", "AINY_EXACT_CARD_PACKAGE"),
        "otainy": ("FULL_FUNCTION_FORMULA", "ot|ain|y", "OT+AIN+Y", "DANACH · ANTEIL · POSTEN", 6, ("ot", "OT"), ("ainy", "AIN+Y"), "NONE", "AINY_EXACT_CARD_PACKAGE"),
        "opoeey": ("FUNCTION_SHELL_PLUS_LEARNED_CORE", "[STERNSTELLENNAME:opo]|eey", "EE+Y", "[STERNSTELLENNAME:opo] · GRAD II · POSTEN", 3, ("NONE", "NONE"), ("eey", "EE+Y"), "NONE", "EEY_GRADE_BOUNDARY_CHANNEL"),
        "yddy": ("FULL_FUNCTION_FORMULA", "y|d|dy", "Y+D_ADDR+Y", "POSTEN · HIER · POSTEN", 4, ("yddy", "Y+D_ADDR+Y"), ("NONE", "NONE"), "NONE", "YDY_OVERLAPPING_TWO_ARM_PACKAGE"),
    }

    revised_rows: list[dict[str, object]] = []
    target_rows: list[dict[str, object]] = []
    for ordinal, old in enumerate(source, start=1):
        plan = plans.get(old["surface"])
        if plan:
            status, seg, recipe, default, known, prefix, suffix, internal, change = plan
        else:
            status, seg, recipe, default = old["gdt463_hybrid_status"], old["surface_segmentation"], old["ordered_function_recipe_trace"], old["revised_short_default_de"]
            known, prefix, suffix, internal, change = int(old["known_function_character_count"]), (old["prefix_stem"], old["prefix_recipe"]), (old["suffix_stem"], old["suffix_recipe"]), old["internal_stem_trace"], "UNCHANGED"
        row = {
            "gdt464_label_id": f"G464-L{ordinal:03d}", "gdt463_label_id": old["gdt463_label_id"],
            "source_event_id": old["source_event_id"], "physical_page": old["physical_page"], "register": old["register"],
            "locus": old["locus"], "owner_de": old["owner_de"], "surface": old["surface"], "content_class": old["content_class"],
            "gdt463_hybrid_status": old["gdt463_hybrid_status"], "gdt464_hybrid_status": status,
            "surface_segmentation": seg, "prefix_stem": prefix[0], "prefix_recipe": prefix[1],
            "internal_stem_trace": internal, "suffix_stem": suffix[0], "suffix_recipe": suffix[1],
            "owner_family_stem_trace": old["owner_family_stem_trace"], "known_function_character_count": known,
            "remaining_learned_character_count": len(old["surface"]) - known, "surface_character_count": old["surface_character_count"],
            "known_function_fraction": f"{known / len(old['surface']):.6f}", "ordered_function_recipe_trace": recipe,
            "revised_short_default_de": default, "gdt464_change": change,
            "strongest_rival": "EMBEDDED_PACKAGE_IS_NAME_SPELLING" if plan else old["strongest_rival"],
            "image_object_id": old["image_object_id"], "review_image_sha256": old["review_image_sha256"],
        }
        revised_rows.append(row)
        if plan:
            target_rows.append({
                "target_id": f"G464-T{len(target_rows) + 1:02d}", "source_event_id": old["source_event_id"],
                "physical_page": old["physical_page"], "surface": old["surface"], "content_class": old["content_class"],
                "old_status": old["gdt463_hybrid_status"], "new_status": status,
                "selected_surface_segmentation": seg, "selected_function_recipe": recipe, "selected_literal_de": default,
                "old_known_character_count": old["known_function_character_count"], "new_known_character_count": known,
                "added_known_character_count": known - int(old["known_function_character_count"]), "revision_channel": change,
            })
    write_tsv(OUT / "gdt464_10_target_revisions.tsv", target_rows)
    write_tsv(OUT / "gdt464_107_revised_hybrid_dictionary.tsv", revised_rows)

    revised_index = {row["surface"]: row for row in revised_rows}
    residual_rows: list[dict[str, object]] = []
    for ordinal, surface in enumerate(RESIDUALS, start=1):
        old, new = source_index[surface], revised_index[surface]
        residual_rows.append({
            "residual_id": f"G464-R{ordinal:02d}", "surface": surface, "physical_page": old["physical_page"],
            "content_class": old["content_class"], "old_status": old["gdt463_hybrid_status"], "new_status": new["gdt464_hybrid_status"],
            "selected_segmentation": new["surface_segmentation"], "selected_recipe": new["ordered_function_recipe_trace"],
            "revised_short_default_de": new["revised_short_default_de"], "known_character_count": new["known_function_character_count"],
            "remaining_learned_character_count": new["remaining_learned_character_count"],
            "decision": "KEEP_WHOLE_ONLY_RESIDUAL" if surface == "oiil" else "PROMOTE_BOUNDED_BRIDGE",
            "strict_owner_family_bridge": "NONE",
        })
    write_tsv(OUT / "gdt464_7_residual_decisions.tsv", residual_rows)

    page_rows: list[dict[str, object]] = []
    for page in sorted({row["physical_page"] for row in revised_rows}):
        selected = [row for row in revised_rows if row["physical_page"] == page]
        statuses = Counter(str(row["gdt464_hybrid_status"]) for row in selected)
        page_rows.append({
            "physical_page": page, "register": selected[0]["register"], "content_class": selected[0]["content_class"],
            "label_count": len(selected), "full_function_formula_count": statuses["FULL_FUNCTION_FORMULA"],
            "function_shell_plus_core_count": statuses["FUNCTION_SHELL_PLUS_LEARNED_CORE"],
            "owner_family_only_count": statuses["OWNER_FAMILY_STEM_ONLY"], "whole_learned_label_count": statuses["WHOLE_LEARNED_LABEL"],
            "gdt464_change_count": sum(row["gdt464_change"] != "UNCHANGED" for row in selected),
            "known_function_character_count": sum(int(row["known_function_character_count"]) for row in selected),
            "surface_character_count": sum(int(row["surface_character_count"]) for row in selected),
        })
    write_tsv(OUT / "gdt464_6_page_summary.tsv", page_rows)

    statuses = Counter(str(row["gdt464_hybrid_status"]) for row in revised_rows)
    known = sum(int(row["known_function_character_count"]) for row in revised_rows)
    total = sum(int(row["surface_character_count"]) for row in revised_rows)
    result = {
        "status": "FOUR_BOUNDED_BRIDGES_REDUCE_WHOLE_LABEL_TAIL_TO_ONE", "source_label_count": len(source),
        "bridge_count": len(decisions), "changed_label_count": len(target_rows), "source_residual_count": len(RESIDUALS),
        "promoted_residual_count": sum(row["decision"] == "PROMOTE_BOUNDED_BRIDGE" for row in residual_rows),
        "remaining_whole_label_count": statuses["WHOLE_LEARNED_LABEL"],
        "remaining_whole_labels": sorted(row["surface"] for row in revised_rows if row["gdt464_hybrid_status"] == "WHOLE_LEARNED_LABEL"),
        "revised_hybrid_status_counts": dict(sorted(statuses.items())),
        "labels_with_any_function_count": sum(int(row["known_function_character_count"]) > 0 for row in revised_rows),
        "labels_with_any_structure_count": sum(int(row["known_function_character_count"]) > 0 or row["owner_family_stem_trace"] != "NONE" for row in revised_rows),
        "known_function_character_count": known, "surface_character_count": total,
        "known_function_character_fraction": f"{known / total:.6f}",
        "strict_residual_owner_family_bridge_count": len(touching_families),
        "new_core_meanings": 0, "new_pages": 0, "surface_predictions": 0, "confirmed_lexemes": 0,
    }
    (OUT / "gdt464_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
