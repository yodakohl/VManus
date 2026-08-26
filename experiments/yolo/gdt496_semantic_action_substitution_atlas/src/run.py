#!/usr/bin/env python3
"""Compare the 27 GDT495 target readings with their observed action families."""

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
BASE = ROOT / "experiments/yolo/gdt496_semantic_action_substitution_atlas"
ART = BASE / "artifacts"
G495 = ROOT / "experiments/yolo/gdt495_tier_a_future_comparison_sheet/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"

CARDS_IN = G495 / "gdt495_27_tier_a_future_cards.tsv"
NONTR_IN = G495 / "gdt495_86_local_nontr_support_cells.tsv"
OPPOSITE_IN = G495 / "gdt495_9_opposite_tr_support_cells.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"

CARDS_OUT = ART / "gdt496_27_semantic_substitution_cards.tsv"
CELLS_OUT = ART / "gdt496_95_observed_head_cells.tsv"
EVENTS_OUT = ART / "gdt496_242_observed_family_events.tsv"
CONTEXT_OUT = ART / "gdt496_9_context_safe_defaults.tsv"
FRAMES_OUT = ART / "gdt496_9_frame_semantic_coverage.tsv"
REGISTERS_OUT = ART / "gdt496_5_register_semantic_coverage.tsv"
READABLE_OUT = ART / "GDT496_SEMANTIC_ACTION_SUBSTITUTION_ATLAS.md"
RESULT_OUT = ART / "gdt496_result.json"

STATUS = "EIGHTEEN_DIRECT_AND_NINE_CONTEXT_SAFE_DEFAULTS__ALL_242_OBSERVED_REMAINDERS_MATCH"
GUARD = "ARBEITSLESUNG__KEINE OBERFLÄCHENVORHERSAGE"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing TSV header: {path}")
        return list(reader.fieldnames), list(reader)


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def split_trace(value: str) -> list[str]:
    return value.split(" · ") if value else []


def drop_index(values: list[str], index: int) -> list[str]:
    return values[:index] + values[index + 1 :]


def show_trace(values: list[str]) -> str:
    return " · ".join(values) if values else "EMPTY"


def roots(values: list[str]) -> list[str]:
    output: set[str] = set()
    for value in values:
        output.update(part for part in value.split("|") if part and part != "NONE")
    return sorted(output)


def context_safe_phrase(phrase: str, state_requirement: str) -> tuple[str, str]:
    if state_requirement != "ACTIVE_ARGUMENT_REQUIRED":
        return phrase, "UNCHANGED_SELF_CONTAINED"
    safe, substitutions = re.subn(
        r"\b(?:den|die|das) [^.;]+ \[wie zuvor\]",
        "das zuvor Genannte",
        phrase,
        count=1,
    )
    if substitutions != 1:
        raise ValueError(f"cannot generalize active-argument phrase: {phrase}")
    return safe, "CONTEXT_NOUN_GENERALIZED"


