#!/usr/bin/env python3
"""Compose exact registered H-wholes and bounded split fields after ``ol``.

Selection uses only surfaces and reader exactness over GDT776's fixed 376-row
renderer.  The one-character EVA strings stay opaque transcription labels.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt777_ol_registered_split_fusion_composer"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
G776 = ROOT / "experiments/yolo/gdt776_ol_h4_h3_medial_register_bridge/artifacts/GDT776_376_RENDERER.tsv"
G736 = ROOT / "experiments/yolo/gdt736_opaque_head_record_role_bridge/artifacts/OPAQUE_96_CONCRETE_ROLE_GRID.tsv"
G737_FORMS = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_273_FORM_ROLE_BRIDGE.tsv"
G737_BODIES = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_BODY_WORKING_CANDIDATES.tsv"
G737_UPDATE = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/TRANSFER_MODEL_UPDATE.tsv"
G759_SPANS = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv"
G759_DICT = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/GDT759_EXACT_CONSTRUCTION_DICTIONARY.tsv"
G759_BOUND = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/QUANTITY_7_EXACT_BOUNDARY_BRIDGES.tsv"
G762 = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/SEMANTIC_PRECEDENCE_REPAIR_AUDIT.tsv"
G769_CORE = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/src/core_atlas.py"
SPECS = SRC / "REGISTERED_FIELD_SPECS.tsv"
HEADS = frozenset({"p", "s", "r", "l"})
BANNED = re.compile(r"(?i)(pulver|samen|wurzel|holz|drogen)")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def serialise(value: object) -> object:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return f"{value:.9f}"
    return value


def write_tsv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    material = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in material:
            writer.writerow({field: serialise(row.get(field, "")) for field in fields})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_locks() -> int:
    rows = read_tsv(SRC / "SOURCE_LOCK.tsv")
    assert len(rows) == 14
    for row in rows:
        relative = Path(row["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        assert sha256(ROOT / relative) == row["expected_sha256"], f"source changed: {relative}"
    return len(rows)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def physical_folio(page: str) -> str:
    if page.startswith("fRos"):
        return "fRos"
    match = re.match(r"^(f\d+)", page)
    assert match is not None, page
    return match.group(1)


def cosine(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    keys = set(left) | set(right)
    numerator = sum(float(left.get(key, 0)) * float(right.get(key, 0)) for key in keys)
    lnorm = math.sqrt(sum(float(value) ** 2 for value in left.values()))
    rnorm = math.sqrt(sum(float(value) ** 2 for value in right.values()))
    return numerator / (lnorm * rnorm) if lnorm and rnorm else 0.0


def position_class(start: int, end: int, count: int) -> str:
    if start == 1 and end == count:
        return "ONLY"
    if start == 1:
        return "FIRST"
    if end == count:
        return "FINAL"
    return "MIDDLE"


def load_registry(specs: Sequence[Mapping[str, str]]) -> tuple[dict[str, dict[str, object]], list[dict[str, object]]]:
    held_bodies = {row["body"]: row for row in read_tsv(G737_BODIES)}
    registry: dict[str, dict[str, object]] = {}
    for row in read_tsv(G736):
        registry[row["form"]] = {
            "registered_form": row["form"], "head_id": row["opaque_head_id"], "body": row["body"],
            "registry_source": "GDT736_TRAINING", "record_role": row["selected_formal_role"],
            "body_candidate_de": row["revised_body_role_de"], "body_confidence": row["body_role_confidence"],
            "registry_exact_occurrences": int(row["reader_exact_occurrences"]),
            "registry_renderer_de": row["structural_role_render_de"], "inherited_whole_status": row["status"],
        }
    for row in read_tsv(G737_FORMS):
        form, body = row["form"], row["body"]
        assert form not in registry and body in held_bodies
        body_row = held_bodies[body]
        assert row["exploratory_body_candidate_de"] == body_row["concrete_body_role_de"]
        assert row["body_candidate_renderer_license"] == body_row["renderer_license"] == "0"
        registry[form] = {
            "registered_form": form, "head_id": row["opaque_head_id"], "body": body,
            "registry_source": "GDT737_HELD", "record_role": row["gdt736_training_record_role"],
            "body_candidate_de": row["exploratory_body_candidate_de"],
            "body_confidence": row["exploratory_candidate_confidence"],
            "registry_exact_occurrences": int(row["atlas_reader_exact"]),
            "registry_renderer_de": row["exploratory_renderer_de"],
            "inherited_whole_status": row["inherited_whole_status"],
        }
    transfer = {row["claim_id"]: row for row in read_tsv(G737_UPDATE)}
    assert transfer["C03"]["new_live_status"] == "RETAIN_AS_RELATIVE_POSITION_SUBROLES"
    repair = {row["surface"]: row for row in read_tsv(G762)}
    source_specs = {row["registered_form"]: row for row in specs}
    assert len(source_specs) == len(specs) == 17
    output: list[dict[str, object]] = []
    for form in sorted(source_specs):
        source, registered = source_specs[form], registry[form]
        assert source["expected_head_id"] == registered["head_id"]
        assert source["expected_body"] == registered["body"]
        assert source["source_mode"] == registered["registry_source"]
        visible = " ".join(source[key] for key in (
            "selected_whole_field_de", "selected_split_field_de", "alternate_1_de", "alternate_2_de",
            "positive_evidence", "counterevidence",
        ))
        assert BANNED.search(visible) is None, (form, visible)
        repaired = repair.get(form)
        if registered["registry_source"] == "GDT736_TRAINING" and form != "saiin":
            assert repaired is not None and repaired["old_literal_head_noun_detected"] == "1"
            assert repaired["component_export_credit"] == "0"
        output.append({
            **registered, "semantic_family": source["semantic_family"],
            "selected_whole_field_de": source["selected_whole_field_de"],
            "selected_split_field_de": source["selected_split_field_de"], "confidence": source["confidence"],
            "alternate_1_de": source["alternate_1_de"], "alternate_2_de": source["alternate_2_de"],
            "positive_evidence": source["positive_evidence"], "counterevidence": source["counterevidence"],
            "gdt759_exact_expression": source["gdt759_exact_expression"], "scope_status": source["scope_status"],
            "gdt762_repair_present": int(repaired is not None),
            "gdt762_repair_decision": repaired["decision"] if repaired else "SUPERSEDED_BY_GDT759_S_VALUE_REPAIR",
            "retired_literal_patient_removed": 1, "literal_head_lexeme": "UNRESOLVED",
            "default_is_translation": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    return registry, output


def build_span_cohort(base: Sequence[Mapping[str, str]], context: object,
                      registry: Mapping[str, Mapping[str, object]],
                      specs: Mapping[str, Mapping[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    selected: list[dict[str, object]] = []
    excluded: list[dict[str, object]] = []
    for source in base:
        locus, ol_ordinal = source["locus"], int(source["ordinal"])
        line = context.by_line[locus]
        if ol_ordinal >= len(line):
            assert source["right_surface"] == "NONE"
            continue
        ol_token, right_token = line[ol_ordinal - 1], line[ol_ordinal]
        assert str(ol_token["eva"]) == "ol" and str(right_token["eva"]) == source["right_surface"]
        ol_exact = bool(context.exact[(locus, int(ol_token["token_index"]))])
        right_exact = bool(context.exact[(locus, int(right_token["token_index"]))])
        assert ol_exact and int(source["right_reader_exact"]) == int(right_exact)
        candidates: list[tuple[str, str, int, bool, str]] = []
        if source["right_surface"] in registry:
            candidates.append(("REGISTERED_COMPLETE_WHOLE", source["right_surface"], ol_ordinal + 1,
                               right_exact, "RIGHT_TOKEN_READER_EXACT"))
        if source["right_surface"] in HEADS and ol_ordinal + 1 < len(line):
            successor = line[ol_ordinal + 1]
            fused = source["right_surface"] + str(successor["eva"])
            if fused in registry:
                successor_exact = bool(context.exact[(locus, int(successor["token_index"]))])
                candidates.insert(0, ("REGISTERED_SPLIT_FIELD", fused, ol_ordinal + 2,
                                      right_exact and successor_exact, "RIGHT_AND_SUCCESSOR_READER_EXACT"))
        if not candidates:
            continue
        branch, fused, end_ordinal, eligible, exactness_rule = candidates[0]
        if not eligible:
            successor_exact = end_ordinal == ol_ordinal + 1 or bool(
                context.exact[(locus, int(line[end_ordinal - 1]["token_index"]))]
            )
            excluded.append({
                "page": source["page"], "physical_folio": source["physical_folio"], "locus": locus,
                "ol_ordinal": ol_ordinal, "candidate_branch": branch,
                "candidate_span_eva": " ".join(str(token["eva"]) for token in line[ol_ordinal - 1:end_ordinal]),
                "candidate_registered_form": fused, "right_reader_exact": int(right_exact),
                "successor_reader_exact": int(successor_exact), "exclusion_reason": f"FAIL_{exactness_rule}",
                "selection_uses_occurrence_id": 0, "component_export_credit": 0,
            })
            continue
        registered, spec = registry[fused], specs[fused]
        is_split = branch == "REGISTERED_SPLIT_FIELD"
        default = spec["selected_split_field_de"] if is_split else spec["selected_whole_field_de"]
        assert default != "NONE"
        selected.append({
            "span_id": "PENDING", "page": source["page"], "physical_folio": source["physical_folio"],
            "locus": locus, "section": source["section"], "language": source["language"], "hand": source["hand"],
            "register_id": f"{source['section']}|{source['language']}|{source['hand']}",
            "ol_ordinal": ol_ordinal, "field_start_ordinal": ol_ordinal + 1, "field_end_ordinal": end_ordinal,
            "line_token_count": len(line), "span_line_position": position_class(ol_ordinal, end_ordinal, len(line)),
            "branch": branch, "written_span_eva": " ".join(str(token["eva"]) for token in line[ol_ordinal - 1:end_ordinal]),
            "right_field_eva": " ".join(str(token["eva"]) for token in line[ol_ordinal:end_ordinal]),
            "registered_fused_form": fused, "opaque_head_surface": fused[0], "body_surface": registered["body"],
            "head_id": registered["head_id"], "registry_source": registered["registry_source"],
            "record_role": registered["record_role"], "semantic_family": spec["semantic_family"],
            "old_gdt776_default_de": source["gdt776_default_de"],
            "old_gdt776_contextual": int(source["gdt776_renderer_contextual"]),
            "new_gdt777_default_de": default, "fallback_replacement": 1 - int(source["gdt776_renderer_contextual"]),
            "contextual_sharpening": int(source["gdt776_renderer_contextual"]),
            "consumed_token_count": end_ordinal - ol_ordinal,
            "consumed_token_ids": "|".join(f"{locus}@{ordinal}" for ordinal in range(ol_ordinal + 1, end_ordinal + 1)),
            "confidence": spec["confidence"], "positive_evidence": spec["positive_evidence"],
            "counterevidence": spec["counterevidence"], "alternate_1_de": spec["alternate_1_de"],
            "alternate_2_de": spec["alternate_2_de"],
            "selection_rule": "SURFACE_REGISTERED_AND_REQUIRED_TOKENS_READER_EXACT__NO_OCCURRENCE_ID",
            "exactness_rule": exactness_rule, "written_line_eva": source["written_line_eva"],
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    selected.sort(key=lambda row: (str(row["page"]), str(row["locus"]), int(row["ol_ordinal"])))
    excluded.sort(key=lambda row: (str(row["page"]), str(row["locus"]), int(row["ol_ordinal"])))
    for number, row in enumerate(selected, 1):
        row["span_id"] = f"G777-S{number:03d}"
    assert len(selected) == 23
    assert Counter(row["branch"] for row in selected) == Counter({"REGISTERED_COMPLETE_WHOLE": 16, "REGISTERED_SPLIT_FIELD": 7})
    assert sum(int(row["fallback_replacement"]) for row in selected) == 14
    assert sum(int(row["contextual_sharpening"]) for row in selected) == 9
    assert len({row["registered_fused_form"] for row in selected}) == 17
    assert len(excluded) == 7
    assert Counter(row["candidate_branch"] for row in excluded) == Counter({"REGISTERED_COMPLETE_WHOLE": 5, "REGISTERED_SPLIT_FIELD": 2})
    consumed = [token for row in selected for token in str(row["consumed_token_ids"]).split("|")]
    assert len(consumed) == len(set(consumed)) == 30
    return selected, excluded


def exact_occurrences(context: object, form: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for locus in sorted(context.by_line):
        line = context.by_line[locus]
        for index, token in enumerate(line):
            if str(token["eva"]) != form or not context.exact[(locus, int(token["token_index"]))]:
                continue
            rows.append({
                "page": str(token["page"]), "physical_folio": physical_folio(str(token["page"])),
                "locus": locus, "register_id": f"{token['section']}|{token['language']}|{token['hand']}",
                "position": position_class(index + 1, index + 1, len(line)),
                "left": str(line[index - 1]["eva"]) if index > 0 and context.exact[(locus, int(line[index - 1]["token_index"]))] else "EDGE_OR_NONEXACT",
                "right": str(line[index + 1]["eva"]) if index + 1 < len(line) and context.exact[(locus, int(line[index + 1]["token_index"]))] else "EDGE_OR_NONEXACT",
            })
    return rows


def exact_split_occurrences(context: object, head: str, body: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for locus in sorted(context.by_line):
        line = context.by_line[locus]
        for index, (left, right) in enumerate(zip(line, line[1:])):
            if str(left["eva"]) != head or str(right["eva"]) != body:
                continue
            if not context.exact[(locus, int(left["token_index"]))] or not context.exact[(locus, int(right["token_index"]))]:
                continue
            rows.append({
                "page": str(left["page"]), "physical_folio": physical_folio(str(left["page"])),
                "locus": locus, "register_id": f"{left['section']}|{left['language']}|{left['hand']}",
                "position": position_class(index + 1, index + 2, len(line)),
                "left": str(line[index - 1]["eva"]) if index > 0 and context.exact[(locus, int(line[index - 1]["token_index"]))] else "EDGE_OR_NONEXACT",
                "right": str(line[index + 2]["eva"]) if index + 2 < len(line) and context.exact[(locus, int(line[index + 2]["token_index"]))] else "EDGE_OR_NONEXACT",
            })
    return rows


def feature_vector(rows: Sequence[Mapping[str, object]], field: str) -> Counter[str]:
    return Counter(str(row[field]) for row in rows)


def neighbor_vector(rows: Sequence[Mapping[str, object]]) -> Counter[str]:
    output: Counter[str] = Counter()
    for row in rows:
        output[f"L:{row['left']}"] += 1
        output[f"R:{row['right']}"] += 1
    return output


def build_profiles(context: object, registry_rows: Sequence[Mapping[str, object]],
                   spans: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    dictionary = {row["exact_expression_eva"]: row for row in read_tsv(G759_DICT)}
    boundaries = read_tsv(G759_BOUND)
    span_atlas = read_tsv(G759_SPANS)
    output: list[dict[str, object]] = []
    for registered in registry_rows:
        form, body = str(registered["registered_form"]), str(registered["body"])
        fused = exact_occurrences(context, form)
        split = exact_split_occurrences(context, form[0], body)
        assert len(fused) == int(registered["registry_exact_occurrences"]), (form, len(fused), registered["registry_exact_occurrences"])
        expression = f"{form[0]} {body}"
        g759 = dictionary.get(expression)
        boundary_count = sum(
            row["head_surface"] == form[0] and row["value_surface"] == body
            and row["fused_surface"] == form and row["bridge_class"] == "EXACT_NORMALIZED_BOUNDARY_EQUIVALENCE"
            for row in boundaries
        )
        if form == "saiin":
            assert g759 is not None
            assert int(g759["exact_occurrences"]) == len(split) == 23
            assert int(g759["fused_counterpart_occurrences"]) == len(fused) == 89
            assert int(g759["exact_boundary_bridges"]) == boundary_count == 4
            assert sum(row["exact_span_eva"] == expression for row in span_atlas) == 23
        renderer_rows = [row for row in spans if row["registered_fused_form"] == form]
        if boundary_count:
            relation = "ALTERNATE_READER_BOUNDARY_EQUIVALENT__FIELD_BODY_SHARED"
        elif fused and split:
            relation = "DISTINCT_SURFACE_CONSTRUCTIONS__REGISTERED_BODY_SHARED"
        elif split:
            relation = "SPLIT_ONLY_IN_GUARDED_CACHE__REGISTERED_BODY_SHARED"
        else:
            relation = "FUSED_ONLY_IN_GUARDED_CACHE__NO_SPLIT_CLAIM"
        output.append({
            "registered_form": form, "head_id": registered["head_id"], "opaque_head_surface": form[0],
            "body_surface": body, "semantic_family": registered["semantic_family"],
            "guarded_fused_exact_occurrences": len(fused), "guarded_fused_physical_folios": len({row["physical_folio"] for row in fused}),
            "guarded_split_exact_occurrences": len(split), "guarded_split_physical_folios": len({row["physical_folio"] for row in split}),
            "renderer_whole_spans": sum(row["branch"] == "REGISTERED_COMPLETE_WHOLE" for row in renderer_rows),
            "renderer_split_spans": sum(row["branch"] == "REGISTERED_SPLIT_FIELD" for row in renderer_rows),
            "register_cosine_fused_split": cosine(feature_vector(fused, "register_id"), feature_vector(split, "register_id")),
            "line_position_cosine_fused_split": cosine(feature_vector(fused, "position"), feature_vector(split, "position")),
            "outer_neighbor_cosine_fused_split": cosine(neighbor_vector(fused), neighbor_vector(split)),
            "gdt759_exact_span_occurrences": int(g759["exact_occurrences"]) if g759 else 0,
            "gdt759_exact_boundary_bridges": boundary_count, "profile_relation": relation,
            "boundary_equivalence_required_for_renderer": 0, "literal_spelling_identity_inferred": 0,
            "semantic_identity_inferred": 0, "component_export_credit": 0,
        })
    assert len(output) == 17
    return output


def build_sal_control(context: object, registry: Mapping[str, Mapping[str, object]],
                      exclusions: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    assert registry["sal"]["head_id"] == "H2" and registry["sal"]["body"] == "al"
    raw_split = 0
    exact_split = 0
    for locus in sorted(context.by_line):
        line = context.by_line[locus]
        for left, right in zip(line, line[1:]):
            if str(left["eva"]) == "s" and str(right["eva"]) == "al":
                raw_split += 1
                exact_split += int(
                    context.exact[(locus, int(left["token_index"]))]
                    and context.exact[(locus, int(right["token_index"]))]
                )
    fused = exact_occurrences(context, "sal")
    local = [row for row in exclusions if row["candidate_registered_form"] == "sal"]
    assert len(fused) == int(registry["sal"]["registry_exact_occurrences"]) == 33
    assert raw_split == 5 and exact_split == 0 and len(local) == 1
    return [{
        "registered_form": "sal", "head_id": "H2", "opaque_head_surface": "s", "body_surface": "al",
        "guarded_fused_exact_occurrences": len(fused), "guarded_raw_split_occurrences": raw_split,
        "guarded_reader_exact_split_occurrences": exact_split, "ol_local_raw_candidates": len(local),
        "ol_local_reader_exact_candidates": 0, "failed_locus": local[0]["locus"],
        "failed_token": "al", "decision": "EXCLUDE_SPLIT__SUCCESSOR_NOT_READER_EXACT",
        "boundary_equivalence_inferred": 0, "semantic_identity_inferred": 0, "component_export_credit": 0,
    }]


def build_renderer(base: Sequence[Mapping[str, str]], spans: Sequence[Mapping[str, object]]) -> tuple[list[dict[str, object]], set[str]]:
    by_position = {(str(row["locus"]), int(row["ol_ordinal"])): row for row in spans}
    assert len(by_position) == len(spans)
    output: list[dict[str, object]] = []
    consumed: set[str] = set()
    retained_source_fields = (
        "target_occurrence_id", "page", "physical_folio", "locus", "section", "language", "hand",
        "ordinal", "right_surface", "right_ordinal", "right_reader_exact", "written_line_eva",
        "gdt776_branch", "gdt776_default_de", "gdt776_renderer_contextual",
        "gdt776_span_consumes_right_token", "gdt776_span_id", "gdt776_right_whole",
        "gdt776_candidate_whole_de", "gdt776_semantic_family", "gdt776_confidence",
        "gdt776_positive_evidence", "gdt776_counterevidence", "gdt776_scope_status",
        "gdt776_dispatch_rule", "gdt776_structural_bridge", "default_is_translation",
        "confirmed_lexeme", "confirmed_plaintext", "component_export_credit",
    )
    for source in base:
        span = by_position.get((source["locus"], int(source["ordinal"])))
        row: dict[str, object] = {field: source[field] for field in retained_source_fields}
        inherited_ids = f"{source['locus']}@{int(source['ordinal']) + 1}" if int(source["gdt776_span_consumes_right_token"]) else "NONE"
        row.update({
            "gdt777_branch": "INHERITED_GDT776", "gdt777_default_de": source["gdt776_default_de"],
            "gdt777_renderer_contextual": int(source["gdt776_renderer_contextual"]),
            "gdt777_span_id": source["gdt776_span_id"], "gdt777_registered_form": "NONE",
            "gdt777_field_head_surface": "NONE", "gdt777_body_surface": "NONE",
            "gdt777_semantic_family": source["gdt776_semantic_family"], "gdt777_confidence": source["gdt776_confidence"],
            "gdt777_consumed_token_count": int(source["gdt776_span_consumes_right_token"]),
            "gdt777_consumed_token_ids": inherited_ids, "gdt777_fallback_replacement": 0,
            "gdt777_contextual_sharpening": 0, "gdt777_positive_evidence": source["gdt776_positive_evidence"],
            "gdt777_counterevidence": source["gdt776_counterevidence"], "gdt777_dispatch_rule": "INHERITED_GDT776",
            "gdt777_default_is_translation": 0, "gdt777_confirmed_lexeme": 0,
            "gdt777_confirmed_plaintext": 0, "gdt777_component_export_credit": 0,
        })
        if span is not None:
            row.update({
                "gdt777_branch": f"GDT777_{span['branch']}", "gdt777_default_de": span["new_gdt777_default_de"],
                "gdt777_renderer_contextual": 1, "gdt777_span_id": span["span_id"],
                "gdt777_registered_form": span["registered_fused_form"],
                "gdt777_field_head_surface": span["opaque_head_surface"], "gdt777_body_surface": span["body_surface"],
                "gdt777_semantic_family": span["semantic_family"], "gdt777_confidence": span["confidence"],
                "gdt777_consumed_token_count": span["consumed_token_count"],
                "gdt777_consumed_token_ids": span["consumed_token_ids"],
                "gdt777_fallback_replacement": span["fallback_replacement"],
                "gdt777_contextual_sharpening": span["contextual_sharpening"],
                "gdt777_positive_evidence": span["positive_evidence"],
                "gdt777_counterevidence": span["counterevidence"], "gdt777_dispatch_rule": span["selection_rule"],
            })
        output.append(row)
        if row["gdt777_consumed_token_ids"] != "NONE":
            for token_id in str(row["gdt777_consumed_token_ids"]).split("|"):
                assert token_id not in consumed, token_id
                consumed.add(token_id)
        assert BANNED.search(" ".join(str(value) for value in row.values())) is None
    assert len(output) == 376
    assert sum(int(row["gdt777_renderer_contextual"]) for row in output) == 163
    assert sum(int(row["gdt777_fallback_replacement"]) for row in output) == 14
    assert sum(int(row["gdt777_contextual_sharpening"]) for row in output) == 9
    assert len(consumed) == 120
    return output, consumed


def build_dictionary(registry_rows: Sequence[Mapping[str, object]], spans: Sequence[Mapping[str, object]],
                     profiles: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    profile = {row["registered_form"]: row for row in profiles}
    output: list[dict[str, object]] = []
    for registered in registry_rows:
        form = str(registered["registered_form"])
        selected = [row for row in spans if row["registered_fused_form"] == form]
        whole = sum(row["branch"] == "REGISTERED_COMPLETE_WHOLE" for row in selected)
        split = sum(row["branch"] == "REGISTERED_SPLIT_FIELD" for row in selected)
        preferred = registered["selected_split_field_de"] if split and not whole else registered["selected_whole_field_de"]
        output.append({
            "entry": form, "head_id": registered["head_id"], "opaque_head_surface": form[0],
            "body_surface": registered["body"], "semantic_family": registered["semantic_family"],
            "preferred_gdt777_default_de": preferred, "whole_context_default_de": registered["selected_whole_field_de"],
            "split_context_default_de": registered["selected_split_field_de"], "confidence": registered["confidence"],
            "renderer_whole_spans": whole, "renderer_split_spans": split,
            "guarded_fused_exact_occurrences": profile[form]["guarded_fused_exact_occurrences"],
            "guarded_split_exact_occurrences": profile[form]["guarded_split_exact_occurrences"],
            "positive_evidence": registered["positive_evidence"], "counterevidence": registered["counterevidence"],
            "alternate_1_de": registered["alternate_1_de"], "alternate_2_de": registered["alternate_2_de"],
            "profile_relation": profile[form]["profile_relation"], "scope_status": registered["scope_status"],
            "retired_literal_patient_removed": 1, "default_is_translation": 0,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    assert len(output) == 17
    return output


def build_passages(renderer: Sequence[Mapping[str, object]], spans: Sequence[Mapping[str, object]],
                   context: object) -> list[dict[str, object]]:
    selected_by_position = {(str(row["locus"]), int(row["ol_ordinal"])): row for row in spans}
    renderer_by_position = {(str(row["locus"]), int(row["ordinal"])): row for row in renderer}
    output: list[dict[str, object]] = []
    for number, locus in enumerate(sorted({str(row["locus"]) for row in spans}), 1):
        line = context.by_line[locus]
        rendered: list[str] = []
        consumed: set[int] = set()
        for ordinal, token in enumerate(line, 1):
            if ordinal in consumed:
                continue
            dispatch = renderer_by_position.get((locus, ordinal))
            if dispatch is None:
                rendered.append(str(token["eva"]))
                continue
            selected = selected_by_position.get((locus, ordinal))
            if selected is not None or int(dispatch["gdt777_renderer_contextual"]):
                rendered.append(f"⟦{dispatch['gdt777_default_de']}⟧")
                count = int(dispatch["gdt777_consumed_token_count"])
                consumed.update(range(ordinal + 1, ordinal + count + 1))
            else:
                rendered.append(str(token["eva"]))
        additions = [row for row in spans if row["locus"] == locus]
        first = additions[0]
        output.append({
            "passage_patch_id": f"G777-P{number:03d}", "page": first["page"], "physical_folio": first["physical_folio"],
            "locus": locus, "section": first["section"], "language": first["language"], "hand": first["hand"],
            "selected_spans": len(additions), "fallback_replacements": sum(int(row["fallback_replacement"]) for row in additions),
            "contextual_sharpenings": sum(int(row["contextual_sharpening"]) for row in additions),
            "selected_units_de": " || ".join(f"{row['written_span_eva']} → {row['new_gdt777_default_de']}" for row in additions),
            "written_line_eva": " ".join(str(token["eva"]) for token in line), "practical_patch_de": " ".join(rendered),
            "patch_legend": "double brackets are replaceable exact-span defaults; unbracketed EVA remains unresolved",
            "default_is_translation": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    assert sum(int(row["selected_spans"]) for row in output) == 23
    return output


def make_packet(spans: Sequence[Mapping[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    packet: list[dict[str, object]] = []
    crosswalk: list[dict[str, object]] = []
    for number, span in enumerate(spans, 1):
        is_split = span["branch"] == "REGISTERED_SPLIT_FIELD"
        pivot = int(span["field_start_ordinal"]) if is_split else int(span["ol_ordinal"])
        target = int(span["field_end_ordinal"])
        edge_id, batch = f"G777-E{number:03d}", "REGISTERED_SPLIT" if is_split else "REGISTERED_WHOLE"
        packet.append({
            "edge_id": edge_id, "batch_id": f"GDT777_{batch}", "page": span["page"],
            "physical_folio": span["physical_folio"], "diagram_unit_id": f"LINE:{span['locus']}",
            "pivot_visual_id": f"TOKEN:{span['locus']}:{pivot}", "pivot_locus": f"{span['locus']}@{pivot}",
            "target_visual_id": f"TOKEN:{span['locus']}:{target}", "target_locus": f"{span['locus']}@{target}",
            "relation_type": "NEXT_TOKEN", "direction_basis": "TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_ADJACENCY", "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT769", "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE", "source_aware_localizer": "GDT777_RUNNER",
            "relation_reviewer": "GDT777_VALIDATOR", "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "UNREVIEWED_TEXT_RELATION", "formal_access_state": "SEALED_NOT_ACCESSED",
            "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
        crosswalk.append({
            "edge_id": edge_id, "batch_id": f"GDT777_{batch}", "span_id": span["span_id"],
            "page": span["page"], "physical_folio": span["physical_folio"], "locus": span["locus"],
            "ol_ordinal": span["ol_ordinal"], "field_start_ordinal": span["field_start_ordinal"],
            "field_end_ordinal": span["field_end_ordinal"], "written_span_eva": span["written_span_eva"],
            "registered_fused_form": span["registered_fused_form"], "head_id": span["head_id"],
            "body_surface": span["body_surface"], "selection_rule": span["selection_rule"],
            "score_eligible": 0, "component_export_credit": 0,
        })
    assert len(packet) == len(crosswalk) == 23
    return packet, crosswalk


def build_report(result: Mapping[str, object], passages: Sequence[Mapping[str, object]],
                 profiles: Sequence[Mapping[str, object]]) -> str:
    split_profiles = [row for row in profiles if int(row["renderer_split_spans"])]
    examples = [row for locus in ("f55v.10", "f105r.15", "f108v.25", "f82r.31") for row in passages if row["locus"] == locus]
    rendered_examples = "\n\n".join(
        f"- `{row['locus']}`: `{row['written_line_eva']}`\n  → {row['practical_patch_de']}" for row in examples
    )
    profile_lines = "\n".join(
        f"- `{row['opaque_head_surface']} {row['body_surface']}` / `{row['registered_form']}`: "
        f"split={row['guarded_split_exact_occurrences']}, fused={row['guarded_fused_exact_occurrences']}, "
        f"Register-Cosinus={float(row['register_cosine_fused_split']):.3f}, Klasse `{row['profile_relation']}`."
        for row in split_profiles
    )
    return f"""# GDT777 — registrierte Ganz- und Splitfelder nach `ol`

