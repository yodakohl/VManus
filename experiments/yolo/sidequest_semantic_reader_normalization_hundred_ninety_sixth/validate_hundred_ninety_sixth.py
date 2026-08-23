#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    surfaces = read("HUNDRED_NINETY_SIXTH_230_SURFACE_NORMALIZATION.tsv")
    aliases = read("HUNDRED_NINETY_SIXTH_57_ALIAS_NORMALIZATION.tsv")
    rules = read("HUNDRED_NINETY_SIXTH_10_READER_RULES.tsv")
    observed = read("HUNDRED_NINETY_SIXTH_381_EVENT_READER_AUDIT.tsv")
    parallel = read("HUNDRED_NINETY_SIXTH_25_TOKEN_TWO_HAND_NORMALIZATION.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "230_unique_surfaces": len(surfaces) == 230 and len({row["surface"] for row in surfaces}) == 230,
        "173_master_forms": sum(row["is_master_form"] == "YES" for row in surfaces) == 173,
        "57_aliases": len(aliases) == 57 and all(row["is_master_form"] == "NO" for row in aliases),
        "ten_rules": len(rules) == 10 and sum(int(row["alias_surfaces"]) for row in rules) == 57,
        "381_readback": len(observed) == 381 and all(row["exact_readback"] == "YES" for row in observed),
        "25_parallel_readback": len(parallel) == 25 and all(row["same_card_readback"] == "YES" for row in parallel),
        "no_empty_values": all(row["portable_value_de"] for row in surfaces),
        "sealed_absent": summary["sealed_pages_accessed"] is False,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
