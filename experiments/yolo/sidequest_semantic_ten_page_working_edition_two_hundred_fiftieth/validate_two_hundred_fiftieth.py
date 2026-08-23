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
    dictionary = rows("TWO_HUNDRED_FIFTIETH_REVISED_173_CARD_DICTIONARY.tsv")
    prose = rows("TWO_HUNDRED_FIFTIETH_381_PROSE_EVENTS.tsv")
    statements = rows("TWO_HUNDRED_FIFTIETH_116_PROSE_STATEMENTS.tsv")
    astro = rows("TWO_HUNDRED_FIFTIETH_395_ASTRO_GROUPS.tsv")
    loci = rows("TWO_HUNDRED_FIFTIETH_142_ASTRO_LOCI.tsv")
    unified = rows("TWO_HUNDRED_FIFTIETH_776_GROUP_WORKING_EDITION.tsv")
    checks = {
        "173_cards": len(dictionary) == 173,
        "381_prose": len(prose) == 381,
        "116_statements": len(statements) == 116,
        "395_astro": len(astro) == 395,
        "142_loci": len(loci) == 142,
        "776_unified": len(unified) == 776,
        "776_unique_ids": len({r["unified_id"] for r in unified}) == 776,
        "ten_pages": {r["page"] for r in unified} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "all_dictionary_cores": all(r["portable_core_de"].strip() for r in dictionary),
        "all_unified_cores": all(r["portable_core_de"].strip() for r in unified),
        "all_unified_local": all(r["local_expansion_de"].strip() for r in unified),
        "astro_page_counts": Counter(r["page"] for r in astro) == {"f67r2": 190, "f68r1": 65, "f69v": 140},
        "prose_page_count_381": sum(1 for r in unified if r["section"] == "PROSE") == 381,
        "astro_page_count_395": sum(1 for r in unified if r["section"] == "ASTRO") == 395,
        "five_revised_card_cores": sum(r["dictionary_layer"] == "CROSS_REGISTER_REVISED_CORE" for r in dictionary) == 5,
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in unified),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
