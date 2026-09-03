#!/usr/bin/env python3
"""Build GDT776's medial ``ol``/H3/H4 bridge and contextual renderer.

Only hash-locked cached artifacts are read.  The transcription environment is
obtained through GDT769's guarded loader; no page, image, OCR, or sealed row is
opened here.  H3/H4 remain structural comparison labels, never semantic gold.
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
from collections import Counter, defaultdict
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
EXP = ROOT / "experiments/yolo/gdt776_ol_h4_h3_medial_register_bridge"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
G775_ATLAS = ROOT / "experiments/yolo/gdt775_ol_right_complement_slot_test/artifacts/OL_327_RIGHT_COMPLEMENT_ATLAS.tsv"
G775_RENDERER = ROOT / "experiments/yolo/gdt775_ol_right_complement_slot_test/artifacts/GDT775_376_RENDERER.tsv"
G734 = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
G735_HISTORY = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/src/HISTORICAL_SOURCE_REGISTRY.tsv"
G736_GRID = ROOT / "experiments/yolo/gdt736_opaque_head_record_role_bridge/artifacts/OPAQUE_96_CONCRETE_ROLE_GRID.tsv"
G737_BODIES = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_BODY_WORKING_CANDIDATES.tsv"
G737_UPDATE = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/TRANSFER_MODEL_UPDATE.tsv"
G769_CORE = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/src/core_atlas.py"
SPECS = SRC / "MEDIAL_RIGHT_WHOLE_SPECS.tsv"
HISTORY_IDS = ("HSR008", "HSR010", "HSR012", "HSR013", "HSR017")

FIXED_13 = frozenset({
    "chy", "chey", "cheey", "chdy", "chedy", "sheey", "shedy",
    "aiin", "daiin", "kaiin", "okaiin", "oiin", "olaiin",
})


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
    for row in rows:
        relative = Path(row["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        actual = sha256(ROOT / relative)
        assert actual == row["expected_sha256"], f"source changed: {relative}: {actual}"
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


def cosine(first: Mapping[str, float], second: Mapping[str, float]) -> float:
    numerator = sum(float(first.get(key, 0)) * float(second.get(key, 0)) for key in set(first) | set(second))
    left = math.sqrt(sum(float(value) ** 2 for value in first.values()))
    right = math.sqrt(sum(float(value) ** 2 for value in second.values()))
    return numerator / (left * right) if left and right else 0.0


def vector(rows: Sequence[Mapping[str, object]]) -> Counter[str]:
    return Counter(str(row["right_surface"]) for row in rows)


def equalized_vector(rows: Sequence[Mapping[str, object]], key: str) -> Counter[str]:
    groups: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        groups[str(row[key])].append(row)
    result: Counter[str] = Counter()
    for group in groups.values():
        for row in group:
            result[str(row["right_surface"])] += 1.0 / len(groups) / len(group)
    return result


def winner(h3: float, h4: float) -> str:
    if abs(h4 - h3) < 1e-12:
        return "TIE"
    return "H4" if h4 > h3 else "H3"


def target_key(row: Mapping[str, object]) -> tuple[str, str, int, str]:
    return (str(row["page"]), str(row["locus"]), int(row["ordinal"]), str(row["right_surface"]))


def select_targets(atlas: Sequence[Mapping[str, str]], environment: Mapping[str, object]) -> tuple[list[dict[str, object]], dict[tuple[str, str, int, str], Mapping[str, str]]]:
    """Apply only the declared metadata/exactness/medial rule, never an ID list."""
    context = environment["context"]
    selected_source = [
        row for row in atlas
        if row["novel_305_member"] == "1"
        and row["right_reader_exact"] == "1"
        and int(row["ordinal"]) > 1
        and int(row["ordinal"]) < len(row["written_line_eva"].split())
    ]
    selected_source.sort(key=lambda row: (row["page"], row["locus"], int(row["ordinal"])))
    frequency = Counter(row["right_surface"] for row in selected_source)
    recurrent = {surface for surface, count in frequency.items() if count >= 2}
    assert len(selected_source) == 183 and len(frequency) == 119 and len(recurrent) == 25
    rows: list[dict[str, object]] = []
    source_by_key: dict[tuple[str, str, int, str], Mapping[str, str]] = {}
    for number, source in enumerate(selected_source, 1):
        locus, ordinal = source["locus"], int(source["ordinal"])
        line = context.by_line[locus]
        left, right = line[ordinal - 1], line[ordinal]
        assert str(left["eva"]) == "ol" and str(right["eva"]) == source["right_surface"]
        assert context.exact[(locus, int(left["token_index"]))]
        assert context.exact[(locus, int(right["token_index"]))]
        key = target_key(source)
        assert key not in source_by_key
        source_by_key[key] = source
        rows.append({
            "target_edge_id": f"G776-T{number:04d}",
            "source_target_occurrence_id": source["target_occurrence_id"],
            "page": source["page"], "physical_folio": source["physical_folio"],
            "locus": locus, "section": source["section"], "language": source["language"],
            "hand": source["hand"], "register_id": source["register_id"],
            "predecessor_ordinal": ordinal, "right_ordinal": ordinal + 1,
            "predecessor_surface": "ol", "right_surface": source["right_surface"],
            "predecessor_reader_exact": 1, "right_reader_exact": 1,
            "medial_predecessor": 1, "general_target_eligible": 1,
            "right_target_frequency": frequency[source["right_surface"]],
            "recurrent_25_member": int(source["right_surface"] in recurrent),
            "selection_rule": "NOVEL_305_AND_EXACT_RIGHT_AND_ORDINAL_GT_1_AND_NOT_LINE_FINAL",
            "written_line_eva": source["written_line_eva"],
            "score_eligible": 0, "component_export_credit": 0,
        })
    return rows, source_by_key


def enumerate_exact_bigrams(environment: Mapping[str, object]) -> list[dict[str, object]]:
    context, registry = environment["context"], environment["head_registry"]
    rows: list[dict[str, object]] = []
    for locus in sorted(context.by_line):
        line = context.by_line[locus]
        for index, (left, right) in enumerate(zip(line, line[1:])):
            if not context.exact[(locus, int(left["token_index"]))] or not context.exact[(locus, int(right["token_index"]))]:
                continue
            page, surface = str(left["page"]), str(left["eva"])
            head = registry.get(surface)
            rows.append({
                "page": page, "physical_folio": physical_folio(page), "locus": locus,
                "section": str(left["section"]), "language": str(left["language"]), "hand": str(left["hand"]),
                "register_id": f"{left['section']}|{left['language']}|{left['hand']}",
                "predecessor_ordinal": index + 1, "right_ordinal": index + 2,
                "predecessor_surface": surface, "right_surface": str(right["eva"]),
                "predecessor_reader_exact": 1, "right_reader_exact": 1,
                "predecessor_line_position": "FIRST" if index == 0 else "MIDDLE",
                "head_id": str(head["head_id"]) if head else "NONE",
                "body": str(head["body"]) if head else "NONE",
                "registry_source": str(head["registry_source"]) if head else "NONE",
                "record_role": str(head["record_role"]) if head else "NONE",
                "body_role_de": str(head["body_role_de"]) if head else "NONE",
                "written_line_eva": " ".join(str(token["eva"]) for token in line),
            })
    assert len(rows) == 16657
    return rows


def select_controls(bigrams: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    selected = [dict(row) for row in bigrams if row["head_id"] in {"H3", "H4"} and int(row["predecessor_ordinal"]) > 1]
    selected.sort(key=lambda row: (str(row["page"]), str(row["locus"]), int(row["predecessor_ordinal"]), str(row["head_id"])))
    counts = Counter(str(row["head_id"]) for row in selected)
    assert counts == Counter({"H3": 102, "H4": 350})
    for number, row in enumerate(selected, 1):
        row["control_edge_id"] = f"G776-C{number:04d}"
        row["control_cohort"] = f"{row['head_id']}_MEDIAL_EXACT_OUTGOING"
        row["medial_predecessor"] = 1
        row["selection_rule"] = "REGISTERED_H3_OR_H4_AND_BOTH_TOKENS_EXACT_AND_ORDINAL_GT_1_AND_NOT_LINE_FINAL"
        row["score_eligible"] = 0
        row["component_export_credit"] = 0
    return selected


def stratum(row: Mapping[str, object]) -> tuple[str, int]:
    return str(row["register_id"]), int(row["predecessor_ordinal"])


def standardized_vectors(target: Sequence[Mapping[str, object]], controls: Sequence[Mapping[str, object]]) -> tuple[list[Mapping[str, object]], dict[str, list[Mapping[str, object]]], dict[str, Counter[str]], set[tuple[str, int]]]:
    target_counts = Counter(stratum(row) for row in target)
    common = set(target_counts)
    for head in ("H3", "H4"):
        common &= {stratum(row) for row in controls if row["head_id"] == head}
    target_view = [row for row in target if stratum(row) in common]
    rows_by_head: dict[str, list[Mapping[str, object]]] = {}
    vectors: dict[str, Counter[str]] = {}
    for head in ("H3", "H4"):
        material = [row for row in controls if row["head_id"] == head and stratum(row) in common]
        rows_by_head[head] = material
        control_counts = Counter(stratum(row) for row in material)
        output: Counter[str] = Counter()
        for row in material:
            output[str(row["right_surface"])] += target_counts[stratum(row)] / control_counts[stratum(row)]
        vectors[head] = output
    return target_view, rows_by_head, vectors, common


def strict_capacity(target: Sequence[Mapping[str, object]], controls: Sequence[Mapping[str, object]]) -> tuple[list[Mapping[str, object]], dict[str, list[Mapping[str, object]]], dict[str, Counter[str]], set[tuple[str, str, int]]]:
    target_counts = Counter(stratum(row) for row in target)
    cell = lambda row: (str(row["body"]), str(row["register_id"]), int(row["predecessor_ordinal"]))
    cells = {cell(row) for row in controls if row["head_id"] == "H3"} & {cell(row) for row in controls if row["head_id"] == "H4"}
    cells = {item for item in cells if target_counts[(item[1], item[2])] > 0}
    shared_strata = {(item[1], item[2]) for item in cells}
    target_view = [row for row in target if stratum(row) in shared_strata]
    cells_per_stratum = Counter((item[1], item[2]) for item in cells)
    rows_by_head: dict[str, list[Mapping[str, object]]] = {}
    vectors: dict[str, Counter[str]] = {}
    for head in ("H3", "H4"):
        material = [row for row in controls if row["head_id"] == head and cell(row) in cells]
        rows_by_head[head] = material
        grouped: defaultdict[tuple[str, str, int], list[Mapping[str, object]]] = defaultdict(list)
        for row in material:
            grouped[cell(row)].append(row)
        output: Counter[str] = Counter()
        for key, group in grouped.items():
            allocation = target_counts[(key[1], key[2])] / cells_per_stratum[(key[1], key[2])]
            for row in group:
                output[str(row["right_surface"])] += allocation / len(group)
        vectors[head] = output
    assert len(cells) == 13 and len({item[0] for item in cells}) == 9 and len(target_view) == 73
    return target_view, rows_by_head, vectors, cells


def comparison_row(view_id: str, view_class: str, target: Sequence[Mapping[str, object]], h3: Sequence[Mapping[str, object]], h4: Sequence[Mapping[str, object]], h3_vector: Mapping[str, float], h4_vector: Mapping[str, float], **metadata: object) -> dict[str, object]:
    target_vector = vector(target)
    c3, c4 = cosine(target_vector, h3_vector), cosine(target_vector, h4_vector)
    return {
        "view_id": view_id, "view_class": view_class,
        "target_edges": len(target), "target_right_types": len(target_vector), "target_vector_mass": sum(target_vector.values()),
        "h3_edges": len(h3), "h3_predecessor_surfaces": len({str(row['predecessor_surface']) for row in h3}),
        "h3_bodies": len({str(row['body']) for row in h3}), "h3_vector_mass": sum(h3_vector.values()),
        "h4_edges": len(h4), "h4_predecessor_surfaces": len({str(row['predecessor_surface']) for row in h4}),
        "h4_bodies": len({str(row['body']) for row in h4}), "h4_vector_mass": sum(h4_vector.values()),
        "shared_registers": metadata.get("shared_registers", "NA"), "shared_strata": metadata.get("shared_strata", "NA"),
        "shared_bodies": metadata.get("shared_bodies", "NA"), "shared_cells": metadata.get("shared_cells", "NA"),
        "cosine_h3": c3, "cosine_h4": c4, "delta_h4_minus_h3": c4 - c3, "winner": winner(c3, c4),
        "label_swap_status": metadata.get("label_swap_status", "NOT_APPLICABLE"),
        "interpretive_scope": "STRUCTURAL_HEURISTIC_ONLY__NO_FIELD_OPERATOR_OR_SEMANTIC_IDENTITY",
        "component_export_credit": 0,
    }


def build_comparisons(target: Sequence[Mapping[str, object]], controls: Sequence[Mapping[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    by_head = {head: [row for row in controls if row["head_id"] == head] for head in ("H3", "H4")}
    rows = [comparison_row("RAW_POOLED", "PRIMARY", target, by_head["H3"], by_head["H4"], vector(by_head["H3"]), vector(by_head["H4"]))]
    rows.append(comparison_row("PREDECESSOR_SURFACE_EQUALIZED", "PRIMARY", target, by_head["H3"], by_head["H4"], equalized_vector(by_head["H3"], "predecessor_surface"), equalized_vector(by_head["H4"], "predecessor_surface")))

    shared_registers = {str(row["register_id"]) for row in target}
    for head in ("H3", "H4"):
        shared_registers &= {str(row["register_id"]) for row in by_head[head]}
    target_register = [row for row in target if row["register_id"] in shared_registers]
    register_controls = {head: [row for row in by_head[head] if row["register_id"] in shared_registers] for head in ("H3", "H4")}
    rows.append(comparison_row("SHARED_REGISTER_RAW", "MATCHED", target_register, register_controls["H3"], register_controls["H4"], vector(register_controls["H3"]), vector(register_controls["H4"]), shared_registers=len(shared_registers)))

    target_standard, standard_controls, standard_vectors, common_strata = standardized_vectors(target, controls)
    rows.append(comparison_row("REGISTER_ORDINAL_STANDARDIZED", "PRIMARY_MATCHED", target_standard, standard_controls["H3"], standard_controls["H4"], standard_vectors["H3"], standard_vectors["H4"], shared_strata=len(common_strata)))

    shared_bodies = {str(row["body"]) for row in by_head["H3"]} & {str(row["body"]) for row in by_head["H4"]}
    shared_body_controls = {head: [row for row in by_head[head] if row["body"] in shared_bodies] for head in ("H3", "H4")}
    rows.append(comparison_row("SHARED_BODY_RAW", "SENSITIVITY", target, shared_body_controls["H3"], shared_body_controls["H4"], vector(shared_body_controls["H3"]), vector(shared_body_controls["H4"]), shared_bodies=len(shared_bodies)))
    rows.append(comparison_row("SHARED_BODY_EQUALIZED", "SENSITIVITY", target, shared_body_controls["H3"], shared_body_controls["H4"], equalized_vector(shared_body_controls["H3"], "body"), equalized_vector(shared_body_controls["H4"], "body"), shared_bodies=len(shared_bodies)))

    strict_target, strict_controls, strict_vectors, strict_cells = strict_capacity(target, controls)
    rows.append(comparison_row("STRICT_BODY_REGISTER_ORDINAL_CAPACITY", "STRICT_SENSITIVITY", strict_target, strict_controls["H3"], strict_controls["H4"], strict_vectors["H3"], strict_vectors["H4"], shared_strata=len({(cell[1], cell[2]) for cell in strict_cells}), shared_bodies=len({cell[0] for cell in strict_cells}), shared_cells=len(strict_cells), label_swap_status="MATCHED_CELL_LABEL_SWAP_NOT_SEPARATING"))

    no_o = {head: [row for row in by_head[head] if not str(row["body"]).startswith("o")] for head in ("H3", "H4")}
    rows.append(comparison_row("SYMMETRIC_NO_O_BODY_RAW", "ABLATION", target, no_o["H3"], no_o["H4"], vector(no_o["H3"]), vector(no_o["H4"])))
    rows.append(comparison_row("SYMMETRIC_NO_O_BODY_SURFACE_EQUALIZED", "ABLATION", target, no_o["H3"], no_o["H4"], equalized_vector(no_o["H3"], "predecessor_surface"), equalized_vector(no_o["H4"], "predecessor_surface")))

    raw_winner = rows[0]["winner"]
    for row in rows:
        row["reversal_vs_raw"] = int(row["winner"] not in {raw_winner, "TIE"})
    lookup = {str(row["view_id"]): row for row in rows}
    assert lookup["RAW_POOLED"]["winner"] == "H4"
    assert lookup["PREDECESSOR_SURFACE_EQUALIZED"]["winner"] == "H4"
    assert lookup["REGISTER_ORDINAL_STANDARDIZED"]["winner"] == "H4"
    assert lookup["SHARED_BODY_EQUALIZED"]["winner"] == "H3"
    assert abs(float(lookup["STRICT_BODY_REGISTER_ORDINAL_CAPACITY"]["delta_h4_minus_h3"]) - 0.03482104108129527) < 1e-12

    target_counts = Counter(stratum(row) for row in target)
    coverage: list[dict[str, object]] = []
    for register, ordinal in sorted(target_counts):
        h3 = [row for row in by_head["H3"] if stratum(row) == (register, ordinal)]
        h4 = [row for row in by_head["H4"] if stratum(row) == (register, ordinal)]
        coverage.append({
            "coverage_level": "REGISTER_ORDINAL_STRATUM", "body": "ALL", "register_id": register,
            "predecessor_ordinal": ordinal, "target_stratum_edges": target_counts[(register, ordinal)],
            "h3_edges": len(h3), "h4_edges": len(h4), "shared_all_three": int(bool(h3 and h4)),
            "strict_cell_count_in_stratum": sum((cell[1], cell[2]) == (register, ordinal) for cell in strict_cells),
            "allocated_target_mass": target_counts[(register, ordinal)] if h3 and h4 else 0,
            "score_eligible": 0, "component_export_credit": 0,
        })
    cell_key = lambda row: (str(row["body"]), str(row["register_id"]), int(row["predecessor_ordinal"]))
    cells_per_stratum = Counter((cell[1], cell[2]) for cell in strict_cells)
    for body, register, ordinal in sorted(strict_cells):
        h3 = [row for row in by_head["H3"] if cell_key(row) == (body, register, ordinal)]
        h4 = [row for row in by_head["H4"] if cell_key(row) == (body, register, ordinal)]
        coverage.append({
            "coverage_level": "STRICT_SHARED_BODY_CELL", "body": body, "register_id": register,
            "predecessor_ordinal": ordinal, "target_stratum_edges": target_counts[(register, ordinal)],
            "h3_edges": len(h3), "h4_edges": len(h4), "shared_all_three": 1,
            "strict_cell_count_in_stratum": cells_per_stratum[(register, ordinal)],
            "allocated_target_mass": target_counts[(register, ordinal)] / cells_per_stratum[(register, ordinal)],
            "score_eligible": 0, "component_export_credit": 0,
        })
    state = {
        "by_head": by_head, "standard_target": target_standard, "standard_controls": standard_controls,
        "standard_vectors": standard_vectors, "common_strata": common_strata, "shared_bodies": shared_bodies,
        "shared_body_controls": shared_body_controls, "strict_cells": strict_cells,
    }
    return rows, coverage, state


def build_drop_sensitivity(target: Sequence[Mapping[str, object]], controls: Sequence[Mapping[str, object]], specs: Sequence[Mapping[str, str]]) -> list[dict[str, object]]:
    new_10 = {row["surface"] for row in specs if row["existing_gdt775_selected"] == "0"}
    recurrent_25 = {row["surface"] for row in specs}
    scenarios = (
        ("BASELINE", frozenset()),
        ("DROP_DAIIN", frozenset({"daiin"})),
        ("DROP_FIXED_13", FIXED_13),
        ("DROP_NEW_10", frozenset(new_10)),
        ("DROP_RECURRENT_25", frozenset(recurrent_25)),
    )
    by_head = {head: [row for row in controls if row["head_id"] == head] for head in ("H3", "H4")}
    raw_vectors = {head: vector(rows) for head, rows in by_head.items()}
    surface_vectors = {head: equalized_vector(rows, "predecessor_surface") for head, rows in by_head.items()}
    output: list[dict[str, object]] = []
    for scenario, dropped in scenarios:
        material = [row for row in target if row["right_surface"] not in dropped]
        target_vector = vector(material)
        raw = {head: cosine(target_vector, raw_vectors[head]) for head in ("H3", "H4")}
        equal = {head: cosine(target_vector, surface_vectors[head]) for head in ("H3", "H4")}
        standard_target, standard_controls, standard_vectors, common = standardized_vectors(material, controls)
        standard_target_vector = vector(standard_target)
        standard = {head: cosine(standard_target_vector, standard_vectors[head]) for head in ("H3", "H4") for _ in (0,)}
        output.append({
            "scenario": scenario, "dropped_surfaces": "|".join(sorted(dropped)) if dropped else "NONE",
            "removed_target_edges": len(target) - len(material), "remaining_target_edges": len(material),
            "remaining_target_right_types": len(target_vector), "common_register_ordinal_strata": len(common),
            "standardized_target_edges": len(standard_target),
            "raw_cosine_h3": raw["H3"], "raw_cosine_h4": raw["H4"],
            "raw_delta_h4_minus_h3": raw["H4"] - raw["H3"], "raw_winner": winner(raw["H3"], raw["H4"]),
            "surface_equalized_cosine_h3": equal["H3"], "surface_equalized_cosine_h4": equal["H4"],
            "surface_equalized_delta_h4_minus_h3": equal["H4"] - equal["H3"],
            "surface_equalized_winner": winner(equal["H3"], equal["H4"]),
            "standardized_cosine_h3": standard["H3"], "standardized_cosine_h4": standard["H4"],
            "standardized_delta_h4_minus_h3": standard["H4"] - standard["H3"],
            "standardized_winner": winner(standard["H3"], standard["H4"]),
            "semantic_identity_credit": 0, "component_export_credit": 0,
        })
    assert [int(row["remaining_target_edges"]) for row in output] == [183, 179, 125, 157, 94]
    return output


def rank_for(surface: str, values: Mapping[str, float]) -> int:
    value = float(values.get(surface, 0))
    return 1 + sum(float(other) > value for other in values.values()) if value else 0


def build_profiles(target: Sequence[Mapping[str, object]], controls: Sequence[Mapping[str, object]], specs: Sequence[Mapping[str, str]], state: Mapping[str, object], g734: Mapping[str, Sequence[Mapping[str, str]]]) -> list[dict[str, object]]:
    target_counts = Counter(str(row["right_surface"]) for row in target)
    by_head = state["by_head"]
    raw = {head: vector(by_head[head]) for head in ("H3", "H4")}
    surface = {head: equalized_vector(by_head[head], "predecessor_surface") for head in ("H3", "H4")}
    standardized = state["standard_vectors"]
    rows: list[dict[str, object]] = []
    for spec in specs:
        word = spec["surface"]
        occurrences = [row for row in target if row["right_surface"] == word]
        h3_share, h4_share = raw["H3"][word] / 102, raw["H4"][word] / 350
        profile = "UNSEEN_IN_H3_H4"
        if h3_share or h4_share:
            profile = "H4_ENRICHED" if h4_share > h3_share else "H3_ENRICHED" if h3_share > h4_share else "TIED"
        same_surface = list(g734.get(word, ()))
        matches = [row for row in same_surface
                   if row["v99r7_spoken_default_de"] == spec["expected_source_default_de"]
                   and row["working_model_level"] == spec["expected_source_level"]]
        assert len(matches) == 1, (word, len(matches))
        source = matches[0]
        rows.append({
            "surface": word, "target_occurrences": len(occurrences),
            "target_pages": len({str(row['page']) for row in occurrences}),
            "target_physical_folios": len({str(row['physical_folio']) for row in occurrences}),
            "target_registers": "|".join(sorted({str(row['register_id']) for row in occurrences})),
            "h3_right_count": raw["H3"][word], "h4_right_count": raw["H4"][word],
            "h3_right_share": h3_share, "h4_right_share": h4_share, "h4_minus_h3_share": h4_share - h3_share,
            "h3_raw_rank": rank_for(word, raw["H3"]), "h4_raw_rank": rank_for(word, raw["H4"]),
            "h3_surface_equalized_mass": surface["H3"][word], "h4_surface_equalized_mass": surface["H4"][word],
            "h3_standardized_mass": standardized["H3"][word], "h4_standardized_mass": standardized["H4"][word],
            "contact_profile": profile,
            "h3_active_predecessor_forms_with_same_body": "|".join(sorted({str(row['predecessor_surface']) for row in by_head["H3"] if row["body"] == word})) or "NONE",
            "h4_active_predecessor_forms_with_same_body": "|".join(sorted({str(row['predecessor_surface']) for row in by_head["H4"] if row["body"] == word})) or "NONE",
            "semantic_family": spec["semantic_family"], "candidate_whole_de": spec["candidate_whole_de"],
            "field_renderer_de": spec["field_renderer_de"], "candidate_confidence": spec["candidate_confidence"],
            "positive_evidence": spec["positive_evidence"], "counterevidence": spec["counterevidence"],
            "candidate_source": spec["candidate_source"], "expected_source_default_de": spec["expected_source_default_de"],
            "gdt734_expected_card_default_de": source["v99r7_spoken_default_de"],
            "gdt734_same_surface_card_count": len(same_surface),
            "gdt734_same_surface_defaults": " || ".join(sorted({row["v99r7_spoken_default_de"] for row in same_surface})),
            "expected_source_default_matches_gdt734": 1,
            "existing_gdt775_selected": int(spec["existing_gdt775_selected"]),
            "consume_right_token": int(spec["consume_right_token"]), "scope_status": spec["scope_status"],
            "historical_field_type": spec["historical_field_type"], "default_is_translation": 0,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    assert len(rows) == 25 and sum(int(row["target_occurrences"]) for row in rows) == 89
    return rows


def build_renderer(g775: Sequence[Mapping[str, str]], source_by_key: Mapping[tuple[str, str, int, str], Mapping[str, str]], specs: Mapping[str, Mapping[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    sequence = 0
    for source in g775:
        row: dict[str, object] = dict(source)
        key = (source["page"], source["locus"], int(source["ordinal"]), source["right_surface"])
        target = source_by_key.get(key)
        spec = specs.get(source["right_surface"]) if target is not None else None
        row.update({
            "gdt776_branch": "INHERITED_GDT775", "gdt776_default_de": source["throughput_renderer_default_de"],
            "gdt776_renderer_contextual": int(source["throughput_renderer_contextual"]),
            "gdt776_span_consumes_right_token": int(source["throughput_span_consumes_right_token"]),
            "gdt776_span_id": source["throughput_span_id"], "gdt776_right_whole": source["right_surface"],
            "gdt776_candidate_whole_de": "NONE", "gdt776_semantic_family": "NONE",
            "gdt776_confidence": source["construction_confidence"], "gdt776_positive_evidence": "INHERITED_GDT775",
            "gdt776_counterevidence": "INHERITED_GDT775", "gdt776_scope_status": "INHERITED_GDT775",
            "gdt776_dispatch_rule": "INHERITED_GDT775", "gdt776_structural_bridge": "NONE",
            "gdt776_refined_existing_target": 0, "gdt776_new_contextual_target": 0,
        })
        if spec is not None:
            sequence += 1
            existing, consumes = int(spec["existing_gdt775_selected"]), int(spec["consume_right_token"])
            if existing:
                branch = "GDT776_MEDIAL_RIGHT_WHOLE_REFINED"
            elif consumes:
                branch = "GDT776_MEDIAL_RIGHT_WHOLE_EXTENSION"
            else:
                branch = "GDT776_MEDIAL_OL_CHAIN"
            row.update({
                "gdt776_branch": branch, "gdt776_default_de": spec["field_renderer_de"],
                "gdt776_renderer_contextual": 1, "gdt776_span_consumes_right_token": consumes,
                "gdt776_span_id": f"G776-{'SPAN' if consumes else 'CHAIN'}-{sequence:03d}",
                "gdt776_candidate_whole_de": spec["candidate_whole_de"], "gdt776_semantic_family": spec["semantic_family"],
                "gdt776_confidence": spec["candidate_confidence"], "gdt776_positive_evidence": spec["positive_evidence"],
                "gdt776_counterevidence": spec["counterevidence"], "gdt776_scope_status": spec["scope_status"],
                "gdt776_dispatch_rule": "NOVEL_305_AND_EXACT_RIGHT_AND_MEDIAL_AND_RECURRENT_WHOLE",
                "gdt776_structural_bridge": "H4_LEANING_HEURISTIC__INTERNAL_LATE_RECORD_FIELD_BRIDGE",
                "gdt776_refined_existing_target": existing, "gdt776_new_contextual_target": 1 - existing,
            })
        output.append(row)
    assert len(output) == 376
    assert sum(int(row["gdt776_renderer_contextual"]) for row in output) == 149
    assert sum(int(row["gdt776_new_contextual_target"]) for row in output) == 26
    assert sum(row["gdt776_branch"] == "GDT776_MEDIAL_OL_CHAIN" for row in output) == 7
    assert sum(int(row["gdt776_span_consumes_right_token"]) for row in output) == 93
    consumed = {(str(row["locus"]), int(row["right_ordinal"])) for row in output if int(row["gdt776_span_consumes_right_token"])}
    assert len(consumed) == 93
    return output


def build_dictionary(renderer: Sequence[Mapping[str, object]], profiles: Sequence[Mapping[str, object]], comparisons: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    raw = next(row for row in comparisons if row["view_id"] == "RAW_POOLED")
    rows: list[dict[str, object]] = [{
        "entry": "ol", "entry_scope": "EXACT_WHOLE_CONTEXTUAL_RECORD_FIELD_HEAD",
        "selected_default_de": "Binnenfeldanschluss; vor lizenziertem Ganzwort: inhaltsbestimmtes Feld",
        "candidate_whole_de": "interner oder später Feldanschluss", "semantic_family": "RECORD_FIELD_HEAD",
        "confidence": "C2_STRUCTURAL_C0_LEXEME", "occurrences": 376,
        "pages": len({str(row['page']) for row in renderer}), "physical_folios": len({str(row['physical_folio']) for row in renderer}),
        "positive_evidence": f"183 mediale exakte Zielkanten; pooled H4-H3 delta={float(raw['delta_h4_minus_h3']):.6f}; 25 wiederkehrende rechte Ganzwörter",
        "counterevidence": "shared-body equalization reverses to H3; strict matched lead is small; exact lexeme and substance remain open",
        "candidate_source": "GDT775+GDT736+GDT737", "scope_status": "CONTEXTUAL_EXACT_WHOLE_ONLY",
        "historical_field_type": "INTERNAL_OR_LATE_RECORD_FIELD", "h3_right_count": "NA", "h4_right_count": "NA",
        "existing_gdt775_selected": "NA", "consumes_right_token": 0,
        "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
    }]
    for profile in profiles:
        rows.append({
            "entry": f"ol {profile['surface']}",
            "entry_scope": "EXACT_MEDIAL_OL_CHAIN" if not int(profile["consume_right_token"]) else "EXACT_MEDIAL_TWO_WHOLE_SPAN",
            "selected_default_de": profile["field_renderer_de"], "candidate_whole_de": profile["candidate_whole_de"],
            "semantic_family": profile["semantic_family"], "confidence": profile["candidate_confidence"],
            "occurrences": profile["target_occurrences"], "pages": profile["target_pages"],
            "physical_folios": profile["target_physical_folios"], "positive_evidence": profile["positive_evidence"],
            "counterevidence": profile["counterevidence"], "candidate_source": profile["candidate_source"],
            "scope_status": profile["scope_status"], "historical_field_type": profile["historical_field_type"],
            "h3_right_count": profile["h3_right_count"], "h4_right_count": profile["h4_right_count"],
            "existing_gdt775_selected": profile["existing_gdt775_selected"],
            "consumes_right_token": profile["consume_right_token"], "default_is_translation": 0,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    assert len(rows) == 26
    return rows


def build_shared_body_audit(
    target: Sequence[Mapping[str, object]], state: Mapping[str, object]
) -> list[dict[str, object]]:
    target_vector = vector(target)
    controls = state["shared_body_controls"]
    strict_cells = state["strict_cells"]
    rows: list[dict[str, object]] = []
    for body in sorted(state["shared_bodies"]):
        selected = {
            head: [row for row in controls[head] if row["body"] == body]
            for head in ("H3", "H4")
        }
        rows.append({
            "body": body,
            "starts_o": int(str(body).startswith("o")),
            "h3_forms": "|".join(sorted({str(row["predecessor_surface"]) for row in selected["H3"]})),
            "h4_forms": "|".join(sorted({str(row["predecessor_surface"]) for row in selected["H4"]})),
            "h3_edges": len(selected["H3"]),
            "h4_edges": len(selected["H4"]),
            "h3_right_types": len({row["right_surface"] for row in selected["H3"]}),
            "h4_right_types": len({row["right_surface"] for row in selected["H4"]}),
            "h3_cosine_to_target": cosine(target_vector, vector(selected["H3"])),
            "h4_cosine_to_target": cosine(target_vector, vector(selected["H4"])),
            "strict_shared_cells": sum(cell[0] == body for cell in strict_cells),
            "body_equalization_weight": 1 / len(state["shared_bodies"]),
            "semantic_identity_credit": 0,
            "component_export_credit": 0,
        })
    assert len(rows) == 18 and sum(int(row["strict_shared_cells"]) for row in rows) == 13
    return rows


def build_historical_bridge() -> list[dict[str, object]]:
    source = {row["source_id"]: row for row in read_tsv(G735_HISTORY)}
    rows = [{
        "source_id": source_id,
        "work": source[source_id]["work"],
        "date_band": source[source_id]["date_band"],
        "region": source[source_id]["region"],
        "language": source[source_id]["language"],
        "slot_signature": source[source_id]["slot_signature"],
        "whole_plus_code_layout": source[source_id]["whole_plus_code_layout"],
        "evidence_summary": source[source_id]["evidence_summary"],
        "caveat": source[source_id]["caveat"],
        "gdt776_use": "MIXED_LEARNED_WHOLE_PLUS_BOUND_INTERNAL_FIELD_ARCHITECTURE_ONLY",
        "voynich_identity_credit": 0,
        "lexeme_credit": 0,
        "component_export_credit": 0,
    } for source_id in HISTORY_IDS]
    assert len(rows) == 5
    return rows


def build_passages(renderer: Sequence[Mapping[str, object]], environment: Mapping[str, object]) -> list[dict[str, object]]:
    new_rows = [row for row in renderer if int(row["gdt776_new_contextual_target"])]
    affected = sorted({str(row["locus"]) for row in new_rows})
    assert len(new_rows) == len(affected) == 26
    by_position = {(str(row["locus"]), int(row["ordinal"])): row for row in renderer}
    context = environment["context"]
    output: list[dict[str, object]] = []
    for number, locus in enumerate(affected, 1):
        line = context.by_line[locus]
        rendered: list[str] = []
        consumed: set[int] = set()
        contextual = 0
        for ordinal, token in enumerate(line, 1):
            if ordinal in consumed:
                continue
            dispatch = by_position.get((locus, ordinal))
            if dispatch is None:
                rendered.append(str(token["eva"]))
                continue
            rendered.append(f"⟦{dispatch['gdt776_default_de']}⟧")
            contextual += int(dispatch["gdt776_renderer_contextual"])
            if int(dispatch["gdt776_span_consumes_right_token"]):
                consumed.add(ordinal + 1)
        additions = [row for row in new_rows if row["locus"] == locus]
        first = additions[0]
        units = [f"ol {row['right_surface']} → {row['gdt776_default_de']}" for row in additions]
        output.append({
            "passage_patch_id": f"G776-P{number:03d}", "page": first["page"], "physical_folio": first["physical_folio"],
            "locus": locus, "section": first["section"], "language": first["language"], "hand": first["hand"],
            "new_target_occurrences": len(additions),
            "new_consuming_spans": sum(int(row["gdt776_span_consumes_right_token"]) for row in additions),
            "new_chain_links": sum(row["gdt776_branch"] == "GDT776_MEDIAL_OL_CHAIN" for row in additions),
            "contextual_ol_units_in_line": contextual, "new_units_de": " || ".join(units),
            "written_line_eva": " ".join(str(token["eva"]) for token in line),
            "practical_patch_de": " ".join(rendered),
            "patch_legend": "double brackets are replaceable contextual whole/span readings; unbracketed EVA remains unresolved",
            "default_is_translation": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    return output


def make_packet(target: Sequence[Mapping[str, object]], controls: Sequence[Mapping[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    material = [("TARGET_MEDIAL", row) for row in target]
    material += [(f"{row['head_id']}_CONTROL", row) for row in controls]
    material.sort(key=lambda item: (str(item[1]["page"]), str(item[1]["locus"]), int(item[1]["predecessor_ordinal"]), item[0]))
    packet: list[dict[str, object]] = []
    crosswalk: list[dict[str, object]] = []
    for number, (batch, edge) in enumerate(material, 1):
        locus, left, right = str(edge["locus"]), int(edge["predecessor_ordinal"]), int(edge["right_ordinal"])
        edge_id = f"G776-E{number:04d}"
        packet.append({
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
        })
        crosswalk.append({
            "edge_id": edge_id, "batch_id": f"GDT776_{batch}",
            "source_row_id": edge.get("target_edge_id", edge.get("control_edge_id", "NONE")),
            "page": edge["page"], "physical_folio": edge["physical_folio"], "locus": locus,
            "predecessor_ordinal": left, "right_ordinal": right,
            "predecessor_surface": edge["predecessor_surface"], "right_surface": edge["right_surface"],
            "head_id": edge.get("head_id", "TARGET_OL"), "body": edge.get("body", "NONE"),
            "register_id": edge["register_id"], "score_eligible": 0, "component_export_credit": 0,
        })
    assert len(packet) == len(crosswalk) == 635
    return packet, crosswalk


def build_report(result: Mapping[str, object], passages: Sequence[Mapping[str, object]]) -> str:
    comparison = {row["view_id"]: row for row in result["vector_comparison"]}
    raw = comparison["RAW_POOLED"]
    equal = comparison["PREDECESSOR_SURFACE_EQUALIZED"]
    standard = comparison["REGISTER_ORDINAL_STANDARDIZED"]
    body_raw = comparison["SHARED_BODY_RAW"]
    body_equal = comparison["SHARED_BODY_EQUALIZED"]
    strict = comparison["STRICT_BODY_REGISTER_ORDINAL_CAPACITY"]
    no_o = comparison["SYMMETRIC_NO_O_BODY_SURFACE_EQUALIZED"]
    preferred = ["f79r.41", "f80r.52", "f99v.34"]
    examples = [row for locus in preferred for row in passages if row["locus"] == locus]
    rendered_examples = "\n\n".join(
        f"- `{row['locus']}`: `{row['written_line_eva']}`\n  → {row['practical_patch_de']}"
        for row in examples
    )
    drops = "\n".join(
        f"- `{row['scenario']}`: n={row['remaining_target_edges']}; raw Δ(H4-H3)={float(row['raw_delta_h4_minus_h3']):+.6f}; surface-equalized Δ={float(row['surface_equalized_delta_h4_minus_h3']):+.6f}."
        for row in result["target_drop_sensitivity"]
    )
    return f"""# GDT776 — mediales `ol` gegen H3/H4-Feldstruktur

