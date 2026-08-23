#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    core = rows("HUNDRED_SIXTEENTH_70_CORE_CARD_AUDIT.tsv")
    portable = rows("HUNDRED_SIXTEENTH_SEVENTEEN_EXACT_PORTABLE_CARDS.tsv")
    dictionary = rows("HUNDRED_SIXTEENTH_173_FINAL_TEACHING_DICTIONARY.tsv")
    checks = {
        "core_70": len(core) == 70,
        "portable_core_13": sum(r["core_card_status"] == "PORTABLE_EXACT_CORE_CARD" for r in core) == 13,
        "bio_core_35": sum(r["core_card_status"] == "BIO_CORE_ATOM_CARD" for r in core) == 35,
        "herbal_core_22": sum(r["core_card_status"] == "HERBAL_CORE_ATOM_CARD" for r in core) == 22,
        "portable_total_17": len(portable) == 17,
        "dictionary_173": len(dictionary) == 173,
        "aiin_universal": next(r for r in portable if r["master_form"] == "aiin")["portability_breadth"] == "UNIVERSAL_ALL_PROSE_RECORDS",
        "portable_has_both_sections": all(int(r["herbal_event_count"]) > 0 and int(r["biological_event_count"]) > 0 for r in portable),
        "tier_sum": sum(1 for _ in dictionary) == 173,
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in dictionary),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
