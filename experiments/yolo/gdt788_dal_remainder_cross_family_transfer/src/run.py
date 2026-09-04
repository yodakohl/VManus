#!/usr/bin/env python3
"""Build the guarded GDT788 DAL remainder transfer experiment."""

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
EXP = ROOT / "experiments/yolo/gdt788_dal_remainder_cross_family_transfer"
SRC, ART = EXP / "src", EXP / "artifacts"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
OVERRIDES = SRC / "DEFAULT_OVERRIDES.tsv"
CORPUS_MODULE = SRC / "corpus.py"
MODEL_MODULE = SRC / "model.py"
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
    "PARTIAL__107_RAW_FORMS__415_RAW__80_EXACT_FORMS__304_EXACT__"
    "40_PRIMARY_LATTICE_CELLS__SHIFT_BOTH_2_OF10__CORE_BOTH_4_OF10__"
    "FORMAL_FAMILY_WHOLE_ONLY__107_DEFAULTS__ZERO_COMPONENT_EXPORT__"
    "ZERO_NEW_RENDERER_LICENSE"
)

OUTPUT_NAMES = (
    "GDT788_107_DAL_FAMILY_CENSUS.tsv",
    "GDT788_304_DAL_EXACT_OCCURRENCES.tsv",
    "GDT788_40_PRIMARY_AL_DAL_AR_DAR_LATTICE.tsv",
    "GDT788_64_EXPANDED_AL_DAL_AR_DAR_LATTICE.tsv",
    "GDT788_185_RAW_X_DAL_SPANS.tsv",
    "GDT788_115_EXACT_X_DAL_SPANS.tsv",
    "GDT788_4_FUSED_SPLIT_FAMILIES.tsv",
    "GDT788_304_STOLFI_BOUNDARY_OCCURRENCES.tsv",
    "GDT788_80_STOLFI_BOUNDARY_SUMMARY.tsv",
    "GDT788_42_FOLIO_BALANCED_PROFILES.tsv",
    "GDT788_996_SEMANTIC_LEAKAGE_MASK.tsv",
    "GDT788_10_LEARNED_WHOLE_CONTROLS.tsv",
    "GDT788_10_PRIMARY_FACTORIAL_TRANSFER.tsv",
    "GDT788_4_MODEL_SUMMARY.tsv",
    "GDT788_140_AXIS_DID_CONTRASTS.tsv",
    "GDT788_14_AXIS_DID_SUMMARY.tsv",
    "GDT788_107_WORKING_DICTIONARY.tsv",
    "GDT788_80_PRACTICAL_PASSAGES.tsv",
    "GDT788_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv",
    "GDT788_GUARDED_SOURCE_STATS.tsv",
    "GDT788_GDT388_115_SEPARATED_SPAN_PACKET.tsv",
    "GDT788_RELATION_EDGE_CROSSWALK.tsv",
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
    if len(rows) != 23:
        raise AssertionError(f"expected 23 source locks, got {len(rows)}")
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
        "historical_word_credit": 0,
        "phonetic_or_eva_letter_credit": 0,
        "component_export_credit": 0,
    })
    return row


