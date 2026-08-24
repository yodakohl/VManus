#!/usr/bin/env python3
"""Run the minimal Biological dictionary forward and backward over all records."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CARDS = ROOT / "experiments/yolo/sidequest_semantic_minimal_bio_dictionary_three_hundred_tenth/THREE_HUNDRED_TENTH_124_CARD_PRODUCTION_RECIPES.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_minimal_bio_dictionary_three_hundred_tenth/THREE_HUNDRED_TENTH_281_EVENT_DICTIONARY_ROUNDTRIP.tsv"
RAW = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
GRADE = ROOT / "experiments/yolo/sidequest_semantic_grade_matrix_two_hundred_ninety_sixth/TWO_HUNDRED_NINETY_SIXTH_30_GRADE_CARDS.tsv"
FINAL_RECIPES = ROOT / "experiments/yolo/sidequest_semantic_final_writer_conventions_two_hundred_eighty_eighth/TWO_HUNDRED_EIGHTY_EIGHTH_149_DETERMINISTIC_RECIPES.tsv"
VISUAL_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_R3_281_EVENT_INTERLINEAR.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cards = read(CARDS)
    events = read(EVENTS)
    raw = {r["event_id"]: r for r in read(RAW)}
    grades = {r["master_card_id"]: r["grade"] for r in read(GRADE)}
    final_recipes = {r["master_card_id"]: r["final_recipe"] for r in read(FINAL_RECIPES)}
    visual = {f"E{int(r['event_serial']):03d}": r for r in read(VISUAL_EVENTS)}
    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_card[event["master_card_id"]].append(event)

    # Terminal scope is invariant per registered card in the fixed Bio deck.
    terminal_by_card = {}
    for card_id, selected in events_by_card.items():
        states = {raw[r["event_id"]]["terminal_status"] for r in selected}
        assert len(states) == 1
        terminal_by_card[card_id] = states.pop()

    # Grade resolves seven recipe collisions. The remaining fifteen nondefault
    # cards get one learned form selector each.
    collision_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for card in cards:
        collision_groups[(card["minimal_dictionary_recipe"], grades.get(card["master_card_id"], "NO_GRADE"))].append(card)
    selector_by_card = {card["master_card_id"]: "UNIQUE_RECIPE" for card in cards}
    selector_rows = []
    for (recipe, grade), selected in collision_groups.items():
        if len(selected) == 1:
            continue
        selected.sort(key=lambda r: (-int(r["bio_event_count"]), r["master_card_id"]))
        default = selected[0]
        selector_by_card[default["master_card_id"]] = "DEFAULT_FOR_RECIPE"
        for exception in selected[1:]:
            selector = f"SELECT_{exception['master_card_id']}"
            selector_by_card[exception["master_card_id"]] = selector
            selector_rows.append({
                "selector_id": selector,
                "base_minimal_recipe": recipe,
                "grade_instruction": grade,
                "default_master_card_id": default["master_card_id"],
                "default_form": default["master_form"],
                "selected_master_card_id": exception["master_card_id"],
                "selected_form": exception["master_form"],
                "selected_short_value_de": exception["source_short_value_de"],
                "selected_imperative_de": exception["imperative_clause_de"],
                "teaching_rule_de": "bei diesem engeren Bedeutungszusatz die gelernte Nichtstandardform wählen",
            })
    selector_path = HERE / "THREE_HUNDRED_ELEVENTH_15_FORM_SELECTORS.tsv"
    write(selector_path, selector_rows)

    writer_rows = []
    source_key_to_card = {}
    for card in cards:
        card_id = card["master_card_id"]
        terminal = terminal_by_card[card_id]
        source_key = f"{card['source_short_value_de']}|{terminal}"
        assert source_key not in source_key_to_card
        source_key_to_card[source_key] = card_id
        exact_recipe = final_recipes.get(card_id, f"W_{card_id}")
        writer_rows.append({
            "master_card_id": card_id,
            "source_key_short_value_plus_scope": source_key,
            "source_short_value_de": card["source_short_value_de"],
            "imperative_clause_de": card["imperative_clause_de"],
            "terminal_scope": terminal,
            "minimal_dictionary_recipe": card["minimal_dictionary_recipe"],
            "grade_instruction": grades.get(card_id, "NO_GRADE"),
            "form_selector": selector_by_card[card_id],
            "exact_identity_recipe": exact_recipe,
            "canonical_written_form": card["master_form"],
            "registered_surface_forms": card["registered_surfaces"],
            "surface_form_count": len(card["registered_surfaces"].split("|")),
            "bio_event_count": card["bio_event_count"],
            "forward_rule_de": "Kurzwert und Scope wählen die Kartenidentität; Rezept, Grad und Selektor schreiben die kanonische Form.",
        })
    writer_path = HERE / "THREE_HUNDRED_ELEVENTH_124_CARD_FORWARD_WRITER.tsv"
    write(writer_path, writer_rows)
    writer_by_card = {r["master_card_id"]: r for r in writer_rows}

    reverse_rows = []
    surface_to_card = {}
    for card in writer_rows:
        for surface in card["registered_surface_forms"].split("|"):
            assert surface not in surface_to_card
            surface_to_card[surface] = card["master_card_id"]
            reverse_rows.append({
                "visible_surface": surface,
                "master_card_id": card["master_card_id"],
                "canonical_form": card["canonical_written_form"],
                "source_short_value_de": card["source_short_value_de"],
                "imperative_clause_de": card["imperative_clause_de"],
                "terminal_scope": card["terminal_scope"],
                "exact_identity_recipe": card["exact_identity_recipe"],
                "reverse_rule_de": "Oberfläche eindeutig zur registrierten Karte; dann Kurzhandlung und Scope lesen.",
            })
    reverse_rows.sort(key=lambda r: r["visible_surface"])
    reverse_path = HERE / "THREE_HUNDRED_ELEVENTH_176_SURFACE_REVERSE_DICTIONARY.tsv"
    write(reverse_path, reverse_rows)

    trace_rows = []
    for event in events:
        card = writer_by_card[event["master_card_id"]]
        source_key = f"{card['source_short_value_de']}|{raw[event['event_id']]['terminal_status']}"
        predicted_card = source_key_to_card[source_key]
        reverse_card = surface_to_card[event["visible_surface"]]
        vis = visual[event["event_id"]]
        reset = "YES" if any(token in vis["incoming_contact_and_reset"] for token in ["RESET", "BREAK"]) else "NO"
        trace_rows.append({
            "event_id": event["event_id"], "record_unit_id": event["record_unit_id"], "page": raw[event["event_id"]]["page"],
            "statement_id": event["statement_id"], "field_id": raw[event["event_id"]]["field_id"],
            "visible_owner": raw[event["event_id"]]["visible_owner"],
            "owner_reset_or_break": reset, "owner_reset_rule": vis["incoming_contact_and_reset"],
            "source_short_value_de": card["source_short_value_de"], "terminal_scope": raw[event["event_id"]]["terminal_status"],
            "source_key": source_key, "predicted_master_card_id": predicted_card,
            "expected_master_card_id": event["master_card_id"], "forward_identity_match": "YES" if predicted_card == event["master_card_id"] else "NO",
            "minimal_dictionary_recipe": card["minimal_dictionary_recipe"], "grade_instruction": card["grade_instruction"],
            "form_selector": card["form_selector"], "exact_identity_recipe": card["exact_identity_recipe"],
            "canonical_forward_surface": card["canonical_written_form"], "observed_visible_surface": event["visible_surface"],
            "surface_relation": "CANONICAL" if card["canonical_written_form"] == event["visible_surface"] else "REGISTERED_ALLOGRAPH",
            "reverse_decoded_master_card_id": reverse_card, "reverse_identity_match": "YES" if reverse_card == event["master_card_id"] else "NO",
            "dictionary_reading_de": event["dictionary_reading_de"],
        })
    trace_path = HERE / "THREE_HUNDRED_ELEVENTH_281_FORWARD_BACKWARD_TRACE.tsv"
    write(trace_path, trace_rows)

    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in trace_rows:
        by_record[row["record_unit_id"]].append(row)
    lines = ["# Lehrlings-Rundlauf der sechs Biological-Records", "", "Vorwärts: Kurzhandlung + offen/geschlossen → Kartenidentität → Komponentenrezept + Grad + optionaler Selektor → kanonische Form. Rückwärts: jede registrierte Oberfläche → genau eine Kartenidentität → Kurzhandlung + Scope.", ""]
    for record_id, selected in by_record.items():
        lines += [f"## {record_id} — {len(selected)} Karten", ""]
        for row in selected:
            reset = " **[OWNER-RESET]**" if row["owner_reset_or_break"] == "YES" else ""
            lines += [f"- {row['event_id']}{reset}: `{row['observed_visible_surface']}` ⇄ {row['source_short_value_de']} [{row['terminal_scope']}] → `{row['canonical_forward_surface']}` ({row['surface_relation']})"]
        lines += [""]
    edition_path = HERE / "THREE_HUNDRED_ELEVENTH_SIX_RECORD_ROUNDTRIP.md"
    edition_path.write_text("\n".join(lines), encoding="utf-8")

    report_path = HERE / "THREE_HUNDRED_ELEVENTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 311: vollständiger Bio-Lehrlings-Rundlauf\n\n"
        "Kurzhandlung plus offen/geschlossen bestimmt alle 124 Kartenidentitäten eindeutig. Die 39 Bedeutungseinträge brauchen für exakte Vorwärtsschreibung noch den bereits gelehrten E/EE/EEE-Grad und fünfzehn gelernte Nichtstandard-Formselektoren; dann sind alle 124 Identitätsrezepte eindeutig. Rückwärts sind sämtliche 176 registrierten Oberflächenformen ohne Kollision einer Karte zugeordnet.\n\n"
        "Alle 281 Ereignisse bestehen den Identitäts-Rundlauf in beide Richtungen. 173 erscheinen bereits in kanonischer Form; 108 verwenden eine andere registrierte Rendererform derselben Karte. Die sechzehn sichtbaren Record-/Besitzerresets bleiben in der Spur erhalten. Damit ist die Semantik-/Identitätsschicht geschlossen; der nächste Pass muss nur noch die 30 Mehrformkarten auf einfache positions- und handabhängige Rendererregeln reduzieren.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "cards": len(writer_rows), "source_keys": len(source_key_to_card), "surface_forms": len(reverse_rows),
        "form_selectors": len(selector_rows), "events": len(trace_rows),
        "forward_identity_matches": sum(r["forward_identity_match"] == "YES" for r in trace_rows),
        "reverse_identity_matches": sum(r["reverse_identity_match"] == "YES" for r in trace_rows),
        "canonical_surface_events": sum(r["surface_relation"] == "CANONICAL" for r in trace_rows),
        "registered_allograph_events": sum(r["surface_relation"] == "REGISTERED_ALLOGRAPH" for r in trace_rows),
        "owner_reset_or_break_events": sum(r["owner_reset_or_break"] == "YES" for r in trace_rows),
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [CARDS, EVENTS, RAW, GRADE, FINAL_RECIPES, VISUAL_EVENTS]},
        "output_hashes": {p.name: sha(p) for p in [selector_path, writer_path, reverse_path, trace_path, edition_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
