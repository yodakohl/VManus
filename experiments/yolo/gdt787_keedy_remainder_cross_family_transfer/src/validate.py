#!/usr/bin/env python3
"""Validate GDT787 locks, artifacts, semantic ceiling and byte replay."""

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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
EXP = ROOT / "experiments/yolo/gdt787_keedy_remainder_cross_family_transfer"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
RUN = SRC / "run.py"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
SPECS = SRC / "WHOLE_DEFAULT_SPECS.tsv"
RELATION_INTAKE = ROOT / "tools/relation_edge_intake.py"

GENERATED = (
    "GDT787_38_FAMILY_CENSUS.tsv",
    "GDT787_370_EXACT_OCCURRENCE_ATLAS.tsv",
    "GDT787_50_COMPLETE_PARADIGM.tsv",
    "GDT787_6_HOT_FORMAL_CONTRASTS.tsv",
    "GDT787_59_RAW_SEPARATED_SPANS.tsv",
    "GDT787_20_EXACT_SEPARATED_SPANS.tsv",
    "GDT787_5_FUSED_SPLIT_FAMILIES.tsv",
    "GDT787_27_STOLFI_BOUNDARY_SUMMARY.tsv",
    "GDT787_370_STOLFI_BOUNDARY_OCCURRENCES.tsv",
    "GDT787_9_FACTORIAL_MODEL.tsv",
    "GDT787_3_MODEL_SUMMARY.tsv",
    "GDT787_9_END_CLOSE_CONTRASTS.tsv",
    "GDT787_62_SANITIZED_AXIS_CONTRASTS.tsv",
    "GDT787_6_SANITIZED_AXIS_SUMMARY.tsv",
    "GDT787_38_WORKING_DICTIONARY.tsv",
    "GDT787_27_PRACTICAL_PASSAGES.tsv",
    "GDT787_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv",
    "GDT787_GUARDED_SOURCE_STATS.tsv",
    "GDT787_GDT388_SEPARATED_SPAN_PACKET.tsv",
    "GDT787_RELATION_EDGE_CROSSWALK.tsv",
    "RELATION_PACKET_INTAKE.json",
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


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(left - right) <= tolerance


def main() -> int:
    audit = Audit()

    locks = read_tsv(SOURCE_LOCK)
    audit.check(len(locks) == 19, "19 source locks")
    for row in locks:
        relative = Path(row["path"])
        audit.check(
            not relative.is_absolute() and ".." not in relative.parts,
            f"safe source-lock path {relative}",
        )
        audit.check((ROOT / relative).is_file(), f"locked input exists {relative}")
        audit.check(
            sha256(ROOT / relative) == row["expected_sha256"],
            f"locked input hash {relative}",
        )

    corpus = load_module("gdt787_corpus_validation", SRC / "corpus.py").compute(ROOT)
    model = load_module("gdt787_model_validation", SRC / "model.py").compute(ROOT)
    axes = load_module("gdt787_axis_validation", SRC / "axis_audit.py").compute(ROOT)
    run_module = load_module("gdt787_run_validation", RUN)
    audit.check(tuple(run_module.OUTPUT_NAMES) == GENERATED, "runner output registry")

    cd = corpus["diagnostics"]
    audit.check((cd["raw_family_rows"], cd["raw_family_occurrences"]) == (38, 601), "38 forms / 601 raw tokens")
    audit.check((cd["reader_exact_family_surfaces"], cd["reader_exact_family_occurrences"]) == (27, 370), "27 forms / 370 reader-exact tokens")
    audit.check((cd["reader_exact_nonbare_surfaces"], cd["reader_exact_nonbare_occurrences"]) == (26, 348), "26 nonbare forms / 348 exact tokens")
    audit.check((cd["paradigm_cells"], cd["paradigm_observed_exact_cells"]) == (50, 50), "complete 10 by 5 paradigm")
    audit.check((cd["paradigm_raw_occurrences"], cd["paradigm_reader_exact_occurrences"]) == (2208, 1664), "paradigm occurrence totals")
    audit.check((cd["raw_separated_x_keedy_spans"], cd["reader_exact_separated_x_keedy_spans"]) == (59, 20), "raw and exact separated spans")
    audit.check(cd["fused_and_split_left_types"] == 5, "five fused and separated left types")
    audit.check((cd["current_alternate_reader_split_candidates"], cd["current_alternate_split_candidates_reader_exact"]) == (4, 0), "four raw alternate-reader splits and zero exact")
    audit.check((cd["stolfi_fused_nonbare_occurrences"], cd["stolfi_split_nonbare_occurrences"], cd["stolfi_bare_matches"]) == (59, 1, 7), "Stolfi boundary totals")
    audit.check(cd["sealed_f84_rows_materialised"] == 0, "corpus materialized no f84/f84r")

    md = model["diagnostics"]
    audit.check(md["recommendation"] == "WHOLE_ONLY", "model selects whole-only")
    audit.check((md["primary_additive_beats_same_x"], md["primary_additive_beats_learned_whole"], md["primary_additive_beats_both"]) == (5, 4, 3), "primary win counts 5/4/3")
    audit.check(close(md["primary_additive_macro_similarity"], 0.677608041989992), "additive macro similarity")
    audit.check(close(md["primary_same_x_macro_similarity"], 0.7011328240773806), "same-X macro similarity")
    audit.check(close(md["primary_learned_whole_macro_similarity"], 0.6751929582501742), "learned-whole macro similarity")
    audit.check(md["additive_beats_adversarial_best"] == 2, "two adversarial-best wins")
    audit.check(md["reader_exact_keedy_targets_masked"] == 27 and md["gdt754_provenance_surfaces_masked"] == 172, "target and provenance masking")
    audit.check(md["forbidden_f84_or_f84r_materialized"] == 0, "model materialized no f84/f84r")

    axis_expected = {
        ("HOT", 1): (6, 0, 4, 0, 2, -0.03828122484368679, 0.96875),
        ("HOT", 3): (6, 0, 3, 0, 3, -0.02118985338637332, 0.96875),
        ("END", 1): (6, 3, 5, 0, 1, 0.12665172508083866, 0.09375),
        ("END", 3): (8, 1, 5, 0, 3, 0.22331966820772223, 0.1640625),
        ("CLOSE", 1): (2, 14, 2, 0, 0, 0.01329492266992267, 0.5),
        ("CLOSE", 3): (3, 13, 2, 0, 1, 0.023751147475276346, 0.75),
    }
    axis_rows = {(row["contrast"], row["radius"]): row for row in axes["summary_rows"]}
    audit.check(set(axis_rows) == set(axis_expected), "six sanitized axis summaries")
    for key, expected in axis_expected.items():
        row = axis_rows[key]
        actual = (
            row["informative_type_pairs"], row["na"], row["positive"],
            row["zero"], row["negative"], row["mean_directional_delta"],
            row["exact_two_sided_sign_flip_p"],
        )
        audit.check(actual[:5] == expected[:5], f"axis direction counts {key}")
        audit.check(close(float(actual[5]), expected[5]), f"axis mean {key}")
        audit.check(close(float(actual[6]), expected[6]), f"axis sign-flip {key}")
    audit.check(axes["diagnostics"]["decision"] == "NO_AXIS_EXPORT__END_BEST_WEAK_LEAD", "sanitized axis decision")
    audit.check(axes["diagnostics"]["forbidden_f84_or_f84r_materialized"] == 0, "axis audit materialized no f84/f84r")

    expected_counts = {
        "GDT787_38_FAMILY_CENSUS.tsv": 38,
        "GDT787_370_EXACT_OCCURRENCE_ATLAS.tsv": 370,
        "GDT787_50_COMPLETE_PARADIGM.tsv": 50,
        "GDT787_6_HOT_FORMAL_CONTRASTS.tsv": 6,
        "GDT787_59_RAW_SEPARATED_SPANS.tsv": 59,
        "GDT787_20_EXACT_SEPARATED_SPANS.tsv": 20,
        "GDT787_5_FUSED_SPLIT_FAMILIES.tsv": 5,
        "GDT787_27_STOLFI_BOUNDARY_SUMMARY.tsv": 27,
        "GDT787_370_STOLFI_BOUNDARY_OCCURRENCES.tsv": 370,
        "GDT787_9_FACTORIAL_MODEL.tsv": 9,
        "GDT787_3_MODEL_SUMMARY.tsv": 3,
        "GDT787_9_END_CLOSE_CONTRASTS.tsv": 9,
        "GDT787_62_SANITIZED_AXIS_CONTRASTS.tsv": 62,
        "GDT787_6_SANITIZED_AXIS_SUMMARY.tsv": 6,
        "GDT787_38_WORKING_DICTIONARY.tsv": 38,
        "GDT787_27_PRACTICAL_PASSAGES.tsv": 27,
        "GDT787_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv": 2,
        "GDT787_GUARDED_SOURCE_STATS.tsv": 4,
        "GDT787_GDT388_SEPARATED_SPAN_PACKET.tsv": 20,
        "GDT787_RELATION_EDGE_CROSSWALK.tsv": 20,
    }
    for name, count in expected_counts.items():
        rows = read_tsv(ART / name)
        audit.check(len(rows) == count, f"{name} row count")

    family = read_tsv(ART / "GDT787_38_FAMILY_CENSUS.tsv")
    audit.check(sum(int(row["raw_occurrences"]) for row in family) == 601, "family artifact raw total")
    audit.check(sum(int(row["reader_exact_occurrences"]) for row in family) == 370, "family artifact exact total")
    audit.check(all(row["component_export_credit"] == "0" for row in family), "family artifact no component export")

    exact = read_tsv(ART / "GDT787_370_EXACT_OCCURRENCE_ATLAS.tsv")
    audit.check(all(row["reader_exact"] == "1" for row in exact), "all exact atlas rows reader-exact")
    audit.check(not any(row["page"].startswith("f84") for row in exact), "exact atlas excludes f84/f84r")
    audit.check(len({row["surface"] for row in exact}) == 27, "exact atlas has 27 surfaces")

    paradigm = read_tsv(ART / "GDT787_50_COMPLETE_PARADIGM.tsv")
    audit.check(all(int(row["reader_exact_occurrences"]) > 0 for row in paradigm), "all 50 paradigm cells observed exact")
    audit.check(len({row["prefix"] for row in paradigm}) == 10 and len({row["tail"] for row in paradigm}) == 5, "paradigm dimensions")

    raw_spans = read_tsv(ART / "GDT787_59_RAW_SEPARATED_SPANS.tsv")
    exact_spans = read_tsv(ART / "GDT787_20_EXACT_SEPARATED_SPANS.tsv")
    audit.check(all(row["all_three_readers_preserve_pair"] == "1" for row in exact_spans), "all exact separated pairs preserved by three readers")
    audit.check(len({row["left_surface"] for row in raw_spans}) == 37 and len({row["left_surface"] for row in exact_spans}) == 18, "raw and exact separated left-type counts")
    fused_split = read_tsv(ART / "GDT787_5_FUSED_SPLIT_FAMILIES.tsv")
    audit.check({row["left_whole"] for row in fused_split} == {"al", "cheol", "chol", "ol", "sol"}, "five fused/split families")

    stolfi_occ = read_tsv(ART / "GDT787_370_STOLFI_BOUNDARY_OCCURRENCES.tsv")
    audit.check(Counter(row["boundary_status"] for row in stolfi_occ)["FUSED_WHOLE_AT_SAME_LOCUS"] == 59, "59 Stolfi fused nonbare occurrences")
    audit.check(sum(int(row["stolfi_split_left_keedy_count"]) for row in stolfi_occ) == 1, "one Stolfi split nonbare occurrence")

    factorial = read_tsv(ART / "GDT787_9_FACTORIAL_MODEL.tsv")
    audit.check({row["x"] for row in factorial if row["additive_beats_both"] == "1"} == {"cho", "l", "o"}, "three both-null wins are cho/l/o")
    audit.check(all(row["score_semantics"] == "JENSEN_SHANNON_SIMILARITY_NOT_PROBABILITY" for row in factorial), "factorial score semantics")

    specs = read_tsv(SPECS)
    dictionary = read_tsv(ART / "GDT787_38_WORKING_DICTIONARY.tsv")
    spec_by_surface = {row["surface"]: row for row in specs}
    dict_by_surface = {row["surface"]: row for row in dictionary}
    audit.check(set(dict_by_surface) == set(spec_by_surface), "dictionary covers all 38 specified surfaces")
    audit.check(all(row["preferred_working_default_de"] == spec_by_surface[row["surface"]]["default_de"] for row in dictionary), "dictionary defaults equal registered specs")
    audit.check(all(
        row["rival_1_de"]
        and row["rival_2_de"]
        and row["rival_2_mechanism_de"]
        and len({row["preferred_working_default_de"], row["rival_1_de"], row["rival_2_de"]}) == 3
        and row["rival_2_mechanism_de"] not in {row["preferred_working_default_de"], row["rival_1_de"], row["rival_2_de"]}
        and any(marker in row["rival_2_mechanism_de"].lower() for marker in ("ganzwort", "kompositionshypothese"))
        for row in dictionary
    ), "every display has two distinct semantic rivals and a distinct mechanism alternative")
    audit.check(all(row["positive_evidence_de"] and row["counterevidence_de"] for row in dictionary), "every display has evidence and counterevidence")
    audit.check(Counter(row["display_scope"] for row in dictionary) == Counter({"READER_EXACT_COMPLETE_WHOLE_ONLY": 27, "RAW_READER_WARNING_ONLY": 11}), "27 exact display cards / 11 warnings")
    audit.check(sum(int(row["reader_exact_occurrences"]) for row in dictionary) == 370, "dictionary exact occurrence total")
    audit.check(all(row["gdt787_new_renderer_license"] == "0" and row["portable_keedy_component_used"] == "0" for row in dictionary), "zero new renderer licences and component uses")
    audit.check(all(zeros(row) and row["replaceable"] == "1" for row in dictionary), "dictionary semantic ceiling")
    audit.check(dict_by_surface["keedy"]["preferred_working_default_de"] == "heißer Endzustand", "bare keedy short whole default")
    audit.check(all("HOT" in row["display_hypothesis_not_exportable"] and "END_STAGE" in row["display_hypothesis_not_exportable"] for row in dictionary), "shared HOT/END display prior visibly marked")
    default_text = "\n".join(row["preferred_working_default_de"].lower() for row in dictionary)
    audit.check(not any(word in default_text for word in ("holz", "wurzel", "samen", "saat", "abgeschlossen")), "retired automatic prose absent from defaults")
    audit.check(all(0 <= int(row["confidence_0_100_not_probability"]) <= 100 and row["confidence_basis"] == "EDITORIAL_EVIDENCE_WEIGHT_NOT_FORMULA_NOT_PROBABILITY" for row in dictionary), "confidence scale explicitly editorial")

    passages = read_tsv(ART / "GDT787_27_PRACTICAL_PASSAGES.tsv")
    audit.check({row["surface"] for row in passages} == {row["surface"] for row in dictionary if row["reader_exact_surface"] == "1"}, "one passage per exact display surface")
    audit.check(all(f"⟦{row['surface']} = {row['working_default_de']}⟧" in row["target_focused_line"] for row in passages), "passage focus displays complete whole")
    audit.check(all(zeros(row) and row["gdt787_new_renderer_license"] == row["portable_component_used"] == "0" for row in passages), "passage semantic ceiling")

    historical = read_tsv(ART / "GDT787_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv")
    audit.check({row["source_id"] for row in historical} == {"HSR008", "HSR010"}, "two period architecture controls")
    audit.check(all(zeros(row) and row["selects_keedy_identity"] == row["selects_keedy_segmentation"] == "0" for row in historical), "historical controls give zero Voynich identity credit")

    packet_path = ART / "GDT787_GDT388_SEPARATED_SPAN_PACKET.tsv"
    intake_module = load_module("gdt787_relation_validation", RELATION_INTAKE)
    intake = intake_module.validate_relation_edge_packet(packet_path)
    audit.check(intake["status"] == "VALID_ACQUISITION_NOT_SCORE_READY", "direct relation packet intake status")
    audit.check(intake["packet_rows"] == 20 and intake["eligible_edges"] == 0 and not intake["score_ready"] and not intake["errors"], "relation packet remains ineligible and error-free")
    committed_intake = json.loads((ART / "RELATION_PACKET_INTAKE.json").read_text(encoding="utf-8"))
    audit.check(committed_intake == intake, "committed relation intake equals executable intake")
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT, text=True, capture_output=True,
    )
    audit.check(completed.returncode == 0, "vmanus-exp check-edge-packet succeeds")
    cli_intake = json.loads(completed.stdout)
    audit.check(cli_intake == intake, "CLI relation intake equals direct intake")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(result["experiment_id"] == "GDT787" and result["status"].startswith("PARTIAL__38_RAW_FORMS__601_RAW"), "result identity and status")
    audit.check(result["model"]["recommendation"] == "WHOLE_ONLY" and result["adjudication"]["portable_keedy_remainder"] == "C0_INACTIVE__WHOLE_ONLY", "result records whole-only decision")
    audit.check(result["dictionary"] == {"raw_forms_with_nonempty_defaults": 38, "reader_exact_display_cards": 27, "raw_reader_warning_cards": 11, "new_renderer_licenses": 0, "portable_component_exports": 0, "shared_family_display_prior": "HOT|END_STAGE_C0_NOT_EXPORTABLE"}, "result dictionary policy")
    audit.check(result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == result["specific_substances"] == result["component_exports"] == 0, "result semantic ceiling")
    audit.check(result["new_pages"] == result["new_images"] == result["new_ocr"] == result["new_transcriptions"] == result["sealed_pages_accessed"] == 0, "result no new or sealed access")

    report = REPORT.read_text(encoding="utf-8")
    audit.check("WHOLE_ONLY" in report and "C0-Familienprior" in report, "report states whole-only and shared C0 display prior")
    audit.check("null neue\nRenderer-Lizenzen" in report and "nicht 38 unabhängig" in report, "report states zero new licences and no independent 38-fold evidence")
    audit.check("2/16" in report and "3/16" in report and "`NA`" in report, "report states informative CLOSE coverage")
    audit.check("Der nächste Rest ist `dal`" in report, "report names dal as next remainder")

    private_home = "/" + "home" + "/"
    key_marker = "BEGIN " + "PRIVATE KEY"
    for path in sorted(p for p in EXP.rglob("*") if p.is_file() and p != ART / "VALIDATION.json"):
        data = path.read_bytes()
        audit.check(private_home.encode() not in data and key_marker.encode() not in data, f"privacy markers absent {path.relative_to(EXP)}")

    with tempfile.TemporaryDirectory(prefix="gdt787-replay-") as directory:
        replay_artifacts = Path(directory) / "artifacts"
        completed = subprocess.run(
            [sys.executable, "-B", str(RUN), "--artifacts-dir", str(replay_artifacts)],
            cwd=ROOT, text=True, capture_output=True,
        )
        audit.check(completed.returncode == 0, "runner replay succeeds")
        if completed.returncode != 0:
            raise AssertionError(completed.stderr)
        for name in GENERATED:
            audit.check((replay_artifacts / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")

    validation = {
        "experiment_id": "GDT787",
        "status": "PASS",
        "checks": audit.checks,
        "messages": audit.messages,
        "source_locks": len(locks),
        "generated_files_replayed": len(GENERATED),
        "relation_packet_status": intake["status"],
        "claim_ceiling": (
            "C2 observed complete-word boundaries; C1 formal keedy family and "
            "at most inherited whole roles; C0 shared display prior and semantic "
            "hypotheses; zero new renderer licence, plaintext, identity or component."
        ),
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
