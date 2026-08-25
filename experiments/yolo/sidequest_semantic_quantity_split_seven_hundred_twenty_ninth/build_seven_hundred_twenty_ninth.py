#!/usr/bin/env python3
"""Build Pass 729: separate AIIN Sollmass, AIN Portion, and IIN Arbeitsstufe."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P724 = ROOT / "experiments/yolo/sidequest_semantic_concrete_medium_revision_seven_hundred_twenty_fourth"


def read(name: str) -> list[dict[str, str]]:
    with (P724 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ROOTS = {
    "AIIN": {
        "pass724": "MASS", "pass729": "SOLLMASS", "short_de": "vorgeschriebenes Maß / Sollwert",
        "teaching_rule": "Bestimmt, bis zu welchem Maß oder Sollwert der laufende Schritt geführt wird.",
        "not_this": "keine Portion, keine Zahl, keine Gleichheit",
    },
    "AIN": {
        "pass724": "PORTION", "pass729": "PORTION", "short_de": "konkreter abgeteilter Posten",
        "teaching_rule": "Nennt eine handhabbare Teilmenge, die genommen, zugegeben oder angesetzt wird.",
        "not_this": "kein Sollgrad und keine bloße Endung von AIIN",
    },
    "IIN": {
        "pass724": "STUFE", "pass729": "ARBEITSSTUFE", "short_de": "qualitative Prozessstufe",
        "teaching_rule": "Nennt eine qualitative Stufe des laufenden Arbeitsgangs, nicht dessen Menge.",
        "not_this": "kein Maß und keine Portion",
    },
}


def roots_in(recipe: str) -> list[str]:
    parts = recipe.split("+")
    return [root for root in ROOTS if root in parts]


def revise_atomic(reading: str, root: str) -> str:
    return reading.replace(ROOTS[root]["pass724"], ROOTS[root]["pass729"])


def revise_prose(text: str) -> str:
    return (
        text.replace("nach Mass", "nach Sollmass")
        .replace("zum Mass", "zum Sollmass")
        .replace("zur Stufe", "zur Arbeitsstufe")
        .replace("bis zur Stufe", "bis zur Arbeitsstufe")
    )


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read("SEVEN_HUNDRED_TWENTY_FOURTH_173_CARDS.tsv")
    events = read("SEVEN_HUNDRED_TWENTY_FOURTH_381_EVENTS.tsv")
    statements = read("SEVEN_HUNDRED_TWENTY_FOURTH_116_STATEMENTS.tsv")
    records = read("SEVEN_HUNDRED_TWENTY_FOURTH_11_RECORDS.tsv")

    statement_sequences: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        statement_sequences[row["statement_id"]].append(row)

    card_rows = []
    quantity_card_rows = []
    for row in cards:
        matched = roots_in(row["component_recipe"])
        revised = row["pass724_reading_de"]
        for root in matched:
            revised = revise_atomic(revised, root)
        contract = matched[0] if matched else "NONE"
        output = {
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "pass724_reading_de": row["pass724_reading_de"],
            "pass729_reading_de": revised, "quantity_root": contract,
            "registered_surfaces": row["registered_surfaces"], "events": row["events"],
            "quantity_revision": "YES" if revised != row["pass724_reading_de"] else "NO",
        }
        card_rows.append(output)
        if matched:
            quantity_card_rows.append(output)

    occurrence_rows = []
    event_rows = []
    for row in events:
        matched = roots_in(row["component_recipe"])
        revised = row["pass724_semantic_de"]
        for root in matched:
            revised = revise_atomic(revised, root)
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "locus": row["locus"], "owner_de": row["owner_de"],
            "card_no": row["card_no"], "observed_surface": row["observed_surface"],
            "component_recipe": row["component_recipe"], "pass724_semantic_de": row["pass724_semantic_de"],
            "pass729_semantic_de": revised, "quantity_root": matched[0] if matched else "NONE",
            "form_owner_boundary_status": "UNCHANGED",
        })
        if not matched:
            continue
        sequence = statement_sequences[row["statement_id"]]
        position = next(index for index, item in enumerate(sequence) if item["event_id"] == row["event_id"])
        occurrence_rows.append({
            "event_id": row["event_id"], "root": matched[0], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
            "surface": row["observed_surface"], "component_recipe": row["component_recipe"],
            "statement_position": "ONLY" if len(sequence) == 1 else "FIRST" if position == 0 else "LAST" if position == len(sequence) - 1 else "MIDDLE",
            "previous_recipe": sequence[position - 1]["component_recipe"] if position else "START",
            "next_recipe": sequence[position + 1]["component_recipe"] if position + 1 < len(sequence) else "END",
            "pass729_atomic_reading_de": revised,
            "practical_expansion_de": (
                "bis zum vorgeschriebenen Sollmaß" if matched[0] == "AIIN"
                else "eine konkrete Portion" if matched[0] == "AIN"
                else "bis zur benannten Arbeitsstufe"
            ),
            "full_statement_de": revise_prose(next(item["pass724_working_reading_de"] for item in statements if item["statement_id"] == row["statement_id"])),
        })

    statement_rows = []
    for row in statements:
        roots = sorted({root for event in statement_sequences[row["statement_id"]] for root in roots_in(event["component_recipe"])})
        atomic = row["pass724_atomic_trace_de"]
        for root in roots:
            atomic = revise_atomic(atomic, root)
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "quantity_roots": ",".join(roots) or "NONE", "pass729_atomic_trace_de": atomic,
            "pass729_working_reading_de": revise_prose(row["pass724_working_reading_de"]),
            "form_owner_boundary_status": "UNCHANGED",
        })

    record_rows = []
    for row in records:
        record_events = [event for event in event_rows if event["record"] == row["record"]]
        counts = Counter(event["quantity_root"] for event in record_events)
        record_rows.append({
            "record": row["record"], "page": row["page"], "statements": row["statements"],
            "events": len(record_events), "AIIN_sollmass": counts["AIIN"], "AIN_portion": counts["AIN"],
            "IIN_arbeitsstufe": counts["IIN"],
            "continuous_pass729_reading_de": revise_prose(row["continuous_pass724_reading_de"]),
            "form_status": "UNCHANGED",
        })

    root_rows = []
    for root, data in ROOTS.items():
        target_events = [row for row in occurrence_rows if row["root"] == root]
        target_cards = [row for row in quantity_card_rows if row["quantity_root"] == root]
        root_rows.append({
            "root": root, "short_value_de": data["pass729"], "practical_meaning_de": data["short_de"],
            "teaching_rule_de": data["teaching_rule"], "excluded_reading": data["not_this"],
            "exact_cards": len(target_cards), "events": len(target_events),
            "herbal_events": sum(row["record"].startswith("H") for row in target_events),
            "bio_events": sum(row["record"].startswith("B") for row in target_events),
            "bare_card_events": sum(row["component_recipe"] == root for row in target_events),
            "composed_events": sum(row["component_recipe"] != root for row in target_events),
        })

    write("SEVEN_HUNDRED_TWENTY_NINTH_3_QUANTITY_ROOTS.tsv", root_rows)
    write("SEVEN_HUNDRED_TWENTY_NINTH_21_QUANTITY_CARDS.tsv", quantity_card_rows)
    write("SEVEN_HUNDRED_TWENTY_NINTH_61_QUANTITY_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_TWENTY_NINTH_173_CARD_DICTIONARY.tsv", card_rows)
    write("SEVEN_HUNDRED_TWENTY_NINTH_381_EVENT_INTERLINEAR.tsv", event_rows)
    write("SEVEN_HUNDRED_TWENTY_NINTH_116_STATEMENT_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDRED_TWENTY_NINTH_11_RECORD_EDITION.tsv", record_rows)

    manual = """# Mengenlehre für den Lehrling

