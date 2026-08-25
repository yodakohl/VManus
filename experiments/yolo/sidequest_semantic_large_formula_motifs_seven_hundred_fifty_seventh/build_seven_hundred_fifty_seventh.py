#!/usr/bin/env python3
"""Build Pass 757: shared motifs inside the seven large learned formulas."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P756 = ROOT / "experiments/yolo/sidequest_semantic_small_phrase_reorder_seven_hundred_fifty_sixth"
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"


FAMILY_FOR = {
    "H1-S001": "HERBAL_OWNER_MATERIAL_ECHO",
    "H2-S001": "HERBAL_OWNER_MATERIAL_ECHO",
    "H5-S001": "HERBAL_OWNER_MATERIAL_ECHO",
    "H3-S001": "HERBAL_WET_PROCESS_CADENCE",
    "B1-S002": "BIO_ADDRESS_CONTINUATION_ECHO",
    "B3-S021": "BIO_ADDRESS_CONTINUATION_ECHO",
    "B6-S001": "BIO_ADDRESS_CONTINUATION_ECHO",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def flatten(sequence: str) -> list[str]:
    return [component for card in sequence.split(" | ") for component in card.replace("UNPACKED(", "").replace(")", "").split("+")]


def main() -> None:
    residual = read(P756 / "SEVEN_HUNDRED_FIFTY_SIXTH_7_LARGE_FORMULA_RESIDUALS.tsv")
    clean = {row["statement_id"]: row for row in read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv")}
    component_values = {
        row["component"]: row["short_value_de"]
        for row in read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_39_COMPONENT_DICTIONARY.tsv")
    }
    assert set(FAMILY_FOR) == {row["statement_id"] for row in residual}

    card_statements: dict[str, set[str]] = defaultdict(set)
    card_occurrences: Counter[str] = Counter()
    component_statements: dict[str, set[str]] = defaultdict(set)
    component_occurrences: Counter[str] = Counter()
    for row in residual:
        statement_id = row["statement_id"]
        for card in row["observed_recipe_sequence_after_reveal"].split(" | "):
            card_statements[card].add(statement_id)
            card_occurrences[card] += 1
            for component in card.split("+"):
                component_statements[component].add(statement_id)
                component_occurrences[component] += 1
    shared_cards = {card for card, statements in card_statements.items() if len(statements) >= 2}

    formula_rows = []
    aggregate_missing: Counter[str] = Counter()
    aggregate_extra: Counter[str] = Counter()
    for row in residual:
        statement_id = row["statement_id"]
        predicted = row["small_phrase_recipe_sequence"].split(" | ")
        observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
        predicted_components = Counter(flatten(row["small_phrase_recipe_sequence"]))
        observed_components = Counter(flatten(row["observed_recipe_sequence_after_reveal"]))
        missing = observed_components - predicted_components
        extra = predicted_components - observed_components
        aggregate_missing.update(missing)
        aggregate_extra.update(extra)
        shared_positions = sum(card in shared_cards for card in observed)
        formula_rows.append({
            "statement_id": statement_id,
            "page": row["page"],
            "record": row["record"],
            "formula_family": FAMILY_FOR[statement_id],
            "owner_noun_de": clean[statement_id]["owner_noun_de"],
            "clean_workshop_reading_de": clean[statement_id]["clean_workshop_reading_de"],
            "predicted_cards": len(predicted),
            "observed_cards": len(observed),
            "shared_card_positions": shared_positions,
            "formula_local_card_positions": len(observed) - shared_positions,
            "missing_components": "+".join(item for item, count in sorted(missing.items()) for _ in range(count)) or "NONE",
            "extra_components": "+".join(item for item, count in sorted(extra.items()) for _ in range(count)) or "NONE",
            "observed_recipe_sequence": row["observed_recipe_sequence_after_reveal"],
            "motif_rendered_sequence": " | ".join(f"<{card}>" if card in shared_cards else card for card in observed),
        })

    shared_rows = []
    for number, card in enumerate(sorted(shared_cards, key=lambda item: (-len(card_statements[item]), -card_occurrences[item], item)), start=1):
        shared_rows.append({
            "motif_id": f"M{number:02d}",
            "card_recipe": card,
            "formula_statements": len(card_statements[card]),
            "formula_occurrences": card_occurrences[card],
            "statement_ids": ",".join(sorted(card_statements[card])),
            "atomic_reading_de": " · ".join(component_values[component] for component in card.split("+")),
            "teaching_role": "SHARED_EXACT_CARD_INSIDE_LARGE_FORMULA",
        })

    component_rows = []
    for component in sorted(component_statements, key=lambda item: (-len(component_statements[item]), -component_occurrences[item], item)):
        if len(component_statements[component]) < 2:
            continue
        component_rows.append({
            "component": component,
            "formula_statements": len(component_statements[component]),
            "formula_occurrences": component_occurrences[component],
            "statement_ids": ",".join(sorted(component_statements[component])),
            "status": "SHARED_COMPONENT_AXIS_NOT_A_NEW_MEANING",
        })

    family_rows = []
    descriptions = {
        "HERBAL_OWNER_MATERIAL_ECHO": "long plant-owner clause repeats material/preparation/current-item addresses",
        "HERBAL_WET_PROCESS_CADENCE": "memorized seven-card strain/hold/fill/close process cadence",
        "BIO_ADDRESS_CONTINUATION_ECHO": "station clause repeats target, continuation, measure and current-item cards",
    }
    for family in descriptions:
        rows = [row for row in formula_rows if row["formula_family"] == family]
        family_rows.append({
            "formula_family": family,
            "statements": len(rows),
            "statement_ids": ",".join(str(row["statement_id"]) for row in rows),
            "predicted_cards": sum(int(row["predicted_cards"]) for row in rows),
            "observed_cards": sum(int(row["observed_cards"]) for row in rows),
            "shared_card_positions": sum(int(row["shared_card_positions"]) for row in rows),
            "formula_local_card_positions": sum(int(row["formula_local_card_positions"]) for row in rows),
            "description": descriptions[family],
            "teaching_action": "learn one family shell plus exact exemplar sequence",
        })

    missing_rows = []
    for component in sorted(set(aggregate_missing) | set(aggregate_extra), key=lambda item: (-aggregate_missing[item], item)):
        missing_rows.append({
            "component": component,
            "missing_occurrences": aggregate_missing[component],
            "extra_occurrences": aggregate_extra[component],
            "net_missing": aggregate_missing[component] - aggregate_extra[component],
        })

    write("SEVEN_HUNDRED_FIFTY_SEVENTH_7_LARGE_FORMULAS.tsv", formula_rows)
    write("SEVEN_HUNDRED_FIFTY_SEVENTH_8_SHARED_CARD_MOTIFS.tsv", shared_rows)
    write("SEVEN_HUNDRED_FIFTY_SEVENTH_22_SHARED_COMPONENT_AXES.tsv", component_rows)
    write("SEVEN_HUNDRED_FIFTY_SEVENTH_3_FORMULA_FAMILIES.tsv", family_rows)
    write("SEVEN_HUNDRED_FIFTY_SEVENTH_14_COMPONENT_GAPS.tsv", missing_rows)

    report = """# Pass 757 — Motive der sieben grossen Formeln

