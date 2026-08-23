#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roles = read("TWO_HUNDRED_EIGHTY_NINTH_29_ASTRO_ROLE_RECIPES.tsv")
    reverse = read("TWO_HUNDRED_EIGHTY_NINTH_265_REVERSE_ENCODINGS.tsv")
    whole = read("TWO_HUNDRED_EIGHTY_NINTH_46_ASTRO_WHOLE_SIGNS.tsv")
    local = read("TWO_HUNDRED_EIGHTY_NINTH_67_LOCAL_COPY_KEYS.tsv")
    checks = {
        "roles_29": len(roles) == 29,
        "portable_groups_265": len(reverse) == 265,
        "portable_forms_188": len({r["resulting_visible_surface"] for r in reverse}) == 188,
        "portable_serials_unique": len({r["group_serial"] for r in reverse}) == 265,
        "generation_complete": all(r["generation_status"] == "GENERATED_FROM_RULE_PLUS_REGISTERED_OR_LOCAL_CORE" for r in reverse),
        "strategies_11": len({r["writer_strategy"] for r in reverse}) == 11,
        "whole_forms_46": len(whole) == 46,
        "whole_groups_51": sum(int(r["group_count"]) for r in whole) == 51,
        "local_forms_67": len(local) == 67,
        "local_groups_79": sum(int(r["group_count"]) for r in local) == 79,
        "all_395": len(reverse) + sum(int(r["group_count"]) for r in whole) + sum(int(r["group_count"]) for r in local) == 395,
        "no_sealed_page": all("f84" not in "\t".join(r.values()).lower() for r in roles + reverse + whole + local),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
