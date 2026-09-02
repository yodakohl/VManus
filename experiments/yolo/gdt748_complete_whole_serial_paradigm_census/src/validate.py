#!/usr/bin/env python3
"""Invariant audit and byte-identical replay for GDT748."""

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
BASE = Path("experiments/yolo/gdt748_complete_whole_serial_paradigm_census")
EXP = ROOT / BASE
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "PARTIAL__45136_WINDOWS__4080_ONE_OPEN__1406_PREDICTIVE_FRAMES__"
    "1125_POSITIONS__UNCONDITIONED_189_OF_429__FORM_BRIDGE_96_OF_126__"
    "MULTIBRIDGE_18_OF_20__237_FORM_BRIDGED_POSITIONS__122_SURFACES__"
    "16_RECURRENT_ROLE_LEADS__1_NEW_OPEN_WHOLE__13_WEAK_REINFORCED__"
    "2_RETIRED_LITERAL_REPLACED__QOCHEY_STRONGEST_FRAME_ONLY__"
    "ZERO_LEXEME_OR_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "ELIGIBLE_ONE_OPEN_FRAME_CENSUS.tsv",
    "PREDICTIVE_SERIAL_FRAME_CENSUS.tsv",
    "COLLAPSED_POSITION_EVIDENCE.tsv",
    "FORM_BRIDGED_POSITION_EVIDENCE.tsv",
    "SURFACE_PREDICTION_CENSUS.tsv",
    "HELD_12_SERIAL_AUDIT.tsv",
    "KNOWN_LEAVE_ONE_OUT_CALIBRATION.tsv",
    "FORM_BRIDGE_CALIBRATION_CENSUS.tsv",
    "GDT748_COMPLETE_WHOLE_SERIAL_READER.md",
    "GDT748_GDT388_SERIAL_EDGE_PACKET.tsv",
    "GDT748_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)
