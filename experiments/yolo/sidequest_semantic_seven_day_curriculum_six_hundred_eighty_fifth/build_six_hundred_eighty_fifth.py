#!/usr/bin/env python3
"""Build a seven-day supervised curriculum for the current workshop model."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"
P680 = ROOT / "experiments/yolo/sidequest_semantic_owner_expanded_compact_edition_six_hundred_eightieth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


DAYS = [
    (1, "GRUNDHANDLUNGEN", "OK CHD SH SHED CHK SOLK P LSH", "acht Grundhandlungen sprechen und auf vorhandenen Karten zeigen", "8 roots; open/closed pair drill"),
    (2, "HILFSHANDLUNGEN", "CFH CH T K S L R LD", "auswringen abnehmen eintragen dosieren teilen weiterleiten kuehlen befestigen", "8 roots; action-chain copying"),
    (3, "GEGENSTAND_ADRESSE", "CTH AIR OR HO CKH O OL OT AL AR Y", "Zustand Gegenstand Quelle Ziel Folge und aktuellen Posten unterscheiden", "11 roots; owner-address drill"),
    (4, "PARAMETER_UND_SCHLUSS", "AIN AIIN IIN AN DA E EE EEE DY OS RESUME_CARD TALAM", "Portion Mass Stufe Grad Schluss und drei Ganzbefehle lernen", "12 roots; mass/portion and Y/DY drill"),
    (5, "ZWOLF_HAEUFIGE_FAMILIEN", "", "48 Vierstufenuebungen aus dem Zwolferblatt", "12 recipe families;140 source events represented"),
    (6, "KARTENBUCH_UND_SELTENE_FORMEN", "", "34 Reiter zehn Doppelzeilen und seltene KEEP-ADD-DROP-REPLACE-Zettel benutzen", "38 remaining recurrent families;113 rare lessons"),
    (7, "GANZE_RECORDS", "", "H3 B1 und B6 vollstaendig schreiben und ruecklesen", "3 records;92 events;three owner modes"),
]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    roots = {row["component"]: row for row in read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")}
    records = {row["record"]: row for row in read(P680 / "SIX_HUNDRED_EIGHTIETH_11_CONTINUOUS_OWNER_RECORDS.tsv")}

    day_rows = []
    for day, title, root_string, goal, workload in DAYS:
        components = root_string.split() if root_string else []
        day_rows.append({
            "day": day,
            "lesson": title,
            "new_components": " ".join(components) if components else "NONE_NEW",
            "new_component_count": len(components),
            "spoken_values_de": " | ".join(roots[component]["compact_table_value_de"] for component in components) if components else "PRACTICE_ONLY",
            "day_goal_de": goal,
            "fixed_workload": workload,
            "expected_book_use": "OPEN_COPYBOOK",
            "end_of_day_check_de": "Diktat in Rezept umsetzen Karte finden Oberflaeche kopieren und atomar ruecklesen.",
        })

    session_templates = {
        1: ["Meister zeigt und spricht neue Zeichen", "Lehrling sortiert sie in den richtigen Kasten", "Bestehende Karten abschreiben und ruecklesen"],
        2: ["Neue Hilfshandlungen mit Gesten lernen", "Zwei- und Dreiaktionsketten aus dem Buch suchen", "Fehlkopien verbessern und laut ruecklesen"],
        3: ["Bildbesitzer gegen Kartenwert trennen", "Quelle Ziel Lauf Ansatz und Dies an Bildern ueben", "Recordabschnitte mit Besitzerwechsel kopieren"],
        4: ["Portion Mass Stufe und Grade sprechen", "Y gegen lizenzierte DY-Endkarte ueben", "Drei Ganzbefehle ohne Zerlegung kopieren"],
        5: ["Zwölf Familien hören und Rezept nennen", "Karten- und Oberflaechenwahl in48 Drills", "Haeufige Fehler gegenseitig korrigieren"],
        6: ["34 Reiter und zehn Doppelzeilen benutzen", "Seltene Ein- bis Dreischrittvarianten suchen", "Zwölf schwerste Karten mit offenem Buch kopieren"],
        7: ["H3 Pflanzenrecord schreiben", "B1 Beckenrecord schreiben", "B6 Nebenstation schreiben und alle drei ruecklesen"],
    }
    session_rows = []
    for day in range(1, 8):
        for session_no, instruction in enumerate(session_templates[day], start=1):
            session_rows.append({
                "day": day,
                "session": session_no,
                "duration_hours": 2,
                "instruction_de": instruction,
                "master_present": "YES",
                "copybook_open": "YES",
            })

    trial_rows = []
    for trial_no, record_id in enumerate(["H3", "B1", "B6"], start=1):
        record = records[record_id]
        trial_rows.append({
            "trial_no": trial_no,
            "record": record_id,
            "page": record["page"],
            "statements": record["statements"],
            "events": record["events"],
            "owner_sequence": record["owners_in_order"],
            "copy_task_de": "Exakte sichtbare Folge mit offenem Kartenbuch kopieren.",
            "readback_task_de": "Jede Karte atomar und danach den ganzen Record mit Besitzer sprechen.",
            "completion_rule": "NO_SKIPPED_EVENT__NO_INVENTED_SURFACE__OWNER_CHANGE_RETAINED",
        })

    error_rows = [
        ("E01", "MASS_AS_PORTION", "AIIN als PORTION", "AIIN=MASS; AIN=PORTION"),
        ("E02", "SOURCE_TARGET_SWAP", "AR und AL vertauscht", "AR=QUELLE; AL=ZIEL"),
        ("E03", "Y_AS_CLOSE", "sichtbares dy schliesst automatisch", "Y=DIES; nur lizenzierte Endkarte schliesst"),
        ("E04", "EE_AS_CLOSE", "LANG beendet den Gang", "EE ist nur Grad; Endkarte gesondert suchen"),
        ("E05", "OT_AS_OL", "DANACH und FORTSETZEN vertauscht", "OT neuer Folgegang; OL gleicher Gang"),
        ("E06", "FREE_SURFACE_SPELLING", "Oberflaeche aus Bausteinen erfunden", "nur vorhandene Kartenform kopieren"),
        ("E07", "WRONG_DOUBLE_VARIANT", "falsche Karte einer Doppelzeile", "Seite Record und lokales Exemplar vergleichen"),
        ("E08", "OWNER_OMITTED", "DIES ohne Bildbesitzer gelesen", "Besitzer vor dem Rezept merken"),
        ("E09", "LINE_AS_SENTENCE_END", "am Zeilenende unnoetig geschlossen", "Aussage darf ueber die Zeile weiterlaufen"),
        ("E10", "WHOLE_CARD_SPLIT", "FACH oder VERWAHREN zerlegt", "Nomenklatorbefehle als Ganzes lernen"),
    ]
    error_table = [{"error_id": eid, "error": error, "symptom_de": symptom, "master_correction_de": correction} for eid, error, symptom, correction in error_rows]

    write("SIX_HUNDRED_EIGHTY_FIFTH_7_DAY_CURRICULUM.tsv", day_rows)
    write("SIX_HUNDRED_EIGHTY_FIFTH_21_TWO_HOUR_SESSIONS.tsv", session_rows)
    write("SIX_HUNDRED_EIGHTY_FIFTH_3_FINAL_RECORD_TRIALS.tsv", trial_rows)
    write("SIX_HUNDRED_EIGHTY_FIFTH_10_ERROR_RUBRIC.tsv", error_table)

    summary = {
        "status": "PASS",
        "days": len(day_rows),
        "sessions": len(session_rows),
        "supervised_hours": sum(int(row["duration_hours"]) for row in session_rows),
        "roots_introduced": sum(int(row["new_component_count"]) for row in day_rows),
        "final_trial_records": len(trial_rows),
        "final_trial_events": sum(int(row["events"]) for row in trial_rows),
        "error_classes": len(error_table),
        "graduation_level": "SUPERVISED_COPYBOOK_LITERACY_NOT_MEMORY_MASTERY",
    }
    (HERE / "SIX_HUNDRED_EIGHTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
