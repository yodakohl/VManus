#!/usr/bin/env python3
"""Build the guarded GDT789 AR remainder transfer experiment."""

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
EXP = ROOT / "experiments/yolo/gdt789_ar_remainder_cross_family_transfer"
SRC, ART = EXP / "src", EXP / "artifacts"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
OVERRIDES = SRC / "DEFAULT_OVERRIDES.tsv"
CORPUS_MODULE = SRC / "corpus.py"
MODEL_MODULE = SRC / "model.py"
G734_DICTIONARY = ROOT / (
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/"
    "V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
)
G735_ARCHITECTURE = ROOT / (
    "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/"
    "HISTORICAL_SOURCE_ARCHITECTURE_MATRIX.tsv"
)
RELATION_INTAKE = ROOT / "tools/relation_edge_intake.py"

STATUS = (
    "PARTIAL__285_RAW_FORMS__1698_RAW__225_EXACT_FORMS__1348_EXACT__"
    "47_ROBUST_AR_OR_PREFIXES__SUPPORT_ADD_BOTH_7_OF31__HISTORICAL_EXCLUSION_8_OF31__"
    "RN12_0_OF7__RN23_0_OF6__BARE_AR_ANTEIL__WHOLE_ONLY__"
    "285_DEFAULTS__ZERO_COMPONENT_EXPORT__ZERO_NEW_RENDERER_LICENSE"
)

OUTPUT_NAMES = (
    "GDT789_285_AR_FAMILY_CENSUS.tsv", "GDT789_1348_AR_EXACT_OCCURRENCES.tsv",
    "GDT789_40_GDT788_SQUARE_REFERENCE.tsv", "GDT789_94_ROBUST_AR_OR_LATTICE.tsv",
    "GDT789_28_RN12_LATTICE.tsv", "GDT789_24_RN23_LATTICE.tsv",
    "GDT789_318_RAW_X_AR_SPANS.tsv", "GDT789_192_EXACT_X_AR_SPANS.tsv",
    "GDT789_20_FUSED_SPLIT_FAMILIES.tsv", "GDT789_1348_STOLFI_BOUNDARY_OCCURRENCES.tsv",
    "GDT789_225_STOLFI_BOUNDARY_SUMMARY.tsv", "GDT789_13_BARE_HEAD_CONSTRUCTIONS.tsv",
    "GDT789_96_FOLIO_BALANCED_PROFILES.tsv", "GDT789_2140_SEMANTIC_LEAKAGE_MASK.tsv",
    "GDT789_47_LEARNED_WHOLE_CONTROLS.tsv", "GDT789_47_AR_OR_TRANSFER.tsv",
    "GDT789_15_TRANSFER_SUMMARY.tsv", "GDT789_658_AXIS_CONTRASTS.tsv",
    "GDT789_42_AXIS_SUMMARY.tsv", "GDT789_94_VALUE_BINDING_SIGNATURES.tsv",
    "GDT789_13_RN_TRANSFER.tsv", "GDT789_8_RN_SUMMARY.tsv",
    "GDT789_253_ROLE_PROTOTYPE_LOO.tsv", "GDT789_3_ROLE_PROTOTYPE_SUMMARY.tsv",
    "GDT789_97_TARGET_ROLE_PROFILES.tsv", "GDT789_285_WORKING_DICTIONARY.tsv",
    "GDT789_225_PRACTICAL_PASSAGES.tsv", "GDT789_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv",
    "GDT789_GUARDED_SOURCE_STATS.tsv", "GDT789_GDT388_192_SEPARATED_SPAN_PACKET.tsv",
    "GDT789_RELATION_EDGE_CROSSWALK.tsv", "RELATION_PACKET_INTAKE.json",
    "RESULT.json", "README.md",
)

