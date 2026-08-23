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
    names = ["TWO_HUNDRED_SEVENTH_TEN_PRODUCTIVE_PHRASE_FRAMES.tsv", "TWO_HUNDRED_SEVENTH_TEN_LEARNED_PHRASE_CHAINS.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    frames = read("TWO_HUNDRED_SEVENTH_TEN_PRODUCTIVE_PHRASE_FRAMES.tsv")
    chains = read("TWO_HUNDRED_SEVENTH_TEN_LEARNED_PHRASE_CHAINS.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "ten_productive_frames": len(frames) == 10 and len({row["frame_id"] for row in frames}) == 10,
        "all_frames_recur": all(int(row["occurrences"]) >= 3 for row in frames),
        "ten_learned_chains": len(chains) == 10 and len({row["chain_id"] for row in chains}) == 10,
        "chains_have_real_positions": all(int(row["start_position"]) >= 1 and int(row["token_count"]) >= 2 for row in chains),
        "22_statements_have_frames": summary["statements_touched_by_productive_frames"] == 22,
        "116_statements_source": summary["statements"] == 116,
        "381_events_source": summary["events"] == 381,
        "all_values_concrete": all(row["example_values_de"] and "UNKNOWN" not in row["example_values_de"] for row in frames),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": not any("f84" in value.lower() for rows in (frames, chains) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_seventh.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
