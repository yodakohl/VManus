#!/usr/bin/env python3
"""Build GDT740's local-host attachment adjudication.

GDT739 selected semantic hosts by proximity. GDT740 asks whether each selected
host is directly attached to the complete target whole or merely nearby.
Immediate contacts remain occurrence-scoped working binders; radius-two
contacts with an independently emitted intervening cell become discovery-only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
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
BASE_REL = Path("experiments/yolo/gdt740_local_host_attachment_adjudication")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G739_REL = Path("experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch")
G739_RUN_REL = G739_REL / "src/run.py"
G739_ART_REL = G739_REL / "artifacts"
G738_REL = Path("experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication")
PATCH_REL = G738_REL / "artifacts/OCCURRENCE_RENDERER_PATCH.tsv"

module_spec = importlib.util.spec_from_file_location("gdt739_builder", ROOT / G739_RUN_REL)
if module_spec is None or module_spec.loader is None:
    raise RuntimeError("cannot load GDT739 guarded cache and renderer helpers")
g739 = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(g739)

SCALAR_FORMS = set(g739.SCALAR_FORMS)
STATE_FORMS = set(g739.STATE_FORMS)
SCALAR_CLASSES = set(g739.SCALAR_CLASSES)
CARRIER_AXES = tuple(g739.CARRIER_AXES)
EXPECTED_HOST_SIDE = {"H1": "R", "H2": "R", "H3": "L", "H4": "L"}
OUTPUT_NAMES = (
    "TYPED_104_RING_EVIDENCE.tsv",
    "SELECTED_103_CONTACT_ATTACHMENT.tsv",
    "ORDERED_PAIR_100_RECURRENCE.tsv",
    "TARGET_95_ATTACHMENT_ADJUDICATION.tsv",
    "TARGET_202_RENDERER_PATCH_V2.tsv",
    "FORM_12_ATTACHMENT_PROFILE.tsv",
    "PASSAGE_20_ATTACHMENT_REVIEW.tsv",
    "GDT740_ATTACHMENT_READER.md",
    "GDT740_GDT388_EDGE_PACKET.tsv",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="ignore",
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


def integer_or_none(value: str) -> int | None:
    return None if value == "NA" else int(value)


def selected_roles(dispatch: dict[str, str], window: dict[str, str]) -> set[str]:
    """Reconstruct exactly the GDT739 selecting semantic roles."""
    if window["eligible_local_anchor"] != "1":
        return set()
    roles: set[str] = set()
    selecting_distance = integer_or_none(dispatch["selecting_anchor_distance"])
    if selecting_distance == int(window["distance"]):
        if dispatch["family"] == "SCALAR":
            # A conflicted scalar ring remains open and selects no axis class.
            if dispatch["dimension_dispatch"] in window["scalar_host_types"].split("|"):
                roles.add("AXIS")
        elif dispatch["favored_axis_not_automatic"] in window["axis_tags"].split("|"):
            roles.add("AXIS")
    carrier_distance = integer_or_none(dispatch["carrier_anchor_distance"])
    if carrier_distance == int(window["distance"]):
        carrier_axes = set(dispatch["carrier_dispatch"].split("_"))
        if carrier_axes.intersection(window["axis_tags"].split("|")):
            roles.add("CARRIER")
    return roles


def exact_pair_census() -> tuple[
    Counter[tuple[str, int, str]],
    Counter[tuple[str, int, str]],
    Counter[tuple[str, int, str, str]],
    dict[tuple[str, int, str], list[str]],
    dict[tuple[str, int], dict[str, str]],
    dict[str, int],
]:
    """Count ordered pairs only after the inherited guarded projection."""
    by_line, exact, guards = g739.g738.token_context()
    counts: Counter[tuple[str, int, str]] = Counter()
    raw_counts: Counter[tuple[str, int, str]] = Counter()
    triple_counts: Counter[tuple[str, int, str, str]] = Counter()
    loci: dict[tuple[str, int, str], list[str]] = defaultdict(list)
    for locus, line in by_line.items():
        for index, token in enumerate(line):
            for offset in (-2, -1, 1, 2):
                neighbor_index = index + offset
                if not 0 <= neighbor_index < len(line):
                    continue
                neighbor = line[neighbor_index]
                key = (token["eva"], offset, neighbor["eva"])
                raw_counts[key] += 1
                if not exact[(locus, int(token["token_index"]))]:
                    continue
                if not exact[(locus, int(neighbor["token_index"]))]:
                    continue
                counts[key] += 1
                loci[key].append(
                    f"{locus}@{int(token['token_index'])}>{int(neighbor['token_index'])}"
                )
                if abs(offset) == 2:
                    middle = line[index + (1 if offset > 0 else -1)]
                    if exact[(locus, int(middle["token_index"]))]:
                        triple_counts[(token["eva"], offset, middle["eva"], neighbor["eva"])] += 1
    return counts, raw_counts, triple_counts, loci, g739.g738.compact_cells(), guards


def build_contacts(
    dispatches: list[dict[str, str]], windows: list[dict[str, str]],
    cells: dict[tuple[str, int], dict[str, str]],
    pair_counts: Counter[tuple[str, int, str]],
    raw_pair_counts: Counter[tuple[str, int, str]],
    triple_counts: Counter[tuple[str, int, str, str]],
    pair_loci: dict[tuple[str, int, str], list[str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    windows_by_patch: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in windows:
        windows_by_patch[row["patch_id"]].append(row)

    contacts: list[dict[str, object]] = []
    target_positions = {
        (row["locus"], int(row["token_ordinal"])) for row in dispatches
    }
    for dispatch in dispatches:
        for window in windows_by_patch[dispatch["patch_id"]]:
            roles = selected_roles(dispatch, window)
            if not roles:
                continue
            offset = int(window["signed_offset"])
            key = (dispatch["surface"], offset, window["neighbor_surface"])
            recurrence = pair_counts[key]
            expected_side = EXPECTED_HOST_SIDE[dispatch["opaque_head_id"]]
            direction_match = int(window["side"] == expected_side)
            distance = int(window["distance"])
            if distance == 1 and recurrence >= 2:
                decision = "STRONG_REPEAT_EXPECTED" if direction_match else "STRONG_REPEAT_REVERSE"
            elif distance == 1 and direction_match:
                decision = "SUPPORTED_DIRECTION_DIRECT"
            elif distance == 1:
                decision = "PROVISIONAL_REVERSE_DIRECT"
            else:
                decision = "NEAR_ONLY_HOLD"

            middle_surface = "NONE"
            middle_role = "NOT_APPLICABLE"
            middle_unknown = "NA"
            middle_emits = 0
            middle_head = 0
            middle_target = 0
            exact_full_frame = recurrence
            target_cell = cells[(window["locus"], int(window["target_ordinal"]))]
            neighbor_cell = cells[(window["locus"], int(window["neighbor_ordinal"]))]
            if offset < 0:
                manuscript_frame = f"{window['neighbor_surface']} {dispatch['surface']}"
            else:
                manuscript_frame = f"{dispatch['surface']} {window['neighbor_surface']}"
            if distance == 2:
                middle_ordinal = int(window["target_ordinal"]) + (1 if offset > 0 else -1)
                middle = cells[(window["locus"], middle_ordinal)]
                middle_surface = middle["surface"]
                middle_role = middle["practical_unit_role"]
                middle_unknown = middle["unknown_v99r7"]
                middle_emits = int(middle_role == "EMIT_CELL_ONCE")
                middle_head = int(g739.strict_initial_head(middle_surface))
                middle_target = int((window["locus"], middle_ordinal) in target_positions)
                exact_full_frame = triple_counts[
                    (dispatch["surface"], offset, middle_surface, window["neighbor_surface"])
                ]
                manuscript_frame = (
                    f"{window['neighbor_surface']} {middle_surface} {dispatch['surface']}"
                    if offset < 0 else
                    f"{dispatch['surface']} {middle_surface} {window['neighbor_surface']}"
                )

            contacts.append({
                "attachment_contact_id": "", "window_id": window["window_id"],
                "dispatch_id": dispatch["dispatch_id"], "patch_id": dispatch["patch_id"],
                "occurrence_id": dispatch["occurrence_id"], "page": dispatch["page"],
                "locus": dispatch["locus"], "target_ordinal": dispatch["token_ordinal"],
                "target_surface": dispatch["surface"], "opaque_head_id": dispatch["opaque_head_id"],
                "line_position": dispatch["line_position"], "selected_roles": "+".join(sorted(roles)),
                "side": window["side"], "signed_offset": offset, "distance": distance,
                "neighbor_ordinal": window["neighbor_ordinal"],
                "neighbor_surface": window["neighbor_surface"],
                "neighbor_semantic_value_de": window["neighbor_semantic_value_de"],
                "neighbor_axis_tags": window["axis_tags"],
                "neighbor_scalar_host_types": window["scalar_host_types"],
                "ordered_pair_key": f"{dispatch['surface']}@{offset:+d}@{window['neighbor_surface']}",
                "manuscript_order_full_frame": manuscript_frame,
                "guarded_reader_exact_pair_occurrences": recurrence,
                "guarded_reader_exact_full_frame_occurrences": exact_full_frame,
                "guarded_zl3b_pair_occurrences": raw_pair_counts[key],
                "raw_only_repeat_control": int(raw_pair_counts[key] >= 2 and recurrence < 2),
                "guarded_reader_exact_pair_loci": "|".join(sorted(pair_loci[key])),
                "expected_host_side_from_formal_role": expected_side,
                "formal_role_direction_match": direction_match,
                "historical_order_prior": (
                    "LEFT_HOST_PRIMARY_MICROENTRY" if window["side"] == "L"
                    else "RIGHT_SCOPE_OR_INVERSION_POSSIBLE"
                ),
                "intervening_surface": middle_surface,
                "intervening_practical_unit_role": middle_role,
                "intervening_unknown_v99r7": middle_unknown,
                "intervening_emits_own_unit": middle_emits,
                "intervening_strict_initial_head": middle_head,
                "intervening_another_gdt738_target": middle_target,
                "target_practical_unit_layer": target_cell["practical_unit_layer"],
                "target_practical_unit_id": target_cell["practical_unit_id"],
                "target_practical_unit_role": target_cell["practical_unit_role"],
                "neighbor_practical_unit_layer": neighbor_cell["practical_unit_layer"],
                "neighbor_practical_unit_id": neighbor_cell["practical_unit_id"],
                "neighbor_practical_unit_role": neighbor_cell["practical_unit_role"],
                "shared_bound_practical_span": int(
                    target_cell["practical_unit_layer"] != "SINGLE_CELL_UNIT"
                    and neighbor_cell["practical_unit_layer"] != "SINGLE_CELL_UNIT"
                    and target_cell["practical_unit_id"] == neighbor_cell["practical_unit_id"]
                ),
                "attachment_decision": decision,
                "axis_role_retained": 0, "carrier_role_retained": 0,
                "renderer_role_retained": 0,
                "scope": "THIS_COMPLETE_WHOLE_AT_THIS_ENUMERATED_OCCURRENCE_ONLY",
                "literal_plaintext_claimed": 0, "component_export_credit": 0,
                "_window": window,
            })

    contacts.sort(key=lambda row: (int(str(row["dispatch_id"])[6:]), int(row["signed_offset"])))
    for index, row in enumerate(contacts, start=1):
        row["attachment_contact_id"] = f"G740-C{index:04d}"

    keys = sorted({
        (str(row["target_surface"]), int(row["signed_offset"]), str(row["neighbor_surface"]))
        for row in contacts
    })
    pair_id = {key: f"G740-P{index:03d}" for index, key in enumerate(keys, start=1)}
    for row in contacts:
        key = (str(row["target_surface"]), int(row["signed_offset"]), str(row["neighbor_surface"]))
        row["pair_id"] = pair_id[key]

    pair_rows: list[dict[str, object]] = []
    for key in keys:
        members = [row for row in contacts if (
            row["target_surface"], row["signed_offset"], row["neighbor_surface"]
        ) == key]
        exact_loci = sorted(pair_loci[key])
        pair_rows.append({
            "pair_id": pair_id[key], "target_surface": key[0], "signed_offset": key[1],
            "side": "L" if key[1] < 0 else "R", "distance": abs(key[1]),
            "neighbor_surface": key[2], "selected_contact_occurrences": len(members),
            "guarded_reader_exact_pair_occurrences": pair_counts[key],
            "guarded_zl3b_pair_occurrences": raw_pair_counts[key],
            "raw_only_repeat_control": int(raw_pair_counts[key] >= 2 and pair_counts[key] < 2),
            "guarded_reader_exact_pair_loci": "|".join(exact_loci),
            "guarded_pages": len({value.split(".")[0] for value in exact_loci}),
            "selected_roles": "|".join(sorted({str(row["selected_roles"]) for row in members})),
            "pair_recurrence_decision": (
                "REPEATED_DIRECT_PAIR" if abs(key[1]) == 1 and pair_counts[key] >= 2
                else "RAW_REPEAT_READER_VARIANT_CONTROL" if abs(key[1]) == 1 and raw_pair_counts[key] >= 2
                else "UNIQUE_DIRECT_PAIR" if abs(key[1]) == 1
                else "UNIQUE_RADIUS_TWO_PAIR"
            ),
            "lexeme_or_component_export": 0,
        })
    return contacts, pair_rows


def typed_ring_evidence(
    dispatches: list[dict[str, str]], windows: list[dict[str, str]],
    contacts: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Preserve the complete 104-row ring evidence, including open conflicts."""
    by_window = {str(row["window_id"]): row for row in contacts}
    dispatch_map = {row["dispatch_id"]: row for row in dispatches}
    evidence_windows = set(by_window)
    for dispatch in dispatches:
        if dispatch["dimension_dispatch"] != "OPEN_SCALAR_CONFLICT":
            continue
        for window in windows:
            if window["patch_id"] != dispatch["patch_id"]:
                continue
            if (
                window["eligible_local_anchor"] == "1"
                and window["distance"] == dispatch["selecting_anchor_distance"]
                and window["scalar_host_types"] != "NONE"
            ):
                evidence_windows.add(window["window_id"])
    window_map = {row["window_id"]: row for row in windows}
    output: list[dict[str, object]] = []
    for window_id in sorted(
        evidence_windows,
        key=lambda value: (
            int(window_map[value]["patch_id"].split("P")[1]),
            int(window_map[value]["signed_offset"]),
        ),
    ):
        window = window_map[window_id]
        dispatch = dispatch_map[next(
            row["dispatch_id"] for row in dispatches if row["patch_id"] == window["patch_id"]
        )]
        binding = by_window.get(window_id)
        conflict = (
            dispatch["dimension_dispatch"] == "OPEN_SCALAR_CONFLICT"
            and window["distance"] == dispatch["selecting_anchor_distance"]
            and window["scalar_host_types"] != "NONE"
        )
        evidence_roles: list[str] = []
        if binding:
            evidence_roles.extend(str(binding["selected_roles"]).split("+"))
        if conflict:
            evidence_roles.append("NONBINDING_AXIS_CONFLICT_EVIDENCE")
        output.append({
            "ring_evidence_id": f"G740-E{len(output) + 1:04d}",
            "window_id": window_id, "dispatch_id": dispatch["dispatch_id"],
            "patch_id": dispatch["patch_id"], "page": dispatch["page"],
            "locus": dispatch["locus"], "target_surface": dispatch["surface"],
            "side": window["side"], "signed_offset": window["signed_offset"],
            "distance": window["distance"], "neighbor_surface": window["neighbor_surface"],
            "neighbor_axis_tags": window["axis_tags"],
            "neighbor_scalar_host_types": window["scalar_host_types"],
            "evidence_roles": "+".join(dict.fromkeys(evidence_roles)),
            "binding_contact_id": binding["attachment_contact_id"] if binding else "NONE",
            "binding_roles": binding["selected_roles"] if binding else "NONE",
            "role_bearing_binding_contact": int(binding is not None),
            "conflict_only_nonbinding_contact": int(binding is None and conflict),
            "plaintext_or_component_export": 0,
        })
    return output


