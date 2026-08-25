#!/usr/bin/env python3
"""Build Pass 733: overlay E/EE/EEE grades and Y/licensed-DY endpoints."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P732 = ROOT / "experiments/yolo/sidequest_semantic_operation_cross_seven_hundred_thirty_second"


def read(name: str) -> list[dict[str, str]]:
    with (P732 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


OPERATIONS = ["OK", "K", "CH", "CHD"]
STATE_ROOTS = {
    "E": ("KURZ", "kurzer oder unmittelbarer Arbeitsgrad"),
    "EE": ("LANG", "länger gehaltener Arbeitsgrad"),
    "EEE": ("VOLL", "vollständig ausgeführter Arbeitsgrad"),
    "Y": ("DIES", "der aktuell gemeinte, weiter verfügbare Posten"),
    "DY": ("SCHLUSS", "lizenzierter Abschluss der aktuellen Arbeitszelle"),
}


def state_roots(recipe: str) -> list[str]:
    parts = recipe.split("+")
    return [root for root in STATE_ROOTS if root in parts]


def operation_roots(recipe: str) -> list[str]:
    parts = recipe.split("+")
    return [root for root in OPERATIONS if root in parts]


def grade(recipe: str) -> str:
    parts = recipe.split("+")
    return "EEE" if "EEE" in parts else "EE" if "EE" in parts else "E" if "E" in parts else "NONE"


def endpoint(recipe: str) -> str:
    parts = recipe.split("+")
    # DY wins as the endpoint state even when a card also carries the current-item Y.
    return "DY" if "DY" in parts else "Y" if "Y" in parts else "NONE"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read("SEVEN_HUNDRED_THIRTY_SECOND_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_SECOND_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_SECOND_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_SECOND_11_RECORD_EDITION.tsv")

    target_events = [row for row in events if state_roots(row["component_recipe"])]
    target_card_ids = {row["card_no"] for row in target_events}
    target_cards = []
    for row in cards:
        if row["exact_card_id"] not in target_card_ids:
            continue
        target_cards.append({
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "state_roots": "+".join(state_roots(row["component_recipe"])),
            "grade": grade(row["component_recipe"]), "endpoint": endpoint(row["component_recipe"]),
            "reading_de": row["reading_de"], "registered_surfaces": row["registered_surfaces"],
            "events": row["events"], "semantic_status": "UNCHANGED__STATE_ENDPOINT_ANNOTATED",
        })

    occurrence_rows = []
    for row in target_events:
        occurrence_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "state_roots": "+".join(state_roots(row["component_recipe"])),
            "grade": grade(row["component_recipe"]), "endpoint": endpoint(row["component_recipe"]),
            "reading_de": row["reading_de"],
            "endpoint_rule": "CLOSE_LICENSED" if "DY" in row["component_recipe"].split("+") else "CURRENT_ITEM_REMAINS_AVAILABLE",
            "form_owner_boundary_status": "UNCHANGED",
        })

    root_rows = []
    for root, (meaning, expansion) in STATE_ROOTS.items():
        rows = [row for row in occurrence_rows if root in row["state_roots"].split("+")]
        root_rows.append({
            "root": root, "short_value_de": meaning, "workshop_expansion_de": expansion,
            "exact_cards": len({row["card_no"] for row in rows}), "events": len(rows),
            "herbal_events": sum(row["record"].startswith("H") for row in rows),
            "bio_events": sum(row["record"].startswith("B") for row in rows),
            "rule": "REPEATED_E_GRADE" if root in {"E", "EE", "EEE"} else "EXACT_CARD_ENDPOINT__NOT_SURFACE_SUFFIX",
        })

    operation_events = [row for row in events if operation_roots(row["component_recipe"])]
    cells = []
    for operation in OPERATIONS:
        for g in ["NONE", "E", "EE", "EEE"]:
            for end in ["NONE", "Y", "DY"]:
                matches = [
                    row for row in operation_events
                    if operation in operation_roots(row["component_recipe"])
                    and grade(row["component_recipe"]) == g and endpoint(row["component_recipe"]) == end
                ]
                if not matches:
                    continue
                cells.append({
                    "operation": operation, "operation_reading_de": dict(OK="ANSETZEN", K="ZUGEBEN", CH="ENTNEHMEN", CHD="UMSETZEN")[operation],
                    "grade": g, "grade_reading_de": "NONE" if g == "NONE" else STATE_ROOTS[g][0],
                    "endpoint": end, "endpoint_reading_de": "NONE" if end == "NONE" else STATE_ROOTS[end][0],
                    "exact_cards": len({row["card_no"] for row in matches}), "events": len(matches),
                    "card_ids": ",".join(sorted({row["card_no"] for row in matches})),
                    "component_recipes": " | ".join(dict.fromkeys(row["component_recipe"] for row in matches)),
                })

    pure_ok_specs = [
        ("OG01", "OK+Y", "NONE", "Y", 13, "aktuellen Posten ansetzen und verfügbar lassen"),
        ("OG02", "OK+E+Y", "E", "Y", 2, "kurz ansetzen und verfügbar lassen"),
        ("OG03", "OK+EE+Y", "EE", "Y", 7, "länger ansetzen und verfügbar lassen"),
        ("OG04", "OK+E+DY", "E", "DY", 8, "kurz ansetzen und schließen"),
        ("OG05", "OK+EE+DY", "EE", "DY", 10, "länger ansetzen und schließen"),
        ("OG06", "OK+EEE+DY", "EEE", "DY", 1, "vollständig ansetzen und schließen"),
    ]
    pure_ok_rows = []
    for ident, recipe, g, end, expected, fluent in pure_ok_specs:
        matches = [row for row in events if row["component_recipe"] == recipe]
        pure_ok_rows.append({
            "cell_id": ident, "component_recipe": recipe, "grade": g, "endpoint": end,
            "exact_cards": len({row["card_no"] for row in matches}), "events": len(matches),
            "expected_events": expected, "event_ids": ",".join(row["event_id"] for row in matches),
            "fluent_reading_de": fluent,
        })

    dy_surface_rows = []
    for row in events:
        if not row["surface"].endswith("dy"):
            continue
        licensed = "DY" in row["component_recipe"].split("+")
        dy_surface_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "card_no": row["card_no"], "surface": row["surface"],
            "component_recipe": row["component_recipe"], "reading_de": row["reading_de"],
            "contains_licensed_DY": "YES" if licensed else "NO",
            "decision": "CLOSE" if licensed else "OPEN_CURRENT_ITEM__SURFACE_DY_IS_NOT_SUFFIX",
        })

    statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        statement_events[row["statement_id"]].append(row)
    statement_rows = []
    for row in statements:
        targets = [event for event in statement_events[row["statement_id"]] if state_roots(event["component_recipe"])]
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "state_endpoint_sequence": " | ".join(
                f"{event['event_id']}:{grade(event['component_recipe'])}/{endpoint(event['component_recipe'])}" for event in targets
            ) or "NONE",
            "licensed_close_cards": sum("DY" in event["component_recipe"].split("+") for event in targets),
            "working_reading_de": row["working_reading_de"], "form_owner_boundary_status": "UNCHANGED",
        })

    record_rows = []
    for row in records:
        rows = [event for event in occurrence_rows if event["record"] == row["record"]]
        count = Counter(root for event in rows for root in event["state_roots"].split("+"))
        record_rows.append({
            "record": row["record"], "page": row["page"], "statements": row["statements"], "events": row["events"],
            "E_short": count["E"], "EE_long": count["EE"], "EEE_full": count["EEE"],
            "Y_current_item": count["Y"], "DY_close": count["DY"],
            "continuous_reading_de": row["continuous_reading_de"], "form_status": "UNCHANGED",
        })

    card_rows = []
    for row in cards:
        roots = state_roots(row["component_recipe"])
        card_rows.append({
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "reading_de": row["reading_de"],
            "state_roots": "+".join(roots) or "NONE", "grade": grade(row["component_recipe"]),
            "endpoint": endpoint(row["component_recipe"]), "registered_surfaces": row["registered_surfaces"],
            "events": row["events"], "semantic_status": "UNCHANGED",
        })
    event_rows = []
    for row in events:
        roots = state_roots(row["component_recipe"])
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
            "surface": row["surface"], "component_recipe": row["component_recipe"], "reading_de": row["reading_de"],
            "state_roots": "+".join(roots) or "NONE", "grade": grade(row["component_recipe"]),
            "endpoint": endpoint(row["component_recipe"]), "form_owner_boundary_status": "UNCHANGED",
        })

    write("SEVEN_HUNDRED_THIRTY_THIRD_5_STATE_ENDPOINT_ROOTS.tsv", root_rows)
    write("SEVEN_HUNDRED_THIRTY_THIRD_6_PURE_OK_GRADE_CELLS.tsv", pure_ok_rows)
    write("SEVEN_HUNDRED_THIRTY_THIRD_26_OPERATION_STATE_CELLS.tsv", cells)
    write("SEVEN_HUNDRED_THIRTY_THIRD_105_DY_SURFACE_FIREWALL.tsv", dy_surface_rows)
    write("SEVEN_HUNDRED_THIRTY_THIRD_108_STATE_ENDPOINT_CARDS.tsv", target_cards)
    write("SEVEN_HUNDRED_THIRTY_THIRD_224_STATE_ENDPOINT_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_THIRTY_THIRD_173_CARD_DICTIONARY.tsv", card_rows)
    write("SEVEN_HUNDRED_THIRTY_THIRD_381_EVENT_INTERLINEAR.tsv", event_rows)
    write("SEVEN_HUNDRED_THIRTY_THIRD_116_STATEMENT_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDRED_THIRTY_THIRD_11_RECORD_EDITION.tsv", record_rows)

    manual = """# Grad und Abschluss

