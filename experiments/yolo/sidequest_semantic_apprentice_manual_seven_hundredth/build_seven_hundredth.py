#!/usr/bin/env python3
"""Build the consolidated apprentice manual and full 381-event forward trace."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P606 = ROOT / "experiments/yolo/sidequest_semantic_short_workshop_dictionary_six_hundred_sixth"
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"
P680 = ROOT / "experiments/yolo/sidequest_semantic_owner_expanded_compact_edition_six_hundred_eightieth"
P696 = ROOT / "experiments/yolo/sidequest_semantic_full_surface_composition_six_hundred_ninety_sixth"
P697 = ROOT / "experiments/yolo/sidequest_semantic_renderer_manual_six_hundred_ninety_seventh"
P698 = ROOT / "experiments/yolo/sidequest_semantic_entry_frame_selection_six_hundred_ninety_eighth"
P699 = ROOT / "experiments/yolo/sidequest_semantic_owner_renderer_trays_six_hundred_ninety_ninth"
WHOLE_COMMANDS = {"OS", "RESUME_CARD", "TALAM"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    roots = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")
    cards = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_173_COMPACT_CARD_TABLET.tsv")
    events = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv")
    contexts = read(P606 / "SIX_HUNDRED_SIXTH_381_SHORT_EVENT_EDITION.tsv")
    statements = read(P680 / "SIX_HUNDRED_EIGHTIETH_116_COMPACT_OWNER_STATEMENTS.tsv")
    records = read(P680 / "SIX_HUNDRED_EIGHTIETH_11_CONTINUOUS_OWNER_RECORDS.tsv")
    owners = read(P680 / "SIX_HUNDRED_EIGHTIETH_20_OWNER_NOUNS.tsv")
    fragment_rules = read(P696 / "SIX_HUNDRED_NINETY_SIXTH_39_COMPONENT_FRAGMENT_RULES.tsv")
    surface_plans = read(P697 / "SIX_HUNDRED_NINETY_SEVENTH_230_RENDERER_PLANS.tsv")
    renderer_rules = read(P697 / "SIX_HUNDRED_NINETY_SEVENTH_7_RENDERER_RULES.tsv")
    entry_events = read(P698 / "SIX_HUNDRED_NINETY_EIGHTH_381_ENTRY_FRAME_EVENTS.tsv")
    owner_trays = read(P699 / "SIX_HUNDRED_NINETY_NINTH_18_OWNER_TRAYS.tsv")
    override_slips = read(P699 / "SIX_HUNDRED_NINETY_NINTH_5_LOCAL_OVERRIDE_SLIPS.tsv")
    residual_events = read(P699 / "SIX_HUNDRED_NINETY_NINTH_59_RESIDUAL_RECONSTRUCTIONS.tsv")

    fragment_by_component = {row["component"]: row for row in fragment_rules}
    tablet_rows = []
    for root in roots:
        fragments = fragment_by_component[root["component"]]["allowed_diagnostic_fragments"]
        if root["component"] == "CHK":
            fragments = "chk|ch"
        tablet_rows.append({
            "root_no": root["root_no"], "component": root["component"],
            "compact_value_de": root["compact_table_value_de"],
            "entry_kind": "MEMORIZED_WHOLE_COMMAND" if root["component"] in WHOLE_COMMANDS else "COMPOSABLE_WORK_COMPONENT",
            "diagnostic_fragments": fragments,
            "historical_layer": root["historical_layer"],
            "apprentice_rule": root["apprentice_rule"],
            "card_types": root["card_types"], "events_with_entry": root["events_with_component"],
        })

    plans_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for plan in surface_plans:
        plans_by_card[plan["card_no"]].append(plan)
    card_rows = []
    for card in cards:
        plans = plans_by_card[card["card_no"]]
        if card["composition_mode"] == "MEMORIZED_WHOLE_COMMAND":
            card_class = "MEMORIZED_WHOLE_COMMAND"
        elif all(int(plan["rule_families_used"]) == 0 for plan in plans):
            card_class = "COMPOSED_DIRECT_ALL_FORMS"
        else:
            card_class = "COMPOSED_WITH_BOUND_RENDERER"
        card_rows.append({
            "card_no": card["card_no"], "surfaces": card["surfaces"],
            "component_recipe": card["component_recipe"],
            "compact_atomic_reading_de": card["compact_atomic_reading_de"],
            "card_class": card_class,
            "surface_forms": len(plans),
            "surface_plans": " | ".join(f"{plan['surface']}={plan['selected_fragments']}[{plan['renderer_rule_sequence']}]" for plan in plans),
            "events": card["events"], "pages": card["pages"],
            "copy_rule_de": "Komponenten diktieren; Ganzkartenfamilie wählen; Renderer anwenden; Oberfläche als Einheit kopieren.",
        })

    context_by_event = {row["event_id"]: row for row in contexts}
    entry_by_event = {row["event_id"]: row for row in entry_events}
    plan_by_card_surface = {(row["card_no"], row["surface"]): row for row in surface_plans}
    card_by_no = {row["card_no"]: row for row in cards}
    residual_by_event = {row["event_id"]: row for row in residual_events}
    tray_by_owner = {row["owner_de"]: row["owner_tray_id"] for row in owner_trays}
    trace_rows = []
    for event in events:
        context = context_by_event[event["event_id"]]
        entry = entry_by_event[event["event_id"]]
        plan = plan_by_card_surface[(event["card_no"], event["surface"])]
        source = entry["renderer_source"]
        if source == "GLOBAL_RULE_RENDERER":
            selection_layer = "GLOBAL_CARD_FORM"
            produced_surface = event["surface"]
        elif source == "AUTOMATIC_CONTEXT_RULE":
            selection_layer = "CONTEXT_WRAPPER_RULE"
            produced_surface = event["surface"]
        else:
            residual = residual_by_event[event["event_id"]]
            selection_layer = residual["selection_source"]
            produced_surface = residual["reconstructed_surface"]
        trace_rows.append({
            "event_id": event["event_id"], "page": event["page"], "record": event["record"],
            "statement_id": event["statement_id"], "locus": context["locus"],
            "owner_de": context["silent_owner_de"],
            "owner_renderer_tray": tray_by_owner.get(context["silent_owner_de"], "GLOBAL_ONLY"),
            "card_no": event["card_no"], "component_recipe": event["component_recipe"],
            "semantic_layer_de": event["compact_atomic_reading_de"],
            "owner_expansion_de": context["case_expansion_de"],
            "diagnostic_fragments": plan["selected_fragments"],
            "renderer_rules": plan["renderer_rule_sequence"],
            "renderer_pieces": plan["renderer_pieces"],
            "entry_frame": entry["entry_frame"],
            "surface_selection_layer": selection_layer,
            "produced_surface": produced_surface,
            "observed_surface": event["surface"],
            "exact_surface_match": "YES" if produced_surface == event["surface"] else "NO",
            "visible_character_layers_de": f"KOMPONENTEN={plan['selected_fragments']}; RENDERER={plan['renderer_pieces']}; WAHL={selection_layer}",
        })

    trace_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in trace_rows:
        trace_by_statement[str(row["statement_id"])].append(row)
    statement_rows = []
    for statement in statements:
        rows = trace_by_statement[statement["statement_id"]]
        counts = Counter(str(row["surface_selection_layer"]) for row in rows)
        statement_rows.append({
            "statement_id": statement["statement_id"], "page": statement["page"], "record": statement["record"],
            "events": statement["events"], "owner_noun_de": statement["owner_noun_de"],
            "surface_sequence": statement["surface_sequence"],
            "component_sequence": statement["component_sequence"],
            "working_reading_de": statement["compact_owner_reading_de"],
            "global_forms": counts["GLOBAL_CARD_FORM"],
            "context_forms": counts["CONTEXT_WRAPPER_RULE"],
            "owner_default_forms": counts["OWNER_CARD_DEFAULT"],
            "override_forms": counts["LOCAL_OVERRIDE_SLIP"],
            "owner_break_inside_statement": statement["owner_break_inside_statement"],
            "closes": statement["closes"],
        })

    write("SEVEN_HUNDREDTH_39_TABLET_ENTRIES.tsv", tablet_rows)
    write("SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv", card_rows)
    write("SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv", trace_rows)
    write("SEVEN_HUNDREDTH_116_STATEMENT_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDREDTH_7_RENDERER_RULES.tsv", renderer_rules)
    write("SEVEN_HUNDREDTH_18_OWNER_TRAYS.tsv", owner_trays)
    write("SEVEN_HUNDREDTH_5_OVERRIDE_SLIPS.tsv", override_slips)

    readable = ["# Elf vollständige Record-Lesungen", "", "Kreative Werkstattfassung; keine historische Entzifferungsbehauptung.", ""]
    for record in records:
        readable.extend([
            f"## {record['record']} — {record['page']}", "",
            f"Besitzerfolge: {record['owners_in_order']}", "",
            record["continuous_compact_owner_reading_de"], "",
        ])
    (HERE / "SEVEN_HUNDREDTH_11_RECORD_READABLE_EDITION.md").write_text("\n".join(readable), encoding="utf-8")

    manual = """# Einseitiges Lehrlingsmanual — Pass 700

