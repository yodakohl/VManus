#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    family = rows("TWO_HUNDRED_SIXTY_SEVENTH_10_ASTRO_AIN_AN_GROUPS.tsv")
    forms = rows("TWO_HUNDRED_SIXTY_SEVENTH_NINE_AIN_AN_FORM_TYPES.tsv")
    revised = rows("TWO_HUNDRED_SIXTY_SEVENTH_REVISED_395_ASTRO_GROUPS.tsv")
    endings = Counter(r["quantity_ending"] for r in family)
    status = Counter(r["composition_status"] for r in family)
    checks = {
        "10_groups": len(family) == 10 and len({r["group_serial"] for r in family}) == 10,
        "nine_forms": len(forms) == 9 and len({r["visible_surface"] for r in forms}) == 9,
        "seven_ain_three_an": endings == {"AIN": 7, "AN": 3},
        "nine_full_one_partial": status == {"FULL_40_COMPONENT_PARSE": 9, "LOCAL_CORE_PLUS_AIN": 1},
        "all_f67": {r["page"] for r in family} == {"f67r2"},
        "an_forms_exact": {r["visible_surface"] for r in family if r["quantity_ending"] == "AN"} == {"dokan", "oeoldan", "oran"},
        "dokan_has_ok_an": next(r for r in family if r["visible_surface"] == "dokan")["component_parse"] == "D_PREVIOUS+OK+AN",
        "395_revised": len(revised) == 395 and len({r["group_serial"] for r in revised}) == 395,
        "ten_revision_flags": sum(r["revision_267"] == "AIN_AN_COMPOSITION" for r in revised) == 10,
        "preserve_aiin_revisions": sum(r["revision_266"] == "AIIN_COMPOSITION" for r in revised) == 13,
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in revised),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
