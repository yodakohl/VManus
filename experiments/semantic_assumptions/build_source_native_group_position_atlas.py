#!/usr/bin/env python3
"""Build a complete exact-family-form position atlas from the confirmed edge layer."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
EDGE = RESULTS / "source_native_edge_grammar.json"
EDGE_VALIDATION = RESULTS / "source_native_edge_grammar_validation.json"
SPEC = BASE / "SOURCE_NATIVE_GROUP_POSITION_ATLAS_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_TSV = RESULTS / "source_native_group_position_atlas.tsv"
OUT_JSON = RESULTS / "source_native_group_position_atlas.json"
OUT_REPORT = RESULTS / "source_native_group_position_atlas_report.md"

FROZEN = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    EDGE: "2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
}
CONTRASTS = {
    "FIRST_LAST": ("FIRST", "LAST"),
    "EDGE_CORE": ("EDGE", "CORE"),
}
FIELDS = [
    "family_surface", "total_count", "physical_folios", "pages",
    "first_count", "last_count", "core_count", "single_count",
    "effective_folios", "maximum_folio_share", "effective_sections",
    "currier_a_count", "currier_b_count", "currier_unknown_count",
    "first_last_support", "first_last_log_odds_ratio",
    "first_last_positive_folds", "first_last_negative_folds",
    "first_last_minimum_fold", "first_last_maximum_fold", "first_last_label",
    "edge_core_support", "edge_core_log_odds_ratio",
    "edge_core_positive_folds", "edge_core_negative_folds",
    "edge_core_minimum_fold", "edge_core_maximum_fold", "edge_core_label",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.fullmatch(r"(f[0-9]+)[rv][0-9]*", page)
    if match is None:
        raise ValueError(f"bad page: {page}")
    return match.group(1)


def role(row: dict[str, str]) -> str:
    index = int(row["consensus_group_index"])
    count = int(row["consensus_group_count"])
    if count == 1:
        if index != 1:
            raise ValueError("single-group index drift")
        return "SINGLE"
    if index == 1:
        return "FIRST"
    if index == count:
        return "LAST"
    if not 1 < index < count:
        raise ValueError("group index drift")
    return "CORE"


def contrast_role(position: str, contrast: str) -> str | None:
    if contrast == "FIRST_LAST":
        return position if position in {"FIRST", "LAST"} else None
    if contrast == "EDGE_CORE":
        if position in {"FIRST", "LAST"}:
            return "EDGE"
        return "CORE" if position == "CORE" else None
    raise ValueError(contrast)


def log_odds(a: int, b: int, c: int, d: int) -> float:
    return math.log((a + 0.5) / (b + 0.5)) - math.log((c + 0.5) / (d + 0.5))


def effective_count(values: Counter[str]) -> float:
    total = sum(values.values())
    if total == 0:
        return 0.0
    entropy = -sum((n / total) * math.log(n / total) for n in values.values())
    return math.exp(entropy)


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing to overwrite group-position atlas")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    edge = json.loads(EDGE.read_text(encoding="utf-8"))
    validation = json.loads(EDGE_VALIDATION.read_text(encoding="utf-8"))
    if edge["decision"] != "CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR":
        raise SystemExit("source-native edge grammar is not confirmed")
    if not all(edge["target_gates"].values()):
        raise SystemExit("source-native edge target gates are not all true")
    if validation["status"] != "PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION":
        raise SystemExit("source-native edge validation is not PASS")

    with GROUPS.open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    rows = []
    for raw in source:
        if raw["strict_zero_alternative"] != "1" or raw["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        rows.append({
            "surface": raw["family_surface"], "folio": folio(raw["page"]),
            "page": raw["page"], "section": raw["section"],
            "currier": raw["currier"], "role": role(raw),
        })
    if len(rows) != 21899:
        raise ValueError("strict prose count drift")
    roles = Counter(row["role"] for row in rows)
    if roles != Counter({"CORE": 16528, "FIRST": 2676, "LAST": 2676, "SINGLE": 19}):
        raise ValueError("role count drift")
    folios = sorted({row["folio"] for row in rows})
    if len(folios) != 94:
        raise ValueError("folio count drift")

    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_surface[row["surface"]].append(row)
    if len(by_surface) != 2856:
        raise ValueError("family-surface inventory drift")

    global_cells: dict[str, Counter[str]] = {}
    folio_cells: dict[str, dict[str, Counter[str]]] = {}
    surface_cells: dict[str, dict[str, Counter[str]]] = {}
    surface_folio_cells: dict[str, dict[str, dict[str, Counter[str]]]] = {}
    for contrast in CONTRASTS:
        global_cells[contrast] = Counter()
        folio_cells[contrast] = defaultdict(Counter)
        surface_cells[contrast] = defaultdict(Counter)
        surface_folio_cells[contrast] = defaultdict(lambda: defaultdict(Counter))
        for row in rows:
            state = contrast_role(row["role"], contrast)
            if state is None:
                continue
            global_cells[contrast][state] += 1
            folio_cells[contrast][row["folio"]][state] += 1
            surface_cells[contrast][row["surface"]][state] += 1
            surface_folio_cells[contrast][row["surface"]][row["folio"]][state] += 1

    output = []
    for surface in sorted(by_surface):
        observed = by_surface[surface]
        role_counts = Counter(row["role"] for row in observed)
        folio_counts = Counter(row["folio"] for row in observed)
        section_counts = Counter(row["section"] for row in observed)
        currier_counts = Counter(row["currier"] for row in observed)
        record: dict[str, object] = {
            "family_surface": surface,
            "total_count": len(observed),
            "physical_folios": len(folio_counts),
            "pages": len({row["page"] for row in observed}),
            "first_count": role_counts["FIRST"],
            "last_count": role_counts["LAST"],
            "core_count": role_counts["CORE"],
            "single_count": role_counts["SINGLE"],
            "effective_folios": effective_count(folio_counts),
            "maximum_folio_share": max(folio_counts.values()) / len(observed),
            "effective_sections": effective_count(section_counts),
            "currier_a_count": currier_counts["A"],
            "currier_b_count": currier_counts["B"],
            "currier_unknown_count": currier_counts[""],
        }
        general_eligible = len(observed) >= 20 and len(folio_counts) >= 10
        for contrast, (positive_state, negative_state) in CONTRASTS.items():
            cells = surface_cells[contrast][surface]
            global_count = global_cells[contrast]
            a, b = cells[positive_state], cells[negative_state]
            c = global_count[positive_state] - a
            d = global_count[negative_state] - b
            coefficient = log_odds(a, b, c, d)
            fold_values = []
            for held in folios:
                own_held = surface_folio_cells[contrast][surface][held]
                all_held = folio_cells[contrast][held]
                aa = a - own_held[positive_state]
                bb = b - own_held[negative_state]
                cc = c - (all_held[positive_state] - own_held[positive_state])
                dd = d - (all_held[negative_state] - own_held[negative_state])
                fold_values.append(log_odds(aa, bb, cc, dd))
            positive_folds = sum(value > 0 for value in fold_values)
            negative_folds = sum(value < 0 for value in fold_values)
            support = a + b
            if not general_eligible or support < 20:
                label = "INSUFFICIENT"
            elif coefficient >= 1.0 and positive_folds >= 90:
                label = f"{positive_state}_ASSOCIATED"
            elif coefficient <= -1.0 and negative_folds >= 90:
                label = f"{negative_state}_ASSOCIATED"
            else:
                label = "UNRESOLVED"
            prefix = contrast.lower()
            record.update({
                f"{prefix}_support": support,
                f"{prefix}_log_odds_ratio": coefficient,
                f"{prefix}_positive_folds": positive_folds,
                f"{prefix}_negative_folds": negative_folds,
                f"{prefix}_minimum_fold": min(fold_values),
                f"{prefix}_maximum_fold": max(fold_values),
                f"{prefix}_label": label,
            })
        output.append(record)

    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    labels = {
        "FIRST_LAST": Counter(row["first_last_label"] for row in output),
        "EDGE_CORE": Counter(row["edge_core_label"] for row in output),
    }
    occurrence_coverage = {
        "FIRST_LAST": Counter(), "EDGE_CORE": Counter(),
    }
    for row in output:
        occurrence_coverage["FIRST_LAST"][row["first_last_label"]] += int(row["total_count"])
        occurrence_coverage["EDGE_CORE"][row["edge_core_label"]] += int(row["total_count"])
    strongest_first = sorted(
        (row for row in output if row["first_last_label"] == "FIRST_ASSOCIATED"),
        key=lambda row: (-float(row["first_last_log_odds_ratio"]), row["family_surface"]),
    )[:12]
    strongest_last = sorted(
        (row for row in output if row["first_last_label"] == "LAST_ASSOCIATED"),
        key=lambda row: (float(row["first_last_log_odds_ratio"]), row["family_surface"]),
    )[:12]
    strongest_edge = sorted(
        (row for row in output if row["edge_core_label"] == "EDGE_ASSOCIATED"),
        key=lambda row: (-float(row["edge_core_log_odds_ratio"]), row["family_surface"]),
    )[:12]
    strongest_core = sorted(
        (row for row in output if row["edge_core_label"] == "CORE_ASSOCIATED"),
        key=lambda row: (float(row["edge_core_log_odds_ratio"]), row["family_surface"]),
    )[:12]
    result = {
        "experiment": "SOURCE_NATIVE_GROUP_POSITION_ATLAS",
        "status": "PASS_DESCRIPTIVE_EXACT_GROUP_POSITION_DECOMPOSITION",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, BUILDER)},
        "counts": {
            "strict_confirmed_prose_groups": len(rows),
            "physical_folios": len(folios),
            "family_surfaces": len(output),
            "role_counts": dict(sorted(roles.items())),
            "eligible_surface_types": sum(
                int(row["total_count"]) >= 20 and int(row["physical_folios"]) >= 10
                for row in output
            ),
            "labels": {key: dict(sorted(value.items())) for key, value in labels.items()},
            "occurrences_by_label": {
                key: dict(sorted(value.items())) for key, value in occurrence_coverage.items()
            },
        },
        "classification_rule": {
            "minimum_total_occurrences": 20,
            "minimum_physical_folios": 10,
            "minimum_contrast_support": 20,
            "minimum_absolute_log_odds_ratio": 1.0,
            "minimum_same_direction_leave_folio_out_folds": 90,
            "total_folds": 94,
            "separately_confirmatory": False,
        },
        "strongest_first": strongest_first,
        "strongest_last": strongest_last,
        "strongest_edge": strongest_edge,
        "strongest_core": strongest_core,
        "tsv_sha256": sha(OUT_TSV),
        "english_glosses": 0,
        "claim_ceiling": (
            "Complete descriptive decomposition of recurring exact STA-family group forms under the "
            "already confirmed source-native edge architecture. Position labels are stable relative "
            "associations, not exclusive positions, START/STOP words, function/content parts of "
            "speech, sounds, morphemes, lexemes, plaintext, language, cipher, or translation."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    first_text = ", ".join(row["family_surface"] for row in strongest_first[:6])
    last_text = ", ".join(row["family_surface"] for row in strongest_last[:6])
    edge_text = ", ".join(row["family_surface"] for row in strongest_edge[:6])
    core_text = ", ".join(row["family_surface"] for row in strongest_core[:6])
    report = f"""# Source-native exact-group position atlas