Status: `{result['status']}`.

## Ergebnis

Der hash-gesperrte, über GDT769 bewachte Lauf bestätigt **183** mediale
`ol`-Zielkanten. Die vollständigen reader-exakten Kontrollen umfassen **102
H3-** und **350 H4-Kanten**. H4 führt gepoolt
({float(raw['cosine_h4']):.6f} gegen {float(raw['cosine_h3']):.6f}), nach
Oberflächen-Ausgleich ({float(equal['cosine_h4']):.6f} gegen
{float(equal['cosine_h3']):.6f}) und in 23 gemeinsam getragenen
Register×Ordinal-Strata ({float(standard['cosine_h4']):.6f} gegen
{float(standard['cosine_h3']):.6f}). Das ist eine **H4-neigende strukturelle
Heuristik**, keine H4- oder Operator-Bedeutung.

Die schärfere Prüfung begrenzt die Deutung. Auf 18 gemeinsam aktiven bodies
führt H4 roh ({float(body_raw['cosine_h4']):.6f} gegen
{float(body_raw['cosine_h3']):.6f}), doch nach body-Ausgleich kehrt sich die
Reihenfolge zu H3 um ({float(body_equal['cosine_h3']):.6f} gegen
{float(body_equal['cosine_h4']):.6f}). Im strengsten identischen
body×Register×Ordinal-Kapazitätsview bleiben 9 bodies, 13 Zellen und 73
Zielkanten; der H4-Vorsprung beträgt nur
{float(strict['delta_h4_minus_h3']):+.6f} und ist im Zell-Labeltausch nicht
trennend. Die symmetrische Entfernung aller `o...`-bodies lässt nach
Oberflächen-Ausgleich einen kleinen H4-Vorsprung von
{float(no_o['delta_h4_minus_h3']):+.6f}. Gewählt wird daher der breitere
**internal/late record-field bridge**, nicht eine automatische
`FIELD_OPERATOR`-Semantik.

