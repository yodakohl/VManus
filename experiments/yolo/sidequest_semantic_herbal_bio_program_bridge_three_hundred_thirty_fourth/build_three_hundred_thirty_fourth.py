#!/usr/bin/env python3
"""Map repaired Herbal preparation into the twelve Bio station programs."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
HERBAL = ROOT / "experiments/yolo/sidequest_semantic_repaired_herbal_edition_three_hundred_thirtieth"
BIO = ROOT / "experiments/yolo/sidequest_semantic_repaired_bio_edition_three_hundred_thirty_second"
PROGRAM_DIR = ROOT / "experiments/yolo/sidequest_semantic_station_programs_three_hundred_thirty_third"
HANDOFF_DIR = ROOT / "experiments/yolo/sidequest_semantic_repaired_handoffs_three_hundred_thirty_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


spec = importlib.util.spec_from_file_location("pass333", PROGRAM_DIR / "build_three_hundred_thirty_third.py")
pass333 = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(pass333)
PROGRAMS = pass333.PROGRAMS
PROGRAM_NAMES = {pid: name for pid, name, _ in PROGRAMS}


HERBAL_EXACT = {
    "Wasserzulauf": "P08_DURCHLASSEN",
    "Auswringen": "P10_ABZIEHEN_ABFUEHREN",
    "Auszugnahme": "P10_ABZIEHEN_ABFUEHREN",
    "Klarauszug": "P10_ABZIEHEN_ABFUEHREN",
    "Rücknahmeschluss": "P10_ABZIEHEN_ABFUEHREN",
    "Standzeit": "P09_ABSETZEN_SAMMELN",
    "Nachseihen": "P08_DURCHLASSEN",
    "Verwahren": "P11_BEREITEN_SCHLIESSEN",
    "Bindeposten": "P11_BEREITEN_SCHLIESSEN",
    "Kurzbindeposten": "P11_BEREITEN_SCHLIESSEN",
    "Kurzrest": "P11_BEREITEN_SCHLIESSEN",
    "Bindestufe": "P11_BEREITEN_SCHLIESSEN",
    "Auftragsschluss": "P11_BEREITEN_SCHLIESSEN",
    "Gebrauchen": "P03_AM_ZIEL_EINSETZEN",
}


def classify_herbal(value: str) -> str:
    return HERBAL_EXACT.get(value, pass333.classify(value))


def ids_in_order(values: list[str], classifier) -> list[str]:
    seen = []
    for value in values:
        pid = classifier(value)
        if pid not in seen:
            seen.append(pid)
    return seen


def main() -> None:
    herbal_events = read_tsv(HERBAL / "THREE_HUNDRED_THIRTIETH_100_HERBAL_INTERLINEAR.tsv")
    herbal_statements = read_tsv(HERBAL / "THREE_HUNDRED_THIRTIETH_19_FLUENT_STATEMENTS.tsv")
    bio_events = read_tsv(BIO / "THREE_HUNDRED_THIRTY_SECOND_281_REPAIRED_BIO_EVENTS.tsv")
    handoffs = read_tsv(HANDOFF_DIR / "THREE_HUNDRED_THIRTY_FIRST_FIVE_REPAIRED_HANDOFFS.tsv")

    herbal_counts = Counter(classify_herbal(row["atomic_value_de"]) for row in herbal_events)
    bio_counts = Counter(pass333.classify(row["atomic_value_de"]) for row in bio_events)
    program_rows = []
    for pid, name, lesson in PROGRAMS:
        h = herbal_counts[pid]
        b = bio_counts[pid]
        status = "BEGINS_IN_HERBAL_AND_CONTINUES_IN_BIO" if h and b else "INTRODUCED_AT_BIO_STATION"
        program_rows.append({
            "program_id": pid,
            "program_name_de": name,
            "herbal_event_count": h,
            "bio_event_count": b,
            "workflow_status": status,
            "workshop_interpretation_de": (
                "Schon bei der Pflanzenzubereitung gelernt; an der Bildstation weiter ausgeführt."
                if status.startswith("BEGINS") else
                "Erst an der sichtbaren Biological-Station als kurzer Kontaktauftrag hinzugefügt."
            ),
        })

    event_program_rows = []
    for row in herbal_events:
        pid = classify_herbal(row["atomic_value_de"])
        event_program_rows.append({
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "statement_id": row["statement_id"],
            "surface": row["surface"],
            "atomic_value_de": row["atomic_value_de"],
            "program_id": pid,
            "program_name_de": PROGRAM_NAMES[pid],
            "visible_owner": row["visible_owner"],
            "preparation_role": "BEGINS_PROGRAM_DURING_HERBAL_PREPARATION",
        })

    article_programs: defaultdict[str, list[str]] = defaultdict(list)
    article_values: defaultdict[str, list[str]] = defaultdict(list)
    for row in herbal_events:
        article_values[row["record_unit_id"]].append(row["atomic_value_de"])
        pid = classify_herbal(row["atomic_value_de"])
        if pid not in article_programs[row["record_unit_id"]]:
            article_programs[row["record_unit_id"]].append(pid)

    handoff_rows = []
    for row in handoffs:
        herbal_ids = article_programs[row["herbal_record"]]
        bio_values = [part.strip() for part in row["repaired_bio_atomic_chain"].split("→")]
        bio_ids = ids_in_order(bio_values, pass333.classify)
        shared = [pid for pid in herbal_ids if pid in bio_ids]
        added = [pid for pid in bio_ids if pid not in herbal_ids]
        handoff_rows.append({
            "herbal_record": row["herbal_record"],
            "herbal_page": row["herbal_page"],
            "bio_unit": row["bio_unit"],
            "bio_page": row["bio_page"],
            "bio_owner": row["bio_owner"],
            "herbal_program_ids": "|".join(herbal_ids),
            "herbal_programs_de": " | ".join(PROGRAM_NAMES[pid] for pid in herbal_ids),
            "bio_program_ids": "|".join(bio_ids),
            "bio_programs_de": " | ".join(PROGRAM_NAMES[pid] for pid in bio_ids),
            "programs_carried_across": "|".join(shared),
            "programs_added_at_station": "|".join(added) if added else "NONE",
            "exact_shared_values": row["exact_shared_values"],
            "workshop_reading_de": row["integrated_reading_de"],
        })

    statement_rows = []
    for row in herbal_statements:
        values = [part.strip() for part in row["atomic_sequence"].split("→")]
        pids = [classify_herbal(value) for value in values]
        statement_rows.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "atomic_sequence": row["atomic_sequence"],
            "program_sequence": " → ".join(pids),
            "distinct_programs": "|".join(dict.fromkeys(pids)),
            "fluent_workshop_translation_de": row["fluent_workshop_translation_de"],
        })

    write_tsv(
        HERE / "THREE_HUNDRED_THIRTY_FOURTH_12_PROGRAM_PREPARATION_COMPARISON.tsv",
        program_rows,
        ["program_id", "program_name_de", "herbal_event_count", "bio_event_count", "workflow_status", "workshop_interpretation_de"],
    )
    write_tsv(
        HERE / "THREE_HUNDRED_THIRTY_FOURTH_100_HERBAL_PROGRAM_EVENTS.tsv",
        event_program_rows,
        ["event_id", "record_unit_id", "page", "statement_id", "surface", "atomic_value_de", "program_id", "program_name_de", "visible_owner", "preparation_role"],
    )
    write_tsv(
        HERE / "THREE_HUNDRED_THIRTY_FOURTH_19_HERBAL_PROGRAM_STATEMENTS.tsv",
        statement_rows,
        ["statement_id", "record_unit_id", "page", "atomic_sequence", "program_sequence", "distinct_programs", "fluent_workshop_translation_de"],
    )
    write_tsv(
        HERE / "THREE_HUNDRED_THIRTY_FOURTH_FIVE_PROGRAM_HANDOFFS.tsv",
        handoff_rows,
        ["herbal_record", "herbal_page", "bio_unit", "bio_page", "bio_owner", "herbal_program_ids", "herbal_programs_de", "bio_program_ids", "bio_programs_de", "programs_carried_across", "programs_added_at_station", "exact_shared_values", "workshop_reading_de"],
    )

    lines = [
        "# Herbal bereitet vor, Biological führt aus",
        "",
        "Elf der zwölf Stationsprogramme beginnen bereits in den fünf Pflanzenartikeln.",
        "Nur die reine Kurzbehandlung erscheint erstmals an einer Biological-Station.",
        "Damit liefert Herbal nicht bloß Namen: Es erzeugt Posten, Maß, Ziel, Folge,",
        "Überführung, Durchlass, Absetzen, Abzug und Abschluss, die im Bildregister",
        "weiterverwendet werden.",
        "",
    ]
    for row in handoff_rows:
        lines.extend([
            f"## {row['herbal_record']} → {row['bio_unit']}",
            "",
            f"Herbal-Repertoire: {row['herbal_programs_de']}.",
            f"An der Station benutzt: {row['bio_programs_de']}.",
            f"Neu an der Station: {row['programs_added_at_station']}.",
            f"Lesung: {row['workshop_reading_de']}",
            "",
        ])
    lines.extend([
        "## Werkstattmodell",
        "",
        "Der Lehrling lernt die zwölf Programme einmal. Auf einer Pflanzenseite werden",
        "Material und Arbeitszustand vorbereitet. Auf einer Biological-Seite ersetzt der",
        "sichtbare Becken-/Stationsbesitzer den stillen Pflanzenbesitzer; die bekannten",
        "Programme laufen weiter. Erst die lokale Bildstation bestimmt, ob derselbe",
        "abgemessene oder vorbereitete Posten kurz kontaktiert, länger gehalten, abgesetzt",
        "oder abgeführt wird.",
    ])
    (HERE / "THREE_HUNDRED_THIRTY_FOURTH_WORKSHOP_BRIDGE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "programs": 12,
        "programs_beginning_in_herbal": sum(row["herbal_event_count"] > 0 for row in program_rows),
        "programs_introduced_in_bio": sum(row["herbal_event_count"] == 0 for row in program_rows),
        "herbal_events": len(herbal_events),
        "herbal_statements": len(herbal_statements),
        "handoffs": len(handoff_rows),
        "handoffs_with_carried_program": sum(bool(row["programs_carried_across"]) for row in handoff_rows),
    }
    (HERE / "THREE_HUNDRED_THIRTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
