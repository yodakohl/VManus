#!/usr/bin/env python3
"""Select one recurrent structural slot without using its occupant identity."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "consensus_structural_record_interlinear_v1.tsv"
SOURCE_VALIDATION = RESULTS / "consensus_structural_record_interlinear_v1_validation.json"
METHOD = BASE / "CSRMS001_MASKED_RECURRENT_SLOT_SELECTION_METHOD.md"
BUILDER = Path(__file__).resolve()
OUT_TSV = RESULTS / "csrms001_masked_recurrent_slot_selection.tsv"
OUT_JSON = RESULTS / "csrms001_masked_recurrent_slot_selection.json"
OUT_REPORT = RESULTS / "csrms001_masked_recurrent_slot_selection_report.md"

FROZEN = {
    SOURCE: "7c375a9336588096e657917548eb3f2038828d9d6d42b75da2d24b57ccd3f387",
    SOURCE_VALIDATION: "368d1be6a70c403f77abb5f87e3c0635bea1cf084c6b7408530cbf857c2e1533",
}
EXPRESSION = re.compile(
    r"^([SFCL]):[^{}]+\{adj=([^;]+);fl=([^;]+);ec=([^;]+);"
    r"o=([0-9]+);c=([0-9]+);p=[^{};]+\}$"
)
FOLIO = re.compile(r"^f([0-9]+)")
LEVELS = (
    "FULL", "COMPOSITION", "TENDENCY_COUNTS_BINARY", "TENDENCY_EDGE", "EDGE_ONLY"
)
MIN_OCCURRENCES = 10
MIN_FOLIOS = 8
MIN_SECTIONS = 2
TSV_FIELDS = (
    "occurrence_order", "record_order", "segment_id", "page", "physical_folio",
    "section", "currier", "hand", "record_length", "occupant_ordinal",
    "selected_level", "context_sha256",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False) + "\n").encode("utf-8")


def shell(group: tuple[str, str, str, str, int, int], level: str) -> tuple[object, ...]:
    position, adjacency, first_last, edge_core, opening, closing = group
    if level == "FULL":
        return position, adjacency, first_last, edge_core, opening, closing
    if level == "COMPOSITION":
        return (position, adjacency.count("F"), adjacency.count("D"),
                adjacency.count("U"), first_last, edge_core,
                int(opening > 0), int(closing > 0))
    if level == "TENDENCY_COUNTS_BINARY":
        return position, first_last, edge_core, int(opening > 0), int(closing > 0)
    if level == "TENDENCY_EDGE":
        return position, first_last, edge_core
    if level == "EDGE_ONLY":
        return position, edge_core
    raise ValueError(level)


def context_bytes(context: tuple[object, ...]) -> bytes:
    return json.dumps(context, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def main() -> None:
    outputs = (OUT_TSV, OUT_JSON, OUT_REPORT)
    if any(path.exists() for path in outputs):
        raise SystemExit("refusing to overwrite CSRMS001 selection artifacts")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    validation = json.loads(SOURCE_VALIDATION.read_text(encoding="utf-8"))
    if validation.get("status") != "PASS_INDEPENDENT_RECORD_LEVEL_CONSENSUS_RECONSTRUCTION":
        raise SystemExit("source validation status mismatch")

    eligible: list[tuple[dict[str, str], list[tuple[str, str, str, str, int, int]], int]] = []
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["grammar_scope"] != "CONFIRMED_PROSE":
                continue
            if row["transcription_consensus_status"] != "ALL_MEMBER_AND_BOUNDARY_STABLE":
                continue
            groups = []
            for expression in row["formal_expression"].split(" | "):
                match = EXPRESSION.fullmatch(expression)
                if not match:
                    raise ValueError(f"bad formal expression: {expression}")
                position, adjacency, first_last, edge_core, opening, closing = match.groups()
                groups.append((position, adjacency, first_last, edge_core,
                               int(opening), int(closing)))
            if len(groups) != int(row["group_count"]):
                raise ValueError("group-count drift")
            if not 5 <= len(groups) <= 12:
                continue
            folio_match = FOLIO.match(row["page"])
            if not folio_match:
                raise ValueError(f"unrecognized physical folio: {row['page']}")
            eligible.append((row, groups, int(folio_match.group(1))))

    level_summaries: list[dict[str, object]] = []
    selected_level = ""
    selected_context: tuple[object, ...] | None = None
    selected_observations: list[dict[str, object]] = []
    masked_slot_count = sum(max(0, len(groups) - 4) for _, groups, _ in eligible)

    for level in LEVELS:
        contexts: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
        for row, groups, physical_folio in eligible:
            length = len(groups)
            for index in range(2, length - 2):
                context = (
                    row["currier"], length, index + 1,
                    shell(groups[index - 1], level), shell(groups[index + 1], level),
                )
                contexts[context].append({
                    "record_order": int(row["record_order"]),
                    "segment_id": row["segment_id"],
                    "page": row["page"],
                    "physical_folio": physical_folio,
                    "section": row["section"],
                    "currier": row["currier"],
                    "hand": row["hand"],
                    "record_length": length,
                    "occupant_ordinal": index + 1,
                })

        ranked: list[tuple[int, int, int, int, bytes, tuple[object, ...], list[dict[str, object]]]] = []
        passing = 0
        for context, observations in contexts.items():
            folios = len({item["physical_folio"] for item in observations})
            sections = len({item["section"] for item in observations})
            hands = len({item["hand"] for item in observations})
            if (len(observations) >= MIN_OCCURRENCES and folios >= MIN_FOLIOS
                    and sections >= MIN_SECTIONS):
                passing += 1
                ranked.append((-folios, -len(observations), -sections, -hands,
                               context_bytes(context), context, observations))
        ranked.sort()
        all_folios = [len({item["physical_folio"] for item in observations})
                      for observations in contexts.values()]
        all_occurrences = [len(observations) for observations in contexts.values()]
        level_summaries.append({
            "level": level,
            "unique_contexts": len(contexts),
            "passing_contexts": passing,
            "maximum_physical_folios": max(all_folios),
            "maximum_occurrences": max(all_occurrences),
        })
        if ranked:
            _, _, _, _, _, selected_context, selected_observations = ranked[0]
            selected_level = level
            break

    status = "PASS_MASKED_RECURRENT_SLOT_SELECTED" if selected_context else "STOP_NO_RECURRENT_FILLER_BLIND_SLOT"
    decision = "AUTHORIZE_ONE_EXACT_OCCUPANT_UNMASK" if selected_context else "CLOSE_EXACT_RECURRENT_SLOT_ROUTE"
    context_hash = hashlib.sha256(context_bytes(selected_context)).hexdigest() if selected_context else ""
    selected_observations.sort(key=lambda item: (int(item["record_order"]), str(item["segment_id"])))

    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for order, item in enumerate(selected_observations, 1):
            writer.writerow({"occurrence_order": order, **item,
                             "selected_level": selected_level,
                             "context_sha256": context_hash})

    result = {
        "experiment": "CSRMS001_MASKED_RECURRENT_SLOT_SELECTION",
        "status": status,
        "decision": decision,
        "scope": {
            "eligible_records": len(eligible),
            "masked_candidate_slots": masked_slot_count,
            "record_length_min": 5,
            "record_length_max": 12,
            "minimum_edge_distance_groups": 2,
        },
        "gates": {
            "minimum_occurrences": MIN_OCCURRENCES,
            "minimum_physical_folios": MIN_FOLIOS,
            "minimum_sections": MIN_SECTIONS,
        },
        "coarsening_ladder": level_summaries,
        "selection": None if selected_context is None else {
            "level": selected_level,
            "context": selected_context,
            "context_sha256": context_hash,
            "occurrences": len(selected_observations),
            "physical_folios": len({item["physical_folio"] for item in selected_observations}),
            "sections": sorted({str(item["section"]) for item in selected_observations}),
            "hands": sorted({str(item["hand"]) for item in selected_observations}),
        },
        "filler_identity_accessed": False,
        "forbidden_fields_accessed": [],
        "inputs": {path.name: sha(path) for path in FROZEN} | {
            METHOD.name: sha(METHOD), BUILDER.name: sha(BUILDER),
        },
        "outputs": {OUT_TSV.name: sha(OUT_TSV)},
        "claim_ceiling": (
            "A pass selects one recurrent surface-blind structural slot for a single exact "
            "occupant unmask. It assigns no word, part of speech, morpheme, sound, language, "
            "cipher operation, plaintext, meaning, or translation."
        ),
    }
    OUT_JSON.write_bytes(canonical(result))
    report = f"""# CSRMS001 masked recurrent-slot selection

Status: **{status}**

The filler-blind scan retained **{len(eligible)}** stable confirmed-prose records
and **{masked_slot_count:,}** interior candidate positions.  Exact neighbouring
shells were too sparse.  The first registered coarsening level to pass was
**{selected_level or 'NONE'}**.

The frozen selection has **{len(selected_observations)}** occurrences on
**{len({item['physical_folio'] for item in selected_observations})}** physical
folios across **{len({item['section'] for item in selected_observations})}**
sections.  Selection used exact Currier, record length, occupant ordinal, and
only the neighbours' already established first/last-tendency and edge/core
states.  The occupying family, exact member, surface, path, EVA, and current
formal features were not accessed.

Decision: **{decision}**.  This selects a structural comparison point only; it
does not assign a word, part of speech, morpheme, sound, language, cipher
operation, plaintext, meaning, or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
