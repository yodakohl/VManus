#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_twenty_third.py")], check=True)
    candidates = read("EIGHT_HUNDRED_TWENTY_THIRD_6_SHED_CANDIDATES.tsv")
    audit = read("EIGHT_HUNDRED_TWENTY_THIRD_40_HOLD_WAIT_MEMBERSHIPS.tsv")
    patterns = read("EIGHT_HUNDRED_TWENTY_THIRD_3_SHED_PATTERNS.tsv")
    distinctions = read("EIGHT_HUNDRED_TWENTY_THIRD_2_HOLD_WAIT_DISTINCTIONS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_TWENTY_THIRD_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = Counter(row["component"] for row in audit)
    pattern_counts = {row["pattern"]: int(row["events"]) for row in patterns}
    checks = {
        "forty_memberships": len(audit) == 40 and counts == Counter({"SH": 25, "SHED": 15}),
        "shed_patterns_exact": pattern_counts == {"SHED+DY": 12, "R+SHED+DY": 1, "SHED+AL": 2},
        "thirteen_closed_two_open": summary["shed_closed"] == 13 and summary["shed_open_target"] == 2,
        "candidate_kept_once": len(candidates) == 6 and sum(row["decision"] == "KEEP" for row in candidates) == 1 and next(row for row in candidates if row["decision"] == "KEEP")["candidate"] == "STEHENLASSEN",
        "distinction_active_released": len(distinctions) == 2 and {row["agent_control"] for row in distinctions} == {"ACTIVE", "RELEASED"},
        "all_full_contexts": all(row["full_statement_de"] for row in audit),
        "no_revision": summary["meaning_revisions"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_TWENTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
