#!/usr/bin/env python3
"""Independent validator for GDT725/V98."""

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
EXP = ROOT / "experiments/yolo/gdt725_v98_final_low_hardcap_dictionary_dispatch"
SRC = EXP / "src"
ART = EXP / "artifacts"
G724 = ROOT / "experiments/yolo/gdt724_v97_remaining_indexed_share_core_context_repair/artifacts"
HISTORICAL = "H0_NONE"
EXPECTED_STATUS = (
    "PASS_V98_16_FINAL_LOW_HARDCAP_READINGS_AUDITED__21_POSITIONS__"
    "9_CORE_OR_STRUCTURAL_REPAIRS_PLUS_7_RETAINED__"
    "5_STRUCTURAL_READINGS_SEPARATED__4_ACTION_WHOLES_RETAINED__"
    "72_EVIDENCE_BINDINGS__0_UNAUDITED_HARDCAP__"
    "NO_COMPONENT_EXPORT_NO_SCORE_CREDIT__ALL_H0_NONE"
)
ACTION_IDS = {"aiijy#1", "da#1", "qy#1", "ypchesy#1"}
STRUCTURAL_IDS = {"dy#1", "dy#2", "y#1", "y#2", "yey#1"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def split_pipe(value: str) -> list[str]:
    return [
        item.strip()
        for item in value.split("|")
        if item.strip() and item.strip() not in {"NONE", "0"}
    ]


def parse_selector(value: str) -> dict[str, str]:
    output: dict[str, str] = {}
    for part in value.split(";"):
        field, expected = part.split("=", 1)
        assert field and field not in output
        output[field] = expected
    return output


def fingerprint(row: dict[str, str]) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def render_values(values: list[str]) -> str:
    """Independent prose join used to replay, not trust, the built line artifact."""

    rendered = ""
    for value in values:
        if value in {".", ";"}:
            rendered = rendered.rstrip(" ·") + value
            continue
        if rendered:
            rendered += " " if rendered.endswith((".", ";", ":")) else " · "
        rendered += value
    return rendered


def replay_line(
    rows: list[dict[str, str]],
    value_field: str,
    spans: list[dict[str, str]],
    overrides: dict[str, str],
) -> tuple[str, list[str], list[str]]:
    """Reconstruct one locus from ordered contexts and independently consume spans."""

    assert rows
    locus = rows[0]["locus"]
    ordered = sorted(rows, key=lambda row: int(row["token_ordinal"]))
    assert all(row["locus"] == locus for row in ordered)
    by_position = {row["position_id"]: row for row in ordered}
    assert len(by_position) == len(ordered)
    realized = {row["position_id"]: row[value_field] for row in ordered}
    omitted: set[str] = set()
    span_ids: list[str] = []
    for span in spans:
        if span["locus"] != locus:
            continue
        left_id, right_id = span["left_position_id"], span["right_position_id"]
        assert left_id in by_position and right_id in by_position
        assert by_position[left_id]["surface"] == span["left_surface"]
        assert by_position[right_id]["surface"] == span["right_surface"]
        assert left_id not in omitted and right_id not in omitted
        realized[left_id] = span["render_once_de"]
        omitted.add(right_id)
        span_ids.append(span["bound_span_id"])
    override_ids: list[str] = []
    for position_id, value in overrides.items():
        if position_id in by_position:
            assert position_id not in omitted
            realized[position_id] = value
            override_ids.append(position_id)
    return (
        render_values(
            [
                realized[row["position_id"]]
                for row in ordered
                if row["position_id"] not in omitted
            ]
        ),
        span_ids,
        override_ids,
    )


def main() -> int:
    checks: Counter[str] = Counter()

    def check(group: str, condition: bool, detail: Any = "") -> None:
        assert condition, (group, detail)
        checks[group] += 1

    reading_specs = read_tsv(SRC / "V98_16_READING_SPECS.tsv")
    position_specs = read_tsv(SRC / "V98_21_POSITION_SPECS.tsv")
    companion_specs = read_tsv(SRC / "V98_1_COMPANION_LINE_RENDER_SPEC.tsv")
    lexical = read_tsv(ART / "V98_324_ACTIVE_LEXICAL_READINGS.tsv")
    contexts = read_tsv(ART / "V98_479_CONTEXT_REALIZATIONS.tsv")
    census = read_tsv(ART / "V98_35_READING_AUDIT.tsv")
    decisions = read_tsv(ART / "V98_16_FINAL_HARDCAP_DECISIONS.tsv")
    lineage = read_tsv(ART / "V98_16_LINEAGE_AUDIT.tsv")
    evidence = read_tsv(ART / "V98_72_EVIDENCE_BINDINGS.tsv")
    rivals = read_tsv(ART / "V98_48_RIVAL_MODEL_COMPARISON.tsv")
    renderer = read_tsv(ART / "V98_21_POSITION_RENDERER.tsv")
    dispatch = read_tsv(ART / "V98_16_ACTION_STRUCTURAL_DISPATCH_AUDIT.tsv")
    scope = read_tsv(ART / "V98_7_SCOPE_DICTIONARY.tsv")
    lines = read_tsv(ART / "V98_18_REPAIRED_LINES.tsv")
    companion_audit = read_tsv(ART / "V98_1_COMPANION_LINE_RENDER_AUDIT.tsv")
    complete = read_tsv(ART / "V98_COMPLETE_WORD_CONFIDENCE.tsv")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    source_lexical = read_tsv(G724 / "V97_324_ACTIVE_LEXICAL_READINGS.tsv")
    source_contexts = read_tsv(G724 / "V97_479_CONTEXT_REALIZATIONS.tsv")
    source_spans = read_tsv(G724 / "V97_5_BOUND_SPAN_RENDERER.tsv")

    check("counts", len(reading_specs) == 16)
    check("counts", len(position_specs) == 21)
    check("counts", len(companion_specs) == 1)
    check("counts", len(lexical) == 324)
    check("counts", len(contexts) == 479)
    check("counts", len(census) == 35)
    check("counts", len(decisions) == 16)
    check("counts", len(lineage) == 16)
    check("counts", len(evidence) == 72)
    check("counts", len(rivals) == 48)
    check("counts", len(renderer) == 21)
    check("counts", len(dispatch) == 16)
    check("counts", len(scope) == 7)
    check("counts", len(lines) == 18)
    check("counts", len(companion_audit) == 1)
    check("counts", len(complete) == 1586)
    check("counts", len({row["surface"] for row in complete}) == 1582)

    spec_by_id = {row["source_reading_id"]: row for row in reading_specs}
    target_ids = set(spec_by_id)
    check("targets", len(target_ids) == 16)
    check(
        "targets",
        Counter(row["decision"] for row in reading_specs)
        == Counter({"REVISE": 9, "RETAIN": 7}),
    )
    check(
        "targets",
        {row["source_reading_id"] for row in reading_specs if row["value_kind"] == "ACTION_WHOLE"}
        == ACTION_IDS,
    )
    check(
        "targets",
        {
            row["source_reading_id"]
            for row in reading_specs
            if row["value_kind"].startswith("STRUCTURAL")
        }
        == STRUCTURAL_IDS,
    )
    check("targets", all(row["component_global_export_allowed"] == "0" for row in reading_specs))
    check("targets", all(row["historical_confirmation"] if "historical_confirmation" in row else True for row in reading_specs))

    lexical_by_source: dict[str, dict[str, str]] = {}
    for row in lexical:
        for source_id in split_pipe(row["source_reading_ids"]):
            check("lexical_index", source_id not in lexical_by_source, source_id)
            lexical_by_source[source_id] = row
    check("lexical_index", len(lexical_by_source) == 332)

    source_lexical_by_reading = {row["v97_reading_id"]: row for row in source_lexical}
    for source_id, spec in spec_by_id.items():
        row = lexical_by_source[source_id]
        source = source_lexical_by_reading[source_id]
        score = int(row["working_model_score_0_100_not_probability"])
        check("target_lexical", row["surface"] == spec["surface"], source_id)
        check("target_lexical", row["v98_lexical_core_de"] == spec["v98_dictionary_default_de"], source_id)
        check("target_lexical", row["v98_context_realizations_de"] == spec["v98_context_summary_de"], source_id)
        check("target_lexical", row["v98_prior_lexical_core_de"] == spec["expected_old_core_de"], source_id)
        check("target_lexical", source["v97_lexical_core_de"] == spec["expected_old_core_de"], source_id)
        check("target_lexical", row["working_model_level"] == level(score), source_id)
        check("target_lexical", row["score_delta_lexical_core"] == "0", source_id)
        check("target_lexical", row["v98_value_kind"] == spec["value_kind"], source_id)
        check("target_lexical", row["v98_structural_tag"] == spec["structural_tag"], source_id)
        check("target_lexical", row["v98_action_default_allowed"] == spec["action_default_allowed"], source_id)
        check("target_lexical", row["v98_component_global_export_allowed"] == "0", source_id)
        check("target_lexical", row["historical_confirmation"] == HISTORICAL, source_id)
        check("target_lexical", "GDT725" in split_pipe(row["source_gdts"]), source_id)
        if spec["decision"] == "REVISE":
            check("target_lexical", row["v98_lexical_core_de"] != source["v97_lexical_core_de"], source_id)
            check("target_lexical", row["last_semantic_writer"] == "GDT725", source_id)
        else:
            check("target_lexical", row["v98_lexical_core_de"] == source["v97_lexical_core_de"], source_id)

    check("lexical_parity", len(source_lexical) == len(lexical))
    for source, target in zip(source_lexical, lexical, strict=True):
        targeted = source["v97_reading_id"] in target_ids
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
            check("lexical_parity", source[field] == target[field], (source["surface"], field))
        if not targeted:
            check("lexical_parity", source["v97_lexical_core_de"] == target["v98_lexical_core_de"], source["surface"])
            check("lexical_parity", source["v97_context_realizations_de"] == target["v98_context_realizations_de"], source["surface"])

    position_by_id = {row["position_id"]: row for row in position_specs}
    context_by_position = {row["position_id"]: row for row in contexts}
    source_context_by_position = {row["position_id"]: row for row in source_contexts}
    check("context_index", len(context_by_position) == 479)
    for position_id, spec in position_by_id.items():
        row = context_by_position[position_id]
        source = source_context_by_position[position_id]
        reading_spec = spec_by_id[spec["source_reading_id"]]
        for field, expected in (
            ("source_reading_id", spec["source_reading_id"]),
            ("page", spec["expected_page"]),
            ("locus", spec["expected_locus"]),
            ("token_ordinal", spec["expected_token_ordinal"]),
            ("surface", spec["expected_surface"]),
            ("v98_lexical_core_de", reading_spec["v98_dictionary_default_de"]),
            ("v98_context_realization_de", spec["v98_context_realization_de"]),
            ("v98_expected_left_surface", spec["expected_left_surface"]),
            ("v98_expected_right_surface", spec["expected_right_surface"]),
            ("v68_clause_type", spec["expected_clause_type"]),
            ("v68_action_license", spec["expected_action_license"]),
            ("v98_component_global_export_allowed", "0"),
            ("v98_value_kind", reading_spec["value_kind"]),
            ("v98_structural_tag", reading_spec["structural_tag"]),
        ):
            check("target_context", row[field] == expected, (position_id, field))
        check("target_context", source["v97_context_realization_de"] == spec["expected_old_context_de"], position_id)

    check("context_parity", len(source_contexts) == len(contexts))
    for source, target in zip(source_contexts, contexts, strict=True):
        targeted = source["position_id"] in position_by_id
        for field in (
            "position_id",
            "page",
            "locus",
            "token_ordinal",
            "surface",
            "source_reading_id",
            "v68_action_license",
        ):
            check("context_parity", source[field] == target[field], (source["position_id"], field))
        if not targeted:
            check("context_parity", source["v97_lexical_core_de"] == target["v98_lexical_core_de"], source["position_id"])
            check("context_parity", source["v97_context_realization_de"] == target["v98_context_realization_de"], source["position_id"])

    companion_spec_by_position = {
        row["position_id"]: row for row in companion_specs
    }
    companion_audit_by_position = {
        row["position_id"]: row for row in companion_audit
    }
    check(
        "companion",
        set(companion_spec_by_position) == set(companion_audit_by_position) == {"P265"},
    )
    for position_id, spec in companion_spec_by_position.items():
        audit = companion_audit_by_position[position_id]
        source_context = source_context_by_position[position_id]
        target_context = context_by_position[position_id]
        for field, expected in (
            ("source_reading_id", spec["source_reading_id"]),
            ("page", spec["expected_page"]),
            ("locus", spec["expected_locus"]),
            ("token_ordinal", spec["expected_token_ordinal"]),
            ("surface", spec["expected_surface"]),
            ("source_gdt", spec["source_gdt"]),
            ("source_artifact", spec["source_artifact"]),
            ("source_selector", spec["source_selector"]),
            ("line_render_once_de", spec["line_render_once_de"]),
            ("repair_scope", "LINE_RENDERER_ONLY"),
            ("score_delta", "0"),
            ("component_global_export_allowed", "0"),
            ("score_credit", "0"),
            ("historical_confirmation", HISTORICAL),
        ):
            check("companion", audit[field] == expected, (position_id, field))
        check(
            "companion",
            source_context["v97_context_realization_de"]
            == target_context["v98_context_realization_de"]
            == spec["expected_context_realization_de"],
            position_id,
        )
        check(
            "companion",
            audit["v98_dictionary_core_unchanged_de"]
            == source_context["v97_lexical_core_de"]
            == target_context["v98_lexical_core_de"],
            position_id,
        )
        check(
            "companion",
            audit["v97_lexical_score"]
            == audit["v98_lexical_score_unchanged"]
            == source_context["v97_lexical_score"]
            == target_context["v98_lexical_score"],
            position_id,
        )
        path = ROOT / spec["source_artifact"]
        check("companion", path.is_file(), position_id)
        selector = parse_selector(spec["source_selector"])
        matches = [
            candidate
            for candidate in read_tsv(path)
            if all(candidate.get(field) == expected for field, expected in selector.items())
        ]
        check("companion", len(matches) == 1, (position_id, len(matches)))
        check(
            "companion",
            audit["matched_source_row_fingerprint_sha256"]
            == fingerprint(matches[0]),
            position_id,
        )
        check(
            "companion",
            audit["matched_source_literal_de"] == matches[0]["new_literal_gloss_de"],
            position_id,
        )
        check(
            "companion",
            spec["line_render_once_de"].replace("vorstehenden ", "")
            == matches[0]["new_literal_gloss_de"],
            position_id,
        )

    check("census", all(row["disposition"] != "HELD_FOR_LATER_REPAIR" for row in census))
    check(
        "census",
        Counter(row["disposition"] for row in census)
        == Counter(
            {
                "REVISED_IN_V97": 16,
                "REVIEWED_RETAINED_IN_V97": 3,
                "REVISED_IN_V98": 9,
                "REVIEWED_RETAINED_IN_V98": 7,
            }
        ),
    )

    decision_by_id = {row["source_reading_id"]: row for row in decisions}
    lineage_by_id = {row["source_reading_id"]: row for row in lineage}
    dispatch_by_id = {row["source_reading_id"]: row for row in dispatch}
    check("decision_index", set(decision_by_id) == set(lineage_by_id) == set(dispatch_by_id) == target_ids)
    for source_id, spec in spec_by_id.items():
        decision = decision_by_id[source_id]
        lineage_row = lineage_by_id[source_id]
        dispatch_row = dispatch_by_id[source_id]
        check("decisions", decision["decision"] == spec["decision"], source_id)
        check("decisions", decision["v98_dictionary_default_de"] == spec["v98_dictionary_default_de"], source_id)
        check("decisions", decision["score_delta"] == "0", source_id)
        check("decisions", decision["component_global_export_allowed"] == "0", source_id)
        check("lineage", lineage_row["origin_gdt"] == spec["origin_gdt"], source_id)
        check("lineage", lineage_row["origin_composition"] == spec["origin_composition"], source_id)
        check("lineage", lineage_row["component_global_export_allowed"] == "0", source_id)
        check("dispatch", dispatch_row["value_kind"] == spec["value_kind"], source_id)
        check("dispatch", dispatch_row["component_global_export_allowed"] == "0", source_id)
        expected_status = (
            "PASS_EXACT_ACTION_WHOLE"
            if source_id in ACTION_IDS
            else (
                "PASS_STRUCTURAL_TAG_SEPARATED_FROM_RENDERER"
                if source_id in STRUCTURAL_IDS
                else "PASS_NOMINAL_WITHOUT_HIDDEN_IMPERATIVE"
            )
        )
        check("dispatch", dispatch_row["audit_status"] == expected_status, source_id)

    binding_ids: set[str] = set()
    cache: dict[Path, list[dict[str, str]]] = {}
    for row in evidence:
        check("bindings", row["binding_id"] not in binding_ids, row["binding_id"])
        binding_ids.add(row["binding_id"])
        check("bindings", row["source_reading_id"] in target_ids, row["binding_id"])
        check("bindings", "f84" not in row["evidence_path"].casefold(), row["binding_id"])
        check("bindings", row["source_row_match"] == "1", row["binding_id"])
        check("bindings", row["score_credit_family_ids"] == "NONE", row["binding_id"])
        check("bindings", row["historical_confirmation"] == HISTORICAL, row["binding_id"])
        path = ROOT / row["evidence_path"]
        check("bindings", path.is_file(), row["binding_id"])
        if path not in cache:
            cache[path] = read_tsv(path)
        selector = parse_selector(row["selector"])
        matches = [
            candidate
            for candidate in cache[path]
            if all(candidate.get(field) == expected for field, expected in selector.items())
        ]
        check("bindings", len(matches) == 1, (row["binding_id"], len(matches)))
        check("fingerprints", row["matched_row_fingerprint_sha256"] == fingerprint(matches[0]), row["binding_id"])
        check(
            "sealed",
            all(
                not matches[0].get(field, "").casefold().startswith("f84")
                for field in ("page", "locus")
            ),
            row["binding_id"],
        )
    check("bindings", len(binding_ids) == 72)
    check(
        "bindings",
        Counter(row["evidence_role"] for row in evidence)
        == Counter(
            {
                "V97_ACTIVE_LEXICAL": 16,
                "V97_HELD_AUDIT": 16,
                "V97_EXACT_CONTEXT": 21,
                "GDT675_ORIGIN_ROW": 1,
                "GDT677_ORIGIN_ROW": 1,
                "GDT678_ORIGIN_ROW": 2,
                "GDT680_ORIGIN_ROW": 3,
                "GDT681_ORIGIN_ROW": 5,
                "GDT687_ORIGIN_ROW": 7,
            }
        ),
    )

    rivals_by_id: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rivals:
        rivals_by_id[row["source_reading_id"]].append(row)
        check("rivals", row["component_global_export_allowed"] == "0", row["source_reading_id"])
        check("rivals", row["score_credit"] == "0", row["source_reading_id"])
    check("rivals", set(rivals_by_id) == target_ids)
    for source_id, rows in rivals_by_id.items():
        check("rivals", len(rows) == 3, source_id)
        selected = [row for row in rows if row["selected"] == "1"]
        check("rivals", len(selected) == 1 and selected[0]["model_id"].startswith("A_SELECTED"), source_id)

    renderer_by_position = {row["position_id"]: row for row in renderer}
    check("renderer", set(renderer_by_position) == set(position_by_id))
    for position_id, row in renderer_by_position.items():
        spec = position_by_id[position_id]
        check("renderer", row["source_reading_id"] == spec["source_reading_id"], position_id)
        check("renderer", row["local_context_realization_de"] == spec["v98_context_realization_de"], position_id)
        check("renderer", row["component_global_export_allowed"] == "0", position_id)

    check("lines", {row["locus"] for row in lines} == {row["expected_locus"] for row in position_specs})
    lines_by_locus = {row["locus"]: row for row in lines}
    for row in lines:
        check("lines", "; ·" not in row["v98_reader_de"], row["locus"])
        check("lines", ": ·" not in row["v98_reader_de"], row["locus"])
        check(
            "lines",
            int(row["renderer_change_count"])
            == int(row["v97_reader_de"] != row["v98_reader_de"]),
            row["locus"],
        )
        check("lines", row["historical_confirmation"] == HISTORICAL, row["locus"])

    target_loci = set(lines_by_locus)
    source_rows_by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    target_rows_by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    target_specs_by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_contexts:
        if row["locus"] in target_loci:
            source_rows_by_locus[row["locus"]].append(row)
    for row in contexts:
        if row["locus"] in target_loci:
            target_rows_by_locus[row["locus"]].append(row)
    for row in position_specs:
        target_specs_by_locus[row["expected_locus"]].append(row)
    companion_overrides = {
        row["position_id"]: row["line_render_once_de"] for row in companion_specs
    }
    for locus, built in lines_by_locus.items():
        source_rows = sorted(
            source_rows_by_locus[locus], key=lambda row: int(row["token_ordinal"])
        )
        target_rows = sorted(
            target_rows_by_locus[locus], key=lambda row: int(row["token_ordinal"])
        )
        target_specs = sorted(
            target_specs_by_locus[locus],
            key=lambda row: int(row["expected_token_ordinal"]),
        )
        check(
            "line_replay",
            [row["position_id"] for row in source_rows]
            == [row["position_id"] for row in target_rows],
            locus,
        )
        expected_old, expected_span_ids, old_override_ids = replay_line(
            source_rows, "v97_context_realization_de", source_spans, {}
        )
        expected_new, new_span_ids, new_override_ids = replay_line(
            target_rows,
            "v98_context_realization_de",
            source_spans,
            companion_overrides,
        )
        check("line_replay", not old_override_ids, locus)
        check("line_replay", expected_span_ids == new_span_ids, locus)
        for field, expected in (
            ("page", source_rows[0]["page"]),
            ("locus", locus),
            (
                "target_position_ids",
                "|".join(row["position_id"] for row in target_specs),
            ),
            (
                "target_reading_ids",
                "|".join(row["source_reading_id"] for row in target_specs),
            ),
            (
                "target_surfaces",
                "|".join(row["expected_surface"] for row in target_specs),
            ),
            ("surface_sequence", " ".join(row["surface"] for row in source_rows)),
            ("v97_reader_de", expected_old),
            ("v98_reader_de", expected_new),
            (
                "changed_target_positions",
                str(
                    sum(
                        source["v97_context_realization_de"]
                        != target["v98_context_realization_de"]
                        for source, target in zip(source_rows, target_rows, strict=True)
                    )
                ),
            ),
            (
                "executed_bound_span_ids",
                "|".join(expected_span_ids) if expected_span_ids else "NONE",
            ),
            (
                "companion_line_render_position_ids",
                "|".join(new_override_ids) if new_override_ids else "NONE",
            ),
            ("renderer_change_count", str(int(expected_old != expected_new))),
        ):
            check("line_replay", built[field] == expected, (locus, field))
        for span in source_spans:
            if span["locus"] != locus:
                continue
            check(
                "line_replay",
                expected_old.count(span["render_once_de"]) == 1
                and expected_new.count(span["render_once_de"]) == 1,
                span["bound_span_id"],
            )
            left_value = source_context_by_position[span["left_position_id"]][
                "v97_context_realization_de"
            ]
            right_value = source_context_by_position[span["right_position_id"]][
                "v97_context_realization_de"
            ]
            standalone_pair = render_values([left_value, right_value])
            check(
                "line_replay",
                standalone_pair not in expected_old and standalone_pair not in expected_new,
                span["bound_span_id"],
            )
        for position_id in new_override_ids:
            phrase = companion_overrides[position_id]
            check("line_replay", expected_new.count(phrase) == 1, position_id)
            check("line_replay", phrase not in expected_old, position_id)

    executed_span_ids = [
        span_id
        for row in lines
        for span_id in split_pipe(row["executed_bound_span_ids"])
    ]
    companion_position_ids = [
        position_id
        for row in lines
        for position_id in split_pipe(row["companion_line_render_position_ids"])
    ]
    check("lines", Counter(executed_span_ids) == Counter({"B001": 1, "B002": 1}))
    check("lines", Counter(companion_position_ids) == Counter({"P265": 1}))
    span_by_id = {row["bound_span_id"]: row for row in source_spans}
    check("lines", set(span_by_id) >= {"B001", "B002"})
    for span_id in ("B001", "B002"):
        locus = span_by_id[span_id]["locus"]
        expected = span_by_id[span_id]["render_once_de"]
        check("lines", expected in lines_by_locus[locus]["v97_reader_de"], span_id)
        check("lines", expected in lines_by_locus[locus]["v98_reader_de"], span_id)

    check(
        "lines",
        "drei Portionen des Anteils I des heißen Holzansatzes"
        in lines_by_locus["f86v3.13"]["v98_reader_de"],
    )
    check(
        "lines",
        "drei · heißer Holzanteil I"
        not in lines_by_locus["f86v3.13"]["v98_reader_de"],
    )
    check(
        "lines",
        "Anteil I des heißen Holzansatzes; drei Portionen davon"
        in lines_by_locus["f86v6.5"]["v98_reader_de"],
    )
    check(
        "lines",
        "heißer Holzanteil I · drei"
        not in lines_by_locus["f86v6.5"]["v98_reader_de"],
    )
    check(
        "lines",
        "drei Portionen des vorstehenden eingeweichten Arzneikompositums."
        in lines_by_locus["f76v.10"]["v98_reader_de"],
    )
    check("lines", " · drei." not in lines_by_locus["f76v.10"]["v98_reader_de"])
    check(
        "lines",
        "anschließend: trocken am Ende des Grades"
        in lines_by_locus["f105r.2"]["v98_reader_de"],
    )
    check(
        "lines",
        "Anschließend: mittlere Trockenstufe erreicht"
        in lines_by_locus["f86v3.13"]["v98_reader_de"],
    )

    check(
        "dictionary",
        Counter(row["working_model_level"] for row in lexical)
        == Counter(
            {
                "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7,
                "W1_WEAK_WORKING": 135,
                "W2_PROVISIONAL_WORKING": 163,
                "W3_SOLID_WORKING_THEORY": 19,
            }
        ),
    )
    active_complete = [row for row in complete if row["current_layer"] == "ACTIVE_V98_LEXICAL_CORE"]
    check("dictionary", len(active_complete) == 324)
    for row in complete:
        check("complete", bool(row["working_meaning_de"]), row["reading_id"])
        score = int(row["working_model_score_0_100_not_probability"])
        check("complete", row["working_model_level"] == level(score), row["reading_id"])
        check("complete", bool(row["positive_evidence_de"]), row["reading_id"])
        check("complete", bool(row["counterevidence_de"]), row["reading_id"])
        check("complete", row["historical_confirmation"] == HISTORICAL, row["reading_id"])

    preserved = [
        ("V97_5_BOUND_SPAN_RENDERER.tsv", "V98_5_BOUND_SPAN_RENDERER.tsv"),
        ("V97_5_BOUND_SPAN_EXECUTION_AUDIT.tsv", "V98_5_BOUND_SPAN_EXECUTION_AUDIT.tsv"),
        ("V97_2_ONE_SHOT_RENDER_DIRECTIVES.tsv", "V98_2_ONE_SHOT_RENDER_DIRECTIVES.tsv"),
        ("V97_8_F7R2_RENDERED_UNITS.tsv", "V98_8_F7R2_RENDERED_UNITS.tsv"),
    ]
    for source_name, target_name in preserved:
        check("preserved", file_sha(G724 / source_name) == file_sha(ART / target_name), target_name)

    check("result", result["experiment_id"] == "GDT725")
    check("result", result["status"] == EXPECTED_STATUS)
    check("result", result["target_readings_audited"] == 16)
    check("result", result["target_positions"] == 21)
    check("result", result["target_lines"] == 18)
    check("result", result["target_pages"] == 17)
    check("result", result["revised_defaults_or_structural_tags"] == 9)
    check("result", result["reviewed_retained_exact_wholes"] == 7)
    check("result", result["structural_readings_separated_from_spoken_translation"] == 5)
    check("result", result["exact_action_wholes_retained"] == 4)
    check("result", result["primary_evidence_bindings"] == 72)
    check("result", result["remaining_unaudited_hardcap_readings"] == 0)
    check("result", result["remaining_low_confidence_readings_by_score"] == 16)
    check("result", result["score_delta_total"] == 0)
    check("result", result["component_global_exports"] == 0)
    check("result", result["bound_spans_executed_in_target_lines"] == 2)
    check("result", result["companion_line_renderer_repairs"] == 1)
    check("result", result["companion_line_renderer_score_or_core_delta"] == 0)
    check("result", result["complete_dictionary_rows_with_default_confidence_and_evidence"] == 1586)
    check("result", result["f84_or_f84r_used"] == 0)

    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    report_compact = " ".join(report.split())
    check("report", EXPECTED_STATUS in report)
    check("report", "zwei Portionen" in report)
    check("report", "[STRUKTUR: SATZSCHLUSS]" in report)
    check("report", "eine Teilmenge abmessen" in report)
    check("report", "GDT686" in report)
    check("report", "B001" in report and "B002" in report)
    check(
        "report",
        "drei Portionen des vorstehenden eingeweichten Arzneikompositums"
        in report_compact,
    )
    check("report", "0 unaudierte" in report)
    check("report", "f84" in report and "f84r" in report)

    check("sealed", all("f84" not in row["expected_page"].casefold() for row in position_specs))
    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    check("sealed", manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"})
    check("sealed", manifest["experiment_id"] == "GDT725")

    validation = {
        "experiment_id": "GDT725",
        "status": "PASS",
        "checks_passed": sum(checks.values()),
        "check_groups": dict(sorted(checks.items())),
        "target_readings_audited": 16,
        "target_positions": 21,
        "revised_defaults_or_structural_tags": 9,
        "reviewed_retained_exact_wholes": 7,
        "structural_readings_separated_from_spoken_translation": 5,
        "exact_action_wholes_retained": 4,
        "evidence_bindings_replayed": 72,
        "companion_line_source_bindings_replayed": 1,
        "bound_spans_executed_in_target_lines": 2,
        "companion_line_renderer_repairs": 1,
        "remaining_unaudited_hardcap_readings": 0,
        "remaining_low_confidence_readings_by_score": 16,
        "component_global_exports": 0,
        "score_delta_total": 0,
        "complete_dictionary_rows_with_default_confidence_and_evidence": 1586,
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
