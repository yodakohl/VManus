#!/usr/bin/env python3
"""Artifact validation and byte replay for GDT747."""

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
BASE = Path("experiments/yolo/gdt747_supported_whole_passage_application")
EXP = ROOT / BASE
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "PARTIAL__12_GDT746_SUPPORTED_WHOLES__64_OCCURRENCES__62_LINES__"
    "1_CONTRASTIVE_LOCAL_PARADIGMS__2_MULTIWHOLE_LOCAL_SUPPORTS__"
    "16_SINGLE_WHOLE_LOCAL_SUPPORTS__62_STRONG_CONCRETE_TOKEN_DELTA__"
    "6_PASSAGE_BLOCKS__ZERO_LITERAL_IDENTITIES__ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "SUPPORTED_12_PASSAGE_VALUES.tsv",
    "TOKEN_PASSAGE_RENDER.tsv",
    "OCCURRENCE_64_LOCAL_SUPPORT.tsv",
    "LINE_62_PASSAGE_CENSUS.tsv",
    "CANDIDATE_12_PASSAGE_CENSUS.tsv",
    "BLOCK_6_PASSAGE_CENSUS.tsv",
    "GDT747_SUPPORTED_WHOLE_PASSAGE_READER.md",
    "GDT747_GDT388_SERIAL_PARADIGM_EDGE_PACKET.tsv",
    "GDT747_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)
