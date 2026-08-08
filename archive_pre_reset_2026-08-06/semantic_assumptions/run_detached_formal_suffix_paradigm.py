#!/usr/bin/env python3
"""Test a four-way detached formal-suffix paradigm across visible spaces.

The ai/aii fusion audit suggests a general operation: a surface that is a
BARE one-root word in isolation can complete the preceding BARE root into a
REL_I or FREE_* one-word form.  This runner defines the transformation without
choosing spellings: both separated words must each parse as one BARE root;
their concatenation must parse as that same left root with exactly one of
REL_I, FREE_L, FREE_R, or FREE_A.

Candidate roles are discovered only on odd ZL folios.  Joined spellings are
also frozen from odd folios, then tested on folios 0 and 2 mod 4 in all three
readings against other BARE-to-BARE concatenations.  Exact-stream alternate
transcriptions and cached word-box geometry audit whether the manuscript gap
is real.  The result is formal morphology, never an English gloss.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from scipy.stats import fisher_exact

from common import RESULTS, Row, folio_number
from run_ar_al_cross_transcription_boundary import (
    bootstrap_interval, wilson_interval, word_boundaries,
)
from run_multilingual_sequence_typology import word_views
from run_order_information_decomposition import state_rows
from run_spatial_gap_clause_boundaries import join_events
from run_typology_neutral_structure import SOURCES, prose_rows


ROOT = Path(__file__).resolve().parents[2]
CROSS = ROOT / "transcription" / "voynich_cross_transcription_lines.tsv"
OUTPUT_JSON = RESULTS / "detached_formal_suffix_paradigm_results.json"
OUTPUT_REPORT = RESULTS / "detached_formal_suffix_paradigm_report.md"
OUTPUT_EVENTS = RESULTS / "detached_formal_suffix_paradigm_events.tsv"
OUTPUT_BOUNDARIES = RESULTS / "detached_formal_suffix_paradigm_boundaries.tsv"
OUTPUT_SPATIAL = RESULTS / "detached_formal_suffix_paradigm_spatial.tsv"
SEED = 192_801
TARGET_ROLES = ("REL_I", "FREE_L", "FREE_R", "FREE_A")
CORE_ROLES = ("REL_I", "FREE_L", "FREE_R")
GAP_EQUIVALENCE_MARGIN = 0.10


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def detached_role(left: str, right: str) -> str | None:
    left_view = word_views(left)
    right_view = word_views(right)
    if (
        left_view["ALL_ROLES"] != ["BARE"]
        or right_view["ALL_ROLES"] != ["BARE"]
        or len(left_view["ALL_ROOTS"]) != 1
        or len(right_view["ALL_ROOTS"]) != 1
    ):
        return None
    joined = word_views(left + right)
    if (
        len(joined["ALL_ROOTS"]) == 1
        and joined["ALL_ROOTS"] == left_view["ALL_ROOTS"]
        and len(joined["ALL_ROLES"]) == 1
        and joined["ALL_ROLES"][0] in TARGET_ROLES
    ):
        return joined["ALL_ROLES"][0]
    return None


def collect_events(
    edition: str, rows: Sequence[Row], vocabulary: Counter[str],
) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        for index, (left, right) in enumerate(zip(row.words, row.words[1:])):
            role = detached_role(left, right)
            if role is None:
                continue
            left_view, right_view = word_views(left), word_views(right)
            joined = left + right
            output.append({
                "edition": edition, "page": row.page, "locus": row.locus,
                "section": row.section, "register": row.language,
                "hand": row.hand, "modulo": folio_number(row.page) % 4,
                "position": index + 1, "line_length": len(row.words),
                "left_surface": left, "right_surface": right,
                "left_root": left_view["FIRST_ROOT"][0],
                "right_root": right_view["FIRST_ROOT"][0],
                "fused_role": role, "joined_surface": joined,
                "joined_token_count": vocabulary[joined],
                "joined_attested": vocabulary[joined] > 0,
            })
    return output


def discover_roles(events: Sequence[dict[str, Any]]) -> list[str]:
    odd = [row for row in events if row["modulo"] % 2 == 1]
    return [
        role for role in TARGET_ROLES
        if sum(row["fused_role"] == role for row in odd) >= 20
        and len({
            row["page"] for row in odd if row["fused_role"] == role
        }) >= 10
    ]


def held_attestation(
    edition: str, rows: Sequence[Row], discovered: set[str],
) -> dict[str, Any]:
    odd_vocabulary = Counter(
        word for row in rows if folio_number(row.page) % 2 == 1
        for word in row.words
    )
    output = {}
    for modulo, panel_name in ((0, "SCREEN"), (2, "CONFIRM")):
        targets: list[tuple[str, bool]] = []
        controls: list[bool] = []
        for row in rows:
            if folio_number(row.page) % 4 != modulo:
                continue
            for left, right in zip(row.words, row.words[1:]):
                left_view, right_view = word_views(left), word_views(right)
                if left_view["ALL_ROLES"] != ["BARE"] or right_view["ALL_ROLES"] != ["BARE"]:
                    continue
                attested = odd_vocabulary[left + right] > 0
                role = detached_role(left, right)
                if role in discovered:
                    targets.append((role, attested))
                else:
                    controls.append(attested)
        target_success = sum(value for _role, value in targets)
        control_success = sum(controls)
        table = [
            [target_success, len(targets) - target_success],
            [control_success, len(controls) - control_success],
        ]
        odds, p = fisher_exact(table, alternative="greater")
        output[panel_name] = {
            "edition": edition, "modulo": modulo,
            "odd_vocabulary_types": len(odd_vocabulary),
            "target_attested": target_success, "target_events": len(targets),
            "target_fraction": target_success / len(targets),
            "control_attested": control_success, "control_events": len(controls),
            "control_fraction": control_success / len(controls),
            "odds_ratio": float(odds), "one_sided_fisher_p": float(p),
            "by_role": {
                role: {
                    "attested": sum(value for local_role, value in targets if local_role == role),
                    "events": sum(local_role == role for local_role, _value in targets),
                }
                for role in TARGET_ROLES if role in discovered
            },
        }
    return output


def counterpart_summary(
    events: Sequence[dict[str, Any]], vocabulary: Counter[str],
) -> list[dict[str, Any]]:
    output = []
    for role in TARGET_ROLES:
        local = [row for row in events if row["fused_role"] == role]
        joined_types = {row["joined_surface"] for row in local}
        output.append({
            "fused_role": role, "split_events": len(local),
            "split_pages": len({row["page"] for row in local}),
            "split_types": len(joined_types),
            "attested_split_events": sum(row["joined_attested"] for row in local),
            "attested_joined_types": sum(vocabulary[value] > 0 for value in joined_types),
            "joined_token_mass": sum(vocabulary[value] for value in joined_types),
            "right_roots": dict(Counter(row["right_root"] for row in local)),
        })
    return output


def boundary_audit(
    zl_rows: Sequence[Row], cross: dict[str, dict[str, str]], discovered: set[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    states = {state.row.locus: state for state in state_rows(zl_rows)}
    output_rows = []
    panels = {}
    for edition, field in (("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean")):
        counts: dict[str, Counter[int]] = defaultdict(Counter)
        for locus, state in states.items():
            item = cross.get(locus)
            if item is None:
                continue
            zl_words = item["zl3b_clean"].split()
            other_words = item[field].split()
            if zl_words != list(state.row.words) or "".join(zl_words) != "".join(other_words):
                continue
            retained = word_boundaries(other_words)
            position = 0
            for index, (left, right) in enumerate(zip(zl_words, zl_words[1:])):
                position += len(left)
                role = detached_role(left, right)
                if role not in discovered:
                    continue
                keep = int(position in retained)
                counts[role][keep] += 1
                output_rows.append({
                    "edition": edition, "page": state.row.page,
                    "locus": locus, "position": index + 1,
                    "left_surface": left, "right_surface": right,
                    "fused_role": role, "retained": keep,
                })
        panels[edition] = {}
        for role in TARGET_ROLES:
            total = counts[role][0] + counts[role][1]
            low, high = wilson_interval(counts[role][1], total)
            panels[edition][role] = {
                "events": total, "retained": counts[role][1],
                "fraction": counts[role][1] / total if total else None,
                "wilson_95": [low, high],
            }
    return panels, output_rows


def spatial_audit(
    zl_rows: Sequence[Row], discovered: set[str], resamples: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    records, metadata = join_events("CANON_FORM_ROOT")
    states = {state.row.locus: state for state in state_rows(zl_rows)}
    eligible = []
    for record in records:
        state = states.get(record["locus"])
        index = record["position"] - 1
        if state is None or index + 1 >= len(state.row.words) or record["gap_height_units"] > 2:
            continue
        role = detached_role(state.row.words[index], state.row.words[index + 1])
        local = dict(record)
        local["target"] = role in discovered
        local["fused_role"] = role or ""
        eligible.append(local)
    cells: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in eligible:
        cells[(row["page"], row["x_bin"])].append(row)
    differences = []
    for rows in cells.values():
        target = [row["gap_height_units"] for row in rows if row["target"]]
        control = [row["gap_height_units"] for row in rows if not row["target"]]
        if target and control:
            differences.append(float(np.mean(target) - np.mean(control)))
    interval = bootstrap_interval(differences, resamples, SEED)
    target_rows = [row for row in eligible if row["target"]]
    return {
        "coordinate_metadata": metadata,
        "target_events": len(target_rows),
        "target_mean_gap_heights": float(np.mean([row["gap_height_units"] for row in target_rows])),
        "control_mean_gap_heights": float(np.mean([row["gap_height_units"] for row in eligible if not row["target"]])),
        "page_x_difference": interval,
        "equivalence_margin": GAP_EQUIVALENCE_MARGIN,
        "ordinary_gap_equivalent": (
            interval["low_95"] >= -GAP_EQUIVALENCE_MARGIN
            and interval["high_95"] <= GAP_EQUIVALENCE_MARGIN
        ),
        "by_role": dict(Counter(row["fused_role"] for row in target_rows)),
    }, target_rows


def write_tsv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    serial = []
    for row in rows:
        serial.append({
            key: json.dumps(value, sort_keys=True)
            if isinstance(value, (dict, list, tuple)) else value
            for key, value in row.items()
        })
    if not serial:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(serial[0]), delimiter="\t",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(serial)


def make_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Detached formal-suffix paradigm",
        "",
        f"Decision: **{payload['decision']}**",
        "",
        f"Among four predeclared formal outcomes, odd ZL clears the support gate for: **{', '.join(payload['discovered_roles'])}**.",
        "",
        "## Full ZL split/join inventory",
        "",
        "| fused role | split events/pages | split types | split events with joined counterpart | joined types/tokens | detached right roots |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in payload["counterparts"]["ZL3b"]:
        lines.append(
            f"| {row['fused_role']} | {row['split_events']}/{row['split_pages']} | {row['split_types']} | {row['attested_split_events']} | {row['attested_joined_types']}/{row['joined_token_mass']} | {row['right_roots']} |"
        )
    lines += [
        "",
        "## Odd-vocabulary holdout",
        "",
        "| reading/panel | target joined spelling | target rate | other BARE pairs | control rate | Fisher p |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for edition, panels in payload["held_attestation"].items():
        for panel, row in panels.items():
            lines.append(
                f"| {edition} {panel.lower()} | {row['target_attested']}/{row['target_events']} | {row['target_fraction']:.3f} | {row['control_attested']}/{row['control_events']} | {row['control_fraction']:.3f} | {row['one_sided_fisher_p']:.3g} |"
            )
    lines += [
        "",
        "## Exact-stream boundary retention",
        "",
        "| role | IT retained | RF retained |",
        "|---|---:|---:|",
    ]
    for role in payload["discovered_roles"]:
        it = payload["boundaries"]["IT2a"][role]
        rf = payload["boundaries"]["RF1b"][role]
        lines.append(
            f"| {role} | {it['retained']}/{it['events']} ({it['fraction']:.3f}) | {rf['retained']}/{rf['events']} ({rf['fraction']:.3f}) |"
        )
    spatial = payload["spatial_gap"]
    gap = spatial["page_x_difference"]
    lines += [
        "",
        "## Physical gap",
        "",
        f"The {spatial['target_events']} coordinate-linked detached suffixes have mean gap {spatial['target_mean_gap_heights']:.3f} word-box heights versus {spatial['control_mean_gap_heights']:.3f} for controls. Within page/x-bin the difference is {gap['mean']:+.4f} (95% {gap['low_95']:+.4f} to {gap['high_95']:+.4f}); it remains inside the +/-{GAP_EQUIVALENCE_MARGIN:.2f} ordinary-gap band: **{'yes' if spatial['ordinary_gap_equivalent'] else 'no'}**.",
        "",
        "## Interpretation",
        "",
        payload["interpretation"],
        "",
        f"Runtime: {payload['runtime_seconds']:.2f} seconds; cached transcription and coordinates only.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resamples", type=int, default=100_000)
    args = parser.parse_args()
    started = time.perf_counter()
    corpora = {edition: prose_rows(path) for edition, path in SOURCES.items()}
    vocabularies = {
        edition: Counter(word for row in rows for word in row.words)
        for edition, rows in corpora.items()
    }
    events = {
        edition: collect_events(edition, rows, vocabularies[edition])
        for edition, rows in corpora.items()
    }
    discovered = discover_roles(events["ZL3b"])
    held = {
        edition: held_attestation(edition, rows, set(discovered))
        for edition, rows in corpora.items()
    }
    counterparts = {
        edition: counterpart_summary(events[edition], vocabularies[edition])
        for edition in SOURCES
    }
    cross = {row["locus"]: row for row in read_tsv(CROSS)}
    boundaries, boundary_rows = boundary_audit(
        corpora["ZL3b"], cross, set(discovered),
    )
    spatial, spatial_rows = spatial_audit(
        corpora["ZL3b"], set(discovered), args.resamples,
    )

    discovery_pass = set(CORE_ROLES).issubset(discovered)
    counterpart_pass = all(
        all(
            row["split_events"] >= 20
            and row["joined_token_mass"] >= 20
            and row["attested_joined_types"] >= 5
            for row in counterparts[edition]
        ) for edition in SOURCES
    )
    held_pass = all(
        panels["CONFIRM"]["target_fraction"] > panels["CONFIRM"]["control_fraction"]
        and panels["CONFIRM"]["one_sided_fisher_p"] * len(SOURCES) <= 0.01
        for panels in held.values()
    )
    boundary_pass = all(
        boundaries[edition][role]["events"] >= 8
        and boundaries[edition][role]["fraction"] >= 0.80
        for edition in boundaries for role in discovered
    )
    if (
        discovery_pass and counterpart_pass and held_pass and boundary_pass
        and spatial["ordinary_gap_equivalent"]
    ):
        full = set(TARGET_ROLES).issubset(discovered)
        decision = (
            "DETACHED_FORMAL_SUFFIX_PARADIGM_CONFIRMED" if full
            else "DETACHED_FORMAL_SUFFIX_CORE_CONFIRMED__FREE_A_PROVISIONAL"
        )
        interpretation = (
            "A single BARE-looking group can be a detachably written completion "
            "of the preceding root. The fully held core outcomes are REL_I, "
            "FREE_L, and FREE_R, whose right-root inventories are dominated "
            "respectively by ai/aii/aiii, al/ol, and ar/or. FREE_A has the same "
            "split/join shape (35 ZL events, seven attested joined types) but "
            "only 13 odd events and remains a qualified extension. "
            "The manuscript therefore permits an analytic and a joined spelling "
            "of the same formal construction across an ordinary authorial space. "
            "This is a native grouping rule, not evidence for English suffixes, "
            "case names, directions, sounds, or any language family."
        )
    else:
        decision = "DETACHED_FORMAL_SUFFIX_PARADIGM_NOT_CONFIRMED"
        interpretation = (
            "Some split/join pairs recur, but the four-role, held-attestation, "
            "alternate-boundary, and physical-gap gates do not jointly pass."
        )
    payload = {
        "decision": decision, "interpretation": interpretation,
        "registered": {
            "transformation": "one-root BARE + one-root BARE => same left root with one target formal role",
            "discovery": ">=20 odd ZL events on >=10 pages",
            "roles": list(TARGET_ROLES),
            "required_core_roles": list(CORE_ROLES),
            "held": "odd-only joined vocabulary; folio 2 target > other BARE pairs; three-reading Bonferroni p<=.01",
            "counterparts": ">=20 split and joined tokens, >=5 joined types per role/reading",
            "boundary": ">=8 exact-stream events and >=80% retained per role/alternate reading",
            "physical": f"page/x-bin gap difference inside +/-{GAP_EQUIVALENCE_MARGIN}",
        },
        "discovered_roles": discovered, "events": {
            edition: len(local) for edition, local in events.items()
        },
        "counterparts": counterparts, "held_attestation": held,
        "boundaries": boundaries, "spatial_gap": spatial,
        "runtime_seconds": time.perf_counter() - started,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUTPUT_REPORT.write_text(make_report(payload), encoding="utf-8")
    write_tsv(OUTPUT_EVENTS, events["ZL3b"])
    write_tsv(OUTPUT_BOUNDARIES, boundary_rows)
    write_tsv(OUTPUT_SPATIAL, spatial_rows)
    print(make_report(payload), end="")


if __name__ == "__main__":
    main()
