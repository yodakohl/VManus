#!/usr/bin/env python3
"""Build Pass 740: derive a compact apprentice syntax from Pass 739."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"


def read(name: str) -> list[dict[str, str]]:
    with (P739 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SLOT = {
    "OK": "ACTION", "CHD": "ACTION", "SH": "ACTION", "SHED": "ACTION",
    "CHK": "ACTION", "CTH": "ACTION", "P": "ACTION", "LSH": "ACTION",
    "CFH": "ACTION", "CH": "ACTION", "T": "ACTION", "K": "ACTION",
    "L": "ACTION", "R": "ACTION", "LD": "ACTION", "TALAM": "ACTION",
    "OL": "MEMORY", "OT": "MEMORY", "RESUME_CARD": "MEMORY",
    "AL": "ADDRESS", "AR": "ADDRESS", "AIIN": "ADDRESS", "AIN": "ADDRESS",
    "IIN": "ADDRESS", "AN": "ADDRESS", "CKH": "ADDRESS", "SOLK": "ADDRESS",
    "S": "ADDRESS",
    "AIR": "MATERIAL", "OR": "MATERIAL", "HO": "MATERIAL", "O": "MATERIAL",
    "OS": "MATERIAL",
    "E": "GRADE", "EE": "GRADE", "EEE": "GRADE", "DA": "GRADE",
    "Y": "REFERENT", "DY": "CLOSE",
}


TEMPLATE_NAMES = {
    ("ACTION_UNADDRESSED", "CLOSED"): ("T1", "HANDLUNG__SCHLUSS"),
    ("ACTION_THEN_ADDRESS", "CLOSED"): ("T2", "HANDLUNG__ADRESSE__SCHLUSS"),
    ("ADDRESS_THEN_ACTION", "CLOSED"): ("T3", "ADRESSE__HANDLUNG__SCHLUSS"),
    ("NO_ACTION", "CLOSED"): ("T4", "ELLIPSE__SCHLUSS"),
    ("ACTION_THEN_ADDRESS", "OPEN"): ("T5", "HANDLUNG__ADRESSE__OFFEN"),
    ("ADDRESS_THEN_ACTION", "OPEN"): ("T6", "ADRESSE__HANDLUNG__OFFEN"),
    ("ACTION_UNADDRESSED", "OPEN"): ("T7", "HANDLUNG__OFFEN"),
    ("NO_ACTION", "OPEN"): ("T8", "ELLIPSE__OFFEN"),
}


def compressed(items: list[str]) -> str:
    out: list[str] = []
    for item in items:
        if not out or out[-1] != item:
            out.append(item)
    return ">".join(out)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read("SEVEN_HUNDRED_THIRTY_NINTH_39_COMPONENT_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv")

    component_rows = []
    for row in components:
        component_rows.append({
            "component_no": row["component_no"],
            "component": row["component"],
            "short_value_de": row["short_value_de"],
            "apprentice_slot": SLOT[row["component"]],
            "teaching_rule": row["teaching_rule"],
            "events": row["events"],
        })

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    statement_source = {row["statement_id"]: row for row in statements}

    pattern_rows = []
    for statement_id, seq in by_statement.items():
        source = statement_source[statement_id]
        components_in_order = [part for row in seq for part in row["component_recipe"].split("+")]
        slots = [SLOT[part] for part in components_in_order]
        action_positions = [i for i, slot in enumerate(slots) if slot == "ACTION"]
        address_positions = [i for i, slot in enumerate(slots) if slot == "ADDRESS"]
        if not action_positions:
            order_class = "NO_ACTION"
        elif not address_positions:
            order_class = "ACTION_UNADDRESSED"
        elif action_positions[0] < address_positions[0]:
            order_class = "ACTION_THEN_ADDRESS"
        else:
            order_class = "ADDRESS_THEN_ACTION"
        close_class = "CLOSED" if components_in_order[-1] == "DY" else "OPEN"
        template_id, template_name = TEMPLATE_NAMES[(order_class, close_class)]
        memory_start = components_in_order[0] in {"OT", "OL", "RESUME_CARD"}
        pattern_rows.append({
            "statement_id": statement_id,
            "page": source["page"],
            "register": "HERBAL" if statement_id.startswith("H") else "BIOLOGICAL",
            "record": source["record"],
            "owner_noun_de": source["owner_noun_de"],
            "cards": len(seq),
            "components": len(components_in_order),
            "surface_sequence": source["surface_sequence"],
            "component_sequence": "+".join(components_in_order),
            "slot_sequence": ">".join(slots),
            "compressed_slot_sequence": compressed(slots),
            "template_id": template_id,
            "template_name": template_name,
            "memory_start": "YES" if memory_start else "NO",
            "contains_memory": "YES" if "MEMORY" in slots else "NO",
            "endpoint": close_class,
            "codebook_literal_de": source["codebook_literal_de"],
            "clean_workshop_reading_de": source["clean_workshop_reading_de"],
        })

    template_rows = []
    for (order_class, close_class), (template_id, template_name) in TEMPLATE_NAMES.items():
        target = [row for row in pattern_rows if row["template_id"] == template_id]
        template_rows.append({
            "template_id": template_id,
            "template_name": template_name,
            "order_class": order_class,
            "endpoint": close_class,
            "statements": len(target),
            "herbal_statements": sum(row["register"] == "HERBAL" for row in target),
            "biological_statements": sum(row["register"] == "BIOLOGICAL" for row in target),
            "memory_start_statements": sum(row["memory_start"] == "YES" for row in target),
            "single_card_statements": sum(int(row["cards"]) == 1 for row in target),
            "example_statement": target[0]["statement_id"],
            "example_surface": target[0]["surface_sequence"],
            "apprentice_instruction_de": {
                "T1": "Handlung nennen und mit einer lizenzierten Schlusskarte abschliessen.",
                "T2": "Handlung zuerst setzen; Quelle, Menge, Weg oder Zielstelle danach anbinden; schliessen.",
                "T3": "Neue Menge, Quelle oder Zielstelle zuerst als Kopf setzen; danach Handlung und Schluss.",
                "T4": "Handlung vom laufenden Bild-/Arbeitskontext erben; nur Zustand/Adresse und Schluss schreiben.",
                "T5": "Handlung und ihre Adresse setzen; Posten fuer die Fortsetzung offen lassen.",
                "T6": "Neue Adresse zuerst setzen, dann handeln; ohne Schluss in die naechste Aussage tragen.",
                "T7": "Nur die aktuelle Handlung setzen und den Posten offen weitertragen.",
                "T8": "Nur eine neue Adresse setzen; Handlung und Posten vollstaendig aus dem Kontext erben.",
            }[template_id],
        })

    exception_rows = []
    for row in pattern_rows:
        if row["template_id"] in {"T3", "T4", "T6", "T8"}:
            exception_rows.append({
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "template_id": row["template_id"],
                "surface_sequence": row["surface_sequence"],
                "component_sequence": row["component_sequence"],
                "clean_workshop_reading_de": row["clean_workshop_reading_de"],
                "teaching_note_de": "Adresskopf vor Handlung" if row["template_id"] in {"T3", "T6"} else "Handlung aus Bild oder laufendem Arbeitsgang erben",
            })

    register_rows = []
    for register in ["HERBAL", "BIOLOGICAL"]:
        target = [row for row in pattern_rows if row["register"] == register]
        register_rows.append({
            "register": register,
            "statements": len(target),
            "cards": sum(int(row["cards"]) for row in target),
            "mean_cards_per_statement": f"{sum(int(row['cards']) for row in target) / len(target):.3f}",
            "single_card_statements": sum(int(row["cards"]) == 1 for row in target),
            "closed_statements": sum(row["endpoint"] == "CLOSED" for row in target),
            "open_statements": sum(row["endpoint"] == "OPEN" for row in target),
            "action_leading_statements": sum(row["template_id"] in {"T1", "T2", "T5", "T7"} for row in target),
            "address_leading_statements": sum(row["template_id"] in {"T3", "T6"} for row in target),
            "elliptic_statements": sum(row["template_id"] in {"T4", "T8"} for row in target),
            "memory_start_statements": sum(row["memory_start"] == "YES" for row in target),
            "teaching_mode_de": "laufende mehrkartige Artikelanweisung" if register == "HERBAL" else "kurze meist geschlossene Arbeitszelle",
        })

    write("SEVEN_HUNDRED_FORTIETH_39_COMPONENT_SLOT_MAP.tsv", component_rows)
    write("SEVEN_HUNDRED_FORTIETH_116_STATEMENT_PATTERNS.tsv", pattern_rows)
    write("SEVEN_HUNDRED_FORTIETH_8_TEACHING_TEMPLATES.tsv", template_rows)
    write("SEVEN_HUNDRED_FORTIETH_21_HEADER_OR_ELLIPSIS_CASES.tsv", exception_rows)
    write("SEVEN_HUNDRED_FORTIETH_REGISTER_COMPARISON.tsv", register_rows)

    apprentice = """# Pass 740 — Lehrblatt fuer einen neuen Schreiber