SURFACE_STATUS_COUNTS = Counter({
    "S0_MIXED_SERIAL_PREDICTIONS": 16,
    "S1_CONSENSUS_WITH_DIMENSION_CONFLICT": 7,
    "S1_SHORT_FORM_CONTROL_RIVAL": 3,
    "S1_SINGLE_WRITTEN_SERIAL_LEAD": 80,
    "S2_RECURRENT_SERIAL_CONSENSUS": 6,
    "S3_RECURRENT_CROSS_PAGE_SERIAL_CONSENSUS": 10,
})
ROLE_DECISION_COUNTS = Counter({
    "NEW_OPEN_WHOLE_ROLE_LEAD": 1,
    "NO_RECURRENT_ROLE_EXPORT": 106,
    "REINFORCE_OR_NARROW_WEAK_AXIS_CARD": 13,
    "REPLACE_RETIRED_LITERAL_WITH_AXIS_ROLE_LEAD": 2,
})
CALIBRATION_EXPECTED = {
    "UNCONDITIONED_ALL": (429, 189, 141, 106),
    "READER_EXACT_ALL": (245, 113, 87, 52),
    "NO_FORM_BRIDGE": (303, 93, 64, 76),
    "FORM_BRIDGE_ANY": (126, 96, 77, 30),
    "FORM_BRIDGE_READER_EXACT": (69, 55, 45, 12),
    "DIRECT_EDIT1_BRIDGE": (54, 43, 39, 14),
    "DIRECT_EDIT2_ONLY_BRIDGE": (72, 53, 38, 16),
    "MULTIPLE_EDIT2_BRIDGES": (20, 18, 16, 4),
}


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
    return set() if text in {"", "NONE", "OPEN", "NA"} else set(text.split("|"))


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
    check(manifest["experiment_id"] == "GDT748", "manifest id")
    check(manifest["slug"] == "complete_whole_serial_paradigm_census", "manifest slug")
    check(manifest["status"] == STATUS, "manifest status")
    check(
        manifest["dependencies"]
        == ["GDT388", "GDT734", "GDT739", "GDT743", "GDT745", "GDT747"],
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

    eligible = read_tsv(art / GENERATED[0])
    predictive = read_tsv(art / GENERATED[1])
    evidence = read_tsv(art / GENERATED[2])
    bridged = read_tsv(art / GENERATED[3])
    surfaces = read_tsv(art / GENERATED[4])
    held = read_tsv(art / GENERATED[5])
    calibration = read_tsv(art / GENERATED[6])
    calibration_census = read_tsv(art / GENERATED[7])

    check(len(eligible) == 3975, "3975 eligible frames")
    check(len(predictive) == 1406, "1406 predictive frames")
    check(len(evidence) == 1125, "1125 collapsed positions")
    check(len(bridged) == 237, "237 form-bridged positions")
    check(len(surfaces) == 122, "122 bridged surfaces")
    check(len(held) == 12, "12 held candidates")
    check(len(calibration) == 429, "429 calibration positions")
    check(len(calibration_census) == 8, "eight calibration classes")

    check(len({row["frame_id"] for row in eligible}) == 3975, "unique eligible ids")
    check(len({row["frame_id"] for row in predictive}) == 1406, "unique predictive ids")
    check(len({row["evidence_id"] for row in evidence}) == 1125, "unique evidence ids")
    check(
        len({(row["locus"], row["target_ordinal"]) for row in evidence}) == 1125,
        "unique evidence coordinates",
    )
    check(len({row["target_surface"] for row in surfaces}) == 122, "unique surfaces")
    check(len({row["calibration_id"] for row in calibration}) == 429, "unique calibration ids")

    predictive_ids = {row["frame_id"] for row in predictive}
    check(predictive_ids <= {row["frame_id"] for row in eligible}, "predictive subset")
    evidence_ids = {row["evidence_id"] for row in evidence}
    bridged_ids = {row["evidence_id"] for row in bridged}
    check(bridged_ids <= evidence_ids, "bridged evidence subset")
    for row in eligible:
        frame = row["frame_id"]
        check(row["known_card_count"] in {"2", "3"}, f"known count {frame}")
        check(int(row["distinct_known_surfaces"]) >= 2, f"distinct known {frame}")
        check(row["literal_identity"] == "OPEN", f"frame literal {frame}")
        check(row["confirmed_lexeme"] == "0", f"frame lexeme {frame}")
        check(row["component_export_credit"] == "0", f"frame component {frame}")
        check(not row["page"].startswith("f84"), f"sealed frame {frame}")
    for row in predictive:
        check(row["predicted_quality_stage_axes"] != "NONE", f"predictive axes {row['frame_id']}")
    for row in evidence:
        evidence_id = row["evidence_id"]
        check(int(row["overlapping_predictive_frames"]) >= 1, f"overlap count {evidence_id}")
        check(row["best_frame_id"] in predictive_ids, f"best frame join {evidence_id}")
        check(row["literal_identity"] == "OPEN", f"evidence literal {evidence_id}")
        check(row["confirmed_lexeme"] == "0", f"evidence lexeme {evidence_id}")
        check(row["component_export_credit"] == "0", f"evidence component {evidence_id}")
    for row in bridged:
        evidence_id = row["evidence_id"]
        check(int(row["minimum_whole_edit_distance"]) <= 2, f"bridge distance {evidence_id}")
        check(int(row["known_wholes_within_edit2"]) >= 1, f"bridge count {evidence_id}")
        check(int(row["whole_form_bridge_weight"]) in {1, 2, 3}, f"bridge weight {evidence_id}")

    check(Counter(row["serial_status"] for row in surfaces) == SURFACE_STATUS_COUNTS, "surface statuses")
    check(Counter(row["role_decision"] for row in surfaces) == ROLE_DECISION_COUNTS, "role decisions")
    surface_map = {row["target_surface"]: row for row in surfaces}
    recurrent = [row for row in surfaces if row["serial_status"].startswith(("S2_", "S3_"))]
    check(len(recurrent) == 16, "sixteen recurrent role leads")
    check(surface_map["okechy"]["serial_consensus_axes"] == "HOT", "okechy hot")
    check(surface_map["okechy"]["position_evidence_units"] == "2", "okechy two positions")
    check(surface_map["okechy"]["pages"] == "2", "okechy two pages")
    check(surface_map["okechy"]["role_decision"] == "NEW_OPEN_WHOLE_ROLE_LEAD", "okechy new lead")
    check(surface_map["qokedy"]["serial_consensus_axes"] == "END_STAGE", "qokedy end")
    check(surface_map["qokedy"]["position_evidence_units"] == "8", "qokedy eight")
    check(surface_map["okedy"]["serial_consensus_axes"] == "HOT", "okedy hot")
    check(surface_map["cheol"]["serial_consensus_axes"] == "DRY", "cheol dry")
    check(surface_map["olkar"]["role_decision"] == "REPLACE_RETIRED_LITERAL_WITH_AXIS_ROLE_LEAD", "olkar axis only")
    check(surface_map["lkeey"]["role_decision"] == "REPLACE_RETIRED_LITERAL_WITH_AXIS_ROLE_LEAD", "lkeey axis only")
    for row in surfaces:
        surface = row["target_surface"]
        check(row["literal_identity"] == "OPEN", f"surface literal {surface}")
        check(row["confirmed_lexeme"] == "0", f"surface lexeme {surface}")
        check(row["component_export_credit"] == "0", f"surface component {surface}")
        if row["serial_status"].startswith(("S2_", "S3_")):
            check(int(row["position_evidence_units"]) >= 2, f"recurrent positions {surface}")
            check(row["serial_consensus_axes"] != "NONE", f"recurrent axes {surface}")
        if len(surface) <= 2:
            check(row["serial_status"] == "S1_SHORT_FORM_CONTROL_RIVAL", f"short form rival {surface}")

    held_map = {row["candidate_surface"]: row for row in held}
    check(held_map["cheeey"]["serial_consensus_axes"] == "DRY", "cheeey serial dry")
    check(held_map["cheeey"]["serial_prior_result"] == "GDT747_PRIOR_REINFORCED", "cheeey prior reinforced")
    check(held_map["qochey"]["serial_position_evidence_units"] == "3", "qochey three frames")
    check(held_map["qochey"]["serial_consensus_axes"] == "NONE", "qochey no repeat consensus")
    check(held_map["qochey"]["strongest_single_evidence_axes"] == "DRY|MIDDLE_STAGE", "qochey strongest frame")
    check(
        held_map["qochey"]["serial_prior_result"]
        == "GDT747_PRIOR_STRONGEST_FRAME_REINFORCED_WITH_RIVALS",
        "qochey rival status",
    )
    check(held_map["chtl"]["serial_position_evidence_units"] == "0", "chtl no bridged frame")

    check(Counter(row["any_axis_hit"] for row in calibration) == Counter({"0": 240, "1": 189}), "calibration hits")
    calibration_map = {row["calibration_class"]: row for row in calibration_census}
    check(set(calibration_map) == set(CALIBRATION_EXPECTED), "calibration classes")
    for name, expected in CALIBRATION_EXPECTED.items():
        row = calibration_map[name]
        observed = tuple(int(row[field]) for field in (
            "positions", "any_axis_hits", "full_prediction_subsets",
            "opposition_contradictions",
        ))
        check(observed == expected, f"calibration counts {name}")
    check(calibration_map["NO_FORM_BRIDGE"]["interpretation"] == "DO_NOT_EXPORT_SERIAL_AXIS_AS_WORD_VALUE", "no bridge blocked")
    check(calibration_map["FORM_BRIDGE_ANY"]["interpretation"] == "USE_AS_EXPLORATORY_WHOLE_ROLE_BRIDGE", "form bridge usable")
    check(calibration_map["MULTIPLE_EDIT2_BRIDGES"]["interpretation"] == "STRONGEST_EXPLORATORY_BRIDGE_CLASS", "multi bridge strongest")

    packet_path = art / "GDT748_GDT388_SERIAL_EDGE_PACKET.tsv"
    packet = read_tsv(packet_path)
    intake = json.loads((art / "GDT748_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8"))
    check(len(packet) == 237, "237 relation rows")
    check(intake["status"] == "INVALID_PACKET" and not intake["score_ready"], "edge invalid not ready")
    expected_errors = [
        f"edge row {number}: formal access is not sealed"
        for number in range(2, 239)
    ]
    check(intake["errors"] == expected_errors, "edge sole formal errors")
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)], cwd=ROOT,
        check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    check(completed.returncode == 1, "edge checker expected return")
    check(json.loads(completed.stdout) == intake, "edge checker replay")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT748_RESULT_V1", "result schema")
    check(result["status"] == "PARTIAL_UNCONDITIONED_SERIAL_RULE_WEAK_FORM_BRIDGE_RETAINS_EXPLORATORY_LEADS", "result status")
    scope = result["scope"]
    expected_scope = {
        "all_length3_4_windows": 45136,
        "allowed_pages": 179,
        "collapsed_leave_one_out_positions": 429,
        "eligible_two_distinct_known_wholes": 3975,
        "form_bridged_position_evidence_units": 237,
        "form_bridged_target_surfaces": 122,
        "held_candidates": 12,
        "predictive_quality_or_stage_frames": 1406,
        "raw_leave_one_out_frames": 520,
        "token_cards": 32339,
        "unconditioned_predictive_position_evidence_units": 1125,
        "windows_with_exactly_one_non_w23_card": 4080,
    }
    check(scope == expected_scope, "result scope")
    check(result["surface_status_counts"] == dict(sorted(SURFACE_STATUS_COUNTS.items())), "result statuses")
    check(result["role_decision_counts"] == dict(sorted(ROLE_DECISION_COUNTS.items())), "result decisions")
    check(result["claim_ceiling"] == {
        "confirmed_lexemes": 0,
        "literal_identifications": 0,
        "component_export_credit": 0,
        "unseen_form_predictions": 0,
    }, "result ceiling")
    for name, digest in result["output_sha256"].items():
        check(sha256(art / name) == digest, f"result hash {name}")

    for binding in manifest["outputs"]:
        if binding["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / binding["path"]
        check(path.is_file(), f"output exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"output hash {binding['path']}")

    with tempfile.TemporaryDirectory(prefix=".gdt748_replay_", dir=EXP) as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)], cwd=ROOT,
            check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay return")
        for name in GENERATED:
            check((replay / name).is_file(), f"replay exists {name}")
            check((replay / name).read_bytes() == (art / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT748_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": expected_scope,
        "calibration": {
            "unconditioned_hits": "189/429",
            "form_bridge_hits": "96/126",
            "multiple_bridge_hits": "18/20",
        },
        "role_decisions": dict(sorted(ROLE_DECISION_COUNTS.items())),
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
