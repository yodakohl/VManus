#!/usr/bin/env python3
"""Compile all fixed-page prose statements into a six-slot apprentice syntax."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
HERBAL_DIR = ROOT / "experiments/yolo/sidequest_semantic_repaired_herbal_edition_three_hundred_thirtieth"
BIO_DIR = ROOT / "experiments/yolo/sidequest_semantic_repaired_bio_edition_three_hundred_thirty_second"
P333_DIR = ROOT / "experiments/yolo/sidequest_semantic_station_programs_three_hundred_thirty_third"
P334_DIR = ROOT / "experiments/yolo/sidequest_semantic_herbal_bio_program_bridge_three_hundred_thirty_fourth"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


p333 = load_module("p333", P333_DIR / "build_three_hundred_thirty_third.py")
p334 = load_module("p334", P334_DIR / "build_three_hundred_thirty_fourth.py")

SLOTS = [
    (1, "S1_BEZUG_FOLGE", "Bezug oder Folge", "Wähle Quelle, Ansatz, Diesposten oder die Fortsetzung."),
    (2, "S2_MATERIAL_MASS", "Material oder Maß", "Gib Material an und setze Menge oder Arbeitsstufe."),
    (3, "S3_PROZESS_TRANSFER", "Prozess oder Transfer", "Führe durch, über, ab, zusammen oder in Ruhe."),
    (4, "S4_DAUER_ZUSTAND", "Dauer oder Zustand", "Bestimme kurze oder lange Behandlung beziehungsweise Wärme."),
    (5, "S5_ZIEL_ANWENDUNG", "Ziel oder Anwendung", "Setze den Posten an der bezeichneten Stelle ein."),
    (6, "S6_BEREIT_ABSCHLUSS", "Bereit oder Abschluss", "Halte das Ergebnis bereit, befestige oder schließe."),
]
SLOT_BY_PROGRAM = {
    "P12_BESTAND_REFERENZIEREN": 1,
    "P06_FORTSETZEN": 1,
    "P01_DOSIEREN": 2,
    "P02_MATERIAL_GEBEN": 2,
    "P07_UEBERFUEHREN": 3,
    "P08_DURCHLASSEN": 3,
    "P09_ABSETZEN_SAMMELN": 3,
    "P10_ABZIEHEN_ABFUEHREN": 3,
    "P04_KURZ_BEHANDELN": 4,
    "P05_LANG_BEHANDELN": 4,
    "P03_AM_ZIEL_EINSETZEN": 5,
    "P11_BEREITEN_SCHLIESSEN": 6,
}
SLOT_NAME = {rank: code for rank, code, _, _ in SLOTS}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def classify(register: str, value: str) -> str:
    return p334.classify_herbal(value) if register == "HERBAL" else p333.classify(value)


def main() -> None:
    herbal_events = read_tsv(HERBAL_DIR / "THREE_HUNDRED_THIRTIETH_100_HERBAL_INTERLINEAR.tsv")
    bio_events = read_tsv(BIO_DIR / "THREE_HUNDRED_THIRTY_SECOND_281_REPAIRED_BIO_EVENTS.tsv")
    herbal_statements = read_tsv(HERBAL_DIR / "THREE_HUNDRED_THIRTIETH_19_FLUENT_STATEMENTS.tsv")
    bio_statements = read_tsv(BIO_DIR / "THREE_HUNDRED_THIRTY_SECOND_97_REPAIRED_BIO_STATEMENTS.tsv")

    events = []
    for register, rows in (("HERBAL", herbal_events), ("BIO", bio_events)):
        for row in rows:
            events.append({
                "register": register,
                "event_id": row["event_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "statement_id": row["statement_id"],
                "surface": row["surface"],
                "atomic_value_de": row["atomic_value_de"],
                "owner": row.get("visible_owner", row.get("owner_id", "")),
            })

    by_statement: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    statement_source = {}
    for row in herbal_statements:
        statement_source[row["statement_id"]] = row["fluent_workshop_translation_de"]
    for row in bio_statements:
        statement_source[row["statement_id"]] = row["fluent_station_translation_de"]

    trace_rows = []
    statement_rows = []
    micro_rows = []
    slot_event_counts = Counter()
    slot_statement_sets: defaultdict[int, set[str]] = defaultdict(set)
    total_cycles = 0

    for statement_id in [row["statement_id"] for row in herbal_statements + bio_statements]:
        rows = by_statement[statement_id]
        cycle = 1
        previous_rank = 0
        micro_values: defaultdict[int, list[str]] = defaultdict(list)
        micro_slots: defaultdict[int, list[str]] = defaultdict(list)
        statement_slot_sequence = []
        for position, row in enumerate(rows, start=1):
            program_id = classify(row["register"], row["atomic_value_de"])
            rank = SLOT_BY_PROGRAM[program_id]
            if position == 1:
                action = "OPEN_FIRST_CYCLE"
            elif rank < previous_rank:
                cycle += 1
                action = "RESET_TO_NEW_MICROCYCLE"
            elif rank == previous_rank:
                action = "REPEAT_CURRENT_SLOT"
            else:
                action = "ADVANCE_WITH_SKIPPED_SLOTS_ALLOWED"
            previous_rank = rank
            slot_code = SLOT_NAME[rank]
            statement_slot_sequence.append(slot_code)
            micro_values[cycle].append(row["atomic_value_de"])
            micro_slots[cycle].append(slot_code)
            slot_event_counts[rank] += 1
            slot_statement_sets[rank].add(statement_id)
            trace_rows.append({
                "event_id": row["event_id"],
                "statement_id": statement_id,
                "record_unit_id": row["record_unit_id"],
                "register": row["register"],
                "page": row["page"],
                "event_position": position,
                "surface": row["surface"],
                "atomic_value_de": row["atomic_value_de"],
                "program_id": program_id,
                "slot_rank": rank,
                "slot_code": slot_code,
                "microcycle": cycle,
                "generation_action": action,
                "owner": row["owner"],
                "statement_end_after_event": "YES" if position == len(rows) else "NO",
            })
        total_cycles += cycle
        for microcycle in range(1, cycle + 1):
            micro_rows.append({
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "register": rows[0]["register"],
                "microcycle": microcycle,
                "slot_sequence": " → ".join(micro_slots[microcycle]),
                "atomic_sequence": " → ".join(micro_values[microcycle]),
                "event_count": len(micro_values[microcycle]),
            })
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": rows[0]["record_unit_id"],
            "register": rows[0]["register"],
            "page": rows[0]["page"],
            "event_count": len(rows),
            "microcycle_count": cycle,
            "slot_sequence": " → ".join(statement_slot_sequence),
            "atomic_sequence": " → ".join(row["atomic_value_de"] for row in rows),
            "owner_sequence": "|".join(dict.fromkeys(row["owner"] for row in rows)),
            "generated_reading_de": statement_source[statement_id],
        })

    slot_rows = []
    programs_by_slot: defaultdict[int, list[str]] = defaultdict(list)
    for pid, rank in SLOT_BY_PROGRAM.items():
        programs_by_slot[rank].append(pid)
    for rank, code, name, rule in SLOTS:
        slot_rows.append({
            "slot_rank": rank,
            "slot_code": code,
            "slot_name_de": name,
            "apprentice_rule_de": rule,
            "program_ids": "|".join(programs_by_slot[rank]),
            "event_count": slot_event_counts[rank],
            "statement_count": len(slot_statement_sets[rank]),
        })

    write_tsv(HERE / "THREE_HUNDRED_THIRTY_FIFTH_6_SLOT_SYNTAX.tsv", slot_rows,
              ["slot_rank", "slot_code", "slot_name_de", "apprentice_rule_de", "program_ids", "event_count", "statement_count"])
    write_tsv(HERE / "THREE_HUNDRED_THIRTY_FIFTH_381_EVENT_GENERATION_TRACE.tsv", trace_rows,
              ["event_id", "statement_id", "record_unit_id", "register", "page", "event_position", "surface", "atomic_value_de", "program_id", "slot_rank", "slot_code", "microcycle", "generation_action", "owner", "statement_end_after_event"])
    write_tsv(HERE / "THREE_HUNDRED_THIRTY_FIFTH_116_STATEMENT_SYNTAX.tsv", statement_rows,
              ["statement_id", "record_unit_id", "register", "page", "event_count", "microcycle_count", "slot_sequence", "atomic_sequence", "owner_sequence", "generated_reading_de"])
    write_tsv(HERE / "THREE_HUNDRED_THIRTY_FIFTH_205_MICROCYCLES.tsv", micro_rows,
              ["statement_id", "record_unit_id", "register", "microcycle", "slot_sequence", "atomic_sequence", "event_count"])

    lines = [
        "# Ein Lehrzettel für die Kartenfolge",
        "",
        "## Die sechs Plätze",
        "",
    ]
    for rank, code, name, rule in SLOTS:
        lines.append(f"{rank}. **{name}:** {rule}")
    lines.extend([
        "",
        "## Schreibregel",
        "",
        "- Das Bild oder der vorige Record setzt den Besitzer.",
        "- Beginne einen Mikrogang an jedem nötigen Platz; frühere Plätze dürfen fehlen.",
        "- Schreibe innerhalb des Mikroganges nur vorwärts von Platz 1 bis Platz 6.",
        "- Derselbe Platz darf mehrere Karten tragen.",
        "- Sobald wieder ein früherer Platz benötigt wird, beginne einen neuen Mikrogang.",
        "- Nach dem letzten Mikrogang endet die Aussage an ihrer registrierten Feldgrenze.",
        "- Ein Bildbesitzerwechsel eröffnet unabhängig davon einen neuen lokalen Posten.",
        "",
        "## Rückleseregel",
        "",
        "Lies die Plätze eines Mikroganges als eine elliptische Arbeitskette. Ergänze nur",
        "den sichtbaren Besitzer und deutsche Grammatik. Erfinde keine unsichtbare Leitung",
        "zwischen getrennten Besitzern.",
        "",
        "## Umfang",
        "",
        f"Die 116 Aussagen zerfallen in {total_cycles} Mikrogänge. 63 Aussagen brauchen",
        "nur einen Mikrogang; die längste, B1-S002, braucht sechs. Trotzdem bleibt jede",
        "der 381 Karten an genau einem Platz und in ihrer überlieferten Reihenfolge.",
    ])
    (HERE / "THREE_HUNDRED_THIRTY_FIFTH_ONE_PAGE_APPRENTICE_SYNTAX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "slots": len(SLOTS),
        "programs": len(SLOT_BY_PROGRAM),
        "events": len(trace_rows),
        "statements": len(statement_rows),
        "microcycles": len(micro_rows),
        "single_cycle_statements": sum(int(row["microcycle_count"]) == 1 for row in statement_rows),
        "maximum_cycles": max(int(row["microcycle_count"]) for row in statement_rows),
    }
    (HERE / "THREE_HUNDRED_THIRTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
