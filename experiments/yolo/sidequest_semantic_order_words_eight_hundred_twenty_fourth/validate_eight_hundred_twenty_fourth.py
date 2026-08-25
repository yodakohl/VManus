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
    subprocess.run(["python", str(HERE / "build_eight_hundred_twenty_fourth.py")], check=True)
    audit = read("EIGHT_HUNDRED_TWENTY_FOURTH_75_ORDER_MEMBERSHIPS.tsv")
    distinctions = read("EIGHT_HUNDRED_TWENTY_FOURTH_3_ORDER_DISTINCTIONS.tsv")
    candidates = read("EIGHT_HUNDRED_TWENTY_FOURTH_6_OS_CANDIDATES.tsv")
    trace = read("EIGHT_HUNDRED_TWENTY_FOURTH_7_H1_LOCAL_TRACE.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_TWENTY_FOURTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = Counter(row["component"] for row in audit)
    checks = {
        "seventy_five_memberships": len(audit) == 75 and counts == Counter({"OL": 48, "OT": 26, "OS": 1}),
        "seventy_two_unique_events": summary["unique_events"] == 72,
        "three_distinct_roles": len(distinctions) == 3 and all(row["decision"] == "KEEP" for row in distinctions),
        "orthogonal_role_flags": {(row["same_operation"], row["next_operation"], row["additive_only"]) for row in distinctions} == {("YES", "NO", "NO"), ("NO", "YES", "NO"), ("NO", "NO", "YES")},
        "os_candidate_kept": len(candidates) == 6 and next(row for row in candidates if row["decision"] == "KEEP")["candidate"] == "DAZU",
        "h1_has_os_then_ot": [row["order_role"] for row in trace].count("ADDITIVE_OS") == 1 and [row["order_role"] for row in trace].count("NEXT_OT") == 1 and next(i for i,row in enumerate(trace) if row["order_role"] == "ADDITIVE_OS") < next(i for i,row in enumerate(trace) if row["order_role"] == "NEXT_OT"),
        "no_revision": summary["meaning_revisions"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_TWENTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
