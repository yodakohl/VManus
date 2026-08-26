#!/usr/bin/env python3
"""Validate GDT401 transition grouping and two-stage scope closure."""

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
TRANSITIONS = OUT / "gdt401_three_transition_adjudication.tsv"
RESOLUTIONS = OUT / "gdt401_four_attachment_resolution.tsv"
PARENTS = OUT / "gdt401_parent_examples.tsv"
FACTORS = OUT / "gdt401_factor_support.tsv"
DECK = OUT / "gdt401_error_deck_v2.tsv"
RESULT = OUT / "gdt401_result.json"
VALIDATION = OUT / "gdt401_validation.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source = read_tsv(SOURCE)
    transitions = read_tsv(TRANSITIONS)
    resolutions = read_tsv(RESOLUTIONS)
    parents = read_tsv(PARENTS)
    factors = read_tsv(FACTORS)
    deck = read_tsv(DECK)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    source_by_id = {row["attachment_id"]: row for row in source}
    checks: dict[str, dict[str, object]] = {}

    def check(name: str, condition: bool, observed: object) -> None:
        checks[name] = {"pass": bool(condition), "observed": observed}

    expected_ids = {"G399-A01468", "G399-A02820", "G399-A03234", "G399-A03235"}
    check("source_count", len(source) == 4374, len(source))
    check("transition_count", len(transitions) == 3, len(transitions))
    check("resolution_count", len(resolutions) == 4, len(resolutions))
    check("resolution_identity", {row["attachment_id"] for row in resolutions} == expected_ids, sorted(row["attachment_id"] for row in resolutions))
    check("transition_partition", sum(int(row["attachment_count"]) for row in transitions) == 4, [row["attachment_count"] for row in transitions])
    check("f82_is_one_two_focus_transition", [row["attachment_count"] for row in transitions if row["physical_page"] == "f82r"] == ["2"], [row["attachment_count"] for row in transitions if row["physical_page"] == "f82r"])
    check("all_scope_green", all(row["scope_result"] == "GREEN_EXISTING_TWO_STAGE_PARSE" for row in resolutions), Counter(row["scope_result"] for row in resolutions))
    check("one_semantic_caution", Counter(row["semantic_result"] for row in resolutions) == Counter({"UNCHANGED_CORE_VALUE": 3, "AMBER_KEEP_EE_INSIDE_OT_PACKET": 1}), Counter(row["semantic_result"] for row in resolutions))
    check("all_target_r", all(row["target_action"] == "R" and row["target_action_atom_ordinal"] == "1" for row in resolutions), [(row["target_action"], row["target_action_atom_ordinal"]) for row in resolutions])
    check("all_one_card", all(row["card_distance"] == "1" for row in resolutions), [row["card_distance"] for row in resolutions])
    check("no_owner_cross", all(row["owner_boundary_crossed"] == "NO" for row in resolutions), [row["owner_boundary_crossed"] for row in resolutions])
    check("target_recipe_starts_r", all(row["target_recipe"].split("+")[0] == "R" for row in resolutions), [row["target_recipe"] for row in resolutions])
    check("source_rows_agree", all(source_by_id[row["attachment_id"]]["chosen_action"] == "R" for row in resolutions), len(resolutions))
    check("three_distinct_statements", len({row["statement_id"] for row in transitions}) == 3, [row["statement_id"] for row in transitions])
    check("no_locus_crossing", all(row["physical_locus_crossing"] == "NO" for row in transitions), [row["physical_locus_crossing"] for row in transitions])
    check("parent_count", len(parents) == 13, len(parents))
    check("outside_parents_nonbio", all(row["register"] != "BIOLOGICAL" for row in parents if row["evidence_role"] == "OUTSIDE_REGISTER_PARENT"), Counter(row["register"] for row in parents if row["evidence_role"] == "OUTSIDE_REGISTER_PARENT"))
    check("parent_register_coverage", {row["register"] for row in parents if row["evidence_role"] == "OUTSIDE_REGISTER_PARENT"} == {"HERBAL", "CELESTIAL", "PHARMA"}, sorted({row["register"] for row in parents if row["evidence_role"] == "OUTSIDE_REGISTER_PARENT"}))
    check("same_register_control", [row["attachment_id"] for row in parents if row["evidence_role"] == "SAME_REGISTER_PACKET_CONTROL"] == ["G399-A02584"], [row["attachment_id"] for row in parents if row["evidence_role"] == "SAME_REGISTER_PACKET_CONTROL"])
    check("factor_count", len(factors) == 5, len(factors))
    factor_by_name = {row["factor"]: row for row in factors}
    check("forward_count", factor_by_name["BOUNDED_NEXT_CARD_ACTION"]["occurrences"] == "127", factor_by_name["BOUNDED_NEXT_CARD_ACTION"]["occurrences"])
    check("r_head_count", factor_by_name["R_POSITIONAL_HEAD"]["occurrences"] == "60", factor_by_name["R_POSITIONAL_HEAD"]["occurrences"])
    check("r_head_all_registers", factor_by_name["R_POSITIONAL_HEAD"]["registers"] == "BIOLOGICAL|CELESTIAL|HERBAL|PHARMA", factor_by_name["R_POSITIONAL_HEAD"]["registers"])
    check("r_head_multiple_scope_classes", len(factor_by_name["R_POSITIONAL_HEAD"]["attachment_classes"].split("|")) == 5, factor_by_name["R_POSITIONAL_HEAD"]["attachment_classes"])
    check("forward_multiple_heads", len(factor_by_name["BOUNDED_NEXT_CARD_ACTION"]["chosen_actions"].split("|")) == 9, factor_by_name["BOUNDED_NEXT_CARD_ACTION"]["chosen_actions"])
    check("forward_to_r_five_attachments", factor_by_name["FORWARD_THEN_R_HEAD"]["occurrences"] == "5", factor_by_name["FORWARD_THEN_R_HEAD"]["occurrences"])
    check("deck_count", len(deck) == 14, len(deck))
    check("deck_forward_addition", [row["gdt401_addition"] for row in deck if row["trigger"] == "HEADLESS_PACKAGE_NEXT_CARD"] == ["KNOWN_FORWARD_TO_R_IS_GREEN_WHEN_R_IS_FIRST_VISIBLE_HEAD"], [row["gdt401_addition"] for row in deck if row["trigger"] == "HEADLESS_PACKAGE_NEXT_CARD"])
    check("result_status", result["status"] == "AMBER_SCOPE_CLOSED__ONE_SEMANTIC_CAUTION_RETAINED", result["status"])
    check("no_new_scope_family", result["new_coarse_scope_family_count"] == 0, result["new_coarse_scope_family_count"])
    check("sealed_pages_absent", not any(row["physical_page"].startswith("f84") for row in transitions + parents), sorted({row["physical_page"] for row in transitions + parents if row["physical_page"].startswith("f84")}))
    check("result_hashes", all(sha256(OUT / name) == digest for name, digest in result["output_hashes"].items()), len(result["output_hashes"]))

    tracked = [TRANSITIONS, RESOLUTIONS, PARENTS, FACTORS, DECK, RESULT, HERE / "REPORT.md", HERE / "MANUAL_THREE_TRANSITIONS.md", HERE / "NEXT_FOUR_PAGE_ERROR_DECK_V2.md"]
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
