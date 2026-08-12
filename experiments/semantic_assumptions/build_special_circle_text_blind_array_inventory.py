#!/usr/bin/env python3
"""Build the source-native filler-blind f67--f73 array inventory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
SOURCE = BASE / "results/existing_human_exact_locus_annotations.tsv"
METHOD = BASE / "SPECIAL_CIRCLE_TEXT_BLIND_ARRAY_INVENTORY_METHOD.md"
OUT_TSV = BASE / "results/special_circle_text_blind_array_inventory.tsv"
OUT_JSON = BASE / "results/special_circle_text_blind_array_inventory.json"
OUT_MD = BASE / "results/special_circle_text_blind_array_inventory_report.md"
SUFFIXES = {"L0", "Ls", "Lz", "La", "Ri", "Ro"}
FIELDS = (
    "array_index",
    "array_id",
    "slot_index",
    "slot_count",
    "occupancy_state",
    "physical_folio",
    "page",
    "unit",
    "locus",
    "source_locus",
    "normalized_code",
    "unit_description",
    "local_comment",
    "local_relation_tags",
    "unit_relation_tags",
    "relation_scope",
    "certainty",
    "source_path",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if not match or not 67 <= int(match.group(1)[1:]) <= 73:
        raise SystemExit(f"invalid special-circle page: {page}")
    return match.group(1)


def build_rows() -> list[dict[str, str]]:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    group_order: list[tuple[str, str]] = []
    for row in source_rows:
        match = re.match(r"^f(\d+)", row["page"])
        if not match or not 67 <= int(match.group(1)) <= 73:
            continue
        key = (row["page"], row["unit"])
        if key not in grouped:
            group_order.append(key)
        grouped[key].append(row)
    selected = []
    for key in group_order:
        rows = grouped[key]
        individual_count = sum(
            bool(row["normalized_code"]) and row["normalized_code"][-2:] in SUFFIXES for row in rows
        )
        if individual_count >= 3:
            selected.append((key, rows))
    output: list[dict[str, str]] = []
    for array_index, ((page, unit), rows) in enumerate(selected, 1):
        array_id = f"SCARR{array_index:03d}|{page}|{unit}"
        for slot_index, row in enumerate(rows, 1):
            if row["normalized_code"]:
                occupancy_state = "TRANSCRIBED"
            elif "missing" in row["local_comment"].lower() or "not labeled" in row["local_comment"].lower():
                occupancy_state = "ABSENT"
            elif "trace" in row["local_comment"].lower() or "unreadable" in row["local_comment"].lower():
                occupancy_state = "UNREADABLE_TRACE"
            else:
                raise SystemExit(f"unclassified empty-code row: {row['locus']}")
            output.append(
                {
                    "array_index": str(array_index),
                    "array_id": array_id,
                    "slot_index": str(slot_index),
                    "slot_count": str(len(rows)),
                    "occupancy_state": occupancy_state,
                    "physical_folio": physical_folio(page),
                    "page": page,
                    "unit": unit,
                    "locus": row["locus"],
                    "source_locus": row["source_locus"],
                    "normalized_code": row["normalized_code"] or "NONE",
                    "unit_description": row["unit_description"],
                    "local_comment": row["local_comment"],
                    "local_relation_tags": row["local_relation_tags"] or "NONE",
                    "unit_relation_tags": row["unit_relation_tags"] or "NONE",
                    "relation_scope": row["relation_scope"],
                    "certainty": row["certainty"],
                    "source_path": row["source_path"],
                }
            )
    return output


def tsv_bytes(rows: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def build() -> tuple[list[dict[str, str]], dict[str, object], str]:
    rows = build_rows()
    array_ids = list(dict.fromkeys(row["array_id"] for row in rows))
    page_counts = Counter(row["page"] for row in rows)
    folio_counts = Counter(row["physical_folio"] for row in rows)
    absent = [row for row in rows if row["occupancy_state"] == "ABSENT"]
    unreadable = [row for row in rows if row["occupancy_state"] == "UNREADABLE_TRACE"]
    transcribed = [row for row in rows if row["occupancy_state"] == "TRANSCRIBED"]
    if (len(array_ids), len(rows), len(transcribed), len(unreadable), len(absent)) != (45, 504, 502, 1, 1):
        raise SystemExit("registered inventory counts changed")
    if len(page_counts) != 23 or len(folio_counts) != 7:
        raise SystemExit("registered page/folio counts changed")
    result: dict[str, object] = {
        "experiment": "SPECIAL_CIRCLE_TEXT_BLIND_ARRAY_INVENTORY",
        "schema": "SPECIAL_CIRCLE_TEXT_BLIND_ARRAY_INVENTORY_V2",
        "status": "PASS_CORRECTED_VERSIONED_TEXT_BLIND_SPECIAL_CIRCLE_INVENTORY",
        "decision": "STOP_OMISSION_PATTERN_ONE_EXPLICIT_ABSENCE",
        "counts": {
            "arrays": len(array_ids),
            "slots": len(rows),
            "transcribed_slots": len(transcribed),
            "unreadable_trace_slots": len(unreadable),
            "source_explicit_absent_slots": len(absent),
            "page_panels": len(page_counts),
            "physical_folios": len(folio_counts),
            "within_array_linear_adjacencies": len(rows) - len(array_ids),
        },
        "arrays_by_physical_folio": dict(sorted(Counter(row["physical_folio"] for row in rows if row["slot_index"] == "1").items())),
        "slots_by_physical_folio": dict(sorted(folio_counts.items())),
        "nontranscribed_slots": [
            {
                "array_id": row["array_id"],
                "page": row["page"],
                "unit": row["unit"],
                "locus": row["locus"],
                "slot_index": int(row["slot_index"]),
                "occupancy_state": row["occupancy_state"],
            }
            for row in unreadable + absent
        ],
        "inputs": {
            str(SOURCE.relative_to(ROOT)): sha(SOURCE),
            str(METHOD.relative_to(ROOT)): sha(METHOD),
        },
        "inventory_tsv_sha256": hashlib.sha256(tsv_bytes(rows)).hexdigest(),
        "historical_eas001_relation": {
            "same_inventory": False,
            "historical_counts": {"arrays": 46, "slots": 391, "physical_folios": 13},
            "current_counts": {"arrays": 45, "slots": 504, "physical_folios": 7},
            "historical_score_inherited": False,
        },
        "claim_ceiling": (
            "This is a new filler-blind source inventory of 45 human-defined special-circle arrays and 504 slots, including "
            "one unreadable trace slot and one explicitly absent slot. One true absence on one folio cannot support an "
            "omission-pattern test. The inventory does "
            "not reconstruct or validate historical EAS001, establish record boundaries, equate slots across diagrams, or "
            "supply any direction, month, star, nymph, object, field, word, sound, language, cipher, plaintext, meaning, or "
            "translation."
        ),
    }
    report = (
        "# Special-circle text-blind array inventory\n\n"
        "Status: **PASS — CORRECTED VERSIONED FILLER-BLIND INVENTORY**.\n\n"
        "A mechanical scan of the current human exact-locus annotation table selects **45 arrays**, **504 slots**, "
        "**502 transcribed label/radial slots**, **1 unreadable trace slot**, and **1 source-explicit absent slot** across **23 page panels** on "
        "**7 physical folios** from f67 through f73. Selection uses only page, unit, and human layout code; no Voynich "
        "surface, family, member, root, parser role, gloss, or image feature enters.\n\n"
        "This is not the lost historical EAS001 inventory: its 45/504/7 scope differs from the historical 46/391/13 "
        "summary, and no historical score is inherited. The two nontranscribed rows are not homologous omissions: "
        "f67v2.21 retains unreadable ink traces, while only f72r2.33 is explicitly unlabelled. One secure absence on one "
        "folio is insufficient for an omission-pattern test. "
        "It establishes no record boundary or cross-diagram slot equivalence and supplies no direction, month, star, nymph, "
        "object, field, word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    return rows, result, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows, result, report = build()
    if args.write:
        OUT_TSV.write_bytes(tsv_bytes(rows))
        OUT_JSON.write_bytes(canonical(result))
        OUT_MD.write_text(report, encoding="utf-8")
    else:
        print(canonical(result).decode(), end="")


if __name__ == "__main__":
    main()
