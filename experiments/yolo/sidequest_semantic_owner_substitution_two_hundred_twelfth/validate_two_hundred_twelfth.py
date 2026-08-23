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
    names = ["TWO_HUNDRED_TWELFTH_10_IDENTICAL_BRIDGE_TOKENS.tsv", "TWO_HUNDRED_TWELFTH_FOUR_OWNER_SUBSTITUTIONS.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    tokens = read("TWO_HUNDRED_TWELFTH_10_IDENTICAL_BRIDGE_TOKENS.tsv")
    fields = read("TWO_HUNDRED_TWELFTH_FOUR_OWNER_SUBSTITUTIONS.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "four_fields": len(fields) == 4,
        "ten_tokens": len(tokens) == 10 and [int(row["sequence"]) for row in tokens] == list(range(1, 11)),
        "nine_unique_cards": summary["unique_cards"] == 9,
        "all_values_identical": all(row["invariant_card_value_de"] == row["herbal_card_value_de"] == row["bio_card_value_de"] for row in tokens),
        "no_value_changed": summary["changed_card_values"] == 0,
        "every_field_same_stream": all(row["card_stream_identical"] == "YES" for row in fields),
        "three_frames_one_whole": summary["phrase_licensed_fields"] == 3 and summary["whole_card_fields"] == 1,
        "owner_words_differ": all(row["herbal_owner_supplied_words"] != row["bio_owner_supplied_words"] for row in fields),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": not any("f84" in value.lower() for rows in (tokens, fields) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_twelfth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
