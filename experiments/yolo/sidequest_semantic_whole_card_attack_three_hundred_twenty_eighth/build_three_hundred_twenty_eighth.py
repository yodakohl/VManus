#!/usr/bin/env python3
"""Attack the 23 whole cards with the existing 40 components only."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_complete_atomic_deck_three_hundred_twenty_seventh"
DICTIONARY = BASE / "THREE_HUNDRED_TWENTY_SEVENTH_173_ATOMIC_DICTIONARY.tsv"
EVENTS = BASE / "THREE_HUNDRED_TWENTY_SEVENTH_381_ATOMIC_EVENTS.tsv"

PROMOTIONS = {
    "tchody": ("TCH_PREPARATION+O_WITHDRAW+DY", "Rücknahmeschluss", "TCH, Rücknahme und Schluss sind bereits im 40er-Deck; Kälte war eine lokale Expansion."),
    "schoal": ("HO+AL", "Zieleingabe", "Die sichtbare HO-Zutat steht an AL-Stelle; Wein war nicht auf der Karte verankert."),
    "sshkchdy": ("CHD+DY", "Umsetzschluss", "Der lange Vorbau bleibt Renderer; CHD-Umsetzen plus DY-Schluss reicht."),
    "rshedy": ("SHED+DY", "Absetzschluss", "R bleibt Renderer; SHED-Absetzen und DY-Schluss sind produktiv."),
    "etyd": ("E+TY+D_PREVIOUS", "Kurzrest", "Kurzgrad plus Teil und Vorbezug bilden den kleinen Rest am Ende der Wurzelzubereitung."),
    "ytey": ("Y+TY+E", "Kurzteil", "Aktueller Posten plus Teil plus Kurzgrad erklärt die Karte ohne Füll-Ganzwort."),
    "lkedy": ("L+K_BINDER+E+DY", "Kurzabzugsschluss", "Abzug, Binder, Kurzgrad und Schluss erklären den bisherigen Weiterabzug."),
    "dshedy": ("D_PREVIOUS+SHED+DY", "Vorabsetzschluss", "Vorposten plus Absetzen plus Schluss ersetzt die ungebundene Frischspülungslesung."),
}

RETAIN_REASONS = {
    "dl": "D+L ergäbe Vorabzug, nicht den zweimal benötigten Zusatz.",
    "qekey": "E/K/Y liefert keine eindeutige Bearbeitungsart.",
    "dain": "D+AIN ergäbe Vorportion; die zwei Einlagekontexte verlangen eine gelernte Karte.",
    "sotodan": "OT/D/AN ergibt keine eindeutige Gebrauchsoperation.",
    "dchey": "D+Y kann am Recordanfang keinen Vorposten meinen; das bildlokale Wurzelteil bleibt gelernt.",
    "tshol": "TY/OL erklärt weder das Pflanzenmaterial noch die konkrete Auswahl.",
    "cheeckhody": "CKH/O/DY erklärt Durchlass und Schluss, aber nicht die Anwendungsoperation.",
    "sh": "Kein vorhandener Kern erzeugt den bildlokalen Pflanzenteil.",
    "ly": "L+Y ergäbe Abzugsposten, nicht das sichtbare Empfangsgefäß.",
    "cheey|shey": "Klarauszug bleibt die bewährte ungeteilte Produktkarte.",
    "cfhy": "Auswringen hat keinen vorhandenen Operationskern.",
    "ches": "E allein erklärt das Teilen nicht.",
    "cphy": "P erklärt den Empfänger, nicht das Nachseihen.",
    "talam": "AL erklärt eine Stelle, nicht das Verwahren.",
    "qokylddy": "OK+Y+L+DY erklärt Einsatz und Schluss, aber nicht das Befestigen.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base_dictionary = read(DICTIONARY)
    base_events = read(EVENTS)
    whole = [x for x in base_dictionary if x["deck_class"] == "MEMORIZED_WHOLE_CARD"]
    attacks = []
    revised_dictionary = []
    old_atom = {x["joint_tuple_id"]: x["atomic_value_de"] for x in base_dictionary}
    new_atom = dict(old_atom)
    new_class = {x["joint_tuple_id"]: x["deck_class"] for x in base_dictionary}
    new_formula = {x["joint_tuple_id"]: x["component_formula"] for x in base_dictionary}

    for row in whole:
        surface = row["surface_family"]
        if surface in PROMOTIONS:
            formula, value, reason = PROMOTIONS[surface]
            decision = "PROMOTE_WITH_EXISTING_COMPONENTS"
            new_atom[row["joint_tuple_id"]] = value
            new_class[row["joint_tuple_id"]] = "PRODUCTIVE_COMPOSITION"
            new_formula[row["joint_tuple_id"]] = formula
        else:
            formula, value, reason = "WHOLE_CARD", row["atomic_value_de"], RETAIN_REASONS[surface]
            decision = "RETAIN_MEMORIZED_WHOLE_CARD"
        attacks.append(
            {
                "joint_tuple_id": row["joint_tuple_id"],
                "surface_family": surface,
                "events": row["occurrences"],
                "old_atomic_value_de": row["atomic_value_de"],
                "decision": decision,
                "new_component_formula": formula,
                "new_atomic_value_de": value,
                "new_components_added": "0",
                "reason_de": reason,
            }
        )

    for row in base_dictionary:
        out = dict(row)
        out["deck_class"] = new_class[row["joint_tuple_id"]]
        out["component_formula"] = new_formula[row["joint_tuple_id"]]
        out["atomic_value_de"] = new_atom[row["joint_tuple_id"]]
        if row["joint_tuple_id"] in {x["joint_tuple_id"] for x in attacks if x["decision"].startswith("PROMOTE")}:
            out["atomic_value_source"] = "PASS328_EXISTING_COMPONENT_REANALYSIS"
        revised_dictionary.append(out)

    revised_events = []
    old_by_statement: dict[str, list[str]] = defaultdict(list)
    new_by_statement: dict[str, list[str]] = defaultdict(list)
    statement_meta = {}
    for row in base_events:
        out = dict(row)
        old_by_statement[row["statement_id"]].append(row["atomic_value_de"])
        out["atomic_value_de"] = new_atom[row["joint_tuple_id"]]
        out["deck_class"] = new_class[row["joint_tuple_id"]]
        new_by_statement[row["statement_id"]].append(out["atomic_value_de"])
        statement_meta[row["statement_id"]] = (row["record_unit_id"], row["page"])
        revised_events.append(out)

    changed_statements = []
    for statement_id in old_by_statement:
        if old_by_statement[statement_id] != new_by_statement[statement_id]:
            record, page = statement_meta[statement_id]
            changed_statements.append(
                {
                    "statement_id": statement_id,
                    "record_unit_id": record,
                    "page": page,
                    "old_atomic_sequence": " → ".join(old_by_statement[statement_id]),
                    "new_atomic_sequence": " → ".join(new_by_statement[statement_id]),
                }
            )

    retained = [x for x in revised_dictionary if x["deck_class"] == "MEMORIZED_WHOLE_CARD"]
    write("THREE_HUNDRED_TWENTY_EIGHTH_23_WHOLE_CARD_ATTACKS.tsv", attacks)
    write("THREE_HUNDRED_TWENTY_EIGHTH_15_RETAINED_WHOLE_CARDS.tsv", retained)
    write("THREE_HUNDRED_TWENTY_EIGHTH_173_REVISED_DICTIONARY.tsv", revised_dictionary)
    write("THREE_HUNDRED_TWENTY_EIGHTH_381_REVISED_EVENTS.tsv", revised_events)
    write("THREE_HUNDRED_TWENTY_EIGHTH_SIX_REVISED_STATEMENTS.tsv", changed_statements)
    names = [
        "THREE_HUNDRED_TWENTY_EIGHTH_23_WHOLE_CARD_ATTACKS.tsv",
        "THREE_HUNDRED_TWENTY_EIGHTH_15_RETAINED_WHOLE_CARDS.tsv",
        "THREE_HUNDRED_TWENTY_EIGHTH_173_REVISED_DICTIONARY.tsv",
        "THREE_HUNDRED_TWENTY_EIGHTH_381_REVISED_EVENTS.tsv",
        "THREE_HUNDRED_TWENTY_EIGHTH_SIX_REVISED_STATEMENTS.tsv",
    ]
    summary = {
        "status": "PASS",
        "attacked_whole_cards": len(attacks),
        "promoted_cards": sum(x["decision"] == "PROMOTE_WITH_EXISTING_COMPONENTS" for x in attacks),
        "retained_whole_cards": len(retained),
        "components_added": 0,
        "productive_cards": sum(x["deck_class"] == "PRODUCTIVE_COMPOSITION" for x in revised_dictionary),
        "productive_events": sum(x["deck_class"] == "PRODUCTIVE_COMPOSITION" for x in revised_events),
        "whole_card_events": sum(x["deck_class"] == "MEMORIZED_WHOLE_CARD" for x in revised_events),
        "revised_statements": len(changed_statements),
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_TWENTY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
