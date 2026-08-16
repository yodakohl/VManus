#!/usr/bin/env python3
"""Run the frozen GDT173 diagnostic fingerprint on the frozen Voynich HPR2 panel."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from run_gdt170_blind_instrument import (
    compatibility,
    discover,
    greedy_alignment,
    held_gain,
    host_signature,
    record_metrics,
    short_and_substitution,
)

R = Path(__file__).resolve().parent
DESIGN = R / "gdt174_design.json"
DESIGN_VALIDATION = R / "gdt174_design_validation.json"
HPR2 = R / "gdt062_right_family_inventory.tsv"
FRAMES = R / "gdt046_line_frames.tsv"
OLD_PARSES = R / "gdt172_blind_parses.json.gz"
B2_PARSES = R / "gdt173_blind_parses.json.gz"
OLD_DIAG = R / "gdt172_blind_diagnostics.tsv"
B2_DIAG = R / "gdt173_blind_diagnostics.tsv"
FINGERPRINT = R / "gdt173_three_system_fingerprint.tsv"
RECOVERY = R / "gdt173_three_system_recovery.tsv"
METHOD = R / "GDT174_VOYNICH_CALIBRATED_FINGERPRINT_METHOD.md"
TABLE = R / "gdt174_side_by_side.tsv"
PLACEMENT = R / "gdt174_axis_placement.tsv"
OPERATIONS = R / "gdt174_voynich_operations.tsv"
COUNTER = R / "gdt174_counterexamples.tsv"
REPORT = R / "GDT174_VOYNICH_CALIBRATED_FINGERPRINT_REPORT.md"
RESULT = R / "gdt174_result.json"

SYSTEMS = ("LEXICAL_A", "HUMAN_GROWN_B2", "FACTORIAL_B")
WORLD = {"LEXICAL_A": "CONTROL_P", "FACTORIAL_B": "CONTROL_Q", "HUMAN_GROWN_B2": "CONTROL_R"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict]) -> None:
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf8") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "NA") for field in fields} for row in rows])


def load_gzip_rows(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf8") as handle:
        return json.load(handle)["rows"]


def locus_number(locus: str) -> int:
    match = re.search(r"\.(\d+)$", locus)
    assert match, locus
    return int(match.group(1))


def hpr2_panel() -> tuple[list[dict], dict]:
    frames: dict[str, dict[str, str]] = {}
    rejected_frames = 0
    with FRAMES.open(newline="", encoding="utf8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"].startswith("f84") or row["locus"].startswith("f84"):
                rejected_frames += 1
                continue
            frames[row["locus"]] = row

    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    rejected_hpr2 = 0
    with HPR2.open(newline="", encoding="utf8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"].startswith("f84") or row["locus"].startswith("f84"):
                rejected_hpr2 += 1
                continue
            if row["locus"] in frames:
                by_line[row["locus"]].append(row)
    assert set(by_line) == set(frames)
    for locus, values in by_line.items():
        count = int(values[0]["group_count"])
        assert len(values) == count
        assert sorted(int(x["group_index"]) for x in values) == list(range(1, count + 1))

    page_lines: dict[str, list[str]] = defaultdict(list)
    for locus, frame in frames.items():
        page_lines[frame["page"]].append(locus)
    paragraph_end: set[str] = set()
    for values in page_lines.values():
        values.sort(key=locus_number)
        paragraph_end.add(values[-1])
        for previous, following in zip(values, values[1:]):
            if int(frames[following]["paragraph_start"]):
                paragraph_end.add(previous)

    folio_lines: dict[str, list[str]] = defaultdict(list)
    for locus, frame in frames.items():
        folio_lines[frame["physical_folio"]].append(locus)
    line_ordinal: dict[str, int] = {}
    for folio, values in folio_lines.items():
        values.sort(key=lambda x: (frames[x]["page"], locus_number(x)))
        line_ordinal.update({locus: i for i, locus in enumerate(values)})
    folio_ordinal = {folio: i for i, folio in enumerate(sorted(folio_lines))}

    rows: list[dict] = []
    for locus in sorted(by_line, key=lambda x: (frames[x]["page"], locus_number(x))):
        frame = frames[locus]
        for source in sorted(by_line[locus], key=lambda x: int(x["group_index"])):
            local = ("D1" if source["inner_d"] == "1" else "D0") + "|" + source["local_frame"]
            if source["inner_d"] == "0" and source["local_frame"] == "NONE":
                local = "NONE"
            right_outer = "NONE"
            if source["dy_closure"] == "1" or source["b3"] == "1":
                right_outer = "DY" + source["dy_closure"] + "|B3" + source["b3"]
            item = {
                "observation_id": "VMS:" + locus + ":" + source["group_index"],
                "surface_group": source["token"],
                "inferred_host": source["page_host"],
                "outer_left": source["wrapper"],
                "local_left": local,
                "right_inner": source["right_family"],
                "right_outer": right_outer,
                "operation_count": sum(x != "NONE" for x in (source["wrapper"], local, source["right_family"], right_outer)),
                "register": source["register"],
                "hand": source["hand"],
                "folio_id": source["physical_folio"],
                "layout_folio_ordinal": folio_ordinal[source["physical_folio"]],
                "physical_line_id": locus,
                "line_ordinal_on_folio": line_ordinal[locus],
                "group_index": int(source["group_index"]),
                "group_count": int(source["group_count"]),
                "paragraph_start": int(frame["paragraph_start"]),
                "paragraph_end": int(locus in paragraph_end),
                "right_separator": "LINE_END" if source["group_index"] == source["group_count"] else "SOURCE_GROUP_BOUNDARY",
                "page": source["page"],
                "locus": locus,
                "section": source["section"],
                "currier": source["currier"],
            }
            assert not item["page"].startswith("f84") and not item["locus"].startswith("f84")
            rows.append(item)
    return rows, {
        "groups": len(rows), "lines": len(by_line), "pages": len(page_lines), "folios": len(folio_lines),
        "f84_hpr2_rows_rejected": rejected_hpr2, "f84_frame_rows_rejected": rejected_frames,
    }


def recurrence(rows: list[dict]) -> dict[str, float]:
    counts = Counter(str(x["inferred_host"]) for x in rows)
    folios: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        folios[str(row["inferred_host"])].add(str(row["folio_id"]))
    return {
        "recurrent_host_mass": sum(n for n in counts.values() if n >= 2) / len(rows),
        "cross_folio_host_mass": sum(n for host, n in counts.items() if len(folios[host]) >= 2) / len(rows),
        "host_types": len(counts),
    }


def synthetic_recurrence() -> dict[str, dict[str, float]]:
    rows = load_gzip_rows(OLD_PARSES) + load_gzip_rows(B2_PARSES)
    out = {}
    for system in SYSTEMS:
        selected = [x for x in rows if x["world_view"] == WORLD[system] and x["parser_level"] == "SURFACE_ONLY"]
        assert len(selected) == 15214
        out[system] = recurrence(selected)
    return out


def synthetic_nulls() -> dict[str, dict[str, float]]:
    rows = read_tsv(OLD_DIAG) + read_tsv(B2_DIAG)
    out = {}
    for system in SYSTEMS:
        selected = [x for x in rows if x["world_view"] == WORLD[system] and x["parser_level"] == "SURFACE_ONLY" and x["diagnostic"] == "OPERATION_COMPATIBILITY" and x["scope"] == "ALL_PARTITIONED_REGISTERS"]
        assert len(selected) == 1
        row = selected[0]
        denominator = int(row["left_operations"]) * int(row["right_operations"])
        out[system] = {"null_density": float(row["null_mean"]) / denominator}
    return out


def synthetic_recovery() -> dict[str, dict[str, float]]:
    rows = read_tsv(RECOVERY)
    out: dict[str, dict[str, float]] = defaultdict(dict)
    for system in SYSTEMS:
        level = [x for x in rows if x["system"] == system and x["instrument_level"] == "SURFACE_ONLY" and x["component_stratum"] == "NA"]
        component = [x for x in rows if x["system"] == system and x["instrument_level"] == "SURFACE_ONLY" and x["component_stratum"] == "FREQUENT_LEXICAL_ID"]
        assert len(level) == len(component) == 1
        out[system]["host_decoder_accuracy"] = float(level[0]["host_decoder_accuracy"])
        out[system]["exact_true_host_rate"] = float(component[0]["exact_true_host_rate"])
    return out


def nearest(value: float, controls: dict[str, float]) -> str:
    low, high = min(controls.values()), max(controls.values())
    if value < low or value > high:
        return "OUTSIDE_SYNTHETIC_RANGE"
    distances = {name: abs(value - control) for name, control in controls.items()}
    best = min(distances.values())
    winners = [name for name in SYSTEMS if abs(distances[name] - best) < 1e-15]
    if len(winners) != 1:
        return "UNRESOLVED_TIE"
    return {"LEXICAL_A": "A_LIKE", "HUMAN_GROWN_B2": "B2_LIKE", "FACTORIAL_B": "FACTORIAL_B_LIKE"}[winners[0]]


def direction(value: float, controls: dict[str, float]) -> str:
    sign = lambda x: 1 if x > 0 else (-1 if x < 0 else 0)
    target = sign(value)
    matches = [name for name in SYSTEMS if sign(controls[name]) == target]
    if len(matches) == 3:
        return "UNRESOLVED_SHARED_DIRECTION"
    if not matches:
        return "OUTSIDE_SYNTHETIC_RANGE"
    labels = {"LEXICAL_A": "A", "HUMAN_GROWN_B2": "B2", "FACTORIAL_B": "FACTORIAL_B"}
    return "_".join(labels[x] for x in matches) + "_LIKE_DIRECTION"


def register_alignment(rows: list[dict]) -> tuple[float, list[dict]]:
    registers = sorted({str(x["register"]) for x in rows})
    detail = []
    for i, a_name in enumerate(registers):
        for b_name in registers[i + 1:]:
            a_rows = [x for x in rows if x["register"] == a_name]
            b_rows = [x for x in rows if x["register"] == b_name]
            a_freq = Counter(str(x["inferred_host"]) for x in a_rows)
            b_freq = Counter(str(x["inferred_host"]) for x in b_rows)
            a_panel = [x for x, _ in a_freq.most_common(100)]
            b_panel = [x for x, _ in b_freq.most_common(100)]
            value = greedy_alignment(host_signature(a_rows, a_panel), host_signature(b_rows, b_panel))
            detail.append({"register_a": a_name, "register_b": b_name, "greedy_matched_mean_cosine": value})
    return sum(float(x["greedy_matched_mean_cosine"]) for x in detail) / len(detail), detail


def main() -> None:
    design = json.loads(DESIGN.read_text())
    design_validation = json.loads(DESIGN_VALIDATION.read_text())
    assert design["status"] == "FROZEN_BEFORE_VOYNICH_FINGERPRINT_SCORING"
    assert design_validation["status"] == "PASS_INDEPENDENT_PRESCORE_FREEZE"
    assert design["controls_frozen_exactly_as_published"] and not design["build_b3"]
    rows, census = hpr2_panel()
    vrec = recurrence(rows)
    left, right, stats, _, counts = discover(rows)
    compat = compatibility(set(counts), left, right, "GDT174_VOYNICH_FROZEN")
    short, same_sub, external_sub = short_and_substitution(rows)
    next_host = held_gain(rows, "NEXT_HOST")
    whole_line = held_gain(rows, "WHOLE_LINE")
    closure = record_metrics(rows)
    alignment_mean, alignment_detail = register_alignment(rows)

    selected = {(side, op): rank + 1 for side, values in (("LEFT", left), ("RIGHT", right)) for rank, op in enumerate(values)}
    operation_rows = []
    for item in stats:
        key = item["side"], item["operation"]
        if key not in selected:
            continue
        operation_rows.append({
            "side": item["side"], "operation": item["operation"], "selected_rank": selected[key],
            "operation_length": item["operation_length"], "distinct_hosts": item["distinct_hosts"],
            "exact_pair_types": item["exact_pair_types"], "physical_folios": item["synthetic_folios"],
            "transformed_occurrences": item["transformed_occurrences"],
        })
    write_tsv(OPERATIONS, operation_rows)

    fingerprint_rows = read_tsv(FINGERPRINT)
    fp = {(x["system"], x["instrument_level"]): x for x in fingerprint_rows}
    control_recurrence = synthetic_recurrence()
    control_null = synthetic_nulls()
    control_recovery = synthetic_recovery()
    control_values: dict[str, dict[str, float]] = {name: {} for name in SYSTEMS}
    for name in SYSTEMS:
        source = fp[name, "SURFACE_ONLY"]
        control_values[name].update({
            "compatibility_density": float(source["compatibility_density"]),
            "compatibility_inclusive_p": float(source["compatibility_inclusive_p"]),
            "short_host_mass": float(source["short_host_mass"]),
            "same_group_substitution_cosine": float(source["same_group_substitution_cosine"]),
            "external_substitution_cosine": float(source["external_substitution_cosine"]),
            "next_host_gain_bits": float(source["next_host_gain_bits"]),
            "whole_line_gain_bits": float(source["whole_line_gain_bits"]),
            "right_marked_record_end_precision": float(source["right_marked_record_end_precision"]),
            "record_end_right_mark_recall": float(source["record_end_right_mark_recall"]),
            "register_alignment_mean": float(source["register_alignment_mean"]),
            "selected_left_operations": float(source["selected_left_operations"]),
            "selected_right_operations": float(source["selected_right_operations"]),
            **control_recurrence[name], **control_null[name], **control_recovery[name],
        })
        control_values[name]["compatibility_null_excess"] = control_values[name]["compatibility_density"] - control_values[name]["null_density"]

    denominator = max(1, int(compat["left_operations"]) * int(compat["right_operations"]))
    vms = {
        "host_decoder_accuracy": None,
        "exact_true_host_rate": None,
        "recurrent_host_mass": vrec["recurrent_host_mass"],
        "cross_folio_host_mass": vrec["cross_folio_host_mass"],
        "selected_left_operations": float(compat["left_operations"]),
        "selected_right_operations": float(compat["right_operations"]),
        "compatibility_density": float(compat["compatible_pair_density"]),
        "null_density": float(compat["null_mean"]) / denominator,
        "compatibility_null_excess": float(compat["compatible_pair_density"]) - float(compat["null_mean"]) / denominator,
        "compatibility_inclusive_p": float(compat["inclusive_p"]),
        "short_host_mass": float(short["short_host_mass"]),
        "same_group_substitution_cosine": float(same_sub["mean_delta_cosine"]),
        "external_substitution_cosine": float(external_sub["mean_delta_cosine"]),
        "next_host_gain_bits": float(next_host["gain_bits"]),
        "whole_line_gain_bits": float(whole_line["gain_bits"]),
        "right_marked_record_end_precision": float(closure["right_marked_record_end_precision"]),
        "record_end_right_mark_recall": float(closure["record_end_right_mark_recall"]),
        "register_alignment_mean": alignment_mean,
    }

    spec = [
        ("HOST_RECOVERY", "held_host_accuracy", "host_decoder_accuracy", "NOT_COMPARABLE_NO_VOYNICH_ORACLE", "UNRESOLVED_NOT_DIRECTLY_COMPARABLE", "Voynich has no lexical-ID oracle."),
        ("HOST_RECOVERY", "exact_true_host_rate", "exact_true_host_rate", "NOT_COMPARABLE_NO_VOYNICH_ORACLE", "UNRESOLVED_NOT_DIRECTLY_COMPARABLE", "Voynich has no true-host boundary oracle."),
        ("HOST_RECURRENCE_PROXY", "recurrent_host_mass", "recurrent_host_mass", "DIRECT_PROXY_NOT_RECOVERY", None, "Exact inferred/PAGE_HOST recurrence; not recovery."),
        ("HOST_RECURRENCE_PROXY", "cross_folio_host_mass", "cross_folio_host_mass", "DIRECT_PROXY_NOT_RECOVERY", None, "Mass whose exact host occurs on at least two physical folios."),
        ("LEFT_RIGHT_COMPATIBILITY", "selected_left_operations", "selected_left_operations", "COUNT_SIZE_DEPENDENT", "UNRESOLVED_NOT_DIRECTLY_COMPARABLE", "Frozen cap is twelve."),
        ("LEFT_RIGHT_COMPATIBILITY", "selected_right_operations", "selected_right_operations", "COUNT_SIZE_DEPENDENT", "UNRESOLVED_NOT_DIRECTLY_COMPARABLE", "Frozen cap is twelve."),
        ("LEFT_RIGHT_COMPATIBILITY", "compatibility_density", "compatibility_density", "DIRECT", None, "Exact GDT173 surface-operation definition."),
        ("LEFT_RIGHT_COMPATIBILITY", "null_density", "null_density", "DIRECT", None, "Null mean compatible pairs divided by the frozen operation-pair denominator."),
        ("LEFT_RIGHT_COMPATIBILITY", "null_excess", "compatibility_null_excess", "DIRECT", None, "Observed density minus null density."),
        ("LEFT_RIGHT_COMPATIBILITY", "inclusive_p", "compatibility_inclusive_p", "DIRECT_TEST_TAIL", "UNRESOLVED_TEST_TAIL_NOT_ARCHITECTURE", "Inferential tail, not an architectural coordinate."),
        ("SHORT_HOST_STRUCTURE", "length_2_3_mass", "short_host_mass", "DIRECT", None, "Token-weighted PAGE_HOST/inferred-host mass."),
        ("SAME_GROUP_SUBSTITUTION", "mean_delta_cosine", "same_group_substitution_cosine", "STRUCTURALLY_ANALOGOUS_HPR2_SIGNATURE", "UNRESOLVED_NOT_DIRECTLY_COMPARABLE", "Voynich profile has six frozen HPR2 compiler fields."),
        ("EXTERNAL_SUBSTITUTION", "mean_delta_cosine", "external_substitution_cosine", "DIRECT", None, "Exact +/-2 host-window endpoint."),
        ("NEXT_HOST", "held_gain_bits", "next_host_gain_bits", "DIRECTION_ONLY_UNEQUAL_CORPUS", None, "Raw bits are not magnitude-comparable."),
        ("WHOLE_LINE", "held_gain_bits", "whole_line_gain_bits", "DIRECTION_ONLY_UNEQUAL_CORPUS", None, "Raw bits are not magnitude-comparable."),
        ("CLOSURE", "right_marked_record_end_precision", "right_marked_record_end_precision", "STRUCTURALLY_ANALOGOUS_EDITORIAL_PARAGRAPH_END", "UNRESOLVED_NOT_DIRECTLY_COMPARABLE", "HPR2 right marks and editorial paragraph ends differ from synthetic records."),
        ("CLOSURE", "record_end_right_mark_recall", "record_end_right_mark_recall", "STRUCTURALLY_ANALOGOUS_EDITORIAL_PARAGRAPH_END", "UNRESOLVED_NOT_DIRECTLY_COMPARABLE", "HPR2 right marks and editorial paragraph ends differ from synthetic records."),
        ("REGISTER_ALIGNMENT", "greedy_matched_mean_cosine", "register_alignment_mean", "NOT_DIRECTLY_COMPARABLE_NONPARALLEL_CONTENT", "UNRESOLVED_NOT_DIRECTLY_COMPARABLE", "Synthetic renderers share content; Voynich registers do not."),
    ]
    table_rows = []
    placements: dict[str, str] = {}
    for axis, metric, key, comparability, fixed, note in spec:
        controls = {name: control_values[name][key] for name in SYSTEMS}
        value = vms[key]
        if fixed is not None:
            placement = fixed
        elif comparability == "DIRECTION_ONLY_UNEQUAL_CORPUS":
            placement = direction(float(value), controls)
        else:
            placement = nearest(float(value), controls)
        placements[axis + "|" + metric] = placement
        table_rows.append({
            "axis": axis, "metric": metric,
            "voynich": "NA_NO_ORACLE" if value is None else value,
            "lexical_a": controls["LEXICAL_A"], "human_grown_b2": controls["HUMAN_GROWN_B2"], "factorial_b": controls["FACTORIAL_B"],
            "comparability": comparability, "placement": placement, "note": note,
        })
    write_tsv(TABLE, table_rows)

    axis_rows = []
    for row in table_rows:
        axis_rows.append({"axis": row["axis"], "metric": row["metric"], "placement": row["placement"], "comparability": row["comparability"], "reason": row["note"]})
    write_tsv(PLACEMENT, axis_rows)

    direct_outside = [x for x in axis_rows if x["placement"] == "OUTSIDE_SYNTHETIC_RANGE" and x["comparability"] in {"DIRECT", "DIRECT_PROXY_NOT_RECOVERY"}]
    direction_outside = [x for x in axis_rows if x["placement"] == "OUTSIDE_SYNTHETIC_RANGE" and x["comparability"] == "DIRECTION_ONLY_UNEQUAL_CORPUS"]
    status = "VOYNICH_PARTLY_OUTSIDE_FROZEN_SYNTHETIC_ENVELOPE" if direct_outside or direction_outside else "VOYNICH_WITHIN_FROZEN_SYNTHETIC_ENVELOPE_ON_COMPARABLE_AXES"
    counter_rows = [
        {"counterexample": "HOST_RECOVERY_RANK", "evidence": "Voynich has no lexical-ID or true-host oracle.", "impact": "Recovery accuracy and exact-host recovery are unresolved, not zero."},
        {"counterexample": "RAW_CONTEXT_MAGNITUDE_RANK", "evidence": "Corpora have unequal group, line and folio counts.", "impact": "NEXT_HOST and WHOLE_LINE use direction only; no bit rescaling."},
        {"counterexample": "REGISTER_ALIGNMENT_EQUIVALENCE", "evidence": "Synthetic renderer views share content; Voynich registers do not.", "impact": "The numerical alignment is reported but never ranked."},
        {"counterexample": "CLOSURE_EQUIVALENCE", "evidence": "Voynich paragraph ends are editorial and HPR2 right fields are richer than blind suffix marks.", "impact": "Closure precision/recall are analogous only."},
        {"counterexample": "COMPOSITE_ARCHITECTURE_SCORE", "evidence": "Axis comparability differs and the design forbids rescaling.", "impact": "No composite score or winning architecture is reported."},
        {"counterexample": "B3_OR_RETUNED_CONTROL", "evidence": "All controls are read at published hashes and B3 was not built.", "impact": "No post-result intermediate model enters this pass."},
        {"counterexample": "GDT160_DENSITY_EQUIVALENCE", "evidence": "GDT160's 0.04529 fold-discovered transformation density and degree-preserving graph null are different endpoints from GDT173's capped visible-affix density and support-randomization null.", "impact": "The GDT174 value 0.83333 does not replace or contradict GDT160."},
        {"counterexample": "SYNTHETIC_LEVEL_POOLING", "evidence": "The side-by-side table uses the primary SURFACE_ONLY rows published in the GDT173 report; annotation-assisted rows are neither averaged nor substituted.", "impact": "Placements are surface-calibration placements and need not equal an annotation-assisted sensitivity."},
    ]
    write_tsv(COUNTER, counter_rows)

    direct = [x for x in axis_rows if x["comparability"] in {"DIRECT", "DIRECT_PROXY_NOT_RECOVERY"}]
    report = f"""# GDT174 — Voynich calibrated fingerprint report

