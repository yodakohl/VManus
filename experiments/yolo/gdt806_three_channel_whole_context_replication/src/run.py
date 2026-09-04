#!/usr/bin/env python3
"""Build GDT806's transparent three-channel whole-context rival test."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import subprocess
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt806_three_channel_whole_context_replication"
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = Path(__file__).resolve()
G734_DICT = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
G738_HOLDS = ROOT / "experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/artifacts/MANUAL_HOLD_AUDIT.tsv"
G739_AXES = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/ANCHOR_AXIS_SPECS.tsv"
G739_WINDOWS = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/artifacts/WINDOW_202_TOKEN_AUDIT.tsv"
G754_DECISIONS = ROOT / "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
G800_OCCURRENCES = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
G802_CONTEXTS = ROOT / "experiments/yolo/gdt802_masked_lm_neighbour_context_transfer/artifacts/GDT802_4137_MASKED_NEIGHBOUR_ATLAS.tsv"
G803_BRACKETS = ROOT / "experiments/yolo/gdt803_recurrent_context_rarity_discriminator/artifacts/GDT803_12_BIDIRECTIONAL_BRACKETS.tsv"
G804_CONTROLS = ROOT / "experiments/yolo/gdt804_bracket_middle_independent_field_bridge/artifacts/GDT804_NEAREST_CONTROL_POOLS.tsv"
G805_ATLAS = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator/artifacts/GDT805_1086_EXTERNAL_CONTEXT_ATLAS.tsv"
G805_AUDIT = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator/artifacts/GDT805_131_GDT739_SURFACE_PROJECTION_AUDIT.tsv"
G805_FRAMES = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator/artifacts/GDT805_13_REPEATED_FRAME_TYPES.tsv"
G805_SOURCE_LOCK = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator/artifacts/SOURCE_LOCK.tsv"
G805_RUN = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator/src/run.py"
RIVAL_SPECS = SRC / "RIVAL_SIGNATURE_SPECS.tsv"
FRAME_SPECS = SRC / "FRAME_RIVAL_SPECS.tsv"
PREREG = EXP / "PREREGISTRATION.md"
METHOD = EXP / "METHOD.md"
VMANUS_EXP = ROOT / "vmanus-exp"
EDGE_VALIDATOR = ROOT / "tools/relation_edge_intake.py"

TARGETS = ("cheol", "otal", "okal", "ol", "qokeol", "qokol")
ALL_TARGETS = {"chal", "chedal", "cheol", "okail", "okal", "ol", "otal", "qokeol", "qokol", "qotal", "sail"}
C1 = "C1_EXACT_LOCAL"
C2 = "C2_GDT739_NARROW_PROJECTED"
C3 = "C3_GDT734_GLOBAL_RESIDUAL"
FULL = "GDT734_GLOBAL652_SENSITIVITY"
CHANNELS = (C1, C2, C3)
SCORED_CHANNELS = (C2, C3, FULL)
DENOMS = ("MAPPED_CONTACTS", "ALL_OPPORTUNITIES")
VIEWS = ("RAW", "PAIR_STABLE")
SIDES = ("L1", "R1")
THRESHOLD = Fraction(1, 20)
MACROS = {
    "QUALITY": frozenset(("HOT", "COLD", "DRY", "MOIST")),
    "SCALAR": frozenset(("AMOUNT", "VALUE", "PASS")),
    "CARRIER": frozenset(("PART", "MATERIAL", "PREPARATION")),
    "PROCESS": frozenset(("PROCESS", "CLOSE")),
}
EXPECTED_CAP = {
    "cheol": ((1, 1, 1, 0), (10, 11, 8, 7), (42, 49, 31, 33), (53, 61, 40, 40)),
    "otal": ((0, 0, 0, 0), (12, 7, 10, 6), (50, 37, 34, 30), (62, 44, 44, 36)),
    "okal": ((0, 0, 0, 0), (14, 9, 6, 7), (60, 48, 42, 28), (74, 57, 48, 35)),
    "ol": ((0, 2, 0, 2), (34, 47, 27, 30), (178, 191, 122, 118), (212, 240, 149, 150)),
    "qokeol": ((0, 0, 0, 0), (2, 4, 2, 3), (11, 12, 7, 8), (13, 16, 9, 11)),
    "qokol": ((0, 1, 0, 1), (5, 6, 3, 4), (35, 37, 27, 27), (40, 44, 30, 32)),
}
EXPECTED_MAPPED_LOFO = {
    "cheol": (13, 42), "otal": (12, 32), "okal": (10, 42),
    "ol": (37, 69), "qokeol": (5, 8), "qokol": (7, 35),
}
EXPECTED_ALL_LOFO = {"cheol": 63, "otal": 48, "okal": 52, "ol": 92, "qokeol": 22, "qokol": 46}
EDGE_FIELDS = (
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
    "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
    "relation_type", "direction_basis", "ownership_basis", "geometry_only_selection",
    "source_manifest_id", "page_crop_sha256", "pivot_crop_sha256", "target_crop_sha256",
    "source_aware_localizer", "relation_reviewer", "relation_confidence", "ambiguity_state",
    "formal_access_state", "fold_assignment", "eligibility_status",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        if not rows:
            raise AssertionError(f"empty artifact without schema: {path.name}")
        fields = tuple(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def fs(value: Fraction | None) -> str:
    return "NA" if value is None else f"{value.numerator}/{value.denominator}"


def ds(value: Fraction | None) -> str:
    return "NA" if value is None else f"{float(value):.12g}"


def sign(value: Fraction | None) -> int:
    if value is None or value == 0:
        return 0
    return 1 if value > 0 else -1


def median(values: Sequence[Fraction]) -> Fraction:
    ordered = sorted(values)
    if len(ordered) == 12:
        return (ordered[5] + ordered[6]) / 2
    if len(ordered) == 11:
        return ordered[5]
    raise AssertionError(f"unsupported median n={len(ordered)}")


def tags(value: str) -> tuple[str, ...]:
    return tuple(x for x in value.split("|") if x and x not in {"NONE", "BOUNDARY", "TARGET_WHOLE_NO_SEMANTIC_CREDIT"})


def macro_tags(axes: Iterable[str]) -> frozenset[str]:
    aset = set(axes)
    return frozenset(group for group, members in MACROS.items() if aset & members)


def candidate_label(value: Fraction | None, candidates: Sequence[dict[str, str]]) -> str:
    return candidates[0]["candidate_id"] if sign(value) > 0 else candidates[1]["candidate_id"] if sign(value) < 0 else "NONE"


def import_g805() -> Any:
    spec = importlib.util.spec_from_file_location("gdt805_reference", G805_RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import GDT805 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_specs() -> tuple[dict[str, list[dict[str, str]]], list[dict[str, str]]]:
    rows = read_tsv(RIVAL_SPECS)
    if len(rows) != 12 or set(row["target_surface"] for row in rows) != set(TARGETS):
        raise AssertionError("rival signature cohort drift")
    grouped: dict[str, list[dict[str, str]]] = {}
    for target in TARGETS:
        pair = sorted((row for row in rows if row["target_surface"] == target), key=lambda row: row["candidate_order"])
        if [row["candidate_order"] for row in pair] != ["A", "B"]:
            raise AssertionError(f"rival order drift for {target}")
        for row in pair:
            if row["left_macro"] not in MACROS or row["right_macro"] not in MACROS:
                raise AssertionError(f"unknown rival macro: {target}")
            if any(row[field] != "0" for field in ("prior_mutation_credit", "semantic_credit", "renderer_license", "component_export_credit")):
                raise AssertionError(f"nonzero rival credit: {target}")
        grouped[target] = pair
    frames = read_tsv(FRAME_SPECS)
    expected_frames = {"G805-F01", "G805-F05", "G805-F06", "G805-F08", "G805-F11", "G805-F12", "G805-F13"}
    if len(frames) != 7 or {row["source_frame_id"] for row in frames} != expected_frames:
        raise AssertionError("frame spec cohort drift")
    for row in frames:
        if any(row[field] != "0" for field in ("frame_decision_credit", "frame_score_weight", "semantic_credit", "renderer_license", "confirmed_lexeme", "component_export_credit")):
            raise AssertionError(f"nonzero frame credit: {row['source_frame_id']}")
    return grouped, frames


def build_global_deck(axis_specs: Sequence[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    compiled = [(row["axis_id"], row["axis_group"], re.compile(row["keyword_regex"].replace("\\\\", "\\"), re.IGNORECASE)) for row in axis_specs]
    source = read_tsv(G734_DICT)
    quarantined = {row["surface"] for row in read_tsv(G754_DECISIONS)}
    held = {row["surface"] for row in read_tsv(G738_HOLDS)}
    if len(source) != 1606 or len({row["surface"] for row in source}) != 1602 or len(quarantined) != 172 or len(held) != 14:
        raise AssertionError("global source/quarantine capacity drift")
    stages: list[tuple[str, list[dict[str, str]]]] = [("SOURCE_GDT734", source)]
    rows = [row for row in source if row["working_model_level"].startswith(("W2", "W3"))]
    stages.append(("W2_W3", rows))
    rows = [row for row in rows if row["gdt734_composition_semantic_credit"] == "0" and row["gdt734_component_export_allowed"] == "0"]
    stages.append(("ZERO_COMPOSITION_AND_COMPONENT", rows))
    retired = ("pulver", "samen", "saat", "wurzel", "holz")
    rows = [row for row in rows if not any(word in row["v99r7_spoken_default_de"].lower() for word in retired)]
    stages.append(("RETIRED_LITERAL_FREE", rows))
    tag_map: dict[tuple[str, str], tuple[str, ...]] = {}
    selected = []
    for row in rows:
        matched = tuple(axis for axis, _group, regex in compiled if regex.search(row["v99r7_spoken_default_de"]))
        if matched:
            tag_map[(row["surface"], row["reading_id"])] = matched
            selected.append(row)
    rows = selected
    stages.append(("AXIS_REGEX_MATCH", rows))
    rows = [row for row in rows if row["unconditional_global_export_allowed"] == "1"]
    stages.append(("UNCONDITIONAL_GLOBAL", rows))

    # The duplicate agreement/collapse gate intentionally occurs only after
    # row-wise global-export eligibility.  Non-exported duplicate dchey rows
    # can never enter this deck and therefore must not trigger a false abort.
    grouped: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["surface"]].append(row)
    collapsed: list[dict[str, str]] = []
    for surface in sorted(grouped):
        variants = grouped[surface]
        signatures = {
            (row["working_model_level"], row["gdt734_composition_semantic_credit"], row["gdt734_component_export_allowed"],
             row["unconditional_global_export_allowed"], row["v99r7_spoken_default_de"], tag_map[(surface, row["reading_id"])])
            for row in variants
        }
        if len(signatures) != 1:
            raise AssertionError(f"conflicting globally eligible duplicate: {surface}")
        collapsed.append(variants[0])
    rows = collapsed
    if len(rows) != 726:
        raise AssertionError("post-global duplicate collapse drift")
    rows = [row for row in rows if row["surface"] not in quarantined]
    stages.append(("MINUS_GDT754_172", rows))
    rows = [row for row in rows if row["surface"] not in held]
    stages.append(("MINUS_GDT738_14", rows))
    rows = [row for row in rows if row["surface"] not in ALL_TARGETS]
    stages.append(("MINUS_GDT805_11_TARGETS", rows))
    expected = [(1606, 1602), (990, 989), (984, 983), (777, 776), (769, 768), (726, 726), (659, 659), (657, 657), (652, 652)]
    audit = []
    for order, ((name, stage), want) in enumerate(zip(stages, expected, strict=True), start=1):
        got = (len(stage), len({row["surface"] for row in stage}))
        if got != want:
            raise AssertionError(f"global stage drift {name}: {got} != {want}")
        audit.append({"stage_order": order, "stage_id": name, "rows": got[0], "unique_surfaces": got[1],
                      "expected_rows": want[0], "expected_unique_surfaces": want[1], "assertion_pass": 1})
    deck = []
    for row in sorted(rows, key=lambda item: item["surface"]):
        axes = tag_map[(row["surface"], row["reading_id"])]
        deck.append({
            "surface": row["surface"], "source_reading_id": row["reading_id"], "working_model_level": row["working_model_level"],
            "v99r7_spoken_default_de": row["v99r7_spoken_default_de"], "axis_tags": "|".join(axes),
            "macro_tags": "|".join(sorted(macro_tags(axes))), "unconditional_global_export_allowed": 1,
            "gdt734_composition_semantic_credit": 0, "gdt734_component_export_allowed": 0,
            "gdt806_semantic_credit": 0, "gdt806_renderer_license": 0,
        })
    return audit, deck


def load_events(g805: Any, narrow: dict[str, tuple[str, ...]], exact: dict[tuple[str, str, int, str], tuple[str, ...]]) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]], list[dict[str, Any]], list[dict[str, str]]]:
    target_events = [dict(row) for row in read_tsv(G805_ATLAS) if row["surface"] in TARGETS]
    if len(target_events) != 967:
        raise AssertionError(f"six-target atlas drift: {len(target_events)}")
    discovery = {row["occurrence_id"] for row in read_tsv(G803_BRACKETS)}
    if any(row["occurrence_id"] in discovery for row in target_events):
        raise AssertionError("GDT803 discovery leakage")
    control_rows = [row for row in read_tsv(G804_CONTROLS) if row["pool_variant"] == "PRIMARY_K12" and row["target_surface"] in TARGETS]
    if len(control_rows) != 72:
        raise AssertionError("six-target K12 row drift")
    for target in TARGETS:
        subset = sorted((row for row in control_rows if row["target_surface"] == target), key=lambda row: int(row["neighbor_rank"]))
        if len(subset) != 12 or len({row["control_surface"] for row in subset}) != 12 or [int(row["neighbor_rank"]) for row in subset] != list(range(1, 13)):
            raise AssertionError(f"K12 pool drift: {target}")
        if any(row["outcome_fields_used_for_matching"] != "NONE" for row in subset):
            raise AssertionError(f"K12 outcome matching leakage: {target}")
    surfaces = {row["control_surface"] for row in control_rows}
    if len(surfaces) != 20 or surfaces & ALL_TARGETS:
        raise AssertionError("K12 surface union/target overlap drift")
    reader = g805.ReaderContext()
    base = {row["occurrence_id"]: row for row in read_tsv(G800_OCCURRENCES)}
    contexts = read_tsv(G802_CONTEXTS)
    by_surface: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in contexts:
        source = base[row["occurrence_id"]]
        if row["terminal"] == "l" and source["surface"] in surfaces:
            event = g805.build_context_event(row, source, reader, ALL_TARGETS, narrow, exact, {})
            by_surface[source["surface"]].append(event)
    if sum(map(len, by_surface.values())) != 1737 or set(by_surface) != surfaces:
        raise AssertionError("K12 reconstructed event drift")
    return target_events, dict(by_surface), reader.stats, control_rows


def decorate(events: Sequence[dict[str, Any]], residual: dict[str, dict[str, Any]], global_deck: dict[str, dict[str, Any]]) -> None:
    """Assign every immediate flank to at most one disjoint channel."""
    for event in events:
        for side in ("l1", "r1"):
            surface = str(event[f"{side}_surface"])
            kind = str(event[f"{side}_anchor_kind"])
            local_axes = tags(str(event[f"{side}_axis_tags"]))
            channel, axes = "NONE", ()
            if kind == "GDT739_EXACT_ACTIVE_CELL":
                channel, axes = C1, local_axes
            elif kind == "GDT805_EXPLORATORY_SURFACE_AXIS_PROJECTION":
                channel, axes = C2, local_axes
            elif surface in residual:
                channel, axes = C3, tags(str(residual[surface]["axis_tags"]))
            full_axes = tags(str(global_deck[surface]["axis_tags"])) if surface in global_deck else ()
            if (channel != "NONE") != bool(full_axes):
                raise AssertionError(f"partition/full mismatch: {event['occurrence_id']}:{side}:{surface}:{channel}")
            event[f"{side}_gdt806_channel"] = channel
            event[f"{side}_gdt806_axes"] = "|".join(axes) or "NONE"
            event[f"{side}_gdt806_macros"] = "|".join(sorted(macro_tags(axes))) or "NONE"
            event[f"{side}_gdt806_full_axes"] = "|".join(full_axes) or "NONE"
            event[f"{side}_gdt806_full_macros"] = "|".join(sorted(macro_tags(full_axes))) or "NONE"


def contact_axes(event: dict[str, Any], side: str, channel: str) -> tuple[str, ...]:
    prefix = side.lower()
    if channel == FULL:
        return tags(str(event[f"{prefix}_gdt806_full_axes"]))
    if event[f"{prefix}_gdt806_channel"] != channel:
        return ()
    return tags(str(event[f"{prefix}_gdt806_axes"]))


def opportunities(events: Sequence[dict[str, Any]], side: str, view: str, omit_folio: str | None = None) -> list[dict[str, Any]]:
    prefix = side.lower()
    return [
        event for event in events
        if (omit_folio is None or event["physical_folio"] != omit_folio)
        and (view == "RAW" or str(event[f"{prefix}_pair_sequence_stable_all_three"]) == "1")
    ]


def candidate_score(events: Sequence[dict[str, Any]], candidate: dict[str, str], channel: str, denominator: str, view: str, omit_folio: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {}
    rates: list[Fraction] = []
    for side in SIDES:
        available = opportunities(events, side, view, omit_folio)
        mapped = [event for event in available if contact_axes(event, side, channel)]
        denominator_events = mapped if denominator == "MAPPED_CONTACTS" else available
        wanted = candidate["left_macro" if side == "L1" else "right_macro"]
        hits = sum(wanted in macro_tags(contact_axes(event, side, channel)) for event in available)
        den = len(denominator_events)
        rate = Fraction(hits, den) if den else None
        result[f"{side.lower()}_hits"] = hits
        result[f"{side.lower()}_den"] = den
        result[f"{side.lower()}_rate"] = rate
        if rate is not None:
            rates.append(rate)
    result["score"] = (rates[0] + rates[1]) / 2 if len(rates) == 2 else None
    return result


def duel(events: Sequence[dict[str, Any]], candidates: Sequence[dict[str, str]], channel: str, denominator: str, view: str, omit_folio: str | None = None) -> dict[str, Any]:
    a = candidate_score(events, candidates[0], channel, denominator, view, omit_folio)
    b = candidate_score(events, candidates[1], channel, denominator, view, omit_folio)
    delta = None if a["score"] is None or b["score"] is None else a["score"] - b["score"]
    return {"a": a, "b": b, "delta": delta}


def robust(events: Sequence[dict[str, Any]], channel: str, denominator: str, omit_folio: str | None = None) -> bool:
    for side in SIDES:
        available = opportunities(events, side, "PAIR_STABLE", omit_folio)
        selected = [event for event in available if contact_axes(event, side, channel)] if denominator == "MAPPED_CONTACTS" else available
        if len(selected) < 2 or len({event["physical_folio"] for event in selected}) < 2:
            return False
    return True


def capacity(events: Sequence[dict[str, Any]], channel: str, denominator: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    union: set[str] = set()
    for side in SIDES:
        raw_all = opportunities(events, side, "RAW")
        stable_all = opportunities(events, side, "PAIR_STABLE")
        raw = [event for event in raw_all if contact_axes(event, side, channel)] if denominator == "MAPPED_CONTACTS" else raw_all
        stable = [event for event in stable_all if contact_axes(event, side, channel)] if denominator == "MAPPED_CONTACTS" else stable_all
        union.update(str(event["physical_folio"]) for event in stable)
        p = side.lower()
        result[f"{p}_raw_contacts"] = len(raw)
        result[f"{p}_raw_folios"] = len({event["physical_folio"] for event in raw})
        result[f"{p}_stable_contacts"] = len(stable)
        result[f"{p}_stable_folios"] = len({event["physical_folio"] for event in stable})
    result["stable_union_folios"] = len(union)
    result["stable_robust_capacity"] = int(
        result["l1_stable_contacts"] >= 2 and result["r1_stable_contacts"] >= 2
        and result["l1_stable_folios"] >= 2 and result["r1_stable_folios"] >= 2
        and result["stable_union_folios"] >= 4
    )
    return result


def build_contacts(target_events: Sequence[dict[str, Any]], controls: dict[str, list[dict[str, Any]]], membership: Sequence[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    subjects = [("TARGET", event) for event in target_events]
    subjects += [("K12_CONTROL", event) for surface in sorted(controls) for event in controls[surface]]
    for kind, event in subjects:
        for side in SIDES:
            p = side.lower()
            rows.append({
                "contact_id": f"G806-C{len(rows) + 1:05d}", "subject_kind": kind,
                "subject_surface": event["surface"], "occurrence_id": event["occurrence_id"],
                "source_selector": event["source_selector"], "physical_folio": event["physical_folio"],
                "locus": event["locus"], "token_index": event["token_index"], "side": side,
                "neighbor_surface": event[f"{p}_surface"], "pair_sequence_stable_all_three": event[f"{p}_pair_sequence_stable_all_three"],
                "assigned_disjoint_channel": event[f"{p}_gdt806_channel"], "channel_axis_tags": event[f"{p}_gdt806_axes"],
                "channel_macro_tags": event[f"{p}_gdt806_macros"], "global652_mapped": int(event[f"{p}_gdt806_full_axes"] != "NONE"),
                "global652_axis_tags": event[f"{p}_gdt806_full_axes"], "global652_macro_tags": event[f"{p}_gdt806_full_macros"],
                "semantic_credit": 0, "renderer_license": 0, "component_export_credit": 0,
            })
    pools = [{
        "target_surface": row["target_surface"], "neighbor_rank": row["neighbor_rank"], "control_surface": row["control_surface"],
        "control_occurrences": len(controls[row["control_surface"]]), "individual_covariate_distance": row["individual_covariate_distance"],
        "outcome_fields_used_for_matching": row["outcome_fields_used_for_matching"], "replacement_allowed": 0,
    } for row in membership]
    return rows, pools


def build_capacities(target_events: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in target_events:
        grouped[str(event["surface"])].append(event)
    rows = []
    for target in TARGETS:
        for index, channel in enumerate((C1, C2, C3, FULL)):
            cap = capacity(grouped[target], channel, "MAPPED_CONTACTS")
            got = (cap["l1_raw_contacts"], cap["r1_raw_contacts"], cap["l1_stable_contacts"], cap["r1_stable_contacts"])
            if got != EXPECTED_CAP[target][index]:
                raise AssertionError(f"capacity drift {target}:{channel}: {got}")
            rows.append({"target_surface": target, "channel": channel, "denominator": "MAPPED_CONTACTS", **cap, "expected_exact_capacity_pass": 1})
        rows.append({"target_surface": target, "channel": "ALL_CHANNEL_NUMERATORS", "denominator": "ALL_OPPORTUNITIES",
                     **capacity(grouped[target], FULL, "ALL_OPPORTUNITIES"), "expected_exact_capacity_pass": 1})
    all_rows = [row for row in rows if row["denominator"] == "ALL_OPPORTUNITIES"]
    raw = (sum(row["l1_raw_contacts"] for row in all_rows), sum(row["r1_raw_contacts"] for row in all_rows))
    stable = (sum(row["l1_stable_contacts"] for row in all_rows), sum(row["r1_stable_contacts"] for row in all_rows))
    if raw != (967, 967) or stable != (600, 594):
        raise AssertionError(f"all-opportunity denominator drift: {raw}/{stable}")
    return rows


def build_atlas_wide_audit(events: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assert the frozen eleven-target audit separately from duel denominators."""
    if len(events) != 1086 or {str(event["surface"]) for event in events} != ALL_TARGETS - {"okail"}:
        raise AssertionError("eleven-target GDT805 atlas drift")
    expected = {
        C1: (1, 5, 1, 4), C2: (91, 87, 65, 60),
        C3: (427, 421, 300, 277), FULL: (519, 513, 366, 341),
    }
    output = []
    for channel in (C1, C2, C3, FULL):
        values = []
        for side in SIDES:
            raw = sum(bool(contact_axes(event, side, channel)) for event in events)
            stable = sum(bool(contact_axes(event, side, channel)) and str(event[f"{side.lower()}_pair_sequence_stable_all_three"]) == "1" for event in events)
            values.extend((raw, stable))
        # values is L raw, L stable, R raw, R stable; normalize to frozen order.
        got = (values[0], values[2], values[1], values[3])
        if got != expected[channel]:
            raise AssertionError(f"eleven-target atlas capacity drift {channel}: {got}")
        output.append({
            "scope": "GDT805_ELEVEN_TARGET_ATLAS_AUDIT_ONLY", "channel": channel,
            "raw_l1": got[0], "raw_r1": got[1], "pair_stable_l1": got[2], "pair_stable_r1": got[3],
            "used_as_six_target_duel_denominator": 0, "assertion_pass": 1,
        })
    return output


