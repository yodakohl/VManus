#!/usr/bin/env python3
"""Project repeated Source CH-bearing packages onto the open CH+CH target."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt508_source_chch_repeated_package_bridge"
ART = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G425 = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts"
G436 = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts"
G500 = ROOT / "experiments/yolo/gdt500_repeated_action_fluency_matrix/artifacts"
G507 = ROOT / "experiments/yolo/gdt507_contextual_pair_argument_bridge_atlas/artifacts"

DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
FACTORS_IN = G425 / "gdt425_4576_event_factorized_action_replay.tsv"
STREAM_IN = G436 / "gdt436_4576_oracle_free_stream_readings.tsv"
FLUENCY_IN = G500 / "gdt500_15_repeated_action_fluency_cards.tsv"
TARGETS_IN = G507 / "gdt507_4_target_context_bridge_cards.tsv"

PAIRS_OUT = ART / "gdt508_2_source_repeated_ch_package_pairs.tsv"
ARMS_OUT = ART / "gdt508_4_package_cancellation_arms.tsv"
TARGET_OUT = ART / "gdt508_1_source_chch_local_bridge_card.tsv"
READABLE_OUT = ART / "GDT508_SOURCE_CHCH_REPEATED_PACKAGE_BRIDGE.md"
RESULT_OUT = ART / "gdt508_result.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
STATUS = "SOURCE_CHCH_GAINS_LOCAL_REPEATED_PACKAGE_BRIDGE__ALL_FOUR_CONTEXT_TARGETS_HAVE_LOCAL_SUPPORT"
GUARD = "LOCAL_PACKAGE_PROJECTION_ONLY__BARE_SOURCE_CHCH_TARGET_REMAINS_UNOBSERVED"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def common_prefix(left: list[str], right: list[str]) -> list[str]:
    result: list[str] = []
    for a, b in zip(left, right):
        if a != b:
            break
        result.append(a)
    return result


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _dictionary_fields, dictionary = read_tsv(DICTIONARY_IN)
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _factor_fields, factors = read_tsv(FACTORS_IN)
    _stream_fields, stream = read_tsv(STREAM_IN)
    _fluency_fields, fluency = read_tsv(FLUENCY_IN)
    _target_fields, targets = read_tsv(TARGETS_IN)
    if (len(dictionary), len(clauses), len(factors), len(stream), len(fluency), len(targets)) != (46, 4576, 4576, 4576, 15, 4):
        raise ValueError("GDT413/GDT416/GDT425/GDT436/GDT500/GDT507 source drift")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    factor_by_event = {row["global_running_event_id"]: row for row in factors}
    stream_by_event = {row["event_id"]: row for row in stream}
    target = next(row for row in targets if row["target_matrix_cell_id"] == "G498-M456")
    fluency_card = next(row for row in fluency if row["source_matrix_cell_id"] == "G498-M456")
    if target["ordered_action_pair"] != "CH+CH" or target["target_register"] != "SOURCE_SECTION_T":
        raise ValueError("Source CH+CH target drift")
    if fluency_card["current_default_phrase_de"] != target["target_current_default_phrase_de"]:
        raise ValueError("GDT500/GDT507 phrase drift")

    pair_rows: list[dict[str, object]] = []
    arm_rows: list[dict[str, object]] = []
    for left_index, left in enumerate(clauses):
        for intervening_count in (0, 1):
            right_index = left_index + intervening_count + 1
            if right_index >= len(clauses):
                continue
            right = clauses[right_index]
            middle = clauses[left_index + 1 : right_index]
            if left["register"] != "SOURCE_SECTION_T" or right["register"] != "SOURCE_SECTION_T":
                continue
            if (left["physical_page"], left["global_statement_id"], left["owner_class"], left["owner_de"]) != (
                right["physical_page"], right["global_statement_id"], right["owner_class"], right["owner_de"]
            ):
                continue
            if int(right["card_ordinal_in_statement"]) != int(left["card_ordinal_in_statement"]) + intervening_count + 1:
                continue
            if left["explicit_action_roots"] != right["explicit_action_roots"]:
                continue
            actions = left["explicit_action_roots"].split("|")
            if actions.count("CH") != 1 or not actions or actions[0] != "CH":
                continue
            if left["explicit_argument_roots"] != "NONE" or right["explicit_argument_roots"] != "NONE":
                continue
            inherited = left["inherited_argument_root"]
            if inherited == "NONE" or right["inherited_argument_root"] != inherited:
                continue

            left_recipe = left["component_recipe"].split("+")
            right_recipe = right["component_recipe"].split("+")
            prefix = common_prefix(left_recipe, right_recipe)
            left_removed = left_recipe.copy()
            left_removed.remove("CH")
            right_removed = right_recipe.copy()
            right_removed.remove("CH")
            left_state = stream_by_event[left["global_running_event_id"]]
            right_state = stream_by_event[right["global_running_event_id"]]
            middle_ids = [row["global_running_event_id"] for row in middle]
            middle_recipes = [row["component_recipe"] for row in middle]
            middle_argument_roots = [row["explicit_argument_roots"] if row["explicit_argument_roots"] != "NONE" else row["inherited_argument_root"] for row in middle]
            relation = "EXACT_DUPLICATED_PACKAGE" if left_recipe == right_recipe else "SHARED_PREFIX_PACKAGE_WITH_RIGHT_EXTENSION"
            pair_id = f"G508-P{len(pair_rows) + 1:02d}"
            pair_rows.append({
                "source_repeated_package_pair_id": pair_id,
                "package_relation": relation,
                "physical_page": left["physical_page"],
                "register": left["register"],
                "owner_class": left["owner_class"],
                "owner_de": left["owner_de"],
                "global_statement_id": left["global_statement_id"],
                "left_event_id": left["global_running_event_id"],
                "right_event_id": right["global_running_event_id"],
                "left_card_ordinal": left["card_ordinal_in_statement"],
                "right_card_ordinal": right["card_ordinal_in_statement"],
                "intervening_card_count": intervening_count,
                "intervening_event_ids": "|".join(middle_ids) if middle_ids else "NONE",
                "intervening_component_recipes": "|".join(middle_recipes) if middle_recipes else "NONE",
                "intervening_argument_roots": "|".join(middle_argument_roots) if middle_argument_roots else "NONE",
                "left_surface": left["surface"],
                "right_surface": right["surface"],
                "left_component_recipe": left["component_recipe"],
                "right_component_recipe": right["component_recipe"],
                "shared_action_roots": left["explicit_action_roots"],
                "shared_component_prefix": "+".join(prefix),
                "shared_component_prefix_length": len(prefix),
                "same_surface": "YES" if left["surface"] == right["surface"] else "NO",
                "same_component_recipe": "YES" if left_recipe == right_recipe else "NO",
                "same_imperative_clause": "YES" if left["imperative_clause_de"] == right["imperative_clause_de"] else "NO",
                "shared_inherited_argument_root": inherited,
                "left_stream_active_argument_before": left_state["active_argument_before"],
                "left_stream_active_argument_after": left_state["active_argument_after"],
                "right_stream_active_argument_before": right_state["active_argument_before"],
                "right_stream_active_argument_after": right_state["active_argument_after"],
                "middle_preserves_or_reasserts_argument": "YES" if all(stream_by_event[row["global_running_event_id"]]["active_argument_after"] == inherited for row in middle) else ("NOT_APPLICABLE" if not middle else "NO"),
                "left_factorized_action_replay_status": factor_by_event[left["global_running_event_id"]]["factorized_action_replay_status"],
                "right_factorized_action_replay_status": factor_by_event[right["global_running_event_id"]]["factorized_action_replay_status"],
                "left_imperative_clause_de": left["imperative_clause_de"],
                "right_imperative_clause_de": right["imperative_clause_de"],
                "projected_target_action_recipe": "CH+CH",
                "projected_fluent_default_de": fluency_card["current_default_phrase_de"],
                "projection_status": "LOCAL_REPEATED_CH_PACKAGE_BRIDGE__TARGET_UNOBSERVED",
                "guard": GUARD,
            })

            for side, source, removed, state in (
                ("LEFT", left, left_removed, left_state),
                ("RIGHT", right, right_removed, right_state),
            ):
                arm_rows.append({
                    "package_cancellation_arm_id": f"G508-A{len(arm_rows) + 1:02d}",
                    "source_repeated_package_pair_id": pair_id,
                    "side": side,
                    "source_event_id": source["global_running_event_id"],
                    "source_component_recipe": source["component_recipe"],
                    "source_action_roots": source["explicit_action_roots"],
                    "retained_target_action_root": "CH",
                    "retained_ch_component_position": source["component_recipe"].split("+").index("CH") + 1,
                    "removed_package_atoms": "+".join(removed) if removed else "NONE",
                    "removed_package_values_de": " · ".join(values[atom] for atom in removed) if removed else "NONE",
                    "removed_package_atom_count": len(removed),
                    "inherited_argument_root": source["inherited_argument_root"],
                    "stream_active_argument_before": state["active_argument_before"],
                    "stream_active_argument_after": state["active_argument_after"],
                    "source_imperative_clause_de": source["imperative_clause_de"],
                    "target_action_slot_ordinal": 1 if side == "LEFT" else 2,
                    "target_action_slot_retained": "YES",
                    "foreign_package_frame_transferred": "NO",
                    "guard": GUARD,
                })

    if (len(pair_rows), len(arm_rows)) != (2, 4):
        raise ValueError(f"expected two Source repeated-package pairs/four arms, got {len(pair_rows)}/{len(arm_rows)}")

    selected = next(row for row in pair_rows if row["package_relation"] == "EXACT_DUPLICATED_PACKAGE")
    corroborating = next(row for row in pair_rows if row["package_relation"] == "SHARED_PREFIX_PACKAGE_WITH_RIGHT_EXTENSION")
    target_card = [{
        "source_chch_local_bridge_card_id": "G508-T01",
        "source_gdt507_target_context_bridge_card_id": target["target_context_bridge_card_id"],
        "target_matrix_cell_id": target["target_matrix_cell_id"],
        "target_action_recipe": target["target_action_recipe"],
        "target_register": target["target_register"],
        "target_current_default_phrase_de": target["target_current_default_phrase_de"],
        "gdt500_compression_rule": fluency_card["compression_rule"],
        "old_gdt507_bridge_tier": target["new_context_bridge_tier"],
        "old_gdt507_context_bridge_locality": target["context_bridge_locality"],
        "new_local_bridge_tier": "LOCAL_REPEATED_PACKAGE_CANCELLATION_PLUS_CROSS_REGISTER_DIRECT_PAIR",
        "new_context_support_locality": "LOCAL_SOURCE_PACKAGE_LEVEL",
        "source_repeated_package_pair_count": len(pair_rows),
        "selected_exact_duplicate_pair_id": selected["source_repeated_package_pair_id"],
        "selected_exact_duplicate_event_ids": f"{selected['left_event_id']}→{selected['right_event_id']}",
        "selected_exact_duplicate_recipe": selected["left_component_recipe"],
        "selected_exact_duplicate_argument_root": selected["shared_inherited_argument_root"],
        "selected_exact_duplicate_clause_de": selected["left_imperative_clause_de"],
        "corroborating_one_gap_pair_id": corroborating["source_repeated_package_pair_id"],
        "corroborating_event_ids": f"{corroborating['left_event_id']}→{corroborating['intervening_event_ids']}→{corroborating['right_event_id']}",
        "corroborating_shared_prefix": corroborating["shared_component_prefix"],
        "corroborating_argument_root": corroborating["shared_inherited_argument_root"],
        "retained_target_action_slots": 2,
        "local_package_projection_de": "Behalte aus jedem der zwei Source-Pakete genau CH; streiche den jeweils alten T-/Relationsrahmen und lies die zwei erhaltenen CH-Slots als zweimalige Handlung am selben geerbten Argument.",
        "target_bridge_status": "LOCAL_CONTEXT_BRIDGED_WORKING__TARGET_RECIPE_UNOBSERVED",
        "all_four_gdt507_context_targets_have_local_support": "YES",
        "target_evidence_status_retained": target["target_evidence_status_retained"],
        "target_phrase_changed": "NO",
        "working_root_meaning_changed": "NO",
        "surface_prediction_made": "NO",
        "occurrence_prediction_made": "NO",
        "guard": GUARD,
    }]

    write_tsv(PAIRS_OUT, pair_rows)
    write_tsv(ARMS_OUT, arm_rows)
    write_tsv(TARGET_OUT, target_card)

    readable = [
        "# GDT508 — Lokale Source-Brücke für `CH+CH`",
        "",
        f"Status: `{STATUS}`",
        "",
        "## Exakte Wiederholung",
        "",
        f"`{selected['left_event_id']}→{selected['right_event_id']}` wiederholt `{selected['left_component_recipe']}` ohne Zwischenkarte, mit derselben Oberfläche, derselben Klausel und demselben geerbten `{selected['shared_inherited_argument_root']}`.",
        "",
        f"> {selected['left_imperative_clause_de']} {selected['right_imperative_clause_de']}",
        "",
        "Aus jedem Paket bleibt für die Zielprojektion genau `CH`; der gemeinsame `T+AR`-Rahmen wird nicht übertragen. Die zwei erhaltenen Slots ergeben den bereits festen GDT500-Default:",
        "",
        f"> {fluency_card['current_default_phrase_de']}",
        "",
        "## Zweite lokale Folge",
        "",
        f"`{corroborating['left_event_id']}→{corroborating['intervening_event_ids']}→{corroborating['right_event_id']}` wiederholt den Präfix `{corroborating['shared_component_prefix']}` um eine sichtbare Argumentkarte; beide äußeren Pakete erben `{corroborating['shared_inherited_argument_root']}`.",
        "",
        "## Grenze",
        "",
        "Dies ist eine lokale Paketprojektion, kein beobachtetes nacktes `CH+CH`-Rezept. Der ältere direkte Paarträger bleibt registerübergreifend. Phrase, zwei Handlungsslots, Wurzelwerte, Evidenzklasse und alle Oberflächen bleiben unverändert.",
    ]
    READABLE_OUT.write_text("\n".join(readable) + "\n", encoding="utf-8")

    relations = Counter(str(row["package_relation"]) for row in pair_rows)
    result = {
        "status": STATUS,
        "source_repeated_ch_package_pairs": len(pair_rows),
        "exact_duplicated_package_pairs": relations["EXACT_DUPLICATED_PACKAGE"],
        "one_intervening_card_package_pairs": sum(int(row["intervening_card_count"]) == 1 for row in pair_rows),
        "shared_prefix_extension_pairs": relations["SHARED_PREFIX_PACKAGE_WITH_RIGHT_EXTENSION"],
        "package_cancellation_arms": len(arm_rows),
        "retained_ch_action_slots": sum(int(row["target_action_slot_retained"] == "YES") for row in arm_rows),
        "source_chch_target_cards": len(target_card),
        "all_four_context_targets_have_local_support": 1,
        "target_recipe_observations": 0,
        "target_phrases_changed": 0,
        "working_root_meanings_changed": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
