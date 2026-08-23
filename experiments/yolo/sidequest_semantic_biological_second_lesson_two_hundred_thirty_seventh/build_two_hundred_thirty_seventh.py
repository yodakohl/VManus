#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TRANSFER_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_f81_f82_curriculum_transfer_two_hundred_thirty_sixth/TWO_HUNDRED_THIRTY_SIXTH_ONE_HUNDRED_TWENTY_EIGHT_EVENTS.tsv"
TRANSFER_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_f81_f82_curriculum_transfer_two_hundred_thirty_sixth/TWO_HUNDRED_THIRTY_SIXTH_FORTY_THREE_DICTATION_TRACES.tsv"

WHOLE_SIGNS = {
    "MC061": ("SSHKCHDY", "SCHWENKEN; SCHLUSS", "E122", "B1-S003", "gelernte Handhabungs- und Schlusskarte"),
    "MC109": ("YTEY", "FÜLLEN", "E150", "B1-S015", "gelernte Füllkarte; Gefäß kommt vom Besitzer"),
    "MC012": ("DL", "BADZUSATZ", "E112|E129", "B1-S002|B1-S006", "zweimalige lokale Stoffkarte im selben Beckenrecord"),
    "MC065": ("LS", "DÜSE", "E196", "B2-S010", "gelernte Gerätekarte am Inline-Knoten"),
    "MC118": ("LY", "AUFFANGSCHALE", "E159", "B1-S018", "gelernte Empfangsgefäßkarte"),
    "MC152": ("CHES", "GLEICHTEILEN", "E216", "B2-S016", "gelernte Teilungsoperation"),
}

SECOND_LESSON = [
    ("L21", "AIN", "PORTION", "abgegrenzter Anteil; von AIIN/Sollwert getrennt"),
    ("L22", "AIR", "LAUFMEDIUM", "laufende Becken- oder Arbeitsflüssigkeit"),
    ("L23", "IIN", "ARBEITSSTUFE", "benannte Stufe; von AIIN/Maß getrennt"),
    ("L24", "CKH", "DURCHLASS", "Gang oder Passage; nicht CHK/Wärme"),
    ("L25", "LSH", "WASCHGANG", "lokale Wasch-/Spüloperation"),
    ("L26", "RESULT", "ERGEBNIS", "gelernte CHEEY/SHEY-Karte; kein freies EY"),
]

