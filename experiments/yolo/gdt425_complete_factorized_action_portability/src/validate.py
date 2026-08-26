#!/usr/bin/env python3
"""Validate GDT425 complete factorized action portability."""

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
BASE = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt425_4576_event_factorized_action_replay.tsv",
        OUT / "gdt425_5051_focus_edge_portability.tsv",
        OUT / "gdt425_649_adjacent_pair_portability.tsv",
        OUT / "gdt425_639_close_edge_portability.tsv",
        OUT / "gdt425_9_local_action_appendix.tsv",
        OUT / "gdt425_7_gdt424_rule_revisions.tsv",
        OUT / "gdt425_24_page_summary.tsv",
        OUT / "COMPLETE_ACTION_GRAMMAR_CARD.md",
        OUT / "gdt425_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}
    events = read_tsv("gdt425_4576_event_factorized_action_replay.tsv")
    focus = read_tsv("gdt425_5051_focus_edge_portability.tsv")
    pairs = read_tsv("gdt425_649_adjacent_pair_portability.tsv")
    closes = read_tsv("gdt425_639_close_edge_portability.tsv")
    appendix = read_tsv("gdt425_9_local_action_appendix.tsv")
    revisions = read_tsv("gdt425_7_gdt424_rule_revisions.tsv")
    pages = read_tsv("gdt425_24_page_summary.tsv")
    result = json.loads((OUT / "gdt425_result.json").read_text(encoding="utf-8"))

    checks = {
        "events_4576": len(events) == 4576,
        "event_ids_unique": len({row["global_running_event_id"] for row in events}) == 4576,
        "action_events_4558": sum(row["explicit_action_roots"] != "NONE" or row["inherited_action_root"] != "NONE" for row in events) == 4558,
        "cross_page_action_events_4549": sum(row["factorized_action_replay_status"] == "CROSS_PAGE_ACTION_FACTORS_COMPLETE" for row in events) == 4549,
        "local_action_events_9": sum(row["factorized_action_replay_status"] == "LOCAL_ACTION_APPENDIX_REQUIRED" for row in events) == 9,
        "local_owner_only_1": sum(row["factorized_action_replay_status"] == "LOCAL_OWNER_CHANNEL_ONLY" for row in events) == 1,
        "outside_action_17": sum(row["factorized_action_replay_status"] == "OUTSIDE_ACTION_GRAMMAR_NO_ACTION_HEAD" for row in events) == 17,
        "focus_edges_5051": len(focus) == 5051,
        "focus_cross_page_5047": sum(row["portability_status"] == "CROSS_PAGE_EXACT_FOCUS_EDGE" for row in focus) == 5047,
        "focus_local_action_3": sum(row["portability_status"] == "LOCAL_ACTION_FOCUS_EDGE" for row in focus) == 3,
        "focus_local_owner_1": sum(row["portability_status"] == "LOCAL_OWNER_CHANNEL_ALLOWED" for row in focus) == 1,
        "adjacent_pairs_649": len(pairs) == 649,
        "adjacent_pairs_cross_page_641": sum(row["portability_status"] == "CROSS_PAGE_EXACT_ADJACENT_PAIR" for row in pairs) == 641,
        "adjacent_pairs_old_special_2": sum(row["portability_status"] in {"OLD_REPEATED_ACTION_SCOPE", "OLD_R_TOPOLOGY_SPLIT"} for row in pairs) == 2,
        "adjacent_pairs_local_6": sum(row["portability_status"] == "LOCAL_ADJACENT_PAIR" for row in pairs) == 6,
        "closes_639": len(closes) == 639,
        "all_closes_cross_page": all(row["portability_status"] == "CROSS_PAGE_ACTION_CLOSE" and int(row["other_page_count"]) > 0 for row in closes),
        "appendix_rules_9": len(appendix) == 9,
        "appendix_ids_unique": len({row["rule_id"] for row in appendix}) == 9,
        "appendix_6_pairs_3_focus": sum(row["rule_type"] == "LOCAL_ADJACENT_PAIR" for row in appendix) == 6 and sum(row["rule_type"] == "LOCAL_ACTION_FOCUS_EDGE" for row in appendix) == 3,
        "gdt424_revisions_7": len(revisions) == 7,
        "gdt424_promotions_3": sum(row["gdt425_decision"] == "PROMOTED_CROSS_PAGE_FROM_COMPLEX_CONTEXT" for row in revisions) == 3,
        "pages_24": len(pages) == 24,
        "page_event_sum_4576": sum(int(row["event_count"]) for row in pages) == 4576,
        "no_forbidden_page": all("f84" not in path.read_text(encoding="utf-8").lower() for path in tracked),
        "no_new_roots": result["new_roots"] == 0,
        "no_dictionary_revisions": result["dictionary_revisions"] == 0,
        "no_new_pages": result["new_pages"] == 0,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {"status": "PASS" if not failed else "FAIL", "check_count": len(checks), "failure_count": len(failed), "checks": checks}
    (OUT / "gdt425_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
