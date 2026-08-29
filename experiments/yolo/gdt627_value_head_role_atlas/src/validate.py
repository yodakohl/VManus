#!/usr/bin/env python3
"""Validate and byte-replay GDT627."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt627_value_head_role_atlas")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RESULT_REL = BASE_REL / "artifacts/RESULT.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
G623_DICT = ROOT / "experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/WORKING_DICTIONARY_V2.tsv"
G624_READER = ROOT / "experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/PRODUCTIVE_READER.tsv"
GENERATED_RELS = (
    BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    BASE_REL / "artifacts/HEAD_ROLE_ATLAS.tsv",
    BASE_REL / "artifacts/QUALITY_AXIS_DEGREE_OCCURRENCES.tsv",
    BASE_REL / "artifacts/QUALITY_AXIS_DEGREE_MATRIX.tsv",
    BASE_REL / "artifacts/LOCAL_THERMAL_MOISTURE_DEGREE_PAIRS.tsv",
    BASE_REL / "artifacts/FIXED_VALUE_FRAMES.tsv",
    BASE_REL / "artifacts/D_VALUE_FIXED_FRAMES.tsv",
    BASE_REL / "artifacts/D_CHOL_TERMINAL_WITNESSES.tsv",
    BASE_REL / "artifacts/D_PART_CONTACTS.tsv",
    BASE_REL / "artifacts/D_PART_BRACKETS.tsv",
    BASE_REL / "artifacts/WORKING_DICTIONARY_V4.tsv",
    BASE_REL / "artifacts/CONCRETE_READINGS_V2.tsv",
    RESULT_REL,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[str] = []

    def require(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    before = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    completed = subprocess.run(
        [sys.executable, str(BASE / "src/run.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(completed.returncode == 0, "builder exits zero")
    require(
        "heads=545 axis=1561 matrix=31/32 pairs=33 fixed=72 dframes=27 dpart=46" in completed.stdout,
        "builder summary",
    )
    after = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    require(before == after, "builder replay is byte-identical")

    result = json.loads((ROOT / RESULT_REL).read_text(encoding="utf-8"))
    require(result["schema"] == "GDT627_VALUE_HEAD_ROLE_ATLAS_RESULT_V1", "result schema")
    require(
        result["status"] == "QUALITY_DEGREE_SERIES_PROMOTED__D_FREE_MEASURE_HEAD_PROMOTED__A_VALUE_LINKER",
        "result status",
    )
    claimed_hash = result.pop("content_sha256")
    require(canonical_hash(result) == claimed_hash, "canonical result hash")
    result["content_sha256"] = claimed_hash
    require(result["guard"] == {
        "f1r": "EXCLUDED_IN_INHERITED_ATLAS",
        "f84": "FORBIDDEN",
        "f84r": "FORBIDDEN",
        "new_image_pages": 0,
        "new_source_queries": 0,
        "safe_occurrences": 5176,
        "safe_pages": 179,
    }, "scope guard")
    require(result["head_roles"]["heads"] == 545, "545 classified heads")
    require(result["head_roles"]["composed_or_bare_value_occurrences"] == 3169, "3169 composed or bare values")
    require(result["head_roles"]["role_head_counts"] == {
        "BARE_VALUE": 1,
        "FREE_MEASURE_OR_DEGREE_HEAD": 1,
        "OPEN_VALUE_HEAD": 494,
        "PLANT_PART_VALUE": 7,
        "QUALITY_AXIS_DEGREE": 11,
        "QUALITY_BUNDLE_DEGREE": 31,
    }, "head-role partition")
    require(result["quality_axis_degrees"] == {
        "adjacent_pairs": 13,
        "adjacent_same_degree_pairs": 9,
        "core_matrix_cells": 32,
        "local_thermal_moisture_pairs": 33,
        "occupied_core_cells": 31,
        "occurrences": 1561,
        "pages": 143,
        "primitive_cells": 16,
        "same_degree_pairs": 20,
        "stable_pairs": 30,
        "surfaces": 34,
        "triple_stable_occurrences": 1399,
    }, "quality-axis result summary")
    require(result["fixed_value_frames"] == {
        "all_stable_frames": 35,
        "d_frames": 27,
        "four_value_frames": 1,
        "frames": 72,
        "heads": 7,
    }, "fixed-frame result summary")
    require(result["d_free_measure"]["occurrences"] == 948, "948 d-head occurrences")
    require(result["d_free_measure"]["pages"] == 176, "d head on 176 pages")
    require(result["d_free_measure"]["mixed_value_lines"] == 49, "49 d mixed-value lines")
    require(result["d_free_measure"]["chol_terminal_values"] == ["I", "II", "III", "IV"], "chol-terminal I-IV")
    require(result["d_free_measure"]["chol_terminal_witnesses"] == 13, "thirteen chol-terminal witnesses")
    require(result["d_free_measure"]["part_contacts"] == 46, "46 d-part contacts")
    require(result["d_free_measure"]["part_brackets"] == 10, "ten d-part brackets")
    require(result["manual_sources"] == {
        "concrete_readings": 10,
        "historical_syntax_comparators": 6,
        "visual_judgments": 8,
    }, "manual-source counts")
    for path, expected in result["inputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"input hash {path}")
    for path, expected in result["outputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"output hash {path}")
    require(
        set(result["outputs"]) == {str(path) for path in GENERATED_RELS if path != RESULT_REL},
        "result binds every generated evidence file",
    )

    allowlist = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    require(len(allowlist) == 179, "allow-list length")
    require(sha256(ART / "PAGE_ALLOWLIST.tsv") == "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483", "canonical allow-list hash")
    require("f1r" not in {row["page"] for row in allowlist}, "allow-list excludes f1r")
    require(not any(row["page"].startswith("f84") for row in allowlist), "allow-list excludes f84 family")

    inherited = {row["surface"]: row for row in read_tsv(G623_DICT)}
    require(inherited["k"]["default_meaning_de"] == "heiß", "inherited k hot")
    require(inherited["t"]["default_meaning_de"] == "kalt", "inherited t cold")
    require(inherited["ch"]["default_meaning_de"] == "trocken", "inherited ch dry")
    require(inherited["sh"]["default_meaning_de"] == "feucht", "inherited sh moist")
    productive = {row["surface"]: row for row in read_tsv(G624_READER)}
    require(productive["qokchy"]["composition"].startswith("qo+k+ch"), "inherited qok hot-dry composition")
    require(productive["qotshy"]["composition"].startswith("qo+t+sh"), "inherited qot cold-moist composition")

    roles = read_tsv(ART / "HEAD_ROLE_ATLAS.tsv")
    require(len(roles) == 545, "545 role rows")
    require(sum(int(row["occurrences"]) for row in roles) == 5176, "all occurrences assigned once")
    require(Counter(row["role"] for row in roles) == Counter({
        "OPEN_VALUE_HEAD": 494,
        "QUALITY_BUNDLE_DEGREE": 31,
        "QUALITY_AXIS_DEGREE": 11,
        "PLANT_PART_VALUE": 7,
        "FREE_MEASURE_OR_DEGREE_HEAD": 1,
        "BARE_VALUE": 1,
    }), "role rows partition")
    d_role = next(row for row in roles if row["head"] == "da")
    require(tuple(d_role[f"count_{roman}"] for roman in ("I", "II", "III", "IV")) == ("17", "193", "721", "17"), "d exact I-IV counts")
    require(d_role["role"] == "FREE_MEASURE_OR_DEGREE_HEAD", "d role assignment")
    require(d_role["default_policy"] == "COMPOSE", "d composes")

    axis = read_tsv(ART / "QUALITY_AXIS_DEGREE_OCCURRENCES.tsv")
    require(len(axis) == 1561, "1561 quality-axis values")
    require(len({row["page"] for row in axis}) == 143, "quality-axis values on 143 pages")
    require(sum(int(row["triple_reading_token_stable"]) for row in axis) == 1399, "1399 stable quality-axis values")
    require(not any(row["page"] == "f1r" or row["page"].startswith("f84") for row in axis), "axis atlas excludes forbidden pages")

    matrix = read_tsv(ART / "QUALITY_AXIS_DEGREE_MATRIX.tsv")
    require(len(matrix) == 32, "complete 32-cell quality matrix")
    require(sum(int(row["occupied"]) for row in matrix) == 31, "31 occupied quality cells")
    require(sum(int(row["occupied"]) for row in matrix if row["quality_root"] in {"k", "t", "ch", "sh"}) == 16, "all sixteen primitive cells occupied")
    cells = {(row["quality_root"], row["working_roman"]): int(row["occurrences"]) for row in matrix}
    require(tuple(cells["k", value] for value in ("I", "II", "III", "IV")) == (2, 43, 74, 4), "hot I-IV counts")
    require(tuple(cells["t", value] for value in ("I", "II", "III", "IV")) == (1, 9, 45, 1), "cold I-IV counts")
    require(tuple(cells["ch", value] for value in ("I", "II", "III", "IV")) == (12, 19, 48, 1), "dry I-IV counts")
    require(tuple(cells["sh", value] for value in ("I", "II", "III", "IV")) == (6, 9, 19, 1), "moist I-IV counts")
    require(tuple(cells["qok", value] for value in ("I", "II", "III", "IV")) == (8, 273, 261, 2), "qok I-IV counts")
    require(tuple(cells["qot", value] for value in ("I", "II", "III", "IV")) == (2, 60, 79, 1), "qot I-IV counts")
    require(cells["ot", "IV"] == 0, "only missing core cell is ot IV")

    pairs = read_tsv(ART / "LOCAL_THERMAL_MOISTURE_DEGREE_PAIRS.tsv")
    require(len(pairs) == 33, "33 local quality-axis pairs")
    require(sum(int(row["token_distance"]) == 1 for row in pairs) == 13, "thirteen adjacent quality pairs")
    require(sum(int(row["same_degree"]) for row in pairs) == 20, "twenty same-degree quality pairs")
    require(sum(int(row["token_distance"]) == 1 and int(row["same_degree"]) for row in pairs) == 9, "nine adjacent same-degree quality pairs")
    require(sum(int(row["both_triple_token_stable"]) for row in pairs) == 30, "thirty stable quality pairs")
    pair_key = {(row["locus"], row["thermal_surface"], row["moisture_surface"]): row for row in pairs}
    require(pair_key["f111v.33", "qokan", "chan"]["working_pair_de"] == "heiß im qo-Qualitätsrahmen Grad I; trocken Grad I", "f111v hot-dry I")
    require(pair_key["f107v.7", "qokain", "chain"]["same_degree"] == "1", "f107v hot-dry II")
    require(pair_key["f106r.20", "qokaiin", "shaiin"]["same_degree"] == "1", "f106r hot-moist III")

    frames = read_tsv(ART / "FIXED_VALUE_FRAMES.tsv")
    require(len(frames) == 72, "72 multi-value fixed frames")
    require(Counter(row["head"] for row in frames) == Counter({"da": 27, "qoka": 14, "a": 13, "sa": 9, "oka": 7, "ola": 1, "ota": 1}), "fixed-frame heads")
    four = [row for row in frames if row["distinct_values"] == "4"]
    require(len(four) == 1, "one identical four-value frame")
    require((four[0]["head"], four[0]["left_surface"], four[0]["right_surface"], four[0]["values"]) == ("da", "chol", "<END>", "I|II|III|IV"), "d owns chol terminal I-IV frame")
    d_frames = read_tsv(ART / "D_VALUE_FIXED_FRAMES.tsv")
    require(len(d_frames) == 27 and all(row["head"] == "da" for row in d_frames), "27 isolated d frames")

    d_chol = read_tsv(ART / "D_CHOL_TERMINAL_WITNESSES.tsv")
    require(len(d_chol) == 13, "thirteen d chol-terminal rows")
    require(Counter(row["working_roman"] for row in d_chol) == Counter({"III": 9, "II": 2, "I": 1, "IV": 1}), "chol-terminal value counts")
    require(all(row["surface_line"].split()[-2] == "chol" and row["surface_line"].split()[-1] == row["surface"] for row in d_chol), "chol-terminal frame materialized")
    require(next(row for row in d_chol if row["locus"] == "f2r.7")["surface"] == "dan", "f2r value I witness")
    require(next(row for row in d_chol if row["locus"] == "f17r.11")["surface"] == "daiiin", "f17r value IV witness")

    contacts = read_tsv(ART / "D_PART_CONTACTS.tsv")
    require(len(contacts) == 46, "46 exact d-part contacts")
    require(Counter(row["working_roman"] for row in contacts) == Counter({"III": 41, "II": 5}), "d-part contacts use II and III")
    require(Counter(row["direction"] for row in contacts) == Counter({"PART_THEN_D": 23, "D_THEN_PART": 21, "PART_D_PART": 2}), "d-part contact directions")
    require(any(row["locus"] == "f45v.2" and row["direction"] == "PART_D_PART" for row in contacts), "f45 part-d-part witness")
    brackets = read_tsv(ART / "D_PART_BRACKETS.tsv")
    require(len(brackets) == 10, "ten bounded part brackets")
    require(Counter(row["working_roman"] for row in brackets) == Counter({"III": 9, "II": 1}), "bracket value counts")

    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V4.tsv")
    require(len(dictionary) == 15, "fifteen compact dictionary rows")
    require(next(row for row in dictionary if row["entry"] == "a")["kind"] == "VALUE_SLOT_LINKER", "a is value-slot linker")
    require(next(row for row in dictionary if row["entry"] == "d")["kind"] == "FREE_VALUE_HEAD", "d is free value head")
    require(next(row for row in dictionary if row["entry"] == "daiin")["working_meaning_de"].startswith("Maß-/Portionswert III"), "daiin concrete default")
    require(any(row["entry"].startswith("kan/kain/kaiin/kaiiin") and row["working_meaning_de"] == "heiß, Grad I/II/III/IV" for row in dictionary), "hot degree dictionary series")

    cases = read_tsv(ART / "CONCRETE_READINGS_V2.tsv")
    require(len(cases) == 10, "ten concrete readings")
    require(next(row for row in cases if row["case_id"] == "HOT_DRY_I")["working_reading_de"] == "heiß ersten Grades; trocken ersten Grades", "concrete hot-dry I")
    require(next(row for row in cases if row["case_id"] == "HOT_MOIST_III")["working_reading_de"] == "heiß dritten Grades; feucht dritten Grades", "concrete hot-moist III")
    require(next(row for row in cases if row["case_id"] == "F45_PART_DOSE")["working_reading_de"] == "Blüten-/Pflanzenteil, drei Portionen/Maße; Blattgut", "concrete f45 part-dose reading")

    historical = read_tsv(ART / "HISTORICAL_SYNTAX_COMPARATORS.tsv")
    require(len(historical) == 6, "six historical syntax comparators")
    require({"WELLCOME_MS542_ALOES", "VAT_PAL_LAT_1234", "WELLCOME_MS492_DOSE", "DURHAM_BIII12"} <= {row["source_id"] for row in historical}, "historical source identities")
    visual = read_tsv(ART / "MANUAL_VISUAL_JUDGMENTS.tsv")
    require(len(visual) == 8, "eight visual and layout judgments")
    require(all(row["new_image_pages"] == "0" for row in visual), "no new image page")
    require(any(row["judgment_id"] == "VIS_F15R_SAME_PART_D_VALUES" for row in visual), "same-part variable-d control retained")

    private_pattern = re.compile(
        "/" + "home/|/" + "tmp/|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|"
        "AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|"
        "password\\s*[=:]|api[_-]?key\\s*[=:]|secret\\s*[=:]",
        re.IGNORECASE,
    )
    scan_paths = (
        BASE / "README.md",
        BASE / "METHOD.md",
        BASE / "REPORT.md",
        BASE / "experiment.json",
        BASE / "artifacts/README.md",
        ART / "HISTORICAL_SYNTAX_COMPARATORS.tsv",
        ART / "MANUAL_VISUAL_JUDGMENTS.tsv",
        *[ROOT / path for path in GENERATED_RELS],
    )
    for path in scan_paths:
        require(not private_pattern.search(path.read_text(encoding="utf-8")), f"privacy scan {path.relative_to(ROOT)}")

    payload = {
        "schema": "GDT627_VALIDATION_V1",
        "experiment_id": "GDT627",
        "status": "PASS",
        "checks": checks,
        "check_count": len(checks),
        "result_sha256": sha256(ROOT / RESULT_REL),
    }
    (ROOT / VALIDATION_REL).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
