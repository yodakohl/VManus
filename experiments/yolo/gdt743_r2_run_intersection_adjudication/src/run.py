#!/usr/bin/env python3
"""Test carrier-run direction overrides and partial-axis intersections."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt743_r2_run_intersection_adjudication")
EXP = ROOT / BASE_REL
DEFAULT_ARTIFACTS = EXP / "artifacts"
G742_ART = ROOT / "experiments/yolo/gdt742_r2_open_collision_adjudication/artifacts"
G739_ART = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/artifacts"
QUALITY = {"HOT", "COLD", "DRY", "MOIST"}
CARRIERS = {"PREPARATION", "MATERIAL", "PART"}
CARRIER_ORDER = ("PREPARATION", "MATERIAL", "PART")
FORMAL_SIDE = {"H1": "R", "H2": "R", "H3": "L", "H4": "L"}
STATUS = (
    "PARTIAL__REQUESTED_CARRIER_COVERAGE_GE3_ANALOGY_ADDS_D0075__"
    "RUN_GATE_ABLATION_ONE_TO_ONE_EXCLUDES_ZERO__"
    "CONDITIONED_HOT_INTERSECTION_REMAINS_OPEN_LEAD__"
    "36_AXIS__46_CARRIER__59_SPECIFIC__143_OPEN__"
    "PROVISIONAL_COMPOSITE_RULE__ZERO_LEXEME_OR_COMPONENT_EXPORT__NO_NEW_PAGE"
)
OUTPUT_NAMES = (
    "TARGET_202_REQUESTED_CARRIER_COVERAGE_FEATURES.tsv",
    "R2_41_EXTENSION_DISPATCH.tsv",
    "RUN_8_REQUESTED_CARRIER_COVERAGE_CENSUS.tsv",
    "CARRIER_6_UNCONDITIONED_COVERAGE_CENSUS.tsv",
    "AXIS_5_INHERITED_FAVORED_CENSUS.tsv",
    "CANDIDATE_4_REMAINING_ROLE_ADJUDICATION.tsv",
    "TARGET_202_RENDERER_PATCH_V5.tsv",
    "FOCUS_3_EXTENSION_REVIEW.tsv",
    "GDT743_GDT388_RUN_OVERRIDE_EDGE_PACKET.tsv",
    "GDT743_RUN_INTERSECTION_READER.md",
)
DECISION_FIELDS = (
    "distance", "selected_roles", "formal_role_direction_match",
    "guarded_reader_exact_full_frame_occurrences", "middle_reader_exact",
    "middle_known", "intervening_emits_own_unit",
    "intervening_strict_initial_head", "intervening_another_gdt738_target",
    "middle_barrier", "target_wanted_carrier_set", "host_carrier_set",
    "middle_carrier_set", "target_dimension", "target_favored_axis",
    "host_quality_set", "middle_quality_set", "host_scalar_class_set",
    "middle_scalar_class_set", "axis_continuity",
    "selected_side_requested_carrier_coverage_screened",
    "opposite_side_requested_carrier_coverage_screened",
    "selected_side_first_three_coverage_no_close",
    "requested_carrier_ge3_unique_to_selected_side",
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


def values(value: object, separator: str = "|") -> set[str]:
    text = str(value)
    if text in {"", "NONE", "NA", "OPEN", "NOT_APPLICABLE"}:
        return set()
    return set(text.split(separator))


def carrier_values(value: object) -> set[str]:
    return values(str(value).replace("_", "|")) & CARRIERS


def clean_window(row: dict[str, str]) -> bool:
    return bool(
        row["neighbor_reader_exact"] == "1"
        and row["neighbor_unknown_v99r7"] == "0"
        and row["neighbor_composition_semantic_credit"] == "0"
        and row["strict_initial_head_neighbor"] == "0"
        and row["another_gdt738_target"] == "0"
        and row["retired_patient_words"] == "NONE"
    )


def contiguous_run(
    windows: dict[tuple[str, int], dict[str, str]], side: str,
    wanted: set[str], tag: str | None = None,
    forbidden_tags: set[str] | None = None,
) -> dict[str, object]:
    raw = 0
    clean = 0
    exact_carrier = 0
    first_three_no_close = True
    members: list[str] = []
    if not wanted and tag is None:
        return {
            "raw": 0, "clean": 0, "exact": 0, "first_three_no_close": 0,
            "members": "NONE",
        }
    for distance in range(1, 6):
        row = windows.get((side, distance))
        if row is None:
            break
        tags = values(row["axis_tags"])
        if tags & (forbidden_tags or set()):
            break
        carries = tag in tags if tag is not None else bool(wanted <= (tags & CARRIERS))
        if not carries:
            break
        raw += 1
        members.append(f"{distance}:{row['neighbor_surface']}:{row['axis_tags']}")
        if distance <= 3 and "CLOSE" in tags:
            first_three_no_close = False
        if clean_window(row) and clean == distance - 1:
            clean += 1
            if tag is None and (tags & CARRIERS) == wanted and exact_carrier == distance - 1:
                exact_carrier += 1
        if "CLOSE" in tags:
            break
    return {
        "raw": raw,
        "clean": clean,
        "exact": exact_carrier,
        "first_three_no_close": int(first_three_no_close and clean >= 3),
        "members": "|".join(members) or "NONE",
    }


def target_coverage_features(
    dispatches: list[dict[str, str]], windows: list[dict[str, str]],
    patches: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    by_patch: dict[str, dict[tuple[str, int], dict[str, str]]] = defaultdict(dict)
    for row in windows:
        key = (row["side"], int(row["distance"]))
        if key in by_patch[row["patch_id"]]:
            raise AssertionError("duplicate target window coordinate")
        by_patch[row["patch_id"]][key] = row
    output: list[dict[str, object]] = []
    for source in dispatches:
        wanted = carrier_values(source["carrier_dispatch"])
        target_windows = by_patch[source["patch_id"]]
        left = contiguous_run(target_windows, "L", wanted)
        right = contiguous_run(target_windows, "R", wanted)
        left_no_process_pass = contiguous_run(
            target_windows, "L", wanted, forbidden_tags={"PROCESS", "PASS"},
        )
        right_no_process_pass = contiguous_run(
            target_windows, "R", wanted, forbidden_tags={"PROCESS", "PASS"},
        )
        left_no_process = contiguous_run(
            target_windows, "L", wanted, forbidden_tags={"PROCESS"},
        )
        right_no_process = contiguous_run(
            target_windows, "R", wanted, forbidden_tags={"PROCESS"},
        )
        left_no_pass = contiguous_run(
            target_windows, "L", wanted, forbidden_tags={"PASS"},
        )
        right_no_pass = contiguous_run(
            target_windows, "R", wanted, forbidden_tags={"PASS"},
        )
        left_no_close = contiguous_run(
            target_windows, "L", wanted, forbidden_tags={"CLOSE"},
        )
        right_no_close = contiguous_run(
            target_windows, "R", wanted, forbidden_tags={"CLOSE"},
        )
        left_no_process_pass_close = contiguous_run(
            target_windows, "L", wanted, forbidden_tags={"PROCESS", "PASS", "CLOSE"},
        )
        right_no_process_pass_close = contiguous_run(
            target_windows, "R", wanted, forbidden_tags={"PROCESS", "PASS", "CLOSE"},
        )
        clean_long_sides = [
            side for side, run in (("L", left), ("R", right))
            if int(run["clean"]) >= 3 and int(run["first_three_no_close"])
        ]
        unique_side = clean_long_sides[0] if len(clean_long_sides) == 1 else "NONE"
        favored = source["favored_axis_not_automatic"]
        if favored in QUALITY:
            left_axis = contiguous_run(target_windows, "L", set(), favored)
            right_axis = contiguous_run(target_windows, "R", set(), favored)
        else:
            left_axis = {"clean": 0}
            right_axis = {"clean": 0}
        patch = patches[source["dispatch_id"]]
        output.append({
            "run_feature_id": f"G743-T{len(output) + 1:04d}",
            "gdt739_dispatch_id": source["dispatch_id"],
            "gdt738_patch_id": source["patch_id"],
            "page": source["page"], "locus": source["locus"],
            "target_ordinal": source["token_ordinal"], "target_surface": source["surface"],
            "opaque_head_id": source["opaque_head_id"],
            "formal_carrier_side": FORMAL_SIDE[source["opaque_head_id"]],
            "requested_carrier_set": "|".join(carrier for carrier in CARRIER_ORDER if carrier in wanted) or "NONE",
            "gdt739_requested_carrier_dispatch": source["carrier_dispatch"],
            "gdt742_carrier_dispatch": patch["gdt742_carrier_dispatch"],
            "left_requested_carrier_coverage_raw": left["raw"],
            "right_requested_carrier_coverage_raw": right["raw"],
            "left_requested_carrier_coverage_screened": left["clean"],
            "right_requested_carrier_coverage_screened": right["clean"],
            "left_requested_carrier_exact_set_screened": left["exact"],
            "right_requested_carrier_exact_set_screened": right["exact"],
            "left_requested_carrier_no_process_screened": left_no_process["clean"],
            "right_requested_carrier_no_process_screened": right_no_process["clean"],
            "left_requested_carrier_no_pass_screened": left_no_pass["clean"],
            "right_requested_carrier_no_pass_screened": right_no_pass["clean"],
            "left_requested_carrier_no_close_screened": left_no_close["clean"],
            "right_requested_carrier_no_close_screened": right_no_close["clean"],
            "left_requested_carrier_no_process_pass_screened": left_no_process_pass["clean"],
            "right_requested_carrier_no_process_pass_screened": right_no_process_pass["clean"],
            "left_requested_carrier_no_process_pass_close_screened": left_no_process_pass_close["clean"],
            "right_requested_carrier_no_process_pass_close_screened": right_no_process_pass_close["clean"],
            "left_first_three_coverage_no_close": left["first_three_no_close"],
            "right_first_three_coverage_no_close": right["first_three_no_close"],
            "requested_carrier_ge3_unique_side": unique_side,
            "requested_carrier_ge3_formal_direction_match": int(unique_side != "NONE" and unique_side == FORMAL_SIDE[source["opaque_head_id"]]),
            "requested_carrier_coverage_members": left["members"] if unique_side == "L" else right["members"] if unique_side == "R" else "NONE",
            "favored_axis": favored,
            "left_inherited_favored_axis_coverage_screened": left_axis["clean"],
            "right_inherited_favored_axis_coverage_screened": right_axis["clean"],
            "bilateral_favored_axis_support": int(int(left_axis["clean"]) >= 1 and int(right_axis["clean"]) >= 1),
            "bilateral_two_by_two_favored_axis_support": int(int(left_axis["clean"]) >= 2 and int(right_axis["clean"]) >= 2),
            "current_carrier_bound": int(patch["gdt742_carrier_dispatch"] != "OPEN"),
            "current_axis_specific": patch["axis_specific_dispatch_retained"],
            "new_page_or_transcription": 0,
            "literal_plaintext_claimed": 0,
            "component_export_credit": 0,
        })
    return output


def unconditional_carrier_coverage_census(
    dispatches: list[dict[str, str]], windows: list[dict[str, str]],
    patches: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    """Expose every >=3 carrier-coverage case, not only inherited requests."""
    by_patch: dict[str, dict[tuple[str, int], dict[str, str]]] = defaultdict(dict)
    for row in windows:
        by_patch[row["patch_id"]][(row["side"], int(row["distance"]))] = row
    output: list[dict[str, object]] = []
    for source in dispatches:
        for candidate in CARRIER_ORDER:
            left = contiguous_run(by_patch[source["patch_id"]], "L", {candidate})
            right = contiguous_run(by_patch[source["patch_id"]], "R", {candidate})
            qualifying = [
                side for side, coverage in (("L", left), ("R", right))
                if int(coverage["clean"]) >= 3 and int(coverage["first_three_no_close"])
            ]
            if len(qualifying) != 1:
                continue
            side = qualifying[0]
            selected = left if side == "L" else right
            patch = patches[source["dispatch_id"]]
            requested = carrier_values(source["carrier_dispatch"])
            output.append({
                "coverage_id": f"G743-U{len(output) + 1:02d}",
                "gdt739_dispatch_id": source["dispatch_id"],
                "gdt738_patch_id": source["patch_id"],
                "page": source["page"], "locus": source["locus"],
                "target_ordinal": source["token_ordinal"],
                "target_surface": source["surface"],
                "opaque_head_id": source["opaque_head_id"],
                "formal_carrier_side": FORMAL_SIDE[source["opaque_head_id"]],
                "candidate_carrier": candidate,
                "coverage_unique_side": side,
                "coverage_screened": selected["clean"],
                "coverage_exact_set_screened": selected["exact"],
                "coverage_members": selected["members"],
                "formal_direction_match": int(side == FORMAL_SIDE[source["opaque_head_id"]]),
                "gdt739_requested_carrier_dispatch": source["carrier_dispatch"],
                "requested_candidate_matches_scan": int(requested == {candidate}),
                "gdt742_carrier_dispatch": patch["gdt742_carrier_dispatch"],
                "prior_carrier_matches_scan": int(patch["gdt742_carrier_dispatch"] == candidate),
                "current_carrier_bound": int(patch["gdt742_carrier_dispatch"] != "OPEN"),
                "new_page_or_transcription": 0,
                "literal_plaintext_claimed": 0,
                "component_export_credit": 0,
            })
    return output


def coverage_sensitivity(rows: list[dict[str, object]]) -> dict[str, list[str]]:
    def ids_for(left: str, right: str) -> list[str]:
        return sorted(
            str(row["gdt739_dispatch_id"])
            for row in rows
            if max(int(row[left]), int(row[right])) >= 3
        )

    return {
        "base_requested_carrier_coverage_ge3_ids": sorted(
            str(row["gdt739_dispatch_id"])
            for row in rows if row["requested_carrier_ge3_unique_side"] != "NONE"
        ),
        "exact_carrier_set_prefix_ge3_ids": ids_for(
            "left_requested_carrier_exact_set_screened",
            "right_requested_carrier_exact_set_screened",
        ),
        "exclude_process_ge3_ids": ids_for(
            "left_requested_carrier_no_process_screened",
            "right_requested_carrier_no_process_screened",
        ),
        "exclude_pass_ge3_ids": ids_for(
            "left_requested_carrier_no_pass_screened",
            "right_requested_carrier_no_pass_screened",
        ),
        "exclude_close_ge3_ids": ids_for(
            "left_requested_carrier_no_close_screened",
            "right_requested_carrier_no_close_screened",
        ),
        "exclude_process_pass_ge3_ids": ids_for(
            "left_requested_carrier_no_process_pass_screened",
            "right_requested_carrier_no_process_pass_screened",
        ),
        "exclude_process_pass_close_ge3_ids": ids_for(
            "left_requested_carrier_no_process_pass_close_screened",
            "right_requested_carrier_no_process_pass_close_screened",
        ),
    }


def common_frame(feature: dict[str, str]) -> bool:
    return bool(
        feature["distance"] == "2"
        and int(feature["guarded_reader_exact_full_frame_occurrences"]) >= 1
        and feature["middle_reader_exact"] == "1"
        and feature["middle_known"] == "1"
        and feature["intervening_emits_own_unit"] == "1"
        and feature["intervening_strict_initial_head"] == "0"
        and feature["intervening_another_gdt738_target"] == "0"
    )


def adjudicate_r2(feature: dict[str, str]) -> dict[str, object]:
    """Recompute GDT742 and add one surface-/identity-/outcome-free run branch."""
    if set(feature) != set(DECISION_FIELDS):
        raise AssertionError("GDT743 decision record changed")
    selected = values(feature["selected_roles"], "+")
    wanted = carrier_values(feature["target_wanted_carrier_set"])
    host_carriers = carrier_values(feature["host_carrier_set"])
    middle_carriers = carrier_values(feature["middle_carrier_set"])
    frame = common_frame(feature)
    open_frame = bool(frame and feature["middle_barrier"] == "OPEN")
    direction = feature["formal_role_direction_match"] == "1"
    exact_axis = feature["axis_continuity"] == "EXACT_SINGLE"
    full_carrier = bool(wanted and wanted <= host_carriers and wanted <= middle_carriers)
    axis_active = bool(open_frame and direction and selected == {"AXIS"} and exact_axis)
    base_carrier = bool(
        open_frame and direction and full_carrier
        and (
            selected == {"CARRIER"}
            or selected == {"AXIS", "CARRIER"} and feature["axis_continuity"] == "NONE"
        )
    )
    relaxed_reverse_full_carrier = bool(
        open_frame and not direction and "CARRIER" in selected and full_carrier
    )
    coverage_gate = bool(
        int(feature["selected_side_requested_carrier_coverage_screened"]) >= 3
        and int(feature["opposite_side_requested_carrier_coverage_screened"]) < 3
        and feature["selected_side_first_three_coverage_no_close"] == "1"
        and feature["requested_carrier_ge3_unique_to_selected_side"] == "1"
    )
    run_override = bool(relaxed_reverse_full_carrier and coverage_gate)
    carrier_active = bool(base_carrier or run_override)

    intersection = (
        values(feature["host_quality_set"]) & values(feature["middle_quality_set"]) & QUALITY
    )
    generic_intersection = bool(
        open_frame and "AXIS" in selected
        and "QUALITY_DEGREE" in values(feature["host_scalar_class_set"])
        and "QUALITY_DEGREE" in values(feature["middle_scalar_class_set"])
        and len(intersection) == 1
    )
    favored_intersection = bool(
        generic_intersection and feature["axis_continuity"] == "PARTIAL"
        and intersection == {feature["target_favored_axis"]}
    )
    if run_override:
        trace = "PROVISIONAL_REQUESTED_CARRIER_COVERAGE_ANALOGY"
    elif axis_active:
        trace = "GDT742_STRICT_AXIS_RELAY"
    elif base_carrier:
        trace = "GDT742_CARRIER_RELAY"
    else:
        trace = "R2_HOLD"
    return {
        "axis_active": int(axis_active),
        "carrier_active": int(carrier_active),
        "run_override": int(run_override),
        "relaxed_reverse_full_carrier": int(relaxed_reverse_full_carrier),
        "coverage_gate": int(coverage_gate),
        "coverage_excludes_relaxed_trigger": int(relaxed_reverse_full_carrier and not coverage_gate),
        "generic_intersection": int(generic_intersection),
        "favored_intersection": int(favored_intersection),
        "intersection_axis_set": "|".join(sorted(intersection)) or "NONE",
        "common_frame": int(frame),
        "full_carrier": int(full_carrier),
        "trace": trace,
    }


def r2_dispatch(
    source_contacts: list[dict[str, str]], runs: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for source in source_contacts:
        if source["distance"] != "2":
            continue
        run = runs[source["dispatch_id"]]
        if carrier_values(source["target_wanted_carrier_set"]) != carrier_values(run["requested_carrier_set"]):
            raise AssertionError("contact/run requested carrier mismatch")
        side = source["side"]
        opposite = "R" if side == "L" else "L"
        decision_record = {field: source[field] for field in DECISION_FIELDS if field in source}
        decision_record.update({
            "selected_side_requested_carrier_coverage_screened": str(run[f"{'left' if side == 'L' else 'right'}_requested_carrier_coverage_screened"]),
            "opposite_side_requested_carrier_coverage_screened": str(run[f"{'left' if opposite == 'L' else 'right'}_requested_carrier_coverage_screened"]),
            "selected_side_first_three_coverage_no_close": str(run[f"{'left' if side == 'L' else 'right'}_first_three_coverage_no_close"]),
            "requested_carrier_ge3_unique_to_selected_side": str(int(run["requested_carrier_ge3_unique_side"] == side)),
        })
        decision = adjudicate_r2(decision_record)
        old_axis = int(source["gdt742_axis_role_retained"])
        old_carrier = int(source["gdt742_carrier_role_retained"])
        new_axis = int(decision["axis_active"])
        new_carrier = int(decision["carrier_active"])
        row: dict[str, object] = dict(source)
        row.update({
            "left_requested_carrier_coverage_raw": run["left_requested_carrier_coverage_raw"],
            "right_requested_carrier_coverage_raw": run["right_requested_carrier_coverage_raw"],
            "left_requested_carrier_coverage_screened": run["left_requested_carrier_coverage_screened"],
            "right_requested_carrier_coverage_screened": run["right_requested_carrier_coverage_screened"],
            "left_requested_carrier_exact_set_screened": run["left_requested_carrier_exact_set_screened"],
            "right_requested_carrier_exact_set_screened": run["right_requested_carrier_exact_set_screened"],
            "requested_carrier_ge3_unique_side": run["requested_carrier_ge3_unique_side"],
            "intersection_axis_set": decision["intersection_axis_set"],
            "generic_singleton_axis_intersection": decision["generic_intersection"],
            "favored_partial_axis_intersection": decision["favored_intersection"],
            "gdt743_axis_role_retained": new_axis,
            "gdt743_carrier_role_retained": new_carrier,
            "gdt743_renderer_role_retained": int(new_axis or new_carrier),
            "relaxed_reverse_full_carrier_trigger": decision["relaxed_reverse_full_carrier"],
            "requested_carrier_coverage_gate": decision["coverage_gate"],
            "requested_carrier_coverage_override": decision["run_override"],
            "coverage_excludes_relaxed_trigger": decision["coverage_excludes_relaxed_trigger"],
            "gdt743_rule_trace": decision["trace"],
            "axis_changed_from_gdt742": int(new_axis != old_axis),
            "carrier_changed_from_gdt742": int(new_carrier != old_carrier),
            "role_changed_from_gdt742": int(new_axis != old_axis or new_carrier != old_carrier),
            "dispatcher_uses_dispatch_id_or_locus": 0,
            "literal_plaintext_claimed": 0,
            "component_export_credit": 0,
        })
        output.append(row)
    return output


def carrier_name(row: dict[str, object]) -> str:
    carriers = carrier_values(row["target_wanted_carrier_set"])
    return "_".join(carrier for carrier in CARRIER_ORDER if carrier in carriers) or "OPEN"


def render_open_scalar(source: dict[str, str], carrier: str, coverage_length: int) -> str:
    if source["family"] != "SCALAR" or source["gdt742_dimension_dispatch"] != "OPEN_SCALAR":
        raise AssertionError("GDT743 carrier promotion is not an open scalar")
    render = (
        f"Skalarstufe {source['level']} [Carrier={carrier.replace('_', '+')}; "
        f"Dimension offen; provisorischer R{coverage_length}-Lauf]"
    )
    if source["surface"] == "sain" and source["line_position"] == "FIRST":
        render += "; Eintrag"
    elif source["surface"] == "rain":
        render += "; Abschlussbezug" if source["line_position"] == "LAST" else "; interner Rückbezug"
    elif source["surface"] == "lain":
        render = "interne " + render
    elif source["surface"] == "skaiin" and source["line_position"] == "FIRST":
        render += "; Eintrag"
    return render


def renderer_patches(
    source_patches: list[dict[str, str]], contacts: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_dispatch: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in contacts:
        by_dispatch[str(row["dispatch_id"])].append(row)
    output: list[dict[str, object]] = []
    for source in source_patches:
        rows = by_dispatch.get(source["gdt739_dispatch_id"], [])
        carrier = source["gdt742_carrier_dispatch"]
        active = [row for row in rows if int(row["gdt743_carrier_role_retained"])]
        if carrier == "OPEN" and active:
            choices = {carrier_name(row) for row in active}
            if len(choices) != 1:
                raise AssertionError("ambiguous GDT743 carrier")
            carrier = next(iter(choices))
        render = source["gdt742_working_render_de"]
        if carrier != source["gdt742_carrier_dispatch"]:
            lengths = {
                int(row[f"{'left' if row['side'] == 'L' else 'right'}_requested_carrier_coverage_screened"])
                for row in active
            }
            if len(lengths) != 1:
                raise AssertionError("ambiguous GDT743 coverage length")
            render = render_open_scalar(source, carrier, next(iter(lengths)))
        changed = int(carrier != source["gdt742_carrier_dispatch"] or render != source["gdt742_working_render_de"])
        specific = int(
            int(source["axis_specific_dispatch_retained"])
            or carrier != "OPEN" or source["gdt742_state_mode"] == "PROCESS_RESULT"
        )
        output.append({
            "gdt743_patch_id": f"G743-R{len(output) + 1:04d}",
            **{field: source[field] for field in source},
            "gdt743_rule_trace": "PROVISIONAL_REQUESTED_CARRIER_COVERAGE_ANALOGY" if changed else "GDT742_RENDER_INHERITED",
            "gdt743_dimension_dispatch": source["gdt742_dimension_dispatch"],
            "gdt743_carrier_dispatch": carrier,
            "gdt743_state_mode": source["gdt742_state_mode"],
            "gdt743_working_render_de": render,
            "carrier_locally_bound_gdt743": int(carrier != "OPEN"),
            "specific_local_dispatch_gdt743": specific,
            "changed_from_gdt742": changed,
            "active_run_override_contacts": sum(int(row["requested_carrier_coverage_override"]) for row in rows),
            "dispatcher_uses_dispatch_id_or_locus_gdt743": 0,
        })
    return output


def candidate_adjudication(
    source_candidates: list[dict[str, str]], contacts: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for source in source_candidates:
        if source["gdt742_role_active"] == "1":
            continue
        contact = contacts[source["attachment_contact_id"]]
        role = source["candidate_role"]
        new_active = int(contact["gdt743_axis_role_retained"] if role == "AXIS" else contact["gdt743_carrier_role_retained"])
        if role == "CARRIER" and int(contact["requested_carrier_coverage_override"]):
            status = "PROMOTE_PROVISIONAL_COMPOSITE_RUN_CARRIER"
            reason = (
                "the requested PREPARATION candidate has a unique reader-screened R4 coverage run "
                "satisfying the >=3 gate; this exploratory licence combines a reverse H4 R1 analogy "
                "and, separately, an open full-carrier R2 relay, while the run gate excludes no R2 rival"
            )
        elif role == "AXIS" and int(contact["favored_partial_axis_intersection"]):
            status = "HOLD_FAVORED_INTERSECTION_LEAD"
            reason = (
                "the inherited HOT candidate equals the one-tag host-middle intersection; "
                "this conditional consistency does not license an axis"
            )
        else:
            status = "HOLD_OPEN_COLLISION"
            failures: list[str] = []
            if contact["middle_barrier"] != "OPEN":
                failures.append(f"middle barrier is {contact['middle_barrier']}")
            if role == "AXIS" and contact["axis_continuity"] == "PARTIAL":
                failures.append(f"singleton intersection {contact['intersection_axis_set']} does not receive renderer licence")
            if role == "CARRIER" and not int(contact["requested_carrier_coverage_override"]):
                failures.append("no unique requested-carrier coverage run satisfying the >=3 gate")
            reason = "; ".join(failures) or "the remaining role is not licensed by GDT743"
        output.append({
            "adjudication_id": f"G743-C{len(output) + 1:02d}",
            "gdt742_adjudication_id": source["adjudication_id"],
            "attachment_contact_id": source["attachment_contact_id"],
            "gdt739_dispatch_id": source["gdt739_dispatch_id"],
            "page": source["page"], "locus": source["locus"],
            "target_surface": source["target_surface"],
            "candidate_role": role,
            "gdt742_role_active": source["gdt742_role_active"],
            "gdt743_role_active": new_active,
            "changed_from_gdt742": int(new_active != int(source["gdt742_role_active"])),
            "gdt743_status": status,
            "intersection_axis_set": contact["intersection_axis_set"],
            "left_requested_carrier_coverage_screened": contact["left_requested_carrier_coverage_screened"],
            "right_requested_carrier_coverage_screened": contact["right_requested_carrier_coverage_screened"],
            "working_reason": reason,
            "renderer_license": new_active,
            "literal_plaintext_claimed": 0,
            "component_export_credit": 0,
        })
    return output


def focus_reviews(
    source_focus: list[dict[str, str]], candidates: list[dict[str, object]],
    patches: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    by_dispatch: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in candidates:
        by_dispatch[str(row["gdt739_dispatch_id"])].append(row)
    source_map = {row["gdt739_dispatch_id"]: row for row in source_focus}
    output: list[dict[str, object]] = []
    for dispatch_id in sorted(by_dispatch):
        source = source_map[dispatch_id]
        rows = by_dispatch[dispatch_id]
        if any(str(row["gdt743_status"]).startswith("PROMOTE") for row in rows):
            decision = "PROMOTE_CARRIER_ONLY_PROVISIONAL_COMPOSITE"
        elif any(row["gdt743_status"] == "HOLD_FAVORED_INTERSECTION_LEAD" for row in rows):
            decision = "HOLD_AXIS_WITH_FAVORED_INTERSECTION_LEAD"
        else:
            decision = "HOLD_OPEN_COLLISION"
        patch = patches[dispatch_id]
        output.append({
            "focus_id": f"G743-F{len(output) + 1:02d}",
            "gdt742_focus_id": source["focus_id"],
            "gdt739_dispatch_id": dispatch_id,
            "page": source["page"], "locus": source["locus"],
            "target_ordinal": source["target_ordinal"],
            "target_surface": source["target_surface"],
            "candidate_roles": "+".join(sorted(str(row["candidate_role"]) for row in rows)),
            "line_eva_cached": source["line_eva_cached"],
            "radius_two_frame_manuscript_order": source["radius_two_frame_manuscript_order"],
            "gdt742_target_render_de": patch["gdt742_working_render_de"],
            "gdt743_target_render_de": patch["gdt743_working_render_de"],
            "focus_decision": decision,
            "working_reason": " | ".join(str(row["working_reason"]) for row in rows),
            "reader_note": "cached line and target-level working audit only; no plaintext clause or word translation is implied",
            "new_page_or_transcription": 0,
        })
    return output


def physical_folio(page: str) -> str:
    digits = "".join(character for character in page[1:] if character.isdigit())
    return f"f{digits}" if digits else page


def edge_packet(
    candidates: list[dict[str, object]], contacts: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for candidate in candidates:
        if not int(candidate["changed_from_gdt742"]):
            continue
        contact = contacts[str(candidate["attachment_contact_id"])]
        output.append({
            "edge_id": f"G743E{len(output) + 1:03d}",
            "batch_id": "GDT743_REQUESTED_CARRIER_COVERAGE_ANALOGY",
            "page": contact["page"], "physical_folio": physical_folio(str(contact["page"])),
            "diagram_unit_id": "CACHED_TEXT_LINE",
            "pivot_visual_id": f"TARGET_TOKEN_{contact['target_ordinal']}",
            "pivot_locus": f"{contact['locus']}@{contact['target_ordinal']}",
            "target_visual_id": f"R2_HOST_TOKEN_{contact['neighbor_ordinal']}",
            "target_locus": f"{contact['locus']}@{contact['neighbor_ordinal']}",
            "relation_type": "REQUESTED_CARRIER_COVERAGE_ANALOGY",
            "direction_basis": "UNIQUE_READER_SCREENED_COVERAGE_GE3_ANALOGICALLY_OVERRIDES_FORMAL_SIDE_PRIOR",
            "ownership_basis": "FULL_REQUESTED_CARRIER_IN_MIDDLE_HOST_AND_NEXT_CELL",
            "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT743",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT743_BUILDER",
            "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "C_PROVISIONAL_COMPOSITE_ANALOGY",
            "ambiguity_state": "OCCURRENCE_SCOPED_WORKING_PROMOTION",
            "formal_access_state": "FORMAL_ACCESSED",
            "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_FORMAL_ATTACHMENT_EDGE",
        })
    return output


def reader_markdown(
    requested_runs: list[dict[str, object]], all_carrier_runs: list[dict[str, object]],
    axis_rows: list[dict[str, object]],
    candidates: list[dict[str, object]], focus: list[dict[str, object]],
    r2_rows: list[dict[str, object]], sensitivity: dict[str, list[str]],
) -> str:
    relaxed = sum(int(row["relaxed_reverse_full_carrier_trigger"]) for row in r2_rows)
    promoted = sum(int(row["requested_carrier_coverage_override"]) for row in r2_rows)
    excluded = sum(int(row["coverage_excludes_relaxed_trigger"]) for row in r2_rows)
    lines = [
        "# GDT743 run/intersection reader", "",
        "One occurrence receives an explicitly exploratory carrier-only renderer licence.",
        "The analogy combines a reverse-side H4 direct-contact pattern and, separately,",
        "a full open radius-two carrier relay. No previous positive contact combines both",
        "properties. H4 is an analyst-imposed direction prior, not a manuscript label;",
        "this is not independent historical confirmation or a word translation.", "",
        "## Decisive ablation: the coverage gate does not discriminate", "",
        f"The relaxed reverse/full-carrier R2 trigger selects {relaxed} row; after the",
        f"requested-carrier coverage gate it still selects {promoted}; exclusions by the",
        f"coverage gate: {excluded}. The run therefore does not solve the R2 collision or",
        "remove a false positive. D0075 is retained only as a provisional composite",
        "working assumption for the renderer.", "",
        "## Requested-carrier coverage comparator class", "",
        "`screened` means reader-exact, known, no retired-patient tag, no strict head,",
        "no second target and no composition credit. It does not mean semantically pure.", "",
        "| target | requested carrier | screened L | screened R | formal side | prior carrier |", "|---|---|---:|---:|---|---|",
    ]
    for row in requested_runs:
        if int(row["requested_carrier_ge3_qualifier"]):
            lines.append(
                f"| `{row['gdt739_dispatch_id']}` `{row['target_surface']}` | {row['requested_carrier_set']} | "
                f"{row['left_requested_carrier_coverage_screened']} | {row['right_requested_carrier_coverage_screened']} | "
                f"{row['formal_carrier_side']} | {row['gdt742_carrier_dispatch']} |"
            )
    lines.extend([
        "", "Three members were already carrier-bound: two direction-matching direct",
        "patterns and D0045, a reverse H4 R1 control. D0045 is not historical evidence,",
        "not an R2 positive and does not prove that an independently emitting middle",
        "cell may be crossed. D0075 is a unique four-cell PREPARATION-containment run",
        "satisfying the >=3 gate. Its contiguous exact-carrier-set prefix is only 2",
        "because d3 adds MATERIAL; excluding PROCESS cuts the screened prefix at d2;",
        "d4 carries CLOSE. D0075 survives PASS-only and CLOSE-delimiter variants, but",
        "disappears under exact-set, PROCESS and PROCESS+PASS exclusions.", "",
        "| sensitivity | qualifying IDs |", "|---|---|",
        f"| permissive requested-carrier coverage | {', '.join(sensitivity['base_requested_carrier_coverage_ge3_ids'])} |",
        f"| exact carrier-set prefix | {', '.join(sensitivity['exact_carrier_set_prefix_ge3_ids'])} |",
        f"| exclude PROCESS | {', '.join(sensitivity['exclude_process_ge3_ids'])} |",
        f"| exclude PASS | {', '.join(sensitivity['exclude_pass_ge3_ids'])} |",
        f"| exclude CLOSE | {', '.join(sensitivity['exclude_close_ge3_ids'])} |",
        f"| exclude PROCESS+PASS | {', '.join(sensitivity['exclude_process_pass_ge3_ids'])} |",
        f"| exclude PROCESS+PASS+CLOSE | {', '.join(sensitivity['exclude_process_pass_close_ge3_ids'])} |", "",
        "## Carrier-unconditioned coverage countercases", "",
        "Scanning PREPARATION, MATERIAL and PART independently over all 202 targets yields",
        "six qualifying target/carrier pairs. Two are hidden by requested-carrier",
        "conditioning and are shown explicitly.", "",
        "| target | scanned carrier | side/length | inherited request | request matches | prior carrier |", "|---|---|---|---|---:|---|",
    ])
    for row in all_carrier_runs:
        lines.append(
            f"| `{row['gdt739_dispatch_id']}` `{row['target_surface']}` | {row['candidate_carrier']} | "
            f"{row['coverage_unique_side']}/{row['coverage_screened']} | "
            f"{row['gdt739_requested_carrier_dispatch']} | {row['requested_candidate_matches_scan']} | "
            f"{row['gdt742_carrier_dispatch']} |"
        )
    lines.extend([
        "", "Coverage alone therefore cannot name the carrier. The requested carrier and",
        "favored axis are inherited model candidates derived before GDT743; neither the",
        "run nor the intersection names a manuscript field.", "", "## Remaining candidate roles", "",
        "| target | role | decision | intersection | screened requested coverage L/R |", "|---|---|---|---|---|",
    ])
    for row in candidates:
        lines.append(
            f"| `{row['gdt739_dispatch_id']}` `{row['target_surface']}` | {row['candidate_role']} | "
            f"{row['gdt743_status']} | {row['intersection_axis_set']} | "
            f"{row['left_requested_carrier_coverage_screened']}/{row['right_requested_carrier_coverage_screened']} |"
        )
    lines.extend(["", "## Three cached focus lines", ""])
    for row in focus:
        lines.extend([
            f"### {row['focus_id']} — {row['locus']}", "", f"`{row['line_eva_cached']}`", "",
            f"Frame: `{row['radius_two_frame_manuscript_order']}`", "",
            f"Working model render (not plaintext): **{row['gdt743_target_render_de']}** — {row['focus_decision']}", "",
        ])
    favored = [row for row in axis_rows if int(row["bilateral_two_by_two_favored_axis_support"])]
    lines.extend([
        "## HOT intersection lead", "",
        "The census is conditioned on each target's inherited favored-axis tag.",
        f"It has {len(axis_rows)} bilateral targets; {len(favored)} has screened two-by-two",
        "support. At D0040, HOT is the inherited candidate and the selected right frame",
        "has HOT as its only common quality tag; two model-tagged cells on each flank",
        "also contain HOT. This is conditional internal consistency for a HOT-only lead,",
        "not an independent axis discovery. The renderer remains open because the",
        "reverse partial-R2 projection has only this trigger.", "", "## Ceiling and pivot", "",
        "MATERIAL, PREPARATION, HOT and the German renderer are model tags, not decoded",
        "words. No component, lexeme, plaintext clause, ingredient, patient, species,",
        "disease, cure, unit, page, image or transcription is added. Attachment tuning",
        "now stops unless a genuinely new comparator appears; the next route moves to",
        "concrete recurrent whole-field candidates across multiple cached contexts.", "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    source_contacts = read_tsv(G742_ART / "CONTACT_103_ROLE_SEPARATION_DISPATCH.tsv")
    source_candidates = read_tsv(G742_ART / "CANDIDATE_8_ROLE_ADJUDICATION.tsv")
    source_patches = read_tsv(G742_ART / "TARGET_202_RENDERER_PATCH_V4.tsv")
    source_focus = read_tsv(G742_ART / "FOCUS_7_CACHED_LINE_REVIEW.tsv")
    dispatches = read_tsv(G739_ART / "DIMENSION_202_DISPATCH.tsv")
    windows = read_tsv(G739_ART / "WINDOW_202_TOKEN_AUDIT.tsv")
    source_decks = (source_contacts, source_candidates, source_patches, source_focus, dispatches, windows)
    if any(
        row.get("page", "").startswith("f84") or row.get("locus", "").startswith("f84")
        for deck in source_decks for row in deck
    ):
        raise AssertionError("sealed page entered GDT743")
    if (
        len(source_contacts) != 103 or len(source_candidates) != 8
        or len(source_patches) != 202 or len(dispatches) != 202 or len(windows) != 1373
        or len({row["attachment_contact_id"] for row in source_contacts}) != 103
        or len({row["gdt739_dispatch_id"] for row in source_patches}) != 202
        or len({row["dispatch_id"] for row in dispatches}) != 202
        or len({row["window_id"] for row in windows}) != 1373
    ):
        raise AssertionError("GDT743 source boundary or key uniqueness changed")

    patch_map = {row["gdt739_dispatch_id"]: row for row in source_patches}
    target_coverages = target_coverage_features(dispatches, windows, patch_map)
    run_map = {str(row["gdt739_dispatch_id"]): row for row in target_coverages}
    all_carrier_runs = unconditional_carrier_coverage_census(dispatches, windows, patch_map)
    sensitivity = coverage_sensitivity(target_coverages)
    r2 = r2_dispatch(source_contacts, run_map)
    r2_map = {str(row["attachment_contact_id"]): row for row in r2}
    candidates = candidate_adjudication(source_candidates, r2_map)
    patches = renderer_patches(source_patches, r2)
    new_patch_map = {str(row["gdt739_dispatch_id"]): row for row in patches}
    focus = focus_reviews(source_focus, candidates, new_patch_map)
    requested_runs = [
        {
            **row,
            "requested_coverage_census_id": f"G743-L{index:02d}",
            "requested_carrier_ge3_qualifier": int(row["requested_carrier_ge3_unique_side"] != "NONE"),
        }
        for index, row in enumerate(
            (
                row for row in target_coverages
                if max(
                    int(row["left_requested_carrier_coverage_raw"]),
                    int(row["right_requested_carrier_coverage_raw"]),
                ) >= 3
            ),
            start=1,
        )
    ]
    axis_rows = [
        {**row, "axis_census_id": f"G743-A{index:02d}"}
        for index, row in enumerate((row for row in target_coverages if int(row["bilateral_favored_axis_support"])), start=1)
    ]
    edges = edge_packet(candidates, r2_map)
    reader = reader_markdown(
        requested_runs, all_carrier_runs, axis_rows, candidates, focus, r2, sensitivity,
    )

    write_tsv(
        output_dir / "TARGET_202_REQUESTED_CARRIER_COVERAGE_FEATURES.tsv",
        target_coverages, target_coverages[0].keys(),
    )
    write_tsv(output_dir / "R2_41_EXTENSION_DISPATCH.tsv", r2, r2[0].keys())
    write_tsv(
        output_dir / "RUN_8_REQUESTED_CARRIER_COVERAGE_CENSUS.tsv",
        requested_runs, requested_runs[0].keys(),
    )
    write_tsv(
        output_dir / "CARRIER_6_UNCONDITIONED_COVERAGE_CENSUS.tsv",
        all_carrier_runs, all_carrier_runs[0].keys(),
    )
    write_tsv(
        output_dir / "AXIS_5_INHERITED_FAVORED_CENSUS.tsv",
        axis_rows, axis_rows[0].keys(),
    )
    write_tsv(output_dir / "CANDIDATE_4_REMAINING_ROLE_ADJUDICATION.tsv", candidates, candidates[0].keys())
    write_tsv(output_dir / "TARGET_202_RENDERER_PATCH_V5.tsv", patches, patches[0].keys())
    write_tsv(output_dir / "FOCUS_3_EXTENSION_REVIEW.tsv", focus, focus[0].keys())
    write_tsv(output_dir / "GDT743_GDT388_RUN_OVERRIDE_EDGE_PACKET.tsv", edges, edges[0].keys())
    (output_dir / "GDT743_RUN_INTERSECTION_READER.md").write_text(reader, encoding="utf-8")

    artifact_hashes = {
        str(BASE_REL / "artifacts" / name): sha256(output_dir / name)
        for name in OUTPUT_NAMES
    }
    result = {
        "schema": "GDT743_R2_RUN_INTERSECTION_ADJUDICATION_V1",
        "status": STATUS,
        "scope": {
            "inherited_allowlist_pages": 179, "renderer_positions": len(patches),
            "window_rows": len(windows), "radius_two_contacts": len(r2),
            "remaining_candidate_roles_entered_post_decision": len(candidates),
            "focus_cached_lines": len(focus), "new_pages_used": 0,
            "f84_used": False, "f84r_used": False,
        },
        "requested_carrier_coverage_census": {
            "raw_ge3_targets": len(requested_runs),
            "screened_unique_ge3_targets": sum(int(row["requested_carrier_ge3_qualifier"]) for row in requested_runs),
            "screened_unique_previously_carrier_bound": sum(int(row["requested_carrier_ge3_qualifier"]) and int(row["current_carrier_bound"]) for row in requested_runs),
            "unconditioned_target_carrier_pairs": len(all_carrier_runs),
            "unconditioned_request_mismatches": sum(not int(row["requested_candidate_matches_scan"]) for row in all_carrier_runs),
            "new_run_override_contacts": sum(int(row["requested_carrier_coverage_override"]) for row in r2),
            "new_run_override_roles": sum(int(row["changed_from_gdt742"]) for row in candidates),
        },
        "r2_ablation": {
            "relaxed_reverse_full_carrier_triggers": sum(int(row["relaxed_reverse_full_carrier_trigger"]) for row in r2),
            "post_coverage_gate_triggers": sum(int(row["requested_carrier_coverage_override"]) for row in r2),
            "excluded_by_coverage_gate": sum(int(row["coverage_excludes_relaxed_trigger"]) for row in r2),
        },
        "sensitivity": sensitivity,
        "axis_census": {
            "bilateral_favored_axis_targets": len(axis_rows),
            "bilateral_two_by_two_targets": sum(int(row["bilateral_two_by_two_favored_axis_support"]) for row in axis_rows),
            "favored_partial_r2_leads": sum(int(row["favored_partial_axis_intersection"]) for row in r2),
            "new_axis_roles": sum(int(row["axis_changed_from_gdt742"]) for row in r2),
        },
        "roles": {
            "gdt742_active_r2_roles": sum(int(row["gdt742_axis_role_retained"]) + int(row["gdt742_carrier_role_retained"]) for row in r2),
            "gdt743_active_r2_roles": sum(int(row["gdt743_axis_role_retained"]) + int(row["gdt743_carrier_role_retained"]) for row in r2),
            "remaining_open_candidate_roles": sum(not int(row["gdt743_role_active"]) for row in candidates),
            "remaining_open_candidate_targets": len({row["gdt739_dispatch_id"] for row in candidates if not int(row["gdt743_role_active"])}),
        },
        "renderer": {
            "axis_specific_occurrences": sum(int(row["axis_specific_dispatch_retained"]) for row in patches),
            "carrier_bound_occurrences": sum(int(row["carrier_locally_bound_gdt743"]) for row in patches),
            "specific_occurrences": sum(int(row["specific_local_dispatch_gdt743"]) for row in patches),
            "fully_open_occurrences": sum(not int(row["specific_local_dispatch_gdt743"]) for row in patches),
            "changed_from_gdt742": sum(int(row["changed_from_gdt742"]) for row in patches),
        },
        "edge_intake": {"expected_status": "INVALID_PACKET", "packet_rows": len(edges), "score_ready": False},
        "claims": {
            "new_axes": 0, "components_exported": 0, "lexemes_identified": 0,
            "plaintext_clauses": 0, "literal_patients_or_species": 0,
            "unseen_forms_licensed": 0, "new_pages": 0,
        },
        "next_route": "CONCRETE_RECURRENT_WHOLE_FIELD_BRIDGE_ACROSS_MULTIPLE_CACHED_CONTEXTS",
        "artifact_hashes": artifact_hashes,
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": STATUS,
        "requested_carrier_coverage_census": result["requested_carrier_coverage_census"],
        "r2_ablation": result["r2_ablation"],
        "axis_census": result["axis_census"], "renderer": result["renderer"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
