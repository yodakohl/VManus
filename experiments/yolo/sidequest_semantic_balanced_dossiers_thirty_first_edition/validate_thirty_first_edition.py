#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dossiers = read("THIRTY_FIRST_FOUR_BALANCED_DOSSIERS.tsv")
steps = read("THIRTY_FIRST_TWELVE_BENCH_STEPS.tsv")
checks = {
    "four_dossiers": len(dossiers) == 4,
    "twelve_steps": len(steps) == 12,
    "three_steps_each": all(sum(row["dossier_id"] == dossier["dossier_id"] for row in steps) == 3 for dossier in dossiers),
    "bench_order": all(row["bench_order"] == "WHEN>WHAT>HOW" for row in dossiers),
    "116_statements": sum(int(row["prose_statement_count"]) for row in dossiers) == 116,
    "381_prose_groups": sum(int(row["prose_group_count"]) for row in dossiers) == 381,
    "142_astro_loci": sum(int(row["astro_locus_count"]) for row in dossiers) == 142,
    "395_astro_groups": sum(int(row["astro_group_count"]) for row in dossiers) == 395,
    "776_total_groups": sum(int(row["total_group_count"]) for row in dossiers) == 776,
    "no_written_pointer": all(row["cross_page_pointer"] == "NONE__MASTER_ASSEMBLES_CASE" for row in dossiers),
    "all_balanced_text": all(row["balanced_what_de"] and row["balanced_how_de"] and row["visible_condition_de"] for row in dossiers),
    "readable": (HERE / "THIRTY_FIRST_FOUR_COMPLETE_BALANCED_DOSSIERS.md").exists(),
    "report": (HERE / "THIRTY_FIRST_EDITION_REPORT.md").exists(),
}
sealed = "f" + "84"
checks["sealed_absent"] = all(
    sealed not in path.read_text(encoding="utf-8").lower()
    for path in HERE.iterdir()
    if path.is_file()
)
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