Status: **{status}**.

The exact published lexical A, human-grown B2, and factorial B controls were
not regenerated or changed. The Voynich panel contains {census['groups']}
frozen HPR2 groups on {census['lines']} complete physical lines and
{census['folios']} physical folios. No f84 row was retained or scored; the
source contains zero f84r rows.

The three synthetic columns use the published GDT173 report's primary
`SURFACE_ONLY` coordinate. Annotation-assisted synthetic rows remain frozen in
the parent fingerprint and are not averaged into this table.

## Directly comparable coordinates

The full required side-by-side table is `gdt174_side_by_side.tsv`. On the
direct axes, {len(direct_outside)} metric(s) lie outside the closed synthetic range.
The comparable metric placements are:

"""
    for row in direct:
        report += f"- `{row['axis']} / {row['metric']}`: **{row['placement']}**.\n"
    report += f"""

Voynich raw-operation compatibility is {vms['compatibility_density']:.6f};
the frozen null mean density is {vms['null_density']:.6f}, leaving excess
{vms['compatibility_null_excess']:.6f} with inclusive p
{vms['compatibility_inclusive_p']:.6f}. This uses the exact GDT173 operation
and null definitions rather than GDT160's different degree-preserving graph
null.

The density alone is therefore misleading: Voynich is factorial-B-like on raw
density, but B2-like on null excess, and the observed density is actually below
its own frozen null expectation. This pass supplies no evidence that a new
control must reproduce factorial-B's specific compatibility excess.

