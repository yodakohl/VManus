#!/usr/bin/env python3
"""Validate GDT423 leave-one-page action grammar replay."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt423_leave_one_page_action_grammar_replay"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt423_4576_event_leave_page_replay.tsv",
        OUT / "gdt423_1129_page_slot_cell_replay.tsv",
        OUT / "gdt423_24_page_key_summary.tsv",
        OUT / "gdt423_57_red_page_slot_cells.tsv",
        OUT / "NEXT_PAGE_ACTION_GRAMMAR_CARD.md",
        OUT / "gdt423_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    events = read_tsv("gdt423_4576_event_leave_page_replay.tsv")
    cells = read_tsv("gdt423_1129_page_slot_cell_replay.tsv")
    pages = read_tsv("gdt423_24_page_key_summary.tsv")
    red = read_tsv("gdt423_57_red_page_slot_cells.tsv")
    result = json.loads((OUT / "gdt423_result.json").read_text(encoding="utf-8"))
    clean = [row for row in events if row["grammar_category"] in {"CLEAN_SINGLE_HEAD", "CLEAN_ORDERED_PAIR"}]

    checks = {
        "events_4576": len(events) == 4576,
        "event_ids_unique": len({row["global_running_event_id"] for row in events}) == 4576,
        "page_keys_24": len(pages) == 24,
        "page_cells_1129": len(cells) == 1129,
        "page_cell_keys_unique": len({(row["held_out_page"], row["slot_skeleton"]) for row in cells}) == 1129,
        "red_cells_57": len(red) == 57,
        "clean_events_2662": len(clean) == 2662,
        "green_clean_2553": sum(row["leave_page_replay_status"] == "GREEN_EXACT_SLOT_SKELETON_FROM_OTHER_PAGE" for row in clean) == 2553,
        "amber_clean_50": sum(row["leave_page_replay_status"] == "AMBER_MARGINS_OLD_COMBINATION_NEW" for row in clean) == 50,
        "red_clean_59": sum(row["leave_page_replay_status"] == "RED_PAGE_PRIVATE_HEAD_OR_SLOT" for row in clean) == 59,
        "category_distribution": {category: sum(row["grammar_category"] == category for row in events) for category in {row["grammar_category"] for row in events}} == {
            "CLEAN_SINGLE_HEAD": 2099,
            "CLEAN_ORDERED_PAIR": 563,
            "NONCLEAN_SINGLE_HEAD": 85,
            "NONCLEAN_ORDERED_PAIR": 45,
            "LONG_ACTION_CHAIN": 168,
            "NO_ACTION_HEAD": 1616,
        },
        "red_causes_nonempty": all(row["red_causes"] != "NONE" for row in red),
        "all_long_chains_green": all(row["leave_page_replay_status"] == "GREEN_LONG_CHAIN_REDUCED_BY_GDT422" for row in events if row["grammar_category"] == "LONG_ACTION_CHAIN"),
        "all_no_action_outside_scope": all(row["leave_page_replay_status"] == "OUTSIDE_ACTION_GRAMMAR__ROOT_READING_UNCHANGED" for row in events if row["grammar_category"] == "NO_ACTION_HEAD"),
        "page_sums_events": sum(int(row["event_count"]) for row in pages) == 4576,
        "page_sums_clean": sum(int(row["clean_slot_event_count"]) for row in pages) == 2662,
        "no_forbidden_page": all("f84" not in path.read_text(encoding="utf-8").lower() for path in tracked),
        "no_new_pages": result["new_pages"] == 0,
        "no_dictionary_revisions": result["dictionary_revisions"] == 0,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt423_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
