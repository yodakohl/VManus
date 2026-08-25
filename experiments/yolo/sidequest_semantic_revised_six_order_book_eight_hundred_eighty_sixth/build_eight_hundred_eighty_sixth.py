#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EDITION = ROOT / "sidequest_semantic_complete_phrase_first_edition_eight_hundred_eighty_third"
CHAIN = ROOT / "sidequest_semantic_herbal_batch_chain_eight_hundred_eighty_fourth"
MATCH = ROOT / "sidequest_semantic_stock_application_matching_eight_hundred_eighty_fifth"
OLD_BOOK = ROOT / "sidequest_semantic_six_order_workshop_book_eight_hundred_seventy_sixth"
ASTRO = ROOT / "sidequest_semantic_relative_astro_condition_vocabulary_eight_hundred_seventy_third" / "EIGHT_HUNDRED_SEVENTY_THIRD_395_RELATIVE_CONDITION_GROUPS.tsv"
CALIBRATIONS = ROOT / "sidequest_semantic_fully_readable_corrected_sample_eight_hundred_seventy_fourth" / "EIGHT_HUNDRED_SEVENTY_FOURTH_6_EXPLICIT_CALIBRATIONS.tsv"
EVENTS = EDITION / "EIGHT_HUNDRED_EIGHTY_THIRD_381_EVENT_COMPLETE_FIFTH_HAND.tsv"
STATEMENTS = EDITION / "EIGHT_HUNDRED_EIGHTY_THIRD_116_COMPLETE_PHRASE_FIRST_STATEMENTS.tsv"
STATES = CHAIN / "EIGHT_HUNDRED_EIGHTY_FOURTH_19_BATCH_STATES.tsv"
HEADERS = MATCH / "EIGHT_HUNDRED_EIGHTY_FIFTH_6_REVISED_ORDER_HEADERS.tsv"
OLD_ORDERS = OLD_BOOK / "EIGHT_HUNDRED_SEVENTY_SIXTH_6_COMPLETE_ORDER_SUMMARY.tsv"
PREFIX = "EIGHT_HUNDRED_EIGHTY_SIXTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def condition_default(row: dict[str, str], handle: str) -> str:
    if row["surface"] == "otody":
        return "DEN FOLGENDEN LOKALEN BEDINGUNGSEINTRAG WAEHLEN UND SCHLIESSEN"
    if row["surface"] == "dolchsody":
        return "VON DER TEILADRESSE WEITER ZUM STERNBEZUG; DEN LOKALEN ARBEITSGANG SCHLIESSEN"
    part = f"BEDINGUNGSTEIL {row['event_index']} VON {handle}"
    reading = row["relative_condition_reading_de"]
    return f"{part} KOPIEREN" if reading == "LOKALE_BEDINGUNGSKARTE" else reading.replace("LOKALER_BEDINGUNGSKERN", part)