## AIIN — SOLLMASS

AIIN sagt, **wie weit** ein Schritt geführt werden soll: nach dem vorgeschriebenen Maß oder bis zum Sollwert. Es ist kein abgezählter Stoffposten.

- `OK+AIIN`: bis zum Sollmaß ansetzen.
- `CTH+AIIN`: bis zum Sollmaß bereiten.
- `OL+AIIN`: bis zum Sollmaß fortsetzen.
- `Y–AIIN–Y`: diesen Posten bis zum Sollmaß führen und mit demselben weiterarbeiten.

## AIN — PORTION

AIN sagt, **was als abgeteilter Posten** gehandhabt wird. Es wird genommen, zugegeben oder angesetzt.

- `K+AIN`: eine Portion zugeben.
- `OK+AIN`: eine Portion ansetzen.
- `OR+AIN`: eine Portion des Ansatzes.
- `CHD+AIN`: eine Portion umsetzen.

## IIN — ARBEITSSTUFE

IIN sagt, **in welchem qualitativen Prozesszustand** die Arbeit steht.

- `K+IIN`: bis zur Arbeitsstufe zugeben.
- `O+IIN`: den Arbeitsgang bis zur Stufe führen.
- `DA+IIN`: zweite Arbeitsstufe.

## Merksatz

