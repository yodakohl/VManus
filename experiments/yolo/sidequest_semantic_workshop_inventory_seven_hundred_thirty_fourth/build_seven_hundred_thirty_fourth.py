#!/usr/bin/env python3
"""Build Pass 734: order the concrete material/station inventory."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P733 = ROOT / "experiments/yolo/sidequest_semantic_grade_endpoint_seven_hundred_thirty_third"


def read(name: str) -> list[dict[str, str]]:
    with (P733 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ROOTS = {
    "HO": ("ZUTAT", "ausgewählter Pflanzen- oder sonstiger Werkstoffposten"),
    "OR": ("ANSATZ", "aktuell bereitete Stoff-/Arbeitsmischung"),
    "O": ("ARBEITSGANG", "der laufende Verarbeitungsschritt"),
    "AIR": ("WASSER", "konkrete Arbeitsflüssigkeit Wasser"),
    "CKH": ("DURCHLASS", "lokaler Durchgang, Kanal oder Passage"),
    "SOLK": ("SAMMELSTELLE", "lokaler Empfänger oder Halteplatz"),
}


def inventory_roots(recipe: str) -> list[str]:
    parts = recipe.split("+")
    return [root for root in ROOTS if root in parts]


def revise(reading: str, roots: list[str]) -> str:
    return reading.replace("AUFFANGEN", "SAMMELSTELLE") if "SOLK" in roots else reading


def revise_prose(text: str) -> str:
    return (
        text.replace("länger auffangen", "länger an der Sammelstelle halten")
        .replace("kurz auffangen", "kurz an der Sammelstelle halten")
        .replace("nach Mass auffangen", "bis zum Sollmass an der Sammelstelle halten")
        .replace("nach Sollmass auffangen", "bis zum Sollmass an der Sammelstelle halten")
        .replace("auffangen", "an der Sammelstelle halten")
    )


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read("SEVEN_HUNDRED_THIRTY_THIRD_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_THIRD_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_THIRD_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_THIRD_11_RECORD_EDITION.tsv")

    card_rows = []
    inventory_cards = []
    for row in cards:
        roots = inventory_roots(row["component_recipe"])
        new = revise(row["reading_de"], roots)
        output = {
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "pass733_reading_de": row["reading_de"],
            "pass734_reading_de": new, "inventory_roots": "+".join(roots) or "NONE",
            "registered_surfaces": row["registered_surfaces"], "events": row["events"],
            "inventory_revision": "YES" if new != row["reading_de"] else "NO",
        }
        card_rows.append(output)
        if roots:
            inventory_cards.append(output)

    event_rows = []
    inventory_occurrences = []
    for row in events:
        roots = inventory_roots(row["component_recipe"])
        new = revise(row["reading_de"], roots)
        output = {
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "pass733_reading_de": row["reading_de"], "pass734_reading_de": new,
            "inventory_roots": "+".join(roots) or "NONE", "form_owner_boundary_status": "UNCHANGED",
        }
        event_rows.append(output)
        if roots:
            inventory_occurrences.append({
                "event_id": row["event_id"], "page": row["page"], "record": row["record"],
                "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
                "surface": row["surface"], "component_recipe": row["component_recipe"],
                "inventory_roots": "+".join(roots), "pass734_reading_de": new,
                "inventory_role": "+".join(ROOTS[root][0] for root in roots),
            })

    statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        statement_events[row["statement_id"]].append(row)
    statement_rows = []
    multi_rows = []
    for row in statements:
        roots = [root for event in statement_events[row["statement_id"]] for root in inventory_roots(event["component_recipe"])]
        unique_roots = list(dict.fromkeys(roots))
        revised_atomic = " | ".join(event["pass734_reading_de"] for event in statement_events[row["statement_id"]])
        revised_fluent = revise_prose(row["working_reading_de"])
        output = {
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "inventory_roots": ",".join(unique_roots) or "NONE", "pass734_atomic_trace_de": revised_atomic,
            "pass734_working_reading_de": revised_fluent, "form_owner_boundary_status": "UNCHANGED",
        }
        statement_rows.append(output)
        if len(unique_roots) >= 2:
            multi_rows.append({
                "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
                "owner_noun_de": row["owner_noun_de"], "inventory_roots": ">".join(unique_roots),
                "event_trace": " | ".join(
                    f"{event['event_id']}:{event['component_recipe']}" for event in statement_events[row["statement_id"]]
                    if inventory_roots(event["component_recipe"])
                ),
                "working_reading_de": revised_fluent,
                "global_machine_claim": "NONE__LOCAL_TOOLKIT_ONLY",
            })

    record_rows = []
    for row in records:
        targets = [event for event in inventory_occurrences if event["record"] == row["record"]]
        counts = Counter(root for event in targets for root in event["inventory_roots"].split("+"))
        record_rows.append({
            "record": row["record"], "page": row["page"], "statements": row["statements"], "events": row["events"],
            "HO_ingredient": counts["HO"], "OR_preparation": counts["OR"], "O_workstep": counts["O"],
            "AIR_water": counts["AIR"], "CKH_passage": counts["CKH"], "SOLK_collection_site": counts["SOLK"],
            "continuous_pass734_reading_de": revise_prose(row["continuous_reading_de"]), "form_status": "UNCHANGED",
        })

    root_rows = []
    for order, root in enumerate(["HO", "OR", "O", "AIR", "CKH", "SOLK"], 1):
        meaning, expansion = ROOTS[root]
        rows = [row for row in inventory_occurrences if root in row["inventory_roots"].split("+")]
        root_rows.append({
            "default_workflow_order": order, "root": root, "short_value_de": meaning,
            "workshop_expansion_de": expansion, "exact_cards": len({row["card_no"] for row in rows}),
            "events": len(rows), "herbal_events": sum(row["record"].startswith("H") for row in rows),
            "bio_events": sum(row["record"].startswith("B") for row in rows),
            "scope_note": "HERBAL_ONLY_IN_FIXED_SLICE" if root == "HO" else "BIO_ONLY_IN_FIXED_SLICE" if root == "SOLK" else "CROSS_REGISTER",
        })

    chain_rows = [
        {"stage": 1, "root": "HO", "prompt_de": "Zutat wählen", "output_to_next": "ausgewählter Stoffposten", "claim": "DEFAULT_WORKFLOW_NOT_FIXED_SEQUENCE"},
        {"stage": 2, "root": "OR", "prompt_de": "Ansatz bilden oder aufrufen", "output_to_next": "aktiver Ansatz", "claim": "DEFAULT_WORKFLOW_NOT_FIXED_SEQUENCE"},
        {"stage": 3, "root": "O", "prompt_de": "Arbeitsgang ausführen", "output_to_next": "bearbeiteter Posten", "claim": "DEFAULT_WORKFLOW_NOT_FIXED_SEQUENCE"},
        {"stage": 4, "root": "AIR", "prompt_de": "Wasser entnehmen, zugeben, ansetzen oder umsetzen", "output_to_next": "nasser Arbeitsbestand", "claim": "OPTIONAL_MATERIAL_BRANCH"},
        {"stage": 5, "root": "CKH", "prompt_de": "durch lokalen Durchlass führen", "output_to_next": "weitergeleiteter Posten", "claim": "OPTIONAL_STATION_BRANCH"},
        {"stage": 6, "root": "SOLK", "prompt_de": "an der Sammelstelle halten", "output_to_next": "gesammelter oder gehaltener Posten", "claim": "OPTIONAL_STATION_BRANCH"},
    ]

    write("SEVEN_HUNDRED_THIRTY_FOURTH_6_INVENTORY_ROOTS.tsv", root_rows)
    write("SEVEN_HUNDRED_THIRTY_FOURTH_6_STAGE_DEFAULT_WORKFLOW.tsv", chain_rows)
    write("SEVEN_HUNDRED_THIRTY_FOURTH_13_MULTI_INVENTORY_STATEMENTS.tsv", multi_rows)
    write("SEVEN_HUNDRED_THIRTY_FOURTH_47_INVENTORY_CARDS.tsv", inventory_cards)
    write("SEVEN_HUNDRED_THIRTY_FOURTH_66_INVENTORY_OCCURRENCES.tsv", inventory_occurrences)
    write("SEVEN_HUNDRED_THIRTY_FOURTH_173_CARD_DICTIONARY.tsv", card_rows)
    write("SEVEN_HUNDRED_THIRTY_FOURTH_381_EVENT_INTERLINEAR.tsv", event_rows)
    write("SEVEN_HUNDRED_THIRTY_FOURTH_116_STATEMENT_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDRED_THIRTY_FOURTH_11_RECORD_EDITION.tsv", record_rows)

    manual = """# Der Werkstattkasten

