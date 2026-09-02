#!/usr/bin/env python3
"""Reproducible post-result route feasibility diagnostics for GDT750."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt750_form_gated_direct_host_dispatch"
RUN = BASE / "src/run.py"
DEFAULT_OUTPUT = BASE / "artifacts/ROUTE_FEASIBILITY.json"
ALL_AXES = (
    "HOT", "COLD", "DRY", "MOIST", "BEGIN_STAGE", "MIDDLE_STAGE",
    "END_STAGE", "AMOUNT", "PART", "MATERIAL", "PREPARATION", "PROCESS",
    "PASS",
)


def load_run():
    spec = importlib.util.spec_from_file_location("gdt750_for_route_diagnostic", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {RUN}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def broad_hosts(module, context, surface: str, locus: str, ordinal: int) -> list[set[str]]:
    line = context.by_line[locus]
    hosts: list[set[str]] = []
    for offset in (-1, 1):
        host_ordinal = ordinal + offset
        if not 1 <= host_ordinal <= len(line):
            continue
        token = line[host_ordinal - 1]
        if token["eva"] == surface or module.levenshtein(surface, token["eva"]) != 1:
            continue
        cell = context.cells[(locus, host_ordinal)]
        host_axes = set(module.g749.g746.clean_axes(
            cell,
            context.exact[(locus, int(token["token_index"]))],
            context.patterns,
        ))
        if "CLOSE" in host_axes:
            continue
        host_axes &= set(ALL_AXES)
        if host_axes:
            hosts.append(host_axes)
    return hosts


def build() -> dict[str, object]:
    module = load_run()
    context = module.Context()
    targets = module.g749.build_targets()
    references = module.g749.reference_specs()
    target_audit, feature_rows, _ = module.g749.build_occurrence_audit(
        targets, references
    )

    reference_quality = {
        row["known_surface"]: set(module.split_axes(row["known_axes"]))
        & set(module.QUALITY_STAGE_AXES)
        for row in references
    }
    open_positions: defaultdict[str, list[tuple[str, int]]] = defaultdict(list)
    exact_occurrences: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    canonical_axes_rows: defaultdict[str, list[tuple[str, ...]]] = defaultdict(list)
    for locus, line in context.by_line.items():
        for ordinal, token in enumerate(line, start=1):
            exact = context.exact[(locus, int(token["token_index"]))]
            cell = context.cells[(locus, ordinal)]
            if exact:
                exact_occurrences[token["eva"]].append({
                    "locus": locus,
                    "ordinal": ordinal,
                    "line_length": len(line),
                })
            clean = tuple(module.g749.g746.clean_axes(
                cell, exact, context.patterns
            ))
            if clean:
                canonical_axes_rows[token["eva"]].append(clean)
            if exact and cell["unknown_v99r7"] == "1":
                open_positions[cell["surface"]].append((locus, ordinal))

    recurrent = {
        surface: positions for surface, positions in open_positions.items()
        if len(positions) >= 2
    }
    open_priors: dict[tuple[str, int], dict[str, object]] = {}
    eligible: dict[str, list[tuple[str, int]]] = {}
    for surface, positions in recurrent.items():
        prior = module.form_prior(surface, 1, reference_quality)
        open_priors[(surface, 1)] = prior
        if prior["prior_axes"]:
            eligible[surface] = positions
    discovery = {
        (row["target_surface"], row["locus"], int(row["token_ordinal"]))
        for row in target_audit if int(row["gdt748_discovery_position"])
    }
    open_active: list[tuple[str, str, int, str]] = []
    for surface, positions in eligible.items():
        for locus, ordinal in positions:
            prediction = module.predict(
                context, surface, locus, ordinal, module.VARIANTS[2], open_priors
            )
            if prediction["emitted_axes"]:
                open_active.append((
                    surface, locus, ordinal,
                    module.joined(prediction["emitted_axes"]),
                ))
    active_outside_discovery = [
        row for row in open_active if (row[0], row[1], row[2]) not in discovery
    ]

    reference_all = {
        row["known_surface"]: set(module.split_axes(row["known_axes"]))
        & set(ALL_AXES)
        for row in references
    }
    broad_rows = [
        row for row in feature_rows
        if row["surface"] in reference_all and int(row["reader_exact"])
        and reference_all[str(row["surface"])]
    ]
    broad_total = Counter()
    broad_axis: defaultdict[str, Counter[str]] = defaultdict(Counter)
    broad_false_surfaces = Counter()
    for row in broad_rows:
        surface = str(row["surface"])
        neighbors = [
            known for known in reference_all
            if known != surface and module.levenshtein(surface, known) == 1
        ]
        counts = Counter(
            axis for known in neighbors for axis in reference_all[known]
        )
        allowed = {axis for axis in ALL_AXES if counts[axis] >= 2}
        hosts = broad_hosts(
            module, context, surface, str(row["locus"]),
            int(row["token_ordinal"]),
        )
        predicted = set().union(*hosts) & allowed if hosts else set()
        for dimension in (
            {"HOT", "COLD"}, {"DRY", "MOIST"},
            {"BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE"},
        ):
            if len(predicted & dimension) > 1:
                predicted -= dimension
        truth = reference_all[surface]
        true = predicted & truth
        false = predicted - truth
        missed = truth - predicted
        broad_total.update({
            "positions": bool(predicted),
            "contradiction_positions": bool(false),
            "tp": len(true), "fp": len(false), "fn": len(missed),
        })
        broad_false_surfaces.update({surface: len(false)})
        for axis in ALL_AXES:
            broad_axis[axis].update({
                "tp": axis in true, "fp": axis in false, "fn": axis in missed,
            })

    canonical_axes = {
        surface: set(Counter(rows).most_common(1)[0][0])
        for surface, rows in canonical_axes_rows.items()
    }
    q_pairs = [
        (surface, surface[1:]) for surface in sorted(canonical_axes)
        if surface.startswith("q") and surface[1:] in canonical_axes
    ]
    q_occurrences = sum(len(exact_occurrences[q_surface]) for q_surface, _ in q_pairs)
    base_occurrences = sum(len(exact_occurrences[base]) for _, base in q_pairs)

    q_first = base_first = q_last = base_last = 0
    q_first_signs = Counter()
    q_last_signs = Counter()
    normalized_deltas: list[float] = []
    for q_surface, base in q_pairs:
        q_rows = exact_occurrences[q_surface]
        base_rows = exact_occurrences[base]
        q_first_rate = sum(row["ordinal"] == 1 for row in q_rows) / len(q_rows)
        base_first_rate = sum(row["ordinal"] == 1 for row in base_rows) / len(base_rows)
        q_last_rate = sum(row["ordinal"] == row["line_length"] for row in q_rows) / len(q_rows)
        base_last_rate = sum(row["ordinal"] == row["line_length"] for row in base_rows) / len(base_rows)
        q_first += sum(row["ordinal"] == 1 for row in q_rows)
        base_first += sum(row["ordinal"] == 1 for row in base_rows)
        q_last += sum(row["ordinal"] == row["line_length"] for row in q_rows)
        base_last += sum(row["ordinal"] == row["line_length"] for row in base_rows)
        q_first_signs.update({
            "q_higher" if q_first_rate > base_first_rate else
            "base_higher" if base_first_rate > q_first_rate else "tie": 1
        })
        q_last_signs.update({
            "q_higher" if q_last_rate > base_last_rate else
            "base_higher" if base_last_rate > q_last_rate else "tie": 1
        })
        q_position = sum(
            (int(row["ordinal"]) - 1) / max(1, int(row["line_length"]) - 1)
            for row in q_rows
        ) / len(q_rows)
        base_position = sum(
            (int(row["ordinal"]) - 1) / max(1, int(row["line_length"]) - 1)
            for row in base_rows
        ) / len(base_rows)
        normalized_deltas.append(q_position - base_position)

    direct_contacts: list[tuple[str, str, str]] = []
    for q_surface, base in q_pairs:
        for occurrence in exact_occurrences[q_surface]:
            locus = str(occurrence["locus"])
            ordinal = int(occurrence["ordinal"])
            line = context.by_line[locus]
            for offset in (-1, 1):
                neighbor_ordinal = ordinal + offset
                if not 1 <= neighbor_ordinal <= len(line):
                    continue
                token = line[neighbor_ordinal - 1]
                if token["eva"] != base:
                    continue
                if not context.exact[(locus, int(token["token_index"]))]:
                    continue
                direct_contacts.append((q_surface, base, locus))

    return {
        "schema": "GDT750_ROUTE_FEASIBILITY_V1",
        "status": "OPEN_EXPANSION_ZERO_NEW__BROAD_CARRIER_RULE_FAILS__Q_BASE_SHELL_ROUTE_LIVE",
        "open_quality_stage_expansion": {
            "reader_exact_open_positions": sum(map(len, open_positions.values())),
            "open_surfaces": len(open_positions),
            "recurrent_open_surfaces": len(recurrent),
            "recurrent_open_positions": sum(map(len, recurrent.values())),
            "distance1_multi_prior_surfaces": len(eligible),
            "distance1_multi_prior_positions": sum(map(len, eligible.values())),
            "active_surfaces": len({row[0] for row in open_active}),
            "active_positions": len(open_active),
            "active_cards": [
                {"surface": surface, "locus": locus, "token_ordinal": ordinal, "axes": axis_value}
                for surface, locus, ordinal, axis_value in open_active
            ],
            "active_outside_prior_discovery_positions": len(active_outside_discovery),
            "disposition": "DO_NOT_OPEN_NAIVE_ALL_RECURRENT_ROUTE",
        },
        "broad_axis_sensitivity": {
            "known_occurrences": len(broad_rows),
            "predicted_positions": broad_total["positions"],
            "contradiction_positions": broad_total["contradiction_positions"],
            "tp": broad_total["tp"], "fp": broad_total["fp"],
            "fn": broad_total["fn"],
            "precision": round(broad_total["tp"] / (broad_total["tp"] + broad_total["fp"]), 6),
            "recall": round(broad_total["tp"] / (broad_total["tp"] + broad_total["fn"]), 6),
            "axis_results": {
                axis: dict(broad_axis[axis]) for axis in ALL_AXES
                if broad_axis[axis]["tp"] or broad_axis[axis]["fp"]
            },
            "false_axis_surfaces": dict(sorted(
                (surface, count) for surface, count in broad_false_surfaces.items()
                if count
            )),
            "disposition": "REJECT_BLANKET_CARRIER_AMOUNT_PROCESS_EXTENSION",
        },
        "q_base_shell_feasibility": {
            "clean_complete_surfaces": len(canonical_axes),
            "q_base_pairs": len(q_pairs),
            "quality_stage_exactly_preserved_pairs": sum(
                (canonical_axes[q_surface] & set(module.QUALITY_STAGE_AXES))
                == (canonical_axes[base] & set(module.QUALITY_STAGE_AXES))
                for q_surface, base in q_pairs
            ),
            "unprefixed_preparation_q_not_pairs": sum(
                "PREPARATION" in canonical_axes[base]
                and "PREPARATION" not in canonical_axes[q_surface]
                for q_surface, base in q_pairs
            ),
            "q_preparation_unprefixed_not_pairs": sum(
                "PREPARATION" in canonical_axes[q_surface]
                and "PREPARATION" not in canonical_axes[base]
                for q_surface, base in q_pairs
            ),
            "reader_exact_q_occurrences": q_occurrences,
            "reader_exact_unprefixed_occurrences": base_occurrences,
            "raw_q_line_first": q_first,
            "raw_unprefixed_line_first": base_first,
            "raw_q_line_last": q_last,
            "raw_unprefixed_line_last": base_last,
            "pair_balanced_line_first_signs": dict(sorted(q_first_signs.items())),
            "pair_balanced_line_last_signs": dict(sorted(q_last_signs.items())),
            "pair_balanced_mean_normalized_position_delta_q_minus_unprefixed": round(
                sum(normalized_deltas) / len(normalized_deltas), 6
            ),
            "q_earlier_pairs": sum(delta < 0 for delta in normalized_deltas),
            "q_later_pairs": sum(delta > 0 for delta in normalized_deltas),
            "direct_reader_exact_q_base_contacts": len(direct_contacts),
            "direct_contact_pair_types": len({row[:2] for row in direct_contacts}),
            "direct_contact_pages": len({row[2].split(".")[0] for row in direct_contacts}),
            "interpretation": (
                "The semantic asymmetry is inherited and requires an independent "
                "raw-placement audit; the earlier q-side and fewer q-side line ends "
                "make that bounded complete-pair audit the live route."
            ),
        },
        "claim_ceiling": (
            "Route navigation only. No q character, prefix, morpheme, sound, lexeme, "
            "plaintext, preparation identity or other component value is established."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = build()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
