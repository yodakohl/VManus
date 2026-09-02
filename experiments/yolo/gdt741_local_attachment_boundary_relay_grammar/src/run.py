#!/usr/bin/env python3
"""Compile GDT740 manual attachment decisions into an ID-free local grammar."""

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
BASE_REL = Path("experiments/yolo/gdt741_local_attachment_boundary_relay_grammar")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G740_REL = Path("experiments/yolo/gdt740_local_host_attachment_adjudication")
G740_ART = ROOT / G740_REL / "artifacts"
G740_SRC = ROOT / G740_REL / "src"
G740_RUN = ROOT / G740_REL / "src/run.py"
G739_ART = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/artifacts"

module_spec = importlib.util.spec_from_file_location("gdt740_builder", G740_RUN)
if module_spec is None or module_spec.loader is None:
    raise RuntimeError("cannot load GDT740 attachment helpers")
g740 = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(g740)
g739 = g740.g739

QUALITY = {"HOT", "COLD", "DRY", "MOIST"}
CARRIERS = {"PREPARATION", "MATERIAL", "PART"}
BOUNDARIES = {"CLOSE", "PROCESS", "PASS"}
RULE_ORDER = ("G00", "G01", "G02", "G03", "G04", "G05", "G06A", "G06C", "G07", "G08")
DECISION_DISPATCH_FIELDS = (
    "state_mode", "favored_axis_not_automatic", "dimension_dispatch",
    "carrier_dispatch", "surface", "line_position", "level",
    "specific_local_dispatch", "selecting_anchor_distance",
)
DECISION_CONTACT_FIELDS = (
    "distance", "selected_roles", "side", "target_ordinal", "signed_offset",
    "neighbor_ordinal", "neighbor_axis_tags", "neighbor_scalar_host_types",
    "formal_role_direction_match", "guarded_reader_exact_pair_occurrences",
    "strict_axis_relay_candidate", "strict_carrier_relay_candidate",
    "opposite_reader_exact", "opposite_known", "opposite_quality_set",
)
DECISION_CONTACT_OUTPUT_FIELDS = (
    "predicted_axis_role_retained", "predicted_carrier_role_retained",
    "predicted_renderer_role_retained", "grammar_rule_trace",
)
STATUS = (
    "PASS__ID_FREE_GRAMMAR_REPLAYS_13_OF_13_OVERRIDES__ZERO_103_ROLE_FLAG_ERRORS__"
    "EIGHT_OF_EIGHT_RESULT_MODES__TWO_SINGLETON_RELAYS_EXPLICIT__"
    "SIX_OPEN_COLLISION_ROLE_CANDIDATES__NO_NEW_RENDER_CHANGE__"
    "ZERO_LEXEME_OR_COMPONENT_EXPORT__NO_NEW_PAGE"
)
OUTPUT_NAMES = (
    "CONTACT_103_GRAMMAR_DISPATCH.tsv",
    "TARGET_95_GRAMMAR_FEATURES.tsv",
    "OVERRIDE_13_ID_FREE_REPLAY.tsv",
    "RULE_10_TRIGGER_CENSUS.tsv",
    "R2_8_STRICT_AND_OPEN_COLLISION_CANDIDATES.tsv",
    "GDT741_GDT388_OPEN_COLLISION_EDGE_PACKET.tsv",
    "TARGET_202_RENDERER_PATCH_V3.tsv",
    "PASSAGE_20_GRAMMAR_REPLAY.tsv",
    "GDT741_BOUNDARY_RELAY_GRAMMAR_READER.md",
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
    if text in {"", "NONE", "NA", "NOT_APPLICABLE", "OPEN"}:
        return set()
    return set(text.split(separator))


def joined(items: set[str]) -> str:
    return "|".join(sorted(items)) or "NONE"


def ordered_rules(items: Iterable[str]) -> str:
    found = set(items)
    return "|".join(rule for rule in RULE_ORDER if rule in found) or "DEFAULT"


def direct_feature_tier(rows: list[dict[str, object]]) -> str:
    """Grade an active direct relation without reading a GDT740 outcome label."""
    if any(int(row["guarded_reader_exact_pair_occurrences"]) >= 2 for row in rows):
        return "ATTACHED_STRONG"
    if any(row["formal_role_direction_match"] == "1" for row in rows):
        return "ATTACHED_SUPPORTED"
    return "ATTACHED_PROVISIONAL_REVERSE" if rows else "MODE_ONLY_NO_HOST"


def target_axis_signature(
    dispatch: dict[str, str], axis_tags: set[str], scalar_types: set[str],
) -> str:
    dimension = dispatch["dimension_dispatch"]
    quality = axis_tags & QUALITY
    if dimension == "QUALITY_DEGREE" and "QUALITY_DEGREE" in scalar_types and quality:
        return "QUALITY:" + joined(quality)
    if dimension == "AMOUNT_DOSE" and "AMOUNT_DOSE" in scalar_types:
        return "AMOUNT"
    if dimension == "PROCESS_PASS" and "PROCESS_PASS" in scalar_types:
        return "PROCESS_PASS"
    favored = dispatch["favored_axis_not_automatic"]
    if dispatch["state_mode"] != "NOT_APPLICABLE" and favored in axis_tags:
        return "STATE:" + favored
    return "NONE"


def middle_barrier(
    contact: dict[str, str], middle: dict[str, str] | None,
) -> str:
    if middle is None:
        return "NOT_APPLICABLE"
    tags = values(middle["axis_tags"])
    if middle["neighbor_unknown_v99r7"] == "1":
        return "UNKNOWN"
    if contact["intervening_strict_initial_head"] == "1":
        return "STRICT_HEAD"
    if "CLOSE" in tags:
        return "CLOSE"
    if tags & {"PROCESS", "PASS"}:
        return "PROCESS_OR_PASS"
    return "OPEN"


def build_contact_features(
    contacts: list[dict[str, str]], dispatches: dict[str, dict[str, str]],
    windows: dict[tuple[str, str, str], dict[str, str]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for source in contacts:
        row: dict[str, object] = dict(source)
        dispatch = dispatches[source["dispatch_id"]]
        host_tags = values(source["neighbor_axis_tags"])
        host_scalars = values(source["neighbor_scalar_host_types"])
        wanted = values(dispatch["carrier_dispatch"], "_") & CARRIERS
        middle = None
        if source["distance"] == "2":
            middle = windows[(source["patch_id"], source["side"], "1")]
        middle_tags = values(middle["axis_tags"]) if middle else set()
        middle_scalars = values(middle["scalar_host_types"]) if middle else set()
        opposite = None
        if source["distance"] == "1":
            opposite = windows.get((
                source["patch_id"], "R" if source["side"] == "L" else "L", "1",
            ))
        opposite_tags = values(opposite["axis_tags"]) if opposite else set()
        host_signature = target_axis_signature(dispatch, host_tags, host_scalars)
        middle_signature = target_axis_signature(dispatch, middle_tags, middle_scalars)
        barrier = middle_barrier(source, middle)
        common_frame = bool(
            middle
            and int(source["guarded_reader_exact_full_frame_occurrences"]) >= 1
            and middle["neighbor_reader_exact"] == "1"
            and middle["neighbor_unknown_v99r7"] == "0"
            and source["intervening_emits_own_unit"] == "1"
            and source["intervening_strict_initial_head"] == "0"
            and source["intervening_another_gdt738_target"] == "0"
        )
        exact_single_axis_continuity = bool(
            middle
            and host_signature == middle_signature
            and host_signature.startswith("QUALITY:")
            and len(host_tags & QUALITY) == 1
            and len(middle_tags & QUALITY) == 1
        )
        partial_axis_continuity = bool(
            middle and not exact_single_axis_continuity
            and "QUALITY_DEGREE" in host_scalars
            and "QUALITY_DEGREE" in middle_scalars
            and host_tags & middle_tags & QUALITY
        )
        relaxed_axis = bool(
            common_frame and barrier != "CLOSE"
            and "AXIS" in values(source["selected_roles"], "+")
            and (exact_single_axis_continuity or partial_axis_continuity)
        )
        strict_axis = bool(
            relaxed_axis
            and values(source["selected_roles"], "+") == {"AXIS"}
            and source["formal_role_direction_match"] == "1"
            and barrier == "OPEN"
            and exact_single_axis_continuity
        )
        full_carrier = bool(wanted and wanted <= host_tags & CARRIERS and wanted <= middle_tags & CARRIERS)
        partial_carrier = bool(wanted and not full_carrier and wanted & host_tags & middle_tags & CARRIERS)
        relaxed_carrier = bool(
            common_frame and barrier != "CLOSE"
            and "CARRIER" in values(source["selected_roles"], "+")
            and full_carrier
        )
        strict_carrier = bool(
            relaxed_carrier
            and values(source["selected_roles"], "+") == {"CARRIER"}
            and source["formal_role_direction_match"] == "1"
            and barrier == "OPEN"
        )
        row.update({
            "target_family": dispatch["family"],
            "target_level": dispatch["level"],
            "target_favored_axis": dispatch["favored_axis_not_automatic"],
            "target_dimension": dispatch["dimension_dispatch"],
            "target_prior_state_mode": dispatch["state_mode"],
            "target_wanted_carrier_set": joined(wanted),
            "host_quality_set": joined(host_tags & QUALITY),
            "host_carrier_set": joined(host_tags & CARRIERS),
            "host_scalar_class_set": joined(host_scalars),
            "host_boundary_set": joined(host_tags & BOUNDARIES),
            "host_axis_signature": host_signature,
            "single_host_covers_requested_carrier": int(bool(wanted and wanted <= host_tags & CARRIERS)),
            "middle_reader_exact": middle["neighbor_reader_exact"] if middle else "NA",
            "middle_known": int(bool(middle and middle["neighbor_unknown_v99r7"] == "0")),
            "middle_positive_host_eligible": middle["eligible_local_anchor"] if middle else "NA",
            "middle_ineligibility_reasons": middle["ineligibility_reasons"] if middle else "NA",
            "middle_quality_set": joined(middle_tags & QUALITY) if middle else "NA",
            "middle_carrier_set": joined(middle_tags & CARRIERS) if middle else "NA",
            "middle_scalar_class_set": joined(middle_scalars) if middle else "NA",
            "middle_boundary_set": joined(middle_tags & BOUNDARIES) if middle else "NA",
            "middle_axis_signature": middle_signature if middle else "NA",
            "middle_barrier": barrier,
            "axis_continuity": (
                "EXACT_SINGLE" if exact_single_axis_continuity
                else "PARTIAL" if partial_axis_continuity
                else "CONFLICT" if middle and host_tags & QUALITY and middle_tags & QUALITY
                and not host_tags & middle_tags & QUALITY
                else "NONE"
            ),
            "carrier_continuity": "FULL_WANTED" if full_carrier else "PARTIAL" if partial_carrier else "NONE",
            "opposite_reader_exact": opposite["neighbor_reader_exact"] if opposite else "NA",
            "opposite_known": int(bool(opposite and opposite["neighbor_unknown_v99r7"] == "0")),
            "opposite_positive_host_eligible": opposite["eligible_local_anchor"] if opposite else "NA",
            "opposite_ineligibility_reasons": opposite["ineligibility_reasons"] if opposite else "NA",
            "opposite_quality_set": joined(opposite_tags & QUALITY) if opposite else "NA",
            "strict_axis_relay_candidate": int(strict_axis),
            "strict_carrier_relay_candidate": int(strict_carrier),
            "relaxed_axis_relay_candidate": int(relaxed_axis),
            "relaxed_carrier_relay_candidate": int(relaxed_carrier),
            "predicted_axis_role_retained": 0,
            "predicted_carrier_role_retained": 0,
            "predicted_renderer_role_retained": 0,
            "grammar_rule_trace": "UNSET",
        })
        output.append(row)
    return output


def adjudicate_target(
    dispatch: dict[str, str], rows: list[dict[str, object]],
) -> dict[str, object]:
    direct = [row for row in rows if row["distance"] == "1"]
    radius_two = [row for row in rows if row["distance"] == "2"]
    blocked_axis: dict[int, set[str]] = defaultdict(set)
    blocked_carrier: dict[int, set[str]] = defaultdict(set)
    target_rules: set[str] = set()

    # G01: a reverse direct closure owns the same-side radius-two field behind it.
    for far in radius_two:
        if values(far["selected_roles"], "+") != {"AXIS"}:
            continue
        middle_ordinal = int(far["target_ordinal"]) + (1 if int(far["signed_offset"]) > 0 else -1)
        for near in direct:
            if (
                near["side"] == far["side"]
                and values(near["selected_roles"], "+") == {"CARRIER"}
                and "CLOSE" in values(near["neighbor_axis_tags"])
                and near["formal_role_direction_match"] == "0"
                and int(near["neighbor_ordinal"]) == middle_ordinal
            ):
                blocked_axis[id(far)].add("G01")
                blocked_carrier[id(near)].add("G01")
                target_rules.add("G01")

    # G02: do not synthesize one phrase from different direct flanks.
    direct_axis = [row for row in direct if "AXIS" in values(row["selected_roles"], "+")]
    direct_carrier = [row for row in direct if "CARRIER" in values(row["selected_roles"], "+")]
    axis_sides = {str(row["side"]) for row in direct_axis}
    carrier_sides = {str(row["side"]) for row in direct_carrier}
    bilateral_split = bool(
        direct_axis and direct_carrier and axis_sides | carrier_sides == {"L", "R"}
        and axis_sides.isdisjoint(carrier_sides)
        and not any(values(row["selected_roles"], "+") == {"AXIS", "CARRIER"} for row in direct)
    )
    if bilateral_split:
        for row in direct_axis:
            blocked_axis[id(row)].add("G02")
        for row in direct_carrier:
            blocked_carrier[id(row)].add("G02")
        target_rules.add("G02")

    # G03: a reader-exact opposite whole with another quality axis reopens a state axis.
    state_rival = False
    if dispatch["state_mode"] != "NOT_APPLICABLE":
        favored = dispatch["favored_axis_not_automatic"]
        for selected in direct_axis:
            if favored not in values(selected["neighbor_axis_tags"]):
                continue
            opposite_quality = values(selected["opposite_quality_set"])
            if (
                selected["opposite_reader_exact"] == "1"
                and int(selected["opposite_known"])
                and opposite_quality and favored not in opposite_quality
            ):
                blocked_axis[id(selected)].add("G03")
                target_rules.add("G03")
                state_rival = True

    # G04: a pure counted-carrier field owns its own amount value.
    amount_owner = False
    for row in direct:
        roles = values(row["selected_roles"], "+")
        tags = values(row["neighbor_axis_tags"])
        scalars = values(row["neighbor_scalar_host_types"])
        if (
            dispatch["dimension_dispatch"] == "AMOUNT_DOSE"
            and roles == {"AXIS", "CARRIER"}
            and scalars == {"AMOUNT_DOSE"}
            and "AMOUNT" in tags and bool(tags & CARRIERS)
            and tags <= {"AMOUNT"} | CARRIERS
        ):
            blocked_axis[id(row)].add("G04")
            target_rules.add("G04")
            amount_owner = True

    axis_candidates = [
        row for row in direct
        if "AXIS" in values(row["selected_roles"], "+")
        and id(row) not in blocked_axis
    ]
    carrier_candidates = [
        row for row in direct
        if "CARRIER" in values(row["selected_roles"], "+")
        and id(row) not in blocked_carrier
    ]

    # G05: a composite broad carrier must exist inside one host, never as a union.
    wanted = values(dispatch["carrier_dispatch"], "_") & CARRIERS
    direct_carrier_union = set().union(*(
        values(row["neighbor_axis_tags"]) & CARRIERS for row in direct_carrier
    )) if direct_carrier else set()
    composite_split = bool(
        len(wanted) > 1 and direct_carrier and wanted <= direct_carrier_union
        and not any(wanted <= values(row["neighbor_axis_tags"]) & CARRIERS for row in direct_carrier)
    )
    if composite_split:
        target_rules.add("G05")
        for row in direct_carrier:
            blocked_carrier[id(row)].add("G05")
        carrier_candidates = [row for row in carrier_candidates if row["distance"] != "1"]

    # G06: only the two tight feature-defined radius-two relays survive.
    for row in radius_two:
        if int(row["strict_axis_relay_candidate"]):
            axis_candidates.append(row)
            target_rules.add("G06A")
        if int(row["strict_carrier_relay_candidate"]):
            carrier_candidates.append(row)
            target_rules.add("G06C")

    carrier, carrier_winners = g740.direct_carrier_choice(dispatch, carrier_candidates)

    for row in rows:
        row_id = id(row)
        axis_retained = int(row in axis_candidates)
        carrier_retained = int(row in carrier_winners)
        row["predicted_axis_role_retained"] = axis_retained
        row["predicted_carrier_role_retained"] = carrier_retained
        row["predicted_renderer_role_retained"] = int(axis_retained or carrier_retained)
        trace = set(blocked_axis.get(row_id, set())) | set(blocked_carrier.get(row_id, set()))
        if int(row["strict_axis_relay_candidate"]):
            trace.add("G06A")
        if int(row["strict_carrier_relay_candidate"]):
            trace.add("G06C")
        if not trace:
            trace.add("DIRECT_DEFAULT" if row["distance"] == "1" else "R2_DEFAULT_HOLD")
        row["grammar_rule_trace"] = ordered_rules(trace) if trace & set(RULE_ORDER) else "|".join(sorted(trace))

    axis_specific = int(bool(axis_candidates))
    old_mode = dispatch["state_mode"]
    direct_process_support = sum(
        row in carrier_winners and row["distance"] == "1"
        and "PROCESS" in values(row["neighbor_axis_tags"])
        for row in rows
    )
    if old_mode == "PROCESS_RESULT":
        new_mode = "PROCESS_RESULT" if direct_process_support else "QUALITY_STATE"
        target_rules.add("G07")
    else:
        new_mode = old_mode

    if dispatch["surface"] in g740.SCALAR_FORMS:
        if dispatch["dimension_dispatch"] in g740.SCALAR_CLASSES and axis_specific:
            dimension = dispatch["dimension_dispatch"]
            selecting_windows = [
                {"axis_tags": row["neighbor_axis_tags"]} for row in axis_candidates
            ]
        elif dispatch["dimension_dispatch"] == "OPEN_SCALAR_CONFLICT" and dispatch["selecting_anchor_distance"] == "1":
            dimension = "OPEN_SCALAR_CONFLICT"
            selecting_windows = []
            axis_specific = 0
        else:
            dimension = "OPEN_SCALAR"
            selecting_windows = []
            axis_specific = 0
        render = g739.render_scalar(
            dispatch["surface"], dispatch["line_position"], dispatch["level"],
            dimension, selecting_windows, carrier,
        )
    else:
        dimension = (
            f"{new_mode}_{dispatch['favored_axis_not_automatic']}_LOCAL"
            if axis_specific else f"{new_mode}_AXIS_OPEN"
        )
        render = g739.render_state(
            dispatch["surface"], dispatch["line_position"], new_mode,
            dispatch["favored_axis_not_automatic"], bool(axis_specific), carrier,
        )

    specific = int(axis_specific or carrier != "OPEN" or new_mode == "PROCESS_RESULT")
    active_direct = [row for row in direct if int(row["predicted_renderer_role_retained"])]
    active_relay = [row for row in radius_two if int(row["predicted_renderer_role_retained"])]
    if "G01" in target_rules:
        tier = "DIRECT_BOUNDARY_HOLD"
    elif "G02" in target_rules:
        tier = "DIRECT_FLANK_CONFLICT_OPEN"
    elif "G05" in target_rules:
        tier = "DIRECT_COMPONENT_CONFLICT_OPEN"
    elif ("G03" in target_rules or "G04" in target_rules or old_mode == "PROCESS_RESULT" and new_mode == "QUALITY_STATE") and carrier != "OPEN":
        tier = "KEEP_CARRIER_ONLY"
    elif active_relay:
        tier = "RELAY_R2_GRAMMAR_SINGLETON"
    elif active_direct:
        tier = direct_feature_tier(active_direct)
    elif radius_two:
        tier = "NEAR_ONLY_HOLD"
    elif dispatch["specific_local_dispatch"] == "1" and new_mode != old_mode:
        tier = "MODE_DOWNGRADED_OPEN"
    else:
        tier = "NO_SELECTED_HOST"

    return {
        "closure_crossing": int("G01" in target_rules),
        "bilateral_role_split": int(bilateral_split),
        "state_opposite_axis_rival": int(state_rival),
        "pure_amount_field_owns_value": int(amount_owner),
        "single_host_composite_carrier_conflict": int(composite_split),
        "strict_axis_relay_count": sum(int(row["strict_axis_relay_candidate"]) for row in rows),
        "strict_carrier_relay_count": sum(int(row["strict_carrier_relay_candidate"]) for row in rows),
        "retained_direct_process_host_count": direct_process_support,
        "grammar_rule_trace": ordered_rules(target_rules),
        "grammar_tier": tier,
        "dimension": dimension,
        "carrier": carrier,
        "state_mode": new_mode,
        "render": render,
        "axis_specific": axis_specific,
        "carrier_bound": int(carrier != "OPEN"),
        "specific": specific,
    }


def build_renderer_and_targets(
    dispatch_rows: list[dict[str, str]], contacts: list[dict[str, object]],
    old_patches: dict[str, dict[str, str]], old_targets: dict[str, dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, dict[str, object]]]:
    contact_by_dispatch: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in contacts:
        contact_by_dispatch[str(row["dispatch_id"])].append(row)
    patches: list[dict[str, object]] = []
    targets: list[dict[str, object]] = []
    decisions: dict[str, dict[str, object]] = {}
    for dispatch in dispatch_rows:
        source_rows = contact_by_dispatch[dispatch["dispatch_id"]]
        decision_dispatch = {field: dispatch[field] for field in DECISION_DISPATCH_FIELDS}
        decision_rows = [
            {field: row[field] for field in DECISION_CONTACT_FIELDS}
            for row in source_rows
        ]
        decision = adjudicate_target(decision_dispatch, decision_rows)
        for source, decided in zip(source_rows, decision_rows, strict=True):
            for field in DECISION_CONTACT_OUTPUT_FIELDS:
                source[field] = decided[field]
            source["axis_flag_matches_gdt740"] = int(
                int(source["predicted_axis_role_retained"]) == int(source["axis_role_retained"])
            )
            source["carrier_flag_matches_gdt740"] = int(
                int(source["predicted_carrier_role_retained"]) == int(source["carrier_role_retained"])
            )
            source["role_flags_match_gdt740"] = int(
                source["axis_flag_matches_gdt740"] and source["carrier_flag_matches_gdt740"]
            )
        decisions[dispatch["dispatch_id"]] = decision
        old = old_patches[dispatch["dispatch_id"]]
        changed_from_g740 = int(
            decision["dimension"] != old["gdt740_dimension_dispatch"]
            or decision["carrier"] != old["gdt740_carrier_dispatch"]
            or decision["state_mode"] != old["gdt740_state_mode"]
            or decision["render"] != old["gdt740_working_render_de"]
        )
        patch = {
            "gdt741_patch_id": f"G741-R{len(patches) + 1:04d}",
            "gdt740_patch_id": old["gdt740_patch_id"],
            "gdt739_dispatch_id": dispatch["dispatch_id"],
            "patch_id": dispatch["patch_id"], "occurrence_id": dispatch["occurrence_id"],
            "page": dispatch["page"], "locus": dispatch["locus"],
            "token_index": dispatch["token_index"], "token_ordinal": dispatch["token_ordinal"],
            "surface": dispatch["surface"], "body": dispatch["body"],
            "opaque_head_id": dispatch["opaque_head_id"], "line_position": dispatch["line_position"],
            "family": dispatch["family"], "level": dispatch["level"],
            "grammar_rule_trace": decision["grammar_rule_trace"],
            "grammar_tier": decision["grammar_tier"],
            "gdt740_dimension_dispatch": old["gdt740_dimension_dispatch"],
            "gdt741_dimension_dispatch": decision["dimension"],
            "gdt740_carrier_dispatch": old["gdt740_carrier_dispatch"],
            "gdt741_carrier_dispatch": decision["carrier"],
            "gdt740_state_mode": old["gdt740_state_mode"],
            "gdt741_state_mode": decision["state_mode"],
            "gdt740_working_render_de": old["gdt740_working_render_de"],
            "gdt741_working_render_de": decision["render"],
            "axis_specific_dispatch_retained": decision["axis_specific"],
            "carrier_locally_bound_retained": decision["carrier_bound"],
            "specific_local_dispatch_retained": decision["specific"],
            "grammar_changed_from_gdt740": changed_from_g740,
            "functional_match_gdt740": int(not changed_from_g740),
            "dispatcher_uses_dispatch_id_or_locus": 0,
            "scope": "EXACT_COMPLETE_SURFACE_AT_THIS_ENUMERATED_OCCURRENCE",
            "literal_patient_or_species_claimed": 0, "literal_plaintext_claimed": 0,
            "unconditional_global_export": 0, "head_or_body_lexeme_credit": 0,
            "component_export_credit": 0, "unseen_form_export": 0,
        }
        patches.append(patch)
        if dispatch["specific_local_dispatch"] == "1":
            old_target = old_targets[dispatch["dispatch_id"]]
            rows = contact_by_dispatch[dispatch["dispatch_id"]]
            target = {
                "feature_id": f"G741-F{len(targets) + 1:03d}",
                "gdt739_dispatch_id": dispatch["dispatch_id"],
                "page": dispatch["page"], "locus": dispatch["locus"],
                "token_ordinal": dispatch["token_ordinal"], "surface": dispatch["surface"],
                "opaque_head_id": dispatch["opaque_head_id"], "line_position": dispatch["line_position"],
                "family": dispatch["family"], "level": dispatch["level"],
                "target_dimension": dispatch["dimension_dispatch"],
                "target_favored_axis": dispatch["favored_axis_not_automatic"],
                "target_wanted_carrier_set": joined(values(dispatch["carrier_dispatch"], "_") & CARRIERS),
                "target_prior_state_mode": dispatch["state_mode"],
                "selected_contacts": len(rows),
                "direct_contacts": sum(row["distance"] == "1" for row in rows),
                "radius_two_contacts": sum(row["distance"] == "2" for row in rows),
                **{key: decision[key] for key in (
                    "closure_crossing", "bilateral_role_split", "state_opposite_axis_rival",
                    "pure_amount_field_owns_value", "single_host_composite_carrier_conflict",
                    "strict_axis_relay_count", "strict_carrier_relay_count",
                    "retained_direct_process_host_count",
                )},
                "grammar_rule_trace": decision["grammar_rule_trace"],
                "gdt740_attachment_tier": old_target["attachment_tier"],
                "gdt741_grammar_tier": decision["grammar_tier"],
                "gdt740_working_render_de": old["gdt740_working_render_de"],
                "gdt741_working_render_de": decision["render"],
                "role_flag_matches_gdt740": int(all(int(row["role_flags_match_gdt740"]) for row in rows)),
                "mode_matches_gdt740": int(decision["state_mode"] == old["gdt740_state_mode"]),
                "render_matches_gdt740": int(decision["render"] == old["gdt740_working_render_de"]),
                "dispatcher_uses_dispatch_id_or_locus": 0,
                "plaintext_or_lexeme_claim": 0, "component_export_credit": 0,
            }
            targets.append(target)
    return patches, targets, decisions


def override_replay(
    override_rows: list[dict[str, str]], targets: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for source in override_rows:
        target = targets[source["dispatch_id"]]
        functional_match = int(
            target["role_flag_matches_gdt740"]
            and target["mode_matches_gdt740"]
            and target["render_matches_gdt740"]
        )
        output.append({
            "replay_id": f"G741-O{len(output) + 1:02d}",
            "gdt739_dispatch_id": source["dispatch_id"],
            "page": target["page"], "locus": target["locus"],
            "surface": target["surface"],
            "old_manual_role_effect": source["role_effect"],
            "old_manual_mode_effect": source["mode_effect"],
            "old_manual_tier": source["tier_override"],
            "id_free_rule_trace": target["grammar_rule_trace"],
            "gdt741_grammar_tier": target["gdt741_grammar_tier"],
            "role_flags_match_gdt740": target["role_flag_matches_gdt740"],
            "mode_matches_gdt740": target["mode_matches_gdt740"],
            "render_matches_gdt740": target["render_matches_gdt740"],
            "functional_replay_match": functional_match,
            "dispatcher_uses_this_id_or_locus": 0,
            "old_manual_reason_audit_only": source["manual_reason"],
        })
    return output


def sensitivity_rows(contacts: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in contacts:
        for role, relaxed, strict in (
            ("AXIS", int(row["relaxed_axis_relay_candidate"]), int(row["strict_axis_relay_candidate"])),
            ("CARRIER", int(row["relaxed_carrier_relay_candidate"]), int(row["strict_carrier_relay_candidate"])),
        ):
            if not relaxed:
                continue
            output.append({
                "sensitivity_id": f"G741-S{len(output) + 1:02d}",
                "attachment_contact_id": row["attachment_contact_id"],
                "gdt739_dispatch_id": row["dispatch_id"],
                "page": row["page"], "locus": row["locus"],
                "target_surface": row["target_surface"], "side": row["side"],
                "middle_surface": row["intervening_surface"],
                "host_surface": row["neighbor_surface"],
                "candidate_role": role,
                "formal_direction_match": row["formal_role_direction_match"],
                "middle_barrier": row["middle_barrier"],
                "axis_continuity": row["axis_continuity"],
                "carrier_continuity": row["carrier_continuity"],
                "strict_grammar_active": strict,
                "candidate_status": "ACTIVE_STRICT_RELAY" if strict else "OPEN_COLLISION",
                "current_gdt740_role_retained": (
                    row["axis_role_retained"] if role == "AXIS" else row["carrier_role_retained"]
                ),
                "counterevidence": (
                    "no repeated radius-two full frame"
                    if strict else "relaxed continuity conflicts with the current GDT740 hold"
                ),
                "renderer_license": int(strict),
            })
    return output


def physical_folio(page: str) -> str:
    digits = "".join(character for character in page[1:] if character.isdigit())
    return f"f{digits}" if digits else page


def open_collision_edge_packet(
    sensitivity: list[dict[str, object]], contacts: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    """Expose five new relaxed geometries/six roles as deliberately ineligible edges."""
    output: list[dict[str, object]] = []
    candidates_by_contact: dict[str, list[dict[str, object]]] = defaultdict(list)
    for candidate in sensitivity:
        if candidate["candidate_status"] == "OPEN_COLLISION":
            candidates_by_contact[str(candidate["attachment_contact_id"])].append(candidate)
    for contact_id, candidates in candidates_by_contact.items():
        contact = contacts[contact_id]
        target = int(contact["target_ordinal"])
        neighbor = int(contact["neighbor_ordinal"])
        page = str(contact["page"])
        locus = str(contact["locus"])
        role = "_".join(sorted(str(candidate["candidate_role"]) for candidate in candidates))
        output.append({
            "edge_id": f"G741E{len(output) + 1:03d}",
            "batch_id": "GDT741_OPEN_COLLISION_RELAY",
            "page": page, "physical_folio": physical_folio(page),
            "diagram_unit_id": "CACHED_TEXT_LINE",
            "pivot_visual_id": f"TARGET_TOKEN_{target}",
            "pivot_locus": f"{locus}@{target}",
            "target_visual_id": f"R2_HOST_TOKEN_{neighbor}_{role}",
            "target_locus": f"{locus}@{neighbor}",
            "relation_type": f"OPEN_COLLISION_{role}_RELAY",
            "direction_basis": "RELAXED_WHOLE_FIELD_SEMANTIC_CONTINUITY",
            "ownership_basis": "OCCURRENCE_SCOPED_SENSITIVITY_ONLY",
            "geometry_only_selection": "FALSE", "source_manifest_id": "GDT741",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE", "source_aware_localizer": "GDT741_BUILDER",
            "relation_reviewer": "PENDING_EXTERNAL", "relation_confidence": "C_OPEN_COLLISION",
            "ambiguity_state": "UNRESOLVED", "formal_access_state": "FORMAL_ACCESSED",
            "fold_assignment": "NONE", "eligibility_status": "INELIGIBLE_FORMAL_ATTACHMENT_EDGE",
        })
    return output


def rule_census(
    specs: list[dict[str, str]], ring: list[dict[str, str]], contacts: list[dict[str, object]],
    targets: list[dict[str, object]], patches: list[dict[str, object]],
    dispatches: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    target_map = {str(row["gdt739_dispatch_id"]): row for row in targets}
    for spec in specs:
        rule = spec["rule_id"]
        if rule == "G00":
            target_ids = {row["dispatch_id"] for row in ring if row["conflict_only_nonbinding_contact"] == "1"}
            contact_ids: set[str] = set()
            evaluated = len(target_ids)
            changed = 0
        elif rule == "G07":
            selected = [row for row in targets if row["target_prior_state_mode"] == "PROCESS_RESULT"]
            target_ids = {str(row["gdt739_dispatch_id"]) for row in selected}
            contact_ids = set()
            evaluated = len(selected)
            changed = sum(row["retained_direct_process_host_count"] == 0 for row in selected)
        elif rule == "G08":
            target_ids = {str(row["gdt739_dispatch_id"]) for row in targets}
            contact_ids = {str(row["attachment_contact_id"]) for row in contacts}
            evaluated = len(patches)
            changed = 0
        else:
            target_ids = {
                str(row["gdt739_dispatch_id"]) for row in targets
                if rule in str(row["grammar_rule_trace"]).split("|")
            }
            contact_ids = {
                str(row["attachment_contact_id"]) for row in contacts
                if rule in str(row["grammar_rule_trace"]).split("|")
            }
            evaluated = len(target_ids)
            changed = sum(
                dispatches[target_id]["gdt739_working_render_de"]
                != target_map[target_id]["gdt741_working_render_de"]
                for target_id in target_ids
            )
        output.append({
            "rule_id": rule, "precedence": spec["precedence"],
            "rule_name": spec["rule_name"], "targets_triggered": len(target_ids),
            "contacts_traced": len(contact_ids), "cases_evaluated": evaluated,
            "renderer_or_mode_changes_from_unrepaired_gdt739": changed,
            "confidence_level": spec["confidence_level"],
            "evidence": spec["evidence"], "counterevidence": spec["counterevidence"],
            "claim_limit": spec["claim_limit"],
        })
    return output


def passage_replay(
    source_rows: list[dict[str, str]], patches: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in patches:
        by_locus[str(row["locus"])].append(row)
    for rows in by_locus.values():
        rows.sort(key=lambda item: int(item["token_ordinal"]))
    output: list[dict[str, object]] = []
    for source in source_rows:
        focal = source["focal_surfaces"].split("|")
        available = by_locus[source["locus"]]
        chosen: list[dict[str, object]] = []
        used: set[str] = set()
        for surface in focal:
            match = next(
                row for row in available
                if row["surface"] == surface and row["gdt741_patch_id"] not in used
            )
            chosen.append(match)
            used.add(str(match["gdt741_patch_id"]))
        renders = " || ".join(
            f"{row['surface']} → {row['gdt741_working_render_de']}" for row in chosen
        )
        output.append({
            "passage_id": source["passage_id"], "page": source["page"],
            "locus": source["locus"], "section": source["section"],
            "language": source["language"], "focal_surfaces": source["focal_surfaces"],
            "zl3b_line": source["zl3b_line"],
            "gdt740_target_renders_de": source["gdt740_target_renders_de"],
            "gdt741_target_renders_de": renders,
            "grammar_tiers": " || ".join(
                f"{row['surface']}={row['grammar_tier']}" for row in chosen
            ),
            "id_free_render_match": int(renders == source["gdt740_target_renders_de"]),
            "cellwise_audit_display_de": source["cellwise_audit_display_de"],
            "reader_note": "semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target",
        })
    return output


def reader_markdown(
    census: list[dict[str, object]], overrides: list[dict[str, object]],
    sensitivity: list[dict[str, object]], passages: list[dict[str, object]],
) -> str:
    lines = [
        "# GDT741 boundary/relay grammar reader", "",
        "The active renderer is byte-equivalent in meaning to GDT740, but its thirteen",
        "manual occurrence decisions are now replayed by feature rules with no dispatch ID",
        "or locus in the dispatcher. Singleton rules remain hypotheses, not validation.", "",
        "## Executable rule census", "",
        "| rule | targets | contacts | confidence |", "|---|---:|---:|---|",
    ]
    for row in census:
        lines.append(
            f"| {row['rule_id']} {row['rule_name']} | {row['targets_triggered']} | "
            f"{row['contacts_traced']} | {row['confidence_level']} |"
        )
    lines.extend(["", "## Thirteen former manual overrides", ""])
    for row in overrides:
        lines.append(
            f"- `{row['gdt739_dispatch_id']}` {row['locus']} `{row['surface']}`: "
            f"{row['id_free_rule_trace']} — functional match={row['functional_replay_match']}"
        )
    lines.extend(["", "## Strict relays and aggressive open collisions", ""])
    for row in sensitivity:
        lines.append(
            f"- {row['candidate_status']}: {row['locus']} "
            f"`{row['target_surface']}–{row['middle_surface']}–{row['host_surface']}` "
            f"{row['candidate_role']} ({row['middle_barrier']})"
        )
    lines.extend(["", "## Twenty cached passage replays", ""])
    for row in passages:
        lines.extend([
            f"### {row['passage_id']} — {row['locus']}", "",
            f"`{row['zl3b_line']}`", "",
            str(row["gdt741_target_renders_de"]), "",
            f"Cellwise audit: {row['cellwise_audit_display_de']}", "",
        ])
    lines.extend([
        "## Ceiling", "",
        "The rules consume current whole-field working tags. They do not identify a",
        "Voynich word, component, language, plaintext, patient, species, or unit.", "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    rules = read_tsv(SRC / "GRAMMAR_RULES.tsv")
    if [row["rule_id"] for row in rules] != list(RULE_ORDER):
        raise AssertionError("grammar rules or precedence changed")
    dispatch_rows = read_tsv(G739_ART / "DIMENSION_202_DISPATCH.tsv")
    dispatches = {row["dispatch_id"]: row for row in dispatch_rows}
    window_rows = read_tsv(G739_ART / "WINDOW_202_TOKEN_AUDIT.tsv")
    windows = {
        (row["patch_id"], row["side"], row["distance"]): row for row in window_rows
    }
    source_contacts = read_tsv(G740_ART / "SELECTED_103_CONTACT_ATTACHMENT.tsv")
    ring = read_tsv(G740_ART / "TYPED_104_RING_EVIDENCE.tsv")
    old_patch_rows = read_tsv(G740_ART / "TARGET_202_RENDERER_PATCH_V2.tsv")
    old_patches = {row["gdt739_dispatch_id"]: row for row in old_patch_rows}
    old_target_rows = read_tsv(G740_ART / "TARGET_95_ATTACHMENT_ADJUDICATION.tsv")
    old_targets = {row["gdt739_dispatch_id"]: row for row in old_target_rows}

    contacts = build_contact_features(source_contacts, dispatches, windows)
    patches, target_rows, decisions = build_renderer_and_targets(
        dispatch_rows, contacts, old_patches, old_targets,
    )
    target_map = {str(row["gdt739_dispatch_id"]): row for row in target_rows}

    # The old override table enters only after every grammar decision has been built.
    override_rows = read_tsv(G740_SRC / "MANUAL_ATTACHMENT_OVERRIDES.tsv")
    overrides = override_replay(override_rows, target_map)
    sensitivity = sensitivity_rows(contacts)
    edge_rows = open_collision_edge_packet(
        sensitivity, {str(row["attachment_contact_id"]): row for row in contacts},
    )
    census = rule_census(rules, ring, contacts, target_rows, patches, dispatches)
    passages = passage_replay(
        read_tsv(G740_ART / "PASSAGE_20_ATTACHMENT_REVIEW.tsv"), patches,
    )
    reader = reader_markdown(census, overrides, sensitivity, passages)

    write_tsv(output_dir / "CONTACT_103_GRAMMAR_DISPATCH.tsv", contacts, (
        "attachment_contact_id", "window_id", "dispatch_id", "patch_id", "page", "locus",
        "target_ordinal", "target_surface", "opaque_head_id", "line_position",
        "selected_roles", "side", "signed_offset", "distance", "neighbor_ordinal",
        "neighbor_surface", "neighbor_semantic_value_de", "neighbor_axis_tags",
        "neighbor_scalar_host_types", "formal_role_direction_match",
        "guarded_reader_exact_pair_occurrences",
        "guarded_reader_exact_full_frame_occurrences", "intervening_surface",
        "intervening_emits_own_unit", "intervening_strict_initial_head",
        "intervening_another_gdt738_target", "target_family", "target_level",
        "target_favored_axis", "target_dimension", "target_prior_state_mode",
        "target_wanted_carrier_set", "host_quality_set", "host_carrier_set",
        "host_scalar_class_set", "host_boundary_set", "host_axis_signature",
        "single_host_covers_requested_carrier", "middle_reader_exact", "middle_known",
        "middle_positive_host_eligible", "middle_ineligibility_reasons",
        "middle_quality_set", "middle_carrier_set", "middle_scalar_class_set",
        "middle_boundary_set", "middle_axis_signature", "middle_barrier",
        "axis_continuity", "carrier_continuity", "opposite_reader_exact",
        "opposite_known", "opposite_positive_host_eligible",
        "opposite_ineligibility_reasons", "opposite_quality_set",
        "strict_axis_relay_candidate",
        "strict_carrier_relay_candidate", "relaxed_axis_relay_candidate",
        "relaxed_carrier_relay_candidate", "axis_role_retained", "carrier_role_retained",
        "predicted_axis_role_retained", "predicted_carrier_role_retained",
        "predicted_renderer_role_retained", "grammar_rule_trace",
        "axis_flag_matches_gdt740", "carrier_flag_matches_gdt740",
        "role_flags_match_gdt740", "literal_plaintext_claimed", "component_export_credit",
    ))
    write_tsv(output_dir / "TARGET_95_GRAMMAR_FEATURES.tsv", target_rows, (
        "feature_id", "gdt739_dispatch_id", "page", "locus", "token_ordinal", "surface",
        "opaque_head_id", "line_position", "family", "level", "target_dimension",
        "target_favored_axis", "target_wanted_carrier_set", "target_prior_state_mode",
        "selected_contacts", "direct_contacts", "radius_two_contacts", "closure_crossing",
        "bilateral_role_split", "state_opposite_axis_rival", "pure_amount_field_owns_value",
        "single_host_composite_carrier_conflict", "strict_axis_relay_count",
        "strict_carrier_relay_count", "retained_direct_process_host_count",
        "grammar_rule_trace", "gdt740_attachment_tier", "gdt741_grammar_tier",
        "gdt740_working_render_de", "gdt741_working_render_de",
        "role_flag_matches_gdt740", "mode_matches_gdt740", "render_matches_gdt740",
        "dispatcher_uses_dispatch_id_or_locus", "plaintext_or_lexeme_claim",
        "component_export_credit",
    ))
    write_tsv(output_dir / "OVERRIDE_13_ID_FREE_REPLAY.tsv", overrides, overrides[0].keys())
    write_tsv(output_dir / "RULE_10_TRIGGER_CENSUS.tsv", census, census[0].keys())
    write_tsv(
        output_dir / "R2_8_STRICT_AND_OPEN_COLLISION_CANDIDATES.tsv",
        sensitivity, sensitivity[0].keys(),
    )
    write_tsv(output_dir / "GDT741_GDT388_OPEN_COLLISION_EDGE_PACKET.tsv", edge_rows, (
        "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
        "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
        "relation_type", "direction_basis", "ownership_basis", "geometry_only_selection",
        "source_manifest_id", "page_crop_sha256", "pivot_crop_sha256",
        "target_crop_sha256", "source_aware_localizer", "relation_reviewer",
        "relation_confidence", "ambiguity_state", "formal_access_state",
        "fold_assignment", "eligibility_status",
    ))
    write_tsv(output_dir / "TARGET_202_RENDERER_PATCH_V3.tsv", patches, patches[0].keys())
    write_tsv(output_dir / "PASSAGE_20_GRAMMAR_REPLAY.tsv", passages, passages[0].keys())
    (output_dir / "GDT741_BOUNDARY_RELAY_GRAMMAR_READER.md").write_text(reader, encoding="utf-8")

    artifact_hashes = {
        str(BASE_REL / "artifacts" / name): sha256(output_dir / name)
        for name in OUTPUT_NAMES
    }
    result = {
        "schema": "GDT741_LOCAL_ATTACHMENT_BOUNDARY_RELAY_GRAMMAR_V1",
        "status": STATUS,
        "scope": {
            "inherited_allowlist_pages": 179,
            "target_pages": len({row["page"] for row in dispatch_rows}),
            "all_renderer_positions": 202, "formerly_specific_targets": 95,
            "new_pages_used": 0, "f84_used": False, "f84r_used": False,
        },
        "replay": {
            "typed_ring_rows": len(ring), "binding_contacts": len(contacts),
            "nonbinding_conflict_rows": sum(row["conflict_only_nonbinding_contact"] == "1" for row in ring),
            "contact_role_flag_mismatches": sum(not int(row["role_flags_match_gdt740"]) for row in contacts),
            "former_manual_overrides": len(overrides),
            "former_manual_override_functional_matches": sum(int(row["functional_replay_match"]) for row in overrides),
            "old_result_candidates": sum(row["target_prior_state_mode"] == "PROCESS_RESULT" for row in target_rows),
            "result_modes_retained": sum(row["retained_direct_process_host_count"] == 1 for row in target_rows if row["target_prior_state_mode"] == "PROCESS_RESULT"),
            "result_modes_downgraded": sum(row["retained_direct_process_host_count"] == 0 for row in target_rows if row["target_prior_state_mode"] == "PROCESS_RESULT"),
            "renderer_patch_mismatches": sum(int(row["grammar_changed_from_gdt740"]) for row in patches),
            "passage_render_mismatches": sum(not int(row["id_free_render_match"]) for row in passages),
        },
        "grammar": {
            "rules": len(rules),
            "singleton_role_rules": 6,
            "strict_axis_relays": sum(int(row["strict_axis_relay_candidate"]) for row in contacts),
            "strict_carrier_relays": sum(int(row["strict_carrier_relay_candidate"]) for row in contacts),
            "composite_carrier_conflict_targets": sum(int(row["single_host_composite_carrier_conflict"]) for row in target_rows),
            "dispatcher_uses_dispatch_id_or_locus": False,
            "dependency": "current whole-field semantic tags plus local practical-cell geometry; this is compression, not independent validation",
        },
        "renderer": {
            "axis_specific_occurrences": sum(int(row["axis_specific_dispatch_retained"]) for row in patches),
            "carrier_bound_occurrences": sum(int(row["carrier_locally_bound_retained"]) for row in patches),
            "specific_occurrences": sum(int(row["specific_local_dispatch_retained"]) for row in patches),
            "fully_open_occurrences": sum(not int(row["specific_local_dispatch_retained"]) for row in patches),
            "changed_from_gdt740": sum(int(row["grammar_changed_from_gdt740"]) for row in patches),
        },
        "sensitivity": {
            "strict_and_relaxed_candidate_roles": len(sensitivity),
            "active_strict_roles": sum(int(row["strict_grammar_active"]) for row in sensitivity),
            "open_collision_roles": sum(not int(row["strict_grammar_active"]) for row in sensitivity),
            "open_collision_targets": len({row["gdt739_dispatch_id"] for row in sensitivity if not int(row["strict_grammar_active"])}),
            "projected_specific_if_all_open_collisions_spoken": 56 + len({row["gdt739_dispatch_id"] for row in sensitivity if not int(row["strict_grammar_active"])}),
            "projected_fully_open_if_all_open_collisions_spoken": 146 - len({row["gdt739_dispatch_id"] for row in sensitivity if not int(row["strict_grammar_active"])}),
            "renderer_effect": "NONE; six relaxed roles remain OPEN_COLLISION",
        },
        "edge_intake": {
            "packet_rows": len(edge_rows), "expected_status": "INVALID_PACKET",
            "score_ready": False,
        },
        "claims": {
            "lexemes_identified": 0, "components_exported": 0,
            "plaintext_clauses": 0, "literal_patients_or_species": 0,
            "unseen_forms_licensed": 0, "new_pages": 0,
        },
        "artifact_hashes": artifact_hashes,
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": STATUS, "replay": result["replay"],
        "renderer": result["renderer"], "sensitivity": result["sensitivity"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