def score_output(target: str, kind: str, subject: str, channel: str, denominator: str, view: str, result: dict[str, Any], candidates: Sequence[dict[str, str]]) -> dict[str, Any]:
    a, b = result["a"], result["b"]
    return {
        "target_reference": target, "subject_kind": kind, "subject_surface": subject, "channel": channel,
        "denominator": denominator, "view": view, "candidate_a": candidates[0]["candidate_id"], "candidate_b": candidates[1]["candidate_id"],
        "a_l1_hits": a["l1_hits"], "a_l1_denominator": a["l1_den"], "a_l1_rate": fs(a["l1_rate"]),
        "a_r1_hits": a["r1_hits"], "a_r1_denominator": a["r1_den"], "a_r1_rate": fs(a["r1_rate"]),
        "candidate_a_score": fs(a["score"]), "b_l1_hits": b["l1_hits"], "b_l1_denominator": b["l1_den"],
        "b_l1_rate": fs(b["l1_rate"]), "b_r1_hits": b["r1_hits"], "b_r1_denominator": b["r1_den"],
        "b_r1_rate": fs(b["r1_rate"]), "candidate_b_score": fs(b["score"]),
        "uncentered_delta_a_minus_b": fs(result["delta"]), "uncentered_delta_decimal": ds(result["delta"]),
        "bilaterally_scoreable": int(result["delta"] is not None),
    }


