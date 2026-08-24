#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    rules = read("FIVE_HUNDRED_FORTIETH_NINE_PREDICTIVE_RENDERER_RULES.tsv")
    realized = read("FIVE_HUNDRED_FORTIETH_TWENTY_REALIZED_COMPOSITION_PREDICTIONS.tsv")
    surfaces = read("FIVE_HUNDRED_FORTIETH_FORTY_SEVEN_ACTIVE_PREDICTED_SURFACES.tsv")
    rejected = read("FIVE_HUNDRED_FORTIETH_ONE_REJECTED_SURFACE_COLLISION.tsv")
    checks = {
        "rules9": len(rules) == 9 and len({row["rule_id"] for row in rules}) == 9,
        "predictions20": len(realized) == 20 and len({row["prediction_id"] for row in realized}) == 20,
        "surfaces47": len(surfaces) == 47 and len({row["predicted_surface"] for row in surfaces}) == 47,
        "surface_partition": Counter(row["prediction_id"] for row in surfaces) == Counter({row["prediction_id"]: int(row["surface_variant_count"]) for row in realized}),
        "all_writable": all(row["renderer_status"] == "WRITABLE_BY_EXISTING_RULE_FAMILY" for row in realized),
        "all_unsighted": all(row["observed_status"] == "NOT_OBSERVED_ON_TEN_PAGES" for row in realized) and all(row["status"] == "PREDICTED_NOT_SIGHTED" for row in surfaces),
        "no_collisions": all(row["observed_surface_collision"] == "NO" for row in surfaces),
        "one_rejected_collision": len(rejected) == 1 and rejected[0]["predicted_surface"] == "chair" and rejected[0]["collision_card_ids"] == "PROC006",
        "no_empty_surface": all(row["predicted_surface"] for row in surfaces),
        "no_sealed_tokens": all("f84" not in "\t".join(row.values()).lower() for row in [*rules, *realized, *surfaces]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FORTIETH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
