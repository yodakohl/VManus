#!/usr/bin/env python3
"""Recover broader old directional support for the four GDT502 open edges."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt503_four_open_edge_long_chain_recovery"
ART = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G421 = ROOT / "experiments/yolo/gdt421_ordered_action_pair_slot_license/artifacts"
G422 = ROOT / "experiments/yolo/gdt422_multi_action_chain_pair_reduction/artifacts"
G425 = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts"
G426 = ROOT / "experiments/yolo/gdt426_typed_action_family_prediction/artifacts"
G427 = ROOT / "experiments/yolo/gdt427_typed_prediction_specificity_repair/artifacts"
G444 = ROOT / "experiments/yolo/gdt444_focus_separated_action_pair_atlas/artifacts"
G502 = ROOT / "experiments/yolo/gdt502_supported_frontier_comparison_cards/artifacts"

OPEN_IN = G502 / "gdt502_4_open_frontier_cards.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
PAIR421_IN = G421 / "gdt421_81_ordered_pair_profiles.tsv"
GAPS422_IN = G422 / "gdt422_11_pair_gap_adjudications.tsv"
ADJ425_IN = G425 / "gdt425_649_adjacent_pair_portability.tsv"
PAIR426_IN = G426 / "gdt426_81_exact_action_pair_status.tsv"
LEAVEOUT427_IN = G427 / "gdt427_15_singleton_pair_leaveout.tsv"
SEP_SUMMARY444_IN = G444 / "gdt444_44_pair_separator_summary.tsv"
SEP_MATRIX444_IN = G444 / "gdt444_484_focus_separated_pair_matrix.tsv"

CARDS_OUT = ART / "gdt503_4_corrected_open_edge_cards.tsv"
PAIR_OUT = ART / "gdt503_2_directional_pair_support_summaries.tsv"
WITNESS_OUT = ART / "gdt503_2_long_chain_clause_witnesses.tsv"
PEER_OUT = ART / "gdt503_8_peer_pair_analogies.tsv"
REVERSE_OUT = ART / "gdt503_2_reverse_order_contrasts.tsv"
SEPARATOR_OUT = ART / "gdt503_11_ch_chd_separator_routes.tsv"
READABLE_OUT = ART / "GDT503_FOUR_OPEN_EDGE_RECOVERY_CARDS.md"
RESULT_OUT = ART / "gdt503_result.json"

TARGET_PAIRS = ("CH>CHD", "CH>OK")
STATUS = "BOTH_OPEN_RECIPES_HAVE_ONE_OLD_DIRECTIONAL_CHAIN__DIRECT_AND_SEPARATOR_SUPPORT_DISTINGUISHED"
GUARD = "BROADER_CHAIN_SUPPORT_ONLY__TWO_HEAD_TARGETS_REMAIN_COMPOSED__NO_SURFACE_PREDICTION"


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


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _open_fields, open_cards = read_tsv(OPEN_IN)
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _p421_fields, pairs421 = read_tsv(PAIR421_IN)
    _gap_fields, gaps422 = read_tsv(GAPS422_IN)
    _adj_fields, adjacent425 = read_tsv(ADJ425_IN)
    _p426_fields, pairs426 = read_tsv(PAIR426_IN)
    _leaveout_fields, leaveout427 = read_tsv(LEAVEOUT427_IN)
    _sep_summary_fields, sep_summary444 = read_tsv(SEP_SUMMARY444_IN)
    _sep_matrix_fields, sep_matrix444 = read_tsv(SEP_MATRIX444_IN)
    if (len(open_cards), len(clauses), len(pairs421), len(gaps422), len(adjacent425), len(pairs426), len(leaveout427), len(sep_summary444), len(sep_matrix444)) != (4, 4576, 81, 11, 649, 81, 15, 44, 484):
        raise ValueError("source count drift")

    pair421_by_key = {row["ordered_pair"].replace("+", ">", 1): row for row in pairs421}
    pair426_by_key = {row["ordered_pair"]: row for row in pairs426}
    gap_by_pair = {row["missing_pair"].replace("+", ">", 1): row for row in gaps422}
    adjacent_by_pair: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in adjacent425:
        adjacent_by_pair[row["ordered_pair"]].append(row)
    leaveout_by_pair = {row["ordered_pair"]: row for row in leaveout427}
    sep_summary_by_pair = {row["direct_pair"]: row for row in sep_summary444}
    separators_by_pair: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sep_matrix444:
        separators_by_pair[row["direct_pair"]].append(row)
    clause_by_event = {row["global_running_event_id"]: row for row in clauses}

    pair_summaries: list[dict[str, object]] = []
    long_witnesses: list[dict[str, object]] = []
    peer_rows: list[dict[str, object]] = []
    reverse_rows: list[dict[str, object]] = []
    separator_rows: list[dict[str, object]] = []
    for pair_key in TARGET_PAIRS:
        left, right = pair_key.split(">")
        old_two_head = pair421_by_key[pair_key]
        broad = pair426_by_key[pair_key]
        gap = gap_by_pair[pair_key]
        event_ids = gap["global_running_event_ids"].split("|")
        if len(event_ids) != 1 or int(gap["event_count"]) != 1:
            raise ValueError(f"expected singleton long-chain witness: {pair_key}")
        clause = clause_by_event[event_ids[0]]
        direct_rows = adjacent_by_pair[pair_key]
        direct_component_adjacency = bool(direct_rows)
        if pair_key == "CH>CHD":
            if direct_component_adjacency or gap["between_atoms"] == "NONE":
                raise ValueError("CH>CHD separator distinction drift")
            support_class = "ORDERED_ACTION_CHAIN_WITH_VISIBLE_SEPARATOR"
            support_reading = "NEHMEN steht vor BEARBEITEN; EE+D_ADDR trennt die Pakete sichtbar."
        else:
            if len(direct_rows) != 1 or gap["between_atoms"] != "NONE":
                raise ValueError("CH>OK direct distinction drift")
            support_class = "EMBEDDED_DIRECT_COMPONENT_ADJACENCY"
            support_reading = "NEHMEN steht direkt vor SETZEN innerhalb einer längeren Drei-Handlungs-Karte."
        leaveout = leaveout_by_pair[pair_key]
        separators = separators_by_pair[pair_key]
        separator_summary = sep_summary_by_pair.get(pair_key)
        reverse_key = f"{right}>{left}"
        reverse = pair426_by_key[reverse_key]

        pair_summaries.append({
            "pair_summary_id": f"G503-P{len(pair_summaries) + 1:02d}",
            "ordered_action_pair": pair_key,
            "portable_pair_reading_de": old_two_head["ordered_reading_de"],
            "gdt421_exact_two_head_status": old_two_head["status"],
            "gdt421_exact_two_head_event_count": old_two_head["event_count"],
            "gdt421_exact_two_head_recipe_type_count": old_two_head["exact_recipe_type_count"],
            "gdt426_broad_action_chain_status": broad["pair_status"],
            "gdt426_broad_action_chain_event_count": broad["event_count"],
            "gdt426_broad_action_chain_pages": broad["pages"],
            "gdt422_long_recipe": gap["component_recipe"],
            "gdt422_action_chain": gap["action_chain"],
            "gdt422_between_atoms": gap["between_atoms"],
            "gdt422_repair_rule": gap["repair_rule"],
            "long_chain_event_id": event_ids[0],
            "long_chain_page": gap["pages"],
            "long_chain_register": gap["registers"],
            "direct_component_adjacency": "YES" if direct_component_adjacency else "NO",
            "direct_adjacency_gdt425_status": direct_rows[0]["portability_status"] if direct_rows else "NONE",
            "corrected_support_class": support_class,
            "corrected_support_reading_de": support_reading,
            "gdt427_leaveout_prediction": leaveout["prediction"],
            "gdt427_typed_transition": leaveout["typed_transition"],
            "peer_transition_other_support_pages": leaveout["other_support_pages"],
            "reverse_order_pair": reverse_key,
            "reverse_order_event_count": reverse["event_count"],
            "reverse_order_pages": reverse["pages"],
            "accepted_single_separator_count": separator_summary["accepted_separator_count"] if separator_summary else "NOT_APPLICABLE_DIRECT_LOCAL_PAIR",
            "direct_pair_remains_unlicensed_after_separator_test": separator_summary["direct_pair_remains_unlicensed"] if separator_summary else "NOT_APPLICABLE_DIRECT_LOCAL_PAIR",
            "target_two_head_recipe_observed": "NO",
            "target_evidence_status_retained": "COMPOSED_WORKING",
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        })
        long_witnesses.append({
            "long_chain_witness_id": f"G503-W{len(long_witnesses) + 1:02d}",
            "ordered_action_pair": pair_key,
            "global_running_event_id": event_ids[0],
            "physical_page": clause["physical_page"],
            "register": clause["register"],
            "surface": clause["surface"],
            "component_recipe": clause["component_recipe"],
            "explicit_action_roots": clause["explicit_action_roots"],
            "between_atoms": gap["between_atoms"],
            "repair_rule": gap["repair_rule"],
            "imperative_clause_de": clause["imperative_clause_de"],
            "owner_local_atom_reading_de": clause["owner_local_atom_reading_de"],
            "portable_back_projection_de": clause["portable_back_projection_de"],
            "gdt416_roundtrip_exact": clause["roundtrip_exact"],
            "direct_component_adjacency": "YES" if direct_component_adjacency else "NO",
            "guard": GUARD,
        })
        for peer in pairs426:
            if peer["left_class"] == broad["left_class"] and peer["right_class"] == broad["right_class"] and peer["ordered_pair"] != pair_key:
                peer_rows.append({
                    "peer_analogy_id": f"G503-A{len(peer_rows) + 1:02d}",
                    "target_ordered_pair": pair_key,
                    "target_typed_transition": f'{broad["left_class"]}>{broad["right_class"]}',
                    "peer_ordered_pair": peer["ordered_pair"],
                    "peer_event_count": peer["event_count"],
                    "peer_page_count": peer["page_count"],
                    "peer_pages": peer["pages"],
                    "peer_surface_count": peer["surface_count"],
                    "peer_pair_status": peer["pair_status"],
                    "same_typed_transition": "YES",
                    "target_pair_promoted": "NO",
                    "guard": GUARD,
                })
        reverse_rows.append({
            "reverse_contrast_id": f"G503-R{len(reverse_rows) + 1:02d}",
            "target_ordered_pair": pair_key,
            "target_broad_chain_event_count": broad["event_count"],
            "reverse_ordered_pair": reverse_key,
            "reverse_broad_chain_event_count": reverse["event_count"],
            "reverse_page_count": reverse["page_count"],
            "reverse_pages": reverse["pages"],
            "directional_reading_de": f'{left} vor {right}; Umkehrung {reverse_key} hat {reverse["event_count"]} alte Aktionsketten.',
            "order_collapsed": "NO",
            "guard": GUARD,
        })
        if pair_key == "CH>CHD":
            for route in separators:
                separator_rows.append({
                    "separator_route_id": f"G503-S{len(separator_rows) + 1:02d}",
                    "target_ordered_pair": pair_key,
                    "separator_focus": route["separator_focus"],
                    "separated_recipe": route["separated_recipe"],
                    "separated_factor_gate_status": route["separated_factor_gate_status"],
                    "separator_decision": route["separator_decision"],
                    "scope_selector_rules": route["scope_selector_rules"],
                    "portable_factor_rules": route["portable_factor_rules"],
                    "ordered_literal_reading_de": route["ordered_literal_reading_de"],
                    "direct_pair_promoted": route["direct_pair_promoted"],
                    "surface_or_occurrence_prediction": route["surface_or_occurrence_prediction"],
                    "guard": GUARD,
                })

    card_rows: list[dict[str, object]] = []
    summary_by_pair = {str(row["ordered_action_pair"]): row for row in pair_summaries}
    for source in open_cards:
        pair_key = source["ordered_action_pair"].replace("+", ">", 1)
        summary = summary_by_pair[pair_key]
        card_rows.append({
            "corrected_open_card_id": f"G503-C{len(card_rows) + 1:02d}",
            "source_gdt502_open_card_id": source["open_card_id"],
            "target_matrix_cell_id": source["target_matrix_cell_id"],
            "target_action_recipe": source["target_action_recipe"],
            "target_register": source["target_register"],
            "target_portable_trace_de": source["target_portable_trace_de"],
            "target_owner_local_trace_de": source["target_owner_local_trace_de"],
            "target_current_default_phrase_de": source["target_current_default_phrase_de"],
            "ordered_action_pair": pair_key,
            "gdt421_two_head_event_count": summary["gdt421_exact_two_head_event_count"],
            "broader_old_chain_event_count": summary["gdt426_broad_action_chain_event_count"],
            "broader_old_chain_event_id": summary["long_chain_event_id"],
            "broader_old_chain_recipe": summary["gdt422_long_recipe"],
            "broader_old_chain_page": summary["long_chain_page"],
            "direct_component_adjacency": summary["direct_component_adjacency"],
            "corrected_support_class": summary["corrected_support_class"],
            "corrected_support_reading_de": summary["corrected_support_reading_de"],
            "assumption_retained": "YES",
            "target_two_head_recipe_observed": "NO",
            "target_current_phrase_changed": "NO",
            "target_evidence_status_retained": "COMPOSED_WORKING",
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        })

    write_tsv(CARDS_OUT, card_rows)
    write_tsv(PAIR_OUT, pair_summaries)
    write_tsv(WITNESS_OUT, long_witnesses)
    write_tsv(PEER_OUT, peer_rows)
    write_tsv(REVERSE_OUT, reverse_rows)
    write_tsv(SEPARATOR_OUT, separator_rows)

    lines = [
        "# GDT503 — die vier offenen Kanten besitzen alte Richtungssequenzen",
        "",
        f"Status: `{STATUS}`",
        "",
        "GDT421 fand kein eigenständiges Rezept mit genau diesen zwei Köpfen. Die",
        "breitere alte Kettenebene enthält jedoch jede Richtung einmal. Direkte",
        "Komponentennachbarschaft und sichtbare Slottrennung bleiben unterschieden.",
        "",
    ]
    for row in card_rows:
        witness = next(item for item in long_witnesses if item["ordered_action_pair"] == row["ordered_action_pair"])
        lines.extend([
            f'## {row["corrected_open_card_id"]} · `{row["target_action_recipe"]}` · {row["target_register"]}',
            "",
            f'- **Aktueller Satz:** {row["target_current_default_phrase_de"]}',
            f'- Korrigierte Stütze: `{row["corrected_support_class"]}` — {row["corrected_support_reading_de"]}',
            f'- Alter Träger: `{witness["component_recipe"]}` · {witness["physical_page"]} · {witness["imperative_clause_de"]}',
            f'- Eigenständiges Zwei-Kopf-Rezept beobachtet: **nein**; Annahme bleibt komponiert.',
            "",
        ])
    lines.extend([f"`{GUARD}`", ""])
    READABLE_OUT.write_text("\n".join(lines), encoding="utf-8")

    result = {
        "status": STATUS,
        "corrected_open_cards": len(card_rows),
        "target_pair_recipes": len(pair_summaries),
        "gdt421_exact_two_head_events": sum(int(row["gdt421_exact_two_head_event_count"]) for row in pair_summaries),
        "broader_old_directional_chain_events": sum(int(row["gdt426_broad_action_chain_event_count"]) for row in pair_summaries),
        "concrete_long_chain_clause_witnesses": len(long_witnesses),
        "direct_component_adjacency_pair_types": sum(row["direct_component_adjacency"] == "YES" for row in pair_summaries),
        "visible_separator_pair_types": sum(row["corrected_support_class"] == "ORDERED_ACTION_CHAIN_WITH_VISIBLE_SEPARATOR" for row in pair_summaries),
        "peer_pair_analogies": len(peer_rows),
        "peer_pair_analogy_events": sum(int(row["peer_event_count"]) for row in peer_rows),
        "reverse_order_contrasts": len(reverse_rows),
        "reverse_order_events": sum(int(row["reverse_broad_chain_event_count"]) for row in reverse_rows),
        "ch_chd_accepted_single_separator_routes": len(separator_rows),
        "all_separator_routes_keep_direct_pair_unpromoted": sum(row["direct_pair_promoted"] == "NO" for row in separator_rows),
        "gdt416_long_chain_roundtrips_exact": sum(row["gdt416_roundtrip_exact"] == "YES" for row in long_witnesses),
        "target_current_phrases_retained": sum(row["target_current_phrase_changed"] == "NO" for row in card_rows),
        "composed_labels_retained": sum(row["target_evidence_status_retained"] == "COMPOSED_WORKING" for row in card_rows),
        "open_assumptions_retained": sum(row["assumption_retained"] == "YES" for row in card_rows),
        "target_two_head_recipes_observed": sum(row["target_two_head_recipe_observed"] == "YES" for row in card_rows),
        "working_root_meaning_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
