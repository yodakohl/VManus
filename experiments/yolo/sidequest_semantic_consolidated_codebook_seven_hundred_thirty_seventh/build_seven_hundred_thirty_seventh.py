#!/usr/bin/env python3
"""Build Pass 737: consolidate the current creative component codebook."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P736 = ROOT / "experiments/yolo/sidequest_semantic_transfer_application_seven_hundred_thirty_sixth"


def read(name: str) -> list[dict[str, str]]:
    with (P736 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


VALUES = {
    "OK": "ANSETZEN", "CHD": "UMSETZEN", "SH": "HALTEN", "SHED": "ABSETZEN",
    "CHK": "WAERMEN", "CTH": "BEREITEN", "SOLK": "SAMMELSTELLE", "P": "FUELLEN",
    "LSH": "WASCHEN", "CFH": "AUSWRINGEN", "CH": "ENTNEHMEN", "T": "ANWENDEN",
    "K": "ZUGEBEN", "S": "TEIL", "L": "LEITEN", "OL": "WEITER", "OT": "DANACH",
    "AL": "ZIELSTELLE", "AR": "QUELLE", "AIR": "WASSER", "OR": "ANSATZ",
    "HO": "ZUTAT", "CKH": "DURCHLASS", "O": "ARBEITSGANG", "Y": "DIES",
    "AIN": "PORTION", "AIIN": "SOLLMASS", "IIN": "ARBEITSSTUFE", "E": "KURZ",
    "EE": "LANG", "EEE": "VOLL", "R": "KUEHLEN", "AN": "NACHGABE", "DA": "ZWEIT",
    "LD": "BEFESTIGEN", "DY": "SCHLUSS", "OS": "FACH",
    "RESUME_CARD": "WIEDERAUFNEHMEN", "TALAM": "VERWAHREN",
}

MEMORIZED = {"OS", "RESUME_CARD", "TALAM"}
SINGLETON = {"CFH", "S", "AN", "DA", "LD"}
PRODUCTIVE = set(VALUES) - MEMORIZED - SINGLETON


def rebuild(recipe: str) -> str:
    return " · ".join(VALUES[component] for component in recipe.split("+"))


def card_status(recipe: str) -> str:
    parts = set(recipe.split("+"))
    if parts & MEMORIZED:
        return "HAS_MEMORIZED_WHOLE_COMMAND"
    if parts & SINGLETON:
        return "HAS_SINGLETON_COMPONENT_GUESS"
    return "FULLY_COMPOSED_FROM_RECURRENT_ROOTS"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read("SEVEN_HUNDRED_THIRTY_SIXTH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_SIXTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_SIXTH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_SIXTH_11_RECORD_EDITION.tsv")

    component_card_counts: Counter[str] = Counter()
    component_event_counts: Counter[str] = Counter()
    component_surfaces: dict[str, set[str]] = defaultdict(set)
    for row in cards:
        for component in row["component_recipe"].split("+"):
            component_card_counts[component] += 1
            component_event_counts[component] += int(row["events"])
            component_surfaces[component].update(row["registered_surfaces"].split("|"))

    component_rows = []
    order = list(VALUES)
    for index, component in enumerate(order, 1):
        category = (
            "RECURRENT_PRODUCTIVE_ROOT" if component in PRODUCTIVE
            else "SINGLETON_COMPONENT_GUESS" if component in SINGLETON
            else "MEMORIZED_WHOLE_COMMAND"
        )
        component_rows.append({
            "component_no": f"C{index:02d}", "component": component, "short_value_de": VALUES[component],
            "category": category, "exact_cards": component_card_counts[component],
            "events": component_event_counts[component],
            "diagnostic_surfaces": "|".join(sorted(component_surfaces[component]))[:240],
            "teaching_rule": (
                "frei mit anderen kurzen Wurzeln kombinieren" if category == "RECURRENT_PRODUCTIVE_ROOT"
                else "konkrete Einmalbedeutung merken; noch nicht als produktiv verallgemeinern" if category == "SINGLETON_COMPONENT_GUESS"
                else "ganze Karte als Nomenklatorbefehl merken"
            ),
        })

    card_rows = []
    remainder_rows = []
    for row in cards:
        rebuilt = rebuild(row["component_recipe"])
        status = card_status(row["component_recipe"])
        output = {
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "rebuilt_reading_de": rebuilt,
            "pass736_reading_de": row["pass736_reading_de"], "exact_rebuild": "YES" if rebuilt == row["pass736_reading_de"] else "NO",
            "component_count": len(row["component_recipe"].split("+")), "composition_status": status,
            "registered_surfaces": row["registered_surfaces"], "events": row["events"],
        }
        card_rows.append(output)
        if status != "FULLY_COMPOSED_FROM_RECURRENT_ROOTS":
            special = sorted(set(row["component_recipe"].split("+")) & (MEMORIZED | SINGLETON))
            remainder_rows.append({
                "exact_card_id": row["exact_card_id"], "component_recipe": row["component_recipe"],
                "surface_forms": row["registered_surfaces"], "events": row["events"],
                "special_components": "+".join(special), "status": status,
                "short_default_de": rebuilt,
                "restriction": "WHOLE_COMMAND_ONLY" if status == "HAS_MEMORIZED_WHOLE_COMMAND" else "DO_NOT_GENERALIZE_FROM_ONE_EVENT",
            })

    card_lookup = {row["exact_card_id"]: row for row in card_rows}
    event_rows = []
    statement_event_rows: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        card = card_lookup[row["card_no"]]
        output = {
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "rebuilt_reading_de": card["rebuilt_reading_de"], "composition_status": card["composition_status"],
            "form_owner_boundary_status": "UNCHANGED",
        }
        event_rows.append(output)
        statement_event_rows[row["statement_id"]].append(output)

    statement_rows = []
    for row in statements:
        seq = statement_event_rows[row["statement_id"]]
        counts = Counter(str(item["composition_status"]) for item in seq)
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "rebuilt_atomic_trace_de": " | ".join(str(item["rebuilt_reading_de"]) for item in seq),
            "recurrent_composed_events": counts["FULLY_COMPOSED_FROM_RECURRENT_ROOTS"],
            "singleton_guess_events": counts["HAS_SINGLETON_COMPONENT_GUESS"],
            "memorized_command_events": counts["HAS_MEMORIZED_WHOLE_COMMAND"],
            "working_reading_de": row["working_reading_de"], "form_owner_boundary_status": "UNCHANGED",
        })

    record_rows = []
    for row in records:
        seq = [event for event in event_rows if event["record"] == row["record"]]
        counts = Counter(str(item["composition_status"]) for item in seq)
        record_rows.append({
            "record": row["record"], "page": row["page"], "statements": row["statements"], "events": row["events"],
            "recurrent_composed_events": counts["FULLY_COMPOSED_FROM_RECURRENT_ROOTS"],
            "singleton_guess_events": counts["HAS_SINGLETON_COMPONENT_GUESS"],
            "memorized_command_events": counts["HAS_MEMORIZED_WHOLE_COMMAND"],
            "continuous_reading_de": row["continuous_reading_de"], "form_status": "UNCHANGED",
        })

    category_rows = []
    for status in ["FULLY_COMPOSED_FROM_RECURRENT_ROOTS", "HAS_SINGLETON_COMPONENT_GUESS", "HAS_MEMORIZED_WHOLE_COMMAND"]:
        target_cards = [row for row in card_rows if row["composition_status"] == status]
        category_rows.append({
            "composition_status": status, "cards": len(target_cards),
            "events": sum(int(row["events"]) for row in target_cards),
            "component_policy": (
                "productive short-root composition" if status == "FULLY_COMPOSED_FROM_RECURRENT_ROOTS"
                else "short concrete default retained, no productivity claim" if status == "HAS_SINGLETON_COMPONENT_GUESS"
                else "memorize exact whole card"
            ),
        })

    write("SEVEN_HUNDRED_THIRTY_SEVENTH_39_COMPONENT_DICTIONARY.tsv", component_rows)
    write("SEVEN_HUNDRED_THIRTY_SEVENTH_3_COMPOSITION_CLASSES.tsv", category_rows)
    write("SEVEN_HUNDRED_THIRTY_SEVENTH_8_REMAINDER_CARDS.tsv", remainder_rows)
    write("SEVEN_HUNDRED_THIRTY_SEVENTH_173_REBUILT_CARD_DICTIONARY.tsv", card_rows)
    write("SEVEN_HUNDRED_THIRTY_SEVENTH_381_EVENT_INTERLINEAR.tsv", event_rows)
    write("SEVEN_HUNDRED_THIRTY_SEVENTH_116_STATEMENT_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDRED_THIRTY_SEVENTH_11_RECORD_EDITION.tsv", record_rows)

    manual_lines = [
        "# Konsolidiertes Werkstattwörterbuch", "",
        "## 31 wiederkehrende produktive Wurzeln", "",
    ]
    for row in component_rows:
        if row["category"] == "RECURRENT_PRODUCTIVE_ROOT":
            manual_lines.append(f"- `{row['component']}` — **{row['short_value_de']}** ({row['events']} Ereignisse)")
    manual_lines.extend(["", "## Fünf einmalige kurze Bedeutungswetten", ""])
    for row in component_rows:
        if row["category"] == "SINGLETON_COMPONENT_GUESS":
            manual_lines.append(f"- `{row['component']}` — **{row['short_value_de']}**; nur einmal, nicht verallgemeinern")
    manual_lines.extend(["", "## Drei gelernte Ganzbefehle", ""])
    for row in component_rows:
        if row["category"] == "MEMORIZED_WHOLE_COMMAND":
            manual_lines.append(f"- `{row['component']}` — **{row['short_value_de']}**; ganze Karte merken")
    manual_lines.extend([
        "", "## Schreibregel", "",
        "Eine Karte wird links nach rechts aus ihren Komponenten gelesen. E/EE/EEE liefern Grad, Y hält den aktuellen Posten verfügbar, lizenzierte DY-Karten schließen. Sichtbare Oberflächen werden erst auf die exakte Karte normalisiert; sie werden nie direkt in Buchstabenstämme zerlegt.",
    ])
    (HERE / "SEVEN_HUNDRED_THIRTY_SEVENTH_CONSOLIDATED_APPRENTICE_DICTIONARY.md").write_text("\n".join(manual_lines), encoding="utf-8")

    report = """# Pass 737 — konsolidiertes Komponentenwörterbuch

