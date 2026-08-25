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
    subprocess.run(["python", str(HERE / "build_eight_hundred_twenty_second.py")], check=True)
    candidates = read("EIGHT_HUNDRED_TWENTY_SECOND_6_P_CANDIDATES.tsv")
    events = read("EIGHT_HUNDRED_TWENTY_SECOND_3_P_EVENTS.tsv")
    statements = read("EIGHT_HUNDRED_TWENTY_SECOND_3_REVISED_STATEMENTS.tsv")
    audit = read("EIGHT_HUNDRED_TWENTY_SECOND_51_TRANSFER_MEMBERSHIPS.tsv")
    distinctions = read("EIGHT_HUNDRED_TWENTY_SECOND_3_TRANSFER_DISTINCTIONS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_TWENTY_SECOND_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = Counter(row["component"] for row in audit)
    checks = {
        "three_p_cards_events_statements": len(events) == 3 and len(statements) == 3 and len({row["surface"] for row in events}) == 3,
        "p_literal_revised": all("EINBRINGEN" in row["revised_literal_de"] and "EINFUELLEN" not in row["revised_literal_de"] for row in events),
        "statements_revised": all("einbring" in row["revised_reading_de"].lower() and "einfuell" not in row["revised_reading_de"].lower() for row in statements),
        "candidate_selected_once": len(candidates) == 6 and sum(row["decision"] == "SELECT_CORE_VALUE" for row in candidates) == 1,
        "transfer_counts": len(audit) == 51 and counts == Counter({"L": 27, "K": 21, "P": 3}),
        "fifty_unique_transfer_events": summary["unique_transfer_events"] == 50,
        "three_distinctions": len(distinctions) == 3 and {row["short_value_de"] for row in distinctions} == {"ZUGEBEN", "EINBRINGEN", "LEITEN"},
        "two_visible_one_local_receiver": Counter(row["receiver_status"] for row in events) == Counter({"VISIBLE_RECEIVER": 2, "LOCAL_WORK_SITE_ONLY": 1}),
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_TWENTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
