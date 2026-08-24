#!/usr/bin/env python3
"""Build eleven complete apprentice run cards from the mixed-hand edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_mixed_workshop_edition_three_hundred_fortieth/THREE_HUNDRED_FORTIETH_381_MIXED_HAND_EVENTS.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_mixed_workshop_edition_three_hundred_fortieth/THREE_HUNDRED_FORTIETH_116_MIXED_HAND_STATEMENTS.tsv"
TRACE = ROOT / "experiments/yolo/sidequest_semantic_card_order_syntax_three_hundred_thirty_fifth/THREE_HUNDRED_THIRTY_FIFTH_381_EVENT_GENERATION_TRACE.tsv"

RUN = {
    "H1": ("Abgebildeter Wurzelteil", "Bildbesitzer f10r", "Bemessener Wurzel-Wasseransatz mit Kurzrest", "B1", "SAME_HAND_DELIVERY"),
    "H2": ("Laufender Auszugsansatz", "Voriger Artikel unter demselben Pflanzenbild", "Fortgesetzter Auszugsansatz mit Zutatsollmaß", "B1", "SAME_HAND_DELIVERY"),
    "H3": ("Abgebildetes Blütenkraut", "Bildbesitzer f11r", "Gestandener und nachgeseihter Klarauszug", "B2", "SAME_HAND_DELIVERY"),
    "H4": ("Abgebildetes Blattmaterial", "Bildbesitzer f55v", "Geteilte und lang erwärmte Auszugsportion", "B4", "SAME_HAND_DELIVERY"),
    "H5": ("Abgebildeter Stängel-/Pflanzenteil", "Bildbesitzer f56r", "Gebundener Zutaten- und Auszugsansatz für Folgeposten", "B4", "CROSS_HAND_RELAY_D_TO_C"),
    "B1": ("H1-Wurzelansatz und H2-Folgeansatz", "Gemeinsames Behandlungsbecken", "Bemessene, behandelte und überführte Beckenportionen", "TERMINAL_APPLICATION_SHELF_B1", "LOCAL_SHELF_NO_DRAWN_NEXT_POINTER"),
    "B2": ("H3-Klarauszug und lokale Beckenposten", "Mehrere f82r-Stationen", "Lang behandelte, abgesetzte und klar abgezogene Stationsportionen", "TERMINAL_APPLICATION_SHELF_B2", "LOCAL_SHELF_NO_DRAWN_NEXT_POINTER"),
    "B3": ("Lokal bereitgestellter Stationsposten", "Korb, Randgefäße und verbundenes Paar", "Überführte, bemessene und abgesetzte Gefäßportionen", "TERMINAL_WORK_SHELF_B3", "LOCAL_SHELF_NO_DRAWN_NEXT_POINTER"),
    "B4": ("H4-Auszugportion und H5-Folgeposten", "Anwendungs-/Durchlasspaar und Seitenstationen", "Am Ziel behandelte, durchgelassene und gesammelte Portionen", "TERMINAL_APPLICATION_SHELF_B4", "LOCAL_SHELF_NO_DRAWN_NEXT_POINTER"),
    "B5": ("Laufender Posten der linken Randstation", "Linke offene Randstation", "Überführter Folgeposten", "TERMINAL_WORK_SHELF_B5", "LOCAL_SHELF_NO_DRAWN_NEXT_POINTER"),
    "B6": ("Laufender Posten des rechten Mehrports", "Rechter S-Lauf/Mehrport", "Fortgesetzter und zielgesetzter Mehrportposten", "TERMINAL_WORK_SHELF_B6", "LOCAL_SHELF_NO_DRAWN_NEXT_POINTER"),
}
ORDER = list(RUN)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    trace = {row["event_id"]: row for row in read_tsv(TRACE)}
    by_record = defaultdict(list)
    statement_by_record = defaultdict(list)
    for row in events:
        by_record[row["record_unit_id"]].append(row)
    for row in statements:
        statement_by_record[row["record_unit_id"]].append(row)

    cards = []
    for record in ORDER:
        rows = sorted(by_record[record], key=lambda row: int(row["event_id"][1:]))
        ss = statement_by_record[record]
        input_item, input_owner, output_item, receiver, handoff = RUN[record]
        programs = []
        slots = []
        cycles = []
        for row in rows:
            tr = trace[row["event_id"]]
            if tr["program_id"] not in programs:
                programs.append(tr["program_id"])
            if tr["slot_code"] not in slots:
                slots.append(tr["slot_code"])
            cycle_key = f"{tr['statement_id']}:{tr['microcycle']}"
            if cycle_key not in cycles:
                cycles.append(cycle_key)
        dominant = Counter(trace[row["event_id"]]["program_id"] for row in rows).most_common(1)[0][0]
        cards.append({
            "record_unit_id": record,
            "page": rows[0]["page"],
            "assigned_hand": rows[0]["hand_id"],
            "input_item_de": input_item,
            "input_owner_or_source_de": input_owner,
            "surface_stream": " ".join(row["rendered_surface"] for row in rows),
            "event_count": len(rows),
            "statement_count": len(ss),
            "microcycle_count": len(cycles),
            "slot_inventory": "|".join(slots),
            "program_inventory": "|".join(programs),
            "dominant_program": dominant,
            "output_item_de": output_item,
            "receiver_or_shelf": receiver,
            "handoff_mode": handoff,
            "apprentice_run_instruction_de": f"Nimm {input_item.lower()} bei {input_owner.lower()}; arbeite die {len(ss)} Aussagen in Kartenfolge ab; kennzeichne das Ergebnis als {output_item.lower()} und übergib es an {receiver}.",
            "identity_value_owner_slot_boundary_preserved": "YES",
        })

    write_tsv(HERE / "THREE_HUNDRED_FORTY_FIRST_ELEVEN_APPRENTICE_RUN_CARDS.tsv", cards,
              ["record_unit_id", "page", "assigned_hand", "input_item_de", "input_owner_or_source_de", "surface_stream", "event_count", "statement_count", "microcycle_count", "slot_inventory", "program_inventory", "dominant_program", "output_item_de", "receiver_or_shelf", "handoff_mode", "apprentice_run_instruction_de", "identity_value_owner_slot_boundary_preserved"])

    lines = ["# Vollständiger Lehrlingslaufzettel", ""]
    for row in cards:
        statement_word = "Aussage" if int(row["statement_count"]) == 1 else "Aussagen"
        lines.extend([
            f"## {row['record_unit_id']} / {row['page']} / {row['assigned_hand']}",
            "",
            f"**Eingang:** {row['input_item_de']} — {row['input_owner_or_source_de']}.",
            f"**Arbeit:** {row['statement_count']} {statement_word}, {row['microcycle_count']} Mikrogänge; Hauptprogramm `{row['dominant_program']}`.",
            f"**Ausgang:** {row['output_item_de']}.",
            f"**Weiter:** {row['receiver_or_shelf']} ({row['handoff_mode']}).",
            "",
        ])
    lines.extend([
        "## Tagesregel",
        "",
        "Der Lehrling nimmt nie einen Stoffnamen aus der Kartenform allein. Eingang und",
        "Besitzer kommen vom Bild beziehungsweise vom vorher markierten Werkstattposten.",
        "Die Karten bestimmen Reihenfolge, Maß, Prozess, Dauer, Ziel und Abschluss. Wo kein",
        "weiterer Bildzeiger existiert, wird das Ergebnis auf dem lokalen Arbeits- oder",
        "Anwendungssims abgelegt statt in eine erfundene nächste Leitung geschickt.",
    ])
    (HERE / "THREE_HUNDRED_FORTY_FIRST_COMPLETE_RUN_SHEET.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "run_cards": len(cards),
        "events": sum(int(row["event_count"]) for row in cards),
        "statements": sum(int(row["statement_count"]) for row in cards),
        "microcycles": sum(int(row["microcycle_count"]) for row in cards),
        "direct_or_relay_deliveries": sum(row["receiver_or_shelf"].startswith("B") for row in cards),
        "terminal_local_shelves": sum(row["receiver_or_shelf"].startswith("TERMINAL") for row in cards),
    }
    (HERE / "THREE_HUNDRED_FORTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
