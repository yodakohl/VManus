#!/usr/bin/env python3
from pathlib import Path
import csv, json

HERE = Path(__file__).resolve().parent
def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))
rows = read("ASTRO_301_RESIDUAL_PARSE.tsv")
paradigm = read("YK_YT_PARADIGM.tsv")
groups = read("YK_YT_43_GROUP_READINGS.tsv")
checks = {
    "types_301": len(rows) == 301,
    "groups_395": sum(int(r["occurrences"]) for r in rows) == 395,
    "yk_21_types": sum(r["new_local_core"] == "YK" for r in rows) == 21,
    "yk_26_groups": sum(int(r["occurrences"]) for r in rows if r["new_local_core"] == "YK") == 26,
    "yt_15_types": sum(r["new_local_core"] == "YT" for r in rows) == 15,
    "yt_17_groups": sum(int(r["occurrences"]) for r in rows if r["new_local_core"] == "YT") == 17,
    "paradigm_36_types": len(paradigm) == 36,
    "promoted_43_groups": len(groups) == 43,
    "all_promoted_have_owner": all(r["visible_owner"] for r in groups),
    "report_present": (HERE / "ASTRO_RESIDUAL_MORPHOLOGY_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_token_absent"] = all(sealed not in p.read_text(encoding="utf-8").lower() for p in HERE.iterdir() if p.is_file())
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS": raise SystemExit(1)
