#!/usr/bin/env python3
"""Independent source, metric, renderer, packet, and replay audit for GDT776."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from types import ModuleType
from typing import Callable, Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt776_ol_h4_h3_medial_register_bridge"
SRC, ART = EXP / "src", EXP / "artifacts"
RUN, REPORT, VALIDATION = SRC / "run.py", EXP / "REPORT.md", ART / "VALIDATION.json"
G775_ATLAS = ROOT / "experiments/yolo/gdt775_ol_right_complement_slot_test/artifacts/OL_327_RIGHT_COMPLEMENT_ATLAS.tsv"
G775_RENDERER = ROOT / "experiments/yolo/gdt775_ol_right_complement_slot_test/artifacts/GDT775_376_RENDERER.tsv"
G734 = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
G735_HISTORY = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/src/HISTORICAL_SOURCE_REGISTRY.tsv"
G736_GRID = ROOT / "experiments/yolo/gdt736_opaque_head_record_role_bridge/artifacts/OPAQUE_96_CONCRETE_ROLE_GRID.tsv"
G737_FORMS = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_273_FORM_ROLE_BRIDGE.tsv"
G737_BODIES = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_BODY_WORKING_CANDIDATES.tsv"
G737_UPDATE = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/TRANSFER_MODEL_UPDATE.tsv"
G769_CORE = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/src/core_atlas.py"
SPECS = SRC / "MEDIAL_RIGHT_WHOLE_SPECS.tsv"
MANIFEST = EXP / "experiment.json"

FIXED_13 = frozenset({
    "chy", "chey", "cheey", "chdy", "chedy", "sheey", "shedy",
    "aiin", "daiin", "kaiin", "okaiin", "oiin", "olaiin",
})
HISTORY_IDS = ("HSR008", "HSR010", "HSR012", "HSR013", "HSR017")
EXPECTED_OUTPUTS = frozenset({
    "TARGET_183_MEDIAL_EDGE_ATLAS.tsv", "H34_452_MEDIAL_CONTROL_EDGE_ATLAS.tsv",
    "H34_VECTOR_COMPARISON.tsv", "H34_MATCH_STRATUM_COVERAGE.tsv",
    "H34_RECURRENT_25_WHOLE_PROFILES.tsv", "H34_TARGET_DROP_SENSITIVITY.tsv",
    "H34_SHARED_BODY_AUDIT.tsv", "GDT776_376_RENDERER.tsv",
    "GDT776_WORKING_DICTIONARY.tsv", "GDT776_PASSAGE_PATCHES.tsv",
    "HISTORICAL_FIELD_BRIDGE.tsv", "GDT776_GDT388_RELATION_PACKET.tsv",
    "GDT776_RELATION_EDGE_CROSSWALK.tsv", "RELATION_PACKET_INTAKE.json", "RESULT.json",
})
FLOAT_TOLERANCE = 5e-8


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    if match is None:
        raise AssertionError(page)
    return match.group(1)


def cosine(first: Mapping[str, float], second: Mapping[str, float]) -> float:
    keys = set(first) | set(second)
    numerator = sum(float(first.get(key, 0)) * float(second.get(key, 0)) for key in keys)
    left = math.sqrt(sum(float(value) ** 2 for value in first.values()))
    right = math.sqrt(sum(float(value) ** 2 for value in second.values()))
    return numerator / (left * right) if left and right else 0.0


def vector(rows: Sequence[Mapping[str, object]]) -> Counter[str]:
    return Counter(str(row["right_surface"]) for row in rows)


def equalized_vector(rows: Sequence[Mapping[str, object]], key: str) -> Counter[str]:
    groups: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        groups[str(row[key])].append(row)
    output: Counter[str] = Counter()
    for material in groups.values():
        for row in material:
            output[str(row["right_surface"])] += 1 / len(groups) / len(material)
    return output


def class_winner(h3: float, h4: float) -> str:
    if abs(h4 - h3) < 1e-12:
        return "TIE"
    return "H4" if h4 > h3 else "H3"


def stratum(row: Mapping[str, object]) -> tuple[str, int]:
    return str(row["register_id"]), int(row["predecessor_ordinal"])


def compare_fields(
    check: Callable[[bool, str], None], actual: Mapping[str, str], expected: Mapping[str, object],
    label: str, float_fields: Iterable[str] = (),
) -> None:
    numeric = set(float_fields)
    for field, value in expected.items():
        if field not in actual:
            check(False, f"{label} missing field {field}")
        elif field in numeric:
            try:
                valid = abs(float(actual[field]) - float(value)) <= FLOAT_TOLERANCE
            except ValueError:
                valid = False
            check(valid, f"{label} differs: {field}")
        else:
            check(actual[field] == str(value), f"{label} differs: {field}")


def declared_outputs() -> tuple[str, ...]:
    """Read the runner's literal output contract without importing it."""
    tree = ast.parse(RUN.read_text(encoding="utf-8"))
    assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "outputs" for target in node.targets)]
    if len(assignments) != 1 or not isinstance(assignments[0].value, (ast.List, ast.Tuple)):
        raise AssertionError("runner outputs declaration not uniquely readable")
    names: list[str] = []
    for element in assignments[0].value.elts:
        if not isinstance(element, ast.Tuple) or not element.elts:
            raise AssertionError("runner output row is not a tuple")
        name = ast.literal_eval(element.elts[0])
        if not isinstance(name, str):
            raise AssertionError("runner output name is not literal")
        names.append(name)
    json_calls: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "write_json" or not node.args:
            continue
        path = node.args[0]
        if (isinstance(path, ast.BinOp) and isinstance(path.op, ast.Div)
                and isinstance(path.left, ast.Name) and path.left.id == "artifacts"
                and isinstance(path.right, ast.Constant) and isinstance(path.right.value, str)):
            json_calls.append((node.lineno, path.right.value))
    names.extend(name for _line, name in sorted(json_calls))
    if len(names) != len(set(names)):
        raise AssertionError("duplicate runner output name")
    return tuple(names)


def renderer_predicate_leaks() -> list[str]:
    """Occurrence IDs and literal loci may be carried, but not used to dispatch."""
    source = RUN.read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "build_renderer"]
    if len(functions) != 1:
        return ["build_renderer not uniquely found"]
    predicates: list[ast.AST] = []
    for node in ast.walk(functions[0]):
        if isinstance(node, (ast.If, ast.IfExp, ast.While)):
            predicates.append(node.test)
        elif isinstance(node, ast.comprehension):
            predicates.extend(node.ifs)
    leaks: list[str] = []
    for predicate in predicates:
        text = ast.get_source_segment(source, predicate) or ast.dump(predicate)
        if "occurrence_id" in text or re.search(r"['\"]f(?:\d+|Ros)[rv]?\d*\.", text):
            leaks.append(text)
    return leaks


def standardized_vectors(
    target: Sequence[Mapping[str, object]], controls: Sequence[Mapping[str, object]],
) -> tuple[list[Mapping[str, object]], dict[str, list[Mapping[str, object]]], dict[str, Counter[str]], set[tuple[str, int]]]:
    target_counts = Counter(stratum(row) for row in target)
    common = set(target_counts)
    for head in ("H3", "H4"):
        common &= {stratum(row) for row in controls if row["head_id"] == head}
    target_view = [row for row in target if stratum(row) in common]
    by_head: dict[str, list[Mapping[str, object]]] = {}
    vectors: dict[str, Counter[str]] = {}
    for head in ("H3", "H4"):
        material = [row for row in controls if row["head_id"] == head and stratum(row) in common]
        by_head[head] = material
        capacity = Counter(stratum(row) for row in material)
        output: Counter[str] = Counter()
        for row in material:
            output[str(row["right_surface"])] += target_counts[stratum(row)] / capacity[stratum(row)]
        vectors[head] = output
    return target_view, by_head, vectors, common


