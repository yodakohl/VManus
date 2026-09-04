#!/usr/bin/env python3
"""Independently validate GDT795 and two byte-identical builder replays."""

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
from typing import Any

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt795_source_native_family_kluge_transfer"
SRC = BASE / "src"
ART = BASE / "artifacts"
RUN = SRC / "run.py"
LOCK = SRC / "SOURCE_LOCK.tsv"
RELATION_INTAKE = ROOT / "tools/relation_edge_intake.py"

OUTPUT_NAMES = (
    "GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv",
    "GDT795_11_RECURRENT_FAMILY_SIGNATURES.tsv",
    "GDT795_26_LOFO_BOUNDARY_FAMILY_TARGETS.tsv",
    "GDT795_EXACT_REPRESENTATION_SUMMARY.tsv",
    "GDT795_99_FAMILY_SIMILARITY_PREDICTIONS.tsv",
    "GDT795_SIMILARITY_MODEL_SUMMARY.tsv",
    "GDT795_SHARED_TEMPLATE_TRANSFORMS.tsv",
    "GDT795_RELATIVE_DISTANCE_AUDIT.tsv",
    "GDT795_5_CONTEXTUAL_POSITION_CARDS.tsv",
    "GDT795_CANDIDATE_ADJUDICATION.tsv",
    "GDT795_RELATION_EDGE_PACKET.tsv",
    "GDT795_HOMOLOG_VS_LOCAL_ORDER_MATCHES.tsv",
    "RESULT.json",
)

REQUIRED_LOCK_PATHS = {
    "experiments/yolo/gdt795_source_native_family_kluge_transfer/METHOD.md",
    "experiments/yolo/gdt795_source_native_family_kluge_transfer/PREREGISTRATION.md",
    "experiments/yolo/gdt795_source_native_family_kluge_transfer/src/GUARDED_QUERY_SPECS.tsv",
    "experiments/yolo/gdt795_source_native_family_kluge_transfer/src/CANDIDATE_MODEL_SPECS.tsv",
    "experiments/yolo/gdt795_source_native_family_kluge_transfer/src/run.py",
    "experiments/yolo/gdt795_source_native_family_kluge_transfer/src/validate.py",
    "experiments/yolo/gdt794_complete_label_multiform_slot_transfer/artifacts/GDT794_216_ADMITTED_CIRCLE_LABEL_ATLAS.tsv",
    "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv",
    "gdt233_prefix_manifest.tsv",
}

