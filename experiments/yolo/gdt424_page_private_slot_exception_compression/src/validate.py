#!/usr/bin/env python3
"""Validate GDT424 red-cell compression."""

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
BASE = ROOT / "experiments/yolo/gdt424_page_private_slot_exception_compression"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt424_59_red_event_factorization.tsv",
        OUT / "gdt424_92_focus_edge_replay.tsv",
        OUT / "gdt424_14_private_pair_event_adjudications.tsv",
        OUT / "gdt424_9_close_edge_replay.tsv",
        OUT / "gdt424_57_red_cell_compression.tsv",
        OUT / "gdt424_7_local_appendix_rules.tsv",
        OUT / "MINIMAL_LOCAL_ACTION_APPENDIX.md",
        OUT / "gdt424_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    events = read_tsv("gdt424_59_red_event_factorization.tsv")
    focus = read_tsv("gdt424_92_focus_edge_replay.tsv")
    pairs = read_tsv("gdt424_14_private_pair_event_adjudications.tsv")
    closes = read_tsv("gdt424_9_close_edge_replay.tsv")
    cells = read_tsv("gdt424_57_red_cell_compression.tsv")
    appendix = read_tsv("gdt424_7_local_appendix_rules.tsv")
    result = json.loads((OUT / "gdt424_result.json").read_text(encoding="utf-8"))

    checks = {
        "red_events_59": len(events) == 59,
        "red_event_ids_unique": len({row["global_running_event_id"] for row in events}) == 59,
        "focus_edges_92": len(focus) == 92,
        "focus_edges_90_cross_page": sum(row["factorized_replay_status"] == "OLD_FOCUS_EDGE_OTHER_PAGE" for row in focus) == 90,
        "focus_edges_2_local": sum(row["factorized_replay_status"] == "LOCAL_FOCUS_EDGE" for row in focus) == 2,
        "private_pair_events_14": len(pairs) == 14,
        "private_pair_splits_9": sum(row["pair_decision"] == "SPLIT_BY_VISIBLE_PACKAGE_OR_R_TOPOLOGY" for row in pairs) == 9,
        "private_adjacent_pairs_5": sum(row["pair_decision"] == "LOCAL_ADJACENT_ORDERED_PAIR" for row in pairs) == 5,
        "close_edges_9": len(closes) == 9,
        "close_edges_8_cross_page": sum(row["close_replay_status"] == "OLD_TERMINAL_HEAD_CLOSE_OTHER_PAGE" for row in closes) == 8,
        "close_edges_1_local": sum(row["close_replay_status"] == "LOCAL_TERMINAL_HEAD_CLOSE" for row in closes) == 1,
        "red_cells_57": len(cells) == 57,
        "resolved_cells_50": sum(row["compression_status"] == "RESOLVED_CELL" for row in cells) == 50,
        "appendix_cells_7": sum(row["compression_status"] == "LOCAL_APPENDIX_CELL" for row in cells) == 7,
        "resolved_events_52": sum(row["compression_status"] == "RESOLVED_BY_FACTORIZED_OLD_RULES" for row in events) == 52,
        "appendix_events_7": sum(row["compression_status"] == "LOCAL_APPENDIX_RULE_REQUIRED" for row in events) == 7,
        "appendix_rules_7": len(appendix) == 7,
        "appendix_rule_ids_unique": len({row["rule_id"] for row in appendix}) == 7,
        "appendix_types_5_pairs_1_focus_1_package": sum(row["rule_type"] == "LOCAL_ADJACENT_ORDERED_PAIR" for row in appendix) == 5 and sum(row["rule_type"] == "LOCAL_FOCUS_EDGE" for row in appendix) == 1 and sum(row["rule_type"] == "LOCAL_COMPOSITE_PACKAGE" for row in appendix) == 1,
        "appendix_pages_6": len({page for row in appendix for page in row["pages"].split("|")}) == 6,
        "all_local_until_second_page": all(row["portable_status"] == "LOCAL_ONLY_UNTIL_SECOND_PAGE" for row in appendix),
        "no_forbidden_page": all("f84" not in path.read_text(encoding="utf-8").lower() for path in tracked),
        "no_new_roots": result["new_roots"] == 0,
        "no_dictionary_revisions": result["dictionary_revisions"] == 0,
        "no_new_pages": result["new_pages"] == 0,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt424_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
