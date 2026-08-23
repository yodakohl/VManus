#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("TWO_HUNDRED_EIGHTY_SIXTH_36_PRODUCTIVE_ROOTS.tsv")
    templates = read("TWO_HUNDRED_EIGHTY_SIXTH_124_COMPOSITION_TEMPLATES.tsv")
    whole = read("TWO_HUNDRED_EIGHTY_SIXTH_23_WHOLE_SIGNS.tsv")
    framed = read("TWO_HUNDRED_EIGHTY_SIXTH_ONE_FRAMED_WHOLE_EXCEPTION.tsv")
    exercises = read("TWO_HUNDRED_EIGHTY_SIXTH_40_REVERSE_ENCODINGS.tsv")
    forecasts = read("TWO_HUNDRED_EIGHTY_SIXTH_12_NEW_COMPOSITION_FORECASTS.tsv")
    checks = {
        "roots_36": len(roots) == 36,
        "templates_124": len(templates) == 124,
        "template_card_types_149": sum(int(r["card_type_count"]) for r in templates) == 149,
        "unique_templates_104": sum(int(r["card_type_count"]) == 1 for r in templates) == 104,
        "ambiguous_templates_20": sum(int(r["card_type_count"]) > 1 for r in templates) == 20,
        "whole_signs_23": len(whole) == 23,
        "composed_events_352": sum(int(r["event_support"]) for r in templates) == 352,
        "whole_events_28": sum(int(r["event_support"]) for r in whole) == 28,
        "framed_whole_1_event": len(framed) == 1 and sum(int(r["event_support"]) for r in framed) == 1,
        "canonical_hits_324": sum(int(r["canonical_event_hits"]) for r in templates) == 324,
        "exercises_40": len(exercises) == 40,
        "forecasts_12": len(forecasts) == 12,
        "all_exercises_have_answer": all(r["teaching_answer_de"].strip() for r in exercises),
        "all_forecasts_have_recipe": all(r["predicted_family_recipe"].strip() and r["predicted_surface_skeleton"].strip() for r in forecasts),
        "no_sealed_page": all("f84" not in "\t".join(r.values()).lower() for r in roots + templates + whole + framed + exercises + forecasts),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