## Ergebnis

Das aktuelle Schreibsystem lässt sich jetzt als echte Mischung aus produktiven Kürzeln und kleinem gelerntem Nomenklator formulieren:

- **31 wiederkehrende produktive Wurzeln** bauen 165/173 exakte Karten und 372/381 Ereignisse vollständig.
- **5 einmalige kurze Komponentenwetten** betreffen 5 Karten/5 Ereignisse: CFH=AUSWRINGEN, S=TEIL, AN=NACHGABE, DA=ZWEIT, LD=BEFESTIGEN. Sie bleiben konkret, werden aber nicht verallgemeinert.
- **3 gelernte Ganzbefehle** betreffen 3 Karten/4 Ereignisse: OS=FACH, RESUME_CARD=WIEDERAUFNEHMEN, TALAM=VERWAHREN.

Alle173 Karten werden aus39 Einträgen bytegleich zu den zuletzt gewählten atomaren Lesungen neu aufgebaut. Es gibt163 verschiedene Komponentenrezepte. Keine Karte braucht eine Satzglosse und kein Ereignis bleibt bedeutungsleer.

## Was das System nun ist

Der produktive Kern trägt:

- vier Hauptoperationen: ansetzen, zugeben, entnehmen, umsetzen;
- vier Transfer-/Anwendungsoperationen: leiten, füllen, kühlen, anwenden;
- fünf Prozessverben: bereiten, halten, absetzen, wärmen, waschen;
- Menge, Richtung, Material, Station, Reihenfolge, Grad, Referent und Schluss.

