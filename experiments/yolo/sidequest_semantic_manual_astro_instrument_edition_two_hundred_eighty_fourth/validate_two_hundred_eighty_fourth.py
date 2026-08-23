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
    loci = read("TWO_HUNDRED_EIGHTY_FOURTH_142_MANUAL_LOCUS_TRANSLATIONS.tsv")
    pages = read("TWO_HUNDRED_EIGHTY_FOURTH_THREE_INSTRUMENT_NARRATIVES.tsv")
    checks = {
        "loci_142": len(loci) == 142,
        "groups_395": sum(int(r["group_count"]) for r in loci) == 395,
        "pages_3": len(pages) == 3,
        "page_loci_exact": Counter(r["page"] for r in loci) == Counter({"f67r2": 74, "f68r1": 37, "f69v": 31}),
        "page_groups_exact": {r["page"]: int(r["group_count"]) for r in pages} == {"f67r2": 190, "f68r1": 65, "f69v": 140},
        "loci_unique": len({(r["page"], r["locus"]) for r in loci}) == 142,
        "translations_complete": all(r["manual_locus_translation_de"].strip() for r in loci),
        "templates_8": len({r["astro_template"] for r in loci}) == 8,
        "no_orientation": all(r["orientation"] == "NOT_REQUIRED__SELECT_BY_VISIBLE_OWNER" for r in loci),
        "no_cross_page_key": all(r["cross_page_key"] == "NONE" for r in loci),
        "f69_local_28": sum(r["visible_owner"].startswith("A3_LEFT_RADIAL_SLOT_") for r in loci) == 28,
        "f68_star_28": sum(r["visible_owner"].startswith("A2_STAR_STATION_") for r in loci) == 28,
        "no_sealed_page": all("f84" not in "\t".join(r.values()).lower() for r in loci + pages),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
