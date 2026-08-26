#!/usr/bin/env python3
"""Find target-register factor bridges for GDT509's four cross-frame cards."""

from __future__ import annotations

import csv
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt510_four_cross_frame_local_factor_bridges"
ART = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G425 = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts"
G436 = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts"
G509 = ROOT / "experiments/yolo/gdt509_eleven_pair_target_evidence_strength_deck/artifacts"

DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
FACTORS_IN = G425 / "gdt425_4576_event_factorized_action_replay.tsv"
STREAM_IN = G436 / "gdt436_4576_oracle_free_stream_readings.tsv"
DECK_IN = G509 / "gdt509_11_pair_target_evidence_strength_cards.tsv"

SUFFIX_OUT = ART / "gdt510_1_celestial_pch_local_suffix_carrier.tsv"
RECTANGLES_OUT = ART / "gdt510_3_schd_local_head_argument_rectangles.tsv"
WITNESSES_OUT = ART / "gdt510_6_schd_selected_head_witnesses.tsv"
UPGRADES_OUT = ART / "gdt510_4_cross_frame_target_local_upgrade_cards.tsv"
READABLE_OUT = ART / "GDT510_FOUR_CROSS_FRAME_LOCAL_FACTOR_BRIDGES.md"
RESULT_OUT = ART / "gdt510_result.json"

STATUS = "CELESTIAL_PCH_HAS_LOCAL_SUFFIX__THREE_SCHD_TARGETS_HAVE_LOCAL_HEAD_ARGUMENT_RECTANGLES"
GUARD = "LOCAL_FACTOR_BRIDGE_ONLY__BARE_TARGETS_UNOBSERVED__CROSS_PAIR_ORDER_RETAINED_WHERE_NEEDED"


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


def event_number(event_id: str) -> int:
    return int(event_id.rsplit("E", 1)[1])


def y_mode(row: dict[str, str]) -> str | None:
    explicit = [] if row["explicit_argument_roots"] == "NONE" else row["explicit_argument_roots"].split("|")
    if "Y" in explicit:
        return "EXPLICIT_Y"
    if row["inherited_argument_root"] == "Y":
        return "INHERITED_Y"
    return None