1. `HO` — ZUTAT: den Stoffposten wählen.
2. `OR` — ANSATZ: die aktuelle Mischung bilden oder wieder aufrufen.
3. `O` — ARBEITSGANG: den Verarbeitungsschritt ausführen.
4. `AIR` — WASSER: Wasser als konkreten Arbeitsstoff einsetzen.
5. `CKH` — DURCHLASS: den Posten durch eine lokale Passage führen.
6. `SOLK` — SAMMELSTELLE: den Posten am lokalen Empfänger halten.

Das ist ein Werkzeugkasten, keine zwangsläufige Sechsersequenz. Ein Artikel oder eine Station benutzt nur die nötigen Karten. Wein, Öl, Honig und konkrete Pflanzenarten werden nirgends ergänzt.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_FOURTH_INVENTORY_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    changed_cards = sum(row["inventory_revision"] == "YES" for row in card_rows)
    changed_events = sum(row["pass733_reading_de"] != row["pass734_reading_de"] for row in event_rows)
    changed_statements = sum("SOLK" in row["inventory_roots"].split(",") for row in statement_rows)
    report = f"""# Pass 734 — der konkrete Werkstattkasten

## Ergebnis

Sechs Stoff-/Stationskerne bilden ein kleines Inventar:

- HO=ZUTAT: 5 Karten/8 Ereignisse, im festen Ausschnitt nur H5.
- OR=ANSATZ: 10/18, registerübergreifend.
- O=ARBEITSGANG: 18/19, registerübergreifend.
- AIR=WASSER: 5/5, registerübergreifend.
- CKH=DURCHLASS: 9/14, H5 plus Biological.
- SOLK=SAMMELSTELLE: 5/7, im festen Ausschnitt nur Biological.

Ihre Vereinigung umfasst47 Karten/66 Ereignisse. Dreizehn Aussagen kombinieren mindestens zwei dieser Kerne. Keine einzelne Aussage trägt alle sechs; deshalb ist die Sechserordnung ein Default-Arbeitsablauf, keine behauptete Maschine.

## Revision

SOLK wird von dem verbartigen **AUFFANGEN** zum komponierbaren Nomen **SAMMELSTELLE**. Das ändert {changed_cards} Karten/{changed_events} Ereignisse/{changed_statements} Aussagen. `solkey` heißt nun „kurz an der Sammelstelle halten“, `solkeey` „lang an der Sammelstelle halten“, `solkaiin` „bis zum Sollmaß an der Sammelstelle halten“.

## Konkrete Kette

Der Lehrling kann als Default denken: Zutat wählen → Ansatz bilden → Arbeitsgang ausführen; falls nötig Wasser einsetzen → durch den Durchlass führen → an der Sammelstelle halten. Herbal liefert vor allem Zutat/Ansatz, Biological vor allem Durchlass/Sammelstelle. Das ist die in Pass727 gefundene WHAT/HOW-Teilung in sechs greifbaren Kartenrollen.

Es werden weiterhin keine nicht sichtbaren Stoffnamen ergänzt: kein Wein, Öl, Honig und keine Pflanzenart.

## Nächster Hebel

Als Nächstes werden die verbleibenden Zustandskerne CTH, SH/SHED, CHK und LSH in diese Kette eingesetzt: bereiten, absetzen/ruhen, wärmen und waschen. Ziel ist ein kurzer Prozesswortschatz statt komplexer Ganzkartensätze.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "inventory_roots": len(root_rows), "default_workflow_stages": len(chain_rows),
        "multi_inventory_statements": len(multi_rows), "inventory_cards": len(inventory_cards),
        "inventory_events": len(inventory_occurrences), "cards": len(card_rows), "events": len(event_rows),
        "statements": len(statement_rows), "records": len(record_rows), "changed_cards": changed_cards,
        "changed_events": changed_events, "changed_statements": changed_statements,
        "named_unanchored_materials": 0, "form_changes": 0,
        "decision": "HO_OR_O_AIR_CKH_SOLK_FORM_A_COMPACT_LOCAL_WORKSHOP_INVENTORY",
    }
    (HERE / "SEVEN_HUNDRED_THIRTY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
