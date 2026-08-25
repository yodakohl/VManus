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
    subprocess.run(["python3", str(OUT / "build_nine_hundred_forty_ninth.py")], check=True)
    families = rows("PASS949_63_LEARNED_CARD_FAMILIES.tsv")
    variants = rows("PASS949_132_SURFACE_VARIANTS.tsv")
    events = rows("PASS949_2511_EXTENDED_THREE_LAYER_EDITION.tsv")
    counts = Counter(row["codebook_layer"] for row in events)
    checks = [
        ("families_63", len(families) == 63, len(families)),
        ("variants_132", len(variants) == 132, len(variants)),
        ("events_2511", len(events) == 2511, len(events)),
        ("events_unique", len({row["event_id"] for row in events}) == 2511, "unique"),
        ("promoted_105", sum(row["pass949_revision"] == "PROMOTED_RECURRENT_FORMULA" for row in events) == 105, "promoted"),
        ("productive_903", counts["PRODUCTIVE_ABBREVIATION_COMPOSITION"] == 903, counts),
        ("learned_1107", counts["LEARNED_FORMULA_CARD"] == 1107, counts),
        ("local_501", counts["LOCAL_NOMENCLATOR_OR_ADDRESS"] == 501, counts),
        ("new_families_16", len([row for row in families if row["learned_card_id"].startswith("P949-")]) == 16, "new"),
        ("learned_ids_bound", all(row["learned_card_id"] != "NONE" for row in events if row["codebook_layer"] == "LEARNED_FORMULA_CARD"), "bound"),
        ("nonlearned_ids_none", all(row["learned_card_id"] == "NONE" for row in events if row["codebook_layer"] != "LEARNED_FORMULA_CARD"), "none"),
        ("all_values", all(row["current_value_de"].strip() for row in events), "values"),
        ("sealed_absent", "f84" not in "".join(str(row) for row in events).lower(), "sealed"),
    ]
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": str(detail)} for name, ok, detail in checks]}
    (OUT / "PASS949_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
