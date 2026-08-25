#!/usr/bin/env python3
"""Build Pass 744: classify the remaining card-packing failures."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P743 = ROOT / "experiments/yolo/sidequest_semantic_helper_cue_packer_seven_hundred_forty_third"


def read(name: str) -> list[dict[str, str]]:
    with (P743 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def flatten(recipe_sequence: str) -> list[str]:
    cleaned = recipe_sequence.replace("UNPACKED(", "").replace(")", "").replace(" | ", "+")
    return cleaned.split("+") if cleaned else []


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    errors = read("SEVEN_HUNDRED_FORTY_THIRD_PACKING_ERRORS.tsv")
    audit = read("SEVEN_HUNDRED_FORTY_THIRD_116_REFINED_PACKING_AUDIT.tsv")
    audit_lookup = {row["statement_id"]: row for row in audit}

    taxonomy_rows = []
    missing_total: Counter[str] = Counter()
    extra_total: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    register_counts: Counter[tuple[str, str]] = Counter()
    for row in errors:
        predicted = Counter(flatten(row["packed_recipe_sequence"]))
        observed = Counter(flatten(row["observed_recipe_sequence_after_reveal"]))
        missing = observed - predicted
        extra = predicted - observed
        missing_total.update(missing)
        extra_total.update(extra)
        if row["missing_components"] != "NONE" or row["extra_components"] != "NONE":
            error_class = "SEMANTIC_SET_GAP"
        elif not missing and not extra:
            error_class = "TRUE_SEGMENTATION"
        elif set(missing) == {"Y"} and not extra:
            error_class = "Y_COPY_ONLY"
        elif "Y" in missing and not extra:
            error_class = "Y_PLUS_OTHER_COPY"
        elif not extra:
            error_class = "NON_Y_COPY"
        else:
            error_class = "EXTRA_HELPER_OR_MIXED"
        register = "HERBAL" if row["statement_id"].startswith("H") else "BIOLOGICAL"
        class_counts[error_class] += 1
        register_counts[(error_class, register)] += 1
        taxonomy_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "register": register, "error_class": error_class,
            "missing_occurrences": "+".join(item for item, count in sorted(missing.items()) for _ in range(count)) or "NONE",
            "extra_occurrences": "+".join(item for item, count in sorted(extra.items()) for _ in range(count)) or "NONE",
            "missing_y_count": missing["Y"], "card_count_delta": row["card_count_delta"],
            "predicted_recipe_sequence": row["packed_recipe_sequence"],
            "observed_recipe_sequence": row["observed_recipe_sequence_after_reveal"],
            "next_rule_de": {
                "SEMANTIC_SET_GAP": "fehlenden redaktionellen Inhalt nicht durch Packregel erfinden",
                "Y_COPY_ONLY": "aktiven Y-Posten in jede Y-valente Deckkarte kopieren",
                "Y_PLUS_OTHER_COPY": "Y kopieren; danach weitere wiederholte Adresse/Operation behandeln",
                "NON_Y_COPY": "wiederholte Adresse/Operation explizit in mehrere Karten verteilen",
                "TRUE_SEGMENTATION": "zwischen gleichwertigen attestierten Packungen priorisieren",
                "EXTRA_HELPER_OR_MIXED": "ein verbliebenes Hilfswort entfernen und Y-Kopie pruefen",
            }[error_class],
        })

    component_rows = []
    for component in sorted(set(missing_total) | set(extra_total), key=lambda item: (-missing_total[item], item)):
        component_rows.append({
            "component": component,
            "missing_occurrences": missing_total[component],
            "extra_occurrences": extra_total[component],
            "net_missing": missing_total[component] - extra_total[component],
            "priority": "P1_ACTIVE_REFERENT_COPY" if component == "Y" else "P2_OTHER_REPETITION",
        })

    class_rows = []
    class_order = ["Y_COPY_ONLY", "Y_PLUS_OTHER_COPY", "NON_Y_COPY", "SEMANTIC_SET_GAP", "TRUE_SEGMENTATION", "EXTRA_HELPER_OR_MIXED"]
    for rank, error_class in enumerate(class_order, 1):
        class_rows.append({
            "priority_rank": rank,
            "error_class": error_class,
            "statements": class_counts[error_class],
            "herbal_statements": register_counts[(error_class, "HERBAL")],
            "biological_statements": register_counts[(error_class, "BIOLOGICAL")],
            "repair_de": {
                "Y_COPY_ONLY": "Y-Valenz aus dem gelernten Deck anwenden; keine neue Bedeutung.",
                "Y_PLUS_OTHER_COPY": "zuerst Y-Valenz, danach lokale Wiederholungszahl fuer Menge/Adresse.",
                "NON_Y_COPY": "Mehrfachnennung von OL/AL/AIIN/Operationen als Kartenwiederholung lernen.",
                "SEMANTIC_SET_GAP": "Fluessige Ausgabe ergaenzen oder als redaktionelle Ellipse markieren.",
                "TRUE_SEGMENTATION": "Deckhaeufigkeit und Registermodus entscheiden zwischen gleichen Komponenten.",
                "EXTRA_HELPER_OR_MIXED": "den letzten ueberzaehligen Hilfscue entfernen.",
            }[error_class],
        })

    true_segmentation = [{
        "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
        "predicted_recipe_sequence": row["predicted_recipe_sequence"],
        "observed_recipe_sequence": row["observed_recipe_sequence"],
        "difference_de": "gleiche Komponenten mit anderer attestierter Kartenreihenfolge/-grenze",
    } for row in taxonomy_rows if row["error_class"] == "TRUE_SEGMENTATION"]

    write("SEVEN_HUNDRED_FORTY_FOURTH_42_ERROR_TAXONOMY.tsv", taxonomy_rows)
    write("SEVEN_HUNDRED_FORTY_FOURTH_18_MISSING_COPY_COMPONENTS.tsv", component_rows)
    write("SEVEN_HUNDRED_FORTY_FOURTH_6_REPAIR_PRIORITIES.tsv", class_rows)
    write("SEVEN_HUNDRED_FORTY_FOURTH_3_TRUE_SEGMENTATION_CASES.tsv", true_segmentation)

    report = f"""# Pass 744 — was die42 Fehler wirklich sind

