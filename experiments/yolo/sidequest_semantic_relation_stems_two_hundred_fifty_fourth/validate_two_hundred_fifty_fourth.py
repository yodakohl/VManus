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
    stems = rows("TWO_HUNDRED_FIFTY_FOURTH_SIX_RELATION_STEMS.tsv")
    cards = rows("TWO_HUNDRED_FIFTY_FOURTH_102_RELATION_CARDS.tsv")
    prose = rows("TWO_HUNDRED_FIFTY_FOURTH_219_PROSE_OCCURRENCES.tsv")
    astro = rows("TWO_HUNDRED_FIFTY_FOURTH_67_ASTRO_OCCURRENCES.tsv")
    expected_cards = {"AR": 10, "AL": 21, "OL": 24, "OT": 16, "OR": 9, "Y": 43}
    expected_prose = {"AR": 14, "AL": 38, "OL": 48, "OT": 26, "OR": 17, "Y": 103}
    expected_astro = {"AR": 6, "AL": 8, "OL": 9, "OT": 6, "OR": 3, "Y": 41}

    def count(data: list[dict[str, str]]) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for row in data:
            counter.update(row["relation_stems"].split("|"))
        return dict(counter)

    checks = {
        "six_stems": len(stems) == 6 and {r["stem"] for r in stems} == set(expected_cards),
        "102_cards": len(cards) == 102 and len({r["master_card_id"] for r in cards}) == 102,
        "219_prose_events": len(prose) == 219 and len({r["event_id"] for r in prose}) == 219,
        "67_astro_groups": len(astro) == 67 and len({r["group_serial"] for r in astro}) == 67,
        "per_stem_cards": count(cards) == expected_cards,
        "per_stem_prose": count(prose) == expected_prose,
        "per_stem_astro": count(astro) == expected_astro,
        "fixed_pages_only": {r["page"] for r in prose} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"} and {r["page"] for r in astro} <= {"f67r2", "f68r1", "f69v"},
        "no_empty_values": all(r["relation_skeleton_de"].strip() and r["portable_core_de"].strip() for r in prose),
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in prose + astro),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
