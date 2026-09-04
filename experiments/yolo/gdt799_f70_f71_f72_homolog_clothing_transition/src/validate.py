#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt799_f70_f71_f72_homolog_clothing_transition"
SRC = BASE / "src"
ART = BASE / "artifacts"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
ACQUISITION = ART / "GDT799_18_BLIND_VISUAL_ACQUISITION.tsv"
TRANSITIONS = ART / "GDT799_9_FIXED_HOMOLOG_TRANSITIONS.tsv"
RANKINGS = ART / "GDT799_400_CLOTHING_TRANSFORM_RANKINGS.tsv"
TESTS = ART / "GDT799_EXACT_TESTS.tsv"
CANDIDATES = ART / "GDT799_CANDIDATE_ADJUDICATION.tsv"
EDGE_AUDIT = ART / "GDT799_GDT388_EDGE_PACKET_AUDIT.json"
REPORT = BASE / "REPORT.md"

COVERED = "TORSO_COVERED"
UNCOVERED = "TORSO_UNCOVERED"
UNCERTAIN = "UNCERTAIN"
DECISIVE = {COVERED, UNCOVERED}
TARGETS = (6, 7, 8, 9, 10, 11, 12, 13, 15)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_indices(name: str) -> tuple[int, ...]:
    orientation = 1 if name[0] == "R" else -1
    shift = int(name[1:])
    return tuple((orientation * coordinate + shift) % 10 for coordinate in range(10))


def pair_score(left: Sequence[str | None], right: Sequence[str | None]) -> tuple[int, int]:
    pairs = [(a, b) for a, b in zip(left, right, strict=True) if a in DECISIVE and b in DECISIVE]
    return sum(a == b for a, b in pairs), len(pairs)


def score_three(
    f70: Sequence[str | None],
    f71: Sequence[str | None],
    f72: Sequence[str | None],
    name71: str,
    name72: str,
) -> tuple[int, int, int, int, int, int, int, int, float]:
    b = [f71[index] for index in transform_indices(name71)]
    c = [f72[index] for index in transform_indices(name72)]
    m01, n01 = pair_score(f70, b)
    m02, n02 = pair_score(f70, c)
    m12, n12 = pair_score(b, c)
    matches, comparisons = m01 + m02 + m12, n01 + n02 + n12
    return m01, n01, m02, n02, m12, n12, matches, comparisons, matches / comparisons