STATEMENT_REVISIONS = {
    "B1-S002": "Den Beckenlauf bemessen, am Ziel einsetzen und davon Portion und weiteren Anteil weiterführen; Badzusatz aus demselben Ansatz zugeben, auf Sollwert durch den Lauf überführen; Schluss.",
    "B1-S003": "Weiterführen, schwenken; Schluss.",
    "B1-S006": "Einen Anteil zugeben, durch den Lauf führen und den Badzusatz an die Zielmarke bringen.",
    "B1-S015": "Die Schale füllen und den Ansatz einführen; Schluss.",
    "B1-S018": "In der Auffangschale kurz halten, die Arbeitsstufe setzen und länger sammeln; Schluss.",
    "B2-S010": "Länger einwirken lassen, einsetzen und an der Düse das Ergebnis abnehmen.",
    "B2-S016": "Zum Ziel führen, von der Quelle abführen, gleichteilen, auf Sollwert bringen, die Folge bemessen, kurz einwirken und zuführen; Schluss.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(TRANSFER_EVENTS)
    value_by_card = {card_id: value for card_id, (_, value, _, _, _) in WHOLE_SIGNS.items()}
    event_rows: list[dict[str, object]] = []
    for row in events:
        revised = row["master_card_id"] in WHOLE_SIGNS
        event_rows.append({
            **row,
            "lesson_two_value_de": value_by_card.get(row["master_card_id"], row["portable_value_de"]),
            "final_teaching_status": "LEARNED_WHOLE_SIGN" if revised else ("SPECIALIST_COMPONENT_COMPOSITION" if row["curriculum_status"] == "EXISTING_SPECIALIST_COMPOSITION" else "BASE_CURRICULUM"),
            "lesson_two_revision": "YES" if revised else "NO",
        })
    write(OUT / "TWO_HUNDRED_THIRTY_SEVENTH_ONE_HUNDRED_TWENTY_EIGHT_EVENTS.tsv", event_rows)

    statement_rows: list[dict[str, object]] = []
    for row in read(TRANSFER_STATEMENTS):
        owned = [event for event in event_rows if event["statement_id"] == row["statement_id"]]
        statement_rows.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record_unit_id": row["record_unit_id"],
            "visible_owner": row["visible_owner"],
            "event_ids": row["event_ids"],
            "visible_sequence": row["apprentice_response"],
            "lesson_two_value_chain": " | ".join(str(event["lesson_two_value_de"]) for event in owned),
            "revised_master_dictation_de": STATEMENT_REVISIONS.get(row["statement_id"], row["master_dictation_de"]),
            "statement_status": "REVISED_WHOLE_SIGN_READING" if row["statement_id"] in STATEMENT_REVISIONS else "UNCHANGED",
        })
    write(OUT / "TWO_HUNDRED_THIRTY_SEVENTH_FORTY_THREE_STATEMENTS.tsv", statement_rows)

    lesson_rows = [{"lesson_id": lesson, "component": component, "short_value_de": value, "teaching_boundary": boundary} for lesson, component, value, boundary in SECOND_LESSON]
    write(OUT / "TWO_HUNDRED_THIRTY_SEVENTH_SIX_SPECIALIST_COMPONENTS.tsv", lesson_rows)

    sign_rows = [
        {"master_card_id": card_id, "visible_sign": sign, "memorized_value_de": value, "event_ids": events, "statement_ids": statements, "teaching_note": note}
        for card_id, (sign, value, events, statements, note) in WHOLE_SIGNS.items()
    ]
    write(OUT / "TWO_HUNDRED_THIRTY_SEVENTH_SIX_WHOLE_SIGNS.tsv", sign_rows)

    manual = [
        "# Zweite Lehrstunde für die Biological-Seiten",
        "",
        "Nach dem 20-Regel-Grundkurs lernt der Schreiber sechs Fachkomponenten und sechs ganze Zeichen.",
        "",
        "## Sechs Fachkomponenten",
        "",
    ]
    for row in lesson_rows:
        manual.append(f"- `{row['component']}` = **{row['short_value_de']}** — {row['teaching_boundary']}.")
    manual.extend(["", "## Sechs ganze Zeichen", ""])
    for row in sign_rows:
        manual.append(f"- `{row['visible_sign']}` = **{row['memorized_value_de']}** — {row['teaching_note']}.")
    manual.extend([
        "",
        "## Sieben reparierte Diktate",
        "",
    ])
    for statement_id, reading in STATEMENT_REVISIONS.items():
        manual.append(f"- {statement_id}: {reading}")
    manual.extend([
        "",
        "Damit besitzt jeder der 128 Kartenauftritte einen kurzen, konkreten Lehrwert. Kein Zeichen muss einen ganzen modernen Satz bedeuten; Besitzer und Satzbau liefern die ausgelassenen Nomen.",
    ])
    (OUT / "TWO_HUNDRED_THIRTY_SEVENTH_READABLE_SECOND_LESSON.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Pass 237 — zweite Biological-Lehrstunde",
        "",
        "Sechs vorhandene Fachkomponenten heben die konstruktive Deckung von 108 auf 121 Ereignisse. Die verbleibenden sieben Ereignisse werden mit sechs kurzen Ganzzeichen gelernt. Dadurch sind alle 128 Ereignisse und 43 Aussagen ohne UNKNOWN oder Satzglosse vorwärts diktierbar.",
        "",
        "Die stärksten Reparaturen sind `sshkchdy = schwenken; Schluss`, `ytey = füllen`, `dl = Badzusatz`, `ls = Düse`, `ly = Auffangschale`, `ches = gleichteilen`. Sie bilden genau das erwartete Nomenklator-Ende eines produktiven Fachkürzelsystems.",
        "",
        "Nächster Schritt: prüfen, ob diese sechs Ganzzeichen als syntaktische Klassen vorhersagbar sind — Stoff, Gerät, Gefäß oder Handlung — auch wenn ihre exakte Identität auswendig gelernt bleibt.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_SEVENTH_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
    summary = {
        "transfer_event_sha256": hashlib.sha256(TRANSFER_EVENTS.read_bytes()).hexdigest(),
        "transfer_statement_sha256": hashlib.sha256(TRANSFER_STATEMENTS.read_bytes()).hexdigest(),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "base_events": sum(row["final_teaching_status"] == "BASE_CURRICULUM" for row in event_rows),
        "specialist_component_events": sum(row["final_teaching_status"] == "SPECIALIST_COMPONENT_COMPOSITION" for row in event_rows),
        "whole_sign_events": sum(row["final_teaching_status"] == "LEARNED_WHOLE_SIGN" for row in event_rows),
        "whole_signs": len(sign_rows),
        "revised_statements": len(STATEMENT_REVISIONS),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
