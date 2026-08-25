#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    audit = read("SEVEN_HUNDRED_SIXTY_EIGHTH_19_LINE_PACKER_AUDIT.tsv")
    lines = read("SEVEN_HUNDRED_SIXTY_EIGHTH_TRANSITION_LINE_WIDTHS.tsv")
    rules = read("SEVEN_HUNDRED_SIXTY_EIGHTH_5_PACKER_RULES.tsv")
    licenses = read("SEVEN_HUNDRED_SIXTY_EIGHTH_LOCAL_LAYOUT_LICENSE.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SIXTY_EIGHTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_rule = {row["rule_id"]: row for row in rules}
    copies = [row for row in audit if row["observed_edge_copy"] == "YES"]
    checks = {
        "nineteen_transitions": len(audit) == 19,
        "one_observed_copy_lt06": len(copies) == 1 and copies[0]["transition_id"] == "LT06",
        "space_nine_candidates": sum(row["space_proxy_fits"] == "YES" for row in audit) == 9,
        "space_rule_eight_false_positives": (by_rule["R1_SPACE_PROXY_ONLY"]["tp"], by_rule["R1_SPACE_PROXY_ONLY"]["fp"], by_rule["R1_SPACE_PROXY_ONLY"]["fn"]) == ("1", "8", "0"),
        "space_owner_six_false_positives": (by_rule["R2_SPACE_OWNER_NO_CLOSE"]["tp"], by_rule["R2_SPACE_OWNER_NO_CLOSE"]["fp"]) == ("1", "6"),
        "local_license_exact": (by_rule["R5_LOCAL_MASTER_LICENSE"]["tp"], by_rule["R5_LOCAL_MASTER_LICENSE"]["fp"], by_rule["R5_LOCAL_MASTER_LICENSE"]["fn"]) == ("1", "0", "0"),
        "one_non_general_license": len(licenses) == 1 and licenses[0]["generalize"] == "NO" and licenses[0]["source_event"] == "E181" and licenses[0]["rendered_edge_copy"] == "E180",
        "line_widths_nonempty": len(lines) >= 20 and all(int(row["char_width_proxy"]) > 0 for row in lines),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (audit, lines, rules, licenses) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["space_proxy_candidates"] == 9,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
