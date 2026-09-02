#!/usr/bin/env python3
"""Independent audit and byte replay for GDT741."""

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
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt741_local_attachment_boundary_relay_grammar")
EXP = ROOT / BASE
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
G740 = ROOT / "experiments/yolo/gdt740_local_host_attachment_adjudication"
G740_ART = G740 / "artifacts"
G739_ART = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/artifacts"
STATUS = (
    "PASS__ID_FREE_GRAMMAR_REPLAYS_13_OF_13_OVERRIDES__ZERO_103_ROLE_FLAG_ERRORS__"
    "EIGHT_OF_EIGHT_RESULT_MODES__TWO_SINGLETON_RELAYS_EXPLICIT__"
    "SIX_OPEN_COLLISION_ROLE_CANDIDATES__NO_NEW_RENDER_CHANGE__"
    "ZERO_LEXEME_OR_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "CONTACT_103_GRAMMAR_DISPATCH.tsv", "TARGET_95_GRAMMAR_FEATURES.tsv",
    "OVERRIDE_13_ID_FREE_REPLAY.tsv", "RULE_10_TRIGGER_CENSUS.tsv",
    "R2_8_STRICT_AND_OPEN_COLLISION_CANDIDATES.tsv",
    "GDT741_GDT388_OPEN_COLLISION_EDGE_PACKET.tsv",
    "TARGET_202_RENDERER_PATCH_V3.tsv", "PASSAGE_20_GRAMMAR_REPLAY.tsv",
    "GDT741_BOUNDARY_RELAY_GRAMMAR_READER.md", "RESULT.json",
)
RULE_IDS = ("G00", "G01", "G02", "G03", "G04", "G05", "G06A", "G06C", "G07", "G08")
RETIRED = ("pulver", "samen", "saat", "wurzel", "holz")
QUALITY = {"HOT", "COLD", "DRY", "MOIST"}
CARRIERS = {"PREPARATION", "MATERIAL", "PART"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def split_values(value: str, separator: str = "|") -> set[str]:
    if value in {"", "NONE", "NA", "OPEN", "NOT_APPLICABLE"}:
        return set()
    return set(value.split(separator))


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
    check(manifest["experiment_id"] == "GDT741", "manifest experiment id")
    check(manifest["slug"] == "local_attachment_boundary_relay_grammar", "manifest slug")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed selectors forbidden")
    placeholder = (
        manifest["status"] == "REGISTERED_UNSCORED" and manifest["inputs"] == []
        and manifest["outputs"] == []
        and manifest["validation"] == {"artifact": None, "status": "NOT_RUN"}
    )
    if placeholder:
        check(True, "manifest placeholder accepted before sealing")
    else:
        check(manifest["status"] == STATUS, "manifest status")
        check(manifest["validation"] == {"artifact": str(VALIDATION_REL), "status": "PASS"}, "manifest validation contract")
        check(bool(manifest["inputs"]) and bool(manifest["outputs"]), "sealed manifest has bindings")
        for binding in manifest["inputs"]:
            path = ROOT / binding["path"]
            require(not Path(binding["path"]).is_absolute(), f"absolute input: {binding['path']}")
            require(path.is_file() and sha256(path) == binding["sha256"], f"input mismatch: {binding['path']}")
        check(True, "all manifest inputs exist and hash-match")
        expected = {str(BASE / "artifacts" / name) for name in GENERATED} | {str(VALIDATION_REL)}
        check(expected <= {row["path"] for row in manifest["outputs"]}, "manifest binds generated outputs")
        for binding in manifest["outputs"]:
            if binding["path"] == str(VALIDATION_REL):
                continue
            path = ROOT / binding["path"]
            require(path.is_file() and sha256(path) == binding["sha256"], f"output mismatch: {binding['path']}")
        check(True, "all non-validation outputs hash-match")

    check(art.is_dir(), "artifact directory exists")
    check(all((art / name).is_file() for name in GENERATED), "all generated artifacts exist")

    rules = read_tsv(EXP / "src/GRAMMAR_RULES.tsv")
    check(tuple(row["rule_id"] for row in rules) == RULE_IDS, "ten ordered grammar rules")
    check(all(not re.search(r"G739-D\d|f\d+[rv]", row["feature_condition"]) for row in rules), "rule conditions contain no dispatch id or locus")
    run_text = RUN.read_text(encoding="utf-8")
    check(
        "G739-D0" not in run_text
        and not re.search(r"[\"']f\d+[rv](?:\d+)?[\"']", run_text),
        "dispatcher source hardcodes no target id or locus",
    )
    check(
        run_text.index("patches, target_rows, decisions = build_renderer_and_targets(")
        < run_text.index("override_rows = read_tsv"),
        "manual override table enters only after grammar decisions",
    )
    tree = ast.parse(run_text)
    field_sets: dict[str, tuple[str, ...]] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in {"DECISION_DISPATCH_FIELDS", "DECISION_CONTACT_FIELDS"}:
                field_sets[node.targets[0].id] = tuple(ast.literal_eval(node.value))
    expected_decision_dispatch_fields = (
        "state_mode", "favored_axis_not_automatic", "dimension_dispatch",
        "carrier_dispatch", "surface", "line_position", "level",
        "specific_local_dispatch", "selecting_anchor_distance",
    )
    expected_decision_contact_fields = (
        "distance", "selected_roles", "side", "target_ordinal", "signed_offset",
        "neighbor_ordinal", "neighbor_axis_tags", "neighbor_scalar_host_types",
        "formal_role_direction_match", "guarded_reader_exact_pair_occurrences",
        "strict_axis_relay_candidate", "strict_carrier_relay_candidate",
        "opposite_reader_exact", "opposite_known", "opposite_quality_set",
    )
    check(
        field_sets == {
            "DECISION_DISPATCH_FIELDS": expected_decision_dispatch_fields,
            "DECISION_CONTACT_FIELDS": expected_decision_contact_fields,
        },
        "decision records equal the independent identity/outcome-free field contract",
    )
    forbidden_decision_fields = {
        "dispatch_id", "patch_id", "occurrence_id", "page", "locus", "window_id",
        "attachment_contact_id", "attachment_decision", "axis_role_retained",
        "carrier_role_retained", "renderer_role_retained", "gdt740_working_render_de",
        "gdt740_dimension_dispatch", "gdt740_carrier_dispatch", "gdt740_state_mode",
        "mode_matches_gdt740", "render_matches_gdt740", "functional_match_gdt740",
        "manual_reason", "role_effect", "mode_effect", "tier_override",
    }
    dispatcher_source = run_text[
        run_text.index("def adjudicate_target("):run_text.index("def build_renderer_and_targets(")
    ]
    check(
        not any(f'[{key!r}]' in dispatcher_source or f'["{key}"]' in dispatcher_source for key in forbidden_decision_fields),
        "dispatcher body cannot address forbidden identity or outcome fields",
    )

    source_contacts = read_tsv(G740_ART / "SELECTED_103_CONTACT_ATTACHMENT.tsv")
    source_contact_map = {row["attachment_contact_id"]: row for row in source_contacts}
    source_ring = read_tsv(G740_ART / "TYPED_104_RING_EVIDENCE.tsv")
    source_patches = read_tsv(G740_ART / "TARGET_202_RENDERER_PATCH_V2.tsv")
    source_patch_map = {row["gdt739_dispatch_id"]: row for row in source_patches}
    source_targets = read_tsv(G740_ART / "TARGET_95_ATTACHMENT_ADJUDICATION.tsv")
    source_windows = read_tsv(G739_ART / "WINDOW_202_TOKEN_AUDIT.tsv")
    window_map = {(row["patch_id"], row["side"], row["distance"]): row for row in source_windows}
    source_dispatches = {
        row["dispatch_id"]: row for row in read_tsv(G739_ART / "DIMENSION_202_DISPATCH.tsv")
    }
    check(len(source_ring) == 104 and sum(row["conflict_only_nonbinding_contact"] == "1" for row in source_ring) == 1, "104 ring rows include one nonbinding conflict")
    check(len(source_contacts) == 103 and len(source_contact_map) == 103, "103 source binding contacts")

    contacts = read_tsv(art / "CONTACT_103_GRAMMAR_DISPATCH.tsv")
    check(len(contacts) == len({row["attachment_contact_id"] for row in contacts}) == 103, "103 unique grammar contact rows")
    check({row["attachment_contact_id"] for row in contacts} == set(source_contact_map), "grammar contact deck equals GDT740 deck")
    for row in contacts:
        source = source_contact_map[row["attachment_contact_id"]]
        dispatch = source_dispatches[row["dispatch_id"]]
        require(all(row[field] == source[field] for field in (
            "window_id", "dispatch_id", "patch_id", "page", "locus", "target_ordinal",
            "target_surface", "selected_roles", "side", "signed_offset", "distance",
            "neighbor_ordinal", "neighbor_surface", "neighbor_axis_tags",
            "neighbor_scalar_host_types", "formal_role_direction_match",
            "guarded_reader_exact_pair_occurrences",
            "guarded_reader_exact_full_frame_occurrences",
            "intervening_emits_own_unit", "intervening_strict_initial_head",
            "intervening_another_gdt738_target",
        )), f"contact provenance: {row['attachment_contact_id']}")
        require(row["axis_flag_matches_gdt740"] == row["carrier_flag_matches_gdt740"] == row["role_flags_match_gdt740"] == "1", f"contact flag replay: {row['attachment_contact_id']}")
        require(row["predicted_axis_role_retained"] == source["axis_role_retained"], f"axis replay: {row['attachment_contact_id']}")
        require(row["predicted_carrier_role_retained"] == source["carrier_role_retained"], f"carrier replay: {row['attachment_contact_id']}")
        require(row["literal_plaintext_claimed"] == row["component_export_credit"] == "0", f"contact exports zero: {row['attachment_contact_id']}")
        wanted = split_values(dispatch["carrier_dispatch"], "_") & CARRIERS
        require(row["target_family"] == dispatch["family"] and row["target_level"] == dispatch["level"], f"target class: {row['attachment_contact_id']}")
        require(row["target_favored_axis"] == dispatch["favored_axis_not_automatic"] and row["target_dimension"] == dispatch["dimension_dispatch"] and row["target_prior_state_mode"] == dispatch["state_mode"], f"target semantic features: {row['attachment_contact_id']}")
        require(split_values(row["target_wanted_carrier_set"]) == wanted, f"target carrier set: {row['attachment_contact_id']}")
        if row["distance"] == "2":
            middle = window_map[(row["patch_id"], row["side"], "1")]
            require(row["intervening_surface"] == middle["neighbor_surface"], f"middle surface: {row['attachment_contact_id']}")
            require(row["middle_reader_exact"] == middle["neighbor_reader_exact"], f"middle exactness: {row['attachment_contact_id']}")
            require(row["middle_known"] == str(int(middle["neighbor_unknown_v99r7"] == "0")), f"middle known: {row['attachment_contact_id']}")
            require(row["middle_positive_host_eligible"] == middle["eligible_local_anchor"], f"middle positive-host eligibility: {row['attachment_contact_id']}")
            require(row["middle_ineligibility_reasons"] == middle["ineligibility_reasons"], f"middle ineligibility reason: {row['attachment_contact_id']}")
            host_tags = split_values(row["neighbor_axis_tags"])
            host_scalars = split_values(row["neighbor_scalar_host_types"])
            middle_tags = split_values(middle["axis_tags"])
            middle_scalars = split_values(middle["scalar_host_types"])
            expected_barrier = (
                "UNKNOWN" if middle["neighbor_unknown_v99r7"] == "1"
                else "STRICT_HEAD" if row["intervening_strict_initial_head"] == "1"
                else "CLOSE" if "CLOSE" in middle_tags
                else "PROCESS_OR_PASS" if middle_tags & {"PROCESS", "PASS"}
                else "OPEN"
            )
            require(row["middle_barrier"] == expected_barrier, f"independent middle barrier: {row['attachment_contact_id']}")

            def axis_signature(tags: set[str], scalars: set[str]) -> str:
                quality = tags & QUALITY
                if dispatch["dimension_dispatch"] == "QUALITY_DEGREE" and "QUALITY_DEGREE" in scalars and quality:
                    return "QUALITY:" + "|".join(sorted(quality))
                if dispatch["dimension_dispatch"] == "AMOUNT_DOSE" and "AMOUNT_DOSE" in scalars:
                    return "AMOUNT"
                if dispatch["dimension_dispatch"] == "PROCESS_PASS" and "PROCESS_PASS" in scalars:
                    return "PROCESS_PASS"
                favored = dispatch["favored_axis_not_automatic"]
                if dispatch["state_mode"] != "NOT_APPLICABLE" and favored in tags:
                    return "STATE:" + favored
                return "NONE"

            host_signature = axis_signature(host_tags, host_scalars)
            middle_signature = axis_signature(middle_tags, middle_scalars)
            exact_axis = bool(
                host_signature == middle_signature
                and host_signature.startswith("QUALITY:")
                and len(host_tags & QUALITY) == len(middle_tags & QUALITY) == 1
            )
            partial_axis = bool(
                not exact_axis and "QUALITY_DEGREE" in host_scalars
                and "QUALITY_DEGREE" in middle_scalars
                and host_tags & middle_tags & QUALITY
            )
            common_frame = bool(
                int(row["guarded_reader_exact_full_frame_occurrences"]) >= 1
                and row["middle_reader_exact"] == "1" and row["middle_known"] == "1"
                and row["intervening_emits_own_unit"] == "1"
                and row["intervening_strict_initial_head"] == "0"
                and row["intervening_another_gdt738_target"] == "0"
            )
            selected = split_values(row["selected_roles"], "+")
            relaxed_axis = bool(
                common_frame and row["middle_barrier"] != "CLOSE"
                and "AXIS" in selected and (exact_axis or partial_axis)
            )
            strict_axis = bool(
                relaxed_axis and selected == {"AXIS"}
                and row["formal_role_direction_match"] == "1"
                and row["middle_barrier"] == "OPEN" and exact_axis
            )
            full_carrier = bool(
                wanted and wanted <= (host_tags & CARRIERS) and wanted <= (middle_tags & CARRIERS)
            )
            relaxed_carrier = bool(
                common_frame and row["middle_barrier"] != "CLOSE"
                and "CARRIER" in selected and full_carrier
            )
            strict_carrier = bool(
                relaxed_carrier and selected == {"CARRIER"}
                and row["formal_role_direction_match"] == "1"
                and row["middle_barrier"] == "OPEN"
            )
            require(row["host_axis_signature"] == host_signature and row["middle_axis_signature"] == middle_signature, f"independent axis signatures: {row['attachment_contact_id']}")
            require(row["axis_continuity"] == ("EXACT_SINGLE" if exact_axis else "PARTIAL" if partial_axis else "CONFLICT" if host_tags & QUALITY and middle_tags & QUALITY and not host_tags & middle_tags & QUALITY else "NONE"), f"independent axis continuity: {row['attachment_contact_id']}")
            require(row["carrier_continuity"] == ("FULL_WANTED" if full_carrier else "PARTIAL" if wanted and wanted & host_tags & middle_tags & CARRIERS else "NONE"), f"independent carrier continuity: {row['attachment_contact_id']}")
            require(row["relaxed_axis_relay_candidate"] == str(int(relaxed_axis)) and row["strict_axis_relay_candidate"] == str(int(strict_axis)), f"independent axis relay flags: {row['attachment_contact_id']}")
            require(row["relaxed_carrier_relay_candidate"] == str(int(relaxed_carrier)) and row["strict_carrier_relay_candidate"] == str(int(strict_carrier)), f"independent carrier relay flags: {row['attachment_contact_id']}")
        else:
            opposite_side = "R" if row["side"] == "L" else "L"
            opposite = window_map.get((row["patch_id"], opposite_side, "1"))
            if opposite is None:
                require(all(row[field] == "NA" for field in (
                    "opposite_reader_exact", "opposite_positive_host_eligible",
                    "opposite_ineligibility_reasons", "opposite_quality_set",
                )) and row["opposite_known"] == "0", f"absent opposite field: {row['attachment_contact_id']}")
            else:
                require(row["opposite_reader_exact"] == opposite["neighbor_reader_exact"], f"opposite exactness: {row['attachment_contact_id']}")
                require(row["opposite_known"] == str(int(opposite["neighbor_unknown_v99r7"] == "0")), f"opposite known: {row['attachment_contact_id']}")
                require(row["opposite_positive_host_eligible"] == opposite["eligible_local_anchor"], f"opposite positive-host eligibility: {row['attachment_contact_id']}")
                require(row["opposite_ineligibility_reasons"] == opposite["ineligibility_reasons"], f"opposite ineligibility reason: {row['attachment_contact_id']}")
                require(row["opposite_quality_set"] == ("|".join(sorted(split_values(opposite["axis_tags"]) & {"HOT", "COLD", "DRY", "MOIST"})) or "NONE"), f"opposite quality set: {row['attachment_contact_id']}")
            require(all(row[field] == "0" for field in (
                "strict_axis_relay_candidate", "strict_carrier_relay_candidate",
                "relaxed_axis_relay_candidate", "relaxed_carrier_relay_candidate",
            )), f"direct contact has no relay flags: {row['attachment_contact_id']}")
    check(True, "all contact provenance, atomic joins, relay flags, role replays and exports are coherent")
    check(Counter(row["grammar_rule_trace"] for row in contacts) == Counter({
        "DIRECT_DEFAULT": 53, "R2_DEFAULT_HOLD": 38, "G05": 4, "G01": 2,
        "G02": 2, "G06A": 1, "G03": 1, "G06C": 1, "G04": 1,
    }), "contact rule trace census")
    check(sum(int(row["predicted_renderer_role_retained"]) for row in contacts) == 57, "57 retained contact rows")
    check(sum(int(row["predicted_axis_role_retained"]) for row in contacts) == 36, "36 retained axis role flags")
    check(sum(int(row["predicted_carrier_role_retained"]) for row in contacts) == 44, "44 retained carrier role flags")
    r2 = [row for row in contacts if row["distance"] == "2"]
    check(len(r2) == 41 and Counter(row["middle_barrier"] for row in r2) == Counter({
        "OPEN": 24, "CLOSE": 9, "UNKNOWN": 6, "STRICT_HEAD": 1,
        "PROCESS_OR_PASS": 1,
    }), "41 radius-two barrier classes")
    check(sum(row["intervening_strict_initial_head"] == "1" for row in r2) == 2, "two radius-two strict heads including one unknown overlap")
    check(Counter(row["axis_continuity"] for row in r2) == Counter({
        "NONE": 25, "CONFLICT": 11, "PARTIAL": 3, "EXACT_SINGLE": 2,
    }), "radius-two axis continuity classes")
    check(Counter(row["carrier_continuity"] for row in r2) == Counter({
        "NONE": 33, "FULL_WANTED": 6, "PARTIAL": 2,
    }), "radius-two carrier continuity classes")
    check(
        all(row["middle_positive_host_eligible"] == "0" for row in r2 if row["strict_axis_relay_candidate"] == "1" or row["strict_carrier_relay_candidate"] == "1"),
        "strict relay middles remain relational-only rather than positive hosts",
    )

    targets = read_tsv(art / "TARGET_95_GRAMMAR_FEATURES.tsv")
    check(len(targets) == len({row["gdt739_dispatch_id"] for row in targets}) == 95, "95 unique target feature rows")
    source_target_map = {row["gdt739_dispatch_id"]: row for row in source_targets}
    check({row["gdt739_dispatch_id"] for row in targets} == set(source_target_map), "target feature deck exactly equals the GDT740 target set")
    contact_by_dispatch: dict[str, list[dict[str, str]]] = {}
    for row in contacts:
        contact_by_dispatch.setdefault(row["dispatch_id"], []).append(row)
    for row in targets:
        dispatch_id = row["gdt739_dispatch_id"]
        source_target = source_target_map[dispatch_id]
        dispatch = source_dispatches[dispatch_id]
        target_contacts = contact_by_dispatch.get(dispatch_id, [])
        require(row["gdt740_attachment_tier"] == source_target["attachment_tier"], f"target old-tier provenance: {dispatch_id}")
        require(all(row[field] == dispatch[field] for field in (
            "page", "locus", "token_ordinal", "surface", "opaque_head_id",
            "line_position", "family", "level",
        )), f"target dispatch provenance: {dispatch_id}")
        require(int(row["selected_contacts"]) == len(target_contacts), f"target selected-contact count: {dispatch_id}")
        require(int(row["direct_contacts"]) == sum(contact["distance"] == "1" for contact in target_contacts), f"target direct-contact count: {dispatch_id}")
        require(int(row["radius_two_contacts"]) == sum(contact["distance"] == "2" for contact in target_contacts), f"target radius-two count: {dispatch_id}")
    check(True, "all 95 target provenance and contact counts independently match")
    check(Counter(row["grammar_rule_trace"] for row in targets) == Counter({
        "DEFAULT": 79, "G07": 8, "G05": 2, "G06A": 1, "G03": 1,
        "G06C": 1, "G01": 1, "G04": 1, "G02": 1,
    }), "target rule trace census")
    check(all(row["role_flag_matches_gdt740"] == row["mode_matches_gdt740"] == row["render_matches_gdt740"] == "1" for row in targets), "all target functions replay GDT740")
    check(all(row["dispatcher_uses_dispatch_id_or_locus"] == row["plaintext_or_lexeme_claim"] == row["component_export_credit"] == "0" for row in targets), "target id and export claims zero")
    check(sum(row["target_prior_state_mode"] == "PROCESS_RESULT" for row in targets) == 8, "eight old result candidates")
    check(sum(row["target_prior_state_mode"] == "PROCESS_RESULT" and row["retained_direct_process_host_count"] == "1" for row in targets) == 1, "one direct-process result survives")
    check(sum(row["target_prior_state_mode"] == "PROCESS_RESULT" and row["retained_direct_process_host_count"] == "0" for row in targets) == 7, "seven unsupported results downgrade")
    singleton_columns = (
        "closure_crossing", "bilateral_role_split", "state_opposite_axis_rival",
        "pure_amount_field_owns_value", "strict_axis_relay_count", "strict_carrier_relay_count",
    )
    check(all(sum(int(row[column]) for row in targets) == 1 for column in singleton_columns), "six role rules remain singleton triggers")
    check(sum(int(row["single_host_composite_carrier_conflict"]) for row in targets) == 2, "two composite carrier conflicts")

    overrides = read_tsv(art / "OVERRIDE_13_ID_FREE_REPLAY.tsv")
    source_overrides = read_tsv(G740 / "src/MANUAL_ATTACHMENT_OVERRIDES.tsv")
    source_override_map = {row["dispatch_id"]: row for row in source_overrides}
    check(len(overrides) == 13 and len({row["gdt739_dispatch_id"] for row in overrides}) == 13, "thirteen former manual overrides audited")
    check(len(source_overrides) == 13 and {row["gdt739_dispatch_id"] for row in overrides} == set(source_override_map), "override replay deck exactly equals the bound manual source")
    for row in overrides:
        source = source_override_map[row["gdt739_dispatch_id"]]
        require(row["old_manual_role_effect"] == source["role_effect"], f"override role provenance: {row['gdt739_dispatch_id']}")
        require(row["old_manual_mode_effect"] == source["mode_effect"], f"override mode provenance: {row['gdt739_dispatch_id']}")
        require(row["old_manual_tier"] == source["tier_override"], f"override tier provenance: {row['gdt739_dispatch_id']}")
        require(row["old_manual_reason_audit_only"] == source["manual_reason"], f"override reason provenance: {row['gdt739_dispatch_id']}")
    check(True, "all old manual fields retain exact source provenance")
    check(all(row["functional_replay_match"] == "1" for row in overrides), "thirteen of thirteen overrides functionally replay")
    check(all(row["dispatcher_uses_this_id_or_locus"] == "0" for row in overrides), "override identifiers audit but do not dispatch")
    check(Counter(row["id_free_rule_trace"] for row in overrides) == Counter({
        "G07": 7, "G06A": 1, "G06C": 1, "G03": 1, "G04": 1,
        "G01": 1, "G02": 1,
    }), "override replay rules are exact")

    census = read_tsv(art / "RULE_10_TRIGGER_CENSUS.tsv")
    check(tuple(row["rule_id"] for row in census) == RULE_IDS, "ten-row rule census")
    census_map = {row["rule_id"]: row for row in census}
    check({rule: int(census_map[rule]["targets_triggered"]) for rule in ("G01", "G02", "G03", "G04", "G06A", "G06C")} == {rule: 1 for rule in ("G01", "G02", "G03", "G04", "G06A", "G06C")}, "six singleton census triggers")
    check(census_map["G05"]["targets_triggered"] == "2" and census_map["G05"]["contacts_traced"] == "4", "composite-carrier census")
    check(census_map["G06A"]["renderer_or_mode_changes_from_unrepaired_gdt739"] == census_map["G06C"]["renderer_or_mode_changes_from_unrepaired_gdt739"] == "0", "strict relays preserve their GDT739 render while replacing manual lookup")
    check(census_map["G07"]["cases_evaluated"] == "8" and census_map["G07"]["renderer_or_mode_changes_from_unrepaired_gdt739"] == "7", "result-mode census")

    sensitivity = read_tsv(art / "R2_8_STRICT_AND_OPEN_COLLISION_CANDIDATES.tsv")
    check(len(sensitivity) == 8 and Counter(row["candidate_role"] for row in sensitivity) == Counter({"AXIS": 4, "CARRIER": 4}), "eight relaxed role candidates split four/four")
    expected_sensitivity = {
        (row["attachment_contact_id"], role)
        for row in contacts
        for role, flag in (
            ("AXIS", row["relaxed_axis_relay_candidate"]),
            ("CARRIER", row["relaxed_carrier_relay_candidate"]),
        )
        if flag == "1"
    }
    check({(row["attachment_contact_id"], row["candidate_role"]) for row in sensitivity} == expected_sensitivity, "sensitivity deck exactly equals independently verified relaxed flags")
    for row in sensitivity:
        contact = source_contact_map[row["attachment_contact_id"]]
        grammar_contact = next(
            candidate for candidate in contacts
            if candidate["attachment_contact_id"] == row["attachment_contact_id"]
        )
        role = row["candidate_role"]
        strict = grammar_contact[
            "strict_axis_relay_candidate" if role == "AXIS" else "strict_carrier_relay_candidate"
        ]
        require(all(row[field] == expected for field, expected in (
            ("gdt739_dispatch_id", grammar_contact["dispatch_id"]),
            ("page", grammar_contact["page"]), ("locus", grammar_contact["locus"]),
            ("target_surface", grammar_contact["target_surface"]),
            ("side", grammar_contact["side"]),
            ("middle_surface", grammar_contact["intervening_surface"]),
            ("host_surface", grammar_contact["neighbor_surface"]),
            ("formal_direction_match", grammar_contact["formal_role_direction_match"]),
            ("middle_barrier", grammar_contact["middle_barrier"]),
            ("axis_continuity", grammar_contact["axis_continuity"]),
            ("carrier_continuity", grammar_contact["carrier_continuity"]),
        )), f"sensitivity contact provenance: {row['sensitivity_id']}")
        require(row["strict_grammar_active"] == row["renderer_license"] == strict, f"sensitivity strict licence: {row['sensitivity_id']}")
        require(row["candidate_status"] == ("ACTIVE_STRICT_RELAY" if strict == "1" else "OPEN_COLLISION"), f"sensitivity status: {row['sensitivity_id']}")
        require(row["current_gdt740_role_retained"] == contact["axis_role_retained" if role == "AXIS" else "carrier_role_retained"], f"sensitivity old-role provenance: {row['sensitivity_id']}")
    check(True, "all eight sensitivity rows retain exact contact, status and licence provenance")
    check(Counter(row["candidate_status"] for row in sensitivity) == Counter({"OPEN_COLLISION": 6, "ACTIVE_STRICT_RELAY": 2}), "two active relays and six open collisions")
    check(len({row["gdt739_dispatch_id"] for row in sensitivity if row["candidate_status"] == "OPEN_COLLISION"}) == 5, "six open roles occupy five targets")
    check(all(row["renderer_license"] == row["strict_grammar_active"] for row in sensitivity), "only strict candidates receive renderer licence")

    patches = read_tsv(art / "TARGET_202_RENDERER_PATCH_V3.tsv")
    check(len(patches) == len({row["gdt741_patch_id"] for row in patches}) == 202, "202 unique renderer patches")
    check({row["gdt739_dispatch_id"] for row in patches} == set(source_patch_map), "renderer covers GDT740 source")
    for row in patches:
        source = source_patch_map[row["gdt739_dispatch_id"]]
        require(row["gdt740_patch_id"] == source["gdt740_patch_id"], f"patch source id: {row['gdt741_patch_id']}")
        require(all(row[field] == source[field] for field in (
            "patch_id", "occurrence_id", "page", "locus", "token_index",
            "token_ordinal", "surface", "body", "opaque_head_id",
            "line_position", "family", "level",
        )), f"patch provenance fields: {row['gdt741_patch_id']}")
        require(row["gdt741_dimension_dispatch"] == source["gdt740_dimension_dispatch"], f"patch dimension replay: {row['gdt741_patch_id']}")
        require(row["gdt741_carrier_dispatch"] == source["gdt740_carrier_dispatch"], f"patch carrier replay: {row['gdt741_patch_id']}")
        require(row["gdt741_state_mode"] == source["gdt740_state_mode"], f"patch mode replay: {row['gdt741_patch_id']}")
        require(row["gdt741_working_render_de"] == source["gdt740_working_render_de"], f"patch render replay: {row['gdt741_patch_id']}")
        require(row["grammar_changed_from_gdt740"] == "0" and row["functional_match_gdt740"] == "1", f"patch functional replay: {row['gdt741_patch_id']}")
        require(all(row[field] == "0" for field in (
            "dispatcher_uses_dispatch_id_or_locus", "literal_patient_or_species_claimed",
            "literal_plaintext_claimed", "unconditional_global_export",
            "head_or_body_lexeme_credit", "component_export_credit", "unseen_form_export",
        )), f"patch exports zero: {row['gdt741_patch_id']}")
        require(not any(word in row["gdt741_working_render_de"].lower() for word in RETIRED), f"retired literal in render: {row['gdt741_patch_id']}")
    check(True, "all 202 patches replay GDT740 without ids or exports")
    check(sum(int(row["axis_specific_dispatch_retained"]) for row in patches) == 36, "renderer retains 36 axes")
    check(sum(int(row["carrier_locally_bound_retained"]) for row in patches) == 43, "renderer retains 43 carriers")
    check(sum(int(row["specific_local_dispatch_retained"]) for row in patches) == 56, "renderer retains 56 specific positions")
    check(sum(not int(row["specific_local_dispatch_retained"]) for row in patches) == 146, "renderer leaves 146 fully open")

    passages = read_tsv(art / "PASSAGE_20_GRAMMAR_REPLAY.tsv")
    check(len(passages) == len({row["passage_id"] for row in passages}) == 20, "twenty passage grammar replays")
    check(all(row["id_free_render_match"] == "1" for row in passages), "all passage target renders match")
    check(all("no clause or attachment is implied" in row["reader_note"] for row in passages), "passage displays disclaim clause and attachment")
    reader = (art / "GDT741_BOUNDARY_RELAY_GRAMMAR_READER.md").read_text(encoding="utf-8")
    check(all(row["passage_id"] in reader for row in passages), "reader contains every passage")

    edges = read_tsv(art / "GDT741_GDT388_OPEN_COLLISION_EDGE_PACKET.tsv")
    check(len(edges) == 5 and len({(row["pivot_locus"], row["target_locus"]) for row in edges}) == 5, "five unique open-collision geometries encode six candidate roles")
    check(all(row["eligibility_status"] == "INELIGIBLE_FORMAL_ATTACHMENT_EDGE" for row in edges), "all open-collision edges are explicitly ineligible")
    intake = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(art / "GDT741_GDT388_OPEN_COLLISION_EDGE_PACKET.tsv")],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    intake_payload = json.loads(intake.stdout)
    check(intake.returncode == 1 and intake_payload["status"] == "INVALID_PACKET", "GDT388 intake rejects relaxed semantic edges")
    check(not intake_payload["score_ready"] and not intake_payload["capacity_gate_50_edges_5_folios"] and not intake_payload["holdout_gate"] and not intake_payload["mobile_null_gate"], "all edge score-readiness gates remain closed")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT741_LOCAL_ATTACHMENT_BOUNDARY_RELAY_GRAMMAR_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"]["new_pages_used"] == 0 and result["scope"]["f84_used"] is False and result["scope"]["f84r_used"] is False, "result preserves sealed scope")
    check(result["replay"]["contact_role_flag_mismatches"] == result["replay"]["renderer_patch_mismatches"] == result["replay"]["passage_render_mismatches"] == 0, "result records zero replay mismatches")
    check(result["replay"]["former_manual_override_functional_matches"] == 13, "result records 13 override matches")
    check(result["grammar"]["dispatcher_uses_dispatch_id_or_locus"] is False and result["grammar"]["singleton_role_rules"] == 6, "result records id-free singleton grammar")
    check(result["renderer"] == {
        "axis_specific_occurrences": 36, "carrier_bound_occurrences": 43,
        "specific_occurrences": 56, "fully_open_occurrences": 146,
        "changed_from_gdt740": 0,
    }, "result renderer remains GDT740-equivalent")
    check(result["sensitivity"]["active_strict_roles"] == 2 and result["sensitivity"]["open_collision_roles"] == 6 and result["sensitivity"]["open_collision_targets"] == 5, "result sensitivity counts")
    check(result["sensitivity"]["projected_specific_if_all_open_collisions_spoken"] == 61 and result["sensitivity"]["projected_fully_open_if_all_open_collisions_spoken"] == 141, "result aggressive projection is 61/141")
    check(result["edge_intake"] == {"expected_status": "INVALID_PACKET", "packet_rows": 5, "score_ready": False}, "result edge intake summary")
    check(all(value == 0 for value in result["claims"].values()), "result claim ceiling remains zero")
    for name in GENERATED[:-1]:
        rel = str(BASE / "artifacts" / name)
        require(result["artifact_hashes"][rel] == sha256(art / name), f"result hash: {name}")
    check(True, "result artifact hashes match")

    with tempfile.TemporaryDirectory(prefix="gdt741-replay-") as temporary:
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