def target_tier(rows: list[dict[str, object]]) -> str:
    decisions = {str(row["attachment_decision"]) for row in rows}
    if decisions.intersection({"STRONG_REPEAT_EXPECTED", "STRONG_REPEAT_REVERSE"}):
        return "ATTACHED_STRONG"
    if "SUPPORTED_DIRECTION_DIRECT" in decisions:
        return "ATTACHED_SUPPORTED"
    if "PROVISIONAL_REVERSE_DIRECT" in decisions:
        return "ATTACHED_PROVISIONAL_REVERSE"
    if "NEAR_ONLY_HOLD" in decisions:
        return "NEAR_ONLY_HOLD"
    return "MODE_ONLY_NO_HOST"


def retained_role_rows(rows: list[dict[str, object]], role: str) -> list[dict[str, object]]:
    return [row for row in rows if int(row["distance"]) == 1 and role in str(row["selected_roles"]).split("+")]


def direct_carrier_choice(
    dispatch: dict[str, str], direct_rows: list[dict[str, object]],
) -> tuple[str, list[dict[str, object]]]:
    """Retain a composite carrier only when one host itself carries it.

    GDT739 could union carrier components supplied by distinct flanking hosts.
    That is proximity fusion rather than evidence that one microentry has a
    composite carrier, so GDT740 opens the slot in those cases.
    """
    if not direct_rows:
        return "OPEN", []
    wanted = tuple(axis for axis in CARRIER_AXES if axis in dispatch["carrier_dispatch"].split("_"))
    if not wanted:
        return "OPEN", []
    winners = [
        row for row in direct_rows
        if set(wanted) <= {
            axis for axis in CARRIER_AXES
            if axis in str(row["neighbor_axis_tags"]).split("|")
        }
    ]
    if winners:
        return "_".join(wanted), winners
    return "OPEN", []


