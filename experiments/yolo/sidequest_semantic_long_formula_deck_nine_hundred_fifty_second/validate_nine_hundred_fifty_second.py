#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(OUT / "build_nine_hundred_fifty_second.py")], check=True)
    families = rows("PASS952_79_LEARNED_CARD_FAMILIES.tsv")
    variants = rows("PASS952_155_SURFACE_VARIANTS.tsv")
    events = rows("PASS952_2511_LONG_FORMULA_EDITION.tsv")
    counts = Counter(row["codebook_layer"] for row in events)
    checks = [
        ("families_79", len(families) == 79, len(families)),
        ("variants_155", len(variants) == 155, len(variants)),
        ("events_2511", len(events) == 2511, len(events)),
        ("events_unique", len({row["event_id"] for row in events}) == 2511, "unique"),
        ("promoted_58", sum(row["formula_deck_revision"] == "PROMOTED_LONG_FORMULA" for row in events) == 58, "promoted"),
        ("productive_845", counts["PRODUCTIVE_ABBREVIATION_COMPOSITION"] == 845, counts),
        ("learned_1165", counts["LEARNED_FORMULA_CARD"] == 1165, counts),
        ("local_501", counts["LOCAL_NOMENCLATOR_OR_ADDRESS"] == 501, counts),
        ("all_learned_bound", all(row["learned_card_id"] != "NONE" for row in events if row["codebook_layer"] == "LEARNED_FORMULA_CARD"), "bound"),
        ("nonlearned_none", all(row["learned_card_id"] == "NONE" for row in events if row["codebook_layer"] != "LEARNED_FORMULA_CARD"), "none"),
        ("sealed_absent", "f84" not in "".join(str(row) for row in events).lower(), "sealed"),
    ]
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": str(detail)} for name, ok, detail in checks]}
    (OUT / "PASS952_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
