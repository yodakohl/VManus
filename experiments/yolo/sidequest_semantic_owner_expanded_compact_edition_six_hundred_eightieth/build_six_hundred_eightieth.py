#!/usr/bin/env python3
"""Build a compact 116-statement edition with explicit visual-owner nouns."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P675 = ROOT / "experiments/yolo/sidequest_semantic_short_fragment_cleanup_six_hundred_seventy_fifth"
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"
P21 = ROOT / "experiments/yolo/sidequest_semantic_owner_filled_twenty_first_edition"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


OWNER_NOUN = {
    "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB": "die breite gezahnte Bluetenpflanze",
    "WHOLE_DENSE_BLUE_FLOWERED_CROWN_PLANT": "die dicht bluehende Kronenpflanze",
    "WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT": "die breitblaettrige rispige Pflanze",
    "WHOLE_MULTIHEAD_SPINY_OR_EMBLEMATIC_HERB": "die mehrkoepfige stachelige Pflanze",
    "B1_SHARED_TWO_ROW_POOL": "das gemeinsame zweireihige Becken",
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": "die oberen Paarbecken mit Zylinder",
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": "die linke Mittelstation mit Zwischenknoten",
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": "die rechte unklare Mittelstation",
    "B2_LOWER_POOL_EDGE_STATIONS": "die Randstationen des unteren Beckens",
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": "das untere gruene Figurenbecken",
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": "die obere offene Faecherstation",
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": "das runde Mittelgefaess",
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": "das untere Korbgefaess",
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": "der bildlich unverbundene Zwischenabschnitt",
    "B3_MAIN_ARCH_LINKED_PAIR": "das durch den Bogen verbundene Hauptpaar",
    "B4_MAIN_ARCH_LINKED_PAIR": "das zweite durch den Bogen verbundene Hauptpaar",
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": "die linke offene Randstation",
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": "die rechte S-Lauf-Mehrfachstation",
    "B5_LEFT_OPEN_FRINGE_STATION": "die linke offene Nebenstation",
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": "die rechte S-Lauf-Nebenstation",
}

OWNER_CONTEXT = {
    "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB": "bei der breiten gezahnten Bluetenpflanze",
    "WHOLE_DENSE_BLUE_FLOWERED_CROWN_PLANT": "bei der dicht bluehenden Kronenpflanze",
    "WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT": "bei der breitblaettrigen rispigen Pflanze",
    "WHOLE_MULTIHEAD_SPINY_OR_EMBLEMATIC_HERB": "bei der mehrkoepfigen stacheligen Pflanze",
    "B1_SHARED_TWO_ROW_POOL": "am gemeinsamen zweireihigen Becken",
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": "an den oberen Paarbecken mit Zylinder",
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": "an der linken Mittelstation mit Zwischenknoten",
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": "an der rechten unklaren Mittelstation",
    "B2_LOWER_POOL_EDGE_STATIONS": "an den Randstationen des unteren Beckens",
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": "am unteren gruenen Figurenbecken",
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": "an der oberen offenen Faecherstation",
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": "am runden Mittelgefaess",
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": "am unteren Korbgefaess",
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": "im bildlich unverbundenen Zwischenabschnitt",
    "B3_MAIN_ARCH_LINKED_PAIR": "am durch den Bogen verbundenen Hauptpaar",
    "B4_MAIN_ARCH_LINKED_PAIR": "am zweiten durch den Bogen verbundenen Hauptpaar",
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": "an der linken offenen Randstation",
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": "an der rechten S-Lauf-Mehrfachstation",
    "B5_LEFT_OPEN_FRINGE_STATION": "an der linken offenen Nebenstation",
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": "an der rechten S-Lauf-Nebenstation",
}


def owner_phrase(owner: str) -> str:
    return " und ".join(OWNER_NOUN[part] for part in owner.split("|"))


def owner_context(owner: str) -> str:
    return " und ".join(OWNER_CONTEXT[part] for part in owner.split("|"))


def compact_fluent(text: str) -> str:
    replacements = [
        ("aus dem Vorrat", "aus der Quelle"), ("Aus dem Vorrat", "Aus der Quelle"),
        ("vom Vorrat", "von der Quelle"), ("Vom Vorrat", "Von der Quelle"),
        ("an der Zielstelle", "am Ziel"), ("An der Zielstelle", "Am Ziel"),
        ("zur Zielstelle", "zum Ziel"), ("Zur Zielstelle", "Zum Ziel"),
        ("die Zielstelle", "das Ziel"), ("Die Zielstelle", "Das Ziel"),
        ("der Zielstelle", "dem Ziel"), ("Der Zielstelle", "Dem Ziel"),
        ("bis zur Arbeitsstufe", "bis zur Stufe"), ("Bis zur Arbeitsstufe", "Bis zur Stufe"),
        ("nach Sollmass", "nach Mass"), ("Nach Sollmass", "Nach Mass"),
        ("im Arbeitsgang", "im Gang"), ("Im Arbeitsgang", "Im Gang"),
        ("den Arbeitsgang", "den Gang"), ("Den Arbeitsgang", "Den Gang"),
        ("Fluessigkeitslauf", "Lauf"), ("fluessigkeitslauf", "Lauf"),
        ("Zielstelle", "Ziel"), ("zielstelle", "Ziel"),
        ("Arbeitsstufe", "Stufe"), ("arbeitsstufe", "Stufe"),
        ("Arbeitsgang", "Gang"), ("arbeitsgang", "Gang"),
        ("Arbeitsfach", "Fach"), ("arbeitsfach", "Fach"),
        ("Sollmass", "Mass"), ("sollmass", "Mass"),
        ("Vorrat", "Quelle"), ("vorrat", "Quelle"),
        ("Arbeitsposten", "Posten"), ("arbeitsposten", "Posten"),
        ("Nachportion", "Nachgabe"), ("nachportion", "Nachgabe"),
        ("Zweitmarker", "Zweitzeichen"), ("zweitmarker", "Zweitzeichen"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    statements = read(P675 / "SIX_HUNDRED_SEVENTY_FIFTH_116_CLEAN_STATEMENTS.tsv")
    owners = {row["statement_id"]: row for row in read(P21 / "TWENTY_FIRST_116_OWNER_FILLED_PROSE.tsv")}
    events = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    rows = []
    for statement in statements:
        sid = statement["statement_id"]
        owner = owners[sid]
        event_rows = by_statement[sid]
        components = {component for event in event_rows for component in event["component_recipe"].split("+")}
        owner_noun = owner_phrase(owner["image_owner"])
        context = owner_context(owner["image_owner"])
        expansions = []
        if "Y" in components:
            expansions.append(f"DIES=aktueller Posten {context}")
        if "AIR" in components:
            expansions.append(f"LAUF=lokaler Lauf {context}")
        if "AL" in components:
            expansions.append(f"ZIEL=bezeichnetes Ziel {context}")
        if "AR" in components:
            expansions.append(f"QUELLE=lokaler Ausgang {context}")
        compact_text = compact_fluent(statement["fluent_workshop_reading_de"])
        rows.append({
            "statement_id": sid,
            "page": statement["page"],
            "record": statement["record"],
            "events": statement["events"],
            "surface_sequence": statement["surface_sequence"],
            "component_sequence": statement["component_sequence"],
            "compact_atomic_sequence_de": " | ".join(event["compact_atomic_reading_de"] for event in event_rows),
            "image_owner": owner["image_owner"],
            "owner_noun_de": owner_noun,
            "owner_context_de": context,
            "owner_kind": owner["owner_kind"],
            "owner_break_inside_statement": owner["owner_break_inside_statement"],
            "owner_supplied_expansions_de": " | ".join(expansions) if expansions else "KEINE_DIES_LAUF_ZIEL_QUELLE_KARTE",
            "compact_owner_reading_de": f"{context[0].upper() + context[1:]}: {compact_text}",
            "closes": statement["closes"],
        })

    records = []
    for record in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]:
        selected = [row for row in rows if row["record"] == record]
        records.append({
            "record": record,
            "page": selected[0]["page"],
            "statements": len(selected),
            "events": sum(int(row["events"]) for row in selected),
            "owners_in_order": " -> ".join(dict.fromkeys(str(row["owner_noun_de"]) for row in selected)),
            "continuous_compact_owner_reading_de": " ".join(str(row["compact_owner_reading_de"]) for row in selected),
        })

    owner_rows = [
        {"image_owner": owner, "owner_noun_de": noun, "owner_context_de": OWNER_CONTEXT[owner], "statements": sum(row["image_owner"] == owner or owner in row["image_owner"].split("|") for row in rows)}
        for owner, noun in OWNER_NOUN.items()
    ]
    write("SIX_HUNDRED_EIGHTIETH_116_COMPACT_OWNER_STATEMENTS.tsv", rows)
    write("SIX_HUNDRED_EIGHTIETH_11_CONTINUOUS_OWNER_RECORDS.tsv", records)
    write("SIX_HUNDRED_EIGHTIETH_20_OWNER_NOUNS.tsv", owner_rows)

    summary = {
        "status": "PASS",
        "statements": len(rows),
        "events": sum(int(row["events"]) for row in rows),
        "records": len(records),
        "owner_nouns": len(owner_rows),
        "statements_with_owner_expansion": sum(row["owner_supplied_expansions_de"] != "KEINE_DIES_LAUF_ZIEL_QUELLE_KARTE" for row in rows),
        "statements_with_owner_break": sum(row["owner_break_inside_statement"] == "YES" for row in rows),
    }
    (HERE / "SIX_HUNDRED_EIGHTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