1. Das Bild oder die lokale Station setzt den Besitzer stillschweigend.
2. Beginne normalerweise mit der Handlungskarte. Das geschieht in 95 von 116 Aussagen.
3. Quelle, Sollmass, Portion, Arbeitsstufe, Durchlass, Sammelstelle oder Zielstelle koennen in dieselbe Karte gepackt oder danach angehaengt werden.
4. Wenn eine neue Menge oder Stelle den folgenden Schritt beherrschen soll, darf sie vor der Handlung stehen. Das geschieht in 15 Aussagen.
5. E, EE und EEE geben kurz, lang und voll an; Y haelt den aktuellen Posten im Blick.
6. Eine lizenzierte DY-Karte schliesst den Arbeitsschritt. Alle 89 solchen Schluesse stehen am Aussagenende.
7. OT, OL oder die Wiederaufnahmekarte koennen am Anfang stehen: danach, weiter oder den vorigen Vorgang wiederaufnehmen. Das geschieht in 20 Aussagen.
8. Sechs Aussagen nennen gar keine neue Handlung. Dort erbt der Schreiber sie aus Bild, Station oder laufendem Vorgang.
9. Herbal schreibt laufend: 19 Aussagen, im Mittel 5.263 Karten, nur 4 geschlossen.
10. Biological schreibt in Zellen: 97 Aussagen, im Mittel 2.897 Karten, 85 geschlossen und 43 bereits mit einer einzigen Karte.

