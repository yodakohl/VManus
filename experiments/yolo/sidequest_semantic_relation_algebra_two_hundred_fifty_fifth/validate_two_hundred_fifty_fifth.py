#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    algebra = rows("TWO_HUNDRED_FIFTY_FIFTH_15_PAIR_ALGEBRA.tsv")
    cards = rows("TWO_HUNDRED_FIFTY_FIFTH_20_MULTI_STEM_CARDS.tsv")
    occ = rows("TWO_HUNDRED_FIFTY_FIFTH_26_MULTI_STEM_OCCURRENCES.tsv")
    observed = {r["stem_pair"] for r in algebra if r["inventory_status"] == "OBSERVED"}
    missing = {r["stem_pair"] for r in algebra if r["inventory_status"] == "MISSING_COMBINATION"}
    checks = {
        "15_pairs": len(algebra) == 15 and len({r["stem_pair"] for r in algebra}) == 15,
        "11_observed": len(observed) == 11,
        "four_missing_exact": missing == {"AR|AL", "AR|OL", "AR|OR", "AL|OL"},
        "20_multi_cards": len(cards) == 20 and len({r["master_card_id"] for r in cards}) == 20,
        "26_occurrences": len(occ) == 26 and len({r["event_id"] for r in occ}) == 26,
        "one_triple": sum(r["relation_stems"] == "OL|OT|Y" for r in cards) == 1,
        "triple_recomposed": next(r for r in cards if r["relation_stems"] == "OL|OT|Y")["recomposed_core_de"] == "danach mit diesem Posten weiter",
        "all_contexts_present": all(r["full_visible_sequence"].strip() and r["complete_local_translation_de"].strip() for r in occ),
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in occ),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
