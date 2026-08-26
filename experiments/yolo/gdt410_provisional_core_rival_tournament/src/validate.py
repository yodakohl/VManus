#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    subprocess.run(["python3", str(HERE / "src/run.py")], cwd=ROOT, check=True)
    paths = sorted(OUT.glob("gdt410_*.tsv"))
    first = {str(path): digest(path) for path in paths}
    subprocess.run(["python3", str(HERE / "src/run.py")], cwd=ROOT, check=True)
    second = {str(path): digest(path) for path in paths}
    scores = rows("gdt410_candidate_scorecard.tsv")
    profiles = rows("gdt410_ten_core_complement_profiles.tsv")
    samples = rows("gdt410_50_full_statement_rival_readings.tsv")
    dictionary = rows("gdt410_final_19_core_dictionary.tsv")
    result = json.loads((OUT / "gdt410_result.json").read_text(encoding="utf-8"))
    checks = {
        "scores_30": len(scores) == 30,
        "profiles_10": len(profiles) == 10,
        "samples_50": len(samples) == 50,
        "dictionary_19": len(dictionary) == 19,
        "one_selected_per_root": all(sum(row["selected_value"] == "YES" for row in scores if row["root"] == root) == 1 for root in {row["root"] for row in scores}),
        "selected_score_not_below_rivals": all(int(row["selection_margin"]) >= 0 for row in profiles),
        "five_promoted": len(result["promoted_roots"]) == 5,
        "five_provisional": len(result["remaining_provisional_roots"]) == 5,
        "final_decisions_14_5": result["final_decision_counts"] == {"KEEP": 14, "KEEP_PROVISIONAL": 5},
        "no_empty_reading": all(row["selected_literal_reading_de"] and row["rival_a_literal_reading_de"] and row["rival_b_literal_reading_de"] for row in samples),
        "deterministic_rebuild": first == second,
        "status_exact": result["status"] == "FIVE_PROVISIONAL_VALUES_REMAIN__FIVE_PROMOTED_BY_FULL_STATEMENT_RIVALS",
        "no_forbidden_page": not any("f84" in "\t".join(row.values()).lower() for table in (scores, profiles, samples, dictionary) for row in table),
    }
    validation = {"status": "PASS" if all(checks.values()) else "FAIL", "check_count": len(checks), "failure_count": sum(not value for value in checks.values()), "checks": checks}
    (OUT / "gdt410_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
