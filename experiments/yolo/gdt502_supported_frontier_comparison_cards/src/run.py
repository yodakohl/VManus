#!/usr/bin/env python3
"""Publish one concrete old-clause comparison card for each supported GDT501 cell."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt502_supported_frontier_comparison_cards"
ART = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G501 = ROOT / "experiments/yolo/gdt501_old_value_frontier_partial_support_atlas/artifacts"

CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
RANKED_IN = G501 / "gdt501_50_ranked_frontier_cells.tsv"
CANDIDATE_IN = G501 / "gdt501_partial_subrecipe_candidates.tsv"
WITNESS_IN = G501 / "gdt501_exact_partial_recipe_witnesses.tsv"
PAIR_IN = G501 / "gdt501_ordered_action_pair_support.tsv"
CARDS_OUT = ART / "gdt502_46_supported_frontier_cards.tsv"
SELECTED_OUT = ART / "gdt502_46_selected_old_clause_witnesses.tsv"
OPEN_OUT = ART / "gdt502_4_open_frontier_cards.tsv"
CHANNEL_OUT = ART / "gdt502_support_channel_coverage.tsv"
FRAME_OUT = ART / "gdt502_5_frame_card_coverage.tsv"
READABLE_OUT = ART / "GDT502_FORTY_SIX_SUPPORTED_FRONTIER_COMPARISON_CARDS.md"
RESULT_OUT = ART / "gdt502_result.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
CHANNEL_ORDER = {
    "LOCAL_NEAR_ACTION_RECIPE": 0,
    "LOCAL_ACTION_PARTIAL_RECIPE": 1,
    "ORDERED_PAIR_TARGET_REGISTER": 2,
    "CROSS_NEAR_ACTION_RECIPE": 3,
    "ORDERED_PAIR_OTHER_REGISTER": 4,
    "CROSS_ACTION_PARTIAL_RECIPE": 5,
    "LOCAL_FRAME_BACKBONE_RECIPE": 6,
}
STATUS = "FORTY_SIX_SUPPORTED_FRONTIER_CARDS_HAVE_CONCRETE_OLD_CLAUSES__FOUR_OPEN_EDGES_RETAINED"
GUARD = "COMPARISON_CARD_ONLY__CURRENT_TARGET_PHRASE_AND_COMPOSED_STATUS_RETAINED"


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


def page_key(page: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", page)
    if match:
        return int(match.group(1)), 0 if match.group(2) == "r" else 1, int(match.group(3) or 0), page
    return 10**9, 0, 0, page


def select_phrase(rows: list[dict[str, str]]) -> tuple[str, int]:
    counts = Counter(row["imperative_clause_de"] for row in rows)
    return sorted(counts.items(), key=lambda item: (-item[1], len(item[0].split()), len(item[0]), item[0]))[0]


def clause_payload(rows: list[dict[str, str]]) -> dict[str, object]:
    selected, carriers = select_phrase(rows)
    pages = sorted({row["physical_page"] for row in rows}, key=page_key)
    return {
        "support_event_count": len(rows),
        "support_clause_form_count": len({row["imperative_clause_de"] for row in rows}),
        "selected_old_clause_de": selected,
        "selected_old_clause_carrier_count": carriers,
        "all_old_clauses_de": " || ".join(sorted({row["imperative_clause_de"] for row in rows})),
        "support_event_ids": "|".join(row["global_running_event_id"] for row in rows),
        "support_pages": "|".join(pages),
        "support_page_count": len(pages),
        "support_surfaces": "|".join(sorted({row["surface"] for row in rows})),
        "support_surface_count": len({row["surface"] for row in rows}),
        "support_roundtrip_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in rows) else "NO",
    }


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _ranked_fields, ranked = read_tsv(RANKED_IN)
    _candidate_fields, candidates = read_tsv(CANDIDATE_IN)
    _witness_fields, witnesses = read_tsv(WITNESS_IN)
    _pair_fields, pairs = read_tsv(PAIR_IN)
    if (len(clauses), len(ranked), len(candidates), len(witnesses), len(pairs)) != (4576, 50, 167, 285, 30):
        raise ValueError("GDT416/GDT501 source drift")
    supported = [row for row in ranked if row["frontier_support_tier"] != "D_ATOMIC_VALUES_ONLY"]
    open_rows = [row for row in ranked if row["frontier_support_tier"] == "D_ATOMIC_VALUES_ONLY"]
    if (len(supported), len(open_rows)) != (46, 4):
        raise ValueError("supported/open split drift")

    candidates_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    witnesses_by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    pair_by_target = {row["target_matrix_cell_id"]: row for row in pairs}
    clauses_by_recipe_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    pair_carrier_groups: dict[str, dict[tuple[str, str], list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in candidates:
        candidates_by_target[row["target_matrix_cell_id"]].append(row)
    for row in witnesses:
        witnesses_by_candidate[row["partial_candidate_id"]].append(row)
    for row in clauses:
        clauses_by_recipe_register[(row["component_recipe"], row["register"])].append(row)
        explicit_pair = row["explicit_action_roots"].replace("|", "+")
        if len(row["explicit_action_roots"].split("|")) == 2:
            pair_carrier_groups[explicit_pair][(row["component_recipe"], row["register"])].append(row)

    card_rows: list[dict[str, object]] = []
    selected_rows: list[dict[str, object]] = []
    for target in supported:
        target_id = target["source_matrix_cell_id"]
        options: list[dict[str, object]] = []
        for candidate in candidates_by_target[target_id]:
            candidate_witnesses = witnesses_by_candidate[candidate["partial_candidate_id"]]
            local = [row for row in candidate_witnesses if row["witness_relation"] == "SAME_REGISTER"]
            cross = [row for row in candidate_witnesses if row["witness_relation"] == "CROSS_REGISTER"]
            contains_action = candidate["contains_target_action_root"] == "YES"
            near = candidate["near_single_deletion"] == "YES"
            if local and contains_action:
                channel = "LOCAL_NEAR_ACTION_RECIPE" if near else "LOCAL_ACTION_PARTIAL_RECIPE"
                chosen_witness = local[0]
                options.append({"channel": channel, "candidate": candidate, "witness": chosen_witness})
            if cross and contains_action:
                channel = "CROSS_NEAR_ACTION_RECIPE" if near else "CROSS_ACTION_PARTIAL_RECIPE"
                chosen_witness = sorted(
                    cross,
                    key=lambda row: (-int(row["observed_event_count"]), -int(row["observed_clause_form_count"]), -int(row["observed_page_count"]), row["witness_register"]),
                )[0]
                options.append({"channel": channel, "candidate": candidate, "witness": chosen_witness})
            if local and not contains_action:
                options.append({"channel": "LOCAL_FRAME_BACKBONE_RECIPE", "candidate": candidate, "witness": local[0]})

        pair = pair_by_target.get(target_id)
        if pair and pair["pair_status"] == "PAIR_ATTESTED":
            channel = "ORDERED_PAIR_TARGET_REGISTER" if pair["pair_attested_in_target_register"] == "YES" else "ORDERED_PAIR_OTHER_REGISTER"
            groups = pair_carrier_groups[pair["ordered_action_pair"]]
            if not groups:
                raise ValueError(f"missing concrete pair carriers: {target_id}")
            group_key, group_rows = sorted(
                groups.items(),
                key=lambda item: (
                    0 if item[0][1] == target["register"] else 1,
                    len(item[0][0].split("+")),
                    -len(item[1]),
                    len({row["imperative_clause_de"] for row in item[1]}),
                    item[0][0],
                    item[0][1],
                ),
            )[0]
            options.append({"channel": channel, "pair": pair, "pair_group_key": group_key, "pair_group_rows": group_rows})
        if not options:
            raise ValueError(f"supported target lacks concrete option: {target_id}")

        def option_key(option: dict[str, object]) -> tuple[object, ...]:
            channel = str(option["channel"])
            if "candidate" in option:
                candidate = option["candidate"]
                witness = option["witness"]
                return (
                    CHANNEL_ORDER[channel],
                    -int(candidate["partial_component_count"]),
                    -int(witness["observed_event_count"]),
                    0 if candidate["contiguous_in_target"] == "YES" else 1,
                    candidate["partial_candidate_id"],
                    witness["witness_register"],
                )
            pair_group_rows = option["pair_group_rows"]
            pair_group_key = option["pair_group_key"]
            return (
                CHANNEL_ORDER[channel],
                -2,
                -len(pair_group_rows),
                0,
                pair_group_key[0],
                pair_group_key[1],
            )

        chosen = sorted(options, key=option_key)[0]
        channel = str(chosen["channel"])
        if "candidate" in chosen:
            candidate = chosen["candidate"]
            witness = chosen["witness"]
            support_recipe = witness["partial_recipe"]
            support_register = witness["witness_register"]
            source_rows = clauses_by_recipe_register[(support_recipe, support_register)]
            support_relation = witness["witness_relation"]
            support_candidate_id = candidate["partial_candidate_id"]
            target_removed_positions = candidate["removal_position_sets"]
            target_added_components = candidate["removed_token_sets"]
            ordered_pair = target["ordered_action_pair"]
            channel_basis = "EXACT_COMPLETE_GDT416_PARTIAL_RECIPE"
        else:
            pair = chosen["pair"]
            support_recipe, support_register = chosen["pair_group_key"]
            source_rows = chosen["pair_group_rows"]
            support_relation = "SAME_REGISTER" if support_register == target["register"] else "CROSS_REGISTER"
            support_candidate_id = "NONE"
            target_removed_positions = "NONE"
            target_added_components = "+".join(token for token in target["action_recipe"].split("+") if token not in ACTION_ROOTS) or "NONE"
            ordered_pair = pair["ordered_action_pair"]
            channel_basis = "EXACT_GDT416_CLAUSE_WITH_ATTESTED_GDT421_ORDERED_PAIR"
        payload = clause_payload(source_rows)
        card_id = f"G502-F{len(card_rows) + 1:02d}"
        card = {
            "comparison_card_id": card_id,
            "gdt501_frontier_priority_rank": target["frontier_priority_rank"],
            "gdt501_frontier_support_tier": target["frontier_support_tier"],
            "target_matrix_cell_id": target_id,
            "target_frame": target["frozen_frame"],
            "target_action_root": target["action_root"],
            "target_action_recipe": target["action_recipe"],
            "target_register": target["register"],
            "target_portable_trace_de": target["portable_component_trace_de"],
            "target_owner_local_trace_de": target["owner_local_component_trace_de"],
            "target_current_default_phrase_de": target["current_default_phrase_de"],
            "support_channel": channel,
            "support_channel_basis": channel_basis,
            "support_partial_candidate_id": support_candidate_id,
            "support_recipe": support_recipe,
            "support_register_relation": support_relation,
            "support_register": support_register,
            "support_component_count": len(support_recipe.split("+")),
            "target_component_count": target["component_count"],
            "target_removed_position_sets": target_removed_positions,
            "target_added_component_sets": target_added_components,
            "ordered_action_pair": ordered_pair,
            **payload,
            "target_current_phrase_changed": "NO",
            "target_evidence_status_retained": target["evidence_status_retained"],
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        }
        card_rows.append(card)
        selected_rows.append({
            "selected_witness_id": f"G502-W{len(selected_rows) + 1:02d}",
            "comparison_card_id": card_id,
            "target_matrix_cell_id": target_id,
            "support_channel": channel,
            "support_recipe": support_recipe,
            "support_register": support_register,
            "support_event_count": payload["support_event_count"],
            "support_event_ids": payload["support_event_ids"],
            "support_pages": payload["support_pages"],
            "support_surfaces": payload["support_surfaces"],
            "selected_old_clause_de": payload["selected_old_clause_de"],
            "selected_old_clause_carrier_count": payload["selected_old_clause_carrier_count"],
            "all_old_clauses_de": payload["all_old_clauses_de"],
            "support_roundtrip_exact": payload["support_roundtrip_exact"],
            "guard": GUARD,
        })

    open_cards: list[dict[str, object]] = []
    for row in open_rows:
        open_cards.append({
            "open_card_id": f"G502-O{len(open_cards) + 1:02d}",
            "gdt501_frontier_priority_rank": row["frontier_priority_rank"],
            "target_matrix_cell_id": row["source_matrix_cell_id"],
            "target_action_recipe": row["action_recipe"],
            "target_register": row["register"],
            "target_portable_trace_de": row["portable_component_trace_de"],
            "target_owner_local_trace_de": row["owner_local_component_trace_de"],
            "target_current_default_phrase_de": row["current_default_phrase_de"],
            "ordered_action_pair": row["ordered_action_pair"],
            "ordered_pair_old_event_count": row["ordered_pair_event_count"],
            "open_reason": "NO_EXACT_MULTIATOM_PARTIAL_AND_ORDERED_PAIR_UNATTESTED",
            "assumption_retained": "YES",
            "target_current_phrase_changed": "NO",
            "target_evidence_status_retained": row["evidence_status_retained"],
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        })

    write_tsv(CARDS_OUT, card_rows)
    write_tsv(SELECTED_OUT, selected_rows)
    write_tsv(OPEN_OUT, open_cards)

    channel_rows: list[dict[str, object]] = []
    for channel in sorted({str(row["support_channel"]) for row in card_rows}, key=lambda value: CHANNEL_ORDER[value]):
        group = [row for row in card_rows if row["support_channel"] == channel]
        channel_rows.append({
            "support_channel": channel,
            "card_count": len(group),
            "support_event_count": sum(int(row["support_event_count"]) for row in group),
            "support_page_union_count": len({page for row in group for page in str(row["support_pages"]).split("|")}),
            "same_register_card_count": sum(row["support_register_relation"] == "SAME_REGISTER" for row in group),
            "cross_register_card_count": sum(row["support_register_relation"] == "CROSS_REGISTER" for row in group),
            "all_roundtrips_exact": "YES" if all(row["support_roundtrip_exact"] == "YES" for row in group) else "NO",
            "all_target_phrases_retained": "YES",
        })
    write_tsv(CHANNEL_OUT, channel_rows)

    frame_rows: list[dict[str, object]] = []
    for frame in sorted({row["target_frame"] for row in card_rows} | {row["frozen_frame"] for row in open_rows}):
        closed = [row for row in card_rows if row["target_frame"] == frame]
        opened = [row for row in open_rows if row["frozen_frame"] == frame]
        frame_rows.append({
            "frozen_frame": frame,
            "supported_card_count": len(closed),
            "open_card_count": len(opened),
            "selected_old_clause_event_count": sum(int(row["support_event_count"]) for row in closed),
            "support_channel_count": len({row["support_channel"] for row in closed}),
            "all_target_phrases_retained": "YES",
        })
    write_tsv(FRAME_OUT, frame_rows)

    lines = [
        "# GDT502 — 46 konkrete Vergleichskarten der ehemaligen Restfront",
        "",
        f"Status: `{STATUS}`",
        "",
        "Jede gestützte GDT501-Zelle steht nun neben genau einer deterministisch",
        "gewählten alten Klausel. Teilrezept, Paar, Register, Events und Seiten",
        "bleiben sichtbar; die Zielphrase bleibt unverändert komponiert.",
        "",
        "## Die 46 Karten",
        "",
    ]
    for row in card_rows:
        lines.extend([
            f'### {row["comparison_card_id"]} · `{row["target_action_recipe"]}` · {row["target_register"]}',
            "",
            f'- **Aktueller Zielsatz:** {row["target_current_default_phrase_de"]}',
            f'- Alter Träger: `{row["support_recipe"]}` · {row["support_register"]} · `{row["support_channel"]}`.',
            f'- **Alte Klausel:** {row["selected_old_clause_de"]}',
            f'- Ergänzte Zielkomponenten: `{row["target_added_component_sets"]}`; alte Events: {row["support_event_count"]}; Seiten: `{row["support_pages"]}`.',
            "",
        ])
    lines.extend(["## Vier offene Kanten", ""])
    for row in open_cards:
        lines.append(f'- `{row["target_action_recipe"]}` · {row["target_register"]}: {row["target_current_default_phrase_de"]}')
    lines.extend(["", f"`{GUARD}`", ""])
    READABLE_OUT.write_text("\n".join(lines), encoding="utf-8")

    channels = Counter(str(row["support_channel"]) for row in card_rows)
    result = {
        "status": STATUS,
        "supported_comparison_cards": len(card_rows),
        "selected_old_clause_witnesses": len(selected_rows),
        "open_cards_retained": len(open_cards),
        "local_near_action_cards": channels["LOCAL_NEAR_ACTION_RECIPE"],
        "local_action_partial_cards": channels["LOCAL_ACTION_PARTIAL_RECIPE"],
        "ordered_pair_target_register_cards": channels["ORDERED_PAIR_TARGET_REGISTER"],
        "cross_near_action_cards": channels["CROSS_NEAR_ACTION_RECIPE"],
        "ordered_pair_other_register_cards": channels["ORDERED_PAIR_OTHER_REGISTER"],
        "cross_action_partial_cards": channels["CROSS_ACTION_PARTIAL_RECIPE"],
        "local_frame_backbone_cards": channels["LOCAL_FRAME_BACKBONE_RECIPE"],
        "selected_old_clause_events": sum(int(row["support_event_count"]) for row in card_rows),
        "selected_old_clause_unique_event_ids": len({event for row in card_rows for event in str(row["support_event_ids"]).split("|")}),
        "selected_old_clause_page_union": len({page for row in card_rows for page in str(row["support_pages"]).split("|")}),
        "all_support_roundtrips_exact": sum(row["support_roundtrip_exact"] == "YES" for row in card_rows),
        "target_current_phrases_retained": sum(row["target_current_phrase_changed"] == "NO" for row in card_rows) + sum(row["target_current_phrase_changed"] == "NO" for row in open_cards),
        "composed_labels_retained": sum(row["target_evidence_status_retained"] == "COMPOSED_WORKING" for row in card_rows) + sum(row["target_evidence_status_retained"] == "COMPOSED_WORKING" for row in open_cards),
        "open_assumptions_retained": sum(row["assumption_retained"] == "YES" for row in open_cards),
        "working_root_meaning_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "support_channel_count": len(channel_rows),
        "frame_count": len(frame_rows),
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
