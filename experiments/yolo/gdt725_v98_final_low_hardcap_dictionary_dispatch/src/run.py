#!/usr/bin/env python3
"""Build V98 by auditing the final sixteen low-hardcap dictionary readings."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt725_v98_final_low_hardcap_dictionary_dispatch"
SRC = EXP / "src"
ART = EXP / "artifacts"
G724 = ROOT / "experiments/yolo/gdt724_v97_remaining_indexed_share_core_context_repair/artifacts"

SOURCE_LEXICAL = G724 / "V97_324_ACTIVE_LEXICAL_READINGS.tsv"
SOURCE_CONTEXT = G724 / "V97_479_CONTEXT_REALIZATIONS.tsv"
SOURCE_CENSUS = G724 / "V97_35_HELD_READING_AUDIT.tsv"
SOURCE_COMPLETE = G724 / "V97_COMPLETE_WORD_CONFIDENCE.tsv"
SOURCE_SPANS = G724 / "V97_5_BOUND_SPAN_RENDERER.tsv"
SOURCE_SPAN_EXECUTION = G724 / "V97_5_BOUND_SPAN_EXECUTION_AUDIT.tsv"
SOURCE_DIRECTIVES = G724 / "V97_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
SOURCE_F7R2 = G724 / "V97_8_F7R2_RENDERED_UNITS.tsv"
READING_SPECS = SRC / "V98_16_READING_SPECS.tsv"
POSITION_SPECS = SRC / "V98_21_POSITION_SPECS.tsv"
COMPANION_LINE_SPEC = SRC / "V98_1_COMPANION_LINE_RENDER_SPEC.tsv"

HISTORICAL = "H0_NONE"
STATUS = (
    "PASS_V98_16_FINAL_LOW_HARDCAP_READINGS_AUDITED__21_POSITIONS__"
    "9_CORE_OR_STRUCTURAL_REPAIRS_PLUS_7_RETAINED__"
    "5_STRUCTURAL_READINGS_SEPARATED__4_ACTION_WHOLES_RETAINED__"
    "72_EVIDENCE_BINDINGS__0_UNAUDITED_HARDCAP__"
    "NO_COMPONENT_EXPORT_NO_SCORE_CREDIT__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None
) -> None:
    materialized = list(rows)
    if fields is None:
        fields = list(materialized[0]) if materialized else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fields})


def split_pipe(value: str) -> list[str]:
    return [
        item.strip()
        for item in value.split("|")
        if item.strip() and item.strip() not in {"NONE", "0"}
    ]


def append_pipe(value: str, addition: str) -> str:
    output: list[str] = []
    for item in [*split_pipe(value), *split_pipe(addition)]:
        if item not in output:
            output.append(item)
    return "|".join(output) if output else "NONE"


def rename_v97(row: dict[str, str]) -> dict[str, Any]:
    return {
        key.replace("v97", "v98").replace("V97", "V98"): value
        for key, value in row.items()
    }


def level(score: int) -> str:
    if score < 20:
        return "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY"
    if score < 40:
        return "W1_WEAK_WORKING"
    if score < 60:
        return "W2_PROVISIONAL_WORKING"
    if score < 80:
        return "W3_SOLID_WORKING_THEORY"
    return "W4_STRONG_WORKING_THEORY"


def fingerprint(row: dict[str, str]) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def parse_selector(selector: str) -> dict[str, str]:
    output: dict[str, str] = {}
    for part in selector.split(";"):
        field, value = part.split("=", 1)
        assert field and field not in output
        output[field] = value
    return output


def select_one(rows: list[dict[str, str]], selector: str) -> dict[str, str]:
    expected = parse_selector(selector)
    matches = [
        row
        for row in rows
        if all(row.get(field) == value for field, value in expected.items())
    ]
    assert len(matches) == 1, (selector, len(matches))
    return matches[0]


def target_indexes(
    lexical: list[dict[str, str]],
    contexts: list[dict[str, str]],
    census: list[dict[str, str]],
) -> tuple[
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
]:
    lexical_by_source: dict[str, dict[str, str]] = {}
    for row in lexical:
        for source_id in split_pipe(row["source_reading_ids"]):
            assert source_id not in lexical_by_source
            lexical_by_source[source_id] = row
    return (
        lexical_by_source,
        {row["position_id"]: row for row in contexts},
        {row["source_reading_id"]: row for row in census},
    )


def source_cache_and_origins(
    reading_specs: list[dict[str, str]], position_specs: list[dict[str, str]]
) -> tuple[dict[Path, list[dict[str, str]]], dict[str, list[tuple[str, dict[str, str]]]]]:
    cache: dict[Path, list[dict[str, str]]] = {}
    positions_by_reading: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in position_specs:
        positions_by_reading[row["source_reading_id"]].append(row)
    origins: dict[str, list[tuple[str, dict[str, str]]]] = {}
    for spec in reading_specs:
        path = ROOT / spec["origin_artifact"]
        assert "f84" not in str(path).casefold()
        if path not in cache:
            cache[path] = read_tsv(path)
        selected: list[tuple[str, dict[str, str]]] = []
        if spec["origin_selector"] == "POSITION_ROWS":
            for position in positions_by_reading[spec["source_reading_id"]]:
                selector = (
                    f"locus={position['expected_locus']};"
                    f"ordinal={position['expected_token_ordinal']};"
                    f"surface={position['expected_surface']}"
                )
                selected.append((selector, select_one(cache[path], selector)))
        else:
            selected.append(
                (spec["origin_selector"], select_one(cache[path], spec["origin_selector"]))
            )
        assert selected
        for _, row in selected:
            assert all(
                not row.get(field, "").casefold().startswith("f84")
                for field in ("page", "locus")
            )
        origins[spec["source_reading_id"]] = selected
    return cache, origins


def build_lineage(
    reading_specs: list[dict[str, str]],
    origins: dict[str, list[tuple[str, dict[str, str]]]],
    positions_by_reading: dict[str, list[dict[str, str]]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for spec in reading_specs:
        source_id = spec["source_reading_id"]
        source_rows = origins[source_id]
        positions = positions_by_reading[source_id]
        output.append(
            {
                "source_reading_id": source_id,
                "surface": spec["surface"],
                "position_ids": "|".join(row["position_id"] for row in positions),
                "active_position_count": len(positions),
                "active_page_count": len({row["expected_page"] for row in positions}),
                "origin_gdt": spec["origin_gdt"],
                "origin_artifact": spec["origin_artifact"],
                "origin_selectors": "|".join(selector for selector, _ in source_rows),
                "origin_row_count": len(source_rows),
                "origin_row_fingerprints_sha256": "|".join(
                    fingerprint(row) for _, row in source_rows
                ),
                "origin_composition": spec["origin_composition"],
                "origin_support_de": spec["origin_support_de"],
                "old_default_de": spec["expected_old_core_de"],
                "v98_dictionary_default_de": spec["v98_dictionary_default_de"],
                "v98_context_summary_de": spec["v98_context_summary_de"],
                "value_kind": spec["value_kind"],
                "structural_tag": spec["structural_tag"],
                "decision": spec["decision"],
                "action_default_allowed": spec["action_default_allowed"],
                "exact_whole_surface_default_allowed": spec[
                    "exact_whole_surface_default_allowed"
                ],
                "component_global_export_allowed": 0,
                "score_credit": 0,
                "historical_confirmation": HISTORICAL,
            }
        )
    return output


def binding_row(
    number: int,
    source_id: str,
    surface: str,
    role: str,
    path: Path,
    selector: str,
    row: dict[str, str],
) -> dict[str, Any]:
    assert "f84" not in str(path).casefold()
    return {
        "binding_id": f"E{number:03d}",
        "source_reading_id": source_id,
        "surface": surface,
        "evidence_role": role,
        "evidence_path": str(path.relative_to(ROOT)),
        "selector": selector,
        "matched_row_fingerprint_sha256": fingerprint(row),
        "source_row_match": 1,
        "score_credit_family_ids": "NONE",
        "historical_confirmation": HISTORICAL,
    }


def build_evidence(
    reading_specs: list[dict[str, str]],
    position_specs: list[dict[str, str]],
    lexical: list[dict[str, str]],
    contexts: list[dict[str, str]],
    census: list[dict[str, str]],
    origins: dict[str, list[tuple[str, dict[str, str]]]],
) -> list[dict[str, Any]]:
    lexical_by_source, context_by_position, census_by_source = target_indexes(
        lexical, contexts, census
    )
    specs_by_id = {row["source_reading_id"]: row for row in reading_specs}
    output: list[dict[str, Any]] = []

    def add(source_id: str, role: str, path: Path, selector: str, row: dict[str, str]) -> None:
        output.append(
            binding_row(
                len(output) + 1,
                source_id,
                specs_by_id[source_id]["surface"],
                role,
                path,
                selector,
                row,
            )
        )

    for spec in reading_specs:
        source_id = spec["source_reading_id"]
        add(
            source_id,
            "V97_ACTIVE_LEXICAL",
            SOURCE_LEXICAL,
            f"v97_reading_id={source_id}",
            lexical_by_source[source_id],
        )
        add(
            source_id,
            "V97_HELD_AUDIT",
            SOURCE_CENSUS,
            f"source_reading_id={source_id}",
            census_by_source[source_id],
        )
    for position in position_specs:
        source_id = position["source_reading_id"]
        add(
            source_id,
            "V97_EXACT_CONTEXT",
            SOURCE_CONTEXT,
            f"position_id={position['position_id']}",
            context_by_position[position["position_id"]],
        )
    for spec in reading_specs:
        source_id = spec["source_reading_id"]
        path = ROOT / spec["origin_artifact"]
        for selector, row in origins[source_id]:
            add(source_id, f"{spec['origin_gdt']}_ORIGIN_ROW", path, selector, row)
    assert len(output) == 72
    assert len({row["binding_id"] for row in output}) == 72
    return output


def build_companion_line_audit(
    companion_specs: list[dict[str, str]],
    source_contexts: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Bind line-only prose repairs without changing a dictionary core or score."""

    context_by_position = {row["position_id"]: row for row in source_contexts}
    output: list[dict[str, Any]] = []
    for spec in companion_specs:
        path = ROOT / spec["source_artifact"]
        assert "f84" not in str(path).casefold()
        source = select_one(read_tsv(path), spec["source_selector"])
        context = context_by_position[spec["position_id"]]
        assert (
            context["source_reading_id"],
            context["page"],
            context["locus"],
            context["token_ordinal"],
            context["surface"],
            context["v97_context_realization_de"],
        ) == (
            spec["source_reading_id"],
            spec["expected_page"],
            spec["expected_locus"],
            spec["expected_token_ordinal"],
            spec["expected_surface"],
            spec["expected_context_realization_de"],
        )
        assert (
            source["page"],
            source["locus"],
            source["ordinal"],
            source["surface"],
        ) == (
            spec["expected_page"],
            spec["expected_locus"],
            spec["expected_token_ordinal"],
            spec["expected_surface"],
        )
        assert (
            spec["line_render_once_de"].replace("vorstehenden ", "")
            == source["new_literal_gloss_de"]
        )
        output.append(
            {
                "position_id": spec["position_id"],
                "source_reading_id": spec["source_reading_id"],
                "page": spec["expected_page"],
                "locus": spec["expected_locus"],
                "token_ordinal": spec["expected_token_ordinal"],
                "surface": spec["expected_surface"],
                "source_gdt": spec["source_gdt"],
                "source_artifact": spec["source_artifact"],
                "source_selector": spec["source_selector"],
                "matched_source_row_fingerprint_sha256": fingerprint(source),
                "matched_source_literal_de": source["new_literal_gloss_de"],
                "v97_context_realization_de": context[
                    "v97_context_realization_de"
                ],
                "v98_dictionary_core_unchanged_de": context[
                    "v97_lexical_core_de"
                ],
                "v97_lexical_score": context["v97_lexical_score"],
                "v98_lexical_score_unchanged": context["v97_lexical_score"],
                "score_delta": 0,
                "line_render_once_de": spec["line_render_once_de"],
                "repair_scope": "LINE_RENDERER_ONLY",
                "evidence_de": spec["evidence_de"],
                "component_global_export_allowed": 0,
                "score_credit": 0,
                "historical_confirmation": HISTORICAL,
            }
        )
    return output


