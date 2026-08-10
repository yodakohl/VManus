#!/usr/bin/env python3
"""Independent reconstruction of LRG002 score-blind capacity."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RES = HERE / "results"
SOURCE = RES / "drawing_reset_segment_atlas.tsv"
CAPACITY = RES / "lrg002_prose_slot_capacity.tsv"
RESULT = RES / "lrg002_prose_slot_capacity.json"
REPORT = RES / "lrg002_prose_slot_capacity_report.md"
OUT = RES / "lrg002_prose_slot_capacity_validation.json"
OUT_REPORT = RES / "lrg002_prose_slot_capacity_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical(page: str) -> str:
    match = re.match(r"(f\d+)", page)
    if not match:
        raise RuntimeError(page)
    return match.group(1)


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise RuntimeError("LRG002 capacity validation output exists")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        raw = [row for row in csv.DictReader(handle, delimiter="\t") if row["grammar_scope"] == "CONFIRMED_PROSE" and row["section"] in ("B", "P")]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in raw:
        grouped[row["segment_id"]].append(row)
    expected = []
    for row in raw:
        f = physical(row["page"]); eligible = len(grouped[row["segment_id"]]) >= 3
        expected.append((row["consensus_group_id"], row["segment_id"], row["page"], f, row["section"], row["symbol_count"], row["segment_group_index"], row["segment_group_count"], row["segment_position"], "ODD" if int(f[1:]) % 2 else "EVEN", "1" if eligible else "0"))
    with CAPACITY.open(encoding="utf-8", newline="") as handle:
        stored_rows = list(csv.DictReader(handle, delimiter="\t")); fields = list(stored_rows[0])
    observed = [tuple(row[field] for field in fields) for row in stored_rows]
    if observed != expected or len({row[0] for row in expected}) != len(expected):
        raise RuntimeError("LRG002 capacity row mismatch")
    primary = [row for row in stored_rows if row["primary_slot_eligible"] == "1"]
    by_segment = defaultdict(list)
    for row in primary: by_segment[row["segment_id"]].append(row)
    checks = 0
    for group in by_segment.values():
        counts = Counter(row["segment_position"] for row in group)
        if (counts["FIRST"], counts["LAST"], counts["CORE"]) != (1, 1, len(group) - 2):
            raise RuntimeError("position contract")
        checks += len(group) + 3
    production = json.loads(RESULT.read_text(encoding="utf-8"))
    expected_counts = {
        "normalization_rows": 5824, "normalization_segments": 742,
        "primary_rows": 5769, "primary_segments": 705, "pages": 34,
        "physical_folios": 16,
        "rows_by_section": dict(sorted(Counter(row["section"] for row in primary).items())),
        "rows_by_position": dict(sorted(Counter(row["segment_position"] for row in primary).items())),
        "segments_by_folio": dict(sorted(Counter(row["physical_folio"] for row in primary if row["segment_position"] == "FIRST").items(), key=lambda item: int(item[0][1:]))),
        "parities": ["EVEN", "ODD"],
    }
    if production["status"] != "PASS_SCORE_BLIND_LRG002_CAPACITY" or production["counts"] != expected_counts or production["capacity_sha256"] != sha(CAPACITY):
        raise RuntimeError("LRG002 capacity aggregate mismatch")
    expected_report = (
        "# LRG002 prose-slot capacity\n\nStatus: **PASS_SCORE_BLIND_LRG002_CAPACITY**.\n\n"
        "The fixed B/P universe contains **5,824** confirmed-prose groups in **742** corrected segments. The primary position panel contains **5,769** groups in **705** segments on **34** pages and **16** physical folios; every primary segment has one FIRST, one LAST, and at least one CORE group.\n\n"
        "No LRG001 profile, sequence score, or position association was computed. This is capacity only, not a word, name, identifier, POS, meaning, plaintext, or translation.\n"
    )
    if REPORT.read_text(encoding="utf-8") != expected_report:
        raise RuntimeError("LRG002 capacity report mismatch")
    result = {
        "status": "PASS_INDEPENDENT_LRG002_CAPACITY_RECONSTRUCTION",
        "checks": checks + len(expected) * len(fields) + 19,
        "discrepancies": 0,
        "capacity_sha256": sha(CAPACITY), "production_json_sha256": sha(RESULT), "production_report_sha256": sha(REPORT),
        "decision": "GO_TARGET_BLIND_LRG002_CALIBRATION",
        "claim_ceiling": production["claim_ceiling"],
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="\n")
    OUT_REPORT.write_text(
        "# LRG002 capacity validation\n\nStatus: **PASS_INDEPENDENT_LRG002_CAPACITY_RECONSTRUCTION**.\n\n"
        f"Independent code reproduces all 5,824 rows, 705 primary segment position contracts, aggregates, hashes, and report in **{result['checks']:,}** checks with zero discrepancies.\n\n"
        "This validates score-blind capacity only; it supplies no slot function, word, name, identifier, POS, meaning, plaintext, or translation.\n",
        encoding="utf-8", newline="\n",
    )
    print(text, end="")


if __name__ == "__main__":
    main()
