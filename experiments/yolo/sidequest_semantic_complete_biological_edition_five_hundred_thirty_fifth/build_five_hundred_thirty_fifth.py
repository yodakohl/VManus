#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P526 = ROOT / "experiments/yolo/sidequest_semantic_bound_master_exemplar_five_hundred_twenty_sixth"
P532 = ROOT / "experiments/yolo/sidequest_semantic_b1_pool_modules_five_hundred_thirty_second"
P533 = ROOT / "experiments/yolo/sidequest_semantic_b2_station_book_five_hundred_thirty_third"
P534 = ROOT / "experiments/yolo/sidequest_semantic_f83_complete_edition_five_hundred_thirty_fourth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


OWNER_NAMES = {
    "B1_SHARED_TWO_ROW_POOL": "gemeinsame zweireihige Figuren-/Beckenstation",
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": "oberes Beckenpaar mit Zylinder",
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": "mittleres linkes Handgerät mit Inline-Knoten",
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": "mittlere rechte, bildlich unklare Station",
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": "unteres grünes Mehrfigurenbecken",
    "B2_LOWER_POOL_EDGE_STATIONS": "kleine Randstationen des unteren Beckens",
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": "obere offene Fächerstation am Rand",
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": "mittlere Randfigur im runden Gefäß",
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": "untere Randfigur im korbartigen Gefäß",
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": "unverbundener Zwischenbereich zwischen Rand und Hauptpaar",
    "B3_MAIN_ARCH_LINKED_PAIR": "unteres sichtbares Figurenpaar mit gemeinsamem Bogen",
    "B4_MAIN_ARCH_LINKED_PAIR": "sichtbares Figurenpaar mit gemeinsamem Bogen im B4-Record",
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": "linke Hauptstation mit offenem Fransenlauf",
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": "rechte Hauptstation mit S-Lauf und Mehrarmknoten",
    "B5_LEFT_OPEN_FRINGE_STATION": "linke Fransenstation im eigenen B5-Nachtrag",
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": "rechter S-Lauf im eigenen B6-Nachtrag",
}


def page_unit(record: str) -> str:
    if record == "B1":
        return "F81"
    if record == "B2":
        return "F82"
    return "F83"


def phrase(reading: str) -> str:
    parts = reading.split(" · ")
    if parts and parts[-1] == "Schluss":
        return (" ".join(parts[:-1]) + "; schließen").strip()
    return " ".join(parts)


def source_cell_readings() -> dict[str, str]:
    result: dict[str, str] = {}
    for row in read_tsv(P532 / "FIVE_HUNDRED_THIRTY_SECOND_TWENTY_ONE_B1_OPERATING_CELLS.tsv"):
        result[row["statement_id"]] = row["fluent_pool_reading_de"]
    for row in read_tsv(P533 / "FIVE_HUNDRED_THIRTY_THIRD_TWENTY_TWO_B2_OPERATING_CELLS.tsv"):
        result[row["statement_id"]] = row["fluent_station_reading_de"]
    for row in read_tsv(P534 / "FIVE_HUNDRED_THIRTY_FOURTH_FIFTY_FOUR_F83_OPERATING_CELLS.tsv"):
        result[row["statement_id"]] = row["complete_workshop_reading_de"]
    return result


