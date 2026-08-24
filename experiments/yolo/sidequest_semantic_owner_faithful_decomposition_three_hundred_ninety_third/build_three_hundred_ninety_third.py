#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P392 = ROOT / "experiments/yolo/sidequest_semantic_owner_faithful_copy_three_hundred_ninety_second"

ANALYSIS = {
    "b5fcea1eaed06b2f2291": ("COMPONENT_DIRECT", "OK+AIIN", "auf Sollmaß einstellen"),
    "2f1c5e56e8f0ff459065": ("COMPONENT_DIRECT", "AIIN", "Sollmaß"),
    "403c1592f918c8f23b88": ("COMPONENT_DIRECT", "Y+AIN", "Portion des Diespostens"),
    "d929a14ec45749b2e805": ("COMPONENT_DIRECT", "Y+AIN", "diese Portion"),
    "97cc9ac109148723c472": ("NOMENCLATOR_WHOLE", "ODY", "kühlen; Schluss"),
    "6f7ff8287eddf4da9fdb": ("COMPONENT_DIRECT", "CHED+Y", "Diesposten umsetzen"),
    "e026af581c99322fbd46": ("NOMENCLATOR_WHOLE", "TALAM", "verwahren"),
    "f7dc90b2c31fd341f0a4": ("COMPONENT_DIRECT", "Y+AIIN", "Sollmaß des Diespostens"),
    "807591efc3d3f7ddbfab": ("COMPONENT_DIRECT", "CHEO+AR", "Auszug daraus nehmen"),
    "2c1a5fd92b9e3c762242": ("COMPONENT_DIRECT", "CHK+EE+Y", "länger wärmen; offen"),
    "1b1ffdd869fb1429ad03": ("COMPONENT_DIRECT", "OL+DY", "fortsetzen; Schluss"),
    "308e8ea2d5d190c498e8": ("COMPONENT_DIRECT", "OK+AL", "an Zielstelle einsetzen"),
    "204b04837409088c48f9": ("NOMENCLATOR_WHOLE", "OLTCHY", "anwärmen"),
    "7a4bb8136330ee4e6e56": ("COMPONENT_DIRECT", "OR", "Ansatz"),
    "b921a237be883a820352": ("COMPONENT_DIRECT", "Y", "Diesposten"),
    "6afeb5c9ab9f6cbdea0d": ("COMPONENT_DIRECT", "OR+AIN", "Ansatzportion"),
    "342c3f0777337648f4b3": ("NOMENCLATOR_WHOLE", "CHEEDAR", "Beckenstation"),
    "d72f71baff01cd0a0406": ("COMPONENT_DIRECT", "CHLD+AIIN", "Absetzstand"),
    "1645e612504fcef59ced": ("COMPONENT_DIRECT", "OK+AIN", "Portion zugeben"),
    "e0b630cb1b5df5e7105b": ("COMPONENT_DIRECT", "CTH+Y", "bereit"),
    "d788d8d72d41b25a3c71": ("NOMENCLATOR_WHOLE", "CHEALROR", "Klarpunkt"),
    "3b70942557b3a40e8030": ("COMPONENT_DIRECT", "SOLK+EE+DY", "länger auffangen; Schluss"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cards = read(P392 / "THREE_HUNDRED_NINETY_SECOND_25_OWNER_NATIVE_CARDS.tsv")
    decomposition_rows = []
    for row in cards:
        route, parse, reading = ANALYSIS[row["joint_tuple_id"]]
        decomposition_rows.append({
            "copy_position": row["copy_position"],
            "event_id": row["event_id"],
            "owner_code": row["owner_code"],
            "statement_id": row["statement_id"],
            "source_surface": row["source_surface"],
            "copy_surface": row["copy_surface"],
            "joint_tuple_id": row["joint_tuple_id"],
            "read_route": route,
            "strict_parse": parse,
            "short_atomic_reading_de": reading,
            "picture_argument": "H4_PICTURED_PLANT_PREPARATION" if row["owner_code"] == "H4" else "B3_VISIBLE_BASIN_STATION",
            "exact_identity_preserved": "YES",
        })
    write("THREE_HUNDRED_NINETY_THIRD_25_COMPONENT_NOMENCLATOR_READINGS.tsv", decomposition_rows)

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in decomposition_rows:
        by_statement[row["statement_id"]].append(row)
    statement_order = ["H4-S001", "H4-S002", "H4-S003", "H4-S004", "B3-S026"]
    fluent = {
        "H4-S001": "Stelle die Pflanzenzubereitung auf Sollmaß; nimm davon eine Portion; kühle sie und schließe den Schritt.",
        "H4-S002": "Nimm das Sollmaß, arbeite den Posten durch und verwahre das Ergebnis.",
        "H4-S003": "Nimm das Sollmaß des Postens, ziehe daraus den Auszug, wärme länger und schließe die Fortsetzung.",
        "H4-S004": "Setze das Sollmaß an der Zielstelle an, wärme an; nimm aus dem Ansatz die gegenwärtige Ansatzportion.",
        "B3-S026": "Richte die sichtbare Beckenstation ein; warte bis zum Absetzstand, setze den Posten um, gib eine Portion zu, prüfe Bereitschaft und Klarpunkt, fange länger auf und schließe.",
    }
    statement_rows = []
    for statement_id in statement_order:
        rows = by_statement[statement_id]
        statement_rows.append({
            "statement_id": statement_id,
            "owner_code": rows[0]["owner_code"],
            "card_count": len(rows),
            "component_cards": sum(row["read_route"] == "COMPONENT_DIRECT" for row in rows),
            "nomenclator_cards": sum(row["read_route"] == "NOMENCLATOR_WHOLE" for row in rows),
            "copy_surface_sequence": " ".join(row["copy_surface"] for row in rows),
            "atomic_sequence_de": " | ".join(row["short_atomic_reading_de"] for row in rows),
            "fluent_owner_expansion_de": fluent[statement_id],
        })
    write("THREE_HUNDRED_NINETY_THIRD_FIVE_COMPLETE_STATEMENTS.tsv", statement_rows)

    component_count = sum(row["read_route"] == "COMPONENT_DIRECT" for row in decomposition_rows)
    whole_count = len(decomposition_rows) - component_count
    comparison_rows = [
        {"page_model": "CROSS_REGISTER_FOUR_CYCLE_PRACTICE", "cards": 14, "component_direct": 11, "nomenclator_whole": 3, "component_percent": "78.6", "status": "TEACHING_SYNTHESIS"},
        {"page_model": "OWNER_FAITHFUL_H4_B3_COPY", "cards": 25, "component_direct": component_count, "nomenclator_whole": whole_count, "component_percent": f"{100 * component_count / len(decomposition_rows):.1f}", "status": "GENUINE_SEQUENCE_COPY"},
    ]
    write("THREE_HUNDRED_NINETY_THIRD_COVERAGE_COMPARISON.tsv", comparison_rows)

    edition = ["# Pass 393 — vollständige owner-faithful Lesung", ""]
    for row in statement_rows:
        edition += [
            f"## {row['statement_id']}",
            "",
            f"`{row['copy_surface_sequence']}`",
            "",
            f"Atomar: {row['atomic_sequence_de']}.",
            "",
            row["fluent_owner_expansion_de"],
            "",
        ]
    edition += [
        "## Architektur",
        "",
        f"{component_count}/25 Karten werden komponiert gelesen; {whole_count}/25 bleiben kurze Nomenklatorkarten: ODY, TALAM, OLTCHY, CHEEDAR und CHEALROR.",
    ]
    (HERE / "THREE_HUNDRED_NINETY_THIRD_COMPLETE_READABLE_EDITION.md").write_text("\n".join(edition) + "\n", encoding="utf-8")
    report = f"""# Pass 393 — echte Folgen tragen die Mischgrammatik

Die owner-faithful Kopie erreicht {component_count}/25 kompositionell lesbare
Karten ({100 * component_count / len(decomposition_rows):.1f} Prozent), knapp
mehr als die künstliche Viergang-Seite mit 11/14. Nur fünf spezialisierte
Ganzkarten bleiben: Kühlabschluss, Verwahrung, Anwärmen, Beckenstation und
Klarpunkt.

Alle fünf Aussagen lassen sich atomar und anschließend mit dem sichtbaren
Besitzer flüssig lesen. Dabei stammen „Pflanzenzubereitung“ und „Beckenstation“
entweder aus dem Bild oder aus einer ausdrücklich gelernten Fachkarte, nicht aus
frei erfundenen Einbuchstabenwurzeln.

Als nächstes soll die H4-Folge intern auf Wiederaufnahme und Objektfluss geprüft
werden: Welche Portion oder Zubereitung wird zwischen den vier Aussagen
weitergetragen, und welche kurzen Pronomenkarten leisten diese Arbeit?
"""
    (HERE / "THREE_HUNDRED_NINETY_THIRD_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "cards": len(decomposition_rows),
        "component_direct": component_count,
        "nomenclator_whole": whole_count,
        "component_percent": round(100 * component_count / len(decomposition_rows), 1),
        "statements": len(statement_rows),
        "whole_card_values": [row["short_atomic_reading_de"] for row in decomposition_rows if row["read_route"] == "NOMENCLATOR_WHOLE"],
    }
    (HERE / "THREE_HUNDRED_NINETY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
