#!/usr/bin/env python3
"""Invariant and byte-replay validation for GDT753."""

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
BASE = Path("experiments/yolo/gdt753_qokeol_okeol_whole_role_census")
EXP = ROOT / BASE
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "PARTIAL__75_EXACT_TARGET_OCCURRENCES_40_PAGES__34_COMPLETE_FIELDS__"
    "Q_PROCESS_MATERIAL_MIDDLE_3_BASE_4__Q_PREPARATION_6_BASE_8__"
    "DIRECTIONAL_GATE_FAILS__TEN_MATCHED_PAIR_GATES_ZERO__"
    "GDT664_GDT666_COMPOSITIONAL_PROSE_DEMOTED__"
    "SHARED_HEAT_MIDDLE_HYPOTHESIS_RETAINED__WHOLE_PAIR_LEAD_RETAINED__"
    "ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "MATCHED_11_PAIR_CONTROL_DECK.tsv",
    "TARGET_AND_CONTROL_OCCURRENCE_FIELDS.tsv",
    "SURFACE_22_ROLE_CENSUS.tsv",
    "PAIR_11_ROLE_COMPARISON.tsv",
    "INHERITED_ROLE_PROVENANCE_AUDIT.tsv",
    "QOKEOL_OKEOL_75_OCCURRENCE_READER.tsv",
    "GDT753_QOKEOL_OKEOL_ROLE_READER.md",
    "RESULT.json",
)
EXPECTED_PAIRS = [
    ("TARGET_Q_PAIR", "qokeol", "okeol", "34", "41", "0.000000"),
    ("MATCHED_Q_PAIR", "qoteey", "oteey", "38", "90", "0.881403"),
    ("MATCHED_Q_PAIR", "qotedy", "otedy", "49", "75", "0.949739"),
    ("MATCHED_Q_PAIR", "qotain", "otain", "60", "88", "1.306493"),
    ("MATCHED_Q_PAIR", "qoaiin", "oaiin", "20", "17", "1.358123"),
    ("MATCHED_Q_PAIR", "qokair", "okair", "17", "17", "1.512274"),
    ("MATCHED_NONQ_PAIR", "ykaiin", "kaiin", "33", "44", "0.097980"),
    ("MATCHED_NONQ_PAIR", "okeedy", "keedy", "49", "22", "0.958850"),
    ("MATCHED_NONQ_PAIR", "ykeedy", "keedy", "19", "22", "1.161791"),
    ("MATCHED_NONQ_PAIR", "otchor", "tchor", "16", "17", "1.569433"),
    ("MATCHED_NONQ_PAIR", "otchol", "tchol", "24", "11", "1.589235"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
    check(manifest["experiment_id"] == "GDT753", "manifest id")
    check(manifest["slug"] == "qokeol_okeol_whole_role_census", "manifest slug")
    check(manifest["status"] == STATUS, "manifest status")
    check(manifest["dependencies"] == [
        "GDT664", "GDT666", "GDT734", "GDT744", "GDT751", "GDT752",
    ], "manifest dependencies")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed data")
    check(bool(manifest["question"]), "manifest question")
    check(bool(manifest["claim_ceiling"]), "manifest claim ceiling")
    check(manifest["validation"] == {
        "artifact": str(VALIDATION_REL), "status": "PASS",
    }, "validation contract")
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash {binding['path']}")

    pairs = read_tsv(art / GENERATED[0])
    occurrences = read_tsv(art / GENERATED[1])
    surfaces = read_tsv(art / GENERATED[2])
    comparisons = read_tsv(art / GENERATED[3])
    provenance = read_tsv(art / GENERATED[4])
    reader_rows = read_tsv(art / GENERATED[5])
    check(len(pairs) == 11, "eleven pairs")
    check(len(occurrences) == 803, "803 occurrence fields")
    check(len(surfaces) == 22, "22 surface rows")
    check(len(comparisons) == 11, "eleven comparisons")
    check(len(provenance) == 2, "two provenance rows")
    check(len(reader_rows) == 75, "75 target reader rows")
    check(len({row["gdt753_occurrence_id"] for row in occurrences}) == 803, "unique occurrence ids")
    check(len({row["gdt753_reader_id"] for row in reader_rows}) == 75, "unique reader ids")

    observed_pairs = [
        (
            row["comparison_group"], row["prefix_surface"], row["base_surface"],
            row["prefix_reader_exact_occurrences"], row["base_reader_exact_occurrences"],
            row["pre_outcome_match_cost"],
        )
        for row in pairs
    ]
    check(observed_pairs == EXPECTED_PAIRS, "fixed pair deck")
    check(all(row["matching_used_position_semantics_or_role_outcome"] == "0" for row in pairs), "outcome-free matching")
    check(all(row["literal_identity"] == "OPEN" for row in pairs), "pair literal open")
    check(all(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0" for row in pairs), "pair no lexeme or component")

    check(Counter(row["comparison_group"] for row in occurrences) == Counter({
        "TARGET_Q_PAIR": 75,
        "MATCHED_Q_PAIR": 471,
        "MATCHED_NONQ_PAIR": 257,
    }), "occurrence group counts")
    check(sum(row["boundary_complete"] == "1" for row in occurrences) == 393, "393 complete fields")
    for row in occurrences:
        occurrence_id = row["gdt753_occurrence_id"]
        check(not row["page"].startswith("f84"), f"sealed page absent {occurrence_id}")
        words = row["written_line_eva"].split()
        ordinal = int(row["token_ordinal"])
        check(words[ordinal - 1] == row["surface"], f"surface coordinate {occurrence_id}")
        check(int(row["line_token_count"]) == len(words), f"line length {occurrence_id}")
        complete = row["boundary_complete"] == "1"
        expected_complete = (
            not row["left_boundary_reason"].startswith("RADIUS5")
            and not row["right_boundary_reason"].startswith("RADIUS5")
        )
        check(complete == expected_complete, f"field completeness {occurrence_id}")
        if row["anchor_surfaces"] != "NONE":
            anchors = set(row["anchor_surfaces"].split("|"))
            check(row["surface"] not in anchors and row["paired_surface"] not in anchors, f"pair excluded as anchor {occurrence_id}")
        for field in (
            "process_or_material_middle_support", "preparation_support",
            "quality_stage_support", "process_support", "material_support",
            "middle_stage_support",
        ):
            check(row[field] == "0" or complete, f"complete-only role {occurrence_id} {field}")
        check(row["literal_identity"] == "OPEN", f"occurrence literal open {occurrence_id}")
        check(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0", f"occurrence no export {occurrence_id}")

    target_occurrences = [row for row in occurrences if row["comparison_group"] == "TARGET_Q_PAIR"]
    check(Counter(row["surface"] for row in target_occurrences) == Counter({
        "qokeol": 34, "okeol": 41,
    }), "target 34 41")
    check(len({row["page"] for row in target_occurrences}) == 40, "target 40 pages")
    check(sum(row["boundary_complete"] == "1" for row in target_occurrences) == 34, "target 34 complete")
    check(Counter((row["pair_side"], row["boundary_complete"]) for row in target_occurrences) == Counter({
        ("PREFIX", "1"): 15, ("PREFIX", "0"): 19,
        ("BASE", "1"): 19, ("BASE", "0"): 22,
    }), "target complete by side")
    check({row["current_inherited_semantic_value_de_not_used_as_field_anchor"] for row in target_occurrences if row["surface"] == "qokeol"} == {"erhitze den Drogenstoff bis zur Mittelstufe"}, "q old prose exact")
    check({row["current_inherited_semantic_value_de_not_used_as_field_anchor"] for row in target_occurrences if row["surface"] == "okeol"} == {"Grundansatz bis zur mittleren Heizstufe erwärmt"}, "base old prose exact")

    surface_map = {(row["gdt753_pair_id"], row["pair_side"]): row for row in surfaces}
    q_surface = surface_map[("G753-P01", "PREFIX")]
    base_surface = surface_map[("G753-P01", "BASE")]
    check(tuple(q_surface[field] for field in (
        "reader_exact_occurrences", "reader_exact_pages", "complete_fields",
        "process_or_material_middle_support_fields", "process_or_material_middle_support_pages",
        "preparation_support_fields", "preparation_support_pages",
        "process_or_material_middle_rate", "preparation_rate",
    )) == ("34", "24", "15", "3", "2", "6", "6", "0.200000", "0.400000"), "q target census")
    check(tuple(base_surface[field] for field in (
        "reader_exact_occurrences", "reader_exact_pages", "complete_fields",
        "process_or_material_middle_support_fields", "process_or_material_middle_support_pages",
        "preparation_support_fields", "preparation_support_pages",
        "process_or_material_middle_rate", "preparation_rate",
    )) == ("41", "24", "19", "4", "4", "8", "8", "0.210526", "0.421053"), "base target census")

    target_comparison = next(row for row in comparisons if row["comparison_group"] == "TARGET_Q_PAIR")
    check(target_comparison["process_material_middle_rate_delta_prefix_minus_base"] == "-0.010526", "target process delta")
    check(target_comparison["preparation_rate_delta_base_minus_prefix"] == "0.021053", "target preparation delta")
    check(target_comparison["cross_page_directional_role_gate"] == "0", "target gate fails")
    check(sum(int(row["cross_page_directional_role_gate"]) for row in comparisons) == 0, "all eleven gates zero")
    for row in comparisons + surfaces:
        check(row["literal_identity"] == "OPEN", f"summary literal open {row.get('gdt753_pair_id', 'surface')}")
        check(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0", "summary no export")

    provenance_map = {row["surface"]: row for row in provenance}
    check(set(provenance_map) == {"qokeol", "okeol"}, "provenance surfaces")
    check(provenance_map["qokeol"]["source_experiment"] == "GDT666", "q source GDT666")
    check(provenance_map["qokeol"]["source_decision_id"] == "G666-D149", "q decision id")
    check(provenance_map["qokeol"]["source_composition"] == "QO_COMMAND+K_HOT+E_MIDDLE+OL_MATERIAL", "q source composition")
    check(provenance_map["okeol"]["source_experiment"] == "GDT664", "base source GDT664")
    check(provenance_map["okeol"]["source_decision_id"] == "G664-D030", "base decision id")
    check(provenance_map["okeol"]["source_composition"] == "O_PREP+K_HOT+E_MIDDLE+OL_BASE", "base source composition")
    for row in provenance:
        check(row["source_card_type"] == "PRODUCTIVE_COMPOUND", f"source composed {row['surface']}")
        check(row["provenance_finding"] == "CONCRETE_PROSE_DERIVED_FROM_ANALYST_COMPONENT_COMPOSITION", f"provenance finding {row['surface']}")
        check(row["current_spoken_disposition"] == "DEMOTE_LITERAL_COMMAND_PATIENT_AND_PREPARATION_ROLE", f"demotion {row['surface']}")
        check(row["current_working_whole_default_de"] == "Wärme-/Mittelstufenfeld; genaue Funktion und Träger offen", f"working default {row['surface']}")
        check(row["whole_pair_relation"] == "RETAIN_COMPLETE_FORM_PAIR_LEAD", f"pair retained {row['surface']}")
        check(row["independent_directional_whole_role_gate"] == "0", f"provenance gate zero {row['surface']}")
        check(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0", f"provenance no export {row['surface']}")

    check(Counter(row["role_evidence_decision"] for row in reader_rows) == Counter({
        "CENSORED_FIELD_NO_ROLE_CREDIT": 41,
        "PREPARATION_CONTEXT": 11,
        "COMPLETE_OPEN_CONTEXT": 11,
        "PROCESS_MATERIAL_MIDDLE_CONTEXT": 7,
        "OTHER_ANCHORED_CONTEXT": 5,
    }), "reader decision counts")
    check(all(row["old_concrete_render_disposition"] == "DEMOTED_TO_BACKGROUND_HYPOTHESIS" for row in reader_rows), "all old renders demoted")
    check(all(row["current_working_whole_default_de"] == "Wärme-/Mittelstufenfeld; genaue Funktion und Träger offen" for row in reader_rows), "all reader defaults corrected")
    check(all(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0" for row in reader_rows), "reader no export")

    reader = (art / GENERATED[6]).read_text(encoding="utf-8")
    check("GDT666 `PRODUCTIVE_COMPOUND`" in reader, "reader q provenance")
    check("GDT664 `PRODUCTIVE_COMPOUND`" in reader, "reader base provenance")
    check("Wärme-/Mittelstufenfeld; genaue Funktion und Träger offen" in reader, "reader corrected default")
    check("no value is exported to EVA `q`, `o`, `k`, `e`, `ol`" in reader, "reader no component export")

    result = json.loads((art / GENERATED[7]).read_text(encoding="utf-8"))
    check(result["schema"] == "GDT753_RESULT_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"] == {
        "matched_nonq_pairs": 5,
        "matched_q_pairs": 5,
        "target_base_exact_occurrences": 41,
        "target_combined_pages": 40,
        "target_complete_fields": 34,
        "target_prefix_exact_occurrences": 34,
        "target_total_exact_occurrences": 75,
        "total_occurrence_fields": 803,
        "total_pair_deck": 11,
    }, "result scope")
    check(result["control_gate_counts"] == {
        "matched_nonq_directional_gates": 0,
        "matched_q_directional_gates": 0,
    }, "control gate counts")
    check(result["renderer_correction"] == {
        "complete_form_pair_lead_retained": 1,
        "current_working_default_both": "Wärme-/Mittelstufenfeld; genaue Funktion und Träger offen",
        "old_okeol_literal_prose_active": 0,
        "old_qokeol_literal_prose_active": 0,
        "shared_heat_middle_background_hypothesis_retained": 1,
    }, "result renderer correction")
    check(result["guard"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}, "guard exact")
    check(result["claim_boundary"] == {
        "confirmed_lexemes": 0,
        "f84_accessed": False,
        "f84r_accessed": False,
        "literal_process_or_preparation_words": 0,
        "new_pages": 0,
        "plaintext_clauses": 0,
        "q_component_export_credit": 0,
    }, "claim boundary")

    for binding in manifest["outputs"]:
        if binding["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / binding["path"]
        check(path.is_file(), f"output exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"output hash {binding['path']}")

    with tempfile.TemporaryDirectory(prefix=".gdt753_replay_", dir=EXP) as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)],
            cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay return")
        for name in GENERATED:
            check((replay / name).is_file(), f"replay exists {name}")
            check((replay / name).read_bytes() == (art / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT753_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": result["scope"],
        "target_role_result": result["target_role_result"],
        "renderer_correction": result["renderer_correction"],
        "claim_ceiling": (
            "Complete-form occurrence fields and provenance correction only. "
            "The shared heat/middle-stage reading remains a working hypothesis. "
            "No character, prefix, morpheme, sound, abbreviation, substring, "
            "confirmed lexeme, literal command, patient, preparation, ingredient, "
            "plant, disease, cure, person, vessel, unit, plaintext, new page, "
            "image, transcription, f84 or f84r."
        ),
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