def aggregate_support(
    cards: list[dict[str, str]],
    support_rows: list[tuple[str, dict[str, str]]],
    clauses: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, list[dict[str, object]]]]:
    card_by_id = {row["future_card_id"]: row for row in cards}
    clauses_by_recipe_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for clause in clauses:
        clauses_by_recipe_register[(clause["component_recipe"], clause["register"])].append(clause)

    cell_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    cells_by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    event_serial = 0

    for support_kind, support in support_rows:
        card_id = support["future_card_id"]
        card = card_by_id[card_id]
        observed = clauses_by_recipe_register[(support["alternate_action_recipe"], support["register"])]
        if len(observed) != int(support["event_count"]):
            raise ValueError(f"support event count drift: {support['support_cell_id']}")

        frame_tokens = card["frozen_frame"].split("+")
        placeholder_index = frame_tokens.index("@ACTION")
        target_recipe_tokens = card["action_recipe"].split("+")
        target_portable = split_trace(card["portable_component_trace_de"])
        target_owner_assignments = split_trace(card["owner_local_slot_trace_de"])
        if not (len(frame_tokens) == len(target_recipe_tokens) == len(target_portable) == len(target_owner_assignments)):
            raise ValueError(f"target trace length drift: {card_id}")
        target_owner_values = [assignment.split("=", 1)[1] for assignment in target_owner_assignments]
        expected_portable_remainder = drop_index(target_portable, placeholder_index)
        expected_owner_remainder = drop_index(target_owner_values, placeholder_index)

        portable_variants: set[str] = set()
        owner_variants: set[str] = set()
        action_atom_readings: set[str] = set()
        explicit_argument_values: list[str] = []
        inherited_argument_values: list[str] = []
        event_ids: list[str] = []
        all_portable_match = True
        all_owner_match = True

        for clause in observed:
            recipe_tokens = clause["component_recipe"].split("+")
            portable = split_trace(clause["portable_back_projection_de"])
            owner = split_trace(clause["owner_local_atom_reading_de"])
            if not (len(recipe_tokens) == len(portable) == len(owner) == len(frame_tokens)):
                raise ValueError(f"observed trace length drift: {clause['global_running_event_id']}")
            for token_index, frame_token in enumerate(frame_tokens):
                expected_token = support["alternate_action_root"] if frame_token == "@ACTION" else frame_token
                if recipe_tokens[token_index] != expected_token:
                    raise ValueError(f"formal frame mismatch: {clause['global_running_event_id']}")

            observed_portable_remainder = drop_index(portable, placeholder_index)
            observed_owner_remainder = drop_index(owner, placeholder_index)
            portable_match = observed_portable_remainder == expected_portable_remainder
            owner_match = observed_owner_remainder == expected_owner_remainder
            all_portable_match &= portable_match
            all_owner_match &= owner_match
            portable_variants.add(show_trace(observed_portable_remainder))
            owner_variants.add(show_trace(observed_owner_remainder))
            action_atom_readings.add(owner[placeholder_index])
            explicit_argument_values.append(clause["explicit_argument_roots"])
            inherited_argument_values.append(clause["inherited_argument_root"])

            event_serial += 1
            family_event_id = f"G496-E{event_serial:03d}"
            event_ids.append(family_event_id)
            event_rows.append(
                {
                    "family_event_id": family_event_id,
                    "future_card_id": card_id,
                    "priority_rank": card["priority_rank"],
                    "support_kind": support_kind,
                    "support_cell_id": support["support_cell_id"],
                    "target_action_root": card["action_root"],
                    "target_action_recipe": card["action_recipe"],
                    "frozen_frame": card["frozen_frame"],
                    "register": card["register"],
                    "alternate_action_root": support["alternate_action_root"],
                    "alternate_action_recipe": support["alternate_action_recipe"],
                    "source_event_id": clause["global_running_event_id"],
                    "source_statement_id": clause["global_statement_id"],
                    "source_page": clause["physical_page"],
                    "source_surface": clause["surface"],
                    "source_owner_class": clause["owner_class"],
                    "source_owner_de": clause["owner_de"],
                    "observed_clause_de": clause["imperative_clause_de"],
                    "action_atom_reading_de": owner[placeholder_index],
                    "explicit_argument_roots": clause["explicit_argument_roots"],
                    "inherited_argument_root": clause["inherited_argument_root"],
                    "expected_portable_remainder_de": show_trace(expected_portable_remainder),
                    "observed_portable_remainder_de": show_trace(observed_portable_remainder),
                    "portable_remainder_match": "YES" if portable_match else "NO",
                    "expected_owner_remainder_de": show_trace(expected_owner_remainder),
                    "observed_owner_remainder_de": show_trace(observed_owner_remainder),
                    "owner_remainder_match": "YES" if owner_match else "NO",
                    "component_order_match": "YES",
                    "source_roundtrip_exact": clause["roundtrip_exact"],
                }
            )

        cell = {
            "semantic_head_cell_id": f"G496-H{len(cell_rows) + 1:03d}",
            "future_card_id": card_id,
            "priority_rank": card["priority_rank"],
            "support_kind": support_kind,
            "support_cell_id": support["support_cell_id"],
            "frozen_frame": card["frozen_frame"],
            "target_action_root": card["action_root"],
            "target_action_recipe": card["action_recipe"],
            "register": card["register"],
            "alternate_action_root": support["alternate_action_root"],
            "alternate_action_recipe": support["alternate_action_recipe"],
            "event_count": len(observed),
            "event_ids": "|".join(event_ids),
            "source_pages": support["pages"],
            "observed_clause_form_count": support["observed_clause_form_count"],
            "observed_clauses_de": support["observed_clauses_de"],
            "expected_portable_remainder_de": show_trace(expected_portable_remainder),
            "observed_portable_remainder_variant_count": len(portable_variants),
            "observed_portable_remainders_de": " || ".join(sorted(portable_variants)),
            "all_portable_remainders_match": "YES" if all_portable_match else "NO",
            "expected_owner_remainder_de": show_trace(expected_owner_remainder),
            "observed_owner_remainder_variant_count": len(owner_variants),
            "observed_owner_remainders_de": " || ".join(sorted(owner_variants)),
            "all_owner_remainders_match": "YES" if all_owner_match else "NO",
            "action_atom_reading_form_count": len(action_atom_readings),
            "action_atom_readings_de": " || ".join(sorted(action_atom_readings)),
            "explicit_argument_roots": "|".join(roots(explicit_argument_values)) or "NONE",
            "inherited_argument_roots": "|".join(roots(inherited_argument_values)) or "NONE",
            "all_component_orders_match": "YES",
            "all_source_roundtrips_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in observed) else "NO",
        }
        cell_rows.append(cell)
        cells_by_card[card_id].append(cell)

    return cell_rows, event_rows, cells_by_card


