#!/usr/bin/env python3
"""Build Pass 728: turn the six cross-register bigrams into four teaching templates."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P724 = ROOT / "experiments/yolo/sidequest_semantic_concrete_medium_revision_seven_hundred_twenty_fourth"
P727 = ROOT / "experiments/yolo/sidequest_semantic_what_how_bridge_seven_hundred_twenty_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


TEMPLATES = [
    {
        "template_id": "PT1", "name": "POSTFIX_MEASURE",
        "licensed_bigrams": "PROC008>PROC009 | PROC013>PROC009 | PROC019>PROC009",
        "abstract_form": "X + AIIN", "apprentice_rule_de": "Führe X bis zum vorgeschriebenen Maß oder Arbeitsgrad.",
        "short_reading_de": "X BIS ZUM MASS", "semantic_load": "AIIN=Mass; X liefert Handlung oder aktuellen Posten",
        "counter_rule": "AIIN benennt weder Stoff noch Gleichheit.",
    },
    {
        "template_id": "PT2", "name": "PREFIX_MEASURED_ITEM",
        "licensed_bigrams": "PROC009>PROC019", "abstract_form": "AIIN + Y",
        "apprentice_rule_de": "Halte den aktuell gemeinten Posten im vorgeschriebenen Maß bereit.",
        "short_reading_de": "DIESEN POSTEN NACH MASS", "semantic_load": "AIIN=Mass; Y=dieser aktuelle Posten",
        "counter_rule": "Kein zweiter Operand und kein Gleichheitszeichen.",
    },
    {
        "template_id": "PT3", "name": "CURRENT_PREPARATION",
        "licensed_bigrams": "PROC016>PROC019", "abstract_form": "OR + Y",
        "apprentice_rule_de": "Behandle den laufenden Posten als den gegenwärtigen Ansatz.",
        "short_reading_de": "DIESER ANSATZ", "semantic_load": "OR=Ansatz; Y=aktuell gemeinter Posten",
        "counter_rule": "Kein bestimmter Pflanzenname und kein bestimmtes Becken.",
    },
    {
        "template_id": "PT4", "name": "CONTINUE_PREPARATION",
        "licensed_bigrams": "PROC022>PROC013", "abstract_form": "OL+OR + OL",
        "apprentice_rule_de": "Arbeite mit demselben Ansatz weiter.",
        "short_reading_de": "DENSELBEN ANSATZ FORTSETZEN", "semantic_load": "OL+OR=fortgesetzter Ansatz; OL=weiter",
        "counter_rule": "Keine neue Charge und kein Seitenverweis.",
    },
]


BIGRAM_TEMPLATE = {
    "PROC008>PROC009": "PT1", "PROC013>PROC009": "PT1", "PROC019>PROC009": "PT1",
    "PROC009>PROC019": "PT2", "PROC016>PROC019": "PT3", "PROC022>PROC013": "PT4",
}


OCCURRENCE_READINGS = {
    ("H1-S001", "PROC008>PROC009"): "Diesen Posten bis zum Maß ansetzen.",
    ("B3-S030", "PROC008>PROC009"): "Diesen Posten bis zum Maß ansetzen.",
    ("H2-S001", "PROC009>PROC019"): "Den aktuellen Posten nach dem Maß beibehalten.",
    ("B2-S012", "PROC009>PROC019"): "Den aktuellen Posten nach dem Maß beibehalten.",
    ("B3-S003", "PROC009>PROC019"): "Den aktuellen Posten nach dem Maß beibehalten.",
    ("H2-S002", "PROC013>PROC009"): "Bis zum Maß weiterarbeiten.",
    ("B6-S001", "PROC013>PROC009"): "Bis zum Maß weiterarbeiten.",
    ("H2-S003", "PROC016>PROC019"): "Diesen Ansatz als laufenden Posten führen.",
    ("H4-S004", "PROC016>PROC019"): "Diesen Ansatz als laufenden Posten führen.",
    ("B4-S014", "PROC016>PROC019"): "Diesen Ansatz als laufenden Posten führen.",
    ("H2-S001", "PROC019>PROC009"): "Diesen Posten bis zum Maß führen.",
    ("H3-S003", "PROC019>PROC009"): "Diesen Posten bis zum Maß führen.",
    ("B3-S003", "PROC019>PROC009"): "Diesen Posten bis zum Maß führen.",
    ("B3-S021", "PROC019>PROC009"): "Diesen Posten bis zum Maß führen.",
    ("H2-S002", "PROC022>PROC013"): "Mit demselben Ansatz weiterarbeiten.",
    ("B1-S002", "PROC022>PROC013"): "Mit demselben Ansatz weiterarbeiten.",
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P724 / "SEVEN_HUNDRED_TWENTY_FOURTH_381_EVENTS.tsv")
    statements = read(P724 / "SEVEN_HUNDRED_TWENTY_FOURTH_116_STATEMENTS.tsv")
    bigrams = read(P727 / "SEVEN_HUNDRED_TWENTY_SEVENTH_6_SHARED_BIGRAMS.tsv")

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    statement_lookup = {row["statement_id"]: row for row in statements}

    occurrence_rows = []
    for bigram in bigrams:
        cards = tuple(bigram["card_sequence"].split(">"))
        for statement_id, sequence in by_statement.items():
            sequence_cards = [row["card_no"] for row in sequence]
            for index in range(len(sequence_cards) - 1):
                if tuple(sequence_cards[index : index + 2]) != cards:
                    continue
                pair = sequence[index : index + 2]
                key = (statement_id, bigram["card_sequence"])
                occurrence_rows.append({
                    "occurrence_id": f"PO{len(occurrence_rows) + 1:02d}",
                    "bridge_id": bigram["bridge_id"], "template_id": BIGRAM_TEMPLATE[bigram["card_sequence"]],
                    "register": "HERBAL_WHAT" if statement_id.startswith("H") else "BIOLOGICAL_HOW",
                    "statement_id": statement_id, "page": pair[0]["page"], "record": pair[0]["record"],
                    "event_ids": ",".join(row["event_id"] for row in pair),
                    "surface_pair": " ".join(row["observed_surface"] for row in pair),
                    "card_pair": bigram["card_sequence"],
                    "component_pair": ">".join(row["component_recipe"] for row in pair),
                    "local_template_reading_de": OCCURRENCE_READINGS[key],
                    "full_statement_de": statement_lookup[statement_id]["pass724_working_reading_de"],
                    "direct_cross_reference": "NONE",
                })

    assignment_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        assignment_by_statement[str(row["statement_id"])].append(row)
    statement_rows = []
    for row in statements:
        assigned = assignment_by_statement[row["statement_id"]]
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "surface_sequence": row["surface_sequence"],
            "component_sequence": row["component_sequence"],
            "portable_templates": ",".join(dict.fromkeys(str(item["template_id"]) for item in assigned)) or "NONE",
            "portable_occurrences": len(assigned),
            "template_expansions_de": " | ".join(str(item["local_template_reading_de"]) for item in assigned) or "NONE",
            "complete_reading_de": row["pass724_working_reading_de"],
            "form_owner_boundary_status": "UNCHANGED",
        })

    record_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in occurrence_rows:
        record_counts[str(row["record"])][str(row["template_id"])] += 1
    record_rows = []
    for record in [f"H{i}" for i in range(1, 6)] + [f"B{i}" for i in range(1, 7)]:
        count = record_counts[record]
        record_rows.append({
            "record": record, "register": "HERBAL_WHAT" if record.startswith("H") else "BIOLOGICAL_HOW",
            "PT1_postfix_measure": count["PT1"], "PT2_prefix_measured_item": count["PT2"],
            "PT3_current_preparation": count["PT3"], "PT4_continue_preparation": count["PT4"],
            "portable_template_occurrences": sum(count.values()),
            "teaching_status": "USES_PORTABLE_MINIGRAMMAR" if count else "WHOLE_CARD_ONLY_IN_THIS_SLICE",
        })

    write("SEVEN_HUNDRED_TWENTY_EIGHTH_4_TEACHING_TEMPLATES.tsv", TEMPLATES)
    write("SEVEN_HUNDRED_TWENTY_EIGHTH_16_TEMPLATE_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_TWENTY_EIGHTH_116_STATEMENT_TEMPLATE_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDRED_TWENTY_EIGHTH_11_RECORD_TEMPLATE_SUMMARY.tsv", record_rows)

    manual = """# Vier portable Mini-Schablonen für den Lehrling

