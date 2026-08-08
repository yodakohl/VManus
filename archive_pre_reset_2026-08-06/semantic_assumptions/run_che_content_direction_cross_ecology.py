#!/usr/bin/env python3
"""Test exact che-to-value content direction on three independent label axes.

The pharmaceutical, zodiac, and biological root-only label axes were already
validated without this target.  They are trained in their own source sections
and applied unchanged to disjoint H/S/T prose.  Exact two-unit ``che+VALUE``
events compete with other one-unit E-bound carriers carrying the same value
root on the same physical page and in the same word-position quintile.

This is a transfer test of a relative semantic direction, not an English-word
or part-of-speech decoder.  ZL/IT/RF are robustness readings of the same ink.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from common import RESULTS, folio_number, parse_rows
from run_che_carrier_content_asymmetry import (
    Event, PRIMARY, VIEWS, page_values, sign_flip, t_statistic,
)
from run_internal_utterance_grammar import line_nodes
from run_multi_label_d_headedness import (
    AXES, APPLICATION_SECTIONS, source_scale, source_validation, train_axis,
)
from run_section_content_bridge import SOURCES


PRIOR = RESULTS / "multi_label_d_headedness_results.json"
PRIOR_CHE = RESULTS / "che_carrier_content_asymmetry_results.json"
OUTPUT_JSON = RESULTS / "che_content_direction_cross_ecology_results.json"
OUTPUT_REPORT = RESULTS / "che_content_direction_cross_ecology_report.md"
AXIS_NAMES = ("PHARMA_LABEL", "ZODIAC_LABEL", "BIO_LABEL")
POSITION_BINS = 5
FAMILY_P_GATE = 0.05
MIN_MATCHED_STRATA = 20
SEED = 41_083_301 + 8_171


def collect_events(
    rows: Sequence[Any], parity: int, weights: dict[str, float], scale: float,
) -> tuple[list[Event], dict[str, Any]]:
    output = []
    endpoint_total = 0
    endpoint_covered = 0
    for row in rows:
        if (
            row.kind != "P"
            or row.section not in APPLICATION_SECTIONS
            or folio_number(row.page) % 2 != parity
        ):
            continue
        nodes = line_nodes(row)
        for word_index, node in enumerate(nodes):
            if not (
                len(node.units) == 2
                and node.roles == ("BOUND_E", "BARE")
            ):
                continue
            position_bin = min(
                POSITION_BINS - 1,
                int(POSITION_BINS * (word_index + 0.5) / len(nodes)),
            )
            carrier_root = node.roots[0]
            value_root = node.roots[1]
            endpoint_total += 2
            endpoint_covered += int(carrier_root in weights) + int(value_root in weights)
            output.append(Event(
                page=row.page,
                locus=row.locus,
                word_index=word_index + 1,
                position_bin=position_bin,
                carrier=node.units[0],
                carrier_root=carrier_root,
                value_root=value_root,
                is_che=node.units[0] == "che",
                delta=(
                    weights.get(value_root, 0.0)
                    - weights.get(carrier_root, 0.0)
                ) / scale,
            ))
    return output, {
        "events": len(output),
        "che_events": sum(event.is_che for event in output),
        "other_carrier_events": sum(not event.is_che for event in output),
        "endpoint_coverage": endpoint_covered / max(endpoint_total, 1),
    }


def evaluate_axis(
    rows: Sequence[Any], spec: Any, repeats: int, seed: int,
) -> dict[str, Any]:
    weights = train_axis(list(rows), spec, None)
    scale = source_scale(list(rows), spec, weights)
    output = {
        "source_validation": source_validation(list(rows), spec),
        "source_roots": len(weights),
        "source_scale": scale,
        "panels": {},
    }
    for parity, parity_name in ((1, "odd"), (0, "even")):
        events, event_audit = collect_events(rows, parity, weights, scale)
        panel = {}
        for view_index, view in enumerate(VIEWS):
            values, view_audit = page_values(events, view)
            panel[view] = {
                **sign_flip(
                    list(values.values()), repeats,
                    seed + parity * 10 + view_index,
                ),
                "audit": {**event_audit, **view_audit},
                "page_values": values,
            }
        output["panels"][parity_name] = panel
    return output


def deletion_audit(
    rows: Sequence[Any], spec: Any,
) -> dict[str, Any]:
    weights = train_axis(list(rows), spec, None)
    scale = source_scale(list(rows), spec, weights)
    events = []
    for parity in (1, 0):
        local, _audit = collect_events(rows, parity, weights, scale)
        events.extend(local)
    _values, audit = page_values(events, PRIMARY)
    value_support = Counter(dict(audit["matched_values"]))
    carrier_support = Counter(dict(audit["control_carriers"]))
    value_rows = []
    for value, support in value_support.most_common(10):
        values, local = page_values(
            [event for event in events if event.value_root != value], PRIMARY,
        )
        array = list(values.values())
        value_rows.append({
            "removed": value,
            "support": support,
            "mean": float(np.mean(array)) if array else 0.0,
            "t": t_statistic(array),
            "pages": len(array),
            "matched_strata": local["matched_strata"],
        })
    carrier_rows = []
    for carrier, support in carrier_support.most_common(10):
        values, local = page_values(
            [event for event in events if event.carrier != carrier], PRIMARY,
        )
        array = list(values.values())
        carrier_rows.append({
            "removed": carrier,
            "support": support,
            "mean": float(np.mean(array)) if array else 0.0,
            "t": t_statistic(array),
            "pages": len(array),
            "matched_strata": local["matched_strata"],
        })
    return {
        "values": value_rows,
        "control_carriers": carrier_rows,
        "all_value_deletions_positive": all(row["mean"] > 0 for row in value_rows),
        "all_carrier_deletions_positive": all(row["mean"] > 0 for row in carrier_rows),
    }


def planted(
    rows: Sequence[Any], spec: Any, repeats: int, seed: int,
) -> dict[str, Any]:
    weights = train_axis(list(rows), spec, None)
    scale = source_scale(list(rows), spec, weights)
    output = {}
    for parity, parity_name in ((1, "odd"), (0, "even")):
        events, _audit = collect_events(rows, parity, weights, scale)
        shifted = [
            replace(event, delta=event.delta + (0.75 if event.is_che else 0.0))
            for event in events
        ]
        values, audit = page_values(shifted, PRIMARY)
        output[parity_name] = {
            **sign_flip(list(values.values()), repeats, seed + parity),
            "audit": audit,
        }
    return output


def report(payload: dict[str, Any]) -> str:
    lines = [
        "# Exact `che+VALUE` content direction across label ecologies", "",
        f"Decision: **{payload['status']}**", "",
        "Three root-only axes are frozen from pharmaceutical, zodiac, and biological illustration-label systems. They are applied only to disjoint H/S/T prose. Positive means that exact che-to-value rises more than other E-bound carriers after exact physical-page, value-root, and word-position matching.", "",
        "| axis | reading | split | absolute rise / six-view p | matched excess / six-view p | matched pages / strata |",
        "|---|---|---|---:|---:|---:|",
    ]
    for axis in AXIS_NAMES:
        for edition in SOURCES:
            for parity in ("odd", "even"):
                panel = payload["axes"][axis][edition]["panels"][parity]
                absolute = panel["ABSOLUTE_RISE"]
                matched = panel["VALUE_MATCHED_EXCESS"]
                lines.append(
                    f"| {axis} | {edition} | {parity} | "
                    f"{absolute['mean']:+.4f} / {absolute['family_p']:.6g} | "
                    f"{matched['mean']:+.4f} / {matched['family_p']:.6g} | "
                    f"{matched['pages']} / {matched['audit']['matched_strata']} |"
                )
    lines += ["", "## Robustness", ""]
    for axis in AXIS_NAMES:
        deletion = payload["deletions"][axis]
        lines.append(
            f"- {axis}: top-10 value deletions all positive="
            f"{deletion['all_value_deletions_positive']}; top-10 control-carrier "
            f"deletions all positive={deletion['all_carrier_deletions_positive']}."
        )
    inherited = payload["inherited_pharmaceutical_process_control"]
    lines += [
        "",
        f"The earlier pharmaceutical-axis generated-process audit remains inherited rather than recounted: {inherited['joint_exceedances']}/{inherited['controls']} axes passed source plus target (p={inherited['joint_p']:.6g}); {inherited['target_only_exceedances']}/{inherited['controls']} matched target magnitude when source validity was ignored (p={inherited['target_only_p']:.6g}).",
        "",
        "## Interpretation", "",
        payload["interpretation"], "",
        f"Runtime: {payload['runtime_seconds']:.3f} seconds; cached text only.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--permutations", type=int, default=200_000)
    args = parser.parse_args()
    started = time.perf_counter()

    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    if prior["status"] != "MULTI_LABEL_D_HEADEDNESS_CONFIRMED":
        raise RuntimeError("multi-label axis evidence changed")
    if tuple(prior["confirmed_axes"]) != AXIS_NAMES:
        raise RuntimeError(f"frozen axis inventory changed: {prior['confirmed_axes']}")
    prior_che = json.loads(PRIOR_CHE.read_text(encoding="utf-8"))
    if prior_che["status"] != "CHE_LOW_CONTENT_CARRIER_TO_HIGHER_CONTENT_VALUE_QUALIFIED_CONFIRMED":
        raise RuntimeError("prior che direction changed")

    specs = {spec.name: spec for spec in AXES if spec.name in AXIS_NAMES}
    corpora = {edition: parse_rows(path) for edition, path in SOURCES.items()}
    axes: dict[str, Any] = {axis: {} for axis in AXIS_NAMES}
    for axis_index, axis in enumerate(AXIS_NAMES):
        spec = specs[axis]
        for edition_index, (edition, rows) in enumerate(corpora.items()):
            axes[axis][edition] = evaluate_axis(
                rows, spec, args.permutations,
                SEED + axis_index * 10_000 + edition_index * 100,
            )

    # Correct the three predeclared semantic axes and both required views
    # within each reading/parity.
    for edition in SOURCES:
        for parity in ("odd", "even"):
            for axis in AXIS_NAMES:
                for view in VIEWS:
                    row = axes[axis][edition]["panels"][parity][view]
                    row["family_p"] = min(
                        1.0, len(AXIS_NAMES) * len(VIEWS) * row["p"],
                    )

    deletions = {
        axis: deletion_audit(corpora["ZL3b"], specs[axis])
        for axis in AXIS_NAMES
    }
    plant = planted(
        corpora["ZL3b"], specs["PHARMA_LABEL"], args.permutations,
        SEED + 90_000,
    )

    source_pass = all(
        axes[axis][edition]["source_validation"]["passed"]
        for axis in AXIS_NAMES for edition in SOURCES
    )
    support_pass = all(
        axes[axis][edition]["panels"][parity][PRIMARY]["audit"]["matched_strata"]
        >= MIN_MATCHED_STRATA
        for axis in AXIS_NAMES for edition in SOURCES
        for parity in ("odd", "even")
    )
    panels_pass = all(
        axes[axis][edition]["panels"][parity][view]["mean"] > 0
        and axes[axis][edition]["panels"][parity][view]["family_p"] <= FAMILY_P_GATE
        for axis in AXIS_NAMES for edition in SOURCES
        for parity in ("odd", "even") for view in VIEWS
    )
    deletions_pass = all(
        deletions[axis]["all_value_deletions_positive"]
        and deletions[axis]["all_carrier_deletions_positive"]
        for axis in AXIS_NAMES
    )
    plant_pass = all(
        row["mean"] > 0 and row["p"] <= 0.01 for row in plant.values()
    )
    passed = source_pass and support_pass and panels_pass and deletions_pass and plant_pass
    status = (
        "CHE_CONTENT_DIRECTION_CROSS_ECOLOGY_CONFIRMED"
        if passed else "CHE_CONTENT_DIRECTION_CROSS_ECOLOGY_NOT_CONFIRMED"
    )
    interpretation = (
        "The lower-content che carrier to higher-content carried-value direction transfers through all three independently validated label ecologies on disjoint prose. This upgrades the relation from a pharmaceutical-axis-specific clue to a cross-ecology relative content direction. It remains a structural semantic relation, not evidence that che is a verb, copula, classifier, preposition, IS, HAS, or any English lexeme; the carried value is not thereby a noun or name."
        if passed else
        "The exact che-to-value direction does not clear the complete three-axis transfer gate. Retain the v0.47 pharmaceutical-axis-qualified direction only; do not call it a manuscript-general semantic head relation or assign an English gloss."
    )
    inherited = {
        key: prior_che["process_controls"][key]
        for key in (
            "controls", "joint_exceedances", "joint_p",
            "target_only_exceedances", "target_only_p", "source_eligible",
        )
    }
    payload = {
        "status": status,
        "design": {
            "frozen_axes": list(AXIS_NAMES),
            "application_sections": sorted(APPLICATION_SECTIONS),
            "conditioning": "physical page + carried value root + word-position quintile",
            "required_views": list(VIEWS),
            "family_p_gate": FAMILY_P_GATE,
            "minimum_matched_strata": MIN_MATCHED_STRATA,
            "alternate_transcriptions_are_robustness_readings": True,
        },
        "axes": axes,
        "deletions": deletions,
        "plant": plant,
        "inherited_pharmaceutical_process_control": inherited,
        "gates": {
            "source": source_pass,
            "support": support_pass,
            "panels": panels_pass,
            "deletions": deletions_pass,
            "plant": plant_pass,
        },
        "interpretation": interpretation,
        "runtime_seconds": time.perf_counter() - started,
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    OUTPUT_REPORT.write_text(report(payload), encoding="utf-8")
    print(json.dumps({
        "status": status,
        "gates": payload["gates"],
        "panels": {
            axis: {
                edition: {
                    parity: {
                        view: {
                            "mean": axes[axis][edition]["panels"][parity][view]["mean"],
                            "t": axes[axis][edition]["panels"][parity][view]["t"],
                            "family_p": axes[axis][edition]["panels"][parity][view]["family_p"],
                            "strata": axes[axis][edition]["panels"][parity][view]["audit"]["matched_strata"],
                        }
                        for view in VIEWS
                    }
                    for parity in ("odd", "even")
                }
                for edition in SOURCES
            }
            for axis in AXIS_NAMES
        },
        "runtime_seconds": payload["runtime_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
