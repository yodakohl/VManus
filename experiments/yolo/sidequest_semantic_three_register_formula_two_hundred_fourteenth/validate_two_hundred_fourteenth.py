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
    names = ["TWO_HUNDRED_FOURTEENTH_10_THREE_REGISTER_TOKENS.tsv", "TWO_HUNDRED_FOURTEENTH_FOUR_PARALLEL_FIELDS.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    tokens = read("TWO_HUNDRED_FOURTEENTH_10_THREE_REGISTER_TOKENS.tsv")
    fields = read("TWO_HUNDRED_FOURTEENTH_FOUR_PARALLEL_FIELDS.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "four_fields": len(fields) == 4,
        "ten_tokens": len(tokens) == 10 and [int(row["sequence"]) for row in tokens] == list(range(1, 11)),
        "eight_unique_cards": summary["unique_cards"] == 8,
        "all_surfaces_attested_in_astro": summary["all_selected_surfaces_seen_in_astro"] is True,
        "all_surfaces_registered": all(row["selected_surface"] in row["registered_surfaces"].split("|") for row in tokens),
        "values_identical_all_registers": all(row["portable_value_de"] == row["herbal_value_de"] == row["bio_value_de"] == row["astro_value_de"] for row in tokens),
        "zero_changed_values": summary["changed_values"] == 0,
        "all_expansions_present": all(row["herbal_expansion_de"] and row["bio_expansion_de"] and row["astro_expansion_de"] for row in fields),
        "revised_values_used": any(row["portable_value_de"] == "Sollwert" for row in tokens) and any(row["portable_value_de"] == "Freigabewert" for row in tokens),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": not any("f84" in value.lower() for rows in (tokens, fields) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_fourteenth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
