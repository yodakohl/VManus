#!/usr/bin/env python3
"""Build the source-only, direction-masked balanced pair panel."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/semantic_assumptions/directional_label_placement_capacity/HORIZONTAL_SOURCE_PANEL.tsv"
OUTPUT = ROOT / "experiments/semantic_assumptions/directional_label_placement/MASKED_PAIR_PANEL.tsv"
AUDIT = ROOT / "experiments/semantic_assumptions/directional_label_placement/PAIRING_AUDIT.json"
SALT = "DIRECTIONPLACEMENT001"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def natural(value: str) -> tuple[object, ...]:
    return tuple(int(x) if x.isdigit() else x for x in re.split(r"(\d+)", value))


def ranks(total: int, retained: int) -> list[int]:
    if not 1 <= retained <= total:
        raise ValueError("invalid retained count")
    if retained == 1:
        return [(total - 1) // 2]
    denominator = retained - 1
    return [
        (index * (total - 1) + denominator // 2) // denominator
        for index in range(retained)
    ]


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    groups = defaultdict(list)
    for row in rows:
        groups[row["stratum_id"]].append(row)

    output = []
    retained_counts = Counter()
    for stratum, members in sorted(groups.items(), key=lambda item: natural(item[0])):
        east = sorted(
            (row for row in members if row["class"] == "EAST"),
            key=lambda row: natural(row["source_locus"]),
        )
        west = sorted(
            (row for row in members if row["class"] == "WEST"),
            key=lambda row: natural(row["source_locus"]),
        )
        if not east or not west:
            raise ValueError(f"unmatched stratum: {stratum}")
        if len(east) >= len(west):
            east = [east[index] for index in ranks(len(east), len(west))]
        else:
            west = [west[index] for index in ranks(len(west), len(east))]
        for number, (east_row, west_row) in enumerate(zip(east, west), 1):
            pair_id = f"{stratum}|P{number:02d}"
            members_by_mask = sorted(
                (east_row, west_row),
                key=lambda row: hashlib.sha256(
                    f"{SALT}|{pair_id}|{row['source_locus']}".encode()
                ).hexdigest(),
            )
            for side, row in zip(("A", "B"), members_by_mask):
                output.append(
                    {
                        "pair_id": pair_id,
                        "side": side,
                        "physical_folio": row["physical_folio"],
                        "page": row["page"],
                        "stratum_id": stratum,
                        "source_locus": row["source_locus"],
                        "normalized_code": row["normalized_code"],
                        "object_tags": row["object_tags"],
                        "readings": row["readings"],
                    }
                )
                retained_counts[row["physical_folio"]] += 1

    fields = [
        "pair_id", "side", "physical_folio", "page", "stratum_id",
        "source_locus", "normalized_code", "object_tags", "readings",
    ]
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    assert len(output) == 32
    assert len({row["pair_id"] for row in output}) == 16
    assert len({row["source_locus"] for row in output}) == 32
    assert set(retained_counts) == {"f68", "f88", "f89", "f99", "f100", "f102"}
    assert "class" not in fields and "EAST" not in OUTPUT.read_text() and "WEST" not in OUTPUT.read_text()
    payload = {
        "status": "PASS_SOURCE_ORDER_BALANCED_MASKED_PAIRS",
        "source_sha256": digest(SOURCE),
        "output_sha256": digest(OUTPUT),
        "pair_count": 16,
        "locus_count": 32,
        "physical_folios": 6,
        "rows_by_folio": dict(sorted(retained_counts.items(), key=lambda item: natural(item[0]))),
        "mask_salt": SALT,
        "direction_column_present": False,
        "voynich_strings_read": False,
        "target_assignment_extracted": False,
    }
    AUDIT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
