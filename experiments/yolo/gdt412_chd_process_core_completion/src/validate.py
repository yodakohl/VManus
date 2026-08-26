#!/usr/bin/env python3
import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = ROOT / "experiments/yolo/gdt412_chd_process_core_completion"
OUT = HERE / "artifacts"
RUN = HERE / "src/run.py"


def read_tsv(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes():
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("gdt412_*")) if path.name != "gdt412_validation.json"}


def main():
    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True)
    first = hashes()
    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True)
    second = hashes()
    occurrences = read_tsv("gdt412_301_chd_occurrence_comparison.tsv")
    families = read_tsv("gdt412_78_chd_recipe_families.tsv")
    matrix = read_tsv("gdt412_20_register_family_matrix.tsv")
    scores = read_tsv("gdt412_candidate_scorecard.tsv")
    contexts = read_tsv("gdt412_cross_register_family_contexts.tsv")
    dictionary = read_tsv("gdt412_final_19_core_dictionary.tsv")
    result = json.loads((OUT / "gdt412_result.json").read_text(encoding="utf-8"))
    family_counts = Counter(row["family_class"] for row in occurrences)
    checks = {
        "occurrences_301": len(occurrences) == 301 and len({row["global_running_event_id"] for row in occurrences}) == 301,
        "families_78": len(families) == 78 and sum(int(row["event_count"]) for row in families) == 301,
        "matrix_20": len(matrix) == 20 and sum(int(row["event_count"]) for row in matrix) == 301,
        "score_rows_3": len(scores) == 3 and sum(row["selected"] == "YES" for row in scores) == 1,
        "class_counts_exact": family_counts == {"BARE_CHD_Y": 107, "TERMINAL_DY": 94, "OPEN_ARGUMENT_OR_RELATION": 89, "OTHER_OPEN": 11},
        "open_207_terminal_94": result["open_event_count"] == 207 and result["terminal_event_count"] == 94,
        "dictionary_19_all_keep": len(dictionary) == 19 and Counter(row["decision"] for row in dictionary) == {"KEEP": 19},
        "chd_bearbeiten": any(row["root"] == "CHD" and row["selected_minimal_value_de"] == "BEARBEITEN" for row in dictionary),
        "all_occurrence_readings": all(row["selected_event_reading_de"] and row["umsetzen_rival_reading_de"] and row["abschliessen_rival_reading_de"] for row in occurrences),
        "all_five_registers": {row["register"] for row in occurrences} == {"HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA", "SOURCE_SECTION_T"},
        "context_count_15": len(contexts) == 15,
        "status_exact": result["status"] == "NINETEEN_BROAD_WORKING_VALUES_COMPLETE__CHD_IS_PROCESS_NOT_CLOSE",
        "no_forbidden_page": not any("f84" in "\t".join(row.values()).lower() for table in (occurrences, families, matrix, scores, contexts, dictionary) for row in table),
        "deterministic_rebuild": first == second,
    }
    validation = {"status": "PASS" if all(checks.values()) else "FAIL", "check_count": len(checks), "failure_count": sum(not value for value in checks.values()), "checks": checks}
    (OUT / "gdt412_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
