#!/usr/bin/env python3
"""Reproducible structural audit of the 376 reader-exact ``ol`` positions.

The script reads only published, already admitted artifacts and GDT769's
guarded cache provider.  It opens no image or new transcription.  All output
is written beneath an explicitly supplied directory; the GDT774 main runner
is deliberately independent of this audit helper.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import random
import re
import subprocess
import sys
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

G769_EXACT_REL = Path(
    "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/"
    "artifacts/TARGET_526_EXACT_CONTEXT_ATLAS.tsv"
)
G769_FRAME_REL = Path(
    "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/"
    "artifacts/FRAME_LOCUS_EVIDENCE.tsv"
)
G769_CORE_REL = Path(
    "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/src/core_atlas.py"
)
G769_MANIFEST_REL = Path(
    "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/experiment.json"
)
G764_RUN_REL = Path(
    "experiments/yolo/gdt764_bounded_value_field_dispatch/src/run.py"
)
G764_MANIFEST_REL = Path(
    "experiments/yolo/gdt764_bounded_value_field_dispatch/experiment.json"
)
G683_AUDIT_REL = Path(
    "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/"
    "artifacts/OL_463_OCCURRENCE_AUDIT.tsv"
)
G683_REPEAT_REL = Path(
    "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/"
    "artifacts/ADJACENT_OL_PAIRS.tsv"
)
G762_AMOUNT_REL = Path(
    "experiments/yolo/gdt762_moist_medium_candidate_discrimination/"
    "artifacts/OL_AMOUNT_EXPRESSION_CONTACT_ATLAS.tsv"
)
G771_LEFT_REL = Path(
    "experiments/yolo/gdt771_complete_cache_discriminator_sufficiency/"
    "artifacts/OL_LEFT_BRANCH_ATLAS.tsv"
)
G773_DEFAULT_REL = Path(
    "experiments/yolo/gdt773_ol_capacity_equalized_composition_audit/"
    "artifacts/OL_CONTEXTUAL_DEFAULTS.tsv"
)

SOURCE_RELS = (
    G769_EXACT_REL,
    G769_FRAME_REL,
    G769_CORE_REL,
    G769_MANIFEST_REL,
    G764_RUN_REL,
    G764_MANIFEST_REL,
    G683_AUDIT_REL,
    G683_REPEAT_REL,
    G762_AMOUNT_REL,
    G771_LEFT_REL,
    G773_DEFAULT_REL,
)

CHANNELS = (
    "AMOUNT",
    "VALUE",
    "BOUNDED_VALUE",
    "STATE_DRY",
    "STATE_MOIST",
    "PROCESS",
    "CLOSE",
    "OLY",
)

NULL_SPECS = {
    "N01_FOLIO_SLOT_POSITION": {
        "seed": 776,
        "strata": "PHYSICAL_FOLIO",
        "algorithm": (
            "For every replicate, sample without replacement exactly the observed "
            "number of ol tokens from all reader-exact cache slots on each physical "
            "folio; combine folio samples and recount position, paragraph-boundary, "
            "same-line unordered-pair and physically-adjacent-pair statistics."
        ),
    },
    "N02_FOLIO_POSITION_NEIGHBOR": {
        "seed": 778,
        "strata": "PHYSICAL_FOLIO|LINE_POSITION",
        "algorithm": (
            "For every replicate, sample without replacement exactly the observed "
            "number of ol tokens within each physical-folio by FIRST/MIDDLE/LAST "
            "stratum; recount distinct written left neighbors, right neighbors and "
            "ordered left-right frames. Neighbor exactness is not required."
        ),
    },
    "N03_REGISTER_REPEAT": {
        "seed": 774,
        "strata": "SECTION|LANGUAGE|HAND",
        "algorithm": (
            "For every replicate, sample without replacement exactly the observed "
            "number of ol tokens from reader-exact cache slots in each section, "
            "language and hand stratum; recount same-line unordered pairs and "
            "physically-adjacent pairs."
        ),
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_read_tsv(
    path: Path, *, selector: str, allowed_values: Iterable[str], columns: Sequence[str]
) -> list[dict[str, str]]:
    """Materialize mixed TSV rows only after selector rejection by vmanus-exp."""
    relative = path.relative_to(ROOT)
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(relative),
        "--selector", selector, "--columns", ",".join(columns),
    ]
    for value in sorted(set(allowed_values)):
        command.extend(["--allow", value])
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    if "GUARD_STATS" not in completed.stderr:
        raise AssertionError(f"guard statistics missing for {relative}")
    return list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))


def write_tsv(
    path: Path, rows: Sequence[Mapping[str, object]], fields: Sequence[str]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({field: serialise(row.get(field, "")) for field in fields})


def serialise(value: object) -> object:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return f"{value:.6f}"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if not match:
        raise ValueError(f"unrecognised page selector: {page}")
    return match.group(1)


def safe_z(observed: float, expected: float, variance: float) -> float:
    return (observed - expected) / math.sqrt(variance) if variance > 0 else 0.0


def target_rows() -> list[dict[str, str]]:
    rows = [row for row in read_tsv(ROOT / G769_EXACT_REL) if row["surface"] == "ol"]
    assert len(rows) == 376
    assert len({row["target_occurrence_id"] for row in rows}) == 376
    assert len({row["locus"] for row in rows}) == 340
    assert len({row["page"] for row in rows}) == 98
    assert len({row["physical_folio"] for row in rows}) == 61
    assert not any(row["page"].startswith("f84") for row in rows)
    for row in rows:
        tokens = row["written_line_eva"].split()
        assert tokens[int(row["ordinal"]) - 1] == "ol"
    return rows


def direction_items(signature: Mapping[str, object], channel: str) -> list[dict[str, object]]:
    evidence = signature.get("channel_evidence", {})
    if not isinstance(evidence, Mapping):
        return []
    items = evidence.get(channel, [])
    return [dict(item) for item in items if isinstance(item, Mapping)]


def build_position_atlas(rows: Sequence[dict[str, str]]) -> list[dict[str, object]]:
    by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_locus[row["locus"]].append(row)
    output: list[dict[str, object]] = []
    for row in rows:
        ordinal = int(row["ordinal"])
        tokens = row["written_line_eva"].split()
        ordinals = sorted(int(item["ordinal"]) for item in by_locus[row["locus"]])
        left_distances = [ordinal - value for value in ordinals if value < ordinal]
        right_distances = [value - ordinal for value in ordinals if value > ordinal]
        signature = json.loads(row["direct_signatures"])
        channels = list(signature["signature_channels"])
        eligible_counts = signature["semantic_donor_eligible_neighbor_evidence_counts"]
        output.append(
            {
                "target_occurrence_id": row["target_occurrence_id"],
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "locus": row["locus"],
                "section": row["section"],
                "language": row["language"],
                "hand": row["hand"],
                "ordinal": ordinal,
                "line_token_count": int(row["line_token_count"]),
                "line_position": row["line_position"],
                "normalized_line_position": float(row["normalized_line_position"]),
                "paragraph_start_line": int(row["paragraph_start_line"]),
                "paragraph_end_line": int(row["paragraph_end_line"]),
                "true_paragraph_opener": int(row["true_paragraph_opener"]),
                "true_paragraph_closer": int(row["true_paragraph_closer"]),
                "line_ol_multiplicity": len(ordinals),
                "previous_ol_distance": min(left_distances) if left_distances else "NONE",
                "next_ol_distance": min(right_distances) if right_distances else "NONE",
                "adjacent_ol_left": int(bool(left_distances and min(left_distances) == 1)),
                "adjacent_ol_right": int(bool(right_distances and min(right_distances) == 1)),
                "previous_surface": tokens[ordinal - 2] if ordinal > 1 else "LINE_START",
                "next_surface": tokens[ordinal] if ordinal < len(tokens) else "LINE_END",
                "direct_signature_channels": "|".join(channels) or "NONE",
                "direct_signature_channel_count": len(channels),
                "eligible_direct_neighbor_channels": "|".join(
                    channel for channel in CHANNELS if int(eligible_counts.get(channel, 0))
                )
                or "NONE",
                "eligible_direct_neighbor_evidence_count": sum(
                    int(value) for value in eligible_counts.values()
                ),
                "written_line_eva": row["written_line_eva"],
            }
        )
    return sorted(output, key=lambda row: str(row["target_occurrence_id"]))


def build_signature_matrix(rows: Sequence[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        signature = json.loads(row["direct_signatures"])
        selected = set(signature["signature_channels"])
        eligible = signature["semantic_donor_eligible_neighbor_evidence_counts"]
        record: dict[str, object] = {
            "target_occurrence_id": row["target_occurrence_id"],
            "page": row["page"],
            "physical_folio": row["physical_folio"],
            "locus": row["locus"],
            "ordinal": int(row["ordinal"]),
        }
        for channel in CHANNELS:
            items = direction_items(signature, channel)
            record[f"{channel.lower()}_present"] = int(channel in selected)
            record[f"{channel.lower()}_directions"] = (
                "|".join(sorted({str(item.get("direction", "NONE")) for item in items}))
                or "NONE"
            )
            record[f"{channel.lower()}_evidence_count"] = len(items)
            record[f"{channel.lower()}_eligible_neighbor_count"] = int(
                eligible.get(channel, 0)
            )
        output.append(record)
    return sorted(output, key=lambda row: str(row["target_occurrence_id"]))


def amount_position_ids(
    rows: Sequence[dict[str, str]], index: Mapping[tuple[str, int], str]
) -> set[str]:
    output: set[str] = set()
    source_rows = read_tsv(ROOT / G762_AMOUNT_REL)
    assert len(source_rows) == 16
    directed_edges = 0
    for row in source_rows:
        tokens = row["written_line_eva"].split()
        expression = row["amount_expression_eva"].split()
        sides = set(row["ol_sides_relative_to_amount"].split("|"))
        local: set[tuple[str, int]] = set()
        for start in range(len(tokens) - len(expression) + 1):
            if tokens[start : start + len(expression)] != expression:
                continue
            if "L" in sides and start > 0 and tokens[start - 1] == "ol":
                local.add((row["locus"], start))  # start is the 1-based ol ordinal here
            after = start + len(expression)
            if "R" in sides and after < len(tokens) and tokens[after] == "ol":
                local.add((row["locus"], after + 1))
        assert len(local) == int(row["ol_directed_edges"]), row["ol_amount_contact_id"]
        directed_edges += len(local)
        for key in local:
            assert key in index, key
            output.add(index[key])
    assert directed_edges == len(output) == 17
    return output


def build_evidence_sets(rows: Sequence[dict[str, str]]) -> dict[str, set[str]]:
    index = {
        (row["locus"], int(row["ordinal"])): row["target_occurrence_id"]
        for row in rows
    }
    frame_sets: defaultdict[str, set[str]] = defaultdict(set)
    for row in read_tsv(ROOT / G769_FRAME_REL):
        if row["target_surface"] == "ol":
            frame_sets[row["frame_id"]].add(row["target_occurrence_id"])
    amount = amount_position_ids(rows, index)
    strict_left = {
        row["target_occurrence_id"]
        for row in guarded_read_tsv(
            ROOT / G771_LEFT_REL,
            selector="page",
            allowed_values={row["page"] for row in rows},
            columns=("page", "target_occurrence_id", "strict_discriminator_eligible"),
        )
        if row["strict_discriminator_eligible"] == "1"
    }
    nominal = (
        frame_sets["F01_AMOUNT_DIRECT"]
        | frame_sets["F02_VALUE_DIRECT"]
        | frame_sets["F06_TARGET_BEFORE_PROCESS"]
    )
    field = frame_sets["F14_MEDIAL_TWO_SIDED_LINKER"] & (
        frame_sets["F15_STATE_TRANSITION_BRIDGE"]
        | frame_sets["F16_RELATIONAL_AMOUNT_ORDER"]
    )
    gdt773 = {
        index[(row["locus"], int(row["ordinal"]))]
        for row in read_tsv(ROOT / G773_DEFAULT_REL)
    }
    assert len(amount) == 17
    assert len(strict_left) == 14
    assert len(nominal) == 34
    assert len(field) == 38
    assert len(gdt773) == 15
    return {
        "A_GDT762_AMOUNT": amount,
        "S_GDT771_STRICT_LEFT": strict_left,
        "N_GDT769_R01_POSITIVE": nominal,
        "L_GDT769_R05_CONJUNCTION": field,
        "D_GDT773_CALIBRATION": gdt773,
    }


def build_evidence_atlas(
    rows: Sequence[dict[str, str]], evidence: Mapping[str, set[str]]
) -> tuple[list[dict[str, object]], Counter[str]]:
    legacy = {
        (row["locus"], int(row["ordinal"])): row
        for row in guarded_read_tsv(
            ROOT / G683_AUDIT_REL,
            selector="page",
            allowed_values={row["page"] for row in rows},
            columns=(
                "page", "locus", "ordinal", "working_translation_de",
                "evidence_type", "semantic_decision",
            ),
        )
    }
    output: list[dict[str, object]] = []
    masks: Counter[str] = Counter()
    for row in rows:
        occurrence_id = row["target_occurrence_id"]
        a = occurrence_id in evidence["A_GDT762_AMOUNT"]
        s = occurrence_id in evidence["S_GDT771_STRICT_LEFT"]
        n = occurrence_id in evidence["N_GDT769_R01_POSITIVE"]
        l = occurrence_id in evidence["L_GDT769_R05_CONJUNCTION"]
        d = occurrence_id in evidence["D_GDT773_CALIBRATION"]
        mask = "".join(letter for letter, value in (("A", a), ("S", s), ("N", n), ("L", l)) if value) or "NONE"
        masks[mask] += 1
        if l and not n:
            disposition = "FIELD_LINK_ONLY"
        elif n and not l:
            disposition = "NOMINAL_HEAD_ONLY"
        elif n and l:
            disposition = "FIELD_NOMINAL_OVERLAP"
        elif a or s:
            disposition = "AMOUNT_OR_STRICT_LEFT_ONLY"
        else:
            disposition = "UNTYPED"
        old = legacy[(row["locus"], int(row["ordinal"]))]
        signature = json.loads(row["direct_signatures"])
        output.append(
            {
                "target_occurrence_id": occurrence_id,
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "locus": row["locus"],
                "ordinal": int(row["ordinal"]),
                "evidence_mask": mask,
                "gdt762_amount_position": int(a),
                "gdt771_strict_left": int(s),
                "gdt769_r01_positive_occurrence": int(n),
                "gdt769_r05_conjunction_occurrence": int(l),
                "gdt773_calibration_case": int(d),
                "any_direct_signature": int(bool(signature["signature_channels"])),
                "structural_disposition": disposition,
                "gdt683_working_translation_de": old["working_translation_de"],
                "gdt683_evidence_type": old["evidence_type"],
                "gdt683_semantic_decision": old["semantic_decision"],
                "translation_credit": 0,
                "component_export_credit": 0,
            }
        )
    assert len(output) == 376
    assert set(item["gdt683_working_translation_de"] for item in output) == {"Grundansatz"}
    assert set(item["gdt683_evidence_type"] for item in output) == {
        "GDT664_PUBLISHED_LEARNED_WHOLE"
    }
    assert sum(mask != "NONE" for mask in (row["evidence_mask"] for row in output)) == 73
    assert masks == Counter(
        {
            "NONE": 303,
            "L": 26,
            "N": 19,
            "ANL": 7,
            "AS": 6,
            "S": 6,
            "NL": 4,
            "AN": 2,
            "SN": 1,
            "A": 1,
            "ASNL": 1,
        }
    )
    return sorted(output, key=lambda row: str(row["target_occurrence_id"])), masks


def subset_summary(
    group_id: str, axis: str, value: str, rows: Sequence[dict[str, str]]
) -> dict[str, object]:
    by_locus: defaultdict[str, list[int]] = defaultdict(list)
    for row in rows:
        by_locus[row["locus"]].append(int(row["ordinal"]))
    first = sum(row["line_position"] == "FIRST" for row in rows)
    middle = sum(row["line_position"] == "MIDDLE" for row in rows)
    last = sum(row["line_position"] == "LAST" for row in rows)
    repeated_lines = sum(len(values) > 1 for values in by_locus.values())
    repeated_occurrences = sum(len(values) for values in by_locus.values() if len(values) > 1)
    same_line_pairs = sum(len(values) * (len(values) - 1) // 2 for values in by_locus.values())
    adjacent_pairs = sum(
        right == left + 1
        for values in by_locus.values()
        for left, right in zip(sorted(values), sorted(values)[1:])
    )
    expected = sum(1 / int(row["line_token_count"]) for row in rows)
    variance = sum(
        (1 / int(row["line_token_count"]))
        * (1 - 1 / int(row["line_token_count"]))
        for row in rows
    )
    direct = [json.loads(row["direct_signatures"]) for row in rows]
    count = len(rows)
    return {
        "group_id": group_id,
        "group_axis": axis,
        "group_value": value,
        "occurrences": count,
        "loci": len(by_locus),
        "pages": len({row["page"] for row in rows}),
        "physical_folios": len({row["physical_folio"] for row in rows}),
        "line_first": first,
        "line_middle": middle,
        "line_last": last,
        "line_first_rate": first / count if count else 0.0,
        "line_middle_rate": middle / count if count else 0.0,
        "line_last_rate": last / count if count else 0.0,
        "paragraph_start_line": sum(int(row["paragraph_start_line"]) for row in rows),
        "paragraph_end_line": sum(int(row["paragraph_end_line"]) for row in rows),
        "true_paragraph_opener": sum(int(row["true_paragraph_opener"]) for row in rows),
        "true_paragraph_closer": sum(int(row["true_paragraph_closer"]) for row in rows),
        "mean_normalized_line_position": (
            sum(float(row["normalized_line_position"]) for row in rows) / count
            if count
            else 0.0
        ),
        "conditional_uniform_first_expected": expected,
        "conditional_uniform_first_z": safe_z(first, expected, variance),
        "conditional_uniform_last_z": safe_z(last, expected, variance),
        "repeated_lines": repeated_lines,
        "repeated_occurrences": repeated_occurrences,
        "same_line_unordered_pairs": same_line_pairs,
        "adjacent_ol_pairs": adjacent_pairs,
        "any_direct_signature_occurrences": sum(
            bool(item["signature_channels"]) for item in direct
        ),
        **{
            f"{channel.lower()}_occurrences": sum(
                channel in item["signature_channels"] for item in direct
            )
            for channel in CHANNELS
        },
    }


def build_register_summary(rows: Sequence[dict[str, str]]) -> list[dict[str, object]]:
    groups: list[tuple[str, str, str, Callable[[dict[str, str]], bool]]] = [
        ("ALL", "ALL", "ALL", lambda row: True),
        ("SECTION_B", "SECTION", "B", lambda row: row["section"] == "B"),
        ("SECTION_NON_B", "SECTION", "NON_B", lambda row: row["section"] != "B"),
        ("HAND_2", "HAND", "2", lambda row: row["hand"] == "2"),
        ("HAND_NON_2", "HAND", "NON_2", lambda row: row["hand"] != "2"),
    ]
    for section in sorted({row["section"] for row in rows}):
        groups.append(
            (
                f"SECTION_{section}_ALL",
                "SECTION",
                section,
                lambda row, section=section: row["section"] == section,
            )
        )
    for language in sorted({row["language"] for row in rows}):
        groups.append(
            (
                f"LANGUAGE_{language}",
                "LANGUAGE",
                language,
                lambda row, language=language: row["language"] == language,
            )
        )
    for hand in sorted({row["hand"] for row in rows}):
        groups.append(
            (
                f"HAND_{hand}_ALL",
                "HAND",
                hand,
                lambda row, hand=hand: row["hand"] == hand,
            )
        )
    return [
        subset_summary(group_id, axis, value, [row for row in rows if predicate(row)])
        for group_id, axis, value, predicate in groups
    ]


def build_repeat_atlas(rows: Sequence[dict[str, str]]) -> list[dict[str, object]]:
    by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_locus[row["locus"]].append(row)
    output: list[dict[str, object]] = []
    for locus, group in sorted(by_locus.items()):
        if len(group) < 2:
            continue
        group = sorted(group, key=lambda row: int(row["ordinal"]))
        ordinals = [int(row["ordinal"]) for row in group]
        distances = [right - left for left, right in zip(ordinals, ordinals[1:])]
        signature_count = sum(
            bool(json.loads(row["direct_signatures"])["signature_channels"])
            for row in group
        )
        adjacent_signature_tokens = 0
        for index, row in enumerate(group):
            adjacent = (
                (index > 0 and ordinals[index] - ordinals[index - 1] == 1)
                or (index + 1 < len(group) and ordinals[index + 1] - ordinals[index] == 1)
            )
            if adjacent and json.loads(row["direct_signatures"])["signature_channels"]:
                adjacent_signature_tokens += 1
        output.append(
            {
                "page": group[0]["page"],
                "physical_folio": group[0]["physical_folio"],
                "locus": locus,
                "section": group[0]["section"],
                "language": group[0]["language"],
                "hand": group[0]["hand"],
                "ol_multiplicity": len(group),
                "ol_occurrence_ids": "|".join(row["target_occurrence_id"] for row in group),
                "ol_ordinals": "|".join(map(str, ordinals)),
                "consecutive_ol_distances": "|".join(map(str, distances)),
                "same_line_unordered_pairs": len(group) * (len(group) - 1) // 2,
                "adjacent_ol_pairs": sum(distance == 1 for distance in distances),
                "signature_occurrences": signature_count,
                "adjacent_tokens_with_any_signature": adjacent_signature_tokens,
                "written_line_eva": group[0]["written_line_eva"],
            }
        )
    assert len(output) == 32
    assert Counter(row["ol_multiplicity"] for row in output) == Counter({2: 28, 3: 4})
    assert sum(int(row["adjacent_ol_pairs"]) for row in output) == 7
    assert sum(int(row["adjacent_tokens_with_any_signature"]) for row in output) == 0
    guarded_legacy_pairs = guarded_read_tsv(
        ROOT / G683_REPEAT_REL,
        selector="page",
        allowed_values={row["page"] for row in rows},
        columns=("page", "locus", "left_ordinal", "right_ordinal"),
    )
    assert len(guarded_legacy_pairs) == 7
    return output


def build_neighbor_summaries(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, int]]:
    surfaces: defaultdict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    frames: defaultdict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        tokens = row["written_line_eva"].split()
        ordinal = int(row["ordinal"])
        left = tokens[ordinal - 2] if ordinal > 1 else "LINE_START"
        right = tokens[ordinal] if ordinal < len(tokens) else "LINE_END"
        surfaces["LEFT", left].append(row)
        surfaces["RIGHT", right].append(row)
        frames[left, right].append(row)
    surface_rows: list[dict[str, object]] = []
    for (direction, surface), group in sorted(
        surfaces.items(), key=lambda item: (item[0][0], -len(item[1]), item[0][1])
    ):
        surface_rows.append(
            {
                "direction": direction,
                "neighbor_surface": surface,
                "occurrences": len(group),
                "pages": len({row["page"] for row in group}),
                "physical_folios": len({row["physical_folio"] for row in group}),
                "section_counts": dict(sorted(Counter(row["section"] for row in group).items())),
            }
        )
    frame_rows: list[dict[str, object]] = []
    for (left, right), group in sorted(
        frames.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        if len(group) < 2:
            continue
        frame_rows.append(
            {
                "left_surface": left,
                "right_surface": right,
                "frame_occurrences": len(group),
                "pages": len({row["page"] for row in group}),
                "physical_folios": len({row["physical_folio"] for row in group}),
                "occurrence_ids": "|".join(row["target_occurrence_id"] for row in group),
                "loci": "|".join(row["locus"] for row in group),
            }
        )
    metrics = {
        "unique_left_neighbors": len({surface for direction, surface in surfaces if direction == "LEFT"}),
        "unique_right_neighbors": len({surface for direction, surface in surfaces if direction == "RIGHT"}),
        "unique_neighbor_frames": len(frames),
        "repeated_neighbor_frames": len(frame_rows),
    }
    assert metrics == {
        "unique_left_neighbors": 225,
        "unique_right_neighbors": 188,
        "unique_neighbor_frames": 367,
        "repeated_neighbor_frames": 7,
    }
    return surface_rows, frame_rows, metrics


def build_exact_slots() -> tuple[list[dict[str, object]], dict[str, object]]:
    core = load_module("gdt769_structural_audit_core", ROOT / G769_CORE_REL)
    _, environment = core.load_guarded_environment(ROOT)
    context = environment["context"]
    line_meta = environment["line_meta"]
    assert dict(environment["guard"]) == {
        "selected": 4137,
        "skipped_forbidden": 98,
        "skipped_not_allowed": 1150,
    }
    output: list[dict[str, object]] = []
    for line_id, (locus, line) in enumerate(sorted(context.by_line.items())):
        meta = line_meta[locus]
        for index, token in enumerate(line):
            if not bool(context.exact[(locus, int(token["token_index"]))]):
                continue
            page = str(token["page"])
            assert not page.startswith("f84")
            position = (
                "SINGLE"
                if len(line) == 1
                else "FIRST"
                if index == 0
                else "LAST"
                if index == len(line) - 1
                else "MIDDLE"
            )
            output.append(
                {
                    "slot_id": len(output),
                    "line_id": line_id,
                    "line_ordinal": index + 1,
                    "locus": locus,
                    "page": page,
                    "physical_folio": physical_folio(page),
                    "section": str(token["section"]),
                    "language": str(token["language"]),
                    "hand": str(token["hand"]),
                    "line_position": position,
                    "is_line_first": int(index == 0),
                    "is_line_middle": int(index != 0 and index != len(line) - 1),
                    "is_line_last": int(index == len(line) - 1),
                    "true_paragraph_opener": int(
                        index == 0 and str(meta["paragraph_start"]) == "1"
                    ),
                    "true_paragraph_closer": int(
                        index == len(line) - 1 and str(meta["paragraph_end"]) == "1"
                    ),
                    "left_surface": str(line[index - 1]["eva"]) if index else "LINE_START",
                    "right_surface": (
                        str(line[index + 1]["eva"]) if index + 1 < len(line) else "LINE_END"
                    ),
                }
            )
    assert len(output) == 24090
    return output, dict(environment["guard"])


def select_by_strata(
    rng: random.Random,
    pools: Mapping[tuple[str, ...], list[int]],
    target_counts: Mapping[tuple[str, ...], int],
) -> list[int]:
    selected: list[int] = []
    for key in sorted(target_counts):
        count = target_counts[key]
        assert count <= len(pools[key]), (key, count, len(pools[key]))
        selected.extend(rng.sample(pools[key], count))
    return selected


def quantile(sorted_values: Sequence[int], proportion: float) -> int:
    return sorted_values[int(proportion * (len(sorted_values) - 1))]


def null_row(
    null_id: str,
    metric: str,
    observed: int,
    values: list[int],
    iterations: int,
) -> dict[str, object]:
    values.sort()
    spec = NULL_SPECS[null_id]
    return {
        "null_id": null_id,
        "seed": spec["seed"],
        "iterations": iterations,
        "stratification": spec["strata"],
        "metric": metric,
        "observed": observed,
        "null_mean": sum(values) / iterations,
        "null_q025": quantile(values, 0.025),
        "null_median": quantile(values, 0.5),
        "null_q975": quantile(values, 0.975),
        "p_lower_add_one": (1 + sum(value <= observed for value in values)) / (iterations + 1),
        "p_upper_add_one": (1 + sum(value >= observed for value in values)) / (iterations + 1),
        "algorithm": spec["algorithm"],
    }


def simulation_nulls(
    target: Sequence[dict[str, str]], slots: Sequence[dict[str, object]], iterations: int
) -> list[dict[str, object]]:
    target_by_locus: defaultdict[str, list[int]] = defaultdict(list)
    for row in target:
        target_by_locus[row["locus"]].append(int(row["ordinal"]))
    observed = {
        "line_first": sum(row["line_position"] == "FIRST" for row in target),
        "line_middle": sum(row["line_position"] == "MIDDLE" for row in target),
        "line_last": sum(row["line_position"] == "LAST" for row in target),
        "true_paragraph_opener": sum(int(row["true_paragraph_opener"]) for row in target),
        "true_paragraph_closer": sum(int(row["true_paragraph_closer"]) for row in target),
        "same_line_unordered_pairs": sum(
            len(values) * (len(values) - 1) // 2 for values in target_by_locus.values()
        ),
        "adjacent_pairs": sum(
            right == left + 1
            for values in target_by_locus.values()
            for left, right in zip(sorted(values), sorted(values)[1:])
        ),
    }
    lefts: set[str] = set()
    rights: set[str] = set()
    frames: set[tuple[str, str]] = set()
    for row in target:
        tokens = row["written_line_eva"].split()
        ordinal = int(row["ordinal"])
        left = tokens[ordinal - 2] if ordinal > 1 else "LINE_START"
        right = tokens[ordinal] if ordinal < len(tokens) else "LINE_END"
        lefts.add(left)
        rights.add(right)
        frames.add((left, right))
    observed.update(
        {
            "unique_left_neighbors": len(lefts),
            "unique_right_neighbors": len(rights),
            "unique_neighbor_frames": len(frames),
        }
    )

    output: list[dict[str, object]] = []

    # N01: physical-folio counts fixed, every reader-exact slot exchangeable.
    n01 = "N01_FOLIO_SLOT_POSITION"
    pools01: defaultdict[tuple[str, ...], list[int]] = defaultdict(list)
    for index, slot in enumerate(slots):
        pools01[(str(slot["physical_folio"]),)].append(index)
    counts01 = Counter((row["physical_folio"],) for row in target)
    values01 = {metric: [] for metric in (
        "line_first",
        "line_middle",
        "line_last",
        "true_paragraph_opener",
        "true_paragraph_closer",
        "same_line_unordered_pairs",
        "adjacent_pairs",
    )}
    rng = random.Random(int(NULL_SPECS[n01]["seed"]))
    for _ in range(iterations):
        chosen = select_by_strata(rng, pools01, counts01)
        chosen_set = set(chosen)
        line_counts = Counter(int(slots[index]["line_id"]) for index in chosen)
        values01["line_first"].append(
            sum(int(slots[index]["is_line_first"]) for index in chosen)
        )
        values01["line_middle"].append(
            sum(int(slots[index]["is_line_middle"]) for index in chosen)
        )
        values01["line_last"].append(
            sum(int(slots[index]["is_line_last"]) for index in chosen)
        )
        values01["true_paragraph_opener"].append(
            sum(int(slots[index]["true_paragraph_opener"]) for index in chosen)
        )
        values01["true_paragraph_closer"].append(
            sum(int(slots[index]["true_paragraph_closer"]) for index in chosen)
        )
        values01["same_line_unordered_pairs"].append(
            sum(value * (value - 1) // 2 for value in line_counts.values())
        )
        values01["adjacent_pairs"].append(
            sum(
                index + 1 in chosen_set
                and int(slots[index + 1]["line_id"]) == int(slot["line_id"])
                and int(slots[index + 1]["line_ordinal"])
                == int(slot["line_ordinal"]) + 1
                for index in chosen
                for slot in (slots[index],)
                if index + 1 < len(slots)
            )
        )
    output.extend(
        null_row(n01, metric, observed[metric], values, iterations)
        for metric, values in values01.items()
    )

    # N02: folio and target line-position counts fixed before neighbor diversity.
    n02 = "N02_FOLIO_POSITION_NEIGHBOR"
    pools02: defaultdict[tuple[str, ...], list[int]] = defaultdict(list)
    for index, slot in enumerate(slots):
        pools02[(str(slot["physical_folio"]), str(slot["line_position"]))].append(index)
    counts02 = Counter((row["physical_folio"], row["line_position"]) for row in target)
    values02 = {metric: [] for metric in (
        "unique_left_neighbors",
        "unique_right_neighbors",
        "unique_neighbor_frames",
    )}
    rng = random.Random(int(NULL_SPECS[n02]["seed"]))
    for _ in range(iterations):
        chosen = select_by_strata(rng, pools02, counts02)
        values02["unique_left_neighbors"].append(
            len({str(slots[index]["left_surface"]) for index in chosen})
        )
        values02["unique_right_neighbors"].append(
            len({str(slots[index]["right_surface"]) for index in chosen})
        )
        values02["unique_neighbor_frames"].append(
            len(
                {
                    (str(slots[index]["left_surface"]), str(slots[index]["right_surface"]))
                    for index in chosen
                }
            )
        )
    output.extend(
        null_row(n02, metric, observed[metric], values, iterations)
        for metric, values in values02.items()
    )

    # N03: register counts fixed, local repetition assessed without semantic tags.
    n03 = "N03_REGISTER_REPEAT"
    pools03: defaultdict[tuple[str, ...], list[int]] = defaultdict(list)
    for index, slot in enumerate(slots):
        pools03[
            (str(slot["section"]), str(slot["language"]), str(slot["hand"]))
        ].append(index)
    counts03 = Counter((row["section"], row["language"], row["hand"]) for row in target)
    values03 = {"same_line_unordered_pairs": [], "adjacent_pairs": []}
    rng = random.Random(int(NULL_SPECS[n03]["seed"]))
    for _ in range(iterations):
        chosen = select_by_strata(rng, pools03, counts03)
        chosen_set = set(chosen)
        line_counts = Counter(int(slots[index]["line_id"]) for index in chosen)
        values03["same_line_unordered_pairs"].append(
            sum(value * (value - 1) // 2 for value in line_counts.values())
        )
        values03["adjacent_pairs"].append(
            sum(
                index + 1 in chosen_set
                and int(slots[index + 1]["line_id"]) == int(slot["line_id"])
                and int(slots[index + 1]["line_ordinal"])
                == int(slot["line_ordinal"]) + 1
                for index in chosen
                for slot in (slots[index],)
                if index + 1 < len(slots)
            )
        )
    output.extend(
        null_row(n03, metric, observed[metric], values, iterations)
        for metric, values in values03.items()
    )
    return output


def build_folio_holdouts(
    rows: Sequence[dict[str, str]], evidence: Mapping[str, set[str]]
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for held in sorted({row["physical_folio"] for row in rows}):
        subset = [row for row in rows if row["physical_folio"] != held]
        summary = subset_summary(f"HOLD_{held}", "PHYSICAL_FOLIO", held, subset)
        ids = {row["target_occurrence_id"] for row in subset}
        summary.update(
            {
                "held_folio": held,
                "removed_occurrences": len(rows) - len(subset),
                "r01_positive_remaining": len(ids & evidence["N_GDT769_R01_POSITIVE"]),
                "r05_conjunction_remaining": len(ids & evidence["L_GDT769_R05_CONJUNCTION"]),
                "gdt762_amount_remaining": len(ids & evidence["A_GDT762_AMOUNT"]),
                "gdt771_strict_left_remaining": len(ids & evidence["S_GDT771_STRICT_LEFT"]),
                "typed_union_remaining": len(
                    ids
                    & (
                        evidence["A_GDT762_AMOUNT"]
                        | evidence["S_GDT771_STRICT_LEFT"]
                        | evidence["N_GDT769_R01_POSITIVE"]
                        | evidence["L_GDT769_R05_CONJUNCTION"]
                    )
                ),
            }
        )
        output.append(summary)
    assert len(output) == 61
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=20000)
    args = parser.parse_args()
    if args.iterations <= 0:
        raise ValueError("iterations must be positive")
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = target_rows()
    position_atlas = build_position_atlas(rows)
    signature_matrix = build_signature_matrix(rows)
    evidence = build_evidence_sets(rows)
    evidence_atlas, masks = build_evidence_atlas(rows, evidence)
    repeat_atlas = build_repeat_atlas(rows)
    neighbor_surfaces, neighbor_frames, neighbor_metrics = build_neighbor_summaries(rows)
    register_summary = build_register_summary(rows)
    slots, guard = build_exact_slots()
    null_rows = simulation_nulls(rows, slots, args.iterations)
    folio_holdouts = build_folio_holdouts(rows, evidence)

    write_tsv(output_dir / "OL_376_STRUCTURAL_POSITION_ATLAS.tsv", position_atlas, list(position_atlas[0]))
    write_tsv(output_dir / "OL_DIRECT_SIGNATURE_DIRECTION_MATRIX.tsv", signature_matrix, list(signature_matrix[0]))
    write_tsv(output_dir / "OL_EVIDENCE_VENN_DISPATCH.tsv", evidence_atlas, list(evidence_atlas[0]))
    write_tsv(output_dir / "OL_SELF_REPEAT_ATLAS.tsv", repeat_atlas, list(repeat_atlas[0]))
    write_tsv(output_dir / "OL_NEIGHBOR_SURFACE_SUMMARY.tsv", neighbor_surfaces, list(neighbor_surfaces[0]))
    write_tsv(output_dir / "OL_REPEATED_NEIGHBOR_FRAMES.tsv", neighbor_frames, list(neighbor_frames[0]))
    write_tsv(output_dir / "OL_REGISTER_SUMMARY.tsv", register_summary, list(register_summary[0]))
    write_tsv(output_dir / "OL_FOLIO_HOLDOUT.tsv", folio_holdouts, list(folio_holdouts[0]))
    write_tsv(output_dir / "OL_POSITION_MATCHED_NULL.tsv", null_rows, list(null_rows[0]))

    signature_counts = Counter()
    signature_directions: defaultdict[str, Counter[str]] = defaultdict(Counter)
    eligible_direct_counts = Counter()
    any_signatures = 0
    any_eligible = 0
    for row in rows:
        signature = json.loads(row["direct_signatures"])
        channels = signature["signature_channels"]
        signature_counts.update(channels)
        for channel in CHANNELS:
            signature_directions[channel].update(
                str(item.get("direction", "NONE"))
                for item in direction_items(signature, channel)
            )
        any_signatures += bool(channels)
        eligible = signature["semantic_donor_eligible_neighbor_evidence_counts"]
        eligible_direct_counts.update(
            {
                channel: int(value)
                for channel, value in eligible.items()
                if int(value)
            }
        )
        any_eligible += any(int(value) for value in eligible.values())

    selected_union = (
        evidence["A_GDT762_AMOUNT"]
        | evidence["S_GDT771_STRICT_LEFT"]
        | evidence["N_GDT769_R01_POSITIVE"]
        | evidence["L_GDT769_R05_CONJUNCTION"]
    )
    calibration = evidence["D_GDT773_CALIBRATION"]
    row_by_id = {row["target_occurrence_id"]: row for row in rows}
    register_by_id = {str(row["group_id"]): row for row in register_summary}
    compact_nulls: defaultdict[str, dict[str, object]] = defaultdict(dict)
    for row in null_rows:
        compact_nulls[str(row["null_id"])][str(row["metric"])] = {
            key: row[key]
            for key in (
                "observed",
                "null_mean",
                "null_q025",
                "null_median",
                "null_q975",
                "p_lower_add_one",
                "p_upper_add_one",
            )
        }

    def holdout_range(field: str) -> dict[str, float]:
        values = [float(row[field]) for row in folio_holdouts]
        return {"minimum": min(values), "maximum": max(values)}

    result = {
        "status": "PASS__376_OL__STRUCTURAL_AUDIT__NO_NEW_PAGE",
        "source_files": {
            str(path): sha256(ROOT / path) for path in SOURCE_RELS
        },
        "guarded_cache": {
            "guard": guard,
            "reader_exact_slots": len(slots),
            "forbidden_page_access": False,
        },
        "null_contract": {
            "iterations": args.iterations,
            "quantiles": "sorted_values[floor(p*(iterations-1))]",
            "tail_probabilities": "add-one empirical: (1 + count)/(iterations + 1)",
            "specifications": NULL_SPECS,
        },
        "null_results": dict(compact_nulls),
        "corpus": {
            "occurrences": len(rows),
            "loci": len({row["locus"] for row in rows}),
            "pages": len({row["page"] for row in rows}),
            "physical_folios": len({row["physical_folio"] for row in rows}),
            "line_position_counts": dict(sorted(Counter(row["line_position"] for row in rows).items())),
            "paragraph_start_line_occurrences": sum(int(row["paragraph_start_line"]) for row in rows),
            "paragraph_end_line_occurrences": sum(int(row["paragraph_end_line"]) for row in rows),
            "true_paragraph_openers": sum(int(row["true_paragraph_opener"]) for row in rows),
            "true_paragraph_closers": sum(int(row["true_paragraph_closer"]) for row in rows),
        },
        "repetition": {
            "repeated_lines": len(repeat_atlas),
            "double_lines": sum(int(row["ol_multiplicity"]) == 2 for row in repeat_atlas),
            "triple_lines": sum(int(row["ol_multiplicity"]) == 3 for row in repeat_atlas),
            "repeated_occurrences": sum(int(row["ol_multiplicity"]) for row in repeat_atlas),
            "same_line_unordered_pairs": sum(int(row["same_line_unordered_pairs"]) for row in repeat_atlas),
            "adjacent_pairs": sum(int(row["adjacent_ol_pairs"]) for row in repeat_atlas),
            "adjacent_tokens_with_any_direct_signature": sum(
                int(row["adjacent_tokens_with_any_signature"]) for row in repeat_atlas
            ),
        },
        "neighbors": neighbor_metrics,
        "direct_signatures": {
            "any_signature_occurrences": any_signatures,
            "no_signature_occurrences": len(rows) - any_signatures,
            "channel_occurrence_counts": dict(sorted(signature_counts.items())),
            "channel_direction_counts": {
                channel: dict(sorted(counts.items()))
                for channel, counts in sorted(signature_directions.items())
                if counts
            },
            "semantically_eligible_direct_neighbor_occurrences": any_eligible,
            "semantically_eligible_neighbor_evidence_counts": dict(
                sorted(eligible_direct_counts.items())
            ),
        },
        "evidence_sets": {
            key: len(value) for key, value in evidence.items()
        },
        "evidence_mask_counts": dict(sorted(masks.items())),
        "typed_union_occurrences": len(selected_union),
        "untyped_occurrences": len(rows) - len(selected_union),
        "gdt773_selection_enrichment": {
            "calibration_cases": len(calibration),
            "calibration_in_typed_union": len(calibration & selected_union),
            "global_typed_union": len(selected_union),
            "calibration_with_direct_signature": sum(
                bool(json.loads(row_by_id[occurrence_id]["direct_signatures"])["signature_channels"])
                for occurrence_id in calibration
            ),
            "global_with_direct_signature": any_signatures,
        },
        "legacy_gdt683_crosswalk": {
            "grundansatz_occurrences": sum(
                row["gdt683_working_translation_de"] == "Grundansatz"
                for row in evidence_atlas
            ),
            "single_inherited_evidence_type": "GDT664_PUBLISHED_LEARNED_WHOLE",
            "independent_contextual_confirmations_added": 0,
        },
        "register_highlights": {
            group_id: {
                key: register_by_id[group_id][key]
                for key in (
                    "occurrences",
                    "line_first",
                    "line_middle",
                    "line_last",
                    "conditional_uniform_first_z",
                    "repeated_occurrences",
                    "same_line_unordered_pairs",
                    "any_direct_signature_occurrences",
                )
            }
            for group_id in ("SECTION_B", "SECTION_NON_B", "HAND_2", "HAND_NON_2")
        },
        "physical_folio_holdout_ranges": {
            field: holdout_range(field)
            for field in (
                "occurrences",
                "line_first_rate",
                "line_middle_rate",
                "line_last_rate",
                "conditional_uniform_first_z",
                "any_direct_signature_occurrences",
                "amount_occurrences",
                "process_occurrences",
                "close_occurrences",
                "r01_positive_remaining",
                "r05_conjunction_remaining",
                "typed_union_remaining",
            )
        },
        "claim_ceiling": (
            "Structural positions, recurrence, exact neighboring surfaces, authored "
            "signature channels and analyst-model evidence sets only. No lexeme, "
            "plaintext, component, language, substance or operation is confirmed."
        ),
    }
    with (output_dir / "STRUCTURAL_AUDIT_RESULT.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