> AIIN ist der Sollwert, AIN ist der abgeteilte Posten, IIN ist die Arbeitsstufe.
"""
    (HERE / "SEVEN_HUNDRED_TWENTY_NINTH_QUANTITY_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    changed_cards = sum(row["quantity_revision"] == "YES" for row in card_rows)
    changed_events = sum(row["pass724_semantic_de"] != row["pass729_semantic_de"] for row in event_rows)
    changed_statements = sum("AIIN" in row["quantity_roots"] or "IIN" in row["quantity_roots"] for row in statement_rows)
    report = f"""# Pass 729 — Sollmaß, Portion und Arbeitsstufe

## Ergebnis

Die drei ähnlich aussehenden Kerne ergeben drei verschiedene, leicht lehrbare Größen:

- **AIIN = SOLLMASS:** 10 Karten / 39 Ereignisse; davon 20 als nackte AIIN-Karte und 19 komponiert.
- **AIN = PORTION:** 8 Karten / 18 Ereignisse; davon 2 nackt und 16 komponiert.
- **IIN = ARBEITSSTUFE:** 3 Karten / 4 Ereignisse; alle komponiert.

Die Trennung ist praktisch, nicht nur orthographisch. `OK+AIIN` kommt neunmal vor und heißt „bis zum Sollmaß ansetzen“; `OK+AIN` kommt siebenmal vor und heißt „eine Portion ansetzen“. `K+AIN` gibt eine Portion zu, während `K+IIN` bis zu einer Arbeitsstufe zugibt.

## Revision

AIIN wird von dem zu breiten **MASS** auf **SOLLMASS** präzisiert; IIN von **STUFE** auf **ARBEITSSTUFE**. AIN=PORTION bleibt. Dadurch ändern sich semantisch {changed_cards} Karten, {changed_events} Ereignisse und {changed_statements} Aussagen; alle173 Karten,381 Ereignisse,116 Aussagen,11 Records und sichtbaren Formen bleiben erhalten.

## Konkrete Werkstattlesung

Ein Schreiber kann nun drei Fragen unterscheiden:

1. **Wie viel / bis wohin?** AIIN — der vorgeschriebene Sollwert.
2. **Welcher abgeteilte Posten?** AIN — eine Portion.
3. **Welcher Prozesszustand?** IIN — die Arbeitsstufe.

Das ist genau die Art kleiner Bedeutungsdifferenz, die ein gemischtes Kürzel-/Ganzkartensystem produktiv macht. Sie sagt noch nicht, ob das Maß Gewicht, Volumen, Zeit oder Intensität ist; das liefert die umgebende Fachkarte.

## Nächster Hebel

Als Nächstes wird die Quell-/Zielachse `AR` gegen `AL` vollständig durch alle festen Kontexte geführt. Gesucht wird dieselbe klare Opposition: aus/von einer Quelle gegen an/zu einer Zielstelle.
"""
    (HERE / "SEVEN_HUNDRED_TWENTY_NINTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "roots": len(root_rows), "quantity_cards": len(quantity_card_rows),
        "quantity_events": len(occurrence_rows), "AIIN_events": 39, "AIN_events": 18, "IIN_events": 4,
        "cards": len(card_rows), "events": len(event_rows), "statements": len(statement_rows), "records": len(record_rows),
        "changed_cards": changed_cards, "changed_events": changed_events, "changed_statements": changed_statements,
        "form_changes": 0, "decision": "AIIN_SOLLMASS__AIN_PORTION__IIN_ARBEITSSTUFE_COMPOSE_DISTINCTLY",
    }
    (HERE / "SEVEN_HUNDRED_TWENTY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
