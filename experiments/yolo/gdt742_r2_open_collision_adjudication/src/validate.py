#!/usr/bin/env python3
"""Independent atomic-feature audit and byte replay for GDT742."""

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
BASE = Path("experiments/yolo/gdt742_r2_open_collision_adjudication")
EXP = ROOT / BASE
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
G741_ART = ROOT / "experiments/yolo/gdt741_local_attachment_boundary_relay_grammar/artifacts"
COMPACT = (
    ROOT
    / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch"
    / "artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv"
)
STATUS = (
    "PARTIAL__ROLE_SEPARATED_CARRIER_RELAY_ADDS_TWO_TARGETS__"
    "FOUR_OF_EIGHT_R2_CANDIDATE_ROLES_ACTIVE__FOUR_OPEN_ROLES_ON_THREE_TARGETS__"
    "45_CARRIER_BOUND__58_SPECIFIC__144_OPEN__ZERO_NEW_AXIS__"
    "ZERO_LEXEME_OR_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "CONTACT_103_ROLE_SEPARATION_DISPATCH.tsv",
    "R2_32_FEATURE_CLASS_CENSUS.tsv",
    "CANDIDATE_8_ROLE_ADJUDICATION.tsv",
    "TARGET_202_RENDERER_PATCH_V4.tsv",
    "FOCUS_7_CACHED_LINE_REVIEW.tsv",
    "GDT742_GDT388_TWO_CARRIER_RELAY_EDGE_PACKET.tsv",
    "GDT742_ROLE_SEPARATION_READER.md",
    "RESULT.json",
)
HASHED_BY_RESULT = GENERATED[:-1]
DECISION_FIELDS = (
    "distance", "selected_roles", "formal_role_direction_match",
    "guarded_reader_exact_full_frame_occurrences", "middle_reader_exact",
    "middle_known", "intervening_emits_own_unit",
    "intervening_strict_initial_head", "intervening_another_gdt738_target",
    "middle_barrier", "target_wanted_carrier_set", "host_carrier_set",
    "middle_carrier_set", "axis_continuity",
)
CLASS_FIELDS = (
    "selected_roles", "formal_role_direction_match",
    "guarded_reader_exact_full_frame_occurrences", "middle_reader_exact",
    "middle_known", "intervening_emits_own_unit",
    "intervening_strict_initial_head", "intervening_another_gdt738_target",
    "middle_barrier", "axis_continuity", "carrier_continuity",
)
QUALITY = {"HOT", "COLD", "DRY", "MOIST"}
CARRIERS = {"PREPARATION", "MATERIAL", "PART"}
CARRIER_ORDER = ("PREPARATION", "MATERIAL", "PART")
ZERO_EXPORT_FIELDS = (
    "literal_patient_or_species_claimed", "literal_plaintext_claimed",
    "unconditional_global_export", "head_or_body_lexeme_credit",
    "component_export_credit", "unseen_form_export",
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


def split_values(value: str, separator: str = "|") -> set[str]:
    if value in {"", "NONE", "NA", "OPEN", "NOT_APPLICABLE"}:
        return set()
    return set(value.split(separator))


def independent_r2(row: dict[str, str]) -> dict[str, object]:
    """Recompute all GDT742 role predicates from GDT741's atomic columns."""
    if row["distance"] != "2":
        raise AssertionError("independent_r2 received a direct contact")
    selected = split_values(row["selected_roles"], "+")
    wanted = split_values(row["target_wanted_carrier_set"])
    host_carriers = split_values(row["host_carrier_set"])
    middle_carriers = split_values(row["middle_carrier_set"])
    host_quality = split_values(row["host_quality_set"])
    middle_quality = split_values(row["middle_quality_set"])
    host_scalar = split_values(row["host_scalar_class_set"])
    middle_scalar = split_values(row["middle_scalar_class_set"])
    middle_boundaries = split_values(row["middle_boundary_set"])

    if row["middle_known"] == "0":
        barrier = "UNKNOWN"
    elif row["intervening_strict_initial_head"] == "1":
        barrier = "STRICT_HEAD"
    elif "CLOSE" in middle_boundaries:
        barrier = "CLOSE"
    elif middle_boundaries & {"PROCESS", "PASS"}:
        barrier = "PROCESS_OR_PASS"
    else:
        barrier = "OPEN"

    exact_axis = bool(
        row["target_dimension"] == "QUALITY_DEGREE"
        and "QUALITY_DEGREE" in host_scalar
        and "QUALITY_DEGREE" in middle_scalar
        and host_quality == middle_quality
        and len(host_quality) == 1
    )
    partial_axis = bool(
        not exact_axis
        and "QUALITY_DEGREE" in host_scalar
        and "QUALITY_DEGREE" in middle_scalar
        and bool(host_quality & middle_quality & QUALITY)
    )
    if exact_axis:
        axis_continuity = "EXACT_SINGLE"
    elif partial_axis:
        axis_continuity = "PARTIAL"
    elif host_quality and middle_quality and not host_quality & middle_quality & QUALITY:
        axis_continuity = "CONFLICT"
    else:
        axis_continuity = "NONE"

    full_carrier = bool(wanted and wanted <= host_carriers and wanted <= middle_carriers)
    partial_carrier = bool(wanted & host_carriers & middle_carriers & CARRIERS)
    carrier_continuity = "FULL_WANTED" if full_carrier else "PARTIAL" if partial_carrier else "NONE"
    common = bool(
        int(row["guarded_reader_exact_full_frame_occurrences"]) >= 1
        and row["middle_reader_exact"] == "1"
        and row["middle_known"] == "1"
        and row["intervening_emits_own_unit"] == "1"
        and row["intervening_strict_initial_head"] == "0"
        and row["intervening_another_gdt738_target"] == "0"
    )
    open_direction = bool(common and barrier == "OPEN" and row["formal_role_direction_match"] == "1")
    axis_active = bool(open_direction and selected == {"AXIS"} and axis_continuity == "EXACT_SINGLE")
    carrier_active = bool(
        open_direction and full_carrier
        and (selected == {"CARRIER"} or selected == {"AXIS", "CARRIER"} and axis_continuity == "NONE")
    )
    trace = (
        "STRICT_AXIS_RELAY" if axis_active
        else "STRICT_CARRIER_RELAY" if carrier_active and selected == {"CARRIER"}
        else "ROLE_SEPARATED_CARRIER_RELAY" if carrier_active
        else "R2_HOLD"
    )
    return {
        "barrier": barrier, "axis_continuity": axis_continuity,
        "carrier_continuity": carrier_continuity, "common": int(common),
        "full_carrier": int(full_carrier), "axis_active": int(axis_active),
        "carrier_active": int(carrier_active), "trace": trace,
    }


def independent_open_scalar_render(source: dict[str, str], carrier: str) -> str:
    if source["family"] != "SCALAR" or source["gdt741_dimension_dispatch"] != "OPEN_SCALAR":
        raise AssertionError("new carrier is not attached to an open scalar source")
    genitive = {
        "PREPARATION": "der Zubereitung", "MATERIAL": "des Materials",
        "PART": "der Teilfraktion", "PREPARATION_MATERIAL": "des Zubereitungsmaterials",
        "PREPARATION_PART": "der Zubereitungsfraktion", "MATERIAL_PART": "des Materialteils",
        "PREPARATION_MATERIAL_PART": "der Zubereitungsfraktion",
    }[carrier]
    base = f"Skalarstufe {source['level']} {genitive}; Dimension offen"
    if source["surface"] == "sain" and source["line_position"] == "FIRST":
        base += "; Eintrag"
    elif source["surface"] == "rain":
        base += "; Abschlussbezug" if source["line_position"] == "LAST" else "; interner Rückbezug"
    elif source["surface"] == "lain":
        base = "interne " + base
    elif source["surface"] == "skaiin" and source["line_position"] == "FIRST":
        base += "; Eintrag"
    return base


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
    check(manifest["experiment_id"] == "GDT742", "manifest experiment id")
    check(manifest["slug"] == "r2_open_collision_adjudication", "manifest slug")
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
        expected_outputs = {
            str(BASE / name) for name in ("README.md", "METHOD.md", "PREREGISTRATION.md", "REPORT.md")
        } | {str(BASE / "src" / name) for name in ("run.py", "validate.py")} | {
            str(BASE / "artifacts" / name) for name in ("README.md", *GENERATED, "VALIDATION.json")
        }
        check(expected_outputs <= {row["path"] for row in manifest["outputs"]}, "manifest binds all experiment outputs")
        for binding in manifest["outputs"]:
            if binding["path"] == str(VALIDATION_REL):
                continue
            path = ROOT / binding["path"]
            require(path.is_file() and sha256(path) == binding["sha256"], f"output mismatch: {binding['path']}")
        check(True, "all non-validation outputs hash-match")

    check(art.is_dir(), "artifact directory exists")
    check(all((art / name).is_file() for name in GENERATED), "all generated artifacts exist")

    run_text = RUN.read_text(encoding="utf-8")
    check(
        "G739-D0" not in run_text and not re.search(r"[\"']f\d+[rv](?:\.\d+)?[\"']", run_text),
        "builder hardcodes no dispatch id or locus",
    )
    tree = ast.parse(run_text)
    declared: dict[str, tuple[str, ...]] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in {"DECISION_FIELDS", "CLASS_FIELDS"}:
                declared[node.targets[0].id] = tuple(ast.literal_eval(node.value))
    check(declared == {"DECISION_FIELDS": DECISION_FIELDS, "CLASS_FIELDS": CLASS_FIELDS}, "decision and class fields equal the independent whitelist")
    decision_source = run_text[run_text.index("def adjudicate_r2("):run_text.index("def contact_dispatch(")]
    forbidden = {
        "attachment_contact_id", "dispatch_id", "patch_id", "page", "locus",
        "target_surface", "neighbor_surface", "predicted_axis_role_retained",
        "predicted_carrier_role_retained", "renderer_role_retained",
        "gdt741_role_active", "candidate_status", "counterevidence",
    }
    check(
        not any(f'["{field}"]' in decision_source or f"['{field}']" in decision_source for field in forbidden),
        "adjudicator cannot address identity, surface or predecessor outcomes",
    )
    check(
        run_text.index("contacts = contact_dispatch(source_contacts)")
        < run_text.index("candidates = candidate_adjudication(source_candidates"),
        "candidate outcome deck enters only after role decisions",
    )

    source_contacts = read_tsv(G741_ART / "CONTACT_103_GRAMMAR_DISPATCH.tsv")
    source_candidates = read_tsv(G741_ART / "R2_8_STRICT_AND_OPEN_COLLISION_CANDIDATES.tsv")
    source_patches = read_tsv(G741_ART / "TARGET_202_RENDERER_PATCH_V3.tsv")
    check(len(source_contacts) == 103 and len(source_candidates) == 8 and len(source_patches) == 202, "fixed GDT741 source decks")
    check(not any(row["page"].startswith("f84") for row in source_contacts), "source contact deck excludes sealed pages")
    source_contact_map = {row["attachment_contact_id"]: row for row in source_contacts}

    contacts = read_tsv(art / "CONTACT_103_ROLE_SEPARATION_DISPATCH.tsv")
    check(len(contacts) == len({row["attachment_contact_id"] for row in contacts}) == 103, "103 unique contact decisions")
    check({row["attachment_contact_id"] for row in contacts} == set(source_contact_map), "contact output exactly covers GDT741")
    contact_map = {row["attachment_contact_id"]: row for row in contacts}
    shared_contact_fields = set(source_contacts[0]) & set(contacts[0])
    for row in contacts:
        source = source_contact_map[row["attachment_contact_id"]]
        require(all(row[field] == source[field] for field in shared_contact_fields), f"contact provenance: {row['attachment_contact_id']}")
        if row["distance"] == "2":
            expected = independent_r2(source)
            require(source["middle_barrier"] == expected["barrier"], f"independent barrier: {row['attachment_contact_id']}")
            require(source["axis_continuity"] == expected["axis_continuity"], f"independent axis continuity: {row['attachment_contact_id']}")
            require(source["carrier_continuity"] == expected["carrier_continuity"], f"independent carrier continuity: {row['attachment_contact_id']}")
            new_axis = int(expected["axis_active"])
            new_carrier = int(expected["carrier_active"])
            require(row["common_frame_recomputed"] == str(expected["common"]), f"common frame: {row['attachment_contact_id']}")
            require(row["full_carrier_continuity_recomputed"] == str(expected["full_carrier"]), f"carrier coverage: {row['attachment_contact_id']}")
            require(row["gdt742_rule_trace"] == expected["trace"], f"rule trace: {row['attachment_contact_id']}")
        else:
            new_axis = int(source["predicted_axis_role_retained"])
            new_carrier = int(source["predicted_carrier_role_retained"])
            require(row["gdt742_rule_trace"] == "GDT741_DIRECT_INHERITED", f"direct trace: {row['attachment_contact_id']}")
            require(row["common_frame_recomputed"] == "0", f"direct common-frame zero: {row['attachment_contact_id']}")
        old_axis = int(source["predicted_axis_role_retained"])
        old_carrier = int(source["predicted_carrier_role_retained"])
        require(row["gdt742_axis_role_retained"] == str(new_axis), f"new axis: {row['attachment_contact_id']}")
        require(row["gdt742_carrier_role_retained"] == str(new_carrier), f"new carrier: {row['attachment_contact_id']}")
        require(row["gdt742_renderer_role_retained"] == str(int(new_axis or new_carrier)), f"renderer role: {row['attachment_contact_id']}")
        require(row["axis_changed_from_gdt741"] == str(int(new_axis != old_axis)), f"axis delta: {row['attachment_contact_id']}")
        require(row["carrier_changed_from_gdt741"] == str(int(new_carrier != old_carrier)), f"carrier delta: {row['attachment_contact_id']}")
        require(row["role_changed_from_gdt741"] == str(int(new_axis != old_axis or new_carrier != old_carrier)), f"role delta: {row['attachment_contact_id']}")
        require(row["dispatcher_uses_dispatch_id_or_locus"] == row["literal_plaintext_claimed"] == row["component_export_credit"] == "0", f"contact zero export: {row['attachment_contact_id']}")
    check(True, "all 103 roles independently recompute from atomic fields")
    r2 = [row for row in contacts if row["distance"] == "2"]
    check(len(r2) == 41 and len(contacts) - len(r2) == 62, "41 radius-two and 62 direct contacts")
    check(Counter(row["middle_barrier"] for row in r2) == Counter({"OPEN": 24, "CLOSE": 9, "UNKNOWN": 6, "STRICT_HEAD": 1, "PROCESS_OR_PASS": 1}), "radius-two boundary census")
    check(Counter(row["axis_continuity"] for row in r2) == Counter({"NONE": 25, "CONFLICT": 11, "PARTIAL": 3, "EXACT_SINGLE": 2}), "radius-two axis continuity census")
    check(Counter(row["carrier_continuity"] for row in r2) == Counter({"NONE": 33, "FULL_WANTED": 6, "PARTIAL": 2}), "radius-two carrier continuity census")
    changed_contacts = {row["dispatch_id"] for row in contacts if row["role_changed_from_gdt741"] == "1"}
    check(changed_contacts == {"G739-D0143", "G739-D0164"}, "post-decision delta set is exactly the two carrier relays")
    check(sum(int(row["axis_changed_from_gdt741"]) for row in contacts) == 0, "zero axis changes")
    check(sum(int(row["carrier_changed_from_gdt741"]) for row in contacts) == 2, "two carrier changes")
    check(all(row["role_changed_from_gdt741"] == "0" for row in contacts if row["distance"] == "1"), "all direct contacts remain unchanged")
    check(sum(row["role_changed_from_gdt741"] == "0" for row in r2) == 39, "39 of 41 radius-two contacts remain unchanged")
    active_r2_roles = {
        (row["dispatch_id"], role)
        for row in r2
        for role, flag in (("AXIS", row["gdt742_axis_role_retained"]), ("CARRIER", row["gdt742_carrier_role_retained"]))
        if flag == "1"
    }
    check(active_r2_roles == {("G739-D0003", "AXIS"), ("G739-D0126", "CARRIER"), ("G739-D0143", "CARRIER"), ("G739-D0164", "CARRIER")}, "four active radius-two roles")
    by_dispatch: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in contacts:
        by_dispatch[row["dispatch_id"]].append(row)
    nearest_holds = {dispatch: by_dispatch[dispatch][0] for dispatch in ("G739-D0015", "G739-D0062", "G739-D0068", "G739-D0075", "G739-D0166")}
    check(nearest_holds["G739-D0062"]["carrier_continuity"] == "PARTIAL" and nearest_holds["G739-D0062"]["gdt742_carrier_role_retained"] == "0", "D0062 partial-coverage counterexample remains held")
    check(nearest_holds["G739-D0166"]["carrier_continuity"] == "NONE" and nearest_holds["G739-D0166"]["gdt742_carrier_role_retained"] == "0", "D0166 missing-middle counterexample remains held")
    check(nearest_holds["G739-D0075"]["formal_role_direction_match"] == "0" and nearest_holds["G739-D0075"]["gdt742_carrier_role_retained"] == "0", "D0075 reverse-direction carrier remains held")
    check(nearest_holds["G739-D0015"]["middle_barrier"] == "STRICT_HEAD" and nearest_holds["G739-D0015"]["gdt742_carrier_role_retained"] == "0", "D0015 strict-head carrier remains held")
    check(nearest_holds["G739-D0068"]["carrier_continuity"] == "NONE" and nearest_holds["G739-D0068"]["axis_continuity"] == "CONFLICT", "D0068 dual-failure counterexample remains held")

    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in r2:
        grouped[tuple(row[field] for field in CLASS_FIELDS)].append(row)
    classes = read_tsv(art / "R2_32_FEATURE_CLASS_CENSUS.tsv")
    check(len(grouped) == len(classes) == 32, "32 reduced outcome-free feature classes")
    check(sum(len(rows) > 1 for rows in grouped.values()) == 7, "seven reduced classes repeat")
    expected_keys = sorted(grouped)
    check(tuple(row["feature_class_id"] for row in classes) == tuple(f"G742-K{index:02d}" for index in range(1, 33)), "ordered feature-class ids")
    for output, key in zip(classes, expected_keys, strict=True):
        rows = grouped[key]
        signature = ";".join(f"{field}={value}" for field, value in zip(CLASS_FIELDS, key, strict=True))
        promotions = sum(int(row["carrier_changed_from_gdt741"]) for row in rows)
        active = sum(int(row["gdt742_renderer_role_retained"]) for row in rows)
        status = "REPEATED_ROLE_SEPARATION_PROMOTION" if promotions else "ACTIVE_STRICT_CLASS" if active else "REPEATED_HOLD_CLASS" if len(rows) > 1 else "SINGLETON_HOLD_CLASS"
        require(output["feature_signature"] == signature, f"class signature: {output['feature_class_id']}")
        require(output["contacts"] == str(len(rows)), f"class count: {output['feature_class_id']}")
        require(output["targets"] == str(len({row['dispatch_id'] for row in rows})), f"class targets: {output['feature_class_id']}")
        require(output["member_contact_ids_audit_only"] == "|".join(row["attachment_contact_id"] for row in rows), f"class contact audit: {output['feature_class_id']}")
        require(output["member_dispatch_ids_audit_only"] == "|".join(row["dispatch_id"] for row in rows), f"class target audit: {output['feature_class_id']}")
        old_patterns = "|".join(sorted({f"A{row['predicted_axis_role_retained']}C{row['predicted_carrier_role_retained']}" for row in rows}))
        new_patterns = "|".join(sorted({f"A{row['gdt742_axis_role_retained']}C{row['gdt742_carrier_role_retained']}" for row in rows}))
        require(output["gdt741_role_patterns"] == old_patterns and output["gdt742_role_patterns"] == new_patterns, f"class role patterns: {output['feature_class_id']}")
        require(output["new_carrier_promotions"] == str(promotions) and output["class_status"] == status, f"class decision: {output['feature_class_id']}")
        require(output["repeated_feature_class"] == str(int(len(rows) > 1)) and output["literal_plaintext_claimed"] == "0", f"class ceiling: {output['feature_class_id']}")
    check(True, "all 32 feature classes independently replay")
    promotion_classes = [row for row in classes if row["new_carrier_promotions"] != "0"]
    check(len(promotion_classes) == 1 and promotion_classes[0]["contacts"] == promotion_classes[0]["new_carrier_promotions"] == "2", "one repeated two-member promotion class")

    candidates = read_tsv(art / "CANDIDATE_8_ROLE_ADJUDICATION.tsv")
    source_candidate_map = {row["sensitivity_id"]: row for row in source_candidates}
    check(len(candidates) == 8 and len({row["adjudication_id"] for row in candidates}) == 8, "eight unique role adjudications")
    check({row["gdt741_sensitivity_id"] for row in candidates} == set(source_candidate_map), "candidate deck exactly covers GDT741 sensitivity")
    for row in candidates:
        source = source_candidate_map[row["gdt741_sensitivity_id"]]
        contact = contact_map[row["attachment_contact_id"]]
        role = row["candidate_role"]
        require(row["attachment_contact_id"] == source["attachment_contact_id"] and row["gdt739_dispatch_id"] == source["gdt739_dispatch_id"], f"candidate identity provenance: {row['adjudication_id']}")
        require(all(row[field] == source[field] for field in ("page", "locus", "target_surface", "candidate_role")), f"candidate surface provenance: {row['adjudication_id']}")
        require(all(row[field] == contact[source_field] for field, source_field in (("selected_roles", "selected_roles"), ("formal_direction_match", "formal_role_direction_match"), ("middle_barrier", "middle_barrier"), ("axis_continuity", "axis_continuity"), ("carrier_continuity", "carrier_continuity"))), f"candidate feature provenance: {row['adjudication_id']}")
        old = contact["predicted_axis_role_retained" if role == "AXIS" else "predicted_carrier_role_retained"]
        new = contact["gdt742_axis_role_retained" if role == "AXIS" else "gdt742_carrier_role_retained"]
        changed = str(int(old == "0" and new == "1"))
        expected_status = "PROMOTE_ROLE_SEPARATED_CARRIER" if changed == "1" else "ACTIVE_INHERITED_STRICT_RELAY" if new == "1" else "HOLD_OPEN_COLLISION"
        require(row["gdt741_role_active"] == old and row["gdt742_role_active"] == new and row["changed_from_gdt741"] == changed, f"candidate role outcome: {row['adjudication_id']}")
        require(row["gdt742_status"] == expected_status and row["renderer_license"] == new, f"candidate status and licence: {row['adjudication_id']}")
        require(row["literal_plaintext_claimed"] == row["component_export_credit"] == "0" and bool(row["working_reason"]), f"candidate ceiling: {row['adjudication_id']}")
    check(True, "all eight candidate roles retain source and rule provenance")
    check(Counter(row["candidate_role"] for row in candidates) == Counter({"AXIS": 4, "CARRIER": 4}), "candidate deck splits four axes and four carriers")
    check(Counter(row["gdt742_status"] for row in candidates) == Counter({"HOLD_OPEN_COLLISION": 4, "ACTIVE_INHERITED_STRICT_RELAY": 2, "PROMOTE_ROLE_SEPARATED_CARRIER": 2}), "candidate status census")
    check({row["gdt739_dispatch_id"] for row in candidates if row["changed_from_gdt741"] == "1"} == {"G739-D0143", "G739-D0164"}, "candidate promotions equal contact deltas")
    check({row["gdt739_dispatch_id"] for row in candidates if row["gdt742_role_active"] == "0"} == {"G739-D0040", "G739-D0075", "G739-D0184"}, "four open roles remain on three targets")

    patches = read_tsv(art / "TARGET_202_RENDERER_PATCH_V4.tsv")
    source_patch_map = {row["gdt739_dispatch_id"]: row for row in source_patches}
    check(len(patches) == len({row["gdt742_patch_id"] for row in patches}) == 202, "202 unique renderer patches")
    check({row["gdt739_dispatch_id"] for row in patches} == set(source_patch_map), "renderer exactly covers GDT741")
    for row in patches:
        source = source_patch_map[row["gdt739_dispatch_id"]]
        dispatch_contacts = by_dispatch.get(row["gdt739_dispatch_id"], [])
        active_carriers = [contact for contact in dispatch_contacts if contact["gdt742_carrier_role_retained"] == "1"]
        expected_carrier = source["gdt741_carrier_dispatch"]
        if expected_carrier == "OPEN" and active_carriers:
            sets = {tuple(carrier for carrier in CARRIER_ORDER if carrier in split_values(contact["target_wanted_carrier_set"])) for contact in active_carriers}
            require(len(sets) == 1, f"unambiguous carrier source: {row['gdt742_patch_id']}")
            expected_carrier = "_".join(next(iter(sets)))
        expected_render = source["gdt741_working_render_de"] if expected_carrier == source["gdt741_carrier_dispatch"] else independent_open_scalar_render(source, expected_carrier)
        expected_changed = int(expected_carrier != source["gdt741_carrier_dispatch"] or expected_render != source["gdt741_working_render_de"])
        expected_specific = int(int(source["axis_specific_dispatch_retained"]) or expected_carrier != "OPEN" or source["gdt741_state_mode"] == "PROCESS_RESULT")
        shared = ("gdt741_patch_id", "gdt739_dispatch_id", "patch_id", "occurrence_id", "page", "locus", "token_index", "token_ordinal", "surface", "body", "opaque_head_id", "line_position", "family", "level")
        require(all(row[field] == source[field] for field in shared), f"patch provenance: {row['gdt742_patch_id']}")
        require(row["gdt741_dimension_dispatch"] == row["gdt742_dimension_dispatch"] == source["gdt741_dimension_dispatch"], f"patch dimension: {row['gdt742_patch_id']}")
        require(row["gdt741_carrier_dispatch"] == source["gdt741_carrier_dispatch"] and row["gdt742_carrier_dispatch"] == expected_carrier, f"patch carrier: {row['gdt742_patch_id']}")
        require(row["gdt741_state_mode"] == row["gdt742_state_mode"] == source["gdt741_state_mode"], f"patch mode: {row['gdt742_patch_id']}")
        require(row["gdt741_working_render_de"] == source["gdt741_working_render_de"] and row["gdt742_working_render_de"] == expected_render, f"patch render: {row['gdt742_patch_id']}")
        require(row["axis_specific_dispatch_retained"] == source["axis_specific_dispatch_retained"], f"patch axis flag: {row['gdt742_patch_id']}")
        require(row["carrier_locally_bound_retained"] == str(int(expected_carrier != "OPEN")) and row["specific_local_dispatch_retained"] == str(expected_specific), f"patch specificity: {row['gdt742_patch_id']}")
        require(row["active_radius_two_carrier_contacts"] == str(sum(contact["distance"] == "2" and contact["gdt742_carrier_role_retained"] == "1" for contact in dispatch_contacts)), f"patch active relay count: {row['gdt742_patch_id']}")
        require(row["changed_from_gdt741"] == str(expected_changed) and row["gdt742_rule_trace"] == ("ROLE_SEPARATED_CARRIER_RELAY" if expected_changed else "GDT741_RENDER_INHERITED"), f"patch delta: {row['gdt742_patch_id']}")
        require(row["dispatcher_uses_dispatch_id_or_locus"] == "0" and all(row[field] == "0" for field in ZERO_EXPORT_FIELDS), f"patch zero export: {row['gdt742_patch_id']}")
    check(True, "all 202 renderer patches independently recompute")
    check(sum(int(row["axis_specific_dispatch_retained"]) for row in patches) == 36, "renderer has 36 axes")
    check(sum(int(row["carrier_locally_bound_retained"]) for row in patches) == 45, "renderer has 45 carriers")
    check(sum(int(row["specific_local_dispatch_retained"]) for row in patches) == 58, "renderer has 58 specific positions")
    check(sum(row["specific_local_dispatch_retained"] == "0" for row in patches) == 144, "renderer leaves 144 positions fully open")
    changed_patches = {row["gdt739_dispatch_id"]: row for row in patches if row["changed_from_gdt741"] == "1"}
    check(set(changed_patches) == {"G739-D0143", "G739-D0164"}, "exactly two renderer patches change")
    check(changed_patches["G739-D0143"]["gdt742_working_render_de"] == "Skalarstufe II des Materials; Dimension offen; Abschlussbezug", "rain receives only local material carrier")
    check(changed_patches["G739-D0164"]["gdt742_working_render_de"] == "Skalarstufe II der Zubereitung; Dimension offen; Eintrag", "sain receives only local preparation carrier")

    focus = read_tsv(art / "FOCUS_7_CACHED_LINE_REVIEW.tsv")
    check(len(focus) == len({row["focus_id"] for row in focus}) == 7, "seven unique cached focus lines")
    candidate_target_ids = {row["gdt739_dispatch_id"] for row in candidates}
    check({row["gdt739_dispatch_id"] for row in focus} == candidate_target_ids, "focus deck exactly covers candidate targets")
    focus_loci = {row["locus"] for row in focus}
    compact_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(COMPACT):
        if row["locus"] in focus_loci:
            compact_by_locus[row["locus"]].append(row)
    patch_map = {row["gdt739_dispatch_id"]: row for row in patches}
    candidate_by_dispatch: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        candidate_by_dispatch[row["gdt739_dispatch_id"]].append(row)
    for row in focus:
        contact = by_dispatch[row["gdt739_dispatch_id"]][0]
        line = sorted(compact_by_locus[row["locus"]], key=lambda item: int(item["token_ordinal"]))
        ordinals = {int(item["token_ordinal"]): item["surface"] for item in line}
        start = min(int(contact["target_ordinal"]), int(contact["neighbor_ordinal"]))
        stop = max(int(contact["target_ordinal"]), int(contact["neighbor_ordinal"]))
        frame = " ".join(ordinals[index] for index in range(start, stop + 1))
        candidate_rows = candidate_by_dispatch[row["gdt739_dispatch_id"]]
        statuses = {item["gdt742_status"] for item in candidate_rows}
        expected_decision = "PROMOTE_CARRIER_ONLY" if "PROMOTE_ROLE_SEPARATED_CARRIER" in statuses else "INHERIT_STRICT_RELAY" if statuses == {"ACTIVE_INHERITED_STRICT_RELAY"} else "HOLD_OPEN_COLLISION"
        require(row["page"] == contact["page"] and row["locus"] == contact["locus"], f"focus locus provenance: {row['focus_id']}")
        require(row["target_ordinal"] == contact["target_ordinal"] and row["target_surface"] == contact["target_surface"], f"focus target provenance: {row['focus_id']}")
        require(row["candidate_roles"] == "+".join(sorted(item["candidate_role"] for item in candidate_rows)), f"focus roles: {row['focus_id']}")
        require(row["line_eva_cached"] == " ".join(item["surface"] for item in line), f"focus cached line: {row['focus_id']}")
        require(row["radius_two_frame_manuscript_order"] == frame, f"focus frame: {row['focus_id']}")
        require(row["gdt741_target_render_de"] == patch_map[row["gdt739_dispatch_id"]]["gdt741_working_render_de"] and row["gdt742_target_render_de"] == patch_map[row["gdt739_dispatch_id"]]["gdt742_working_render_de"], f"focus renderer: {row['focus_id']}")
        require(row["focus_decision"] == expected_decision and row["new_page_or_transcription"] == "0", f"focus decision and scope: {row['focus_id']}")
        require("no plaintext clause" in row["reader_note"], f"focus clause disclaimer: {row['focus_id']}")
    check(True, "all seven lines rebuild from the admitted compact cache")
    check(not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in focus), "focus deck excludes sealed pages")
    reader = (art / "GDT742_ROLE_SEPARATION_READER.md").read_text(encoding="utf-8")
    check(all(row["focus_id"] in reader and row["line_eva_cached"] in reader for row in focus), "reader contains every focus line")
    check("not a word translation" in reader and "No new axis, component, lexeme, plaintext clause" in reader, "reader states working ceiling")

    edges = read_tsv(art / "GDT742_GDT388_TWO_CARRIER_RELAY_EDGE_PACKET.tsv")
    check(len(edges) == 2 and len({(row["pivot_locus"], row["target_locus"]) for row in edges}) == 2, "two unique provisional relation edges")
    check(all(row["eligibility_status"] == "INELIGIBLE_FORMAL_ATTACHMENT_EDGE" for row in edges), "both relation edges explicitly ineligible")
    check({row["page"] for row in edges} == {"f77v", "f112r"} and not any(row["page"].startswith("f84") for row in edges), "relation packet has exact admitted pages")
    intake = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(art / "GDT742_GDT388_TWO_CARRIER_RELAY_EDGE_PACKET.tsv")],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    intake_payload = json.loads(intake.stdout)
    check(intake.returncode == 1 and intake_payload["status"] == "INVALID_PACKET", "GDT388 intake rejects provisional carrier edges")
    check(not intake_payload["score_ready"] and not intake_payload["capacity_gate_50_edges_5_folios"] and not intake_payload["holdout_gate"] and not intake_payload["mobile_null_gate"], "all relation score-readiness gates remain closed")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT742_R2_OPEN_COLLISION_ADJUDICATION_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"] == {"candidate_roles": 8, "candidate_targets": 7, "f84_used": False, "f84r_used": False, "focus_cached_lines": 7, "inherited_allowlist_pages": 179, "new_pages_used": 0, "radius_two_contacts": 41, "renderer_positions": 202}, "result scope")
    check(result["feature_classes"] == {"promoted_class_members": 2, "promotion_classes": 1, "radius_two_classes": 32, "repeated_classes": 7}, "result feature-class summary")
    check(result["roles"] == {"axis_role_changes": 0, "carrier_role_changes": 2, "gdt741_active_candidate_roles": 2, "gdt742_active_candidate_roles": 4, "new_carrier_roles": 2, "open_candidate_roles": 4, "open_candidate_targets": 3}, "result role summary")
    check(result["renderer"] == {"axis_specific_occurrences": 36, "carrier_bound_occurrences": 45, "changed_from_gdt741": 2, "fully_open_occurrences": 144, "specific_occurrences": 58}, "result renderer summary")
    check(result["edge_intake"] == {"expected_status": "INVALID_PACKET", "packet_rows": 2, "score_ready": False}, "result edge summary")
    check(all(value == 0 for value in result["claims"].values()), "result claim ceiling remains zero")
    for name in HASHED_BY_RESULT:
        rel = str(BASE / "artifacts" / name)
        require(result["artifact_hashes"][rel] == sha256(art / name), f"result hash: {name}")
    check(set(result["artifact_hashes"]) == {str(BASE / "artifacts" / name) for name in HASHED_BY_RESULT}, "result binds exactly seven compact artifacts")

    with tempfile.TemporaryDirectory(prefix="gdt742-replay-") as temporary:
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
        "rule_triggers": {"inherited_strict": 2, "new_role_separated_carriers": 2, "remaining_open_roles": 4},
        "checks": checks,
    }
    if not args.no_write:
        (art / "VALIDATION.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8",
        )
    print(json.dumps({
        "status": "PASS", "checks_passed": len(checks),
        "builder_replay": "BYTE_IDENTICAL", "edge_intake": "INVALID_PACKET",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
