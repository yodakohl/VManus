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
    subprocess.run(["python", str(HERE / "build_eight_hundred_twenty_fifth.py")], check=True)
    audit = read("EIGHT_HUNDRED_TWENTY_FIFTH_62_QUANTITY_MEMBERSHIPS.tsv")
    ladder = read("EIGHT_HUNDRED_TWENTY_FIFTH_4_LEVEL_LADDER.tsv")
    candidates = read("EIGHT_HUNDRED_TWENTY_FIFTH_6_S_CANDIDATES.tsv")
    trace = read("EIGHT_HUNDRED_TWENTY_FIFTH_6_S_LOCAL_TRACE.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_TWENTY_FIFTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = Counter(row["component"] for row in audit)
    checks = {
        "sixty_two_memberships": len(audit) == 62 and counts == Counter({"AIIN": 39, "AIN": 18, "IIN": 4, "S": 1}),
        "four_types_distinct": len(ladder) == 4 and len({row["ontological_type"] for row in ladder}) == 4,
        "s_kept_provisional": next(row for row in ladder if row["component"] == "S")["decision"] == "KEEP_PROVISIONAL",
        "candidate_selected": len(candidates) == 6 and next(row for row in candidates if row["decision"] == "KEEP_PROVISIONAL")["candidate"] == "PROBE",
        "sample_precedes_measure": next(i for i,row in enumerate(trace) if row["quantity_role"] == "SAMPLE") < next(i for i,row in enumerate(trace) if row["quantity_role"] == "PRESCRIBED_VALUE"),
        "all_contexts_present": all(row["full_statement_de"] for row in audit),
        "no_revision": summary["meaning_revisions"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_TWENTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
