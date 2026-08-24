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
    parses = read("FOUR_HUNDRED_SIXTY_NINTH_399_PARSE_TO_CANONICAL_SURFACE.tsv")
    predictions = read("FOUR_HUNDRED_SIXTY_NINTH_776_FORWARD_SURFACE_PREDICTIONS.tsv")
    families = read("FOUR_HUNDRED_SIXTY_NINTH_50_ALLOGRAPH_FAMILIES.tsv")
    units = read("FOUR_HUNDRED_SIXTY_NINTH_14_UNIT_FORWARD_WRITER_SUMMARY.tsv")
    errors = read("FOUR_HUNDRED_SIXTY_NINTH_170_ALLOGRAPH_REMAINDERS.tsv")
    by_parse = {row["formal_parse"]: row for row in parses}
    checks = {
        "parses_399": len(parses) == 399,
        "predictions_776": len(predictions) == 776,
        "families_50": len(families) == 50,
        "units_14": len(units) == 14,
        "errors_170": len(errors) == 170,
        "visible_surface_types_487": len({row["observed_surface"] for row in predictions}) == 487,
        "single_surface_parses_349": sum(int(row["surface_types"]) == 1 for row in parses) == 349,
        "canonical_exact_606": sum(row["exact_surface_match"] == "YES" for row in predictions) == 606,
        "canonical_is_attested": all(row["canonical_surface"] in row["all_attested_surfaces"].split("|") for row in parses),
        "prediction_matches_table": all(row["canonical_predicted_surface"] == by_parse[row["formal_parse"]]["canonical_surface"] for row in predictions),
        "all_predictions_valid": all(row["valid_attested_surface_for_parse"] == "YES" for row in predictions),
        "unit_partition": sum(int(row["groups"]) for row in units) == 776,
        "domain_partition": [sum(row["domain"] == domain for row in predictions) for domain in ("PROSE", "ASTRO")] == [381, 395],
        "fixed_pages": {row["page"] for row in predictions} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_absent": all("f84" not in (row["page"] + row["locus"]).lower() for row in predictions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SIXTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