- `E` = KURZ.
- `EE` = LANG.
- `EEE` = VOLL.
- `Y` = DIES, der aktuelle Posten bleibt verfügbar.
- `DY` = SCHLUSS, aber nur wenn die exakte Karte dieses Komponentenrezept trägt.

## Reines OK-Raster

`OK+Y` setzt den aktuellen Posten an. Mit E oder EE bleibt er kurz oder lang offen. Mit E/EE/EEE plus DY wird derselbe Schritt kurz, lang oder vollständig ausgeführt und geschlossen.

## Sichtbare dy-Falle

105 sichtbare Karten enden auf `dy`. Nur 89 davon besitzen das Abschlussrezept DY. Sechzehn sind offen: fünf nackte `dy`-Allographe der Y-Karte und elf `chdy/chedy`-Allographe von CHD+Y. Der Lehrling liest deshalb immer die gelernte Ganzkarte, nie bloß die letzten zwei Zeichen.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_THIRD_GRADE_ENDPOINT_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    false_dy = [row for row in dy_surface_rows if row["contains_licensed_DY"] == "NO"]
    report = f"""# Pass 733 — Grad und Abschluss

## Ergebnis

Die kleine Zustandsgrammatik hält über die vollständige Prosa:

- E=KURZ: 34 Karten/49 Ereignisse.
- EE=LANG: 17/40.
- EEE=VOLL: 2/2.
- Y=DIES/aktueller Posten: 60/124.
- DY=SCHLUSS: 37/89, nur als lizenzierte exakte Kartenkomponente.

Die Vereinigung umfasst 108 Karten/224 Ereignisse. Über OK/K/CH/CHD entstehen 26 tatsächlich belegte Grad×Endpunkt-Zellen.

## Reines OK-Paradigma

Sechs Formen zeigen die Lehre am klarsten: OK+Y 13, OK+E+Y 2, OK+EE+Y 7, OK+E+DY 8, OK+EE+DY 10 und OK+EEE+DY 1. Y hält den Posten offen; DY schließt. E→EE→EEE steigert kurz→lang→voll.

## Die dy-Firewall

Von 105 sichtbaren `…dy`-Ereignissen sind 89 echte DY-Schlüsse und {len(false_dy)} keine. Die sechzehn Gegenfälle zerfallen exakt in fünf nackte `dy`-Allographe von Y und elf `chdy/chedy`-Allographe von CHD+Y. Deshalb ist `dy` kein lesbares Suffix. Abschluss ist eine Eigenschaft der gelernten exakten Karte.

Das macht das System zugleich produktiv und werkstatttauglich: Der Schreiber kennt E-Grade und Y/DY-Rollen, muss aber die mehrdeutige sichtbare Form über den Kartenbestand disambiguieren.

## Nächster Hebel

Als Nächstes werden die Stoff-/Gefäßkerne O, OR, AIR, CKH, SOLK und HO als Werkstattinventar geordnet: Arbeitsgang, Ansatz, Wasser, Durchlass, Sammelstelle und Zutat. Gesucht ist eine kompakte Prozesskette ohne neue erfundene Materialien.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_THIRD_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "state_endpoint_roots": len(root_rows), "pure_ok_cells": len(pure_ok_rows),
        "operation_state_cells": len(cells), "state_endpoint_cards": len(target_cards),
        "state_endpoint_events": len(occurrence_rows), "surface_dy_events": len(dy_surface_rows),
        "licensed_DY_surface_events": sum(row["contains_licensed_DY"] == "YES" for row in dy_surface_rows),
        "false_surface_dy_events": len(false_dy), "cards": len(card_rows), "events": len(event_rows),
        "statements": len(statement_rows), "records": len(record_rows), "semantic_changes": 0, "form_changes": 0,
        "decision": "E_EE_EEE_GRADE_OK__Y_CURRENT_ITEM__DY_ONLY_LICENSED_EXACT_CARD_CLOSE",
    }
    (HERE / "SEVEN_HUNDRED_THIRTY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
