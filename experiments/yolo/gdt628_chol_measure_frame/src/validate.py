#!/usr/bin/env python3
"""Validate and byte-replay GDT628."""

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
BASE_REL = Path("experiments/yolo/gdt628_chol_measure_frame")
BASE = ROOT / BASE_REL
ART = BASE / "artifacts"
RESULT_REL = BASE_REL / "artifacts/RESULT.json"
VALIDATION_REL = BASE_REL / "artifacts/VALIDATION.json"
G623_DICT = ROOT / "experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/WORKING_DICTIONARY_V2.tsv"
G624_READER = ROOT / "experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/PRODUCTIVE_READER.tsv"
G625_CTH = ROOT / "experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts/CTH_ROOT_FAMILY.tsv"
GENERATED_RELS = (
    BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    BASE_REL / "artifacts/OL_OR_QUALITY_CARRIER_MATRIX.tsv",
    BASE_REL / "artifacts/OL_OR_CARRIER_OCCURRENCES.tsv",
    BASE_REL / "artifacts/LOCAL_CARRIER_CONTRASTS.tsv",
    BASE_REL / "artifacts/LOCAL_CARRIER_CONTRAST_SUMMARY.tsv",
    BASE_REL / "artifacts/CHOL_OCCURRENCES.tsv",
    BASE_REL / "artifacts/CHOL_EXTENSION_PROFILE.tsv",
    BASE_REL / "artifacts/VALUE_REALIZATION_PATHS.tsv",
    BASE_REL / "artifacts/VALUE_REALIZATION_SUMMARY.tsv",
    BASE_REL / "artifacts/CHOL_VALUE_REALIZATIONS.tsv",
    BASE_REL / "artifacts/CHOL_D_TERMINAL_WITNESSES.tsv",
    BASE_REL / "artifacts/OL_QUALITY_D_VALUE_PHRASES.tsv",
    BASE_REL / "artifacts/OR_CARRIER_D_VALUE_PHRASES.tsv",
    BASE_REL / "artifacts/CHOL_ROLE_RANKING.tsv",
    BASE_REL / "artifacts/WORKING_DICTIONARY_V5.tsv",
    BASE_REL / "artifacts/CONCRETE_READINGS_V3.tsv",
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
        [sys.executable, str(BASE / "src/run.py")], cwd=ROOT,
        text=True, capture_output=True, check=False,
    )
    require(completed.returncode == 0, "builder exits zero")
    require(
        "lattice=48/54 tokens=2264 same_line=141 adjacent=43 chol=343 extensions=130 "
        "modes={'DIRECT_A_VALUE': 117, 'FUSED_D_VALUE': 15, 'SEPARATE_D_VALUE': 120} "
        "cholvalues=43 terminal=13 olD=80 orD=25" in completed.stdout,
        "builder summary",
    )
    after = {str(path): sha256(ROOT / path) for path in GENERATED_RELS}
    require(before == after, "builder replay is byte-identical")

    result = json.loads((ROOT / RESULT_REL).read_text(encoding="utf-8"))
    require(result["schema"] == "GDT628_CHOL_QUALITY_CARRIER_RESULT_V1", "result schema")
    require(result["status"] == "OL_QUALITY_CARRIER_LATTICE__CHOL_DRY_DEGREES_I_IV__D_CONTEXT_SPLIT", "result status")
    claimed_hash = result.pop("content_sha256")
    require(canonical_hash(result) == claimed_hash, "canonical result hash")
    result["content_sha256"] = claimed_hash
    require(result["guard"] == {
        "cross_query": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151},
        "f1r": "EXCLUDED_BY_ALLOWLIST", "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
        "new_image_pages": 0, "safe_cross_rows": 4137, "safe_pages": 179, "safe_token_rows": 32339,
        "token_query": {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940},
    }, "guarded source scope")
    require(result["carrier_lattice"] == {
        "adjacent_contrasts": 43,
        "contrast_type_counts": {
            "ENDING_OL_OR": 97, "MOISTURE_CH_SH": 29, "THERMAL_K_T": 3,
            "WRAPPER_BARE_O": 5, "WRAPPER_BARE_QO": 6, "WRAPPER_O_QO": 1,
        },
        "coreful_ol_occupied_cells": 23, "coreful_ol_registered_cells": 24,
        "local_contrasts": 141, "loci": 1544, "occupied_cells": 48,
        "occurrences": 2264, "ol_occupied_cells": 25, "ol_occurrences": 1402,
        "or_occupied_cells": 23, "or_occurrences": 862,
        "pages": 177, "registered_cells": 54, "stable_local_contrasts": 112,
        "stable_adjacent_contrasts": 38, "stable_occurrences": 1909,
    }, "carrier-lattice result summary")
    require(result["chol"] == {
        "exact_occurrences": 343, "exact_stable_occurrences": 303,
        "extension_class_occurrences": {
            "BOTH_OR_INTERNAL": 33, "EXACT": 343, "LEFT_EXTENSION": 209, "RIGHT_EXTENSION": 105,
        },
        "pages": 125, "position_counts": {"FIRST": 18, "LAST": 5, "MIDDLE": 320},
        "substring_occurrences": 690, "substring_types": 130,
        "working_default": "chol=ch+ol=trocken; nominal trockenes Gut/Material",
    }, "chol result summary")
    require(result["value_realization"] == {
        "all_carrier_mode_counts": {"DIRECT_A_VALUE": 117, "FUSED_D_VALUE": 15, "SEPARATE_D_VALUE": 120},
        "all_carrier_occurrences": 252,
        "chol_mode_counts": {"DIRECT_A_VALUE": 3, "FUSED_D_VALUE": 3, "SEPARATE_D_VALUE": 37},
        "chol_realizations": 43, "chol_stable_realizations": 35, "chol_terminal_separate": 13,
        "chol_terminal_context_classes": {"MULTI_CLAUSE_REQUIRED": 3, "QUALITY_ANCHORED": 4, "QUALITY_OR_DOSE": 6},
        "chol_value_counts": {"I": 2, "II": 4, "III": 35, "IV": 2},
        "ol_quality_separate_phrases": 80, "or_carrier_separate_phrases": 25,
    }, "value-realization result summary")
    require(result["manual_sources"] == {
        "concrete_readings": 19, "historical_syntax_comparators": 6,
        "inherited_visual_judgments": 8, "role_models": 5,
        "transcription_variant_concrete_readings": 5, "triple_exact_concrete_readings": 14,
    }, "manual source counts")
    for path, expected in result["inputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"input hash {path}")
    for path, expected in result["outputs"].items():
        require((ROOT / path).is_file() and sha256(ROOT / path) == expected, f"output hash {path}")
    require(set(result["outputs"]) == {str(path) for path in GENERATED_RELS if path != RESULT_REL}, "result binds every generated evidence file")

    allowlist = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    pages = {row["page"] for row in allowlist}
    require(len(allowlist) == 179 and len(pages) == 179, "179-page allow-list")
    require(sha256(ART / "PAGE_ALLOWLIST.tsv") == "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483", "canonical allow-list hash")
    require("f1r" not in pages, "allow-list excludes f1r")
    require(not any(page.startswith("f84") for page in pages), "allow-list excludes f84 family")

    inherited = {row["surface"]: row for row in read_tsv(G623_DICT)}
    require(inherited["k"]["default_meaning_de"] == "heiß", "inherited k hot")
    require(inherited["t"]["default_meaning_de"] == "kalt", "inherited t cold")
    require(inherited["ch"]["default_meaning_de"] == "trocken", "inherited ch dry")
    require(inherited["sh"]["default_meaning_de"] == "feucht", "inherited sh moist")
    productive = {row["surface"]: row for row in read_tsv(G624_READER)}
    require(productive["qokchy"]["composition"].startswith("qo+k+ch"), "inherited qok hot-dry composition")
    require(productive["qotshy"]["composition"].startswith("qo+t+sh"), "inherited qot cold-moist composition")
    cth_family = {row["surface"]: row for row in read_tsv(G625_CTH)}
    require(cth_family["cthar"]["root_default_de"] == "Blatt-/Krautteil-Familie", "inherited cthar part family")

    matrix = read_tsv(ART / "OL_OR_QUALITY_CARRIER_MATRIX.tsv")
    require(len(matrix) == 54, "54 registered carrier cells")
    require(sum(int(row["occupied"]) for row in matrix) == 48, "48 occupied carrier cells")
    require(sum(int(row["occurrences"]) for row in matrix) == 2264, "2264 carrier tokens")
    require(sum(int(row["triple_stable_occurrences"]) for row in matrix) == 1909, "1909 stable carrier tokens")
    cells = {row["surface"]: row for row in matrix}
    key_cell_counts = {
        "ol": (463, 376), "or": (321, 235), "chol": (343, 303), "chor": (190, 176),
        "shol": (163, 146), "shor": (91, 77), "kol": (30, 20), "tol": (34, 27),
        "kchol": (24, 19), "tchol": (16, 11), "kshol": (2, 2), "tshol": (6, 6),
        "qokchol": (15, 15), "qotchol": (13, 13),
    }
    require(all((int(cells[s]["occurrences"]), int(cells[s]["triple_stable_occurrences"])) == counts for s, counts in key_cell_counts.items()), "key carrier-cell counts")
    require(cells["chol"]["composition"] == "BARE+ch+ol", "chol composition")
    require(cells["chol"]["role"] == "QUALITY_STATE_CARRIER", "chol carrier role")
    require(cells["or"]["role"] == "BASE_NOMINAL_PART_CARRIER", "or base nominal carrier role")
    require(cells["chor"]["role"] == "PART_TERM__QUALITY_RIVAL", "chor remains part rival")

    occurrences = read_tsv(ART / "OL_OR_CARRIER_OCCURRENCES.tsv")
    require(len(occurrences) == 2264, "2264 occurrence rows")
    require(len({row["page"] for row in occurrences}) == 177, "carrier lattice on 177 pages")
    require(len({row["locus"] for row in occurrences}) == 1544, "carrier lattice at 1544 loci")
    require(sum(int(row["triple_reading_token_stable"]) for row in occurrences) == 1909, "occurrence stability total")
    require(not any(row["page"] == "f1r" or row["page"].startswith("f84") for row in occurrences), "occurrences exclude forbidden pages")

    contrasts = read_tsv(ART / "LOCAL_CARRIER_CONTRASTS.tsv")
    require(len(contrasts) == 141, "141 same-line carrier contrasts")
    require(sum(int(row["both_have_stable_token"]) for row in contrasts) == 112, "112 stable same-line contrasts")
    require(sum(int(row["adjacent"]) for row in contrasts) == 43, "43 adjacent carrier contrasts")
    require(sum(int(row["both_have_adjacent_stable_tokens"]) for row in contrasts) == 38, "38 stable adjacent carrier contrasts")
    require(Counter(row["contrast_type"] for row in contrasts) == Counter({
        "ENDING_OL_OR": 97, "MOISTURE_CH_SH": 29, "THERMAL_K_T": 3,
        "WRAPPER_BARE_O": 5, "WRAPPER_BARE_QO": 6, "WRAPPER_O_QO": 1,
    }), "contrast-type partition")
    contrast_summary = read_tsv(ART / "LOCAL_CARRIER_CONTRAST_SUMMARY.tsv")
    require(len(contrast_summary) == 18, "18 contrast summary rows")
    contrast_key = {(row["left_surface"], row["right_surface"]): row for row in contrast_summary}
    require((contrast_key["ol", "or"]["lines"], contrast_key["ol", "or"]["stable_lines"]) == ("53", "36"), "ol/or same-line contrast")
    require((contrast_key["chol", "chor"]["lines"], contrast_key["chol", "chor"]["stable_lines"]) == ("32", "30"), "chol/chor same-line contrast")
    require((contrast_key["chol", "shol"]["lines"], contrast_key["chol", "shol"]["stable_lines"]) == ("20", "17"), "chol/shol same-line contrast")
    require((contrast_key["chol", "chor"]["adjacent_lines"], contrast_key["chol", "chor"]["stable_adjacent_lines"]) == ("14", "14"), "chol/chor adjacent contrast")
    require((contrast_key["chol", "shol"]["adjacent_lines"], contrast_key["chol", "shol"]["stable_adjacent_lines"]) == ("8", "7"), "chol/shol adjacent contrast")

    chol = read_tsv(ART / "CHOL_OCCURRENCES.tsv")
    require(len(chol) == 343, "343 exact chol occurrences")
    require(len({row["page"] for row in chol}) == 125, "chol on 125 pages")
    require(sum(int(row["triple_reading_token_stable"]) for row in chol) == 303, "303 stable chol occurrences")
    require(Counter(row["position"] for row in chol) == Counter({"MIDDLE": 320, "FIRST": 18, "LAST": 5}), "chol line positions")
    require(all(row["composition"] == "ch+ol" for row in chol), "all exact chol rows segmented ch+ol")

    extensions = read_tsv(ART / "CHOL_EXTENSION_PROFILE.tsv")
    require(len(extensions) == 130, "130 chol-containing surface types")
    require(sum(int(row["occurrences"]) for row in extensions) == 690, "690 chol-containing tokens")
    require(Counter({kind: sum(int(row["occurrences"]) for row in extensions if row["extension_class"] == kind) for kind in {row["extension_class"] for row in extensions}}) == Counter({
        "EXACT": 343, "LEFT_EXTENSION": 209, "RIGHT_EXTENSION": 105, "BOTH_OR_INTERNAL": 33,
    }), "chol extension-class counts")
    extension_map = {row["surface"]: row for row in extensions}
    require(extension_map["cholaiin"]["working_parse"] == "CHOL_DIRECT_VALUE", "cholaiin direct-value parse")
    require(extension_map["choldaiin"]["working_parse"] == "CHOL_FUSED_D_VALUE", "choldaiin fused-value parse")
    require(extension_map["choly"]["working_parse"] == "CHOL_CLOSURE_FORM", "choly closure extension")

    value_grid = read_tsv(ART / "VALUE_REALIZATION_PATHS.tsv")
    require(len(value_grid) == 648, "54 by four by three realization grid")
    summary = {row["realization_mode"]: row for row in read_tsv(ART / "VALUE_REALIZATION_SUMMARY.tsv")}
    require({mode: (int(row["occurrences"]), int(row["triple_stable_occurrences"]), int(row["bases_with_occurrence"])) for mode, row in summary.items()} == {
        "DIRECT_A_VALUE": (117, 95, 15), "FUSED_D_VALUE": (15, 9, 5), "SEPARATE_D_VALUE": (120, 93, 23),
    }, "three realization-mode totals")
    require(all(row["registered_cells"] == "216" for row in summary.values()), "216 cells per realization mode")

    chol_values = read_tsv(ART / "CHOL_VALUE_REALIZATIONS.tsv")
    require(len(chol_values) == 43, "43 chol value realizations")
    require(Counter(row["realization_mode"] for row in chol_values) == Counter({"SEPARATE_D_VALUE": 37, "DIRECT_A_VALUE": 3, "FUSED_D_VALUE": 3}), "chol realization-mode counts")
    require(Counter(row["working_roman"] for row in chol_values) == Counter({"III": 35, "II": 4, "I": 2, "IV": 2}), "chol I-IV value counts")
    require(sum(int(row["all_expression_tokens_stable"]) for row in chol_values) == 35, "35 stable chol values")
    require({row["realization_mode"] for row in chol_values if row["working_roman"] == "III"} == {"DIRECT_A_VALUE", "FUSED_D_VALUE", "SEPARATE_D_VALUE"}, "degree III has all three spacing modes")

    terminal = read_tsv(ART / "CHOL_D_TERMINAL_WITNESSES.tsv")
    require(len(terminal) == 13, "thirteen terminal separate chol values")
    require(Counter(row["working_roman"] for row in terminal) == Counter({"III": 9, "II": 2, "I": 1, "IV": 1}), "terminal chol I-IV values")
    require(sum(int(row["all_expression_tokens_stable"]) for row in terminal) == 10, "ten stable terminal chol values")
    require(Counter(row["local_evidence_class"] for row in terminal) == Counter({"QUALITY_OR_DOSE": 6, "QUALITY_ANCHORED": 4, "MULTI_CLAUSE_REQUIRED": 3}), "terminal context-strength classes")
    require(all(row["surface_line"].split()[-2:] == ["chol", row["d_value_surface"]] for row in terminal), "terminal chol frame materialized")
    require(next(row for row in terminal if row["locus"] == "f2r.7")["d_value_surface"] == "dan", "f2r dry-I witness")
    require(next(row for row in terminal if row["locus"] == "f17r.11")["d_value_surface"] == "daiiin", "f17r dry-IV witness")
    require(next(row for row in terminal if row["locus"] == "f17r.11")["earlier_part_surfaces"] == "cthar", "f17r inherited part anchor")
    require(next(row for row in terminal if row["locus"] == "f18r.2")["all_expression_tokens_stable"] == "0", "f18r value-II instability exposed")

    ol_phrases = read_tsv(ART / "OL_QUALITY_D_VALUE_PHRASES.tsv")
    require(len(ol_phrases) == 80, "80 OL quality plus separate d-value phrases")
    require(Counter(row["working_roman"] for row in ol_phrases) == Counter({"III": 64, "II": 11, "IV": 3, "I": 2}), "OL phrase value counts")
    require(sum(int(row["all_expression_tokens_stable"]) for row in ol_phrases) == 64, "64 stable OL phrases")
    require(sum(int(row["phrase_line_end"]) for row in ol_phrases) == 28, "28 terminal OL phrases")
    require(all(row["contextual_role"] == "QUALITY_DEGREE" for row in ol_phrases), "OL d-values receive degree role")
    or_phrases = read_tsv(ART / "OR_CARRIER_D_VALUE_PHRASES.tsv")
    require(len(or_phrases) == 25, "25 OR carrier plus separate d-value phrases")
    require(Counter(row["working_roman"] for row in or_phrases) == Counter({"III": 24, "II": 1}), "OR phrase value counts")
    require(sum(int(row["all_expression_tokens_stable"]) for row in or_phrases) == 19, "19 stable OR phrases")
    require(next(row for row in or_phrases if row["locus"] == "f49v.38")["all_expression_tokens_stable"] == "0", "split f49v OR phrase is not stable")
    require(sum(int(row["phrase_line_end"]) for row in or_phrases) == 4, "four terminal OR phrases")
    require(all(row["contextual_role"] == "PART_AMOUNT_OR_QUALITY_DEGREE" for row in or_phrases), "OR d-values preserve amount-degree split")

    ranking = read_tsv(ART / "CHOL_ROLE_RANKING.tsv")
    require(len(ranking) == 5, "five explicit chol role models")
    require(ranking[0]["model"] == "CH_PLUS_OL_DRY_QUALITY_CARRIER" and ranking[0]["disposition"] == "PRIMARY_DEFAULT", "dry carrier model ranks first")
    require(ranking[1]["model"] == "DRY_MATERIAL_PLUS_PORTION" and ranking[1]["disposition"] == "LIVE_NOMINAL_RIVAL", "portion rival remains live")
    require(ranking[-1]["model"] == "CHOL_AS_SEPARATOR_OR_CLOSURE_ONLY" and ranking[-1]["disposition"] == "REJECTED_AS_DEFAULT", "separator-only model rejected")

    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V5.tsv")
    require(len(dictionary) == 28, "twenty-eight consolidated dictionary rows")
    entries = {row["entry"]: row for row in dictionary}
    require(entries["a"]["kind"] == "VALUE_SLOT_LINKER", "inherited value linker retained")
    require(entries["n/in/iin/iiin"]["working_meaning_de"] == "I/II/III/IV", "inherited I-IV tail retained")
    require(entries["dan/dain/daiin/daiiin"]["kind"] == "CONTEXTUAL_VALUE_SERIES", "free value series context split")
    require(entries["ol"]["kind"] == "QUALITY_STATE_MATERIAL_CARRIER", "ol carrier dictionary entry")
    require(entries["chol"]["composition"] == "ch+ol", "chol dictionary composition")
    require(entries["cholaiin"]["working_meaning_de"] == "trocken, Grad III", "cholaiin concrete dictionary reading")
    require(entries["choldaiin"]["working_meaning_de"] == "trocken, Grad III", "choldaiin concrete dictionary reading")
    require(entries["d"]["kind"] == "DETACHED_VALUE_HEAD", "d contextual value head")
    require(entries["chor"]["status"] == "INHERITED_CONTEXT_SPLIT", "chor remains context split")

    cases = read_tsv(ART / "CONCRETE_READINGS_V3.tsv")
    require(len(cases) == 19, "nineteen concrete readings")
    case_map = {row["case_id"]: row for row in cases}
    require(Counter(row["reader_status"] for row in cases) == Counter({"TRIPLE_EXACT": 14, "TRANSCRIPTION_VARIANT": 5}), "concrete reading transcription status")
    require(case_map["DRY_I"]["working_reading_de"] == "trocken, ersten Grades", "concrete dry I")
    require(case_map["DRY_IV"]["working_reading_de"] == "trocken, vierten Grades", "concrete dry IV")
    require(case_map["HOT_DRY_III"]["working_reading_de"] == "heiß-trocken, dritten Grades", "concrete hot-dry III")
    require(case_map["DRY_III_DIRECT"]["surface_expression"] == "cholaiin", "direct dry-III witness")
    require(case_map["DRY_III_FUSED"]["surface_expression"] == "choldaiin", "fused dry-III witness")
    require(case_map["F17_TWO_GRADES"]["working_reading_de"] == "vegetatives Gut: heiß Grad III; trocken Grad IV", "f17 two-grade working clause")
    require(case_map["F17_TWO_GRADES"]["reader_status"] == "TRIPLE_EXACT", "f17 clause exact in all readings")
    require(case_map["HOT_IV"]["reader_note"].endswith("IT2a"), "hot-IV transcription variant exposed")
    require(case_map["F51_MATCHED_III"]["reader_note"].endswith("RF1b"), "f51 transcription variant exposed")
    require(case_map["F45_OR_PART"]["reading_type"] == "OR_PART_VALUE_RIVAL", "f45 OR rival explicit")

    private_pattern = re.compile(
        "/" + "home/|/" + "tmp/|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|"
        "AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|"
        "password\\s*[=:]|api[_-]?key\\s*[=:]|secret\\s*[=:]", re.IGNORECASE,
    )
    scan_paths = (
        BASE / "README.md", BASE / "METHOD.md", BASE / "REPORT.md", BASE / "experiment.json",
        BASE / "artifacts/README.md", *[ROOT / path for path in GENERATED_RELS],
    )
    for path in scan_paths:
        require(path.is_file(), f"required file {path.relative_to(ROOT)}")
        require(not private_pattern.search(path.read_text(encoding="utf-8")), f"privacy scan {path.relative_to(ROOT)}")

    payload = {
        "schema": "GDT628_VALIDATION_V1", "experiment_id": "GDT628", "status": "PASS",
        "checks": checks, "check_count": len(checks), "result_sha256": sha256(ROOT / RESULT_REL),
    }
    (ROOT / VALIDATION_REL).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
