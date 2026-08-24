#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("THREE_HUNDRED_SIXTY_FIFTH_380_CARD_RECONSTRUCTION.tsv")
    statements = read("THREE_HUNDRED_SIXTY_FIFTH_116_STATEMENT_RECONSTRUCTION.tsv")
    records = read("THREE_HUNDRED_SIXTY_FIFTH_11_RECORD_RECONSTRUCTION.tsv")
    checks = {
        "380_cards": len(cards) == 380 and len({r["source_position_id"] for r in cards}) == 380,
        "all_values_exact": all(r["exact_value"] == "YES" for r in cards),
        "all_identities_exact": all(r["exact_identity"] == "YES" for r in cards),
        "all_surfaces_exact": all(r["exact_surface"] == "YES" for r in cards),
        "72_pair_events": sum(r["pair_id"] != "NONE" for r in cards) == 72,
        "14_pair_ids": len({r["pair_id"] for r in cards if r["pair_id"] != "NONE"}) == 14,
        "pair_routes_contextual": all(r["context_cue"] != "NONE" for r in cards if r["pair_id"] != "NONE"),
        "116_statements": len(statements) == 116 and all(r["exact_statement"] == "YES" for r in statements),
        "statement_events_once": sorted(r["event_id"] for r in cards) == sorted(e for r in statements for e in r["source_event_ids"].split("|")),
        "11_records": len(records) == 11 and all(r["exact_record"] == "YES" for r in records),
        "record_counts_sum": sum(int(r["source_cards"]) for r in records) == 380,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SIXTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
