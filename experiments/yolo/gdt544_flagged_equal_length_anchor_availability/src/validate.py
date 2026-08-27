#!/usr/bin/env python3
"""Independent validation for GDT544."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt544_flagged_equal_length_anchor_availability"
OUT = BASE / "artifacts"
G543 = ROOT / "experiments/yolo/gdt543_fragment_directional_extension_frames/artifacts"
CARD_IN = G543 / "gdt543_81_fragment_extension_cards.tsv"
CANDIDATE_IN = G543 / "gdt543_104_longest_anchor_candidates.tsv"
ARM_IN = G543 / "gdt543_93_directional_extension_arms.tsv"
FLAGGED_OUT = OUT / "gdt544_16_flagged_target_anchor_availability.tsv"
UNUSED_OUT = OUT / "gdt544_23_unused_candidate_owners.tsv"
SUMMARY_OUT = OUT / "gdt544_anchor_availability_summary.tsv"
BOOK_OUT = OUT / "GDT544_EQUAL_LENGTH_ANCHOR_AVAILABILITY.md"
RESULT_OUT = OUT / "gdt544_result.json"
VALIDATION_OUT = OUT / "gdt544_validation.json"
RUNNER = BASE / "src/run.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cards = read_tsv(CARD_IN)
    candidates = read_tsv(CANDIDATE_IN)
    arms = read_tsv(ARM_IN)
    flagged_rows = read_tsv(FLAGGED_OUT)
    unused_rows = read_tsv(UNUSED_OUT)
    summary = read_tsv(SUMMARY_OUT)
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    checks = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("gdt543_card_count", len(cards) == 81, len(cards))
    check("gdt543_candidate_count", len(candidates) == 104, len(candidates))
    check("gdt543_arm_count", len(arms) == 93, len(arms))
    check("flagged_row_count", len(flagged_rows) == 16, len(flagged_rows))
    check("unused_row_count", len(unused_rows) == 23, len(unused_rows))

    context_flags = {row["surface"] for row in cards if row["anchor_context_relation"] == "TARGET_MODE_SET_DISJOINT"}
    interface_flags = {row["target_surface"] for row in arms if int(row["old_interface_event_count"]) == 0}
    flagged = context_flags | interface_flags
    check("context_flag_count", len(context_flags) == 12, sorted(context_flags))
    check("interface_flag_count", len(interface_flags) == 6, sorted(interface_flags))
    check("flag_overlap_count", len(context_flags & interface_flags) == 2 and context_flags & interface_flags == {"chady", "chap"}, sorted(context_flags & interface_flags))
    check("flag_union_count", len(flagged) == 16, sorted(flagged))
    check("flagged_surface_set", {row["surface"] for row in flagged_rows} == flagged, sorted({row["surface"] for row in flagged_rows} ^ flagged))

    candidates_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        candidates_by_surface[row["surface"]].append(row)
    multiplicity = Counter(len(candidates_by_surface[surface]) for surface in flagged)
    check("all_flagged_have_one_candidate", multiplicity == Counter({1: 16}), dict(sorted(multiplicity.items())))
    flagged_unused = [row for row in candidates if row["surface"] in flagged and row["selected"] == "NO"]
    check("zero_flagged_unused_candidates", not flagged_unused, flagged_unused)

    expected_unused = {
        (row["surface"], row["anchor_recipe"], row["anchor_start_atom"])
        for row in candidates
        if row["selected"] == "NO"
    }
    actual_unused = {
        (row["surface"], row["unused_anchor_recipe"], row["anchor_start_atom"])
        for row in unused_rows
    }
    check("unused_inventory_exact", expected_unused == actual_unused, sorted(expected_unused ^ actual_unused))
    unused_owners = {row["surface"] for row in unused_rows}
    check("unused_owner_count", len(unused_owners) == 20, len(unused_owners))
    check("unused_owners_disjoint_from_flags", not unused_owners & flagged, sorted(unused_owners & flagged))
    clean_multiplicity = Counter(len(candidates_by_surface[surface]) for surface in unused_owners)
    check("clean_multioption_multiplicity", clean_multiplicity == Counter({2: 17, 3: 3}), dict(sorted(clean_multiplicity.items())))
    check("unused_rows_mark_clean", all(row["target_is_flagged"] == "NO" and row["ownership_class"] == "CLEAN_TARGET_UNUSED_OPTION" for row in unused_rows), sorted(row["surface"] for row in unused_rows if row["target_is_flagged"] != "NO" or row["ownership_class"] != "CLEAN_TARGET_UNUSED_OPTION"))

    flagged_row_failures = []
    for row in flagged_rows:
        surface = row["surface"]
        reasons = set(row["flag_reasons"].split("|"))
        expected_reasons = ({"ANCHOR_CONTEXT_MODE_DIFFERENCE"} if surface in context_flags else set()) | ({"NEW_ATOM_INTERFACE"} if surface in interface_flags else set())
        if reasons != expected_reasons or row["equal_length_candidate_count"] != "1" or row["unused_equal_length_candidate_count"] != "0" or row["decision"] != "NO_EQUAL_LENGTH_REANCHOR_AVAILABLE":
            flagged_row_failures.append(surface)
    check("flagged_rows_replay", not flagged_row_failures, flagged_row_failures)

    summary_map = {row["metric"]: row["value"] for row in summary}
    check("summary_core_metrics", all(summary_map.get(key) == value for key, value in {
        "context_flag_target_count": "12",
        "new_interface_target_count": "6",
        "overlap_target_count": "2",
        "union_flagged_target_count": "16",
        "flagged_unused_equal_length_candidate_count": "0",
        "total_unused_equal_length_candidate_count": "23",
        "unused_candidate_owner_target_count": "20",
    }.items()), summary_map)
    book = BOOK_OUT.read_text(encoding="utf-8")
    check("book_status", result["status"] in book, result["status"])
    check("book_flagged_inventory", sum(f"`{surface}`" in book for surface in flagged) == 16, sum(f"`{surface}`" in book for surface in flagged))
    check("book_clean_owner_inventory", all(f"`{surface}`" in book for surface in unused_owners), len(unused_owners))

    expected_result = {
        "status": "ZERO_FLAGGED_TARGETS_HAVE_ALTERNATIVE_LONGEST_ANCHOR__23_UNUSED_BELONG_TO_20_CLEAN_TARGETS",
        "context_flag_target_count": 12,
        "new_interface_target_count": 6,
        "overlap_target_count": 2,
        "union_flagged_target_count": 16,
        "flagged_target_with_unused_equal_length_anchor_count": 0,
        "flagged_unused_equal_length_candidate_count": 0,
        "total_unused_equal_length_candidate_count": 23,
        "unused_candidate_owner_target_count": 20,
        "unused_candidate_clean_owner_count": 20,
        "unused_candidate_flagged_owner_count": 0,
        "all_flagged_candidate_multiplicity": {"1": 16},
        "clean_multioption_target_multiplicity": {"2": 17, "3": 3},
        "new_pages": 0,
        "card_changes": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    check("result_exact", result == expected_result, result)

    generated = [FLAGGED_OUT, UNUSED_OUT, SUMMARY_OUT, BOOK_OUT, RESULT_OUT]
    before = {path.name: digest(path) for path in generated}
    rerun = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    after = {path.name: digest(path) for path in generated}
    check("generator_rerun_exit", rerun.returncode == 0, rerun.stdout)
    check("generator_byte_determinism", before == after, after)

    failed = [row for row in checks if not row["passed"]]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
