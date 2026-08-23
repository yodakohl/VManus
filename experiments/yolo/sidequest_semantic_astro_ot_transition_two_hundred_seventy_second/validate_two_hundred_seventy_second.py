#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rows = read("TWO_HUNDRED_SEVENTY_SECOND_26_OT_TRANSITIONS.tsv")
    forms = read("TWO_HUNDRED_SEVENTY_SECOND_25_OT_FORMS.tsv")
    registers = read("TWO_HUNDRED_SEVENTY_SECOND_REGISTER_TRANSFER.tsv")
    revised = read("TWO_HUNDRED_SEVENTY_SECOND_REVISED_395_ASTRO_GROUPS.tsv")
    checks = {
        "26_transitions": len(rows) == 26,
        "25_forms": len(forms) == 25,
        "all_three_pages": {r["page"] for r in rows} == {"f67r2", "f68r1", "f69v"},
        "page_counts": Counter(r["page"] for r in rows) == {"f67r2": 3, "f68r1": 7, "f69v": 16},
        "all_contain_ot": all("ot" in r["visible_surface"] for r in rows),
        "all_following_post": all(r["portable_ot_value_de"] == "FOLGEPOSTEN" for r in rows),
        "four_register_rows": len(registers) == 4,
        "total_58": next(r for r in registers if r["register"] == "TOTAL")["known_ot_uses"] == "58",
        "395_revised": len(revised) == 395,
        "26_revision_flags": sum(r["revision_272"] == "OT_FOLLOWING_POST" for r in revised) == 26,
        "prior_relation_flags_preserved": sum(r["revision_271"] == "OR_OL_RELATION_SUFFIX" for r in revised) == 25,
        "sealed_pages_absent": all(r["page"] not in {"f84", "f84r"} for r in revised),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    (OUT / "VALIDATION.json").write_text(json.dumps({"status": status, "checks": checks}, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
