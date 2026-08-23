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
    names = ["TWO_HUNDRED_EIGHTH_22_TOKEN_LICENSED_ROUNDTRIP.tsv", "TWO_HUNDRED_EIGHTH_SIX_LICENSED_FIELDS.tsv", "TWO_HUNDRED_EIGHTH_16_LICENSED_BRIDGES.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    tokens = read("TWO_HUNDRED_EIGHTH_22_TOKEN_LICENSED_ROUNDTRIP.tsv")
    fields = read("TWO_HUNDRED_EIGHTH_SIX_LICENSED_FIELDS.tsv")
    bridges = read("TWO_HUNDRED_EIGHTH_16_LICENSED_BRIDGES.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    expected_frames = {"PF01", "PF03", "PF07", "PF09"}
    expected_chains = {"LC02", "LC04"}
    checks = {
        "six_fields": len(fields) == 6,
        "22_tokens": len(tokens) == 22 and [int(row["sequence"]) for row in tokens] == list(range(1, 23)),
        "16_bridges": len(bridges) == 16,
        "all_bridges_licensed": all(row["bridge_status"].startswith("LICENSED") for row in bridges),
        "four_frame_fields": {row["license_id"] for row in fields if row["license_type"] == "PRODUCTIVE_FRAME"} == expected_frames,
        "two_chain_fields": {row["license_id"] for row in fields if row["license_type"] == "LEARNED_CHAIN"} == expected_chains,
        "all_readbacks_exact": all(row["readback_status"] == "EXACT" and row["intended_card_id"] == row["decoded_card_id"] for row in tokens),
        "five_modes_used": {row["field_mode"] for row in fields} == {"CH", "D", "O", "Q", "S"},
        "no_unlicensed_bridge": summary["unlicensed_bridges"] == 0,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": not any("f84" in value.lower() for rows in (tokens, fields, bridges) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_eighth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