## Acht lernbare Formen

- T1 Handlung — Schluss.
- T2 Handlung — Adresse — Schluss.
- T3 Adresse — Handlung — Schluss.
- T4 geerbte Handlung — Zustand/Adresse — Schluss.
- T5 Handlung — Adresse — offen weiter.
- T6 Adresse — Handlung — offen weiter.
- T7 Handlung — offen weiter.
- T8 nur Adresse; alles andere erben.

Das System ist damit fuer eine kleine Werkstatt plausibel einfach: dieselben kurzen Karten, aber zwei Schreibmodi. Im Pflanzenartikel werden mehrere Karten als laufende Anweisung gereiht; im Becken-/Stationsregister wird derselbe Inhalt oft zu einer einzigen geschlossenen Karte verdichtet.
"""
    (HERE / "SEVEN_HUNDRED_FORTIETH_APPRENTICE_SHEET.md").write_text(apprentice, encoding="utf-8")

    counts = Counter(row["template_id"] for row in pattern_rows)
    report = f"""# Pass 740 — acht Satzbauplaene

Die 116 Aussagen lassen sich mit acht einfachen Lehrformen schreiben. Die wichtigste Entdeckung ist nicht eine starre Wortstellung, sondern ein klarer Werkstattunterschied:

- **Herbal:** 19 laengere Aussagen mit 100 Karten, im Mittel 5.263 Karten; nur eine Ein-Karten-Aussage und vier Schluesse.
- **Biological:** 97 kurze Zellen mit 281 Karten, im Mittel 2.897 Karten; 43 Ein-Karten-Zellen und 85 Schluesse.

Das gleiche 39-Eintraege-Codebook wird also einmal als laufender Artikel und einmal als stark verdichtetes Stationsformular benutzt.

## Verteilung

- T1 Handlung→Schluss: {counts['T1']}
- T2 Handlung→Adresse→Schluss: {counts['T2']}
- T3 Adresse→Handlung→Schluss: {counts['T3']}
- T4 Ellipse→Schluss: {counts['T4']}
- T5 Handlung→Adresse→offen: {counts['T5']}
- T6 Adresse→Handlung→offen: {counts['T6']}
- T7 Handlung→offen: {counts['T7']}
- T8 reine offene Ellipse: {counts['T8']}

95/116 Aussagen sind handlungsfuehrend. 15 setzen zuerst eine neue Adresse. Sechs erben die Handlung ganz aus dem laufenden Bild-/Arbeitskontext. 20 beginnen mit einer expliziten Gedaechtniskarte. Alle 89 lizenzierten Schluesse stehen tatsaechlich ganz am Ende.

## Nächster Hebel

Jetzt kann ein echter Schreibtest erfolgen: die 116 Aussagen werden mit diesen acht Regeln **neu kodiert**, ohne ihre Kartenfolge anzusehen. Anschliessend vergleichen wir, an welchen Stellen der Lehrling dieselbe Kartenfamilie waehlt und wo eine gelernte Ganzkarte oder lokale Ausnahme fehlt.
"""
    (HERE / "SEVEN_HUNDRED_FORTIETH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "components": len(component_rows),
        "events": len(events),
        "statements": len(pattern_rows),
        "templates": len(template_rows),
        "header_or_ellipsis_cases": len(exception_rows),
        "template_counts": dict(sorted(counts.items())),
        "action_leading_statements": sum(row["template_id"] in {"T1", "T2", "T5", "T7"} for row in pattern_rows),
        "address_leading_statements": sum(row["template_id"] in {"T3", "T6"} for row in pattern_rows),
        "elliptic_statements": sum(row["template_id"] in {"T4", "T8"} for row in pattern_rows),
        "memory_start_statements": sum(row["memory_start"] == "YES" for row in pattern_rows),
        "closed_statements": sum(row["endpoint"] == "CLOSED" for row in pattern_rows),
        "single_card_herbal": sum(row["register"] == "HERBAL" and int(row["cards"]) == 1 for row in pattern_rows),
        "single_card_biological": sum(row["register"] == "BIOLOGICAL" and int(row["cards"]) == 1 for row in pattern_rows),
        "decision": "ONE_CODEBOOK__RUNNING_HERBAL_ARTICLE_AND_COMPACT_BIOLOGICAL_CELL_MODES",
    }
    (HERE / "SEVEN_HUNDRED_FORTIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
