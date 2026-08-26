#!/usr/bin/env python3
"""Rank the actual local linkage behind GDT510's three S+CHD+Y rectangles."""

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
BASE = ROOT / "experiments/yolo/gdt511_schd_local_linkage_strength_atlas"
ART = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G436 = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts"
G507 = ROOT / "experiments/yolo/gdt507_contextual_pair_argument_bridge_atlas/artifacts"
G510 = ROOT / "experiments/yolo/gdt510_four_cross_frame_local_factor_bridges/artifacts"

CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
STREAM_IN = G436 / "gdt436_4576_oracle_free_stream_readings.tsv"
BENCHMARK_IN = G507 / "gdt507_13_adjacent_event_same_argument_bridges.tsv"
RECTANGLES_IN = G510 / "gdt510_3_schd_local_head_argument_rectangles.tsv"
UPGRADES_IN = G510 / "gdt510_4_cross_frame_target_local_upgrade_cards.tsv"

CANDIDATES_OUT = ART / "gdt511_62_schd_local_linkage_candidates.tsv"
CARDS_OUT = ART / "gdt511_3_register_linkage_strength_cards.tsv"
CORRIDORS_OUT = ART / "gdt511_88_selected_link_corridor_events.tsv"
BENCHMARK_OUT = ART / "gdt511_1_gdt507_immediate_bridge_benchmark.tsv"
READABLE_OUT = ART / "GDT511_SCHD_LOCAL_LINKAGE_STRENGTH_ATLAS.md"
RESULT_OUT = ART / "gdt511_result.json"

STATUS = "SOURCE_SAME_STATEMENT__PHARMA_SAME_OWNER_PAGE__CELESTIAL_SAME_PAGE__ZERO_IMMEDIATE_OR_Y_CONTINUOUS"
GUARD = "LINKAGE_STRENGTH_ONLY__LOCAL_HEAD_RECTANGLES_NOT_PROMOTED_TO_LOCAL_PAIR"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def y_mode(row: dict[str, str]) -> str | None:
    explicit = [] if row["explicit_argument_roots"] == "NONE" else row["explicit_argument_roots"].split("|")
    if "Y" in explicit:
        return "EXPLICIT_Y"
    if row["inherited_argument_root"] == "Y":
        return "INHERITED_Y"
    return None


def event_number(event_id: str) -> int:
    return int(event_id.rsplit("E", 1)[1])


