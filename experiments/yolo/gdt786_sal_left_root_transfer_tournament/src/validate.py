#!/usr/bin/env python3
"""Validate GDT786 source locks, artifacts, ceiling and byte replay."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
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
EXP = ROOT / "experiments/yolo/gdt786_sal_left_root_transfer_tournament"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
RUN = SRC / "run.py"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"

GENERATED = (
    "GDT786_14_TARGET_OCCURRENCE_ATLAS.tsv",
    "GDT786_29_SAME_REMAINDER_CONTROL_TYPES.tsv",
    "GDT786_10_PRIMARY_MODEL_SCORECARD.tsv",
    "GDT786_8_MODEL_SUMMARY.tsv",
    "GDT786_11_SENSITIVITY_SCORECARD.tsv",
    "GDT786_39_ROOT_RECOGNITION.tsv",
    "GDT786_2_REPEAT_COHERENCE.tsv",
    "GDT786_12_SPLIT_BOUNDARY_AUDIT.tsv",
    "GDT786_2_REVERSE_EXACT_CONTACTS.tsv",
    "GDT786_STOLFI_BOUNDARY_ATLAS.tsv",
    "GDT786_12_REMAINDER_EVIDENCE.tsv",
    "GDT786_12_WORKING_DICTIONARY.tsv",
    "GDT786_14_PRACTICAL_PASSAGES.tsv",
    "GDT786_4_HISTORICAL_COMPARATORS.tsv",
    "GDT786_1_CHORCHOLSAL_CORRECTION.tsv",
    "RESULT.json",
    "README.md",
)
ZERO_FIELDS = (
    "default_is_translation", "confirmed_lexeme", "confirmed_plaintext",
    "specific_substance_confirmed", "component_export_credit",
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


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        audit.check(not relative.is_absolute() and ".." not in relative.parts, f"safe lock path {relative}")
        audit.check((ROOT / relative).is_file(), f"locked input exists {relative}")
        audit.check(sha256(ROOT / relative) == row["expected_sha256"], f"locked input hash {relative}")

    target_specs = read_tsv(SRC / "TARGET_12_SPECS.tsv")
    passage_specs = read_tsv(SRC / "PASSAGE_14_SPECS.tsv")
    model_specs = read_tsv(SRC / "MODEL_SPECS.tsv")
    historical_specs = read_tsv(SRC / "HISTORICAL_ROLE_SPECS.tsv")
    audit.check((len(target_specs), len(passage_specs), len(model_specs), len(historical_specs)) == (12, 14, 8, 4), "registered deck sizes")
    audit.check(len({row["surface"] for row in target_specs}) == 12, "twelve unique target wholes")
    audit.check(Counter(row["historical_preference"] for row in passage_specs) == Counter({"LEARNED_WHOLE": 8, "DRUG_COMPOSITE": 3, "TIE": 3}), "manual historical preferences")
    audit.check(all(row["voynich_identity_credit"] == row["spelling_credit"] == "0" for row in historical_specs), "historical bridge has zero identity/spelling credit")

    geometry = load_module("gdt786_geometry_validation", SRC / "geometry.py").compute()
    qualitative = load_module("gdt786_qualitative_validation", SRC / "qualitative.py").compute(ROOT)
    remainder = load_module("gdt786_remainder_validation", SRC / "remainder_evidence.py").compute(ROOT)
    primary = geometry["primary_model_summary"]
    recognition = geometry["root_recognition_summary"]
    audit.check(geometry["recommendation"] == "RED_PRODUCTIVE_LEFT_CORE__YELLOW_FORMAL_STRING_FAMILY_ONLY", "independent geometry recommendation")
    audit.check((primary["types"], primary["scored_occurrences"]) == (10, 12), "ten primary types / twelve occurrences")
    audit.check(abs(primary["additive_macro_distance"] - 0.555076037598336) < 1e-15, "additive distance")
    audit.check(abs(primary["same_x_null_macro_distance"] - 0.5590798324189528) < 1e-15, "same-X distance")
    audit.check(primary["additive_wins_over_same_x_null"] == 5, "additive wins five of ten")
    audit.check(abs(primary["additive_vs_same_x_null_exact_sign_flip_p"] - 0.4443359375) < 1e-15, "exact sign-flip value")
    audit.check(all(value is False for value in geometry["green_gates"].values()), "all six productive-root gates fail")
    audit.check(recognition["sal"]["top_1"] == 2 and recognition["sal"]["top_2"] == 5, "sal inverse recognition")
    audit.check(recognition["controls"]["top_1"] == 17 and recognition["controls"]["top_2"] == 27, "control inverse recognition")
    audit.check([row["ascending_distance_rank"] for row in geometry["repeat_coherence"]["targets"]] == [51, 49], "poor salo/saly repeat coherence")
    audit.check(geometry["split_diagnostic"]["exact_sal_then_remainder"] == 0 and geometry["split_diagnostic"]["exact_remainder_then_sal"] == 2, "forward/reverse exact contacts")

    qsummary = qualitative["summary"]
    audit.check((qsummary["target_types"], qsummary["target_occurrences"], qsummary["target_pages"]) == (12, 14, 13), "qualitative target census")
    audit.check(qsummary["current_reader_fused_occurrences"] == 14, "all current reader target occurrences fused")
    audit.check(qsummary["raw_separated_sal_x_pairs"] == 1 and qsummary["reader_exact_separated_sal_x_pairs"] == 0, "one raw and zero exact forward splits")
    audit.check((qsummary["stolfi_same_locus_rows"], qsummary["stolfi_fused_same_locus"], qsummary["stolfi_alternate_same_locus"], qsummary["stolfi_sal_x_split_same_locus"]) == (7, 6, 1, 0), "Stolfi boundary census")
    audit.check(qsummary["forbidden_page_rows_materialized"] == 0, "no forbidden page materialized")
    audit.check(remainder["surface_count"] == 12 and remainder["compositional_candidate_count"] == 6, "independent remainder audit")
    remainder_qa = remainder["qa"]
    audit.check(
        all(value is True for key, value in remainder_qa.items() if key not in {"individual_eva_character_export", "confirmed_lexemes"})
        and remainder_qa["individual_eva_character_export"] is False
        and remainder_qa["confirmed_lexemes"] == 0,
        "remainder QA",
    )

    expected_counts = {
        "GDT786_14_TARGET_OCCURRENCE_ATLAS.tsv": 14,
        "GDT786_29_SAME_REMAINDER_CONTROL_TYPES.tsv": 29,
        "GDT786_10_PRIMARY_MODEL_SCORECARD.tsv": 10,
        "GDT786_8_MODEL_SUMMARY.tsv": 8,
        "GDT786_11_SENSITIVITY_SCORECARD.tsv": 11,
        "GDT786_39_ROOT_RECOGNITION.tsv": 39,
        "GDT786_2_REPEAT_COHERENCE.tsv": 2,
        "GDT786_12_SPLIT_BOUNDARY_AUDIT.tsv": 12,
        "GDT786_2_REVERSE_EXACT_CONTACTS.tsv": 2,
        "GDT786_STOLFI_BOUNDARY_ATLAS.tsv": 14,
        "GDT786_12_REMAINDER_EVIDENCE.tsv": 12,
        "GDT786_12_WORKING_DICTIONARY.tsv": 12,
        "GDT786_14_PRACTICAL_PASSAGES.tsv": 14,
        "GDT786_4_HISTORICAL_COMPARATORS.tsv": 4,
        "GDT786_1_CHORCHOLSAL_CORRECTION.tsv": 1,
    }
    for name, count in expected_counts.items():
        rows = read_tsv(ART / name)
        audit.check(len(rows) == count, f"{name} row count")

    target_rows = read_tsv(ART / "GDT786_14_TARGET_OCCURRENCE_ATLAS.tsv")
    audit.check(Counter(row["surface"] for row in target_rows) == Counter(row["surface"] for row in passage_specs), "target artifact exact surface census")
    audit.check(len({row["page"] for row in target_rows}) == 13 and len({row["physical_folio"] for row in target_rows}) == 11, "target pages and physical folios")
    audit.check(all(zeros(row) and row["reader_exact_target"] == "1" for row in target_rows), "target ceiling and exactness")

    model_rows = read_tsv(ART / "GDT786_8_MODEL_SUMMARY.tsv")
    models = {row["model_id"]: row for row in model_rows}
    audit.check(models["M01"]["decision"] == "NUMERIC_LEAD_NOT_ROBUST__NO_PORTABLE_TRANSFER", "additive decision")
    audit.check(models["M04"]["decision"] == "FORMAL_STRING_FAMILY_RETAINED", "formal family retained")
    audit.check(models["M08"]["decision"] == "SAME_FORMAL_FIT_AS_M01__ZERO_EXCLUSIVE_SALT_SIGNAL", "salt formal tie has no identity signal")
    audit.check(all(zeros(row) and row["selected_portable_model"] == "0" for row in model_rows), "model ceiling")

    split_rows = read_tsv(ART / "GDT786_12_SPLIT_BOUNDARY_AUDIT.tsv")
    audit.check(sum(int(row["raw_pair_occurrences"]) for row in split_rows) == 1, "one raw sal-X split")
    audit.check(sum(int(row["reader_exact_pair_occurrences"]) for row in split_rows) == 0, "zero reader-exact sal-X split")
    audit.check(next(row for row in split_rows if row["remainder"] == "ol")["raw_pair_coordinates"] == "f75v.15:1-2", "raw sal ol coordinate")
    stolfi = read_tsv(ART / "GDT786_STOLFI_BOUNDARY_ATLAS.tsv")
    audit.check(Counter(row["boundary_status"] for row in stolfi) == Counter({"NO_STOLFI_ROWS_FOR_PAGE": 4, "NO_SAME_LOCUS_ROW": 3, "FUSED_WHOLE_AT_SAME_LOCUS": 6, "ALTERNATE_READING_OR_OTHER_BOUNDARY": 1}), "Stolfi artifact status counts")
    alternative = next(row for row in stolfi if row["boundary_status"] == "ALTERNATE_READING_OR_OTHER_BOUNDARY")
    audit.check(alternative["surface"] == "salal" and "s,alal" in alternative["stolfi_raw_text"], "Stolfi salal alternative boundary")

    dictionary = read_tsv(ART / "GDT786_12_WORKING_DICTIONARY.tsv")
    by_entry = {row["entry"]: row for row in dictionary}
    expected_defaults = {
        "salal": "Drogenmaterial I", "salar": "Drogenanteil I",
        "saldal": "abgemessene Rohdroge", "saldam": "Pflanzendroge",
        "saldy": "Fertigdroge", "salf": "Drogenname",
        "salkeedy": "erhitzte Fertigdroge", "salo": "Arzneidroge",
        "salol": "Drogenzubereitung", "salshcthdy": "feuchte Fertigdroge",
        "saltar": "kalter Drogenanteil I", "saly": "Arzneidroge",
    }
    audit.check({entry: row["preferred_working_default_de"] for entry, row in by_entry.items()} == expected_defaults, "twelve concrete whole defaults")
    audit.check(all(zeros(row) and row["replaceable"] == "1" and row["portable_sal_root_used"] == row["portable_remainder_used"] == "0" for row in dictionary), "dictionary ceiling and no export")
    audit.check(sum(int(row["reader_exact_occurrences"]) for row in dictionary) == 14, "dictionary exact occurrence total")

    passages = read_tsv(ART / "GDT786_14_PRACTICAL_PASSAGES.tsv")
    audit.check(all(f"⟦{row['surface']} = {row['focus_display_de']}⟧" in row["target_focused_line"] for row in passages), "every passage displays its complete target whole")
    audit.check(all(zeros(row) and row["portable_component_used"] == "0" for row in passages), "passage ceiling")
    historical = read_tsv(ART / "GDT786_4_HISTORICAL_COMPARATORS.tsv")
    audit.check(all(zeros(row) and row["selects_voynich_mechanism"] == "0" for row in historical), "historical artifact ceiling")
    correction = read_tsv(ART / "GDT786_1_CHORCHOLSAL_CORRECTION.tsv")[0]
    audit.check(correction["gdt785_default_de"] == correction["gdt786_default_de"] == "trockene Blütendroge" and correction["display_changed"] == "0", "chorcholsal display continuity")
    audit.check(correction["gdt786_internal_sal_status"] == "C0_GLOSS_MEMORY_ONLY__NOT_SEMANTIC_EVIDENCE" and zeros(correction), "chorcholsal internal sal removed as evidence")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(result["experiment_id"] == "GDT786" and result["status"].startswith("PARTIAL__12_SAL_PREFIX_WHOLES"), "result identity and status")
    audit.check(result["target"] == {"complete_forms": 12, "reader_exact_occurrences": 14, "primary_forms": 10, "primary_occurrences": 12, "page_labels": 13, "physical_folios": 11}, "result target census")
    audit.check(result["adjudication"]["productive_sal_left_root"] == "C0_RETAINED_INACTIVE_HYPOTHESIS", "root assumption retained but inactive")
    audit.check(result["adjudication"]["formal_sal_left_family"] == "C1_RETAINED" and result["adjudication"]["portable_component_exports"] == 0, "formal family only")
    audit.check(result["adjudication"]["form_specific_composite_leads"] == ["saldal", "salkeedy", "saltar"], "three preferred form-specific composites")
    audit.check(result["adjudication"]["salt_preferred_contexts"] == 0, "salt wins zero contexts")
    audit.check(result["chorcholsal"]["display_changed"] is False and result["chorcholsal"]["internal_sal_evidence"] == "REMOVED_FROM_ACTIVE_JUSTIFICATION", "result chorcholsal correction")
    audit.check(result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == result["specific_substances"] == result["component_exports"] == 0, "result semantic ceiling")
    audit.check(result["new_pages"] == result["new_images"] == result["new_ocr"] == result["new_transcriptions"] == result["sealed_pages_accessed"] == 0, "no new or sealed source access")
    audit.check(result["relation_packet"].startswith("NOT_APPLICABLE"), "no diagram relation claim from word geometry")

    report = REPORT.read_text(encoding="utf-8")
    audit.check("a real family, but not yet a semantic root" in report and "C0 hypothesis" in report, "report states exploratory outcome")
    audit.check("`saldam` is simply **Pflanzendroge**" in report and "`salf` is **Drogenname**" in report, "report removes overcomplex pseudo-glosses")
    audit.check("first `keedy`, then `dal`, `ar` and" in report, "report names next route")

    private_home = "/" + "home" + "/"
    key_marker = "BEGIN " + "PRIVATE KEY"
    for path in sorted(p for p in EXP.rglob("*") if p.is_file() and p != ART / "VALIDATION.json"):
        data = path.read_bytes()
        audit.check(private_home.encode() not in data and key_marker.encode() not in data, f"privacy markers absent {path.relative_to(EXP)}")

    with tempfile.TemporaryDirectory(prefix="gdt786-replay-") as directory:
        replay_root = Path(directory)
        replay_artifacts, replay_report = replay_root / "artifacts", replay_root / "REPORT.md"
        completed = subprocess.run(
            [sys.executable, "-B", str(RUN), "--artifacts-dir", str(replay_artifacts), "--report-path", str(replay_report)],
            cwd=ROOT, text=True, capture_output=True,
        )
        audit.check(completed.returncode == 0, "runner replay succeeds")
        if completed.returncode != 0:
            raise AssertionError(completed.stderr)
        for name in GENERATED:
            audit.check((replay_artifacts / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")
        audit.check(replay_report.read_bytes() == REPORT.read_bytes(), "byte replay REPORT.md")

    validation = {
        "experiment_id": "GDT786", "status": "PASS", "checks": audit.checks,
        "messages": audit.messages, "source_locks": len(locks),
        "generated_files_replayed": len(GENERATED) + 1,
        "claim_ceiling": "C2 observed wholes; C1 formal sal family and form-specific whole roles; C0 replaceable displays; zero plaintext, substance identity, EVA value or component export.",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
