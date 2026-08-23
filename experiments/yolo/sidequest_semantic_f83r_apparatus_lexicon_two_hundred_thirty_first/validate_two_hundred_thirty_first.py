#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARTIFACTS = [
    "TWO_HUNDRED_THIRTY_FIRST_EIGHT_LOCAL_CARD_ANALYSES.tsv",
    "TWO_HUNDRED_THIRTY_FIRST_APPARATUS_COMPOSITION_RULES.tsv",
    "TWO_HUNDRED_THIRTY_FIRST_FIVE_PHASE_APPARATUS_LEXICON.tsv",
    "TWO_HUNDRED_THIRTY_FIRST_READABLE_APPARATUS_LEXICON.md",
    "TWO_HUNDRED_THIRTY_FIRST_REPORT.md",
    "BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ARTIFACTS}


def main() -> None:
    cards = read(ARTIFACTS[0])
    rules = read(ARTIFACTS[1])
    phases = read(ARTIFACTS[2])
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "eight_exact_cards": len(cards) == 8 and len({row["master_card_id"] for row in cards}) == 8,
        "five_two_one_split": summary["fully_compositional"] == 5 and summary["compositional_with_renderer_hull"] == 2 and summary["learned_whole_cards"] == 1,
        "only_lo_whole": {row["visible_surface"] for row in cards if row["new_analysis_status"] == "LEARNED_WHOLE_CARD"} == {"lo"},
        "exact_events": {row["event_id"] for row in cards} == {"E231", "E240", "E248", "E250", "E253", "E260", "E261", "E263"},
        "six_rules": len(rules) == 6,
        "five_phases": len(phases) == 5,
        "all_values_short": all(0 < len(row["selected_short_value_de"].split()) <= 5 for row in cards),
        "no_station_noun_in_card_value": all(not any(noun in row["selected_short_value_de"].lower() for noun in ("gefäß", "station", "becken")) for row in cards),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in " ".join((OUT / name).read_text(encoding="utf-8").lower() for name in ARTIFACTS),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_thirty_first.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
