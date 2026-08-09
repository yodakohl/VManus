#!/usr/bin/env python3
"""Independent source-only validation of the masked balanced pair panel."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/semantic_assumptions/directional_label_placement_capacity/HORIZONTAL_SOURCE_PANEL.tsv"
PANEL = ROOT / "experiments/semantic_assumptions/directional_label_placement/MASKED_PAIR_PANEL.tsv"
AUDIT = ROOT / "experiments/semantic_assumptions/directional_label_placement/PAIRING_AUDIT.json"
OUTPUT = ROOT / "experiments/semantic_assumptions/directional_label_placement/PAIRING_VALIDATION.json"
SALT = "DIRECTIONPLACEMENT001"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(value: str):
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value))


def choose(total: int, count: int):
    if count == 1:
        return [(total - 1) // 2]
    denominator = count - 1
    return [(j * (total - 1) + denominator // 2) // denominator for j in range(count)]


def main() -> None:
    source = list(csv.DictReader(SOURCE.open(newline="", encoding="utf-8"), delimiter="\t"))
    disk = list(csv.DictReader(PANEL.open(newline="", encoding="utf-8"), delimiter="\t"))
    audit = json.loads(AUDIT.read_text())
    groups = defaultdict(list)
    source_by_locus = {}
    for row in source:
        groups[row["stratum_id"]].append(row)
        source_by_locus[row["source_locus"]] = row
    expected = []
    for stratum, rows in sorted(groups.items(), key=lambda item: key(item[0])):
        east = sorted([r for r in rows if r["class"] == "EAST"], key=lambda r: key(r["source_locus"]))
        west = sorted([r for r in rows if r["class"] == "WEST"], key=lambda r: key(r["source_locus"]))
        if len(east) >= len(west):
            east = [east[i] for i in choose(len(east), len(west))]
        else:
            west = [west[i] for i in choose(len(west), len(east))]
        for number, pair in enumerate(zip(east, west), 1):
            pair_id = f"{stratum}|P{number:02d}"
            ordered = sorted(pair, key=lambda r: hashlib.sha256(f"{SALT}|{pair_id}|{r['source_locus']}".encode()).hexdigest())
            for side, row in zip(("A", "B"), ordered):
                expected.append({
                    "pair_id": pair_id, "side": side,
                    "physical_folio": row["physical_folio"], "page": row["page"],
                    "stratum_id": stratum, "source_locus": row["source_locus"],
                    "normalized_code": row["normalized_code"], "object_tags": row["object_tags"],
                    "readings": row["readings"],
                })
    pair_classes = defaultdict(set)
    for row in disk:
        pair_classes[row["pair_id"]].add(source_by_locus[row["source_locus"]]["class"])
    checks = {
        "source_hash": audit["source_sha256"] == sha(SOURCE),
        "panel_hash": audit["output_sha256"] == sha(PANEL),
        "exact_reconstruction": disk == expected,
        "sixteen_pairs": len({r["pair_id"] for r in disk}) == 16,
        "thirty_two_unique_loci": len(disk) == len({r["source_locus"] for r in disk}) == 32,
        "two_sides_each": all(Counter(r["side"] for r in disk if r["pair_id"] == pair) == {"A": 1, "B": 1} for pair in pair_classes),
        "one_east_one_west_each": all(classes == {"EAST", "WEST"} for classes in pair_classes.values()),
        "same_stratum_each": all(len({r["stratum_id"] for r in disk if r["pair_id"] == pair}) == 1 for pair in pair_classes),
        "six_folios": len({r["physical_folio"] for r in disk}) == 6,
        "direction_masked": "class" not in disk[0] and "EAST" not in PANEL.read_text() and "WEST" not in PANEL.read_text(),
        "no_voynich_string_access": audit["voynich_strings_read"] is False,
        "target_unextracted": audit["target_assignment_extracted"] is False,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "checks": checks,
        "panel_sha256": sha(PANEL),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