def rerender(
    dispatch: dict[str, str], contact_rows: list[dict[str, object]], override: dict[str, str],
) -> tuple[str, str, str, str, int, int]:
    for row in contact_rows:
        row["axis_role_retained"] = row["carrier_role_retained"] = row["renderer_role_retained"] = 0
    axis_rows = retained_role_rows(contact_rows, "AXIS")
    carrier_rows = retained_role_rows(contact_rows, "CARRIER")
    effect = override.get("role_effect", "KEEP")
    if effect == "RETAIN_R2_AXIS":
        axis_rows = [
            row for row in contact_rows if "AXIS" in str(row["selected_roles"]).split("+")
        ]
    elif effect == "RETAIN_R2_CARRIER":
        carrier_rows = [
            row for row in contact_rows if "CARRIER" in str(row["selected_roles"]).split("+")
        ]
    elif effect == "DROP_AXIS":
        axis_rows = []
    elif effect == "DROP_CARRIER":
        carrier_rows = []
    elif effect == "DROP_BOTH":
        axis_rows = []
        carrier_rows = []
    carrier, carrier_winners = direct_carrier_choice(dispatch, carrier_rows)
    new_mode = (
        override["mode_effect"]
        if override.get("mode_effect") in {"QUALITY_STATE", "PROCESS_RESULT"}
        else dispatch["state_mode"]
    )
    surface = dispatch["surface"]
    if surface in SCALAR_FORMS:
        original = dispatch["dimension_dispatch"]
        if original in SCALAR_CLASSES and axis_rows:
            dimension = original
            selecting_windows = [row["_window"] for row in axis_rows]
            axis_specific = 1
        elif original == "OPEN_SCALAR_CONFLICT" and dispatch["selecting_anchor_distance"] == "1":
            dimension = "OPEN_SCALAR_CONFLICT"
            selecting_windows = []
            axis_specific = 0
        else:
            dimension = "OPEN_SCALAR"
            selecting_windows = []
            axis_specific = 0
        render = g739.render_scalar(
            surface, dispatch["line_position"], dispatch["level"], dimension,
            selecting_windows, carrier,
        )
    else:
        axis_specific = int(bool(axis_rows))
        dimension = (
            f"{new_mode}_{dispatch['favored_axis_not_automatic']}_LOCAL"
            if axis_specific else f"{new_mode}_AXIS_OPEN"
        )
        render = g739.render_state(
            surface, dispatch["line_position"], new_mode,
            dispatch["favored_axis_not_automatic"], bool(axis_specific), carrier,
        )
    if axis_specific:
        for row in axis_rows:
            row["axis_role_retained"] = 1
    for row in carrier_winners:
        row["carrier_role_retained"] = 1
    for row in contact_rows:
        row["renderer_role_retained"] = int(
            int(row["axis_role_retained"]) or int(row["carrier_role_retained"])
        )
    carrier_bound = int(carrier != "OPEN")
    specific = int(axis_specific or carrier_bound or new_mode == "PROCESS_RESULT")
    return dimension, carrier, render, new_mode, axis_specific, specific