def main() -> None:
    all_events = read_tsv(P526 / "FIVE_HUNDRED_TWENTY_SIXTH_381_BOUND_EXEMPLAR_LOG.tsv")
    bio = [row for row in all_events if row["record"].startswith("B")]
    herbal_cards = {row["card_no"] for row in all_events if row["record"].startswith("H")}

    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in bio:
        by_card[row["card_no"]].append(row)
    dictionary: list[dict[str, str]] = []
    for card_no, rows in by_card.items():
        readings = {row["apprentice_spoken_reading_de"] for row in rows}
        if len(readings) != 1:
            raise ValueError(f"Biological card drift {card_no}: {readings}")
        units = list(dict.fromkeys(page_unit(row["record"]) for row in rows))
        dictionary.append(
            {
                "card_no": card_no,
                "component_parse": rows[0]["component_parse"],
                "invariant_card_reading_de": next(iter(readings)),
                "occurrences": str(len(rows)),
                "page_units": "|".join(units),
                "records": "|".join(dict.fromkeys(row["record"] for row in rows)),
                "surfaces": "|".join(dict.fromkeys(row["renderer_final_surface"] for row in rows)),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "recurs_on_two_or_more_bio_pages": "YES" if len(units) >= 2 else "NO",
                "recurs_on_all_three_bio_pages": "YES" if len(units) == 3 else "NO",
                "shared_with_herbal": "YES" if card_no in herbal_cards else "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FIFTH_ONE_HUNDRED_TWENTY_FOUR_BIO_CARD_DICTIONARY.tsv", dictionary)

    event_rows: list[dict[str, str]] = []
    for row in bio:
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "locus": row["locus"],
                "visible_owner_id": row["owner_code"],
                "visible_owner_de": OWNER_NAMES[row["owner_code"]],
                "surface": row["renderer_final_surface"],
                "card_no": row["card_no"],
                "component_parse": row["component_parse"],
                "invariant_card_reading_de": row["apprentice_spoken_reading_de"],
                "minimum_source_clause_de": phrase(row["apprentice_spoken_reading_de"]),
                "primitive": row["procedure_tokens"],
                "terminal": "YES" if "CLOSE" in row["procedure_tokens"].split(">") else "NO",
                "global_network_edge": "NONE",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FIFTH_TWO_HUNDRED_EIGHTY_ONE_BIO_EVENT_INTERLINEAR.tsv", event_rows)

    fluent = source_cell_readings()
    statement_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        statement_members[row["statement_id"]].append(row)
    cells: list[dict[str, str]] = []
    for statement_id, members in statement_members.items():
        owners = list(dict.fromkeys(row["visible_owner_id"] for row in members))
        cells.append(
            {
                "statement_id": statement_id,
                "page": members[0]["page"],
                "record": members[0]["record"],
                "visible_owner_ids": "|".join(owners),
                "visible_owner_de": " | ".join(OWNER_NAMES[owner] for owner in owners),
                "loci": "|".join(dict.fromkeys(row["locus"] for row in members)),
                "event_ids": "|".join(row["event_id"] for row in members),
                "surfaces": " ".join(row["surface"] for row in members),
                "card_literal_de": "; ".join(row["invariant_card_reading_de"] for row in members),
                "complete_workshop_reading_de": fluent[statement_id],
                "terminal": "YES" if any(row["terminal"] == "YES" for row in members) else "NO",
                "crosses_visible_owner_boundary": "YES" if len(owners) > 1 else "NO",
                "global_network_claim": "NONE",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FIFTH_NINETY_SEVEN_BIO_OPERATING_CELLS.tsv", cells)

    modules: list[dict[str, str]] = []
    for number, owner_id in enumerate(dict.fromkeys(row["visible_owner_id"] for row in event_rows), 1):
        members = [row for row in event_rows if row["visible_owner_id"] == owner_id]
        touching = [row for row in cells if owner_id in row["visible_owner_ids"].split("|")]
        primitives = Counter(
            primitive for row in members for primitive in row["primitive"].split(">")
        )
        modules.append(
            {
                "module_no": str(number),
                "page": members[0]["page"],
                "records": "|".join(dict.fromkeys(row["record"] for row in members)),
                "visible_owner_id": owner_id,
                "visible_owner_de": OWNER_NAMES[owner_id],
                "events": str(len(members)),
                "event_ids": "|".join(row["event_id"] for row in members),
                "statement_ids": "|".join(row["statement_id"] for row in touching),
                "closed_cells_touching": str(sum(row["terminal"] == "YES" for row in touching)),
                "open_cells_touching": str(sum(row["terminal"] == "NO" for row in touching)),
                "dominant_primitives": "|".join(value for value, _ in primitives.most_common(4)),
                "relation_to_other_modules": "LOCAL_VISIBLE_OWNER_NO_GLOBAL_NETWORK",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FIFTH_SIXTEEN_VISIBLE_OWNER_MODULES.tsv", modules)

    recurrent = [row for row in dictionary if row["recurs_on_two_or_more_bio_pages"] == "YES"]
    write_tsv("FIVE_HUNDRED_THIRTY_FIFTH_THIRTY_TWO_CROSS_PAGE_BIO_CARDS.tsv", recurrent)
    herbal_shared = [row for row in dictionary if row["shared_with_herbal"] == "YES"]
    write_tsv("FIVE_HUNDRED_THIRTY_FIFTH_SEVENTEEN_HERBAL_BIO_SHARED_CARDS.tsv", herbal_shared)
    boundaries = [row for row in cells if row["crosses_visible_owner_boundary"] == "YES"]
    write_tsv("FIVE_HUNDRED_THIRTY_FIFTH_FOUR_OWNER_BOUNDARY_CELLS.tsv", boundaries)

    lines = [
        "# Biological — vollständige Sechs-Record-Werkstattausgabe",
        "",
        "Alle 281 Karten sind gelesen. Bildbesitzer bleiben lokal; es wird kein Gesamtrohrnetz ergänzt.",
        "",
    ]
    for record in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        record_cells = [row for row in cells if row["record"] == record]
        lines.extend([f"## {record} — {record_cells[0]['page']}", ""])
        for cell in record_cells:
            prefix = f"[{cell['visible_owner_de']}] "
            lines.append(f"- {cell['statement_id']}: {prefix}{cell['complete_workshop_reading_de']}")
        lines.append("")
    (HERE / "FIVE_HUNDRED_THIRTY_FIFTH_COMPLETE_BIOLOGICAL_EDITION.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    recurrent_events = sum(int(row["occurrences"]) for row in recurrent)
    all_three = [row for row in recurrent if row["recurs_on_all_three_bio_pages"] == "YES"]
    summary = {
        "status": "PASS",
        "pages": ["f81v", "f82r", "f83r"],
        "records": 6,
        "events": len(event_rows),
        "record_event_counts": dict(Counter(row["record"] for row in event_rows)),
        "statements": len(cells),
        "closed_cells": sum(row["terminal"] == "YES" for row in cells),
        "open_cells": sum(row["terminal"] == "NO" for row in cells),
        "exact_cards": len(dictionary),
        "owner_modules": len(modules),
        "owner_event_counts": {row["visible_owner_id"]: int(row["events"]) for row in modules},
        "cross_owner_cells": [row["statement_id"] for row in boundaries],
        "cross_page_cards": len(recurrent),
        "cross_page_card_events": recurrent_events,
        "all_three_page_cards": len(all_three),
        "all_three_page_card_events": sum(int(row["occurrences"]) for row in all_three),
        "herbal_shared_cards": len(herbal_shared),
        "global_network_edges_added": 0,
    }
    (HERE / "FIVE_HUNDRED_THIRTY_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