def frame_atoms(row: dict[str, str], head: str) -> list[str]:
    tokens = row["component_recipe"].split("+")
    result = tokens.copy()
    result.remove(head)
    if y_mode(row) == "EXPLICIT_Y":
        result.remove("Y")
    return result


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _dictionary_fields, dictionary = read_tsv(DICTIONARY_IN)
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _factor_fields, factors = read_tsv(FACTORS_IN)
    _stream_fields, stream = read_tsv(STREAM_IN)
    _deck_fields, deck = read_tsv(DECK_IN)
    if (len(dictionary), len(clauses), len(factors), len(stream), len(deck)) != (46, 4576, 4576, 4576, 11):
        raise ValueError("GDT413/GDT416/GDT425/GDT436/GDT509 source drift")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    factor_by_event = {row["global_running_event_id"]: row for row in factors}
    stream_by_event = {row["event_id"]: row for row in stream}
    cross_cards = [row for row in deck if row["evidence_route"] == "B_CROSS_REGISTER_FRAME_REDUCTION"]
    if len(cross_cards) != 4:
        raise ValueError("expected four GDT509 cross-frame targets")

    pch_target = next(row for row in cross_cards if row["target_action_recipe"] == "P+CH+E+Y")
    suffix_matches: list[tuple[dict[str, str], int]] = []
    target_tokens = pch_target["target_action_recipe"].split("+")
    for clause in clauses:
        if clause["register"] != pch_target["target_register"]:
            continue
        tokens = clause["component_recipe"].split("+")
        for start in range(len(tokens) - len(target_tokens) + 1):
            if tokens[start : start + len(target_tokens)] == target_tokens:
                suffix_matches.append((clause, start))
    if len(suffix_matches) != 1:
        raise ValueError(f"expected one Celestial P+CH+E+Y local contiguous carrier, got {len(suffix_matches)}")
    suffix_clause, suffix_start = suffix_matches[0]
    suffix_tokens = suffix_clause["component_recipe"].split("+")
    removed_prefix = suffix_tokens[:suffix_start]
    removed_suffix = suffix_tokens[suffix_start + len(target_tokens) :]
    suffix_factor = factor_by_event[suffix_clause["global_running_event_id"]]
    suffix_state = stream_by_event[suffix_clause["global_running_event_id"]]
    suffix_row = [{
        "local_suffix_carrier_id": "G510-P01",
        "source_gdt509_card_id": pch_target["evidence_strength_card_id"],
        "target_matrix_cell_id": pch_target["target_matrix_cell_id"],
        "target_register": pch_target["target_register"],
        "target_action_recipe": pch_target["target_action_recipe"],
        "global_running_event_id": suffix_clause["global_running_event_id"],
        "physical_page": suffix_clause["physical_page"],
        "owner_class": suffix_clause["owner_class"],
        "owner_de": suffix_clause["owner_de"],
        "surface": suffix_clause["surface"],
        "source_component_recipe": suffix_clause["component_recipe"],
        "source_explicit_action_roots": suffix_clause["explicit_action_roots"],
        "target_contiguous_start_position": suffix_start + 1,
        "target_contiguous_end_position": suffix_start + len(target_tokens),
        "target_contiguous_exact": "YES",
        "removed_prefix_atoms": "+".join(removed_prefix) if removed_prefix else "NONE",
        "removed_prefix_values_de": " · ".join(values[atom] for atom in removed_prefix) if removed_prefix else "NONE",
        "removed_suffix_atoms": "+".join(removed_suffix) if removed_suffix else "NONE",
        "retained_target_atoms": "+".join(target_tokens),
        "explicit_argument_roots": suffix_clause["explicit_argument_roots"],
        "inherited_argument_root": suffix_clause["inherited_argument_root"],
        "stream_active_argument_before": suffix_state["active_argument_before"],
        "stream_active_argument_after": suffix_state["active_argument_after"],
        "stream_state_matches_reference": suffix_state["state_matches_reference"],
        "factorized_action_replay_status": suffix_factor["factorized_action_replay_status"],
        "source_imperative_clause_de": suffix_clause["imperative_clause_de"],
        "target_working_translation_de": pch_target["working_translation_de"],
        "upgrade_status": "LOCAL_BROADER_CHAIN_CONTIGUOUS_SUFFIX_REDUCTION",
        "target_recipe_observed_exactly": "NO",
        "guard": GUARD,
    }]

    schd_cards = sorted((row for row in cross_cards if row["target_action_recipe"] == "S+CHD+Y"), key=lambda row: row["target_register"])
    if len(schd_cards) != 3:
        raise ValueError("expected three S+CHD+Y cross-frame targets")

    rectangle_rows: list[dict[str, object]] = []
    witness_rows: list[dict[str, object]] = []
    selected_by_card: dict[str, dict[str, object]] = {}
    for card in schd_cards:
        register = card["target_register"]
        s_candidates = [row for row in clauses if row["register"] == register and row["explicit_action_roots"] == "S" and y_mode(row)]
        chd_candidates = [row for row in clauses if row["register"] == register and row["explicit_action_roots"] == "CHD" and y_mode(row)]
        candidate_pairs = [(left, right) for left in s_candidates for right in chd_candidates]
        if not candidate_pairs:
            raise ValueError(f"missing S/CHD Y rectangle in {register}")

        def rank(pair: tuple[dict[str, str], dict[str, str]]) -> tuple[object, ...]:
            left, right = pair
            return (
                left["owner_de"] != right["owner_de"],
                left["physical_page"] != right["physical_page"],
                left["global_statement_id"] != right["global_statement_id"],
                event_number(left["global_running_event_id"]) > event_number(right["global_running_event_id"]),
                len(frame_atoms(left, "S")) + len(frame_atoms(right, "CHD")),
                abs(event_number(left["global_running_event_id"]) - event_number(right["global_running_event_id"])),
                left["global_running_event_id"],
                right["global_running_event_id"],
            )

        selected_s, selected_chd = min(candidate_pairs, key=rank)
        same_owner = selected_s["owner_de"] == selected_chd["owner_de"]
        same_page = selected_s["physical_page"] == selected_chd["physical_page"]
        same_statement = selected_s["global_statement_id"] == selected_chd["global_statement_id"]
        chronological = event_number(selected_s["global_running_event_id"]) < event_number(selected_chd["global_running_event_id"])
        rectangle_id = f"G510-R{len(rectangle_rows) + 1:02d}"
        rectangle = {
            "local_head_argument_rectangle_id": rectangle_id,
            "source_gdt509_card_id": card["evidence_strength_card_id"],
            "target_matrix_cell_id": card["target_matrix_cell_id"],
            "target_register": register,
            "target_action_recipe": card["target_action_recipe"],
            "local_s_on_y_event_count": len(s_candidates),
            "local_chd_on_y_event_count": len(chd_candidates),
            "local_s_chd_y_candidate_pair_count": len(candidate_pairs),
            "selected_s_event_id": selected_s["global_running_event_id"],
            "selected_chd_event_id": selected_chd["global_running_event_id"],
            "selected_s_page": selected_s["physical_page"],
            "selected_chd_page": selected_chd["physical_page"],
            "selected_s_owner_de": selected_s["owner_de"],
            "selected_chd_owner_de": selected_chd["owner_de"],
            "selected_same_page": "YES" if same_page else "NO",
            "selected_same_owner": "YES" if same_owner else "NO",
            "selected_same_statement": "YES" if same_statement else "NO",
            "selected_s_before_chd_in_stream": "YES" if chronological else "NO",
            "selected_s_y_mode": y_mode(selected_s),
            "selected_chd_y_mode": y_mode(selected_chd),
            "selected_s_component_recipe": selected_s["component_recipe"],
            "selected_chd_component_recipe": selected_chd["component_recipe"],
            "selected_s_frame_atoms": "+".join(frame_atoms(selected_s, "S")) if frame_atoms(selected_s, "S") else "NONE",
            "selected_chd_frame_atoms": "+".join(frame_atoms(selected_chd, "CHD")) if frame_atoms(selected_chd, "CHD") else "NONE",
            "cross_register_pair_order_evidence_ids": card["source_evidence_ids"],
            "target_working_translation_de": card["working_translation_de"],
            "rectangle_status": "LOCAL_S_ON_Y_PLUS_CHD_ON_Y__CROSS_REGISTER_S_TO_CHD_ORDER",
            "target_recipe_observed_exactly": "NO",
            "guard": GUARD,
        }
        rectangle_rows.append(rectangle)
        selected_by_card[card["evidence_strength_card_id"]] = rectangle

        for head, selected in (("S", selected_s), ("CHD", selected_chd)):
            state = stream_by_event[selected["global_running_event_id"]]
            factor = factor_by_event[selected["global_running_event_id"]]
            removed = frame_atoms(selected, head)
            witness_rows.append({
                "selected_head_witness_id": f"G510-W{len(witness_rows) + 1:02d}",
                "local_head_argument_rectangle_id": rectangle_id,
                "target_register": register,
                "action_head": head,
                "global_running_event_id": selected["global_running_event_id"],
                "global_statement_id": selected["global_statement_id"],
                "physical_page": selected["physical_page"],
                "owner_class": selected["owner_class"],
                "owner_de": selected["owner_de"],
                "surface": selected["surface"],
                "component_recipe": selected["component_recipe"],
                "y_mode": y_mode(selected),
                "explicit_argument_roots": selected["explicit_argument_roots"],
                "inherited_argument_root": selected["inherited_argument_root"],
                "non_head_non_y_frame_atoms": "+".join(removed) if removed else "NONE",
                "non_head_non_y_frame_values_de": " · ".join(values[atom] for atom in removed) if removed else "NONE",
                "stream_active_argument_before": state["active_argument_before"],
                "stream_active_argument_after": state["active_argument_after"],
                "stream_state_matches_reference": state["state_matches_reference"],
                "factorized_action_replay_status": factor["factorized_action_replay_status"],
                "imperative_clause_de": selected["imperative_clause_de"],
                "guard": GUARD,
            })

    upgrade_rows: list[dict[str, object]] = []
    for card in cross_cards:
        if card["target_action_recipe"] == "P+CH+E+Y":
            local_mechanism = "LOCAL_BROADER_CHAIN_CONTIGUOUS_SUFFIX_REDUCTION"
            local_evidence = suffix_clause["global_running_event_id"]
            support_locality = "LOCAL_TARGET_REGISTER"
            residual = "Der Zielrahmen ist nur als Suffix einer längeren lokalen Drei-Aktions-Karte alt; die nackte Zielkarte bleibt unbelegt."
        else:
            rectangle = selected_by_card[card["evidence_strength_card_id"]]
            local_mechanism = "LOCAL_HEAD_ARGUMENT_RECTANGLE_PLUS_CROSS_REGISTER_PAIR_ORDER"
            local_evidence = f"{rectangle['selected_s_event_id']}|{rectangle['selected_chd_event_id']}|{rectangle['cross_register_pair_order_evidence_ids']}"
            support_locality = "LOCAL_HEAD_ARGUMENT_FACTORS__CROSS_PAIR_ORDER"
            residual = "S auf Y und CHD auf Y sind lokal; ihre gerichtete Verbindung bleibt aus einem anderen Register übernommen."
        upgrade_rows.append({
            "cross_frame_local_upgrade_card_id": f"G510-T{len(upgrade_rows) + 1:02d}",
            "source_gdt509_card_id": card["evidence_strength_card_id"],
            "target_matrix_cell_id": card["target_matrix_cell_id"],
            "target_register": card["target_register"],
            "target_action_recipe": card["target_action_recipe"],
            "working_translation_de": card["working_translation_de"],
            "old_gdt509_evidence_route": card["evidence_route"],
            "new_local_support_mechanism": local_mechanism,
            "new_support_locality": support_locality,
            "local_and_cross_evidence_ids": local_evidence,
            "residual_weakness_de": residual,
            "target_bridge_status": "LOCAL_FACTOR_BRIDGED_WORKING__TARGET_RECIPE_UNOBSERVED",
            "target_evidence_status_retained": card["target_evidence_status_retained"],
            "target_phrase_changed": "NO",
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        })

    if (len(rectangle_rows), len(witness_rows), len(upgrade_rows)) != (3, 6, 4):
        raise ValueError("GDT510 output cardinality drift")

    write_tsv(SUFFIX_OUT, suffix_row)
    write_tsv(RECTANGLES_OUT, rectangle_rows)
    write_tsv(WITNESSES_OUT, witness_rows)
    write_tsv(UPGRADES_OUT, upgrade_rows)

    readable = [
        "# GDT510 — Lokale Faktoren für die vier registerfremden Karten",
        "",
        f"Status: `{STATUS}`",
        "",
        "## Celestial `P+CH+E+Y`",
        "",
        f"`{suffix_clause['global_running_event_id']}` enthält das Ziel als exakten zusammenhängenden Suffix in Position {suffix_start + 1}–{suffix_start + len(target_tokens)}:",
        "",
        f"`{suffix_clause['component_recipe']}` → entferne Präfix `{'+'.join(removed_prefix)}` → `{pch_target['target_action_recipe']}`.",
        "",
        f"> {pch_target['working_translation_de']}",
        "",
        "## Drei lokale `S`/`CHD`-Rechtecke",
        "",
        "| Register | S-auf-Y | CHD-auf-Y | Kombinationen | ausgewählte Zeugen |",
        "|---|---:|---:|---:|---|",
    ]
    for row in rectangle_rows:
        readable.append(
            f"| {row['target_register']} | {row['local_s_on_y_event_count']} | {row['local_chd_on_y_event_count']} | "
            f"{row['local_s_chd_y_candidate_pair_count']} | `{row['selected_s_event_id']}` + `{row['selected_chd_event_id']}` |"
        )
    readable.extend([
        "",
        "Die lokale Rechteckbrücke liefert beide Handlungsköpfe auf demselben Argumenttyp `Y`. Die Richtung `S>CHD` bleibt durch den alten registerübergreifenden Träger `G407-E1883` verankert.",
        "",
        "## Grenze",
        "",
        "Keine der vier nackten Zielkarten wird beobachtet. Die Suffix- und Rechteckfaktoren erklären nur lokale Komponierbarkeit; alle vier Arbeitsübersetzungen und `COMPOSED_WORKING`-Labels bleiben unverändert.",
    ])
    READABLE_OUT.write_text("\n".join(readable) + "\n", encoding="utf-8")

    result = {
        "status": STATUS,
        "cross_frame_target_cards": len(cross_cards),
        "celestial_pch_local_contiguous_suffix_carriers": len(suffix_row),
        "schd_local_head_argument_rectangles": len(rectangle_rows),
        "schd_local_s_on_y_events": sum(int(row["local_s_on_y_event_count"]) for row in rectangle_rows),
        "schd_local_chd_on_y_events": sum(int(row["local_chd_on_y_event_count"]) for row in rectangle_rows),
        "schd_local_candidate_head_pairs": sum(int(row["local_s_chd_y_candidate_pair_count"]) for row in rectangle_rows),
        "selected_local_head_witnesses": len(witness_rows),
        "upgraded_target_cards": len(upgrade_rows),
        "all_eleven_pair_targets_now_have_some_local_support": 1,
        "schd_cards_still_using_cross_register_pair_order": len(rectangle_rows),
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