def strict_vectors(
    target: Sequence[Mapping[str, object]], controls: Sequence[Mapping[str, object]],
) -> tuple[list[Mapping[str, object]], dict[str, list[Mapping[str, object]]], dict[str, Counter[str]], set[tuple[str, str, int]]]:
    target_counts = Counter(stratum(row) for row in target)
    cell = lambda row: (str(row["body"]), str(row["register_id"]), int(row["predecessor_ordinal"]))
    cells = {cell(row) for row in controls if row["head_id"] == "H3"}
    cells &= {cell(row) for row in controls if row["head_id"] == "H4"}
    cells = {key for key in cells if target_counts[(key[1], key[2])]}
    shared_strata = {(key[1], key[2]) for key in cells}
    target_view = [row for row in target if stratum(row) in shared_strata]
    cells_per_stratum = Counter((key[1], key[2]) for key in cells)
    by_head: dict[str, list[Mapping[str, object]]] = {}
    vectors: dict[str, Counter[str]] = {}
    for head in ("H3", "H4"):
        material = [row for row in controls if row["head_id"] == head and cell(row) in cells]
        by_head[head] = material
        grouped: defaultdict[tuple[str, str, int], list[Mapping[str, object]]] = defaultdict(list)
        for row in material:
            grouped[cell(row)].append(row)
        output: Counter[str] = Counter()
        for key, group in grouped.items():
            allocation = target_counts[(key[1], key[2])] / cells_per_stratum[(key[1], key[2])]
            for row in group:
                output[str(row["right_surface"])] += allocation / len(group)
        vectors[head] = output
    return target_view, by_head, vectors, cells


