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
    matches = rows("TWO_HUNDRED_SIXTY_NINTH_FOUR_ASTRO_MATCH_GROUPS.tsv")
    matrix = rows("TWO_HUNDRED_SIXTY_NINTH_FOUR_GAP_OUTCOMES.tsv")
    revised = rows("TWO_HUNDRED_SIXTY_NINTH_REVISED_395_ASTRO_GROUPS.tsv")
    pair_counts = Counter(r["relation_pair"] for r in matches)
    checks = {
        "four_matches": len(matches) == 4 and len({r["group_serial"] for r in matches}) == 4,
        "three_forms": {r["visible_surface"] for r in matches} == {"saral", "olar", "okolar"},
        "two_pairs_two_each": pair_counts == {"AR|AL": 2, "AR|OL": 2},
        "pages_f67_f69": {r["page"] for r in matches} == {"f67r2", "f69v"},
        "four_gap_rows": len(matrix) == 4 and {r["prose_gap_pair"] for r in matrix} == {"AR|AL", "AR|OL", "AR|OR", "AL|OL"},
        "two_match_two_none": sum(r["astro_status"] == "PRODUCTIVE_MATCH" for r in matrix) == 2 and sum(r["astro_status"] == "NO_DIRECT_MATCH" for r in matrix) == 2,
        "395_revised": len(revised) == 395 and len({r["group_serial"] for r in revised}) == 395,
        "four_revision_flags": sum(r["revision_269"] == "RELATION_GAP_MATCH" for r in revised) == 4,
        "prior_revisions_preserved": sum(r["revision_266"] == "AIIN_COMPOSITION" for r in revised) == 13 and sum(r["revision_267"] == "AIN_AN_COMPOSITION" for r in revised) == 10 and sum(r["revision_268"] == "AIR_PATH_COMPOSITION" for r in revised) == 12,
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
