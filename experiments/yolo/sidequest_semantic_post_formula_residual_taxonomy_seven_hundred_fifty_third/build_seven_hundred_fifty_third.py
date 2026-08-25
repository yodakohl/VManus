#!/usr/bin/env python3
"""Build Pass 753: classify the 19 post-formula residual statements."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P752 = ROOT / "experiments/yolo/sidequest_semantic_continuation_bridge_formula_seven_hundred_fifty_second"


CLASSES = {
    "MINIMAL_SINGLE_CHANGE": {"H3-S004", "H5-S002", "B1-S015", "B2-S004", "B2-S005", "B2-S016", "B3-S011"},
    "SEGMENTATION_OR_REDISTRIBUTION": {"B1-S006", "B4-S002"},
    "SMALL_PHRASE_REORDER": {"H4-S001", "H5-S003", "B3-S032"},
    "LARGE_LEARNED_FORMULA": {"H1-S001", "H2-S001", "H3-S001", "H5-S001", "B1-S002", "B3-S021", "B6-S001"},
}

REPAIR_LABELS = {
    "H3-S004": "append active-item card after CTH+Y",
    "H5-S002": "pack HO with Y after resume",
    "B1-S015": "use attested T+E+Y order",
    "B2-S004": "pack L with CKH+Y",
    "B2-S005": "repeat OK+AIIN once",
    "B2-S016": "pack OK with AIIN",
    "B3-S011": "pack AR with active Y",
    "B1-S006": "split L+CKH+Y into CKH+Y then L",
    "B4-S002": "move OL and copied Y across two neighboring cards",
    "H4-S001": "repack measure, activation and two portion cards",
    "H5-S003": "swap SH/HO and double OK inside final card",
    "B3-S032": "repack AIN under CHD and redistribute OT/grade/close",
    "H1-S001": "insert whole OS card and learned OT action phrase",
    "H2-S001": "expand preparation/measure/current-item formula",
    "H3-S001": "replace opening and terminal fallbacks with learned wet-process cards",
    "H5-S001": "repeat HO owner/material slots across long Herbal clause",
    "B1-S002": "large continuation/address formula with repeated AL/OL/AIIN",
    "B3-S021": "large target/current-item expansion around SHED and close",
    "B6-S001": "large grade/current-item/continuation expansion",
}


def read() -> list[dict[str, str]]:
    path = P752 / "SEVEN_HUNDRED_FIFTY_SECOND_19_RESIDUAL_ERRORS.tsv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def components(sequence: str) -> list[str]:
    return [
        component
        for card in sequence.split(" | ")
        for component in card.replace("UNPACKED(", "").replace(")", "").split("+")
    ]


def edit_distance(left: list[str], right: list[str]) -> int:
    previous = list(range(len(right) + 1))
    for row_no, left_item in enumerate(left, start=1):
        current = [row_no]
        for column, right_item in enumerate(right, start=1):
            current.append(min(current[-1] + 1, previous[column] + 1, previous[column - 1] + (left_item != right_item)))
        previous = current
    return previous[-1]


def main() -> None:
    source = read()
    class_for = {statement: group for group, statements in CLASSES.items() for statement in statements}
    assert set(class_for) == {row["statement_id"] for row in source}
    rows = []
    for row in source:
        predicted = row["continuation_bridge_recipe_sequence"].split(" | ")
        observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
        predicted_components = Counter(components(row["continuation_bridge_recipe_sequence"]))
        observed_components = Counter(components(row["observed_recipe_sequence_after_reveal"]))
        missing = observed_components - predicted_components
        extra = predicted_components - observed_components
        group = class_for[row["statement_id"]]
        rows.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "residual_class": group,
            "predicted_cards": len(predicted),
            "observed_cards": len(observed),
            "card_edit_distance": edit_distance(predicted, observed),
            "missing_component_count": sum(missing.values()),
            "missing_components": "+".join(item for item, count in sorted(missing.items()) for _ in range(count)) or "NONE",
            "extra_component_count": sum(extra.values()),
            "extra_components": "+".join(item for item, count in sorted(extra.items()) for _ in range(count)) or "NONE",
            "smallest_repair": REPAIR_LABELS[row["statement_id"]],
            "next_priority": "NOW" if group == "MINIMAL_SINGLE_CHANGE" else ("AFTER_MINIMAL" if group == "SEGMENTATION_OR_REDISTRIBUTION" else "LATER"),
            "predicted_recipe_sequence": row["continuation_bridge_recipe_sequence"],
            "observed_recipe_sequence": row["observed_recipe_sequence_after_reveal"],
        })

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["residual_class"])].append(row)
    summary_rows = []
    descriptions = {
        "MINIMAL_SINGLE_CHANGE": "one insertion, one wrapper, one duplication or one within-card order choice",
        "SEGMENTATION_OR_REDISTRIBUTION": "same or nearly same components divided differently across adjacent cards",
        "SMALL_PHRASE_REORDER": "two or three coordinated packing changes",
        "LARGE_LEARNED_FORMULA": "long multi-card expression needing several repeated or whole-card values",
    }
    for group in CLASSES:
        items = grouped[group]
        summary_rows.append({
            "residual_class": group,
            "statements": len(items),
            "statement_ids": ",".join(str(row["statement_id"]) for row in items),
            "mean_card_edit_distance": f"{sum(int(row['card_edit_distance']) for row in items) / len(items):.3f}",
            "missing_components": sum(int(row["missing_component_count"]) for row in items),
            "extra_components": sum(int(row["extra_component_count"]) for row in items),
            "description": descriptions[group],
            "action": "implement exact context rules next" if group == "MINIMAL_SINGLE_CHANGE" else "retain for later pass",
        })

    write("SEVEN_HUNDRED_FIFTY_THIRD_19_RESIDUAL_TAXONOMY.tsv", rows)
    write("SEVEN_HUNDRED_FIFTY_THIRD_4_CLASS_SUMMARY.tsv", summary_rows)
    write("SEVEN_HUNDRED_FIFTY_THIRD_7_MINIMAL_NEXT_CASES.tsv", [row for row in rows if row["residual_class"] == "MINIMAL_SINGLE_CHANGE"])

    report = """# Pass 753 — Restklassifikation nach der Phrasenschicht

