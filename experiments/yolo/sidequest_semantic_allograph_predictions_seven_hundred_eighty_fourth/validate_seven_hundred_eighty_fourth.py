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
    predictions = read("SEVEN_HUNDRED_EIGHTY_FOURTH_95_SURFACE_PREDICTIONS.tsv")
    hits = read("SEVEN_HUNDRED_EIGHTY_FOURTH_18_SAME_RECIPE_HITS.tsv")
    collisions = read("SEVEN_HUNDRED_EIGHTY_FOURTH_2_CROSS_RECIPE_COLLISIONS.tsv")
    strong = read("SEVEN_HUNDRED_EIGHTY_FOURTH_5_STRONG_UNSEEN_PARTNERS.tsv")
    score = read("SEVEN_HUNDRED_EIGHTY_FOURTH_2_OPERATION_SCORECARD.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_EIGHTY_FOURTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_op = {row["operation"]: row for row in score}
    checks = {
        "counts_95_18_2_5_2": (len(predictions), len(hits), len(collisions), len(strong), len(score)) == (95, 18, 2, 5, 2),
        "status_partition": sum(row["status"] == "UNATTESTED_ON_FIXED_TEN_PAGES" for row in predictions) == 75,
        "op1_27_8_0_19": tuple(int(by_op["OP1_CHED_CHD"][key]) for key in ("predictions", "same_recipe_hits", "different_recipe_collisions", "unattested")) == (27, 8, 0, 19),
        "op2_68_10_2_56": tuple(int(by_op["OP2_Y_CHY"][key]) for key in ("predictions", "same_recipe_hits", "different_recipe_collisions", "unattested")) == (68, 10, 2, 56),
        "collision_is_ly_lchy": {(row["source_surface"], row["predicted_partner_surface"]) for row in collisions} == {("ly", "lchy"), ("lchy", "ly")},
        "strong_five": {row["predicted_partner_surface"] for row in strong} == {"chdchy", "schdy", "tchdy", "okchdy", "qotchdy"},
        "strong_unattested": all(row["status"] == "UNATTESTED_ON_FIXED_TEN_PAGES" and row["already_licensed_recipe_family"] == "YES" for row in strong),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (predictions, hits, collisions, strong, score) for row in rows),
        "summary_pass": summary["status"] == "PASS" and (summary["predictions"], summary["same_recipe_hits"], summary["cross_recipe_collisions"], summary["unattested"], summary["strong_unseen"]) == (95, 18, 2, 75, 5),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTY_FOURTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
