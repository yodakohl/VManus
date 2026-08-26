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
HERE = ROOT / "experiments/yolo/gdt411_provisional_core_process_position"
OUT = HERE / "artifacts"
RUN = HERE / "src/run.py"


def read_tsv(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest_outputs():
    names = (
        "gdt411_81_action_transition_matrix.tsv",
        "gdt411_five_core_candidate_scorecard.tsv",
        "gdt411_five_core_process_profiles.tsv",
        "gdt411_25_cross_register_statement_examples.tsv",
        "gdt411_final_19_core_dictionary.tsv",
        "gdt411_result.json",
    )
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> int:
    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True)
    first = digest_outputs()
    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True)
    second = digest_outputs()
    transitions = read_tsv("gdt411_81_action_transition_matrix.tsv")
    scores = read_tsv("gdt411_five_core_candidate_scorecard.tsv")
    profiles = read_tsv("gdt411_five_core_process_profiles.tsv")
    examples = read_tsv("gdt411_25_cross_register_statement_examples.tsv")
    dictionary = read_tsv("gdt411_final_19_core_dictionary.tsv")
    result = json.loads((OUT / "gdt411_result.json").read_text(encoding="utf-8"))
    checks = {
        "transitions_81": len(transitions) == 81,
        "scores_15": len(scores) == 15,
        "profiles_5": len(profiles) == 5,
        "examples_25": len(examples) == 25,
        "dictionary_19": len(dictionary) == 19 and len({row["root"] for row in dictionary}) == 19,
        "selected_once_per_root": all(sum(row["selected_value"] == "YES" for row in scores if row["root"] == root) == 1 for root in {row["root"] for row in scores}),
        "every_target_all_registers": all(len({row["register"] for row in examples if row["root"] == root}) == 5 for root in {row["root"] for row in profiles}),
        "transition_symmetry_accounting": all(int(row["left_to_right_count"]) - int(row["right_to_left_count"]) == int(row["directional_delta"]) for row in transitions),
        "ch_to_k_216_98": any(row["left_action"] == "CH" and row["right_action"] == "K" and row["left_to_right_count"] == "216" and row["right_to_left_count"] == "98" for row in transitions),
        "final_decisions_18_1": Counter(row["decision"] for row in dictionary) == {"KEEP": 18, "KEEP_PROVISIONAL": 1},
        "chd_only_provisional": [row["root"] for row in dictionary if row["decision"] == "KEEP_PROVISIONAL"] == ["CHD"],
        "air_is_bahn": any(row["root"] == "AIR" and row["selected_minimal_value_de"] == "BAHN" for row in dictionary),
        "all_examples_nonempty": all(row["surface_sequence"] and row["recipe_sequence"] and row["revised_literal_core_reading_de"] for row in examples),
        "no_forbidden_page": not any("f84" in "\t".join(row.values()).lower() for table in (transitions, scores, profiles, examples, dictionary) for row in table),
        "status_exact": result["status"] == "FOUR_MORE_CORES_STABILIZED__CHD_REMAINS_PROVISIONAL",
        "deterministic_rebuild": first == second,
    }
    validation = {"status": "PASS" if all(checks.values()) else "FAIL", "check_count": len(checks), "failure_count": sum(not value for value in checks.values()), "checks": checks}
    (OUT / "gdt411_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