Die sieben letzten Aussagen sind nicht sieben voellig fremde Saetze. Sie teilen einen deutlichen Adresskern.

## Gemeinsame Substanz

- Y und AIIN kommen in allen sieben Formeln vor.
- OL kommt in sechs, AL und OR in je fuenf vor.
- Acht exakte Karten (`AIIN`, `Y`, `AL`, `OL`, `CTH+Y`, `AR`, `OK+AIIN`, `OK+Y`) werden in mindestens zwei der sieben Formeln wiederverwendet.
- Diese acht Motive belegen31 von74 sichtbaren Kartenpositionen;43 Positionen bleiben formell lokal.

Die Restluecke besteht aus36 fehlenden Komponenten bei nur zwei ueberzaehligen Y. Am haeufigsten fehlen Y9, AL4, OL4 sowie T/O/HO je3. Das ist typisch fuer ausgelassene Besitzer-/Adresswiederholung, nicht fuer fehlende neue Stoffnamen.

## Drei Lehrfamilien

1. **Herbal owner/material echo**: H1-S001,H2-S001,H5-S001 wiederholen Pflanzenmaterial, Ansatz, Sollmass und aktuellen Posten innerhalb langer Artikelklauseln.
2. **Herbal wet-process cadence**: H3-S001 ist eine einzelne gelernte sieben-Karten-Folge fuer Halten, Auswringen, Fuellen und Schluss.
3. **Bio address/continuation echo**: B1-S002,B3-S021,B6-S001 wiederholen Zielstelle, WEITER, Sollmass und aktuellen Posten in Stationszellen.

Der Lehrling muss also keine sieben unverbundenen Saetze memorieren. Er lernt drei Schablonen, acht gemeinsame Kartenmotive und sieben konkrete Exemplarfolgen. Als naechstes wird genau dieses 3+8+7-Deck in den Packer eingebaut.
"""
    (HERE / "SEVEN_HUNDRED_FIFTY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "large_formulas": len(formula_rows),
        "formula_families": len(family_rows),
        "observed_formula_cards": sum(int(row["observed_cards"]) for row in formula_rows),
        "predicted_formula_cards": sum(int(row["predicted_cards"]) for row in formula_rows),
        "shared_card_motifs": len(shared_rows),
        "shared_card_positions": sum(int(row["shared_card_positions"]) for row in formula_rows),
        "formula_local_card_positions": sum(int(row["formula_local_card_positions"]) for row in formula_rows),
        "shared_component_axes": len(component_rows),
        "missing_components": sum(aggregate_missing.values()),
        "extra_components": sum(aggregate_extra.values()),
        "semantic_changes": 0,
        "deck_changes": 0,
        "decision": "SEVEN_LARGE_FORMULAS_SHARE_EIGHT_CARDS_AND_THREE_SHELLS__BUILD_3_PLUS_8_PLUS_7_TEACHING_DECK",
    }
    (HERE / "SEVEN_HUNDRED_FIFTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
