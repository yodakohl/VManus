#!/usr/bin/env python3
"""Build exact quantity, part-state and preparation-value constructions."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import json
import subprocess
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
BASE_REL = Path("experiments/yolo/gdt759_quantity_part_state_construction_atlas")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G758_RUN_REL = Path(
    "experiments/yolo/gdt758_ychor_follower_global_content_census/src/run.py"
)
G758_OCC_REL = Path(
    "experiments/yolo/gdt758_ychor_follower_global_content_census/"
    "artifacts/FOLLOWER_11_1141_OCCURRENCE_ATLAS.tsv"
)
G758_READER_REL = Path(
    "experiments/yolo/gdt758_ychor_follower_global_content_census/"
    "artifacts/YCHOR_13_REVISED_READER.tsv"
)
G734_DICT_REL = Path(
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/"
    "artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
)
G755_BANK_REL = Path(
    "experiments/yolo/gdt755_top24_historical_register_crosswalk/"
    "src/HISTORICAL_EXPRESSION_BANK.tsv"
)
G755_SOURCES_REL = Path(
    "experiments/yolo/gdt755_top24_historical_register_crosswalk/"
    "src/HISTORICAL_SOURCE_REGISTRY.tsv"
)
G729_HISTORY_REL = Path(
    "experiments/yolo/gdt729_v99r3_fourteen_indexed_quantity_dispatch/"
    "artifacts/HISTORICAL_QUANTITY_COMPARATORS.tsv"
)
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
READERS = ("zl3b_clean", "it2a_clean", "rf1b_clean")
QUANTITY_HEADS = ("s", "or", "ar")
VALUE_FORMS = ("an", "ain", "aiin", "aiiin")
VALUE_DE = {"an": "I", "ain": "II", "aiin": "III", "aiiin": "IV"}
FUSED_S_FORMS = ("san", "sain", "saiin", "saiiin")
OUTPUT_NAMES = (
    "EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv",
    "QUANTITY_96_EXACT_PAIR_ATLAS.tsv",
    "EXACT_CONSTRUCTION_26_PAIR_SUMMARY.tsv",
    "QUANTITY_51_READER_BOUNDARY_CANDIDATES.tsv",
    "QUANTITY_7_EXACT_BOUNDARY_BRIDGES.tsv",
    "FUSED_S_VALUE_FAMILY_REVISION.tsv",
    "PART_STATE_23_EXACT_PAIR_ATLAS.tsv",
    "ODOL_OLS_14_OCCURRENCE_ADJUDICATION.tsv",
    "GDT759_EXACT_CONSTRUCTION_DICTIONARY.tsv",
    "GDT759_13_YCHOR_REVISED_READER.tsv",
    "S_154_CONTEXT_DISPATCH.tsv",
    "HISTORICAL_CONSTRUCTION_COMPARATORS.tsv",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__122_EXACT_CONSTRUCTION_SPANS__96_QUANTITY__"
    "7_EXACT_BOUNDARY_BRIDGES__S_AIIN_SAIIN_SINGLE_EXPRESSION__"
    "OLD_SEED_FAMILY_QUARANTINED__23_PART_STATE__15_CHOR_CHOL__"
    "6_CTHY_CHOL__3_OLS_VALUE__OLS_PREPARATION_REVISED__"
    "ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g758 = load_module("gdt758_builder_for_gdt759", ROOT / G758_RUN_REL)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]
) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def fixed(number: float) -> str:
    return f"{number:.6f}"


def line_position(ordinal: int, count: int) -> str:
    if count == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == count:
        return "LAST"
    return "MIDDLE"


def guarded_cross_query(pages: set[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(CROSS_REL),
        "--selector", "page",
    ]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend((
        "--columns",
        "page,locus,all_three_present,zl3b_clean,it2a_clean,rf1b_clean",
        "--forbid-prefix", "f84", "--forbid-prefix", "f84r",
    ))
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded cross query failed")
    stat_lines = [
        line for line in completed.stderr.splitlines()
        if line.startswith("GUARD_STATS ")
    ]
    if len(stat_lines) != 1:
        raise RuntimeError("guard statistics missing")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(row["page"].startswith("f84") for row in rows):
        raise RuntimeError("sealed page materialized")
    return rows, {
        key: int(value)
        for key, value in json.loads(stat_lines[0][12:]).items()
    }


def normalize_quantity(words: list[str]) -> list[str]:
    output: list[str] = []
    index = 0
    while index < len(words):
        if (
            index + 1 < len(words)
            and words[index] in QUANTITY_HEADS
            and words[index + 1] in VALUE_FORMS
        ):
            output.append(words[index] + words[index + 1])
            index += 2
        else:
            output.append(words[index])
            index += 1
    return output


def boundary_mode(words: list[str], head: str, value: str) -> str:
    separated = any(
        left == head and right == value
        for left, right in zip(words, words[1:])
    )
    fused = head + value in words
    if separated and fused:
        return "BOTH"
    if separated:
        return "SEPARATE"
    if fused:
        return "FUSED"
    return "ABSENT"


def build_boundary_rows(
    cross_rows: list[dict[str, str]]
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for source in cross_rows:
        words = {reader: source[reader].split() for reader in READERS}
        normalized = {
            reader: " ".join(normalize_quantity(words[reader]))
            for reader in READERS
        }
        for head in QUANTITY_HEADS:
            for value in VALUE_FORMS:
                modes = {
                    reader: boundary_mode(words[reader], head, value)
                    for reader in READERS
                }
                mode_set = set(modes.values())
                has_separate = bool(mode_set & {"SEPARATE", "BOTH"})
                has_fused = bool(mode_set & {"FUSED", "BOTH"})
                if not (has_separate and has_fused):
                    continue
                exact_normalized = int(len(set(normalized.values())) == 1)
                output.append({
                    "boundary_candidate_id": "",
                    "page": source["page"],
                    "locus": source["locus"],
                    "head_surface": head,
                    "value_surface": value,
                    "fused_surface": head + value,
                    "value_label": VALUE_DE[value],
                    "zl3b_mode": modes["zl3b_clean"],
                    "it2a_mode": modes["it2a_clean"],
                    "rf1b_mode": modes["rf1b_clean"],
                    "all_three_present": source["all_three_present"],
                    "line_normalized_identical_after_target_merges": exact_normalized,
                    "bridge_class": (
                        "EXACT_NORMALIZED_BOUNDARY_EQUIVALENCE"
                        if exact_normalized else
                        "LOCAL_BOUNDARY_CANDIDATE_WITH_OTHER_READER_DIFFERENCES"
                    ),
                    "zl3b_line": source["zl3b_clean"],
                    "it2a_line": source["it2a_clean"],
                    "rf1b_line": source["rf1b_clean"],
                    "zl3b_normalized": normalized["zl3b_clean"],
                    "it2a_normalized": normalized["it2a_clean"],
                    "rf1b_normalized": normalized["rf1b_clean"],
                    "same_manuscript_alternate_readings": 1,
                    "semantic_identity_inferred": 0,
                    "component_export_credit": 0,
                })
    output.sort(key=lambda row: (
        str(row["page"]), str(row["locus"]),
        str(row["head_surface"]), str(row["value_surface"]),
    ))
    for number, row in enumerate(output, start=1):
        row["boundary_candidate_id"] = f"G759-B{number:03d}"
    return output


def build_span_rows(
    context: object,
    line_meta: dict[str, dict[str, str]],
    pair_data: dict[str, object],
    rules: list[dict[str, str]],
) -> list[dict[str, object]]:
    rule_by_pair = {
        (row["left_surface"], row["right_surface"]): row for row in rules
    }
    pairs: Counter[tuple[str, str]] = pair_data["pairs"]  # type: ignore[assignment]
    lefts: Counter[str] = pair_data["left_opportunities"]  # type: ignore[assignment]
    rights: Counter[str] = pair_data["right_opportunities"]  # type: ignore[assignment]
    occurrences: Counter[str] = pair_data["occurrences"]  # type: ignore[assignment]
    total = int(pair_data["total_pairs"])
    output: list[dict[str, object]] = []
    for locus, line in context.by_line.items():
        for index, (left, right) in enumerate(zip(line, line[1:])):
            left_surface = str(left["eva"])
            right_surface = str(right["eva"])
            rule = rule_by_pair.get((left_surface, right_surface))
            if rule is None:
                continue
            if not (
                context.exact[(locus, int(left["token_index"]))]
                and context.exact[(locus, int(right["token_index"]))]
            ):
                continue
            denominator = int(lefts[left_surface])
            background = int(rights[right_surface])
            conditional = int(pairs[(left_surface, right_surface)]) / denominator
            baseline = background / total
            ordinal = index + 1
            previous = str(line[index - 1]["eva"]) if index else "LINE_EDGE"
            following = (
                str(line[index + 2]["eva"])
                if index + 2 < len(line) else "LINE_EDGE"
            )
            meta = line_meta[locus]
            output.append({
                "construction_span_id": "",
                "rule_id": rule["rule_id"],
                "family": rule["family"],
                "page": left["page"],
                "physical_folio": g758.g756.g755.g753.g752.g751.g750.g749.g746.g745.physical_folio(left["page"]),
                "locus": locus,
                "left_token_ordinal": ordinal,
                "right_token_ordinal": ordinal + 1,
                "line_token_count": len(line),
                "span_line_position": line_position(ordinal, len(line)),
                "paragraph_first_span": int(meta["paragraph_start"] == "1" and ordinal == 1),
                "paragraph_last_span": int(meta["paragraph_end"] == "1" and ordinal + 1 == len(line)),
                "section": left["section"],
                "language": left["language"],
                "hand": left["hand"],
                "left_surface": left_surface,
                "right_surface": right_surface,
                "exact_span_eva": f"{left_surface} {right_surface}",
                "fused_counterpart_surface": left_surface + right_surface,
                "fused_counterpart_reader_exact_occurrences": occurrences[left_surface + right_surface],
                "value_label": VALUE_DE.get(right_surface, "NONE"),
                "immediate_left_context": previous,
                "immediate_right_context": following,
                "written_line_eva": " ".join(str(token["eva"]) for token in line),
                "exact_pair_global_count": pairs[(left_surface, right_surface)],
                "left_exact_right_contexts": denominator,
                "pair_conditional_rate": fixed(conditional),
                "right_surface_global_pair_baseline": fixed(baseline),
                "descriptive_lift": fixed(conditional / baseline if baseline else 0.0),
                "primary_render_de": rule["primary_render_de"],
                "alternate_1_de": rule["alternate_1_de"],
                "alternate_2_de": rule["alternate_2_de"],
                "working_confidence": rule["working_confidence"],
                "rationale": rule["rationale"],
                "claim_scope": rule["claim_scope"],
                "reader_exact_left": 1,
                "reader_exact_right": 1,
                "exact_span_render_once": 1,
                "confirmed_plaintext": 0,
                "component_export_credit": 0,
            })
    output.sort(key=lambda row: (
        str(row["family"]), str(row["page"]), str(row["locus"]),
        int(row["left_token_ordinal"]), str(row["rule_id"]),
    ))
    for number, row in enumerate(output, start=1):
        row["construction_span_id"] = f"G759-S{number:04d}"
    return output


def build_pair_summary(
    rules: list[dict[str, str]],
    spans: list[dict[str, object]],
    pair_data: dict[str, object],
    boundaries: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_rule: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in spans:
        by_rule[str(row["rule_id"])].append(row)
    boundary_by_pair: defaultdict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in boundaries:
        boundary_by_pair[(str(row["head_surface"]), str(row["value_surface"]))].append(row)
    occurrences: Counter[str] = pair_data["occurrences"]  # type: ignore[assignment]
    output: list[dict[str, object]] = []
    for rule in rules:
        selected = by_rule[rule["rule_id"]]
        boundary = boundary_by_pair[(rule["left_surface"], rule["right_surface"])]
        output.append({
            "rule_id": rule["rule_id"],
            "family": rule["family"],
            "left_surface": rule["left_surface"],
            "right_surface": rule["right_surface"],
            "exact_pair_occurrences": len(selected),
            "exact_pair_pages": len({str(row["page"]) for row in selected}),
            "exact_pair_loci": len({str(row["locus"]) for row in selected}),
            "fused_counterpart_surface": rule["left_surface"] + rule["right_surface"],
            "fused_counterpart_reader_exact_occurrences": occurrences[rule["left_surface"] + rule["right_surface"]],
            "reader_boundary_candidates": len(boundary),
            "exact_normalized_boundary_bridges": sum(
                int(row["line_normalized_identical_after_target_merges"])
                for row in boundary
            ),
            "line_first_spans": sum(row["span_line_position"] in {"FIRST", "SINGLE"} for row in selected),
            "line_middle_spans": sum(row["span_line_position"] == "MIDDLE" for row in selected),
            "line_final_spans": sum(
                int(row["paragraph_last_span"]) or (
                    int(row["right_token_ordinal"]) == int(row["line_token_count"])
                ) for row in selected
            ),
            "descriptive_lift": selected[0]["descriptive_lift"] if selected else "0.000000",
            "primary_render_de": rule["primary_render_de"],
            "alternate_1_de": rule["alternate_1_de"],
            "alternate_2_de": rule["alternate_2_de"],
            "working_confidence": rule["working_confidence"],
            "disposition": "LICENSE_EXACT_OBSERVED_SPAN" if selected else "NO_DIRECT_PAIR_OBSERVED",
            "rationale": rule["rationale"],
            "component_export_credit": 0,
        })
    return output


def build_fused_revisions(
    specs: list[dict[str, str]],
    dictionary: list[dict[str, str]],
    pair_data: dict[str, object],
    summaries: list[dict[str, object]],
) -> list[dict[str, object]]:
    occurrences: Counter[str] = pair_data["occurrences"]  # type: ignore[assignment]
    old_by_surface: defaultdict[str, list[str]] = defaultdict(list)
    source_ids: defaultdict[str, list[str]] = defaultdict(list)
    for row in dictionary:
        surface = row["surface"]
        if surface not in FUSED_S_FORMS:
            continue
        old_by_surface[surface].append(row["v99r7_spoken_default_de"])
        source_ids[surface].append(row["reading_id"])
    summary_by_pair = {
        (str(row["left_surface"]), str(row["right_surface"])): row
        for row in summaries
    }
    output: list[dict[str, object]] = []
    for spec in specs:
        pair = (spec["head_surface"], spec["value_surface"])
        summary = summary_by_pair[pair]
        old_values = sorted(set(old_by_surface[spec["surface"]]))
        output.append({
            "surface": spec["surface"],
            "head_surface": spec["head_surface"],
            "value_surface": spec["value_surface"],
            "value_label": VALUE_DE[spec["value_surface"]],
            "reader_exact_fused_occurrences": occurrences[spec["surface"]],
            "reader_exact_separated_occurrences": summary["exact_pair_occurrences"],
            "reader_boundary_candidates": summary["reader_boundary_candidates"],
            "exact_normalized_boundary_bridges": summary["exact_normalized_boundary_bridges"],
            "old_reading_ids": "|".join(sorted(source_ids[spec["surface"]])) or "NONE",
            "old_seed_based_defaults_de": " || ".join(old_values) or "NONE",
            "old_seed_default_disposition": "QUARANTINED_RETIRED_S_EQUALS_SEED_LINEAGE",
            "new_primary_de": spec["new_primary_de"],
            "alternate_1_de": spec["alternate_1_de"],
            "alternate_2_de": spec["alternate_2_de"],
            "working_confidence": spec["working_confidence"],
            "revision_reason": spec["revision_reason"],
            "exact_whole_overlay_allowed": 1,
            "historical_unit_identity_confirmed": 0,
            "component_export_credit": 0,
        })
    return output


def build_odol_ols_adjudication(
    occurrences: list[dict[str, str]],
    spans: list[dict[str, object]],
) -> list[dict[str, object]]:
    span_by_start = {
        (str(row["locus"]), int(row["left_token_ordinal"])): row
        for row in spans if row["family"] == "PREPARATION_VALUE"
    }
    output: list[dict[str, object]] = []
    for row in occurrences:
        if row["surface"] not in {"odol", "ols"}:
            continue
        key = (row["locus"], int(row["token_ordinal"]))
        phrase = span_by_start.get(key)
        if row["surface"] == "odol":
            primary = "abgemessene Zubereitung"
            decision = "KEEP_MEASURED_PREPARATION_C1"
            reason = (
                "zwei Herbal-Vorkommen: einmal Zeilenkopf vor Prozesskette, einmal "
                "direkt nach ychor vor einer unsicheren Mengenform; kein reader-exaktes "
                "odol-Wert-Paar"
            )
            confidence = "C1_SPARSE_MULTIWHOLE_EXPLORATORY"
        else:
            primary = "abgeseihte Zubereitung"
            decision = "REVISE_RESULT_TO_VALUE_BEARING_PREPARATION_C0"
            reason = (
                "drei von fünf exakten rechten Kontexten sind geordnete Werte und "
                "fünf von zwölf Vorkommen sind zeilenfinal; dies trägt eine "
                "Zubereitung, aber weder einen bloßen Imperativ noch sichere Ölidentität"
            )
            confidence = "C0_SPARSE_MIXED_POSITION_EXPLORATORY"
        output.append({
            "surface": row["surface"],
            "page": row["page"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "line_position": row["line_position"],
            "immediate_left_surface": row["immediate_left_surface"],
            "immediate_right_surface": row["immediate_right_surface"],
            "boundary_complete": row["boundary_complete"],
            "independent_anchor_tags": row["independent_anchor_tags"],
            "field_channel": row["field_channel"],
            "written_line_eva": row["written_line_eva"],
            "gdt758_candidate_de": row["gdt758_primary_candidate_de"],
            "gdt759_candidate_de": primary,
            "candidate_changed": int(row["gdt758_primary_candidate_de"] != primary),
            "exact_value_span_render_de": phrase["primary_render_de"] if phrase else "NONE",
            "decision": decision,
            "working_confidence": confidence,
            "reason": reason,
            "oil_rival": "Öl / ölige Zubereitung" if row["surface"] == "ols" else "NONE",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    output.sort(key=lambda row: (str(row["surface"]), str(row["page"]), str(row["locus"])))
    return output


def build_dictionary(
    summaries: list[dict[str, object]]
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in summaries:
        if not int(row["exact_pair_occurrences"]):
            continue
        output.append({
            "exact_expression_eva": f"{row['left_surface']} {row['right_surface']}",
            "family": row["family"],
            "working_render_de": row["primary_render_de"],
            "working_confidence": row["working_confidence"],
            "exact_occurrences": row["exact_pair_occurrences"],
            "pages": row["exact_pair_pages"],
            "fused_counterpart_surface": row["fused_counterpart_surface"],
            "fused_counterpart_occurrences": row["fused_counterpart_reader_exact_occurrences"],
            "exact_boundary_bridges": row["exact_normalized_boundary_bridges"],
            "alternate_1_de": row["alternate_1_de"],
            "alternate_2_de": row["alternate_2_de"],
            "evidence": row["rationale"],
            "scope": "EXACT_OBSERVED_SPAN_ONLY",
            "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    return output


def build_revised_ychor_reader(
    rows: list[dict[str, str]]
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    old = "abgeseihtes Endprodukt"
    new = "abgeseihte Zubereitung"
    for row in rows:
        revised = dict(row)
        changed_fields: list[str] = []
        for field in (
            "token_candidate_map_de", "uncomposed_candidate_render_de",
            "span_composed_candidate_render_de", "recipe_command_rival_render_de",
        ):
            value = revised[field]
            if old in value:
                revised[field] = value.replace(old, new)
                changed_fields.append(field)
        revised["gdt759_changed_from_gdt758"] = int(bool(changed_fields))
        revised["gdt759_change_reason"] = (
            "ols result noun widened to value-bearing strained preparation"
            if changed_fields else "NONE"
        )
        revised["candidate_line_not_plaintext"] = 1
        revised["confirmed_lexeme"] = 0
        output.append(revised)
    return output


def build_s_dispatch(
    occurrences: list[dict[str, str]], rules: list[dict[str, str]]
) -> list[dict[str, object]]:
    quantity_rules = {
        row["right_surface"]: row
        for row in rules
        if row["family"] == "QUANTITY_VALUE" and row["left_surface"] == "s"
    }
    output: list[dict[str, object]] = []
    for row in occurrences:
        if row["surface"] != "s":
            continue
        right = row["immediate_right_surface"]
        right_exact = row["immediate_right_reader_exact"] == "1"
        if right_exact and right in VALUE_FORMS:
            rule = quantity_rules[right]
            context_class = "ORDERED_VALUE_SPAN"
            render = rule["primary_render_de"]
            confidence = rule["working_confidence"]
            alternate = f"{rule['alternate_1_de']} || {rule['alternate_2_de']}"
        elif right_exact and right == "om":
            context_class = "EXACT_S_OM_DISTRIBUTIVE_SPAN"
            render = "je eine Handvoll"
            confidence = "C1_SINGLE_OBSERVED_SPAN"
            alternate = "eine Drachme einer Handvoll || eine gleiche Handvoll"
        elif row["line_position"] in {"LAST", "SINGLE"}:
            context_class = "LINE_FINAL_AMOUNT_FORMULA"
            render = "zu gleichen Teilen"
            confidence = "C0_POSITIONAL_FALLBACK"
            alternate = "Drachmenzeichen || Mengenzeichen"
        else:
            context_class = "OTHER_S_CONTEXT"
            render = "je"
            confidence = "C0_GLOBAL_FALLBACK"
            alternate = "Drachmenzeichen || Mengen-/Anteilszeichen"
        output.append({
            "gdt758_occurrence_id": row["gdt758_occurrence_id"],
            "page": row["page"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "line_position": row["line_position"],
            "immediate_left_surface": row["immediate_left_surface"],
            "immediate_right_surface": right,
            "immediate_right_reader_exact": row["immediate_right_reader_exact"],
            "context_class": context_class,
            "gdt758_global_render_de": row["gdt758_renderer_value_de"],
            "gdt759_context_render_de": render,
            "working_confidence": confidence,
            "live_alternatives_de": alternate,
            "written_line_eva": row["written_line_eva"],
            "exact_whole_or_span_scope": (
                "EXACT_TWO_WHOLE_SPAN" if context_class in {
                    "ORDERED_VALUE_SPAN", "EXACT_S_OM_DISTRIBUTIVE_SPAN"
                } else "S_OCCURRENCE_FALLBACK"
            ),
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def build_historical_comparators(
    bank_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
    quantity_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    selected_ids = {"E004", "E005", "E006"}
    sources = {row["source_id"]: row for row in source_rows}
    output: list[dict[str, object]] = []
    for expression in bank_rows:
        if expression["candidate_id"] not in selected_ids:
            continue
        for source_id in expression["source_ids"].split("|"):
            source = sources[source_id]
            output.append({
                "comparator_id": expression["candidate_id"],
                "source_id": source_id,
                "date_band": source["date_band"],
                "register": source["registers"],
                "source_title": source["work"],
                "primary_url": source["primary_url"],
                "attested_form_or_summary": expression["attested_form"],
                "functional_use": expression["working_gloss_de"],
                "target_family": "S_VALUE_UNIT_OR_EQUAL_AMOUNT",
                "decision_use": (
                    "Drachmen- und Unzenzeichen plus Wert sowie ana bleiben "
                    "konkurrierende historische Funktionsmodelle"
                ),
                "voynich_graphic_identity_credit": 0,
                "historical_lexeme_confirmation": 0,
            })
    for row in quantity_rows:
        output.append({
            "comparator_id": row["comparator_id"],
            "source_id": "EXTERNAL_COMPARATOR",
            "date_band": row["date_scope"],
            "register": row["register"],
            "source_title": row["source_title"],
            "primary_url": row["source_url"],
            "attested_form_or_summary": row["witness_summary_de"],
            "functional_use": row["decision_use"],
            "target_family": "PORTION_SHARE_VALUE_OR_UNIT",
            "decision_use": row["decision_use"],
            "voynich_graphic_identity_credit": 0,
            "historical_lexeme_confirmation": 0,
        })
    return output


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rules = read_tsv(SRC / "EXACT_CONSTRUCTION_PRIORS.tsv")
    fused_specs = read_tsv(SRC / "FUSED_QUANTITY_FAMILY_PRIORS.tsv")
    g758_occurrences = read_tsv(ROOT / G758_OCC_REL)
    g758_reader = read_tsv(ROOT / G758_READER_REL)
    g734_dictionary = read_tsv(ROOT / G734_DICT_REL)
    historical_bank = read_tsv(ROOT / G755_BANK_REL)
    historical_sources = read_tsv(ROOT / G755_SOURCES_REL)
    historical_quantity = read_tsv(ROOT / G729_HISTORY_REL)
    if len(rules) != 26 or len(fused_specs) != 4:
        raise AssertionError("fixed 26 construction priors and four fused revisions required")
    if len({row["rule_id"] for row in rules}) != len(rules):
        raise AssertionError("duplicate construction rule")

    context, line_meta, inherited_guard = g758.g756.g755.g753.g752.g751.load_context()
    pair_data = g758.pair_universe(context)
    allowed_pages = {
        str(token["page"])
        for line in context.by_line.values() for token in line
    }
    cross_rows, cross_guard = guarded_cross_query(allowed_pages)
    boundaries = build_boundary_rows(cross_rows)
    spans = build_span_rows(context, line_meta, pair_data, rules)
    summaries = build_pair_summary(rules, spans, pair_data, boundaries)
    fused_revisions = build_fused_revisions(
        fused_specs, g734_dictionary, pair_data, summaries
    )
    odol_ols = build_odol_ols_adjudication(g758_occurrences, spans)
    dictionary = build_dictionary(summaries)
    revised_reader = build_revised_ychor_reader(g758_reader)
    s_dispatch = build_s_dispatch(g758_occurrences, rules)
    historical = build_historical_comparators(
        historical_bank, historical_sources, historical_quantity
    )
    quantity = [row for row in spans if row["family"] == "QUANTITY_VALUE"]
    part_state = [row for row in spans if row["family"] == "PART_STATE"]
    preparation = [row for row in spans if row["family"] == "PREPARATION_VALUE"]
    exact_boundaries = [
        row for row in boundaries
        if int(row["line_normalized_identical_after_target_merges"])
    ]

    quantity_counts = Counter(
        (str(row["left_surface"]), str(row["right_surface"]))
        for row in quantity
    )
    part_counts = Counter(
        (str(row["left_surface"]), str(row["right_surface"]))
        for row in part_state
    )
    expected_quantity = Counter({
        ("s", "ain"): 1, ("s", "aiin"): 23, ("s", "aiiin"): 1,
        ("or", "ain"): 1, ("or", "aiin"): 36, ("or", "aiiin"): 7,
        ("ar", "ain"): 5, ("ar", "aiin"): 16, ("ar", "aiiin"): 6,
    })
    expected_parts = Counter({
        ("chor", "chol"): 8, ("chol", "chor"): 7,
        ("cthy", "chol"): 2, ("chol", "cthy"): 4,
        ("chor", "qokchol"): 1, ("qokchol", "chor"): 1,
    })
    if quantity_counts != expected_quantity:
        raise AssertionError(f"quantity pair universe changed: {quantity_counts}")
    if part_counts != expected_parts:
        raise AssertionError(f"part-state pair universe changed: {part_counts}")
    if len(preparation) != 3 or len(spans) != 122:
        raise AssertionError("expected 3 preparation and 122 total construction spans")
    if len(boundaries) != 51 or len(exact_boundaries) != 7:
        raise AssertionError("quantity boundary universe changed")
    exact_bridge_counts = Counter(
        (str(row["head_surface"]), str(row["value_surface"]))
        for row in exact_boundaries
    )
    if exact_bridge_counts != Counter({
        ("s", "aiin"): 4, ("or", "ain"): 1,
        ("or", "aiin"): 1, ("ar", "aiin"): 1,
    }):
        raise AssertionError(f"exact boundary bridge counts changed: {exact_bridge_counts}")
    if len(odol_ols) != 14 or len(dictionary) != 17:
        raise AssertionError("odol/ols or construction dictionary universe changed")
    if len(s_dispatch) != 154:
        raise AssertionError("expected all 154 reader-exact s occurrences")
    if Counter(str(row["context_class"]) for row in s_dispatch) != Counter({
        "ORDERED_VALUE_SPAN": 25,
        "EXACT_S_OM_DISTRIBUTIVE_SPAN": 1,
        "LINE_FINAL_AMOUNT_FORMULA": 34,
        "OTHER_S_CONTEXT": 94,
    }):
        raise AssertionError("s context dispatch universe changed")
    if len(historical) != 13:
        raise AssertionError("expected thirteen historical comparator rows")
    if sum(int(row["gdt759_changed_from_gdt758"]) for row in revised_reader) != 1:
        raise AssertionError("expected one revised ychor line")

    write_tsv(output_dir / OUTPUT_NAMES[0], spans, list(spans[0]))
    write_tsv(output_dir / OUTPUT_NAMES[1], quantity, list(quantity[0]))
    write_tsv(output_dir / OUTPUT_NAMES[2], summaries, list(summaries[0]))
    write_tsv(output_dir / OUTPUT_NAMES[3], boundaries, list(boundaries[0]))
    write_tsv(output_dir / OUTPUT_NAMES[4], exact_boundaries, list(exact_boundaries[0]))
    write_tsv(output_dir / OUTPUT_NAMES[5], fused_revisions, list(fused_revisions[0]))
    write_tsv(output_dir / OUTPUT_NAMES[6], part_state, list(part_state[0]))
    write_tsv(output_dir / OUTPUT_NAMES[7], odol_ols, list(odol_ols[0]))
    write_tsv(output_dir / OUTPUT_NAMES[8], dictionary, list(dictionary[0]))
    write_tsv(output_dir / OUTPUT_NAMES[9], revised_reader, list(revised_reader[0]))
    write_tsv(output_dir / OUTPUT_NAMES[10], s_dispatch, list(s_dispatch[0]))
    write_tsv(output_dir / OUTPUT_NAMES[11], historical, list(historical[0]))

    result = {
        "schema": "GDT759_RESULT_V1",
        "status": STATUS,
        "scope": {
            "construction_prior_pairs": len(rules),
            "observed_construction_pair_types": len(dictionary),
            "exact_construction_spans": len(spans),
            "quantity_exact_pair_occurrences": len(quantity),
            "quantity_observed_pair_types": len(quantity_counts),
            "quantity_boundary_candidates": len(boundaries),
            "quantity_exact_normalized_boundary_bridges": len(exact_boundaries),
            "part_state_exact_pair_occurrences": len(part_state),
            "part_state_observed_pair_types": len(part_counts),
            "preparation_value_exact_pair_occurrences": len(preparation),
            "odol_ols_occurrences_adjudicated": len(odol_ols),
            "fused_s_value_forms_revised": len(fused_revisions),
            "fused_s_value_reader_exact_occurrences": sum(
                int(row["reader_exact_fused_occurrences"])
                for row in fused_revisions
            ),
            "revised_ychor_lines": len(revised_reader),
            "changed_ychor_lines": sum(
                int(row["gdt759_changed_from_gdt758"])
                for row in revised_reader
            ),
            "s_context_dispatch_occurrences": len(s_dispatch),
            "historical_comparator_rows": len(historical),
            "cached_pages_in_guarded_context": len(allowed_pages),
        },
        "quantity_result": {
            "s_aiin_exact_separated": quantity_counts[("s", "aiin")],
            "saiin_reader_exact_fused": next(
                int(row["reader_exact_fused_occurrences"])
                for row in fused_revisions if row["surface"] == "saiin"
            ),
            "s_aiin_exact_boundary_bridges": exact_bridge_counts[("s", "aiin")],
            "or_value_pairs": sum(count for (head, _), count in quantity_counts.items() if head == "or"),
            "ar_value_pairs": sum(count for (head, _), count in quantity_counts.items() if head == "ar"),
            "s_value_pairs": sum(count for (head, _), count in quantity_counts.items() if head == "s"),
            "primary_s_aiin_render_de": "drei Drachmen",
            "s_aiin_live_rivals_de": ["drei gleiche Teile", "drei Unzen"],
            "old_seed_family_disposition": "QUARANTINED",
            "s_context_dispatch": {
                key: value for key, value in sorted(Counter(
                    str(row["context_class"]) for row in s_dispatch
                ).items())
            },
        },
        "part_state_result": {
            "chor_chol_both_directions": part_counts[("chor", "chol")] + part_counts[("chol", "chor")],
            "cthy_chol_both_directions": part_counts[("cthy", "chol")] + part_counts[("chol", "cthy")],
            "chor_qokchol_both_directions": part_counts[("chor", "qokchol")] + part_counts[("qokchol", "chor")],
            "direct_sheol_part_pairs": sum(
                count for (left, right), count in part_counts.items()
                if left == "sheol" or right == "sheol"
            ),
            "licensed_exact_phrases_de": [
                "getrockneter Blüten-/Samenstand",
                "getrocknetes Blattgut",
                "erhitzter und getrockneter Blüten-/Samenstand",
            ],
        },
        "preparation_result": {
            "odol": "abgemessene Zubereitung retained C1",
            "ols": "abgeseihtes Endprodukt -> abgeseihte Zubereitung C0",
            "ols_ordered_value_exact_pairs": len(preparation),
            "oil_identity": "LIVE_RIVAL_NOT_SELECTED",
        },
        "guard": {
            "inherited_token_query": inherited_guard,
            "cross_reader_query": cross_guard,
        },
        "claim_boundary": {
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
            "confirmed_historical_units": 0,
            "component_values": 0,
            "new_pages": 0,
            "new_images": 0,
            "new_transcriptions": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (output_dir / OUTPUT_NAMES[12]).write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    result = build(parser.parse_args().output_dir)
    print(json.dumps({
        "status": result["status"],
        "scope": result["scope"],
        "quantity_result": result["quantity_result"],
        "part_state_result": result["part_state_result"],
        "preparation_result": result["preparation_result"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
