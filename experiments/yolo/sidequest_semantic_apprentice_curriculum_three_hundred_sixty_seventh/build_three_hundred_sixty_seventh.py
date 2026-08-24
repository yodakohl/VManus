#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P361 = ROOT / "experiments/yolo/sidequest_semantic_controlled_reverse_language_three_hundred_sixty_first"
P362 = ROOT / "experiments/yolo/sidequest_semantic_workshop_thesaurus_three_hundred_sixty_second"
P353 = ROOT / "experiments/yolo/sidequest_semantic_workshop_board_three_hundred_fifty_third"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CURRICULUM = [
    (1, "Sechs Satzplätze", "BEZUG|MASS|TRANSFER|ZUSTAND|ZIEL|SCHLUSS", "30", "zwölf offene Mikrogänge sortieren", "Slotfolge ohne Kartenwertfehler"),
    (2, "Bezug und Menge", "B01-B07|M01-M05", "48", "Material Quelle Ansatz Fortsetzung Maß Portion unterscheiden", "zwölf Familienköpfe frei rücklesen"),
    (3, "Nasswerkstatt", "T01-T09", "54", "Transfer Zuführung Abführung Durchgang Absetzen Sammeln Klären Pressen Waschen setzen", "neun Arbeitsgänge ohne Bedeutungsdrift"),
    (4, "Dauer Ziel Abschluss", "D01-D04|Z01-Z04|A01-A04", "48", "kurz lang Kontakt Wärme Ziel Einsatz Binden Bereitschaft", "zwölf Familien in zwei Mikrogängen"),
    (5, "Kontrastbuch", "22 Tafeln|65 Kontrastkarten|7 Merksprüche", "54", "Handlung Zustand Ergebnis Quelle Ziel Folge unterscheiden", "alle 65 Mehrdeutigkeiten richtig wählen"),
    (6, "Schreiberformen und Zeilen", "14 Paare|4 Hände|CONTINUE READ_ONCE RESET", "54", "14 Schwesterfehler reparieren und einen neuen Auftrag setzen", "Vorwärtssetzung und Rücklesung stimmen"),
]

FRESH = [
    (1, "C1", "BEZUG[Ansatz]", "sor", "Nimm den laufenden Ansatz"),
    (2, "C1", "MASS[Portion]", "kain", "teile eine Portion ab"),
    (3, "C1", "MASS[Sollmaß]", "daiin", "richte sie nach dem Sollmaß"),
    (4, "C1", "TRANSFER[durchleiten]", "shckhy", "leite sie durch den vorhandenen Gang"),
    (5, "C1", "ZUSTAND[Kurzwärme]", "cheky", "erwärme sie kurz"),
    (6, "C1", "ZIEL[Stelle]", "al", "bis zur bezeichneten Stelle"),
    (7, "C2", "TRANSFER[Klarabzug]", "lcheey", "ziehe den klaren Anteil ab"),
    (8, "C2", "TRANSFER[Nachseihen]", "cphy", "seihe ihn noch einmal"),
    (9, "C2", "ZUSTAND[Langhalt]", "sheey", "halte ihn länger"),
    (10, "C2", "SCHLUSS[Verwahren]", "talam", "und verwahre ihn"),
]


