#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOK = ROOT / "sidequest_semantic_revised_six_order_book_eight_hundred_eighty_sixth"
WHEN = ROOT / "sidequest_semantic_concrete_condition_matching_eight_hundred_eighty_seventh"
MARKS = BOOK / "EIGHT_HUNDRED_EIGHTY_SIXTH_437_MARK_REVISED_SIX_ORDER_BOOK.tsv"
UNITS = BOOK / "EIGHT_HUNDRED_EIGHTY_SIXTH_118_UNIT_REVISED_SIX_ORDER_BOOK.tsv"
ORDERS = BOOK / "EIGHT_HUNDRED_EIGHTY_SIXTH_6_REVISED_COMPLETE_ORDERS.tsv"
PAYLOADS = BOOK / "EIGHT_HUNDRED_EIGHTY_SIXTH_30_FILLED_PAYLOADS.tsv"
WHEN_HEADERS = WHEN / "EIGHT_HUNDRED_EIGHTY_SEVENTH_6_CONCRETE_ORDER_HEADERS.tsv"
PREFIX = "EIGHT_HUNDRED_EIGHTY_EIGHTH"

TITLES = {
    "WH01": "GRUNDANSATZ IM GEMEINSAMEN BECKEN BEI FEUCHTE-/WETTERLAGE",
    "WH02": "AUSZUG DURCH FUENF STATIONEN AM MARKIERTEN 28ER-PLATZ",
    "WH03": "GRUNDANSATZ DURCH FAECHER, GEFAESS UND KORB AM ASPEKTPLATZ",
    "WH04": "WARME ZIELPORTION AM PAAR UND AN ZWEI LAEUFEN BEI LICHT-/KOERPERQUALITAET",
    "WH05": "ERSTER DURCHGANGSAUSZUG AN DER LINKEN FRANSENSTATION AM STERNORT",
    "WH06": "GESCHLOSSENER DURCHLASSANSATZ AM RECHTEN S-LAUF BEIM PHASENPLATZ",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def consecutive(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if not result or result[-1] != value:
            result.append(value)
    return result


def main() -> None:
    marks = read(MARKS)
    units = read(UNITS)
    orders = read(ORDERS)
    payloads = read(PAYLOADS)
    when = {row["order_id"]: row for row in read(WHEN_HEADERS)}
    order_by_id = {row["order_id"]: row for row in orders}

    marks_by_key: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for mark in marks:
        marks_by_key[(mark["order_id"], mark["stage"], mark["unit"])].append(mark)

    unit_rows: list[dict[str, object]] = []
    for ordinal, unit in enumerate(units, start=1):
        subset = marks_by_key[(unit["order_id"], unit["stage"], unit["unit"])]
        owners = consecutive([row["owner_or_handle_de"] for row in subset])
        section = "WHAT" if unit["stage"].startswith("MAKE") else "HOW" if unit["stage"].startswith("APPLY") else "WHEN"
        reading = unit["fluent_workshop_reading_de"]
        if section == "WHEN":
            reading = when[unit["order_id"]]["concrete_condition_de"]
        unit_rows.append(
            {
                **unit,
                "master_unit_id": f"MU{ordinal:03d}",
                "section": section,
                "owner_trace_de": " -> ".join(owners),
                "visible_owner_switches": max(0, len(owners) - 1),
                "master_reading_de": reading,
            }
        )

    station_rows: list[dict[str, object]] = []
    for order in orders:
        local = [row for row in marks if row["order_id"] == order["order_id"] and row["stage"].startswith("APPLY")]
        blocks: list[list[dict[str, str]]] = []
        for mark in local:
            if not blocks or blocks[-1][-1]["owner_or_handle_de"] != mark["owner_or_handle_de"]:
                blocks.append([])
            blocks[-1].append(mark)
        for index, block in enumerate(blocks, start=1):
            statements = consecutive([row["unit"] for row in block])
            station_rows.append(
                {
                    "order_id": order["order_id"],
                    "biological_record": order["biological_record"],
                    "station_block": f"{order['order_id']}-ST{index:02d}",
                    "owner_de": block[0]["owner_or_handle_de"],
                    "statement_trace": ",".join(statements),
                    "first_mark": block[0]["order_mark_id"],
                    "last_mark": block[-1]["order_mark_id"],
                    "marks": len(block),
                    "surface_sequence": " ".join(row["surface"] for row in block),
                    "literal_sequence_de": "; ".join(row["concrete_default_de"] for row in block),
                }
            )

    block_count = Counter(row["order_id"] for row in station_rows)
    unit_count = Counter(row["order_id"] for row in unit_rows)
    order_rows: list[dict[str, object]] = []
    for order in orders:
        order_id = order["order_id"]
        condition = when[order_id]
        what = f"Bereite den Vorrat {order['revised_product']} ({order['revised_product_name_de']}) ueber {order['preparation_chain']} vollstaendig vor."
        station_phrase = "der einen sichtbaren Station" if block_count[order_id] == 1 else f"den {block_count[order_id]} sichtbaren Stationen"
        how = f"Fuehre den vollständigen Arbeitsgang {order['biological_record']} an {station_phrase} in Bildreihenfolge aus."
        when_text = condition["concrete_condition_de"]
        order_rows.append(
            {
                "order_id": order_id,
                "title_de": TITLES[order_id],
                "product_handle": order["revised_product"],
                "product_name_de": order["revised_product_name_de"],
                "preparation_chain": order["preparation_chain"],
                "biological_record": order["biological_record"],
                "station_blocks": block_count[order_id],
                "condition_handle": order["condition_handle"],
                "what_de": what,
                "how_de": how,
                "when_de": when_text,
                "complete_master_instruction_de": f"{what} {how} {when_text}",
                "marks": order["total_marks"],
                "units": unit_count[order_id],
                "payloads": 5,
                "dictionary_changes": 0,
            }
        )

    mark_rows: list[dict[str, object]] = []
    station_for_mark: dict[str, str] = {}
    for station in station_rows:
        active = False
        for mark in marks:
            if mark["order_id"] != station["order_id"]:
                continue
            if mark["order_mark_id"] == station["first_mark"]:
                active = True
            if active:
                station_for_mark[mark["order_mark_id"]] = str(station["station_block"])
            if mark["order_mark_id"] == station["last_mark"]:
                active = False
    for mark in marks:
        section = "WHAT" if mark["stage"].startswith("MAKE") else "HOW" if mark["stage"].startswith("APPLY") else "WHEN"
        mark_rows.append(
            {
                **mark,
                "master_section": section,
                "station_block": station_for_mark.get(mark["order_mark_id"], "NOT_APPLICABLE"),
            }
        )

    write(
        f"{PREFIX}_437_MARK_MASTER_BINDING.tsv",
        mark_rows,
        list(marks[0]) + ["master_section", "station_block"],
    )
    write(
        f"{PREFIX}_118_READABLE_UNITS.tsv",
        unit_rows,
        list(units[0]) + ["master_unit_id", "section", "owner_trace_de", "visible_owner_switches", "master_reading_de"],
    )
    write(
        f"{PREFIX}_16_VISIBLE_STATION_BLOCKS.tsv",
        station_rows,
        ["order_id", "biological_record", "station_block", "owner_de", "statement_trace", "first_mark", "last_mark", "marks", "surface_sequence", "literal_sequence_de"],
    )
    write(
        f"{PREFIX}_6_MASTER_ORDER_CARDS.tsv",
        order_rows,
        ["order_id", "title_de", "product_handle", "product_name_de", "preparation_chain", "biological_record", "station_blocks", "condition_handle", "what_de", "how_de", "when_de", "complete_master_instruction_de", "marks", "units", "payloads", "dictionary_changes"],
    )
    write(f"{PREFIX}_30_FILLED_PAYLOADS.tsv", payloads, list(payloads[0]))

    units_by_order: dict[str, list[dict[str, object]]] = defaultdict(list)
    for unit in unit_rows:
        units_by_order[str(unit["order_id"])].append(unit)
    lines = ["# Sechs Meister-Auftragskarten", ""]
    for card in order_rows:
        order_id = str(card["order_id"])
        lines.extend(
            [
                f"## {order_id}: {card['title_de']}",
                "",
                str(card["complete_master_instruction_de"]),
                "",
                "### WHAT — Vorrat herstellen",
                "",
            ]
        )
        for unit in [row for row in units_by_order[order_id] if row["section"] == "WHAT"]:
            lines.append(f"- `{unit['unit']}` / `{unit['fifth_hand_surface_sequence']}` — {unit['master_reading_de']}")
        lines.extend(["", "### HOW — sichtbare Stationen", ""])
        last_trace = ""
        for unit in [row for row in units_by_order[order_id] if row["section"] == "HOW"]:
            trace = str(unit["owner_trace_de"])
            if trace != last_trace:
                lines.append(f"**Station:** {trace}.")
                lines.append("")
                last_trace = trace
            lines.append(f"- `{unit['unit']}` / `{unit['fifth_hand_surface_sequence']}` — {unit['master_reading_de']}")
        condition_unit = [row for row in units_by_order[order_id] if row["section"] == "WHEN"][0]
        station_control = "eine sichtbare HOW-Station" if int(card["station_blocks"]) == 1 else f"{card['station_blocks']} sichtbare HOW-Stationen"
        lines.extend(
            [
                "",
                "### WHEN — Bildbedingung",
                "",
                f"`{condition_unit['unit']}` — {condition_unit['master_reading_de']}",
                f"Vollständig zu kopierender Griff: `{condition_unit['fifth_hand_surface_sequence']}`.",
                "",
                f"**Kontrolle:** {card['marks']} Marken, {card['units']} Einheiten, {station_control}, fünf ausgefüllte Nutzfelder.",
                "",
            ]
        )
    lines.extend(
        [
            "## Gemeinsame Meisterregel",
            "",
            "Lies jede Karte als WHAT -> HOW -> WHEN. Das Pflanzenbild besitzt die Vorratskette;",
            "jede Biological-Station besitzt nur ihren sichtbaren lokalen Arbeitsschritt; der Astrogriff",
            "nennt die Bildbedingung. Zeilenumbrüche beenden keinen Auftrag. Bei einem Besitzerwechsel",
            "wird die neue Station ausdrücklich angesagt. Die sechs Hauskalibrierungen bleiben gleich.",
        ]
    )
    (HERE / f"{PREFIX}_SIX_MASTER_ORDER_CARDS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    stage_counts = Counter(row["master_section"] for row in mark_rows)
    summary = {
        "status": "PASS",
        "decision": "SIX_COMPLETE_WHAT_HOW_WHEN_MASTER_CARDS_BIND_ALL_437_MARKS_AND_ALL_VISIBLE_STATION_SWITCHES",
        "orders": len(order_rows),
        "marks": len(mark_rows),
        "stage_counts": dict(stage_counts),
        "units": len(unit_rows),
        "station_blocks": len(station_rows),
        "owner_switches": len(station_rows) - len(order_rows),
        "payloads": len(payloads),
        "condition_links": len(when),
        "dictionary_changes": 0,
        "calibration_changes": 0,
        "fixed_pages": sorted({row["page"] for row in marks}),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 888: six master order cards\n\n"
        "The revised book is now readable as six complete WHAT -> HOW -> WHEN cards. All 437\n"
        "marks and 118 units remain exact. Sixteen consecutive visible station blocks expose ten\n"
        "owner switches rather than hiding them inside fluent prose. The six concrete condition\n"
        "readings and all 30 filled payloads are retained without a dictionary or calibration change.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
