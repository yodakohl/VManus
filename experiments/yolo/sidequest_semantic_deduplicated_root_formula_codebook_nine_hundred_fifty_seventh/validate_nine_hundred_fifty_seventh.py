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
    subprocess.run(["python3", str(OUT / "build_nine_hundred_fifty_seventh.py")], check=True)
    formulas = rows("PASS957_66_TRUE_MULTICOMPONENT_FORMULAS.tsv")
    variants = rows("PASS957_126_FORMULA_SURFACE_VARIANTS.tsv")
    removed = rows("PASS957_13_REMOVED_SINGLE_ROOT_FORMULAS.tsv")
    events = rows("PASS957_2511_DEDUPLICATED_THREE_LAYER_EDITION.tsv")
    entries = rows("PASS957_122_ENTRY_CODEBOOK.tsv")
    counts = Counter(row["codebook_layer"] for row in events)
    checks = [
        ("formulas_66", len(formulas) == 66, len(formulas)),
        ("all_formulas_multicomponent", all("+" in row["component_recipe"] for row in formulas), "multi"),
        ("variants_126", len(variants) == 126, len(variants)),
        ("removed_13", len(removed) == 13, len(removed)),
        ("removed_single", all("+" not in row["component"] for row in removed), "single"),
        ("entries_122", len(entries) == 122, len(entries)),
        ("events_2511", len(events) == 2511, len(events)),
        ("demoted_375", sum(row["pass957_revision"] == "SINGLE_ROOT_DEDUPLICATED" for row in events) == 375, "demoted"),
        ("productive_1220", counts["PRODUCTIVE_ABBREVIATION_COMPOSITION"] == 1220, counts),
        ("learned_790", counts["LEARNED_FORMULA_CARD"] == 790, counts),
        ("local_501", counts["LOCAL_NOMENCLATOR_OR_ADDRESS"] == 501, counts),
        ("learned_bound", all(row["formula_card_id"] != "NONE" for row in events if row["codebook_layer"] == "LEARNED_FORMULA_CARD"), "bound"),
        ("sealed_absent", "f84" not in "".join(str(row) for row in events).lower(), "sealed"),
    ]
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": str(detail)} for name, ok, detail in checks]}
    (OUT / "PASS957_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