## PT1 — `X AIIN`

**Lies:** „Führe X bis zum vorgeschriebenen Maß oder Arbeitsgrad.“

X kann der aktuelle Posten (`Y`), sein Ansetzen (`OK+Y`) oder seine Fortsetzung (`OL`) sein. AIIN fügt keinen Stoff und keine Zahl hinzu; es setzt die Sollgröße.

## PT2 — `AIIN Y`

**Lies:** „Halte den aktuell gemeinten Posten im vorgeschriebenen Maß bereit.“

Das ist die vorangestellte Variante. Sie macht Y nicht zu einem zweiten Gegenstand.

## PT3 — `OR Y`

**Lies:** „dieser laufende Ansatz“.

OR liefert die Sache, Y bindet sie an den aktuellen Bild-/Recordposten.

## PT4 — `OL+OR OL`

**Lies:** „mit demselben Ansatz weiterarbeiten“.

Die erste Karte ruft den fortgesetzten Ansatz auf; die zweite hält die Fortsetzung offen.

## Zusammensetzung `Y AIIN Y`

PT1 und PT2 überlappen in einer Dreierform:

> Diesen Posten bis zum Maß führen und mit demselben weiterarbeiten.

Das ist eine Maßklammer. Sie ist einfacher und besser lehrbar als die frühere Vermutung „gleiche Teile“ oder ein Gleichheitsrahmen: Es gibt keine zwei unabhängig benannten Operanden.
"""
    (HERE / "SEVEN_HUNDRED_TWENTY_EIGHTH_FOUR_TEMPLATE_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    report = f"""# Pass 728 — portable Mini-Grammatik