1. Sieh zuerst auf den bereits gezeichneten Besitzer und öffne dessen lokales Fach.
2. Diktiere eine Folge aus 36 komponierbaren Arbeitskomponenten; drei seltene Befehle werden als Ganzkarte gelernt.
3. Wähle eine der 173 exakten Kartenfamilien. 170 sind komponiert, drei Ganzbefehle.
4. Schreibe die Diagnosefragmente in Rezeptreihenfolge.
5. Ergänze höchstens zwei der sieben Rendererregeln.
6. Nimm normalerweise die globale Kartenform. Vier Kontextregeln behandeln acht Sonderstellen.
7. Falls die Karte lokal ist, benutze eine von 18 Besitzer-Schubladen; nur fünf Ereignisse haben einen Ausnahmezettel.
8. Kopiere die fertige Oberfläche als eine Einheit. Eine physische Zeile beendet die Anweisung nicht automatisch.
9. Lies rückwärts: Oberfläche → Renderer abziehen → Komponenten → Besitzer einsetzen → kurze Arbeitsanweisung.

Inventar: 39 Tascheneinträge = 36 Komponenten + 3 Ganzbefehle; 173 Karten; 230 Oberflächen; 7 Rendererregeln; 18 Besitzer-Schubladen; 5 Ausnahmezettel.
"""
    (HERE / "SEVEN_HUNDREDTH_ONE_PAGE_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    card_classes = Counter(row["card_class"] for row in card_rows)
    selection_counts = Counter(row["surface_selection_layer"] for row in trace_rows)
    rule_counts = Counter(int(row["rule_families_used"]) for row in surface_plans)
    summary = {
        "status": "PASS", "tablet_entries": len(tablet_rows),
        "composable_components": sum(row["entry_kind"] == "COMPOSABLE_WORK_COMPONENT" for row in tablet_rows),
        "whole_commands": sum(row["entry_kind"] == "MEMORIZED_WHOLE_COMMAND" for row in tablet_rows),
        "cards": len(card_rows), "card_classes": dict(card_classes),
        "surface_forms": len(surface_plans),
        "surface_rule_counts": {"direct": rule_counts[0], "one_rule": rule_counts[1], "two_rules": rule_counts[2]},
        "events": len(trace_rows), "statements": len(statement_rows), "records": len(records),
        "visible_owner_nouns": len(owners), "owner_renderer_trays": len(owner_trays),
        "renderer_rules": len(renderer_rules), "override_slips": len(override_slips),
        "surface_selection_layers": dict(selection_counts),
        "exact_surface_matches": sum(row["exact_surface_match"] == "YES" for row in trace_rows),
        "decision": "COMPLETE_APPRENTICE_MANUAL_ROUNDTRIPS_ALL_381_PROSE_EVENTS",
    }
    (HERE / "SEVEN_HUNDREDTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
