#!/usr/bin/env python3
"""Artifact validation and byte-identical replay for GDT746."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt746_whole_analogy_distribution_test")
EXP = ROOT / BASE
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "PARTIAL__17_A3_COMPLETE_WHOLES__52_DISTANCE1_RELATIONS__"
    "63_SURFACES__1523_OCCURRENCES__15_PAIR_REINFORCED__"
    "10_PAIR_COMPATIBLE__4_CANDIDATE_MULTI_REINFORCED__"
    "16_DIRECT_IN_85_TOP5_SLOTS__"
    "14_OF_17_FORM_DISTRIBUTION_AXIS_AGREEMENTS__"
    "ZERO_LITERAL_IDENTITIES__ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "A3_17_TARGETS.tsv",
    "SURFACE_63_OCCURRENCE_FEATURES.tsv",
    "CALIBRATION_782_CANDIDATE_KNOWN_SCORES.tsv",
    "PAIR_52_DISTRIBUTION_SCORES.tsv",
    "CANDIDATE_17_DISTRIBUTION_CENSUS.tsv",
    "GDT746_WHOLE_DISTRIBUTION_READER.md",
    "GDT746_GDT388_DISTRIBUTION_EDGE_PACKET.tsv",
    "GDT746_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)
PAIR_COUNTS = Counter({
    "D3_DISTRIBUTION_REINFORCED": 15,
    "D2_DISTRIBUTION_COMPATIBLE": 10,
    "D1_SPARSE_COMPATIBLE": 8,
    "D1_MIXED_OR_ORDINARY": 19,
})
CANDIDATE_COUNTS = Counter({
    "S3_MULTI_NEIGHBOR_DISTRIBUTION_REINFORCED": 4,
    "S2_DISTRIBUTION_SUPPORTED": 8,
    "S1_DISTRIBUTION_OPEN": 2,
    "S1_SINGLETON_REMAINS_OPEN": 3,
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
    check(manifest["experiment_id"] == "GDT746", "manifest id")
    check(manifest["slug"] == "whole_analogy_distribution_test", "manifest slug")
    check(manifest["status"] == STATUS, "manifest status")
    check(
        manifest["dependencies"]
        == ["GDT388", "GDT734", "GDT738", "GDT739", "GDT744", "GDT745"],
        "manifest dependencies",
    )
    check(
        manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
        "sealed data",
    )
    check(bool(manifest["question"]), "manifest question")
    check(bool(manifest["claim_ceiling"]), "manifest claim ceiling")
    check(
        manifest["validation"]
        == {"artifact": str(VALIDATION_REL), "status": "PASS"},
        "manifest validation contract",
    )
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash {binding['path']}")

    manual = read_tsv(SRC / "MANUAL_DISTRIBUTION_ASSESSMENTS.tsv")
    check(len(manual) == 17, "17 manual rows")
    check(len({row["candidate_surface"] for row in manual}) == 17, "manual coverage")
    for row in manual:
        check(bool(row["meaning_action"]), f"manual action {row['candidate_surface']}")
        check(bool(row["next_working_meaning_de"]), f"manual meaning {row['candidate_surface']}")
        check(bool(row["manual_note_de"]), f"manual note {row['candidate_surface']}")
        check("Arbeitsgut" not in row["next_working_meaning_de"], f"no generic renderer {row['candidate_surface']}")

    targets = read_tsv(art / "A3_17_TARGETS.tsv")
    check(len(targets) == 17, "17 A3 targets")
    candidate_surfaces = {row["candidate_surface"] for row in targets}
    check(len(candidate_surfaces) == 17, "17 target surfaces")
    check(sum(int(row["distance1_neighbor_wholes"]) for row in targets) == 52, "52 target relations")
    for row in targets:
        check(row["literal_identity"] == "OPEN", f"target literal {row['candidate_surface']}")
        check(row["confirmed_lexeme"] == "0", f"target lexeme {row['candidate_surface']}")
        check(row["component_export_credit"] == "0", f"target component {row['candidate_surface']}")

    occurrences = read_tsv(art / "SURFACE_63_OCCURRENCE_FEATURES.tsv")
    check(len(occurrences) == 1523, "1523 occurrence rows")
    check(len({row["gdt746_occurrence_id"] for row in occurrences}) == 1523, "unique occurrence ids")
    check(len({row["cell_id"] for row in occurrences}) == 1523, "unique occurrence cells")
    check(len({row["surface"] for row in occurrences}) == 63, "63 occurrence surfaces")
    check(len({row["page"] for row in occurrences}) == 172, "172 cached pages")
    check(sum(int(row["reader_exact"]) for row in occurrences) == 1228, "1228 reader-exact occurrences")
    occurrences_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in occurrences:
        occurrence = row["gdt746_occurrence_id"]
        occurrences_by_surface[row["surface"]].append(row)
        check(not row["page"].startswith("f84"), f"sealed occurrence {occurrence}")
        check(row["surface_roles"] in {"A3_CANDIDATE", "KNOWN_DISTANCE1_NEIGHBOR"}, f"surface role {occurrence}")
        check(row["line_position"] in {"FIRST", "MIDDLE", "LAST", "SINGLE"}, f"line position {occurrence}")
        check(row["nearest_close_signature"] in {
            "NO_CLOSE_WITHIN_5", "LEFT_D1", "LEFT_D2", "LEFT_D3_5",
            "RIGHT_D1", "RIGHT_D2", "RIGHT_D3_5", "BOTH_D1", "BOTH_D2",
            "BOTH_D3_5",
        }, f"closure class {occurrence}")
        check(row["literal_identity"] == "OPEN", f"occurrence literal {occurrence}")
        check(row["confirmed_lexeme"] == "0", f"occurrence lexeme {occurrence}")
        check(row["component_export_credit"] == "0", f"occurrence component {occurrence}")

    calibration = read_tsv(art / "CALIBRATION_782_CANDIDATE_KNOWN_SCORES.tsv")
    check(len(calibration) == 782, "782 calibration rows")
    check(len({row["gdt746_calibration_id"] for row in calibration}) == 782, "unique calibration ids")
    check({row["candidate_surface"] for row in calibration} == candidate_surfaces, "calibration target coverage")
    known_surfaces = {row["known_surface"] for row in calibration}
    check(len(known_surfaces) == 46, "46 known comparison surfaces")
    calibration_by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in calibration:
        relation = row["gdt746_calibration_id"]
        calibration_by_candidate[row["candidate_surface"]].append(row)
        check(row["known_surface"] in known_surfaces, f"known calibration surface {relation}")
        check(0 <= float(row["hybrid_distribution_similarity"]) <= 1, f"hybrid range {relation}")
        check(0 <= float(row["section_removed_local_similarity"]) <= 1, f"local range {relation}")
        check(1 <= int(row["known_whole_rank"]) <= 46, f"rank range {relation}")
        check(0 <= float(row["known_whole_rank_percentile"]) <= 1, f"percentile range {relation}")
        check(0 <= float(row["section_removed_rank_percentile"]) <= 1, f"local percentile range {relation}")
        check(row["literal_identity_credit"] == "0", f"calibration literal {relation}")
        check(row["confirmed_lexeme"] == "0", f"calibration lexeme {relation}")
        check(row["component_export_credit"] == "0", f"calibration component {relation}")
    for candidate, rows in calibration_by_candidate.items():
        check(len(rows) == 46, f"46 calibration rows {candidate}")
        check(len({row["known_surface"] for row in rows}) == 46, f"unique known calibration {candidate}")
        check(sum(int(row["top_five_distribution_neighbor"]) for row in rows) == 5, f"five top slots {candidate}")
    check(sum(int(row["selected_distance1_neighbor"]) for row in calibration) == 52, "52 selected calibration relations")
    check(
        sum(
            int(row["selected_distance1_neighbor"])
            and int(row["top_five_distribution_neighbor"])
            for row in calibration
        ) == 16,
        "16 direct top-five slots",
    )

    pairs = read_tsv(art / "PAIR_52_DISTRIBUTION_SCORES.tsv")
    check(len(pairs) == 52, "52 pair rows")
    check(len({row["gdt746_pair_id"] for row in pairs}) == 52, "unique pair ids")
    check(Counter(row["distribution_status"] for row in pairs) == PAIR_COUNTS, "pair status counts")
    selected_keys = {
        (row["candidate_surface"], row["known_surface"])
        for row in calibration if row["selected_distance1_neighbor"] == "1"
    }
    pair_keys = {(row["candidate_surface"], row["known_neighbor_surface"]) for row in pairs}
    check(pair_keys == selected_keys, "pair calibration join")
    calibration_map = {
        (row["candidate_surface"], row["known_surface"]): row
        for row in calibration
    }
    for row in pairs:
        relation = row["gdt746_pair_id"]
        key = (row["candidate_surface"], row["known_neighbor_surface"])
        source = calibration_map[key]
        check(row["levenshtein_distance"] == "1", f"distance one {relation}")
        check(row["hybrid_distribution_similarity"] == source["hybrid_distribution_similarity"], f"hybrid join {relation}")
        check(row["section_removed_local_similarity"] == source["section_removed_local_similarity"], f"local join {relation}")
        check(row["known_whole_rank_percentile"] == source["known_whole_rank_percentile"], f"rank join {relation}")
        check(row["section_removed_rank_percentile"] == source["section_removed_rank_percentile"], f"local rank join {relation}")
        check(row["candidate_occurrences_reader_exact"] == str(sum(int(item["reader_exact"]) for item in occurrences_by_surface[row["candidate_surface"]])), f"candidate count join {relation}")
        check(row["known_neighbor_occurrences_reader_exact"] == str(sum(int(item["reader_exact"]) for item in occurrences_by_surface[row["known_neighbor_surface"]])), f"known count join {relation}")
        check(row["relation_scope"] == "COMPLETE_WHOLE_DISTRIBUTION_ANALOGY_ONLY", f"whole scope {relation}")
        check(row["literal_identity_credit"] == "0", f"pair literal {relation}")
        check(row["confirmed_lexeme"] == "0", f"pair lexeme {relation}")
        check(row["component_export_credit"] == "0", f"pair component {relation}")

    census = read_tsv(art / "CANDIDATE_17_DISTRIBUTION_CENSUS.tsv")
    check(len(census) == 17, "17 census rows")
    check({row["candidate_surface"] for row in census} == candidate_surfaces, "census coverage")
    check(Counter(row["distribution_status"] for row in census) == CANDIDATE_COUNTS, "candidate status counts")
    manual_map = {row["candidate_surface"]: row for row in manual}
    for row in census:
        candidate = row["candidate_surface"]
        check(row["meaning_action"] == manual_map[candidate]["meaning_action"], f"manual action join {candidate}")
        check(row["next_working_meaning_de"] == manual_map[candidate]["next_working_meaning_de"], f"manual meaning join {candidate}")
        check(row["manual_assessment_note_de"] == manual_map[candidate]["manual_note_de"], f"manual note join {candidate}")
        check(len(row["top5_distribution_surfaces"].split("|")) == 5, f"top-five census {candidate}")
        check(values(row["form_and_top5_axis_agreement"]) <= values(row["gdt745_consensus_axes"]), f"agreement subset {candidate}")
        check(row["literal_identity"] == "OPEN", f"census literal {candidate}")
        check(row["confirmed_lexeme"] == "0", f"census lexeme {candidate}")
        check(row["component_export_credit"] == "0", f"census component {candidate}")
        check(row["unseen_form_export"] == "0", f"census unseen {candidate}")
    check(sum(int(row["top5_direct_distance1_neighbors"]) for row in census) == 16, "census 16 top-five direct slots")
    check(sum(int(row["top5_direct_distance1_neighbors"]) > 0 for row in census) == 11, "11 candidates with top-five direct")
    check(sum(row["form_and_top5_axis_agreement"] != "NONE" for row in census) == 14, "14 form distribution axis agreements")

    packet_path = art / "GDT746_GDT388_DISTRIBUTION_EDGE_PACKET.tsv"
    packet = read_tsv(packet_path)
    intake = json.loads((art / "GDT746_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8"))
    check(len(packet) == 1, "one edge intake row")
    check(packet[0]["relation_type"] == "COMPLETE_WHOLE_DISTRIBUTION_ANALOGY", "edge relation type")
    check(packet[0]["formal_access_state"] == "FORMAL_ACCESSED", "edge formal state")
    check(intake["status"] == "INVALID_PACKET", "edge intake invalid")
    check(not intake["score_ready"], "edge not score ready")
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    check(completed.returncode == 1, "edge checker expected return")
    check(json.loads(completed.stdout) == intake, "edge checker replay")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT746_RESULT_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"]["candidate_wholes"] == 17, "result candidates")
    check(result["scope"]["distance_one_relations"] == 52, "result pairs")
    check(result["scope"]["candidate_known_calibration_relations"] == 782, "result calibration")
    check(result["scope"]["selected_occurrences"] == 1523, "result occurrences")
    check(result["scope"]["reader_exact_occurrences"] == 1228, "result exact occurrences")
    check(result["pair_status_counts"] == dict(sorted(PAIR_COUNTS.items())), "result pair counts")
    check(result["candidate_status_counts"] == dict(sorted(CANDIDATE_COUNTS.items())), "result candidate counts")
    check(result["calibration_summary"]["direct_distance_one_neighbors_in_top_five_slots"] == 16, "result top-five slots")
    check(result["calibration_summary"]["candidates_with_form_top5_axis_agreement"] == 14, "result axis agreements")
    check(result["claim_ceiling"] == {
        "confirmed_lexemes": 0,
        "literal_identifications": 0,
        "component_export_credit": 0,
        "unseen_form_predictions": 0,
    }, "result claim ceiling")
    for name, digest in result["artifacts"].items():
        check(sha256(art / name) == digest, f"result artifact hash {name}")

    for binding in manifest["outputs"]:
        path = ROOT / binding["path"]
        if binding["path"] == str(VALIDATION_REL):
            continue
        check(path.is_file(), f"output exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"output hash {binding['path']}")

    with tempfile.TemporaryDirectory(prefix=".gdt746_replay_", dir=EXP) as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay return")
        for name in GENERATED:
            check((replay / name).is_file(), f"replay exists {name}")
            check((replay / name).read_bytes() == (art / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT746_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": {
            "candidate_wholes": 17,
            "distance_one_relations": 52,
            "calibration_relations": 782,
            "selected_surfaces": 63,
            "selected_occurrences": 1523,
            "reader_exact_occurrences": 1228,
        },
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