EDGE_COLUMNS = (
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
    "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
    "relation_type", "direction_basis", "ownership_basis", "geometry_only_selection",
    "source_manifest_id", "page_crop_sha256", "pivot_crop_sha256", "target_crop_sha256",
    "source_aware_localizer", "relation_reviewer", "relation_confidence",
    "ambiguity_state", "formal_access_state", "fold_assignment", "eligibility_status",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _text(value: object) -> object:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return f"{value:.12f}"
    return "NA" if value is None else value


def write_tsv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str] | None = None) -> None:
    material = list(rows)
    if not material:
        raise AssertionError(f"empty output: {path.name}")
    names = list(fields or ())
    if not names:
        for row in material:
            names.extend(field for field in row if field not in names)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in material:
            writer.writerow({name: _text(row.get(name, "")) for name in names})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_locks() -> tuple[int, str]:
    rows = read_tsv(SOURCE_LOCK)
    if not rows:
        raise AssertionError("empty source lock")
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
        "default_is_translation": 0, "confirmed_lexeme": 0,
        "confirmed_plaintext": 0, "specific_substance_confirmed": 0,
        "historical_word_credit": 0, "phonetic_or_eva_letter_credit": 0,
        "component_export_credit": 0,
    })
    return row


def _best_prior_rows() -> dict[str, dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in read_tsv(G734_DICTIONARY):
        grouped.setdefault(row["surface"], []).append(row)
    return {
        surface: max(rows, key=lambda row: (
            int(row["working_model_score_0_100_not_probability"] or 0),
            int(row["occurrence_count"] or 0), row["reading_id"],
        )) for surface, rows in grouped.items()
    }


def build_dictionary(corpus, model, overrides):
    family = {str(row["surface"]): row for row in corpus["family_rows"]}
    override = {row["surface"]: row for row in overrides}
    if len(family) != 285 or len(override) != 19 or not set(override) <= set(family):
        raise AssertionError("dictionary/override surface contract changed")
    roles = {row["surface"]: row for row in model["target_role_rows"]}
    fused = {row["fused_surface"] for row in corpus["fused_split_rows"]}
    priors = _best_prior_rows()
    role_defaults = {
        "PART": ("Anteilsposten", "Teilmenge", "Wert-/Klassenfeld"),
        "AMOUNT": ("Teilmenge", "Anteilsposten", "Wert-/Klassenfeld"),
        "VALUE": ("Wert-/Klassenfeld", "Anteilsposten", "Teilmenge"),
    }
    output = []
    for surface in sorted(family):
        census = family[surface]
        exact = int(census["reader_exact_surface"])
        count = int(census["reader_exact_occurrences"])
        spec, role = override.get(surface), roles.get(surface)
        if spec:
            default = spec["default_de"]
            rivals = [spec[f"rival_{number}_de"] for number in (1, 2, 3)]
            confidence = int(spec["confidence_0_100_not_probability"])
            label, lineage, decision = spec["confidence_label"], spec["lineage_sources"], spec["lineage_decision"]
            card_class = "EXPLICIT_COMPLETE_WHOLE"
        elif exact and role and int(role["selector_usable"]):
            preferred, first, second = role_defaults[role["predicted_working_role"]]
            default, rivals = preferred, [first, second, "gelernter technischer Ganzname"]
            confidence = min(42, 25 + min(count, 12))
            label, lineage = "C0_PROFILE_GUIDED_WHOLE", "GDT789"
            decision, card_class = "PROFILE_GUIDED_REPLACEABLE_WHOLE_DISPLAY", "PROFILE_GUIDED_COMPLETE_WHOLE"
        elif exact and count >= 2:
            default = "wiederkehrendes Verhältnisfeld"
            rivals = ["Anteilsposten", "Teilmenge", "Wert-/Klassenfeld"]
            confidence, label, lineage = min(38, 25 + count), "C0_RECURRENT_FAMILY_PRIOR", "GDT789"
            decision, card_class = "RECURRENT_COMPLETE_WHOLE_FAMILY_PRIOR", "RECURRENT_WHOLE_FALLBACK"
        elif exact:
            default = "benanntes Verhältnisfeld"
            rivals = ["Anteilsposten", "Teilmenge", "gelernter technischer Ganzname"]
            confidence, label, lineage = 20, "C0_EXACT_SINGLETON_WHOLE", "GDT789"
            decision, card_class = "EXACT_SINGLETON_COMPLETE_WHOLE_PRIOR", "EXACT_SINGLETON_FALLBACK"
        else:
            default = "unbestimmtes Verhältnisfeld"
            rivals = ["Anteilsposten", "Teilmenge", "gelernter technischer Ganzname"]
            confidence, label, lineage = 10, "C0_RAW_READER_WARNING", "GDT789"
            decision, card_class = "RAW_READER_WARNING_ONLY", "RAW_ONLY_FALLBACK"
        if len({default, *rivals}) != 4:
            raise AssertionError(f"non-distinct dictionary options: {surface}")
        if surface in fused and not spec:
            confidence, label = min(45, confidence + 3), label + "_BOUNDARY_BRIDGE"
        positive = (
            f"Vollständige Oberfläche: {census['raw_occurrences']} roh, {count} reader-exakt auf "
            f"{census['reader_exact_physical_folio_count']} Folios. "
            + ("Zusätzlich getrennte X ar-Grenzbrücke. " if surface in fused else "")
            + (f"Nicht freigegebene Profilrivale {role['predicted_working_role']} mit Marge {float(role['winning_margin']):.3f}." if role else "Kein robustes AR/OR-Profilpaar.")
        ) if exact else f"Rohe vollständige Oberfläche mit {census['raw_occurrences']} Vorkommen; keine reader-exakte Kartenlizenz."
        counter = (
            "Der AR-Rest schlägt Xor und gelernte Ganzwörter nur 7/31 in der Stützkohorte und 8/31 in der historischen Ausschlusssicht; "
            "beide R/N-Stufen liefern null Volltreffer. Der Rollenklassifikator verwechselt Mengen- und Wertköpfe. "
            "Die Anzeige ist daher eine ersetzbare Ganzworthypothese, keine ar-Komponente."
        )
        prior = priors.get(surface)
        output.append(zero_ceiling({
            "surface": surface, "card_class": card_class,
            "preferred_working_default_de": default,
            "rival_1_de": rivals[0], "rival_2_de": rivals[1], "rival_3_de": rivals[2],
            "preferred_mechanism": "OBSERVED_COMPLETE_WHOLE_NO_PORTABLE_AR_EXPORT",
            "mechanism_rival_1": "PORTABLE_AR_SHARE_REMAINDER",
            "mechanism_rival_2": "AR_OR_SHELL_CONTRAST", "mechanism_rival_3": "OPAQUE_LEARNED_WHOLE",
            "confidence_0_100_not_probability": confidence, "confidence_label": label,
            "confidence_basis": "EDITORIAL_EVIDENCE_WEIGHT_NOT_FORMULA_NOT_PROBABILITY",
            "display_scope": "READER_EXACT_COMPLETE_WHOLE_ONLY" if exact else "RAW_READER_WARNING_ONLY",
            "lineage_sources": lineage, "lineage_decision": decision,
            "positive_evidence_de": positive, "counterevidence_de": counter,
            "raw_occurrences": census["raw_occurrences"], "raw_page_count": census["raw_page_count"],
            "reader_exact_surface": exact, "reader_exact_occurrences": count,
            "reader_exact_page_count": census["reader_exact_page_count"],
            "reader_exact_physical_folio_count": census["reader_exact_physical_folio_count"],
            "fused_and_separated_boundary_family": int(surface in fused),
            "profile_role_rival": role["predicted_working_role"] if role else "NA",
            "profile_role_selector_usable": role["selector_usable"] if role else 0,
            "replaceable": 1, "gdt789_new_renderer_license": 0, "portable_ar_component_used": 0,
            "prior_gdt734_reading_id": prior["reading_id"] if prior else "NONE",
            "prior_gdt734_default_de": prior["v99r7_spoken_default_de"] if prior else "NONE",
            "prior_gdt734_score_not_probability": prior["working_model_score_0_100_not_probability"] if prior else "NONE",
        }))
    classes = {name: sum(row["card_class"] == name for row in output) for name in sorted({row["card_class"] for row in output})}
    if len(output) != 285 or sum(int(row["reader_exact_surface"]) for row in output) != 225:
        raise AssertionError("dictionary coverage changed")
    if any(not row["preferred_working_default_de"] or not row["positive_evidence_de"] or not row["counterevidence_de"] for row in output):
        raise AssertionError("empty dictionary evidence")
    return output, classes


def build_passages(exact_rows, dictionary):
    cards = {row["surface"]: row for row in dictionary if int(row["reader_exact_surface"])}
    choices = {}
    for row in exact_rows:
        surface = str(row["surface"])
        key = (str(row["page"]), str(row["locus"]), int(row["token_ordinal"]))
        current = choices.get(surface)
        if current is None or key < (str(current["page"]), str(current["locus"]), int(current["token_ordinal"])):
            choices[surface] = row
    if set(choices) != set(cards):
        raise AssertionError("passage/card coverage mismatch")
    output = []
    for number, surface in enumerate(sorted(choices), 1):
        source, card = choices[surface], cards[surface]
        words, ordinal = str(source["current_line"]).split(), int(source["token_ordinal"])
        words[ordinal - 1] = f"⟦{surface} = {card['preferred_working_default_de']}⟧"
        output.append(zero_ceiling({
            "passage_id": f"G789-PASS-{number:03d}", "surface": surface,
            "page": source["page"], "physical_folio": source["physical_folio"],
            "locus": source["locus"], "target_ordinal": ordinal,
            "current_line": source["current_line"], "target_focused_line": " · ".join(words),
            "working_default_de": card["preferred_working_default_de"],
            "rival_1_de": card["rival_1_de"], "rival_2_de": card["rival_2_de"], "rival_3_de": card["rival_3_de"],
            "confidence_0_100_not_probability": card["confidence_0_100_not_probability"],
            "render_status": "DISPLAY_ONLY_COMPLETE_WHOLE_NOT_PLAINTEXT",
            "gdt789_new_renderer_license": 0, "portable_ar_component_used": 0,
        }))
    return output


def build_historical_controls():
    rows = {row["source_id"]: row for row in read_tsv(G735_ARCHITECTURE)}
    return [zero_ceiling({
        "source_id": source_id, "work": rows[source_id]["work"],
        "date_band": rows[source_id]["date_band"], "record_channels": rows[source_id]["record_channels"],
        "observed_slots": rows[source_id]["observed_slots"],
        "architecture_use": "LEARNED_WHOLES_PLUS_BOUND_AMOUNT_VALUE_PART_AND_QUALITY_FIELDS_ONLY",
        "selects_ar_identity": 0, "selects_ar_segmentation": 0,
    }) for source_id in ("HSR008", "HSR010")]


def build_relation_rows(spans, dictionary):
    cards = {row["surface"]: row for row in dictionary}
    packet, crosswalk = [], []
    for number, span in enumerate(spans, 1):
        edge_id, locus = f"G789-E{number:03d}", str(span["locus"])
        left_ordinal, right_ordinal = int(span["left_token_ordinal"]), int(span["right_token_ordinal"])
        packet.append({
            "edge_id": edge_id, "batch_id": "GDT789_SEPARATED_X_AR_SPANS",
            "page": span["page"], "physical_folio": span["physical_folio"], "diagram_unit_id": f"LINE:{locus}",
            "pivot_visual_id": f"TOKEN:{locus}:{left_ordinal}", "pivot_locus": f"{locus}@{left_ordinal}",
            "target_visual_id": f"TOKEN:{locus}:{right_ordinal}", "target_locus": f"{locus}@{right_ordinal}",
            "relation_type": "X_PRECEDES_AR_SEPARATED", "direction_basis": "TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_FIELD_ADJACENCY", "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT789", "page_crop_sha256": "NONE",
            "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT789_RUNNER", "relation_reviewer": "GDT789_VALIDATOR",
            "relation_confidence": "EXPLORATORY", "ambiguity_state": "BOUNDARY_C2_SEMANTICS_C0",
            "formal_access_state": "SEALED_NOT_ACCESSED", "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
        left, fused = str(span["left_surface"]), str(span["left_surface"]) + "ar"
        crosswalk.append(zero_ceiling({
            "edge_id": edge_id, "batch_id": "GDT789_SEPARATED_X_AR_SPANS",
            "page": span["page"], "physical_folio": span["physical_folio"], "locus": locus,
            "left_surface": left, "separated_pair": span["separated_pair"],
            "fused_surface_if_target_family_observed": fused if fused in cards else "NONE",
            "working_ar_default_de": cards["ar"]["preferred_working_default_de"],
            "semantic_score_eligible": 0,
        }))
    if len(packet) != 192:
        raise AssertionError("relation packet count changed")
    return packet, crosswalk


def guarded_source_stats(corpus):
    guard, stolfi = corpus["guard"], corpus["stolfi_guard"]
    return [{
        "source": name, "selected_rows": guard[name]["selected"], "skipped_forbidden": guard[name]["skipped_forbidden"],
        "skipped_not_allowed": guard[name]["skipped_not_allowed"], "base_allowed_pages": guard["allowed_pages"],
        "query_allow_pages": guard["allowed_pages"], "f84_rows_materialised": 0,
    } for name in ("tokens", "cross", "lines")] + [{
        "source": "stolfi", "selected_rows": stolfi["selected"], "skipped_forbidden": stolfi["skipped_forbidden"],
        "skipped_not_allowed": stolfi["skipped_not_allowed"], "base_allowed_pages": guard["allowed_pages"],
        "query_allow_pages": corpus["diagnostics"]["stolfi_requested_pages"], "f84_rows_materialised": 0,
    }]


def artifact_readme() -> str:
    return """# GDT789 artifacts

These files exhaust the longest-ending `*ar` family after assigning `*dar` to
its already tested longer tail. The primary new comparison predicts complete
`Xar` wholes from complete `Xor`, bare `ar`, and bare `or`; it never interprets
EVA letters. A support-first 31-prefix cohort, a mechanically defined but
partly overlapping 31-prefix historical-exclusion cohort, all 47 robust pairs,
and two R/N level grids are reported separately.

Every observed target surface has a short replaceable working card with
confidence, evidence, counterevidence, and three rivals. These are display
hypotheses for complete words, not recovered plaintext. The 192 relation rows
record transcription-order adjacency only and are intentionally not
score-ready visual relation evidence.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    args = parser.parse_args()
    artifacts = args.artifacts_dir.resolve()
    lock_count, lock_hash = verify_locks()
    corpus = load_module("gdt789_corpus", CORPUS_MODULE).compute(ROOT)
    model = load_module("gdt789_model", MODEL_MODULE).compute(ROOT)
    dictionary, dictionary_classes = build_dictionary(corpus, model, read_tsv(OVERRIDES))
    passages = build_passages(corpus["exact_occurrence_rows"], dictionary)
    historical = build_historical_controls()
    packet, crosswalk = build_relation_rows(corpus["clean_exact_separated_rows"], dictionary)
    tsv_outputs = {
        "GDT789_285_AR_FAMILY_CENSUS.tsv": corpus["family_rows"],
        "GDT789_1348_AR_EXACT_OCCURRENCES.tsv": corpus["exact_occurrence_rows"],
        "GDT789_40_GDT788_SQUARE_REFERENCE.tsv": corpus["square_lattice_rows"],
        "GDT789_94_ROBUST_AR_OR_LATTICE.tsv": corpus["ar_or_lattice_rows"],
        "GDT789_28_RN12_LATTICE.tsv": corpus["rn12_lattice_rows"],
        "GDT789_24_RN23_LATTICE.tsv": corpus["rn23_lattice_rows"],
        "GDT789_318_RAW_X_AR_SPANS.tsv": corpus["raw_separated_rows"],
        "GDT789_192_EXACT_X_AR_SPANS.tsv": corpus["clean_exact_separated_rows"],
        "GDT789_20_FUSED_SPLIT_FAMILIES.tsv": corpus["fused_split_rows"],
        "GDT789_1348_STOLFI_BOUNDARY_OCCURRENCES.tsv": corpus["stolfi_occurrence_rows"],
        "GDT789_225_STOLFI_BOUNDARY_SUMMARY.tsv": corpus["stolfi_summary_rows"],
        "GDT789_13_BARE_HEAD_CONSTRUCTIONS.tsv": corpus["construction_rows"],
        "GDT789_96_FOLIO_BALANCED_PROFILES.tsv": model["profile_rows"],
        "GDT789_2140_SEMANTIC_LEAKAGE_MASK.tsv": model["mask_rows"],
        "GDT789_47_LEARNED_WHOLE_CONTROLS.tsv": model["donor_rows"],
        "GDT789_47_AR_OR_TRANSFER.tsv": model["primary_rows"],
        "GDT789_15_TRANSFER_SUMMARY.tsv": model["summary_rows"],
        "GDT789_658_AXIS_CONTRASTS.tsv": model["axis_rows"],
        "GDT789_42_AXIS_SUMMARY.tsv": model["axis_summary_rows"],
        "GDT789_94_VALUE_BINDING_SIGNATURES.tsv": model["construction_rows"],
        "GDT789_13_RN_TRANSFER.tsv": model["rn_rows"],
        "GDT789_8_RN_SUMMARY.tsv": model["rn_summary_rows"],
        "GDT789_253_ROLE_PROTOTYPE_LOO.tsv": model["prototype_rows"],
        "GDT789_3_ROLE_PROTOTYPE_SUMMARY.tsv": model["prototype_summary_rows"],
        "GDT789_97_TARGET_ROLE_PROFILES.tsv": model["target_role_rows"],
        "GDT789_285_WORKING_DICTIONARY.tsv": dictionary,
        "GDT789_225_PRACTICAL_PASSAGES.tsv": passages,
        "GDT789_2_HISTORICAL_ARCHITECTURE_CONTROLS.tsv": historical,
        "GDT789_GUARDED_SOURCE_STATS.tsv": guarded_source_stats(corpus),
        "GDT789_RELATION_EDGE_CROSSWALK.tsv": crosswalk,
    }
    for name, rows in tsv_outputs.items():
        write_tsv(artifacts / name, rows)
    packet_path = artifacts / "GDT789_GDT388_192_SEPARATED_SPAN_PACKET.tsv"
    write_tsv(packet_path, packet, EDGE_COLUMNS)
    intake = load_module("gdt789_relation_intake", RELATION_INTAKE).validate_relation_edge_packet(packet_path)
    if intake["status"] != "VALID_ACQUISITION_NOT_SCORE_READY" or intake["errors"]:
        raise AssertionError(f"unexpected relation intake: {intake}")
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", intake)
    support = next(row for row in model["summary_rows"] if row["cohort"] == "SUPPORT_PRIMARY_31" and row["view"] == "FULL")
    exclusion = next(row for row in model["summary_rows"] if row["cohort"] == "HISTORICAL_EXCLUSION_31" and row["view"] == "FULL")
    result = {
        "experiment_id": "GDT789", "status": STATUS, "source_locks": lock_count,
        "source_lock_sha256": lock_hash, "override_spec_sha256": sha256(OVERRIDES),
        "corpus": corpus["diagnostics"],
        "model": {"support_primary_31": support, "historical_exclusion_31": exclusion,
                  "diagnostics": model["diagnostics"], "recommendation": model["diagnostics"]["recommendation"]},
        "dictionary": {"raw_forms_with_nonempty_defaults": len(dictionary),
                       "reader_exact_display_cards": sum(int(row["reader_exact_surface"]) for row in dictionary),
                       "raw_reader_warning_cards": sum(not int(row["reader_exact_surface"]) for row in dictionary),
                       "classes": dictionary_classes, "new_renderer_licenses": 0, "portable_component_exports": 0},
        "adjudication": {"formal_ar_family": "C1_RETAINED_STRONG",
                         "portable_ar_remainder": "C0_INACTIVE__WHOLE_ONLY",
                         "bare_ar_default_de": "Anteil",
                         "bare_ar_scope": "COMPLETE_WORD_RELATIVE_AMOUNT_OR_RATIO_HEAD",
                         "bare_ar_live_rivals": ["Portion oder Teilmenge", "Stoffklasse", "Wertfeld"],
                         "implicit_level_i": "REMOVED", "automatic_ar_suffix_meaning": "NOT_LICENSED",
                         "default_long_form_mechanism": "LEARNED_OR_FORM_SPECIFIC_COMPLETE_WHOLE",
                         "next_remainder": "ol"},
        "relation_packet": intake,
        "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "specific_substances": 0,
        "component_exports": 0, "new_pages": 0, "new_images": 0, "new_ocr": 0,
        "new_transcriptions": 0, "sealed_pages_accessed": 0,
        "claim_ceiling": "C2 observed current-reader complete-word boundaries; C1 formal AR/OR family and bare ar role head; C0 German complete-whole displays; zero portable component, lexeme, plaintext, or substance.",
    }
    write_json(artifacts / "RESULT.json", result)
    (artifacts / "README.md").write_text(artifact_readme(), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
