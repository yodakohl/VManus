#!/usr/bin/env python3
"""Validate the GDT402 factorized selector/head replay."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "artifacts"
RUN = HERE / "src/run.py"
SOURCE = ROOT / "experiments/yolo/gdt399_creative_scope_rebuild_after_visible_resegmentation/artifacts/gdt399_4374_scope_attachments.tsv"
REPLAY = OUT / "gdt402_4374_factorized_replay.tsv"
AXES = OUT / "gdt402_axis_inventory.tsv"
FORMER = OUT / "gdt402_four_former_amber.tsv"
SUMMARY = OUT / "gdt402_22_page_4_register_replay.tsv"
RESULT = OUT / "gdt402_result.json"
VALIDATION = OUT / "gdt402_validation.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source = read_tsv(SOURCE)
    replay = read_tsv(REPLAY)
    axes = read_tsv(AXES)
    former = read_tsv(FORMER)
    summary = read_tsv(SUMMARY)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: dict[str, dict[str, object]] = {}

    def check(name: str, condition: bool, observed: object) -> None:
        checks[name] = {"pass": bool(condition), "observed": observed}

    check("source_count", len(source) == 4374, len(source))
    check("replay_count", len(replay) == 4374, len(replay))
    check("replay_identity", [row["attachment_id"] for row in replay] == [row["attachment_id"] for row in source], len(replay))
    check("unique_factorized_ids", len({row["factorized_id"] for row in replay}) == 4374, len({row["factorized_id"] for row in replay}))
    check("all_factorized_pass", all(row["factorized_result"] == "PASS_FACTORIZED_SELECTOR_AND_HEAD" for row in replay), Counter(row["factorized_result"] for row in replay))
    check("all_selector_outside_page", all(row["selector_outside_page_level"] != "NONE" for row in replay), Counter(row["selector_outside_page_level"] for row in replay))
    check("all_selector_outside_register", all(row["selector_outside_register_level"] != "NONE" for row in replay), Counter(row["selector_outside_register_level"] for row in replay))
    check("all_heads_outside_page", all(row["head_outside_page"] == "YES" for row in replay), Counter(row["head_outside_page"] for row in replay))
    check("all_heads_outside_register", all(row["head_outside_register"] == "YES" for row in replay), Counter(row["head_outside_register"] for row in replay))
    check("no_owner_crossing", all(row["owner_boundary_crossed"] == "NO" for row in replay), Counter(row["owner_boundary_crossed"] for row in replay))
    check("lookahead_at_most_one", max(int(row["lookahead_cards"]) for row in replay) <= 1, max(int(row["lookahead_cards"]) for row in replay))
    check("axis_inventory_count", len(axes) == 31, Counter(row["axis"] for row in axes))
    axis_counts = Counter(row["axis"] for row in axes)
    check("axis_value_counts", axis_counts == Counter({"SCOPE_SELECTOR": 8, "ACTION_HEAD": 10, "R_TOPOLOGY": 4, "DUPLICATE_MODE": 3, "ATTACHMENT_GEOMETRY": 6}), dict(axis_counts))
    check("eight_scope_selectors", {row["value"] for row in axes if row["axis"] == "SCOPE_SELECTOR"} == {
        "AL_AR_ORDERED_FALLBACK", "INHERITED_ACTION_STACK", "L_AIR_RIGHT_FALLBACK",
        "NEAREST_HEAD_LEFT_TIE", "ONE_CARD_FORWARD", "OWNER_CONTEXT",
        "PREVIOUS_CARD_STACK", "Q_OT_PACKAGE_FORWARD",
    }, sorted(row["value"] for row in axes if row["axis"] == "SCOPE_SELECTOR"))
    check("ten_heads_all_registers", all(row["register_count"] == "4" for row in axes if row["axis"] == "ACTION_HEAD"), [(row["value"], row["register_count"]) for row in axes if row["axis"] == "ACTION_HEAD"])
    check("former_amber_count", len(former) == 4, len(former))
    check("former_amber_ids", {row["attachment_id"] for row in former} == {"G399-A01468", "G399-A02820", "G399-A03234", "G399-A03235"}, sorted(row["attachment_id"] for row in former))
    check("former_amber_exact_selector", all(row["selector_outside_register_level"] == "EXACT_PAYLOAD_SELECTOR" for row in former), [row["selector_outside_register_level"] for row in former])
    check("former_amber_head_direct", all(row["head_outside_register"] == "YES" and row["r_topology_support"] == "DIRECT_OUTSIDE_REGISTER" for row in former), [(row["head_outside_register"], row["r_topology_support"]) for row in former])
    check("summary_count", len(summary) == 26, Counter(row["unit_kind"] for row in summary))
    check("twenty_running_pages_pass", Counter(row["result"] for row in summary if row["unit_kind"] == "PAGE") == Counter({"PASS": 20, "ADDRESS_ONLY": 2}), Counter(row["result"] for row in summary if row["unit_kind"] == "PAGE"))
    check("four_registers_pass", Counter(row["result"] for row in summary if row["unit_kind"] == "REGISTER") == Counter({"PASS": 4}), Counter(row["result"] for row in summary if row["unit_kind"] == "REGISTER"))
    base_fallbacks = [row for row in replay if row["selector_outside_register_level"] == "BASE_SELECTOR"]
    check("one_known_base_fallback", len(base_fallbacks) == 1 and base_fallbacks[0]["attachment_id"] == "G399-A02411", [(row["attachment_id"], row["surface"]) for row in base_fallbacks])
    check("nested_r_single_visible", Counter(row["r_topology_support"] for row in replay)["VISIBLE_R_TOPOLOGY_DERIVATION"] == 1, Counter(row["r_topology_support"] for row in replay))
    check("package_descent_two_visible", Counter(row["duplicate_support"] for row in replay)["VISIBLE_PACKAGE_NESTING_DERIVATION"] == 2, Counter(row["duplicate_support"] for row in replay))
    check("result_status", result["status"] == "COMPLETE_FACTORIZED_SCOPE_PARSER__NO_FALSE_AMBER", result["status"])
    check("result_counts", result["factorized_pass_count"] == 4374 and result["factorized_fail_count"] == 0, {"pass": result["factorized_pass_count"], "fail": result["factorized_fail_count"]})
    check("result_axis_counts", [result["scope_selector_count"], result["action_head_count"], result["attachment_geometry_count"]] == [8, 10, 6], [result["scope_selector_count"], result["action_head_count"], result["attachment_geometry_count"]])
    check("sealed_pages_absent", not any(row["physical_page"].startswith("f84") for row in replay), sorted({row["physical_page"] for row in replay if row["physical_page"].startswith("f84")}))
    check("result_hashes", all(sha256(OUT / name) == digest for name, digest in result["output_hashes"].items()), len(result["output_hashes"]))

    tracked = [REPLAY, AXES, FORMER, SUMMARY, RESULT, HERE / "REPORT.md", HERE / "DETERMINISTIC_NEXT_PAGE_PARSER.md"]
    before = {path.name: sha256(path) for path in tracked}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False)
    after = {path.name: sha256(path) for path in tracked}
    check("deterministic_rebuild", completed.returncode == 0 and before == after, {"returncode": completed.returncode, "hashes_equal": before == after})

    failures = [name for name, value in checks.items() if not value["pass"]]
    payload = {
        "status": "PASS" if not failures else "FAIL",
        "check_count": len(checks),
        "failed_checks": failures,
        "checks": checks,
        "validated_hashes": after,
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
