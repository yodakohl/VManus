#!/usr/bin/env python3
"""Build central V74: R2 content under R3 geometry/contact constraints."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def copy_bytes(source: str, target: str) -> None:
    (ROOT / target).write_bytes((ROOT / source).read_bytes())


def main() -> None:
    copies = {
        "V74_R2_281_BIO_EVENTS.tsv": "V74_SELECTED_281_EVENT_INTERLINEAR.tsv",
        "V74_R2_115_BIO_FIELDS.tsv": "V74_SELECTED_115_FIELD_EDITION.tsv",
        "V74_R2_97_BIO_STATEMENTS.tsv": "V74_SELECTED_97_STATEMENT_EDITION.tsv",
        "V74_R2_SIX_CONTINUOUS_RECORDS.tsv": "V74_SELECTED_SIX_RECORD_EDITION.tsv",
        "V74_R3_STATION_COMPARISON.tsv": "V74_SELECTED_STATION_COMPARISON.tsv",
        "V74_R3_LOCAL_PROCESS_GRAPHS.tsv": "V74_SELECTED_LOCAL_PROCESS_GRAPHS.tsv",
    }
    for source, target in copies.items():
        copy_bytes(source, target)

    events = read_tsv(copies["V74_R2_281_BIO_EVENTS.tsv"])
    fields = read_tsv(copies["V74_R2_115_BIO_FIELDS.tsv"])
    statements = read_tsv(copies["V74_R2_97_BIO_STATEMENTS.tsv"])
    records = read_tsv(copies["V74_R2_SIX_CONTINUOUS_RECORDS.tsv"])
    stations = read_tsv(copies["V74_R3_STATION_COMPARISON.tsv"])
    graph = read_tsv(copies["V74_R3_LOCAL_PROCESS_GRAPHS.tsv"])

    role_files = {
        "R1": ["V74_R1_281_EVENT_INTERLINEAR.tsv", "V74_R1_115_FIELD_EDITION.tsv", "V74_R1_97_STATEMENT_EDITION.tsv", "V74_R1_SIX_RECORD_CONTINUOUS_EDITION.md", "V74_R1_STATION_ATLAS_REPORT.md", "V74_R1_VALIDATION.json"],
        "R2": ["V74_R2_281_BIO_EVENTS.tsv", "V74_R2_115_BIO_FIELDS.tsv", "V74_R2_97_BIO_STATEMENTS.tsv", "V74_R2_SIX_CONTINUOUS_RECORDS.tsv", "V74_R2_UNSUPPORTED_NOUNS.tsv", "V74_R2_BIOLOGICAL_STATION_ATLAS_REPORT.md", "V74_R2_VALIDATION.json"],
        "R3": ["V74_R3_281_EVENT_INTERLINEAR.tsv", "V74_R3_115_FIELD_EDITION.tsv", "V74_R3_97_STATEMENT_EDITION.tsv", "V74_R3_SIX_RECORD_EDITION.tsv", "V74_R3_STATION_COMPARISON.tsv", "V74_R3_LOCAL_PROCESS_GRAPHS.tsv", "V74_R3_TECHNICAL_REPORT.md", "V74_R3_VALIDATION.json"],
        "R4": ["V74_R4_281_EVENT_STATION_ATLAS.tsv", "V74_R4_115_FIELD_STATION_ATLAS.tsv", "V74_R4_97_STATEMENT_STATION_ATLAS.tsv", "V74_R4_SIX_RECORD_STATION_ATLAS.tsv", "V74_R4_CHANCERY_STATION_ATLAS_REPORT.md", "V74_R4_VALIDATION.json"],
    }
    role_bindings = {role: {name: sha256(ROOT / name) for name in names} for role, names in role_files.items()}

    supported = sum(row["v69_source_status"] != "UNKNOWN_EXEMPLAR_WHOLE_CARD" for row in events)
    unresolved = sum(row["owner_status"] == "UNRESOLVED" for row in events)
    hard_breaks = {"B2-S012", "B3-S016", "B3-S026", "B4-S015"}
    statement_ids = {row["statement_id"] for row in statements}
    checks = {
        "events_281": len(events) == 281,
        "events_101_to_381": [int(row["event_serial"]) for row in events] == list(range(101, 382)),
        "fields_115": len(fields) == 115,
        "statements_97": len(statements) == 97,
        "records_6": len(records) == 6,
        "records_B1_to_B6": {row["record_unit_id"] for row in records} == {f"B{i}" for i in range(1, 7)},
        "stations_16": len(stations) == 16,
        "graph_edges_18": len(graph) == 18,
        "graph_never_directed": {row["directedness"] for row in graph} <= {"UNDIRECTED", "NONE"},
        "supported_90": supported == 90,
        "exemplar_191": len(events) - supported == 191,
        "unresolved_events_32": unresolved == 32,
        "hard_break_statements_present": hard_breaks <= statement_ids,
        "all_event_meanings_concrete": all(row["concrete_german_meaning_in_context"].strip() for row in events),
        "all_event_carry_local": all("NEVER_CARRY" in row["carry_policy"] for row in events),
        "all_role_validations_pass": all(json.loads((ROOT / f"V74_{role}_VALIDATION.json").read_text(encoding="utf-8"))["status"] == "PASS" for role in ("R1", "R2", "R3", "R4")),
        "f84_not_named": not any("f84" in row["page"].lower() for row in events),
    }
    payload = {
        "schema": "V74_FOUR_ROLE_SELECTION_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "selection": {
            "content_edition": "R2_LOCAL_BALNEOLOGICAL_THERAPEUTIC_ATLAS",
            "geometry_and_contact_guard": "R3_LOCAL_TECHNICAL_STATION_GRAPH",
            "strongest_rival": "BATHHOUSE_APPARATUS_OPERATION_OR_FORMAL_ICONOGRAPHIC_ATLAS",
            "global_flow": "NOT_INFERRED",
        },
        "counts": {
            "events": len(events), "fields": len(fields), "statements": len(statements), "records": len(records),
            "stations": len(stations), "graph_edges": len(graph), "supported_or_formal_events": supported,
            "exemplar_only_events": len(events) - supported, "unresolved_events": unresolved,
        },
        "checks": checks,
        "role_bindings": role_bindings,
        "selected_bindings": {target: sha256(ROOT / target) for target in copies.values()},
        "sealed_pages_opened": [],
    }
    (ROOT / "V74_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if payload["status"] != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(json.dumps(payload["counts"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