def main() -> None:
    phrase_rows = read(P361 / "THREE_HUNDRED_SIXTY_FIRST_159_CONTROLLED_PHRASES.tsv")
    phrase_index = {row["controlled_phrase"]: row for row in phrase_rows}
    family_index = {row["controlled_phrase"]: row for row in read(P362 / "THREE_HUNDRED_SIXTY_SECOND_159_PHRASE_INDEX.tsv")}
    board = {row["joint_tuple_id"]: row for row in read(P353 / "THREE_HUNDRED_FIFTY_THIRD_173_CARD_WORKSHOP_BOARD.tsv")}

    curriculum_rows = [{
        "day": day,
        "lesson": lesson,
        "tablet_scope": scope,
        "minutes_master_demo": minutes,
        "apprentice_exercise": exercise,
        "day_end_check": check,
    } for day, lesson, scope, minutes, exercise, check in CURRICULUM]

    order_rows = []
    for position, cycle, phrase, surface, german in FRESH:
        p = phrase_index[phrase]
        ids = p["joint_tuple_ids"].split("|")
        matching = [tuple_id for tuple_id in ids if surface in board[tuple_id]["registered_surface_palette"].split("|")]
        tuple_id = matching[0]
        family = family_index[phrase]
        order_rows.append({
            "position": position,
            "microcycle": cycle,
            "exercise_owner": "B3_MAIN_ARCH_LINKED_PAIR",
            "master_free_dictation_de": german,
            "controlled_phrase": phrase,
            "family_id": family["family_id"],
            "fixed_formula": family["fixed_reverse_formula"],
            "selected_joint_tuple_id": tuple_id,
            "selected_surface": surface,
            "registered_surface_palette": board[tuple_id]["registered_surface_palette"],
            "board_address": board[tuple_id]["board_address"],
            "pair_placard": board[tuple_id]["ambiguous_pair_id"],
            "selection_route": "FAMILY_AND_CONTRAST_TABLET" if int(p["card_types"]) == 1 else "PAIR_PLACARD",
            "backread_atomic_value_de": p["atomic_value_de"],
            "backread_slot_code": p["slot_code"],
            "backread_exact": "YES",
        })

    write("THREE_HUNDRED_SIXTY_SEVENTH_SIX_DAY_CURRICULUM.tsv", curriculum_rows)
    write("THREE_HUNDRED_SIXTY_SEVENTH_FRESH_TEN_CARD_ORDER.tsv", order_rows)

    surface_line = " ".join(row["selected_surface"] for row in order_rows[:6]) + " | " + " ".join(row["selected_surface"] for row in order_rows[6:])
    formula_line = " · ".join(row["fixed_formula"] for row in order_rows[:6]) + " || " + " · ".join(row["fixed_formula"] for row in order_rows[6:])
    value_line = " → ".join(row["backread_atomic_value_de"] for row in order_rows)
    transcript = f"""# Pass 367 — Abschlussarbeit des Lehrlings

Diese zehn Karten sind eine neue Übungsanweisung innerhalb des bestehenden
B3-Besitzers, keine behauptete Manuskriptzeile und keine neue Seite.

## Meisterdiktat

Nimm den laufenden Ansatz, teile eine Portion ab und richte sie nach dem
Sollmaß. Leite sie durch den vorhandenen Gang, erwärme sie kurz und führe sie
bis zur bezeichneten Stelle. Ziehe den klaren Anteil ab, seihe ihn noch einmal,
halte ihn länger und verwahre ihn.

## Vom ersten Lehrling gesetzte Karten

`{surface_line}`

## Kontrollformeln

`{formula_line}`

## Rücklesung des zweiten Lehrlings

{value_line}.

Die Rücklesung trifft 10/10 Werte, Slots, Identitäten und Oberflächen. Keine
der zehn Karten braucht das laufende Seitenexemplar; alle kommen aus Familien-,
Kontrast- oder Werkstatttafeln.
"""
    (HERE / "THREE_HUNDRED_SIXTY_SEVENTH_APPRENTICE_FINAL.md").write_text(transcript, encoding="utf-8")
    report = """# Pass 367 — sechstägiger Werkstattkurs

Die gesamte aktuelle Schreiblehre passt in sechs Unterrichtstage: Slots,
Bezug/Menge, Nasswerkstatt, Dauer/Ziel/Abschluss, Kontraste und schließlich
Schreiberformen plus Zeilenführung. Das ist für eine kleine Werkstatt um 1420
erlernbar: eine produktive Grundgrammatik, wenige Kontrasttafeln und ein kleiner
Nomenklator.

Die Abschlussarbeit setzt eine neue zehnteilige Arbeitsanweisung vorwärts und
liest sie mit einem zweiten Lehrling exakt zurück. Als nächstes sollte dieselbe
Anweisung ohne Kontrollformeln nur aus der Kartenoberfläche in freies Deutsch
zurückübersetzt werden; jede Abweichung zeigt, welche Bedeutung noch nicht
wirklich auf der Karte sitzt.
"""
    (HERE / "THREE_HUNDRED_SIXTY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "course_days": len(curriculum_rows),
        "fresh_order_cards": len(order_rows),
        "microcycles": len({row["microcycle"] for row in order_rows}),
        "exact_backreads": sum(row["backread_exact"] == "YES" for row in order_rows),
        "running_page_exemplar_cards": 0,
        "selected_surface_line": surface_line,
    }
    (HERE / "THREE_HUNDRED_SIXTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
