#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_THIRTEENTH_TWO_PORTABLE_REVISIONS.tsv", "TWO_HUNDRED_THIRTEENTH_173_CARD_CROSS_REGISTER_DICTIONARY.tsv", "TWO_HUNDRED_THIRTEENTH_381_EVENT_CROSS_REGISTER_PROSE.tsv", "TWO_HUNDRED_THIRTEENTH_116_STATEMENT_CROSS_REGISTER_PROSE.tsv", "TWO_HUNDRED_THIRTEENTH_395_ASTRO_SURFACE_BRIDGE.tsv", "TWO_HUNDRED_THIRTEENTH_13_ASTRO_BRIDGE_CARD_SUMMARY.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    revisions = read("TWO_HUNDRED_THIRTEENTH_TWO_PORTABLE_REVISIONS.tsv")
    dictionary = read("TWO_HUNDRED_THIRTEENTH_173_CARD_CROSS_REGISTER_DICTIONARY.tsv")
    events = read("TWO_HUNDRED_THIRTEENTH_381_EVENT_CROSS_REGISTER_PROSE.tsv")
    statements = read("TWO_HUNDRED_THIRTEENTH_116_STATEMENT_CROSS_REGISTER_PROSE.tsv")
    astro = read("TWO_HUNDRED_THIRTEENTH_395_ASTRO_SURFACE_BRIDGE.tsv")
    cards = read("TWO_HUNDRED_THIRTEENTH_13_ASTRO_BRIDGE_CARD_SUMMARY.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    values = {row["master_card_id"]: row["current_value_de"] for row in dictionary}
    checks = {
        "two_revisions": len(revisions) == 2 and {row["master_card_id"] for row in revisions} == {"MC039", "MC119"},
        "selected_abstract_values": values["MC039"] == "Sollwert" and values["MC119"] == "Freigabewert",
        "173_381_116": len(dictionary) == 173 and len(events) == 381 and len(statements) == 116,
        "event_values_match": all(row["portable_value_de"] == values[row["master_card_id"]] for row in events),
        "statement_literals_match": all(row["literal_card_reading"] == " | ".join(event["portable_value_de"] for event in events if event["statement_id"] == row["statement_id"]) for row in statements),
        "395_astro_groups": len(astro) == 395,
        "89_all_prose_matches": summary["all_prose_surface_matches"] == 89,
        "66_bridge_matches": summary["bridge_surface_matches"] == 66,
        "13_bridge_cards": len(cards) == 13 and summary["bridge_cards_in_astro"] == 13,
        "page_split": summary["bridge_matches_by_page"] == {"f67r2": 29, "f68r1": 4, "f69v": 33},
        "172_distinct_values_preserved": summary["distinct_values_before"] == 172 and summary["distinct_values_after"] == 172,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "fixed_pages_only": {row["page"] for row in astro} == {"f67r2", "f68r1", "f69v"},
        "sealed_absent": not any("f84" in value.lower() for rows in (revisions, dictionary, events, statements, astro, cards) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_thirteenth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
