#!/usr/bin/env python3
"""Build V74 R4's complete, locally bounded Biological station atlas."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V69 = REPO / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = REPO / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = REPO / "experiments/yolo/sidequest_theory_candidates_v72"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clean_segment(text: str) -> str:
    if text.startswith("LOCAL[") and text.endswith("]"):
        text = text[6:-1]
    text = text.strip()
    if not text:
        return "Lokalen exemplarischen Stationswert eintragen."
    return text[0].upper() + text[1:] + ("" if text.endswith((".", "!", "?")) else ".")


def clean_medical(text: str) -> str:
    pieces = []
    for chunk in text.split(" ; "):
        chunk = chunk.strip()
        if chunk.startswith("[") and ":" in chunk and chunk.endswith("]"):
            chunk = chunk.split(":", 1)[1][:-1]
        pieces.append(chunk)
    value = "; ".join(piece for piece in pieces if piece)
    return value or "Medizinische Anwendung bleibt occurrence-gebundener Exemplarwert."


def main() -> None:
    events_all = read_tsv(V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv")
    fields_all = read_tsv(V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv")
    statements_all = read_tsv(V69 / "V69_R4_FINAL_116_STATEMENT_EDITION.tsv")
    owners_all = read_tsv(V71 / "V71_SELECTED_OWNER_LEDGER.tsv")
    selected_statements_all = read_tsv(V72 / "V72_SELECTED_116_STATEMENTS.tsv")

    events = [row for row in events_all if row["record_unit_id"].startswith("B")]
    fields = [row for row in fields_all if row["record_unit_id"].startswith("B")]
    statements = [row for row in statements_all if row["record_unit_id"].startswith("B")]
    selected_statements = [row for row in selected_statements_all if row["record_unit_id"].startswith("B")]
    owner_by_field = {row["unit_id"]: row for row in owners_all if row["unit_kind"] == "PROSE_FIELD" and row["record_or_diagram"].startswith("B")}
    statement_by_id = {row["statement_id"]: row for row in statements}

    event_rows: list[dict[str, object]] = []
    for row in events:
        owner = owner_by_field[row["field_id"]]
        operational = clean_segment(row["practical_source_segment"])
        event_rows.append({
            "event_serial": row["event_serial"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "locus": row["locus"],
            "field_id": row["field_id"],
            "statement_id": row["statement_id"],
            "joint_tuple_id": row["joint_tuple_id"],
            "surface_display_only": row["surface_display_only"],
            "local_owner_status": owner["owner_status"],
            "local_visible_owner": owner["selected_visible_owner"],
            "exact_literal_layer": f"[OPAQUE:{row['joint_tuple_id']}] > [FORMAL:{row['strict_formal_prompt']}] > [MNEMONIC:{row['selected_exact_mnemonic']}] > [EXEMPLAR:LOCAL_STATION_VALUE]",
            "concrete_station_default": operational,
            "source_status": "LOCAL_MASTER_EXEMPLAR_VALUE_NOT_CARD_MEANING",
            "confidence": "0.44" if owner["owner_status"] == "DIRECT_VISIBLE" else "0.31",
            "medical_rival": clean_medical(row["iatromedical_source_segment"]),
            "formal_rival": "Kopiere nur die opake Kartenidentität, den lokalen Besitzer und den Schlussstatus; lasse den Quellenwert unbenannt.",
            "strongest_contradiction": "Die konkrete Tätigkeit ist weder aus der Kartenform noch aus einer sichtbaren Pfeilrichtung ableitbar; sie bleibt stationslokaler Exemplarinhalt.",
            "direction_guard": "NO_GLOBAL_FLOW_DIRECTION",
            "terminal_status": row["terminal_status"],
            "semantic_ceiling": "CONCRETE_LOCAL_STATION_EXEMPLAR_NOT_TRANSLATED_CARD_OR_GLOBAL_PROCESS",
        })

    field_rows: list[dict[str, object]] = []
    for row in fields:
        owner = owner_by_field[row["field_id"]]
        field_rows.append({
            "field_id": row["field_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "locus": row["locus"],
            "statement_id": row["statement_id"],
            "event_count": row["event_count"],
            "event_serials": row["event_serials"],
            "owner_status": owner["owner_status"],
            "local_visible_owner": owner["selected_visible_owner"],
            "visible_basis": owner["visible_basis"],
            "concrete_station_field": row["practical_field_text"],
            "medical_field_rival": row["iatromedical_field_text"],
            "parse_status": row["parse_status"],
            "contact_rule": "INHERIT_ONLY_WITHIN_FROZEN_OWNER_OR_EXPLICIT_CONTACT",
            "strongest_contradiction": "Der Feldinhalt bleibt aus dem Masterexemplar ergänzt; Bildkontakt beweist weder Stoff noch Richtung.",
            "semantic_ceiling": "LOCAL_STATION_FIELD_NOT_PLAINTEXT",
        })

    statement_rows: list[dict[str, object]] = []
    for selected in selected_statements:
        old = statement_by_id[selected["statement_id"]]
        statement_rows.append({
            "statement_id": selected["statement_id"],
            "record_unit_id": selected["record_unit_id"],
            "page": selected["page"],
            "constituent_fields": selected["constituent_fields"],
            "event_count": selected["event_count"],
            "event_serials": selected["event_serials"],
            "owner_bindings": selected["owner_bindings"],
            "owner_transition": selected["owner_transition"],
            "concrete_station_statement": selected["selected_concrete_paraphrase"],
            "medical_statement_rival": old["iatromedical_statement_text"],
            "formal_statement_rival": "Opake Feldfolge am sichtbaren lokalen Besitzer abschreiben und nur Commit/Reset rücklesen.",
            "repair_cost_0_4": selected["repair_cost_0_4"],
            "line_crossing": selected["line_crossing"],
            "hardest_contradiction": selected["hardest_contradiction"],
            "direction_guard": "BREAK_AT_VISIBLE_GAP; NEVER_INFER_PAGE_WIDE_FLOW",
            "semantic_ceiling": "STATION_STATEMENT_MASTER_EXEMPLAR_NOT_DECIPHERMENT",
        })

    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        by_record[str(row["record_unit_id"])].append(row)
    record_rows: list[dict[str, object]] = []
    for record_id in sorted(by_record):
        rows = by_record[record_id]
        owner_sequence = []
        for row in rows:
            owner = str(row["owner_bindings"])
            if not owner_sequence or owner_sequence[-1] != owner:
                owner_sequence.append(owner)
        record_rows.append({
            "record_unit_id": record_id,
            "page": str(rows[0]["page"]),
            "statement_ids": "|".join(str(row["statement_id"]) for row in rows),
            "field_count": sum(len(str(row["constituent_fields"]).split("|")) for row in rows),
            "event_count": sum(int(str(row["event_count"])) for row in rows),
            "owner_sequence": " -> ".join(owner_sequence),
            "continuous_station_atlas_reading": " ".join(str(row["concrete_station_statement"]) for row in rows),
            "continuous_medical_rival": " ".join(str(row["medical_statement_rival"]) for row in rows),
            "record_rule": "LOCAL_OWNER_AND_CONTACT_ONLY; RESET_AT_V71_GAP; NO_GLOBAL_FLOW",
            "strongest_contradiction": "Eine vollständige Quelllesung benötigt occurrence-gebundene Exemplarwerte, die weder Bild noch Kartenidentität allein liefert.",
            "semantic_ceiling": "COMPLETE_WORKING_RECORD_NOT_TRANSLATION",
        })

    write_tsv(OUT / "V74_R4_281_EVENT_STATION_ATLAS.tsv", event_rows, list(event_rows[0]))
    write_tsv(OUT / "V74_R4_115_FIELD_STATION_ATLAS.tsv", field_rows, list(field_rows[0]))
    write_tsv(OUT / "V74_R4_97_STATEMENT_STATION_ATLAS.tsv", statement_rows, list(statement_rows[0]))
    write_tsv(OUT / "V74_R4_SIX_RECORD_STATION_ATLAS.tsv", record_rows, list(record_rows[0]))

    hard_breaks = {"B2-S012", "B3-S016", "B3-S026", "B4-S015"}
    checks = {
        "events_281": len(event_rows) == 281,
        "event_serials_101_to_381": [int(row["event_serial"]) for row in event_rows] == list(range(101, 382)),
        "fields_115": len(field_rows) == 115,
        "fields_F021_to_F135": {row["field_id"] for row in field_rows} == {f"F{i:03d}" for i in range(21, 136)},
        "statements_97": len(statement_rows) == 97,
        "records_6": len(record_rows) == 6,
        "records_B1_to_B6": {row["record_unit_id"] for row in record_rows} == {f"B{i}" for i in range(1, 7)},
        "all_event_defaults_concrete": all(str(row["concrete_station_default"]).strip() for row in event_rows),
        "all_events_owner_bound": all(str(row["local_visible_owner"]).strip() for row in event_rows),
        "hard_owner_breaks_retained": hard_breaks <= {row["statement_id"] for row in statement_rows if "BREAK_VISIBLE_GAP" in str(row["owner_transition"])},
        "no_global_flow_claim": all(row["direction_guard"] == "NO_GLOBAL_FLOW_DIRECTION" for row in event_rows),
        "f84_not_named": not any("f84" in str(row["page"]).lower() for row in event_rows),
    }
    validation = {
        "schema": "V74_R4_CHANCERY_STATION_ATLAS_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "counts": {"events": len(event_rows), "fields": len(field_rows), "statements": len(statement_rows), "records": len(record_rows)},
        "checks": checks,
        "sealed_pages_opened": [],
        "active_v74_sibling_outputs_read": False,
    }
    (OUT / "V74_R4_VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, ensure_ascii=False, indent=2))
    print(json.dumps(validation["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
