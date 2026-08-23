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
    groups = rows("TWO_HUNDRED_FORTY_SEVENTH_395_GROUP_ASTRO_MANUAL.tsv")
    cards = rows("TWO_HUNDRED_FORTY_SEVENTH_29_KNOWN_PROSE_CARDS.tsv")
    namespaces = rows("TWO_HUNDRED_FORTY_SEVENTH_13_NAMESPACE_LESSONS.tsv")
    counts = Counter(r["curriculum_layer"] for r in groups)
    checks = {
        "395_groups": len(groups) == 395,
        "395_unique_serials": len({r["group_serial"] for r in groups}) == 395,
        "29_known_cards": len(cards) == 29,
        "13_namespaces": len(namespaces) == 13,
        "layer_split_66_23_306": counts == {"THREE_REGISTER_COMMON_CORE": 66, "KNOWN_PROSE_CARD_IN_ASTRO": 23, "ASTRO_LOCAL_LABEL_SIGN": 306},
        "all_known_values_invariant": all(r["value_invariant"] == "YES" for r in cards),
        "all_groups_concrete": all(r["concrete_diagram_reading_de"].strip() for r in groups),
        "three_pages": {r["page"] for r in groups} == {"f67r2", "f68r1", "f69v"},
        "no_join_claim": all("f68r1" not in r["namespaces"] or "f69v" not in r["namespaces"] for r in cards),
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in groups),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