Status: **PASS_DESCRIPTIVE_EXACT_GROUP_POSITION_DECOMPOSITION**

The lossless strict prose layer contains **{len(rows):,}** construction-group
occurrences, **{len(output):,}** exact STA-family surfaces, and **{len(folios)}**
physical folios. **{result['counts']['eligible_surface_types']}** surfaces meet
the common support gate.

Among complete surfaces, the conservative first-versus-last rule identifies
**{labels['FIRST_LAST']['FIRST_ASSOCIATED']}** first-associated and
**{labels['FIRST_LAST']['LAST_ASSOCIATED']}** last-associated forms. The
strongest are `{first_text}` toward the first position and `{last_text}` toward
the last position. The independent edge-versus-core view identifies
**{labels['EDGE_CORE']['EDGE_ASSOCIATED']}** edge-associated and
**{labels['EDGE_CORE']['CORE_ASSOCIATED']}** core-associated forms; leading
examples are `{edge_text}` and `{core_text}`.

This is the first complete source-native whole-group form inventory attached to
the confirmed opening/core/closing architecture. The associations are relative,
not exclusive: many listed forms also occur elsewhere in a locus. They improve
the formal record map but do not identify START/STOP words, parts of speech,
sounds, morphemes, lexemes, plaintext, language, cipher, or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": result["status"], "forms": len(output),
        "first_last": result["counts"]["labels"]["FIRST_LAST"],
        "edge_core": result["counts"]["labels"]["EDGE_CORE"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
