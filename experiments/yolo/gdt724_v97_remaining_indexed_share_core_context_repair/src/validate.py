#!/usr/bin/env python3
"""Independent validator for GDT724/V97."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt724_v97_remaining_indexed_share_core_context_repair"
SRC = EXP / "src"
ART = EXP / "artifacts"
G723 = ROOT / "experiments/yolo/gdt723_v96_twelve_preparation_bound_core_context_repair/artifacts"
HISTORICAL = "H0_NONE"
ACTION_IDS = {"fdar#1", "lldar#1"}
TARGET_IDS = {
    "airoy#1",
    "araram#1",
    "arl#1",
    "chear#1",
    "chotar#1",
    "daiiiry#1",
    "dairody#1",
    "fdar#1",
    "karchees#1",
    "lkar#1",
    "lldar#1",
    "losair#1",
    "ockhdar#1",
    "okeeodar#1",
    "olkaiir#1",
    "oroiir#1",
    "polairy#1",
    "sairy#1",
    "saraiin#1",
}
EXPECTED_STATUS = (
    "PASS_V97_19_REMAINING_INDEXED_SHARE_HOLDS_AUDITED__"
    "16_CORE_CONTEXT_REPAIRS_PLUS_3_EXACT_WHOLES_RETAINED__"
    "2_LOCAL_ACTIONS_SEPARATED__16_WEAK_READINGS_REMAIN__"
    "82_EVIDENCE_BINDINGS__NO_COMPONENT_EXPORT_NO_SCORE_CREDIT__ALL_H0_NONE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def split_pipe(value: str) -> list[str]:
    return [
        part.strip()
        for part in value.split("|")
        if part.strip() and part.strip() not in {"NONE", "0"}
    ]


def parse_selector(value: str) -> dict[str, str]:
    output: dict[str, str] = {}
    for part in value.split(";"):
        field, expected = part.split("=", 1)
        assert field and field not in output
        output[field] = expected
    return output


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
    payload = json.dumps(
        row, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: Counter[str] = Counter()

    def check(group: str, condition: bool, detail: Any = "") -> None:
        assert condition, (group, detail)
        checks[group] += 1

    specs = read_tsv(SRC / "V97_19_AUDIT_SPECS.tsv")
    lexical = read_tsv(ART / "V97_324_ACTIVE_LEXICAL_READINGS.tsv")
    contexts = read_tsv(ART / "V97_479_CONTEXT_REALIZATIONS.tsv")
    census = read_tsv(ART / "V97_35_HELD_READING_AUDIT.tsv")
    delta = read_tsv(ART / "V97_19_INDEXED_SHARE_CORE_CONTEXT_DELTA.tsv")
    scope = read_tsv(ART / "V97_7_SCOPE_DICTIONARY.tsv")
    rivals = read_tsv(ART / "V97_57_RIVAL_MODEL_COMPARISON.tsv")
    evidence = read_tsv(ART / "V97_82_EVIDENCE_BINDINGS.tsv")
    lineage = read_tsv(ART / "V97_19_LINEAGE_AUDIT.tsv")
    renderer = read_tsv(ART / "V97_19_TARGET_RENDERER.tsv")
    separation = read_tsv(ART / "V97_19_ACTION_HEAD_SEPARATION.tsv")
    complete = read_tsv(ART / "V97_COMPLETE_WORD_CONFIDENCE.tsv")
    spans = read_tsv(ART / "V97_5_BOUND_SPAN_RENDERER.tsv")
    execution = read_tsv(ART / "V97_5_BOUND_SPAN_EXECUTION_AUDIT.tsv")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    source_lexical = read_tsv(G723 / "V96_324_ACTIVE_LEXICAL_READINGS.tsv")
    source_context = read_tsv(G723 / "V96_479_CONTEXT_REALIZATIONS.tsv")

    check("counts", len(specs) == 19)
    check("counts", {row["source_reading_id"] for row in specs} == TARGET_IDS)
    check(
        "counts",
        Counter(row["decision"] for row in specs)
        == Counter({"REVISE": 16, "RETAIN": 3}),
    )
    check("counts", len(lexical) == 324)
    check("counts", len(contexts) == 479)
    check("counts", len(census) == 35)
    check("counts", len(delta) == 19)
    check("counts", len(scope) == 7)
    check("counts", len(rivals) == 57)
    check("counts", len(evidence) == 82)
    check("counts", len(lineage) == 19)
    check("counts", len(renderer) == 19)
    check("counts", len(separation) == 19)
    check("counts", len(complete) == 1586)
    check("counts", len({row["surface"] for row in complete}) == 1582)
    check("counts", len(spans) == len(execution) == 5)

    spec_by_id = {row["source_reading_id"]: row for row in specs}
    lexical_by_source: dict[str, dict[str, str]] = {}
    for row in lexical:
        for source_id in split_pipe(row["source_reading_ids"]):
            check("lexical_index", source_id not in lexical_by_source, source_id)
            lexical_by_source[source_id] = row
    check("lexical_index", len(lexical_by_source) == 332)

    for source_id, spec in spec_by_id.items():
        row = lexical_by_source[source_id]
        score = int(row["working_model_score_0_100_not_probability"])
        decision = (
            "REVISE_CORE_AND_CONTEXT_SCOPE"
            if spec["decision"] == "REVISE"
            else "REVIEWED_RETAINED"
        )
        check("target_lexical", row["surface"] == spec["surface"], source_id)
        check(
            "target_lexical",
            row["v97_lexical_core_de"] == spec["v97_lexical_core_de"],
            source_id,
        )
        check(
            "target_lexical",
            row["v97_context_realizations_de"]
            == spec["v97_context_realization_de"],
            source_id,
        )
        check(
            "target_lexical", row["decomposition"] == spec["decomposition"], source_id
        )
        check(
            "target_lexical",
            row["v97_lineage_class"] == spec["lineage_class"],
            source_id,
        )
        check("target_lexical", row["working_model_level"] == level(score), source_id)
        check("target_lexical", row["working_model_level"] == "W1_WEAK_WORKING", source_id)
        check(
            "target_lexical",
            row["context_realization_score_0_100_not_probability"] == str(score),
            source_id,
        )
        check(
            "target_lexical",
            row["score_delta_lexical_core"] == "0",
            source_id,
        )
        check(
            "target_lexical",
            row["v97_component_global_export_allowed"] == "0",
            source_id,
        )
        check(
            "target_lexical",
            row["v97_exact_whole_surface_default_allowed"] == "1",
            source_id,
        )
        check("target_lexical", row["v97_audit_decision"] == decision, source_id)
        check(
            "target_lexical",
            row["v97_prior_lexical_core_de"] == spec["expected_old_core_de"],
            source_id,
        )
        check("target_lexical", "GDT724" in split_pipe(row["source_gdts"]), source_id)
        check(
            "target_lexical",
            row["historical_confirmation"] == HISTORICAL,
            source_id,
        )
        if spec["decision"] == "REVISE":
            check(
                "target_lexical",
                row["v97_lexical_core_de"] != spec["expected_old_core_de"],
                source_id,
            )
            check("target_lexical", row["last_semantic_writer"] == "GDT724", source_id)
        else:
            check(
                "target_lexical",
                row["v97_lexical_core_de"] == spec["expected_old_core_de"],
                source_id,
            )

    for source_id in ACTION_IDS:
        row = lexical_by_source[source_id]
        check(
            "action_separation",
            "abmessen" not in row["v97_lexical_core_de"].casefold(),
            source_id,
        )
        check(
            "action_separation",
            "abmessen" in row["v97_context_realizations_de"].casefold(),
            source_id,
        )

    check("lexical_parity", len(source_lexical) == len(lexical))
    for source, target in zip(source_lexical, lexical, strict=True):
        source_ids = split_pipe(source["source_reading_ids"])
        targeted = any(source_id in TARGET_IDS for source_id in source_ids)
        for field in (
            "surface",
            "source_reading_ids",
            "occurrence_count",
            "page_count",
            "locus_count",
            "working_model_score_0_100_not_probability",
            "working_model_level",
            "historical_confirmation",
        ):
            check(
                "lexical_parity",
                source[field] == target[field],
                (source["surface"], field),
            )
        if not targeted:
            check(
                "lexical_parity",
                source["v96_lexical_core_de"] == target["v97_lexical_core_de"],
                source["surface"],
            )
            check(
                "lexical_parity",
                source["v96_context_realizations_de"]
                == target["v97_context_realizations_de"],
                source["surface"],
            )
            check(
                "lexical_parity",
                source["family_ids"] == target["family_ids"],
                source["surface"],
            )
            check(
                "lexical_parity",
                source["decomposition"] == target["decomposition"],
                source["surface"],
            )
            check(
                "lexical_parity",
                target["v97_audit_decision"] == "NOT_IN_GDT724_TRANCHE",
                source["surface"],
            )

    context_by_position = {row["position_id"]: row for row in contexts}
    check("context_index", len(context_by_position) == 479)
    for source_id, spec in spec_by_id.items():
        row = context_by_position[spec["expected_position_id"]]
        for field, expected in (
            ("source_reading_id", source_id),
            ("surface", spec["surface"]),
            ("page", spec["expected_page"]),
            ("locus", spec["expected_locus"]),
            ("token_ordinal", spec["expected_token_ordinal"]),
            ("v97_lexical_core_de", spec["v97_lexical_core_de"]),
            ("v97_context_realization_de", spec["v97_context_realization_de"]),
            ("v97_expected_left_surface", spec["expected_left_surface"]),
            ("v97_expected_right_surface", spec["expected_right_surface"]),
            ("v68_action_license", spec["expected_action_license"]),
            ("v97_component_global_export_allowed", "0"),
            ("v97_exact_whole_surface_default_allowed", "1"),
            ("v97_lineage_class", spec["lineage_class"]),
        ):
            check("target_context", row[field] == expected, (source_id, field))

    check("context_parity", len(source_context) == len(contexts))
    for source, target in zip(source_context, contexts, strict=True):
        targeted = source["source_reading_id"] in TARGET_IDS
        for field in (
            "position_id",
            "page",
            "locus",
            "token_ordinal",
            "surface",
            "source_reading_id",
            "v68_action_license",
        ):
            check(
                "context_parity",
                source[field] == target[field],
                (source["position_id"], field),
            )
        if not targeted:
            check(
                "context_parity",
                source["v96_lexical_core_de"] == target["v97_lexical_core_de"],
                source["position_id"],
            )
            check(
                "context_parity",
                source["v96_context_realization_de"]
                == target["v97_context_realization_de"],
                source["position_id"],
            )
            check(
                "context_parity",
                source["v96_lexical_score"] == target["v97_lexical_score"],
                source["position_id"],
            )
            check(
                "context_parity",
                source["v96_context_score"] == target["v97_context_score"],
                source["position_id"],
            )
            check(
                "context_parity",
                target["v97_audit_decision"] == "NOT_IN_GDT724_TRANCHE",
                source["position_id"],
            )

    dispositions = Counter(row["disposition"] for row in census)
    check(
        "census",
        dispositions
        == Counter(
            {
                "REVISED_IN_V97": 16,
                "REVIEWED_RETAINED_IN_V97": 3,
                "HELD_FOR_LATER_REPAIR": 16,
            }
        ),
    )
    reviewed = {
        row["source_reading_id"]: row
        for row in census
        if row["disposition"] != "HELD_FOR_LATER_REPAIR"
    }
    check("census", set(reviewed) == TARGET_IDS)
    for source_id, row in reviewed.items():
        spec = spec_by_id[source_id]
        expected_disposition = (
            "REVISED_IN_V97"
            if spec["decision"] == "REVISE"
            else "REVIEWED_RETAINED_IN_V97"
        )
        check("census", row["disposition"] == expected_disposition, source_id)
        check(
            "census",
            row["v97_lexical_core_de"] == spec["v97_lexical_core_de"],
            source_id,
        )
        check(
            "census",
            row["v97_context_realization_de"]
            == spec["v97_context_realization_de"],
            source_id,
        )
        check("census", row["new_lexical_level"] == "W1_WEAK_WORKING", source_id)

    delta_by_id = {row["source_reading_id"]: row for row in delta}
    check("delta", set(delta_by_id) == TARGET_IDS)
    for source_id, row in delta_by_id.items():
        spec = spec_by_id[source_id]
        check("delta", row["decision"] == spec["decision"], source_id)
        check(
            "delta",
            row["old_lexical_core_de"] == spec["expected_old_core_de"],
            source_id,
        )
        check(
            "delta",
            row["v97_lexical_core_de"] == spec["v97_lexical_core_de"],
            source_id,
        )
        check(
            "delta",
            row["v97_context_realization_de"]
            == spec["v97_context_realization_de"],
            source_id,
        )
        check("delta", row["v97_score"] == row["old_score"], source_id)
        check("delta", row["score_credit_family_ids"] == "NONE", source_id)
        check("delta", row["component_global_export_allowed"] == "0", source_id)
        check(
            "delta", row["exact_whole_surface_default_allowed"] == "1", source_id
        )
        check("delta", row["historical_confirmation"] == HISTORICAL, source_id)

    lineage_by_id = {row["source_reading_id"]: row for row in lineage}
    check("lineage", set(lineage_by_id) == TARGET_IDS)
    check(
        "lineage",
        Counter(row["share_source_gdt"] for row in lineage)
        == Counter({"GDT694": 17, "GDT693": 2}),
    )
    for source_id, row in lineage_by_id.items():
        spec = spec_by_id[source_id]
        check("lineage", row["surface"] == spec["surface"], source_id)
        check("lineage", row["v97_decision"] == spec["decision"], source_id)
        check(
            "lineage",
            row["v97_selected_portable_core_de"] == spec["v97_lexical_core_de"],
            source_id,
        )
        check(
            "lineage",
            row["v97_selected_local_renderer_de"]
            == spec["v97_context_realization_de"],
            source_id,
        )
        check(
            "lineage", row["component_global_export_allowed"] == "0", source_id
        )
        check("lineage", row["score_credit"] == "0", source_id)
        check("lineage", row["historical_confirmation"] == HISTORICAL, source_id)

    binding_ids: set[str] = set()
    source_cache: dict[Path, list[dict[str, str]]] = {}
    for row in evidence:
        binding_id = row["binding_id"]
        check("bindings", binding_id not in binding_ids, binding_id)
        binding_ids.add(binding_id)
        check("bindings", "f84" not in row["evidence_path"].casefold(), binding_id)
        check("bindings", row["source_row_match"] == "1", binding_id)
        check("bindings", row["score_credit_family_ids"] == "NONE", binding_id)
        check("bindings", row["historical_confirmation"] == HISTORICAL, binding_id)
        source_path = ROOT / row["evidence_path"]
        check("bindings", source_path.is_file(), binding_id)
        if source_path not in source_cache:
            source_cache[source_path] = read_tsv(source_path)
        selector = parse_selector(row["selector"])
        matches = [
            candidate
            for candidate in source_cache[source_path]
            if all(candidate.get(field) == expected for field, expected in selector.items())
        ]
        check("bindings", len(matches) == 1, (binding_id, len(matches)))
        source = matches[0]
        check(
            "fingerprints",
            row["matched_row_fingerprint_sha256"] == fingerprint(source),
            binding_id,
        )
        check(
            "sealed",
            all(
                not value.casefold().startswith("f84")
                for field, value in source.items()
                if field in {"page", "locus"}
            ),
            binding_id,
        )
    check("bindings", len(binding_ids) == 82)
    check(
        "bindings",
        Counter(row["evidence_role"] for row in evidence)
        == Counter(
            {
                "V96_ACTIVE_LEXICAL": 19,
                "V96_EXACT_CONTEXT": 19,
                "V96_HELD_AUDIT": 19,
                "GDT694_EXACT_MIGRATION": 17,
                "GDT693_EXACT_REVISION": 2,
                "GDT693_R_SELECTOR_MODEL": 1,
                "GDT693_PORTION_CONTROL_MODEL": 1,
                "GDT716_CORE_CONTEXT_REPAIR_TEMPLATE": 1,
                "GDT692_SUPERSEDED_FRACTION_COUNTERMODEL_I": 1,
                "GDT692_SUPERSEDED_FRACTION_COUNTERMODEL_II": 1,
                "GDT692_SUPERSEDED_FRACTION_COUNTERMODEL_III": 1,
            }
        ),
    )

    rival_by_target: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rivals:
        rival_by_target[row["source_reading_id"]].append(row)
        check("rivals", row["score_credit"] == "0", row["source_reading_id"])
        check(
            "rivals",
            row["component_global_export_allowed"] == "0",
            row["source_reading_id"],
        )
    check("rivals", set(rival_by_target) == TARGET_IDS)
    for source_id, rows in rival_by_target.items():
        check("rivals", len(rows) == 3, source_id)
        selected = [row for row in rows if row["portable_default_selected"] == "1"]
        check(
            "rivals",
            len(selected) == 1
            and selected[0]["model_id"]
            == "A_BOUND_CORE_PLUS_EXACT_LOCAL_RENDERER",
            source_id,
        )

    expected_scope = {
        "BOUND_INDEXED_SHARE_SELECTOR",
        "PORTION_DISTINCT_FROM_SHARE",
        "LEARNED_OR_BOUND_WHOLES",
        "ACTIVE_MATERIAL_IDENTITIES",
        "LOCAL_PRODUCT_AND_PATIENT_HEADS",
        "LOCAL_ACTIONS",
        "B003_RENDER_ONCE",
    }
    check("scope", {row["scope_item"] for row in scope} == expected_scope)
    for row in scope:
        check("scope", row["score_credit"] == "0", row["scope_item"])
        check(
            "scope",
            row["component_or_substring_global_export_allowed"] == "0",
            row["scope_item"],
        )
        check(
            "scope",
            row["historical_confirmation"] == HISTORICAL,
            row["scope_item"],
        )

    renderer_by_surface = {row["surface"]: row for row in renderer}
    check(
        "renderer",
        set(renderer_by_surface) == {row["surface"] for row in specs},
    )
    for spec in specs:
        row = renderer_by_surface[spec["surface"]]
        check(
            "renderer",
            row["position_id"] == spec["expected_position_id"],
            spec["surface"],
        )
        check("renderer", row["decision"] == spec["decision"], spec["surface"])
        check(
            "renderer",
            row["portable_lexical_core_de"] == spec["v97_lexical_core_de"],
            spec["surface"],
        )
        check(
            "renderer",
            row["local_context_realization_de"]
            == spec["v97_context_realization_de"],
            spec["surface"],
        )
        check(
            "renderer",
            row["component_global_export_allowed"] == "0",
            spec["surface"],
        )
        check("renderer", row["level"] == "W1_WEAK_WORKING", spec["surface"])

    separation_by_id = {row["source_reading_id"]: row for row in separation}
    check("separation", set(separation_by_id) == TARGET_IDS)
    check(
        "separation",
        sum(row["position_is_action_licensed"] == "1" for row in separation) == 2,
    )
    for source_id, row in separation_by_id.items():
        for field in (
            "portable_action_export_allowed",
            "portable_product_head_export_allowed",
            "component_global_export_allowed",
        ):
            check("separation", row[field] == "0", (source_id, field))
        for local_word in split_pipe(row["local_only_words_or_heads"]):
            check(
                "separation",
                local_word.casefold()
                in row["local_context_realization_de"].casefold(),
                (source_id, local_word),
            )
            check(
                "separation",
                local_word.casefold()
                not in row["portable_lexical_core_de"].casefold(),
                (source_id, local_word),
            )
        expected = (
            "PASS_LOCAL_ACTION_SEPARATED"
            if source_id in ACTION_IDS
            else "PASS_NOMINAL_NO_HIDDEN_ACTION"
        )
        check("separation", row["audit_status"] == expected, source_id)

    levels = Counter(row["working_model_level"] for row in lexical)
    check(
        "dictionary",
        levels
        == Counter(
            {
                "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
                "W1_WEAK_WORKING": 135,
                "W2_PROVISIONAL_WORKING": 163,
                "W3_SOLID_WORKING_THEORY": 19,
            }
        ),
    )
    active_complete = [
        row for row in complete if row["current_layer"] == "ACTIVE_V97_LEXICAL_CORE"
    ]
    check("dictionary", len(active_complete) == 324)
    complete_by_reading = {row["reading_id"]: row for row in active_complete}
    check("dictionary", len(complete_by_reading) == 324)
    for row in complete:
        check("complete", bool(row["working_meaning_de"]), row["reading_id"])
        score = int(row["working_model_score_0_100_not_probability"])
        check("complete", row["working_model_level"] == level(score), row["reading_id"])
        check("complete", bool(row["positive_evidence_de"]), row["reading_id"])
        check("complete", bool(row["counterevidence_de"]), row["reading_id"])
        check(
            "complete",
            row["historical_confirmation"] == HISTORICAL,
            row["reading_id"],
        )
    for source_id, lexical_row in lexical_by_source.items():
        reading_id = lexical_row["v97_reading_id"]
        if reading_id not in complete_by_reading:
            continue
        row = complete_by_reading[reading_id]
        check(
            "dictionary",
            row["working_meaning_de"] == lexical_row["v97_lexical_core_de"],
            source_id,
        )
        check(
            "dictionary",
            row["working_model_score_0_100_not_probability"]
            == lexical_row["working_model_score_0_100_not_probability"],
            source_id,
        )
        check(
            "dictionary",
            row["positive_evidence_de"] == lexical_row["positive_evidence_de"],
            source_id,
        )
        check(
            "dictionary",
            row["counterevidence_de"] == lexical_row["counterevidence_de"],
            source_id,
        )

    source_spans = {
        row["bound_span_id"]: row
        for row in read_tsv(G723 / "V96_5_BOUND_SPAN_RENDERER.tsv")
    }
    target_spans = {row["bound_span_id"]: row for row in spans}
    check("spans", set(source_spans) == set(target_spans))
    for span_id in source_spans:
        source = source_spans[span_id]
        target = target_spans[span_id]
        if span_id == "B003":
            check(
                "spans",
                target["render_once_de"]
                == "vollständig getrocknete Charge aus erhitztem Holzanteil I",
                span_id,
            )
            check("spans", "Droge" not in target["render_once_de"], span_id)
            check("spans", "GDT724" in split_pipe(target["source_gdts"]), span_id)
        else:
            check("spans", source == target, span_id)
    execution_by_id = {row["bound_span_id"]: row for row in execution}
    check("spans", set(execution_by_id) == set(target_spans))
    for span_id, row in execution_by_id.items():
        check(
            "spans",
            row["render_once_de"] == target_spans[span_id]["render_once_de"],
            span_id,
        )
        check("spans", row["execution_status"] == "EXECUTABLE_RENDER_ONCE", span_id)
    check(
        "preserved",
        file_sha(G723 / "V96_2_ONE_SHOT_RENDER_DIRECTIVES.tsv")
        == file_sha(ART / "V97_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"),
    )
    check(
        "preserved",
        file_sha(G723 / "V96_8_F7R2_RENDERED_UNITS.tsv")
        == file_sha(ART / "V97_8_F7R2_RENDERED_UNITS.tsv"),
    )

    check("result", result["experiment_id"] == "GDT724")
    check("result", result["status"] == EXPECTED_STATUS)
    check("result", result["target_readings_audited"] == 19)
    check("result", result["target_positions"] == 19)
    check("result", result["target_pages"] == 10)
    check("result", result["revised_core_context_readings"] == 16)
    check("result", result["reviewed_retained_exact_wholes"] == 3)
    check("result", result["primary_and_countermodel_evidence_bindings"] == 82)
    check(
        "result",
        result["action_positions_with_lexical_action_separation"] == 2,
    )
    check("result", result["nominal_positions_without_hidden_action"] == 17)
    check("result", result["component_global_exports"] == 0)
    check("result", result["score_delta_total"] == 0)
    check("result", result["remaining_unreviewed_weak_readings"] == 16)
    check(
        "result",
        result["complete_dictionary_rows_with_default_confidence_and_evidence"]
        == 1586,
    )
    check("result", result["b003_span_rerendered"] == 1)
    check("result", result["f84_or_f84r_used"] == 0)

    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    check("report", EXPECTED_STATUS in report)
    check("report", "Grundansatz aus Anteil II" in report)
    check("report", "vollständig erhitzter Anteil I" in report)
    check("report", "Holzanteil I abmessen" in report)
    check("report", "16" in report and "3" in report)
    check("report", "f84" in report and "f84r" in report)

    check(
        "sealed",
        all(not row["expected_page"].casefold().startswith("f84") for row in specs),
    )
    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    check(
        "sealed",
        manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
    )
    check("sealed", manifest["experiment_id"] == "GDT724")

    validation = {
        "experiment_id": "GDT724",
        "status": "PASS",
        "checks_passed": sum(checks.values()),
        "check_groups": dict(sorted(checks.items())),
        "target_readings_audited": 19,
        "revised_core_context_readings": 16,
        "reviewed_retained_exact_wholes": 3,
        "evidence_bindings_replayed": 82,
        "action_positions_with_lexical_action_separation": 2,
        "nominal_positions_without_hidden_action": 17,
        "exact_whole_surface_defaults_allowed": 19,
        "component_global_exports": 0,
        "score_delta_total": 0,
        "remaining_unreviewed_weak_readings": 16,
        "complete_dictionary_rows_with_default_confidence_and_evidence": 1586,
        "b003_span_rerendered": 1,
        "f84_or_f84r_used": 0,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
