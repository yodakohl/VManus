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
    family = rows("TWO_HUNDRED_SIXTY_SIXTH_13_ASTRO_AIIN_GROUPS.tsv")
    forms = rows("TWO_HUNDRED_SIXTY_SIXTH_12_AIIN_FORM_TYPES.tsv")
    revised = rows("TWO_HUNDRED_SIXTY_SIXTH_REVISED_395_ASTRO_GROUPS.tsv")
    status = Counter(r["composition_status"] for r in family)
    checks = {
        "13_groups": len(family) == 13 and len({r["group_serial"] for r in family}) == 13,
        "12_forms": len(forms) == 12 and len({r["visible_surface"] for r in forms}) == 12,
        "ten_full_three_partial": status == {"FULL_40_COMPONENT_PARSE": 10, "LOCAL_CORE_PLUS_AIIN": 3},
        "all_three_pages": {r["page"] for r in family} == {"f67r2", "f68r1", "f69v"},
        "two_forecast_hits": {r["visible_surface"] for r in family if r["visible_surface"] in {"alaiin", "chedaiin"}} == {"alaiin", "chedaiin"},
        "aiin_in_every_parse": all("AIIN" in r["component_parse"] and r["aiin_contribution_de"] == "SOLLWERT_ODER_GRAD" for r in family),
        "395_revised": len(revised) == 395 and len({r["group_serial"] for r in revised}) == 395,
        "13_revision_flags": sum(r["revision_266"] == "AIIN_COMPOSITION" for r in revised) == 13,
        "no_empty_readings": all(r["existing_diagram_reading_de"].strip() and r["composed_short_value_de"].strip() for r in family),
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