LOCAL_COUNTS = Counter({
    "L0_FORM_ONLY_NO_CORE": 2,
    "L0_NO_LOCAL_W23_SUPPORT": 43,
    "L1_SINGLE_WHOLE_LOCAL_SUPPORT": 16,
    "L2_MULTIWHOLE_LOCAL_SUPPORT": 2,
    "L3_CONTRASTIVE_SERIAL_PARADIGM": 1,
})
CANDIDATE_COUNTS = Counter({
    "P0_FORM_ONLY_HELD_OPEN": 1,
    "P0_NO_LOCAL_PASSAGE_SUPPORT": 3,
    "P1_LOCAL_PASSAGE_SUPPORT": 6,
    "P2_RECURRENT_MULTIWHOLE_PASSAGE_SUPPORT": 1,
    "P3_CONTRASTIVE_PASSAGE_SUPPORT": 1,
})
RETIRED = (
    "pulver", "samen", "saat", "wurzel", "holz", "blatt", "kraut", "pflanz",
    "wasser", "wein", "öl", "salz", "pfund", "handvoll", "gewichtseinheit",
    "arbeitsgut", "arbeitschritt", "arbeitsmaterial",
)


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
    check(manifest["experiment_id"] == "GDT747", "manifest id")
    check(manifest["slug"] == "supported_whole_passage_application", "manifest slug")
    check(manifest["status"] == STATUS, "manifest status")
    check(
        manifest["dependencies"]
        == ["GDT388", "GDT734", "GDT739", "GDT743", "GDT746"],
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
        "manifest validation contract",
    )
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash {binding['path']}")

    safe_source = read_tsv(SRC / "PASSAGE_SAFE_VALUES.tsv")
    block_specs = read_tsv(SRC / "PASSAGE_BLOCK_SPECS.tsv")
    manual_blocks = read_tsv(SRC / "MANUAL_BLOCK_ASSESSMENTS.tsv")
    check(len(safe_source) == 12, "12 safe source rows")
    check(len({row["candidate_surface"] for row in safe_source}) == 12, "safe source coverage")
    check(sum(row["passage_credit"] == "FORM_AND_DISTRIBUTION_INTERSECTION" for row in safe_source) == 11, "11 intersection source values")
    check(sum(row["passage_credit"] == "FORM_ONLY_NO_PASSAGE_CREDIT" for row in safe_source) == 1, "one form-only source value")
    check(len(block_specs) == 6 and len(manual_blocks) == 6, "six block source cards")
    check({row["block_id"] for row in block_specs} == {row["block_id"] for row in manual_blocks}, "block source join")

    values_rows = read_tsv(art / "SUPPORTED_12_PASSAGE_VALUES.tsv")
    check(len(values_rows) == 12, "12 value cards")
    value_map = {row["candidate_surface"]: row for row in values_rows}
    check(set(value_map) == {row["candidate_surface"] for row in safe_source}, "value card coverage")
    for row in values_rows:
        candidate = row["candidate_surface"]
        check(bool(row["passage_safe_value_de"]), f"value text {candidate}")
        check(not any(word in row["passage_safe_value_de"].lower() for word in RETIRED), f"safe candidate value {candidate}")
        check(row["literal_identity"] == "OPEN", f"value literal {candidate}")
        check(row["confirmed_lexeme"] == "0", f"value lexeme {candidate}")
        check(row["component_export_credit"] == "0", f"value component {candidate}")
    check(value_map["chtl"]["passage_core_axes"] == "NONE", "chtl no passage core")

    tokens = read_tsv(art / "TOKEN_PASSAGE_RENDER.tsv")
    check(len(tokens) == 613, "613 candidate-line token rows")
    check(len({row["gdt747_token_id"] for row in tokens}) == 613, "unique token ids")
    check(len({row["locus"] for row in tokens}) == 62, "62 token loci")
    check(len({row["page"] for row in tokens}) == 40, "40 token pages")
    check(sum(int(row["candidate_token"]) for row in tokens) == 64, "64 candidate tokens")
    check(sum(int(row["strong_concrete_credit"]) for row in tokens if int(row["candidate_token"])) == 62, "62 strong candidate credits")
    token_by_coordinate = {(row["locus"], row["token_ordinal"]): row for row in tokens}
    check(len(token_by_coordinate) == 613, "unique token coordinates")
    for row in tokens:
        token_id = row["gdt747_token_id"]
        check(not row["page"].startswith("f84"), f"sealed token {token_id}")
        check(row["literal_identity"] == "OPEN", f"token literal {token_id}")
        check(row["confirmed_lexeme"] == "0", f"token lexeme {token_id}")
        check(row["component_export_credit"] == "0", f"token component {token_id}")
        if row["source_class"] in {
            "GDT746_FORM_DISTRIBUTION_INTERSECTION", "GDT743_OCCURRENCE_WHOLE",
            "GDT734_W23_SAFE_WHOLE", "GDT734_WEAK_SAFE_WHOLE",
        }:
            check(not any(word in row["after_render_de"].lower() for word in RETIRED), f"no retired visible value {token_id}")
        if row["source_class"] == "WITHHELD_RETIRED_LITERAL":
            check("zurückgehaltene Altidentität" in row["after_render_de"], f"withheld marker {token_id}")

    local = read_tsv(art / "OCCURRENCE_64_LOCAL_SUPPORT.tsv")
    check(len(local) == 64, "64 local rows")
    check(len({row["gdt747_occurrence_id"] for row in local}) == 64, "unique local ids")
    check(Counter(row["local_support_tier"] for row in local) == LOCAL_COUNTS, "local tier counts")
    for row in local:
        occurrence = row["gdt747_occurrence_id"]
        check(row["candidate_surface"] in value_map, f"local candidate {occurrence}")
        check((row["locus"], row["token_ordinal"]) in token_by_coordinate, f"local token join {occurrence}")
        check(values(row["locally_supported_core_axes"]) <= values(row["passage_core_axes"]), f"local axis subset {occurrence}")
        check(0 <= float(row["locally_supported_core_fraction"]) <= 1, f"local fraction {occurrence}")
        check(row["literal_identity"] == "OPEN", f"local literal {occurrence}")
        check(row["confirmed_lexeme"] == "0", f"local lexeme {occurrence}")
        check(row["component_export_credit"] == "0", f"local component {occurrence}")
    contrastive = [row for row in local if row["local_support_tier"] == "L3_CONTRASTIVE_SERIAL_PARADIGM"]
    check(len(contrastive) == 1, "one contrastive row")
    check(
        contrastive[0]["candidate_surface"] == "qochey"
        and contrastive[0]["locus"] == "f104v.23"
        and contrastive[0]["token_ordinal"] == "3",
        "qochey contrastive locus",
    )
    check(contrastive[0]["supporting_whole_surfaces"] == "qokchey|tchey", "qochey support wholes")
    check(contrastive[0]["locally_supported_core_axes"] == "DRY", "qochey supported dry")
    check("HOT" in values(contrastive[0]["neighbor_contrast_axes"]) and "COLD" in values(contrastive[0]["neighbor_contrast_axes"]), "qochey hot cold contrast")
    cheeey_multi = [row for row in local if row["candidate_surface"] == "cheeey" and row["local_support_tier"] == "L2_MULTIWHOLE_LOCAL_SUPPORT"]
    check(len(cheeey_multi) == 2, "two cheeey multiwhole supports")
    check({row["locus"] for row in cheeey_multi} == {"f104v.24", "f113r.49"}, "cheeey support loci")

    lines = read_tsv(art / "LINE_62_PASSAGE_CENSUS.tsv")
    check(len(lines) == 62, "62 line rows")
    check(len({row["locus"] for row in lines}) == 62, "unique line loci")
    check(sum(int(row["candidate_occurrences"]) for row in lines) == 64, "line candidate total")
    check(sum(int(row["strong_concrete_delta"]) for row in lines) == 62, "62 line strong delta")
    check(sum(int(row["strong_concrete_delta"]) > 0 for row in lines) == 61, "61 positive lines")
    check(sum(int(row["after_open_tokens"]) <= 1 for row in lines) == 21, "21 nearly covered lines")
    check(sum(int(row["after_open_tokens"]) == 0 for row in lines) == 2, "two zero ordinary-open lines")
    check(sum(float(row["after_strong_coverage_fraction"]) >= 0.5 for row in lines) == 11, "11 half-strong lines")
    check(sum(int(row["retired_literal_withheld_tokens"]) > 0 for row in lines) == 36, "36 withheld-literal lines")
    for row in lines:
        check(row["literal_plaintext_credit"] == "0", f"line plaintext {row['locus']}")
        check(row["component_export_credit"] == "0", f"line component {row['locus']}")

    candidates = read_tsv(art / "CANDIDATE_12_PASSAGE_CENSUS.tsv")
    check(len(candidates) == 12, "12 candidate census rows")
    check(Counter(row["passage_status"] for row in candidates) == CANDIDATE_COUNTS, "candidate passage counts")
    candidate_map = {row["candidate_surface"]: row for row in candidates}
    check(candidate_map["qochey"]["passage_status"] == "P3_CONTRASTIVE_PASSAGE_SUPPORT", "qochey P3")
    check(candidate_map["cheeey"]["passage_status"] == "P2_RECURRENT_MULTIWHOLE_PASSAGE_SUPPORT", "cheeey P2")
    check(candidate_map["chtl"]["passage_status"] == "P0_FORM_ONLY_HELD_OPEN", "chtl held")
    check({row["candidate_surface"] for row in candidates if row["passage_status"] == "P0_NO_LOCAL_PASSAGE_SUPPORT"} == {"chckh", "chetar", "dsheedy"}, "three no-local candidates")
    for row in candidates:
        candidate = row["candidate_surface"]
        check(row["literal_identity"] == "OPEN", f"candidate literal {candidate}")
        check(row["confirmed_lexeme"] == "0", f"candidate lexeme {candidate}")
        check(row["component_export_credit"] == "0", f"candidate component {candidate}")

    blocks = read_tsv(art / "BLOCK_6_PASSAGE_CENSUS.tsv")
    check(len(blocks) == 6, "six blocks")
    check({row["block_id"] for row in blocks} == {f"G747-B{number:02d}" for number in range(1, 7)}, "block ids")
    check(Counter(row["manual_information_gain"] for row in blocks) == Counter({"HIGH": 3, "MEDIUM": 2, "LOW": 1}), "block information grades")
    check(sum(int(row["tokens"]) for row in blocks) == 187, "187 block tokens")
    block_map = {row["block_id"]: row for row in blocks}
    check(block_map["G747-B05"]["tokens"] == "9", "compact block nine tokens")
    check(block_map["G747-B05"]["strong_concrete_tokens_after"] == "5", "compact block five strong")
    check(block_map["G747-B05"]["open_tokens_after"] == "1", "compact block one open")
    for row in blocks:
        check(row["manual_passage_type"] != "PENDING", f"block type {row['block_id']}")
        check(row["manual_assessment_de"] != "PENDING", f"block assessment {row['block_id']}")
        check(row["literal_plaintext_credit"] == "0", f"block plaintext {row['block_id']}")
        check(row["component_export_credit"] == "0", f"block component {row['block_id']}")

    packet_path = art / "GDT747_GDT388_SERIAL_PARADIGM_EDGE_PACKET.tsv"
    packet = read_tsv(packet_path)
    intake = json.loads((art / "GDT747_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8"))
    check(len(packet) == 1, "one edge row")
    check(packet[0]["pivot_locus"] == "f104v.23@3", "edge pivot")
    check(packet[0]["target_locus"] == "f104v.23@2", "edge target")
    check(packet[0]["relation_type"] == "SERIAL_COMPLETE_WHOLE_AXIS_PARADIGM", "edge type")
    check(intake["status"] == "INVALID_PACKET" and not intake["score_ready"], "edge invalid not ready")
    check(intake["errors"] == ["edge row 2: formal access is not sealed"], "edge sole error")
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)], cwd=ROOT,
        check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    check(completed.returncode == 1, "edge checker expected return")
    check(json.loads(completed.stdout) == intake, "edge checker replay")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT747_RESULT_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"]["supported_candidate_wholes"] == 12, "result candidates")
    check(result["scope"]["candidate_occurrences"] == 64, "result occurrences")
    check(result["scope"]["candidate_lines"] == 62, "result lines")
    check(result["scope"]["candidate_line_tokens"] == 613, "result tokens")
    check(result["scope"]["passage_block_tokens"] == 187, "result block tokens")
    check(result["local_support_tier_counts"] == dict(sorted(LOCAL_COUNTS.items())), "result local counts")
    check(result["candidate_passage_status_counts"] == dict(sorted(CANDIDATE_COUNTS.items())), "result candidate counts")
    check(result["line_coverage"]["strong_concrete_token_delta"] == 62, "result delta")
    check(result["claim_ceiling"] == {
        "confirmed_lexemes": 0,
        "literal_identifications": 0,
        "component_export_credit": 0,
        "unseen_form_predictions": 0,
    }, "result ceiling")
    for name, digest in result["artifacts"].items():
        check(sha256(art / name) == digest, f"result artifact hash {name}")

    for binding in manifest["outputs"]:
        if binding["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / binding["path"]
        check(path.is_file(), f"output exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"output hash {binding['path']}")

    with tempfile.TemporaryDirectory(prefix=".gdt747_replay_", dir=EXP) as temporary:
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
        "schema": "GDT747_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": {
            "supported_candidate_wholes": 12,
            "candidate_occurrences": 64,
            "candidate_lines": 62,
            "candidate_line_tokens": 613,
            "passage_blocks": 6,
            "passage_block_tokens": 187,
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
