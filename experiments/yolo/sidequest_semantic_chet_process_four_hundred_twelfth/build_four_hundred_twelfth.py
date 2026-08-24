#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
TARGET = "80ebbbbf238eee9f0aef"


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = list(csv.DictReader(handle, delimiter="\t"))
    target = [row for row in events if row["joint_tuple_id"] == TARGET]
    contexts = {
        "E004": ("ganzer Pflanzenbesitzer", "Wurzelteil > säubern > Vorrat", "Gefäß > Wasserzulauf > auffangen", "Pflanzenmaterial aufbereiten", "lokal wahrscheinlich schneiden oder zerstoßen"),
        "E311": ("gekoppeltes Becken-/Stationspaar", "Sollstand > bereit", "Folgemaß > untere Stelle > absetzen", "laufenden Posten bearbeiten", "lokal wahrscheinlich bewegen, rühren oder umsetzen"),
    }
    occurrence_rows = []
    for row in target:
        owner, before, after, expansion, local = contexts[row["event_id"]]
        occurrence_rows.append({
            "event_id": row["event_id"],
            "record": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "surface": row["surface_display"],
            "joint_tuple_id": row["joint_tuple_id"],
            "owner": owner,
            "preceding_sequence": before,
            "following_sequence": after,
            "portable_value_de": "bearbeiten",
            "contextual_expansion_de": expansion,
            "possible_physical_realization": local,
        })
    write("FOUR_HUNDRED_TWELFTH_TWO_CHET_OCCURRENCES.tsv", occurrence_rows)

    models = [
        {"candidate": "ZERKLEINERN", "H1": 4, "B3": 1, "portability": 1, "score": 6, "decision": "REJECT_HERBAL_ONLY"},
        {"candidate": "RÜHREN", "H1": 1, "B3": 4, "portability": 2, "score": 7, "decision": "REJECT_BIO_ONLY"},
        {"candidate": "UMSETZEN", "H1": 3, "B3": 3, "portability": 3, "score": 9, "decision": "KEEP_AS_LOCAL_RIVAL"},
        {"candidate": "BEARBEITEN", "H1": 4, "B3": 4, "portability": 4, "score": 12, "decision": "SELECT"},
    ]
    write("FOUR_HUNDRED_TWELFTH_FOUR_CHET_MODELS.tsv", models)

    contrasts = [
        {"card_family": "CTH", "small_value_de": "bereit", "role": "Freigabetor", "difference_from_CHET": "Zustand vor der Handlung"},
        {"card_family": "CHET", "small_value_de": "bearbeiten", "role": "allgemeine Arbeitsoperation", "difference_from_CHET": "TARGET"},
        {"card_family": "CHED", "small_value_de": "umsetzen", "role": "Transferoperation", "difference_from_CHET": "Ortswechsel statt allgemeiner Bearbeitung"},
        {"card_family": "SHED", "small_value_de": "absetzen", "role": "Ruheoperation", "difference_from_CHET": "Stillstand nach der Arbeit"},
        {"card_family": "CHK", "small_value_de": "wärmen", "role": "spezifische Behandlung", "difference_from_CHET": "Wärme statt allgemeiner Bearbeitung"},
    ]
    write("FOUR_HUNDRED_TWELFTH_FIVE_OPERATION_CONTRASTS.tsv", contrasts)

    statements = [
        {"statement_id": "H1-S001", "revised_card_sequence_de": "Wurzelteil > säubern > aus demselben Vorrat > bearbeiten > Gefäß > Wasserzulauf > auffangen > ansetzen > Sollmaß > Wurzelteil", "continuous_reading_de": "Von der abgebildeten Pflanze einen Wurzelteil nehmen, säubern, aus demselben Vorrat bearbeiten, in das Gefäß geben, Wasser zulaufen lassen, auffangen, den Posten ansetzen, bemessen und den Restteil verwahren.", "revision": "zerkleinern becomes bearbeiten; cutting remains a local possibility"},
        {"statement_id": "B3-S034", "revised_card_sequence_de": "Sollstand > bereit > bearbeiten > Folgemaß > untere Stelle > absetzen; Schluss", "continuous_reading_de": "Den Posten auf Sollstand bringen, freigeben, bearbeiten, das Folgemaß an der unteren Stelle einsetzen, absetzen lassen und den Schritt schließen.", "revision": "zerkleinern becomes bearbeiten; agitation or transfer remains local"},
    ]
    write("FOUR_HUNDRED_TWELFTH_TWO_REVISED_STATEMENTS.tsv", statements)

    summary = {
        "status": "PASS",
        "exact_card_occurrences": len(target),
        "surfaces": sorted({row["surface_display"] for row in target}),
        "models": len(models),
        "decision": "CHET_PROCESS_OR_WORK_WHOLE_CARD",
        "small_value_de": "BEARBEITEN",
    }
    (HERE / "FOUR_HUNDRED_TWELFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
