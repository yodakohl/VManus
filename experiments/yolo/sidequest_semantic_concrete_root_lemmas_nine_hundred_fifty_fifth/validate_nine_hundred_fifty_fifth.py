#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(OUT / "build_nine_hundred_fifty_fifth.py")], check=True)
    lemmas = rows("PASS955_56_CONCRETE_ROOT_LEMMAS.tsv")
    examples = rows("PASS955_79_ROOT_TO_FORMULA_EXAMPLES.tsv")
    events = rows("PASS955_2511_SIMPLE_ROOT_AND_FORMULA_EDITION.tsv")
    checks = [
        ("lemmas_56", len(lemmas) == 56, len(lemmas)),
        ("lemmas_unique", len({row["component"] for row in lemmas}) == 56, "unique"),
        ("one_token_lemmas", all(" " not in row["concrete_root_lemma_de"].strip() for row in lemmas), "one-token"),
        ("formulas_79", len(examples) == 79, len(examples)),
        ("events_2511", len(events) == 2511, len(events)),
        ("events_unique", len({row["event_id"] for row in events}) == 2511, "unique"),
        ("all_simple", all(row["simple_card_reading_de"].strip() for row in events), "simple"),
        ("productive_is_lemmas", all(" · " in row["simple_card_reading_de"] or "+" not in row["component_recipe"] for row in events if row["simple_reading_route"] == "ROOT_LEMMA_COMPOSITION"), "composed"),
        ("formula_ids_bound", all(row["learned_card_id"] != "NONE" for row in events if row["simple_reading_route"] == "LEARNED_FORMULA_IDIOM"), "bound"),
        ("sealed_absent", "f84" not in "".join(str(row) for row in events).lower(), "sealed"),
    ]
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS955_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
