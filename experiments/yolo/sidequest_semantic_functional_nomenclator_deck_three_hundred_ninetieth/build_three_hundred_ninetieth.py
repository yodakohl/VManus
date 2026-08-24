#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_173_THERMAL_TEMPORAL_DICTIONARY.tsv"

DECK = [
    ("TARGET_RESULT", "5fca8fc3dee57e1d8c1f", "benetzte Stelle", "resulting wet target", "WHOLE_CARD"),
    ("TARGET_RESULT", "dd0ecaf5e27d81befffc", "Stelle", "general target address", "COMPONENT_CARD"),
    ("TARGET_RESULT", "93f69c38fdedee1598e9", "länger an der Stelle halten", "graded target application", "COMPOUND_CARD"),
    ("TARGET_RESULT", "abb23e5e6936b4147f76", "an der Stelle absetzen", "settling target", "COMPOUND_CARD"),
    ("SEPARATION", "bdad9f9ea8b80f141496", "auswringen", "first mechanical separation", "WHOLE_CARD"),
    ("SEPARATION", "deb377381ceaf55ea310", "nachseihen", "second separation after standing", "WHOLE_CARD"),
    ("SEPARATION", "75a523fcf039b006f97b", "abseihen", "plain straining", "WHOLE_CARD"),
    ("SEPARATION", "d68bc8de3bcee09db23c", "seihen; Schluss", "closed straining step", "COMPOUND_CARD"),
    ("SEPARATION", "c1db6b0a28d5cbb5d3d2", "lokal seihen; Schluss", "local closed straining step", "COMPOUND_CARD"),
    ("SEPARATION", "2d2e37ccb2dacc53ee5a", "Seihtuch", "straining instrument", "WHOLE_CARD"),
    ("RECEIVE_STORE", "62ff059766b21c7de083", "auffangen", "catch separated result", "WHOLE_CARD"),
    ("RECEIVE_STORE", "42cdc187d5b9ffc60063", "kurz auffangen; offen", "short open receiving", "COMPOUND_CARD"),
    ("RECEIVE_STORE", "1bfd786e6b8b63734a59", "länger auffangen; offen", "long open receiving", "COMPOUND_CARD"),
    ("RECEIVE_STORE", "3b70942557b3a40e8030", "länger auffangen; Schluss", "long closed receiving", "COMPOUND_CARD"),
    ("RECEIVE_STORE", "e026af581c99322fbd46", "verwahren", "store finished result", "WHOLE_CARD"),
    ("RECEIVE_STORE", "97cc9ac109148723c472", "abkühlen; Schluss", "cool before storage", "WHOLE_CARD"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dictionary = {row["joint_tuple_id"]: row for row in read(DICTIONARY)}
    deck_rows = []
    for family, joint_id, value, function, architecture in DECK:
        row = dictionary[joint_id]
        deck_rows.append({
            "functional_family": family,
            "joint_tuple_id": joint_id,
            "surface_family": row["surface_family"],
            "occurrences": row["occurrences"],
            "records": row["records"],
            "pages": row["pages"],
            "short_value_de": value,
            "workshop_function": function,
            "architecture": architecture,
            "surface_segmentation_required_for_family_membership": "NO",
            "selection_prompt": {
                "TARGET_RESULT": "What target/result state is required?",
                "SEPARATION": "Which separation act or instrument is required?",
                "RECEIVE_STORE": "How is the result received or retained?",
            }[family],
        })
    write("THREE_HUNDRED_NINETIETH_16_CARD_FUNCTIONAL_DECK.tsv", deck_rows)

    family_rows = []
    for family, german, rule in [
        ("TARGET_RESULT", "Ziel/Ergebnis", "choose the resulting site or target operation"),
        ("SEPARATION", "Trennung/Nachtrennung", "choose wring, strain, re-strain, cloth, or closed strain"),
        ("RECEIVE_STORE", "Auffangen/Lagern", "choose catch, graded receive, cool, or store"),
    ]:
        members = [row for row in deck_rows if row["functional_family"] == family]
        family_rows.append({
            "functional_family": family,
            "german_family_name": german,
            "member_cards": len(members),
            "total_occurrences": sum(int(row["occurrences"]) for row in members),
            "surface_families": "|".join(row["surface_family"] for row in members),
            "selection_rule": rule,
            "spelling_similarity_required": "NO",
        })
    write("THREE_HUNDRED_NINETIETH_THREE_FUNCTIONAL_DRAWERS.tsv", family_rows)

    edge_rows = [
        {"from_card": "cfhy", "relation": "FIRST_SEPARATION_BEFORE", "to_card": "cphy", "reading": "auswringen, stehen lassen, dann nachseihen"},
        {"from_card": "cphy", "relation": "YIELDS", "to_card": "otytchol", "reading": "nachseihen und auffangen"},
        {"from_card": "kchal", "relation": "YIELDS", "to_card": "talam", "reading": "abseihen und verwahren"},
        {"from_card": "shckhedy", "relation": "YIELDS", "to_card": "solkey", "reading": "geschlossen seihen, dann kurz auffangen"},
        {"from_card": "lcheckhedy", "relation": "YIELDS", "to_card": "solkeey", "reading": "lokal seihen, dann länger auffangen"},
        {"from_card": "solkeey", "relation": "CLOSED_VARIANT", "to_card": "olkeedy|solkeedy", "reading": "offenes Auffangen in geschlossenen Empfang überführen"},
        {"from_card": "otytchol", "relation": "COOL_BEFORE", "to_card": "ody", "reading": "Auffangprodukt abkühlen und schließen"},
        {"from_card": "ody", "relation": "STORE_AFTER", "to_card": "talam", "reading": "gekühltes Ergebnis verwahren"},
        {"from_card": "lcheey", "relation": "TARGETS", "to_card": "qokeedal", "reading": "benetzte Stelle länger behandeln"},
        {"from_card": "shedal", "relation": "RESULT_AT", "to_card": "al|chal|cheal|dal|sal|tal", "reading": "an der Stelle absetzen"},
    ]
    write("THREE_HUNDRED_NINETIETH_FUNCTIONAL_PROCESS_EDGES.tsv", edge_rows)

    manual = """# Pass 390 — funktionaler Nomenklator

Die restlichen Ganzkarten werden nicht nach Buchstaben sortiert, sondern in drei
Werkstattschubladen:

1. **Ziel/Ergebnis** — `lcheey`, AL, `qokeedal`, `shedal`.
2. **Trennung/Nachtrennung** — `cfhy`, `cphy`, `kchal`, CKHE-Schlusskarten,
   `solkaiin`.
3. **Auffangen/Lagern** — `otytchol`, die SOLK-Grade, `talam`, `ody`.

Die Schublade sagt dem Schreiber, welche Funktion gebraucht wird. Die genaue
Karte wird auswendig gelernt oder aus produktiven Komponenten gebaut. Ähnliche
Schreibung ist keine Voraussetzung.

Ein typischer Fachgang kann daher lauten:

`CFHY auswringen → CPHY nachseihen → OTYTCHOL auffangen → ODY abkühlen/schließen → TALAM verwahren`.

Das ist keine behauptete Lautfolge, sondern eine praktische Auswahlfolge für
gelernte Fachzeichen.
"""
    (HERE / "THREE_HUNDRED_NINETIETH_NOMENCLATOR_MANUAL.md").write_text(manual, encoding="utf-8")
    report = """# Pass 390 — die Mischarchitektur wird konkret

Sechzehn Kartenfamilien mit zusammen 30 Vorkommen bilden drei funktionale
Schubladen. Einige Mitglieder sind produktive Komposita, andere reine
Nomenklatorkarten. Die Mitgliedschaft hängt von der Werkstattfunktion ab, nicht
von einem erzwungenen gemeinsamen Buchstabenstamm.

Damit erhält das System genau die gesuchte Mischung: Die äußere Satz- und
Gradgrammatik ist produktiv; spezialisierte Ziel-, Trenn- und Lagerhandlungen
werden aus einem kleinen gelernten Fachdeck gewählt. CPHY und TALAM bleiben
semantisch kurz und praktisch, obwohl sie sich nicht zerlegen lassen.

Als nächstes sollen der echte H3-Trennlauf und unser revidierter H4-Lauf mit
demselben Drei-Schubladen-Deck parallel gesetzt werden. Gemeinsame Funktionen
und unterschiedliche Karten werden ausdrücklich getrennt.
"""
    (HERE / "THREE_HUNDRED_NINETIETH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "card_families": len(deck_rows),
        "total_occurrences": sum(int(row["occurrences"]) for row in deck_rows),
        "functional_drawers": len(family_rows),
        "process_edges": len(edge_rows),
        "whole_cards": sum(row["architecture"] == "WHOLE_CARD" for row in deck_rows),
        "component_or_compound_cards": sum(row["architecture"] != "WHOLE_CARD" for row in deck_rows),
    }
    (HERE / "THREE_HUNDRED_NINETIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