## Ergebnis

Die sechs Herbal/Bio-Brücken besitzen zusammen {len(occurrence_rows)} feste Vorkommen und lassen sich ohne neue Karte auf vier Lehrformen reduzieren:

1. `X AIIN` — X bis zum Maß führen.
2. `AIIN Y` — diesen Posten nach Maß bereithalten.
3. `OR Y` — dieser laufende Ansatz.
4. `OL+OR OL` — mit demselben Ansatz weiterarbeiten.

Damit wird `Y–AIIN–Y` konkret revidiert. Die alte attraktive Lesung „gleiche Teile / Gleichheitsrahmen“ wird aufgegeben. Die einfachste Werkstattlektüre ist:

> Diesen Posten bis zum Maß führen und mit demselben weiterarbeiten.

Der Grund ist handwerklich: Y bindet auf beiden Seiten denselben aktuellen Posten; AIIN liefert die Sollgröße. Es fehlen zwei unabhängig adressierte Mengen, die eine Gleichheitslesung bräuchte.

## Reichweite

- {sum(row['register'] == 'HERBAL_WHAT' for row in occurrence_rows)} der 16 Vorkommen liegen in Herbal, {sum(row['register'] == 'BIOLOGICAL_HOW' for row in occurrence_rows)} in Biological.
- Die Schablonen erscheinen in {sum(row['portable_template_occurrences'] != 0 for row in record_rows)} von 11 Records.
- Sie ändern keine der 381 Karten, 116 Aussagen oder Bildbesitzer.
- Sie erklären eine gemeinsame Schreibtechnik, aber weiterhin keinen direkten H→B-Link.

## Was ein Lehrling lernt

Der Lehrling muss keine vollständige Sprache beherrschen. Er lernt vier kurze Montagegriffe und setzt dazwischen gelernte Fachkarten. Das passt zur bisherigen Mischtheorie aus produktiven Kürzeln und memorierten Ganzkarten: Die Mini-Grammatik trägt Maß, Referenz und Fortsetzung; der konkrete Stoff oder Arbeitsgang bleibt in der Fachkarte und im Bild.

## Nächster Hebel

Als Nächstes sollen alle AIIN- und AIN-Kontexte getrennt werden. Wenn AIIN wirklich Sollmaß und AIN wirklich Portion ist, muss die komplette feste Seitenedition zwei verschiedene, praktisch lesbare Reihen ergeben. Dort kann die nächste echte Wortstamm-Komposition entstehen.
"""
    (HERE / "SEVEN_HUNDRED_TWENTY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "templates": len(TEMPLATES), "portable_occurrences": len(occurrence_rows),
        "herbal_occurrences": sum(row["register"] == "HERBAL_WHAT" for row in occurrence_rows),
        "bio_occurrences": sum(row["register"] == "BIOLOGICAL_HOW" for row in occurrence_rows),
        "records_using_templates": sum(row["portable_template_occurrences"] != 0 for row in record_rows),
        "statements": len(statement_rows), "events_bound": sum(int(row["events"]) for row in statement_rows),
        "form_changes": 0, "direct_cross_references": 0,
        "revised_old_y_aiin_y_gloss": "FROM_EQUAL_PARTS_TO_CURRENT_ITEM_MEASURE_BRACKET",
        "decision": "SIX_SHARED_BIGRAMS_REDUCE_TO_FOUR_PORTABLE_TEACHING_TEMPLATES",
    }
    (HERE / "SEVEN_HUNDRED_TWENTY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
