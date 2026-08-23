#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    audit = rows("TWO_HUNDRED_FIFTY_SIXTH_23_WHOLE_SIGN_AUDIT.tsv")
    blockers = rows("TWO_HUNDRED_FIFTY_SIXTH_FOUR_LEXICAL_BLOCKERS.tsv")
    checks = {
        "23_whole_signs": len(audit) == 23 and len({r["master_card_id"] for r in audit}) == 23,
        "four_blockers": len(blockers) == 4 and len({r["master_card_id"] for r in blockers}) == 4,
        "four_pairs_exact": {r["missing_pair"] for r in blockers} == {"AR|AL", "AR|OL", "AR|OR", "AL|OL"},
        "selected_ids_exact": {r["master_card_id"] for r in blockers} == {"MC061", "MC124", "MC049", "MC068"},
        "one_selected_per_pair": len({r["missing_pair"] for r in blockers}) == len(blockers),
        "all_have_context": all(r["visible_contexts"].strip() and r["complete_context_readings_de"].strip() for r in blockers),
        "audit_selection_matches": {r["master_card_id"] for r in audit if r["candidate_status"] == "SELECTED_LEXICAL_BLOCKER"} == {r["master_card_id"] for r in blockers},
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in audit + blockers),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
