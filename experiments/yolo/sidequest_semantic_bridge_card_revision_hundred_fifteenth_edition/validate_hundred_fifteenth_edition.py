#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    bridge = rows("HUNDRED_FIFTEENTH_57_BRIDGE_CARD_AUDIT.tsv")
    atoms = rows("HUNDRED_FIFTEENTH_NINE_BRIDGE_ATOMS.tsv")
    dictionary = rows("HUNDRED_FIFTEENTH_173_REVISED_TEACHING_DICTIONARY.tsv")
    portable = [r for r in bridge if r["bridge_status"] == "PORTABLE_EXACT_BRIDGE_CARD"]
    checks = {
        "bridge_cards_57": len(bridge) == 57,
        "bridge_atoms_9": len(atoms) == 9,
        "dictionary_173": len(dictionary) == 173,
        "portable_exact_4": len(portable) == 4,
        "portable_forms_exact": {r["master_form"] for r in portable} == {"cheeky", "chdy", "chety", "cheey"},
        "bio_only_48": sum(r["bridge_status"] == "BIO_CARD_WITH_SHARED_BRIDGE_ATOM" for r in bridge) == 48,
        "herbal_only_5": sum(r["bridge_status"] == "HERBAL_CARD_WITH_SHARED_BRIDGE_ATOM" for r in bridge) == 5,
        "tier_counts": {tier: sum(r["revised_teaching_tier"] == tier for r in dictionary) for tier in {r["revised_teaching_tier"] for r in dictionary}} == {"PORTABLE_CORE_CARD": 70, "PORTABLE_EXACT_BRIDGE_CARD": 4, "SECTIONAL_CARD_WITH_SHARED_BRIDGE_ATOM": 53, "SPECIALIST_TABLET_CARD": 46},
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in dictionary),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
