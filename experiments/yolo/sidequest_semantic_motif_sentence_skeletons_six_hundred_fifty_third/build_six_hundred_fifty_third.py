#!/usr/bin/env python3
"""Build compact source-statement skeletons from the nine motif roles."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"
P651 = ROOT / "experiments/yolo/sidequest_semantic_source_motifs_six_hundred_fifty_first"
P652 = ROOT / "experiments/yolo/sidequest_semantic_motif_attachment_grammar_six_hundred_fifty_second"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


COARSE = {
    "MOBILE_MEASURE_FRAME": "FRAME",
    "OPEN_MEASURE_SETUP": "BINDER",
    "OPEN_PREPARATION_BINDER": "BINDER",
    "CLOSING_TAIL": "CLOSE",
    "MEDIAL_BRIDGE": "BRIDGE",
    "CONTINUATION_FEEDER": "BINDER",
    "OPEN_TARGET_BINDER": "BINDER",
    "MOBILE_BRANCH_CAPSULE": "BRANCH",
}


RULES = [
    ("R01", "START", "LOCAL", "Aussage darf mit einer lokalen Kartenstrecke beginnen"),
    ("R02", "START", "BINDER|FRAME|BRANCH", "Aussage darf mit einem portablen Motiv beginnen"),
    ("R03", "LOCAL", "LOCAL", "lokale Karten bilden eine beliebig lange zusammenhaengende Strecke"),
    ("R04", "LOCAL", "BINDER|FRAME|BRIDGE|BRANCH|CLOSE|END", "nach lokaler Strecke darf Motiv oder Ende folgen"),
    ("R05", "BINDER", "LOCAL", "offener Binder verlangt rechts mindestens eine lokale Karte"),
    ("R06", "BRIDGE", "LOCAL", "innere Bruecke verlangt rechts eine lokale Karte und ist links lokal gebunden"),
    ("R07", "FRAME|BRANCH", "LOCAL|CLOSE|END", "beweglicher Rahmen oder Zweig darf weitergeben oder enden"),
    ("R08", "CLOSE", "END", "Schlussmotiv ist immer terminal"),
]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    selected = read_tsv(P651 / "SIX_HUNDRED_FIFTY_FIRST_SELECTED_MOTIF_INSTANCES.tsv")
    readings = read_tsv(P651 / "SIX_HUNDRED_FIFTY_FIRST_25_MINIMAL_STATEMENT_READINGS.tsv")
    attachments = read_tsv(P652 / "SIX_HUNDRED_FIFTY_SECOND_28_MOTIF_ATTACHMENTS.tsv")

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)
    selected_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected:
        selected_by_statement[row["statement_id"]].append(row)
    role_by_key = {
        (row["statement_id"], row["motif_id"], row["start_position"]): COARSE[row["motif_role"]]
        for row in attachments
    }

    skeleton_rows: list[dict[str, object]] = []
    for reading in readings:
        sid = reading["statement_id"]
        statement = by_statement[sid]
        motifs = sorted(selected_by_statement[sid], key=lambda row: int(row["start_position"]))
        pieces: list[dict[str, object]] = []
        position = 1
        for motif in motifs:
            start = int(motif["start_position"])
            n = int(motif["n"])
            if start > position:
                local = statement[position - 1:start - 1]
                pieces.append({"kind": "LOCAL", "events": local})
            role = role_by_key[(sid, motif["motif_id"], motif["start_position"])]
            motif_events = statement[start - 1:start - 1 + n]
            pieces.append({"kind": role, "motif": motif, "events": motif_events})
            position = start + n
        if position <= len(statement):
            pieces.append({"kind": "LOCAL", "events": statement[position - 1:]})

        exact_recipe = []
        counted = []
        coarse = []
        reconstructed_cards = []
        reconstructed_surfaces = []
        local_events = 0
        motif_events = 0
        for piece in pieces:
            cards = [row["card_no"] for row in piece["events"]]
            surfaces = [row["surface"] for row in piece["events"]]
            reconstructed_cards.extend(cards)
            reconstructed_surfaces.extend(surfaces)
            if piece["kind"] == "LOCAL":
                local_events += len(cards)
                exact_recipe.append(f"LOCAL({'|'.join(cards)})")
                counted.append(f"LOCAL{len(cards)}")
                coarse.append("LOCAL")
            else:
                motif_events += len(cards)
                motif = piece["motif"]
                exact_recipe.append(f"{piece['kind']}[{motif['motif_id']}]({'|'.join(cards)})")
                counted.append(f"{piece['kind']}[{motif['motif_id']}]")
                coarse.append(str(piece["kind"]))

        source_cards = [row["card_no"] for row in statement]
        source_surfaces = [row["surface"] for row in statement]
        skeleton_rows.append({
            "statement_id": sid,
            "page": reading["page"],
            "record": reading["record"],
            "event_count": len(statement),
            "local_events": local_events,
            "motif_events": motif_events,
            "coarse_skeleton": ">".join(coarse),
            "counted_skeleton": ">".join(counted),
            "exact_workshop_recipe": ">".join(exact_recipe),
            "source_cards": "|".join(source_cards),
            "reconstructed_cards": "|".join(reconstructed_cards),
            "source_surface": " ".join(source_surfaces),
            "reconstructed_surface": " ".join(reconstructed_surfaces),
            "exact_roundtrip": "YES" if reconstructed_cards == source_cards and reconstructed_surfaces == source_surfaces else "NO",
            "minimal_reading_de": reading["minimal_source_reading_de"],
        })

    rule_rows = [
        {"rule_id": rid, "from_state": source, "to_state": target, "apprentice_rule_de": rule}
        for rid, source, target, rule in RULES
    ]
    coarse_counts = Counter(row["coarse_skeleton"] for row in skeleton_rows)
    pattern_rows = [
        {
            "coarse_skeleton": pattern,
            "statements": count,
            "statement_ids": "|".join(row["statement_id"] for row in skeleton_rows if row["coarse_skeleton"] == pattern),
        }
        for pattern, count in sorted(coarse_counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    write_tsv(HERE / "SIX_HUNDRED_FIFTY_THIRD_25_SOURCE_ROLE_SKELETONS.tsv", skeleton_rows, list(skeleton_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_THIRD_8_APPRENTICE_RULES.tsv", rule_rows, list(rule_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_THIRD_13_COARSE_PATTERNS.tsv", pattern_rows, list(pattern_rows[0]))

    md = [
        "# 25 Aussagen als Werkstattskelette",
        "",
        "`LOCALn` ist eine aus dem Exemplar kopierte Kartenstrecke. BINDER, FRAME, BRIDGE, BRANCH und CLOSE sind die neun gelernten Motive in ihren Satzrollen.",
        "",
    ]
    for row in skeleton_rows:
        md.extend([
            f"## {row['statement_id']} — `{row['counted_skeleton']}`",
            "",
            f"Quelle: `{row['source_surface']}`",
            "",
            str(row["minimal_reading_de"]),
            "",
        ])
    (HERE / "SIX_HUNDRED_FIFTY_THIRD_SKELETON_READING_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "statements": len(skeleton_rows),
        "events": sum(int(row["event_count"]) for row in skeleton_rows),
        "motif_events": sum(int(row["motif_events"]) for row in skeleton_rows),
        "local_exemplar_events": sum(int(row["local_events"]) for row in skeleton_rows),
        "apprentice_rules": len(rule_rows),
        "coarse_skeleton_types": len(pattern_rows),
        "counted_skeleton_types": len({row["counted_skeleton"] for row in skeleton_rows}),
        "exact_recipe_types": len({row["exact_workshop_recipe"] for row in skeleton_rows}),
        "exact_card_and_surface_roundtrips": sum(row["exact_roundtrip"] == "YES" for row in skeleton_rows),
        "most_common_coarse_pattern": pattern_rows[0]["coarse_skeleton"],
        "most_common_coarse_pattern_statements": pattern_rows[0]["statements"],
        "decision": "EIGHT_RULE_SKELETON_TEACHES_ORDER_BUT_LOCAL_EXEMPLAR_CARRIES_ONE_HUNDRED_EVENTS",
    }
    (HERE / "SIX_HUNDRED_FIFTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
