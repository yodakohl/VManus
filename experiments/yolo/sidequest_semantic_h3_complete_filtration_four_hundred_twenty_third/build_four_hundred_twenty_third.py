#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

VALUES = {
    "E039": "Blütenkraut", "E040": "Sud", "E041": "auswringen", "E042": "Standzeit", "E043": "nachseihen", "E044": "Klarauszug", "E045": "abkühlen; Schluss",
    "E046": "Reserve setzen",
    "E047": "Fortsetzung", "E048": "dies", "E049": "Trank", "E050": "dies", "E051": "Mass",
    "E052": "Reserve nehmen", "E053": "Fortsetzung einsetzen", "E054": "bereit", "E055": "dies",
}


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = [row for row in csv.DictReader(handle, delimiter="\t") if row["record_unit_id"] == "H3"]
    interlinear = []
    for order, row in enumerate(events, start=1):
        interlinear.append({
            "order": order, "event_id": row["event_id"], "locus": row["locus"], "statement_id": row["statement_id"],
            "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "selected_small_value_de": VALUES[row["event_id"]],
            "process_phase": "SEPARATION_CHAIN" if int(row["event_id"][1:]) <= 45 else ("RESERVE" if row["event_id"] in {"E046", "E052"} else "SECOND_PRODUCT"),
        })
    write("FOUR_HUNDRED_TWENTY_THIRD_H3_17_EVENT_INTERLINEAR.tsv", interlinear)

    statements = [
        {"statement_id": "H3-S001", "events": "E039-E045", "card_sequence_de": "Blütenkraut > Sud > auswringen > Standzeit > nachseihen > Klarauszug > abkühlen; Schluss", "continuous_reading_de": "Blütenkraut zu einem Sud bereiten, auswringen, die Standzeit einhalten, nachseihen, den Klarauszug abnehmen und abkühlen; den Schritt schließen."},
        {"statement_id": "H3-S002", "events": "E046", "card_sequence_de": "Reserve setzen", "continuous_reading_de": "Einen Anteil als Reserve zurückbehalten."},
        {"statement_id": "H3-S003", "events": "E047-E051", "card_sequence_de": "Fortsetzung > dies > Trank > dies > Mass", "continuous_reading_de": "Mit der Fortsetzung daraus einen Trank bereiten und diesen nach Maß abteilen."},
        {"statement_id": "H3-S004", "events": "E052-E055", "card_sequence_de": "Reserve nehmen > Fortsetzung einsetzen > bereit > dies", "continuous_reading_de": "Die Reserve nehmen, als Fortsetzung einsetzen und bereitstellen; dies bleibt der laufende Posten."},
    ]
    write("FOUR_HUNDRED_TWENTY_THIRD_H3_FOUR_STATEMENTS.tsv", statements)

    chain = [
        {"phase": 1, "card": "TSHOL", "small_value_de": "Blütenkraut", "input": "picture-owned plant material", "output": "selected flowering herb"},
        {"phase": 2, "card": "SCHOAL", "small_value_de": "Sud", "input": "flowering herb", "output": "wet preparation"},
        {"phase": 3, "card": "CFHY", "small_value_de": "auswringen", "input": "wet preparation", "output": "pressed liquid"},
        {"phase": 4, "card": "SHFY+AIIN", "small_value_de": "Standzeit", "input": "pressed liquid", "output": "settled liquid"},
        {"phase": 5, "card": "CPHY", "small_value_de": "nachseihen", "input": "settled liquid", "output": "filtered liquid"},
        {"phase": 6, "card": "SHEY", "small_value_de": "Klarauszug", "input": "filtered liquid", "output": "named clear product"},
        {"phase": 7, "card": "TCHODY", "small_value_de": "abkühlen; Schluss", "input": "clear product", "output": "cooled closed preparation"},
    ]
    write("FOUR_HUNDRED_TWENTY_THIRD_SEVEN_STAGE_FILTRATION_CHAIN.tsv", chain)

    reserve = [
        {"event_id": "E046", "surface": "shoyty", "value_de": "Reserve setzen", "position": "after first product", "effect": "one portion held outside the current chain"},
        {"event_id": "E052", "surface": "qotchy", "value_de": "Reserve nehmen", "position": "start of later field", "effect": "held portion becomes active again"},
    ]
    write("FOUR_HUNDRED_TWENTY_THIRD_RESERVE_PAIR.tsv", reserve)

    article_matrix = [
        {"record": "H3", "events": 17, "dominant_work": "separate and clarify", "signature_cards": "wring|stand|re-strain|clear extract", "application_present": "NO", "article_role": "FILTRATION"},
        {"record": "H4", "events": 18, "dominant_work": "measure temper and store", "signature_cards": "portion|cool|store|warm", "application_present": "NO", "article_role": "PREPARATION_STORAGE"},
        {"record": "H5", "events": 27, "dominant_work": "prepare wash apply and use", "signature_cards": "ingredient|wash|apply|use", "application_present": "YES", "article_role": "APPLICATION"},
    ]
    write("FOUR_HUNDRED_TWENTY_THIRD_H3_H4_H5_ARTICLE_MATRIX.tsv", article_matrix)

    summary = {
        "status": "PASS", "events": len(interlinear), "statements": len(statements), "filtration_stages": len(chain),
        "decision": "H3_COMPLETE_FILTRATION_WITH_RESERVE_RECALL", "medium_revision": "WEINSUD_TO_SUD",
    }
    (HERE / "FOUR_HUNDRED_TWENTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
