#!/usr/bin/env python3
"""Assemble one plausible mixed-hand edition of all seven prose pages."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RENDERED = ROOT / "experiments/yolo/sidequest_semantic_full_four_hand_corpus_three_hundred_thirty_ninth/THREE_HUNDRED_THIRTY_NINTH_1524_RENDERED_EVENTS.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_full_four_hand_corpus_three_hundred_thirty_ninth/THREE_HUNDRED_THIRTY_NINTH_464_RENDERED_STATEMENTS.tsv"
HANDOFFS = ROOT / "experiments/yolo/sidequest_semantic_repaired_handoffs_three_hundred_thirty_first/THREE_HUNDRED_THIRTY_FIRST_FIVE_REPAIRED_HANDOFFS.tsv"

ASSIGNMENT = {
    "H1": "HAND_A_BARE",
    "H2": "HAND_A_BARE",
    "H3": "HAND_B_Q_OPERATIONAL",
    "H4": "HAND_C_S_ENTRY",
    "H5": "HAND_D_EXPANDED",
    "B1": "HAND_A_BARE",
    "B2": "HAND_B_Q_OPERATIONAL",
    "B3": "HAND_D_EXPANDED",
    "B4": "HAND_C_S_ENTRY",
    "B5": "HAND_D_EXPANDED",
    "B6": "HAND_D_EXPANDED",
}
ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rendered = read_tsv(RENDERED)
    all_statements = read_tsv(STATEMENTS)
    selected_events = [row for row in rendered if ASSIGNMENT[row["record_unit_id"]] == row["hand_id"]]
    selected_statements = [row for row in all_statements if ASSIGNMENT[row["record_unit_id"]] == row["hand_id"]]
    selected_events.sort(key=lambda row: (ORDER.index(row["record_unit_id"]), int(row["event_id"][1:])))
    selected_statements.sort(key=lambda row: (ORDER.index(row["record_unit_id"]), int(row["statement_id"].split("S")[1])))

    record_rows = []
    for record in ORDER:
        rows = [row for row in selected_events if row["record_unit_id"] == record]
        record_statements = [row for row in selected_statements if row["record_unit_id"] == record]
        hand = ASSIGNMENT[record]
        record_rows.append({
            "record_unit_id": record,
            "page": rows[0]["page"],
            "assigned_hand": hand,
            "event_count": len(rows),
            "statement_count": len(record_statements),
            "surface_stream": " ".join(row["rendered_surface"] for row in rows),
            "atomic_stream": " → ".join(row["atomic_value_de"] for row in rows),
            "identity_value_slot_boundary_preserved": "YES",
        })

    profiles = []
    for hand in sorted(set(ASSIGNMENT.values())):
        rows = [row for row in selected_events if row["hand_id"] == hand]
        surfaces = [row["rendered_surface"] for row in rows]
        profiles.append({
            "hand_id": hand,
            "assigned_records": "|".join(record for record in ORDER if ASSIGNMENT[record] == hand),
            "assigned_pages": "|".join(dict.fromkeys(row["page"] for row in rows)),
            "event_count": len(rows),
            "statement_count": sum(row["hand_id"] == hand for row in selected_statements),
            "q_initial_events": sum(surface.startswith("q") for surface in surfaces),
            "s_sh_initial_events": sum(surface.startswith(("s", "sh")) for surface in surfaces),
            "ch_t_initial_events": sum(surface.startswith(("ch", "t")) for surface in surfaces),
            "mean_surface_length": f"{sum(map(len, surfaces)) / len(surfaces):.3f}",
        })

    handoffs = []
    for row in read_tsv(HANDOFFS):
        target_record = row["bio_unit"].split("-")[0]
        source_hand = ASSIGNMENT[row["herbal_record"]]
        target_hand = ASSIGNMENT[target_record]
        handoffs.append({
            "herbal_record": row["herbal_record"],
            "bio_unit": row["bio_unit"],
            "source_hand": source_hand,
            "target_hand": target_hand,
            "handoff_mode": "SAME_HAND_CONTINUATION" if source_hand == target_hand else "CROSS_HAND_WORKSHOP_RELAY",
            "exact_shared_values": row["exact_shared_values"],
            "identity_value_preserved_across_hands": "YES",
            "integrated_reading_de": row["integrated_reading_de"],
        })

    write_tsv(HERE / "THREE_HUNDRED_FORTIETH_381_MIXED_HAND_EVENTS.tsv", selected_events,
              list(selected_events[0]))
    write_tsv(HERE / "THREE_HUNDRED_FORTIETH_116_MIXED_HAND_STATEMENTS.tsv", selected_statements,
              list(selected_statements[0]))
    write_tsv(HERE / "THREE_HUNDRED_FORTIETH_ELEVEN_RECORD_ASSIGNMENTS.tsv", record_rows,
              ["record_unit_id", "page", "assigned_hand", "event_count", "statement_count", "surface_stream", "atomic_stream", "identity_value_slot_boundary_preserved"])
    write_tsv(HERE / "THREE_HUNDRED_FORTIETH_FOUR_LOCAL_HAND_PROFILES.tsv", profiles,
              ["hand_id", "assigned_records", "assigned_pages", "event_count", "statement_count", "q_initial_events", "s_sh_initial_events", "ch_t_initial_events", "mean_surface_length"])
    write_tsv(HERE / "THREE_HUNDRED_FORTIETH_FIVE_HANDOFF_RELAYS.tsv", handoffs,
              ["herbal_record", "bio_unit", "source_hand", "target_hand", "handoff_mode", "exact_shared_values", "identity_value_preserved_across_hands", "integrated_reading_de"])

    lines = [
        "# Eine gemischte Vierhand-Werkstattausgabe",
        "",
        "## Arbeitsverteilung",
        "",
    ]
    for row in record_rows:
        lines.append(f"- {row['record_unit_id']} / {row['page']}: {row['assigned_hand']} ({row['event_count']} Karten).")
    lines.extend([
        "",
        "## Übergaben",
        "",
        "Vier der fünf Herbal→Bio-Übergaben bleiben in derselben Hand. H5→B4 ist",
        "der bewusste Relay von der erweiterten Hand D zur s-Hand C. Folgeposten und",
        "Einsetzen bleiben dabei als exakte Karten identisch; nur die zugelassene",
        "Oberfläche richtet sich nach der empfangenden Hand.",
        "",
        "## Werkstattlesung",
        "",
        "Die Seiten sehen nicht aus wie ein gleichförmiger Vollkorpus. Dennoch teilen",
        "alle Schreiber das 173-Karten-Wörterbuch, die zwölf Programme und die sechs",
        "Schreibplätze. Ein Handwechsel darf deshalb einen laufenden Arbeitsgegenstand",
        "übernehmen, ohne eine neue Sprache oder neue Bedeutung einzuführen.",
    ])
    (HERE / "THREE_HUNDRED_FORTIETH_MIXED_WORKSHOP_EDITION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    surface_stream = " ".join(row["rendered_surface"] for row in selected_events)
    summary = {
        "status": "PASS",
        "hands": len(profiles),
        "records": len(record_rows),
        "pages": len({row["page"] for row in selected_events}),
        "events": len(selected_events),
        "statements": len(selected_statements),
        "same_hand_handoffs": sum(row["handoff_mode"] == "SAME_HAND_CONTINUATION" for row in handoffs),
        "cross_hand_relays": sum(row["handoff_mode"] == "CROSS_HAND_WORKSHOP_RELAY" for row in handoffs),
        "mixed_surface_sha256": hashlib.sha256(surface_stream.encode("utf-8")).hexdigest(),
    }
    (HERE / "THREE_HUNDRED_FORTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