def _integer(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1


def build_dictionary(
    family_rows: list[dict[str, object]], override_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    family = {str(row["surface"]): row for row in family_rows}
    overrides = {row["surface"]: row for row in override_rows}
    if len(family) != 107 or len(overrides) != 37 or not set(overrides) <= set(family):
        raise AssertionError("dictionary surface or override contract changed")
    exact_overrides = {surface for surface in overrides if int(family[surface]["reader_exact_surface"])}
    raw_overrides = set(overrides) - exact_overrides
    if (len(exact_overrides), len(raw_overrides)) != (34, 3):
        raise AssertionError("expected 34 exact and 3 raw-only overrides")

    prior_rows: dict[str, list[dict[str, str]]] = {}
    for row in read_tsv(G734_DICTIONARY):
        prior_rows.setdefault(row["surface"], []).append(row)
    prior = {
        surface: max(rows, key=lambda row: (
            _integer(row["gdt734_exact_whole_default_allowed"]),
            _integer(row["working_model_score_0_100_not_probability"]),
            _integer(row["occurrence_count"]), row["reading_id"],
        ))
        for surface, rows in prior_rows.items()
    }
    g786 = {row["entry"]: row for row in read_tsv(G786_DICTIONARY)}

    output = []
    for surface in sorted(family):
        census = family[surface]
        exact = int(census["reader_exact_surface"])
        override = overrides.get(surface)
        if override:
            default = override["default_de"]
            rival_1, rival_2 = override["rival_1_de"], override["rival_2_de"]
            score = int(override["confidence_0_100_not_probability"])
            label = override["confidence_label"]
            lineage_sources = override["lineage_sources"]
            lineage_decision = override["lineage_decision"]
            card_class = "EXPLICIT_OVERRIDE"
        else:
            default = "Materialposten I"
            rival_1, rival_2 = "Material I, abgemessen", "Mengen-/Wertfeld I"
            score = 24 if exact else 12
            label = "C0_EXACT_SINGLETON_WHOLE" if exact else "C0_RAW_READER_WARNING"
            lineage_sources = "GDT788"
            lineage_decision = (
                "LEARNED_COMPLETE_WHOLE_WITH_DAL_FAMILY_DISPLAY_PRIOR"
                if exact else "RAW_READER_WARNING_ONLY"
            )
            card_class = "EXACT_SINGLETON_FALLBACK" if exact else "RAW_ONLY_FALLBACK"
        if len({default, rival_1, rival_2}) != 3:
            raise AssertionError(f"non-distinct semantic options: {surface}")
        mechanism = (
            "INHERITED_COMPLETE_WHOLE_NO_INNER_SPLIT" if surface == "dal" else
            "RAW_READER_WARNING_ONLY" if not exact else
            "FORM_SPECIFIC_COMPLETE_WHOLE_NO_COMPONENT_EXPORT" if override else
            "LEARNED_COMPLETE_WHOLE_WITH_DAL_FAMILY_DISPLAY_PRIOR"
        )
        positive = (
            f"Beobachtete vollständige Oberfläche mit {census['raw_occurrences']} rohen und "
            f"{census['reader_exact_occurrences']} reader-exakten Vorkommen auf "
            f"{census['reader_exact_physical_folio_count']} exakten Folios; Kartenlinie {lineage_sources}."
            if exact else
            f"Ein rohes Vorkommen der vollständigen Oberfläche; Kartenlinie {lineage_sources}; "
            "die Anzeige verhindert eine leere Arbeitsstelle."
        )
        counter = (
            "Der SHIFT-Test schlägt beide Kontrollen nur in 2/10, der günstigere CORE-Test in "
            "4/10 Reihen; kein reader-exakter gleichlokaler X|dal-Split und kein d|al-Split. "
            "Die Oberfläche kann ein gelernter Ganzname oder ein anderes Feld sein."
            if exact else
            "Kein reader-exaktes vollständiges Wort; Segmentierung und Bedeutung bleiben offen. "
            "Keine getrennte Grenze, historische Wortidentität oder Renderer-Lizenz."
        )
        inherited = prior.get(surface)
        output.append(zero_ceiling({
            "surface": surface,
            "card_class": card_class,
            "preferred_working_default_de": default,
            "rival_1_de": rival_1,
            "rival_2_de": rival_2,
            "preferred_mechanism": mechanism,
            "mechanism_rival_1": "PORTABLE_DAL_REMAINDER_CANDIDATE",
            "mechanism_rival_2": "OPAQUE_LEARNED_WHOLE_CANDIDATE",
            "display_hypothesis_not_exportable": "MATERIAL|MEASURE|LEVEL_I_C0_FAMILY_PRIOR",
            "confidence_0_100_not_probability": score,
            "confidence_label": label,
            "confidence_basis": "EDITORIAL_EVIDENCE_WEIGHT_NOT_FORMULA_NOT_PROBABILITY",
            "display_scope": "READER_EXACT_COMPLETE_WHOLE_ONLY" if exact else "RAW_READER_WARNING_ONLY",
            "lineage_sources": lineage_sources,
            "lineage_decision": lineage_decision,
            "positive_evidence_de": positive,
            "counterevidence_de": counter,
            "raw_occurrences": census["raw_occurrences"],
            "raw_page_count": census["raw_page_count"],
            "raw_physical_folio_count": census["raw_physical_folio_count"],
            "reader_exact_surface": exact,
            "reader_exact_occurrences": census["reader_exact_occurrences"],
            "reader_exact_page_count": census["reader_exact_page_count"],
            "reader_exact_physical_folio_count": census["reader_exact_physical_folio_count"],
            "reader_exact_display_card": exact,
            "raw_reader_warning": int(not exact),
            "replaceable": 1,
            "gdt788_new_renderer_license": 0,
            "portable_dal_component_used": 0,
            "prior_gdt734_reading_id": inherited["reading_id"] if inherited else "NONE",
            "prior_gdt734_default_de": inherited["v99r7_spoken_default_de"] if inherited else "NONE",
            "prior_gdt734_score_not_probability": inherited["working_model_score_0_100_not_probability"] if inherited else "NONE",
            "prior_gdt734_renderer_decision": inherited["gdt734_renderer_decision"] if inherited else "NONE",
            "gdt786_default_de": g786[surface]["preferred_working_default_de"] if surface in g786 else "NONE",
        }))
    classes = {name: sum(row["card_class"] == name for row in output) for name in {
        "EXPLICIT_OVERRIDE", "EXACT_SINGLETON_FALLBACK", "RAW_ONLY_FALLBACK"
    }}
    if classes != {"EXPLICIT_OVERRIDE": 37, "EXACT_SINGLETON_FALLBACK": 46, "RAW_ONLY_FALLBACK": 24}:
        raise AssertionError(f"dictionary dispatch changed: {classes}")
    if sum(int(row["reader_exact_surface"]) for row in output) != 80:
        raise AssertionError("dictionary exact-surface count changed")
    banned = ("Drogenholz", "Wurzelrohstoff", "Samenrohstoff", "Pulverposten")
    if any(term.lower() in str(row["preferred_working_default_de"]).lower() for term in banned for row in output):
        raise AssertionError("retired automatic patient prose in preferred default")
    return output


def build_passages(
    exact_rows: list[dict[str, object]], dictionary: list[dict[str, object]],
) -> list[dict[str, object]]:
    cards = {str(row["surface"]): row for row in dictionary if int(row["reader_exact_surface"])}
    choices: dict[str, dict[str, object]] = {}
    for row in exact_rows:
        surface = str(row["surface"])
        key = (str(row["page"]), str(row["locus"]), int(row["token_ordinal"]))
        current = choices.get(surface)
        if current is None or key < (str(current["page"]), str(current["locus"]), int(current["token_ordinal"])):
            choices[surface] = row
    if set(choices) != set(cards):
        raise AssertionError("passage choices do not cover exact cards")
    output = []
    for number, surface in enumerate(sorted(choices), 1):
        source, card = choices[surface], cards[surface]
        words = str(source["current_line"]).split()
        ordinal = int(source["token_ordinal"])
        if words[ordinal - 1] != surface:
            raise AssertionError(f"passage ordinal mismatch: {surface}")
        words[ordinal - 1] = f"⟦{surface} = {card['preferred_working_default_de']}⟧"
        output.append(zero_ceiling({
            "passage_id": f"G788-PASS-{number:03d}",
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
            "confidence_0_100_not_probability": card["confidence_0_100_not_probability"],
            "render_status": "DISPLAY_ONLY_COMPLETE_WHOLE_NOT_PLAINTEXT",
            "gdt788_new_renderer_license": 0,
            "portable_dal_component_used": 0,
        }))
    if len(output) != 80:
        raise AssertionError("expected 80 exact-whole passages")
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
            "architecture_use": "LEARNED_WHOLES_PLUS_BOUND_QUALITY_VALUE_AND_RECIPE_FIELDS_ONLY",
            "actual_four_head_one_letter_code_attested": source["actual_four_head_one_letter_code_attested"],
            "selects_dal_identity": 0,
            "selects_dal_segmentation": 0,
        }))
    return output


