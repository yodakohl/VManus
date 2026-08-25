#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    labels = read("PASS988_16_F88R_VISUAL_INGREDIENT_LABELS.tsv")
    batches = read("PASS988_THREE_SILENT_VESSEL_BATCHES.tsv")
    counts = Counter(row["batch_id"] for row in labels)
    checks = {
        "labels_16": len(labels) == 16,
        "label_ids_unique": len({row["teaching_unit_id"] for row in labels}) == 16,
        "event_ids_unique": len({row["event_id"] for row in labels}) == 16,
        "surfaces_unique": len({row["surface"] for row in labels}) == 16,
        "all_ingredient_labels": all(row["visual_role"] == "INGREDIENT_LABEL" for row in labels),
        "batches_three": len(batches) == 3,
        "batch_shape_6_6_4": [counts[row["batch_id"]] for row in batches] == [6, 6, 4],
        "no_textual_headings": all(row["textual_batch_heading"] == "NONE__VESSEL_IS_SILENT_BATCH_OWNER" for row in labels),
        "no_species_names": all(row["species_name"] == "NONE" for row in labels),
        "visible_classes_present": all(row["cautious_visible_material_class_de"] for row in labels),
        "image_hash_fixed": len({row["image_sha256"] for row in labels}) == 1
        and len(labels[0]["image_sha256"]) == 64,
        "sealed_absent": all("f84" not in row["locus"].lower() for row in labels),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS988_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
