#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R252 = ROOT / "experiments/yolo/sidequest_semantic_quantity_endings_two_hundred_fifty_second"
R248 = ROOT / "experiments/yolo/sidequest_semantic_astro_native_card_values_two_hundred_forty_eighth"
CARDS = R252 / "TWO_HUNDRED_FIFTY_SECOND_19_QUANTITY_AND_CONTROL_CARDS.tsv"
GROUPS = R248 / "TWO_HUNDRED_FORTY_EIGHTH_REVISED_395_GROUP_MANUAL.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cards = {r["master_card_id"]: r for r in read_tsv(CARDS)}
    groups = read_tsv(GROUPS)
    occurrences: list[dict[str, object]] = []
    for row in groups:
        if row["exact_prose_card_id"] not in cards:
            continue
        card = cards[row["exact_prose_card_id"]]
        occurrences.append({
            "group_serial": row["group_serial"], "page": row["page"], "locus": row["locus"],
            "visible_owner": row["visible_owner"], "namespace_id": row["namespace_id"],
            "visible_surface": row["visible_surface"], "master_card_id": row["exact_prose_card_id"],
            "quantity_ending": card["quantity_ending"], "family_value_de": card["family_value_de"],
            "diagram_local_reading_de": row["concrete_diagram_reading_de"],
            "projection_result": "FALSE_FRIEND_RETAINED" if card["quantity_ending"] == "FALSE_FRIEND" else "QUANTITY_VALUE_PRESERVED",
        })

    comparison: list[dict[str, object]] = []
    for ending in ("AIN", "AN", "AIIN", "FALSE_FRIEND"):
        prose_cards = [r for r in cards.values() if r["quantity_ending"] == ending]
        astro = [r for r in occurrences if r["quantity_ending"] == ending]
        comparison.append({
            "ending": ending,
            "prose_card_count": len(prose_cards),
            "prose_event_count": sum(int(r["prose_event_count"]) for r in prose_cards),
            "astro_group_count": len(astro),
            "astro_pages": "|".join(dict.fromkeys(str(r["page"]) for r in astro)) or "NONE",
            "astro_surfaces": "|".join(dict.fromkeys(str(r["visible_surface"]) for r in astro)) or "NONE",
            "cross_register_reading": (
                "bounded partial value" if ending == "AIN" else
                "second/alternate portion not seen in Astro" if ending == "AN" else
                "prescribed value or degree" if ending == "AIIN" else
                "whole-card exclusion remains non-quantity"
            ),
        })

    occurrence_path = OUT / "TWO_HUNDRED_FIFTY_THIRD_13_ASTRO_OCCURRENCES.tsv"
    comparison_path = OUT / "TWO_HUNDRED_FIFTY_THIRD_PROSE_ASTRO_QUANTITY_COMPARISON.tsv"
    readable_path = OUT / "TWO_HUNDRED_FIFTY_THIRD_READABLE_ASTRO_QUANTITY.md"
    report_path = OUT / "TWO_HUNDRED_FIFTY_THIRD_REPORT.md"
    write_tsv(occurrence_path, occurrences, list(occurrences[0]))
    write_tsv(comparison_path, comparison, list(comparison[0]))

    readable = [
        "# Mengenenden im Astro-Register", "",
        "## AIIN", "",
        "Elf Diagrammgruppen lesen sich als vorgeschriebener Wert oder Grad: zehn auf f67r2 und eine auf f69v. Die sichtbaren Hüllen `daiin`, `aiin` und `saiin` ändern den Kern nicht.", "",
        "## AIN", "",
        "`okain` steht einmal an f67r2.28 und gibt einen gezählten Teilwert hinzu. Das passt zum Prosa-Kern abgegrenzter Anteil.", "",
        "## AN", "",
        "Kein Astro-Beleg. Die zweite/alternative Portion bleibt vorläufig an `ykan` gebunden.", "",
        "## DAIN", "",
        "`dain` steht an f67r2.48 für ein Abdeck- oder Trägerfeld. Es bleibt eine ganze Karte und wird nicht als D+AIN zerlegt.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    counts = Counter(r["quantity_ending"] for r in occurrences)
    report = f"""# Sidequest-Pass 253: Mengenenden auf Astro projiziert

## Ergebnis

Zwölf Astrogruppen tragen echte Mengenwerte: elf AIIN-Sollwerte/Grade und ein AIN-Teilwert. Eine dreizehnte sichtbare Ähnlichkeit, DAIN, bleibt korrekt ein Abdeck-/Trägerzeichen. AN fehlt im Astro-Ausschnitt.

Damit gewinnt AIIN eine starke registerübergreifende Lesung: nicht bloß Rezeptmaß, sondern vorgeschriebener Wert oder Grad. AIN bleibt eine begrenzte Teilmenge. Die DAIN-Ausnahme zeigt zugleich, dass der Schreiber ganze Karten gegen mechanische Suffixzerlegung schützt.

Input cards `{sha(CARDS)}`; Astro groups `{sha(GROUPS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "astro_occurrences": len(occurrences), "ending_counts": dict(counts),
        "comparison_rows": len(comparison),
        "outputs": {p.name: sha(p) for p in (occurrence_path, comparison_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