Die Restfehler sind fast nie freie Bedeutungsunsicherheit und nur selten echte Wahl zwischen zwei gleichwertigen Kartengrenzen.

## Hauptbefund

- 20 Aussagen: nur **Y-Kopie** fehlt.
- 10 Aussagen: Y plus mindestens eine weitere wiederholte Karte fehlt.
- 5 Aussagen: andere Wiederholung ohne Y fehlt.
- 3 Aussagen: die fluessige Lesung verschweigt schon eine Bedeutungsfamilie.
- 3 Aussagen: echte Segmentierungsalternative bei exakt gleicher Komponentenmultiplizitaet.
- 1 Aussage: ein ueberzaehliges Hilfswort plus Wiederholung.

Ueber alle42 Fehler fehlen104 Komponentenwiederholungen, davon allein60× Y. Danach folgen OL6, AL5, AIIN4, OK4 sowie mehrere kleine Wiederholungen. Es gibt nur eine ueberzaehlige Komponente, OL.

## Bedeutungsrevision von Y

Y bleibt konkret **der aktuell gemeinte Arbeitsposten / dies**. Neu ist die Schreiberregel: Y wird nicht nur einmal genannt und dann sprachlich anaphorisch verstanden. Es ist ein **karteninterner Aktivposten-Slot**, der in jeder Y-valenten Fachkarte erneut gesetzt werden kann. Eine fluessige Uebersetzung sagt `ihn` oder gar nichts; die Werkstatt schreibt Y trotzdem wieder.

Das erklaert zugleich, warum der Packer die richtige Bedeutungsmenge fast immer kennt, aber zu wenige Karten und zu wenige Komponenten schreibt. Die naechste Verbesserung ist somit kein neues Wort, sondern Valenz und Kopie.

## Drei echte Packungsfaelle

Nur B1-S006, B1-S015 und B3-S030 besitzen bereits exakt dieselbe Komponentenmultiplizitaet wie das Original und unterscheiden sich trotzdem in der Kartenpackung. Erst fuer diese drei brauchen wir reine Deckprioritaeten.

## Nächster Hebel

Baue eine Y-Valenztabelle aus dem unveraenderten173er Deck: Welche Handlung-/Grad-/Adressrezepte tragen Y? Lass den Packer den aktiven Posten automatisch in solche Karten kopieren und pruefe danach, wie viele der30 Y-bedingten Fehler verschwinden.
"""
    (HERE / "SEVEN_HUNDRED_FORTY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "packing_errors": len(taxonomy_rows), "classes": len(class_rows),
        "class_counts": dict(class_counts), "missing_component_occurrences": sum(missing_total.values()),
        "missing_y_occurrences": missing_total["Y"], "extra_component_occurrences": sum(extra_total.values()),
        "true_segmentation_cases": len(true_segmentation), "component_inventory_rows": len(component_rows),
        "decision": "ACTIVE_Y_SLOT_COPY_DOMINATES_REMAINDER__ONLY_THREE_ERRORS_ARE_PURE_SEGMENTATION",
    }
    (HERE / "SEVEN_HUNDRED_FORTY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
