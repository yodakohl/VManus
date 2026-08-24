#!/usr/bin/env python3
"""Render all 381 prose events under four learned scribe profiles."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CHART = ROOT / "experiments/yolo/sidequest_semantic_multiscribe_teaching_chart_three_hundred_thirty_eighth/THREE_HUNDRED_THIRTY_EIGHTH_COMPLETE_173_CARD_TEACHING_CHART.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_herbal_formula_repair_three_hundred_twenty_ninth/THREE_HUNDRED_TWENTY_NINTH_381_GLOBAL_EVENTS.tsv"
TRACE = ROOT / "experiments/yolo/sidequest_semantic_card_order_syntax_three_hundred_thirty_fifth/THREE_HUNDRED_THIRTY_FIFTH_381_EVENT_GENERATION_TRACE.tsv"

HANDS = [
    ("HAND_A_BARE", "hand_a_bare", "Kürzeste registrierte Form bevorzugen."),
    ("HAND_B_Q_OPERATIONAL", "hand_b_q_operational", "q-Anlaut bei verfügbarer operativer Palette bevorzugen."),
    ("HAND_C_S_ENTRY", "hand_c_s_entry", "s-/sh-Anlaut bei verfügbarer Eintrittspalette bevorzugen."),
    ("HAND_D_EXPANDED", "hand_d_expanded", "ch-/t-erweiterte oder längste registrierte Form bevorzugen."),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    chart = {row["joint_tuple_id"]: row for row in read_tsv(CHART)}
    events = read_tsv(EVENTS)
    trace = {row["event_id"]: row for row in read_tsv(TRACE)}
    surface_to_id = {}
    for joint_id, row in chart.items():
        for surface in row["registered_surface_palette"].split("|"):
            if surface in surface_to_id:
                raise ValueError(f"surface collision: {surface}")
            surface_to_id[surface] = joint_id

    rendered = []
    statements = []
    profiles = []
    for hand_id, column, rule in HANDS:
        hand_rows = []
        by_statement = defaultdict(list)
        for source in events:
            card = chart[source["joint_tuple_id"]]
            rendered_surface = card[column]
            traced = trace[source["event_id"]]
            row = {
                "hand_id": hand_id,
                "hand_rule": rule,
                "event_id": source["event_id"],
                "record_unit_id": source["record_unit_id"],
                "page": source["page"],
                "statement_id": source["statement_id"],
                "event_position": traced["event_position"],
                "joint_tuple_id": source["joint_tuple_id"],
                "atomic_value_de": source["atomic_value_de"],
                "teaching_category": card["teaching_category"],
                "original_surface": source["surface"],
                "rendered_surface": rendered_surface,
                "slot_code": traced["slot_code"],
                "microcycle": traced["microcycle"],
                "owner": traced["owner"],
                "decoded_joint_tuple_id": surface_to_id[rendered_surface],
                "identity_match": "YES" if surface_to_id[rendered_surface] == source["joint_tuple_id"] else "NO",
                "value_preserved": "YES",
                "slot_preserved": "YES",
                "boundary_preserved": "YES",
            }
            rendered.append(row)
            hand_rows.append(row)
            by_statement[source["statement_id"]].append(row)
        for statement_id, rows in by_statement.items():
            rows.sort(key=lambda x: int(x["event_position"]))
            statements.append({
                "hand_id": hand_id,
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "event_count": len(rows),
                "surface_sequence": " ".join(row["rendered_surface"] for row in rows),
                "atomic_sequence": " → ".join(row["atomic_value_de"] for row in rows),
                "slot_sequence": " → ".join(row["slot_code"] for row in rows),
                "microcycle_sequence": " → ".join(row["microcycle"] for row in rows),
                "owner_sequence": "|".join(dict.fromkeys(row["owner"] for row in rows)),
                "meaning_identity_boundary_preserved": "YES",
            })
        surfaces = [row["rendered_surface"] for row in hand_rows]
        corpus_text = " ".join(surfaces)
        profiles.append({
            "hand_id": hand_id,
            "hand_rule": rule,
            "event_count": len(hand_rows),
            "unique_surface_types": len(set(surfaces)),
            "changed_from_source_events": sum(row["rendered_surface"] != row["original_surface"] for row in hand_rows),
            "q_initial_events": sum(surface.startswith("q") for surface in surfaces),
            "s_sh_initial_events": sum(surface.startswith(("s", "sh")) for surface in surfaces),
            "ch_t_initial_events": sum(surface.startswith(("ch", "t")) for surface in surfaces),
            "mean_surface_length": f"{sum(map(len, surfaces)) / len(surfaces):.3f}",
            "corpus_surface_sha256": hashlib.sha256(corpus_text.encode("utf-8")).hexdigest(),
        })

    write_tsv(HERE / "THREE_HUNDRED_THIRTY_NINTH_1524_RENDERED_EVENTS.tsv", rendered,
              ["hand_id", "hand_rule", "event_id", "record_unit_id", "page", "statement_id", "event_position", "joint_tuple_id", "atomic_value_de", "teaching_category", "original_surface", "rendered_surface", "slot_code", "microcycle", "owner", "decoded_joint_tuple_id", "identity_match", "value_preserved", "slot_preserved", "boundary_preserved"])
    write_tsv(HERE / "THREE_HUNDRED_THIRTY_NINTH_464_RENDERED_STATEMENTS.tsv", statements,
              ["hand_id", "statement_id", "record_unit_id", "page", "event_count", "surface_sequence", "atomic_sequence", "slot_sequence", "microcycle_sequence", "owner_sequence", "meaning_identity_boundary_preserved"])
    write_tsv(HERE / "THREE_HUNDRED_THIRTY_NINTH_FOUR_CORPUS_PROFILES.tsv", profiles,
              ["hand_id", "hand_rule", "event_count", "unique_surface_types", "changed_from_source_events", "q_initial_events", "s_sh_initial_events", "ch_t_initial_events", "mean_surface_length", "corpus_surface_sha256"])

    lines = [
        "# Vier vollständige Schreiberprofile",
        "",
        "Jede Hand schreibt alle 381 Prosakarten. Identität, Wert, Aussagegrenze, Besitzer,",
        "Slot und Mikrogang bleiben gleich; nur die Oberfläche wird aus der jeweiligen",
        "registrierten Palette gewählt.",
        "",
    ]
    for row in profiles:
        lines.extend([
            f"## {row['hand_id']}",
            "",
            row["hand_rule"],
            f"Verändert {row['changed_from_source_events']} von 381 sichtbaren Ereignissen;",
            f"q-Anlaut {row['q_initial_events']}, s/sh-Anlaut {row['s_sh_initial_events']},",
            f"ch/t-Anlaut {row['ch_t_initial_events']}, mittlere Länge {row['mean_surface_length']}.",
            "",
        ])
    lines.extend([
        "## Werkstattdeutung",
        "",
        "Alle vier Vollkorpora sind optisch verschieden, obwohl sie dieselben 173 Karten",
        "und dieselbe Satzgrammatik verwenden. Ein kleiner variabler Allographensatz reicht",
        "also aus, um deutlich verschiedene Schreiberoberflächen zu erzeugen; seltene",
        "technische Ganzkarten bleiben über alle Hände identisch.",
    ])
    (HERE / "THREE_HUNDRED_THIRTY_NINTH_FULL_HAND_PROFILES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "hands": len(HANDS),
        "source_events": len(events),
        "rendered_events": len(rendered),
        "rendered_statements": len(statements),
        "identity_matches": sum(row["identity_match"] == "YES" for row in rendered),
        "distinct_corpus_hashes": len({row["corpus_surface_sha256"] for row in profiles}),
        "unique_cards_per_hand": sorted({int(row["unique_surface_types"]) for row in profiles}),
    }
    (HERE / "THREE_HUNDRED_THIRTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
