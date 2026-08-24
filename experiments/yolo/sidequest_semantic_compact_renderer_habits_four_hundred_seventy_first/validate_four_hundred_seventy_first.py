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
    habits = read("FOUR_HUNDRED_SEVENTY_FIRST_NINE_RENDERER_HABITS.tsv")
    bodies = read("FOUR_HUNDRED_SEVENTY_FIRST_173_BODY_DEFAULT_WRAPPERS.tsv")
    astro_defaults = read("FOUR_HUNDRED_SEVENTY_FIRST_ASTRO_PARSE_DEFAULT_SURFACES.tsv")
    predictions = read("FOUR_HUNDRED_SEVENTY_FIRST_776_COMPACT_RENDERER_PREDICTIONS.tsv")
    exceptions = read("FOUR_HUNDRED_SEVENTY_FIRST_113_EXEMPLAR_RENDERER_EXCEPTIONS.tsv")
    models = read("FOUR_HUNDRED_SEVENTY_FIRST_RENDERER_COMPLEXITY_COMPARISON.tsv")
    checks = {
        "habits_9": len(habits) == 9,
        "bodies_173": len(bodies) == 173,
        "astro_defaults_271": len(astro_defaults) == 271,
        "predictions_776": len(predictions) == 776,
        "exceptions_113": len(exceptions) == 113,
        "models_4": len(models) == 4,
        "prose_exact_314": sum(row["domain"] == "PROSE" and row["exact_without_exemplar"] == "YES" for row in predictions) == 314,
        "astro_exact_349": sum(row["domain"] == "ASTRO" and row["exact_without_exemplar"] == "YES" for row in predictions) == 349,
        "combined_exact_663": sum(row["exact_without_exemplar"] == "YES" for row in predictions) == 663,
        "habits_gain_at_least_2": all(int(row["net_exact_gain"]) >= 2 for row in habits),
        "exception_partition": len(exceptions) + sum(row["exact_without_exemplar"] == "YES" for row in predictions) == 776,
        "domain_partition": [sum(row["domain"] == domain for row in predictions) for domain in ("PROSE", "ASTRO")] == [381, 395],
        "fixed_pages": {row["page"] for row in predictions} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in predictions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SEVENTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
