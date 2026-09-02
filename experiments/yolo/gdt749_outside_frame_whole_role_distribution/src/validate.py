#!/usr/bin/env python3
"""Invariant, edge-gate and byte-replay validation for GDT749."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt749_outside_frame_whole_role_distribution")
EXP = ROOT / BASE
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "PARTIAL__16_RECURRENT_PLUS_QOCHEY__1311_READER_EXACT_OUTSIDE_OCCURRENCES__"
    "CALIBRATION_23_TP_42_FP_60_FN__4_LOCAL_COMPATIBILITY__1_RIVAL_LEADS__"
    "QOCHEY_THREE_OUTSIDE_POSITIONS__ZERO_LITERAL_IDENTITIES__"
    "ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "TARGET_17_FIXED_DECK.tsv",
    "TARGET_OCCURRENCE_AUDIT.tsv",
    "REFERENCE_DISTRIBUTION_SCORES.tsv",
    "KNOWN_46_LEAVE_SELF_CALIBRATION.tsv",
    "TARGET_OUTSIDE_ROLE_CENSUS.tsv",
    "QOCHEY_HYPOTHESIS_SPLIT.tsv",
    "GDT749_OUTSIDE_FRAME_READER.md",
    "GDT749_GDT388_OUTSIDE_EDGE_PACKET.tsv",
    "GDT749_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)
STATUS_COUNTS = Counter({
    "K1_OPEN_OR_BASELINE_LIKE": 3,
    "K1_OUTSIDE_RIVAL_LEAD_NOT_REJECTION": 1,
    "K1_QOCHEY_END_RIVAL_LEAD": 1,
    "K1_SPARSE_COLD_DRY_RIVAL": 1,
    "K1_SPARSE_OUTSIDE_OPEN_WITH_COLD_END_RIVAL": 1,
    "K1_WEAK_LOCAL_COMPATIBILITY": 6,
    "K2_LOCAL_AXIS_COMPATIBILITY_LEAD": 4,
})


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def values(text: str) -> set[str]:
    return set() if text in {"", "NONE"} else set(text.split("|"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    art = args.artifacts_dir.resolve()
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT749", "manifest id")
    check(manifest["slug"] == "outside_frame_whole_role_distribution", "manifest slug")
    check(manifest["status"] == STATUS, "manifest status")
    check(
        manifest["dependencies"]
        == ["GDT388", "GDT734", "GDT739", "GDT746", "GDT748"],
        "manifest dependencies",
    )
    check(
        manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
        "sealed data",
    )
    check(bool(manifest["question"]), "manifest question")
    check(bool(manifest["claim_ceiling"]), "manifest ceiling")
    check(
        manifest["validation"]
        == {"artifact": str(VALIDATION_REL), "status": "PASS"},
        "validation contract",
    )
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash {binding['path']}")

    targets = read_tsv(art / GENERATED[0])
    audit = read_tsv(art / GENERATED[1])
    scores = read_tsv(art / GENERATED[2])
    calibration = read_tsv(art / GENERATED[3])
    census = read_tsv(art / GENERATED[4])
    qochey = read_tsv(art / GENERATED[5])

    check(len(targets) == 17, "17 fixed targets")
    check(len(audit) == 1684, "1684 target occurrences")
    check(len(scores) == 781, "781 reference comparisons")
    check(len(calibration) == 46, "46 leave-self calibration rows")
    check(len(census) == 17, "17 target census rows")
    check(len(qochey) == 3, "three qochey hypotheses")
    check(len({row["target_surface"] for row in targets}) == 17, "unique target forms")
    check(len({row["gdt749_occurrence_id"] for row in audit}) == 1684, "unique occurrence ids")
    check(len({row["gdt749_score_id"] for row in scores}) == 781, "unique score ids")
    check(len({row["known_surface"] for row in calibration}) == 46, "unique calibration forms")

    target_map = {row["target_surface"]: row for row in targets}
    check("qochey" in target_map and target_map["qochey"]["target_class"] == "GDT748_CONFLICTED_SPLIT_DIAGNOSTIC", "qochey diagnostic")
    check(sum(row["target_class"] == "GDT748_RECURRENT_S2_S3_ROLE" for row in targets) == 16, "sixteen recurrent targets")
    check(target_map["okechy"]["prior_role_axes"] == "HOT", "okechy prior hot")
    check(target_map["qochey"]["prior_role_axes"] == "DRY|MIDDLE_STAGE", "qochey strongest prior")
    check(target_map["qochey"]["prior_rival_axes"] == "HOT|END_STAGE", "qochey rival deck")

    discovery_counts = Counter(
        row["target_surface"] for row in audit
        if row["gdt748_discovery_position"] == "1"
    )
    expected_discovery = {
        row["target_surface"]: int(row["discovery_position_evidence_units"])
        for row in targets
    }
    check(dict(discovery_counts) == expected_discovery, "per-target discovery exclusions")
    check(sum(discovery_counts.values()) == 57, "57 discovery positions")
    outside = [row for row in audit if row["gdt748_discovery_position"] == "0"]
    exact = [row for row in outside if row["reader_exact"] == "1"]
    check(len(outside) == 1627, "1627 outside occurrences")
    check(len(exact) == 1311, "1311 exact outside occurrences")
    check(len({row["page"] for row in exact}) == 154, "154 outside pages")
    for row in audit:
        occurrence = row["gdt749_occurrence_id"]
        check(not row["page"].startswith("f84"), f"sealed occurrence {occurrence}")
        check(row["written_line_eva"].split()[int(row["token_ordinal"]) - 1] == row["target_surface"], f"line coordinate {occurrence}")
        check(row["literal_identity"] == "OPEN", f"occurrence literal {occurrence}")
        check(row["confirmed_lexeme"] == "0", f"occurrence lexeme {occurrence}")
        check(row["component_export_credit"] == "0", f"occurrence component {occurrence}")

    score_counts = Counter(row["target_surface"] for row in scores)
    check(score_counts["cheey"] == 45, "cheey self reference removed")
    check(all(count == 46 for surface, count in score_counts.items() if surface != "cheey"), "other targets have 46 references")
    check(sum(row["top_five_reference"] == "1" for row in scores) == 85, "85 top-five slots")
    for row in scores:
        score_id = row["gdt749_score_id"]
        check(row["target_surface"] != row["reference_surface"], f"no score self match {score_id}")
        check(row["literal_identity_credit"] == "0", f"score literal {score_id}")
        check(row["confirmed_lexeme"] == "0", f"score lexeme {score_id}")
        check(row["component_export_credit"] == "0", f"score component {score_id}")

    tp = sum(len(values(row["recovered_true_axes"])) for row in calibration)
    fp = sum(len(values(row["false_predicted_axes"])) for row in calibration)
    fn = sum(len(values(row["missed_true_axes"])) for row in calibration)
    check((tp, fp, fn) == (23, 42, 60), "known calibration 23 42 60")
    check(sum(int(row["reader_exact_occurrences"]) for row in calibration) == 1158, "1158 reference exact occurrences")
    check(sum(int(row["local_true_only_positions"]) + int(row["local_both_positions"]) for row in calibration) == 187, "187 local true hits")
    check(sum(int(row["local_rival_only_positions"]) + int(row["local_both_positions"]) for row in calibration) == 109, "109 local rival hits")

    check(Counter(row["outside_role_status"] for row in census) == STATUS_COUNTS, "calibrated status counts")
    census_map = {row["target_surface"]: row for row in census}
    expected_k2 = {"chdy", "cheey", "okeey", "qokedy"}
    check({surface for surface, row in census_map.items() if row["outside_role_status"] == "K2_LOCAL_AXIS_COMPATIBILITY_LEAD"} == expected_k2, "four K2 forms")
    check(census_map["cheky"]["outside_role_status"] == "K1_OUTSIDE_RIVAL_LEAD_NOT_REJECTION", "cheky rival")
    check(census_map["cheky"]["outside_prior_only_positions"] == "1" and census_map["cheky"]["outside_rival_only_positions"] == "7", "cheky outside polarity")
    check(census_map["kchdy"]["outside_role_status"] == "K1_SPARSE_COLD_DRY_RIVAL", "kchdy sparse rival")
    check(census_map["okechy"]["outside_occurrences_reader_exact"] == "2", "okechy two outside")
    check(census_map["qochey"]["outside_occurrences_reader_exact"] == "3", "qochey three outside")
    check(census_map["qochey"]["outside_role_status"] == "K1_QOCHEY_END_RIVAL_LEAD", "qochey end lead")
    for row in census:
        surface = row["target_surface"]
        check(row["literal_identity"] == "OPEN", f"census literal {surface}")
        check(row["confirmed_lexeme"] == "0", f"census lexeme {surface}")
        check(row["component_export_credit"] == "0", f"census component {surface}")
        check(row["unseen_form_export"] == "0", f"census unseen {surface}")
        check(row["known_calibration_precision"] == "0.353846", f"census precision {surface}")
        check(row["known_calibration_recall"] == "0.277108", f"census recall {surface}")

    qmap = {row["hypothesis_axes"]: row for row in qochey}
    check(set(qmap) == {"DRY|MIDDLE_STAGE", "END_STAGE", "HOT|END_STAGE"}, "qochey hypotheses")
    check(qmap["DRY|MIDDLE_STAGE"]["best_matching_reference_rank"] == "5", "qochey dry middle rank")
    check(qmap["DRY|MIDDLE_STAGE"]["outside_positions_with_any_hypothesis_axis_immediate"] == "0", "qochey dry middle no immediate")
    check(qmap["END_STAGE"]["best_matching_reference_rank"] == "1", "qochey end rank")
    check(qmap["END_STAGE"]["top5_references_with_all_axes"] == "4", "qochey four end top refs")
    check(qmap["HOT|END_STAGE"]["best_matching_reference_rank"] == "4", "qochey hot end rank")

    packet_path = art / "GDT749_GDT388_OUTSIDE_EDGE_PACKET.tsv"
    packet = read_tsv(packet_path)
    intake = json.loads((art / "GDT749_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8"))
    check(len(packet) == 1, "one relation row")
    check(packet[0]["page"] == packet[0]["target_locus"].split(".")[0].split("@")[0], "edge same page")
    check(intake["status"] == "INVALID_PACKET" and not intake["score_ready"], "edge invalid not ready")
    check(intake["errors"] == ["edge row 2: formal access is not sealed"], "edge sole formal error")
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT, check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    check(completed.returncode == 1, "edge checker expected return")
    check(json.loads(completed.stdout) == intake, "edge checker replay")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT749_RESULT_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"] == {
        "discovery_occurrences_excluded": 57,
        "fixed_reference_wholes": 46,
        "outside_occurrences_all_readings": 1627,
        "outside_occurrences_reader_exact": 1311,
        "outside_pages": 154,
        "qochey_split_diagnostic": 1,
        "recurrent_targets": 16,
        "reference_comparisons": 781,
        "target_occurrences_all": 1684,
    }, "result scope")
    check(result["outside_role_status_counts"] == dict(sorted(STATUS_COUNTS.items())), "result status counts")
    check(result["known_whole_leave_self_calibration"]["quality_stage_true_positive_labels"] == 23, "result calibration tp")
    check(result["known_whole_leave_self_calibration"]["quality_stage_false_positive_labels"] == 42, "result calibration fp")
    check(result["known_whole_leave_self_calibration"]["quality_stage_false_negative_labels"] == 60, "result calibration fn")

    for binding in manifest["outputs"]:
        if binding["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / binding["path"]
        check(path.is_file(), f"output exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"output hash {binding['path']}")

    with tempfile.TemporaryDirectory(prefix=".gdt749_replay_", dir=EXP) as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)],
            cwd=ROOT, check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay return")
        for name in GENERATED:
            check((replay / name).is_file(), f"replay exists {name}")
            check((replay / name).read_bytes() == (art / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT749_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": result["scope"],
        "known_calibration": result["known_whole_leave_self_calibration"],
        "outside_role_status_counts": dict(sorted(STATUS_COUNTS.items())),
        "claim_ceiling": result["claim_ceiling"],
    }
    if not args.no_write:
        (art / "VALIDATION.json").write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
