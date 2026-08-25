#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    templates = read("PASS982_THIRTY_FORWARD_COMPOSITION_TEMPLATES.tsv")
    examples = read("PASS982_TWELVE_NEW_PAGE_COMPOSITION_EXAMPLES.tsv")
    checks = {
        "templates_30": len(templates) == 30,
        "template_ids_unique": len({r["template_id"] for r in templates}) == 30,
        "recipes_unique": len({r["component_recipe"] for r in templates}) == 30,
        "all_templates_observed": all(int(r["observed_events"]) > 0 for r in templates),
        "examples_12": len(examples) == 12,
        "four_new_pages": {r["physical_page"] for r in examples} == {"f13r", "f75r", "f70v", "f88r"},
        "all_examples_concrete": all(r["predicted_context_reading_de"] for r in examples),
        "sealed_absent": all("f84" not in r["physical_page"].lower() for r in examples),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS982_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
