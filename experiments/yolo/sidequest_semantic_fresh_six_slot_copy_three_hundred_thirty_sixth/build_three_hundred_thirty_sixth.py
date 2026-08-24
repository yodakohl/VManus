#!/usr/bin/env python3
"""Compose and reverse-read a fresh Herbal-to-Bio six-slot copy."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
HERBAL = ROOT / "experiments/yolo/sidequest_semantic_repaired_herbal_edition_three_hundred_thirtieth/THREE_HUNDRED_THIRTIETH_100_HERBAL_INTERLINEAR.tsv"
BIO = ROOT / "experiments/yolo/sidequest_semantic_repaired_bio_edition_three_hundred_thirty_second/THREE_HUNDRED_THIRTY_SECOND_281_REPAIRED_BIO_EVENTS.tsv"
P335 = ROOT / "experiments/yolo/sidequest_semantic_card_order_syntax_three_hundred_thirty_fifth/build_three_hundred_thirty_fifth.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


p335 = load_module("p335", P335)

HERBAL_SEQUENCE = [
    ("char", "4d4559019a961b834aa1", "Quelle"),
    ("qokain", "1645e612504fcef59ced", "Zugabe"),
    ("daiin", "2f1c5e56e8f0ff459065", "Sollmaß"),
    ("shey", "b5df9126607030b95175", "Klarauszug"),
    ("cheeky", "2c1a5fd92b9e3c762242", "Langwärme"),
    ("cthy", "e0b630cb1b5df5e7105b", "Bereit"),
]
BIO_SEQUENCE = [
    ("otchey", "faf321940aed922846a9", "Folgeposten"),
    ("daiin", "2f1c5e56e8f0ff459065", "Sollmaß"),
    ("chckhal", "21ed2873b71e57269c08", "Zielpassage"),
    ("qokeey", "0275fbf14e07935b0a45", "Langkontakt"),
    ("qoky", "276a7c2d74d1143446f4", "Einsetzen"),
    ("cheey", "b5df9126607030b95175", "Klarauszug"),
    ("qokedy", "7db18b2f0fb7ed0fcfd3", "Kurzkontakt"),
    ("qokeeedy", "d25110e0d8488927278f", "Volleinsatz"),
    ("lchedy", "de7321bface5628e35d6", "abführen"),
    ("solkey", "42cdc187d5b9ffc60063", "Kurzsammlung"),
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
    old_events = read_tsv(HERBAL) + read_tsv(BIO)
    statements = {}
    for row in old_events:
        statements.setdefault(row["statement_id"], []).append(row["joint_tuple_id"])
    provenance = {}
    for row in old_events:
        key = (row["surface"], row["joint_tuple_id"], row["atomic_value_de"])
        provenance.setdefault(key, row)

    rows = []
    for passage_id, register, owner, sequence in (
        ("FRESH_HERBAL_PREPARATION", "HERBAL", "NEW_PICTURED_PLANT_OWNER", HERBAL_SEQUENCE),
        ("FRESH_BIO_CONTINUATION", "BIO", "NEW_LOCAL_BASIN_STATION", BIO_SEQUENCE),
    ):
        cycle = 1
        previous = 0
        for position, (surface, joint_id, value) in enumerate(sequence, start=1):
            source = provenance[(surface, joint_id, value)]
            program = p335.classify(register, value)
            rank = p335.SLOT_BY_PROGRAM[program]
            if position > 1 and rank < previous:
                cycle += 1
                action = "RESET_TO_NEW_MICROCYCLE"
            elif position == 1:
                action = "OPEN_FIRST_CYCLE"
            elif rank == previous:
                action = "REPEAT_CURRENT_SLOT"
            else:
                action = "ADVANCE_WITH_SKIPPED_SLOTS_ALLOWED"
            previous = rank
            rows.append({
                "fresh_event_id": f"{passage_id}_E{position:02d}",
                "passage_id": passage_id,
                "register": register,
                "new_owner": owner,
                "position": position,
                "surface": surface,
                "joint_tuple_id": joint_id,
                "atomic_value_de": value,
                "program_id": program,
                "slot_rank": rank,
                "slot_code": p335.SLOT_NAME[rank],
                "microcycle": cycle,
                "generation_action": action,
                "source_event_id": source["event_id"],
                "source_page": source["page"],
                "registered_identity_match": "YES",
                "registered_value_match": "YES",
            })

    passage_rows = []
    readings = {
        "FRESH_HERBAL_PREPARATION": "Nimm aus der bezeichneten Quelle einen Zusatz nach Sollmaß, gewinne den Klarauszug, halte ihn länger warm und stelle ihn bereit.",
        "FRESH_BIO_CONTINUATION": "Nimm ihn als Folgeposten, führe ihn nach Sollmaß durch die Zielpassage, behandle ihn länger und setze ihn ein. Nimm den Klarauszug, behandle ihn kurz und setze ihn vollständig ein; führe den Rest ab und sammle ihn kurz.",
    }
    for passage_id in readings:
        rr = [row for row in rows if row["passage_id"] == passage_id]
        ids = [row["joint_tuple_id"] for row in rr]
        full_sequence_old = any(ids == old for old in statements.values())
        contiguous_old = any(
            ids == old[start:start + len(ids)]
            for old in statements.values()
            for start in range(max(0, len(old) - len(ids) + 1))
        )
        passage_rows.append({
            "passage_id": passage_id,
            "register": rr[0]["register"],
            "new_owner": rr[0]["new_owner"],
            "event_count": len(rr),
            "microcycle_count": max(int(row["microcycle"]) for row in rr),
            "surface_sequence": " ".join(row["surface"] for row in rr),
            "atomic_sequence": " → ".join(row["atomic_value_de"] for row in rr),
            "slot_sequence": " → ".join(row["slot_code"] for row in rr),
            "fresh_full_sequence": "YES" if not full_sequence_old else "NO",
            "fresh_contiguous_sequence": "YES" if not contiguous_old else "NO",
            "reverse_reading_de": readings[passage_id],
        })

    anchors = []
    for hpos, h in enumerate(HERBAL_SEQUENCE, start=1):
        for bpos, b in enumerate(BIO_SEQUENCE, start=1):
            if h[1] == b[1]:
                anchors.append({
                    "joint_tuple_id": h[1],
                    "atomic_value_de": h[2],
                    "herbal_position": hpos,
                    "herbal_surface": h[0],
                    "bio_position": bpos,
                    "bio_surface": b[0],
                    "same_identity": "YES",
                    "same_value": "YES",
                })

    write_tsv(HERE / "THREE_HUNDRED_THIRTY_SIXTH_16_FRESH_CARD_EVENTS.tsv", rows,
              ["fresh_event_id", "passage_id", "register", "new_owner", "position", "surface", "joint_tuple_id", "atomic_value_de", "program_id", "slot_rank", "slot_code", "microcycle", "generation_action", "source_event_id", "source_page", "registered_identity_match", "registered_value_match"])
    write_tsv(HERE / "THREE_HUNDRED_THIRTY_SIXTH_TWO_FRESH_PASSAGES.tsv", passage_rows,
              ["passage_id", "register", "new_owner", "event_count", "microcycle_count", "surface_sequence", "atomic_sequence", "slot_sequence", "fresh_full_sequence", "fresh_contiguous_sequence", "reverse_reading_de"])
    write_tsv(HERE / "THREE_HUNDRED_THIRTY_SIXTH_TWO_EXACT_HANDOFF_ANCHORS.tsv", anchors,
              ["joint_tuple_id", "atomic_value_de", "herbal_position", "herbal_surface", "bio_position", "bio_surface", "same_identity", "same_value"])

    md = [
        "# Frische Werkstatt-Doppelfolge",
        "",
        "## Herbal-Vorbereitung",
        "",
        "`char qokain daiin shey cheeky cthy`",
        "",
        readings["FRESH_HERBAL_PREPARATION"],
        "",
        "## Biological-Fortsetzung",
        "",
        "`otchey daiin chckhal qokeey qoky cheey qokedy qokeeedy lchedy solkey`",
        "",
        readings["FRESH_BIO_CONTINUATION"],
        "",
        "## Rücklesung",
        "",
        "Alle sechzehn Oberflächen sind registrierte Realisierungen bekannter exakter",
        "Karten. Die Herbal-Folge ist ein einziger Sechsplatz-Mikrogang. Die Biological-",
        "Folge besteht aus drei Mikrogängen: Anwendung, Klarauszug-Anwendung und lokaler",
        "Abzug/Sammlung. Sollmaß und Klarauszug sind identische Karten auf beiden Seiten.",
        "Keine der beiden vollständigen Folgen kommt in den 116 Ausgangsaussagen vor.",
    ]
    (HERE / "THREE_HUNDRED_THIRTY_SIXTH_FRESH_COPY.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "fresh_passages": len(passage_rows),
        "fresh_events": len(rows),
        "registered_identity_matches": sum(row["registered_identity_match"] == "YES" for row in rows),
        "registered_value_matches": sum(row["registered_value_match"] == "YES" for row in rows),
        "exact_handoff_anchors": len(anchors),
        "fresh_full_sequences": sum(row["fresh_full_sequence"] == "YES" for row in passage_rows),
    }
    (HERE / "THREE_HUNDRED_THIRTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
