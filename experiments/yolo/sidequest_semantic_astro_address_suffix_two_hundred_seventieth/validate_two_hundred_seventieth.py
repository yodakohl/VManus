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
    addresses = rows("TWO_HUNDRED_SEVENTIETH_54_LOCAL_ASTRO_ADDRESSES.tsv")
    forms = rows("TWO_HUNDRED_SEVENTIETH_38_ADDRESS_FORM_TYPES.tsv")
    cross = rows("TWO_HUNDRED_SEVENTIETH_BALANCED_ADDRESS_CHANNELS.tsv")
    revised = rows("TWO_HUNDRED_SEVENTIETH_REVISED_395_ASTRO_GROUPS.tsv")
    counts = Counter(r["address_suffix"] for r in addresses)
    checks = {
        "54_addresses": len(addresses) == 54 and len({r["group_serial"] for r in addresses}) == 54,
        "38_forms": len(forms) == 38 and len({r["visible_surface"] for r in forms}) == 38,
        "40_ar_14_al": counts == {"AR": 40, "AL": 14},
        "all_three_pages": {r["page"] for r in addresses} == {"f67r2", "f68r1", "f69v"},
        "suffix_matches_surface": all(r["visible_surface"].endswith(r["address_suffix"].lower()) for r in addresses),
        "two_cross_rows": len(cross) == 2 and {r["address_component"] for r in cross} == {"AR", "AL"},
        "balanced_sixty": all(int(r["terminal_channel_total"]) == 60 for r in cross),
        "395_revised": len(revised) == 395 and len({r["group_serial"] for r in revised}) == 395,
        "54_revision_flags": sum(r["revision_270"] == "AL_AR_ADDRESS_SUFFIX" for r in revised) == 54,
        "gap_matches_preserved": sum(r["revision_269"] == "RELATION_GAP_MATCH" for r in revised) == 4,
        "prior_quantity_path_preserved": sum(r["revision_266"] == "AIIN_COMPOSITION" for r in revised) == 13 and sum(r["revision_267"] == "AIN_AN_COMPOSITION" for r in revised) == 10 and sum(r["revision_268"] == "AIR_PATH_COMPOSITION" for r in revised) == 12,
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
