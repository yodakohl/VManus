#!/usr/bin/env python3
"""Build a narrow form-gated direct-host dispatcher for GDT749 targets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt750_form_gated_direct_host_dispatch")
EXP = ROOT / BASE_REL
DEFAULT_ARTIFACTS = EXP / "artifacts"
G749_RUN_REL = Path(
    "experiments/yolo/gdt749_outside_frame_whole_role_distribution/src/run.py"
)
G740_REPORT_REL = Path(
    "experiments/yolo/gdt740_local_host_attachment_adjudication/REPORT.md"
)

OUTPUT_NAMES = (
    "RULE_VARIANT_CALIBRATION.tsv",
    "KNOWN_1134_OCCURRENCE_CALIBRATION.tsv",
    "FORM_17_PRIOR_DECK.tsv",
    "TARGET_1684_HOST_DISPATCH_AUDIT.tsv",
    "ACTIVE_OCCURRENCE_CARDS.tsv",
    "ACTIVE_HOST_CONTACTS.tsv",
    "FORM_17_DISPATCH_PROFILE.tsv",
    "GDT750_FORM_GATED_HOST_READER.md",
    "GDT750_GDT388_HOST_EDGE_PACKET.tsv",
    "GDT750_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)

QUALITY_STAGE_AXES = (
    "HOT", "COLD", "DRY", "MOIST", "BEGIN_STAGE", "MIDDLE_STAGE",
    "END_STAGE",
)
DIMENSIONS = {
    "THERMAL": ("HOT", "COLD"),
    "MOISTURE": ("DRY", "MOIST"),
    "STAGE": ("BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE"),
}
VARIANTS = (
    ("V0_DIRECT_RAW_R1", None, 1, False, False),
    ("V1_DIRECT_NO_CLOSE_R1", None, 1, True, False),
    ("V2_D1_MULTI_FORM_R1_NO_CLOSE_ACTIVE", 1, 1, True, True),
    ("V3_D1_MULTI_FORM_R2_NO_CLOSE_DISCOVERY", 1, 2, True, True),
    ("V4_D2_MULTI_FORM_R1_NO_CLOSE_SENSITIVITY", 2, 1, True, True),
    ("V5_D2_MULTI_FORM_R2_NO_CLOSE_SENSITIVITY", 2, 2, True, True),
)
ACTIVE_VARIANT = VARIANTS[2][0]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g749 = load_module("gdt749_builder_for_gdt750", ROOT / G749_RUN_REL)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]
) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def split_axes(value: object) -> tuple[str, ...]:
    text = str(value)
    return () if text in {"", "NONE", "OPEN", "EDGE"} else tuple(text.split("|"))


def joined(values: Iterable[str]) -> str:
    chosen = set(values)
    return "|".join(axis for axis in QUALITY_STAGE_AXES if axis in chosen) or "NONE"


def count_string(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def axis_count_string(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(
        f"{axis}:{counts[axis]}" for axis in QUALITY_STAGE_AXES if counts[axis]
    ) or "NONE"


def levenshtein(left: str, right: str) -> int:
    return g749.g746.g745.levenshtein(left, right)


def form_prior(
    surface: str,
    maximum_distance: int,
    reference_axes: dict[str, set[str]],
) -> dict[str, object]:
    neighbors = [
        known for known in sorted(reference_axes)
        if known != surface and levenshtein(surface, known) <= maximum_distance
    ]
    counts = Counter(
        axis for known in neighbors for axis in reference_axes[known]
    )
    axes: set[str] = set()
    decisions: list[str] = []
    for dimension, members_tuple in DIMENSIONS.items():
        members = set(members_tuple)
        best = max((counts[axis] for axis in members), default=0)
        winners = {
            axis for axis in members if counts[axis] == best and counts[axis] >= 2
        }
        if len(winners) == 1:
            winner = next(iter(winners))
            axes.add(winner)
            decisions.append(f"{dimension}:{winner}:{best}")
        else:
            decisions.append(
                f"{dimension}:OPEN:" + ",".join(
                    f"{axis}={counts[axis]}" for axis in members_tuple
                )
            )
    return {
        "maximum_distance": maximum_distance,
        "neighbor_surfaces": neighbors,
        "neighbor_count": len(neighbors),
        "axis_counts": counts,
        "prior_axes": axes,
        "dimension_decisions": decisions,
    }


class Context:
    def __init__(self) -> None:
        self.by_line, self.exact, self.guard = (
            g749.g746.g745.g739.g738.token_context()
        )
        self.cells = g749.g746.g745.g739.g738.compact_cells()
        _, self.patterns = g749.g746.g745.g739.load_axis_specs()

    def hosts(
        self,
        surface: str,
        locus: str,
        ordinal: int,
        maximum_distance: int | None,
        radius: int,
        exclude_close: bool,
    ) -> tuple[int | None, list[dict[str, object]]]:
        line = self.by_line[locus]
        rings: defaultdict[int, list[dict[str, object]]] = defaultdict(list)
        for offset in range(-radius, radius + 1):
            if offset == 0 or not 1 <= ordinal + offset <= len(line):
                continue
            token = line[ordinal + offset - 1]
            host_surface = token["eva"]
            if host_surface == surface:
                continue
            if maximum_distance is not None:
                distance = levenshtein(surface, host_surface)
                if not 1 <= distance <= maximum_distance:
                    continue
            else:
                distance = levenshtein(surface, host_surface)
            cell = self.cells[(locus, ordinal + offset)]
            axes_all = set(
                g749.g746.clean_axes(
                    cell,
                    self.exact[(locus, int(token["token_index"]))],
                    self.patterns,
                )
            )
            if exclude_close and "CLOSE" in axes_all:
                continue
            axes = axes_all & set(QUALITY_STAGE_AXES)
            if not axes:
                continue
            rings[abs(offset)].append({
                "signed_offset": offset,
                "host_surface": host_surface,
                "host_ordinal": ordinal + offset,
                "host_axes": axes,
                "host_axes_all": axes_all,
                "whole_edit_distance": distance,
                "host_cell_id": cell["cell_id"],
            })
        if not rings:
            return None, []
        selected_ring = min(rings)
        return selected_ring, rings[selected_ring]


def predict(
    context: Context,
    surface: str,
    locus: str,
    ordinal: int,
    variant: tuple[str, int | None, int, bool, bool],
    priors: dict[tuple[str, int], dict[str, object]],
) -> dict[str, object]:
    name, maximum_distance, radius, exclude_close, use_form_prior = variant
    ring, hosts = context.hosts(
        surface, locus, ordinal, maximum_distance, radius, exclude_close
    )
    allowed = (
        set(priors[(surface, int(maximum_distance))]["prior_axes"])
        if use_form_prior and maximum_distance is not None else
        set(QUALITY_STAGE_AXES)
    )
    emitted: set[str] = set()
    conflicts: list[str] = []
    for dimension, members_tuple in DIMENSIONS.items():
        members = set(members_tuple)
        candidates = set().union(
            *(set(host["host_axes"]) & members for host in hosts)
        ) if hosts else set()
        candidates &= allowed
        if len(candidates) == 1:
            emitted.update(candidates)
        elif len(candidates) > 1:
            conflicts.append(f"{dimension}:{joined(candidates)}")
    contributing = [
        host for host in hosts if set(host["host_axes"]) & emitted
    ]
    return {
        "variant": name,
        "selected_ring": ring,
        "hosts": hosts,
        "contributing_hosts": contributing,
        "emitted_axes": emitted,
        "conflicts": conflicts,
        "allowed_prior_axes": allowed,
    }


def build_prior_decks(
    targets: list[dict[str, object]],
    references: list[dict[str, str]],
) -> tuple[list[dict[str, object]], dict[tuple[str, int], dict[str, object]], dict[str, set[str]]]:
    reference_axes = {
        row["known_surface"]: set(split_axes(row["known_axes"]))
        & set(QUALITY_STAGE_AXES)
        for row in references
    }
    priors: dict[tuple[str, int], dict[str, object]] = {}
    for surface in set(reference_axes) | {
        str(row["target_surface"]) for row in targets
    }:
        for distance in (1, 2):
            priors[(surface, distance)] = form_prior(
                surface, distance, reference_axes
            )
    output: list[dict[str, object]] = []
    for target in targets:
        surface = str(target["target_surface"])
        d1 = priors[(surface, 1)]
        d2 = priors[(surface, 2)]
        output.append({
            "gdt750_prior_id": f"G750-F{len(output) + 1:02d}",
            "target_surface": surface,
            "gdt749_prior_axes": target["prior_role_axes"],
            "distance1_reference_surfaces": "|".join(d1["neighbor_surfaces"]) or "NONE",
            "distance1_reference_count": d1["neighbor_count"],
            "distance1_axis_counts": axis_count_string(
                axis for axis, count in d1["axis_counts"].items()
                for _ in range(count)
            ),
            "distance1_multi_reference_prior_axes": joined(d1["prior_axes"]),
            "distance1_dimension_decisions": "|".join(d1["dimension_decisions"]),
            "distance2_reference_surfaces": "|".join(d2["neighbor_surfaces"]) or "NONE",
            "distance2_reference_count": d2["neighbor_count"],
            "distance2_axis_counts": axis_count_string(
                axis for axis, count in d2["axis_counts"].items()
                for _ in range(count)
            ),
            "distance2_multi_reference_prior_axes": joined(d2["prior_axes"]),
            "distance2_dimension_decisions": "|".join(d2["dimension_decisions"]),
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output, priors, reference_axes


def build_calibration(
    context: Context,
    references: list[dict[str, str]],
    feature_rows: list[dict[str, object]],
    priors: dict[tuple[str, int], dict[str, object]],
    reference_axes: dict[str, set[str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    reference_surfaces = set(reference_axes)
    rows = [
        row for row in feature_rows
        if row["surface"] in reference_surfaces
        and int(row["reader_exact"])
        and reference_axes[str(row["surface"])]
    ]
    output: list[dict[str, object]] = []
    totals = {
        variant[0]: Counter() for variant in VARIANTS
    }
    for row in rows:
        surface = str(row["surface"])
        truth = reference_axes[surface]
        built: dict[str, object] = {
            "gdt750_calibration_occurrence_id": f"G750-K{len(output) + 1:04d}",
            "known_surface": surface,
            "page": row["page"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "true_quality_stage_axes": joined(truth),
        }
        for variant in VARIANTS:
            result = predict(
                context, surface, str(row["locus"]), int(row["token_ordinal"]),
                variant, priors,
            )
            predicted = set(result["emitted_axes"])
            hit = predicted & truth
            false = predicted - truth
            missed = truth - predicted
            name = variant[0]
            built[f"{name}_predicted_axes"] = joined(predicted)
            built[f"{name}_hit_axes"] = joined(hit)
            built[f"{name}_false_axes"] = joined(false)
            built[f"{name}_selected_ring"] = result["selected_ring"] or "NONE"
            counter = totals[name]
            counter["positions"] += bool(predicted)
            counter["subset_positions"] += bool(predicted and not false)
            counter["contradiction_positions"] += bool(false)
            counter["tp"] += len(hit)
            counter["fp"] += len(false)
            counter["fn"] += len(missed)
        built.update({
            "literal_identity_credit": 0,
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
        output.append(built)
    variants: list[dict[str, object]] = []
    for variant in VARIANTS:
        name = variant[0]
        total = totals[name]
        precision = total["tp"] / (total["tp"] + total["fp"]) if total["tp"] + total["fp"] else 0.0
        recall = total["tp"] / (total["tp"] + total["fn"])
        disposition = (
            "ACTIVE_OCCURRENCE_RENDERER"
            if name == ACTIVE_VARIANT and total["fp"] == 0 else
            "DISCOVERY_ONLY_RADIUS_TWO"
            if name.startswith("V3_") else
            "SENSITIVITY_ONLY_DISTANCE_TWO"
            if name.startswith(("V4_", "V5_")) else
            "REJECT_DIRECT_HOST_TRANSFER"
        )
        variants.append({
            "gdt750_variant_id": name,
            "known_occurrences": len(rows),
            "predicted_positions": total["positions"],
            "all_predictions_subset_of_true_positions": total["subset_positions"],
            "contradiction_positions": total["contradiction_positions"],
            "true_positive_axis_labels": total["tp"],
            "false_positive_axis_labels": total["fp"],
            "false_negative_axis_labels": total["fn"],
            "axis_precision": f"{precision:.6f}",
            "axis_recall": f"{recall:.6f}",
            "disposition": disposition,
            "literal_identity_credit": 0,
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output, variants


def host_string(hosts: list[dict[str, object]]) -> str:
    return "|".join(
        f"{host['signed_offset']}:{host['host_surface']}:{joined(host['host_axes'])}:d{host['whole_edit_distance']}"
        for host in hosts
    ) or "NONE"


def render_axes(axes: set[str]) -> str:
    exact = {
        frozenset({"HOT", "END_STAGE"}): "heißer Zustand an der End-/Vollstufe",
        frozenset({"MOIST", "END_STAGE"}): "feuchter/eingeweichter Zustand an der End-/Vollstufe",
        frozenset({"DRY", "END_STAGE"}): "trockener Zustand an der End-/Vollstufe",
    }
    if frozenset(axes) in exact:
        return exact[frozenset(axes)]
    labels = {
        "HOT": "heißer Zustand",
        "COLD": "kalter Zustand",
        "DRY": "trockener Zustand",
        "MOIST": "feuchter/eingeweichter Zustand",
        "BEGIN_STAGE": "Anfangsstufe",
        "MIDDLE_STAGE": "Mittelstufe",
        "END_STAGE": "End-/Vollstufe",
    }
    return "; ".join(labels[axis] for axis in QUALITY_STAGE_AXES if axis in axes)


def build_target_dispatch(
    context: Context,
    targets: list[dict[str, object]],
    audit: list[dict[str, object]],
    priors: dict[tuple[str, int], dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    target_map = {str(row["target_surface"]): row for row in targets}
    output: list[dict[str, object]] = []
    active_cards: list[dict[str, object]] = []
    contacts: list[dict[str, object]] = []
    for row in audit:
        surface = str(row["target_surface"])
        predictions: dict[str, dict[str, object]] = {}
        if int(row["reader_exact"]):
            for variant in VARIANTS[2:]:
                predictions[variant[0]] = predict(
                    context, surface, str(row["locus"]), int(row["token_ordinal"]),
                    variant, priors,
                )
        active = predictions.get(ACTIVE_VARIANT, {
            "emitted_axes": set(), "selected_ring": None,
            "contributing_hosts": [], "conflicts": [],
        })
        radius_two = predictions.get(VARIANTS[3][0], {
            "emitted_axes": set(), "selected_ring": None, "contributing_hosts": [],
        })
        distance_two = predictions.get(VARIANTS[4][0], {
            "emitted_axes": set(), "selected_ring": None, "contributing_hosts": [],
        })
        active_axes = set(active["emitted_axes"])
        active_outside = int(
            int(row["outside_discovery_primary"]) and bool(active_axes)
        )
        output_row = {
            "gdt750_dispatch_id": f"G750-D{len(output) + 1:04d}",
            "gdt749_occurrence_id": row["gdt749_occurrence_id"],
            "target_surface": surface,
            "page": row["page"],
            "physical_folio": row["physical_folio"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "reader_exact": row["reader_exact"],
            "gdt748_discovery_position": row["gdt748_discovery_position"],
            "outside_discovery_primary": row["outside_discovery_primary"],
            "gdt749_prior_axes": target_map[surface]["prior_role_axes"],
            "distance1_multi_reference_prior_axes": joined(priors[(surface, 1)]["prior_axes"]),
            "active_selected_ring": active["selected_ring"] or "NONE",
            "active_contributing_hosts": host_string(active["contributing_hosts"]),
            "active_emitted_axes": joined(active_axes),
            "active_conflicts": "|".join(active["conflicts"]) or "NONE",
            "active_outside_card": active_outside,
            "radius2_discovery_selected_ring": radius_two["selected_ring"] or "NONE",
            "radius2_discovery_axes": joined(radius_two["emitted_axes"]),
            "radius2_discovery_hosts": host_string(radius_two["contributing_hosts"]),
            "distance2_sensitivity_axes": joined(distance_two["emitted_axes"]),
            "distance2_sensitivity_hosts": host_string(distance_two["contributing_hosts"]),
            "written_line_eva": row["written_line_eva"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        }
        output.append(output_row)
        if not active_outside:
            continue
        card_id = f"G750-A{len(active_cards) + 1:03d}"
        active_cards.append({
            "gdt750_active_card_id": card_id,
            "target_surface": surface,
            "page": row["page"],
            "physical_folio": row["physical_folio"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "emitted_axes": joined(active_axes),
            "working_render_de": render_axes(active_axes),
            "contributing_hosts": host_string(active["contributing_hosts"]),
            "distance1_form_prior_axes": joined(priors[(surface, 1)]["prior_axes"]),
            "gdt749_prior_axes": target_map[surface]["prior_role_axes"],
            "relation_to_gdt749_prior": (
                "AGREES_OR_NARROWS" if active_axes <= set(split_axes(target_map[surface]["prior_role_axes"]))
                else "ADDS_OR_RIVALS_PRIOR"
            ),
            "written_line_eva": row["written_line_eva"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
        for host in active["contributing_hosts"]:
            supported_axes = set(host["host_axes"]) & active_axes
            contacts.append({
                "gdt750_contact_id": f"G750-H{len(contacts) + 1:03d}",
                "gdt750_active_card_id": card_id,
                "target_surface": surface,
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "target_locus": row["locus"],
                "target_ordinal": row["token_ordinal"],
                "host_surface": host["host_surface"],
                "host_locus": row["locus"],
                "host_ordinal": host["host_ordinal"],
                "signed_offset": host["signed_offset"],
                "whole_edit_distance": host["whole_edit_distance"],
                "host_axes": joined(host["host_axes"]),
                "supported_emitted_axes": joined(supported_axes),
                "host_close_excluded": 0,
                "relation_scope": "COMPLETE_WHOLE_DIRECT_HOST_AXIS_ONLY",
                "literal_identity_credit": 0,
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
    return output, active_cards, contacts


def build_profiles(
    targets: list[dict[str, object]],
    priors_deck: list[dict[str, object]],
    dispatch: list[dict[str, object]],
    active: list[dict[str, object]],
) -> list[dict[str, object]]:
    active_map: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    dispatch_map: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in active:
        active_map[str(row["target_surface"])].append(row)
    for row in dispatch:
        dispatch_map[str(row["target_surface"])].append(row)
    prior_map = {str(row["target_surface"]): row for row in priors_deck}
    output: list[dict[str, object]] = []
    for target in targets:
        surface = str(target["target_surface"])
        cards = active_map[surface]
        all_rows = dispatch_map[surface]
        axis_counts = Counter(
            axis for row in cards for axis in split_axes(row["emitted_axes"])
        )
        radius2_only = sum(
            row["active_emitted_axes"] == "NONE"
            and row["radius2_discovery_axes"] != "NONE"
            and row["outside_discovery_primary"] == "1"
            for row in all_rows
        )
        d2_only = sum(
            row["active_emitted_axes"] == "NONE"
            and row["distance2_sensitivity_axes"] != "NONE"
            and row["outside_discovery_primary"] == "1"
            for row in all_rows
        )
        status = (
            "A3_ACTIVE_CROSS_PAGE_FORM_GATED_HOST"
            if len({row["page"] for row in cards}) >= 2 else
            "A1_ACTIVE_SINGLE_OCCURRENCE_FORM_GATED_HOST"
            if cards else
            "A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST"
        )
        if surface == "okeey":
            decision = (
                "At active positions render a hot end-state when both axes occur; "
                "retain HOT/END as a complete-form role, not a lexeme."
            )
        elif surface == "cheky" and cards:
            decision = (
                "One active DRY occurrence rivals the former MIDDLE_STAGE default; "
                "global stage remains open."
            )
        elif cards:
            decision = (
                "Speak only the listed occurrence axes; do not globalize them beyond "
                "the form-gated direct-host positions."
            )
        elif surface in {"qochey", "okechy"}:
            decision = (
                "No active direct host; retain GDT749's rivalized global working card "
                "without an occurrence renderer."
            )
        else:
            decision = "No active direct host; retain the prior only as a silent hypothesis."
        output.append({
            "gdt750_profile_id": f"G750-P{len(output) + 1:02d}",
            "target_surface": surface,
            "gdt749_prior_axes": target["prior_role_axes"],
            "distance1_form_prior_axes": prior_map[surface]["distance1_multi_reference_prior_axes"],
            "active_outside_positions": len(cards),
            "active_outside_pages": len({row["page"] for row in cards}),
            "active_axis_counts": axis_count_string(
                axis for axis, count in axis_counts.items() for _ in range(count)
            ),
            "active_render_counts": count_string(row["working_render_de"] for row in cards),
            "radius2_additional_discovery_positions": radius2_only,
            "distance2_additional_sensitivity_positions": d2_only,
            "dispatch_status": status,
            "working_decision": decision,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
            "unseen_form_export": 0,
        })
    return output


def write_reader(
    path: Path,
    variants: list[dict[str, object]],
    profiles: list[dict[str, object]],
    active: list[dict[str, object]],
) -> None:
    active_map: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in active:
        active_map[str(row["target_surface"])].append(row)
    lines = [
        "# GDT750 form-gated direct-host reader", "",
        "The direct-host rule alone fails. The active rule requires a complete-form",
        "distance-one host, a distance-one form prior supported by at least two",
        "reference wholes, an immediate non-CLOSE contact, and no axis conflict.", "",
        "## Calibration", "",
        "| variant | positions | TP | FP | precision | recall | disposition |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in variants:
        lines.append(
            f"| {row['gdt750_variant_id']} | {row['predicted_positions']} | "
            f"{row['true_positive_axis_labels']} | {row['false_positive_axis_labels']} | "
            f"{float(row['axis_precision']):.3f} | {float(row['axis_recall']):.3f} | "
            f"{row['disposition']} |"
        )
    lines.extend(["", "## Seventeen complete forms", ""])
    for profile in profiles:
        surface = str(profile["target_surface"])
        lines.extend([
            f"### `{surface}` — {profile['dispatch_status']}", "",
            f"- GDT749 prior: `{profile['gdt749_prior_axes']}`; distance-one form prior: "
            f"`{profile['distance1_form_prior_axes']}`",
            f"- Active positions/pages: {profile['active_outside_positions']}/"
            f"{profile['active_outside_pages']}; axes: `{profile['active_axis_counts']}`",
            f"- Decision: {profile['working_decision']}",
        ])
        for card in active_map[surface]:
            lines.append(
                f"  - `{card['locus']}`: **{card['working_render_de']}**; "
                f"host `{card['contributing_hosts']}`; `{card['written_line_eva']}`"
            )
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def edge_packet(
    output_dir: Path, contacts: list[dict[str, object]]
) -> dict[str, object]:
    packet: list[dict[str, object]] = []
    for number, contact in enumerate(contacts, start=1):
        packet.append({
            "edge_id": f"G750E{number:03d}",
            "batch_id": "GDT750_FORM_GATED_DIRECT_HOST",
            "page": contact["page"],
            "physical_folio": contact["physical_folio"],
            "diagram_unit_id": "CACHED_TEXT_COMPLETE_WHOLE_DIRECT_HOST",
            "pivot_visual_id": f"TARGET_WHOLE_{contact['target_surface']}",
            "pivot_locus": f"{contact['target_locus']}@{contact['target_ordinal']}",
            "target_visual_id": f"HOST_WHOLE_{contact['host_surface']}",
            "target_locus": f"{contact['host_locus']}@{contact['host_ordinal']}",
            "relation_type": "FORM_GATED_DIRECT_COMPLETE_WHOLE_HOST",
            "direction_basis": "FORMAL_PAIR_RECURRENCE_AND_RENDERER_ROLE",
            "ownership_basis": "ONE_HOST_ONE_AXIS_CARD_NO_FLANK_FUSION",
            "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT750",
            "page_crop_sha256": "NONE",
            "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT750_BUILDER",
            "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "CALIBRATED_D1_MULTI_REFERENCE_DIRECT_HOST",
            "ambiguity_state": "OCCURRENCE_AXIS_ONLY_LITERAL_IDENTITY_OPEN",
            "formal_access_state": "FORMAL_ACCESSED",
            "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_FORMAL_CONTEXT_RELATION",
        })
    path = output_dir / "GDT750_GDT388_HOST_EDGE_PACKET.tsv"
    write_tsv(path, packet, list(packet[0]))
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(path)],
        cwd=ROOT, check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode not in {0, 1} or not completed.stdout:
        raise AssertionError(f"edge intake failed: {completed.stderr}")
    intake = json.loads(completed.stdout)
    if intake["status"] != "INVALID_PACKET" or intake["score_ready"]:
        raise AssertionError("GDT750 packet unexpectedly score-ready")
    (output_dir / "GDT750_GDT388_EDGE_INTAKE.json").write_text(
        json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return intake


def build(output_dir: Path) -> dict[str, object]:
    targets = g749.build_targets()
    references = g749.reference_specs()
    g749_audit, feature_rows, inherited_guard = g749.build_occurrence_audit(
        targets, references
    )
    prior_deck, priors, reference_axes = build_prior_decks(targets, references)
    context = Context()
    calibration, variants = build_calibration(
        context, references, feature_rows, priors, reference_axes
    )
    dispatch, active, contacts = build_target_dispatch(
        context, targets, g749_audit, priors
    )
    profiles = build_profiles(targets, prior_deck, dispatch, active)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(output_dir / "RULE_VARIANT_CALIBRATION.tsv", variants, list(variants[0]))
    write_tsv(output_dir / "KNOWN_1134_OCCURRENCE_CALIBRATION.tsv", calibration, list(calibration[0]))
    write_tsv(output_dir / "FORM_17_PRIOR_DECK.tsv", prior_deck, list(prior_deck[0]))
    write_tsv(output_dir / "TARGET_1684_HOST_DISPATCH_AUDIT.tsv", dispatch, list(dispatch[0]))
    write_tsv(output_dir / "ACTIVE_OCCURRENCE_CARDS.tsv", active, list(active[0]))
    write_tsv(output_dir / "ACTIVE_HOST_CONTACTS.tsv", contacts, list(contacts[0]))
    write_tsv(output_dir / "FORM_17_DISPATCH_PROFILE.tsv", profiles, list(profiles[0]))
    write_reader(
        output_dir / "GDT750_FORM_GATED_HOST_READER.md", variants, profiles, active
    )
    intake = edge_packet(output_dir, contacts)

    active_variant = next(row for row in variants if row["gdt750_variant_id"] == ACTIVE_VARIANT)
    active_forms = [row for row in profiles if int(row["active_outside_positions"])]
    axis_cards = sum(len(split_axes(row["emitted_axes"])) for row in active)
    status = (
        f"PARTIAL__1134_KNOWN_OCCURRENCE_CALIBRATION__D1_R1_"
        f"{active_variant['true_positive_axis_labels']}_TP_"
        f"{active_variant['false_positive_axis_labels']}_FP_"
        f"{active_variant['predicted_positions']}_POSITIONS__"
        f"{len(active)}_ACTIVE_OUTSIDE_POSITIONS__{len(active_forms)}_FORMS__"
        f"{axis_cards}_AXIS_CARDS__RADIUS2_DISCOVERY_ONLY__"
        "DISTANCE2_SENSITIVITY_ONLY__QOCHEY_OKECHY_NO_ACTIVE_HOST__"
        "ZERO_LITERAL_IDENTITIES__ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
    )
    result = {
        "schema": "GDT750_RESULT_V1",
        "status": status,
        "question": (
            "Can a complete-form distance-one prior supported by multiple known "
            "wholes safely gate immediate complete-whole host axes at GDT749's "
            "seventeen target forms?"
        ),
        "scope": {
            "known_calibration_occurrences": len(calibration),
            "target_occurrences": len(dispatch),
            "outside_reader_exact_occurrences": sum(int(row["outside_discovery_primary"]) for row in dispatch),
            "active_outside_positions": len(active),
            "active_forms": len(active_forms),
            "active_axis_cards": axis_cards,
            "active_host_contacts": len(contacts),
            "allowed_pages": context.guard["allowed_pages"],
        },
        "variant_calibration": {
            str(row["gdt750_variant_id"]): {
                "positions": int(row["predicted_positions"]),
                "tp": int(row["true_positive_axis_labels"]),
                "fp": int(row["false_positive_axis_labels"]),
                "fn": int(row["false_negative_axis_labels"]),
                "precision": float(row["axis_precision"]),
                "recall": float(row["axis_recall"]),
                "disposition": row["disposition"],
            }
            for row in variants
        },
        "form_profiles": {
            str(row["target_surface"]): {
                "active_positions": int(row["active_outside_positions"]),
                "axes": row["active_axis_counts"],
                "status": row["dispatch_status"],
            }
            for row in profiles
        },
        "inherited_guard": inherited_guard,
        "edge_intake": {
            "status": intake["status"],
            "score_ready": intake["score_ready"],
            "errors": intake["errors"],
        },
        "claim_ceiling": (
            "Occurrence-specific complete-whole quality/stage cards only. No "
            "language, sound, abbreviation, EVA component, substring, lexeme, "
            "literal ingredient, plant, disease, cure, person, vessel, unit, "
            "plaintext, unseen form, image, transcription, new page, f84 or f84r."
        ),
        "inputs": {
            str(G749_RUN_REL): sha256(ROOT / G749_RUN_REL),
            str(G740_REPORT_REL): sha256(ROOT / G740_REPORT_REL),
        },
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir.resolve()), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
