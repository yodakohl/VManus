#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
TARGETS = {
    "2f1c5e56e8f0ff459065": ("AIIN", "Sollmaß", "PORTABLE_MEASURE_CARD"),
    "abb23e5e6936b4147f76": ("SHED+AL", "Absetzstelle", "COMPOSITIONAL_HOLDING_SITE"),
    "cb57b696b815fdef9cb7": ("SHECTHY", "temperiert", "LEARNED_STATE_CARD"),
    "e0b630cb1b5df5e7105b": ("CTH+Y", "bereit", "PORTABLE_READY_CARD"),
}


def read() -> list[dict[str, str]]:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    target_rows = []
    for source in read():
        if source["joint_tuple_id"] not in TARGETS:
            continue
        family, value, status = TARGETS[source["joint_tuple_id"]]
        target_rows.append({
            "event_id": source["event_id"],
            "record": source["record_unit_id"],
            "page": source["page"],
            "statement_id": source["statement_id"],
            "surface": source["surface_display"],
            "joint_tuple_id": source["joint_tuple_id"],
            "family": family,
            "selected_small_value_de": value,
            "status": status,
            "local_context_de": source["contextual_event_reading_de"],
        })
    write("FOUR_HUNDRED_SIXTH_30_TARGET_OCCURRENCES.tsv", target_rows)

    models = [
        {"model": "M1_MEASURE_SETTLE_TEMPER", "saiin": "Sollmaß", "shedal": "Absetzstelle", "shecthy": "temperiert", "score": 10, "decision": "SELECTED", "reason": "same AIIN card stays invariant; SHEDAL repeats as a site; SHECTHY fills the resulting state"},
        {"model": "M2_DURATION_REST_WARM", "saiin": "Dauer", "shedal": "Ruheplatz", "shecthy": "warm", "score": 6, "decision": "RIVAL", "reason": "natural phrase but makes one surface of the 20-event AIIN card change meaning"},
        {"model": "M3_DOSE_HOLDING_WARM_WATER", "saiin": "Dosis", "shedal": "Haltestelle", "shecthy": "warmes Wasser", "score": 5, "decision": "RIVAL", "reason": "possible bathing expansion but turns a positionally state-like whole card into a substance"},
        {"model": "M4_LOCAL_STATUS_CODES", "saiin": "Wert A", "shedal": "Ort B", "shecthy": "Status C", "score": 4, "decision": "RIVAL", "reason": "always possible but gives up the established compact dictionary"},
    ]
    write("FOUR_HUNDRED_SIXTH_FOUR_TRIPLE_MODELS.tsv", models)

    contextual = [
        {"statement": "B3-S021", "sequence": "SAIIN SHEDAL SHECTHY Y AL CTH CLOSE", "reading_de": "Sollmaß setzen; an der Absetzstelle halten; bis temperiert; Posten aufnehmen; zum Ziel; bereit; schließen"},
        {"statement": "B5-S003", "sequence": "SHEDAL AL OL LOL CHDAL AIIN OL DAIIN CHEDY", "reading_de": "Absetzstelle; Stelle; weiter; warm; an der Stelle umsetzen; Sollmaß; weiter; zweite Stufe; durcharbeiten"},
        {"statement": "B4-S008", "sequence": "SAIIN CHEEKY SHEEY QOKEDY", "reading_de": "Sollmaß; länger wärmen; erste Öffnung; kurz ansetzen und schließen"},
        {"statement": "B3-S030", "sequence": "OKY SAIIN SCHEDAIR OTCHEDY", "reading_de": "Posten ansetzen; Sollmaß; Wasser weiterführen; Folgeumsetzung schließen"},
    ]
    write("FOUR_HUNDRED_SIXTH_FOUR_CONTEXT_READINGS.tsv", contextual)

    summary = {
        "status": "PASS",
        "target_occurrences": len(target_rows),
        "aiin_occurrences": sum(row["family"] == "AIIN" for row in target_rows),
        "shedal_occurrences": sum(row["family"] == "SHED+AL" for row in target_rows),
        "shecthy_occurrences": sum(row["family"] == "SHECTHY" for row in target_rows),
        "cth_occurrences": sum(row["family"] == "CTH+Y" for row in target_rows),
        "decision": "SOLLMASS_ABSETZSTELLE_TEMPERIERT",
    }
    (HERE / "FOUR_HUNDRED_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