def main() -> int:
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        assert condition, name
        checks.append(name)

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    clone = dict(result)
    content_hash = clone.pop("content_hash")
    check("result_content_hash", content_hash == hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
    for category in ("inputs", "outputs", "implementation"):
        for path, digest in result[category].items():
            check(f"{category}_hash:{path}", sha(ROOT / path) == digest)

    source_lock = read_tsv(SRC / "SOURCE_LOCK.tsv")
    key = read_tsv(SRC / "BLIND_CROP_KEY.tsv")
    r1 = read_tsv(SRC / "VISUAL_REVIEW_R1.tsv")
    r2 = read_tsv(SRC / "VISUAL_REVIEW_R2.tsv")
    adjudication = read_tsv(SRC / "SOURCE_AWARE_ADJUDICATION.tsv")
    f71_rows = read_tsv(SRC / "FROZEN_F71_F9_STATES.tsv")
    acquisition = read_tsv(ACQUISITION)
    transitions = read_tsv(TRANSITIONS)
    rankings = read_tsv(RANKINGS)
    tests = read_tsv(TESTS)
    candidates = read_tsv(CANDIDATES)

    check("three_source_lock_rows", len(source_lock) == 3)
    check("source_lock_selectors", {row["selector"] for row in source_lock} == {"f70v1", "f72r1"})
    check("source_lock_no_sealed", all("f84" not in "|".join(row.values()).lower() for row in source_lock))
    check("source_lock_hashes", all(len(row["sha256"]) == 64 for row in source_lock))
    check("derived_panel_bound", source_lock[2]["parent_source_id"] == "YALE_1006203_F72")
    check("eighteen_crop_keys", len(key) == 18 and len({row["blind_id"] for row in key}) == 18)
    check("crop_ids_closed", {row["blind_id"] for row in key} == {"X01", "X02", "X03", "X04", "X06", "X07", "X08", "X09", "X11", "X12", "X14", "X15", "X17", "X19", "X21", "X22", "X24", "X25"})
    check("nine_per_new_ring", Counter(row["selector"] for row in key) == Counter({"f70v1": 9, "f72r1": 9}))
    check("target_members_exact", all({int(row["a_member"]) for row in key if row["selector"] == selector} == set(TARGETS) for selector in ("f70v1", "f72r1")))
    check("a14_excluded", all(row["a_member"] != "14" for row in key))
    check("crop_geometry", all(row["crop_width"] == "520" and row["crop_height"] == "520" for row in key))
    check("crop_hashes", all(len(row["crop_sha256"]) == 64 for row in key))
    check("crop_sources_closed", {row["crop_source_id"] for row in key} == {"YALE_1006201_F70", "DERIVED_1006203_F72R1_PANEL"})

    ids = {row["blind_id"] for row in key}
    check("review1_complete", len(r1) == 18 and {row["blind_id"] for row in r1} == ids)
    check("review2_complete", len(r2) == 18 and {row["blind_id"] for row in r2} == ids)
    check("review_roles_distinct", {row["reviewer_role"] for row in r1} == {"WORKSHOP_COPYIST"} and {row["reviewer_role"] for row in r2} == {"COSTUME_OBSERVER"})
    check("review_state_inventory", all(row["state"] in DECISIVE | {UNCERTAIN} for row in r1 + r2))
    check("review_confidence_inventory", all(row["confidence"] in {"HIGH", "MEDIUM", "LOW"} for row in r1 + r2))
    check("three_adjudications", {row["blind_id"] for row in adjudication} == {"X04", "X08", "X24"})
    check("adjudicator_disclosed", all(row["adjudicator_disclosure"] == "FULL_PAGE_AND_CROP_KEY_PREVIOUSLY_SEEN" for row in adjudication))

    by_key = {row["blind_id"]: row for row in key}
    by_r1 = {row["blind_id"]: row for row in r1}
    by_r2 = {row["blind_id"]: row for row in r2}
    by_adj = {row["blind_id"]: row for row in adjudication}
    rebuilt: dict[str, tuple[str, str]] = {}
    exact = 0
    opposite = 0
    for blind_id in sorted(ids):
        s1, s2 = by_r1[blind_id]["state"], by_r2[blind_id]["state"]
        if s1 == s2:
            state, agreement = s1, "BLIND_EXACT_AGREEMENT"
            exact += 1
        elif UNCERTAIN in {s1, s2}:
            state, agreement = next(iter({s1, s2} & DECISIVE)), "ONE_DECISIVE_PLUS_ONE_UNCERTAIN"
        else:
            opposite += 1
            state, agreement = by_adj[blind_id]["adjudicated_state"], "OPPOSITE_DECISIVE__SOURCE_AWARE_ADJUDICATED"
        rebuilt[blind_id] = (state, agreement)
    check("fifteen_exact_agreements", exact == 15)
    check("two_opposite_decisive", opposite == 2)
    check("acquisition_18", len(acquisition) == 18 and {row["blind_id"] for row in acquisition} == ids)
    check("acquisition_consensus_rebuilt", all((row["consensus_state"], row["agreement_class"]) == rebuilt[row["blind_id"]] for row in acquisition))
    check("acquisition_key_join", all(all(row[field] == by_key[row["blind_id"]][field] for field in by_key[row["blind_id"]]) for row in acquisition))
    counts = {
        selector: Counter(row["consensus_state"] for row in acquisition if row["selector"] == selector)
        for selector in ("f70v1", "f72r1")
    }
    check("f70_counts", counts["f70v1"] == Counter({UNCOVERED: 6, COVERED: 3}))
    check("f72_counts", counts["f72r1"] == Counter({UNCOVERED: 9}))
    check("only_f70_mobile", counts["f70v1"][COVERED] >= 2 and counts["f70v1"][UNCOVERED] >= 2 and counts["f72r1"][COVERED] < 2)

    check("ten_f71_rows", len(f71_rows) == 10 and {int(row["a_member"]) for row in f71_rows} == set(range(6, 16)))
    check("f71_f9_counts", Counter(row["state"] for row in f71_rows) == Counter({COVERED: 7, UNCOVERED: 2, UNCERTAIN: 1}))
    check("f71_f9_grove_order", [row["grove_ordinal"] for row in f71_rows] == ["1", "10", "9", "8", "7", "6", "5", "4", "3", "2"])
    check("nine_transition_rows", len(transitions) == 9 and {int(row["a_member"]) for row in transitions} == set(TARGETS))
    acquisition_by_selector_member = {(row["selector"], int(row["a_member"])): row["consensus_state"] for row in acquisition}
    f71_by_member = {int(row["a_member"]): row["state"] for row in f71_rows}
    check("transition_states_rebuilt", all(row["f70_state"] == acquisition_by_selector_member[("f70v1", int(row["a_member"]))] and row["f72_state"] == acquisition_by_selector_member[("f72r1", int(row["a_member"]))] and row["f71_f9_state"] == f71_by_member[int(row["a_member"])] for row in transitions))
    a09 = next(row for row in transitions if row["a_member"] == "9")
    check("a09_exact_family", a09["f70_boundary_family"] == a09["f72_boundary_family"] == "AQABAB")
    check("a09_surfaces", a09["f70_surface"] == "okalal" and a09["f72_surface"] == "okalam")
    check("a09_state_contrast", a09["f70_state"] == COVERED and a09["f72_state"] == UNCOVERED)

    f70: list[str | None] = [None] * 10
    f72: list[str | None] = [None] * 10
    for row in acquisition:
        (f70 if row["selector"] == "f70v1" else f72)[int(row["a_member"]) - 6] = row["consensus_state"]
    f71: list[str | None] = [None] * 10
    for row in f71_rows:
        f71[int(row["f71_native_a_member"]) - 6] = row["state"]
    check("missing_a14_preserved", f70[8] is None and f72[8] is None)
    check("f71_native_complete", all(state is not None for state in f71))
    expected_scores: dict[tuple[str, str], tuple[int, int, int, int, int, int, int, int, float]] = {}
    names = [("R" if orientation == 1 else "F") + str(shift) for orientation in (1, -1) for shift in range(10)]
    for name71 in names:
        for name72 in names:
            expected_scores[(name71, name72)] = score_three(f70, f71, f72, name71, name72)
    check("four_hundred_rankings", len(rankings) == 400 and len({(row["transform_f71"], row["transform_f72"]) for row in rankings}) == 400)
    for row in rankings:
        expected = expected_scores[(row["transform_f71"], row["transform_f72"])]
        observed = (
            int(row["f70_f71_matches"]), int(row["f70_f71_comparisons"]),
            int(row["f70_f72_matches"]), int(row["f70_f72_comparisons"]),
            int(row["f71_f72_matches"]), int(row["f71_f72_comparisons"]),
            int(row["matches"]), int(row["comparisons"]), float(row["accuracy"]),
        )
        check(f"transform_score:{row['transform_f71']}:{row['transform_f72']}", observed[:8] == expected[:8] and abs(observed[8] - expected[8]) < 5e-7)
        rank = 1 + sum(other[8] > expected[8] + 1e-12 for other in expected_scores.values())
        ties = sum(abs(other[8] - expected[8]) <= 1e-12 for other in expected_scores.values())
        check(f"transform_rank:{row['transform_f71']}:{row['transform_f72']}", int(row["accuracy_rank"]) == rank and int(row["accuracy_tie_count"]) == ties)
    fixed = next(row for row in rankings if row["is_fixed_f9_r0"] == "1")
    identity = next(row for row in rankings if row["is_identity_r0_r0"] == "1")
    check("fixed_unique", sum(row["is_fixed_f9_r0"] == "1" for row in rankings) == 1 and (fixed["transform_f71"], fixed["transform_f72"]) == ("F9", "R0"))
    check("fixed_readout", fixed["matches"] == "11" and fixed["comparisons"] == "25" and fixed["accuracy"] == "0.440000" and fixed["accuracy_rank"] == "171" and fixed["accuracy_tie_count"] == "28")
    check("identity_readout", identity["matches"] == "11" and identity["comparisons"] == "27" and identity["accuracy"] == "0.407407" and identity["accuracy_rank"] == "257")

    f71_target = [f71_by_member[member] for member in TARGETS]
    null_matches = []
    for selected in itertools.combinations(range(9), 3):
        candidate = [UNCOVERED] * 9
        for index in selected:
            candidate[index] = COVERED
        null_matches.append(pair_score(candidate, f71_target)[0])
    check("margin_worlds", len(null_matches) == 84)
    check("margin_tail", sum(value >= 3 for value in null_matches) == 65)

    test_by_id = {row["test_id"]: row for row in tests}
    check("twelve_tests", len(tests) == 12 and len(test_by_id) == 12)
    check("mobility_test_fails", test_by_id["F72_WITHIN_RING_MOBILITY"]["result"] == "FAIL")
    check("fixed_not_eligible", test_by_id["FIXED_400_TRANSFORM_RANK"]["result"] == "NOT_ELIGIBLE")
    check("margin_test", test_by_id["F70_F71_MARGIN_EXACT"]["observed"] == "matches=3|p=0.773810|worlds=84")
    check("four_candidates", len(candidates) == 4 and len({row["candidate_id"] for row in candidates}) == 4)
    check("page_facies_selected", next(row for row in candidates if row["candidate_id"] == "PAGE_RING_UPPER_TORSO_FACIES")["decision"] == "SELECT_STRUCTURAL_DESCRIPTION")
    check("fixed_relation_not_selected", next(row for row in candidates if row["candidate_id"] == "FIXED_F9_R0_POSITIONAL_CLOTHING_GRAMMAR")["decision"] == "NOT_SELECTED__F72_NONMOBILE")
    check("all_candidate_exports_zero", all(row["component_export_credit"] == "ZERO" and row["confirmed_lexeme"] == "NO" for row in candidates))

    edge = json.loads(EDGE_AUDIT.read_text(encoding="utf-8"))
    edge_live = json.loads(subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str((SRC / "GDT388_EMPTY_EDGE_PACKET.tsv").relative_to(ROOT))], cwd=ROOT, text=True, capture_output=True, check=True).stdout)
    check("edge_audit_replay", edge == edge_live)
    check("edge_not_score_ready", edge["status"] == "VALID_ACQUISITION_NOT_SCORE_READY" and edge["eligible_edges"] == 0 and edge["score_ready"] is False)
    check("result_status", result["status"] == "PARTIAL__18_NEW_STATES__F70_3C6U__F72_0C9U_PAGE_RING_FACIES_ONLY__FIXED_RELATION_NOT_MOBILE__ZERO_LEXEMES")
    check("result_decision", result["decision"] == "PAGE_RING_FACIES_ONLY__FIXED_POSITION_RELATION_NOT_REUSABLE")
    check("result_fixed", result["fixed_alignment"] == {"f70": "R0", "f71": "F9", "f72": "R0", "rank_of_400": 171, "tie_count": 28, "matches": 11, "comparisons": 25, "accuracy": 0.44, "eligible_for_relation_claim": False})
    check("zero_semantic_exports", result["semantic_exports"] == result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == 0)
    check("sealed_absent", result["f84_or_f84r_accessed"] is False)
    report = REPORT.read_text(encoding="utf-8")
    check("report_core_counts", "**15/18**" in report and "| f70v1 outer | 3 | 6 | 0 | yes |" in report and "| f72r1 outer | 0 | 9 | 0 | no |" in report)
    check("report_counterexample", "`okalal`" in report and "`okalam`" in report and "`AQABAB`" in report)

    replay_paths = [ACQUISITION, TRANSITIONS, RANKINGS, TESTS, CANDIDATES, EDGE_AUDIT, REPORT, RESULT]
    before = {str(path): sha(path) for path in replay_paths}
    command = ["python3", str(SRC / "run.py")]
    first_run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    after_first = {str(path): sha(path) for path in replay_paths}
    second_run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    after_second = {str(path): sha(path) for path in replay_paths}
    check("builder_replay_one", before == after_first)
    check("builder_replay_two", after_first == after_second)
    check("builder_status_output", result["status"] in first_run.stdout and result["status"] in second_run.stdout)

    validation: dict[str, Any] = {
        "schema": "GDT799_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "result_hash": sha(RESULT),
        "validator_hash": sha(Path(__file__)),
        "builder_replays": 2,
        "f84_or_f84r_accessed": False,
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(checks)}/{len(checks)}; two byte-identical builder replays")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
