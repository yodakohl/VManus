#!/usr/bin/env python3
"""Validate Pass 1016 local-channel compression."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1015 = ROOT / "experiments/yolo/sidequest_semantic_627_core_owner_edition_one_thousand_fifteenth"
SOURCE_EDITION = PASS1015 / "PASS1015_627_CORE_OWNER_EDITION.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(name: str, condition: bool) -> dict[str, object]:
    return {"name": name, "passed": bool(condition)}


def main() -> None:
    source = read(SOURCE_EDITION)
    signs = read(HERE / "PASS1016_19_LOCAL_SIGN_CHANNELS.tsv")
    channels = read(HERE / "PASS1016_FOUR_LOCAL_CHANNELS.tsv")
    edition = read(HERE / "PASS1016_627_LOCAL_CHANNEL_EDITION.tsv")
    source_by_id = {row["statement_id"]: row for row in source}
    edition_by_id = {row["statement_id"]: row for row in edition}
    summary = json.loads((HERE / "PASS1016_BUILD_SUMMARY.json").read_text())

    checks = [
        check("nineteen_local_signs", len(signs) == 19),
        check("four_local_channels", len(channels) == 4),
        check("all_signs_mapped_once", len({row["sign"] for row in signs}) == 19 and all(row["pass1016_channel"] in {c["channel"] for c in channels} for row in signs)),
        check("local_mentions_527", sum(int(row["running_mentions"]) for row in signs) == 527),
        check("local_events_490", summary["local_event_count"] == 490),
        check("local_statements_210", summary["local_statement_count"] == 210),
        check("place_mentions_473", next(row for row in channels if row["channel"] == "LOCAL_PLACE")["running_mentions"] == "473"),
        check("three_dormant_running_signs", summary["dormant_running_signs"] == ["LOCAL_CHAR_Z", "S_LABEL", "Z_ADDR"]),
        check("statement_count_627", len(source) == len(edition) == 627),
        check("event_count_3888", sum(int(row["event_count"]) for row in edition) == 3888),
        check("same_statement_set", set(source_by_id) == set(edition_by_id)),
        check("surfaces_preserved", all(row["surface_sequence"] == source_by_id[row["statement_id"]]["surface_sequence"] for row in edition)),
        check("components_preserved", all(row["component_sequence"] == source_by_id[row["statement_id"]]["component_sequence"] for row in edition)),
        check("translations_preserved", all(row["pass1015_core_owner_translation_de"] == source_by_id[row["statement_id"]]["pass1015_core_owner_translation_de"] for row in edition)),
        check("all_category_count_31", all(row["pass1016_semantic_category_count"] == "31" for row in edition)),
        check("all_results_complete", all(row["pass1016_result"] == "LOCAL_SIGNS_MAPPED_TO_FOUR_CHANNELS" for row in edition)),
        check("no_unknown_local_channel", all(row["local_channel_sequence"] in {"NONE", "LOCAL_PLACE", "LOCAL_INDEX", "LOCAL_CLASS", "LOCAL_REFERENCE"} or "+" in row["local_channel_sequence"] for row in edition)),
        check("no_sealed_pages", not any("f84" in "\t".join(row.values()).casefold() for row in edition)),
    ]

    before = {path.name: path.read_bytes() for path in HERE.glob("PASS1016_*") if path.name != "PASS1016_VALIDATION.json"}
    subprocess.run(["python3", str(HERE / "build_pass1016.py")], cwd=ROOT, check=True)
    after = {path.name: path.read_bytes() for path in HERE.glob("PASS1016_*") if path.name != "PASS1016_VALIDATION.json"}
    checks.append(check("deterministic_rebuild", before == after))

    result = {
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
    }
    (HERE / "PASS1016_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        for item in checks:
            if not item["passed"]:
                print("FAIL", item["name"])
        raise SystemExit(1)
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
