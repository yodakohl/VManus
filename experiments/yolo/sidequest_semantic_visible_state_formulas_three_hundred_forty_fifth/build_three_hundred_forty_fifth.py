#!/usr/bin/env python3
"""Extract recurrent visible material-state formulas from the 79 state markers."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
AUDIT = ROOT / "experiments/yolo/sidequest_semantic_state_information_channels_three_hundred_forty_fourth/THREE_HUNDRED_FORTY_FOURTH_381_EVENT_STATE_CHANNEL_AUDIT.tsv"
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_herbal_formula_repair_three_hundred_twenty_ninth/THREE_HUNDRED_TWENTY_NINTH_381_GLOBAL_EVENTS.tsv"

FORMULA_NAMES = {
    ("M4_MEASURED_PORTION", "M4_MEASURED_PORTION"): ("F01_MASS_TO_MASS", "Maß nach Maß", "Menge, Stufe oder Portion wird wiederholt oder nachgestellt."),
    ("M2_PREPARATION", "M4_MEASURED_PORTION"): ("F02_PREPARATION_TO_MEASURE", "Ansatz zu Maß", "Eine Zubereitung erhält ihre Sollangabe oder Portion."),
    ("M2_PREPARATION", "M2_PREPARATION"): ("F03_PREPARATION_CONTINUATION", "Ansatz zu Ansatz", "Eine Zubereitung wird als weitere Zubereitung fortgeführt."),
    ("M1_RAW_PART", "M2_PREPARATION"): ("F04_MATERIAL_TO_PREPARATION", "Rohteil zu Ansatz", "Material oder Zutat wird in einen Arbeitsansatz überführt."),
    ("M1_RAW_PART", "M1_RAW_PART"): ("F05_MATERIAL_PAIRING", "Rohteil zu Rohteil", "Zwei Zutaten- oder Teilkarten werden gekoppelt."),
    ("M4_MEASURED_PORTION", "M3_CLEAR_EXTRACT"): ("F06_MEASURE_TO_CLEAR", "Maß zu Klarauszug", "Eine bemessene Portion wird als klarer Anteil gewonnen."),
    ("M4_MEASURED_PORTION", "M1_RAW_PART"): ("F07_MEASURE_TO_ADDITION", "Maß zu Zutat", "Nach der Maßangabe folgt weiteres Material."),
    ("M3_CLEAR_EXTRACT", "M4_MEASURED_PORTION"): ("F08_CLEAR_TO_MEASURE", "Klarauszug zu Maß", "Der klare Anteil wird anschließend bemessen."),
    ("M4_MEASURED_PORTION", "M5_APPLICATION_ITEM"): ("F09_MEASURE_TO_APPLICATION", "Maß zu Anwendung", "Ein bemessener Posten wird zur Anwendungseinheit."),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    audit = {row["event_id"]: row for row in read_tsv(AUDIT)}
    source = read_tsv(SOURCE)
    by_statement = defaultdict(list)
    for position, row in enumerate(source, start=1):
        enriched = dict(row)
        enriched["global_position"] = position
        enriched["state"] = audit[row["event_id"]]["material_state_marker"]
        by_statement[row["statement_id"]].append(enriched)

    marker_rows = []
    link_rows = []
    statement_rows = []
    pair_counts = Counter()
    direct_counts = Counter()
    records_by_pair = defaultdict(set)
    values_by_pair = defaultdict(list)
    for statement_id, rows in by_statement.items():
        markers = [(index, row) for index, row in enumerate(rows) if row["state"] != "NONE"]
        for ordinal, (index, row) in enumerate(markers, start=1):
            marker_rows.append({
                "event_id": row["event_id"],
                "statement_id": statement_id,
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "marker_ordinal_in_statement": ordinal,
                "surface": row["surface"],
                "atomic_value_de": row["atomic_value_de"],
                "state_id": row["state"],
                "event_position_in_statement": index + 1,
            })
        for link_ordinal, ((left_index, left), (right_index, right)) in enumerate(zip(markers, markers[1:]), start=1):
            pair = (left["state"], right["state"])
            pair_counts[pair] += 1
            direct = right_index == left_index + 1
            if direct:
                direct_counts[pair] += 1
            records_by_pair[pair].add(left["record_unit_id"])
            values_by_pair[pair].append(f"{left['atomic_value_de']}→{right['atomic_value_de']}")
            link_rows.append({
                "statement_id": statement_id,
                "record_unit_id": left["record_unit_id"],
                "page": left["page"],
                "link_ordinal": link_ordinal,
                "left_event_id": left["event_id"],
                "right_event_id": right["event_id"],
                "left_state_id": left["state"],
                "right_state_id": right["state"],
                "left_value_de": left["atomic_value_de"],
                "right_value_de": right["atomic_value_de"],
                "intervening_event_count": right_index - left_index - 1,
                "direct_card_adjacency": "YES" if direct else "NO",
                "recurrent_state_formula": "YES" if pair in FORMULA_NAMES else "NO",
            })
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"],
            "event_count": len(rows),
            "state_marker_count": len(markers),
            "state_sequence": " → ".join(row["state"] for _, row in markers) if markers else "NONE",
            "value_sequence": " → ".join(row["atomic_value_de"] for _, row in markers) if markers else "NONE",
        })

    formula_rows = []
    for pair, count in sorted(pair_counts.items(), key=lambda item: (-item[1], item[0])):
        if count < 2:
            continue
        formula_id, name, reading = FORMULA_NAMES[pair]
        formula_rows.append({
            "formula_id": formula_id,
            "formula_name_de": name,
            "left_state_id": pair[0],
            "right_state_id": pair[1],
            "within_statement_count": count,
            "direct_adjacency_count": direct_counts[pair],
            "gapped_count": count - direct_counts[pair],
            "records": "|".join(sorted(records_by_pair[pair])),
            "value_pair_examples": "|".join(dict.fromkeys(values_by_pair[pair])),
            "workshop_reading_de": reading,
        })

    write_tsv(HERE / "THREE_HUNDRED_FORTY_FIFTH_79_ORDERED_STATE_MARKERS.tsv", marker_rows,
              ["event_id", "statement_id", "record_unit_id", "page", "marker_ordinal_in_statement", "surface", "atomic_value_de", "state_id", "event_position_in_statement"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_FIFTH_41_WITHIN_STATEMENT_STATE_LINKS.tsv", link_rows,
              ["statement_id", "record_unit_id", "page", "link_ordinal", "left_event_id", "right_event_id", "left_state_id", "right_state_id", "left_value_de", "right_value_de", "intervening_event_count", "direct_card_adjacency", "recurrent_state_formula"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_FIFTH_NINE_RECURRENT_STATE_FORMULAS.tsv", formula_rows,
              ["formula_id", "formula_name_de", "left_state_id", "right_state_id", "within_statement_count", "direct_adjacency_count", "gapped_count", "records", "value_pair_examples", "workshop_reading_de"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_FIFTH_116_STATEMENT_STATE_SKELETONS.tsv", statement_rows,
              ["statement_id", "record_unit_id", "page", "event_count", "state_marker_count", "state_sequence", "value_sequence"])

    lines = ["# Neun sichtbare Stoffformeln", ""]
    for row in formula_rows:
        lines.extend([
            f"## {row['formula_name_de']} ({row['within_statement_count']}×)",
            "",
            row["workshop_reading_de"],
            f"Direkt benachbart {row['direct_adjacency_count']}×, mit eingeschobenen Arbeitskarten {row['gapped_count']}×; Records {row['records']}.",
            "",
        ])
    lines.extend([
        "## Leseweise",
        "",
        "Die Formel besteht aus zwei aufeinanderfolgenden Stoffmarkern derselben Aussage.",
        "Dazwischen dürfen Arbeitskarten stehen; ihre Zahl ist im Link-Ledger erhalten.",
        "Damit heißt Ansatz→Maß nicht, dass zwei sichtbare Wörter immer unmittelbar",
        "nebeneinanderstehen, sondern dass keine andere Stoffrolle dazwischenliegt.",
    ])
    (HERE / "THREE_HUNDRED_FORTY_FIFTH_VISIBLE_STATE_FORMULAS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "state_markers": len(marker_rows),
        "within_statement_links": len(link_rows),
        "direct_links": sum(row["direct_card_adjacency"] == "YES" for row in link_rows),
        "gapped_links": sum(row["direct_card_adjacency"] == "NO" for row in link_rows),
        "recurrent_formulas": len(formula_rows),
        "statements": len(statement_rows),
        "statements_with_state_markers": sum(int(row["state_marker_count"]) > 0 for row in statement_rows),
    }
    (HERE / "THREE_HUNDRED_FORTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
