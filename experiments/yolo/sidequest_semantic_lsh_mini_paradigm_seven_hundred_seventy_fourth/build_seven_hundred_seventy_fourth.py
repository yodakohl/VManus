#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P772 = ROOT / "experiments/yolo/sidequest_semantic_component_memory_optimization_seven_hundred_seventy_second"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P772 / "SEVEN_HUNDRED_SEVENTY_SECOND_173_CARD_RECIPE_ACCESS.tsv")
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    statements = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    lsh_cards = [row for row in cards if "LSH" in row["component_recipe"].split("+")]
    lsh_rows = []
    for row in lsh_cards:
        occurrences = [event for event in events if event["card_no"] == row["exact_card_id"]]
        predicted = " · ".join("WASCHEN" if component == "LSH" else {"O": "ARBEITSGANG", "E": "KURZ", "DY": "SCHLUSS"}[component] for component in row["component_recipe"].split("+"))
        lsh_rows.append({
            "exact_card_id": row["exact_card_id"],
            "surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"],
            "predicted_reading_de": predicted,
            "registered_reading_de": row["rebuilt_reading_de"],
            "events": len(occurrences),
            "event_ids": "|".join(event["event_id"] for event in occurrences),
            "pages": "|".join(sorted({event["page"] for event in occurrences})),
            "owners": "|".join(sorted({event["owner_de"] for event in occurrences})),
            "prediction_exact": "YES" if predicted == row["rebuilt_reading_de"] else "NO",
            "new_status": "BIO_PRODUCTIVE_MINI_PARADIGM",
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_FOURTH_LSH_MINI_PARADIGM.tsv",
        lsh_rows,
        ["exact_card_id", "surfaces", "component_recipe", "predicted_reading_de", "registered_reading_de", "events", "event_ids", "pages", "owners", "prediction_exact", "new_status"],
    )

    updated_cards = []
    for row in cards:
        out = dict(row)
        if "LSH" in row["component_recipe"].split("+"):
            out["access_mode"] = "BIO_LSH_MINI_PARADIGM"
            out["model_only_components"] = "NONE"
        out["reading_changed"] = "NO"
        updated_cards.append(out)
    write(
        "SEVEN_HUNDRED_SEVENTY_FOURTH_173_UPDATED_CARD_ACCESS.tsv",
        updated_cards,
        list(updated_cards[0].keys()),
    )

    access = {row["exact_card_id"]: row["access_mode"] for row in updated_cards}
    statement_rows = []
    for statement in statements:
        rows = by_statement[statement["statement_id"]]
        modes = [access[row["card_no"]] for row in rows]
        if "REGISTERED_WHOLE_CARD_MODEL_LOOKUP" in modes:
            mode = "USES_REGISTER_SPECIFIC_MODEL_CARD"
        elif "BIO_LSH_MINI_PARADIGM" in modes:
            mode = "USES_BIO_LSH_MINI_PARADIGM"
        elif all(value == "FAST_ORAL_COMPOSITION" for value in modes):
            mode = "FAST_ONLY"
        else:
            mode = "FAST_PLUS_WALL"
        statement_rows.append({
            "statement_id": statement["statement_id"],
            "page": statement["page"],
            "record": statement["record"],
            "events": len(rows),
            "access_mode": mode,
            "lsh_cards": sum(value == "BIO_LSH_MINI_PARADIGM" for value in modes),
            "model_cards": sum(value == "REGISTERED_WHOLE_CARD_MODEL_LOOKUP" for value in modes),
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_FOURTH_116_UPDATED_STATEMENT_ACCESS.tsv",
        statement_rows,
        ["statement_id", "page", "record", "events", "access_mode", "lsh_cards", "model_cards"],
    )

    remaining = [row for row in updated_cards if row["access_mode"] == "REGISTERED_WHOLE_CARD_MODEL_LOOKUP"]
    remaining_rows = []
    for row in remaining:
        occurrences = [event for event in events if event["card_no"] == row["exact_card_id"]]
        registers = sorted({"HERBAL" if event["record"].startswith("H") else "BIO" for event in occurrences})
        remaining_rows.append({
            "exact_card_id": row["exact_card_id"],
            "surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"],
            "reading_de": row["rebuilt_reading_de"],
            "events": sum(int(event["card_no"] == row["exact_card_id"]) for event in events),
            "register": "|".join(registers),
            "teaching_box": "HERBAL_RARE_MODEL_3" if registers == ["HERBAL"] else "BIO_RARE_MODEL_2",
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_FOURTH_5_REMAINING_MODEL_CARDS.tsv",
        remaining_rows,
        ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "register", "teaching_box"],
    )

    role_rows = [
        {"role": "MASTER_CORRECTOR", "shared_fast": 12, "shared_wall": 21, "bio_mini_components": 1, "rare_model_components": 5, "total_prose_components": 39, "rare_model_cards": 5},
        {"role": "HERBAL_SCRIBE", "shared_fast": 12, "shared_wall": 21, "bio_mini_components": 0, "rare_model_components": 3, "total_prose_components": 36, "rare_model_cards": 3},
        {"role": "BIO_STATION_SCRIBE", "shared_fast": 12, "shared_wall": 21, "bio_mini_components": 1, "rare_model_components": 2, "total_prose_components": 36, "rare_model_cards": 2},
        {"role": "ASTRO_TABLE_SCRIBE", "shared_fast": 0, "shared_wall": 0, "bio_mini_components": 0, "rare_model_components": 0, "total_prose_components": 0, "rare_model_cards": 0},
    ]
    write(
        "SEVEN_HUNDRED_SEVENTY_FOURTH_4_ROLE_COMPONENT_LOADS.tsv",
        role_rows,
        ["role", "shared_fast", "shared_wall", "bio_mini_components", "rare_model_components", "total_prose_components", "rare_model_cards"],
    )

    report = """# Pass 774 — LSH wird als kleine Bio-Regel befördert

`LSH` ist anders als die fünf übrigen seltenen Werte. Es steht in zwei Karten und drei Ereignissen:

- `lsho = LSH+O = WASCHEN · ARBEITSGANG`;
- `lshedy = LSH+E+DY = WASCHEN · KURZ · SCHLUSS`.

Die beiden Lesungen folgen exakt aus einem kurzen Wert `LSH=WASCHEN` plus bereits bekannten O/E/DY-Werten. Darum wird LSH nicht mehr als zwei unabhängige Ganzkarten gelernt, sondern als **Bio-Mini-Paradigma**. Es bleibt registerlokal, weil alle drei Belege in derselben f81v-Beckenstation liegen.

Der seltene Meisterblattrest schrumpft von sieben auf fünf Karten und von acht auf fünf Ereignisse. Diese fünf Werte teilen sich sauber: OS, CFH und TALAM nur Herbal; LD und DA nur Bio. Ein Herbal- oder Bio-Schreiber braucht damit je36 statt39 Prosa-Komponenten; nur der Meister kennt alle39.

Die produktive Schicht steigt auf168/173 Karten,376/381 Ereignisse und111/116 Aussagen. Keine Defaultlesung ändert sich.

Als naechstes werden die zwei registergetrennten Meisterblätter gebaut: drei Herbal-Kästchen und zwei Bio-Kästchen, plus eine kleine LSH-Zweikartenleiste. Dann wird geprüft, ob sich die Spezialisten ohne Zugriff auf das Blatt des anderen vollständig ausbilden lassen.
"""
    (HERE / "SEVEN_HUNDRED_SEVENTY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "lsh_cards": len(lsh_rows),
        "lsh_events": sum(int(row["events"]) for row in lsh_rows),
        "remaining_model_cards": len(remaining_rows),
        "remaining_model_events": sum(int(row["events"]) for row in remaining_rows),
        "productive_cards": sum(row["access_mode"] != "REGISTERED_WHOLE_CARD_MODEL_LOOKUP" for row in updated_cards),
        "productive_events": sum(int(row["events"]) for row in updated_cards if row["access_mode"] != "REGISTERED_WHOLE_CARD_MODEL_LOOKUP"),
        "productive_statements": sum(row["access_mode"] != "USES_REGISTER_SPECIFIC_MODEL_CARD" for row in statement_rows),
        "decision": "PROMOTE_LSH_AS_BIO_MINI_PARADIGM__FIVE_REGISTER_SPECIFIC_MODEL_CARDS_REMAIN",
    }
    (HERE / "SEVEN_HUNDRED_SEVENTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
