#!/usr/bin/env python3
"""Validate GDT785 artifacts, guarded provenance, ceiling and exact replay."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Mapping

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt785_sal_exact_whole_field_census"
SRC, ART = EXP / "src", EXP / "artifacts"
RUN = SRC / "run.py"
REPORT = EXP / "REPORT.md"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"

GENERATED = (
    "GDT785_33_EXACT_CONTEXT_ATLAS.tsv", "GDT785_5_POSITION_CONTROLS.tsv",
    "GDT785_EXACT_DIRECT_FRAME_CENSUS.tsv", "GDT785_13_STATE_QUANTITY_DIAGNOSTICS.tsv",
    "GDT785_23_SAL_STRING_FAMILY.tsv", "GDT785_12_TRIGRAM_ROOT_CONTROLS.tsv",
    "GDT785_8_CANDIDATE_SCORECARDS.tsv", "GDT785_5_HISTORICAL_ROLE_COMPARATORS.tsv",
    "GDT785_12_PRACTICAL_PASSAGES.tsv", "GDT785_2_WORKING_DICTIONARY.tsv",
    "GDT785_1_CHORCHOLSAL_BRIDGE.tsv", "GDT785_376_RENDERER.tsv",
    "GDT785_GDT388_REPEATED_FRAME_PACKET.tsv", "GDT785_RELATION_EDGE_CROSSWALK.tsv",
    "RELATION_PACKET_INTAKE.json", "RESULT.json", "README.md",
)
ZERO_FIELDS = ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.messages: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(message)
        self.messages.append(message)


def zeros(row: Mapping[str, str], fields=ZERO_FIELDS) -> bool:
    return all(row.get(field) == "0" for field in fields)


def main() -> int:
    audit = Audit()

    locks = read_tsv(SOURCE_LOCK)
    audit.check(len(locks) == 18, "18 source locks")
    for row in locks:
        relative = Path(row["path"])
        audit.check(not relative.is_absolute() and ".." not in relative.parts, f"safe relative lock {relative}")
        audit.check((ROOT / relative).is_file(), f"locked source exists {relative}")
        audit.check(sha256(ROOT / relative) == row["expected_sha256"], f"locked source hash {relative}")

    candidates_source = read_tsv(SRC / "CANDIDATE_ROLE_SPECS.tsv")
    final_source = read_tsv(SRC / "FINAL_SELECTION_SPEC.tsv")
    passage_source = read_tsv(SRC / "PASSAGE_RENDER_SPECS.tsv")
    historical_source = read_tsv(SRC / "HISTORICAL_ROLE_SPECS.tsv")
    audit.check(len(candidates_source) == 8 and len({row["candidate_id"] for row in candidates_source}) == 8, "eight unique candidate specs")
    audit.check(len(final_source) == 1 and final_source[0]["selected_candidate_id"] == "C01_DRUG_MATERIAL", "single selected drug/material spec")
    audit.check(zeros(final_source[0], ZERO_FIELDS + ("specific_substance_confirmed",)), "final source obeys claim ceiling")
    audit.check(len(passage_source) == 12 and len({row["locus"] for row in passage_source}) == 12, "twelve distinct passage specs")
    audit.check(len(historical_source) == 5 and all(row["spelling_credit"] == row["selects_voynich_identity"] == "0" for row in historical_source), "historical specs have zero identity/spelling credit")

    occurrences = read_tsv(ART / "GDT785_33_EXACT_CONTEXT_ATLAS.tsv")
    audit.check(len(occurrences) == 33, "33 exact sal contexts")
    audit.check(len({row["occurrence_id"] for row in occurrences}) == len({row["locus"] for row in occurrences}) == 33, "unique occurrence IDs and loci")
    audit.check(len({row["page"] for row in occurrences}) == 26 and len({row["physical_folio"] for row in occurrences}) == 23, "26 pages and 23 physical folios")
    audit.check(not any(row["page"].startswith("f84") or row["page"] == "f88r" for row in occurrences), "sealed and downstream target pages absent")
    audit.check(Counter(row["line_position"] for row in occurrences) == Counter({"FIRST": 7, "MIDDLE": 16, "LAST": 10}), "7/16/10 line positions")
    registers = Counter(f"{row['section']}|{row['language']}|{row['hand']}" for row in occurrences)
    audit.check(registers == Counter({"B|B|2": 12, "H|A|1": 7, "S|B|3": 6, "T|B|2": 4, "P|A|1": 3, "H|B|5": 1}), "six expected register cells")
    audit.check(sum(int(row["paragraph_start_line"]) for row in occurrences) == 4 and sum(int(row["paragraph_end_line"]) for row in occurrences) == 6, "paragraph-line profile 4/6")
    audit.check([row["locus"] for row in occurrences if row["sal_at_true_paragraph_start"] == "1"] == ["f75r.47", "f103v.12"], "two true paragraph starts")
    audit.check([row["locus"] for row in occurrences if row["sal_at_true_paragraph_end"] == "1"] == ["f79r.12"], "one true paragraph end")
    mean_position = sum(float(row["normalized_position"]) for row in occurrences) / 33
    audit.check(abs(mean_position - 0.5657877272727273) < 1e-6, "mean normalized position replay")
    dispatches = Counter(row["syntax_dispatch"] for row in occurrences)
    audit.check(dispatches == Counter({"GLOBAL_NOUN": 25, "RIGHT_VALUE_FIELD": 2, "RIGHT_MOIST_GERMAN_REORDER": 2, "LEFT_HEAT_FIELD": 2, "BILATERAL_DRY_VALUE_FIELD": 1, "RIGHT_AMOUNT_FIELD": 1}), "fixed noun with six syntax dispatch classes")
    for row in occurrences:
        ordinal = int(row["sal_ordinal"])
        tokens = row["written_line_eva"].split()
        audit.check(tokens[ordinal - 1] == "sal" and len(tokens) == int(row["line_token_count"]), f"target coordinate {row['occurrence_id']}")
        audit.check(row["fixed_working_default_de"] == "Droge", f"fixed Droge default {row['occurrence_id']}")
        audit.check(zeros(row), f"context ceiling {row['occurrence_id']}")

    controls = {row["control_id"]: row for row in read_tsv(ART / "GDT785_5_POSITION_CONTROLS.tsv")}
    audit.check(set(controls) == {"SAL", "ALL_EXACT", "FULL_FREQ_25_45", "GDT762_CLEAN_FREQ_25_45", "H2_EXACT"}, "five position controls")
    expected_controls = {
        "SAL": ("1", "33", "7", "16", "10", "0", "17", "0.515152", "1"),
        "ALL_EXACT": ("4816", "24090", "2874", "18270", "2704", "242", "5820", "0.241594", "NA"),
        "FULL_FREQ_25_45": ("76", "2576", "224", "2097", "238", "17", "479", "0.185947", "8"),
        "GDT762_CLEAN_FREQ_25_45": ("68", "2293", "218", "1836", "223", "16", "457", "0.199302", "8"),
        "H2_EXACT": ("23", "350", "177", "127", "46", "0", "223", "0.637143", "NA"),
    }
    for name, expected in expected_controls.items():
        row = controls[name]
        actual = tuple(row[field] for field in ("form_count", "exact_occurrences", "first", "middle", "last", "single", "line_boundary_occurrences", "line_boundary_rate", "sal_rank_by_boundary_share"))
        audit.check(actual == expected, f"position control {name}")
        audit.check(row["meaning_credit"] == row["component_export_credit"] == "0", f"position control zero semantic credit {name}")

    frames = read_tsv(ART / "GDT785_EXACT_DIRECT_FRAME_CENSUS.tsv")
    audit.check(len(frames) == 38, "38 unique reader-exact direct frames")
    repeats = {row["written_pair_eva"]: row for row in frames if row["repeated_frame"] == "1"}
    audit.check(set(repeats) == {"sal shol", "sal raiin"}, "only two repeated frames")
    audit.check(repeats["sal shol"]["reader_exact_pair_occurrences"] == "2" and repeats["sal shol"]["loci"] == "f78v.30|f89v1.17", "sal shol twice")
    audit.check(repeats["sal raiin"]["reader_exact_pair_occurrences"] == "2" and repeats["sal raiin"]["loci"] == "f76r.51|f82r.24", "sal raiin twice")
    audit.check(all(row["target_default_used_to_select_frame"] == row["confirmed_plaintext"] == row["component_export_credit"] == "0" for row in frames), "frame selection and claim ceiling")

    diagnostics = {row["metric"]: row for row in read_tsv(ART / "GDT785_13_STATE_QUANTITY_DIAGNOSTICS.tsv")}
    audit.check(len(diagnostics) == 13, "13 state/quantity diagnostics")
    expected_diagnostics = {"LEFT_DIRECT_MOIST": "0", "RIGHT_DIRECT_MOIST": "4", "LEFT_DIRECT_DRY": "0", "RIGHT_DIRECT_DRY": "0", "SAME_LINE_MOIST": "11", "SAME_LINE_DRY": "10", "GDT759_QUANTITY_PAIRS_TOTAL": "96", "GDT759_QUANTITY_PAIRS_WITH_SAL": "0", "EXACT_SAL_BARE_AIN_FAMILY": "0", "EXACT_SAL_RAIIN": "2", "GDT760_DIRECT_AMOUNT_CONTACTS": "1", "RAW_S_AL_SPLIT_CANDIDATES": "5", "EXACT_S_AL_SPLIT_CANDIDATES": "0"}
    audit.check({key: diagnostics[key]["value"] for key in expected_diagnostics} == expected_diagnostics, "state/quantity values")
    audit.check(all(row["selects_specific_substance"] == row["eva_letter_credit"] == row["component_export_credit"] == "0" for row in diagnostics.values()), "diagnostic claim ceiling")

    family = read_tsv(ART / "GDT785_23_SAL_STRING_FAMILY.tsv")
    audit.check(len(family) == 23 and len({row["surface"] for row in family}) == 23, "23 sal-string surfaces")
    audit.check(sum(int(row["reader_exact_occurrences"]) for row in family) == 58, "58 sal-string tokens")
    class_forms = Counter(row["sal_string_class"] for row in family)
    class_occurrences = Counter()
    for row in family:
        class_occurrences[row["sal_string_class"]] += int(row["reader_exact_occurrences"])
        audit.check(row["surface_meaning_assigned_from_sal"] == row["confirmed_component"] == row["component_export_credit"] == "0", f"family ceiling {row['surface']}")
    audit.check(class_forms == Counter({"PREFIX_CORE": 12, "SUFFIX_CORE": 6, "INTERNAL_STRING": 4, "STANDALONE": 1}), "sal family form classes")
    audit.check(class_occurrences == Counter({"STANDALONE": 33, "PREFIX_CORE": 14, "SUFFIX_CORE": 7, "INTERNAL_STRING": 4}), "sal family occurrence classes")
    audit.check(next(row for row in family if row["surface"] == "chorcholsal")["sal_core_status"] == "C0_STRING_ECHO_ONLY", "chorcholsal suffix remains C0 echo")

    roots = {row["root"]: row for row in read_tsv(ART / "GDT785_12_TRIGRAM_ROOT_CONTROLS.tsv")}
    audit.check(len(roots) == 12 and set(roots) == {"air", "cho", "dam", "kar", "lol", "lor", "ody", "sal", "sar", "sor", "tar", "tol"}, "twelve matched three-character roots")
    sal_root = roots["sal"]
    root_fields = ("all_superform_occurrences", "all_superform_types", "clean_prefix_occurrences", "clean_prefix_types", "clean_suffix_occurrences", "clean_suffix_types", "rank_superform_occurrences", "rank_superform_types", "rank_clean_prefix_occurrences", "rank_clean_prefix_types", "rank_clean_suffix_occurrences", "rank_clean_suffix_types")
    audit.check(tuple(sal_root[field] for field in root_fields) == ("25", "22", "13", "11", "2", "1", "11", "10", "5", "3", "11", "12"), "sal morphology ranks and counts")
    audit.check(sal_root["clean_suffix_surfaces"] == "osal", "only clean recurrent X+sal is osal")
    audit.check(all(row["semantic_credit"] == row["component_export_credit"] == "0" for row in roots.values()), "morphology controls have zero semantic export")

    candidates = read_tsv(ART / "GDT785_8_CANDIDATE_SCORECARDS.tsv")
    audit.check(len(candidates) == 8 and [row["score_rank"] for row in candidates] == [str(i) for i in range(1, 9)], "eight ranked candidates")
    audit.check([row["diagnostic_score"] for row in candidates] == ["18", "13", "13", "11", "8", "4", "4", "3"], "candidate diagnostic scores")
    audit.check(candidates[0]["candidate_id"] == "C01_DRUG_MATERIAL" and candidates[0]["one_word_default_de"] == "Droge" and candidates[0]["selected_working_default"] == "1", "Droge winner")
    salt = next(row for row in candidates if row["candidate_id"] == "C05_SALT")
    audit.check(salt["one_word_default_de"] == "Salz" and salt["eva_spelling_credit"] == salt["specific_substance_confirmed"] == "0", "salt retained without spelling or identity credit")
    audit.check(sum(int(row["selected_working_default"]) for row in candidates) == 1, "one candidate selected")
    audit.check(all(row["score_is_probability"] == row["confirmed_lexeme"] == row["specific_substance_confirmed"] == "0" for row in candidates), "scores are not probabilities and identify nothing")

    historical = read_tsv(ART / "GDT785_5_HISTORICAL_ROLE_COMPARATORS.tsv")
    audit.check(len(historical) == 5 and {row["source_id"] for row in historical} == {"HSR010", "HSR016", "HSR012", "HSR013"}, "five period comparators from four sources")
    audit.check(all(row["selects_voynich_identity"] == row["spelling_credit"] == row["voynich_identity_credit"] == row["component_export_credit"] == "0" for row in historical), "historical architecture-only ceiling")

    passages = read_tsv(ART / "GDT785_12_PRACTICAL_PASSAGES.tsv")
    audit.check(len(passages) == 12 and len({row["locus"] for row in passages}) == 12, "twelve practical passage checks")
    audit.check({row["focus_span_eva"] for row in passages} >= {"sal shol", "sal raiin", "sal araiin", "qokeol sal", "okey sal", "cheol sal dain"}, "diagnostic frames represented in passage deck")
    for row in passages:
        audit.check(row["fixed_sal_default_de"] == "Droge" and "Droge" in row["focus_render_de"] and "Droge" in row["full_exploratory_render_de"], f"single fixed passage default {row['passage_id']}")
        audit.check(row["focus_span_eva"] in row["written_line_eva"] and row["written_line_eva"].split()[int(row["sal_ordinal"]) - 1] == "sal", f"passage coordinate {row['passage_id']}")
        audit.check(row["render_status"] == "WORKING_DISPLAY_NOT_PLAINTEXT" and zeros(row), f"passage scope {row['passage_id']}")

    dictionary = {row["entry"]: row for row in read_tsv(ART / "GDT785_2_WORKING_DICTIONARY.tsv")}
    audit.check(set(dictionary) == {"sal", "chorcholsal"}, "two dictionary rows")
    audit.check(dictionary["sal"]["preferred_working_default_de"] == "Droge" and dictionary["sal"]["portable_role_de"] == "nominaler Arzneidrogen- oder Materialkopf", "sal dictionary default and role")
    audit.check(dictionary["sal"]["surface_confidence"] == "C2_COMPLETE_WHOLE" and dictionary["sal"]["role_confidence"] == "C1_WORKING_ROLE" and dictionary["sal"]["identity_confidence"] == "C0_REPLACEABLE_DISPLAY", "sal confidence ladder")
    audit.check(dictionary["chorcholsal"]["preferred_working_default_de"] == "trockene Blütendroge" and dictionary["chorcholsal"]["alternate_2_de"] == "trockenes Blütensalz", "long whole and salt rival retained")
    audit.check(all(zeros(row) and row["replaceable"] == "1" for row in dictionary.values()), "dictionary claim ceiling")

    bridge_rows = read_tsv(ART / "GDT785_1_CHORCHOLSAL_BRIDGE.tsv")
    audit.check(len(bridge_rows) == 1, "one chorcholsal bridge")
    bridge = bridge_rows[0]
    audit.check(bridge["parent_default_de"] == bridge["gdt785_default_de"] == "trockene Blütendroge" and bridge["display_changed"] == "0", "chorcholsal display unchanged")
    audit.check(bridge["target_removed_standalone_sal_occurrences"] == "33" and bridge["target_removed_sal_family_occurrences"] == "57", "downstream target removal")
    audit.check(bridge["sal_inside_target_status"] == "C0_NONEXPORTING_SUFFIX_ECHO" and bridge["suffix_direction_morphology"].startswith("WEAK"), "weak suffix direction explicit")
    audit.check(bridge["salt_rival_de"] == "trockenes Blütensalz" and zeros(bridge), "salt rival and bridge ceiling")

    parent_renderer = read_tsv(ROOT / "experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/artifacts/GDT784_376_RENDERER.tsv")
    renderer = read_tsv(ART / "GDT785_376_RENDERER.tsv")
    audit.check(len(parent_renderer) == len(renderer) == 376, "376 cumulative renderer rows")
    parent_fields = list(parent_renderer[0])
    for before, after in zip(parent_renderer, renderer):
        audit.check(all(after[field] == before[field] for field in parent_fields), f"parent renderer parity {after['target_occurrence_id']}")
        audit.check(after["gdt785_default_is_translation"] == after["gdt785_confirmed_lexeme"] == after["gdt785_confirmed_plaintext"] == after["gdt785_component_export_credit"] == "0", f"renderer ceiling {after['target_occurrence_id']}")
    audit.check(sum(int(row["gdt785_renderer_contextual"]) for row in renderer) == 270, "270 contextual renderer rows")
    audit.check(sum(1 - int(row["gdt785_renderer_contextual"]) for row in renderer) == 106, "106 fallback renderer rows")
    consumed = [token for row in renderer for token in ([] if row["gdt785_consumed_token_ids"] in {"", "NONE"} else row["gdt785_consumed_token_ids"].split("|"))]
    audit.check(len(consumed) == len(set(consumed)) == 230, "230 collision-free consumed token IDs")
    audit.check(sum(int(row["gdt785_display_changed"]) for row in renderer) == 0, "zero cumulative display changes")
    changed = [row for row in renderer if row["gdt785_branch"] == "SAL_ROLE_REINFORCES_EXISTING_WHOLE"]
    audit.check(len(changed) == 1 and changed[0]["locus"] == "f88r.22" and changed[0]["gdt785_default_de"] == "Ansatz: trockene Blütendroge", "one metadata-only cumulative target")

    packet = read_tsv(ART / "GDT785_GDT388_REPEATED_FRAME_PACKET.tsv")
    crosswalk = read_tsv(ART / "GDT785_RELATION_EDGE_CROSSWALK.tsv")
    audit.check(len(packet) == len(crosswalk) == 4 and {row["edge_id"] for row in packet} == {row["edge_id"] for row in crosswalk}, "four repeated-frame relation edges and crosswalk")
    audit.check(Counter(row["relation_type"] for row in packet) == Counter({"SAL_PRECEDES_RAIIN": 2, "SAL_PRECEDES_SHOL": 2}), "two relation types twice")
    audit.check(all(row["eligibility_status"] == "INELIGIBLE_EXPLORATORY_TEXT_RELATION" and row["formal_access_state"] == "SEALED_NOT_ACCESSED" for row in packet), "packet is explicitly exploratory and sealed")
    edge_check = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str(ART / "GDT785_GDT388_REPEATED_FRAME_PACKET.tsv")], cwd=ROOT, text=True, capture_output=True, check=True)
    audit.check("VALID_ACQUISITION_NOT_SCORE_READY" in edge_check.stdout, "executable relation packet intake")
    intake = json.loads((ART / "RELATION_PACKET_INTAKE.json").read_text(encoding="utf-8"))
    audit.check(intake["status"] == "VALID_ACQUISITION_NOT_SCORE_READY" and intake["packet_rows"] == 4 and intake["score_ready"] is False and intake["errors"] == [], "stored relation intake")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(result["experiment_id"] == "GDT785" and result["status"].startswith("PASS__37_RAW__33_EXACT_SAL"), "result identity and pass status")
    audit.check(result["sal"]["reader_exact"] == 33 and result["adjudication"]["practical_default_de"] == "Droge", "result sal outcome")
    audit.check(result["adjudication"]["salt_retained_rival"] is True and result["adjudication"]["salt_spelling_credit"] == 0, "result salt rival without spelling credit")
    audit.check(result["chorcholsal"]["display"] == "trockene Blütendroge" and result["chorcholsal"]["display_changed"] is False, "result long-whole continuity")
    audit.check(result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == result["specific_substances"] == result["component_exports"] == 0, "result claim ceiling")
    audit.check(result["new_pages"] == result["new_images"] == result["new_ocr"] == result["new_transcriptions"] == result["sealed_pages_accessed"] == 0, "no new or sealed source access")
    guard = result["inherited_guard"]
    audit.check(guard["allowed_pages"] == 179 and guard["tokens"] == {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}, "guarded token counts")
    audit.check(guard["cross"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151}, "guarded cross-reader counts")
    audit.check(guard["lines"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}, "guarded line counts")

    report_text = REPORT.read_text(encoding="utf-8")
    audit.check("`sal = Droge`" in report_text and "trockene Blütendroge" in report_text and "trockenes Blütensalz" in report_text, "report publishes selected default and retained rival")
    audit.check("not a deciphered plaintext lexeme" in report_text and "Nothing is freely split or" in report_text, "report states scope")

    private_home = "/" + "home" + "/"
    key_marker = "BEGIN " + "PRIVATE KEY"
    for path in sorted(p for p in EXP.rglob("*") if p.is_file() and "artifacts/VALIDATION.json" not in p.as_posix()):
        data = path.read_bytes()
        audit.check(private_home.encode() not in data and key_marker.encode() not in data, f"privacy markers absent {path.relative_to(EXP)}")

    with tempfile.TemporaryDirectory(prefix="gdt785-replay-") as directory:
        replay_root = Path(directory)
        replay_artifacts = replay_root / "artifacts"
        replay_report = replay_root / "REPORT.md"
        completed = subprocess.run([sys.executable, "-B", str(RUN), "--artifacts-dir", str(replay_artifacts), "--report-path", str(replay_report)], cwd=ROOT, text=True, capture_output=True)
        audit.check(completed.returncode == 0, "runner replay succeeds")
        for name in GENERATED:
            audit.check((replay_artifacts / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")
        audit.check(replay_report.read_bytes() == REPORT.read_bytes(), "byte replay REPORT.md")

    validation = {
        "experiment_id": "GDT785", "status": "PASS", "checks": audit.checks,
        "messages": audit.messages, "source_locks": len(locks), "generated_files_replayed": len(GENERATED) + 1,
        "claim_ceiling": "C2 sal whole, C1 nominal drug/material role, C0 replaceable Droge display and suffix echo; zero plaintext, specific substance, EVA value or component export.",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
