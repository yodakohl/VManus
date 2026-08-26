#!/usr/bin/env python3
"""Validate GDT428 direct action-meaning contrasts."""

from __future__ import annotations

import csv
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
BASE = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt428_9_action_semantic_profiles.tsv",
        OUT / "gdt428_6_within_class_contrasts.tsv",
        OUT / "gdt428_104_direct_substitution_frames.tsv",
        OUT / "ACTION_MEANING_CONTRAST_DECK.md",
        OUT / "gdt428_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(
        ["python3", str(BASE / "src/run.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    after = {path: path.read_bytes() for path in tracked}
    profiles = read_tsv("gdt428_9_action_semantic_profiles.tsv")
    contrasts = read_tsv("gdt428_6_within_class_contrasts.tsv")
    frames = read_tsv("gdt428_104_direct_substitution_frames.tsv")
    result = json.loads((OUT / "gdt428_result.json").read_text(encoding="utf-8"))

    expected_meanings = {
        "CH": "NEHMEN", "S": "WÄHLEN", "K": "GEBEN",
        "OK": "SETZEN", "P": "EINSETZEN", "SH": "HALTEN",
        "CHD": "BEARBEITEN", "T": "EINSTELLEN", "R": "MARKIEREN",
    }
    expected_frames = {
        "CH~S": 12, "K~OK": 34, "K~P": 23,
        "OK~P": 10, "SH~CHD": 14, "T~R": 11,
    }
    frame_counts = Counter(row["contrast_pair"] for row in frames)
    profile_map = {row["action_root"]: row for row in profiles}
    checks = {
        "profiles_9": len(profiles) == 9,
        "profile_roots_exact": set(profile_map) == set(expected_meanings),
        "working_meanings_exact": all(profile_map[root]["working_meaning_de"] == meaning for root, meaning in expected_meanings.items()),
        "all_meanings_retained": all(profile_map[root]["decision"] == f"KEEP_{meaning}" for root, meaning in expected_meanings.items()),
        "action_mentions_3917": sum(int(row["mention_count"]) for row in profiles) == 3917,
        "all_roots_five_registers": all(row["register_count"] == "5" for row in profiles),
        "contrasts_6": len(contrasts) == 6,
        "contrast_pairs_exact": {row["contrast_pair"] for row in contrasts} == set(expected_frames),
        "all_contrasts_distinct": all(row["decision"] == "DISTINCT_MEANINGS_RETAINED" for row in contrasts),
        "frame_rows_104": len(frames) == 104,
        "frame_counts_exact": frame_counts == Counter(expected_frames),
        "all_frames_have_both_sides": all(int(row["left_event_count"]) > 0 and int(row["right_event_count"]) > 0 for row in frames),
        "all_frames_freeze_action_slot": all("@ACTION" in row["frozen_frame"] for row in frames),
        "ch_s_directional_contrast": "364/843" in next(row["decisive_distributional_contrast"] for row in contrasts if row["contrast_pair"] == "CH~S"),
        "k_ok_directional_contrast": "177/492" in next(row["decisive_distributional_contrast"] for row in contrasts if row["contrast_pair"] == "K~OK"),
        "p_bridge_contrast": "76/160" in next(row["decisive_distributional_contrast"] for row in contrasts if row["contrast_pair"] == "OK~P"),
        "sh_chd_grade_contrast": "463 Gradbindungen" in next(row["decisive_distributional_contrast"] for row in contrasts if row["contrast_pair"] == "SH~CHD"),
        "t_r_grade_contrast": "95 Gradbindungen" in next(row["decisive_distributional_contrast"] for row in contrasts if row["contrast_pair"] == "T~R"),
        "result_status": result["status"] == "NINE_ACTION_MEANINGS_RETAINED_WITH_DIRECT_CONTRAST_RULES",
        "result_counts": result["running_event_count"] == 4576 and result["focus_edge_count"] == 5051 and result["close_edge_count"] == 639,
        "no_meaning_revision": result["meaning_revisions"] == 0,
        "no_new_roots": result["new_roots"] == 0,
        "no_new_pages": result["new_pages"] == 0,
        "no_forbidden_page": all("f84" not in path.read_text(encoding="utf-8").lower() for path in tracked),
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt428_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
