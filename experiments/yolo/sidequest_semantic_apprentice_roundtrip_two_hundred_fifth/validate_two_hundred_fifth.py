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
    names = ["TWO_HUNDRED_FIFTH_32_TOKEN_ROUNDTRIP.tsv", "TWO_HUNDRED_FIFTH_SIX_FIELD_WORKSHOP_TEXT.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    tokens = read("TWO_HUNDRED_FIFTH_32_TOKEN_ROUNDTRIP.tsv")
    fields = read("TWO_HUNDRED_FIFTH_SIX_FIELD_WORKSHOP_TEXT.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "six_fields": len(fields) == 6 and len({row["field_id"] for row in fields}) == 6,
        "32_tokens": len(tokens) == 32 and [int(row["sequence"]) for row in tokens] == list(range(1, 33)),
        "all_exact_readback": all(row["readback_status"] == "EXACT" for row in tokens),
        "all_card_ids_preserved": all(row["intended_card_id"] == row["decoded_card_id"] for row in tokens),
        "all_values_preserved": all(row["intended_value_de"] == row["decoded_value_de"] for row in tokens),
        "25_surface_changes": summary["hand_b_surface_changes"] == 25,
        "mixed_system_used": summary["whole_card_tokens"] == 7 and summary["productive_tokens"] == 25,
        "all_five_modes_used": {row["field_mode"] for row in fields} == {"CH", "D", "O", "Q", "S"},
        "nonempty_field_readings": all(row["source_instruction_de"] and row["literal_readback_de"] for row in fields),
        "not_manuscript_data": summary["new_manuscript_data_created"] is False,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": not any("f84" in value.lower() for rows in (tokens, fields) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_fifth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
