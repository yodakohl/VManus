#!/usr/bin/env python3
"""Validate GDT429 direct non-action semantic contrasts."""

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
BASE = ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt429_10_nonaction_semantic_profiles.tsv",
        OUT / "gdt429_13_nonaction_core_contrasts.tsv",
        OUT / "gdt429_256_direct_substitution_frames.tsv",
        OUT / "NONACTION_MEANING_CONTRAST_DECK.md",
        OUT / "gdt429_result.json",
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
    profiles = read_tsv("gdt429_10_nonaction_semantic_profiles.tsv")
    contrasts = read_tsv("gdt429_13_nonaction_core_contrasts.tsv")
    frames = read_tsv("gdt429_256_direct_substitution_frames.tsv")
    result = json.loads((OUT / "gdt429_result.json").read_text(encoding="utf-8"))

    expected_meanings = {
        "Y": "POSTEN", "AIIN": "WERT", "AIN": "ANTEIL", "OR": "EINHEIT",
        "AL": "ZIELORT", "AR": "AUSGANG", "L": "VERBINDUNG", "AIR": "BAHN",
        "OL": "FORTSETZEN", "OT": "DANACH",
    }
    expected_frames = {
        "Y~AIIN": 37, "Y~AIN": 23, "Y~OR": 38,
        "AIIN~AIN": 23, "AIIN~OR": 27, "AIN~OR": 16,
        "AL~AR": 32, "AL~L": 16, "AL~AIR": 8,
        "AR~L": 9, "AR~AIR": 10, "L~AIR": 3,
        "OL~OT": 14,
    }
    profile_map = {row["core_root"]: row for row in profiles}
    frame_counts = Counter(row["contrast_pair"] for row in frames)
    contrast_map = {row["contrast_pair"]: row for row in contrasts}
    checks = {
        "profiles_10": len(profiles) == 10,
        "profile_roots_exact": set(profile_map) == set(expected_meanings),
        "working_meanings_exact": all(profile_map[root]["working_meaning_de"] == meaning for root, meaning in expected_meanings.items()),
        "all_meanings_retained": all(profile_map[root]["decision"] == f"KEEP_{meaning}" for root, meaning in expected_meanings.items()),
        "nonaction_mentions_4588": sum(int(row["mention_count"]) for row in profiles) == 4588,
        "all_roots_five_registers": all(row["register_count"] == "5" for row in profiles),
        "contrasts_13": len(contrasts) == 13,
        "contrast_pairs_exact": set(contrast_map) == set(expected_frames),
        "all_contrasts_distinct": all(row["decision"] == "DISTINCT_MEANINGS_RETAINED" for row in contrasts),
        "frame_rows_256": len(frames) == 256,
        "frame_counts_exact": frame_counts == Counter(expected_frames),
        "all_frames_have_both_sides": all(int(row["left_event_count"]) > 0 and int(row["right_event_count"]) > 0 for row in frames),
        "all_frames_freeze_core_slot": all("@CORE" in row["frozen_frame"] for row in frames),
        "argument_carry_contrast": "152×" in contrast_map["Y~AIIN"]["decisive_distributional_contrast"],
        "value_share_register_contrast": "CELESTIAL 70/432" in contrast_map["AIIN~AIN"]["decisive_distributional_contrast"],
        "target_source_contrast": "12× am Aussagestart" in contrast_map["AL~AR"]["decisive_distributional_contrast"],
        "connection_path_contrast": "127 Handlungen" in contrast_map["L~AIR"]["decisive_distributional_contrast"],
        "order_contrast": "OL endet 420×, OT 2×" in contrast_map["OL~OT"]["decisive_distributional_contrast"],
        "result_status": result["status"] == "TEN_NONACTION_MEANINGS_RETAINED_WITH_DIRECT_CONTRAST_RULES",
        "result_counts": result["running_event_count"] == 4576 and result["focus_edge_count"] == 5051,
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
    (OUT / "gdt429_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