Status: `{result['status']}`.

## Ergebnis

Die feste Oberflächenregel findet **23** reader-exakte Spannen: **16**
`ol + Ganzform`-Vorkommen und **7** `ol + Kopf + body`-Vorkommen. Sie
repräsentieren **17** registrierte fusionierte H-Formen. Vierzehn bisherige
Fallbacks erhalten einen kurzen Feldwert; neun schon kontextuelle Ausgaben
werden geschärft. Damit steigt die kontextuelle Abdeckung des unveränderten
376er `ol`-Bestands von **149 auf 163**, und **120** rechte Token werden im
Gesamtrenderer kollisionsfrei genau einmal konsumiert.

Die Vorabschätzung enthielt `ol s al`. Das `al`-Token ist in der bewachten
Lesung nicht reader-exakt und wird von derselben Regel ausgeschlossen. Ebenso
bleiben fünf nicht-exakte rechte Ganzformen und ein nicht-exaktes `s aiin`
draußen. Der globale Negativkontrollwert ist deutlich: `sal` hat 33 exakte
fusionierte Vorkommen, `s al` aber null exakte unter fünf rohen Paaren. Es gibt
keine handverlesene Occurrence-ID-Liste.

## Konkrete Arbeitswerte

Die neue Ausgabe benutzt kurze gebundene Felder wie `Binnenfeld: heißer Anteil
I`, `Binnenfeld: Trockenansatz`, `Bezugsfeld: Wert III`, `Eintragsfeld:
Trockenresultat I` und `Bezugsfeld: Feuchtresultat II`. `s aiin` erhält an
seinen vier exakten `ol`-Positionen den GDT759-Wert `Menge: drei Drachmen`;
`drei gleiche Teile` und `drei Unzen` bleiben als Rivalen sichtbar. Keine
Karte macht `p`, `s`, `r` oder `l` zu einem Wort oder einer Abkürzung.