def make_patch_and_targets(
    dispatches: list[dict[str, str]], contacts: list[dict[str, object]],
    overrides: dict[str, dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_patch: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in contacts:
        by_patch[str(row["patch_id"])].append(row)

    patches: list[dict[str, object]] = []
    targets: list[dict[str, object]] = []
    for dispatch in dispatches:
        rows = by_patch[dispatch["patch_id"]]
        override = overrides.get(dispatch["dispatch_id"], {})
        dimension, carrier, render, new_mode, axis_specific, specific = rerender(
            dispatch, rows, override
        )
        direct = [row for row in rows if int(row["distance"]) == 1]
        radius_two = [row for row in rows if int(row["distance"]) == 2]
        held = [row for row in radius_two if not int(row["renderer_role_retained"])]
        relays = [row for row in radius_two if int(row["renderer_role_retained"])]
        active = [row for row in rows if int(row["renderer_role_retained"])]
        if override.get("tier_override"):
            tier = override["tier_override"]
        elif active:
            tier = target_tier(active)
        elif direct and dispatch["carrier_dispatch"] != "OPEN":
            tier = "DIRECT_COMPONENT_CONFLICT_OPEN"
        elif radius_two:
            tier = "NEAR_ONLY_HOLD"
        elif dispatch["specific_local_dispatch"] == "1" and new_mode != dispatch["state_mode"]:
            tier = "MODE_DOWNGRADED_OPEN"
        else:
            tier = "NO_SELECTED_HOST"
        changed = int(
            dimension != dispatch["dimension_dispatch"]
            or carrier != dispatch["carrier_dispatch"]
            or render != dispatch["gdt739_working_render_de"]
        )
        patch = {
            "gdt740_patch_id": f"G740-R{len(patches) + 1:04d}",
            "gdt739_dispatch_id": dispatch["dispatch_id"], "patch_id": dispatch["patch_id"],
            "occurrence_id": dispatch["occurrence_id"], "page": dispatch["page"],
            "locus": dispatch["locus"], "token_index": dispatch["token_index"],
            "token_ordinal": dispatch["token_ordinal"], "surface": dispatch["surface"],
            "body": dispatch["body"], "opaque_head_id": dispatch["opaque_head_id"],
            "line_position": dispatch["line_position"], "family": dispatch["family"],
            "level": dispatch["level"], "gdt739_state_mode": dispatch["state_mode"],
            "gdt740_state_mode": new_mode,
            "attachment_tier": tier,
            "selected_contact_count": len(rows), "direct_contact_count": len(direct),
            "radius_two_contact_count": len(radius_two),
            "radius_two_relay_contact_count": len(relays),
            "radius_two_held_contact_count": len(held),
            "repeated_direct_contact_count": sum(int(row["guarded_reader_exact_pair_occurrences"]) >= 2 for row in direct),
            "gdt739_dimension_dispatch": dispatch["dimension_dispatch"],
            "gdt740_dimension_dispatch": dimension,
            "gdt739_carrier_dispatch": dispatch["carrier_dispatch"],
            "gdt740_carrier_dispatch": carrier,
            "gdt739_working_render_de": dispatch["gdt739_working_render_de"],
            "gdt740_working_render_de": render,
            "axis_specific_dispatch_retained": axis_specific,
            "carrier_locally_bound_retained": int(carrier != "OPEN"),
            "specific_local_dispatch_retained": specific,
            "manual_override_applied": int(bool(override)),
            "manual_override_reason": override.get("manual_reason", "NONE"),
            "renderer_changed_from_gdt739": changed,
            "scope": "EXACT_COMPLETE_SURFACE_AT_THIS_ENUMERATED_OCCURRENCE",
            "literal_patient_or_species_claimed": 0, "literal_plaintext_claimed": 0,
            "unconditional_global_export": 0, "head_or_body_lexeme_credit": 0,
            "component_export_credit": 0, "unseen_form_export": 0,
        }
        patches.append(patch)
        if dispatch["specific_local_dispatch"] == "1":
            targets.append({
                "adjudication_id": f"G740-A{len(targets) + 1:03d}",
                "gdt740_patch_id": patch["gdt740_patch_id"],
                "gdt739_dispatch_id": dispatch["dispatch_id"], "patch_id": dispatch["patch_id"],
                "occurrence_id": dispatch["occurrence_id"], "page": dispatch["page"],
                "locus": dispatch["locus"], "token_ordinal": dispatch["token_ordinal"],
                "surface": dispatch["surface"], "opaque_head_id": dispatch["opaque_head_id"],
                "line_position": dispatch["line_position"], "attachment_tier": tier,
                "selected_contacts": len(rows), "direct_contacts": len(direct),
                "radius_two_contacts": len(radius_two),
                "radius_two_relay_contacts": len(relays),
                "radius_two_held_contacts": len(held),
                "strong_repeated_direct_contacts": sum(str(row["attachment_decision"]).startswith("STRONG_REPEAT") for row in direct),
                "formal_direction_supported_direct_contacts": sum(row["formal_role_direction_match"] == 1 for row in direct),
                "formal_direction_reverse_direct_contacts": sum(row["formal_role_direction_match"] == 0 for row in direct),
                "left_direct_contacts": sum(row["side"] == "L" for row in direct),
                "right_direct_contacts": sum(row["side"] == "R" for row in direct),
                "gdt739_dimension_dispatch": dispatch["dimension_dispatch"],
                "gdt740_dimension_dispatch": dimension,
                "gdt739_carrier_dispatch": dispatch["carrier_dispatch"],
                "gdt740_carrier_dispatch": carrier,
                "gdt739_state_mode": dispatch["state_mode"],
                "gdt740_state_mode": new_mode,
                "axis_attachment_outcome": (
                    "DIRECT_FLANK_CONFLICT_OPEN" if tier == "DIRECT_FLANK_CONFLICT_OPEN"
                    else "RETAIN_RELAY" if relays and any(int(row["axis_role_retained"]) for row in relays)
                    else "RETAIN_DIRECT" if axis_specific
                    else "CONFLICT_DIRECT_REMAINS_OPEN" if dispatch["dimension_dispatch"] == "OPEN_SCALAR_CONFLICT"
                    and dispatch["selecting_anchor_distance"] == "1"
                    else "HOLD_RADIUS_TWO" if any("AXIS" in str(row["selected_roles"]) for row in held)
                    else "OPEN_OR_MODE_ONLY"
                ),
                "carrier_attachment_outcome": (
                    tier if tier in {
                        "DIRECT_COMPONENT_CONFLICT_OPEN", "DIRECT_BOUNDARY_HOLD",
                        "DIRECT_FLANK_CONFLICT_OPEN",
                    }
                    else "RETAIN_RELAY" if relays and any(int(row["carrier_role_retained"]) for row in relays)
                    else "RETAIN_DIRECT" if carrier != "OPEN"
                    else "DIRECT_COMPONENT_CONFLICT_OPEN" if direct
                    and dispatch["carrier_dispatch"] != "OPEN"
                    and any("CARRIER" in str(row["selected_roles"]) for row in direct)
                    else "HOLD_RADIUS_TWO" if any("CARRIER" in str(row["selected_roles"]) for row in held)
                    else "OPEN"
                ),
                "gdt739_working_render_de": dispatch["gdt739_working_render_de"],
                "gdt740_working_render_de": render,
                "attachment_evidence": " || ".join(
                    f"{row['side']}{row['distance']} {row['neighbor_surface']} "
                    f"[{row['selected_roles']}→{row['attachment_decision']};retained={row['renderer_role_retained']}]"
                    for row in rows
                ) or "MODE_ONLY_NO_SELECTED_HOST",
                "gdt739_nonbinding_conflict_evidence": (
                    dispatch["selecting_evidence"]
                    if dispatch["dimension_dispatch"] == "OPEN_SCALAR_CONFLICT" else "NONE"
                ),
                "manual_override_applied": int(bool(override)),
                "manual_override_reason": override.get("manual_reason", "NONE"),
                "renderer_changed_from_gdt739": changed,
                "plaintext_or_lexeme_claim": 0, "component_export_credit": 0,
            })
    return patches, targets


def form_profiles(
    patches: list[dict[str, object]], targets: list[dict[str, object]],
) -> list[dict[str, object]]:
    patch_by_form: dict[str, list[dict[str, object]]] = defaultdict(list)
    target_by_form: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in patches:
        patch_by_form[str(row["surface"])].append(row)
    for row in targets:
        target_by_form[str(row["surface"])].append(row)
    output: list[dict[str, object]] = []
    for surface in g739.LICENSED_FORMS:
        rows = patch_by_form[surface]
        adjudicated = target_by_form[surface]
        tiers = Counter(str(row["attachment_tier"]) for row in adjudicated)
        dims = Counter(str(row["gdt740_dimension_dispatch"]) for row in rows)
        carriers = Counter(str(row["gdt740_carrier_dispatch"]) for row in rows)
        renders = Counter(str(row["gdt740_working_render_de"]) for row in rows)
        output.append({
            "surface": surface, "opaque_head_id": rows[0]["opaque_head_id"],
            "family": rows[0]["family"], "level": rows[0]["level"],
            "occurrences": len(rows), "gdt739_specific_targets": len(adjudicated),
            "attached_strong": tiers["ATTACHED_STRONG"], "attached_supported": tiers["ATTACHED_SUPPORTED"],
            "attached_provisional_reverse": tiers["ATTACHED_PROVISIONAL_REVERSE"],
            "near_only_hold": tiers["NEAR_ONLY_HOLD"], "mode_only_no_host": tiers["MODE_ONLY_NO_HOST"],
            "manual_r2_relay": tiers["RELAY_R2_MANUAL"],
            "mode_downgraded_open": tiers["MODE_DOWNGRADED_OPEN"],
            "direct_conflict_or_boundary": sum(
                value for key, value in tiers.items()
                if key in {"DIRECT_COMPONENT_CONFLICT_OPEN", "DIRECT_FLANK_CONFLICT_OPEN", "DIRECT_BOUNDARY_HOLD"}
            ),
            "attachment_tier_counts": "|".join(f"{key}:{tiers[key]}" for key in sorted(tiers)),
            "axis_specific_retained": sum(int(row["axis_specific_dispatch_retained"]) for row in rows),
            "carrier_bound_retained": sum(int(row["carrier_locally_bound_retained"]) for row in rows),
            "specific_retained": sum(int(row["specific_local_dispatch_retained"]) for row in rows),
            "fully_open_after_attachment": sum(not int(row["specific_local_dispatch_retained"]) for row in rows),
            "changed_from_gdt739": sum(int(row["renderer_changed_from_gdt739"]) for row in rows),
            "dimension_dispatch_counts": "|".join(f"{key}:{dims[key]}" for key in sorted(dims)),
            "carrier_dispatch_counts": "|".join(f"{key}:{carriers[key]}" for key in sorted(carriers)),
            "distinct_renders": len(renders), "most_common_render_de": renders.most_common(1)[0][0],
            "global_lexeme_export": 0, "component_export_credit": 0,
        })
    return output


def safe_line_render(
    locus: str, cells_by_locus: dict[str, list[dict[str, str]]],
    patch_by_position: dict[tuple[str, int], dict[str, object]],
) -> str:
    units: list[str] = []
    for cell in cells_by_locus[locus]:
        key = (locus, int(cell["token_ordinal"]))
        if key in patch_by_position:
            units.append(str(patch_by_position[key]["gdt740_working_render_de"]))
            continue
        role = cell["practical_unit_role"]
        if role == "SPAN_COMPANION_SUPPRESSED":
            continue
        if role == "ATTACH_PREVIOUS_NO_UNIT":
            if units:
                units[-1] += cell["surface"]
            continue
        value = cell["v99r7_practical_render_once_de"]
        safe = (
            cell["unknown_v99r7"] == "0"
            and cell["gdt734_confidence_level"].startswith(("W2", "W3"))
            and cell["gdt734_composition_semantic_credit"] == "0"
            and not g739.retired_hits(value)
            and not g739.strict_initial_head(cell["surface"])
        )
        units.append(value if safe else f"[{cell['surface']}:?]")
    return "; ".join(units)


def passage_reviews(
    old_passages: list[dict[str, str]], patches: list[dict[str, object]],
    targets: list[dict[str, object]], cells: dict[tuple[str, int], dict[str, str]],
    manual_specs: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    cells_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cells.values():
        cells_by_locus[row["locus"]].append(row)
    for rows in cells_by_locus.values():
        rows.sort(key=lambda item: int(item["token_ordinal"]))
    patch_by_position = {(str(row["locus"]), int(row["token_ordinal"])): row for row in patches}
    # Representative lines include deliberately open controls that are not in
    # the 95-row formerly-specific adjudication subset, so select from all 202.
    patches_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in patches:
        patches_by_locus[str(row["locus"])].append(row)
    output: list[dict[str, object]] = []
    for old in old_passages:
        focal = old["focal_surfaces"].split("|")
        rows = [row for row in patches_by_locus[old["locus"]] if row["surface"] in focal]
        rows.sort(key=lambda row: int(row["token_ordinal"]))
        if Counter(str(row["surface"]) for row in rows) != Counter(focal):
            raise AssertionError(f"passage target mismatch: {old['passage_id']}")
        spec = manual_specs[old["passage_id"]]
        output.append({
            "passage_id": old["passage_id"], "page": old["page"], "locus": old["locus"],
            "section": old["section"], "language": old["language"],
            "focal_surfaces": old["focal_surfaces"], "zl3b_line": old["zl3b_line"],
            "gdt739_target_renders_de": old["gdt739_target_renders_de"],
            "gdt740_target_renders_de": " || ".join(f"{row['surface']} → {row['gdt740_working_render_de']}" for row in rows),
            "attachment_tiers": " || ".join(f"{row['surface']}={row['attachment_tier']}" for row in rows),
            "manual_visual_verdict": spec["manual_visual_verdict"],
            "manual_reason": spec["manual_reason"],
            "cellwise_audit_display_de": safe_line_render(old["locus"], cells_by_locus, patch_by_position),
            "reader_note": (
                "semicolon-separated cellwise working defaults; no clause or attachment is implied "
                "outside the focal target; unsupported or retired-patient cells remain [surface:?]"
            ),
        })
    return output


def write_reader(
    path: Path, passages: list[dict[str, object]], profiles: list[dict[str, object]],
    targets: list[dict[str, object]],
) -> None:
    tiers = Counter(str(row["attachment_tier"]) for row in targets)
    lines = [
        "# GDT740 direct-attachment reader", "",
        "These remain occurrence-scoped working renders, not plaintext translations.",
        "Direct contacts are attachment-eligible but can lose to a boundary or flank conflict.",
        "Radius-two contacts are held by default; two enumerated same-direction relays survive.", "",
        "## Attachment result", "",
        "Across 95 formerly specific targets: "
        + ", ".join(f"{key}={tiers[key]}" for key in sorted(tiers)) + ".", "",
        "## Twelve-form profile", "",
        "| whole | occurrences | axis kept | carrier kept | fully open | changed | common render |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in profiles:
        lines.append(
            f"| `{row['surface']}` | {row['occurrences']} | {row['axis_specific_retained']} | "
            f"{row['carrier_bound_retained']} | {row['fully_open_after_attachment']} | "
            f"{row['changed_from_gdt739']} | {row['most_common_render_de']} |"
        )
    lines.extend(["", "## Twenty cached passage checks", ""])
    for row in passages:
        lines.extend([
            f"### {row['passage_id']} — {row['locus']} ({row['section']}/{row['language']})", "",
            f"- EVA line: `{row['zl3b_line']}`",
            f"- Targets: **{row['gdt740_target_renders_de']}**",
            f"- Attachment: {row['attachment_tiers']}",
            f"- Manual check: {row['manual_visual_verdict']} — {row['manual_reason']}",
            f"- Cellwise audit display: {row['cellwise_audit_display_de']}",
            "- Display note: semicolon-separated cellwise working defaults; no clause or "
            "attachment is implied outside the focal target.", "",
        ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def physical_folio(page: str) -> str:
    digits = "".join(character for character in page[1:] if character.isdigit())
    return f"f{digits}" if digits else page


def edge_packet(contacts: list[dict[str, object]]) -> list[dict[str, object]]:
    """Expose repeated direct relations to GDT388 as deliberately ineligible."""
    output: list[dict[str, object]] = []
    for row in contacts:
        if int(row["distance"]) != 1 or int(row["guarded_reader_exact_pair_occurrences"]) < 2:
            continue
        target = int(row["target_ordinal"])
        neighbor = int(row["neighbor_ordinal"])
        page = str(row["page"])
        locus = str(row["locus"])
        output.append({
            "edge_id": f"G740E{len(output) + 1:03d}", "batch_id": "GDT740_ATTACHMENT",
            "page": page, "physical_folio": physical_folio(page), "diagram_unit_id": "CACHED_TEXT_LINE",
            "pivot_visual_id": f"TARGET_TOKEN_{target}", "pivot_locus": f"{locus}@{target}",
            "target_visual_id": f"HOST_TOKEN_{neighbor}", "target_locus": f"{locus}@{neighbor}",
            "relation_type": "WORKING_LOCAL_HOST_ATTACHMENT",
            "direction_basis": "FORMAL_PAIR_RECURRENCE_AND_RENDERER_ROLE",
            "ownership_basis": "OCCURRENCE_SCOPED_SEMANTIC_COMPATIBILITY",
            "geometry_only_selection": "FALSE", "source_manifest_id": "GDT740",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT740_BUILDER", "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "B_WORKING_LOCAL", "ambiguity_state": "WORKING_ONLY",
            "formal_access_state": "FORMAL_ACCESSED", "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_FORMAL_ATTACHMENT_EDGE",
        })
    return output


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rules = read_tsv(SRC / "ATTACHMENT_RULES.tsv")
    if [row["rule_id"] for row in rules] != [f"A{number:02d}" for number in range(1, 9)]:
        raise AssertionError("attachment rule deck changed")
    historical = read_tsv(SRC / "HISTORICAL_ATTACHMENT_PRIORS.tsv")
    if len(historical) != 7:
        raise AssertionError("historical attachment prior deck changed")
    manual_rows = read_tsv(SRC / "PASSAGE_MANUAL_ADJUDICATION.tsv")
    manual_specs = {row["passage_id"]: row for row in manual_rows}
    if len(manual_specs) != 20:
        raise AssertionError("twenty passage adjudications required")
    override_rows = read_tsv(SRC / "MANUAL_ATTACHMENT_OVERRIDES.tsv")
    overrides = {row["dispatch_id"]: row for row in override_rows}
    if len(overrides) != 13:
        raise AssertionError("thirteen manual attachment overrides required")

    dispatches = read_tsv(ROOT / G739_ART_REL / "DIMENSION_202_DISPATCH.tsv")
    windows = read_tsv(ROOT / G739_ART_REL / "WINDOW_202_TOKEN_AUDIT.tsv")
    old_passages = read_tsv(ROOT / G739_ART_REL / "REPRESENTATIVE_PASSAGES.tsv")
    source_patches = read_tsv(ROOT / PATCH_REL)
    if len(dispatches) != len(source_patches) or len(dispatches) != 202:
        raise AssertionError("GDT739/GDT738 202-target boundary changed")
    if any(row["page"].startswith("f84") for row in dispatches):
        raise AssertionError("sealed page entered GDT740 target")

    pair_counts, raw_pair_counts, triple_counts, pair_loci, cells, guards = exact_pair_census()
    contacts, pair_rows = build_contacts(
        dispatches, windows, cells, pair_counts, raw_pair_counts, triple_counts, pair_loci
    )
    ring_evidence = typed_ring_evidence(dispatches, windows, contacts)
    patches, targets = make_patch_and_targets(dispatches, contacts, overrides)
    profiles = form_profiles(patches, targets)
    passages = passage_reviews(old_passages, patches, targets, cells, manual_specs)
    edges = edge_packet(contacts)

    contact_fields = [key for key in contacts[0] if not key.startswith("_")]
    write_tsv(output_dir / "TYPED_104_RING_EVIDENCE.tsv", ring_evidence, list(ring_evidence[0]))
    write_tsv(output_dir / "SELECTED_103_CONTACT_ATTACHMENT.tsv", contacts, contact_fields)
    write_tsv(output_dir / "ORDERED_PAIR_100_RECURRENCE.tsv", pair_rows, list(pair_rows[0]))
    write_tsv(output_dir / "TARGET_95_ATTACHMENT_ADJUDICATION.tsv", targets, list(targets[0]))
    write_tsv(output_dir / "TARGET_202_RENDERER_PATCH_V2.tsv", patches, list(patches[0]))
    write_tsv(output_dir / "FORM_12_ATTACHMENT_PROFILE.tsv", profiles, list(profiles[0]))
    write_tsv(output_dir / "PASSAGE_20_ATTACHMENT_REVIEW.tsv", passages, list(passages[0]))
    write_reader(output_dir / "GDT740_ATTACHMENT_READER.md", passages, profiles, targets)
    write_tsv(output_dir / "GDT740_GDT388_EDGE_PACKET.tsv", edges, (
        "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id", "pivot_visual_id",
        "pivot_locus", "target_visual_id", "target_locus", "relation_type", "direction_basis",
        "ownership_basis", "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
        "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer", "relation_reviewer",
        "relation_confidence", "ambiguity_state", "formal_access_state", "fold_assignment",
        "eligibility_status",
    ))

    contact_decisions = Counter(str(row["attachment_decision"]) for row in contacts)
    target_tiers = Counter(str(row["attachment_tier"]) for row in targets)
    scalar = [row for row in patches if row["surface"] in SCALAR_FORMS]
    state = [row for row in patches if row["surface"] in STATE_FORMS]
    scalar_counts = Counter(str(row["gdt740_dimension_dispatch"]) for row in scalar)
    carrier_counts = Counter(str(row["gdt740_carrier_dispatch"]) for row in patches)
    result: dict[str, object] = {
        "schema": "GDT740_LOCAL_HOST_ATTACHMENT_ADJUDICATION_V1",
        "status": (
            "PARTIAL__103_BINDING_CONTACTS_PLUS_ONE_CONFLICT_CUE__62_DIRECT_CONTACTS_ON_58_TARGETS__"
            "39_RADIUS_TWO_HELD_PLUS_TWO_MANUAL_RELAYS__ONE_LOCAL_RESULT_MODE__"
            "BOUNDARY_AND_FLANK_FUSION_REPAIRED__ZERO_LEXEME_OR_COMPONENT_EXPORT__NO_NEW_PAGE"
        ),
        "scope": {
            "inherited_allowlist_pages": guards["allowed_pages"],
            "target_pages": len({row["page"] for row in dispatches}),
            "target_loci": len({row["locus"] for row in dispatches}),
            "new_pages_used": 0, "f84_used": False, "f84r_used": False,
            "guard_stats": {"tokens": guards["tokens"], "cross": guards["cross"]},
        },
        "source": {
            "complete_wholes": 12, "all_renderer_positions": 202,
            "gdt739_specific_targets": len(targets), "selected_contacts": len(contacts),
            "selected_contact_targets": len({row["patch_id"] for row in contacts}),
            "typed_ring_evidence_contacts_including_nonbinding_conflict": 104,
            "nonbinding_conflict_only_contacts": 1,
        },
        "attachment": {
            "contact_distance_counts": dict(sorted(Counter(int(row["distance"]) for row in contacts).items())),
            "contact_role_counts": dict(sorted(Counter(str(row["selected_roles"]) for row in contacts).items())),
            "contact_decisions": dict(sorted(contact_decisions.items())),
            "unique_ordered_pair_keys": len(pair_rows),
            "repeated_ordered_pair_keys": sum(int(row["guarded_reader_exact_pair_occurrences"]) >= 2 for row in pair_rows),
            "repeated_direct_contacts": sum(int(row["guarded_reader_exact_pair_occurrences"]) >= 2 for row in contacts),
            "raw_repeated_ordered_pair_keys": sum(int(row["guarded_zl3b_pair_occurrences"]) >= 2 for row in pair_rows),
            "raw_only_repeat_control_contacts": sum(int(row["raw_only_repeat_control"]) for row in contacts),
            "radius_two_intervening_emit_own_unit": sum(int(row["intervening_emits_own_unit"]) for row in contacts),
            "radius_two_intervening_known": sum(int(row["distance"]) == 2 and row["intervening_unknown_v99r7"] == "0" for row in contacts),
            "renderer_retained_contact_rows": sum(int(row["renderer_role_retained"]) for row in contacts),
            "renderer_retained_role_flags": sum(
                int(row["axis_role_retained"]) + int(row["carrier_role_retained"])
                for row in contacts
            ),
            "renderer_retained_axis_role_flags": sum(int(row["axis_role_retained"]) for row in contacts),
            "renderer_retained_carrier_role_flags": sum(int(row["carrier_role_retained"]) for row in contacts),
            "manual_radius_two_relay_contacts": sum(
                int(row["distance"]) == 2 and int(row["renderer_role_retained"]) for row in contacts
            ),
            "held_radius_two_contacts": sum(
                int(row["distance"]) == 2 and not int(row["renderer_role_retained"]) for row in contacts
            ),
            "target_tiers": dict(sorted(target_tiers.items())),
        },
        "renderer": {
            "scalar_dispatches": dict(sorted(scalar_counts.items())),
            "source_state_modes": dict(sorted(Counter(str(row["gdt739_state_mode"]) for row in state).items())),
            "gdt740_state_modes": dict(sorted(Counter(str(row["gdt740_state_mode"]) for row in state).items())),
            "axis_specific_occurrences": sum(int(row["axis_specific_dispatch_retained"]) for row in patches),
            "carrier_classes": dict(sorted(carrier_counts.items())),
            "carrier_bound_occurrences": sum(int(row["carrier_locally_bound_retained"]) for row in patches),
            "specific_occurrences": sum(int(row["specific_local_dispatch_retained"]) for row in patches),
            "fully_open_occurrences": sum(not int(row["specific_local_dispatch_retained"]) for row in patches),
            "changed_from_gdt739": sum(int(row["renderer_changed_from_gdt739"]) for row in patches),
        },
        "interpretive_update": {
            "direct": "attachment-eligible, but closure boundaries, split carrier components, and opposite-flank axis-carrier fusion can open the role",
            "radius_two": "default discovery-only across an independent cell; two enumerated same-axis or same-carrier relay hypotheses survive",
            "historical_order": "left-host microentry order receives qualitative model weight, not a frequency claim; right contacts remain possible rubric scope or register inversion",
            "formal_order": "H1/H2 right and H3/H4 left is a separate occurrence-role compatibility diagnostic, not a language rule",
            "result_mode": "one direct process-closure occurrence retains result mode; seven former overrides return to descriptive state",
        },
        "edge_intake": {
            "packet_rows": len(edges), "expected_status": "INVALID_PACKET",
            "reason": "formally accessed semantic selection; no external capacity, held-folio or mobile-null gates",
        },
        "claims": {
            "confirmed_lexemes": 0, "plaintext_translations_claimed": 0,
            "species_or_substances_named": 0, "head_or_body_lexeme_credit": 0,
            "component_export_credit": 0, "unseen_forms_predicted": 0,
        },
        "artifact_rows": {
            "TYPED_104_RING_EVIDENCE.tsv": len(ring_evidence),
            "SELECTED_103_CONTACT_ATTACHMENT.tsv": len(contacts),
            "ORDERED_PAIR_100_RECURRENCE.tsv": len(pair_rows),
            "TARGET_95_ATTACHMENT_ADJUDICATION.tsv": len(targets),
            "TARGET_202_RENDERER_PATCH_V2.tsv": len(patches),
            "FORM_12_ATTACHMENT_PROFILE.tsv": len(profiles),
            "PASSAGE_20_ATTACHMENT_REVIEW.tsv": len(passages),
            "GDT740_ATTACHMENT_READER.md": len(passages),
            "GDT740_GDT388_EDGE_PACKET.tsv": len(edges),
        },
        "artifact_hashes": {str(BASE_REL / "artifacts" / name): sha256(output_dir / name) for name in OUTPUT_NAMES},
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    result = build(parser.parse_args().output_dir)
    print(json.dumps({
        "schema": result["schema"], "status": result["status"],
        "attachment": result["attachment"], "renderer": result["renderer"],
        "artifact_rows": result["artifact_rows"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