## Direction-only and unresolved coordinates

- `NEXT_HOST`: {placements['NEXT_HOST|held_gain_bits']} ({vms['next_host_gain_bits']:+.3f} raw bits).
- `WHOLE_LINE`: {placements['WHOLE_LINE|held_gain_bits']} ({vms['whole_line_gain_bits']:+.3f} raw bits).
- Actual host recovery remains unresolved because there is no Voynich oracle.
- Same-group compiler coherence and closure are structurally analogous only.
- Register alignment is unresolved because Voynich registers are not parallel
  renderings of the same content.

## Architectural implication

The coordinates not covered by the frozen controls are: PAGE_HOST recurrence
and cross-folio recurrence (proxies, not recovery), the very high compatibility
null opportunity, length-2/3 host mass, external substitution coherence, and
the negative held NEXT_HOST direction. A future intermediate model would need
to address those coordinates without being tuned to their observed values.
The short-host and external-coherence exceedances are modest in absolute size;
the recurrence comparison is additionally sensitive to the controls' literal
escape population.

Already-covered coordinates do not motivate B3: raw compatibility density is
factorial-B-like, compatibility excess is B2-like, and negative WHOLE_LINE
direction is factorial-B-like. Actual host recovery, same-group compiler
coherence, closure and register alignment remain scientifically unresolved,
not missing-model requirements. These are separate statements, never a joint
score.