def build_lexical(
    source_rows: list[dict[str, str]], reading_specs: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    specs_by_id = {row["source_reading_id"]: row for row in reading_specs}
    output: list[dict[str, Any]] = []
    seen: Counter[str] = Counter()
    for source in source_rows:
        row = rename_v97(source)
        source_ids = split_pipe(source["source_reading_ids"])
        spec = specs_by_id.get(source_ids[0]) if len(source_ids) == 1 else None
        if spec:
            source_id = source_ids[0]
            seen[source_id] += 1
            assert source["v97_lexical_core_de"] == spec["expected_old_core_de"]
            score = int(source["working_model_score_0_100_not_probability"])
            assert source["working_model_level"] == level(score)
            revised = spec["decision"] == "REVISE"
            assert revised == (
                spec["v98_dictionary_default_de"] != spec["expected_old_core_de"]
            )
            row.update(
                {
                    "v98_lexical_core_de": spec["v98_dictionary_default_de"],
                    "v98_context_realizations_de": spec["v98_context_summary_de"],
                    "repair_modes": append_pipe(
                        source["repair_modes"], "GDT725_FINAL_HARDCAP_AUDIT"
                    ),
                    "resolved_debt_atoms": append_pipe(
                        source["resolved_debt_atoms"], "LOW_HARDCAP_REVIEWED"
                    ),
                    "last_semantic_writer": (
                        "GDT725" if revised else source["last_semantic_writer"]
                    ),
                    "base_score": score,
                    "score_delta_lexical_core": 0,
                    "working_model_score_0_100_not_probability": score,
                    "working_model_level": level(score),
                    "context_realization_score_0_100_not_probability": score,
                    "context_realization_level": level(score),
                    "source_gdts": append_pipe(source["source_gdts"], "GDT725"),
                    "source_artifacts": append_pipe(
                        source["source_artifacts"], "V98_16_READING_SPECS.tsv"
                    ),
                    "relation_word_delta": "0_GDT696_TO_GDT725",
                    "positive_evidence_de": (
                        "GDT725 audit: "
                        + spec["evidence_de"]
                        + " || "
                        + source["positive_evidence_de"]
                    ),
                    "counterevidence_de": (
                        "GDT725 Grenze: "
                        + spec["counterevidence_de"]
                        + " || Keine historische Klartextidentifikation."
                    ),
                    "v98_audit_decision": (
                        "REVISED_DICTIONARY_DEFAULT_OR_STRUCTURAL_TAG"
                        if revised
                        else "REVIEWED_RETAINED_EXACT_WHOLE"
                    ),
                    "v98_evidence_class": spec["lineage_class"],
                    "v98_open_semantic_slots": spec["open_semantic_slots"],
                    "v98_component_global_export_allowed": "0",
                    "v98_exact_whole_surface_default_allowed": spec[
                        "exact_whole_surface_default_allowed"
                    ],
                    "v98_lineage_class": spec["lineage_class"],
                    "v98_prior_lexical_core_de": source["v97_lexical_core_de"],
                    "v98_value_kind": spec["value_kind"],
                    "v98_structural_tag": spec["structural_tag"],
                    "v98_action_default_allowed": spec["action_default_allowed"],
                }
            )
        else:
            row.update(
                {
                    "v98_audit_decision": "INHERITED_V97",
                    "v98_evidence_class": "INHERITED_V97",
                    "v98_open_semantic_slots": "NOT_EVALUATED_GDT725",
                    "v98_component_global_export_allowed": "NOT_EVALUATED_GDT725",
                    "v98_exact_whole_surface_default_allowed": "NOT_EVALUATED_GDT725",
                    "v98_lineage_class": "INHERITED_V97",
                    "v98_prior_lexical_core_de": source["v97_lexical_core_de"],
                    "v98_value_kind": "INHERITED_V97",
                    "v98_structural_tag": "INHERITED_V97",
                    "v98_action_default_allowed": "NOT_EVALUATED_GDT725",
                }
            )
        output.append(row)
    assert len(output) == 324
    assert seen == Counter({source_id: 1 for source_id in specs_by_id})
    by_source: dict[str, dict[str, Any]] = {}
    for row in output:
        for source_id in split_pipe(str(row["source_reading_ids"])):
            assert source_id not in by_source
            by_source[source_id] = row
    assert len(by_source) == 332
    return output, by_source


def build_contexts(
    source_rows: list[dict[str, str]],
    reading_specs: list[dict[str, str]],
    position_specs: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    reading_by_id = {row["source_reading_id"]: row for row in reading_specs}
    position_by_id = {row["position_id"]: row for row in position_specs}
    by_locus_ordinal = {
        (row["locus"], int(row["token_ordinal"])): row for row in source_rows
    }
    output: list[dict[str, Any]] = []
    seen: Counter[str] = Counter()
    for source in source_rows:
        source_id = source["source_reading_id"]
        lexical = lexical_by_source[source_id]
        position = position_by_id.get(source["position_id"])
        spec = reading_by_id.get(source_id)
        row = rename_v97(source)
        if position:
            assert spec is not None
            seen[source["position_id"]] += 1
            assert (
                source["page"],
                source["locus"],
                source["token_ordinal"],
                source["surface"],
                source["v97_context_realization_de"],
                source["v68_clause_type"],
                source["v68_action_license"],
            ) == (
                position["expected_page"],
                position["expected_locus"],
                position["expected_token_ordinal"],
                position["expected_surface"],
                position["expected_old_context_de"],
                position["expected_clause_type"],
                position["expected_action_license"],
            )
            ordinal = int(source["token_ordinal"])
            left = (
                "<BOS>"
                if ordinal == 1
                else by_locus_ordinal[(source["locus"], ordinal - 1)]["surface"]
            )
            right = (
                "<EOS>"
                if (source["locus"], ordinal + 1) not in by_locus_ordinal
                else by_locus_ordinal[(source["locus"], ordinal + 1)]["surface"]
            )
            assert (left, right) == (
                position["expected_left_surface"],
                position["expected_right_surface"],
            )
            row.update(
                {
                    "v98_context_realization_de": position[
                        "v98_context_realization_de"
                    ],
                    "v98_repair_mode": position["context_mode"],
                    "v98_resolved_debt_atom": "LOW_HARDCAP_REVIEWED",
                    "v98_audit_decision": (
                        "REVISED_DICTIONARY_DEFAULT_OR_STRUCTURAL_TAG"
                        if spec["decision"] == "REVISE"
                        else "REVIEWED_RETAINED_EXACT_WHOLE"
                    ),
                    "v98_evidence_class": spec["lineage_class"],
                    "v98_open_semantic_slots": spec["open_semantic_slots"],
                    "v98_component_global_export_allowed": "0",
                    "v98_exact_whole_surface_default_allowed": spec[
                        "exact_whole_surface_default_allowed"
                    ],
                    "v98_lineage_class": spec["lineage_class"],
                    "v98_local_context_hypothesis": position["local_evidence_de"],
                    "v98_expected_left_surface": left,
                    "v98_expected_right_surface": right,
                    "v98_value_kind": spec["value_kind"],
                    "v98_structural_tag": spec["structural_tag"],
                    "v98_action_default_allowed": spec["action_default_allowed"],
                }
            )
        else:
            row.update(
                {
                    "v98_context_realization_de": source[
                        "v97_context_realization_de"
                    ],
                    "v98_audit_decision": "INHERITED_V97",
                    "v98_evidence_class": "INHERITED_V97",
                    "v98_open_semantic_slots": "NOT_EVALUATED_GDT725",
                    "v98_component_global_export_allowed": "NOT_EVALUATED_GDT725",
                    "v98_exact_whole_surface_default_allowed": "NOT_EVALUATED_GDT725",
                    "v98_lineage_class": "INHERITED_V97",
                    "v98_value_kind": "INHERITED_V97",
                    "v98_structural_tag": "INHERITED_V97",
                    "v98_action_default_allowed": "NOT_EVALUATED_GDT725",
                }
            )
        row["v98_reading_id"] = lexical["v98_reading_id"]
        row["v98_lexical_core_de"] = lexical["v98_lexical_core_de"]
        row["v98_lexical_score"] = lexical[
            "working_model_score_0_100_not_probability"
        ]
        row["v98_lexical_level"] = lexical["working_model_level"]
        row["v98_context_score"] = lexical[
            "context_realization_score_0_100_not_probability"
        ]
        row["v98_context_level"] = lexical["context_realization_level"]
        row["v98_historical_confirmation"] = HISTORICAL
        output.append(row)
    assert len(output) == 479
    assert seen == Counter({row["position_id"]: 1 for row in position_specs})
    return output


def build_census(
    source_rows: list[dict[str, str]],
    reading_specs: list[dict[str, str]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    specs_by_id = {row["source_reading_id"]: row for row in reading_specs}
    output: list[dict[str, Any]] = []
    for source in source_rows:
        row = rename_v97(source)
        source_id = source["source_reading_id"]
        spec = specs_by_id.get(source_id)
        if spec:
            lexical = lexical_by_source[source_id]
            revised = spec["decision"] == "REVISE"
            row.update(
                {
                    "disposition": (
                        "REVISED_IN_V98" if revised else "REVIEWED_RETAINED_IN_V98"
                    ),
                    "repair_mode": "GDT725_FINAL_HARDCAP_AUDIT",
                    "resolved_debt_atom": "LOW_HARDCAP_REVIEWED",
                    "v98_reading_id": lexical["v98_reading_id"],
                    "v98_lexical_core_de": lexical["v98_lexical_core_de"],
                    "v98_context_realization_de": spec["v98_context_summary_de"],
                    "new_lexical_score": lexical[
                        "working_model_score_0_100_not_probability"
                    ],
                    "new_lexical_level": lexical["working_model_level"],
                    "new_context_score": lexical[
                        "context_realization_score_0_100_not_probability"
                    ],
                    "new_context_level": lexical["context_realization_level"],
                    "positive_evidence_de": spec["evidence_de"],
                    "counterevidence_de": spec["counterevidence_de"],
                    "v98_audit_decision": (
                        "REVISED_DICTIONARY_DEFAULT_OR_STRUCTURAL_TAG"
                        if revised
                        else "REVIEWED_RETAINED_EXACT_WHOLE"
                    ),
                    "v98_evidence_class": spec["lineage_class"],
                    "v98_open_semantic_slots": spec["open_semantic_slots"],
                    "v98_lineage_class": spec["lineage_class"],
                    "v98_value_kind": spec["value_kind"],
                    "v98_structural_tag": spec["structural_tag"],
                }
            )
        else:
            assert source["disposition"] != "HELD_FOR_LATER_REPAIR"
            row["v98_audit_decision"] = "INHERITED_V97_REVIEW"
            row["v98_value_kind"] = "INHERITED_V97"
            row["v98_structural_tag"] = "INHERITED_V97"
        output.append(row)
    assert len(output) == 35
    assert all(row["disposition"] != "HELD_FOR_LATER_REPAIR" for row in output)
    return output


def build_decisions(
    reading_specs: list[dict[str, str]],
    positions_by_reading: dict[str, list[dict[str, str]]],
    lexical_by_source: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for spec in reading_specs:
        source_id = spec["source_reading_id"]
        positions = positions_by_reading[source_id]
        lexical = lexical_by_source[source_id]
        output.append(
            {
                "source_reading_id": source_id,
                "surface": spec["surface"],
                "decision": spec["decision"],
                "position_ids": "|".join(row["position_id"] for row in positions),
                "position_count": len(positions),
                "pages": "|".join(sorted({row["expected_page"] for row in positions})),
                "old_dictionary_default_de": spec["expected_old_core_de"],
                "v98_dictionary_default_de": spec["v98_dictionary_default_de"],
                "v98_context_summary_de": spec["v98_context_summary_de"],
                "value_kind": spec["value_kind"],
                "structural_tag": spec["structural_tag"],
                "score": lexical["working_model_score_0_100_not_probability"],
                "level": lexical["working_model_level"],
                "score_delta": 0,
                "evidence_de": spec["evidence_de"],
                "counterevidence_de": spec["counterevidence_de"],
                "strongest_rival_de": spec["strongest_rival_de"],
                "open_semantic_slots": spec["open_semantic_slots"],
                "action_default_allowed": spec["action_default_allowed"],
                "exact_whole_surface_default_allowed": spec[
                    "exact_whole_surface_default_allowed"
                ],
                "component_global_export_allowed": 0,
                "historical_confirmation": HISTORICAL,
            }
        )
    return output


def build_rivals(reading_specs: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for spec in reading_specs:
        common = {
            "source_reading_id": spec["source_reading_id"],
            "surface": spec["surface"],
            "component_global_export_allowed": 0,
            "score_credit": 0,
            "historical_confirmation": HISTORICAL,
        }
        output.extend(
            [
                {
                    **common,
                    "model_id": "A_SELECTED_BOUND_DEFAULT_PLUS_LOCAL_RENDERER",
                    "candidate_default_de": spec["v98_dictionary_default_de"],
                    "candidate_context_de": spec["v98_context_summary_de"],
                    "decision": "SELECT",
                    "reason_de": spec["evidence_de"],
                    "selected": 1,
                },
                {
                    **common,
                    "model_id": "B_PREVIOUS_DEFAULT",
                    "candidate_default_de": spec["expected_old_core_de"],
                    "candidate_context_de": spec["expected_old_core_de"],
                    "decision": (
                        "RETAINED_AS_SELECTED"
                        if spec["decision"] == "RETAIN"
                        else "REJECT_AS_OVERFULL_OR_RENDERER_ONLY"
                    ),
                    "reason_de": (
                        "Bereits kleinste konkrete Ganzwortlesung."
                        if spec["decision"] == "RETAIN"
                        else "Vermischt Wörterbuchkern mit lokalem Produktkopf oder bloßer Zeichenausgabe."
                    ),
                    "selected": 0,
                },
                {
                    **common,
                    "model_id": "C_STRONGEST_LIVE_RIVAL",
                    "candidate_default_de": spec["strongest_rival_de"],
                    "candidate_context_de": spec["strongest_rival_de"],
                    "decision": "KEEP_LIVE_COUNTERMODEL",
                    "reason_de": spec["counterevidence_de"],
                    "selected": 0,
                },
            ]
        )
    assert len(output) == 48
    return output


def build_position_renderer(
    contexts: list[dict[str, Any]], position_specs: list[dict[str, str]]
) -> list[dict[str, Any]]:
    by_position = {row["position_id"]: row for row in contexts}
    output: list[dict[str, Any]] = []
    for spec in position_specs:
        row = by_position[spec["position_id"]]
        output.append(
            {
                "position_id": row["position_id"],
                "source_reading_id": spec["source_reading_id"],
                "page": row["page"],
                "locus": row["locus"],
                "token_ordinal": row["token_ordinal"],
                "surface": row["surface"],
                "left_surface": spec["expected_left_surface"],
                "right_surface": spec["expected_right_surface"],
                "dictionary_default_de": row["v98_lexical_core_de"],
                "local_context_realization_de": row[
                    "v98_context_realization_de"
                ],
                "value_kind": row["v98_value_kind"],
                "structural_tag": row["v98_structural_tag"],
                "clause_type": row["v68_clause_type"],
                "action_license": row["v68_action_license"],
                "context_mode": spec["context_mode"],
                "local_evidence_de": spec["local_evidence_de"],
                "score": row["v98_lexical_score"],
                "level": row["v98_lexical_level"],
                "component_global_export_allowed": 0,
                "historical_confirmation": HISTORICAL,
            }
        )
    return output


def build_dispatch_audit(reading_specs: list[dict[str, str]]) -> list[dict[str, Any]]:
    action_words = ("abfüllen", "schließen", "abmessen", "nehmen", "trocknen")
    output: list[dict[str, Any]] = []
    for spec in reading_specs:
        default = spec["v98_dictionary_default_de"]
        is_action = spec["value_kind"] == "ACTION_WHOLE"
        is_structural = spec["value_kind"].startswith("STRUCTURAL")
        if is_action:
            assert any(word in default.casefold() for word in action_words)
        elif not is_structural:
            assert not any(word in default.casefold() for word in action_words)
        if is_structural:
            assert default.startswith("[STRUKTUR:")
        output.append(
            {
                "source_reading_id": spec["source_reading_id"],
                "surface": spec["surface"],
                "value_kind": spec["value_kind"],
                "structural_tag": spec["structural_tag"],
                "dictionary_default_de": default,
                "context_summary_de": spec["v98_context_summary_de"],
                "exact_whole_action_default_allowed": spec[
                    "action_default_allowed"
                ],
                "is_structural_not_spoken_lexeme": int(is_structural),
                "component_action_export_allowed": 0,
                "component_structural_export_allowed": 0,
                "component_global_export_allowed": 0,
                "audit_status": (
                    "PASS_EXACT_ACTION_WHOLE"
                    if is_action
                    else (
                        "PASS_STRUCTURAL_TAG_SEPARATED_FROM_RENDERER"
                        if is_structural
                        else "PASS_NOMINAL_WITHOUT_HIDDEN_IMPERATIVE"
                    )
                ),
                "historical_confirmation": HISTORICAL,
            }
        )
    return output


def build_scope_dictionary() -> list[dict[str, Any]]:
    rows = [
        ("STRUCTURAL_TAGS", "dy#1|dy#2|y#1|y#2|yey#1", "benannte Grenz- oder Anschlussfunktion", "Punkt, Semikolon und Hierzu bleiben lokale Renderer"),
        ("EXACT_ACTION_WHOLES", "aiijy|da|qy|ypchesy", "konkrete Ganzwortaktion", "kein Verbwert wird auf Teilstrings exportiert"),
        ("MULTI_POSITION_QUANTITY", "oror", "zwei Portionen", "keine historische Einheit oder Stoffidentität"),
        ("BOUND_MATERIAL_RESULTS", "chpcheey|cpheesy|kodeey|otytchol|taiky|tail", "exakte Stoff-, Mengen- oder Zustandslesung", "Patienten- und Produktköpfe bleiben lokal oder offen"),
        ("POSITION_DISPATCH", "y|dy", "getrennte Reading-IDs je Kontextrolle", "kein universelles y- oder dy-Wort"),
        ("COMPONENT_EXPORT", "all_16", "NONE", "keine neue Stamm-, Teilstring- oder Neuwortregel"),
        ("CONFIDENCE", "all_16", "Scores und W-Level unverändert", "Auditabschluss ist kein Beweisbonus"),
    ]
    return [
        {
            "scope_item": item,
            "readings_or_surfaces": targets,
            "selected_value_de": selected,
            "bounded_limit_de": limit,
            "score_credit": 0,
            "component_global_export_allowed": 0,
            "historical_confirmation": HISTORICAL,
        }
        for item, targets, selected, limit in rows
    ]


def build_complete(
    source_rows: list[dict[str, str]], lexical: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in source_rows:
        if source["current_layer"] == "ACTIVE_V97_LEXICAL_CORE":
            continue
        row = rename_v97(source)
        row.update(
            {
                "v98_audit_decision": "OUTSIDE_ACTIVE_V98_TRANCHE",
                "v98_evidence_class": "INHERITED_GLOBAL_V48",
                "v98_open_semantic_slots": "NOT_EVALUATED_GDT725",
                "v98_component_global_export_allowed": "NOT_EVALUATED_GDT725",
                "v98_exact_whole_surface_default_allowed": "NOT_EVALUATED_GDT725",
                "v98_lineage_class": "INHERITED_GLOBAL_V48",
                "v98_value_kind": "INHERITED_GLOBAL_V48",
                "v98_structural_tag": "NOT_EVALUATED_GDT725",
                "v98_action_default_allowed": "NOT_EVALUATED_GDT725",
            }
        )
        output.append(row)
    for row in lexical:
        output.append(
            {
                "surface": row["surface"],
                "reading_id": row["v98_reading_id"],
                "working_meaning_de": row["v98_lexical_core_de"],
                "current_layer": "ACTIVE_V98_LEXICAL_CORE",
                "semantic_scope": row["semantic_scope"],
                "semantic_applicability": row["semantic_applicability"],
                "form_level": row["form_level"],
                "occurrence_count": row["occurrence_count"],
                "page_count": row["page_count"],
                "locus_count": row["locus_count"],
                "working_model_score_0_100_not_probability": row[
                    "working_model_score_0_100_not_probability"
                ],
                "working_model_level": row["working_model_level"],
                "source_gdts": row["source_gdts"],
                "positive_evidence_de": row["positive_evidence_de"],
                "counterevidence_de": row["counterevidence_de"],
                "historical_confirmation": row["historical_confirmation"],
                "historical_analogue": row["historical_analogue"],
                "relation_word_delta": row["relation_word_delta"],
                "global_export_scope": row["global_export_scope"],
                "bound_span_ids": row["bound_span_ids"],
                "unconditional_global_export_allowed": row[
                    "unconditional_global_export_allowed"
                ],
                "v98_context_realizations_de": row[
                    "v98_context_realizations_de"
                ],
                "source_reading_ids": row["source_reading_ids"],
                "v98_audit_decision": row["v98_audit_decision"],
                "v98_evidence_class": row["v98_evidence_class"],
                "v98_open_semantic_slots": row["v98_open_semantic_slots"],
                "v98_component_global_export_allowed": row[
                    "v98_component_global_export_allowed"
                ],
                "v98_exact_whole_surface_default_allowed": row[
                    "v98_exact_whole_surface_default_allowed"
                ],
                "v98_lineage_class": row["v98_lineage_class"],
                "v98_value_kind": row["v98_value_kind"],
                "v98_structural_tag": row["v98_structural_tag"],
                "v98_action_default_allowed": row[
                    "v98_action_default_allowed"
                ],
            }
        )
    return sorted(output, key=lambda row: (str(row["surface"]), str(row["reading_id"])))


def render_line(values: list[str]) -> str:
    output = ""
    for value in values:
        if value in {".", ";"}:
            output = output.rstrip(" ·") + value
        else:
            if output and not output.endswith(" "):
                output += " " if output.endswith((".", ";", ":")) else " · "
            output += value
    return output


def render_context_rows(
    rows: list[dict[str, Any]],
    value_field: str,
    bound_spans: list[dict[str, str]],
    position_overrides: dict[str, str],
) -> tuple[str, list[str], list[str]]:
    """Render a locus while consuming each admitted two-position span once."""

    assert rows
    locus = str(rows[0]["locus"])
    by_position = {str(row["position_id"]): row for row in rows}
    values = {
        str(row["position_id"]): str(row[value_field])
        for row in rows
    }
    suppressed: set[str] = set()
    executed_spans: list[str] = []
    for span in bound_spans:
        if span["locus"] != locus:
            continue
        left_id = span["left_position_id"]
        right_id = span["right_position_id"]
        assert left_id in by_position and right_id in by_position
        assert by_position[left_id]["surface"] == span["left_surface"]
        assert by_position[right_id]["surface"] == span["right_surface"]
        assert left_id not in suppressed and right_id not in suppressed
        values[left_id] = span["render_once_de"]
        suppressed.add(right_id)
        executed_spans.append(span["bound_span_id"])

    applied_overrides: list[str] = []
    for position_id, value in position_overrides.items():
        if position_id not in by_position:
            continue
        assert position_id not in suppressed
        values[position_id] = value
        applied_overrides.append(position_id)

    ordered_values = [
        values[str(row["position_id"])]
        for row in rows
        if str(row["position_id"]) not in suppressed
    ]
    return render_line(ordered_values), executed_spans, applied_overrides


def build_repaired_lines(
    source_contexts: list[dict[str, str]],
    target_contexts: list[dict[str, Any]],
    position_specs: list[dict[str, str]],
    bound_spans: list[dict[str, str]],
    companion_specs: list[dict[str, str]],
) -> list[dict[str, Any]]:
    target_loci = {row["expected_locus"] for row in position_specs}
    source_by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    target_by_locus: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    targets_by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_contexts:
        if row["locus"] in target_loci:
            source_by_locus[row["locus"]].append(row)
    for row in target_contexts:
        if row["locus"] in target_loci:
            target_by_locus[row["locus"]].append(row)
    for row in position_specs:
        targets_by_locus[row["expected_locus"]].append(row)
    companion_overrides = {
        row["position_id"]: row["line_render_once_de"] for row in companion_specs
    }
    output: list[dict[str, Any]] = []
    for locus in sorted(target_loci):
        source_rows = sorted(source_by_locus[locus], key=lambda row: int(row["token_ordinal"]))
        target_rows = sorted(target_by_locus[locus], key=lambda row: int(row["token_ordinal"]))
        assert [row["position_id"] for row in source_rows] == [
            row["position_id"] for row in target_rows
        ]
        old_values = [row["v97_context_realization_de"] for row in source_rows]
        new_values = [str(row["v98_context_realization_de"]) for row in target_rows]
        old_reader, old_span_ids, old_companion_ids = render_context_rows(
            source_rows,
            "v97_context_realization_de",
            bound_spans,
            {},
        )
        new_reader, new_span_ids, new_companion_ids = render_context_rows(
            target_rows,
            "v98_context_realization_de",
            bound_spans,
            companion_overrides,
        )
        assert old_span_ids == new_span_ids
        assert not old_companion_ids
        target_positions = targets_by_locus[locus]
        output.append(
            {
                "page": source_rows[0]["page"],
                "locus": locus,
                "target_position_ids": "|".join(row["position_id"] for row in target_positions),
                "target_reading_ids": "|".join(row["source_reading_id"] for row in target_positions),
                "target_surfaces": "|".join(row["expected_surface"] for row in target_positions),
                "surface_sequence": " ".join(row["surface"] for row in source_rows),
                "v97_reader_de": old_reader,
                "v98_reader_de": new_reader,
                "changed_target_positions": sum(
                    old != new for old, new in zip(old_values, new_values, strict=True)
                ),
                "executed_bound_span_ids": (
                    "|".join(new_span_ids) if new_span_ids else "NONE"
                ),
                "companion_line_render_position_ids": (
                    "|".join(new_companion_ids) if new_companion_ids else "NONE"
                ),
                "renderer_change_count": int(old_reader != new_reader),
                "historical_confirmation": HISTORICAL,
            }
        )
    assert len(output) == 18
    return output


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    reading_specs = read_tsv(READING_SPECS)
    position_specs = read_tsv(POSITION_SPECS)
    companion_specs = read_tsv(COMPANION_LINE_SPEC)
    assert len(reading_specs) == 16
    assert len(position_specs) == 21
    assert len(companion_specs) == 1
    assert Counter(row["decision"] for row in reading_specs) == Counter(
        {"REVISE": 9, "RETAIN": 7}
    )
    assert sum(row["value_kind"].startswith("STRUCTURAL") for row in reading_specs) == 5
    assert sum(row["value_kind"] == "ACTION_WHOLE" for row in reading_specs) == 4
    assert all("f84" not in row["expected_page"].casefold() for row in position_specs)

    positions_by_reading: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in position_specs:
        positions_by_reading[row["source_reading_id"]].append(row)
    assert set(positions_by_reading) == {
        row["source_reading_id"] for row in reading_specs
    }

    source_lexical = read_tsv(SOURCE_LEXICAL)
    source_context = read_tsv(SOURCE_CONTEXT)
    source_census = read_tsv(SOURCE_CENSUS)
    source_complete = read_tsv(SOURCE_COMPLETE)
    source_spans = read_tsv(SOURCE_SPANS)
    _, origins = source_cache_and_origins(reading_specs, position_specs)

    evidence = build_evidence(
        reading_specs,
        position_specs,
        source_lexical,
        source_context,
        source_census,
        origins,
    )
    lexical, lexical_by_source = build_lexical(source_lexical, reading_specs)
    contexts = build_contexts(
        source_context, reading_specs, position_specs, lexical_by_source
    )
    census = build_census(source_census, reading_specs, lexical_by_source)
    decisions = build_decisions(reading_specs, positions_by_reading, lexical_by_source)
    lineage = build_lineage(reading_specs, origins, positions_by_reading)
    rivals = build_rivals(reading_specs)
    renderer = build_position_renderer(contexts, position_specs)
    dispatch = build_dispatch_audit(reading_specs)
    scope = build_scope_dictionary()
    complete = build_complete(source_complete, lexical)
    companion_audit = build_companion_line_audit(companion_specs, source_context)
    lines = build_repaired_lines(
        source_context,
        contexts,
        position_specs,
        source_spans,
        companion_specs,
    )

    write_tsv(ART / "V98_324_ACTIVE_LEXICAL_READINGS.tsv", lexical)
    write_tsv(ART / "V98_479_CONTEXT_REALIZATIONS.tsv", contexts)
    write_tsv(ART / "V98_35_READING_AUDIT.tsv", census)
    write_tsv(ART / "V98_16_FINAL_HARDCAP_DECISIONS.tsv", decisions)
    write_tsv(ART / "V98_16_LINEAGE_AUDIT.tsv", lineage)
    write_tsv(ART / "V98_72_EVIDENCE_BINDINGS.tsv", evidence)
    write_tsv(ART / "V98_48_RIVAL_MODEL_COMPARISON.tsv", rivals)
    write_tsv(ART / "V98_21_POSITION_RENDERER.tsv", renderer)
    write_tsv(ART / "V98_16_ACTION_STRUCTURAL_DISPATCH_AUDIT.tsv", dispatch)
    write_tsv(ART / "V98_7_SCOPE_DICTIONARY.tsv", scope)
    write_tsv(ART / "V98_18_REPAIRED_LINES.tsv", lines)
    write_tsv(ART / "V98_1_COMPANION_LINE_RENDER_AUDIT.tsv", companion_audit)
    write_tsv(ART / "V98_COMPLETE_WORD_CONFIDENCE.tsv", complete)
    shutil.copyfile(SOURCE_SPANS, ART / "V98_5_BOUND_SPAN_RENDERER.tsv")
    shutil.copyfile(
        SOURCE_SPAN_EXECUTION, ART / "V98_5_BOUND_SPAN_EXECUTION_AUDIT.tsv"
    )
    shutil.copyfile(
        SOURCE_DIRECTIVES, ART / "V98_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"
    )
    shutil.copyfile(SOURCE_F7R2, ART / "V98_8_F7R2_RENDERED_UNITS.tsv")

    levels = Counter(row["working_model_level"] for row in lexical)
    assert levels == Counter(
        {
            "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
            "W1_WEAK_WORKING": 135,
            "W2_PROVISIONAL_WORKING": 163,
            "W3_SOLID_WORKING_THEORY": 19,
        }
    )
    assert len(complete) == 1586
    assert len({row["surface"] for row in complete}) == 1582
    assert all(row["working_meaning_de"] for row in complete)
    assert all(row["positive_evidence_de"] and row["counterevidence_de"] for row in complete)
    assert all(row["historical_confirmation"] == HISTORICAL for row in complete)

    result = {
        "experiment_id": "GDT725",
        "status": STATUS,
        "target_readings_audited": 16,
        "target_positions": 21,
        "target_lines": 18,
        "target_pages": len({row["expected_page"] for row in position_specs}),
        "revised_defaults_or_structural_tags": 9,
        "reviewed_retained_exact_wholes": 7,
        "structural_readings_separated_from_spoken_translation": 5,
        "exact_action_wholes_retained": 4,
        "multi_position_quantity_invariants": 1,
        "primary_evidence_bindings": len(evidence),
        "rival_model_rows": len(rivals),
        "component_global_exports": 0,
        "score_credit_families": 0,
        "score_delta_total": 0,
        "remaining_unaudited_hardcap_readings": 0,
        "remaining_low_confidence_readings_by_score": 16,
        "active_lexical_rows": len(lexical),
        "active_source_readings": len(lexical_by_source),
        "context_positions": len(contexts),
        "confidence_levels": dict(sorted(levels.items())),
        "complete_dictionary_rows": len(complete),
        "complete_dictionary_surfaces": len({row["surface"] for row in complete}),
        "complete_dictionary_rows_with_default_confidence_and_evidence": sum(
            bool(
                row["working_meaning_de"]
                and row["working_model_level"]
                and row["positive_evidence_de"]
                and row["counterevidence_de"]
            )
            for row in complete
        ),
        "bound_spans_preserved": len(source_spans),
        "bound_spans_executed_in_target_lines": len(
            {
                span_id
                for row in lines
                for span_id in split_pipe(str(row["executed_bound_span_ids"]))
            }
        ),
        "companion_line_renderer_repairs": len(companion_audit),
        "companion_line_renderer_score_or_core_delta": 0,
        "one_shot_directives_preserved": len(read_tsv(SOURCE_DIRECTIVES)),
        "f7r2_output_units_preserved": len(read_tsv(SOURCE_F7R2)),
        "f84_or_f84r_used": 0,
        "historical_confirmation": HISTORICAL,
        "canonical_dictionary": (
            "experiments/yolo/gdt725_v98_final_low_hardcap_dictionary_dispatch/"
            "artifacts/V98_COMPLETE_WORD_CONFIDENCE.tsv"
        ),
    }
    (ART / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
