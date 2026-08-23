#!/usr/bin/env python3
"""Validate root and learned-body domain cue coverage."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read_tsv("SEVENTY_FIRST_28_ROOT_REGISTER_PROFILES.tsv")
    learned = read_tsv("SEVENTY_FIRST_54_LEARNED_BODY_CUES.tsv")
    groups = read_tsv("SEVENTY_FIRST_381_GROUP_DOMAIN_CUE_MAP.tsv")
    units = read_tsv("SEVENTY_FIRST_14_UNIT_DOMAIN_CUE_DECISIONS.tsv")
    checks = {
        "twenty_eight_roots": len(roots) == 28 and len({row["root"] for row in roots}) == 28,
        "all_roots_profiled": all(int(row["herbal_group_occurrences"]) + int(row["bio_group_occurrences"]) > 0 for row in roots),
        "no_root_declared_body_specific": all(row["body_or_patient_specific"] == "NO" for row in roots),
        "fifty_four_learned_body_occurrences": len(learned) == 54 and len({row["source_group_id"] for row in learned}) == 54,
        "381_groups": len(groups) == 381 and len({row["source_group_id"] for row in groups}) == 381,
        "fourteen_units": len(units) == 14 and len({row["unit_id"] for row in units}) == 14,
        "all_groups_require_context_for_domain": all(row["domain_decision_from_card_alone"] == "NONE" and row["owner_or_master_required"] == "YES" for row in groups),
        "allowed_pages": {row["page"] for row in groups + units} == ALLOWED,
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in roots + learned + groups + units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
