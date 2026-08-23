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
    names = ["TWO_HUNDRED_ELEVENTH_17_CROSS_REGISTER_CARDS.tsv", "TWO_HUNDRED_ELEVENTH_136_BRIDGE_OCCURRENCES.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    cards = read("TWO_HUNDRED_ELEVENTH_17_CROSS_REGISTER_CARDS.tsv")
    occurrences = read("TWO_HUNDRED_ELEVENTH_136_BRIDGE_OCCURRENCES.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    values = {row["master_card_id"]: row["invariant_value_de"] for row in cards}
    checks = {
        "17_bridge_cards": len(cards) == 17 and len(values) == 17,
        "136_occurrences": len(occurrences) == 136 and len({row["event_id"] for row in occurrences}) == 136,
        "44_herbal_92_bio": summary["herbal_bridge_occurrences"] == 44 and summary["bio_bridge_occurrences"] == 92,
        "16_productive_one_whole": summary["productive_bridge_cards"] == 16 and summary["whole_bridge_cards"] == 1,
        "every_card_in_both_sections": all(int(row["herbal_occurrences"]) > 0 and int(row["bio_occurrences"]) > 0 for row in cards),
        "values_invariant": all(row["invariant_value_de"] == values[row["master_card_id"]] for row in occurrences),
        "all_contexts_present": all(row["left_value_de"] and row["right_value_de"] for row in occurrences),
        "381_source_events": summary["all_prose_events"] == 381,
        "sole_whole_bridge_is_klarlauf": next(row for row in cards if row["master_card_id"] == "MC119")["invariant_value_de"] == "Klarlauf",
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": not any("f84" in value.lower() for rows in (cards, occurrences) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_eleventh.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
