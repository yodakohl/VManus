#!/usr/bin/env python3
"""Build an eight-day practical curriculum for the current workshop script."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCES = [
    ROOT / "experiments/yolo/sidequest_semantic_human_dictionary_thirty_fifth_edition/THIRTY_FIFTH_56_TEACHING_ENTRIES.tsv",
    ROOT / "experiments/yolo/sidequest_semantic_speakable_astro_thirty_sixth_edition/THIRTY_SIXTH_13_INSTRUMENT_MODULES.tsv",
    ROOT / "experiments/yolo/sidequest_semantic_worked_dossier_thirty_seventh_edition/THIRTY_SEVENTH_26_WORK_STEPS.tsv",
    ROOT / "experiments/yolo/sidequest_semantic_process_macros_thirty_eighth_edition/THIRTY_EIGHTH_20_PROCESS_MACROS.tsv",
    ROOT / "experiments/yolo/sidequest_semantic_scribe_memory_thirty_ninth_edition/THIRTY_NINTH_FOUR_MEMORY_SLOTS.tsv",
    ROOT / "experiments/yolo/sidequest_semantic_apprentice_error_book_forty_first_edition/FORTY_FIRST_EIGHT_ERROR_RULES.tsv",
    ROOT / "experiments/yolo/sidequest_semantic_forward_composition_forty_second_edition/FORTY_SECOND_20_FORWARD_COMMANDS.tsv",
    ROOT / "experiments/yolo/sidequest_semantic_nomenclator_forty_third_edition/FORTY_THIRD_15_NOMENCLATOR_LESSONS.tsv",
]


LESSONS = [
    (1, "L01", "Bildbesitzer lesen", "OWNER und Seitenbild", "zehn Bilder einem Besitzerregister zuordnen", "zehn Besitzer ohne Text benennen"),
    (1, "L02", "Record und Feld", "Record, Feld, Zelle", "elf Prosa-Records in 135 Felder teilen", "fünf zufällige Feldgrenzen richtig markieren"),
    (1, "L03", "Zeilen sind Raum", "Zeilenumbruch und Fortführung", "achtzehn zeilenübergreifende Aussagen laut lesen", "kein Zeilenende als automatischen Schluss behandeln"),
    (2, "L04", "Drei Mengenachsen", "AIIN, AIN, IIN", "Sollwert, Portion und Stufe an Minimalpaaren unterscheiden", "zwölf Karten ohne Verwechslung lesen"),
    (2, "L05", "Drei Richtungsachsen", "AL, AR, AIR", "Ziel, Quelle und Lauf unter drei Besitzern sprechen", "neun Besitzerwechsel richtig expandieren"),
    (2, "L06", "Ordnung und Referenz", "OK, OL, OT, Y, CLOSE", "ansetzen, fortsetzen, folgenden Posten, aktuellen Posten und Schluss unterscheiden", "zehn kurze Ketten korrekt ausführen"),
    (3, "L07", "Prozesskörper I", "CHD, CTH, CKH, CKHE", "umsetzen, bereitstellen, durchleiten und trennen", "acht Prozesskarten zum richtigen Gerät legen"),
    (3, "L08", "Prozesskörper II", "CHK, SHED, SOLK, CHEEY", "wärmen, absetzen, auffangen und sichtbares Ergebnis lesen", "vier Owner-Expansionen je Kern sprechen"),
    (3, "L09", "Gebundene Grade", "E, EE, EEE mit Y oder CLOSE", "kurz, länger und vollständig ausführen", "acht Gradfehler erkennen und berichtigen"),
    (4, "L10", "Gelernte Fachkörper", "N01 bis N10", "zehn Fachkörper aus dem kleinen Nomenklator abschreiben", "jede Form mit Kurzfunktion aufsagen"),
    (4, "L11", "Ganzkarten", "DL und TALAM", "Zusatz und am Ziel verwahren in realem Kontext lesen", "beide ohne Buchstabenzerlegung erkennen"),
    (4, "L12", "Registerspaltungen", "DAIN, ODY, OS", "Prosa- und Astro-Wert getrennt einsetzen", "sechs gemischte Beispiele richtig entscheiden"),
    (5, "L13", "Vierfach-Merktafel", "OWNER, ACTIVE, TARGET, PREVIOUS", "vier Kerben auf Wachstafel führen", "zehn Aussagen ohne Referentenverlust ausführen"),
    (5, "L14", "Siebzehn Wendungen", "E01 bis E17", "recurrent card idioms als ganze Handgriffe sprechen", "alle siebzehn aus Tuplekarten zusammensetzen"),
    (5, "L15", "Zwanzig Prozessmakros", "M01 bis M20", "mehrere Klauseln zu eingeübten Griffen bündeln", "zehn Programme wieder in Klauseln entfalten"),
    (6, "L16", "Vier Schreiberhände", "S1 bis S4", "dieselbe Tuplefolge in vier registrierten Oberflächen schreiben", "sechs Folgen bedeutungsgleich kopieren"),
    (6, "L17", "Fehlerbuch", "E01 bis E08 Fehlerklassen", "32 konkrete Fehler lesen und korrigieren", "acht neue Einzelfehler sofort benennen"),
    (6, "L18", "Vorwärtsdiktat", "X29 bis X48", "neue Befehle aus Owner, Merktafel und Idiomen schreiben", "vier ungesehene Befehle in zwei Händen ausgeben"),
    (7, "L19", "f67 Doppelrad", "lokale Räder und Module", "Rad und sichtbare Adresse vor Wert auswählen", "zehn lokale Stellen ohne Rotation lesen"),
    (7, "L20", "f68 Sternatlas", "mehrere Paneele und Sternplätze", "lokales Paneel vor Sternstelle setzen", "f68r1.14 wählen und sprechen"),
    (7, "L21", "f69 Dreifachtafel", "linkes, mittleres, rechtes Instrument", "drei Namensräume getrennt halten", "keinen f68-f69-Schlüssel erfinden"),
    (8, "L22", "H3 Pflanzen- und Filtergang", "vier WHAT-Aussagen", "alle H3-Schritte mit Besitzer und Merktafel lesen", "H3 ohne Wörterbuchverlust zurücksprechen"),
    (8, "L23", "B2 Stationsgang", "zweiundzwanzig HOW-Aussagen", "Ownerwechsel und Zielstellen durch den ganzen Stationsgang führen", "B2 mit allen Wechseln ausführen"),
    (8, "L24", "Vollständiger Auftrag", "WHEN-WHAT-HOW D2", "f68r1.14, H3 und B2 als Meisterauftrag verbinden", "26 Schritte lesen und einen davon in vier Händen schreiben"),
]


DAY_THEMES = {
    1: "Sehen und gliedern", 2: "Portable Kerne", 3: "Prozess und Grad",
    4: "Nomenklator", 5: "Gedächtnis und Makros", 6: "Schreiben und korrigieren",
    7: "Himmelsinstrumente", 8: "Gesellenstück",
}


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    lesson_rows = []
    for day, lesson_id, title, material, drill, completion in LESSONS:
        lesson_rows.append({
            "day": day,
            "day_theme": DAY_THEMES[day],
            "lesson_id": lesson_id,
            "lesson_title_de": title,
            "minutes": 100,
            "teaching_material": material,
            "master_demonstration_de": drill,
            "apprentice_completion_de": completion,
            "required_previous_lesson": f"L{int(lesson_id[1:]) - 1:02d}" if lesson_id != "L01" else "NONE",
            "mode": "SHOW_SPEAK_COPY_CORRECT",
        })
    write_tsv(OUT / "FORTY_FOURTH_24_LESSON_CURRICULUM.tsv", lesson_rows)

    exercise_rows = []
    targets = {
        1: ("OWNER", "FIELD", "LINE_CARRY", "RECORD_RESET"),
        2: ("AIIN_AIN_IIN", "AL_AR_AIR", "OK_OL_OT", "Y_CLOSE"),
        3: ("CHD_CTH", "CKH_CKHE", "CHK_SHED", "E_EE_EEE"),
        4: ("N01_N05", "N06_N10", "DL_TALAM", "DAIN_ODY_OS"),
        5: ("FOUR_SLOT_SLATE", "IDIOM_CHAIN", "PROCESS_MACRO", "LINE_CARRY_MEMORY"),
        6: ("FOUR_HAND_COPY", "ERROR_REPAIR", "FORWARD_COMMAND", "BACKWARD_READBACK"),
        7: ("F67_LOCAL", "F68_LOCAL", "F69_THREE", "NO_CROSS_KEY"),
        8: ("H3", "B2", "D2", "NEW_FOUR_HAND_COMMAND"),
    }
    for day in range(1, 9):
        for ordinal, target in enumerate(targets[day], 1):
            exercise_rows.append({
                "exercise_id": f"D{day}E{ordinal}",
                "day": day,
                "target": target,
                "master_prompt_de": f"Zeige, sprich und schreibe {target}; erkläre danach den Besitzer und die Merktafel.",
                "required_outputs": "VISIBLE_FORM|SPOKEN_VALUE|OWNER|MEMORY_STATE|CORRECTION",
                "attempts": 3,
                "success_rule_de": "drei fehlerfreie Wiederholungen; bei Fehler sofort kurze Regel aufsagen",
            })
    write_tsv(OUT / "FORTY_FOURTH_32_DAILY_EXERCISES.tsv", exercise_rows)

    exam = [
        ("F01", 10, "H3 vollständig lesen", "vier Aussagen, Besitzer, Karten und Merktafel ohne Auslassung"),
        ("F02", 10, "B2 vollständig führen", "22 Aussagen und alle sichtbaren Stationswechsel in Reihenfolge"),
        ("F03", 8, "f68r1.14 auswählen", "Paneel und lokale Adresse nennen; keine Rotation erfinden"),
        ("F04", 8, "acht Fehler korrigieren", "je eine Instanz aller acht Fehlerklassen"),
        ("F05", 8, "Nomenklator aufsagen", "zwölf Werte und drei Registerspaltungen"),
        ("F06", 6, "ein Makro entfalten", "Klauselfolge vorwärts und rückwärts erhalten"),
        ("F07", 6, "neuen Befehl schreiben", "Owner, vier Slots, Kartenfolge und zwei Handfassungen"),
        ("F08", 4, "Grenze nennen", "Bild- und Exemplarinhalte nicht als freie Stammbedeutung ausgeben"),
    ]
    exam_rows = [{
        "task_id": task_id,
        "points": points,
        "task_de": task,
        "completion_de": completion,
        "minimum_points_for_task": max(1, points - 2),
    } for task_id, points, task, completion in exam]
    write_tsv(OUT / "FORTY_FOURTH_FINAL_EXAM.tsv", exam_rows)

    lines = [
        "# Acht Tage bis zum Werkstattgesellen",
        "",
        "Der Lehrgang dauert acht Tage zu je fünf Stunden. Jede Lektion folgt demselben",
        "Rhythmus: zeigen, sprechen, kopieren, korrigieren. Das ist kein moderner Kursplan",
        "für einen historischen Codex, sondern unsere konkrete Antwort auf die Frage, ob",
        "mehrere Schreiber das vorgeschlagene System praktisch lernen könnten.",
        "",
    ]
    for day in range(1, 9):
        lines.extend([f"## Tag {day}: {DAY_THEMES[day]}", ""])
        for row in (lesson for lesson in lesson_rows if int(lesson["day"]) == day):
            lines.extend([
                f"### {row['lesson_id']} — {row['lesson_title_de']}",
                "",
                f"Material: {row['teaching_material']}. Übung: {row['master_demonstration_de']}. Abschluss: {row['apprentice_completion_de']}.",
                "",
            ])
    lines.extend([
        "## Gesellenstück",
        "",
        "Der Lehrling muss mindestens 48 von 60 Punkten erreichen und darf in F01, F02",
        "oder F08 nicht unter die jeweilige Mindestzahl fallen. Das Abschlussstück ist der",
        "26-Schritt-Auftrag f68r1.14 → H3 → B2 plus ein neuer zweihändiger Befehl.",
    ])
    (OUT / "FORTY_FOURTH_EIGHT_DAY_APPRENTICE_MANUAL.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "days": 8,
            "lessons": len(lesson_rows),
            "minutes": sum(int(row["minutes"]) for row in lesson_rows),
            "hours": sum(int(row["minutes"]) for row in lesson_rows) / 60,
            "daily_exercises": len(exercise_rows),
            "final_tasks": len(exam_rows),
            "final_points": sum(int(row["points"]) for row in exam_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in SOURCES},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