def build_scores(target_events: Sequence[dict[str, Any]], control_events: dict[str, list[dict[str, Any]]], pools: dict[str, list[str]], specs: dict[str, list[dict[str, str]]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[tuple[str, str, str, str], dict[str, Any]]]:
    targets: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in target_events:
        targets[str(event["surface"])].append(event)
    score_rows, contrast_rows = [], []
    cache: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for target in TARGETS:
        candidates = specs[target]
        for channel in SCORED_CHANNELS:
            for denominator in DENOMS:
                for view in VIEWS:
                    target_score = duel(targets[target], candidates, channel, denominator, view)
                    score_rows.append(score_output(target, "TARGET", target, channel, denominator, view, target_score, candidates))
                    controls = []
                    for surface in pools[target]:
                        value = duel(control_events[surface], candidates, channel, denominator, view)
                        controls.append((surface, value))
                        score_rows.append(score_output(target, "K12_CONTROL", surface, channel, denominator, view, value, candidates))
                    values = [value["delta"] for _surface, value in controls]
                    scoreable = all(value is not None for value in values)
                    base = median(values) if scoreable else None  # type: ignore[arg-type]
                    centered = None if target_score["delta"] is None or base is None else target_score["delta"] - base
                    orientation = sign(centered)
                    rank: int | None = None
                    if orientation and target_score["delta"] is not None and scoreable:
                        oriented_target = orientation * target_score["delta"]
                        rank = 1 + sum(orientation * value >= oriented_target for value in values)  # type: ignore[operator]
                    robust_controls = sum(robust(control_events[surface], channel, denominator) for surface in pools[target])
                    row = {
                        "target_surface": target, "channel": channel, "denominator": denominator, "view": view,
                        "candidate_a": candidates[0]["candidate_id"], "candidate_b": candidates[1]["candidate_id"],
                        "target_uncentered_delta": fs(target_score["delta"]), "target_uncentered_decimal": ds(target_score["delta"]),
                        "k12_exact_median": fs(base), "k12_exact_median_decimal": ds(base),
                        "target_centered_delta": fs(centered), "target_centered_decimal": ds(centered),
                        "selected_by_centered_sign": candidate_label(centered, candidates), "selected_sign": orientation,
                        "uncentered_centered_same_nonzero_sign": int(orientation != 0 and sign(target_score["delta"]) == orientation),
                        "uncentered_margin_ge_1_20": int(target_score["delta"] is not None and abs(target_score["delta"]) >= THRESHOLD),
                        "centered_margin_ge_1_20": int(centered is not None and abs(centered) >= THRESHOLD),
                        "all_12_controls_bilateral": int(scoreable), "robust_stable_controls": robust_controls,
                        "required_robust_controls_pass": int(view == "RAW" or robust_controls >= 10),
                        "oriented_rank_of_13_ties_against": rank if rank is not None else "NA", "rank_le_3": int(rank is not None and rank <= 3),
                        "control_deltas": "|".join(f"{surface}:{fs(value['delta'])}" for surface, value in controls),
                    }
                    contrast_rows.append(row)
                    cache[(target, channel, denominator, view)] = {
                        **row, "target_value": target_score["delta"], "baseline_value": base, "centered_value": centered,
                        "control_values": {surface: value["delta"] for surface, value in controls},
                    }
        for view in VIEWS:
            value = duel(targets[target], candidates, C1, "MAPPED_CONTACTS", view)
            score_rows.append(score_output(target, "TARGET", target, C1, "MAPPED_CONTACTS", view, value, candidates))
    return score_rows, contrast_rows, cache


def fold_universe(events: Sequence[dict[str, Any]], channel: str, denominator: str) -> list[str]:
    folios: set[str] = set()
    for side in SIDES:
        for event in opportunities(events, side, "PAIR_STABLE"):
            if denominator == "ALL_OPPORTUNITIES" or contact_axes(event, side, channel):
                folios.add(str(event["physical_folio"]))
    return sorted(folios)


def build_lofo(target_events: Sequence[dict[str, Any]], controls: dict[str, list[dict[str, Any]]], pools: dict[str, list[str]], specs: dict[str, list[dict[str, str]]], cache: dict[tuple[str, str, str, str], dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[tuple[str, str, str], dict[str, Any]]]:
    targets: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in target_events:
        targets[str(event["surface"])].append(event)
    rows: list[dict[str, Any]] = []
    summary: dict[tuple[str, str, str], dict[str, Any]] = {}
    for target in TARGETS:
        for cindex, channel in enumerate((C2, C3)):
            for denominator in DENOMS:
                universe = fold_universe(targets[target], channel, denominator)
                expected = EXPECTED_MAPPED_LOFO[target][cindex] if denominator == "MAPPED_CONTACTS" else EXPECTED_ALL_LOFO[target]
                if len(universe) != expected:
                    raise AssertionError(f"LOFO universe drift {target}:{channel}:{denominator}: {len(universe)}")
                selected = int(cache[(target, channel, denominator, "PAIR_STABLE")]["selected_sign"])
                successes = 0
                for folio in universe:
                    target_fold = duel(targets[target], specs[target], channel, denominator, "PAIR_STABLE", folio)
                    control_folds = [(surface, duel(controls[surface], specs[target], channel, denominator, "PAIR_STABLE", folio)) for surface in pools[target]]
                    values = [value["delta"] for _surface, value in control_folds]
                    scoreable = all(value is not None for value in values)
                    base = median(values) if scoreable else None  # type: ignore[arg-type]
                    centered = None if target_fold["delta"] is None or base is None else target_fold["delta"] - base
                    robust_count = sum(robust(controls[surface], channel, denominator, folio) for surface in pools[target])
                    success = bool(selected and scoreable and robust_count >= 10 and sign(target_fold["delta"]) == selected and sign(centered) == selected)
                    successes += int(success)
                    rows.append({
                        "target_surface": target, "channel": channel, "denominator": denominator, "view": "PAIR_STABLE",
                        "omitted_physical_folio": folio, "fixed_selected_sign": selected,
                        "target_uncentered_delta": fs(target_fold["delta"]), "k12_exact_median": fs(base), "target_centered_delta": fs(centered),
                        "target_bilateral": int(target_fold["delta"] is not None), "all_12_controls_bilateral": int(scoreable),
                        "robust_controls_after_drop": robust_count, "fold_success": int(success),
                    })
                passed = successes * 5 >= 4 * len(universe)
                summary[(target, channel, denominator)] = {
                    "folds": len(universe), "successes": successes, "required_successes": (4 * len(universe) + 4) // 5,
                    "exact_gate": f"{successes}*5>=4*{len(universe)}", "pass": int(passed),
                }
    return rows, summary


def build_loco(pools: dict[str, list[str]], cache: dict[tuple[str, str, str, str], dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[tuple[str, str, str, str], dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    summary: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for target in TARGETS:
        for channel in (C2, C3):
            for denominator in DENOMS:
                for view in VIEWS:
                    full = cache[(target, channel, denominator, view)]
                    selected, target_value = int(full["selected_sign"]), full["target_value"]
                    values_by_surface: dict[str, Fraction | None] = full["control_values"]
                    successes = 0
                    for omitted in pools[target]:
                        values = [values_by_surface[surface] for surface in pools[target] if surface != omitted]
                        scoreable = len(values) == 11 and all(value is not None for value in values)
                        base = median(values) if scoreable else None  # type: ignore[arg-type]
                        centered = None if target_value is None or base is None else target_value - base
                        success = bool(selected and sign(centered) == selected)
                        successes += int(success)
                        rows.append({
                            "target_surface": target, "channel": channel, "denominator": denominator, "view": view,
                            "omitted_control_surface": omitted, "fixed_selected_sign": selected,
                            "target_uncentered_delta_unchanged": fs(target_value), "k11_exact_median_sorted_position_6": fs(base),
                            "recomputed_centered_delta": fs(centered), "eleven_controls_scoreable": int(scoreable), "fold_success": int(success),
                        })
                    summary[(target, channel, denominator, view)] = {"folds": 12, "successes": successes, "required_successes": 10, "pass": int(successes >= 10)}
    return rows, summary


def same_direction_margin(values: Sequence[Fraction | None]) -> tuple[bool, int]:
    selected = sign(values[0]) if values else 0
    passed = bool(selected and all(sign(value) == selected for value in values) and all(value is not None and abs(value) >= THRESHOLD for value in values))
    return passed, selected if passed else 0


def overlay_pass(target: str, denominator: str, selected: int, cache: dict[tuple[str, str, str, str], dict[str, Any]]) -> bool:
    if not selected:
        return False
    values: list[Fraction | None] = []
    for view in VIEWS:
        row = cache[(target, FULL, denominator, view)]
        values.extend((row["target_value"], row["centered_value"]))
    return all(sign(value) == selected for value in values)


def build_adjudications(capacities: Sequence[dict[str, Any]], cache: dict[tuple[str, str, str, str], dict[str, Any]], lofo: dict[tuple[str, str, str], dict[str, Any]], loco: dict[tuple[str, str, str, str], dict[str, Any]], specs: dict[str, list[dict[str, str]]]) -> list[dict[str, Any]]:
    caps = {(row["target_surface"], row["channel"], row["denominator"]): row for row in capacities}
    output = []
    for target in TARGETS:
        channel_results: dict[str, dict[str, Any]] = {}
        for channel in (C2, C3):
            mapped_values: list[Fraction | None] = []
            for view in VIEWS:
                item = cache[(target, channel, "MAPPED_CONTACTS", view)]
                mapped_values.extend((item["target_value"], item["centered_value"]))
            mapped_direction, mapped_sign = same_direction_margin(mapped_values)
            mapped_rank = all(int(cache[(target, channel, "MAPPED_CONTACTS", view)]["rank_le_3"]) for view in VIEWS)
            mapped_controls = all(int(cache[(target, channel, "MAPPED_CONTACTS", view)]["all_12_controls_bilateral"]) for view in VIEWS) and int(cache[(target, channel, "MAPPED_CONTACTS", "PAIR_STABLE")]["robust_stable_controls"]) >= 10
            mapped_loco = all(loco[(target, channel, "MAPPED_CONTACTS", view)]["pass"] for view in VIEWS)
            mapped_global = overlay_pass(target, "MAPPED_CONTACTS", mapped_sign, cache)
            mapped_gate = bool(caps[(target, channel, "MAPPED_CONTACTS")]["stable_robust_capacity"] and mapped_direction and mapped_rank and mapped_controls and lofo[(target, channel, "MAPPED_CONTACTS")]["pass"] and mapped_loco and mapped_global)

            all_values: list[Fraction | None] = []
            for view in VIEWS:
                item = cache[(target, channel, "ALL_OPPORTUNITIES", view)]
                all_values.extend((item["target_value"], item["centered_value"]))
            all_direction, all_sign = same_direction_margin(all_values)
            all_matches = bool(mapped_sign and all_sign == mapped_sign)
            all_rank = all(int(cache[(target, channel, "ALL_OPPORTUNITIES", view)]["rank_le_3"]) for view in VIEWS)
            all_controls = all(int(cache[(target, channel, "ALL_OPPORTUNITIES", view)]["all_12_controls_bilateral"]) for view in VIEWS) and int(cache[(target, channel, "ALL_OPPORTUNITIES", "PAIR_STABLE")]["robust_stable_controls"]) >= 10
            all_loco = all(loco[(target, channel, "ALL_OPPORTUNITIES", view)]["pass"] for view in VIEWS)
            all_global = overlay_pass(target, "ALL_OPPORTUNITIES", mapped_sign, cache)
            all_gate = bool(caps[(target, "ALL_CHANNEL_NUMERATORS", "ALL_OPPORTUNITIES")]["stable_robust_capacity"] and all_direction and all_matches and all_rank and all_controls and lofo[(target, channel, "ALL_OPPORTUNITIES")]["pass"] and all_loco and all_global)
            channel_results[channel] = {
                "mapped_sign": mapped_sign, "mapped_capacity_pass": caps[(target, channel, "MAPPED_CONTACTS")]["stable_robust_capacity"],
                "mapped_direction_and_margin_pass": int(mapped_direction), "mapped_rank_pass": int(mapped_rank),
                "mapped_control_capacity_pass": int(mapped_controls), "mapped_lofo_pass": lofo[(target, channel, "MAPPED_CONTACTS")]["pass"],
                "mapped_loco_pass": int(mapped_loco), "mapped_global_overlay_pass": int(mapped_global), "mapped_channel_gate_pass": int(mapped_gate),
                "all_sign": all_sign, "all_direction_and_margin_pass": int(all_direction), "all_direction_matches_mapped": int(all_matches),
                "all_capacity_pass": caps[(target, "ALL_CHANNEL_NUMERATORS", "ALL_OPPORTUNITIES")]["stable_robust_capacity"],
                "all_rank_pass": int(all_rank), "all_control_capacity_pass": int(all_controls),
                "all_lofo_pass": lofo[(target, channel, "ALL_OPPORTUNITIES")]["pass"], "all_loco_pass": int(all_loco),
                "all_global_overlay_pass": int(all_global), "all_channel_gate_pass": int(all_gate),
            }
        c2, c3 = channel_results[C2], channel_results[C3]
        same = bool(c2["mapped_sign"] and c2["mapped_sign"] == c3["mapped_sign"])
        mapped_gate = bool(c2["mapped_channel_gate_pass"] and c3["mapped_channel_gate_pass"] and same)
        cross_gate = bool(mapped_gate and c2["all_channel_gate_pass"] and c3["all_channel_gate_pass"])
        pair = specs[target]
        diagnostic = pair[0] if c2["mapped_sign"] > 0 else pair[1] if c2["mapped_sign"] < 0 else None
        decision = "CROSS_DENOMINATOR_DECK_BREADTH_CONCORDANCE" if cross_gate else "CONDITIONAL_MAPPED_DECK_PREFERENCE" if mapped_gate else "UNRESOLVED_RIVAL"
        selected = diagnostic if decision != "UNRESOLVED_RIVAL" else None
        row: dict[str, Any] = {
            "target_surface": target, "candidate_a": pair[0]["candidate_id"], "candidate_b": pair[1]["candidate_id"],
            "c2_mapped_selected": candidate_label(cache[(target, C2, "MAPPED_CONTACTS", "PAIR_STABLE")]["centered_value"], pair),
            "c3_mapped_selected": candidate_label(cache[(target, C3, "MAPPED_CONTACTS", "PAIR_STABLE")]["centered_value"], pair),
            "c2_c3_same_mapped_direction": int(same),
        }
        for prefix, channel in (("c2", C2), ("c3", C3)):
            row.update({f"{prefix}_{key}": value for key, value in channel_results[channel].items()})
        row.update({
            "conditions_1_to_8_mapped_pass": int(mapped_gate), "condition_9_all_opportunity_pass": int(cross_gate),
            "diagnostic_c2_centered_candidate": diagnostic["candidate_id"] if diagnostic else "NONE",
            "decision": decision, "display_selected_candidate": selected["candidate_id"] if selected else "NONE",
            "display_selected_working_reading_de": selected["concrete_working_reading_de"] if selected else "NONE",
            "new_role_selected": 0, "semantic_credit": 0, "renderer_license": 0, "confirmed_lexeme": 0,
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
        output.append(row)
    return output


def build_frames(frame_specs: Sequence[dict[str, str]], adjudications: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    source = {row["frame_id"]: row for row in read_tsv(G805_FRAMES)}
    decisions = {row["target_surface"]: row["decision"] for row in adjudications}
    output = []
    for spec in frame_specs:
        row = source.get(spec["source_frame_id"])
        if row is None or row["frame_class"] != "REAL_TWO_SIDED_FRAME" or row["surface"] != spec["target_surface"] or row["exact_frame"] != spec["exact_frame"]:
            raise AssertionError(f"frame source drift: {spec['source_frame_id']}")
        output.append({
            **spec, "source_frame_class": row["frame_class"], "source_occurrences": row["occurrences"],
            "source_physical_folios": row["physical_folios"], "source_stable_sequence_occurrences": row["stable_sequence_occurrences"],
            "source_loci": row["loci"], "gdt806_target_decision": decisions[spec["target_surface"]], "decision_changed_by_frame": 0,
        })
    return output


def build_passages(target_events: Sequence[dict[str, Any]], specs: dict[str, list[dict[str, str]]], adjudications: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    decisions = {row["target_surface"]: row["decision"] for row in adjudications}
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in target_events:
        grouped[str(event["surface"])].append(event)
    output = []
    for target in TARGETS:
        ranked = []
        for event in grouped[target]:
            mapped = sum(event[f"{side}_gdt806_channel"] != "NONE" for side in ("l1", "r1"))
            stable = sum(event[f"{side}_gdt806_channel"] != "NONE" and str(event[f"{side}_pair_sequence_stable_all_three"]) == "1" for side in ("l1", "r1"))
            ranked.append((10 * stable + 3 * mapped + int(event["target_token_stable_all_three"]), event))
        ranked.sort(key=lambda item: (-item[0], str(item[1]["physical_folio"]), str(item[1]["locus"]), int(item[1]["token_index"])))
        chosen, used = [], set()
        for score, event in ranked:
            if event["physical_folio"] in used:
                continue
            chosen.append((score, event))
            used.add(event["physical_folio"])
            if len(chosen) == 2:
                break
        if len(chosen) != 2:
            raise AssertionError(f"passage capacity drift: {target}")
        for score, event in chosen:
            pair = specs[target]
            output.append({
                "passage_id": f"G806-P{len(output) + 1:02d}", "target_surface": target,
                "source_selector": event["source_selector"], "physical_folio": event["physical_folio"],
                "locus": event["locus"], "token_index": event["token_index"], "exact_five_window": event["exact_five_window"],
                "full_zl3b_line": event["full_zl3b_line"], "left_surface": event["l1_surface"],
                "left_channel": event["l1_gdt806_channel"], "left_axis_tags": event["l1_gdt806_axes"], "left_macro_tags": event["l1_gdt806_macros"],
                "candidate_a_de": pair[0]["concrete_working_reading_de"], "candidate_b_de": pair[1]["concrete_working_reading_de"],
                "right_surface": event["r1_surface"], "right_channel": event["r1_gdt806_channel"],
                "right_axis_tags": event["r1_gdt806_axes"], "right_macro_tags": event["r1_gdt806_macros"],
                "gdt806_decision": decisions[target], "selection_score": score, "display_only": 1,
                "semantic_credit": 0, "renderer_license": 0, "confirmed_plaintext": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
            })
    return output


def build_edges(target_events: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for event in target_events:
        index = int(event["token_index"])
        for side, prefix, offset in (("L1", "l1", -1), ("R1", "r1", 1)):
            channel = str(event[f"{prefix}_gdt806_channel"])
            if channel == "NONE":
                continue
            page = str(event["source_selector"])
            match = re.match(r"^(f\d+)", page)
            if match is None:
                raise AssertionError(f"folio parse failure: {page}")
            neighbour = str(event[f"{prefix}_surface"])
            output.append({
                "edge_id": f"G806E{len(output) + 1:04d}", "batch_id": "GDT806_THREE_CHANNEL_CONTEXT",
                "page": page, "physical_folio": match.group(1), "diagram_unit_id": "CACHED_TEXT_LINE",
                "pivot_visual_id": f"TOKEN_{event['surface']}_{index}", "pivot_locus": f"{event['locus']}@{index}",
                "target_visual_id": f"TOKEN_{neighbour}_{index + offset}", "target_locus": f"{event['locus']}@{index + offset}",
                "relation_type": f"{channel}_{side}_COMPLETE_WHOLE_CONTEXT", "direction_basis": "WRITTEN_TOKEN_ADJACENCY",
                "ownership_basis": "SAME_CACHED_TEXT_LINE", "geometry_only_selection": "FALSE", "source_manifest_id": "GDT806",
                "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
                "source_aware_localizer": "GDT806_BUILDER", "relation_reviewer": "PENDING_EXTERNAL",
                "relation_confidence": "EXACT_TRANSCRIPTION_ADJACENCY", "ambiguity_state": "WORKING_AXIS_DECK_ZERO_SEMANTIC_CREDIT",
                "formal_access_state": "FORMAL_ACCESSED", "fold_assignment": "NONE",
                "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
            })
    if len(output) != 916:
        raise AssertionError(f"edge packet capacity drift: {len(output)}")
    return output


def edge_intake(packet: Path, output: Path, nrows: int) -> dict[str, Any]:
    completed = subprocess.run([str(VMANUS_EXP), "check-edge-packet", str(packet)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 1 or completed.stderr:
        raise AssertionError(f"edge intake execution drift: {completed.returncode}:{completed.stderr}")
    result = json.loads(completed.stdout)
    if result.get("status") != "INVALID_PACKET" or result.get("packet_rows") != nrows or result.get("score_ready") is not False or result.get("eligible_edges") != 0:
        raise AssertionError("edge intake fail-closed state drift")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def source_lock() -> list[dict[str, str]]:
    paths = (PREREG, METHOD, RUN, RIVAL_SPECS, FRAME_SPECS, G734_DICT, G738_HOLDS, G739_AXES, G739_WINDOWS,
             G754_DECISIONS, G800_OCCURRENCES, G802_CONTEXTS, G803_BRACKETS, G804_CONTROLS, G805_ATLAS,
             G805_AUDIT, G805_FRAMES, G805_SOURCE_LOCK, G805_RUN, VMANUS_EXP, EDGE_VALIDATOR)
    purposes = {
        PREREG: "transparent post-data adversarial freeze", METHOD: "frozen scoring method", RUN: "official GDT806 builder",
        RIVAL_SPECS: "twelve equal-width rivals", FRAME_SPECS: "seven zero-credit frames",
        G734_DICT: "global whole deck source", G738_HOLDS: "manual HOLD mask", G739_AXES: "axis regex and macros",
        G739_WINDOWS: "exact active source cells", G754_DECISIONS: "provenance quarantine mask",
        G800_OCCURRENCES: "K12 occurrence identities", G802_CONTEXTS: "K12 immediate contexts",
        G803_BRACKETS: "discovery subtraction audit", G804_CONTROLS: "fixed PRIMARY_K12 pools",
        G805_ATLAS: "six-target external contexts", G805_AUDIT: "narrow N75 deck", G805_FRAMES: "fixed repeated frames",
        G805_SOURCE_LOCK: "inherited guarded raw-source hash binding",
        G805_RUN: "guarded reader/context reconstruction reference", VMANUS_EXP: "guard/query dispatcher",
        EDGE_VALIDATOR: "GDT388 edge intake",
    }
    rows = [{"path": relative(path), "sha256": sha256(path), "purpose": purposes[path], "access_mode": "SAFE_ARTIFACT_OR_CODE"} for path in paths]
    inherited = {row["path"]: row for row in read_tsv(G805_SOURCE_LOCK)}
    for name in ("transcription/voynich_zl3b_tokens.tsv", "transcription/voynich_cross_transcription_lines.tsv"):
        if name not in inherited:
            raise AssertionError(f"missing inherited raw hash: {name}")
        rows.append({"path": name, "sha256": inherited[name]["sha256"],
                     "purpose": "mixed reader source queried only by guarded GDT805 ReaderContext",
                     "access_mode": "GUARDED_QUERY_ONLY__INHERITED_HASH_NOT_REREAD"})
    return rows


def report_text(result: dict[str, Any], adjudications: Sequence[dict[str, Any]], contrasts: Sequence[dict[str, Any]]) -> str:
    lookup = {(row["target_surface"], row["channel"], row["denominator"], row["view"]): row for row in contrasts}
    lines = [
        "# GDT806 — Drei-Kanal-Ganzwortkontexte", "", f"Status: `{result['status']}`", "", "## Ergebnis", "",
        "Der offizielle exakte Lauf bestätigt die transparent vorab offengelegte Korrektur:",
        "Keines der sechs Ganzwörter passiert zugleich K12-Spezifität, Deckbreite,",
        "Folio-Robustheit und den ungefilterten All-Opportunity-Test. Deshalb wird keine",
        "neue Rolle, Wortbedeutung oder Renderer-Lizenz installiert.", "",
        "Die Globalmenge wurde fail-closed als 652 Oberflächen rekonstruiert; nach Abzug",
        "des engen N75-Decks bleiben 577 disjunkte Residualoberflächen. C1/C2/C3",
        "partitionieren auf den sechs Zielen exakt 454/462 rohe und 320/304",
        "paarsequenzstabile L1/R1-Kontakte.", "", "## Rivalen", "",
        "| Form | C2 zentriert roh/stabil | C3 zentriert roh/stabil | Rang C2 | Rang C3 | Entscheidung |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for decision in adjudications:
        target = decision["target_surface"]
        c2r, c2s = lookup[(target, C2, "MAPPED_CONTACTS", "RAW")], lookup[(target, C2, "MAPPED_CONTACTS", "PAIR_STABLE")]
        c3r, c3s = lookup[(target, C3, "MAPPED_CONTACTS", "RAW")], lookup[(target, C3, "MAPPED_CONTACTS", "PAIR_STABLE")]
        lines.append(f"| `{target}` | {c2r['target_centered_decimal']} / {c2s['target_centered_decimal']} | {c3r['target_centered_decimal']} / {c3s['target_centered_decimal']} | {c2r['oriented_rank_of_13_ties_against']}/{c2s['oriented_rank_of_13_ties_against']} | {c3r['oriented_rank_of_13_ties_against']}/{c3s['oriented_rank_of_13_ties_against']} | `{decision['decision']}` |")
    lines += [
        "", "## Einordnung", "",
        "Die Runde ersetzt einen basisratengetriebenen Ganzwortvergleich durch zwölf",
        "zielspezifische Kontrollganzwörter. `okal` bleibt im Residualdeck sichtbar,",
        "aber C2 scheitert an der gefrorenen Rang-/All-Opportunity-Kette; die übrigen",
        "Rivalen scheitern früher an Richtung, Marge oder Deckübereinstimmung.", "",
        "Alle Werte und Schwellen wurden als exakte Brüche gerechnet. LOFO entfernt",
        "synchron ein physisches Folio aus Ziel und Kontrollen, LOCO genau eine",
        "Kontrolloberfläche; Null, Gleichstand und fehlende Kapazität zählen dagegen.",
        "Die sieben Rahmen und zwölf Passagekarten tragen null Entscheidungs-, Semantik-",
        "und Renderergewicht. Die Achsen stammen aus verwandten deutschen Arbeitsrenderern",
        "und sind keine unabhängige semantische Replikation.", "",
        "Bestätigte Lexeme/Klartextsätze: 0/0. Neue Seiten, Bilder oder Transkriptionen: 0.",
        "f84/f84r-Zeilen: 0. Der GDT388-Einlass bleibt wegen Formalzugriff nicht score-ready.", "",
        "## Reproduktion", "", "```bash",
        "python3 experiments/yolo/gdt806_three_channel_whole_context_replication/src/run.py",
        "python3 experiments/yolo/gdt806_three_channel_whole_context_replication/src/validate.py", "```", "",
    ]
    return "\n".join(lines)


def build(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    specs, frame_specs = load_specs()
    axis_specs = read_tsv(G739_AXES)
    observed = {row["axis_id"]: row["axis_group"] for row in axis_specs}
    expected = {axis: group for group, axes in MACROS.items() for axis in axes}
    if len(axis_specs) != 12 or observed != expected:
        raise AssertionError("GDT739 axis-group map drift")
    stage_audit, global_rows = build_global_deck(axis_specs)
    global_deck = {row["surface"]: row for row in global_rows}
    audit = read_tsv(G805_AUDIT)
    narrow = {row["surface"]: tags(row["axis_tags"]) for row in audit if row["primary_surface_projection_allowed"] == "1"}
    if len(audit) != 131 or len(narrow) != 75 or not set(narrow) <= set(global_deck):
        raise AssertionError("N75/G652 subset drift")
    if sum(int(row["gdt739_active_radius_contacts"]) for row in audit if row["primary_surface_projection_allowed"] == "1") != 111:
        raise AssertionError("N75 active source-contact capacity drift")
    differences = {surface for surface in narrow if set(narrow[surface]) != set(tags(global_deck[surface]["axis_tags"]))}
    if differences != {"qeeey", "qoeeo"}:
        raise AssertionError(f"narrow/global retag difference drift: {differences}")
    residual = {surface: row for surface, row in global_deck.items() if surface not in narrow}
    if len(residual) != 577:
        raise AssertionError("G652 minus N75 drift")
    g805 = import_g805()
    rebuilt_audit, rebuilt_narrow, exact = g805.build_anchor_deck(ALL_TARGETS)
    if len(rebuilt_audit) != 131 or rebuilt_narrow != narrow or len(exact) != 111:
        raise AssertionError("GDT805 anchor deck reconstruction drift")
    target_events, control_events, guard_stats, control_rows = load_events(g805, narrow, exact)
    all_events = list(target_events) + [event for surface in sorted(control_events) for event in control_events[surface]]
    decorate(all_events, residual, global_deck)
    for event in all_events:
        if any(str(event.get(field, "")).startswith("f84") for field in ("source_selector", "physical_folio", "locus")):
            raise AssertionError(f"sealed selector reached GDT806: {event['occurrence_id']}")
    atlas_wide_events = [dict(row) for row in read_tsv(G805_ATLAS)]
    decorate(atlas_wide_events, residual, global_deck)
    atlas_wide_audit = build_atlas_wide_audit(atlas_wide_events)
    contacts, membership = build_contacts(target_events, control_events, control_rows)
    capacities = build_capacities(target_events)
    pools = {target: [row["control_surface"] for row in sorted((r for r in control_rows if r["target_surface"] == target), key=lambda r: int(r["neighbor_rank"]))] for target in TARGETS}
    scores, contrasts, score_cache = build_scores(target_events, control_events, pools, specs)
    lofo_rows, lofo_summary = build_lofo(target_events, control_events, pools, specs, score_cache)
    loco_rows, loco_summary = build_loco(pools, score_cache)
    adjudications = build_adjudications(capacities, score_cache, lofo_summary, loco_summary, specs)
    frames = build_frames(frame_specs, adjudications)
    passages = build_passages(target_events, specs, adjudications)
    edges = build_edges(target_events)

    written: list[Path] = []
    def emit(name: str, rows: Sequence[dict[str, Any]], fields: Sequence[str] | None = None) -> None:
        path = output_dir / name
        write_tsv(path, rows, fields)
        written.append(path)
    emit("SOURCE_LOCK.tsv", source_lock())
    emit("GDT806_GUARDED_QUERY_STATS.tsv", guard_stats)
    emit("GDT806_GLOBAL_DECK_STAGE_AUDIT.tsv", stage_audit)
    emit("GDT806_GLOBAL652_DECK.tsv", global_rows)
    emit("GDT806_ELEVEN_TARGET_ATLAS_CAPACITY_AUDIT.tsv", atlas_wide_audit)
    emit("GDT806_TARGET_AND_K12_CONTACTS.tsv", contacts)
    emit("GDT806_K12_POOL_MEMBERSHIP.tsv", membership)
    emit("GDT806_CHANNEL_CAPACITY.tsv", capacities)
    emit("GDT806_EXACT_RATIONAL_RIVAL_SCORES.tsv", scores)
    emit("GDT806_K12_MEDIAN_RANK_CONTRASTS.tsv", contrasts)
    emit("GDT806_STABLE_LOFO.tsv", lofo_rows)
    emit("GDT806_RAW_STABLE_LOCO.tsv", loco_rows)
    lofo_summary_rows = [{"target_surface": key[0], "channel": key[1], "denominator": key[2], **value} for key, value in sorted(lofo_summary.items())]
    loco_summary_rows = [{"target_surface": key[0], "channel": key[1], "denominator": key[2], "view": key[3], **value} for key, value in sorted(loco_summary.items())]
    emit("GDT806_STABLE_LOFO_SUMMARY.tsv", lofo_summary_rows)
    emit("GDT806_RAW_STABLE_LOCO_SUMMARY.tsv", loco_summary_rows)
    emit("GDT806_6_ADJUDICATIONS.tsv", adjudications)
    emit("GDT806_7_ZERO_CREDIT_FRAMES.tsv", frames)
    emit("GDT806_12_PASSAGE_CARDS.tsv", passages)
    emit("GDT806_GDT388_CONTEXT_EDGE_PACKET.tsv", edges, EDGE_FIELDS)
    intake_path = output_dir / "GDT806_GDT388_EDGE_INTAKE.json"
    intake = edge_intake(output_dir / "GDT806_GDT388_CONTEXT_EDGE_PACKET.tsv", intake_path, len(edges))
    written.append(intake_path)
    counts: defaultdict[str, int] = defaultdict(int)
    for row in adjudications:
        counts[str(row["decision"])] += 1
    if dict(counts) != {"UNRESOLVED_RIVAL": 6}:
        raise AssertionError(f"unexpected official outcome vs independent reference: {dict(counts)}")
    status = "PASS__652_GLOBAL__577_RESIDUAL__967_TARGET_EVENTS__0_CONDITIONAL__0_CROSS_DENOMINATOR__6_UNRESOLVED__0_NEW_ROLES__ZERO_LEXEMES"
    structural = [{
        "experiment": "GDT806", "status": status, "analysis_timing": "TRANSPARENT_POST_DATA_ADVERSARIAL_CORRECTION",
        "target_surfaces": 6, "rival_signatures": 12, "target_events": 967, "k12_pool_rows": 72,
        "unique_k12_control_surfaces": 20, "k12_control_events": 1737, "global_surfaces": 652,
        "narrow_surfaces": 75, "residual_surfaces": 577, "exact_active_source_cells": 111,
        "conditional_mapped_preferences": 0, "cross_denominator_concordances": 0, "unresolved_rivals": 6,
        "new_roles": 0, "confirmed_lexemes": 0, "confirmed_plaintext": 0, "renderer_licenses": 0,
        "component_export_credit": 0, "new_pages_images_or_transcriptions": 0, "f84_or_f84r_rows": 0,
    }]
    emit("GDT806_STRUCTURAL_CARD.tsv", structural)
    result: dict[str, Any] = {
        "experiment_id": "GDT806", "status": status,
        "analysis_timing": "TRANSPARENT_POST_DATA_ADVERSARIAL_CORRECTION__NOT_OUTCOME_BLIND",
        "targets": list(TARGETS), "rival_signatures": 12, "target_events": 967,
        "target_all_opportunity_raw_l1_r1": [967, 967], "target_all_opportunity_stable_l1_r1": [600, 594],
        "k12_pool_rows": 72, "unique_k12_control_surfaces": 20, "k12_control_events": 1737,
        "global_stage_counts": [[row["rows"], row["unique_surfaces"]] for row in stage_audit],
        "global652_surfaces": 652, "narrow75_surfaces": 75, "residual577_surfaces": 577,
        "exact_active_source_cells": 111, "candidate_decisions": {row["target_surface"]: row["decision"] for row in adjudications},
        "decision_counts": dict(counts), "frame_rows_zero_credit": 7, "passage_cards": 12,
        "gdt388_context_edges": len(edges), "gdt388_intake_status": intake["status"], "gdt388_score_ready": intake["score_ready"],
        "new_roles": 0, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "renderer_licenses": 0,
        "component_export_credit": 0, "new_pages_images_or_transcriptions": 0, "f84_or_f84r_rows": 0,
        "output_sha256": {path.name: sha256(path) for path in written},
    }
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    if output_dir.resolve() == ART.resolve():
        (EXP / "REPORT.md").write_text(report_text(result, adjudications, contrasts), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ART)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
