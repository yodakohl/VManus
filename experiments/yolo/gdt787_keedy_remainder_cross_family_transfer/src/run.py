#!/usr/bin/env python3
"""Build GDT787's guarded keedy cross-family transfer tournament."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Iterable, Mapping, Sequence

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
SRC, ART = EXP / "src", EXP / "artifacts"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
WHOLE_SPECS = SRC / "WHOLE_DEFAULT_SPECS.tsv"
CORPUS_MODULE = SRC / "corpus.py"
MODEL_MODULE = SRC / "model.py"
AXIS_MODULE = SRC / "axis_audit.py"
G734_DICTIONARY = ROOT / (
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/"
    "V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
)
G786_DICTIONARY = ROOT / (
    "experiments/yolo/gdt786_sal_left_root_transfer_tournament/artifacts/"
    "GDT786_12_WORKING_DICTIONARY.tsv"
)
G735_ARCHITECTURE = ROOT / (
    "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/"
    "HISTORICAL_SOURCE_ARCHITECTURE_MATRIX.tsv"
)
RELATION_INTAKE = ROOT / "tools/relation_edge_intake.py"

STATUS = (
    "PARTIAL__38_RAW_FORMS__601_RAW__27_EXACT_FORMS__370_EXACT__"
    "50_COMPLETE_PARADIGM_CELLS__9_FACTORIAL_ROWS__"
    "ADDITIVE_BEATS_X_5_OF9__WHOLE_4_OF9__BOTH_3_OF9__"
    "WHOLE_ONLY__END_WEAK__CLOSE_REJECTED__38_DEFAULTS__"
    "ZERO_COMPONENT_EXPORT__ZERO_NEW_RENDERER_LICENSE"
)

OUTPUT_NAMES = (
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

EDGE_COLUMNS = (
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
    "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
    "relation_type", "direction_basis", "ownership_basis",
    "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
    "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer",
    "relation_reviewer", "relation_confidence", "ambiguity_state",
    "formal_access_state", "fold_assignment", "eligibility_status",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _text(value: object) -> object:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return f"{value:.12f}"
    if value is None:
        return "NA"
    return value


def write_tsv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str] | None = None,
) -> None:
    material = list(rows)
    if not material:
        raise AssertionError(f"empty output: {path.name}")
    names = list(fields or ())
    if not names:
        for row in material:
            names.extend(field for field in row if field not in names)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in material:
            writer.writerow({name: _text(row.get(name, "")) for name in names})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


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


def verify_locks() -> tuple[int, str]:
    rows = read_tsv(SOURCE_LOCK)
    if len(rows) != 19:
        raise AssertionError(f"expected 19 source locks, got {len(rows)}")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise AssertionError(f"unsafe source path: {relative}")
        source = ROOT / relative
        if not source.is_file() or sha256(source) != row["expected_sha256"]:
            raise AssertionError(f"source changed: {relative}")
    return len(rows), sha256(SOURCE_LOCK)


def zero_ceiling(row: dict[str, object]) -> dict[str, object]:
    row.update({
        "default_is_translation": 0,
        "confirmed_lexeme": 0,
        "confirmed_plaintext": 0,
        "specific_substance_confirmed": 0,
        "component_export_credit": 0,
    })
    return row


def _integer(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1


def build_dictionary(
    family_rows: list[dict[str, object]], specs: list[dict[str, str]],
) -> list[dict[str, object]]:
    family = {str(row["surface"]): row for row in family_rows}
    if set(family) != {row["surface"] for row in specs}:
        raise AssertionError("whole specifications do not cover exact raw family")

    prior_rows: dict[str, list[dict[str, str]]] = {}
    for row in read_tsv(G734_DICTIONARY):
        prior_rows.setdefault(row["surface"], []).append(row)
    prior: dict[str, dict[str, str]] = {}
    for surface, rows in prior_rows.items():
        prior[surface] = max(
            rows,
            key=lambda row: (
                _integer(row["gdt734_exact_whole_default_allowed"]),
                _integer(row["working_model_score_0_100_not_probability"]),
                _integer(row["occurrence_count"]),
                row["reading_id"],
            ),
        )
    g786 = {row["entry"]: row for row in read_tsv(G786_DICTIONARY)}

    output: list[dict[str, object]] = []
    for spec in specs:
        surface = spec["surface"]
        census = family[surface]
        inherited = prior.get(surface)
        exact = int(census["reader_exact_surface"])
        expected_scope = (
            "READER_EXACT_COMPLETE_WHOLE_ONLY" if exact
            else "RAW_READER_WARNING_ONLY"
        )
        if spec["display_scope"] != expected_scope:
            raise AssertionError(f"reader scope mismatch for {surface}")
        row = zero_ceiling({
            "surface": surface,
            "preferred_working_default_de": spec["default_de"],
            "rival_1_de": spec["rival_1_de"],
            "rival_2_de": spec["rival_2_de"],
            "rival_2_mechanism_de": spec["rival_2_mechanism_de"],
            "display_hypothesis_not_exportable": spec["display_hypothesis_not_exportable"],
            "confidence_0_100_not_probability": spec["confidence_0_100_not_probability"],
            "confidence_label": spec["confidence_label"],
            "confidence_basis": "EDITORIAL_EVIDENCE_WEIGHT_NOT_FORMULA_NOT_PROBABILITY",
            "display_scope": spec["display_scope"],
            "lineage_decision": spec["lineage_decision"],
            "positive_evidence_de": spec["basis_de"],
            "counterevidence_de": spec["counterevidence_de"],
            "raw_occurrences": census["raw_occurrences"],
            "raw_page_count": census["raw_page_count"],
            "raw_physical_folio_count": census["raw_physical_folio_count"],
            "reader_exact_surface": exact,
            "reader_exact_occurrences": census["reader_exact_occurrences"],
            "reader_exact_page_count": census["reader_exact_page_count"],
            "reader_exact_physical_folio_count": census["reader_exact_physical_folio_count"],
            "reader_exact_display_card": exact,
            "raw_reader_warning": int(not exact),
            "gdt787_new_renderer_license": 0,
            "inherited_renderer_scope_unchanged": 1,
            "replaceable": 1,
            "portable_keedy_component_used": 0,
            "prior_gdt734_reading_id": inherited["reading_id"] if inherited else "NONE",
            "prior_gdt734_default_de": inherited["v99r7_spoken_default_de"] if inherited else "NONE",
            "prior_gdt734_score_not_probability": inherited["working_model_score_0_100_not_probability"] if inherited else "NONE",
            "prior_gdt734_renderer_decision": inherited["gdt734_renderer_decision"] if inherited else "NONE",
            "gdt786_default_de": g786[surface]["preferred_working_default_de"] if surface in g786 else "NONE",
        })
        output.append(row)

    defaults = "\n".join(str(row["preferred_working_default_de"]).lower() for row in output)
    for banned in ("holz", "wurzel", "samen", "saat", "abgeschlossen"):
        if banned in defaults:
            raise AssertionError(f"retired automatic prose remains: {banned}")
    if len(output) != 38 or sum(int(row["reader_exact_surface"]) for row in output) != 27:
        raise AssertionError("dictionary shape changed")
    if any(not str(row["preferred_working_default_de"]).strip() for row in output):
        raise AssertionError("empty working default")
    if any(int(row["gdt787_new_renderer_license"]) for row in output):
        raise AssertionError("GDT787 must not silently license display cards")
    return output


def build_passages(
    exact_rows: list[dict[str, object]], dictionary: list[dict[str, object]],
) -> list[dict[str, object]]:
    cards = {
        str(row["surface"]): row
        for row in dictionary if int(row["reader_exact_surface"])
    }
    choices: dict[str, dict[str, object]] = {}
    for row in exact_rows:
        surface = str(row["surface"])
        key = (str(row["page"]), str(row["locus"]), int(row["token_ordinal"]))
        current = choices.get(surface)
        if current is None or key < (
            str(current["page"]), str(current["locus"]), int(current["token_ordinal"])
        ):
            choices[surface] = row
    if set(choices) != set(cards):
        raise AssertionError("passage choices do not cover exact dictionary")
    output: list[dict[str, object]] = []
    for number, surface in enumerate(sorted(choices), 1):
        source, card = choices[surface], cards[surface]
        words = str(source["current_line"]).split()
        ordinal = int(source["token_ordinal"])
        if words[ordinal - 1] != surface:
            raise AssertionError(f"passage ordinal mismatch: {surface}")
        words[ordinal - 1] = f"⟦{surface} = {card['preferred_working_default_de']}⟧"
        output.append(zero_ceiling({
            "passage_id": f"G787-PASS-{number:02d}",
            "surface": surface,
            "page": source["page"],
            "physical_folio": source["physical_folio"],
            "locus": source["locus"],
            "target_ordinal": ordinal,
            "current_line": source["current_line"],
            "target_focused_line": " · ".join(words),
            "working_default_de": card["preferred_working_default_de"],
            "rival_1_de": card["rival_1_de"],
            "rival_2_de": card["rival_2_de"],
            "rival_2_mechanism_de": card["rival_2_mechanism_de"],
            "confidence_0_100_not_probability": card["confidence_0_100_not_probability"],
            "render_status": "DISPLAY_ONLY_COMPLETE_WHOLE_NOT_PLAINTEXT",
            "gdt787_new_renderer_license": 0,
            "portable_component_used": 0,
        }))
    if len(output) != 27:
        raise AssertionError("expected 27 exact-whole passage displays")
    return output


def build_historical_controls() -> list[dict[str, object]]:
    rows = {row["source_id"]: row for row in read_tsv(G735_ARCHITECTURE)}
    output = []
    for source_id in ("HSR008", "HSR010"):
        source = rows[source_id]
        output.append(zero_ceiling({
            "source_id": source_id,
            "work": source["work"],
            "date_band": source["date_band"],
            "record_channels": source["record_channels"],
            "observed_slots": source["observed_slots"],
            "architecture_use": "LEARNED_WHOLES_PLUS_BOUND_SPECIALIST_FIELDS_ONLY",
            "actual_four_head_one_letter_code_attested": source["actual_four_head_one_letter_code_attested"],
            "selects_keedy_identity": 0,
            "selects_keedy_segmentation": 0,
        }))
    return output


def build_relation_rows(
    spans: list[dict[str, object]], dictionary: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    cards = {str(row["surface"]): row for row in dictionary}
    fused = {str(row["surface"]) for row in dictionary if str(row["surface"]) != "keedy"}
    packet: list[dict[str, object]] = []
    crosswalk: list[dict[str, object]] = []
    for number, span in enumerate(spans, 1):
        edge_id = f"G787-E{number:03d}"
        locus = str(span["locus"])
        left_ordinal = int(span["left_token_ordinal"])
        right_ordinal = int(span["right_token_ordinal"])
        left = str(span["left_surface"])
        packet.append({
            "edge_id": edge_id,
            "batch_id": "GDT787_SEPARATED_X_KEEDY_SPANS",
            "page": span["page"],
            "physical_folio": span["physical_folio"],
            "diagram_unit_id": f"LINE:{locus}",
            "pivot_visual_id": f"TOKEN:{locus}:{left_ordinal}",
            "pivot_locus": f"{locus}@{left_ordinal}",
            "target_visual_id": f"TOKEN:{locus}:{right_ordinal}",
            "target_locus": f"{locus}@{right_ordinal}",
            "relation_type": "X_PRECEDES_KEEDY_SEPARATED",
            "direction_basis": "TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_FIELD_ADJACENCY",
            "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT787",
            "page_crop_sha256": "NONE",
            "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT787_RUNNER",
            "relation_reviewer": "GDT787_VALIDATOR",
            "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "BOUNDARY_C2_SEMANTICS_C0",
            "formal_access_state": "SEALED_NOT_ACCESSED",
            "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
        fused_surface = left + "keedy"
        crosswalk.append({
            "edge_id": edge_id,
            "batch_id": "GDT787_SEPARATED_X_KEEDY_SPANS",
            "page": span["page"],
            "physical_folio": span["physical_folio"],
            "locus": locus,
            "left_surface": left,
            "separated_pair": span["separated_pair"],
            "fused_surface_if_observed": fused_surface if fused_surface in fused else "NONE",
            "working_keedy_default_de": cards["keedy"]["preferred_working_default_de"],
            "semantic_score_eligible": 0,
            "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    if len(packet) != 20 or len(crosswalk) != 20:
        raise AssertionError("expected twenty separated-span relation rows")
    return packet, crosswalk


def artifact_readme() -> str:
    return """# GDT787 artifacts

