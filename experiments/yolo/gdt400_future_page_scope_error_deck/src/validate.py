#!/usr/bin/env python3
"""Validate the GDT400 future-page hierarchy and error deck."""

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
REPLAY = OUT / "gdt400_4374_hierarchical_replay.tsv"
SIGNATURES = OUT / "gdt400_signature_support.tsv"
FORWARD = OUT / "gdt400_127_forward_cases.tsv"
OWNER = OUT / "gdt400_126_owner_cases.tsv"
PAGES = OUT / "gdt400_22_page_admission_rehearsal.tsv"
DECK = OUT / "gdt400_error_deck.tsv"
RESULT = OUT / "gdt400_result.json"
VALIDATION = OUT / "gdt400_validation.json"
SHEET = HERE / "NEXT_FOUR_PAGE_ERROR_DECK.md"
REPORT = HERE / "REPORT.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source = read_tsv(SOURCE)
    replay = read_tsv(REPLAY)
    signatures = read_tsv(SIGNATURES)
    forward = read_tsv(FORWARD)
    owner = read_tsv(OWNER)
    pages = read_tsv(PAGES)
    deck = read_tsv(DECK)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: dict[str, dict[str, object]] = {}

    def check(name: str, condition: bool, observed: object) -> None:
        checks[name] = {"pass": bool(condition), "observed": observed}

    check("replay_count", len(replay) == 4374, len(replay))
    check("signature_count", len(signatures) == 544, len(signatures))
    check("forward_count", len(forward) == 127, len(forward))
    check("owner_count", len(owner) == 126, len(owner))
    check("page_count", len(pages) == 22, len(pages))
    check("deck_count", len(deck) == 14, len(deck))
    check("source_attachment_alignment", [row["attachment_id"] for row in replay] == [row["attachment_id"] for row in source], len(replay))
    check("unique_replay_ids", len({row["replay_id"] for row in replay}) == 4374, len({row["replay_id"] for row in replay}))
    check("no_page_private_attachment", all(row["outside_page_support_level"] != "NONE" for row in replay), Counter(row["outside_page_support_level"] for row in replay))
    check("no_register_private_attachment", all(row["outside_register_support_level"] != "NONE" for row in replay), Counter(row["outside_register_support_level"] for row in replay))
    composed = [row for row in replay if row["outside_register_support_level"] == "COMPOSED_RULE_COMPONENTS"]
    check("four_composed_register_fallbacks", len(composed) == 4, [row["attachment_id"] for row in composed])
    check("composed_cases_biological", all(row["register"] == "BIOLOGICAL" for row in composed), Counter(row["register"] for row in composed))
    check("composed_cases_disclosed_as_support", all("R_POSITIONAL_MARKING:" in row["outside_register_support"] for row in composed), [row["outside_register_support"] for row in composed])

    level_counts = Counter(row["signature_level"] for row in signatures)
    check("signature_level_counts", level_counts == Counter({"EXACT_TYPED_HEAD": 372, "TYPED_MICRO": 108, "UNTYPED_MICRO": 40, "COARSE_RULE": 15, "RULE_COMPONENT": 9}), dict(level_counts))
    check("nine_rule_components_cross_page", all(row["page_private"] == "NO" for row in signatures if row["signature_level"] == "RULE_COMPONENT"), sum(row["signature_level"] == "RULE_COMPONENT" for row in signatures))
    check("nine_rule_components_cross_register", all(row["register_private"] == "NO" for row in signatures if row["signature_level"] == "RULE_COMPONENT"), sum(row["signature_level"] == "RULE_COMPONENT" for row in signatures))

    source_by_attachment = {row["attachment_id"]: row for row in source}
    forward_ok = True
    for row in forward:
        source_row = source_by_attachment[row["attachment_id"]]
        next_atoms = row["next_recipe"].split("+")
        position = int(row["chosen_action_atom_ordinal"])
        forward_ok &= (
            source_row["chosen_attachment_class"] == "BOUNDED_NEXT_CARD_ACTION"
            and row["same_statement"] == "YES"
            and row["lookahead_cards"] == "1"
            and 1 <= position <= len(next_atoms)
            and next_atoms[position - 1] == row["chosen_action"]
        )
    check("all_forward_heads_visible_next_card", forward_ok, Counter(row["forward_reason"] for row in forward))
    owner_ids = {row["attachment_id"] for row in owner}
    expected_owner_ids = {row["attachment_id"] for row in source if row["chosen_attachment_class"] == "OWNER_ONLY"}
    check("owner_identity_complete", owner_ids == expected_owner_ids, len(owner_ids))
    check("owner_reasons_complete", all(row["owner_reason"] != "" and row["result"] == "VISIBLE_OWNER_FALLBACK" for row in owner), Counter(row["owner_reason"] for row in owner))

    page_results = Counter(row["future_admission_rehearsal"] for row in pages)
    check("all_running_pages_pass", page_results == Counter({"PASS_HIERARCHICAL_DECK": 20, "ADDRESS_ONLY": 2}), dict(page_results))
    check("page_event_partition", sum(int(row["running_event_count"]) for row in pages) == 3888, sum(int(row["running_event_count"]) for row in pages))
    check("page_focus_partition", sum(int(row["focus_attachment_count"]) for row in pages) == 4374, sum(int(row["focus_attachment_count"]) for row in pages))

    priorities = [int(row["priority"]) for row in deck]
    check("deck_priorities", priorities == list(range(1, 15)), priorities)
    check("deck_color_partition", Counter(row["color"] for row in deck) == Counter({"RED": 7, "GREEN": 4, "AMBER": 3}), Counter(row["color"] for row in deck))
    required_red = {
        "SAME_SURFACE_DIFFERENT_RECIPE", "LOOKAHEAD_OVER_ONE_CARD",
        "OWNER_OR_STATEMENT_BOUNDARY_CROSSING", "KNOWN_CORE_REQUIRES_NEW_VALUE",
        "TENTH_COARSE_SCOPE_FAMILY", "ACTION_LIKE_LABEL_OPENS_PROSE_STACK",
        "INVISIBLE_ATOM_FROM_EDIT_NEIGHBOR",
    }
    check("all_red_failures_present", {row["trigger"] for row in deck if row["color"] == "RED"} == required_red, sorted(row["trigger"] for row in deck if row["color"] == "RED"))

    check("result_private_count_zero", result["private_attachment_count"] == 0, result["private_attachment_count"])
    check("result_counts", result["forward_case_count"] == 127 and result["owner_case_count"] == 126 and result["deck_rule_count"] == 14, {key: result[key] for key in ["forward_case_count", "owner_case_count", "deck_rule_count"]})
    check("sealed_pages_absent", not any(row["physical_page"].startswith("f84") for row in replay), sorted({row["physical_page"] for row in replay if row["physical_page"].startswith("f84")}))
    check("result_hashes", all(sha256(OUT / name) == digest for name, digest in result["output_hashes"].items()), len(result["output_hashes"]))

    tracked = [REPLAY, SIGNATURES, FORWARD, OWNER, PAGES, DECK, RESULT, SHEET, REPORT]
    before = {path.name: sha256(path) for path in tracked}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False)
    after = {path.name: sha256(path) for path in tracked}
    check("deterministic_rebuild", completed.returncode == 0 and before == after, {"returncode": completed.returncode, "hashes_equal": before == after})

    failures = [name for name, value in checks.items() if not value["pass"]]
    payload = {
        "status": "PASS" if not failures else "FAIL", "check_count": len(checks),
        "failed_checks": failures, "checks": checks, "validated_hashes": after,
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