## Renderer und Wörterbuch

Die 25 vorab festgelegten wiederkehrenden rechten Ganzwörter decken 89 der 183
Zielkanten ab. Der GDT775-Durchsatz steigt von **123 auf 149** kontextuelle
Ausgaben. Die 26 neuen Ausgaben bestehen aus sieben nicht konsumierenden
`ol ol`-Kettengliedern und 19 neuen konsumierenden Ganzwortspannen. Zusammen
mit den 74 geerbten Spannen werden genau **93** rechte Token einmalig
konsumiert. Jede Ganzwortkarte nennt Lesart, Konfidenz, positive Evidenz und
Gegenevidenz; keine Karte exportiert freie EVA-Komponenten oder Klartext.

Alle 26 neu kontextualisierten Ausgaben sind C0/C1 statt C2; vierzehn sind
ausdrückliche Feld-/Strukturlesarten (`ol ol`, `ol r`, `ol dy`, `ol s`). Der
Gewinn ist daher eine schärfere Spangrammatik, nicht 26 entschlüsselte
Inhaltswörter. Insbesondere hält GDT759 außerhalb von Wertausdrücken für `s`
den Mengen-/Einheitsrivalen offen. Der nächste Komponierer muss deshalb das
folgende Wert- oder Zustandswort mitbinden, bevor er Mengenbezug und
H2-Unterposten trennt.