Nach Y-Valenz und den vier Phrasenfamilien bleiben19 von116 Aussagen. Sie teilen sich sauber in vier Arbeitsarten.

## Sieben minimale Einzelschritte

Sieben Aussagen brauchen genau eine lokale Änderung: Y anhängen, HO/AR/CKH/AIIN mit ihrem Nachbarn packen, eine Karte duplizieren oder die bereits attestierte Reihenfolge T+E+Y wählen. Ihre Karten-Editdistanz ist jeweils1. Das ist der nächste direkte Hebel.

## Zwei Segmentierungen

B1-S006 besitzt bereits dieselben Komponenten, teilt `L+CKH+Y` aber als `CKH+Y | L`. B4-S002 verschiebt OL und den aktiven Y-Slot zwischen zwei Nachbarkarten. Das sind keine neuen Bedeutungen.

## Drei kleine Phrasenreihenfolgen

H4-S001,H5-S003 und B3-S032 brauchen je zwei bis drei koordinierte Packentscheidungen. Sie bleiben nach dem Minimalpass gut angreifbar.

## Sieben grosse gelernte Formeln

H1-S001,H2-S001,H3-S001,H5-S001,B1-S002,B3-S021 und B6-S001 sind die eigentliche Nomenklatorschicht. Jede verlangt mehrere Wiederholungen, Ganzkarten oder Umordnungen. Sie sollen nicht in falsche Einzelstämme zerlegt werden.

Als naechstes werden exakt die sieben Einzelschritt-Faelle mit vollständiger Kartenumgebung umgesetzt.
"""
    (HERE / "SEVEN_HUNDRED_FIFTY_THIRD_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "residual_statements": len(rows),
        "classes": len(summary_rows),
        "minimal_single_change": len(grouped["MINIMAL_SINGLE_CHANGE"]),
        "segmentation_or_redistribution": len(grouped["SEGMENTATION_OR_REDISTRIBUTION"]),
        "small_phrase_reorder": len(grouped["SMALL_PHRASE_REORDER"]),
        "large_learned_formula": len(grouped["LARGE_LEARNED_FORMULA"]),
        "semantic_changes": 0,
        "deck_changes": 0,
        "decision": "SEVEN_MINIMAL_SINGLE_CHANGES_NEXT__TWO_SEGMENTATIONS__THREE_SMALL_REORDERS__SEVEN_LARGE_FORMULAS",
    }
    (HERE / "SEVEN_HUNDRED_FIFTY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