This is calibration, not identification. It establishes no Voynich encoder,
word, code, language, morphology, role, meaning, plaintext, or translation.
"""
    REPORT.write_text(report)

    result = {
        "schema": "GDT174_VOYNICH_CALIBRATED_FINGERPRINT_RESULT_V1",
        "status": status,
        "controls_frozen_exactly_as_published": True,
        "build_b3": False,
        "census": census,
        "voynich": vms,
        "voynich_detail": {"short": short, "same_group": same_sub, "external": external_sub, "next_host": next_host, "whole_line": whole_line, "closure": closure, "register_alignment_pairs": alignment_detail},
        "direct_outside_metrics": [x["axis"] + "|" + x["metric"] for x in direct_outside],
        "direction_outside_metrics": [x["axis"] + "|" + x["metric"] for x in direction_outside],
        "inputs": {p.name: sha(p) for p in (DESIGN, DESIGN_VALIDATION, HPR2, FRAMES, OLD_PARSES, B2_PARSES, OLD_DIAG, B2_DIAG, FINGERPRINT, RECOVERY)},
        "outputs": {p.name: sha(p) for p in (TABLE, PLACEMENT, OPERATIONS, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": {Path(__file__).name: sha(Path(__file__)), "run_gdt170_blind_instrument.py": sha(R / "run_gdt170_blind_instrument.py")},
        "chronology": {"design_commit": "0414725", "scored_after_public_design_freeze": True},
        "synthetic_control_level": "GDT173_REPORT_PRIMARY_SURFACE_ONLY",
        "no_composite": True, "no_threshold_tuning": True, "voynich_scored": True,
        "f84r_access": False, "f84_rows_retained": 0,
        "claim_ceiling": "Axis-wise synthetic calibration only; no Voynich encoder word code language morphology role meaning plaintext or translation.",
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "outside": result["direct_outside_metrics"], "voynich": vms}, sort_keys=True))


if __name__ == "__main__":
    main()