These files reproduce the guarded keedy family census, the complete 10 by 5
written paradigm, the nine-row semantic transfer tournament, the independently
sanitized HOT/END/CLOSE contrasts, and all 38 replaceable whole-form displays
with two concrete semantic rivals plus a separate mechanism alternative.

The same HOT/END display prior was deliberately supplied to the full family so
that no observed form is left blank. It is a C0 hypothesis, not 38 independent
semantic findings and not a portable keedy component. GDT787 grants zero new
renderer licences; previously inherited scopes remain governed by their own
source experiments.

The 20-row GDT388 packet records transcription-order adjacency only. It is
valid acquisition bookkeeping but intentionally ineligible for semantic
scoring: there are no images, geometry-only selections, mobile nulls or frozen
holdouts. The packet therefore cannot promote a split or a meaning.

Scores are similarities or editorial evidence weights, never probabilities.
German values are concrete exploratory displays, not plaintext. Reader-
unstable surfaces are warning cards.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    args = parser.parse_args()
    artifacts = args.artifacts_dir.resolve()
    lock_count, lock_hash = verify_locks()

    corpus = load_module("gdt787_corpus", CORPUS_MODULE).compute(ROOT)
    model = load_module("gdt787_model", MODEL_MODULE).compute(ROOT)
    axes = load_module("gdt787_axis", AXIS_MODULE).compute(ROOT)
    specs = read_tsv(WHOLE_SPECS)
    dictionary = build_dictionary(corpus["raw_family_rows"], specs)
    passages = build_passages(corpus["exact_occurrence_rows"], dictionary)
    historical = build_historical_controls()
    packet, crosswalk = build_relation_rows(
        corpus["exact_separated_span_rows"], dictionary
    )

    tsv_outputs = {
        "GDT787_38_FAMILY_CENSUS.tsv": corpus["raw_family_rows"],
        "GDT787_370_EXACT_OCCURRENCE_ATLAS.tsv": corpus["exact_occurrence_rows"],
        "GDT787_50_COMPLETE_PARADIGM.tsv": corpus["paradigm_rows"],
        "GDT787_6_HOT_FORMAL_CONTRASTS.tsv": corpus["hot_contrast_rows"],
        "GDT787_59_RAW_SEPARATED_SPANS.tsv": corpus["raw_separated_pair_rows"],
        "GDT787_20_EXACT_SEPARATED_SPANS.tsv": corpus["exact_separated_span_rows"],
        "GDT787_5_FUSED_SPLIT_FAMILIES.tsv": corpus["fused_split_family_rows"],
        "GDT787_27_STOLFI_BOUNDARY_SUMMARY.tsv": corpus["stolfi_boundary_rows"],
        "GDT787_370_STOLFI_BOUNDARY_OCCURRENCES.tsv": corpus["stolfi_boundary_occurrence_rows"],
        "GDT787_9_FACTORIAL_MODEL.tsv": model["factorial_rows"],
        "GDT787_3_MODEL_SUMMARY.tsv": model["summary_rows"],
        "GDT787_9_END_CLOSE_CONTRASTS.tsv": model["contrast_rows"],
        "GDT787_62_SANITIZED_AXIS_CONTRASTS.tsv": axes["contrast_rows"],
        "GDT787_6_SANITIZED_AXIS_SUMMARY.tsv": axes["summary_rows"],
        "GDT787_38_WORKING_DICTIONARY.tsv": dictionary,
        "GDT787_27_PRACTICAL_PASSAGES.tsv": passages,
        "GDT787_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv": historical,
        "GDT787_GUARDED_SOURCE_STATS.tsv": corpus["guarded_source_stats"],
        "GDT787_RELATION_EDGE_CROSSWALK.tsv": crosswalk,
    }
    for name, rows in tsv_outputs.items():
        write_tsv(artifacts / name, rows)
    packet_path = artifacts / "GDT787_GDT388_SEPARATED_SPAN_PACKET.tsv"
    write_tsv(packet_path, packet, EDGE_COLUMNS)

    intake_module = load_module("gdt787_relation_intake", RELATION_INTAKE)
    intake = intake_module.validate_relation_edge_packet(packet_path)
    if intake["status"] != "VALID_ACQUISITION_NOT_SCORE_READY" or intake["errors"]:
        raise AssertionError(f"unexpected relation intake: {intake}")
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", intake)

    full = next(row for row in model["summary_rows"] if row["view"] == "FULL")
    axis_summary = {
        f"{row['contrast']}_R{row['radius']}": {
            "type_pairs": row["type_pairs"],
            "informative_type_pairs": row["informative_type_pairs"],
            "na": row["na"],
            "positive": row["positive"],
            "zero": row["zero"],
            "negative": row["negative"],
            "mean_directional_delta": row["mean_directional_delta"],
            "exact_two_sided_sign_flip_p": row["exact_two_sided_sign_flip_p"],
        }
        for row in axes["summary_rows"]
    }
    result = {
        "experiment_id": "GDT787",
        "status": STATUS,
        "source_locks": lock_count,
        "source_lock_sha256": lock_hash,
        "source_spec_sha256": sha256(WHOLE_SPECS),
        "corpus": corpus["diagnostics"],
        "model": {
            "x_types": full["x_types"],
            "additive_macro_similarity": full["additive_macro_similarity"],
            "same_x_macro_similarity": full["same_x_macro_similarity"],
            "learned_whole_macro_similarity": full["learned_whole_macro_similarity"],
            "additive_beats_same_x": full["additive_beats_same_x"],
            "additive_beats_learned_whole": full["additive_beats_learned_whole"],
            "additive_beats_both": full["additive_beats_both"],
            "additive_beats_adversarial_best": model["diagnostics"]["additive_beats_adversarial_best"],
            "recommendation": model["diagnostics"]["recommendation"],
            "score_semantics": "JENSEN_SHANNON_SIMILARITY_NOT_PROBABILITY",
        },
        "sanitized_axis_audit": {
            "decision": axes["diagnostics"]["decision"],
            "summary": axis_summary,
        },
        "dictionary": {
            "raw_forms_with_nonempty_defaults": 38,
            "reader_exact_display_cards": 27,
            "raw_reader_warning_cards": 11,
            "new_renderer_licenses": 0,
            "portable_component_exports": 0,
            "shared_family_display_prior": "HOT|END_STAGE_C0_NOT_EXPORTABLE",
        },
        "adjudication": {
            "formal_keedy_family": "C1_RETAINED_STRONG",
            "portable_keedy_remainder": "C0_INACTIVE__WHOLE_ONLY",
            "bare_keedy_default_de": "heißer Endzustand",
            "hot_end_in_form_specific_wholes": "MAY_REMAIN_ON_WHOLE_EVIDENCE",
            "automatic_closed_component": "REJECTED",
            "default_long_form_mechanism": "LEARNED_OR_FORM_SPECIFIC_COMPLETE_WHOLE",
            "next_remainder": "dal",
        },
        "relation_packet": intake,
        "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0,
        "specific_substances": 0,
        "component_exports": 0,
        "new_pages": 0,
        "new_images": 0,
        "new_ocr": 0,
        "new_transcriptions": 0,
        "sealed_pages_accessed": 0,
        "claim_ceiling": (
            "C2 observed current-reader complete-word boundaries; C1 formal "
            "keedy family and at most form-specific whole roles; C0 German "
            "displays and semantic transfer hypotheses; zero free component."
        ),
    }
    write_json(artifacts / "RESULT.json", result)
    (artifacts / "README.md").write_text(artifact_readme(), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
