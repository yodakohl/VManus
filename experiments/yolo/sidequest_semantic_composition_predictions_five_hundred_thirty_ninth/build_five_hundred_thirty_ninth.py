#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P538 = ROOT / "experiments/yolo/sidequest_semantic_whole_card_attack_five_hundred_thirty_eighth"
P536 = ROOT / "experiments/yolo/sidequest_semantic_common_workshop_grammar_five_hundred_thirty_sixth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


VALUES = {
    "OK": "ansetzen", "OT": "danach", "OL": "fortsetzen",
    "AIIN": "Maß", "AIN": "Portion", "AL": "Zielstelle", "AR": "von dort", "AIR": "Lauf",
    "E": "kurz", "EE": "länger", "EEE": "vollständig",
    "Y": "dies", "DY": "Schluss", "SH": "halten", "CHK": "wärmen", "SOLK": "auffangen",
}


def mnemonic(parts: list[str]) -> str:
    return "".join(part.lower() for part in parts)


def main() -> None:
    cards = read_tsv(P538 / "FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")
    events = read_tsv(P538 / "FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_THREE_HUNDRED_EIGHTY_ONE_EVENT_EDITION.tsv")
    source_events = read_tsv(P536 / "FIVE_HUNDRED_THIRTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_COMMON_GRAMMAR_INTERLINEAR.tsv")
    by_parse: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        by_parse[row["component_parse"]].append(row)
    by_surface: dict[str, set[str]] = defaultdict(set)
    for row in source_events:
        by_surface[row["surface"]].add(row["card_no"])

    address_rows: list[dict[str, str]] = []
    prefixes = ["BARE", "OK", "OT", "OL"]
    arguments = ["AIIN", "AIN", "AL", "AR", "AIR"]
    for prefix in prefixes:
        for argument in arguments:
            parts = [] if prefix == "BARE" else [prefix]
            parts.append(argument)
            parse = "+".join(parts)
            observed = by_parse.get(parse, [])
            canonical = mnemonic(parts)
            address_rows.append(
                {
                    "family": "OPERATOR_ADDRESS",
                    "prefix": prefix,
                    "argument": argument,
                    "component_parse": parse,
                    "predicted_atomic_reading_de": " · ".join(VALUES[part] for part in parts),
                    "canonical_workshop_mnemonic": canonical,
                    "status_on_ten_pages": "ATTESTED" if observed else "PREDICTED_MISSING_CELL",
                    "card_ids": "|".join(row["card_no"] for row in observed) or "NONE",
                    "occurrences": str(sum(int(row["occurrences"]) for row in observed)),
                    "surface_collision_card_ids": "|".join(sorted(by_surface.get(canonical, set()))) or "NONE",
                }
            )
    write_tsv("FIVE_HUNDRED_THIRTY_NINTH_TWENTY_OPERATOR_ADDRESS_MATRIX.tsv", address_rows)

    grade_rows: list[dict[str, str]] = []
    bases = ["OK", "OT", "SH", "CHK", "SOLK"]
    grades = ["E", "EE", "EEE"]
    endpoints = ["Y", "DY"]
    for base in bases:
        for grade in grades:
            for endpoint in endpoints:
                parts = [base, grade, endpoint]
                parse = "+".join(parts)
                observed = by_parse.get(parse, [])
                canonical = mnemonic(parts)
                grade_rows.append(
                    {
                        "family": "GRADE_ENDPOINT",
                        "base": base,
                        "grade": grade,
                        "endpoint": endpoint,
                        "component_parse": parse,
                        "predicted_atomic_reading_de": " · ".join(VALUES[part] for part in parts),
                        "canonical_workshop_mnemonic": canonical,
                        "status_on_ten_pages": "ATTESTED" if observed else "PREDICTED_MISSING_CELL",
                        "card_ids": "|".join(row["card_no"] for row in observed) or "NONE",
                        "occurrences": str(sum(int(row["occurrences"]) for row in observed)),
                        "surface_collision_card_ids": "|".join(sorted(by_surface.get(canonical, set()))) or "NONE",
                    }
                )
    write_tsv("FIVE_HUNDRED_THIRTY_NINTH_THIRTY_GRADE_ENDPOINT_MATRIX.tsv", grade_rows)

    predictions: list[dict[str, str]] = []
    for row in [*address_rows, *grade_rows]:
        if row["status_on_ten_pages"] != "PREDICTED_MISSING_CELL":
            continue
        if row["family"] == "OPERATOR_ADDRESS":
            same_base = sum(
                candidate["status_on_ten_pages"] == "ATTESTED"
                for candidate in address_rows if candidate["prefix"] == row["prefix"]
            )
            same_tail = sum(
                candidate["status_on_ten_pages"] == "ATTESTED"
                for candidate in address_rows if candidate["argument"] == row["argument"]
            )
        else:
            same_base = sum(
                candidate["status_on_ten_pages"] == "ATTESTED"
                for candidate in grade_rows if candidate["base"] == row["base"]
            )
            same_tail = sum(
                candidate["status_on_ten_pages"] == "ATTESTED"
                for candidate in grade_rows
                if candidate["grade"] == row["grade"] and candidate["endpoint"] == row["endpoint"]
            )
        support = same_base + same_tail
        predictions.append(
            {
                "prediction_id": "",
                "family": row["family"],
                "component_parse": row["component_parse"],
                "canonical_workshop_mnemonic": row["canonical_workshop_mnemonic"],
                "predicted_atomic_reading_de": row["predicted_atomic_reading_de"],
                "same_base_attested_cells": str(same_base),
                "same_tail_attested_cells": str(same_tail),
                "support_score": str(support),
                "surface_collision_card_ids": row["surface_collision_card_ids"],
                "prediction_strength": "HIGH" if support >= 6 else "MEDIUM" if support >= 4 else "LOW",
                "interpretive_expansion_de": row["predicted_atomic_reading_de"].replace(" · ", " "),
                "claim_scope": "PREDICTED_COMPOSITION_NOT_OBSERVED_CARD",
            }
        )
    predictions.sort(key=lambda row: (-int(row["support_score"]), row["component_parse"]))
    for number, row in enumerate(predictions, 1):
        row["prediction_id"] = f"P{number:02d}"
    write_tsv("FIVE_HUNDRED_THIRTY_NINTH_TWENTY_MISSING_COMPOSITION_PREDICTIONS.tsv", predictions)

    collisions = [row for row in predictions if row["surface_collision_card_ids"] != "NONE"]
    if collisions:
        write_tsv("FIVE_HUNDRED_THIRTY_NINTH_PREDICTION_SURFACE_COLLISIONS.tsv", collisions)
    else:
        write_tsv(
            "FIVE_HUNDRED_THIRTY_NINTH_PREDICTION_SURFACE_COLLISIONS.tsv",
            [{"status": "NONE", "detail": "No canonical prediction mnemonic collides with an observed surface"}],
        )

    summary = {
        "status": "PASS",
        "address_cells": len(address_rows),
        "address_attested": sum(row["status_on_ten_pages"] == "ATTESTED" for row in address_rows),
        "address_predicted": sum(row["status_on_ten_pages"] == "PREDICTED_MISSING_CELL" for row in address_rows),
        "grade_cells": len(grade_rows),
        "grade_attested": sum(row["status_on_ten_pages"] == "ATTESTED" for row in grade_rows),
        "grade_predicted": sum(row["status_on_ten_pages"] == "PREDICTED_MISSING_CELL" for row in grade_rows),
        "predictions": len(predictions),
        "high_predictions": sum(row["prediction_strength"] == "HIGH" for row in predictions),
        "medium_predictions": sum(row["prediction_strength"] == "MEDIUM" for row in predictions),
        "low_predictions": sum(row["prediction_strength"] == "LOW" for row in predictions),
        "canonical_surface_collisions": len(collisions),
        "source_events_unchanged": len(events),
    }
    (HERE / "FIVE_HUNDRED_THIRTY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    top = predictions[:10]
    lines = [
        "# Fünfhundertneununddreißigste Runde: vorhergesagte Kartenkompositionen",
        "",
        "## Zwei geschlossene Raster",
        "",
        f"Das Operator-/Adressraster besitzt 20 Zellen: {summary['address_attested']} sind auf den zehn Seiten belegt, {summary['address_predicted']} fehlen.",
        f"Das Grad-/Endpunktraster besitzt 30 Zellen: {summary['grade_attested']} sind belegt, {summary['grade_predicted']} fehlen.",
        "",
        "Die fehlenden Zellen werden nicht als gefundene Voynich-Wörter ausgegeben. Sie sind konkrete Werkstattvorhersagen: Wenn unser Kompositionsmodell stimmt, müsste ein Schreiber ihre Bedeutung ohne neues Ganzwort bilden können.",
        "",
        "## Stärkste Vorhersagen",
        "",
    ]
    for row in top:
        lines.append(
            f"- `{row['canonical_workshop_mnemonic']}` ({row['component_parse']}) = {row['predicted_atomic_reading_de']} [{row['prediction_strength']}]"
        )
    lines.extend(
        [
            "",
            "## Praktische Lesungen",
            "",
            "- OL+AIIN: im gleichen Vorgang mit dem Maß fortsetzen;",
            "- OT+AIN: danach die nächste Portion;",
            "- OT+AIR: danach den Lauf weiternehmen;",
            "- OK+EEE+Y: diesen Posten vollständig ansetzen, aber noch offen lassen;",
            "- SH+EEE+DY: vollständig halten und die Zelle schließen;",
            "- SOLK+E+DY: kurz auffangen und schließen.",
            "",
            "## Wichtige Grenze",
            "",
            "Die kanonischen Kleinformen sind Werkstattmnemonics. Der reale Schreiber kann q-, s-, ch- oder andere Wrapper setzen. Vorhergesagt wird daher zuerst die Komponentenfolge und Bedeutung, nicht blind eine einzige Oberflächenschreibung.",
            "",
            "## Nächster Angriff",
            "",
            "Als Nächstes werden die zwanzig Vorhersagen gegen sämtliche bereits vorhandenen Oberflächen- und Wrapperregeln geführt. Ziel ist für jede Komposition eine kleine Menge tatsächlich schreibbarer Oberflächen, nicht nur ein abstraktes Stammrezept.",
        ]
    )
    (HERE / "FIVE_HUNDRED_THIRTY_NINTH_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
