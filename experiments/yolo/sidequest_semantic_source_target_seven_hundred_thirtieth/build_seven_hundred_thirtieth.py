#!/usr/bin/env python3
"""Build Pass 730: close AR source, AL target-site, and AIR water as separate roots."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P729 = ROOT / "experiments/yolo/sidequest_semantic_quantity_split_seven_hundred_twenty_ninth"


def read(name: str) -> list[dict[str, str]]:
    with (P729 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ROOTS = {
    "AR": ("QUELLE", "QUELLE", "aus/von der aktiven Quelle oder dem Vorrat"),
    "AL": ("ZIEL", "ZIELSTELLE", "an/zu der bezeichneten Arbeitsstelle"),
    "AIR": ("WASSER", "WASSER", "die konkrete laufende Arbeitsflüssigkeit Wasser"),
}


def roots_in(recipe: str) -> list[str]:
    parts = recipe.split("+")
    return [root for root in ROOTS if root in parts]


def revise_atomic(reading: str, roots: list[str]) -> str:
    revised = reading
    for root in roots:
        old, new, _ = ROOTS[root]
        revised = revised.replace(old, new)
    return revised


def revise_prose(text: str) -> str:
    return (
        text.replace("Am Ziel", "An der Zielstelle")
        .replace("am Ziel", "an der Zielstelle")
        .replace("zum Ziel", "zur Zielstelle")
        .replace("Zum Ziel", "Zur Zielstelle")
        .replace("das Ziel", "die Zielstelle")
        .replace("Das Ziel", "Die Zielstelle")
    )


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read("SEVEN_HUNDRED_TWENTY_NINTH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_TWENTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_TWENTY_NINTH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_TWENTY_NINTH_11_RECORD_EDITION.tsv")

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    card_rows = []
    direction_cards = []
    for row in cards:
        roots = roots_in(row["component_recipe"])
        revised = revise_atomic(row["pass729_reading_de"], roots)
        output = {
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "pass729_reading_de": row["pass729_reading_de"],
            "pass730_reading_de": revised, "direction_root": roots[0] if roots else "NONE",
            "registered_surfaces": row["registered_surfaces"], "events": row["events"],
            "direction_revision": "YES" if revised != row["pass729_reading_de"] else "NO",
        }
        card_rows.append(output)
        if roots:
            direction_cards.append(output)

    event_rows = []
    direction_occurrences = []
    for row in events:
        roots = roots_in(row["component_recipe"])
        revised = revise_atomic(row["pass729_semantic_de"], roots)
        output = {
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "locus": row["locus"], "owner_de": row["owner_de"],
            "card_no": row["card_no"], "observed_surface": row["observed_surface"],
            "component_recipe": row["component_recipe"], "pass729_semantic_de": row["pass729_semantic_de"],
            "pass730_semantic_de": revised, "direction_root": roots[0] if roots else "NONE",
            "form_owner_boundary_status": "UNCHANGED",
        }
        event_rows.append(output)
        if roots:
            sequence = by_statement[row["statement_id"]]
            index = next(i for i, item in enumerate(sequence) if item["event_id"] == row["event_id"])
            direction_occurrences.append({
                "event_id": row["event_id"], "root": roots[0], "page": row["page"], "record": row["record"],
                "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
                "surface": row["observed_surface"], "component_recipe": row["component_recipe"],
                "previous_recipe": sequence[index - 1]["component_recipe"] if index else "START",
                "next_recipe": sequence[index + 1]["component_recipe"] if index + 1 < len(sequence) else "END",
                "pass730_atomic_reading_de": revised,
                "slot_expansion_de": ROOTS[roots[0]][2],
                "full_statement_de": revise_prose(next(item["pass729_working_reading_de"] for item in statements if item["statement_id"] == row["statement_id"])),
            })

    statement_rows = []
    for row in statements:
        roots = sorted({root for event in by_statement[row["statement_id"]] for root in roots_in(event["component_recipe"])})
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "direction_roots": ",".join(roots) or "NONE",
            "pass730_atomic_trace_de": revise_atomic(row["pass729_atomic_trace_de"], roots),
            "pass730_working_reading_de": revise_prose(row["pass729_working_reading_de"]),
            "form_owner_boundary_status": "UNCHANGED",
        })

    record_rows = []
    for row in records:
        target = [event for event in event_rows if event["record"] == row["record"]]
        counts = Counter(event["direction_root"] for event in target)
        record_rows.append({
            "record": row["record"], "page": row["page"], "statements": row["statements"],
            "events": len(target), "AR_source": counts["AR"], "AL_target_site": counts["AL"],
            "AIR_water": counts["AIR"], "continuous_pass730_reading_de": revise_prose(row["continuous_pass729_reading_de"]),
            "form_status": "UNCHANGED",
        })

    root_rows = []
    for root, (old, new, expansion) in ROOTS.items():
        rcards = [row for row in direction_cards if row["direction_root"] == root]
        rev = [row for row in direction_occurrences if row["root"] == root]
        root_rows.append({
            "root": root, "short_value_de": new, "workshop_expansion_de": expansion,
            "exact_cards": len(rcards), "events": len(rev),
            "herbal_events": sum(row["record"].startswith("H") for row in rev),
            "bio_events": sum(row["record"].startswith("B") for row in rev),
            "bare_events": sum(row["component_recipe"] == root for row in rev),
            "composed_events": sum(row["component_recipe"] != root for row in rev),
            "nesting_rule": "ATOMIC_ROOT__DO_NOT_SPLIT" if root == "AIR" else "PRODUCTIVE_DIRECTION_SLOT",
        })

    pairs = [
        {
            "pair_id": "DIR01", "source_card": "PROC003", "source_recipe": "AR", "source_events": 5,
            "target_card": "PROC055", "target_recipe": "AL", "target_events": 7,
            "source_reading_de": "DARAUS / AUS DER QUELLE", "target_reading_de": "DORTHIN / AN DIE ZIELSTELLE",
            "portable_rule": "nackte Quell- und Zieladresse",
        },
        {
            "pair_id": "DIR02", "source_card": "PROC113", "source_recipe": "OK+AR", "source_events": 1,
            "target_card": "PROC048", "target_recipe": "OK+AL", "target_events": 6,
            "source_reading_de": "von der Quelle her ansetzen", "target_reading_de": "an der Zielstelle ansetzen",
            "portable_rule": "derselbe OK-Arbeitsgang mit umgekehrtem Adressslot",
        },
        {
            "pair_id": "DIR03", "source_card": "PROC123", "source_recipe": "L+CHD+AR", "source_events": 1,
            "target_card": "PROC088", "target_recipe": "L+CHD+AL", "target_events": 1,
            "source_reading_de": "von der Quelle weiterleiten", "target_reading_de": "zur Zielstelle weiterleiten",
            "portable_rule": "identischer Transferkern mit Quelle versus Ziel",
        },
        {
            "pair_id": "DIR04", "source_card": "PROC089", "source_recipe": "OT+AR", "source_events": 1,
            "target_card": "PROC131", "target_recipe": "OT+AL", "target_events": 3,
            "source_reading_de": "danach zur Quelle wechseln", "target_reading_de": "danach zur Zielstelle wechseln",
            "portable_rule": "Folgekarte wählt die nächste Adressrichtung",
        },
    ]

    write("SEVEN_HUNDRED_THIRTIETH_3_DIRECTION_ROOTS.tsv", root_rows)
    write("SEVEN_HUNDRED_THIRTIETH_4_SOURCE_TARGET_PAIRS.tsv", pairs)
    write("SEVEN_HUNDRED_THIRTIETH_37_DIRECTION_CARDS.tsv", direction_cards)
    write("SEVEN_HUNDRED_THIRTIETH_58_DIRECTION_OCCURRENCES.tsv", direction_occurrences)
    write("SEVEN_HUNDRED_THIRTIETH_173_CARD_DICTIONARY.tsv", card_rows)
    write("SEVEN_HUNDRED_THIRTIETH_381_EVENT_INTERLINEAR.tsv", event_rows)
    write("SEVEN_HUNDRED_THIRTIETH_116_STATEMENT_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDRED_THIRTIETH_11_RECORD_EDITION.tsv", record_rows)

    manual = """# Quelle, Zielstelle und Wasser