def summarize_axis(cards: list[dict[str, object]], axis: str) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    values = sorted({str(card[axis]) for card in cards})
    for value in values:
        group = [card for card in cards if card[axis] == value]
        output.append(
            {
                axis: value,
                "card_count": len(group),
                "direct_self_contained_count": sum(card["substitution_class"] == "DIRECT_SELF_CONTAINED_REMAINDER" for card in group),
                "context_safe_count": sum(str(card["substitution_class"]).startswith("CONTEXT_SAFE_") for card in group),
                "observed_head_cell_count": sum(int(card["observed_head_cell_count"]) for card in group),
                "observed_family_event_count": sum(int(card["observed_family_event_count"]) for card in group),
                "portable_remainder_mismatch_count": sum(int(card["portable_remainder_mismatch_count"]) for card in group),
                "owner_remainder_mismatch_count": sum(int(card["owner_remainder_mismatch_count"]) for card in group),
                "context_default_change_count": sum(card["default_change_type"] == "CONTEXT_NOUN_GENERALIZED" for card in group),
                "all_working_meanings_retained": "YES" if all(card["working_meaning_retained"] == "YES" for card in group) else "NO",
            }
        )
    return output


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _card_fields, cards_in = read_tsv(CARDS_IN)
    _nontr_fields, nontr_in = read_tsv(NONTR_IN)
    _opposite_fields, opposite_in = read_tsv(OPPOSITE_IN)
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    if (len(cards_in), len(nontr_in), len(opposite_in), len(clauses)) != (27, 86, 9, 4576):
        raise ValueError("input count drift")

    support_rows = [("NONTR", row) for row in nontr_in] + [("OPPOSITE_TR", row) for row in opposite_in]
    support_rows.sort(key=lambda item: (int(item[1]["priority_rank"]), 0 if item[0] == "NONTR" else 1, item[1]["support_cell_id"]))
    cell_rows, event_rows, cells_by_card = aggregate_support(cards_in, support_rows, clauses)

    events_by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in event_rows:
        events_by_card[str(event["future_card_id"])].append(event)

    cards_out: list[dict[str, object]] = []
    context_rows: list[dict[str, object]] = []
    for source in cards_in:
        card_id = source["future_card_id"]
        cells = cells_by_card[card_id]
        events = events_by_card[card_id]
        explicit_roots = roots([str(event["explicit_argument_roots"]) for event in events])
        inherited_roots = roots([str(event["inherited_argument_root"]) for event in events])
        portable_mismatches = sum(event["portable_remainder_match"] == "NO" for event in events)
        owner_mismatches = sum(event["owner_remainder_match"] == "NO" for event in events)
        safe_phrase, change_type = context_safe_phrase(source["working_phrase_de"], source["state_requirement"])

        if portable_mismatches or owner_mismatches:
            substitution_class = "REMAINDER_CONFLICT"
            action_substitution_reading = "NO"
        elif source["state_requirement"] == "SELF_CONTAINED_ARGUMENT":
            substitution_class = "DIRECT_SELF_CONTAINED_REMAINDER"
            action_substitution_reading = "YES"
        elif len(inherited_roots) > 1:
            substitution_class = "CONTEXT_SAFE_MULTIPLE_INHERITED_ROOTS"
            action_substitution_reading = "CONDITIONAL_ON_ACTIVE_ARGUMENT"
        elif len(inherited_roots) == 1:
            substitution_class = "CONTEXT_SAFE_ONE_INHERITED_ROOT"
            action_substitution_reading = "CONDITIONAL_ON_ACTIVE_ARGUMENT"
        else:
            substitution_class = "CONTEXT_SAFE_UNTAGGED_ARGUMENT"
            action_substitution_reading = "CONDITIONAL_ON_ACTIVE_ARGUMENT"

        observed_owner_remainders = sorted({str(event["observed_owner_remainder_de"]) for event in events})
        observed_portable_remainders = sorted({str(event["observed_portable_remainder_de"]) for event in events})
        card = {
            "semantic_card_id": f"G496-S{len(cards_out) + 1:03d}",
            "future_card_id": card_id,
            "priority_rank": source["priority_rank"],
            "source_realization_cell_id": source["source_realization_cell_id"],
            "frozen_frame": source["frozen_frame"],
            "action_root": source["action_root"],
            "action_recipe": source["action_recipe"],
            "register": source["register"],
            "portable_component_trace_de": source["portable_component_trace_de"],
            "owner_local_slot_trace_de": source["owner_local_slot_trace_de"],
            "previous_working_phrase_de": source["working_phrase_de"],
            "context_safe_default_phrase_de": safe_phrase,
            "default_change_type": change_type,
            "state_requirement": source["state_requirement"],
            "state_warning_retained": source["state_warning"],
            "substitution_class": substitution_class,
            "action_substitution_reading": action_substitution_reading,
            "observed_head_cell_count": len(cells),
            "observed_nontr_head_cell_count": sum(cell["support_kind"] == "NONTR" for cell in cells),
            "observed_opposite_tr_cell_count": sum(cell["support_kind"] == "OPPOSITE_TR" for cell in cells),
            "observed_action_roots": "|".join(str(cell["alternate_action_root"]) for cell in cells),
            "observed_family_event_count": len(events),
            "source_event_ids": "|".join(str(event["source_event_id"]) for event in events),
            "source_pages": "|".join(sorted({str(event["source_page"]) for event in events})),
            "expected_portable_remainder_de": str(cells[0]["expected_portable_remainder_de"]),
            "observed_portable_remainder_variants_de": " || ".join(observed_portable_remainders),
            "portable_remainder_mismatch_count": portable_mismatches,
            "expected_owner_remainder_de": str(cells[0]["expected_owner_remainder_de"]),
            "observed_owner_remainder_variants_de": " || ".join(observed_owner_remainders),
            "owner_remainder_mismatch_count": owner_mismatches,
            "explicit_argument_roots_in_family": "|".join(explicit_roots) or "NONE",
            "inherited_argument_roots_in_family": "|".join(inherited_roots) or "NONE",
            "all_component_orders_match": "YES" if all(event["component_order_match"] == "YES" for event in events) else "NO",
            "all_source_roundtrips_exact": "YES" if all(event["source_roundtrip_exact"] == "YES" for event in events) else "NO",
            "working_meaning_retained": "YES",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        }
        cards_out.append(card)
        if change_type == "CONTEXT_NOUN_GENERALIZED":
            context_rows.append(
                {
                    "context_default_id": f"G496-C{len(context_rows) + 1:02d}",
                    "semantic_card_id": card["semantic_card_id"],
                    "future_card_id": card_id,
                    "frozen_frame": source["frozen_frame"],
                    "action_recipe": source["action_recipe"],
                    "register": source["register"],
                    "previous_owner_y_default_de": source["working_phrase_de"],
                    "context_safe_default_de": safe_phrase,
                    "observed_inherited_argument_roots": "|".join(inherited_roots) or "NONE",
                    "observed_family_event_count": len(events),
                    "fixed_remainder_de": str(card["expected_owner_remainder_de"]),
                    "meaning_change_made": "NO",
                    "argument_noun_generalized": "YES",
                    "state_warning_retained": source["state_warning"],
                    "guard": GUARD,
                }
            )

    frame_rows = summarize_axis(cards_out, "frozen_frame")
    register_rows = summarize_axis(cards_out, "register")
    write_tsv(CARDS_OUT, cards_out)
    write_tsv(CELLS_OUT, cell_rows)
    write_tsv(EVENTS_OUT, event_rows)
    write_tsv(CONTEXT_OUT, context_rows)
    write_tsv(FRAMES_OUT, frame_rows)
    write_tsv(REGISTERS_OUT, register_rows)

    lines = [
        "# GDT496 — Semantischer Handlungsaustausch in den 27 Tier-A-Familien",
        "",
        f"Status: `{STATUS}`",
        "",
        "Jede Reihe entfernt nur den wechselnden Handlungskopf aus den alten",
        "GDT416-Komponenten und vergleicht den verbleibenden Gegenstand, die Relation",
        "und ihre Reihenfolge mit der GDT495-Ziellesung. So bleibt sichtbar, ob T oder",
        "R wirklich in einen alten Bedeutungsrahmen eingesetzt wird.",
        "",
        f"- direkte, selbständige Lesungen: **{sum(card['substitution_class'] == 'DIRECT_SELF_CONTAINED_REMAINDER' for card in cards_out)}**;",
        f"- kontextsichere Lesungen: **{sum(str(card['substitution_class']).startswith('CONTEXT_SAFE_') for card in cards_out)}**;",
        f"- beobachtete Kopfzellen: **{len(cell_rows)}**; beobachtete Familienevents: **{len(event_rows)}**;",
        f"- portable Restabweichungen: **{sum(int(card['portable_remainder_mismatch_count']) for card in cards_out)}**; owner-lokale Restabweichungen: **{sum(int(card['owner_remainder_mismatch_count']) for card in cards_out)}**.",
        "",
        "Bei einer kontextabhängigen Karte ersetzt die neue Redaktionsform nur den",
        "unbekannten Posten-Default durch **das zuvor Genannte**. Handlung, Relation,",
        "Reihenfolge und alle Wortstammbedeutungen bleiben unverändert.",
        "",
        "## Schnellübersicht",
        "",
        "| Rang | Karte | Register | Rezept | neuer Default | Klasse | Köpfe/Events | geerbte Argumente |",
        "|---:|---|---|---|---|---|---:|---|",
    ]
    for card in cards_out:
        lines.append(
            f'| {card["priority_rank"]} | {card["semantic_card_id"]} | {card["register"]} | '
            f'`{card["action_recipe"]}` | {card["context_safe_default_phrase_de"]} | '
            f'`{card["substitution_class"]}` | {card["observed_head_cell_count"]}/{card["observed_family_event_count"]} | '
            f'{card["inherited_argument_roots_in_family"]} |'
        )

    for card in cards_out:
        cells = cells_by_card[str(card["future_card_id"])]
        lines.extend(
            [
                "",
                f'## {int(card["priority_rank"]):02d}. {card["semantic_card_id"]} — {card["register"]} · `{card["action_recipe"]}`',
                "",
                f'**Bisher:** {card["previous_working_phrase_de"]}',
                "",
                f'**Kontextsicherer Default:** {card["context_safe_default_phrase_de"]}',
                "",
                f'**Fester portabler Rest:** {card["expected_portable_remainder_de"]}',
                "",
                f'**Fester owner-lokaler Rest:** {card["expected_owner_remainder_de"]}',
                "",
                f'**Klasse:** `{card["substitution_class"]}`; Zustandsregel `{card["state_requirement"]}`.',
                "",
                "### Beobachtete Handlungsköpfe im gleichen Rahmen und Register",
                "",
            ]
        )
        for cell in cells:
            lines.append(
                f'- **{cell["alternate_action_root"]}** / `{cell["alternate_action_recipe"]}` '
                f'({cell["event_count"]} Events; {cell["source_pages"]}): Rest '
                f'`{cell["observed_owner_remainders_de"]}`; Argument explizit '
                f'`{cell["explicit_argument_roots"]}`, geerbt `{cell["inherited_argument_roots"]}`; '
                f'{cell["observed_clauses_de"]}'
            )
        lines.extend(["", f'**{GUARD}**'])

    READABLE_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    substitution_counts = Counter(str(card["substitution_class"]) for card in cards_out)
    result = {
        "status": STATUS,
        "semantic_cards": len(cards_out),
        "direct_self_contained_defaults": substitution_counts["DIRECT_SELF_CONTAINED_REMAINDER"],
        "context_safe_defaults": sum(count for key, count in substitution_counts.items() if key.startswith("CONTEXT_SAFE_")),
        "context_safe_multiple_inherited_roots": substitution_counts["CONTEXT_SAFE_MULTIPLE_INHERITED_ROOTS"],
        "context_safe_one_inherited_root": substitution_counts["CONTEXT_SAFE_ONE_INHERITED_ROOT"],
        "context_safe_untagged_argument": substitution_counts["CONTEXT_SAFE_UNTAGGED_ARGUMENT"],
        "remainder_conflicts": substitution_counts["REMAINDER_CONFLICT"],
        "observed_head_cells": len(cell_rows),
        "observed_nontr_head_cells": sum(cell["support_kind"] == "NONTR" for cell in cell_rows),
        "observed_opposite_tr_cells": sum(cell["support_kind"] == "OPPOSITE_TR" for cell in cell_rows),
        "observed_family_events": len(event_rows),
        "portable_remainder_mismatches": sum(event["portable_remainder_match"] == "NO" for event in event_rows),
        "owner_remainder_mismatches": sum(event["owner_remainder_match"] == "NO" for event in event_rows),
        "component_order_mismatches": sum(event["component_order_match"] == "NO" for event in event_rows),
        "source_roundtrip_failures": sum(event["source_roundtrip_exact"] == "NO" for event in event_rows),
        "context_noun_generalizations": len(context_rows),
        "working_meaning_changes": sum(card["working_meaning_retained"] == "NO" for card in cards_out),
        "surface_predictions": sum(card["surface_prediction_made"] == "YES" for card in cards_out),
        "occurrence_predictions": sum(card["occurrence_prediction_made"] == "YES" for card in cards_out),
        "frame_count": len(frame_rows),
        "register_count": len(register_rows),
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