def build_relation_rows(
    spans: list[dict[str, object]], dictionary: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    cards = {str(row["surface"]): row for row in dictionary}
    packet, crosswalk = [], []
    for number, span in enumerate(spans, 1):
        edge_id = f"G788-E{number:03d}"
        locus = str(span["locus"])
        left_ordinal = int(span["left_token_ordinal"])
        right_ordinal = int(span["right_token_ordinal"])
        packet.append({
            "edge_id": edge_id,
            "batch_id": "GDT788_SEPARATED_X_DAL_SPANS",
            "page": span["page"],
            "physical_folio": span["physical_folio"],
            "diagram_unit_id": f"LINE:{locus}",
            "pivot_visual_id": f"TOKEN:{locus}:{left_ordinal}",
            "pivot_locus": f"{locus}@{left_ordinal}",
            "target_visual_id": f"TOKEN:{locus}:{right_ordinal}",
            "target_locus": f"{locus}@{right_ordinal}",
            "relation_type": "X_PRECEDES_DAL_SEPARATED",
            "direction_basis": "TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_FIELD_ADJACENCY",
            "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT788",
            "page_crop_sha256": "NONE",
            "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT788_RUNNER",
            "relation_reviewer": "GDT788_VALIDATOR",
            "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "BOUNDARY_C2_SEMANTICS_C0",
            "formal_access_state": "SEALED_NOT_ACCESSED",
            "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
        left = str(span["left_surface"])
        crosswalk.append(zero_ceiling({
            "edge_id": edge_id,
            "batch_id": "GDT788_SEPARATED_X_DAL_SPANS",
            "page": span["page"],
            "physical_folio": span["physical_folio"],
            "locus": locus,
            "left_surface": left,
            "separated_pair": span["separated_pair"],
            "fused_surface_if_observed": left + "dal" if left + "dal" in cards else "NONE",
            "working_dal_default_de": cards["dal"]["preferred_working_default_de"],
            "semantic_score_eligible": 0,
        }))
    if len(packet) != 115 or len(crosswalk) != 115:
        raise AssertionError("expected 115 separated-span rows")
    return packet, crosswalk


def guarded_source_stats(corpus: Mapping[str, object]) -> list[dict[str, object]]:
    guard, stolfi = corpus["guard"], corpus["stolfi_guard"]
    return [
        {"source": name, "selected_rows": guard[name]["selected"], "skipped_forbidden": guard[name]["skipped_forbidden"], "skipped_not_allowed": guard[name]["skipped_not_allowed"], "base_allowed_pages": guard["allowed_pages"], "query_allow_pages": guard["allowed_pages"], "f84_rows_materialised": 0}
        for name in ("tokens", "cross", "lines")
    ] + [{
        "source": "stolfi", "selected_rows": stolfi["selected"],
        "skipped_forbidden": stolfi["skipped_forbidden"],
        "skipped_not_allowed": stolfi["skipped_not_allowed"],
        "base_allowed_pages": guard["allowed_pages"],
        "query_allow_pages": corpus["diagnostics"]["stolfi_requested_pages"],
        "f84_rows_materialised": 0,
    }]


def artifact_readme() -> str:
    return """# GDT788 artifacts

These files reproduce the guarded 107-form `*dal` census, the complete
10-by-4 primary `al/dal/ar/dar` lattice, the SHIFT and bare-core transfer
models, seven leakage-controlled outside-axis contrasts, and a nonempty
replaceable working card for every observed form.

The 996-surface mask prevents earlier AL/DAL prose, provenance-composed cards,
and quarantined patient words from returning as semantic support. Scores are
distributional similarities or editorial evidence weights, never
probabilities. German card values are concrete exploratory displays attached
to complete observed surfaces, not plaintext and not portable substrings.

The 115-row relation packet records transcription-order adjacency only. It is
valid acquisition bookkeeping but deliberately ineligible for scoring: no
image geometry, mobile null, frozen holdout, or visual relation was supplied.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    args = parser.parse_args()
    artifacts = args.artifacts_dir.resolve()
    lock_count, lock_hash = verify_locks()

    corpus = load_module("gdt788_corpus", CORPUS_MODULE).compute(ROOT)
    model = load_module("gdt788_model", MODEL_MODULE).compute(ROOT)
    dictionary = build_dictionary(corpus["family_rows"], read_tsv(OVERRIDES))
    passages = build_passages(corpus["exact_occurrence_rows"], dictionary)
    historical = build_historical_controls()
    packet, crosswalk = build_relation_rows(corpus["clean_exact_separated_rows"], dictionary)

    tsv_outputs = {
        "GDT788_107_DAL_FAMILY_CENSUS.tsv": corpus["family_rows"],
        "GDT788_304_DAL_EXACT_OCCURRENCES.tsv": corpus["exact_occurrence_rows"],
        "GDT788_40_PRIMARY_AL_DAL_AR_DAR_LATTICE.tsv": corpus["primary_lattice_rows"],
        "GDT788_64_EXPANDED_AL_DAL_AR_DAR_LATTICE.tsv": corpus["sensitivity_lattice_rows"],
        "GDT788_185_RAW_X_DAL_SPANS.tsv": corpus["raw_separated_rows"],
        "GDT788_115_EXACT_X_DAL_SPANS.tsv": corpus["clean_exact_separated_rows"],
        "GDT788_4_FUSED_SPLIT_FAMILIES.tsv": corpus["fused_split_rows"],
        "GDT788_304_STOLFI_BOUNDARY_OCCURRENCES.tsv": corpus["stolfi_occurrence_rows"],
        "GDT788_80_STOLFI_BOUNDARY_SUMMARY.tsv": corpus["stolfi_summary_rows"],
        "GDT788_42_FOLIO_BALANCED_PROFILES.tsv": model["profile_rows"],
        "GDT788_996_SEMANTIC_LEAKAGE_MASK.tsv": model["mask_rows"],
        "GDT788_10_LEARNED_WHOLE_CONTROLS.tsv": model["control_rows"],
        "GDT788_10_PRIMARY_FACTORIAL_TRANSFER.tsv": model["factorial_rows"],
        "GDT788_4_MODEL_SUMMARY.tsv": model["summary_rows"],
        "GDT788_140_AXIS_DID_CONTRASTS.tsv": model["axis_rows"],
        "GDT788_14_AXIS_DID_SUMMARY.tsv": model["axis_summary_rows"],
        "GDT788_107_WORKING_DICTIONARY.tsv": dictionary,
        "GDT788_80_PRACTICAL_PASSAGES.tsv": passages,
        "GDT788_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv": historical,
        "GDT788_GUARDED_SOURCE_STATS.tsv": guarded_source_stats(corpus),
        "GDT788_RELATION_EDGE_CROSSWALK.tsv": crosswalk,
    }
    for name, rows in tsv_outputs.items():
        write_tsv(artifacts / name, rows)
    packet_path = artifacts / "GDT788_GDT388_115_SEPARATED_SPAN_PACKET.tsv"
    write_tsv(packet_path, packet, EDGE_COLUMNS)

    intake_module = load_module("gdt788_relation_intake", RELATION_INTAKE)
    intake = intake_module.validate_relation_edge_packet(packet_path)
    if intake["status"] != "VALID_ACQUISITION_NOT_SCORE_READY" or intake["errors"]:
        raise AssertionError(f"unexpected relation intake: {intake}")
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", intake)

    full = next(row for row in model["summary_rows"] if row["view"] == "FULL")
    result = {
        "experiment_id": "GDT788",
        "status": STATUS,
        "source_locks": lock_count,
        "source_lock_sha256": lock_hash,
        "override_spec_sha256": sha256(OVERRIDES),
        "corpus": corpus["diagnostics"],
        "model": {
            "primary_x_types": 10,
            "shift_macro_similarity": full["shift_macro_similarity"],
            "core_macro_similarity": full["core_macro_similarity"],
            "xal_macro_similarity": full["xal_macro_similarity"],
            "learned_whole_macro_similarity": full["learned_whole_macro_similarity"],
            "shift_beats_both": full["shift_beats_both"],
            "core_beats_both": full["core_beats_both"],
            "semantic_mask_surfaces": model["diagnostics"]["complete_semantic_mask_surfaces"],
            "clean_learned_whole_references": model["diagnostics"]["learned_whole_reference_surfaces_after_mask"],
            "recommendation": model["diagnostics"]["recommendation"],
            "score_semantics": "TARGET_DEFINED_FIELD_JENSEN_SHANNON_SIMILARITY_NOT_PROBABILITY",
        },
        "axis_audit": {
            "rows": len(model["axis_rows"]),
            "summary_rows": len(model["axis_summary_rows"]),
            "decision": "NO_COMMON_AMOUNT_MATERIAL_OR_PART_EXPORT",
        },
        "dictionary": {
            "raw_forms_with_nonempty_defaults": 107,
            "reader_exact_display_cards": 80,
            "raw_reader_warning_cards": 27,
            "explicit_overrides": 37,
            "exact_singleton_fallbacks": 46,
            "raw_only_fallbacks": 24,
            "new_renderer_licenses": 0,
            "portable_component_exports": 0,
            "shared_family_display_prior": "MATERIAL|MEASURE|LEVEL_I_C0_NOT_EXPORTABLE",
        },
        "adjudication": {
            "formal_dal_family": "C1_RETAINED_STRONG",
            "portable_dal_remainder": "C0_INACTIVE__WHOLE_ONLY",
            "bare_dal_default_de": "Material I, abgemessen",
            "bare_dal_value_axis": "OPEN",
            "automatic_d_equals_measure": "NOT_LICENSED",
            "automatic_al_equals_material": "NOT_LICENSED",
            "default_long_form_mechanism": "LEARNED_OR_FORM_SPECIFIC_COMPLETE_WHOLE",
            "next_remainder": "ar",
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
            "C2 observed current-reader complete-word boundaries; C1 formal DAL family and "
            "provenance-bound bare dal role; C0 German whole displays and semantic transfer "
            "hypotheses; zero portable component, lexeme, plaintext, or substance."
        ),
    }
    write_json(artifacts / "RESULT.json", result)
    (artifacts / "README.md").write_text(artifact_readme(), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