EXPECTED_SCHEMAS = {
    OUTPUT_NAMES[0]: (
        "family_atlas_ordinal", "template_id", "template_period", "physical_folio",
        "source_selector", "array_id", "locus", "slot_index", "slot_count",
        "kluge_a_member", "complete_label_surface", "label_token_count",
        "zl_boundary_family", "it_boundary_family", "rf_boundary_family",
        "zl_member_sequence", "it_member_sequence", "rf_member_sequence",
        "member_sequence_max_support", "member_sequence_agreement",
        "canonical_boundary_family", "canonical_compact_family",
        "boundary_reader_support", "compact_reader_support",
        "boundary_supporting_editions", "compact_supporting_editions",
        "agreement_class", "zl_group_count", "it_group_count", "rf_group_count",
        "transferred_prefix", "strict_residual", "zl_alternative_sites",
        "it_alternative_sites", "rf_alternative_sites", "zl_nearest_eva",
        "it_nearest_eva", "rf_nearest_eva", "source_family_semantics",
        "component_export_credit",
    ),
    OUTPUT_NAMES[1]: (
        "canonical_boundary_family", "occurrence_count", "distinct_surface_count",
        "complete_label_surfaces", "physical_folio_count", "physical_folios",
        "template_ids", "a_members", "distinct_a_count",
        "cross_folio_same_a_members", "cross_folio_same_a_family_pair_count",
        "same_a_exact_zl_member_pair_count", "working_default_de", "confidence",
        "evidence", "counterevidence", "renderer_license",
        "component_export_credit", "confirmed_lexeme",
    ),
    OUTPUT_NAMES[2]: (
        "representation_id", "representation_key", "held_physical_folio",
        "target_source_selector", "target_template_id", "target_locus",
        "target_surface", "target_a_member", "training_event_count",
        "training_physical_folios", "training_templates", "training_a_members",
        "training_surfaces", "any_training_exact_a", "any_training_within_one_a",
        "circular_mean_predicted_a", "circular_mean_distance",
        "same_template_training_events", "same_template_any_exact_a",
        "same_template_any_within_one_a", "interpretation_ceiling",
    ),
    OUTPUT_NAMES[3]: (
        "representation_id", "target_event_count", "cross_folio_key_count",
        "any_training_exact_a_count", "any_training_exact_a_rate",
        "any_training_within_one_count", "any_training_within_one_rate",
        "circular_mean_exact_count", "circular_mean_within_one_count",
        "circular_mean_distance", "null_iterations", "null_mean_any_exact_count",
        "null_p_any_exact_ge_observed", "null_mean_circular_distance",
        "null_p_distance_le_observed", "gate_result", "component_export_credit",
    ),
    OUTPUT_NAMES[4]: (
        "representation_id", "held_physical_folio", "target_locus", "target_surface",
        "target_a_member", "candidate_a_count", "true_a_similarity", "rank_low",
        "rank_high", "normalized_midrank", "tie_adjusted_reciprocal_rank",
        "top_a_members", "top_similarity", "fractional_top1_credit",
        "fractional_within_one_credit", "top_support_loci", "top_support_surfaces",
        "interpretation_ceiling",
    ),
    OUTPUT_NAMES[5]: (
        "representation_id", "target_event_count", "fractional_top1",
        "fractional_within_one", "tie_adjusted_mrr", "mean_normalized_rank",
        "null_iterations", "null_mean_fractional_top1", "null_p_top1_ge_observed",
        "null_mean_mrr", "null_p_mrr_ge_observed", "null_mean_rank",
        "null_p_rank_le_observed", "gate_result", "semantic_export",
    ),
    OUTPUT_NAMES[6]: (
        "model_id", "template_id", "left_page", "right_pages", "period",
        "common_exact_family_count", "common_exact_families",
        "native_comparable_positions", "native_exact_hits", "native_matches",
        "best_orientation", "best_shift", "best_comparable_positions",
        "best_exact_hits", "best_matches", "null_iterations", "null_mean_best_hits",
        "null_p_best_hits_ge_observed", "gate_result", "component_export_credit",
    ),
    OUTPUT_NAMES[7]: (
        "left_signature", "right_signature", "f70_left_a", "f70_right_a",
        "f72_left_a", "f72_right_a", "f70_signed_distance", "f72_signed_distance",
        "f70_unsigned_distance", "f72_unsigned_distance",
        "absolute_distance_difference", "candidate", "evidence_status",
        "component_export_credit",
    ),
    OUTPUT_NAMES[8]: (
        "locus", "physical_folio", "source_selector", "template_id",
        "kluge_a_member", "complete_label_surface", "canonical_boundary_family",
        "zl_member_sequence", "working_default_de", "confidence", "evidence",
        "counterevidence", "renderer_license", "prose_export_allowed",
        "component_export_credit", "confirmed_lexeme",
    ),
    OUTPUT_NAMES[9]: (
        "model_id", "unit", "concrete_interpretation", "selection_requirement",
        "selected_working_model", "gate_result", "evidence_and_counterevidence",
        "component_export_credit", "confirmed_lexeme",
    ),
    OUTPUT_NAMES[10]: (
        "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
        "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
        "relation_type", "direction_basis", "ownership_basis",
        "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
        "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer",
        "relation_reviewer", "relation_confidence", "ambiguity_state",
        "formal_access_state", "fold_assignment", "eligibility_status",
    ),
    OUTPUT_NAMES[11]: (
        "scope", "representation_id", "edge_count", "observed_exact_matches",
        "observed_match_rate", "null_iterations", "null_mean_matches",
        "null_p_matches_ge_observed", "interpretation", "semantic_export",
    ),
}

