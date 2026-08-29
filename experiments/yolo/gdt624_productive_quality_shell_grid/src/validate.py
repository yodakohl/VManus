#!/usr/bin/env python3
"""Validate and byte-replay GDT624."""

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
BASE_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RESULT_REL = BASE_REL / "artifacts/RESULT.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
GENERATED_RELS = (
    BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    BASE_REL / "artifacts/GRID_CELLS.tsv",
    BASE_REL / "artifacts/GRID_OCCURRENCES.tsv",
    BASE_REL / "artifacts/QUADRANT_FRAME_COUNTS.tsv",
    BASE_REL / "artifacts/FACTOR_MARGINALS.tsv",
    BASE_REL / "artifacts/LOCAL_ONE_BIT_EDGES.tsv",
    BASE_REL / "artifacts/LOCAL_EDGE_SUMMARY.tsv",
    BASE_REL / "artifacts/WRAPPER_TRIPLETS.tsv",
    BASE_REL / "artifacts/E_LENGTH_SERIES.tsv",
    BASE_REL / "artifacts/E_LENGTH_LOCAL_SERIES.tsv",
    BASE_REL / "artifacts/LOCAL_EXEMPLARS.tsv",
    BASE_REL / "artifacts/LOCAL_HERBAL_BINDINGS.tsv",
    BASE_REL / "artifacts/PRODUCTIVE_READER.tsv",
    BASE_REL / "artifacts/CONCRETE_LINE_READINGS.tsv",
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
    require("cells=48/48 events=829 stable=613 wrapper_triplets=22" in completed.stdout, "builder summary")
    after = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    require(before == after, "builder replay is byte-identical")

    result = json.loads((ROOT / RESULT_REL).read_text(encoding="utf-8"))
    require(result["schema"] == "GDT624_PRODUCTIVE_QUALITY_SHELL_GRID_RESULT_V1", "result schema")
    require(result["status"] == "COMPLETE_48_CELL_SURFACE_LATTICE__COMPOSITIONAL_QUALITY_CORE_WORKING_READER", "result status")
    claimed_hash = result.pop("content_sha256")
    require(canonical_hash(result) == claimed_hash, "canonical result hash")
    result["content_sha256"] = claimed_hash
    require(result["guard"]["safe_pages"] == 179, "179 safe pages")
    require(result["guard"]["safe_tokens"] == 32339, "32339 safe tokens")
    require(result["guard"]["manual_extra_pages"] == ["f31v"], "single visual-only extra page")
    require(result["guard"]["token_query"] == {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}, "token guard counts")
    require(result["guard"]["cross_query"] == {"selected": 4148, "skipped_forbidden": 98, "skipped_not_allowed": 1140}, "cross guard counts with visual extra")
    require(result["grammar"]["values"] == {"k": "HOT", "t": "COLD", "ch": "DRY", "sh": "MOIST"}, "V2 atom values")
    require(result["grammar"]["e"].startswith("FORWARD_BOUND_OR_ATTRIBUTIVE"), "e default is attributive/bound")
    require(result["grammar"]["d"].startswith("GRAMMATICAL_DY_BINDING"), "d default is grammatical binding")
    require("NOT_OPERATION" in result["grammar"]["d"], "d is not an operation")
    require(result["grid"] == {
        "possible_cells": 48, "observed_cells": 48, "triple_stable_cells": 48,
        "occurrences": 829, "it2a_occurrences": 837, "rf1b_occurrences": 670,
        "pages": 157, "loci": 679, "triple_stable_occurrences": 613,
        "wrapper_triplet_page_cases": 22,
    }, "exact grid summary")
    require(result["translation"] == {"complete_word_defaults": 48, "direct_herbal_part_bindings": 6, "rendered_lines": 15, "unknown_surfaces_are_preserved": True}, "translation summary")
    require(result["historical_binding_comparators"] == {"rows": 5, "primary_e_default": "FORWARD_BOUND_OR_ATTRIBUTIVE", "degree_rival": "LIVE", "operation_default": "REJECTED_FOR_GRID_WORDS"}, "historical comparator synthesis")
    for path, expected in result["inputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"input hash {path}")
    for path, expected in result["outputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"output hash {path}")
    require(set(result["outputs"]) == {str(path) for path in GENERATED_RELS if path != RESULT_REL}, "result binds all generated evidence")

    allowlist = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    require(len(allowlist) == 179, "allowlist length")
    require(sha256(ART / "PAGE_ALLOWLIST.tsv") == "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483", "allowlist canonical hash")
    require("f1r" not in {row["page"] for row in allowlist}, "allowlist excludes f1r")
    require(not any(row["page"].startswith("f84") for row in allowlist), "allowlist excludes f84 family")

    cells = read_tsv(ART / "GRID_CELLS.tsv")
    require(len(cells) == 48, "48 cell rows")
    require(len({row["cell_id"] for row in cells}) == 48, "48 unique cell ids")
    require(len({row["surface"] for row in cells}) == 48, "48 unique cell surfaces")
    require(all(int(row["occurrences"]) > 0 for row in cells), "every cell observed")
    require(all(int(row["triple_reading_stable_occurrences"]) > 0 for row in cells), "every cell has stable witness")
    require(sum(int(row["occurrences"]) for row in cells) == 829, "cell ZL total")
    require(sum(int(row["it2a_occurrences"]) for row in cells) == 837, "cell IT total")
    require(sum(int(row["rf1b_occurrences"]) for row in cells) == 670, "cell RF total")
    require(sum(int(row["triple_reading_stable_occurrences"]) for row in cells) == 613, "cell stable total")
    require(all("Operation" not in row["working_default_de"] for row in cells), "no cell translated as operation")

    occurrences = read_tsv(ART / "GRID_OCCURRENCES.tsv")
    require(len(occurrences) == 829, "829 occurrence rows")
    require(len({row["page"] for row in occurrences}) == 157, "157 grid pages")
    require(len({row["locus"] for row in occurrences}) == 679, "679 grid loci")
    require(sum(int(row["triple_reading_token_stable"]) for row in occurrences) == 613, "613 stable occurrence rows")
    require(not any(row["page"] == "f1r" or row["page"].startswith("f84") for row in occurrences), "occurrences exclude forbidden pages")

    frames = read_tsv(ART / "QUADRANT_FRAME_COUNTS.tsv")
    require(len(frames) == 12, "twelve wrapper-ending frames")
    expected_frames = {
        ("BARE", "y"): (31, 6, 27, 3), ("BARE", "ey"): (18, 6, 18, 8),
        ("BARE", "dy"): (17, 4, 12, 5), ("BARE", "edy"): (22, 5, 33, 10),
        ("o", "y"): (22, 10, 40, 4), ("o", "ey"): (29, 9, 26, 7),
        ("o", "dy"): (16, 1, 24, 3), ("o", "edy"): (23, 4, 34, 7),
        ("qo", "y"): (64, 9, 61, 5), ("qo", "ey"): (25, 8, 18, 2),
        ("qo", "dy"): (49, 4, 21, 3), ("qo", "edy"): (39, 10, 24, 3),
    }
    require({(row["wrapper"], row["ending_frame"]): tuple(int(row[key]) for key in ("KCH", "KSH", "TCH", "TSH")) for row in frames} == expected_frames, "exact 12-frame matrix")

    marginals = read_tsv(ART / "FACTOR_MARGINALS.tsv")
    require(len(marginals) == 15, "fifteen factor marginals")
    expected_stable = {("WRAPPER", "BARE"): 146, ("WRAPPER", "o"): 188, ("WRAPPER", "qo"): 279, ("THERMAL", "k"): 311, ("THERMAL", "t"): 302, ("MOISTURE", "ch"): 523, ("MOISTURE", "sh"): 90, ("E_BIT", "0"): 332, ("E_BIT", "1"): 281, ("D_BIT", "0"): 387, ("D_BIT", "1"): 226, ("ENDING", "y"): 234, ("ENDING", "ey"): 153, ("ENDING", "dy"): 98, ("ENDING", "edy"): 128}
    require({(row["dimension"], row["value"]): int(row["stable_min_occurrences"]) for row in marginals} == expected_stable, "factor stable marginals")

    edge_summary = read_tsv(ART / "LOCAL_EDGE_SUMMARY.tsv")
    expected_edges = {
        "THERMAL_K_T": (24, 10, 9, 21, 16), "MOISTURE_CH_SH": (24, 5, 3, 7, 4),
        "E_INSERTION": (24, 2, 2, 3, 2), "D_INSERTION": (24, 4, 1, 4, 1),
        "WRAPPER_BARE_O": (16, 3, 2, 5, 3), "WRAPPER_O_QO": (16, 4, 4, 5, 4),
    }
    require({row["axis"]: tuple(int(row[key]) for key in ("candidate_edge_types", "same_line_edge_types", "triple_stable_edge_types", "same_line_loci", "triple_stable_same_line_loci")) for row in edge_summary} == expected_edges, "local edge summary")
    edges = read_tsv(ART / "LOCAL_ONE_BIT_EDGES.tsv")
    require(len(edges) == 128, "128 one-bit candidate edges")
    require(sum(int(row["same_line_loci"]) for row in edges) == 45, "45 same-line edge witnesses")
    require(sum(int(row["triple_stable_same_line_loci"]) for row in edges) == 30, "30 stable same-line edge witnesses")

    triplets = read_tsv(ART / "WRAPPER_TRIPLETS.tsv")
    require(len(triplets) == 22, "22 wrapper triplets")
    require(len({row["core"] for row in triplets}) == 7, "seven triplet cores")
    require(len({row["page"] for row in triplets}) == 19, "nineteen triplet pages")

    length_rows = read_tsv(ART / "E_LENGTH_SERIES.tsv")
    require(len(length_rows) == 60, "sixty e-length cells")
    require(sum(int(row["occurrences"]) > 0 for row in length_rows) == 40, "forty occupied e-length cells")
    require(sum(int(row["triple_stable_occurrences"]) > 0 for row in length_rows) == 38, "thirty-eight stable e-length cells")
    require(all(int(row["occurrences"]) == 0 for row in length_rows if row["e_length"] == "4"), "e-length four null boundary")
    length_counts = {row["surface"]: int(row["occurrences"]) for row in length_rows}
    require([length_counts[item] for item in ("chdy", "chedy", "cheedy", "shdy", "shedy", "sheedy")] == [133, 470, 56, 40, 390, 77], "principal e-length counts")
    length_local = read_tsv(ART / "E_LENGTH_LOCAL_SERIES.tsv")
    require(len(length_local) == 83, "eighty-three local e-series contacts")

    exemplars = read_tsv(ART / "LOCAL_EXEMPLARS.tsv")
    require(len(exemplars) == 10, "ten local exemplars")
    require(next(row for row in exemplars if row["exemplar_id"] == "STATE_EDY_CH_SH")["all_forms_triple_token_stable"] == "1", "chedy-shedy stable pair")
    require(next(row for row in exemplars if row["exemplar_id"] == "FOUR_CORNERS_ONE_PAGE")["page"] == "f79r", "f79r has all four o-ey corners")
    bindings = read_tsv(ART / "LOCAL_HERBAL_BINDINGS.tsv")
    require(len(bindings) == 6, "six direct Herbal part bindings")
    require(sum(int(row["token_distance"]) == 1 for row in bindings) == 6, "all Herbal bindings adjacent")
    require(all(row["interpretation"].endswith("NOT_OPERATION") for row in bindings), "Herbal bindings are descriptors not operations")
    require({row["working_phrase_de"] for row in bindings} >= {"heiß-trockene Wurzel / Radix", "heiß-trockener Blüten- oder Fruchtstand", "Blüten- oder Fruchtstand: heiß-feucht"}, "concrete Herbal phrases")
    reader = read_tsv(ART / "PRODUCTIVE_READER.tsv")
    require(len(reader) == 48, "48 complete word defaults")
    require(all(row["working_reading_de"] != "NONE" for row in reader), "no grid word lacks a default")
    require(all("attributiv" in row["e_atom"] for row in reader if "+e1+" in row["composition"]), "e forms receive attributive default")
    readings = read_tsv(ART / "CONCRETE_LINE_READINGS.tsv")
    require(len(readings) == 15, "fifteen rendered lines")
    require(all("ANGLE_BRACKETS" in row["unknown_policy"] for row in readings), "unknown surfaces remain visible")
    historical = read_tsv(ART / "HISTORICAL_BINDING_COMPARATORS.tsv")
    require(len(historical) == 5, "five historical binding comparators")
    require({row["source_id"] for row in historical} == {"PAL1085_TABLE", "PAL1234_FORWARD", "WELLCOME542_ALLOMORPHY", "WELLCOME541_CODES", "CLM667_CODES"}, "historical source identities")
    require(next(row for row in historical if row["source_id"] == "WELLCOME542_ALLOMORPHY")["date"] == "Early_15th_century", "Wellcome 542 date")

    private_pattern = re.compile(
        "/" + "home/|/" + "tmp/|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|"
        "AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|"
        "password\\s*[=:]|api[_-]?key\\s*[=:]|secret\\s*[=:]",
        re.IGNORECASE,
    )
    for path in (BASE / "README.md", BASE / "METHOD.md", BASE / "REPORT.md", BASE / "experiment.json", BASE / "artifacts/README.md", ART / "HISTORICAL_BINDING_COMPARATORS.tsv", *[ROOT / item for item in GENERATED_RELS]):
        if path.is_file():
            require(not private_pattern.search(path.read_text(encoding="utf-8")), f"privacy scan {path.relative_to(ROOT)}")

    payload = {
        "schema": "GDT624_VALIDATION_V1",
        "experiment_id": "GDT624",
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