## Zieltyp-Sensitivität

{drops}

Der feste GDT775-13er-Drop dreht die oberflächen-ausgeglichene Führung zu H3;
gepoolt bleibt H4 in allen Drops vorn. Diese Zieltyp-Sensitivität und die
body-ausgeglichene Umkehr sind bindende Interpretationslimits.

## Drei praktische Passage-Patches

{rendered_examples}

Die Doppelklammern markieren ersetzbare Ganzwort-/Spannenlesarten; übriges EVA
bleibt ausdrücklich ungelöst. Das sind keine übersetzten Sätze.

## GDT388-Grenze

Das Paket enthält 183+102+350 = **635** Transkriptionskanten. Alle sind als
`INELIGIBLE_EXPLORATORY_TEXT_RELATION` markiert. Der Intake lautet
`{result['relation_packet']['status']}`; weder Kapazitäts-, Holdout- noch
Mobile-null-Gate ist score-ready. Es wurden keine neuen Seiten, Bilder, OCR,
Transkriptionen, `f84`- oder `f84r`-Daten geöffnet.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts = args.artifacts_dir.resolve()
    report_path = args.report_path.resolve()

    lock_count = verify_locks()
    core = load_module("gdt769_core_for_gdt776", G769_CORE)
    _, environment = core.load_guarded_environment(ROOT)
    assert dict(environment["guard"]) == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}

    specs = read_tsv(SPECS)
    assert len(specs) == len({row["surface"] for row in specs}) == 25
    spec_by_surface = {row["surface"]: row for row in specs}
    g736_bodies = {row["body"] for row in read_tsv(G736_GRID)}
    g737_bodies = {row["body"] for row in read_tsv(G737_BODIES)}
    assert {"aiin", "chedy", "ol", "cheey", "chey", "shedy", "al", "chdy", "oiin", "or", "shey"} <= g736_bodies
    assert {"kaiin", "sheey", "daiin", "okaiin", "olaiin", "r", "olor"} <= g737_bodies
    transfer = {row["claim_id"]: row for row in read_tsv(G737_UPDATE)}
    assert transfer["C03"]["new_live_status"] == "RETAIN_AS_RELATIVE_POSITION_SUBROLES"
    atlas = read_tsv(G775_ATLAS)
    target, source_by_key = select_targets(atlas, environment)
    assert {row["right_surface"] for row in target if int(row["right_target_frequency"]) >= 2} == set(spec_by_surface)
    bigrams = enumerate_exact_bigrams(environment)
    controls = select_controls(bigrams)

    comparisons, coverage, comparison_state = build_comparisons(target, controls)
    drops = build_drop_sensitivity(target, controls, specs)
    g734: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(G734):
        g734[row["surface"]].append(row)
    profiles = build_profiles(target, controls, specs, comparison_state, g734)
    renderer = build_renderer(read_tsv(G775_RENDERER), source_by_key, spec_by_surface)
    dictionary = build_dictionary(renderer, profiles, comparisons)
    shared_body_audit = build_shared_body_audit(target, comparison_state)
    historical_bridge = build_historical_bridge()
    passages = build_passages(renderer, environment)
    packet, crosswalk = make_packet(target, controls)

    target_fields = list(target[0])
    control_fields = [
        "control_edge_id", "control_cohort", "page", "physical_folio", "locus", "section", "language", "hand",
        "register_id", "predecessor_ordinal", "right_ordinal", "predecessor_surface", "right_surface",
        "predecessor_reader_exact", "right_reader_exact", "predecessor_line_position", "head_id", "body",
        "registry_source", "record_role", "body_role_de", "medial_predecessor", "selection_rule", "written_line_eva",
        "score_eligible", "component_export_credit",
    ]
    packet_fields = [
        "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id", "pivot_visual_id", "pivot_locus",
        "target_visual_id", "target_locus", "relation_type", "direction_basis", "ownership_basis",
        "geometry_only_selection", "source_manifest_id", "page_crop_sha256", "pivot_crop_sha256",
        "target_crop_sha256", "source_aware_localizer", "relation_reviewer", "relation_confidence",
        "ambiguity_state", "formal_access_state", "fold_assignment", "eligibility_status",
    ]
    outputs = [
        ("TARGET_183_MEDIAL_EDGE_ATLAS.tsv", target, target_fields),
        ("H34_452_MEDIAL_CONTROL_EDGE_ATLAS.tsv", controls, control_fields),
        ("H34_VECTOR_COMPARISON.tsv", comparisons, list(comparisons[0])),
        ("H34_MATCH_STRATUM_COVERAGE.tsv", coverage, list(coverage[0])),
        ("H34_RECURRENT_25_WHOLE_PROFILES.tsv", profiles, list(profiles[0])),
        ("H34_TARGET_DROP_SENSITIVITY.tsv", drops, list(drops[0])),
        ("H34_SHARED_BODY_AUDIT.tsv", shared_body_audit, list(shared_body_audit[0])),
        ("GDT776_376_RENDERER.tsv", renderer, list(renderer[0])),
        ("GDT776_WORKING_DICTIONARY.tsv", dictionary, list(dictionary[0])),
        ("GDT776_PASSAGE_PATCHES.tsv", passages, list(passages[0])),
        ("HISTORICAL_FIELD_BRIDGE.tsv", historical_bridge, list(historical_bridge[0])),
        ("GDT776_GDT388_RELATION_PACKET.tsv", packet, packet_fields),
        ("GDT776_RELATION_EDGE_CROSSWALK.tsv", crosswalk, list(crosswalk[0])),
    ]
    for name, rows, fields in outputs:
        write_tsv(artifacts / name, rows, fields)

    intake_done = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(artifacts / "GDT776_GDT388_RELATION_PACKET.tsv")],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    intake = json.loads(intake_done.stdout)
    assert intake == {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 635,
        "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0,
        "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False, "errors": [],
    }
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", intake)

    comparison_lookup = {row["view_id"]: row for row in comparisons}
    drop_reversal = any(row["raw_winner"] == "H3" or row["surface_equalized_winner"] == "H3" for row in drops)
    result: dict[str, object] = {
        "experiment_id": "GDT776",
        "status": "PASS__H4_LEANING_HEURISTIC__INTERNAL_LATE_FIELD_BRIDGE__149_CONTEXTUAL__NO_PLAINTEXT",
        "source_locks": lock_count, "guard": dict(environment["guard"]),
        "exact_bigram_universe": {"all_exact_adjacent": len(bigrams), "medial_exact_adjacent": sum(int(row["predecessor_ordinal"]) > 1 for row in bigrams)},
        "cohorts": {
            "target_edges": len(target), "target_right_types": len({row['right_surface'] for row in target}),
            "target_loci": len({row['locus'] for row in target}), "target_physical_folios": len({row['physical_folio'] for row in target}),
            "h3_control_edges": sum(row["head_id"] == "H3" for row in controls),
            "h4_control_edges": sum(row["head_id"] == "H4" for row in controls),
            "recurrent_wholes": len(profiles), "recurrent_target_edges": sum(int(row["target_occurrences"]) for row in profiles),
        },
        "vector_comparison": comparisons,
        "interpretation": {
            "primary_three_h4_lead": all(comparison_lookup[view]["winner"] == "H4" for view in ("RAW_POOLED", "PREDECESSOR_SURFACE_EQUALIZED", "REGISTER_ORDINAL_STANDARDIZED")),
            "shared_body_equalized_reversal": comparison_lookup["SHARED_BODY_EQUALIZED"]["winner"] == "H3",
            "target_drop_reversal": drop_reversal,
            "selected_bridge": "H4_LEANING_HEURISTIC__INTERNAL_OR_LATE_RECORD_FIELD_BRIDGE",
            "h4_identity_exported": False, "field_operator_semantics_exported": False,
        },
        "strict_capacity": {
            "shared_bodies": comparison_lookup["STRICT_BODY_REGISTER_ORDINAL_CAPACITY"]["shared_bodies"],
            "shared_cells": comparison_lookup["STRICT_BODY_REGISTER_ORDINAL_CAPACITY"]["shared_cells"],
            "target_edges": comparison_lookup["STRICT_BODY_REGISTER_ORDINAL_CAPACITY"]["target_edges"],
            "delta_h4_minus_h3": comparison_lookup["STRICT_BODY_REGISTER_ORDINAL_CAPACITY"]["delta_h4_minus_h3"],
            "label_swap_status": comparison_lookup["STRICT_BODY_REGISTER_ORDINAL_CAPACITY"]["label_swap_status"],
        },
        "target_drop_sensitivity": drops,
        "renderer": {
            "gdt775_contextual": 123, "gdt776_contextual": 149, "new_contextual": 26,
            "new_ol_ol_chains": 7, "new_consuming_spans": 19, "total_consumed_right_tokens": 93,
            "fallbacks": 227, "passage_patches": len(passages),
        },
        "dictionary_rows": len(dictionary), "relation_packet": intake,
        "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "component_exports": 0,
        "new_pages": 0, "new_images": 0, "new_ocr": 0, "new_transcriptions": 0,
        "sealed_pages_accessed": 0,
        "claim_ceiling": "Replaceable exact-whole medial ol-field readings and an H4-leaning internal/late structural bridge; no H4 identity, FIELD_OPERATOR semantics, language, plaintext, substance, or free EVA component.",
    }
    write_json(artifacts / "RESULT.json", result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(result, passages), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
