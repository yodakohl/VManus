#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"
P486 = ROOT / "experiments/yolo/sidequest_semantic_flexible_renderer_four_hundred_eighty_sixth"

TARGET = "B1-S002"
MACRO = "BECKENZULAUF ZWEIFACH DOSIEREN UND TEMPERIEREN"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv")
    target = [row for row in events if row["statement_id"] == TARGET]
    manual = read(P486 / "FOUR_HUNDRED_EIGHTY_SIXTH_169_ITEM_GENERATIVE_MANUAL.tsv")
    ledger = read(P486 / "FOUR_HUNDRED_EIGHTY_SIXTH_776_ADMISSIBLE_SURFACE_LEDGER.tsv")

    phases = {
        "E102": ("P1_ZULAUF_EINSTELLEN", "Sollmaß für die Arbeitsflüssigkeit setzen."),
        "E103": ("P1_ZULAUF_EINSTELLEN", "Arbeitsflüssigkeit in den sichtbaren Lauf geben."),
        "E104": ("P1_ZULAUF_EINSTELLEN", "Den Lauf auf das gemeinsame Becken richten."),
        "E105": ("P1_ZULAUF_EINSTELLEN", "Aus der Arbeitsflüssigkeit speisen."),
        "E106": ("P1_ZULAUF_EINSTELLEN", "Den eingestellten Zulauf fortführen."),
        "E107": ("P2_DOPPELTE_PORTION", "Erste Portion derselben Laufflüssigkeit abteilen."),
        "E108": ("P2_DOPPELTE_PORTION", "Zweite parallele Portion aus derselben Laufflüssigkeit abteilen."),
        "E109": ("P2_DOPPELTE_PORTION", "Beide Portionen an das gemeinsame Becken führen."),
        "E110": ("P2_DOPPELTE_PORTION", "Die Doppelportion fortführen."),
        "E111": ("P2_DOPPELTE_PORTION", "Die Doppelportion weiter abkühlen oder temperieren."),
        "E112": ("P2_DOPPELTE_PORTION", "Die temperierte Doppelportion weiterführen."),
        "E113": ("P3_NACHANSATZ_HALTEGANG", "Aus dem temperierten Vorrat den nächsten Ansatz setzen."),
        "E114": ("P3_NACHANSATZ_HALTEGANG", "Den Nachansatz fortführen."),
        "E115": ("P3_NACHANSATZ_HALTEGANG", "Kurz an der Durchgangsstelle halten."),
        "E116": ("P3_NACHANSATZ_HALTEGANG", "Den Sollwert am Durchgang prüfen oder setzen."),
        "E117": ("P3_NACHANSATZ_HALTEGANG", "Länger am gemeinsamen Becken halten."),
        "E118": ("P3_NACHANSATZ_HALTEGANG", "Den Sollwert am Becken prüfen oder setzen."),
        "E119": ("P3_NACHANSATZ_HALTEGANG", "Durch den lokalen Durchlass führen."),
        "E120": ("P3_NACHANSATZ_HALTEGANG", "In den nächsten Zustand umsetzen und den Schritt schließen."),
    }
    trace = []
    for row in target:
        phase, revised = phases[row["event_id"]]
        old_after = row["active_after_de"]
        if row["event_id"] == "E107":
            revised_after = "erste Portion derselben Laufflüssigkeit"
        elif row["event_id"] == "E108":
            revised_after = "zwei parallele Portionen derselben Laufflüssigkeit"
        elif row["event_id"] in {"E109", "E110", "E111", "E112"}:
            revised_after = "temperierte Doppelportion am gemeinsamen Becken"
        elif row["event_id"] == "E113":
            revised_after = "Nachansatz aus der temperierten Doppelportion"
        elif row["event_id"] in {"E114", "E115", "E116", "E117", "E118", "E119", "E120"}:
            revised_after = "gehaltener Nachansatz am gemeinsamen Becken"
        else:
            revised_after = old_after
        trace.append({
            "event_order": len(trace) + 1,
            "event_id": row["event_id"],
            "locus": row["locus"],
            "field_id": row["field_id"],
            "surface": row["surface"],
            "component_parse": row["component_parse"],
            "macro_phase": phase,
            "old_event_reading_de": row["pass481_event_de"],
            "revised_event_reading_de": revised,
            "old_active_after_de": old_after,
            "revised_active_after_de": revised_after,
            "owner_code": row["owner_code"],
            "closes_step": row["closes_step"],
        })
    write("FOUR_HUNDRED_EIGHTY_NINTH_19_EVENT_MACRO_TRACE.tsv", trace)

    nodes = [
        {"node_id": "N1", "object_de": "Arbeitsflüssigkeit im gemeinsamen Becken", "created_at": "OWNER", "role": "SOURCE_STOCK"},
        {"node_id": "N2", "object_de": "eingestellter Flüssigkeitslauf", "created_at": "E103", "role": "FLOW"},
        {"node_id": "N3", "object_de": "erste Portion der Laufflüssigkeit", "created_at": "E107", "role": "SIBLING_PORTION_1"},
        {"node_id": "N4", "object_de": "zweite Portion derselben Laufflüssigkeit", "created_at": "E108", "role": "SIBLING_PORTION_2"},
        {"node_id": "N5", "object_de": "temperierte Doppelportion am Becken", "created_at": "E111", "role": "COMBINED_WORKING_STOCK"},
        {"node_id": "N6", "object_de": "Nachansatz aus der Doppelportion", "created_at": "E113", "role": "SECOND_STAGE_BATCH"},
        {"node_id": "N7", "object_de": "kurz gehaltener Nachansatz am Durchgang", "created_at": "E115", "role": "SHORT_HOLD_STATE"},
        {"node_id": "N8", "object_de": "länger gehaltener Nachansatz am Becken", "created_at": "E117", "role": "LONG_HOLD_STATE"},
        {"node_id": "N9", "object_de": "umgesetzter Beckenbestand", "created_at": "E120", "role": "COMMITTED_OUTPUT"},
    ]
    write("FOUR_HUNDRED_EIGHTY_NINTH_NINE_OBJECT_NODES.tsv", nodes)

    edges = [
        ("E102", "N1", "N1", "SOLLWERT_SETZEN"), ("E103", "N1", "N2", "LAUF_AKTIVIEREN"),
        ("E104", "N2", "N2", "AUF_BECKEN_RICHTEN"), ("E105", "N1", "N2", "AUS_QUELLE_SPEISEN"),
        ("E106", "N2", "N2", "FORTSETZEN"), ("E107", "N2", "N3", "ERSTE_PORTION"),
        ("E108", "N2", "N4", "ZWEITE_PARALLELE_PORTION"), ("E109", "N3|N4", "N5", "ZUM_BECKEN_FUEHREN"),
        ("E110", "N5", "N5", "FORTSETZEN"), ("E111", "N5", "N5", "TEMPERIEREN"),
        ("E112", "N5", "N5", "WEITERFUEHREN"), ("E113", "N5", "N6", "NACHANSATZ_SETZEN"),
        ("E114", "N6", "N6", "FORTSETZEN"), ("E115", "N6", "N7", "KURZ_HALten"),
        ("E116", "N7", "N7", "SOLLWERT_SETZEN"), ("E117", "N7", "N8", "LAENGER_HALTen"),
        ("E118", "N8", "N8", "SOLLWERT_SETZEN"), ("E119", "N8", "N8", "DURCHLASS"),
        ("E120", "N8", "N9", "UMSETZEN_UND_SCHLIESSEN"),
    ]
    edge_rows = [{"edge_order": index + 1, "event_id": event, "source_node": source, "target_node": target_node, "operation": operation} for index, (event, source, target_node, operation) in enumerate(edges)]
    write("FOUR_HUNDRED_EIGHTY_NINTH_19_OBJECT_EDGES.tsv", edge_rows)

    candidates = [
        {"candidate": "A", "macro_name_de": MACRO, "source_quantity_path_target_fit": 6, "image_owner_fit": 5, "two_portion_fit": 5, "invented_content_cost": 1, "total": 15, "decision": "SELECT"},
        {"candidate": "B", "macro_name_de": "ZWEITEILIGES BAD BEREITEN UND LAENGER ANWENDEN", "source_quantity_path_target_fit": 5, "image_owner_fit": 5, "two_portion_fit": 4, "invented_content_cost": 3, "total": 11, "decision": "RIVAL"},
        {"candidate": "C", "macro_name_de": "ZWEI POSTEN DURCH EIN GENERISCHES FORMULAR FUEHREN", "source_quantity_path_target_fit": 4, "image_owner_fit": 1, "two_portion_fit": 4, "invented_content_cost": 1, "total": 8, "decision": "RIVAL"},
    ]
    write("FOUR_HUNDRED_EIGHTY_NINTH_THREE_MACRO_READINGS.tsv", candidates)

    revised_manual = []
    for row in manual:
        new = dict(row)
        if row["item_id"] == "W:B1-S002":
            new["teaching_value_or_rule_de"] = MACRO + ": " + " ".join(item["revised_event_reading_de"] for item in trace)
            new["source_artifact"] = "PASS489_B1_DOUBLE_CHARGE_MACRO"
        revised_manual.append(new)
    write("FOUR_HUNDRED_EIGHTY_NINTH_169_ITEM_MACRO_MANUAL.tsv", revised_manual)

    macro_by_event = {row["event_id"]: row for row in trace}
    revised_ledger = []
    for row in ledger:
        new = dict(row)
        if row["item_id"] in macro_by_event:
            item = macro_by_event[row["item_id"]]
            new["semantic_layer"] = "LOCAL_NOMENCLATOR_MACRO"
            new["syntax_item"] = "W:B1-S002"
            new["concrete_reading_de"] = item["revised_event_reading_de"]
            new["local_macro"] = MACRO
            new["macro_phase"] = item["macro_phase"]
        else:
            new["local_macro"] = "NONE"
            new["macro_phase"] = "NONE"
        revised_ledger.append(new)
    write("FOUR_HUNDRED_EIGHTY_NINTH_776_MACRO_REVISED_LEDGER.tsv", revised_ledger)

    translation = (
        "Setze das Sollmaß. Gib die Arbeitsflüssigkeit in den Lauf und richte ihn auf das gemeinsame Becken. "
        "Teile daraus eine Portion und eine zweite parallele Portion ab, führe beide zum Becken, lasse sie weiter abkühlen und führe sie weiter. "
        "Setze daraus den nächsten Ansatz an; halte ihn kurz am Durchgang bis zum Sollwert, dann länger am Becken bis zum Sollwert, führe ihn hindurch und setze ihn um. Schluss."
    )
    (HERE / "FOUR_HUNDRED_EIGHTY_NINTH_COMPLETE_B1_S002_READING.md").write_text(
        f"# {MACRO}\n\n{translation}\n\n"
        "Die Bildadresse ist das gemeinsame zweireihige Becken. Die Figuren liefern den Besitzer und den Bade-/Arbeitskontext, nicht eine ausdrücklich geschriebene Krankheit.\n",
        encoding="utf-8",
    )

    summary = {
        "status": "PASS", "statement_id": TARGET, "events": len(trace), "phases": len({row["macro_phase"] for row in trace}),
        "object_nodes": len(nodes), "object_edges": len(edge_rows), "parallel_portions": 2,
        "selected_macro": MACRO, "manual_items": len(revised_manual), "ledger_groups": len(revised_ledger),
        "component_meanings_changed": 0, "surface_forms_changed": 0,
    }
    (HERE / "FOUR_HUNDRED_EIGHTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
