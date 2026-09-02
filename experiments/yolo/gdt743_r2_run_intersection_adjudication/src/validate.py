#!/usr/bin/env python3
"""Independent run/intersection audit and byte replay for GDT743."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt743_r2_run_intersection_adjudication")
EXP = ROOT / BASE
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
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
GENERATED = (
    "TARGET_202_REQUESTED_CARRIER_COVERAGE_FEATURES.tsv",
    "R2_41_EXTENSION_DISPATCH.tsv",
    "RUN_8_REQUESTED_CARRIER_COVERAGE_CENSUS.tsv",
    "CARRIER_6_UNCONDITIONED_COVERAGE_CENSUS.tsv",
    "AXIS_5_INHERITED_FAVORED_CENSUS.tsv",
    "CANDIDATE_4_REMAINING_ROLE_ADJUDICATION.tsv",
    "TARGET_202_RENDERER_PATCH_V5.tsv", "FOCUS_3_EXTENSION_REVIEW.tsv",
    "GDT743_GDT388_RUN_OVERRIDE_EDGE_PACKET.tsv",
    "GDT743_RUN_INTERSECTION_READER.md", "RESULT.json",
)
HASHED_BY_RESULT = GENERATED[:-1]
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def values(value: str, separator: str = "|") -> set[str]:
    if value in {"", "NONE", "NA", "OPEN", "NOT_APPLICABLE"}:
        return set()
    return set(value.split(separator))


def carriers(value: str) -> set[str]:
    return values(value.replace("_", "|")) & CARRIERS


def clean(row: dict[str, str]) -> bool:
    return bool(
        row["neighbor_reader_exact"] == "1"
        and row["neighbor_unknown_v99r7"] == "0"
        and row["neighbor_composition_semantic_credit"] == "0"
        and row["strict_initial_head_neighbor"] == "0"
        and row["another_gdt738_target"] == "0"
        and row["retired_patient_words"] == "NONE"
    )


def independent_run(
    windows: dict[tuple[str, int], dict[str, str]], side: str,
    wanted: set[str], favored: str | None = None,
    forbidden_tags: set[str] | None = None,
) -> dict[str, object]:
    raw = clean_length = exact = 0
    first_three_no_close = True
    members: list[str] = []
    if not wanted and favored is None:
        return {"raw": 0, "clean": 0, "exact": 0, "no_close": 0, "members": "NONE"}
    for distance in range(1, 6):
        row = windows.get((side, distance))
        if row is None:
            break
        tags = values(row["axis_tags"])
        if tags & (forbidden_tags or set()):
            break
        carries = favored in tags if favored is not None else wanted <= (tags & CARRIERS)
        if not carries:
            break
        raw += 1
        members.append(f"{distance}:{row['neighbor_surface']}:{row['axis_tags']}")
        if distance <= 3 and "CLOSE" in tags:
            first_three_no_close = False
        if clean(row) and clean_length == distance - 1:
            clean_length += 1
            if favored is None and tags & CARRIERS == wanted and exact == distance - 1:
                exact += 1
        if "CLOSE" in tags:
            break
    return {
        "raw": raw, "clean": clean_length, "exact": exact,
        "no_close": int(first_three_no_close and clean_length >= 3),
        "members": "|".join(members) or "NONE",
    }


def independent_r2(source: dict[str, str], run: dict[str, str]) -> dict[str, object]:
    selected = values(source["selected_roles"], "+")
    wanted = carriers(source["target_wanted_carrier_set"])
    host = carriers(source["host_carrier_set"])
    middle = carriers(source["middle_carrier_set"])
    common = bool(
        int(source["guarded_reader_exact_full_frame_occurrences"]) >= 1
        and source["middle_reader_exact"] == "1" and source["middle_known"] == "1"
        and source["intervening_emits_own_unit"] == "1"
        and source["intervening_strict_initial_head"] == "0"
        and source["intervening_another_gdt738_target"] == "0"
    )
    open_frame = common and source["middle_barrier"] == "OPEN"
    direction = source["formal_role_direction_match"] == "1"
    full = bool(wanted and wanted <= host and wanted <= middle)
    axis = bool(open_frame and direction and selected == {"AXIS"} and source["axis_continuity"] == "EXACT_SINGLE")
    base_carrier = bool(
        open_frame and direction and full
        and (selected == {"CARRIER"} or selected == {"AXIS", "CARRIER"} and source["axis_continuity"] == "NONE")
    )
    side = source["side"]
    opposite = "R" if side == "L" else "L"
    side_screened = int(run[f"{'left' if side == 'L' else 'right'}_requested_carrier_coverage_screened"])
    opposite_screened = int(run[f"{'left' if opposite == 'L' else 'right'}_requested_carrier_coverage_screened"])
    side_no_close = run[f"{'left' if side == 'L' else 'right'}_first_three_coverage_no_close"] == "1"
    relaxed = bool(open_frame and not direction and "CARRIER" in selected and full)
    coverage_gate = bool(
        side_screened >= 3 and opposite_screened < 3 and side_no_close
        and run["requested_carrier_ge3_unique_side"] == side
    )
    override = bool(relaxed and coverage_gate)
    intersection = values(source["host_quality_set"]) & values(source["middle_quality_set"]) & QUALITY
    generic = bool(
        open_frame and "AXIS" in selected
        and "QUALITY_DEGREE" in values(source["host_scalar_class_set"])
        and "QUALITY_DEGREE" in values(source["middle_scalar_class_set"])
        and len(intersection) == 1
    )
    favored = bool(
        generic and source["axis_continuity"] == "PARTIAL"
        and intersection == {source["target_favored_axis"]}
    )
    trace = (
        "PROVISIONAL_REQUESTED_CARRIER_COVERAGE_ANALOGY" if override
        else "GDT742_STRICT_AXIS_RELAY" if axis
        else "GDT742_CARRIER_RELAY" if base_carrier
        else "R2_HOLD"
    )
    return {
        "axis": int(axis), "carrier": int(base_carrier or override),
        "override": int(override), "generic": int(generic), "favored": int(favored),
        "relaxed": int(relaxed), "coverage_gate": int(coverage_gate),
        "coverage_excludes_relaxed": int(relaxed and not coverage_gate),
        "intersection": "|".join(sorted(intersection)) or "NONE", "trace": trace,
    }


def independent_render(source: dict[str, str], carrier: str, coverage_length: int) -> str:
    if source["family"] != "SCALAR" or source["gdt742_dimension_dispatch"] != "OPEN_SCALAR":
        raise AssertionError("changed target is not open scalar")
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    art = args.artifacts_dir.resolve()
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def require(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT743", "manifest experiment id")
    check(manifest["slug"] == "r2_run_intersection_adjudication", "manifest slug")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed selectors forbidden")
    check(manifest["status"] == STATUS, "manifest status")
    check(manifest["dependencies"] == ["GDT739", "GDT742"], "manifest dependencies exact")
    check(bool(manifest["question"]) and bool(manifest["claim_ceiling"]), "manifest question and claim ceiling present")
    check(manifest["validation"] == {"artifact": str(VALIDATION_REL), "status": "PASS"}, "manifest validation contract")
    expected_inputs = {
        "experiments/yolo/gdt742_r2_open_collision_adjudication/artifacts/CONTACT_103_ROLE_SEPARATION_DISPATCH.tsv",
        "experiments/yolo/gdt742_r2_open_collision_adjudication/artifacts/CANDIDATE_8_ROLE_ADJUDICATION.tsv",
        "experiments/yolo/gdt742_r2_open_collision_adjudication/artifacts/TARGET_202_RENDERER_PATCH_V4.tsv",
        "experiments/yolo/gdt742_r2_open_collision_adjudication/artifacts/FOCUS_7_CACHED_LINE_REVIEW.tsv",
        "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/artifacts/DIMENSION_202_DISPATCH.tsv",
        "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/artifacts/WINDOW_202_TOKEN_AUDIT.tsv",
    }
    check({row["path"] for row in manifest["inputs"]} == expected_inputs and len(manifest["inputs"]) == 6, "manifest binds exact six inputs")
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        require(not Path(binding["path"]).is_absolute(), f"absolute input: {binding['path']}")
        require(path.is_file() and sha256(path) == binding["sha256"], f"input mismatch: {binding['path']}")
    check(True, "all manifest inputs hash-match")
    expected_outputs = {
        str(BASE / name) for name in ("README.md", "METHOD.md", "PREREGISTRATION.md", "REPORT.md")
    } | {str(BASE / "src" / name) for name in ("run.py", "validate.py")} | {
        str(BASE / "artifacts" / name) for name in ("README.md", *GENERATED, "VALIDATION.json")
    }
    check({row["path"] for row in manifest["outputs"]} == expected_outputs and len(manifest["outputs"]) == len(expected_outputs), "manifest binds exact output set")
    for binding in manifest["outputs"]:
        if binding["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / binding["path"]
        require(path.is_file() and sha256(path) == binding["sha256"], f"output mismatch: {binding['path']}")
    check(True, "all non-validation output hashes match")

    check(art.is_dir() and all((art / name).is_file() for name in GENERATED), "all generated artifacts exist")
    run_text = RUN.read_text(encoding="utf-8")
    check("G739-D0" not in run_text and not re.search(r"[\"']f\d+[rv](?:\.\d+)?[\"']", run_text), "builder hardcodes no target id or locus")
    tree = ast.parse(run_text)
    declared = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "DECISION_FIELDS":
            declared = tuple(ast.literal_eval(node.value))
    check(declared == DECISION_FIELDS, "decision field whitelist exact")
    decision_source = run_text[run_text.index("def adjudicate_r2("):run_text.index("def r2_dispatch(")]
    forbidden = {
        "attachment_contact_id", "dispatch_id", "patch_id", "page", "locus",
        "target_surface", "gdt742_axis_role_retained", "gdt742_carrier_role_retained",
        "gdt742_status", "renderer_license", "working_reason",
    }
    check(not any(f'["{field}"]' in decision_source or f"['{field}']" in decision_source for field in forbidden), "adjudicator cannot address identity or predecessor outcomes")
    check(run_text.index("r2 = r2_dispatch(source_contacts, run_map)") < run_text.index("candidates = candidate_adjudication(source_candidates"), "candidate outcomes enter after complete decisions")

    source_contacts = read_tsv(G742_ART / "CONTACT_103_ROLE_SEPARATION_DISPATCH.tsv")
    source_candidates = read_tsv(G742_ART / "CANDIDATE_8_ROLE_ADJUDICATION.tsv")
    source_patches = read_tsv(G742_ART / "TARGET_202_RENDERER_PATCH_V4.tsv")
    source_focus = read_tsv(G742_ART / "FOCUS_7_CACHED_LINE_REVIEW.tsv")
    dispatches = read_tsv(G739_ART / "DIMENSION_202_DISPATCH.tsv")
    windows = read_tsv(G739_ART / "WINDOW_202_TOKEN_AUDIT.tsv")
    decks = (source_contacts, source_candidates, source_patches, source_focus, dispatches, windows)
    check((len(source_contacts), len(source_candidates), len(source_patches), len(dispatches), len(windows)) == (103, 8, 202, 202, 1373), "fixed source deck sizes")
    check(not any(row.get("page", "").startswith("f84") or row.get("locus", "").startswith("f84") for deck in decks for row in deck), "all materialized sources exclude sealed pages")
    check(len({row["attachment_contact_id"] for row in source_contacts}) == 103 and len({row["gdt739_dispatch_id"] for row in source_patches}) == 202 and len({row["dispatch_id"] for row in dispatches}) == 202 and len({row["window_id"] for row in windows}) == 1373, "all source keys unique")
    source_patch_map = {row["gdt739_dispatch_id"]: row for row in source_patches}
    dispatch_map = {row["dispatch_id"]: row for row in dispatches}
    windows_by_patch: dict[str, dict[tuple[str, int], dict[str, str]]] = defaultdict(dict)
    for row in windows:
        key = (row["side"], int(row["distance"]))
        require(key not in windows_by_patch[row["patch_id"]], f"duplicate window coordinate: {row['window_id']}")
        windows_by_patch[row["patch_id"]][key] = row
    check(True, "all 1373 window coordinates unique")

    target_runs = read_tsv(art / "TARGET_202_REQUESTED_CARRIER_COVERAGE_FEATURES.tsv")
    check(len(target_runs) == len({row["gdt739_dispatch_id"] for row in target_runs}) == 202, "202 unique target coverage features")
    run_map = {row["gdt739_dispatch_id"]: row for row in target_runs}
    check(set(run_map) == set(dispatch_map), "run deck exactly covers dispatches")
    for row in target_runs:
        source = dispatch_map[row["gdt739_dispatch_id"]]
        patch = source_patch_map[row["gdt739_dispatch_id"]]
        wanted = carriers(source["carrier_dispatch"])
        left = independent_run(windows_by_patch[source["patch_id"]], "L", wanted)
        right = independent_run(windows_by_patch[source["patch_id"]], "R", wanted)
        left_no_process = independent_run(windows_by_patch[source["patch_id"]], "L", wanted, forbidden_tags={"PROCESS"})
        right_no_process = independent_run(windows_by_patch[source["patch_id"]], "R", wanted, forbidden_tags={"PROCESS"})
        left_no_pass = independent_run(windows_by_patch[source["patch_id"]], "L", wanted, forbidden_tags={"PASS"})
        right_no_pass = independent_run(windows_by_patch[source["patch_id"]], "R", wanted, forbidden_tags={"PASS"})
        left_no_close = independent_run(windows_by_patch[source["patch_id"]], "L", wanted, forbidden_tags={"CLOSE"})
        right_no_close = independent_run(windows_by_patch[source["patch_id"]], "R", wanted, forbidden_tags={"CLOSE"})
        left_no_process_pass = independent_run(windows_by_patch[source["patch_id"]], "L", wanted, forbidden_tags={"PROCESS", "PASS"})
        right_no_process_pass = independent_run(windows_by_patch[source["patch_id"]], "R", wanted, forbidden_tags={"PROCESS", "PASS"})
        left_no_process_pass_close = independent_run(windows_by_patch[source["patch_id"]], "L", wanted, forbidden_tags={"PROCESS", "PASS", "CLOSE"})
        right_no_process_pass_close = independent_run(windows_by_patch[source["patch_id"]], "R", wanted, forbidden_tags={"PROCESS", "PASS", "CLOSE"})
        qualifying_sides = [
            side for side, coverage in (("L", left), ("R", right))
            if int(coverage["clean"]) >= 3 and int(coverage["no_close"])
        ]
        unique = qualifying_sides[0] if len(qualifying_sides) == 1 else "NONE"
        favored = source["favored_axis_not_automatic"]
        if favored in QUALITY:
            la = independent_run(windows_by_patch[source["patch_id"]], "L", set(), favored)
            ra = independent_run(windows_by_patch[source["patch_id"]], "R", set(), favored)
        else:
            la = {"clean": 0}; ra = {"clean": 0}
        require(all(row[field] == source[source_field] for field, source_field in (("gdt738_patch_id", "patch_id"), ("page", "page"), ("locus", "locus"), ("target_ordinal", "token_ordinal"), ("target_surface", "surface"), ("opaque_head_id", "opaque_head_id"))), f"run provenance: {row['run_feature_id']}")
        require(row["formal_carrier_side"] == FORMAL_SIDE[source["opaque_head_id"]], f"formal side: {row['run_feature_id']}")
        require(carriers(row["requested_carrier_set"]) == wanted and row["gdt739_requested_carrier_dispatch"] == source["carrier_dispatch"], f"requested carrier: {row['run_feature_id']}")
        require(row["gdt742_carrier_dispatch"] == patch["gdt742_carrier_dispatch"], f"old carrier: {row['run_feature_id']}")
        for side_name, expected in (("left", left), ("right", right)):
            require(row[f"{side_name}_requested_carrier_coverage_raw"] == str(expected["raw"]), f"raw coverage: {row['run_feature_id']}:{side_name}")
            require(row[f"{side_name}_requested_carrier_coverage_screened"] == str(expected["clean"]), f"screened coverage: {row['run_feature_id']}:{side_name}")
            require(row[f"{side_name}_requested_carrier_exact_set_screened"] == str(expected["exact"]), f"exact-set prefix: {row['run_feature_id']}:{side_name}")
            require(row[f"{side_name}_first_three_coverage_no_close"] == str(expected["no_close"]), f"close gate: {row['run_feature_id']}:{side_name}")
        variants = {
            "no_process": (left_no_process, right_no_process),
            "no_pass": (left_no_pass, right_no_pass),
            "no_close": (left_no_close, right_no_close),
            "no_process_pass": (left_no_process_pass, right_no_process_pass),
            "no_process_pass_close": (left_no_process_pass_close, right_no_process_pass_close),
        }
        for label, (expected_left, expected_right) in variants.items():
            require(row[f"left_requested_carrier_{label}_screened"] == str(expected_left["clean"]), f"{label} left: {row['run_feature_id']}")
            require(row[f"right_requested_carrier_{label}_screened"] == str(expected_right["clean"]), f"{label} right: {row['run_feature_id']}")
        require(row["requested_carrier_ge3_unique_side"] == unique, f"unique long side: {row['run_feature_id']}")
        expected_members = left["members"] if unique == "L" else right["members"] if unique == "R" else "NONE"
        require(row["requested_carrier_coverage_members"] == expected_members, f"coverage members: {row['run_feature_id']}")
        require(row["favored_axis"] == favored and row["left_inherited_favored_axis_coverage_screened"] == str(la["clean"]) and row["right_inherited_favored_axis_coverage_screened"] == str(ra["clean"]), f"favored axis coverage: {row['run_feature_id']}")
        require(row["bilateral_favored_axis_support"] == str(int(int(la["clean"]) >= 1 and int(ra["clean"]) >= 1)), f"bilateral favored: {row['run_feature_id']}")
        require(row["bilateral_two_by_two_favored_axis_support"] == str(int(int(la["clean"]) >= 2 and int(ra["clean"]) >= 2)), f"two-by-two favored: {row['run_feature_id']}")
        require(row["current_carrier_bound"] == str(int(patch["gdt742_carrier_dispatch"] != "OPEN")) and row["current_axis_specific"] == patch["axis_specific_dispatch_retained"], f"run outcome comparator: {row['run_feature_id']}")
        require(row["new_page_or_transcription"] == row["literal_plaintext_claimed"] == row["component_export_credit"] == "0", f"run ceiling: {row['run_feature_id']}")
    check(True, "all 202 target coverage and conditioned-axis features independently recompute")
    raw_long_ids = {row["gdt739_dispatch_id"] for row in target_runs if max(int(row["left_requested_carrier_coverage_raw"]), int(row["right_requested_carrier_coverage_raw"])) >= 3}
    clean_long_ids = {row["gdt739_dispatch_id"] for row in target_runs if row["requested_carrier_ge3_unique_side"] != "NONE"}
    check(raw_long_ids == {"G739-D0005", "G739-D0028", "G739-D0035", "G739-D0041", "G739-D0045", "G739-D0065", "G739-D0075", "G739-D0164"}, "eight raw requested-carrier coverage targets")
    check(clean_long_ids == {"G739-D0028", "G739-D0041", "G739-D0045", "G739-D0075"}, "four screened unique requested-carrier coverage targets")
    check(sum(run_map[dispatch]["current_carrier_bound"] == "1" for dispatch in clean_long_ids) == 3, "three of four requested-carrier comparators already carrier-bound")
    check(run_map["G739-D0045"]["formal_carrier_side"] == "L" and run_map["G739-D0045"]["requested_carrier_ge3_unique_side"] == "R", "D0045 is the reverse R1 H4 comparator")
    check(run_map["G739-D0075"]["right_requested_carrier_coverage_screened"] == "4" and run_map["G739-D0075"]["right_requested_carrier_exact_set_screened"] == "2", "D0075 containment coverage is four but exact-set prefix is two")
    check(run_map["G739-D0164"]["right_requested_carrier_coverage_raw"] == "4" and run_map["G739-D0164"]["right_requested_carrier_coverage_screened"] == "2", "D0164 raw coverage is cut by retired-patient control")

    def variant_ids(left: str, right: str) -> set[str]:
        return {row["gdt739_dispatch_id"] for row in target_runs if max(int(row[left]), int(row[right])) >= 3}

    sensitivity = {
        "base_requested_carrier_coverage_ge3_ids": sorted(clean_long_ids),
        "exact_carrier_set_prefix_ge3_ids": sorted(variant_ids("left_requested_carrier_exact_set_screened", "right_requested_carrier_exact_set_screened")),
        "exclude_process_ge3_ids": sorted(variant_ids("left_requested_carrier_no_process_screened", "right_requested_carrier_no_process_screened")),
        "exclude_pass_ge3_ids": sorted(variant_ids("left_requested_carrier_no_pass_screened", "right_requested_carrier_no_pass_screened")),
        "exclude_close_ge3_ids": sorted(variant_ids("left_requested_carrier_no_close_screened", "right_requested_carrier_no_close_screened")),
        "exclude_process_pass_ge3_ids": sorted(variant_ids("left_requested_carrier_no_process_pass_screened", "right_requested_carrier_no_process_pass_screened")),
        "exclude_process_pass_close_ge3_ids": sorted(variant_ids("left_requested_carrier_no_process_pass_close_screened", "right_requested_carrier_no_process_pass_close_screened")),
    }
    check(sensitivity == {
        "base_requested_carrier_coverage_ge3_ids": ["G739-D0028", "G739-D0041", "G739-D0045", "G739-D0075"],
        "exact_carrier_set_prefix_ge3_ids": ["G739-D0028", "G739-D0041"],
        "exclude_process_ge3_ids": ["G739-D0028", "G739-D0041", "G739-D0045"],
        "exclude_pass_ge3_ids": ["G739-D0041", "G739-D0045", "G739-D0075"],
        "exclude_close_ge3_ids": ["G739-D0028", "G739-D0041", "G739-D0045", "G739-D0075"],
        "exclude_process_pass_ge3_ids": ["G739-D0041", "G739-D0045"],
        "exclude_process_pass_close_ge3_ids": ["G739-D0041", "G739-D0045"],
    }, "all requested-carrier sensitivity classes exact")

    r2 = read_tsv(art / "R2_41_EXTENSION_DISPATCH.tsv")
    source_r2 = {row["attachment_contact_id"]: row for row in source_contacts if row["distance"] == "2"}
    check(len(r2) == len({row["attachment_contact_id"] for row in r2}) == len(source_r2) == 41, "41 unique radius-two extension decisions")
    check({row["attachment_contact_id"] for row in r2} == set(source_r2), "R2 output exactly covers source R2")
    r2_map = {row["attachment_contact_id"]: row for row in r2}
    expected_r2: dict[str, dict[str, object]] = {}
    shared_r2 = set(source_contacts[0]) & set(r2[0])
    for row in r2:
        source = source_r2[row["attachment_contact_id"]]
        run = run_map[row["dispatch_id"]]
        expected = independent_r2(source, run)
        expected_r2[row["attachment_contact_id"]] = expected
        require(all(row[field] == source[field] for field in shared_r2), f"R2 provenance: {row['attachment_contact_id']}")
        for field in (
            "left_requested_carrier_coverage_raw", "right_requested_carrier_coverage_raw",
            "left_requested_carrier_coverage_screened", "right_requested_carrier_coverage_screened",
            "left_requested_carrier_exact_set_screened", "right_requested_carrier_exact_set_screened",
            "requested_carrier_ge3_unique_side",
        ):
            require(row[field] == run[field], f"R2 coverage crosswalk: {row['attachment_contact_id']}:{field}")
        require(row["intersection_axis_set"] == expected["intersection"] and row["generic_singleton_axis_intersection"] == str(expected["generic"]) and row["favored_partial_axis_intersection"] == str(expected["favored"]), f"intersection decision: {row['attachment_contact_id']}")
        require(row["gdt743_axis_role_retained"] == str(expected["axis"]) and row["gdt743_carrier_role_retained"] == str(expected["carrier"]), f"R2 roles: {row['attachment_contact_id']}")
        require(
            row["relaxed_reverse_full_carrier_trigger"] == str(expected["relaxed"])
            and row["requested_carrier_coverage_gate"] == str(expected["coverage_gate"])
            and row["requested_carrier_coverage_override"] == str(expected["override"])
            and row["coverage_excludes_relaxed_trigger"] == str(expected["coverage_excludes_relaxed"])
            and row["gdt743_rule_trace"] == expected["trace"],
            f"R2 trace and ablation: {row['attachment_contact_id']}",
        )
        require(row["axis_changed_from_gdt742"] == str(int(int(expected["axis"]) != int(source["gdt742_axis_role_retained"]))) and row["carrier_changed_from_gdt742"] == str(int(int(expected["carrier"]) != int(source["gdt742_carrier_role_retained"]))), f"R2 deltas: {row['attachment_contact_id']}")
        expected_role_change = int(
            int(expected["axis"]) != int(source["gdt742_axis_role_retained"])
            or int(expected["carrier"]) != int(source["gdt742_carrier_role_retained"])
        )
        require(row["gdt743_renderer_role_retained"] == str(int(int(expected["axis"]) or int(expected["carrier"]))) and row["role_changed_from_gdt742"] == str(expected_role_change), f"R2 renderer/change wiring: {row['attachment_contact_id']}")
        require(row["dispatcher_uses_dispatch_id_or_locus"] == row["literal_plaintext_claimed"] == row["component_export_credit"] == "0", f"R2 ceiling: {row['attachment_contact_id']}")
    check(True, "all 41 radius-two decisions independently recompute")
    check({row["dispatch_id"] for row in r2 if row["requested_carrier_coverage_override"] == "1"} == {"G739-D0075"}, "D0075 is the sole provisional R2 coverage analogy")
    check(
        sum(int(row["relaxed_reverse_full_carrier_trigger"]) for row in r2) == 1
        and sum(int(row["requested_carrier_coverage_override"]) for row in r2) == 1
        and sum(int(row["coverage_excludes_relaxed_trigger"]) for row in r2) == 0,
        "R2 coverage ablation is one to one and excludes zero",
    )
    check(sum(int(row["axis_changed_from_gdt742"]) for row in r2) == 0 and sum(int(row["carrier_changed_from_gdt742"]) for row in r2) == 1, "zero axis and one carrier delta")
    check(not any(int(row["gdt742_axis_role_retained"]) and not int(row["gdt743_axis_role_retained"]) or int(row["gdt742_carrier_role_retained"]) and not int(row["gdt743_carrier_role_retained"]) for row in r2), "no inherited active R2 role is deactivated")
    check(sum(int(row["gdt742_axis_role_retained"]) + int(row["gdt742_carrier_role_retained"]) for row in r2) == 4 and sum(int(row["gdt743_axis_role_retained"]) + int(row["gdt743_carrier_role_retained"]) for row in r2) == 5, "active R2 roles move four to five")
    check({row["dispatch_id"] for row in r2 if row["favored_partial_axis_intersection"] == "1"} == {"G739-D0040"}, "D0040 is the sole favored partial-axis lead")
    check(r2_map["G740-C0007"]["requested_carrier_coverage_override"] == "0" and r2_map["G740-C0007"]["middle_barrier"] == "STRICT_HEAD", "D0015 reverse full-carrier negative remains held")

    long_rows = read_tsv(art / "RUN_8_REQUESTED_CARRIER_COVERAGE_CENSUS.tsv")
    check(len(long_rows) == 8 and {row["gdt739_dispatch_id"] for row in long_rows} == raw_long_ids, "requested-carrier census exactly filters eight raw targets")
    check({row["gdt739_dispatch_id"] for row in long_rows if row["requested_carrier_ge3_qualifier"] == "1"} == clean_long_ids, "requested-carrier census marks exact screened class")

    expected_unconditioned: dict[tuple[str, str], dict[str, object]] = {}
    for source in dispatches:
        for candidate in CARRIER_ORDER:
            left = independent_run(windows_by_patch[source["patch_id"]], "L", {candidate})
            right = independent_run(windows_by_patch[source["patch_id"]], "R", {candidate})
            sides = [
                side for side, coverage in (("L", left), ("R", right))
                if int(coverage["clean"]) >= 3 and int(coverage["no_close"])
            ]
            if len(sides) != 1:
                continue
            side = sides[0]
            selected = left if side == "L" else right
            expected_unconditioned[(source["dispatch_id"], candidate)] = {
                "side": side, "screened": selected["clean"],
                "exact": selected["exact"], "members": selected["members"],
                "formal_match": int(side == FORMAL_SIDE[source["opaque_head_id"]]),
            }
    unconditional = read_tsv(art / "CARRIER_6_UNCONDITIONED_COVERAGE_CENSUS.tsv")
    unconditional_keys = {(row["gdt739_dispatch_id"], row["candidate_carrier"]) for row in unconditional}
    check(len(unconditional) == len(unconditional_keys) == 6 and unconditional_keys == set(expected_unconditioned), "six carrier-unconditioned coverage pairs exactly enumerated")
    check(unconditional_keys == {
        ("G739-D0027", "MATERIAL"), ("G739-D0028", "PREPARATION"),
        ("G739-D0041", "MATERIAL"), ("G739-D0045", "MATERIAL"),
        ("G739-D0075", "PREPARATION"), ("G739-D0187", "MATERIAL"),
    }, "unconditioned coverage identities exact")
    for row in unconditional:
        source = dispatch_map[row["gdt739_dispatch_id"]]
        patch = source_patch_map[row["gdt739_dispatch_id"]]
        expected = expected_unconditioned[(row["gdt739_dispatch_id"], row["candidate_carrier"])]
        require(all(row[field] == source[source_field] for field, source_field in (("gdt738_patch_id", "patch_id"), ("page", "page"), ("locus", "locus"), ("target_ordinal", "token_ordinal"), ("target_surface", "surface"), ("opaque_head_id", "opaque_head_id"))), f"unconditioned provenance: {row['coverage_id']}")
        require(row["coverage_unique_side"] == expected["side"] and row["coverage_screened"] == str(expected["screened"]) and row["coverage_exact_set_screened"] == str(expected["exact"]) and row["coverage_members"] == expected["members"], f"unconditioned coverage: {row['coverage_id']}")
        require(row["formal_direction_match"] == str(expected["formal_match"]), f"unconditioned direction: {row['coverage_id']}")
        request_matches = int(carriers(source["carrier_dispatch"]) == {row["candidate_carrier"]})
        require(row["gdt739_requested_carrier_dispatch"] == source["carrier_dispatch"] and row["requested_candidate_matches_scan"] == str(request_matches), f"unconditioned request comparison: {row['coverage_id']}")
        require(row["gdt742_carrier_dispatch"] == patch["gdt742_carrier_dispatch"] and row["prior_carrier_matches_scan"] == str(int(patch["gdt742_carrier_dispatch"] == row["candidate_carrier"])), f"unconditioned prior comparison: {row['coverage_id']}")
        require(row["new_page_or_transcription"] == row["literal_plaintext_claimed"] == row["component_export_credit"] == "0", f"unconditioned ceiling: {row['coverage_id']}")
    check({row["gdt739_dispatch_id"] for row in unconditional if row["requested_candidate_matches_scan"] == "0"} == {"G739-D0027", "G739-D0187"}, "two request-conditioning countercases exposed")

    axis_rows = read_tsv(art / "AXIS_5_INHERITED_FAVORED_CENSUS.tsv")
    bilateral_ids = {row["gdt739_dispatch_id"] for row in target_runs if row["bilateral_favored_axis_support"] == "1"}
    check(len(axis_rows) == 5 and {row["gdt739_dispatch_id"] for row in axis_rows} == bilateral_ids, "five bilateral favored-axis targets")
    check({row["gdt739_dispatch_id"] for row in axis_rows if row["bilateral_two_by_two_favored_axis_support"] == "1"} == {"G739-D0040"}, "D0040 alone has two-by-two favored HOT support")

    candidates = read_tsv(art / "CANDIDATE_4_REMAINING_ROLE_ADJUDICATION.tsv")
    source_open = {row["adjudication_id"]: row for row in source_candidates if row["gdt742_role_active"] == "0"}
    check(len(candidates) == len(source_open) == 4 and {row["gdt742_adjudication_id"] for row in candidates} == set(source_open), "four remaining candidate roles exactly entered post-decision")
    for row in candidates:
        source = source_open[row["gdt742_adjudication_id"]]
        contact = r2_map[row["attachment_contact_id"]]
        role = row["candidate_role"]
        expected = contact["gdt743_axis_role_retained" if role == "AXIS" else "gdt743_carrier_role_retained"]
        require(all(row[field] == source[field] for field in ("attachment_contact_id", "gdt739_dispatch_id", "page", "locus", "target_surface", "candidate_role")), f"candidate provenance: {row['adjudication_id']}")
        require(row["gdt743_role_active"] == expected and row["changed_from_gdt742"] == str(int(source["gdt742_role_active"] != expected)), f"candidate result: {row['adjudication_id']}")
        require(row["renderer_license"] == expected and row["literal_plaintext_claimed"] == row["component_export_credit"] == "0", f"candidate licence ceiling: {row['adjudication_id']}")
    check(True, "all four candidate roles retain exact provenance")
    check({(row["gdt739_dispatch_id"], row["candidate_role"]) for row in candidates if row["changed_from_gdt742"] == "1"} == {("G739-D0075", "CARRIER")}, "only D0075 carrier is promoted")
    check(Counter(row["gdt743_status"] for row in candidates) == Counter({"HOLD_OPEN_COLLISION": 2, "HOLD_FAVORED_INTERSECTION_LEAD": 1, "PROMOTE_PROVISIONAL_COMPOSITE_RUN_CARRIER": 1}), "candidate status census")

    patches = read_tsv(art / "TARGET_202_RENDERER_PATCH_V5.tsv")
    check(len(patches) == len({row["gdt743_patch_id"] for row in patches}) == 202, "202 unique renderer patches")
    check({row["gdt739_dispatch_id"] for row in patches} == set(source_patch_map), "renderer exactly covers GDT742")
    independently_active_by_dispatch: dict[str, list[tuple[dict[str, str], dict[str, object]]]] = defaultdict(list)
    for contact_id, expected in expected_r2.items():
        if int(expected["carrier"]):
            contact = source_r2[contact_id]
            independently_active_by_dispatch[contact["dispatch_id"]].append((contact, expected))
    changed_patches: dict[str, dict[str, str]] = {}
    for row in patches:
        source = source_patch_map[row["gdt739_dispatch_id"]]
        carrier = source["gdt742_carrier_dispatch"]
        active = independently_active_by_dispatch.get(row["gdt739_dispatch_id"], [])
        coverage_length = 0
        if carrier == "OPEN" and active:
            choices = {
                "_".join(candidate for candidate in CARRIER_ORDER if candidate in carriers(contact["target_wanted_carrier_set"]))
                for contact, _ in active
            }
            require(len(choices) == 1 and "" not in choices, f"independent carrier unique: {row['gdt743_patch_id']}")
            carrier = next(iter(choices))
            lengths = {
                int(run_map[contact["dispatch_id"]][f"{'left' if contact['side'] == 'L' else 'right'}_requested_carrier_coverage_screened"])
                for contact, _ in active
            }
            require(len(lengths) == 1, f"independent coverage length unique: {row['gdt743_patch_id']}")
            coverage_length = next(iter(lengths))
        render = (
            source["gdt742_working_render_de"]
            if carrier == source["gdt742_carrier_dispatch"]
            else independent_render(source, carrier, coverage_length)
        )
        shared = set(source) & set(row)
        require(all(row[field] == source[field] for field in shared), f"patch provenance: {row['gdt743_patch_id']}")
        require(row["gdt743_dimension_dispatch"] == source["gdt742_dimension_dispatch"] and row["gdt743_state_mode"] == source["gdt742_state_mode"], f"patch dimension/mode: {row['gdt743_patch_id']}")
        require(row["gdt743_carrier_dispatch"] == carrier and row["gdt743_working_render_de"] == render, f"patch carrier/render: {row['gdt743_patch_id']}")
        expected_changed = int(carrier != source["gdt742_carrier_dispatch"] or render != source["gdt742_working_render_de"])
        expected_specific = int(int(source["axis_specific_dispatch_retained"]) or carrier != "OPEN" or source["gdt742_state_mode"] == "PROCESS_RESULT")
        require(row["changed_from_gdt742"] == str(expected_changed) and row["carrier_locally_bound_gdt743"] == str(int(carrier != "OPEN")) and row["specific_local_dispatch_gdt743"] == str(expected_specific), f"patch delta/specificity: {row['gdt743_patch_id']}")
        expected_override_count = sum(
            int(expected["override"])
            for contact_id, expected in expected_r2.items()
            if source_r2[contact_id]["dispatch_id"] == row["gdt739_dispatch_id"]
        )
        expected_trace = "PROVISIONAL_REQUESTED_CARRIER_COVERAGE_ANALOGY" if expected_changed else "GDT742_RENDER_INHERITED"
        require(row["gdt743_rule_trace"] == expected_trace and row["active_run_override_contacts"] == str(expected_override_count), f"patch trace/override wiring: {row['gdt743_patch_id']}")
        require(row["dispatcher_uses_dispatch_id_or_locus_gdt743"] == "0", f"patch id-use guard: {row['gdt743_patch_id']}")
        if expected_changed:
            changed_patches[row["gdt739_dispatch_id"]] = row
    check(True, "all 202 renderer rows independently recompute")
    check(set(changed_patches) == {"G739-D0075"}, "exactly D0075 renderer changes")
    check(changed_patches["G739-D0075"]["gdt743_working_render_de"] == "Skalarstufe II [Carrier=PREPARATION; Dimension offen; provisorischer R4-Lauf]", "D0075 receives bracketed carrier-only working render")
    check(sum(int(row["axis_specific_dispatch_retained"]) for row in patches) == 36 and sum(int(row["carrier_locally_bound_gdt743"]) for row in patches) == 46, "renderer has 36 axes and 46 carriers")
    check(sum(int(row["specific_local_dispatch_gdt743"]) for row in patches) == 59 and sum(row["specific_local_dispatch_gdt743"] == "0" for row in patches) == 143, "renderer has 59 specific and 143 open")

    focus = read_tsv(art / "FOCUS_3_EXTENSION_REVIEW.tsv")
    focus_ids = {row["gdt739_dispatch_id"] for row in candidates}
    source_focus_map = {row["gdt739_dispatch_id"]: row for row in source_focus}
    patch_map = {row["gdt739_dispatch_id"]: row for row in patches}
    check(len(focus) == 3 and {row["gdt739_dispatch_id"] for row in focus} == focus_ids, "three focus lines exactly cover remaining targets")
    for row in focus:
        source = source_focus_map[row["gdt739_dispatch_id"]]
        require(all(row[field] == source[field] for field in ("page", "locus", "target_ordinal", "target_surface", "line_eva_cached", "radius_two_frame_manuscript_order")), f"focus provenance: {row['focus_id']}")
        require(row["gdt742_target_render_de"] == patch_map[row["gdt739_dispatch_id"]]["gdt742_working_render_de"] and row["gdt743_target_render_de"] == patch_map[row["gdt739_dispatch_id"]]["gdt743_working_render_de"], f"focus renderer: {row['focus_id']}")
        require(row["new_page_or_transcription"] == "0" and "no plaintext clause" in row["reader_note"], f"focus ceiling: {row['focus_id']}")
    check(True, "all focus rows retain exact cached source lines")
    reader = (art / "GDT743_RUN_INTERSECTION_READER.md").read_text(encoding="utf-8")
    check(all(row["focus_id"] in reader and row["line_eva_cached"] in reader for row in focus), "reader contains all focus lines")
    check("not independent" in reader and "not decoded" in reader, "reader exposes provisional ceiling")
    check("exclusions by the" in reader and "gate: 0" in reader and "does not solve the R2 collision" in reader, "reader exposes one-to-one zero-exclusion ablation")
    check("conditioned on each target's inherited favored-axis tag" in reader and "not an independent axis discovery" in reader, "reader exposes inherited HOT conditioning")
    check("D0027" in reader and "D0187" in reader and "Coverage alone therefore cannot name the carrier" in reader, "reader exposes unconditioned countercases")
    check("exact carrier-set prefix" in reader and "exclude PROCESS+PASS+CLOSE" in reader, "reader exposes strict sensitivities")

    edges = read_tsv(art / "GDT743_GDT388_RUN_OVERRIDE_EDGE_PACKET.tsv")
    check(len(edges) == 1 and edges[0]["page"] == "f111v" and edges[0]["relation_type"] == "REQUESTED_CARRIER_COVERAGE_ANALOGY", "one exact D0075 provisional edge")
    check(edges[0]["eligibility_status"] == "INELIGIBLE_FORMAL_ATTACHMENT_EDGE", "run edge explicitly ineligible")
    intake = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(art / "GDT743_GDT388_RUN_OVERRIDE_EDGE_PACKET.tsv")],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    intake_payload = json.loads(intake.stdout)
    check(intake.returncode == 1 and intake_payload["status"] == "INVALID_PACKET", "GDT388 intake rejects provisional run edge")
    check(not intake_payload["score_ready"] and not intake_payload["capacity_gate_50_edges_5_folios"] and not intake_payload["holdout_gate"] and not intake_payload["mobile_null_gate"], "all edge readiness gates remain closed")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT743_R2_RUN_INTERSECTION_ADJUDICATION_V1" and result["status"] == STATUS, "result schema and status")
    check(result["scope"] == {"f84_used": False, "f84r_used": False, "focus_cached_lines": 3, "inherited_allowlist_pages": 179, "new_pages_used": 0, "radius_two_contacts": 41, "remaining_candidate_roles_entered_post_decision": 4, "renderer_positions": 202, "window_rows": 1373}, "result scope")
    check(result["requested_carrier_coverage_census"] == {
        "new_run_override_contacts": 1, "new_run_override_roles": 1,
        "raw_ge3_targets": 8, "screened_unique_ge3_targets": 4,
        "screened_unique_previously_carrier_bound": 3,
        "unconditioned_request_mismatches": 2,
        "unconditioned_target_carrier_pairs": 6,
    }, "result requested-carrier coverage census")
    check(result["r2_ablation"] == {
        "excluded_by_coverage_gate": 0, "post_coverage_gate_triggers": 1,
        "relaxed_reverse_full_carrier_triggers": 1,
    }, "result R2 ablation")
    check(result["sensitivity"] == sensitivity, "result records all sensitivity identities")
    check(result["axis_census"] == {"bilateral_favored_axis_targets": 5, "bilateral_two_by_two_targets": 1, "favored_partial_r2_leads": 1, "new_axis_roles": 0}, "result axis census")
    check(result["roles"] == {"gdt742_active_r2_roles": 4, "gdt743_active_r2_roles": 5, "remaining_open_candidate_roles": 3, "remaining_open_candidate_targets": 3}, "result role census")
    check(result["renderer"] == {"axis_specific_occurrences": 36, "carrier_bound_occurrences": 46, "changed_from_gdt742": 1, "fully_open_occurrences": 143, "specific_occurrences": 59}, "result renderer census")
    check(result["edge_intake"] == {"expected_status": "INVALID_PACKET", "packet_rows": 1, "score_ready": False}, "result edge summary")
    check(result["claims"] == {
        "components_exported": 0, "lexemes_identified": 0, "literal_patients_or_species": 0,
        "new_axes": 0, "new_pages": 0, "plaintext_clauses": 0, "unseen_forms_licensed": 0,
    }, "result claims remain exact zero set")
    check(result["next_route"] == "CONCRETE_RECURRENT_WHOLE_FIELD_BRIDGE_ACROSS_MULTIPLE_CACHED_CONTEXTS", "result records concrete-whole pivot")
    for name in HASHED_BY_RESULT:
        rel = str(BASE / "artifacts" / name)
        require(result["artifact_hashes"][rel] == sha256(art / name), f"result hash: {name}")
    check(set(result["artifact_hashes"]) == {str(BASE / "artifacts" / name) for name in HASHED_BY_RESULT}, "result binds exactly ten artifacts")

    with tempfile.TemporaryDirectory(prefix="gdt743-replay-") as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        require(completed.returncode == 0, "builder replay command")
        for name in GENERATED:
            require((replay / name).is_file(), f"replay output missing: {name}")
            require(sha256(replay / name) == sha256(art / name), f"byte replay: {name}")
    check(True, "builder replay is byte-identical")

    payload = {
        "status": "PASS", "checks_passed": len(checks),
        "builder_replay": "BYTE_IDENTICAL", "edge_intake": "INVALID_PACKET",
        "new_renderer_roles": {"carrier": 1, "axis": 0},
        "checks": checks,
    }
    if not args.no_write:
        (art / "VALIDATION.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "status": "PASS", "checks_passed": len(checks),
        "builder_replay": "BYTE_IDENTICAL", "edge_intake": "INVALID_PACKET",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
