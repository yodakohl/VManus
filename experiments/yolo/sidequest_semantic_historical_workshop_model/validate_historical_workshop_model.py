#!/usr/bin/env python3
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent

def rows(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

checks = {}
layers = rows("FOUR_LAYER_CROSSWALK.tsv")
stems = rows("TWENTY_FIVE_STEM_HISTORICAL_ROLES.tsv")
predictions = rows("PREDICTED_COMPOSITIONS.tsv")
sources = rows("SOURCES.tsv")
checks["four_layers"] = len(layers) == 4
checks["twenty_five_stems"] = len(stems) == 25 and len({r["atom"] for r in stems}) == 25
checks["fifteen_predictions"] = len(predictions) == 15 and len({r["prediction_id"] for r in predictions}) == 15
checks["three_existing_forward_hits"] = sum(r["status_in_current_ten_pages"].startswith("OBSERVED_FORWARD") for r in predictions) == 3
checks["two_existing_oneoffs"] = sum(r["status_in_current_ten_pages"].startswith("OBSERVED_ONE_OFF") for r in predictions) == 2
checks["ten_unseen_predictions"] = sum(r["status_in_current_ten_pages"] == "NOT_YET_ISOLATED" for r in predictions) == 10
checks["sources_present"] = len(sources) >= 8 and all(r["url"].startswith("https://") for r in sources)
sealed_token = "f" + "84"
checks["no_sealed_pages"] = all(sealed_token not in p.read_text(encoding="utf-8").lower() for p in ROOT.iterdir() if p.is_file())
checks["manual_and_report"] = all((ROOT / n).stat().st_size > 1000 for n in ["APPRENTICE_MANUAL_1420.md", "HISTORICAL_ARCHITECTURE_REPORT.md"])
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "counts": {"layers": len(layers), "stems": len(stems), "predictions": len(predictions), "sources": len(sources)}}
(ROOT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False, indent=2))
