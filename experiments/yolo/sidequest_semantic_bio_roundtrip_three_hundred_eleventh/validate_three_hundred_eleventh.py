#!/usr/bin/env python3
"""Validate the complete Biological apprentice roundtrip."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    selectors = read("THREE_HUNDRED_ELEVENTH_15_FORM_SELECTORS.tsv")
    cards = read("THREE_HUNDRED_ELEVENTH_124_CARD_FORWARD_WRITER.tsv")
    reverse = read("THREE_HUNDRED_ELEVENTH_176_SURFACE_REVERSE_DICTIONARY.tsv")
    trace = read("THREE_HUNDRED_ELEVENTH_281_FORWARD_BACKWARD_TRACE.tsv")
    checks = {
        "selectors_15": len(selectors) == 15 and len({r["selector_id"] for r in selectors}) == 15,
        "cards_124": len(cards) == 124 and len({r["master_card_id"] for r in cards}) == 124,
        "source_keys_124": len({r["source_key_short_value_plus_scope"] for r in cards}) == 124,
        "surfaces_176_unique": len(reverse) == 176 and len({r["visible_surface"] for r in reverse}) == 176,
        "events_281": len(trace) == 281 and len({r["event_id"] for r in trace}) == 281,
        "forward_281": all(r["forward_identity_match"] == "YES" for r in trace),
        "reverse_281": all(r["reverse_identity_match"] == "YES" for r in trace),
        "surface_173_108": sum(r["surface_relation"] == "CANONICAL" for r in trace) == 173 and sum(r["surface_relation"] == "REGISTERED_ALLOGRAPH" for r in trace) == 108,
        "owner_resets_16": sum(r["owner_reset_or_break"] == "YES" for r in trace) == 16,
        "all_recipes_nonempty": all(r["exact_identity_recipe"].strip() for r in cards + trace),
        "no_sealed_page": not any("f" + "84" in p.read_text(encoding="utf-8").lower() for p in HERE.glob("*") if p.suffix in {".tsv", ".md"}),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
