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
    subprocess.run(["python3", str(OUT / "build_nine_hundred_fifty_fourth.py")], check=True)
    variants = rows("PASS954_76_RENDERER_VARIANT_PREDICTIONS.tsv")
    forward = rows("PASS954_27_FORWARD_COMPOSITION_PREDICTIONS.tsv")
    checks = [
        ("variant_predictions_76", len(variants) == 76, len(variants)),
        ("forward_predictions_27", len(forward) == 27, len(forward)),
        ("prediction_ids_unique", len({row["prediction_id"] for row in [*variants, *forward]}) == 103, "unique"),
        ("all_values", all(row["predicted_workshop_value_de"].strip() and row["predicted_image_value_de"].strip() for row in [*variants, *forward]), "values"),
        ("all_variant_observed", all(int(row["observed_events"]) > 0 for row in variants), "observed"),
        ("all_routes", all(row["prediction_route"] in {"LEARNED_FORMULA_CARD", "PRODUCTIVE_ABBREVIATION_COMPOSITION"} for row in forward), "routes"),
        ("all_surface_statuses", all(row["surface_prediction_status"] in {"UNSEEN_FORWARD_FORM", "HOMOGRAPH_DIFFERENT_PARSE", "OBSERVED_RECIPE_MATCH"} for row in forward), "statuses"),
        ("homograph_not_match", all(row["component_recipe"] not in row["observed_component_recipes"].split("|") for row in forward if row["surface_prediction_status"] == "HOMOGRAPH_DIFFERENT_PARSE"), "homograph"),
        ("sealed_absent", "f84" not in "".join(str(row) for row in [*variants, *forward]).lower(), "sealed"),
    ]
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS954_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