def view_expectation(
    view_id: str, view_class: str, target: Sequence[Mapping[str, object]],
    h3: Sequence[Mapping[str, object]], h4: Sequence[Mapping[str, object]],
    v3: Mapping[str, float], v4: Mapping[str, float], **metadata: object,
) -> dict[str, object]:
    target_vector = vector(target)
    c3, c4 = cosine(target_vector, v3), cosine(target_vector, v4)
    return {
        "view_id": view_id, "view_class": view_class, "target_edges": len(target),
        "target_right_types": len(target_vector), "target_vector_mass": sum(target_vector.values()),
        "h3_edges": len(h3), "h3_predecessor_surfaces": len({row["predecessor_surface"] for row in h3}),
        "h3_bodies": len({row["body"] for row in h3}), "h3_vector_mass": sum(v3.values()),
        "h4_edges": len(h4), "h4_predecessor_surfaces": len({row["predecessor_surface"] for row in h4}),
        "h4_bodies": len({row["body"] for row in h4}), "h4_vector_mass": sum(v4.values()),
        "shared_registers": metadata.get("shared_registers", "NA"),
        "shared_strata": metadata.get("shared_strata", "NA"),
        "shared_bodies": metadata.get("shared_bodies", "NA"), "shared_cells": metadata.get("shared_cells", "NA"),
        "cosine_h3": c3, "cosine_h4": c4, "delta_h4_minus_h3": c4 - c3,
        "winner": class_winner(c3, c4), "label_swap_status": metadata.get("label_swap_status", "NOT_APPLICABLE"),
        "interpretive_scope": "STRUCTURAL_HEURISTIC_ONLY__NO_FIELD_OPERATOR_OR_SEMANTIC_IDENTITY",
        "component_export_credit": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    args = parser.parse_args()
    artifacts = args.artifacts_dir if args.artifacts_dir.is_absolute() else ROOT / args.artifacts_dir
    checks = 0
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(message)

    outputs = declared_outputs()
    check(frozenset(outputs) == EXPECTED_OUTPUTS and len(outputs) == 15, "runner output contract differs")
    for name in outputs:
        check((artifacts / name).is_file(), f"missing runner artifact {name}")
    check(REPORT.is_file(), "missing report")

    locks = read_tsv(SRC / "SOURCE_LOCK.tsv")
    check(len(locks) == 14 and len({row["path"] for row in locks}) == 14, "source lock row set differs")
    for row in locks:
        relative = Path(row["path"])
        check(not relative.is_absolute() and ".." not in relative.parts, f"unsafe lock path {relative}")
        full = ROOT / relative
        check(full.is_file(), f"missing locked source {relative}")
        if full.is_file():
            check(sha256(full) == row["expected_sha256"], f"source hash differs {relative}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT776", "manifest experiment id differs")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed flags differ")
    check(renderer_predicate_leaks() == [], "occurrence-id or literal-locus renderer predicate found")
    policy_text = SPECS.read_text(encoding="utf-8")
    check(not re.search(r"\bf(?:\d+|Ros)[rv]?\d*\.", policy_text), "hand-picked locus leaked into candidate policy")
    check("G769-T" not in policy_text and "G776-T" not in policy_text, "occurrence id leaked into candidate policy")

    specs = read_tsv(SPECS)
    spec_by = {row["surface"]: row for row in specs}
    check(len(specs) == len(spec_by) == 25, "25-whole candidate deck differs")
    check(all(row["component_export_credit"] == "0" for row in specs), "component credit in candidate deck")
    check(all(row["positive_evidence"] and row["counterevidence"] and row["candidate_confidence"] for row in specs),
          "candidate evidence/confidence is incomplete")
    active_fields = ("candidate_whole_de", "field_renderer_de", "semantic_family", "historical_field_type")
    forbidden_by_surface = {
        "r": re.compile(r"\b(?:root|radix|wurzel\w*)\b", re.I),
        "s": re.compile(r"\b(?:seed|semen|samen\w*|saat\w*)\b", re.I),
        "ol": re.compile(r"\b(?:oil|oleum|öl)\b", re.I),
    }
    for surface, pattern in forbidden_by_surface.items():
        active = " ".join(spec_by[surface][field] for field in active_fields)
        check(pattern.search(active) is None, f"retired {surface} identity in active candidate fields")
    check("no root" in spec_by["r"]["counterevidence"].lower(), "r/root rejection not explicit")
    check("seed" in spec_by["s"]["counterevidence"].lower() and "forbidden" in spec_by["s"]["counterevidence"].lower(),
          "s/seed rejection not explicit")

    training = read_tsv(G736_GRID)
    held = read_tsv(G737_FORMS)
    registry: dict[str, dict[str, str]] = {}
    for source, rows in (("GDT736_TRAINING", training), ("GDT737_HELD", held)):
        for row in rows:
            form = row["form"]
            check(form not in registry, f"duplicate H registry form {form}")
            registry[form] = {
                "head_id": row["opaque_head_id"], "body": row["body"], "registry_source": source,
                "record_role": row.get("selected_formal_role", row.get("gdt736_training_record_role", "OPEN")),
                "body_role_de": row.get("revised_body_role_de", row.get("exploratory_body_candidate_de", "offen")),
            }
    check(len(registry) == 369, "H1-H4 registry size differs")
    check(Counter(row["head_id"] for row in registry.values()) == {"H1": 89, "H2": 95, "H3": 75, "H4": 110},
          "H1-H4 registry class sizes differ")
    check(all(row.get("component_export_credit") == "0" for row in training + held), "component credit in H registry")
    held_bodies = {row["body"] for row in read_tsv(G737_BODIES)}
    training_bodies = {row["body"] for row in training}
    check({"aiin", "chedy", "ol", "cheey", "chey", "shedy", "al", "chdy", "oiin", "or", "shey"} <= training_bodies,
          "GDT736 candidate provenance differs")
    check({"kaiin", "sheey", "daiin", "okaiin", "olaiin", "r", "olor"} <= held_bodies,
          "GDT737 candidate provenance differs")
    transfer = {row["claim_id"]: row for row in read_tsv(G737_UPDATE)}
    check(transfer["C03"]["new_live_status"] == "RETAIN_AS_RELATIVE_POSITION_SUBROLES", "H3/H4 transfer status differs")

    core = load_module("gdt769_core_for_gdt776_validator", G769_CORE)
    _g764, environment = core.load_guarded_environment(ROOT)
    check(dict(environment["guard"]) == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150},
          "guarded cache counts differ")
    context = environment["context"]
    check(not any(str(token["page"]).startswith("f84") for line in context.by_line.values() for token in line),
          "sealed page materialized in guarded cache")
    core_registry = environment["head_registry"]
    check(set(core_registry) == set(registry), "guarded H registry form set differs")
    for form, expected in registry.items():
        check(all(str(core_registry[form][field]) == value for field, value in expected.items()),
              f"guarded H registry metadata differs {form}")

    source_atlas = read_tsv(G775_ATLAS)
    selected_source = [row for row in source_atlas if row["novel_305_member"] == "1"
                       and row["right_reader_exact"] == "1" and int(row["ordinal"]) > 1
                       and int(row["ordinal"]) < len(row["written_line_eva"].split())]
    selected_source.sort(key=lambda row: (row["page"], row["locus"], int(row["ordinal"])))
    target_frequency = Counter(row["right_surface"] for row in selected_source)
    recurrent = {surface for surface, count in target_frequency.items() if count >= 2}
    check(len(selected_source) == 183, "target183 differs")
    check(len(target_frequency) == 119, "target right-type count differs")
    check(len(recurrent) == 25 and sum(target_frequency[surface] for surface in recurrent) == 89,
          "25 recurrent / 89 target count differs")
    check(recurrent == set(spec_by), "recurrent target set differs from fixed specs")

    target_expected: list[dict[str, object]] = []
    target_by_key: dict[tuple[str, str, int, str], dict[str, object]] = {}
    for number, source in enumerate(selected_source, 1):
        locus, ordinal = source["locus"], int(source["ordinal"])
        line = context.by_line[locus]
        left, right = line[ordinal - 1], line[ordinal]
        check(str(left["eva"]) == "ol" and str(right["eva"]) == source["right_surface"],
              f"target cache binding differs {source['target_occurrence_id']}")
        check(bool(context.exact[(locus, int(left["token_index"]))]) and bool(context.exact[(locus, int(right["token_index"]))]),
              f"target exactness differs {source['target_occurrence_id']}")
        expected = {
            "target_edge_id": f"G776-T{number:04d}", "source_target_occurrence_id": source["target_occurrence_id"],
            "page": source["page"], "physical_folio": source["physical_folio"], "locus": locus,
            "section": source["section"], "language": source["language"], "hand": source["hand"],
            "register_id": source["register_id"], "predecessor_ordinal": ordinal, "right_ordinal": ordinal + 1,
            "predecessor_surface": "ol", "right_surface": source["right_surface"],
            "predecessor_reader_exact": 1, "right_reader_exact": 1, "medial_predecessor": 1,
            "general_target_eligible": 1, "right_target_frequency": target_frequency[source["right_surface"]],
            "recurrent_25_member": int(source["right_surface"] in recurrent),
            "selection_rule": "NOVEL_305_AND_EXACT_RIGHT_AND_ORDINAL_GT_1_AND_NOT_LINE_FINAL",
            "written_line_eva": source["written_line_eva"], "score_eligible": 0, "component_export_credit": 0,
        }
        target_expected.append(expected)
        target_by_key[(source["page"], locus, ordinal, source["right_surface"])] = expected

    target_artifact = read_tsv(artifacts / "TARGET_183_MEDIAL_EDGE_ATLAS.tsv")
    check(len(target_artifact) == 183 and len({row["target_edge_id"] for row in target_artifact}) == 183,
          "target artifact row/id count differs")
    for actual, expected in zip(target_artifact, target_expected):
        compare_fields(check, actual, expected, f"target {expected['target_edge_id']}")

    all_exact = medial_exact = 0
    controls_expected: list[dict[str, object]] = []
    for locus in sorted(context.by_line):
        line = context.by_line[locus]
        written = " ".join(str(token["eva"]) for token in line)
        for index, (left, right) in enumerate(zip(line, line[1:])):
            if not context.exact[(locus, int(left["token_index"]))] or not context.exact[(locus, int(right["token_index"]))]:
                continue
            all_exact += 1
            medial_exact += int(index > 0)
            surface = str(left["eva"])
            meta = registry.get(surface)
            if index == 0 or meta is None or meta["head_id"] not in {"H3", "H4"}:
                continue
            page = str(left["page"])
            controls_expected.append({
                "page": page, "physical_folio": physical_folio(page), "locus": locus,
                "section": str(left["section"]), "language": str(left["language"]), "hand": str(left["hand"]),
                "register_id": f"{left['section']}|{left['language']}|{left['hand']}",
                "predecessor_ordinal": index + 1, "right_ordinal": index + 2,
                "predecessor_surface": surface, "right_surface": str(right["eva"]),
                "predecessor_reader_exact": 1, "right_reader_exact": 1, "predecessor_line_position": "MIDDLE",
                **meta, "medial_predecessor": 1,
                "selection_rule": "REGISTERED_H3_OR_H4_AND_BOTH_TOKENS_EXACT_AND_ORDINAL_GT_1_AND_NOT_LINE_FINAL",
                "written_line_eva": written, "score_eligible": 0, "component_export_credit": 0,
            })
    controls_expected.sort(key=lambda row: (str(row["page"]), str(row["locus"]), int(row["predecessor_ordinal"]), str(row["head_id"])))
    for number, row in enumerate(controls_expected, 1):
        row["control_edge_id"] = f"G776-C{number:04d}"
        row["control_cohort"] = f"{row['head_id']}_MEDIAL_EXACT_OUTGOING"
    control_counts = Counter(str(row["head_id"]) for row in controls_expected)
    check((all_exact, medial_exact) == (16657, 14320), "exact bigram universe differs")
    check(control_counts == {"H3": 102, "H4": 350}, "H3=102/H4=350 control counts differ")
    check(len({row["predecessor_surface"] for row in controls_expected if row["head_id"] == "H3"}) == 31,
          "active H3 predecessor count differs")
    check(len({row["predecessor_surface"] for row in controls_expected if row["head_id"] == "H4"}) == 68,
          "active H4 predecessor count differs")

    control_artifact = read_tsv(artifacts / "H34_452_MEDIAL_CONTROL_EDGE_ATLAS.tsv")
    check(len(control_artifact) == 452 and len({row["control_edge_id"] for row in control_artifact}) == 452,
          "control artifact row/id count differs")
    for actual, expected in zip(control_artifact, controls_expected):
        compare_fields(check, actual, expected, f"control {expected['control_edge_id']}")

    by_head = {head: [row for row in controls_expected if row["head_id"] == head] for head in ("H3", "H4")}
    target_rows: Sequence[Mapping[str, object]] = target_expected
    view_rows: list[dict[str, object]] = []
    view_rows.append(view_expectation("RAW_POOLED", "PRIMARY", target_rows, by_head["H3"], by_head["H4"],
                                      vector(by_head["H3"]), vector(by_head["H4"])))
    view_rows.append(view_expectation("PREDECESSOR_SURFACE_EQUALIZED", "PRIMARY", target_rows, by_head["H3"], by_head["H4"],
                                      equalized_vector(by_head["H3"], "predecessor_surface"),
                                      equalized_vector(by_head["H4"], "predecessor_surface")))
    shared_registers = {str(row["register_id"]) for row in target_rows}
    for head in ("H3", "H4"):
        shared_registers &= {str(row["register_id"]) for row in by_head[head]}
    register_target = [row for row in target_rows if row["register_id"] in shared_registers]
    register_control = {head: [row for row in by_head[head] if row["register_id"] in shared_registers] for head in ("H3", "H4")}
    view_rows.append(view_expectation("SHARED_REGISTER_RAW", "MATCHED", register_target,
                                      register_control["H3"], register_control["H4"], vector(register_control["H3"]),
                                      vector(register_control["H4"]), shared_registers=len(shared_registers)))
    standard_target, standard_control, standard_vector, common_strata = standardized_vectors(target_rows, controls_expected)
    view_rows.append(view_expectation("REGISTER_ORDINAL_STANDARDIZED", "PRIMARY_MATCHED", standard_target,
                                      standard_control["H3"], standard_control["H4"], standard_vector["H3"],
                                      standard_vector["H4"], shared_strata=len(common_strata)))
    shared_bodies = {str(row["body"]) for row in by_head["H3"]} & {str(row["body"]) for row in by_head["H4"]}
    shared_control = {head: [row for row in by_head[head] if row["body"] in shared_bodies] for head in ("H3", "H4")}
    view_rows.append(view_expectation("SHARED_BODY_RAW", "SENSITIVITY", target_rows,
                                      shared_control["H3"], shared_control["H4"], vector(shared_control["H3"]),
                                      vector(shared_control["H4"]), shared_bodies=len(shared_bodies)))
    view_rows.append(view_expectation("SHARED_BODY_EQUALIZED", "SENSITIVITY", target_rows,
                                      shared_control["H3"], shared_control["H4"],
                                      equalized_vector(shared_control["H3"], "body"),
                                      equalized_vector(shared_control["H4"], "body"), shared_bodies=len(shared_bodies)))
    strict_target, strict_control, strict_vector, strict_cells = strict_vectors(target_rows, controls_expected)
    view_rows.append(view_expectation("STRICT_BODY_REGISTER_ORDINAL_CAPACITY", "STRICT_SENSITIVITY", strict_target,
                                      strict_control["H3"], strict_control["H4"], strict_vector["H3"], strict_vector["H4"],
                                      shared_strata=len({(cell[1], cell[2]) for cell in strict_cells}),
                                      shared_bodies=len({cell[0] for cell in strict_cells}), shared_cells=len(strict_cells),
                                      label_swap_status="MATCHED_CELL_LABEL_SWAP_NOT_SEPARATING"))
    no_o = {head: [row for row in by_head[head] if not str(row["body"]).startswith("o")] for head in ("H3", "H4")}
    view_rows.append(view_expectation("SYMMETRIC_NO_O_BODY_RAW", "ABLATION", target_rows,
                                      no_o["H3"], no_o["H4"], vector(no_o["H3"]), vector(no_o["H4"])))
    view_rows.append(view_expectation("SYMMETRIC_NO_O_BODY_SURFACE_EQUALIZED", "ABLATION", target_rows,
                                      no_o["H3"], no_o["H4"], equalized_vector(no_o["H3"], "predecessor_surface"),
                                      equalized_vector(no_o["H4"], "predecessor_surface")))
    for row in view_rows:
        row["reversal_vs_raw"] = int(row["winner"] not in {view_rows[0]["winner"], "TIE"})
    expected_views = {str(row["view_id"]): row for row in view_rows}
    observed_views = {row["view_id"]: row for row in read_tsv(artifacts / "H34_VECTOR_COMPARISON.tsv")}
    check(len(observed_views) == len(expected_views) == 9, "vector view set differs")
    view_float_fields = {"target_vector_mass", "h3_vector_mass", "h4_vector_mass", "cosine_h3", "cosine_h4", "delta_h4_minus_h3"}
    for view_id, expected in expected_views.items():
        check(view_id in observed_views, f"missing vector view {view_id}")
        if view_id in observed_views:
            compare_fields(check, observed_views[view_id], expected, f"vector view {view_id}", view_float_fields)
    check(len(shared_bodies) == 18, "18 active shared bodies differ")
    check(expected_views["SHARED_BODY_RAW"]["winner"] == "H4" and expected_views["SHARED_BODY_EQUALIZED"]["winner"] == "H3",
          "shared-body equalization reversal differs")
    check(expected_views["RAW_POOLED"]["winner"] == expected_views["PREDECESSOR_SURFACE_EQUALIZED"]["winner"]
          == expected_views["REGISTER_ORDINAL_STANDARDIZED"]["winner"] == "H4", "primary H4 structural lead differs")
    check(len(common_strata) == 23 and len(standard_target) == 133 and len(strict_cells) == 13
          and len({cell[0] for cell in strict_cells}) == 9 and len(strict_target) == 73,
          "matched/strict capacity counts differ")

    target_strata = Counter(stratum(row) for row in target_rows)
    cells_per_stratum = Counter((cell[1], cell[2]) for cell in strict_cells)
    coverage_expected: list[dict[str, object]] = []
    for register, ordinal in sorted(target_strata):
        h3 = [row for row in by_head["H3"] if stratum(row) == (register, ordinal)]
        h4 = [row for row in by_head["H4"] if stratum(row) == (register, ordinal)]
        coverage_expected.append({
            "coverage_level": "REGISTER_ORDINAL_STRATUM", "body": "ALL", "register_id": register,
            "predecessor_ordinal": ordinal, "target_stratum_edges": target_strata[(register, ordinal)],
            "h3_edges": len(h3), "h4_edges": len(h4), "shared_all_three": int(bool(h3 and h4)),
            "strict_cell_count_in_stratum": cells_per_stratum[(register, ordinal)],
            "allocated_target_mass": target_strata[(register, ordinal)] if h3 and h4 else 0,
            "score_eligible": 0, "component_export_credit": 0,
        })
    cell_key = lambda row: (str(row["body"]), str(row["register_id"]), int(row["predecessor_ordinal"]))
    for body, register, ordinal in sorted(strict_cells):
        coverage_expected.append({
            "coverage_level": "STRICT_SHARED_BODY_CELL", "body": body, "register_id": register,
            "predecessor_ordinal": ordinal, "target_stratum_edges": target_strata[(register, ordinal)],
            "h3_edges": sum(cell_key(row) == (body, register, ordinal) for row in by_head["H3"]),
            "h4_edges": sum(cell_key(row) == (body, register, ordinal) for row in by_head["H4"]),
            "shared_all_three": 1, "strict_cell_count_in_stratum": cells_per_stratum[(register, ordinal)],
            "allocated_target_mass": target_strata[(register, ordinal)] / cells_per_stratum[(register, ordinal)],
            "score_eligible": 0, "component_export_credit": 0,
        })
    coverage_artifact = read_tsv(artifacts / "H34_MATCH_STRATUM_COVERAGE.tsv")
    check(len(coverage_artifact) == len(coverage_expected) == 69, "56-strata plus 13-cell coverage rows differ")
    for actual, expected in zip(coverage_artifact, coverage_expected):
        compare_fields(check, actual, expected,
                       f"coverage {expected['coverage_level']}:{expected['body']}:{expected['register_id']}:{expected['predecessor_ordinal']}",
                       {"allocated_target_mass"})

    shared_audit = {row["body"]: row for row in read_tsv(artifacts / "H34_SHARED_BODY_AUDIT.tsv")}
    check(len(shared_audit) == 18 and set(shared_audit) == shared_bodies, "shared-body audit row set differs")
    target_vector = vector(target_rows)
    for body in sorted(shared_bodies):
        selected = {head: [row for row in shared_control[head] if row["body"] == body] for head in ("H3", "H4")}
        expected = {
            "body": body, "starts_o": int(body.startswith("o")),
            "h3_forms": "|".join(sorted({str(row["predecessor_surface"]) for row in selected["H3"]})),
            "h4_forms": "|".join(sorted({str(row["predecessor_surface"]) for row in selected["H4"]})),
            "h3_edges": len(selected["H3"]), "h4_edges": len(selected["H4"]),
            "h3_right_types": len({row["right_surface"] for row in selected["H3"]}),
            "h4_right_types": len({row["right_surface"] for row in selected["H4"]}),
            "h3_cosine_to_target": cosine(target_vector, vector(selected["H3"])),
            "h4_cosine_to_target": cosine(target_vector, vector(selected["H4"])),
            "strict_shared_cells": sum(cell[0] == body for cell in strict_cells),
            "body_equalization_weight": 1 / 18, "semantic_identity_credit": 0, "component_export_credit": 0,
        }
        compare_fields(check, shared_audit[body], expected, f"shared body {body}",
                       {"h3_cosine_to_target", "h4_cosine_to_target", "body_equalization_weight"})

    drop_sets = (
        ("BASELINE", frozenset()), ("DROP_DAIIN", frozenset({"daiin"})), ("DROP_FIXED_13", FIXED_13),
        ("DROP_NEW_10", frozenset(row["surface"] for row in specs if row["existing_gdt775_selected"] == "0")),
        ("DROP_RECURRENT_25", frozenset(recurrent)),
    )
    raw_vectors = {head: vector(by_head[head]) for head in ("H3", "H4")}
    surface_vectors = {head: equalized_vector(by_head[head], "predecessor_surface") for head in ("H3", "H4")}
    drop_expected: list[dict[str, object]] = []
    for scenario, dropped in drop_sets:
        material = [row for row in target_rows if row["right_surface"] not in dropped]
        tv = vector(material)
        raw = {head: cosine(tv, raw_vectors[head]) for head in ("H3", "H4")}
        equal = {head: cosine(tv, surface_vectors[head]) for head in ("H3", "H4")}
        starget, _scontrol, svectors, common = standardized_vectors(material, controls_expected)
        stv = vector(starget)
        standard = {head: cosine(stv, svectors[head]) for head in ("H3", "H4")}
        drop_expected.append({
            "scenario": scenario, "dropped_surfaces": "|".join(sorted(dropped)) if dropped else "NONE",
            "removed_target_edges": 183 - len(material), "remaining_target_edges": len(material),
            "remaining_target_right_types": len(tv), "common_register_ordinal_strata": len(common),
            "standardized_target_edges": len(starget), "raw_cosine_h3": raw["H3"], "raw_cosine_h4": raw["H4"],
            "raw_delta_h4_minus_h3": raw["H4"] - raw["H3"], "raw_winner": class_winner(raw["H3"], raw["H4"]),
            "surface_equalized_cosine_h3": equal["H3"], "surface_equalized_cosine_h4": equal["H4"],
            "surface_equalized_delta_h4_minus_h3": equal["H4"] - equal["H3"],
            "surface_equalized_winner": class_winner(equal["H3"], equal["H4"]),
            "standardized_cosine_h3": standard["H3"], "standardized_cosine_h4": standard["H4"],
            "standardized_delta_h4_minus_h3": standard["H4"] - standard["H3"],
            "standardized_winner": class_winner(standard["H3"], standard["H4"]),
            "semantic_identity_credit": 0, "component_export_credit": 0,
        })
    drop_artifact = {row["scenario"]: row for row in read_tsv(artifacts / "H34_TARGET_DROP_SENSITIVITY.tsv")}
    check(len(drop_artifact) == 5, "target-drop scenario count differs")
    drop_float_fields = {"raw_cosine_h3", "raw_cosine_h4", "raw_delta_h4_minus_h3",
                         "surface_equalized_cosine_h3", "surface_equalized_cosine_h4",
                         "surface_equalized_delta_h4_minus_h3", "standardized_cosine_h3",
                         "standardized_cosine_h4", "standardized_delta_h4_minus_h3"}
    for expected in drop_expected:
        check(expected["scenario"] in drop_artifact, f"missing drop scenario {expected['scenario']}")
        if expected["scenario"] in drop_artifact:
            compare_fields(check, drop_artifact[str(expected["scenario"])], expected,
                           f"drop {expected['scenario']}", drop_float_fields)
    check(drop_expected[2]["surface_equalized_winner"] == "H3"
          and all(row["raw_winner"] == "H4" for row in drop_expected), "target-drop sensitivity/reversal differs")

    g734_by: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(G734):
        g734_by[row["surface"]].append(row)
    profile_artifact = {row["surface"]: row for row in read_tsv(artifacts / "H34_RECURRENT_25_WHOLE_PROFILES.tsv")}
    check(len(profile_artifact) == 25 and set(profile_artifact) == recurrent, "25-whole profile set differs")
    raw = {head: vector(by_head[head]) for head in ("H3", "H4")}
    surface = {head: equalized_vector(by_head[head], "predecessor_surface") for head in ("H3", "H4")}

    def rank_for(word: str, values: Mapping[str, float]) -> int:
        value = float(values.get(word, 0))
        return 1 + sum(float(other) > value for other in values.values()) if value else 0

    for spec in specs:
        word = spec["surface"]
        occurrences = [row for row in target_rows if row["right_surface"] == word]
        h3_share, h4_share = raw["H3"][word] / 102, raw["H4"][word] / 350
        profile = "UNSEEN_IN_H3_H4"
        if h3_share or h4_share:
            profile = "H4_ENRICHED" if h4_share > h3_share else "H3_ENRICHED" if h3_share > h4_share else "TIED"
        same_cards = g734_by[word]
        card_matches = [row for row in same_cards if row["v99r7_spoken_default_de"] == spec["expected_source_default_de"]
                        and row["working_model_level"] == spec["expected_source_level"]]
        check(len(card_matches) == 1, f"GDT734 expected whole-card binding differs {word}")
        expected = {
            "surface": word, "target_occurrences": len(occurrences), "target_pages": len({row["page"] for row in occurrences}),
            "target_physical_folios": len({row["physical_folio"] for row in occurrences}),
            "target_registers": "|".join(sorted({str(row["register_id"]) for row in occurrences})),
            "h3_right_count": raw["H3"][word], "h4_right_count": raw["H4"][word],
            "h3_right_share": h3_share, "h4_right_share": h4_share, "h4_minus_h3_share": h4_share - h3_share,
            "h3_raw_rank": rank_for(word, raw["H3"]), "h4_raw_rank": rank_for(word, raw["H4"]),
            "h3_surface_equalized_mass": surface["H3"][word], "h4_surface_equalized_mass": surface["H4"][word],
            "h3_standardized_mass": standard_vector["H3"][word], "h4_standardized_mass": standard_vector["H4"][word],
            "contact_profile": profile,
            "h3_active_predecessor_forms_with_same_body": "|".join(sorted({str(row["predecessor_surface"]) for row in by_head["H3"] if row["body"] == word})) or "NONE",
            "h4_active_predecessor_forms_with_same_body": "|".join(sorted({str(row["predecessor_surface"]) for row in by_head["H4"] if row["body"] == word})) or "NONE",
            **{field: spec[field] for field in ("semantic_family", "candidate_whole_de", "field_renderer_de", "candidate_confidence",
                                                "positive_evidence", "counterevidence", "candidate_source", "expected_source_default_de")},
            "gdt734_expected_card_default_de": spec["expected_source_default_de"],
            "gdt734_same_surface_card_count": len(same_cards),
            "gdt734_same_surface_defaults": " || ".join(sorted({row["v99r7_spoken_default_de"] for row in same_cards})),
            "expected_source_default_matches_gdt734": 1, "existing_gdt775_selected": int(spec["existing_gdt775_selected"]),
            "consume_right_token": int(spec["consume_right_token"]), "scope_status": spec["scope_status"],
            "historical_field_type": spec["historical_field_type"], "default_is_translation": 0,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        }
        compare_fields(check, profile_artifact[word], expected, f"profile {word}",
                       {"h3_right_share", "h4_right_share", "h4_minus_h3_share", "h3_surface_equalized_mass",
                        "h4_surface_equalized_mass", "h3_standardized_mass", "h4_standardized_mass"})

    source_renderer = read_tsv(G775_RENDERER)
    renderer = read_tsv(artifacts / "GDT776_376_RENDERER.tsv")
    check(len(source_renderer) == len(renderer) == 376, "renderer376 differs")
    check(len({row["target_occurrence_id"] for row in renderer}) == 376, "renderer occurrence ids are not unique")
    sequence = selected_count = refined_count = new_count = 0
    for source, actual in zip(source_renderer, renderer):
        for field, value in source.items():
            check(actual.get(field) == value, f"renderer did not preserve GDT775 {source['target_occurrence_id']}:{field}")
        key = (source["page"], source["locus"], int(source["ordinal"]), source["right_surface"])
        selected = key in target_by_key and source["right_surface"] in spec_by
        spec = spec_by.get(source["right_surface"]) if selected else None
        if spec is None:
            expected = {
                "gdt776_branch": "INHERITED_GDT775", "gdt776_default_de": source["throughput_renderer_default_de"],
                "gdt776_renderer_contextual": source["throughput_renderer_contextual"],
                "gdt776_span_consumes_right_token": source["throughput_span_consumes_right_token"],
                "gdt776_span_id": source["throughput_span_id"], "gdt776_right_whole": source["right_surface"],
                "gdt776_candidate_whole_de": "NONE", "gdt776_semantic_family": "NONE",
                "gdt776_confidence": source["construction_confidence"], "gdt776_positive_evidence": "INHERITED_GDT775",
                "gdt776_counterevidence": "INHERITED_GDT775", "gdt776_scope_status": "INHERITED_GDT775",
                "gdt776_dispatch_rule": "INHERITED_GDT775", "gdt776_structural_bridge": "NONE",
                "gdt776_refined_existing_target": 0, "gdt776_new_contextual_target": 0,
            }
        else:
            selected_count += 1
            sequence += 1
            existing, consumes = int(spec["existing_gdt775_selected"]), int(spec["consume_right_token"])
            refined_count += existing
            new_count += 1 - existing
            branch = "GDT776_MEDIAL_RIGHT_WHOLE_REFINED" if existing else \
                     "GDT776_MEDIAL_RIGHT_WHOLE_EXTENSION" if consumes else "GDT776_MEDIAL_OL_CHAIN"
            expected = {
                "gdt776_branch": branch, "gdt776_default_de": spec["field_renderer_de"],
                "gdt776_renderer_contextual": 1, "gdt776_span_consumes_right_token": consumes,
                "gdt776_span_id": f"G776-{'SPAN' if consumes else 'CHAIN'}-{sequence:03d}",
                "gdt776_right_whole": source["right_surface"], "gdt776_candidate_whole_de": spec["candidate_whole_de"],
                "gdt776_semantic_family": spec["semantic_family"], "gdt776_confidence": spec["candidate_confidence"],
                "gdt776_positive_evidence": spec["positive_evidence"], "gdt776_counterevidence": spec["counterevidence"],
                "gdt776_scope_status": spec["scope_status"],
                "gdt776_dispatch_rule": "NOVEL_305_AND_EXACT_RIGHT_AND_MEDIAL_AND_RECURRENT_WHOLE",
                "gdt776_structural_bridge": "H4_LEANING_HEURISTIC__INTERNAL_LATE_RECORD_FIELD_BRIDGE",
                "gdt776_refined_existing_target": existing, "gdt776_new_contextual_target": 1 - existing,
            }
        compare_fields(check, actual, expected, f"renderer dispatch {source['target_occurrence_id']}")
    check((selected_count, refined_count, new_count) == (89, 63, 26), "renderer selected/refined/new counts differ")
    contextual = sum(row["gdt776_renderer_contextual"] == "1" for row in renderer)
    check(contextual == 149 and len(renderer) - contextual == 227, "contextual149/fallback227 differs")
    hybrid_contextual = sum(row["hybrid_throughput_contextual"] == "1" or row["gdt776_new_contextual_target"] == "1" for row in renderer)
    check(hybrid_contextual == 155, "derived hybrid155 differs")
    new_consuming = [row for row in renderer if row["gdt776_new_contextual_target"] == "1" and row["gdt776_span_consumes_right_token"] == "1"]
    chains = [row for row in renderer if row["gdt776_branch"] == "GDT776_MEDIAL_OL_CHAIN"]
    check(len(new_consuming) == 19 and len(chains) == 7, "19 consuming / 7 nonconsuming ol-chain additions differ")
    check(all(row["right_surface"] == "ol" and row["gdt776_span_consumes_right_token"] == "0" for row in chains),
          "ol-chain consumption rule differs")
    consumed = [(row["locus"], int(row["right_ordinal"])) for row in renderer if row["gdt776_span_consumes_right_token"] == "1"]
    check(len(consumed) == len(set(consumed)) == 93, "93 unique consumed right tokens differ")
    renderer_by_position = {(row["locus"], int(row["ordinal"])): row for row in renderer}
    check(all((row["locus"], int(row["right_ordinal"])) in renderer_by_position for row in chains),
          "ol-chain right ol is unavailable for its own dispatch")
    for surface_name, pattern in forbidden_by_surface.items():
        selected_rows = [row for row in renderer if row["gdt776_right_whole"] == surface_name
                         and row["gdt776_branch"] != "INHERITED_GDT775"]
        active = " ".join(row[field] for row in selected_rows for field in
                          ("gdt776_default_de", "gdt776_candidate_whole_de", "gdt776_semantic_family"))
        check(pattern.search(active) is None, f"retired {surface_name} identity in active renderer")

    dictionary = read_tsv(artifacts / "GDT776_WORKING_DICTIONARY.tsv")
    dictionary_by = {row["entry"]: row for row in dictionary}
    check(len(dictionary) == len(dictionary_by) == 26, "working dictionary row set differs")
    compare_fields(check, dictionary_by["ol"], {
        "entry_scope": "EXACT_WHOLE_CONTEXTUAL_RECORD_FIELD_HEAD",
        "selected_default_de": "Binnenfeldanschluss; vor lizenziertem Ganzwort: inhaltsbestimmtes Feld",
        "candidate_whole_de": "interner oder später Feldanschluss", "semantic_family": "RECORD_FIELD_HEAD",
        "confidence": "C2_STRUCTURAL_C0_LEXEME", "occurrences": 376, "pages": 98, "physical_folios": 61,
        "scope_status": "CONTEXTUAL_EXACT_WHOLE_ONLY", "historical_field_type": "INTERNAL_OR_LATE_RECORD_FIELD",
        "consumes_right_token": 0, "default_is_translation": 0, "confirmed_lexeme": 0,
        "confirmed_plaintext": 0, "component_export_credit": 0,
    }, "dictionary ol")
    for spec in specs:
        entry = f"ol {spec['surface']}"
        check(entry in dictionary_by, f"missing dictionary entry {entry}")
        if entry not in dictionary_by:
            continue
        profile = profile_artifact[spec["surface"]]
        expected = {
            "entry_scope": "EXACT_MEDIAL_OL_CHAIN" if spec["consume_right_token"] == "0" else "EXACT_MEDIAL_TWO_WHOLE_SPAN",
            "selected_default_de": spec["field_renderer_de"], "candidate_whole_de": spec["candidate_whole_de"],
            "semantic_family": spec["semantic_family"], "confidence": spec["candidate_confidence"],
            "occurrences": profile["target_occurrences"], "pages": profile["target_pages"],
            "physical_folios": profile["target_physical_folios"], "positive_evidence": spec["positive_evidence"],
            "counterevidence": spec["counterevidence"], "candidate_source": spec["candidate_source"],
            "scope_status": spec["scope_status"], "historical_field_type": spec["historical_field_type"],
            "h3_right_count": profile["h3_right_count"], "h4_right_count": profile["h4_right_count"],
            "existing_gdt775_selected": spec["existing_gdt775_selected"], "consumes_right_token": spec["consume_right_token"],
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        }
        compare_fields(check, dictionary_by[entry], expected, f"dictionary {entry}")
    for surface_name, pattern in forbidden_by_surface.items():
        row = dictionary_by[f"ol {surface_name}"]
        active = " ".join(row[field] for field in ("selected_default_de", "candidate_whole_de", "semantic_family"))
        check(pattern.search(active) is None, f"retired {surface_name} identity in working dictionary")
    base_active = " ".join(dictionary_by["ol"][field] for field in ("selected_default_de", "candidate_whole_de", "semantic_family"))
    check(forbidden_by_surface["ol"].search(base_active) is None, "ol/oil identity in base dictionary")

    passages = read_tsv(artifacts / "GDT776_PASSAGE_PATCHES.tsv")
    new_rows = [row for row in renderer if row["gdt776_new_contextual_target"] == "1"]
    affected = sorted({row["locus"] for row in new_rows})
    check(len(passages) == len(affected) == 26, "passage patch count differs")
    for number, (actual, locus) in enumerate(zip(passages, affected), 1):
        line = context.by_line[locus]
        rendered: list[str] = []
        consumed_ordinals: set[int] = set()
        local_contextual = 0
        for ordinal, token in enumerate(line, 1):
            if ordinal in consumed_ordinals:
                continue
            dispatch = renderer_by_position.get((locus, ordinal))
            if dispatch is None:
                rendered.append(str(token["eva"]))
            else:
                rendered.append(f"⟦{dispatch['gdt776_default_de']}⟧")
                local_contextual += int(dispatch["gdt776_renderer_contextual"])
                if dispatch["gdt776_span_consumes_right_token"] == "1":
                    consumed_ordinals.add(ordinal + 1)
        additions = [row for row in new_rows if row["locus"] == locus]
        first = additions[0]
        expected = {
            "passage_patch_id": f"G776-P{number:03d}", "page": first["page"],
            "physical_folio": first["physical_folio"], "locus": locus, "section": first["section"],
            "language": first["language"], "hand": first["hand"], "new_target_occurrences": len(additions),
            "new_consuming_spans": sum(row["gdt776_span_consumes_right_token"] == "1" for row in additions),
            "new_chain_links": sum(row["gdt776_branch"] == "GDT776_MEDIAL_OL_CHAIN" for row in additions),
            "contextual_ol_units_in_line": local_contextual,
            "new_units_de": " || ".join(f"ol {row['right_surface']} → {row['gdt776_default_de']}" for row in additions),
            "written_line_eva": " ".join(str(token["eva"]) for token in line),
            "practical_patch_de": " ".join(rendered),
            "patch_legend": "double brackets are replaceable contextual whole/span readings; unbracketed EVA remains unresolved",
            "default_is_translation": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        }
        compare_fields(check, actual, expected, f"passage {locus}")

    history_source = {row["source_id"]: row for row in read_tsv(G735_HISTORY)}
    history = read_tsv(artifacts / "HISTORICAL_FIELD_BRIDGE.tsv")
    check([row["source_id"] for row in history] == list(HISTORY_IDS), "historical bridge source set/order differs")
    for actual in history:
        source = history_source[actual["source_id"]]
        expected = {field: source[field] for field in ("source_id", "work", "date_band", "region", "language",
                                                       "slot_signature", "whole_plus_code_layout", "evidence_summary", "caveat")}
        expected.update({"gdt776_use": "MIXED_LEARNED_WHOLE_PLUS_BOUND_INTERNAL_FIELD_ARCHITECTURE_ONLY",
                         "voynich_identity_credit": 0, "lexeme_credit": 0, "component_export_credit": 0})
        compare_fields(check, actual, expected, f"history {actual['source_id']}")

    packet = read_tsv(artifacts / "GDT776_GDT388_RELATION_PACKET.tsv")
    crosswalk = read_tsv(artifacts / "GDT776_RELATION_EDGE_CROSSWALK.tsv")
    check(len(packet) == len(crosswalk) == 635, "packet635 row count differs")
    material: list[tuple[str, Mapping[str, object]]] = [("TARGET_MEDIAL", row) for row in target_expected]
    material.extend((f"{row['head_id']}_CONTROL", row) for row in controls_expected)
    material.sort(key=lambda item: (str(item[1]["page"]), str(item[1]["locus"]), int(item[1]["predecessor_ordinal"]), item[0]))
    for number, ((batch, edge), packet_row, crosswalk_row) in enumerate(zip(material, packet, crosswalk), 1):
        edge_id = f"G776-E{number:04d}"
        locus, left, right = str(edge["locus"]), int(edge["predecessor_ordinal"]), int(edge["right_ordinal"])
        expected_packet = {
            "edge_id": edge_id, "batch_id": f"GDT776_{batch}", "page": edge["page"],
            "physical_folio": edge["physical_folio"], "diagram_unit_id": f"LINE:{locus}",
            "pivot_visual_id": f"TOKEN:{locus}:{left}", "pivot_locus": f"{locus}@{left}",
            "target_visual_id": f"TOKEN:{locus}:{right}", "target_locus": f"{locus}@{right}",
            "relation_type": "NEXT_TOKEN", "direction_basis": "TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_ADJACENCY", "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT769", "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE", "source_aware_localizer": "GDT776_RUNNER",
            "relation_reviewer": "GDT776_VALIDATOR", "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "UNREVIEWED_TEXT_RELATION", "formal_access_state": "SEALED_NOT_ACCESSED",
            "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        }
        expected_crosswalk = {
            "edge_id": edge_id, "batch_id": f"GDT776_{batch}",
            "source_row_id": edge.get("target_edge_id", edge.get("control_edge_id", "NONE")),
            "page": edge["page"], "physical_folio": edge["physical_folio"], "locus": locus,
            "predecessor_ordinal": left, "right_ordinal": right, "predecessor_surface": edge["predecessor_surface"],
            "right_surface": edge["right_surface"], "head_id": edge.get("head_id", "TARGET_OL"),
            "body": edge.get("body", "NONE"), "register_id": edge["register_id"],
            "score_eligible": 0, "component_export_credit": 0,
        }
        compare_fields(check, packet_row, expected_packet, f"packet {edge_id}")
        compare_fields(check, crosswalk_row, expected_crosswalk, f"crosswalk {edge_id}")
    check(Counter(row["batch_id"] for row in crosswalk) == {
        "GDT776_TARGET_MEDIAL": 183, "GDT776_H3_CONTROL": 102, "GDT776_H4_CONTROL": 350,
    }, "packet batch counts differ")
    intake_done = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet",
                                  str(artifacts / "GDT776_GDT388_RELATION_PACKET.tsv")],
                                 cwd=ROOT, text=True, capture_output=True)
    check(intake_done.returncode == 0, "check-edge-packet command failed")
    intake = json.loads(intake_done.stdout) if intake_done.returncode == 0 else {}
    expected_intake = {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 635, "eligible_edges": 0,
        "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False, "mobile_null_gate": False,
        "score_ready": False, "errors": [],
    }
    check(intake == expected_intake, "packet is not valid acquisition/not-score-ready")
    stored_intake = json.loads((artifacts / "RELATION_PACKET_INTAKE.json").read_text(encoding="utf-8"))
    check(stored_intake == intake, "stored packet intake differs from executable gate")

    tsv_outputs = [name for name in outputs if name.endswith(".tsv")]
    credit_fields = {"default_is_translation", "confirmed_lexeme", "confirmed_plaintext",
                     "component_export_credit", "semantic_identity_credit", "voynich_identity_credit",
                     "lexeme_credit", "score_eligible"}
    for name in tsv_outputs:
        rows = read_tsv(artifacts / name)
        for row_number, row in enumerate(rows, 1):
            for field in credit_fields & set(row):
                check(row[field] == "0", f"forbidden credit {name}:{row_number}:{field}")
            for field in ("page", "physical_folio", "locus", "pivot_locus", "target_locus"):
                if field in row:
                    check(not row[field].startswith("f84"), f"sealed f84 material in {name}:{row_number}:{field}")

    result = json.loads((artifacts / "RESULT.json").read_text(encoding="utf-8"))
    check(result["experiment_id"] == "GDT776", "result experiment id differs")
    check(result["status"] == "PASS__H4_LEANING_HEURISTIC__INTERNAL_LATE_FIELD_BRIDGE__149_CONTEXTUAL__NO_PLAINTEXT",
          "result status differs")
    check(result["source_locks"] == 14 and result["guard"] == dict(environment["guard"]), "result source/guard summary differs")
    check(result["exact_bigram_universe"] == {"all_exact_adjacent": 16657, "medial_exact_adjacent": 14320},
          "result bigram summary differs")
    check(result["cohorts"] == {
        "target_edges": 183, "target_right_types": 119, "target_loci": 174, "target_physical_folios": 52,
        "h3_control_edges": 102, "h4_control_edges": 350, "recurrent_wholes": 25, "recurrent_target_edges": 89,
    }, "result cohort summary differs")
    check(result["renderer"] == {
        "gdt775_contextual": 123, "gdt776_contextual": 149, "new_contextual": 26,
        "new_ol_ol_chains": 7, "new_consuming_spans": 19, "total_consumed_right_tokens": 93,
        "fallbacks": 227, "passage_patches": 26,
    }, "result renderer summary differs")
    check(result["dictionary_rows"] == 26 and result["relation_packet"] == intake, "result dictionary/packet summary differs")
    check(result["interpretation"] == {
        "primary_three_h4_lead": True, "shared_body_equalized_reversal": True, "target_drop_reversal": True,
        "selected_bridge": "H4_LEANING_HEURISTIC__INTERNAL_OR_LATE_RECORD_FIELD_BRIDGE",
        "h4_identity_exported": False, "field_operator_semantics_exported": False,
    }, "result structural interpretation differs")
    check(result["strict_capacity"]["shared_bodies"] == 9 and result["strict_capacity"]["shared_cells"] == 13
          and result["strict_capacity"]["target_edges"] == 73
          and abs(float(result["strict_capacity"]["delta_h4_minus_h3"])
                  - float(expected_views["STRICT_BODY_REGISTER_ORDINAL_CAPACITY"]["delta_h4_minus_h3"])) <= FLOAT_TOLERANCE
          and result["strict_capacity"]["label_swap_status"] == "MATCHED_CELL_LABEL_SWAP_NOT_SEPARATING",
          "result strict-capacity summary differs")
    check(all(result[field] == 0 for field in ("confirmed_lexemes", "confirmed_plaintext_clauses", "component_exports",
                                               "new_pages", "new_images", "new_ocr", "new_transcriptions",
                                               "sealed_pages_accessed")),
          "result grants forbidden semantic/source credit")
    result_views = {row["view_id"]: row for row in result["vector_comparison"]}
    check(set(result_views) == set(expected_views), "result vector view set differs")
    for view_id, expected in expected_views.items():
        if view_id in result_views:
            check(abs(float(result_views[view_id]["cosine_h3"]) - float(expected["cosine_h3"])) <= 1e-12
                  and abs(float(result_views[view_id]["cosine_h4"]) - float(expected["cosine_h4"])) <= 1e-12,
                  f"result vector metrics differ {view_id}")

    replay_hashes: dict[str, str] = {}
    replay_failures_before = len(failures)
    with tempfile.TemporaryDirectory(prefix="gdt776_validator_replay_", dir=EXP) as temp_name:
        temp = Path(temp_name)
        replay_artifacts, replay_report = temp / "artifacts", temp / "REPORT.md"
        done = subprocess.run(["python3", "-B", str(RUN), "--artifacts-dir", str(replay_artifacts),
                               "--report-path", str(replay_report)], cwd=ROOT, text=True, capture_output=True)
        check(done.returncode == 0, "runner replay failed")
        for name in outputs:
            actual, replay = artifacts / name, replay_artifacts / name
            check(replay.is_file(), f"replay missing {name}")
            if actual.is_file() and replay.is_file():
                check(actual.read_bytes() == replay.read_bytes(), f"replay bytes differ {name}")
                replay_hashes[name] = sha256(replay)
        check(replay_report.is_file(), "replay missing report")
        if replay_report.is_file() and REPORT.is_file():
            check(REPORT.read_bytes() == replay_report.read_bytes(), "report replay bytes differ")

    status = "PASS" if not failures else "FAIL"
    validation = {
        "experiment_id": "GDT776", "status": status, "checks": checks, "failures": failures,
        "source_locks": len(locks), "runner_outputs": len(outputs),
        "runner_replay_byte_identical": len(failures) == replay_failures_before,
        "replay_sha256": replay_hashes,
        "independent_counts": {
            "target_edges": len(target_expected), "target_right_types": len(target_frequency),
            "target_loci": len({row["locus"] for row in target_expected}),
            "target_physical_folios": len({row["physical_folio"] for row in target_expected}),
            "h3_control_edges": control_counts["H3"], "h4_control_edges": control_counts["H4"],
            "recurrent_wholes": len(recurrent), "recurrent_target_edges": sum(target_frequency[word] for word in recurrent),
            "active_shared_bodies": len(shared_bodies), "strict_shared_bodies": len({cell[0] for cell in strict_cells}),
            "strict_shared_cells": len(strict_cells), "renderer_rows": len(renderer), "contextual": contextual,
            "fallbacks": len(renderer) - contextual, "derived_hybrid_contextual": hybrid_contextual,
            "new_consuming_spans": len(new_consuming), "nonconsuming_ol_chains": len(chains),
            "unique_consumed_right_tokens": len(set(consumed)), "packet_rows": len(packet),
        },
        "independent_metrics": {view_id: {"cosine_h3": row["cosine_h3"], "cosine_h4": row["cosine_h4"],
                                                  "delta_h4_minus_h3": row["delta_h4_minus_h3"], "winner": row["winner"]}
                                for view_id, row in expected_views.items()},
        "packet_status": intake.get("status"), "packet_score_ready": intake.get("score_ready"),
        "sealed_flags": manifest.get("sealed_data"),
        "claim_ceiling_respected": not any(marker in failure for failure in failures
                                            for marker in ("forbidden credit", "retired", "sealed f84",
                                                           "semantic/source credit", "identity")),
    }
    # Always write the validation record only to the real experiment artifacts directory.
    VALIDATION.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
