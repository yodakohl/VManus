#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
B1_DIR = ROOT / "experiments/yolo/sidequest_semantic_b1_process_ladder_four_hundred_thirty_first"
ALL = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    b1 = read(B1_DIR / "FOUR_HUNDRED_THIRTY_FIRST_REVISED_B1_66_EVENTS.tsv")
    statements = read(B1_DIR / "FOUR_HUNDRED_THIRTY_FIRST_REVISED_B1_21_STATEMENTS.tsv")
    all_events = read(ALL)
    cards = {
        "2cc8bb3c2af19607888f": ("CKH+Y", "durchführen", "DURCHLASS+CURRENT"),
        "259b2b3b0bf859882e2c": ("CHED+DY", "überführen; Schluss", "TRANSFER+CLOSE"),
        "28ffbc88b97772a75f1e": ("OL+CHED+DY", "weiterführen; Schluss", "CONTINUE+TRANSFER+CLOSE"),
        "433713294b25b0a12f66": ("L+CHED+AL", "zum Auslass führen", "OUTWARD+TRANSFER+TARGET"),
        "b6b654722e55729cc947": ("OT+AR", "danach von dort", "NEXT+SOURCE"),
        "d68bc8de3bcee09db23c": ("SH+CKHE+DY", "seihen; Schluss", "STRAIN+CLOSE"),
    }
    for row in b1:
        if row["joint_tuple_id"] in cards:
            row["small_value_de"] = cards[row["joint_tuple_id"]][1]
            row["lexicon_source"] = "SOURCE_PATH_TARGET_COMPOSITION"
    write("FOUR_HUNDRED_THIRTY_SECOND_REVISED_B1_66_EVENTS.tsv", b1)

    b1_by_event = {row["event_id"]: row for row in b1}
    fluent = {
        "B1-S002": "Nach Maß ansetzen, Beckenwasser an die Stelle setzen, mit demselben Bestand fortsetzen, zwei Portionen an der Stelle führen, warm halten, Zusatz und Fortsetzungsansatz zugeben, bemessen, länger an der Stelle halten, durchführen, überführen und schließen.",
        "B1-S005": "Den vorigen Gang weiterführen, überführen und schließen.",
        "B1-S006": "Eine Portion zugeben, durchführen, den Badzusatz zugeben und abkühlen.",
        "B1-S011": "Durch den Durchlass führen und dies verwenden.",
        "B1-S014": "Dies umsetzen, an die Arbeitsstelle und zum Auslass führen, fortsetzen und danach von dort weiternehmen.",
        "B1-S020": "Kurz wärmen, seihen und schließen.",
    }
    for row in statements:
        ids = row["event_ids"].split("|")
        row["card_sequence_de"] = " > ".join(b1_by_event[event_id]["small_value_de"] for event_id in ids)
        if row["statement_id"] in fluent:
            row["continuous_reading_de"] = fluent[row["statement_id"]]
    write("FOUR_HUNDRED_THIRTY_SECOND_REVISED_B1_21_STATEMENTS.tsv", statements)

    components = [
        {"component": "AL", "value_de": "Zielstelle", "question": "wohin?", "example": "L+CHED+AL = zum Auslass führen"},
        {"component": "AR", "value_de": "Quellseite; von dort", "question": "woher?", "example": "OT+AR = danach von dort"},
        {"component": "CKH", "value_de": "Durchlass", "question": "wodurch?", "example": "CKH+Y = dies durchführen"},
        {"component": "CHED", "value_de": "überführen", "question": "was tun?", "example": "CHED+DY = überführen und schließen"},
        {"component": "L", "value_de": "hinaus", "question": "welche Richtung?", "example": "L+CHED = hinausführen"},
        {"component": "OL", "value_de": "fortsetzen", "question": "welcher Bezug?", "example": "OL+CHED = weiterführen"},
        {"component": "OT", "value_de": "danach", "question": "welche Folge?", "example": "OT+AR = danach von dort"},
        {"component": "SH+CKHE", "value_de": "seihen", "question": "welcher Durchlass?", "example": "SH+CKHE+DY = seihen und schließen"},
        {"component": "DY", "value_de": "Schluss", "question": "ist die Zelle fertig?", "example": "nur in lizenzierter Schlusskarte"},
    ]
    write("FOUR_HUNDRED_THIRTY_SECOND_SOURCE_PATH_TARGET_LEXICON.tsv", components)

    audit = []
    for joint_id, (composition, value, role) in cards.items():
        rows = [row for row in all_events if row["joint_tuple_id"] == joint_id]
        audit.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({row["surface_display"] for row in rows})),
            "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "records": "|".join(sorted({row["record_unit_id"] for row in rows})),
            "composition": composition, "small_value_de": value, "role": role,
        })
    write("FOUR_HUNDRED_THIRTY_SECOND_SIX_CARD_OCCURRENCE_AUDIT.tsv", audit)

    summary = {
        "status": "PASS", "B1_events": len(b1), "B1_statements": len(statements),
        "components": len(components), "exact_cards": len(audit),
        "audited_occurrences": sum(int(row["events"]) for row in audit),
        "revised_value": {"otar": "danach von dort", "schedy": "überführen; Schluss"},
    }
    (HERE / "FOUR_HUNDRED_THIRTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
