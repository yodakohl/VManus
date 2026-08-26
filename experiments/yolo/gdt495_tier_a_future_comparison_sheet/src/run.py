#!/usr/bin/env python3
"""Build the readable future-comparison sheet for the 27 GDT494 Tier-A cards."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt495_tier_a_future_comparison_sheet"
ART = BASE / "artifacts"
G494 = ROOT / "experiments/yolo/gdt494_composed_cell_family_support_ranking/artifacts"

TIER_A_PATH = G494 / "gdt494_27_tier_a_multihead_cards.tsv"
NONTR_PATH = G494 / "gdt494_105_same_register_nontr_support_cells.tsv"
OPPOSITE_PATH = G494 / "gdt494_21_same_register_opposite_tr_cells.tsv"
CROSS_PATH = G494 / "gdt494_98_same_action_cross_register_cells.tsv"

CARD_PATH = ART / "gdt495_27_tier_a_future_cards.tsv"
NONTR_OUT = ART / "gdt495_86_local_nontr_support_cells.tsv"
OPPOSITE_OUT = ART / "gdt495_9_opposite_tr_support_cells.tsv"
CROSS_OUT = ART / "gdt495_43_cross_register_anchor_cells.tsv"
REGISTER_OUT = ART / "gdt495_5_register_card_coverage.tsv"
READABLE_OUT = ART / "GDT495_27_TIER_A_FUTURE_COMPARISON_SHEET.md"
RESULT_OUT = ART / "gdt495_result.json"

GUARD = "KEINE OBERFLÄCHENVORHERSAGE"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def page_key(page: str) -> tuple[int, int, int, str]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", page)
    if match:
        return int(match.group(1)), 0 if match.group(2) == "r" else 1, int(match.group(3) or 0), page
    return 10**9, 0, 0, page


def pages_from(rows: list[dict[str, str]]) -> list[str]:
    pages: set[str] = set()
    for row in rows:
        pages.update(page for page in row["pages"].split("|") if page)
    return sorted(pages, key=page_key)


def event_word(count: int) -> str:
    return "Event" if count == 1 else "Events"


def local_detail(row: dict[str, str]) -> str:
    count = int(row["event_count"])
    return (
        f'{row["support_cell_id"]}: {row["alternate_action_root"]}'
        f'/{row["alternate_action_recipe"]} — {count} {event_word(count)}, '
        f'Seiten {row["pages"]}; {row["observed_clauses_de"]}'
    )


def cross_detail(row: dict[str, str]) -> str:
    count = int(row["event_count"])
    return (
        f'{row["cross_register_cell_id"]}: {row["observed_other_register"]} — '
        f'{count} {event_word(count)}, Seiten {row["pages"]}; '
        f'{row["observed_clauses_de"]}'
    )


def index_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    indexed: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        indexed[row["target_realization_cell_id"]].append(row)
    return indexed


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _tier_fields, tier_rows = read_tsv(TIER_A_PATH)
    nontr_fields, nontr_rows = read_tsv(NONTR_PATH)
    opposite_fields, opposite_rows = read_tsv(OPPOSITE_PATH)
    cross_fields, cross_rows = read_tsv(CROSS_PATH)

    if len(tier_rows) != 27 or any(row["priority_tier"] != "A_MULTIHEAD_SAME_REGISTER" for row in tier_rows):
        raise ValueError("GDT494 Tier-A input is not the fixed 27-card deck")

    target_ids = {row["source_realization_cell_id"] for row in tier_rows}
    selected_nontr = [row for row in nontr_rows if row["target_realization_cell_id"] in target_ids]
    selected_opposite = [row for row in opposite_rows if row["target_realization_cell_id"] in target_ids]
    selected_cross = [row for row in cross_rows if row["target_realization_cell_id"] in target_ids]

    nontr_by_target = index_rows(selected_nontr)
    opposite_by_target = index_rows(selected_opposite)
    cross_by_target = index_rows(selected_cross)
    card_id_by_target: dict[str, str] = {}
    rank_by_target: dict[str, int] = {}
    cards: list[dict[str, object]] = []

    for card_index, source in enumerate(tier_rows, start=1):
        target = source["source_realization_cell_id"]
        card_id = f"G495-F{card_index:03d}"
        card_id_by_target[target] = card_id
        rank_by_target[target] = card_index

        local = sorted(nontr_by_target[target], key=lambda row: row["support_cell_id"])
        opposite = sorted(opposite_by_target[target], key=lambda row: row["support_cell_id"])
        cross = sorted(cross_by_target[target], key=lambda row: row["cross_register_cell_id"])
        all_support = [*local, *opposite, *cross]

        local_roots = [row["alternate_action_root"] for row in local]
        cross_registers = [row["observed_other_register"] for row in cross]
        all_pages = pages_from(all_support)
        local_pages = pages_from(local)
        opposite_pages = pages_from(opposite)
        cross_pages = pages_from(cross)

        if len(set(local_roots)) < 2:
            raise ValueError(f"Tier-A card lost multihead support: {target}")
        if "|".join(local_roots) != source["same_register_nontr_roots"]:
            raise ValueError(f"Tier-A local-root order drift: {target}")
        if sum(int(row["event_count"]) for row in local) != int(source["same_register_nontr_event_count"]):
            raise ValueError(f"Tier-A local event count drift: {target}")

        cards.append(
            {
                "future_card_id": card_id,
                "priority_rank": card_index,
                "source_realization_cell_id": target,
                "frozen_frame": source["frozen_frame"],
                "action_root": source["action_root"],
                "action_recipe": source["action_recipe"],
                "register": source["register"],
                "portable_component_trace_de": source["portable_component_trace_de"],
                "owner_local_slot_trace_de": source["owner_local_slot_trace_de"],
                "working_phrase_de": source["composed_working_phrase_de"],
                "evidence_status_retained": source["evidence_status_retained"],
                "state_requirement": source["state_requirement"],
                "state_warning": source["state_warning"],
                "local_nontr_head_count": len(local_roots),
                "local_nontr_roots": "|".join(local_roots),
                "local_nontr_support_cell_count": len(local),
                "local_nontr_event_count": sum(int(row["event_count"]) for row in local),
                "local_nontr_pages": "|".join(local_pages),
                "local_nontr_support_details_de": " || ".join(local_detail(row) for row in local),
                "opposite_tr_observed": "YES" if opposite else "NO",
                "opposite_tr_root": opposite[0]["alternate_action_root"] if opposite else "NONE",
                "opposite_tr_support_cell_count": len(opposite),
                "opposite_tr_event_count": sum(int(row["event_count"]) for row in opposite),
                "opposite_tr_pages": "|".join(opposite_pages) if opposite_pages else "NONE",
                "opposite_tr_support_details_de": " || ".join(local_detail(row) for row in opposite) if opposite else "NONE",
                "same_action_cross_register_cell_count": len(cross),
                "same_action_cross_registers": "|".join(cross_registers),
                "same_action_cross_register_event_count": sum(int(row["event_count"]) for row in cross),
                "same_action_cross_register_pages": "|".join(cross_pages),
                "same_action_cross_register_details_de": " || ".join(cross_detail(row) for row in cross),
                "all_support_cell_count": len(all_support),
                "all_support_event_count": sum(int(row["event_count"]) for row in all_support),
                "all_old_page_count": len(all_pages),
                "all_old_pages": "|".join(all_pages),
                "all_slot_values_old": source["all_slot_values_old"],
                "composed_working_label_retained": source["composed_working_label_retained"],
                "surface_prediction_made": "NO",
                "occurrence_prediction_made": "NO",
                "comparison_guard": GUARD,
            }
        )

    card_fields = list(cards[0])
    write_tsv(CARD_PATH, card_fields, cards)

    def add_card_fields(rows: list[dict[str, str]], source_fields: list[str]) -> tuple[list[str], list[dict[str, object]]]:
        output_rows: list[dict[str, object]] = []
        for row in rows:
            target = row["target_realization_cell_id"]
            output_rows.append(
                {
                    "future_card_id": card_id_by_target[target],
                    "priority_rank": rank_by_target[target],
                    **row,
                }
            )
        return ["future_card_id", "priority_rank", *source_fields], output_rows

    nontr_out_fields, nontr_out_rows = add_card_fields(selected_nontr, nontr_fields)
    opposite_out_fields, opposite_out_rows = add_card_fields(selected_opposite, opposite_fields)
    cross_out_fields, cross_out_rows = add_card_fields(selected_cross, cross_fields)
    write_tsv(NONTR_OUT, nontr_out_fields, nontr_out_rows)
    write_tsv(OPPOSITE_OUT, opposite_out_fields, opposite_out_rows)
    write_tsv(CROSS_OUT, cross_out_fields, cross_out_rows)

    register_rows: list[dict[str, object]] = []
    for register in sorted({str(card["register"]) for card in cards}):
        group = [card for card in cards if card["register"] == register]
        group_pages: set[str] = set()
        for card in group:
            group_pages.update(str(card["all_old_pages"]).split("|"))
        register_rows.append(
            {
                "register": register,
                "future_card_count": len(group),
                "state_warning_card_count": sum(card["state_warning"] != "NONE" for card in group),
                "local_nontr_support_cell_count": sum(int(card["local_nontr_support_cell_count"]) for card in group),
                "local_nontr_event_count": sum(int(card["local_nontr_event_count"]) for card in group),
                "opposite_tr_support_cell_count": sum(int(card["opposite_tr_support_cell_count"]) for card in group),
                "opposite_tr_event_count": sum(int(card["opposite_tr_event_count"]) for card in group),
                "cross_register_anchor_cell_count": sum(int(card["same_action_cross_register_cell_count"]) for card in group),
                "cross_register_anchor_event_count": sum(int(card["same_action_cross_register_event_count"]) for card in group),
                "unique_old_support_page_count": len(group_pages),
                "unique_old_support_pages": "|".join(sorted(group_pages, key=page_key)),
                "comparison_guard": GUARD,
            }
        )
    write_tsv(REGISTER_OUT, list(register_rows[0]), register_rows)

    all_pages = pages_from([*selected_nontr, *selected_opposite, *selected_cross])
    state_warning_cards = sum(card["state_warning"] != "NONE" for card in cards)
    lines = [
        "# GDT495 — 27 Tier-A-Zukunftskarten",
        "",
        "Status: `TWENTY_SEVEN_TIER_A_CARDS_READY__ONE_HUNDRED_THIRTY_EIGHT_SUPPORT_CELLS_VISIBLE__ZERO_SURFACE_PREDICTIONS`",
        "",
        "Diese 27 Karten sind die dichtesten bereits komponierten T/R-Lesungen aus",
        "GDT494. Jede Karte zeigt den unveränderten Arbeitssatz, seine Komponenten,",
        "jeden lokalen Nicht-T/R-Kopf, eine vorhandene T/R-Gegenseite, alle",
        "registerübergreifenden Anker und sämtliche alten Stützseiten. Die Karten sagen",
        "nicht voraus, welche Zeichenfolge auf einer künftigen Seite stehen wird.",
        "",
        f"Gesamt: **27 Karten**, **{len(selected_nontr)} lokale Nicht-T/R-Zellen / {sum(int(row['event_count']) for row in selected_nontr)} Events**, "
        f"**{len(selected_opposite)} T/R-Gegenzellen / {sum(int(row['event_count']) for row in selected_opposite)} Events**, "
        f"**{len(selected_cross)} registerübergreifende Anker / {sum(int(row['event_count']) for row in selected_cross)} Events**, "
        f"**{len(all_pages)} verschiedene alte Stützseiten** und **{state_warning_cards} Karten mit Zustandswarnung**.",
        "",
        "## Schnellübersicht",
        "",
        "| Rang | Karte | Register | Form | Arbeitslesung | lokale Köpfe | alte Seiten | Zustand |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for card in cards:
        warning = "aktiv" if card["state_warning"] != "NONE" else "selbständig"
        phrase = str(card["working_phrase_de"]).replace("|", "\\|")
        lines.append(
            f'| {card["priority_rank"]} | {card["future_card_id"]} | {card["register"]} | '
            f'`{card["action_recipe"]}` | {phrase} | {card["local_nontr_roots"]} | '
            f'{card["all_old_pages"]} | {warning} |'
        )

    for card in cards:
        target = str(card["source_realization_cell_id"])
        local = sorted(nontr_by_target[target], key=lambda row: row["support_cell_id"])
        opposite = sorted(opposite_by_target[target], key=lambda row: row["support_cell_id"])
        cross = sorted(cross_by_target[target], key=lambda row: row["cross_register_cell_id"])
        lines.extend(
            [
                "",
                f'## {int(card["priority_rank"]):02d}. {card["future_card_id"]} — {card["register"]} · `{card["action_recipe"]}` · `{card["frozen_frame"]}`',
                "",
                f'**Arbeitslesung:** {card["working_phrase_de"]}',
                "",
                f'**Portable Komponenten:** {card["portable_component_trace_de"]}',
                "",
                f'**Owner-lokale Slots:** {card["owner_local_slot_trace_de"]}',
                "",
                f'**Evidenzstatus:** `{card["evidence_status_retained"]}` bleibt unverändert.',
                "",
                f'**Zustand:** `{card["state_requirement"]}`; Warnung `{card["state_warning"]}`.',
                "",
                "### Lokale alte Rahmenfamilie, ohne T/R",
                "",
            ]
        )
        for row in local:
            lines.append(f"- {local_detail(row)}")
        lines.extend(["", "### Beobachtete T/R-Gegenseite", ""])
        if opposite:
            for row in opposite:
                lines.append(f"- {local_detail(row)}")
        else:
            lines.append("- Keine lokale beobachtete T/R-Gegenseite; die zwei oder mehr Nicht-T/R-Köpfe tragen Tier A bereits.")
        lines.extend(["", "### Gleiche Zielhandlung und gleicher Rahmen in anderen Registern", ""])
        for row in cross:
            lines.append(f"- {cross_detail(row)}")
        lines.extend(
            [
                "",
                f'**Alle alten Stützseiten:** {card["all_old_pages"]}',
                "",
                f'**{GUARD}**',
            ]
        )

    READABLE_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = {
        "status": "TWENTY_SEVEN_TIER_A_CARDS_READY__ONE_HUNDRED_THIRTY_EIGHT_SUPPORT_CELLS_VISIBLE__ZERO_SURFACE_PREDICTIONS",
        "tier_a_future_cards": len(cards),
        "local_nontr_support_cells": len(selected_nontr),
        "local_nontr_support_events": sum(int(row["event_count"]) for row in selected_nontr),
        "opposite_tr_support_cells": len(selected_opposite),
        "opposite_tr_support_events": sum(int(row["event_count"]) for row in selected_opposite),
        "cross_register_anchor_cells": len(selected_cross),
        "cross_register_anchor_events": sum(int(row["event_count"]) for row in selected_cross),
        "all_visible_support_cells": len(selected_nontr) + len(selected_opposite) + len(selected_cross),
        "all_visible_support_events": sum(int(row["event_count"]) for row in [*selected_nontr, *selected_opposite, *selected_cross]),
        "unique_old_support_pages": len(all_pages),
        "old_support_pages": all_pages,
        "state_warning_cards": state_warning_cards,
        "self_contained_cards": len(cards) - state_warning_cards,
        "cards_with_two_or_more_local_nontr_heads": sum(int(card["local_nontr_head_count"]) >= 2 for card in cards),
        "cards_with_cross_register_anchor": sum(int(card["same_action_cross_register_cell_count"]) >= 1 for card in cards),
        "cards_with_all_old_slot_values": sum(card["all_slot_values_old"] == "YES" for card in cards),
        "cards_retaining_composed_label": sum(card["composed_working_label_retained"] == "YES" for card in cards),
        "surface_predictions": sum(card["surface_prediction_made"] == "YES" for card in cards),
        "occurrence_predictions": sum(card["occurrence_prediction_made"] == "YES" for card in cards),
        "comparison_guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