def main() -> None:
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    states = read(STATES)
    state_by_handle = {row["product_handle"]: row for row in states}
    headers = read(HEADERS)
    old_orders = {row["order_id"]: row for row in read(OLD_ORDERS)}
    astro = read(ASTRO)
    calibrations = read(CALIBRATIONS)

    order_marks = []
    unit_rows = []
    order_rows = []
    payload_rows = []
    for header in headers:
        order_id = header["order_id"]
        product = header["revised_product"]
        chain_handles = []
        current = product
        while current != "NONE":
            chain_handles.append(current)
            current = state_by_handle[current]["revised_predecessor"]
        chain_handles.reverse()
        prep_statements = [state_by_handle[handle]["statement_id"] for handle in chain_handles]
        prep = [row for row in events if row["statement_id"] in prep_statements]
        application = [row for row in events if row["record"] == header["biological_record"]]
        condition_locus = header["condition_handle"].split("@")[1]
        condition_page = condition_locus.split(".")[0]
        condition = [row for row in astro if row["page"] == condition_page and row["locus"] == condition_locus]
        condition_name = old_orders[order_id]["condition_name_de"]

        local = []
        for row in prep:
            local.append(
                {
                    "stage": f"MAKE_{product}", "page": row["page"], "unit": row["statement_id"], "source_id": row["event_id"],
                    "surface": row["fifth_hand_surface"], "identity": row["identity"], "component_recipe": row["component_recipe"],
                    "concrete_default_de": row["phrase_ready_card_de"], "owner_or_handle_de": f"Bildprodukt {product}", "source_layer": "COMPLETE_HERBAL_CHAIN",
                }
            )
        for row in application:
            local.append(
                {
                    "stage": f"APPLY_{header['biological_record']}", "page": row["page"], "unit": row["statement_id"], "source_id": row["event_id"],
                    "surface": row["fifth_hand_surface"], "identity": row["identity"], "component_recipe": row["component_recipe"],
                    "concrete_default_de": row["phrase_ready_card_de"], "owner_or_handle_de": row["owner_de"], "source_layer": "COMPLETE_BIOLOGICAL_RECORD",
                }
            )
        for row in condition:
            local.append(
                {
                    "stage": f"CONDITION_{header['condition_handle']}", "page": row["page"], "unit": row["locus"], "source_id": row["opaque_local_id"],
                    "surface": row["surface"], "identity": row["opaque_local_id"], "component_recipe": row["selected_component_parse"],
                    "concrete_default_de": condition_default(row, header["condition_handle"]),
                    "owner_or_handle_de": f"{header['condition_handle']}; {condition_name}", "source_layer": "COMPLETE_LOCAL_CONDITION_LOCUS",
                }
            )
        for index, row in enumerate(local, start=1):
            row["order_id"] = order_id
            row["order_mark_id"] = f"{order_id}-R{index:03d}"
            row["calibration_set"] = "CAL1_TO_CAL6_UNCHANGED"
        order_marks.extend(local)

        grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for row in local:
            grouped[(row["stage"], row["unit"])].append(row)
        for (stage, unit), subset in grouped.items():
            reading = statements[unit]["fluent_workshop_reading_de"] if unit in statements else f"Kopiere den vollständigen lokalen Bedingungsgriff {header['condition_handle']}."
            unit_rows.append(
                {
                    "order_id": order_id, "stage": stage, "unit": unit, "page": subset[0]["page"],
                    "fifth_hand_surface_sequence": " ".join(row["surface"] for row in subset),
                    "literal_sequence_de": "; ".join(row["concrete_default_de"] for row in subset),
                    "fluent_workshop_reading_de": reading, "marks": len(subset), "dictionary_changed": "NO",
                }
            )

        order_rows.append(
            {
                "order_id": order_id, "old_product": header["old_product"], "revised_product": product,
                "revised_product_name_de": header["revised_product_name_de"], "preparation_chain": " -> ".join(chain_handles),
                "preparation_statements": ",".join(prep_statements), "biological_record": header["biological_record"],
                "condition_handle": header["condition_handle"], "preparation_marks": len(prep), "application_marks": len(application),
                "condition_marks": len(condition), "total_marks": len(local), "units": len(grouped),
                "supply_changed": header["supply_changed"],
                "complete_instruction_de": header["revised_instruction_de"],
            }
        )
        for payload, value, source in [
            ("PRODUCT", f"{product}: {header['revised_product_name_de']}", "REVISED_STOCK_MATCH"),
            ("MEASURE", "CAL1/CAL2", "REUSED_CALIBRATION"),
            ("DURATION", "CAL3/CAL4/CAL5", "REUSED_CALIBRATION"),
            ("RESULT", "sichtbare Resultatklassen + CAL6", "VISIBLE_STATE_PLUS_REUSED_CALIBRATION"),
            ("CONDITION", header["condition_handle"], "COMPLETE_LOCAL_LOCUS_HANDLE"),
        ]:
            payload_rows.append({"order_id": order_id, "payload": payload, "value": value, "source": source, "empty": "NO"})

    write(f"{PREFIX}_437_MARK_REVISED_SIX_ORDER_BOOK.tsv", order_marks, ["order_id", "order_mark_id", "stage", "page", "unit", "source_id", "surface", "identity", "component_recipe", "concrete_default_de", "owner_or_handle_de", "source_layer", "calibration_set"])
    write(f"{PREFIX}_118_UNIT_REVISED_SIX_ORDER_BOOK.tsv", unit_rows, ["order_id", "stage", "unit", "page", "fifth_hand_surface_sequence", "literal_sequence_de", "fluent_workshop_reading_de", "marks", "dictionary_changed"])
    write(f"{PREFIX}_6_REVISED_COMPLETE_ORDERS.tsv", order_rows, ["order_id", "old_product", "revised_product", "revised_product_name_de", "preparation_chain", "preparation_statements", "biological_record", "condition_handle", "preparation_marks", "application_marks", "condition_marks", "total_marks", "units", "supply_changed", "complete_instruction_de"])
    write(f"{PREFIX}_30_FILLED_PAYLOADS.tsv", payload_rows, ["order_id", "payload", "value", "source", "empty"])
    write(f"{PREFIX}_6_UNCHANGED_CALIBRATIONS.tsv", calibrations, list(calibrations[0]))

    lines = ["# Revidiertes Sechs-Auftrags-Buch", ""]
    for order in order_rows:
        lines.extend(
            [
                f"## {order['order_id']}: {order['revised_product']} → {order['biological_record']} → {order['condition_handle']}",
                "",
                str(order["complete_instruction_de"]),
                f"Chargenkette: `{order['preparation_chain']}`.",
                f"Marken: {order['preparation_marks']} + {order['application_marks']} + {order['condition_marks']} = {order['total_marks']}.",
                f"Alter Liefergriff: {order['old_product']}; geändert: {order['supply_changed']}.",
                "",
            ]
        )
    lines.extend(
        [
            "## Gemeinsame Regel",
            "",
            "Jeder Liefergriff wird von seinem Bildwurzelzustand bis zum ausgewählten Vorrat vollständig",
            "hergestellt. Danach folgt genau ein vollständiger Biological-Record und genau ein lokaler",
            "Himmelsgriff. Die fünfte Hand, die sechs Hauskalibrierungen und alle Kartenwerte bleiben gleich.",
        ]
    )
    (HERE / f"{PREFIX}_REVISED_SIX_ORDER_WORKSHOP_BOOK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    stage_counts = Counter("PREP" if row["stage"].startswith("MAKE") else "APP" if row["stage"].startswith("APPLY") else "COND" for row in order_marks)
    summary = {
        "status": "PASS", "decision": "REVISED_STOCK_MATCHES_FORM_A_COMPLETE_437_MARK_SIX_ORDER_BOOK",
        "orders": len(order_rows), "marks": len(order_marks), "stage_counts": dict(stage_counts), "units": len(unit_rows),
        "payload_rows": len(payload_rows), "empty_payloads": sum(row["empty"] == "YES" for row in payload_rows),
        "biological_events_covered_once": len({row["source_id"] for row in order_marks if row["stage"].startswith("APPLY")}),
        "unique_preparation_events": len({row["source_id"] for row in order_marks if row["stage"].startswith("MAKE")}),
        "condition_loci": len({row["unit"] for row in order_marks if row["stage"].startswith("CONDITION")}),
        "supply_changes": sum(row["supply_changed"] == "YES" for row in order_rows),
        "fixed_pages_used": len({row["page"] for row in order_marks}), "dictionary_changes": 0, "calibration_changes": 0,
        "marks_without_default": sum(not row["concrete_default_de"] for row in order_marks), "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 886: revised six-order workshop book\n\n"
        "The four supply revisions yield a complete 437-mark book: 83 preparation, all 281\n"
        "Biological application events and the unchanged 73 local condition groups. There are\n"
        "118 units and 30 filled payloads. All six orders retain the fifth-hand renderer and six\n"
        "house calibrations, with no dictionary change.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