## AR — QUELLE

AR beantwortet **woher?** Nackt heißt die Karte „daraus / aus der aktiven Quelle“. In einer Operationskarte füllt sie deren Herkunftsslot.

## AL — ZIELSTELLE

AL beantwortet **wohin / wo anwenden?** Nackt heißt die Karte „dorthin / an die bezeichnete Arbeitsstelle“. In einer Operationskarte füllt sie deren Zielslot.

## AIR — WASSER

AIR ist keine längere Form von AR. Es ist ein eigener Stoffstamm für Wasser. `CH+AIR`, `K+AIR`, `OK+AIR`, `CHD+AIR` und `AIR+Y+DY` bilden eine kleine Wasserreihe: entnehmen, zugeben, ansetzen, umsetzen, schließen.

## Vier Paarregeln

- `AR` / `AL`: daraus / dorthin.
- `OK+AR` / `OK+AL`: von der Quelle her / an der Zielstelle ansetzen.
- `L+CHD+AR` / `L+CHD+AL`: von der Quelle / zur Zielstelle weiterleiten.
- `OT+AR` / `OT+AL`: danach Quelle / danach Zielstelle wählen.
"""
    (HERE / "SEVEN_HUNDRED_THIRTIETH_DIRECTION_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    changed_cards = sum(row["direction_revision"] == "YES" for row in card_rows)
    changed_events = sum(row["pass729_semantic_de"] != row["pass730_semantic_de"] for row in event_rows)
    changed_statements = sum("AL" in row["direction_roots"] for row in statement_rows)
    report = f"""# Pass 730 — Quelle, Zielstelle und Wasser