EXPECTED_STATUS = (
    "PARTIAL__101_KLUGE_LOCI__394_GUARDED_GROUP_ROWS__2122_SEALED_ROWS_REJECTED_PRE_MATERIALIZATION__"
    "81_ALL3_BOUNDARY__11_BOUNDARY_ONLY_DISAGREEMENTS__9_FAMILY_DISAGREEMENTS_RESOLVED_2OF3__"
    "55_ALL3_MEMBER_SEQUENCES__74_BOUNDARY_SIGNATURES__73_COMPACT_SIGNATURES__11_RECURRENT__"
    "26_EXACT_LOFO_TARGETS__4_ANY_EXACT_A__6_ANY_PM1__ZERO_EXACT_MEMBER_SAME_K__"
    "T15_TWO_CONTEXTUAL_ANCHORS__SHARED_TRANSFORMS_FAIL__LOCAL_PREFIX_BLOCKING_35_OF_87__WEAK_FAMILY_TEXTURE__"
    "LEARNED_MEMBER_PLUS_GRAPHICAL_LAYER_PRIMARY__ZERO_COMPONENT_EXPORT__ZERO_CONFIRMED_LEXEMES"
)

EXPECTED_SCOPE = {
    "admitted_kluge_loci": 101,
    "physical_folios": 3,
    "source_selectors": 5,
    "new_pages_or_images_opened": 0,
    "mixed_sources_queried": 1,
    "guard_selected_rows": 394,
    "sealed_rows_rejected_before_materialization": 2122,
    "sealed_rows_materialized": 0,
}

EXPECTED_COUNTS = {
    "all3_boundary_and_family": 81,
    "all3_family_boundary_majority": 11,
    "family_two_of_three": 9,
    "all3_member_sequences": 55,
    "member_sequence_two_of_three": 36,
    "member_sequence_all_different": 10,
    "canonical_family_signatures": 74,
    "compact_family_signatures": 73,
    "visible_complete_surfaces": 93,
    "recurrent_family_signatures": 11,
    "recurrent_family_events": 38,
    "exact_boundary_lofo_targets": 26,
    "exact_boundary_any_exact_a": 4,
    "exact_boundary_any_pm1": 6,
    "similarity_targets": 99,
    "contextual_position_cards": 5,
    "selected_context_cards": 4,
    "cross_chart_same_k_pairs": 156,
    "consecutive_source_slot_edges": 87,
    "consecutive_same_prefix_edges": 35,
    "component_exports": 0,
    "confirmed_lexemes": 0,
}

EXPECTED_DECISIONS = {
    "full_family_position_codebook": "NOT_SELECTED",
    "t15_two_anchor_seed": "RETAIN_CONTEXTUAL_COMPLETE_SIGNATURE_CARDS",
    "shared_diagram_transform": "NOT_SELECTED",
    "relative_distance": "ONE_SIX_TO_SEVEN_MEMBER_RIVAL__NOT_EXTERNAL_RELATION_EVIDENCE",
    "family_similarity": "WEAK_FORM_TEXTURE_ONLY",
    "local_prefix_blocking": "SELECTED_AS_GRAPHICAL_RENDERER_STRUCTURE_NOT_CONTENT",
    "same_k_member_identity": "ZERO_OF_156_CROSS_CHART_PAIRS",
    "selected_primary_model": "LEARNED_MEMBER_PLUS_GRAPHICAL_LAYER",
    "next": "TEST_T15_POSITION_CARDS_AGAINST_VISIBLE_FIGURE_ATTRIBUTES_AND_RUNNING_PROSE_HOSTS_WITHOUT_EXPORTING_FAMILY_COMPONENTS",
}


def read_tsv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        return tuple(reader.fieldnames or ()), rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_module(name: str, path: Path):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(label)


def write_validation(audit: Audit, **extra: Any) -> int:
    payload: dict[str, Any] = {
        "status": "PASS" if not audit.failures else "FAIL",
        "checks": audit.checks,
        "failures": audit.failures,
        **extra,
    }
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "VALIDATION.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not audit.failures else 1


