#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P526 = ROOT / "experiments/yolo/sidequest_semantic_bound_master_exemplar_five_hundred_twenty_sixth"


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
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": "obere offene Fächerstation am Rand",
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": "mittlere Randfigur im runden Gefäß",
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": "untere Randfigur im korbartigen Gefäß",
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": "unverbundener Zwischenbereich zwischen Rand und Hauptpaar",
    "B3_MAIN_ARCH_LINKED_PAIR": "unteres sichtbares Figurenpaar mit gemeinsamem Bogen im B3-Record",
    "B4_MAIN_ARCH_LINKED_PAIR": "dasselbe sichtbare Figurenpaar im B4-Record",
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": "linke Hauptstation mit offenem Fransenlauf",
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": "rechte Hauptstation mit S-Lauf und Mehrarmknoten",
    "B5_LEFT_OPEN_FRINGE_STATION": "linke Fransenstation im eigenen B5-Nachtrag",
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": "rechter S-Lauf im eigenen B6-Nachtrag",
}


def phrase(reading: str) -> str:
    parts = reading.split(" · ")
    if parts and parts[-1] == "Schluss":
        body = " ".join(parts[:-1])
        return (body + "; schließen").strip()
    return " ".join(parts)


def main() -> None:
    all_events = read_tsv(P526 / "FIVE_HUNDRED_TWENTY_SIXTH_381_BOUND_EXEMPLAR_LOG.tsv")
    target_records = {"B3", "B4", "B5", "B6"}
    target = [row for row in all_events if row["record"] in target_records]
    prior_cards = {
        row["card_no"]
        for row in all_events
        if row["record"].startswith("H") or row["record"] in {"B1", "B2"}
    }

    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in target:
        by_card[row["card_no"]].append(row)
    dictionary: list[dict[str, str]] = []
    for card_no, rows in by_card.items():
        readings = {row["apprentice_spoken_reading_de"] for row in rows}
        if len(readings) != 1:
            raise ValueError(f"f83 card reading drift {card_no}: {readings}")
        dictionary.append(
            {
                "card_no": card_no,
                "component_parse": rows[0]["component_parse"],
                "invariant_card_reading_de": next(iter(readings)),
                "occurrences": str(len(rows)),
                "records": "|".join(dict.fromkeys(row["record"] for row in rows)),
                "surfaces": "|".join(dict.fromkeys(row["renderer_final_surface"] for row in rows)),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "shared_with_earlier_fixed_pages": "YES" if card_no in prior_cards else "NO",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FOURTH_SEVENTY_NINE_F83_CARD_DICTIONARY.tsv", dictionary)

    event_rows: list[dict[str, str]] = []
    for row in target:
        event_rows.append(
            {
                "event_id": row["event_id"],
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
                "global_cycle_edge": "NONE",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FOURTH_ONE_HUNDRED_FIFTY_THREE_EVENT_INTERLINEAR.tsv", event_rows)

    statement_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        statement_members[row["statement_id"]].append(row)
    cells: list[dict[str, str]] = []
    for statement_id, members in statement_members.items():
        owner_ids = list(dict.fromkeys(row["visible_owner_id"] for row in members))
        segments: list[str] = []
        previous_owner = None
        for row in members:
            if row["visible_owner_id"] != previous_owner:
                if previous_owner is not None:
                    segments.append(
                        f"[ohne Bildkante wechseln zu {row['visible_owner_de']}]"
                    )
                else:
                    segments.append(f"Bei {row['visible_owner_de']}")
                previous_owner = row["visible_owner_id"]
            segments.append(row["minimum_source_clause_de"])
        cells.append(
            {
                "statement_id": statement_id,
                "record": members[0]["record"],
                "visible_owner_ids": "|".join(owner_ids),
                "loci": "|".join(dict.fromkeys(row["locus"] for row in members)),
                "event_ids": "|".join(row["event_id"] for row in members),
                "surfaces": " ".join(row["surface"] for row in members),
                "card_literal_de": "; ".join(row["invariant_card_reading_de"] for row in members),
                "complete_workshop_reading_de": "; dann ".join(segments) + ".",
                "terminal": "YES" if any(row["terminal"] == "YES" for row in members) else "NO",
                "crosses_visible_owner_boundary": "YES" if len(owner_ids) > 1 else "NO",
                "global_cycle_claim": "NONE",
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FOURTH_FIFTY_FOUR_F83_OPERATING_CELLS.tsv", cells)

    owner_order = list(OWNER_NAMES)
    modules: list[dict[str, str]] = []
    for number, owner_id in enumerate(owner_order, 1):
        members = [row for row in event_rows if row["visible_owner_id"] == owner_id]
        touching = [row for row in cells if owner_id in row["visible_owner_ids"].split("|")]
        primitive_counts = Counter(
            primitive
            for row in members
            for primitive in row["primitive"].split(">")
        )
        modules.append(
            {
                "module_no": str(number),
                "record": members[0]["record"],
                "visible_owner_id": owner_id,
                "visible_owner_de": OWNER_NAMES[owner_id],
                "events": str(len(members)),
                "event_ids": "|".join(row["event_id"] for row in members),
                "statement_ids": "|".join(row["statement_id"] for row in touching),
                "closed_cells_touching": str(sum(row["terminal"] == "YES" for row in touching)),
                "open_cells_touching": str(sum(row["terminal"] == "NO" for row in touching)),
                "dominant_primitives": "|".join(
                    primitive for primitive, _ in primitive_counts.most_common(3)
                ),
                "relation_to_other_modules": (
                    "VISIBLE_LINK_WITHIN_OWNER_ONLY"
                    if "LINKED_PAIR" in owner_id or "S_RUN" in owner_id
                    else "LOCAL_STATION_NO_GLOBAL_CYCLE"
                ),
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_FOURTH_TEN_F83_OWNER_MODULES.tsv", modules)

    boundaries = [row for row in cells if row["crosses_visible_owner_boundary"] == "YES"]
    write_tsv("FIVE_HUNDRED_THIRTY_FOURTH_THREE_OWNER_BOUNDARY_CELLS.tsv", boundaries)
    shared = [row for row in dictionary if row["shared_with_earlier_fixed_pages"] == "YES"]
    write_tsv("FIVE_HUNDRED_THIRTY_FOURTH_THIRTY_SIX_PRIOR_SHARED_CARDS.tsv", shared)

    lines = [
        "# f83r / B3–B6 — vollständige lokale Stationsausgabe",
        "",
        "Alle Karten haben einen Default. Besitzergrenzen werden sichtbar markiert; ein Gesamtzyklus wird nicht ergänzt.",
        "",
    ]
    for module in modules:
        lines.extend(
            [
                f"## {module['record']} — {module['visible_owner_de']}",
                "",
            ]
        )
        for cell in cells:
            if module["visible_owner_id"] in cell["visible_owner_ids"].split("|"):
                lines.append(f"- {cell['statement_id']}: {cell['complete_workshop_reading_de']}")
        lines.append("")
    (HERE / "FIVE_HUNDRED_THIRTY_FOURTH_COMPLETE_F83_EDITION.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    summary = {
        "status": "PASS",
        "page": "f83r",
        "records": 4,
        "events": len(event_rows),
        "record_event_counts": dict(Counter(row["record"] for row in event_rows)),
        "statements": len(cells),
        "closed_cells": sum(row["terminal"] == "YES" for row in cells),
        "open_cells": sum(row["terminal"] == "NO" for row in cells),
        "owner_modules": len(modules),
        "owner_event_counts": {row["visible_owner_id"]: int(row["events"]) for row in modules},
        "cross_owner_cells": [row["statement_id"] for row in boundaries],
        "exact_cards": len(dictionary),
        "shared_prior_cards": len(shared),
        "global_cycle_edges_added": 0,
    }
    (HERE / "FIVE_HUNDRED_THIRTY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