## Split gegen Fusion im bewachten Cache

{profile_lines}

Nur `s aiin` / `saiin` besitzt die vier normalisierten
Alternate-Reader-Grenzbrücken aus GDT759. Die anderen Splitformen teilen hier
nur einen registrierten Inhalts-body mit der fusionierten Ganzform; sie werden
nicht als identische Schreibung oder als austauschbares Lexem behauptet.

## Vier Passage-Patches

{rendered_examples}

Doppelklammern markieren ersetzbare exakte Feldwerte; unmarkiertes EVA bleibt
ungelöst. Die Zeilen sind keine Klartextübersetzungen.

## Grenze

Das GDT388-Paket enthält **23** deskriptive Transkriptionsrelationen. Der
Intake lautet `{result['relation_packet']['status']}`; alle Kanten bleiben
`INELIGIBLE_EXPLORATORY_TEXT_RELATION`. Es wurden keine neuen Seiten, Bilder,
OCR, Transkriptionen, `f84`- oder `f84r`-Daten geöffnet.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts, report_path = args.artifacts_dir.resolve(), args.report_path.resolve()
    lock_count = verify_locks()
    core = load_module("gdt769_core_for_gdt777", G769_CORE)
    _, environment = core.load_guarded_environment(ROOT)
    assert dict(environment["guard"]) == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}
    context = environment["context"]
    spec_rows = read_tsv(SPECS)
    registry, registry_rows = load_registry(spec_rows)
    specs = {row["registered_form"]: row for row in spec_rows}
    base = read_tsv(G776)
    assert len(base) == 376 and sum(int(row["gdt776_renderer_contextual"]) for row in base) == 149
    spans, exclusions = build_span_cohort(base, context, registry, specs)
    profiles = build_profiles(context, registry_rows, spans)
    sal_control = build_sal_control(context, registry, exclusions)
    renderer, consumed = build_renderer(base, spans)
    dictionary = build_dictionary(registry_rows, spans, profiles)
    passages = build_passages(renderer, spans, context)
    packet, crosswalk = make_packet(spans)
    outputs = [
        ("REGISTERED_17_FIELD_REGISTRY.tsv", registry_rows, list(registry_rows[0])),
        ("GDT777_23_SPAN_ATLAS.tsv", spans, list(spans[0])),
        ("GDT777_EXACTNESS_EXCLUSIONS.tsv", exclusions, list(exclusions[0])),
        ("SPLIT_FUSION_PROFILE.tsv", profiles, list(profiles[0])),
        ("SAL_SPLIT_NEGATIVE_CONTROL.tsv", sal_control, list(sal_control[0])),
        ("GDT777_376_RENDERER.tsv", renderer, list(renderer[0])),
        ("GDT777_WORKING_DICTIONARY.tsv", dictionary, list(dictionary[0])),
        ("GDT777_PASSAGE_PATCHES.tsv", passages, list(passages[0])),
        ("GDT777_GDT388_RELATION_PACKET.tsv", packet, list(packet[0])),
        ("GDT777_RELATION_EDGE_CROSSWALK.tsv", crosswalk, list(crosswalk[0])),
    ]
    for name, rows, fields in outputs:
        write_tsv(artifacts / name, rows, fields)
    intake_done = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(artifacts / "GDT777_GDT388_RELATION_PACKET.tsv")],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    intake = json.loads(intake_done.stdout)
    assert intake == {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 23, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False, "errors": [],
    }
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", intake)
    saiin = next(row for row in profiles if row["registered_form"] == "saiin")
    result: dict[str, object] = {
        "experiment_id": "GDT777",
        "status": "PASS__23_REGISTERED_SPANS__14_FALLBACKS_REPLACED__9_CONTEXTUAL_SHARPENED__163_CONTEXTUAL__NO_COMPONENT_EXPORT",
        "source_locks": lock_count, "guard": dict(environment["guard"]),
        "cohort": {"renderer_rows": 376, "selected_spans": 23, "registered_whole_spans": 16,
                   "registered_split_spans": 7, "registered_fused_form_types": 17,
                   "fallback_replacements": 14, "contextual_sharpenings": 9,
                   "exactness_exclusions": len(exclusions)},
        "renderer": {"gdt776_contextual": 149, "gdt777_contextual": 163, "new_contextual": 14,
                     "fallbacks": 213, "selected_span_consumed_tokens": 30,
                     "total_consumed_right_tokens": len(consumed), "passage_patches": len(passages)},
        "split_fusion": {"renderer_split_types": 4,
                         "saiin_guarded_fused_exact": int(saiin["guarded_fused_exact_occurrences"]),
                         "s_aiin_guarded_split_exact": int(saiin["guarded_split_exact_occurrences"]),
                         "s_aiin_normalized_boundary_bridges": int(saiin["gdt759_exact_boundary_bridges"]),
                         "sal_fused_exact": int(sal_control[0]["guarded_fused_exact_occurrences"]),
                         "s_al_raw_split": int(sal_control[0]["guarded_raw_split_occurrences"]),
                         "s_al_reader_exact_split": int(sal_control[0]["guarded_reader_exact_split_occurrences"]),
                         "literal_spelling_identity_exported": False, "free_head_component_exported": False},
        "dictionary_rows": len(dictionary), "relation_packet": intake, "retired_literal_patient_leaks": 0,
        "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "component_exports": 0,
        "new_pages": 0, "new_images": 0, "new_ocr": 0, "new_transcriptions": 0,
        "sealed_pages_accessed": 0,
        "claim_ceiling": "Replaceable exact ol+registered-whole and ol+split-field defaults; no free EVA head meaning, spelling identity, language, plaintext, or specific substance.",
    }
    write_json(artifacts / "RESULT.json", result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(result, passages, profiles), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
