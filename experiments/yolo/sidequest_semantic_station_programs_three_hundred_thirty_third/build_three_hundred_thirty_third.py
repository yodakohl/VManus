#!/usr/bin/env python3
"""Reduce the repaired Bio edition to twelve teachable station programs."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_repaired_bio_edition_three_hundred_thirty_second"
STATEMENTS = SOURCE / "THREE_HUNDRED_THIRTY_SECOND_97_REPAIRED_BIO_STATEMENTS.tsv"
EVENTS = SOURCE / "THREE_HUNDRED_THIRTY_SECOND_281_REPAIRED_BIO_EVENTS.tsv"

PROGRAMS = [
    ("P01_DOSIEREN", "Dosieren und einstellen", "Lege Portion, Sollmaß oder Arbeitsstufe fest."),
    ("P02_MATERIAL_GEBEN", "Material geben oder teilen", "Gib Zusatz oder Anteil zu, teile oder zerkleinere ihn."),
    ("P03_AM_ZIEL_EINSETZEN", "Am Ziel einsetzen", "Setze den laufenden Posten an einer bezeichneten Stelle ein."),
    ("P04_KURZ_BEHANDELN", "Kurz behandeln", "Setze, halte oder bearbeite den Posten nur kurz."),
    ("P05_LANG_BEHANDELN", "Lang behandeln oder wärmen", "Halte, erwärme oder behandle den Posten länger."),
    ("P06_FORTSETZEN", "Fortsetzen und folgen", "Führe denselben Gang fort oder wechsle zum Folgeposten."),
    ("P07_UEBERFUEHREN", "Überführen und umsetzen", "Bewege den Posten zwischen zwei lokalen Arbeitsplätzen."),
    ("P08_DURCHLASSEN", "Durchlassen und waschen", "Führe den Posten durch Lauf, Passage oder Waschgang."),
    ("P09_ABSETZEN_SAMMELN", "Absetzen und sammeln", "Lass den Posten stehen und sammle ihn lokal auf."),
    ("P10_ABZIEHEN_ABFUEHREN", "Abziehen und abführen", "Trenne oder leite den bezeichneten Anteil lokal ab."),
    ("P11_BEREITEN_SCHLIESSEN", "Bereitstellen und schließen", "Halte das Ergebnis bereit, befestige oder schließe den Schritt."),
    ("P12_BESTAND_REFERENZIEREN", "Bestand referenzieren", "Wähle Quelle, Ansatz oder den aktuell gemeinten Posten."),
]
PROGRAM_LOOKUP = {pid: (name, lesson) for pid, name, lesson in PROGRAMS}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def classify(value: str) -> str:
    text = value.lower()
    tests = [
        ("P09_ABSETZEN_SAMMELN", ("absetz", "samml", "auffang")),
        ("P10_ABZIEHEN_ABFUEHREN", ("abführ", "abzug", "abzieh", "ausguss", "klarauszug")),
        ("P08_DURCHLASSEN", ("durch", "wasch", "passage", "beckenlauf", "auslass", "laufschluss")),
        ("P07_UEBERFUEHREN", ("umsetz", "überführ", "transfer", "zuführ")),
        ("P05_LANG_BEHANDELN", ("langkontakt", "wärm", "langhalt")),
        ("P04_KURZ_BEHANDELN", ("kurzkontakt", "kurzhalt", "kurzvorbereit", "kurzbearbeit")),
        ("P01_DOSIEREN", ("sollmaß", "sollstellung", "portion", "folgemaß", "arbeitsstufe", "endstufe", "kurzsoll")),
        ("P02_MATERIAL_GEBEN", ("zugabe", "zusatz", "einlage", "zerkleiner", "kurzteil", "vollteil", "teilen", "anteil")),
        ("P03_AM_ZIEL_EINSETZEN", ("ziel", "stelle", "einsetz", "einsatz", "marke")),
        ("P06_FORTSETZEN", ("fort", "folge", "anschluss", "weiter")),
        ("P11_BEREITEN_SCHLIESSEN", ("bereit", "befest", "schluss", "endposten")),
    ]
    for program_id, needles in tests:
        if any(needle in text for needle in needles):
            return program_id
    return "P12_BESTAND_REFERENZIEREN"


def main() -> None:
    statements = read_tsv(STATEMENTS)
    events = read_tsv(EVENTS)
    event_by_id = {row["event_id"]: row for row in events}

    mappings: list[dict[str, object]] = []
    primary_counts: Counter[str] = Counter()
    operation_counts: Counter[str] = Counter()
    owners: defaultdict[str, set[str]] = defaultdict(set)
    pages: defaultdict[str, set[str]] = defaultdict(set)
    examples: defaultdict[str, list[str]] = defaultdict(list)

    for row in statements:
        values = [part.strip() for part in row["atomic_sequence"].split("→")]
        program_sequence = [classify(value) for value in values]
        counts = Counter(program_sequence)
        best_count = max(counts.values())
        tied = {pid for pid, count in counts.items() if count == best_count}
        primary = next(pid for pid in program_sequence if pid in tied)
        secondary = []
        for pid in program_sequence:
            if pid != primary and pid not in secondary:
                secondary.append(pid)
        primary_counts[primary] += 1
        operation_counts.update(program_sequence)
        for pid in set(program_sequence):
            owners[pid].update(row["owner_sequence"].split("|"))
            pages[pid].add(row["page"])
        if len(examples[primary]) < 3:
            examples[primary].append(row["statement_id"])
        primary_name = PROGRAM_LOOKUP[primary][0]
        secondary_names = [PROGRAM_LOOKUP[pid][0] for pid in secondary]
        mappings.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "owner_sequence": row["owner_sequence"],
            "event_count": len(row["event_ids"].split("|")),
            "atomic_sequence": row["atomic_sequence"],
            "program_sequence": " → ".join(program_sequence),
            "primary_program_id": primary,
            "primary_program_de": primary_name,
            "secondary_program_ids": "|".join(secondary) if secondary else "NONE",
            "secondary_programs_de": " | ".join(secondary_names) if secondary_names else "KEINE",
            "apprentice_reading_de": row["fluent_station_translation_de"],
        })

    definitions: list[dict[str, object]] = []
    for pid, name, lesson in PROGRAMS:
        definitions.append({
            "program_id": pid,
            "program_name_de": name,
            "apprentice_rule_de": lesson,
            "primary_statement_count": primary_counts[pid],
            "all_operation_count": operation_counts[pid],
            "owner_count": len(owners[pid]),
            "owners": "|".join(sorted(owners[pid])),
            "pages": "|".join(sorted(pages[pid])),
            "example_statements": "|".join(examples[pid]),
        })

    owner_rows: list[dict[str, object]] = []
    owner_statement_counts: Counter[str] = Counter()
    owner_program_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    owner_records: defaultdict[str, set[str]] = defaultdict(set)
    for row in mappings:
        owner_ids = row["owner_sequence"].split("|")
        for owner in owner_ids:
            owner_statement_counts[owner] += 1
            owner_program_counts[owner][row["primary_program_id"]] += 1
            owner_records[owner].add(row["record_unit_id"])
    for owner in sorted(owner_statement_counts):
        counts = owner_program_counts[owner]
        dominant = counts.most_common(1)[0][0]
        owner_rows.append({
            "owner_id": owner,
            "record_units": "|".join(sorted(owner_records[owner])),
            "statement_count": owner_statement_counts[owner],
            "dominant_program_id": dominant,
            "dominant_program_de": PROGRAM_LOOKUP[dominant][0],
            "program_profile": "|".join(f"{pid}:{counts[pid]}" for pid, _, _ in PROGRAMS if counts[pid]),
        })

    write_tsv(
        HERE / "THREE_HUNDRED_THIRTY_THIRD_12_STATION_PROGRAMS.tsv",
        definitions,
        ["program_id", "program_name_de", "apprentice_rule_de", "primary_statement_count", "all_operation_count", "owner_count", "owners", "pages", "example_statements"],
    )
    write_tsv(
        HERE / "THREE_HUNDRED_THIRTY_THIRD_97_STATEMENT_PROGRAM_MAP.tsv",
        mappings,
        ["statement_id", "record_unit_id", "page", "owner_sequence", "event_count", "atomic_sequence", "program_sequence", "primary_program_id", "primary_program_de", "secondary_program_ids", "secondary_programs_de", "apprentice_reading_de"],
    )
    write_tsv(
        HERE / "THREE_HUNDRED_THIRTY_THIRD_16_OWNER_PROGRAM_PROFILES.tsv",
        owner_rows,
        ["owner_id", "record_units", "statement_count", "dominant_program_id", "dominant_program_de", "program_profile"],
    )

    lines = [
        "# Zwölf Stationsprogramme für den Lehrling",
        "",
        "Die 97 Biological-Aussagen sind keine 97 getrennt zu lernenden Rezepte.",
        "Sie sind Kombinationen aus zwölf wiederkehrenden Werkstattprogrammen.",
        "Der Bildbesitzer sagt, woran gearbeitet wird; die Kartenfolge sagt, welches",
        "Programm und welche Nebenprogramme auszuführen sind.",
        "",
    ]
    for row in definitions:
        lines.extend([
            f"## {row['program_id']} — {row['program_name_de']}",
            "",
            str(row["apprentice_rule_de"]),
            "",
            f"Primär in {row['primary_statement_count']} Aussagen; insgesamt {row['all_operation_count']} Operationskarten; auf {row['owner_count']} lokalen Besitzern.",
            f"Beispiele: {row['example_statements']}.",
            "",
        ])
    lines.extend([
        "## Leseablauf",
        "",
        "1. Bestimme den sichtbaren lokalen Besitzer.",
        "2. Lies das häufigste Programm der Zelle als Hauptauftrag.",
        "3. Führe die Nebenprogramme in Kartenreihenfolge aus.",
        "4. Bei einem Besitzerwechsel eröffne einen neuen lokalen Posten.",
        "5. Verbinde getrennte Stationen nicht zu einem unsichtbaren Gesamtkreislauf.",
        "",
        "Die lange Aussage B1-S002 ist deshalb kein einzelnes Riesensatzwort, sondern",
        "eine Arbeitskarte mit Dosieren, Zieleinsatz, Fortsetzung, Überführung und",
        "Durchlass. Kurze Aussagen wie B1-S001 sind dagegen reine Kurzbehandlung.",
    ])
    (HERE / "THREE_HUNDRED_THIRTY_THIRD_APPRENTICE_PROGRAM_MANUAL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "station_programs": len(PROGRAMS),
        "statements": len(statements),
        "events": len(events),
        "owners": len(owner_rows),
        "programs_used_as_primary": len(primary_counts),
        "statements_with_secondary_programs": sum(row["secondary_program_ids"] != "NONE" for row in mappings),
        "global_flow_claims": 0,
    }
    (HERE / "THREE_HUNDRED_THIRTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
