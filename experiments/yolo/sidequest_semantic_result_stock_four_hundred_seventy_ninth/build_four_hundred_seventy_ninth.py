#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P478 = ROOT / "experiments/yolo/sidequest_semantic_whole_card_slots_four_hundred_seventy_eighth"
P475 = ROOT / "experiments/yolo/sidequest_semantic_readable_compression_four_hundred_seventy_fifth"
TARGET = "b5df9126607030b95175"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dictionary = read(P478 / "FOUR_HUNDRED_SEVENTY_EIGHTH_173_SLOT_REVISED_DICTIONARY.tsv")
    events = read(P478 / "FOUR_HUNDRED_SEVENTY_EIGHTH_381_SLOT_REVISED_EVENTS.tsv")
    astro = read(P475 / "FOUR_HUNDRED_SEVENTY_FIFTH_142_READABLE_ASTRO_LOCI.tsv")
    target_rows = [row for row in events if row["joint_tuple_id"] == TARGET]

    traces = []
    for target in target_rows:
        i = events.index(target)
        same_record = lambda row: row["record_unit_id"] == target["record_unit_id"]
        previous = events[i-1] if i else None
        following = [row for row in events[i+1:i+4] if same_record(row)]
        traces.append({
            "event_id": target["event_id"],
            "record_unit_id": target["record_unit_id"],
            "page": target["page"],
            "statement_id": target["statement_id"],
            "field_id": target["field_id"],
            "owner_code": target["owner_code"],
            "owner_reset_here": target["owner_reset"],
            "source_stock_before_de": target["short_active_before_de"],
            "previous_event_id": previous["event_id"] if previous and same_record(previous) else "NONE",
            "previous_operation_de": previous["pass478_event_de"] if previous and same_record(previous) else "NONE",
            "following_event_ids": "|".join(row["event_id"] for row in following),
            "following_operations_de": " | ".join(row["pass478_event_de"].replace("ERGEBNISPOSTEN", "EMPFANGSBESTAND").replace("Ergebnisbestand", "Empfangsbestand") for row in following),
            "next_owner_reset_within_three": "YES" if any(row["owner_reset"] == "YES" for row in following) else "NO",
            "selected_value_de": "EMPFANGSBESTAND",
            "reading_de": "Der an dieser Station angekommene und nun weiter verfügbare Bestand.",
        })
    write("FOUR_HUNDRED_SEVENTY_NINTH_FOUR_RECEIVED_STOCK_TRACES.tsv", traces)

    candidates = [
        {"candidate": "EMPFANGSBESTAND", "fits_h3_e044": "YES", "fits_b2_e197": "YES", "fits_b2_e203": "YES", "fits_b4_e353": "YES", "failure": "NONE", "decision": "SELECT"},
        {"candidate": "ERGEBNISPOSTEN", "fits_h3_e044": "YES", "fits_b2_e197": "YES", "fits_b2_e203": "STRAIN", "fits_b4_e353": "STRAIN", "failure": "too abstract at owner reset and portion-addition station", "decision": "REPLACE"},
        {"candidate": "ABFLUSS", "fits_h3_e044": "STRAIN", "fits_b2_e197": "YES", "fits_b2_e203": "NO", "fits_b4_e353": "NO", "failure": "cannot open the lower pool or follow an added portion", "decision": "REJECT"},
        {"candidate": "PRUEFERGEBNIS", "fits_h3_e044": "STRAIN", "fits_b2_e197": "STRAIN", "fits_b2_e203": "NO", "fits_b4_e353": "NO", "failure": "successors consume/measure/hold a stock rather than merely report a check", "decision": "REJECT"},
    ]
    write("FOUR_HUNDRED_SEVENTY_NINTH_VALUE_COMPETITION.tsv", candidates)

    revised_dictionary = []
    for row in dictionary:
        out = dict(row)
        if row["joint_tuple_id"] == TARGET:
            out["pass479_previous_value_de"] = row["template_slot_value_de"]
            out["pass479_value_de"] = "EMPFANGSBESTAND"
            out["pass479_revision"] = "YES"
        else:
            out["pass479_previous_value_de"] = row["template_slot_value_de"]
            out["pass479_value_de"] = row["template_slot_value_de"]
            out["pass479_revision"] = "NO"
        revised_dictionary.append(out)
    write("FOUR_HUNDRED_SEVENTY_NINTH_173_RECEIVED_STOCK_DICTIONARY.tsv", revised_dictionary)

    revised_events = []
    for row in events:
        out = dict(row)
        for field in ("pass478_event_de", "short_active_before_de", "short_active_after_de", "referent_resolved_value_de", "active_before_de", "active_after_de"):
            if field in out:
                out[field] = out[field].replace("ERGEBNISPOSTEN", "EMPFANGSBESTAND").replace("Ergebnisbestand", "Empfangsbestand")
        out["pass479_event_de"] = out["pass478_event_de"]
        out["pass479_target_card"] = "YES" if row["joint_tuple_id"] == TARGET else "NO"
        revised_events.append(out)
    write("FOUR_HUNDRED_SEVENTY_NINTH_381_RECEIVED_STOCK_EVENTS.tsv", revised_events)

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in revised_events:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for sid in dict.fromkeys(row["statement_id"] for row in revised_events):
        rows = by_statement[sid]
        statement_rows.append({
            "statement_id": sid,
            "register": rows[0]["register"],
            "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"],
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "contains_received_stock_card": "YES" if any(row["joint_tuple_id"] == TARGET for row in rows) else "NO",
            "received_stock_statement_de": "; ".join(row["pass479_event_de"] for row in rows) + ".",
        })
    write("FOUR_HUNDRED_SEVENTY_NINTH_116_RECEIVED_STOCK_STATEMENTS.tsv", statement_rows)

    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in statement_rows if row["record_unit_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": rows[0]["register"],
            "statements_or_loci": len(rows),
            "groups": sum(int(row["events"]) for row in rows),
            "continuous_received_stock_de": " ".join(row["received_stock_statement_de"] for row in rows),
        })
    for unit in ("A1", "A2", "A3"):
        rows = [row for row in astro if row["diagram_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": "ASTRO",
            "statements_or_loci": len(rows),
            "groups": sum(int(row["groups"]) for row in rows),
            "continuous_received_stock_de": " ".join(row["readable_locus_de"] for row in rows),
        })
    write("FOUR_HUNDRED_SEVENTY_NINTH_14_RECEIVED_STOCK_UNIT_EDITIONS.tsv", units)

    md = ["# Received-stock ten-page edition", ""]
    for unit in units:
        md.extend([f"## {unit['unit_id']} — {unit['page']}", "", unit["continuous_received_stock_de"], ""])
    (HERE / "FOUR_HUNDRED_SEVENTY_NINTH_RECEIVED_STOCK_TEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    summary = {
        "status": "PASS",
        "target_card_events": len(target_rows),
        "target_records": len({row["record_unit_id"] for row in target_rows}),
        "target_registers": len({row["register"] for row in target_rows}),
        "selected_value": "EMPFANGSBESTAND",
        "dictionary_cards": len(revised_dictionary),
        "events": len(revised_events),
        "statements": len(statement_rows),
        "affected_statements": sum(row["contains_received_stock_card"] == "YES" for row in statement_rows),
        "units": len(units),
        "groups": sum(int(row["groups"]) for row in units),
    }
    (HERE / "FOUR_HUNDRED_SEVENTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
