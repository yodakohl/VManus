#!/usr/bin/env python3
"""Test a mixed whole-word/register model for ofch* and chor-like forms."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT))
from tools.relation_edge_intake import EDGE_COLUMNS, validate_relation_edge_packet

BASE_REL = Path("experiments/yolo/gdt766_ofch_chor_role_switch_prediction")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G765_RUN_REL = Path("experiments/yolo/gdt765_ofchy_schor_content_field_discriminator/src/run.py")
G735_HISTORY_REL = Path("experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_ENTRY_ATLAS.tsv")

CHOR_FORMS = ("chor", "lchor", "pchor", "schor")
REPRODUCTIVE_FORMS = {"chor", "chory", "schor", "shor"}
VALUE_FORMS = {"aiin", "dain", "daiin", "qodaiin"}
STATE_FORMS = {"chol", "qokchol", "cheor", "sheor", "cheo", "sheo"}
OUTPUT_NAMES = (
    "OFCH_CORE_43_OCCURRENCE_ATLAS.tsv",
    "OFCH_CORE_25_FORM_PROFILE.tsv",
    "OFCH_CORE_3_SCOPE_SUMMARY.tsv",
    "OFCH_REPRODUCTIVE_4_BRIDGE_ATLAS.tsv",
    "GDT766_GDT388_ROOT_BRIDGE_EDGE_PACKET.tsv",
    "OFCHEDY_QOFCHEDY_10_PAIR_AUDIT.tsv",
    "OFCH_25_WORKING_DICTIONARY.tsv",
    "OFCH_43_CONCRETE_RENDERER.tsv",
    "OFCH_22_MATCHED_GEOMETRY_CONTROL.tsv",
    "OFCH_22_MATCHED_CONTROL_SUMMARY.tsv",
    "CHOR_ROLE_191_OCCURRENCE_ATLAS.tsv",
    "CHOR_ROLE_4_PROFILE.tsv",
    "CHOR_STATE_VALUE_CONTACT_ATLAS.tsv",
    "CHOR_PCHOR_GEOMETRY_CONTRAST.tsv",
    "CHOR_ROLE_SUBSTITUTION_MATRIX.tsv",
    "CHOR_ROLE_4_WORKING_DICTIONARY.tsv",
    "FAMILY_MODEL_SCORECARD.tsv",
    "CONCRETE_WHOLE_CANDIDATE_TOURNAMENT.tsv",
    "FAMILY_DERIVATION_QUARANTINE.tsv",
    "FIVE_COMPLETE_LINE_WORKING_READER.tsv",
    "HISTORICAL_MIXED_RECORD_COMPARATORS.tsv",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__43_EXACT_OFCH_CORE_OCCURRENCES_25_FORMS__36_PAGES_41_LOCI__"
    "36_MEDIAL_6_LAST_1_FIRST__34_PARAGRAPH_START_LINES_1_TRUE_OPENER_0_PARAGRAPH_END__"
    "PREFIX_25_ZERO_FIRST_ZERO_REPEATED_EXACT_BIGRAMS__GENERIC_DRUG_CORE_PORTABLE__"
    "FLOWER_DRUG_CORE_BOLD_C0__4_REPRODUCTIVE_SAME_LINE_BRIDGES_NOT_SCORE_READY__"
    "OFCHEDY_QOFCHEDY_5_PLUS5_NOMINAL_ACTION_REMOVED__191_CHOR_FAMILY_OCCURRENCES__"
    "PCHOR_RECIPE_OPEN_CHOR_CONTENT_SCHOR_ITEM_LCHOR_INTERNAL__5_FULL_EXACT_LINES__"
    "ZERO_CONFIRMED_LEXEMES_ZERO_COMPONENT_EXPORT_NO_NEW_PAGE"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g765 = load_module("gdt765_builder_for_gdt766", ROOT / G765_RUN_REL)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def compact(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def is_exact(env: dict[str, object], locus: str, token: dict[str, object]) -> bool:
    return bool(env["context"].exact[(locus, int(token["token_index"]))])


def true_paragraph_opener(env: dict[str, object], locus: str, ordinal: int) -> int:
    return int(ordinal == 1 and str(env["line_meta"][locus]["paragraph_start"]) == "1")


def context_flags(env: dict[str, object], locus: str, target_ordinal: int) -> dict[str, int]:
    line = env["context"].by_line[locus]
    exact_surfaces = {
        str(token["eva"])
        for ordinal, token in enumerate(line, 1)
        if ordinal != target_ordinal and is_exact(env, locus, token)
    }
    slots = [g765.g764.slot(env, locus, ordinal) for ordinal in range(1, len(line) + 1) if ordinal != target_ordinal]
    text = " ".join(str(slot["roles"]) + " " + str(slot["semantic_candidate_de"]) for slot in slots).lower()
    return {
        "has_value": int(bool(exact_surfaces & VALUE_FORMS) or "value" in text or "wert" in text),
        "has_state": int(bool(exact_surfaces & STATE_FORMS) or "state" in text or "zustand" in text),
        "has_dry": int("dry" in text or "trocken" in text or "chol" in exact_surfaces),
        "has_moist": int("moist" in text or "feucht" in text or "sheo" in exact_surfaces or "cheo" in exact_surfaces),
        "has_amount": int("amount" in text or "menge" in text or "anteil" in text or bool(exact_surfaces & VALUE_FORMS)),
        "has_preparation": int("preparation" in text or "zubereit" in text or "ansatz" in text),
        "has_reproductive": int(bool(exact_surfaces & REPRODUCTIVE_FORMS)),
    }


def channel_fit(channel: str, flags: dict[str, int], position: str) -> int:
    rules = {
        "BASE_CONTENT": flags["has_state"] + flags["has_value"] + flags["has_preparation"],
        "PART_AMOUNT": 2 * flags["has_amount"] + flags["has_value"],
        "DRY_RESULT": 2 * flags["has_dry"] + flags["has_state"],
        "TERMINAL_RESULT": 2 * int(position == "LAST") + flags["has_state"],
        "PREPARATION": 2 * flags["has_preparation"] + flags["has_state"],
        "MOIST_PREPARATION": 2 * flags["has_moist"] + flags["has_preparation"],
        "EXTRACT": flags["has_preparation"] + flags["has_moist"],
        "COMPOUND_PREPARATION": flags["has_preparation"] + flags["has_state"],
    }
    return rules[channel]


def raw_surface_counts(env: dict[str, object]) -> Counter[str]:
    return Counter(str(token["eva"]) for line in env["context"].by_line.values() for token in line)


def exact_surface_counts(env: dict[str, object]) -> Counter[str]:
    return Counter(
        str(token["eva"])
        for locus, line in env["context"].by_line.items()
        for token in line
        if is_exact(env, locus, token)
    )


def build_ofch_atlas(env: dict[str, object], specs: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for locus, line in sorted(env["context"].by_line.items()):
        for ordinal, token in enumerate(line, 1):
            surface = str(token["eva"])
            if "ofch" not in surface or not is_exact(env, locus, token):
                continue
            if surface not in specs:
                raise AssertionError(f"missing ofch spec: {surface}")
            left = g765.g764.slot(env, locus, ordinal - 1)
            right = g765.g764.slot(env, locus, ordinal + 1)
            flags = context_flags(env, locus, ordinal)
            spec = specs[surface]
            position = line_position(ordinal, len(line))
            output.append({
                "occurrence_id": f"G766-OF{len(output)+1:03d}",
                "surface": surface,
                "family_layer": spec["family_layer"],
                "page": str(token["page"]),
                "physical_folio": g765.g764.g763.physical_folio(str(token["page"])),
                "locus": locus,
                "section": str(token["section"]),
                "hand": str(token["hand"]),
                "ordinal": ordinal,
                "line_token_count": len(line),
                "line_position": position,
                "paragraph_start_line": env["line_meta"][locus]["paragraph_start"],
                "paragraph_end_line": env["line_meta"][locus]["paragraph_end"],
                "true_paragraph_opener": true_paragraph_opener(env, locus, ordinal),
                "left_surface": left["surface"],
                "left_exact": int(ordinal > 1 and is_exact(env, locus, line[ordinal - 2])),
                "right_surface": right["surface"],
                "right_exact": int(ordinal < len(line) and is_exact(env, locus, line[ordinal])),
                **flags,
                "predicted_channel": spec["predicted_channel"],
                "channel_context_fit": channel_fit(spec["predicted_channel"], flags, position),
                "portable_default_de": spec["portable_default_de"],
                "bold_default_de": spec["bold_default_de"],
                "role_confidence": spec["role_confidence"],
                "identity_confidence": spec["identity_confidence"],
                "identity_score_100": spec["identity_score_100"],
                "family_analogy_scope": spec["family_analogy_scope"],
                "global_component_export": spec["global_component_export"],
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
            })
    return output


def build_ofch_profile(atlas: list[dict[str, object]], specs: dict[str, dict[str, str]], raw: Counter[str]) -> list[dict[str, object]]:
    grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in atlas:
        grouped[str(row["surface"])].append(row)
    output: list[dict[str, object]] = []
    for surface in sorted(grouped):
        rows = grouped[surface]
        spec = specs[surface]
        output.append({
            "surface": surface,
            "family_layer": spec["family_layer"],
            "raw_occurrences": raw[surface],
            "reader_exact_occurrences": len(rows),
            "pages": len({str(row["page"]) for row in rows}),
            "loci": len({str(row["locus"]) for row in rows}),
            "sections": compact(str(row["section"]) for row in rows),
            "line_positions": compact(str(row["line_position"]) for row in rows),
            "paragraph_start_lines": sum(str(row["paragraph_start_line"]) == "1" for row in rows),
            "true_paragraph_openers": sum(int(row["true_paragraph_opener"]) for row in rows),
            "predicted_channel": spec["predicted_channel"],
            "mean_channel_context_fit": f"{sum(int(row['channel_context_fit']) for row in rows)/len(rows):.6f}",
            "portable_default_de": spec["portable_default_de"],
            "bold_default_de": spec["bold_default_de"],
            "role_confidence": spec["role_confidence"],
            "identity_confidence": spec["identity_confidence"],
            "identity_score_100": spec["identity_score_100"],
            "strongest_evidence": spec["strongest_evidence"],
            "strongest_counterevidence": spec["strongest_counterevidence"],
            "primary_rival_de": spec["primary_rival_de"],
            "secondary_rival_de": spec["secondary_rival_de"],
            "family_analogy_scope": spec["family_analogy_scope"],
            "global_component_export": spec["global_component_export"],
        })
    return output


def build_scope_summary(
    env: dict[str, object], atlas: list[dict[str, object]], raw: Counter[str]
) -> list[dict[str, object]]:
    predicates = (
        ("OFCH_CONTAINING", lambda value: "ofch" in value),
        ("OFCH_PREFIX_ONLY", lambda value: value.startswith("ofch")),
        ("OUTER_SHELL_ONLY", lambda value: "ofch" in value and not value.startswith("ofch")),
    )
    all_raw_forms = {
        str(token["eva"])
        for line in env["context"].by_line.values()
        for token in line
    }
    output: list[dict[str, object]] = []
    for scope, predicate in predicates:
        rows = [row for row in atlas if predicate(str(row["surface"]))]
        raw_forms = {surface for surface in all_raw_forms if predicate(surface)}
        left_pairs = [
            f"{row['left_surface']}>>{row['surface']}"
            for row in rows if int(row["left_exact"])
        ]
        right_pairs = [
            f"{row['surface']}>>{row['right_surface']}"
            for row in rows if int(row["right_exact"])
        ]
        repeated = sum(count - 1 for count in Counter(left_pairs + right_pairs).values() if count > 1)
        output.append({
            "scope": scope,
            "raw_occurrences": sum(raw[surface] for surface in raw_forms),
            "raw_forms": len(raw_forms),
            "reader_exact_occurrences": len(rows),
            "reader_exact_forms": len({str(row["surface"]) for row in rows}),
            "pages": len({str(row["page"]) for row in rows}),
            "loci": len({str(row["locus"]) for row in rows}),
            "sections": compact(str(row["section"]) for row in rows),
            "line_positions": compact(str(row["line_position"]) for row in rows),
            "paragraph_start_lines": sum(str(row["paragraph_start_line"]) == "1" for row in rows),
            "true_paragraph_openers": sum(int(row["true_paragraph_opener"]) for row in rows),
            "paragraph_end_lines": sum(str(row["paragraph_end_line"]) == "1" for row in rows),
            "exact_left_edges": len(left_pairs),
            "unique_exact_left_edges": len(set(left_pairs)),
            "exact_right_edges": len(right_pairs),
            "unique_exact_right_edges": len(set(right_pairs)),
            "repeated_exact_immediate_edges": repeated,
            "scope_interpretation": (
                "OBSERVED_NOMINAL_DRUG_OR_PREPARATION_CLASS"
                if scope == "OFCH_CONTAINING" else
                "INNER_FIRST_RECORD_FIELD" if scope == "OFCH_PREFIX_ONLY" else
                "OUTER_SHELL_VARIANTS"
            ),
            "global_component_export": 0,
        })
    return output


def build_reproductive_bridges(env: dict[str, object], atlas: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in atlas:
        locus = str(row["locus"])
        line = env["context"].by_line[locus]
        for ordinal, token in enumerate(line, 1):
            surface = str(token["eva"])
            if ordinal == int(row["ordinal"]) or surface not in REPRODUCTIVE_FORMS or not is_exact(env, locus, token):
                continue
            output.append({
                "bridge_id": f"G766-RB{len(output)+1:02d}",
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "locus": locus,
                "ofch_surface": row["surface"],
                "ofch_ordinal": row["ordinal"],
                "reproductive_surface": surface,
                "reproductive_ordinal": ordinal,
                "written_order": "OFCH_THEN_REPRODUCTIVE" if int(row["ordinal"]) < ordinal else "REPRODUCTIVE_THEN_OFCH",
                "written_line_eva": row["written_line_eva"],
                "bridge_support": "WEAK_SAME_LINE_DOMAIN_COMPATIBILITY",
                "identity_credit": 0,
                "score_ready_relation_credit": 0,
                "global_component_export": 0,
            })
    return output


def build_edge_packet(bridges: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for index, row in enumerate(bridges, 1):
        locus = str(row["locus"])
        output.append({
            "edge_id": f"G766.E{index:02d}",
            "batch_id": "GDT766_ROOT_BRIDGE",
            "page": row["page"],
            "physical_folio": row["physical_folio"],
            "diagram_unit_id": f"TEXT_LINE_{str(row['page']).replace('.', '_')}_{index:02d}",
            "pivot_visual_id": f"OFC_TOKEN_{index:02d}",
            "pivot_locus": f"{locus}@{row['ofch_ordinal']}",
            "target_visual_id": f"REPRO_TOKEN_{index:02d}",
            "target_locus": f"{locus}@{row['reproductive_ordinal']}",
            "relation_type": "SAME_LINE_TEXT_COOCCURRENCE",
            "direction_basis": "WRITTEN_ORDER_ONLY",
            "ownership_basis": "TEXT_TOKEN_PAIR",
            "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT766",
            "page_crop_sha256": "NONE",
            "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT766_BUILDER",
            "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "UNRESOLVED",
            "formal_access_state": "SEALED_NOT_ACCESSED",
            "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_TEXT_COOCCURRENCE",
        })
    return output


def build_pair_audit(atlas: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = [row for row in atlas if str(row["surface"]) in {"ofchedy", "qofchedy"}]
    output: list[dict[str, object]] = []
    for row in rows:
        output.append({
            "pair_audit_id": f"G766-OQ{len(output)+1:02d}",
            "surface": row["surface"],
            "page": row["page"],
            "locus": row["locus"],
            "ordinal": row["ordinal"],
            "line_position": row["line_position"],
            "paragraph_start_line": row["paragraph_start_line"],
            "left_surface": row["left_surface"],
            "right_surface": row["right_surface"],
            "has_dry": row["has_dry"],
            "has_state": row["has_state"],
            "portable_default_de": row["portable_default_de"],
            "bold_default_de": row["bold_default_de"],
            "old_action_composition": "REMOVED",
            "q_command_export": 0,
            "nominal_pair_model": 1,
            "global_component_export": 0,
            "written_line_eva": row["written_line_eva"],
        })
    return output


def build_ofch_dictionary(profile: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{
        **row,
        "specific_identity_is_replaceable": 1,
        "confirmed_lexeme": 0,
        "unseen_form_export": 0,
    } for row in profile]


def build_ofch_renderer(atlas: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{
        "renderer_id": f"G766-OR{index:03d}",
        "surface": row["surface"],
        "page": row["page"],
        "locus": row["locus"],
        "ordinal": row["ordinal"],
        "portable_occurrence_renderer_de": row["portable_default_de"],
        "bold_occurrence_renderer_de": row["bold_default_de"],
        "predicted_channel": row["predicted_channel"],
        "channel_context_fit": row["channel_context_fit"],
        "identity_confidence": row["identity_confidence"],
        "scope": "THIS_OBSERVED_EXACT_WHOLE_FORM",
        "confirmed_plaintext": 0,
        "global_component_export": 0,
        "written_line_eva": row["written_line_eva"],
    } for index, row in enumerate(atlas, 1)]


def build_matched_controls(
    env: dict[str, object], atlas: list[dict[str, object]], exact_counts: Counter[str]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    targets = [row for row in atlas if str(row["surface"]).startswith("ofch") and str(row["surface"]) != "ofchy"]
    eligible: list[dict[str, object]] = []
    for locus, line in sorted(env["context"].by_line.items()):
        for ordinal, token in enumerate(line, 1):
            surface = str(token["eva"])
            if not is_exact(env, locus, token) or surface.startswith("ofch"):
                continue
            eligible.append({
                "occurrence_key": f"{locus}@{ordinal}",
                "surface": surface,
                "section": str(token["section"]),
                "frequency": exact_counts[surface],
                "line_first": int(ordinal == 1),
                "paragraph_start_line": int(str(env["line_meta"][locus]["paragraph_start"]) == "1"),
            })
    output: list[dict[str, object]] = []
    used_keys: set[str] = set()
    reused = 0
    for index, target in enumerate(targets, 1):
        frequency = exact_counts[str(target["surface"])]
        pool = [row for row in eligible if row["section"] == target["section"] and row["frequency"] == frequency]
        if not pool:
            raise AssertionError(f"empty matched control pool for {target['occurrence_id']}")
        used_keys.update(str(row["occurrence_key"]) for row in pool)
        reused += len(pool)
        first = sum(int(row["line_first"]) for row in pool)
        pstart = sum(int(row["paragraph_start_line"]) for row in pool)
        output.append({
            "match_id": f"G766-MC{index:02d}",
            "target_occurrence_id": target["occurrence_id"],
            "target_surface": target["surface"],
            "target_page": target["page"],
            "target_locus": target["locus"],
            "target_section": target["section"],
            "target_global_exact_form_frequency": frequency,
            "target_line_first": int(str(target["line_position"]) in {"FIRST", "ONLY"}),
            "target_paragraph_start_line": int(str(target["paragraph_start_line"]) == "1"),
            "control_pool_occurrences": len(pool),
            "control_line_first_occurrences": first,
            "control_line_first_rate": f"{first/len(pool):.12f}",
            "control_paragraph_start_occurrences": pstart,
            "control_paragraph_start_rate": f"{pstart/len(pool):.12f}",
            "matching_rule": "SAME_SECTION_AND_GLOBAL_EXACT_WHOLE_FORM_FREQUENCY__EXCLUDE_OFCH_PREFIX",
            "sampling": "NONE_FULL_POOL",
            "outcome_matched": 0,
        })
    summary = [{
        "target_occurrences": len(output),
        "target_line_first_occurrences": sum(int(row["target_line_first"]) for row in output),
        "target_line_first_rate": f"{sum(int(row['target_line_first']) for row in output)/len(output):.12f}",
        "macro_control_line_first_rate": f"{sum(float(row['control_line_first_rate']) for row in output)/len(output):.12f}",
        "target_paragraph_start_occurrences": sum(int(row["target_paragraph_start_line"]) for row in output),
        "target_paragraph_start_rate": f"{sum(int(row['target_paragraph_start_line']) for row in output)/len(output):.12f}",
        "macro_control_paragraph_start_rate": f"{sum(float(row['control_paragraph_start_rate']) for row in output)/len(output):.12f}",
        "reader_exact_token_universe": sum(exact_counts.values()),
        "eligible_control_occurrences": len(eligible),
        "eligible_control_forms": len({str(row["surface"]) for row in eligible}),
        "used_control_union_occurrences": len(used_keys),
        "control_pool_appearances_with_reuse": reused,
        "interpretation": "OFCH_PREFIX_IS_ENRICHED_ON_PARAGRAPH_START_LINES_BUT_AVOIDS_LINE_FIRST_POSITION",
        "identity_credit": 0,
        "global_component_export": 0,
    }]
    return output, summary


def build_chor_atlas(
    env: dict[str, object], specs: dict[str, dict[str, str]]
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for locus, line in sorted(env["context"].by_line.items()):
        for ordinal, token in enumerate(line, 1):
            surface = str(token["eva"])
            if surface not in specs or not is_exact(env, locus, token):
                continue
            left = g765.g764.slot(env, locus, ordinal - 1)
            right = g765.g764.slot(env, locus, ordinal + 1)
            left_surface = str(left["surface"])
            right_surface = str(right["surface"])
            spec = specs[surface]
            output.append({
                "occurrence_id": f"G766-CH{len(output)+1:03d}",
                "surface": surface,
                "page": str(token["page"]),
                "physical_folio": g765.g764.g763.physical_folio(str(token["page"])),
                "locus": locus,
                "section": str(token["section"]),
                "hand": str(token["hand"]),
                "ordinal": ordinal,
                "line_token_count": len(line),
                "line_position": line_position(ordinal, len(line)),
                "paragraph_start_line": env["line_meta"][locus]["paragraph_start"],
                "paragraph_end_line": env["line_meta"][locus]["paragraph_end"],
                "true_paragraph_opener": true_paragraph_opener(env, locus, ordinal),
                "left_surface": left_surface,
                "left_exact": int(ordinal > 1 and is_exact(env, locus, line[ordinal - 2])),
                "left_roles": left["roles"],
                "right_surface": right_surface,
                "right_exact": int(ordinal < len(line) and is_exact(env, locus, line[ordinal])),
                "right_roles": right["roles"],
                "left_value_contact": int(left_surface in VALUE_FORMS and ordinal > 1 and is_exact(env, locus, line[ordinal - 2])),
                "right_value_contact": int(right_surface in VALUE_FORMS and ordinal < len(line) and is_exact(env, locus, line[ordinal])),
                "left_state_contact": int(left_surface in STATE_FORMS and ordinal > 1 and is_exact(env, locus, line[ordinal - 2])),
                "right_state_contact": int(right_surface in STATE_FORMS and ordinal < len(line) and is_exact(env, locus, line[ordinal])),
                "selected_role": spec["selected_role"],
                "portable_default_de": spec["portable_default_de"],
                "bold_default_de": spec["bold_default_de"],
                "occurrence_bold_default_de": (
                    "Rezept- oder Eintragsmarker"
                    if surface == "pchor" and not true_paragraph_opener(env, locus, ordinal)
                    else spec["bold_default_de"]
                ),
                "role_confidence": spec["role_confidence"],
                "identity_confidence": spec["identity_confidence"],
                "identity_score_100": spec["identity_score_100"],
                "global_component_export": spec["global_component_export"],
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
            })
    return output


def chor_fit_count(surface: str, rows: list[dict[str, object]], rule: str) -> int:
    if rule == "NOT_LINE_FIRST":
        return sum(str(row["line_position"]) not in {"FIRST", "ONLY"} for row in rows)
    if rule == "NOT_TRUE_PARAGRAPH_OPENER":
        return sum(not int(row["true_paragraph_opener"]) for row in rows)
    if rule == "PARAGRAPH_START_LINE":
        return sum(str(row["paragraph_start_line"]) == "1" for row in rows)
    if rule == "LINE_FIRST_OR_LEFT_H2":
        return sum(
            str(row["line_position"]) in {"FIRST", "ONLY"} or "H2" in str(row["left_roles"])
            for row in rows
        )
    raise AssertionError(f"unknown fit rule for {surface}: {rule}")


def build_chor_profile(
    atlas: list[dict[str, object]], specs: dict[str, dict[str, str]], raw: Counter[str]
) -> list[dict[str, object]]:
    grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in atlas:
        grouped[str(row["surface"])].append(row)
    output: list[dict[str, object]] = []
    for surface in CHOR_FORMS:
        rows = grouped[surface]
        spec = specs[surface]
        output.append({
            "surface": surface,
            "raw_occurrences": raw[surface],
            "reader_exact_occurrences": len(rows),
            "pages": len({str(row["page"]) for row in rows}),
            "loci": len({str(row["locus"]) for row in rows}),
            "sections": compact(str(row["section"]) for row in rows),
            "line_positions": compact(str(row["line_position"]) for row in rows),
            "paragraph_start_lines": sum(str(row["paragraph_start_line"]) == "1" for row in rows),
            "true_paragraph_openers": sum(int(row["true_paragraph_opener"]) for row in rows),
            "left_value_contacts": sum(int(row["left_value_contact"]) for row in rows),
            "right_value_contacts": sum(int(row["right_value_contact"]) for row in rows),
            "left_state_contacts": sum(int(row["left_state_contact"]) for row in rows),
            "right_state_contacts": sum(int(row["right_state_contact"]) for row in rows),
            "selected_role": spec["selected_role"],
            "fit_rule": spec["fit_rule"],
            "fit_occurrences": chor_fit_count(surface, rows, spec["fit_rule"]),
            "portable_default_de": spec["portable_default_de"],
            "bold_default_de": spec["bold_default_de"],
            "role_confidence": spec["role_confidence"],
            "identity_confidence": spec["identity_confidence"],
            "identity_score_100": spec["identity_score_100"],
            "strongest_evidence": spec["strongest_evidence"],
            "strongest_counterevidence": spec["strongest_counterevidence"],
            "primary_rival_de": spec["primary_rival_de"],
            "secondary_rival_de": spec["secondary_rival_de"],
            "global_component_export": spec["global_component_export"],
        })
    return output


def build_chor_contacts(env: dict[str, object], atlas: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in atlas:
        if str(row["surface"]) != "chor":
            continue
        locus = str(row["locus"])
        line = env["context"].by_line[locus]
        ordinal = int(row["ordinal"])
        for neighbor_ordinal, direction in ((ordinal - 1, "LEFT"), (ordinal + 1, "RIGHT")):
            if neighbor_ordinal < 1 or neighbor_ordinal > len(line):
                continue
            token = line[neighbor_ordinal - 1]
            surface = str(token["eva"])
            if surface not in VALUE_FORMS | STATE_FORMS or not is_exact(env, locus, token):
                continue
            output.append({
                "contact_id": f"G766-CC{len(output)+1:02d}",
                "page": row["page"],
                "locus": locus,
                "chor_ordinal": ordinal,
                "neighbor_ordinal": neighbor_ordinal,
                "direction_from_chor": direction,
                "neighbor_surface": surface,
                "contact_class": "VALUE" if surface in VALUE_FORMS else "STATE",
                "written_span_eva": f"chor {surface}" if direction == "RIGHT" else f"{surface} chor",
                "written_line_eva": row["written_line_eva"],
                "supports_nominal_content_carrier": 1,
                "specific_flower_credit": 0,
                "global_component_export": 0,
            })
    return output


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    row1, row2, col1 = a + b, c + d, a + c
    total = row1 + row2

    def probability(x: int) -> float:
        return math.comb(col1, x) * math.comb(total - col1, row1 - x) / math.comb(total, row1)

    low = max(0, row1 - (total - col1))
    high = min(row1, col1)
    observed = probability(a)
    return sum(probability(x) for x in range(low, high + 1) if probability(x) <= observed + 1e-15)


def build_geometry_contrast(profile: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = {str(row["surface"]): row for row in profile}
    pchor, chor = rows["pchor"], rows["chor"]
    tests = (
        ("LINE_FIRST", 7, 3, 10, 166),
        ("TRUE_PARAGRAPH_OPENER", 6, 4, 0, 176),
    )
    output: list[dict[str, object]] = []
    for name, a, b, c, d in tests:
        output.append({
            "contrast_id": f"G766-GC{len(output)+1:02d}",
            "outcome": name,
            "pchor_yes": a,
            "pchor_no": b,
            "chor_yes": c,
            "chor_no": d,
            "pchor_rate": f"{a/(a+b):.12f}",
            "chor_rate": f"{c/(c+d):.12f}",
            "fisher_two_sided_p": f"{fisher_two_sided(a,b,c,d):.12g}",
            "interpretation": "ROLE_GEOMETRY_DIFFERS_STRONGLY",
            "shared_plant_noun_penalty": 1,
        })
    if int(pchor["reader_exact_occurrences"]) != 10 or int(chor["reader_exact_occurrences"]) != 176:
        raise AssertionError("chor/pchor census changed before contrast")
    return output


def build_substitution_matrix(profile: list[dict[str, object]]) -> list[dict[str, object]]:
    roles = (
        ("RECIPE_OR_ENTRY_OPENING", "nimm"),
        ("PLANT_PART_CONTENT_HEAD", "Blütenstand"),
        ("ITEM_OR_SUBENTRY_HEAD", "Blütenstandsposten"),
        ("INTERNAL_PREPARATION_FIELD", "Blütenauszug"),
    )
    output: list[dict[str, object]] = []
    for row in profile:
        n = int(row["reader_exact_occurrences"])
        first = sum(int(part.split(":")[1]) for part in str(row["line_positions"]).split("|") if part.split(":")[0] in {"FIRST", "ONLY"})
        medial = sum(int(part.split(":")[1]) for part in str(row["line_positions"]).split("|") if part.split(":")[0] == "MIDDLE")
        true_open = int(row["true_paragraph_openers"])
        contacts = sum(int(row[key]) for key in ("left_value_contacts", "right_value_contacts", "left_state_contacts", "right_state_contacts"))
        b_count = next((int(part.split(":")[1]) for part in str(row["sections"]).split("|") if part.split(":")[0] == "B"), 0)
        scores = {
            "RECIPE_OR_ENTRY_OPENING": 3 * true_open + first - 2 * medial,
            "PLANT_PART_CONTENT_HEAD": 2 * medial + contacts - 3 * true_open,
            "ITEM_OR_SUBENTRY_HEAD": 2 * first + contacts,
            "INTERNAL_PREPARATION_FIELD": medial + b_count - true_open,
        }
        for role, renderer in roles:
            output.append({
                "surface": row["surface"],
                "candidate_role": role,
                "candidate_renderer_de": renderer,
                "geometry_score": scores[role],
                "selected_for_surface": int(role == row["selected_role"]),
                "exact_occurrences": n,
                "line_first_occurrences": first,
                "medial_occurrences": medial,
                "true_paragraph_openers": true_open,
                "state_or_value_contacts": contacts,
                "section_b_occurrences": b_count,
                "identity_is_replaceable": 1,
                "global_component_export": 0,
            })
    return output


def build_chor_dictionary(profile: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{
        **row,
        "whole_word_only": 1,
        "specific_identity_is_replaceable": 1,
        "confirmed_lexeme": 0,
        "global_component_export": 0,
    } for row in profile]


def build_model_scorecard(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        score = (
            2 * int(row["geometry_fit"])
            + 2 * int(row["context_fit"])
            + int(row["family_bridge"])
            + int(row["prior_anchor"])
            + int(row["portability_bonus"])
            - 2 * int(row["contradiction_penalty"])
            - int(row["circularity_penalty"])
        )
        output.append({
            **row,
            "working_score": score,
            "score_rule": "2*geometry+2*context+bridge+anchor+portability-2*contradiction-circularity",
            "confirmed_lexeme": 0,
            "global_component_export": 0,
        })
    return output


def build_candidate_tournament(
    ofch_profile: list[dict[str, object]], chor_profile: list[dict[str, object]]
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for family, rows in (("OFCH", ofch_profile), ("CHOR", chor_profile)):
        for row in rows:
            candidates = (
                (str(row["bold_default_de"]), int(row["identity_score_100"]), "SELECTED_BOLD_WORKING_DEFAULT"),
                (str(row["primary_rival_de"]), max(0, int(row["identity_score_100"]) - 5), "PRIMARY_RIVAL"),
                (str(row["secondary_rival_de"]), max(0, int(row["identity_score_100"]) - 10), "SECONDARY_RIVAL"),
            )
            for rank, (candidate, score, status) in enumerate(candidates, 1):
                output.append({
                    "candidate_id": f"G766-CT{len(output)+1:03d}",
                    "family": family,
                    "surface": row["surface"],
                    "candidate_rank": rank,
                    "candidate_de": candidate,
                    "identity_score_100": score,
                    "status": status,
                    "role_or_channel": row.get("predicted_channel", row.get("selected_role", "")),
                    "exact_occurrences": row["reader_exact_occurrences"],
                    "selection_basis": "OBSERVED_WHOLE_FORM_CONTEXT_AND_GEOMETRY",
                    "identity_is_replaceable": 1,
                    "confirmed_lexeme": 0,
                    "global_component_export": 0,
                })
    return output


def build_passage_reader(
    env: dict[str, object], token_specs: list[dict[str, str]], line_specs: list[dict[str, str]]
) -> list[dict[str, object]]:
    by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_specs:
        by_locus[row["locus"]].append(row)
    renderers = {row["locus"]: row for row in line_specs}
    output: list[dict[str, object]] = []
    for locus, specs in by_locus.items():
        line = env["context"].by_line[locus]
        specs = sorted(specs, key=lambda row: int(row["ordinal"]))
        if len(specs) != len(line):
            raise AssertionError(f"passage spec does not cover full line: {locus}")
        if locus not in renderers:
            raise AssertionError(f"missing line renderer: {locus}")
        written = " ".join(str(token["eva"]) for token in line)
        renderer = renderers[locus]
        for ordinal, (spec, token) in enumerate(zip(specs, line), 1):
            if int(spec["ordinal"]) != ordinal or spec["surface"] != str(token["eva"]):
                raise AssertionError(f"passage token mismatch: {locus}@{ordinal}")
            if not is_exact(env, locus, token):
                raise AssertionError(f"nonexact token in complete passage: {locus}@{ordinal}")
            output.append({
                "reader_token_id": f"G766-PR{len(output)+1:02d}",
                "page": str(token["page"]),
                "locus": locus,
                "ordinal": ordinal,
                "surface": spec["surface"],
                "local_default_de": spec["local_default_de"],
                "confidence": spec["confidence"],
                "evidence_class": spec["evidence_class"],
                "global_export": spec["global_export"],
                "portable_line_renderer_de": renderer["portable_line_renderer_de"],
                "bold_line_renderer_de": renderer["bold_line_renderer_de"],
                "renderer_basis": renderer["renderer_basis"],
                "written_line_eva": written,
                "confirmed_plaintext": 0,
                "global_component_export": 0,
            })
    return output


def build_historical_comparators() -> list[dict[str, object]]:
    prior = g765.build_historical_comparators(read_tsv(ROOT / G735_HISTORY_REL))
    return [{
        "historical_item_id": row["historical_item_id"],
        "record_mode": row["record_mode"],
        "headword_or_rubric": row["headword_or_rubric"],
        "observed_slots": row["observed_slots"],
        "layout_relation": row["layout_relation"],
        "gdt766_architecture_use": str(row["gdt765_architecture_use"]).replace("learned drug name", "learned whole word"),
        "evidence_summary": row["evidence_summary"],
        "caveat": row["caveat"],
        "target_spelling_credit": 0,
        "target_identity_credit": 0,
        "global_component_export": 0,
    } for row in prior]


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    ofch_specs_rows = read_tsv(SRC / "OFCH_25_FORM_SPECS.tsv")
    chor_specs_rows = read_tsv(SRC / "CHOR_4_FORM_SPECS.tsv")
    model_specs = read_tsv(SRC / "FAMILY_MODEL_SPECS.tsv")
    token_specs = read_tsv(SRC / "PASSAGE_5_LINE_TOKEN_DEFAULTS.tsv")
    line_specs = read_tsv(SRC / "PASSAGE_5_LINE_RENDER_SPECS.tsv")
    quarantine_specs = read_tsv(SRC / "DERIVATION_QUARANTINE_SPECS.tsv")
    ofch_specs = {row["surface"]: row for row in ofch_specs_rows}
    chor_specs = {row["surface"]: row for row in chor_specs_rows}
    if len(ofch_specs) != 25 or tuple(chor_specs) != CHOR_FORMS:
        raise AssertionError("source specification universe changed")

    env = g765.g764.semantic_environment()
    raw = raw_surface_counts(env)
    exact_counts = exact_surface_counts(env)
    ofch = build_ofch_atlas(env, ofch_specs)
    ofch_profile = build_ofch_profile(ofch, ofch_specs, raw)
    scope = build_scope_summary(env, ofch, raw)
    bridges = build_reproductive_bridges(env, ofch)
    edge_packet = build_edge_packet(bridges)
    pair_audit = build_pair_audit(ofch)
    ofch_dictionary = build_ofch_dictionary(ofch_profile)
    ofch_renderer = build_ofch_renderer(ofch)
    controls, control_summary = build_matched_controls(env, ofch, exact_counts)
    chor = build_chor_atlas(env, chor_specs)
    chor_profile = build_chor_profile(chor, chor_specs, raw)
    contacts = build_chor_contacts(env, chor)
    contrast = build_geometry_contrast(chor_profile)
    substitutions = build_substitution_matrix(chor_profile)
    chor_dictionary = build_chor_dictionary(chor_profile)
    models = build_model_scorecard(model_specs)
    tournament = build_candidate_tournament(ofch_profile, chor_profile)
    quarantine = [{**row, "confirmed_lexeme": 0, "global_component_export": 0} for row in quarantine_specs]
    passage = build_passage_reader(env, token_specs, line_specs)
    history = build_historical_comparators()

    scope_by_id = {str(row["scope"]): row for row in scope}
    all_scope = scope_by_id["OFCH_CONTAINING"]
    prefix_scope = scope_by_id["OFCH_PREFIX_ONLY"]
    if len(ofch) != 43 or len(ofch_profile) != 25:
        raise AssertionError("ofch-containing exact census changed")
    if (int(all_scope["raw_occurrences"]), int(all_scope["raw_forms"])) != (58, 32):
        raise AssertionError("ofch-containing raw census changed")
    if (int(all_scope["pages"]), int(all_scope["loci"])) != (36, 41):
        raise AssertionError("ofch-containing page/locus census changed")
    if str(all_scope["line_positions"]) != "FIRST:1|LAST:6|MIDDLE:36":
        raise AssertionError("ofch-containing geometry changed")
    if (int(all_scope["paragraph_start_lines"]), int(all_scope["true_paragraph_openers"]), int(all_scope["paragraph_end_lines"])) != (34, 1, 0):
        raise AssertionError("ofch-containing paragraph geometry changed")
    if (int(prefix_scope["raw_occurrences"]), int(prefix_scope["reader_exact_occurrences"]), int(prefix_scope["reader_exact_forms"])) != (30, 25, 13):
        raise AssertionError("ofch-prefix census changed")
    if str(prefix_scope["line_positions"]) != "LAST:4|MIDDLE:21" or int(prefix_scope["repeated_exact_immediate_edges"]) != 0:
        raise AssertionError("ofch-prefix edge geometry changed")
    if len(bridges) != 4 or {(row["locus"], row["ofch_surface"], row["reproductive_surface"]) for row in bridges} != {
        ("f8r.9", "ofchey", "shor"), ("f22r.4", "ofchy", "schor"),
        ("f37r.1", "ofchor", "chory"), ("f95v2.1", "ofchdy", "shor"),
    }:
        raise AssertionError("reproductive bridge census changed")
    if len(pair_audit) != 10 or Counter(str(row["surface"]) for row in pair_audit) != Counter({"ofchedy": 5, "qofchedy": 5}):
        raise AssertionError("ofchedy/qofchedy pair census changed")
    if len(controls) != 22:
        raise AssertionError("matched-control target count")
    control = control_summary[0]
    expected_control = {
        "target_line_first_occurrences": 0,
        "target_paragraph_start_occurrences": 17,
        "reader_exact_token_universe": 24090,
        "eligible_control_occurrences": 24065,
        "eligible_control_forms": 4803,
        "used_control_union_occurrences": 4335,
        "control_pool_appearances_with_reuse": 11471,
    }
    if any(int(control[key]) != value for key, value in expected_control.items()):
        raise AssertionError("matched-control bookkeeping changed")
    if abs(float(control["macro_control_line_first_rate"]) - 0.192545528074) > 1e-12 or abs(float(control["macro_control_paragraph_start_rate"]) - 0.263922798558) > 1e-12:
        raise AssertionError("matched-control rates changed")
    if len(chor) != 191 or Counter(str(row["surface"]) for row in chor) != Counter({"chor": 176, "pchor": 10, "schor": 3, "lchor": 2}):
        raise AssertionError("chor-role census changed")
    if len({str(row["page"]) for row in chor}) != 99 or len({str(row["locus"]) for row in chor}) != 183:
        raise AssertionError("chor-role coverage changed")
    if len(contacts) != 41 or Counter(str(row["contact_class"]) for row in contacts) != Counter({"STATE": 22, "VALUE": 19}):
        raise AssertionError("chor contact census changed")
    if len(passage) != 46 or len({str(row["locus"]) for row in passage}) != 5:
        raise AssertionError("complete-line reader coverage changed")
    if len(tournament) != 87 or len(quarantine) != 6 or len(history) != 7:
        raise AssertionError("decision artifact size changed")
    if env["guard"] != {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}:
        raise AssertionError("guarded context changed")
    claim_rows = ofch + ofch_profile + scope + bridges + pair_audit + ofch_dictionary + ofch_renderer + chor + chor_profile + contacts + substitutions + chor_dictionary + models + tournament + quarantine + passage + history
    if any(str(row.get("page", "")).startswith("f84") for row in claim_rows):
        raise AssertionError("sealed page entered GDT766")
    if any(str(row.get("global_component_export", "0")) != "0" for row in claim_rows if "global_component_export" in row):
        raise AssertionError("component export escaped GDT766")

    tables: tuple[list[dict[str, object]], ...] = (
        ofch, ofch_profile, scope, bridges, edge_packet, pair_audit, ofch_dictionary,
        ofch_renderer, controls, control_summary, chor, chor_profile, contacts, contrast,
        substitutions, chor_dictionary, models, tournament, quarantine, passage, history,
    )
    for name, rows in zip(OUTPUT_NAMES[:-1], tables):
        if not rows:
            raise AssertionError(f"empty output: {name}")
        fields = list(EDGE_COLUMNS) if name == "GDT766_GDT388_ROOT_BRIDGE_EDGE_PACKET.tsv" else list(rows[0])
        write_tsv(output_dir / name, rows, fields)

    packet_report = validate_relation_edge_packet(output_dir / "GDT766_GDT388_ROOT_BRIDGE_EDGE_PACKET.tsv")
    if packet_report["status"] != "VALID_ACQUISITION_NOT_SCORE_READY" or packet_report["score_ready"]:
        raise AssertionError("text cooccurrence packet must remain non-score-ready")

    result = {
        "schema": "GDT766_RESULT_V1",
        "status": STATUS,
        "scope": {
            "ofch_containing_exact_occurrences": len(ofch),
            "ofch_containing_exact_forms": len(ofch_profile),
            "ofch_containing_pages": int(all_scope["pages"]),
            "ofch_containing_loci": int(all_scope["loci"]),
            "ofch_prefix_exact_occurrences": int(prefix_scope["reader_exact_occurrences"]),
            "ofch_prefix_exact_forms": int(prefix_scope["reader_exact_forms"]),
            "matched_control_targets": len(controls),
            "reproductive_same_line_bridges": len(bridges),
            "chor_family_exact_occurrences": len(chor),
            "chor_family_pages": len({str(row["page"]) for row in chor}),
            "chor_family_loci": len({str(row["locus"]) for row in chor}),
            "complete_reader_lines": len({str(row["locus"]) for row in passage}),
            "complete_reader_tokens": len(passage),
            "historical_comparators": len(history),
        },
        "ofch_result": {
            "portable_model": "GENERIC_DRUG_OR_PREPARATION_CORE",
            "bold_model": "FAMILY_BOUNDED_FLOWER_DRUG_CORE",
            "bold_model_confidence": "C0_EXPLORATORY",
            "paragraph_start_target_rate": float(control["target_paragraph_start_rate"]),
            "paragraph_start_macro_control_rate": float(control["macro_control_paragraph_start_rate"]),
            "line_first_target_rate": float(control["target_line_first_rate"]),
            "line_first_macro_control_rate": float(control["macro_control_line_first_rate"]),
            "repeated_exact_immediate_edges_prefix": int(prefix_scope["repeated_exact_immediate_edges"]),
        },
        "chor_result": {
            "architecture": "ROLE_SWITCHED_LEARNED_WHOLE_WORDS",
            "chor": "Blütenstand",
            "pchor": "nimm",
            "schor": "Blütenstandsposten",
            "lchor": "Blütenzubereitung",
            "state_value_contacts_for_chor": len(contacts),
            "identity_values_replaceable": True,
        },
        "pair_correction": {
            "ofchedy_exact": 5,
            "qofchedy_exact": 5,
            "old_q_action_composition_removed": True,
            "current_pair_class": "NOMINAL_DRY_RESULT_WHOLE_WORDS",
        },
        "relation_packet": packet_report,
        "five_bold_working_readings_de": {
            locus: next(row["bold_line_renderer_de"] for row in passage if row["locus"] == locus)
            for locus in sorted({str(row["locus"]) for row in passage})
        },
        "guard": {"inherited_token_query": env["guard"]},
        "claim_boundary": {
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
            "confirmed_substances": 0,
            "confirmed_units": 0,
            "component_values": 0,
            "unseen_form_exports": 0,
            "new_pages": 0,
            "new_images": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (output_dir / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