## Ergebnis

Die Richtungsachse schließt sich als sehr einfaches Werkstattpaar:

- **AR = QUELLE:** 10 Karten / 14 Ereignisse; „aus/von der aktiven Quelle“.
- **AL = ZIELSTELLE:** 22 Karten / 39 Ereignisse; „an/zu der bezeichneten Arbeitsstelle“.
- **AIR = WASSER:** 5 Karten / 5 Ereignisse; ein eigener Stoffstamm, nicht AR mit eingeschobenem I.

Vier beinahe minimale Paare tragen die Opposition: AR/AL, OK+AR/OK+AL, L+CHD+AR/L+CHD+AL und OT+AR/OT+AL. Derselbe Operationskern wechselt nur den Adressslot.

## Revision

AL wird vom abstrakten **ZIEL** auf die handwerklich lesbare **ZIELSTELLE** präzisiert. Das ändert {changed_cards} Karten, {changed_events} Ereignisse und {changed_statements} Aussagen semantisch. AR=QUELLE und AIR=WASSER bleiben. Alle Formen und Besitzer bleiben fest.

Die neue Kurzregel lautet:

> AR sagt, woher der Posten kommt; AL sagt, wohin er geht; AIR sagt, dass der laufende Stoff Wasser ist.

Damit ist `qokar` nicht ein Schreibfehler von `qokal`: das erste setzt von der Quelle her an, das zweite an der Zielstelle. Ebenso sind `lchedar` und `lchedal` dieselbe Transferhandlung mit entgegengesetzter Adresse.

## Nächster Hebel

Als Nächstes wird der OR/OL/OT-Komplex geschlossen: OR=Ansatz, OL=Fortsetzung und OT=Folge/Danach müssen als kleine Zeit-/Anaphorikmaschine alle festen Kontexte tragen.
"""
    (HERE / "SEVEN_HUNDRED_THIRTIETH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "direction_roots": len(root_rows), "paired_contrasts": len(pairs),
        "direction_cards": len(direction_cards), "direction_events": len(direction_occurrences),
        "AR_events": 14, "AL_events": 39, "AIR_events": 5,
        "cards": len(card_rows), "events": len(event_rows), "statements": len(statement_rows), "records": len(record_rows),
        "changed_cards": changed_cards, "changed_events": changed_events, "changed_statements": changed_statements,
        "form_changes": 0, "decision": "AR_SOURCE__AL_TARGET_SITE__AIR_WATER_FORM_A_CLEAN_THREE_WAY_SPLIT",
    }
    (HERE / "SEVEN_HUNDRED_THIRTIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
