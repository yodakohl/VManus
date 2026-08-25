#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    manifest = read(HERE / "PASS999_RELEASE_MANIFEST.tsv")
    bound = {row["artifact_role"]: ROOT / row["relative_path"] for row in manifest}
    hashes_ok = all(
        path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        for row, path in ((row, ROOT / row["relative_path"]) for row in manifest)
    )
    rows_ok = all(path.exists() and len(read(path)) == int(row["data_rows"])
                  for row, path in ((row, ROOT / row["relative_path"]) for row in manifest))
    grid = read(bound["CORRECTED_GRID"])
    status = Counter(row["status"] for row in grid)
    formulas = read(bound["FORMULA_LIGATURES"])
    checks = {
        "manifest_17": len(manifest) == 17 and len(bound) == 17,
        "hashes_exact": hashes_ok,
        "row_counts_exact": rows_ok,
        "codebook_159": len(read(bound["CODEBOOK"])) == 159,
        "roots_53": len(read(bound["ROOTS"])) == 53,
        "formulas_30_exact": len(formulas) == 30 and all(row["semantic_relation"] == "EXAKT_WURZELKOMPOSITION" for row in formulas),
        "specialists_56": len(read(bound["SPECIALISTS"])) == 56,
        "events_2511": len(read(bound["EVENTS"])) == 2511,
        "clauses_354": len(read(bound["CLAUSES"])) == 354,
        "addresses_501": len(read(bound["ADDRESSES"])) == 501,
        "pages_14": len(read(bound["PAGES"])) == 14,
        "bio_1280_318": len(read(bound["BIO_EVENT_PHRASES"])) == 1280 and len(read(bound["BIO_CLAUSES"])) == 318,
        "f88_16_3": len(read(bound["F88_LABELS"])) == 16 and len(read(bound["F88_BATCHES"])) == 3,
        "drawer_70": len(read(bound["SECOND_DRAWER"])) == 70,
        "grid_correct": status == Counter({"NICHT_BELEGT": 25, "BELEGT_PRODUKTIV": 24, "BELEGT_ALS_GELERNTE_FORMEL": 12, "NUR_LOKALE_ADRESSE": 2, "NUR_GELERNTE_FACHKARTE": 1}),
        "empty_25": len(read(bound["EMPTY_GRID_CELLS"])) == 25,
        "collisions_3": len(read(bound["SURFACE_COLLISIONS"])) == 3,
        "sealed_paths_absent": not any("f84" in row["relative_path"].lower() for row in manifest),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS999_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