def main() -> int:
    audit = Audit()

    audit.check(LOCK.is_file(), "source lock exists")
    if LOCK.is_file():
        lock_fields, lock_rows = read_tsv(LOCK)
        audit.check(lock_fields == ("path", "sha256", "role"), "source lock exact schema")
        paths = [row.get("path", "") for row in lock_rows]
        audit.check(set(paths) == REQUIRED_LOCK_PATHS, "source lock exact path set")
        audit.check(len(paths) == len(set(paths)), "source lock paths unique")
        audit.check(all(row.get("role", "") for row in lock_rows), "source lock roles populated")
        for row in lock_rows:
            raw_path = row.get("path", "")
            relative = Path(raw_path)
            contained = bool(raw_path) and not relative.is_absolute() and ".." not in relative.parts
            audit.check(contained, f"contained lock path {raw_path}")
            if not contained:
                continue
            path = ROOT / relative
            audit.check(path.is_file(), f"locked source exists {raw_path}")
            expected_hash = row.get("sha256", "")
            audit.check(
                len(expected_hash) == 64 and all(char in "0123456789abcdef" for char in expected_hash),
                f"locked source hash format {raw_path}",
            )
            if path.is_file():
                audit.check(sha256(path) == expected_hash, f"locked source hash {raw_path}")

    for name in OUTPUT_NAMES:
        audit.check((ART / name).is_file(), f"canonical artifact exists {name}")
    if audit.failures:
        return write_validation(
            audit,
            builder_replays_completed=0,
            canonical_outputs_compared=0,
            gdt388_edge_packet_checked=False,
            new_pages_or_images_opened=0,
            sealed_rows_materialized=0,
        )

    replay_one: dict[str, bytes] = {}
    completed_replays = 0
    for replay_index in (1, 2):
        with tempfile.TemporaryDirectory(prefix=f".gdt795_replay_{replay_index}_", dir=BASE) as tmp:
            completed = subprocess.run(
                [sys.executable, str(RUN), "--output-dir", tmp],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            audit.check(completed.returncode == 0, f"builder replay {replay_index} exits zero")
            audit.check(completed.stdout.strip() == EXPECTED_STATUS, f"builder replay {replay_index} exact status")
            audit.check(not completed.stderr.strip(), f"builder replay {replay_index} empty stderr")
            if completed.returncode == 0:
                completed_replays += 1
            for name in OUTPUT_NAMES:
                replay = Path(tmp) / name
                canonical = ART / name
                audit.check(replay.is_file(), f"replay {replay_index} artifact exists {name}")
                if not replay.is_file():
                    continue
                replay_bytes = replay.read_bytes()
                audit.check(replay_bytes == canonical.read_bytes(), f"byte replay {replay_index} canonical {name}")
                if replay_index == 1:
                    replay_one[name] = replay_bytes
                else:
                    audit.check(replay_bytes == replay_one.get(name), f"byte equality replay 1 versus 2 {name}")

    artifacts: dict[str, list[dict[str, str]]] = {}
    for name, expected_schema in EXPECTED_SCHEMAS.items():
        fields, rows = read_tsv(ART / name)
        audit.check(fields == expected_schema, f"exact schema {name}")
        artifacts[name] = rows

    atlas = artifacts[OUTPUT_NAMES[0]]
    recurrent = artifacts[OUTPUT_NAMES[1]]
    exact_targets = artifacts[OUTPUT_NAMES[2]]
    exact_summary = artifacts[OUTPUT_NAMES[3]]
    similarity_targets = artifacts[OUTPUT_NAMES[4]]
    similarity_summary = artifacts[OUTPUT_NAMES[5]]
    transforms = artifacts[OUTPUT_NAMES[6]]
    distances = artifacts[OUTPUT_NAMES[7]]
    cards = artifacts[OUTPUT_NAMES[8]]
    adjudication = artifacts[OUTPUT_NAMES[9]]
    edge_packet = artifacts[OUTPUT_NAMES[10]]
    order_matches = artifacts[OUTPUT_NAMES[11]]
    result = json.loads((ART / OUTPUT_NAMES[12]).read_text(encoding="utf-8"))

    audit.check(len(atlas) == 101 and len({row["locus"] for row in atlas}) == 101, "101 unique Kluge loci")
    audit.check([int(row["family_atlas_ordinal"]) for row in atlas] == list(range(1, 102)), "atlas ordinals 1 through 101")
    audit.check(len({row["array_id"] for row in atlas}) == 11, "11 Kluge arrays")
    audit.check(Counter(row["physical_folio"] for row in atlas) == Counter({"f70": 43, "f71": 15, "f72": 43}), "Kluge loci split 43 15 43")
    audit.check(Counter(row["source_selector"] for row in atlas) == Counter({"f70v1": 14, "f71v": 15, "f72r1": 14, "f70v2": 29, "f72r2": 29}), "five source-selector capacities")
    audit.check(Counter(row["template_id"] for row in atlas) == Counter({"T15": 43, "T30": 58}), "T15 and T30 capacities")
    audit.check(all(int(row["template_period"]) == (15 if row["template_id"] == "T15" else 30) for row in atlas), "template periods agree with template IDs")
    audit.check(len({row["complete_label_surface"] for row in atlas}) == 93, "93 visible complete surfaces")
    audit.check(len({row["canonical_boundary_family"] for row in atlas}) == 74, "74 boundary family signatures")
    audit.check(len({row["canonical_compact_family"] for row in atlas}) == 73, "73 compact family signatures")
    audit.check(sum(int(row["label_token_count"]) for row in atlas) == 131, "131 visible label tokens")
    audit.check(sum(int(row["label_token_count"]) > 1 for row in atlas) == 23, "23 multi-token labels")
    audit.check(sum(int(row["zl_group_count"]) for row in atlas) == 131, "131 ZL source groups")
    audit.check(sum(int(row["it_group_count"]) for row in atlas) == 136, "136 IT source groups")
    audit.check(sum(int(row["rf_group_count"]) for row in atlas) == 127, "127 RF source groups")
    audit.check(sum(sum(int(row[field]) for row in atlas) for field in ("zl_group_count", "it_group_count", "rf_group_count")) == 394, "394 guarded source groups accounted for")
    audit.check(all(int(row["zl_group_count"]) == int(row["label_token_count"]) for row in atlas), "ZL word boundaries preserve every multi-token label")
    audit.check(all(row["canonical_boundary_family"].replace("|", "") == row["canonical_compact_family"] for row in atlas), "compact family removes boundaries only")
    audit.check(Counter(row["agreement_class"] for row in atlas) == Counter({"ALL3_BOUNDARY_AND_FAMILY": 81, "ALL3_FAMILY__BOUNDARY_2OF3": 11, "FAMILY_2OF3": 9}), "boundary-family agreement census")
    audit.check(Counter(row["member_sequence_agreement"] for row in atlas) == Counter({"ALL3_MEMBER_SEQUENCE": 55, "MEMBER_SEQUENCE_2OF3": 36, "MEMBER_SEQUENCE_ALL_DIFFERENT": 10}), "source-member agreement census")
    audit.check(all(int(row["boundary_reader_support"]) >= 2 and int(row["compact_reader_support"]) >= 2 for row in atlas), "every canonical family has a reader majority")
    audit.check(not any(row["locus"].startswith("f84") or row["source_selector"].startswith("f84") for row in atlas), "atlas excludes sealed f84 selectors")
    audit.check(all(row["source_family_semantics"] == "FORMAL_TRANSCRIPTION_FAMILY__NOT_AUTHORIAL_WORD_OR_SOUND" for row in atlas), "atlas family channel remains formal")
    audit.check(all(row["component_export_credit"] == "ZERO" for row in atlas), "atlas exports no component")

    audit.check(len(recurrent) == 11 and sum(int(row["occurrence_count"]) for row in recurrent) == 38, "11 recurrent signatures covering 38 events")
    audit.check(len({row["canonical_boundary_family"] for row in recurrent}) == 11, "recurrent signatures unique")
    audit.check({row["canonical_boundary_family"] for row in recurrent if row["renderer_license"] == "CONTEXTUAL_CIRCLE_CARD_ONLY"} == {"AQABAB", "AQABAG"}, "only two recurrent signatures receive contextual cards")
    audit.check(sum(int(row["cross_folio_same_a_family_pair_count"]) for row in recurrent) == 2, "two cross-folio same-A family pairs")
    audit.check(sum(int(row["same_a_exact_zl_member_pair_count"]) for row in recurrent) == 0, "zero exact source-member same-A pairs")
    audit.check(all(row["working_default_de"] and row["evidence"] and row["counterevidence"] for row in recurrent), "recurrent defaults carry evidence and counterevidence")
    audit.check(all(row["component_export_credit"] == "ZERO" and row["confirmed_lexeme"] == "NO" for row in recurrent), "recurrent cards respect semantic ceiling")

    expected_exact = {
        "VISIBLE_COMPLETE_SURFACE": (6, 3, 0, 2),
        "ZL_MEMBER_SEQUENCE": (4, 2, 0, 2),
        "BOUNDARY_FAMILY": (26, 7, 4, 6),
        "COMPACT_FAMILY": (27, 7, 4, 6),
        "TRANSFERRED_PREFIX": (65, 5, 30, 43),
        "FORMAL_RESIDUAL": (37, 7, 6, 11),
    }
    exact_by_id = {row["representation_id"]: row for row in exact_summary}
    audit.check(len(exact_summary) == 6 and set(exact_by_id) == set(expected_exact), "six exact representation summaries")
    audit.check(all((int(exact_by_id[key]["target_event_count"]), int(exact_by_id[key]["cross_folio_key_count"]), int(exact_by_id[key]["any_training_exact_a_count"]), int(exact_by_id[key]["any_training_within_one_count"])) == expected for key, expected in expected_exact.items()), "exact representation core counts")
    audit.check(exact_by_id["BOUNDARY_FAMILY"]["gate_result"] == "TWO_ANCHORS_ONLY__FAIL_SEVERAL_POSITION_CODEBOOK", "boundary family fails several-position codebook gate")
    audit.check(all(row["component_export_credit"] == "ZERO" for row in exact_summary), "exact summaries export no component")
    audit.check(len(exact_targets) == 26 and all(row["representation_id"] == "BOUNDARY_FAMILY" for row in exact_targets), "26 boundary-family LOFO targets")
    audit.check(sum(row["any_training_exact_a"] == "YES" for row in exact_targets) == 4, "four exact-A boundary targets")
    audit.check(sum(row["any_training_within_one_a"] == "YES" for row in exact_targets) == 6, "six within-one-A boundary targets")
    audit.check(all(row["interpretation_ceiling"] == "COMPLETE_FORMAL_SIGNATURE_POSITION_DIAGNOSTIC_ONLY" for row in exact_targets), "exact targets stay formal position diagnostics")

    audit.check(len(similarity_targets) == 99 and len({row["target_locus"] for row in similarity_targets}) == 99, "99 family-similarity targets")
    audit.check(all(row["representation_id"] == "BOUNDARY_FAMILY_EDIT" for row in similarity_targets), "published similarity target representation")
    audit.check(all(row["interpretation_ceiling"] == "APPROXIMATE_FORM_TEXTURE_POSITION_DIAGNOSTIC_ONLY" for row in similarity_targets), "similarity targets stay texture diagnostics")
    similarity_by_id = {row["representation_id"]: row for row in similarity_summary}
    audit.check(len(similarity_summary) == 3 and set(similarity_by_id) == {"BOUNDARY_FAMILY_EDIT", "COMPACT_FAMILY_EDIT", "VISIBLE_SURFACE_EDIT"}, "three similarity model summaries")
    audit.check(all(int(row["target_event_count"]) == 99 and int(row["null_iterations"]) == 500 for row in similarity_summary), "similarity models use 99 targets and 500 nulls")
    audit.check(similarity_by_id["BOUNDARY_FAMILY_EDIT"]["gate_result"] == similarity_by_id["COMPACT_FAMILY_EDIT"]["gate_result"] == "WEAK_FORM_TEXTURE_ONLY", "family similarities are weak texture only")
    audit.check(similarity_by_id["VISIBLE_SURFACE_EDIT"]["gate_result"] == "VISIBLE_SURFACE_BASELINE_FAIL", "visible-surface baseline fails")
    audit.check(all(row["semantic_export"] == "NONE" for row in similarity_summary), "similarity models export no semantics")

    audit.check(len(transforms) == 5 and len({row["model_id"] for row in transforms}) == 5, "five shared-template transform tests")
    audit.check(max(int(row["best_exact_hits"]) for row in transforms) == 2, "no shared transform reaches three exact signatures")
    audit.check(all(row["gate_result"].startswith("FAIL_") for row in transforms), "every shared transform fails")
    audit.check(all(row["component_export_credit"] == "ZERO" for row in transforms), "shared transforms export no component")
    joint = next(row for row in transforms if row["model_id"] == "T15_ONE_TRANSFORM_AGAINST_TWO_PAGES")
    audit.check((joint["common_exact_families"], joint["best_exact_hits"], joint["gate_result"]) == ("AQABAB|AQABAG", "1", "FAIL_ONE_SHARED_TRANSFORM__THE_TWO_ANCHORS_REQUIRE_DIFFERENT_SHIFTS"), "two T15 anchors do not share one transform")

    audit.check(len(distances) == 3, "three relative-distance comparisons")
    audit.check(sum(row["candidate"] == "SIX_TO_SEVEN_MEMBER_INTERVAL" for row in distances) == 1, "one six-to-seven-member interval rival")
    audit.check(all(row["evidence_status"] == "ANALYTICAL_CATALOGUE_DISTANCE__NOT_GDT388_EXTERNAL_RELATION_EDGE" and row["component_export_credit"] == "ZERO" for row in distances), "relative distances are not external relation evidence")

    audit.check(len(cards) == 5 and len({row["locus"] for row in cards}) == 5, "five contextual position cards")
    audit.check(sum(row["renderer_license"] == "SELECTED_CONTEXT_CARD" for row in cards) == 4, "four selected contextual cards")
    audit.check(Counter(row["canonical_boundary_family"] for row in cards) == Counter({"AQABAB": 2, "AQABAG": 3}), "cards cover two complete family signatures")
    aqabab_cards = [row for row in cards if row["canonical_boundary_family"] == "AQABAB"]
    audit.check({row["kluge_a_member"] for row in aqabab_cards} == {"9"} and len({row["zl_member_sequence"] for row in aqabab_cards}) == 2, "AQABAB position card retains member-sequence disagreement")
    audit.check(all(row["prose_export_allowed"] == "NO" and row["component_export_credit"] == "ZERO" and row["confirmed_lexeme"] == "NO" for row in cards), "context cards cannot enter prose or export components")
    audit.check(all(row["evidence"] and row["counterevidence"] for row in cards), "all position cards carry evidence and counterevidence")

    audit.check(len(adjudication) == 6 and len({row["model_id"] for row in adjudication}) == 6, "six candidate models adjudicated")
    selected = [row for row in adjudication if row["selected_working_model"] == "YES"]
    audit.check(len(selected) == 1 and selected[0]["model_id"] == "LEARNED_MEMBER_PLUS_GRAPHIC_LAYER" and selected[0]["gate_result"] == "SELECTED_PRIMARY", "learned member plus graphic layer is sole primary model")
    audit.check(next(row for row in adjudication if row["model_id"] == "FULL_FAMILY_A_CODE")["gate_result"] == "FAIL", "full family A-code rejected")
    audit.check(all(row["component_export_credit"] == "ZERO" and row["confirmed_lexeme"] == "NO" for row in adjudication), "adjudication exports no components or lexemes")

    audit.check(len(order_matches) == 8, "eight homolog-versus-local-order tests")
    audit.check(Counter(row["scope"] for row in order_matches) == Counter({"CROSS_CHART_SAME_K": 4, "CONSECUTIVE_SOURCE_SLOT": 4}), "four representations in each order scope")
    audit.check(all(int(row["edge_count"]) == (156 if row["scope"] == "CROSS_CHART_SAME_K" else 87) for row in order_matches), "156 homolog and 87 local edges")
    fixed_member = next(row for row in order_matches if row["scope"] == "CROSS_CHART_SAME_K" and row["representation_id"] == "ZL_MEMBER_SEQUENCE")
    local_prefix = next(row for row in order_matches if row["scope"] == "CONSECUTIVE_SOURCE_SLOT" and row["representation_id"] == "TRANSFERRED_PREFIX")
    audit.check(fixed_member["observed_exact_matches"] == "0", "zero exact member sequences at fixed cross-chart K")
    audit.check((local_prefix["observed_exact_matches"], local_prefix["interpretation"]) == ("35", "LOCAL_GRAPHICAL_PREFIX_BLOCKING"), "35 of 87 local prefix matches support graphical blocking")
    audit.check(all(row["semantic_export"] == "NONE" for row in order_matches), "order tests export no semantics")

    edge_fields, _ = read_tsv(ART / OUTPUT_NAMES[10])
    audit.check(len(edge_packet) == 0, "relation edge packet is header-only")
    intake_module = load_module("gdt795_relation_edge_intake", RELATION_INTAKE)
    audit.check(tuple(intake_module.EDGE_COLUMNS) == edge_fields, "relation packet uses exact GDT388 schema")
    intake = intake_module.validate_relation_edge_packet(ART / OUTPUT_NAMES[10])
    expected_intake = {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY",
        "packet_rows": 0,
        "eligible_edges": 0,
        "eligible_folios": 0,
        "discovery_edges": 0,
        "holdout_edges": 0,
        "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False,
        "mobile_null_gate": False,
        "score_ready": False,
        "errors": [],
    }
    audit.check(intake == expected_intake, "empty GDT388 packet is valid acquisition and not score-ready")
    edge_cli = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(ART / OUTPUT_NAMES[10])],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    audit.check(edge_cli.returncode == 0, "GDT388 edge-packet CLI exits zero")
    try:
        edge_cli_payload = json.loads(edge_cli.stdout)
    except json.JSONDecodeError:
        edge_cli_payload = None
    audit.check(edge_cli_payload == intake, "GDT388 CLI and direct intake agree")

    audit.check(result.get("experiment_id") == "GDT795", "result experiment identity")
    audit.check(result.get("status") == EXPECTED_STATUS, "result exact status")
    audit.check(result.get("scope") == EXPECTED_SCOPE, "result exact guarded scope")
    audit.check(result.get("counts") == EXPECTED_COUNTS, "result exact core counts")
    audit.check(result.get("decision") == EXPECTED_DECISIONS, "result exact decisions")
    audit.check(result["scope"]["new_pages_or_images_opened"] == result["scope"]["sealed_rows_materialized"] == 0, "result records zero new or sealed materialization")
    audit.check(result["counts"]["component_exports"] == result["counts"]["confirmed_lexemes"] == 0, "result claim ceiling is zero component exports and lexemes")

    return write_validation(
        audit,
        builder_replays_completed=completed_replays,
        canonical_outputs_compared=len(OUTPUT_NAMES),
        builder_byte_replay=not any(item.startswith("byte ") for item in audit.failures),
        replay_one_equals_replay_two=not any(item.startswith("byte equality replay") for item in audit.failures),
        gdt388_edge_packet_checked=True,
        gdt388_edge_packet_status=intake.get("status"),
        gdt388_score_ready=intake.get("score_ready"),
        claim_ceiling="ZERO_COMPONENT_EXPORT__ZERO_CONFIRMED_LEXEME__NO_PROSE_EXPORT_FROM_CONTEXT_CARDS",
        new_pages_or_images_opened=0,
        mixed_sources_queried=1,
        sealed_rows_materialized=0,
    )


if __name__ == "__main__":
    raise SystemExit(main())
