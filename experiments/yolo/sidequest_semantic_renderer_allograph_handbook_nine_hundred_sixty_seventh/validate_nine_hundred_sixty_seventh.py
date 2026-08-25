#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    pairs = read_tsv("PASS967_82_SIMPLE_ALLOGRAPH_PAIRS.tsv")
    multi = read_tsv("PASS967_97_MULTIFORM_RECIPES.tsv")
    rules = read_tsv("PASS967_RENDERER_RULES.tsv")
    counts = Counter(row["renderer_rule"] for row in pairs)
    checks = {
        "pairs_82": len(pairs) == 82,
        "pair_unique": len({(row["component_recipe"], row["renderer_rule"], row["base_surface"], row["marked_surface"]) for row in pairs}) == 82,
        "multiform_97": len(multi) == 97,
        "multiform_surfaces_227": sum(int(row["variant_count"]) for row in multi) == 227,
        "q_pairs_49": counts["Q_POST_CLOSE_ENTRY_SHELL"] == 49,
        "ch_pairs_18": counts["CH_RENDERER_SHELL"] == 18,
        "d_pairs_7": counts["D_ADDRESS_SHELL"] == 7,
        "s_pairs_6": counts["S_SERIES_SHELL"] == 6,
        "sh_t_pairs_2": counts["SH_HOLD_SHELL"] == 1 and counts["T_ENTRY_SHELL"] == 1,
        "rules_7": len(rules) == 7,
        "semantic_effect_none": all(row["semantic_effect"] == "NONE" for row in pairs + rules),
        "no_sealed_pages": not any("f84" in str(row).lower() for row in pairs + multi + rules),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS967_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