def collapse(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if not result or result[-1] != value:
            result.append(value)
    return result


def frame_atoms(row: dict[str, str], head: str) -> list[str]:
    atoms = row["component_recipe"].split("+")
    atoms.remove(head)
    if y_mode(row) == "EXPLICIT_Y":
        atoms.remove("Y")
    return atoms


def locality_tier(candidate: dict[str, object]) -> str:
    if candidate["s_before_chd"] != "YES":
        return "R_REVERSE_CHD_BEFORE_S"
    if candidate["same_statement"] == "YES":
        return "A_LONG_SAME_STATEMENT_OWNER_PAGE"
    if candidate["same_owner"] == "YES" and candidate["same_page"] == "YES":
        return "B_LONG_SAME_OWNER_PAGE"
    if candidate["same_page"] == "YES":
        return "C_LONG_SAME_PAGE_CROSS_OWNER"
    return "D_REGISTER_ONLY_CROSS_PAGE"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES_IN)
    stream = read_tsv(STREAM_IN)
    benchmark = read_tsv(BENCHMARK_IN)
    rectangles = read_tsv(RECTANGLES_IN)
    upgrades = read_tsv(UPGRADES_IN)
    if (len(clauses), len(stream), len(benchmark), len(rectangles), len(upgrades)) != (4576, 4576, 13, 3, 4):
        raise ValueError("GDT416/GDT436/GDT507/GDT510 source drift")

    stream_position = {row["event_id"]: index for index, row in enumerate(stream)}
    rectangle_by_card = {row["source_gdt509_card_id"]: row for row in rectangles}
    targets = sorted(
        (row for row in upgrades if row["target_action_recipe"] == "S+CHD+Y"),
        key=lambda row: row["target_register"],
    )
    if len(targets) != 3:
        raise ValueError("expected three GDT510 S+CHD+Y targets")

    candidates: list[dict[str, object]] = []
    cards: list[dict[str, object]] = []
    corridors: list[dict[str, object]] = []
    for target in targets:
        register = target["target_register"]
        source_rectangle = rectangle_by_card[target["source_gdt509_card_id"]]
        s_events = [row for row in clauses if row["register"] == register and row["explicit_action_roots"] == "S" and y_mode(row)]
        chd_events = [row for row in clauses if row["register"] == register and row["explicit_action_roots"] == "CHD" and y_mode(row)]
        register_candidates: list[dict[str, object]] = []
        for s_event in s_events:
            for chd_event in chd_events:
                s_id = s_event["global_running_event_id"]
                chd_id = chd_event["global_running_event_id"]
                s_position = stream_position[s_id]
                chd_position = stream_position[chd_id]
                low, high = sorted((s_position, chd_position))
                interval = stream[low : high + 1]
                after_values = [row["active_argument_after"] for row in interval]
                argument_runs = collapse(after_values)
                s_before = s_position < chd_position
                same_page = s_event["physical_page"] == chd_event["physical_page"]
                same_owner = s_event["owner_de"] == chd_event["owner_de"]
                same_statement = s_event["global_statement_id"] == chd_event["global_statement_id"]
                gap = abs(chd_position - s_position) - 1
                uninterrupted_y = all(value == "Y" for value in after_values)
                immediate_same_y = s_before and gap == 0 and same_statement and same_owner and same_page and uninterrupted_y
                gdt507_grade = immediate_same_y and y_mode(s_event) == y_mode(chd_event) == "INHERITED_Y"
                candidate = {
                    "linkage_candidate_id": "PENDING",
                    "source_gdt510_rectangle_id": source_rectangle["local_head_argument_rectangle_id"],
                    "source_gdt510_card_id": target["source_gdt509_card_id"],
                    "target_matrix_cell_id": target["target_matrix_cell_id"],
                    "target_register": register,
                    "target_action_recipe": target["target_action_recipe"],
                    "s_event_id": s_id,
                    "chd_event_id": chd_id,
                    "s_component_recipe": s_event["component_recipe"],
                    "chd_component_recipe": chd_event["component_recipe"],
                    "s_y_mode": y_mode(s_event),
                    "chd_y_mode": y_mode(chd_event),
                    "s_frame_atoms": "+".join(frame_atoms(s_event, "S")) if frame_atoms(s_event, "S") else "NONE",
                    "chd_frame_atoms": "+".join(frame_atoms(chd_event, "CHD")) if frame_atoms(chd_event, "CHD") else "NONE",
                    "s_before_chd": "YES" if s_before else "NO",
                    "intervening_event_count": gap,
                    "same_page": "YES" if same_page else "NO",
                    "same_owner": "YES" if same_owner else "NO",
                    "same_statement": "YES" if same_statement else "NO",
                    "corridor_event_count": len(interval),
                    "corridor_page_count": len({row["physical_page"] for row in interval}),
                    "corridor_owner_count": len({row["owner_de"] for row in interval}),
                    "corridor_statement_count": len({row["statement_id"] for row in interval}),
                    "corridor_argument_after_roots": "|".join(sorted(set(after_values))),
                    "corridor_argument_run_trace": ">".join(argument_runs),
                    "corridor_argument_state_change_count": len(argument_runs) - 1,
                    "corridor_active_y_event_count": sum(value == "Y" for value in after_values),
                    "corridor_non_y_event_count": sum(value != "Y" for value in after_values),
                    "active_y_uninterrupted": "YES" if uninterrupted_y else "NO",
                    "immediate_same_statement_same_y": "YES" if immediate_same_y else "NO",
                    "gdt507_grade_immediate_shared_inherited_argument": "YES" if gdt507_grade else "NO",
                    "locality_tier": "PENDING",
                    "guard": GUARD,
                }
                candidate["locality_tier"] = locality_tier(candidate)
                register_candidates.append(candidate)

        register_candidates.sort(key=lambda row: (event_number(str(row["s_event_id"])), event_number(str(row["chd_event_id"]))))
        for candidate in register_candidates:
            candidate["linkage_candidate_id"] = f"G511-L{len(candidates) + 1:03d}"
            candidates.append(candidate)

        ordered = [row for row in register_candidates if row["s_before_chd"] == "YES"]
        if not ordered:
            raise ValueError(f"no ordered local rectangles for {register}")
        selected = min(
            ordered,
            key=lambda row: (
                row["same_statement"] != "YES",
                row["same_owner"] != "YES",
                row["same_page"] != "YES",
                int(row["intervening_event_count"]),
                int(row["corridor_non_y_event_count"]),
                str(row["s_event_id"]),
                str(row["chd_event_id"]),
            ),
        )

        within_forward = 0
        within_reverse = 0
        for clause in clauses:
            if clause["register"] != register:
                continue
            actions = [] if clause["explicit_action_roots"] == "NONE" else clause["explicit_action_roots"].split("|")
            for left_index, left in enumerate(actions):
                for right in actions[left_index + 1 :]:
                    within_forward += (left, right) == ("S", "CHD")
                    within_reverse += (left, right) == ("CHD", "S")

        card_id = f"G511-C{len(cards) + 1:02d}"
        card = {
            "register_linkage_strength_card_id": card_id,
            "source_gdt510_rectangle_id": source_rectangle["local_head_argument_rectangle_id"],
            "source_gdt510_card_id": target["source_gdt509_card_id"],
            "target_matrix_cell_id": target["target_matrix_cell_id"],
            "target_register": register,
            "target_action_recipe": target["target_action_recipe"],
            "working_translation_de": target["working_translation_de"],
            "local_rectangle_candidate_count": len(register_candidates),
            "ordered_s_before_chd_candidate_count": len(ordered),
            "reverse_chd_before_s_candidate_count": len(register_candidates) - len(ordered),
            "ordered_same_page_count": sum(row["same_page"] == "YES" for row in ordered),
            "ordered_same_owner_count": sum(row["same_owner"] == "YES" for row in ordered),
            "ordered_same_statement_count": sum(row["same_statement"] == "YES" for row in ordered),
            "ordered_immediate_count": sum(int(row["intervening_event_count"]) == 0 for row in ordered),
            "ordered_zero_or_one_gap_count": sum(int(row["intervening_event_count"]) <= 1 for row in ordered),
            "ordered_uninterrupted_y_count": sum(row["active_y_uninterrupted"] == "YES" for row in ordered),
            "gdt507_grade_bridge_count": sum(row["gdt507_grade_immediate_shared_inherited_argument"] == "YES" for row in ordered),
            "target_register_within_event_s_before_chd_count": within_forward,
            "target_register_within_event_chd_before_s_count": within_reverse,
            "selected_linkage_candidate_id": selected["linkage_candidate_id"],
            "selected_linkage_tier": selected["locality_tier"],
            "selected_s_event_id": selected["s_event_id"],
            "selected_chd_event_id": selected["chd_event_id"],
            "selected_intervening_event_count": selected["intervening_event_count"],
            "selected_corridor_statement_count": selected["corridor_statement_count"],
            "selected_corridor_owner_count": selected["corridor_owner_count"],
            "selected_corridor_argument_run_trace": selected["corridor_argument_run_trace"],
            "selected_corridor_non_y_event_count": selected["corridor_non_y_event_count"],
            "gdt510_selected_s_event_id": source_rectangle["selected_s_event_id"],
            "gdt510_selected_chd_event_id": source_rectangle["selected_chd_event_id"],
            "cross_register_pair_order_event_id": source_rectangle["cross_register_pair_order_evidence_ids"],
            "linkage_reading_de": (
                "Beide Köpfe liegen in derselben Anweisung, aber nicht unmittelbar und nicht unter durchgehendem Y-Zustand."
                if selected["same_statement"] == "YES"
                else "Beide Köpfe liegen beim selben Besitzer auf derselben Seite, aber nicht in derselben Anweisung oder unter durchgehendem Y-Zustand."
                if selected["same_owner"] == "YES"
                else "Beide Köpfe liegen auf derselben Seite, aber bei verschiedenen Besitzern und nicht unter durchgehendem Y-Zustand."
            ),
            "linkage_status": "LOCAL_HEAD_INVENTORY_LINK_ONLY__CROSS_REGISTER_PAIR_ORDER_RETAINED",
            "target_recipe_observed_exactly": "NO",
            "target_phrase_changed": "NO",
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        }
        cards.append(card)

        left_position = stream_position[str(selected["s_event_id"])]
        right_position = stream_position[str(selected["chd_event_id"])]
        selected_interval = stream[left_position : right_position + 1]
        for offset, row in enumerate(selected_interval):
            event_id = row["event_id"]
            endpoint = "S_ENDPOINT" if event_id == selected["s_event_id"] else "CHD_ENDPOINT" if event_id == selected["chd_event_id"] else "INTERVENING"
            corridors.append({
                "selected_corridor_event_id": f"G511-E{len(corridors) + 1:03d}",
                "register_linkage_strength_card_id": card_id,
                "target_register": register,
                "selected_linkage_candidate_id": selected["linkage_candidate_id"],
                "corridor_offset": offset,
                "corridor_endpoint_role": endpoint,
                "event_id": event_id,
                "statement_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "owner_de": row["owner_de"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "explicit_action_roots": row["explicit_action_roots"],
                "explicit_argument_roots": row["explicit_argument_roots"],
                "inherited_argument_root": row["inherited_argument_root"],
                "active_argument_before": row["active_argument_before"],
                "active_argument_after": row["active_argument_after"],
                "active_argument_after_is_y": "YES" if row["active_argument_after"] == "Y" else "NO",
                "state_matches_reference": row["state_matches_reference"],
                "guard": GUARD,
            })

    if (len(candidates), len(cards), len(corridors)) != (62, 3, 88):
        raise ValueError(f"GDT511 cardinality drift: {len(candidates)}, {len(cards)}, {len(corridors)}")

    benchmark_row = [{
        "benchmark_card_id": "G511-B01",
        "source_gdt507_adjacent_bridge_count": len(benchmark),
        "source_gdt507_ordered_pairs": "|".join(sorted({row["ordered_action_pair"] for row in benchmark})),
        "source_gdt507_all_stream_consecutive": "YES" if all(row["stream_ordinals_consecutive"] == "YES" for row in benchmark) else "NO",
        "source_gdt507_all_same_statement_owner": "YES" if all(row["global_statement_id"] and row["owner_de"] for row in benchmark) else "NO",
        "source_gdt507_all_shared_inherited_argument": "YES" if all(row["shared_inherited_argument_root"] != "NONE" for row in benchmark) else "NO",
        "gdt511_schd_ordered_rectangle_count": sum(int(row["ordered_s_before_chd_candidate_count"]) for row in cards),
        "gdt511_schd_same_statement_count": sum(int(row["ordered_same_statement_count"]) for row in cards),
        "gdt511_schd_stream_consecutive_count": sum(int(row["ordered_immediate_count"]) for row in cards),
        "gdt511_schd_uninterrupted_y_count": sum(int(row["ordered_uninterrupted_y_count"]) for row in cards),
        "gdt511_gdt507_grade_bridge_count": sum(int(row["gdt507_grade_bridge_count"]) for row in cards),
        "comparison_status": "NO_SCHD_LINK_MATCHES_GDT507_IMMEDIATE_SHARED_ARGUMENT_GRADE",
        "guard": GUARD,
    }]

    write_tsv(CANDIDATES_OUT, candidates)
    write_tsv(CARDS_OUT, cards)
    write_tsv(CORRIDORS_OUT, corridors)
    write_tsv(BENCHMARK_OUT, benchmark_row)

    readable = [
        "# GDT511 — Stärke der lokalen `S+CHD+Y`-Verknüpfungen",
        "",
        f"Status: `{STATUS}`",
        "",
        "| Register | Rechtecke | S→CHD | gleiche Seite | gleicher Besitzer | gleiche Anweisung | stärkster lokaler Griff | Abstand |",
        "|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    for card in cards:
        readable.append(
            f"| {card['target_register']} | {card['local_rectangle_candidate_count']} | {card['ordered_s_before_chd_candidate_count']} | "
            f"{card['ordered_same_page_count']} | {card['ordered_same_owner_count']} | {card['ordered_same_statement_count']} | "
            f"`{card['selected_s_event_id']}→{card['selected_chd_event_id']}` | {card['selected_intervening_event_count']} |"
        )
    readable.extend([
        "",
        "Keines der 46 geordneten Rechtecke ist unmittelbar oder hält `Y` durch den ganzen Korridor aktiv. In keinem der drei Zielregister steht `S>CHD` innerhalb einer Karte. Damit erreicht keiner der lokalen Griffe die unmittelbare, gleichargumentige GDT507-Stufe.",
        "",
        "## Ausgewählte Korridore",
        "",
    ])
    for card in cards:
        readable.append(
            f"- **{card['target_register']}:** `{card['selected_s_event_id']}→{card['selected_chd_event_id']}`, "
            f"{card['selected_intervening_event_count']} Zwischenkarten; Argumentlauf "
            f"`{card['selected_corridor_argument_run_trace']}`. {card['linkage_reading_de']}"
        )
    readable.extend([
        "",
        "## Konsequenz",
        "",
        "Die GDT510-Rechtecke bleiben nützliche lokale Kopf-Inventare, aber keine lokalen Kontextpaar-Zeugen. Source ist stärker als Pharma, Pharma stärker als Celestial. Die gerichtete Komposition bleibt bei `G407-E1883`; Zielrezept, Arbeitsübersetzungen und Wurzelwerte bleiben unverändert.",
    ])
    READABLE_OUT.write_text("\n".join(readable) + "\n", encoding="utf-8")

    result = {
        "status": STATUS,
        "target_register_cards": len(cards),
        "local_rectangle_candidates": len(candidates),
        "ordered_s_before_chd_candidates": sum(int(row["ordered_s_before_chd_candidate_count"]) for row in cards),
        "reverse_chd_before_s_candidates": sum(int(row["reverse_chd_before_s_candidate_count"]) for row in cards),
        "ordered_same_page_candidates": sum(int(row["ordered_same_page_count"]) for row in cards),
        "ordered_same_owner_candidates": sum(int(row["ordered_same_owner_count"]) for row in cards),
        "ordered_same_statement_candidates": sum(int(row["ordered_same_statement_count"]) for row in cards),
        "ordered_immediate_candidates": sum(int(row["ordered_immediate_count"]) for row in cards),
        "ordered_zero_or_one_gap_candidates": sum(int(row["ordered_zero_or_one_gap_count"]) for row in cards),
        "ordered_uninterrupted_y_candidates": sum(int(row["ordered_uninterrupted_y_count"]) for row in cards),
        "target_register_within_event_s_before_chd": sum(int(row["target_register_within_event_s_before_chd_count"]) for row in cards),
        "gdt507_grade_bridges": sum(int(row["gdt507_grade_bridge_count"]) for row in cards),
        "selected_corridor_events": len(corridors),
        "source_linkage_tier": next(row["selected_linkage_tier"] for row in cards if row["target_register"] == "SOURCE_SECTION_T"),
        "pharma_linkage_tier": next(row["selected_linkage_tier"] for row in cards if row["target_register"] == "PHARMA"),
        "celestial_linkage_tier": next(row["selected_linkage_tier"] for row in cards if row["target_register"] == "CELESTIAL"),
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