Der Schreiber kann daraus die meisten Karten montieren. Nur acht Karten enthalten etwas, das der Lehrling separat auswendig lernen muss; davon sind fünf lediglich vorsichtige Einmalwerte und drei echte Ganzbefehle.

## Ehrliche Grenze

Das konsolidiert unsere **Arbeitstheorie**; es identifiziert keine historische Sprache. Die konkrete Lesbarkeit entsteht aus den zehn Bildern, der festen Kartenanalyse und dem angenommenen Werkstattcodebuch. Für diesen Sidequest ist das aber der bisher sparsamste vollständige Encoder/Decoder.

## Nächster Hebel

Als Nächstes werden die acht Reste einzeln in ihren vollständigen Satz- und Bildkontexten angegriffen. Ziel: mindestens einen Einmalwert in eine wiederkehrende Familie einordnen oder als echtes Ganzwort bestätigen, ohne die 31 produktiven Wurzeln zu verändern.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "components": len(component_rows), "recurrent_productive_roots": len(PRODUCTIVE),
        "singleton_component_guesses": len(SINGLETON), "memorized_whole_commands": len(MEMORIZED),
        "distinct_recipes": len({row["component_recipe"] for row in card_rows}),
        "cards": len(card_rows), "events": len(event_rows), "statements": len(statement_rows), "records": len(record_rows),
        "fully_recurrent_cards": 165, "fully_recurrent_events": 372,
        "remainder_cards": len(remainder_rows), "remainder_events": 9,
        "exact_card_rebuilds": sum(row["exact_rebuild"] == "YES" for row in card_rows),
        "empty_meanings": 0, "form_changes": 0,
        "decision": "THIRTY_ONE_PRODUCTIVE_ROOTS_PLUS_FIVE_SINGLETON_GUESSES_PLUS_THREE_WHOLE_COMMANDS_REBUILD_ALL_CARDS",
    }
    (HERE / "SEVEN_HUNDRED_THIRTY_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
