#!/usr/bin/env python3
"""Independent source, dispatch, aggregate, claim-ceiling and replay checks for GDT774."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt774_ol_376_contextual_transfer"
SRC, ART = EXP / "src", EXP / "artifacts"
RUN, REPORT, VALIDATION = SRC / "run.py", EXP / "REPORT.md", ART / "VALIDATION.json"
G769 = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts"
G683 = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts"
G760 = ROOT / "experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts"
G762 = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts"
G763 = ROOT / "experiments/yolo/gdt763_h1_content_vs_record_discriminator/artifacts"
G773 = ROOT / "experiments/yolo/gdt773_ol_capacity_equalized_composition_audit/artifacts"
FALLBACK = "Ansatz-/Zubereitungsposten"

BRANCH = {
    "G774-D00": "GDT773_CALIBRATION_COPY", "G774-D01": "AMOUNT_TO_CONTENT_HEAD",
    "G774-D02": "CONTENT_TO_AMOUNT_HEAD", "G774-D03": "PROCESS_SEQUENCE_RIGHT",
    "G774-D04": "FIELD_CLOSURE_LEFT", "G774-D05": "CLOSE_RIGHT_NOMINAL_VETO",
    "G774-D06": "STATE_FIELD_CHAIN", "G774-D07": "GENERIC_NOMINAL_FALLBACK",
}
POLICY = {
    "G774-D00": (0, "GDT773_CALIBRATION_KEY", "COPY_LOCKED_GDT773_OUTPUT", "COPY_GDT773"),
    "G774-D01": (1, "AMOUNT_CONTACT_TARGET_RIGHT_OF_AMOUNT_AND_NOT_LINE_FINAL", "CONTENT_FIELD_HEAD", "Ansatz:"),
    "G774-D02": (2, "AMOUNT_CONTACT_TARGET_LEFT_OF_AMOUNT", "MEASURE_FIELD_HEAD", "Menge:"),
    "G774-D03": (3, "DIRECT_PROCESS_OR_OLY_RIGHT", "SEQUENCE", "und dann"),
    "G774-D04": (4, "DIRECT_CLOSE_LEFT", "FIELD_BOUNDARY", ";"),
    "G774-D05": (5, "DIRECT_CLOSE_RIGHT", "NOMINAL_VETO", FALLBACK),
    "G774-D06": (6, "F15_STATE_TRANSITION_BRIDGE_AND_F14_MEDIAL_TWO_SIDED", "COORDINATION", "und"),
    "G774-D07": (7, "NO_TRANSFER_SIGNAL", "NOMINAL_FALLBACK", FALLBACK),
}
SOURCE_HASHES = {
    "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts/TARGET_526_EXACT_CONTEXT_ATLAS.tsv": "935c39c026db8a9b282700fec90a4158cc6120323f4080477140922f318cb95a",
    "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts/FRAME_LOCUS_EVIDENCE.tsv": "06fa673a80fdd780b913d9075fd81457e4c88845e81ac51d9460c005a9116c70",
    "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/src/core_atlas.py": "3f66f4db4c749db7496091f8a333fb55db21cbf752b3de7c2f4a3d1b3ec3e063",
    "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/experiment.json": "b4258f4733d1c794fdf7aa19f81318a5cd887cffc451f47952ef42ef324f9556",
    "experiments/yolo/gdt764_bounded_value_field_dispatch/src/run.py": "fe25e46a0a15e53ea3fbb0d95364a4afb8a351a494cfdfd818fdcf9551ceb687",
    "experiments/yolo/gdt764_bounded_value_field_dispatch/experiment.json": "fe30264a4ecbaf6265bc39462438584a8ccbd667745de74ff560fa5a005b9fe4",
    "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts/OL_463_OCCURRENCE_AUDIT.tsv": "b400bf4c895e08051825c82bb2d603fdd94a5304e157d4d01fb782b9c141da55",
    "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts/ADJACENT_OL_PAIRS.tsv": "6fe1c221604348f1aed749df9997c2eb82eae7e9e1636ff1d013172e586422a0",
    "experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts/QUANTITY_281_EXPRESSION_ATLAS.tsv": "fa2b3def5edcbdb631a8cfd0bffd505266f0952afb18f5cae1d05ca0a0abec0c",
    "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/OL_AMOUNT_EXPRESSION_CONTACT_ATLAS.tsv": "dcbe2fceefc377c5f24fb5d3000b2d4348b93c334905bec58bcd79d33b5695df",
    "experiments/yolo/gdt763_h1_content_vs_record_discriminator/artifacts/OL_16_SLOT_FUNCTION_ATLAS.tsv": "0e6ed32b92520f83af3bccd303fe89f5b49cbf3292460361aa3c65b83ddb4343",
    "experiments/yolo/gdt771_complete_cache_discriminator_sufficiency/artifacts/OL_LEFT_BRANCH_ATLAS.tsv": "ebc2e797bedd49a87964140cc9c60ec02339cd05b367f062ce9059afbc295262",
    "experiments/yolo/gdt773_ol_capacity_equalized_composition_audit/artifacts/OL_CONTEXTUAL_DEFAULTS.tsv": "637107f23c3a250e432af83feae9864a1370e9a303eb3e68a9ad9f2827588c82",
    "experiments/yolo/gdt773_ol_capacity_equalized_composition_audit/artifacts/GDT773_OL_WORKING_DICTIONARY.tsv": "4ada5daf6a32bd4594fd02cfced2dd1ce70bfa373ba2d4d961c1d60bc74a3d15",
    "experiments/yolo/gdt773_ol_capacity_equalized_composition_audit/artifacts/RESULT.json": "77e8d70f6937a0207e3e2ccd1637624932a8cf77efc39981f2c70e70a1a81740",
}
AUTO_BRANCH = {"G774-D01": 10, "G774-D02": 5, "G774-D03": 4, "G774-D04": 3,
               "G774-D05": 7, "G774-D06": 27, "G774-D07": 320}
HYBRID_BRANCH = {"G774-D00": 15, "G774-D01": 6, "G774-D02": 3, "G774-D03": 2,
                 "G774-D04": 3, "G774-D05": 7, "G774-D06": 26, "G774-D07": 314}
AUTO_OUTPUT = {"Ansatz:": 10, "Menge:": 5, "und dann": 4, ";": 3, "und": 27, FALLBACK: 327}
HYBRID_OUTPUT = {":": 1, ";": 7, "Ansatz:": 11, "Menge:": 5, "und": 27,
                 "und dann": 4, FALLBACK: 321}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded(path: Path, pages: Iterable[str], columns: Sequence[str]) -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)),
               "--selector", "page", "--columns", ",".join(columns)]
    for page in sorted(set(pages)):
        command.extend(("--allow", page))
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if done.returncode or "GUARD_STATS" not in done.stderr:
        raise AssertionError(f"guarded query failed: {path.relative_to(ROOT)}: {done.stderr}")
    return list(csv.DictReader(io.StringIO(done.stdout), delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_outputs() -> tuple[str, ...]:
    tree = ast.parse(RUN.read_text(encoding="utf-8"))
    found = [node for node in tree.body if isinstance(node, ast.Assign)
             and any(isinstance(target, ast.Name) and target.id == "OUTPUT_NAMES" for target in node.targets)]
    if len(found) != 1:
        raise AssertionError("runner must define one literal OUTPUT_NAMES")
    value = ast.literal_eval(found[0].value)
    if not isinstance(value, (list, tuple)) or not all(isinstance(item, str) for item in value):
        raise AssertionError("OUTPUT_NAMES is not a literal string sequence")
    return tuple(value)


def directions(direct: Mapping[str, object], channel: str) -> set[str]:
    evidence = direct.get("channel_evidence", {})
    if not isinstance(evidence, Mapping) or not isinstance(evidence.get(channel, []), list):
        return set()
    return {str(item["direction"]) for item in evidence[channel]
            if isinstance(item, Mapping) and item.get("direction")}


def join(values: Iterable[str]) -> str:
    values = sorted({value for value in values if value})
    return "|".join(values) if values else "NONE"


def census(rows: Iterable[Mapping[str, object]]) -> dict[str, int]:
    rows = list(rows)
    return {"occurrences": len(rows), "page_labels": len({str(row["page"]) for row in rows}),
            "physical_folios": len({str(row["physical_folio"]) for row in rows}),
            "loci": len({str(row["locus"]) for row in rows})}


def compare(check: Callable[[bool, str], None], actual: Sequence[Mapping[str, object]],
            expected: Sequence[Mapping[str, object]], keys: Sequence[str], fields: Sequence[str], label: str) -> None:
    def index(rows: Sequence[Mapping[str, object]]) -> dict[tuple[str, ...], Mapping[str, object]]:
        return {tuple(str(row[field]) for field in keys): row for row in rows}
    actual_map, expected_map = index(actual), index(expected)
    check(len(actual_map) == len(actual), f"{label}: duplicate actual key")
    check(len(expected_map) == len(expected), f"{label}: duplicate expected key")
    check(set(actual_map) == set(expected_map), f"{label}: key universe differs")
    for key in sorted(set(actual_map) & set(expected_map)):
        for field in fields:
            check(str(actual_map[key].get(field, "")) == str(expected_map[key].get(field, "")),
                  f"{label}: {key} field {field} differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--validation-path", type=Path, default=VALIDATION)
    args = parser.parse_args()
    artifacts = args.artifacts_dir if args.artifacts_dir.is_absolute() else ROOT / args.artifacts_dir
    validation = args.validation_path if args.validation_path.is_absolute() else ROOT / args.validation_path
    checks, failures = 0, []

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(message)

    outputs = literal_outputs()
    expected_outputs = (
        "OL_376_TRANSFER_ATLAS.tsv", "TRANSFER_BRANCH_SUMMARY.tsv", "AMOUNT_17_EDGE_AUDIT.tsv",
        "CALIBRATION_REPLAY_AUDIT.tsv", "DIRECT_SIGNATURE_DIRECTION_SUMMARY.tsv",
        "F15_STATE_BRIDGE_AUDIT.tsv", "LINE_POSITION_REPEAT_AUDIT.tsv", "ADJACENT_OL_PAIR_AUDIT.tsv",
        "REGISTER_DISPATCH_SUMMARY.tsv", "PHYSICAL_FOLIO_TRANSFER_SUMMARY.tsv",
        "LEGACY_GRUNDANSATZ_COMPARISON.tsv", "MANUAL_24_CONTEXT_AUDIT.tsv",
        "GDT774_WORKING_DICTIONARY.tsv", "RESULT.json",
        "structural_audit/OL_376_STRUCTURAL_POSITION_ATLAS.tsv",
        "structural_audit/OL_DIRECT_SIGNATURE_DIRECTION_MATRIX.tsv",
        "structural_audit/OL_EVIDENCE_VENN_DISPATCH.tsv", "structural_audit/OL_SELF_REPEAT_ATLAS.tsv",
        "structural_audit/OL_NEIGHBOR_SURFACE_SUMMARY.tsv",
        "structural_audit/OL_REPEATED_NEIGHBOR_FRAMES.tsv", "structural_audit/OL_REGISTER_SUMMARY.tsv",
        "structural_audit/OL_FOLIO_HOLDOUT.tsv", "structural_audit/OL_POSITION_MATCHED_NULL.tsv",
        "structural_audit/STRUCTURAL_AUDIT_RESULT.json",
    )
    check(outputs == expected_outputs, "runner 24-output contract differs")
    check(all((artifacts / name).is_file() for name in outputs), "a declared artifact is missing")

    locks = read_tsv(SRC / "SOURCE_LOCK.tsv")
    lock_map = {row["path"]: row for row in locks}
    check(len(locks) == len(lock_map) == 15 and set(lock_map) == set(SOURCE_HASHES), "source-lock universe differs")
    actual_hashes: dict[str, str] = {}
    for relative, expected_hash in SOURCE_HASHES.items():
        path = Path(relative)
        check(not path.is_absolute() and ".." not in path.parts, f"unsafe source-lock path: {relative}")
        check(lock_map.get(relative, {}).get("expected_sha256") == expected_hash, f"authored hash differs: {relative}")
        if (ROOT / path).is_file():
            actual_hashes[relative] = sha256(ROOT / path)
            check(actual_hashes[relative] == expected_hash, f"source bytes differ: {relative}")
        else:
            check(False, f"locked source missing: {relative}")

    policies = sorted(read_tsv(SRC / "TRANSFER_POLICY_SPECS.tsv"), key=lambda row: int(row["priority"]))
    policy = {row["rule_id"]: row for row in policies}
    check(len(policies) == len(policy) == 8 and set(policy) == set(POLICY), "policy universe differs")
    check([int(row["priority"]) for row in policies] == list(range(8)), "policy precedence differs")
    for rule_id, expected in POLICY.items():
        row = policy.get(rule_id, {})
        observed = (int(row.get("priority", -1)), row.get("condition_code"),
                    row.get("selected_function"), row.get("default_de"))
        check(observed == expected, f"policy differs: {rule_id}")
        check(row.get("semantic_credit") == row.get("component_export_credit") == "0",
              f"policy grants credit: {rule_id}")
    check(policies[5]["rule_id"] == "G774-D05" and policies[6]["rule_id"] == "G774-D06",
          "close-right nominal veto does not precede F15")

    targets = [row for row in read_tsv(G769 / "TARGET_526_EXACT_CONTEXT_ATLAS.tsv") if row["surface"] == "ol"]
    by_key = {(row["locus"], int(row["ordinal"])): row for row in targets}
    check(len(targets) == len(by_key) == len({row["target_occurrence_id"] for row in targets}) == 376,
          "target occurrence universe differs")
    check(all(row["reader_exact"] == "1" and row["written_line_eva"].split()[int(row["ordinal"]) - 1] == "ol" for row in targets),
          "target exactness/token integrity differs")
    check(all(row["semantic_identity_credit"] == row["component_export_credit"] == "0" for row in targets),
          "target source grants semantic/component credit")
    check(not any(row["page"].startswith("f84") for row in targets), "sealed page entered target universe")
    check(census(targets) == {"occurrences": 376, "page_labels": 98, "physical_folios": 61, "loci": 340},
          "target geometry differs")
    check(Counter(row["line_position"] for row in targets) == {"FIRST": 22, "MIDDLE": 317, "LAST": 37},
          "target line-position census differs")

    frames = [row for row in read_tsv(G769 / "FRAME_LOCUS_EVIDENCE.tsv") if row["target_surface"] == "ol"]
    f14 = {(row["locus"], int(row["ordinal"])) for row in frames if row["frame_id"] == "F14_MEDIAL_TWO_SIDED_LINKER"}
    f15 = {(row["locus"], int(row["ordinal"])): row for row in frames if row["frame_id"] == "F15_STATE_TRANSITION_BRIDGE"}
    check(len(f14) == 212 and len(f15) == 31 and set(f15).issubset(f14), "F14/F15 universe differs")
    check(all(row["reader_exact"] == "1" and row["confirmed_lexeme"] == row["component_export_credit"] == "0" for row in f15.values()),
          "F15 source grants forbidden credit")

    expressions = {row["expression_id"]: row for row in read_tsv(G760 / "QUANTITY_281_EXPRESSION_ATLAS.tsv")}
    contacts = read_tsv(G762 / "OL_AMOUNT_EXPRESSION_CONTACT_ATLAS.tsv")
    slots = read_tsv(G763 / "OL_16_SLOT_FUNCTION_ATLAS.tsv")
    slot_by_contact = {row["source_contact_id"]: row for row in slots}
    check(len(contacts) == len(slots) == len(slot_by_contact) == 16, "amount contact/slot count differs")
    check(set(slot_by_contact) == {row["ol_amount_contact_id"] for row in contacts}, "contact/slot join differs")
    check(sum(int(row["ol_directed_edges"]) for row in contacts) == 17, "raw directed amount edge count differs")
    check(Counter(row["selected_slot_function"] for row in slots) ==
          {"HEAD": 9, "CONTEXT_SECOND_FIELD": 5, "OBJECT_PATIENT": 1, "BILATERAL_AMBIGUOUS": 1},
          "GDT763 slot-function census differs")
    check(all(row["source_relation_marker"] == "NONE" and row["specific_oil_identity"] == "0"
              and row["confirmed_plaintext"] == row["component_export_credit"] == "0" for row in slots),
          "GDT763 claims relation/oil/plaintext/component")
    check(all(row["specific_medium_selected"] == row["confirmed_plaintext"] == row["component_export_credit"] == "0"
              for row in contacts), "GDT762 claims medium/plaintext/component")

    amount_edges: list[dict[str, object]] = []
    amount_any: dict[tuple[str, int], dict[str, object]] = {}
    amount_selected: dict[tuple[str, int], dict[str, object]] = {}
    for contact in contacts:
        expression, slot = expressions[contact["expression_id"]], slot_by_contact[contact["ol_amount_contact_id"]]
        check(expression["locus"] == contact["locus"] == slot["locus"], f"amount join differs: {contact['ol_amount_contact_id']}")
        start, end = int(expression["start_ordinal"]), int(expression["end_ordinal"])
        for side in contact["ol_sides_relative_to_amount"].split("|"):
            ordinal, relation, rule = ((start - 1, "OL_LEFT_OF_AMOUNT", "G774-D02") if side == "L"
                                       else (end + 1, "OL_RIGHT_OF_AMOUNT", "G774-D01"))
            key = (contact["locus"], ordinal)
            target = by_key.get(key)
            check(side in {"L", "R"} and target is not None, f"invalid amount edge: {key}")
            if target is None:
                continue
            line_final = ordinal == int(target["line_token_count"])
            selected = not (relation == "OL_RIGHT_OF_AMOUNT" and line_final)
            edge = {
                "edge_id": f"{contact['ol_amount_contact_id']}-{side}", "source_contact_id": contact["ol_amount_contact_id"],
                "gdt763_slot_id": slot["ol_slot_id"], "expression_id": contact["expression_id"],
                "page": contact["page"], "physical_folio": contact["physical_folio"], "locus": contact["locus"],
                "amount_expression_eva": contact["amount_expression_eva"], "amount_candidate_de": contact["amount_candidate_de"],
                "amount_rivals_de": contact["amount_rivals_de"], "amount_working_confidence": contact["amount_working_confidence"],
                "amount_start_ordinal": start, "amount_end_ordinal": end, "ol_side_relative_to_amount": side,
                "relation": relation, "ol_ordinal": ordinal, "line_token_count": target["line_token_count"],
                "ol_line_final": int(line_final), "conditional_phrase_license": contact["conditional_phrase_license"],
                "gdt762_decision": contact["decision"], "gdt763_slot_function": slot["selected_slot_function"],
                "gdt763_dispatch_basis": slot["dispatch_basis"], "selected_for_transfer": int(selected),
                "exclusion_reason": "NONE" if selected else "DANGLING_CONTENT_HEAD_AT_LINE_END",
                "transfer_rule_id": rule if selected else "G774-D07",
                "automatic_default_de": policy[rule]["default_de"] if selected else FALLBACK,
                "bilateral_contact": int(contact["ol_directed_edges"] == "2"),
                "default_is_translation": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
            }
            check(key not in amount_any, f"duplicate amount edge: {key}")
            amount_any[key] = edge
            if selected:
                amount_selected[key] = edge
            amount_edges.append(edge)
    amount_edges.sort(key=lambda row: (str(row["page"]), str(row["locus"]), int(row["ol_ordinal"])))
    excluded = {(str(row["locus"]), int(row["ol_ordinal"])) for row in amount_edges if not int(row["selected_for_transfer"])}
    check(len(amount_edges) == 17 and len(amount_selected) == 15, "amount edge/selection count differs")
    check(Counter(row["ol_side_relative_to_amount"] for row in amount_edges) == {"R": 12, "L": 5}, "amount direction differs")
    check(excluded == {("f79r.13", 9), ("f79v.25", 9)}, "line-final exclusions differ")
    check(sum(int(row["conditional_phrase_license"]) for row in amount_edges) == 8, "phrase-license edge count differs")
    compare(check, read_tsv(artifacts / "AMOUNT_17_EDGE_AUDIT.tsv"), amount_edges, ("edge_id",),
            tuple(amount_edges[0]), "amount audit")

    calibrations = read_tsv(G773 / "OL_CONTEXTUAL_DEFAULTS.tsv")
    calibration = {(row["locus"], int(row["ordinal"])): row for row in calibrations}
    check(len(calibrations) == len(calibration) == 15, "calibration universe differs")
    check(all(row["default_is_translation"] == row["confirmed_lexeme"] == row["component_export_credit"] == "0"
              for row in calibrations), "calibration source grants credit")

    pages = {row["page"] for row in targets}
    legacy_columns = ("page", "locus", "ordinal", "working_translation_de", "semantic_decision",
                      "evidence_type", "reader_support", "boundary_active", "render_once")
    legacy_rows = guarded(G683 / "OL_463_OCCURRENCE_AUDIT.tsv", pages, legacy_columns)
    legacy = {(row["locus"], int(row["ordinal"])): row for row in legacy_rows}
    check(set(by_key).issubset(legacy), "guarded GDT683 crosswalk incomplete")
    check(all(legacy[key]["working_translation_de"] == "Grundansatz" for key in by_key), "legacy crosswalk not Grundansatz")
    check(sum(legacy[key]["boundary_active"] == "1" for key in by_key) == 4 and
          sum(legacy[key]["render_once"] == "1" for key in by_key) == 0, "legacy boundary/render-once census differs")

    by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in targets:
        by_locus[row["locus"]].append(row)
    for rows in by_locus.values():
        rows.sort(key=lambda row: int(row["ordinal"]))

    atlas_expected: list[dict[str, object]] = []
    for source in sorted(targets, key=lambda row: (row["page"], int(row["line_number"]), int(row["ordinal"]))):
        key = (source["locus"], int(source["ordinal"]))
        direct = json.loads(source["direct_signatures"])
        channels = direct["signature_channels"]
        process_right = "RIGHT" in (directions(direct, "PROCESS") | directions(direct, "OLY"))
        process_left = "LEFT" in (directions(direct, "PROCESS") | directions(direct, "OLY"))
        close_left, close_right = "LEFT" in directions(direct, "CLOSE"), "RIGHT" in directions(direct, "CLOSE")
        edge = amount_selected.get(key)
        if edge and edge["relation"] == "OL_RIGHT_OF_AMOUNT": rule = "G774-D01"
        elif edge and edge["relation"] == "OL_LEFT_OF_AMOUNT": rule = "G774-D02"
        elif process_right: rule = "G774-D03"
        elif close_left: rule = "G774-D04"
        elif close_right: rule = "G774-D05"
        elif key in f15 and key in f14: rule = "G774-D06"
        else: rule = "G774-D07"
        spec, locked = policy[rule], calibration.get(key)
        hybrid_rule = "G774-D00" if locked else rule
        hybrid_default = locked["selected_default_de"] if locked else spec["default_de"]
        hybrid_function = locked["selected_function"] if locked else spec["selected_function"]
        hybrid_confidence = "INHERITED_GDT773_CONTEXT" if locked else spec["base_confidence"]
        repeated = by_locus[source["locus"]]
        ordinals = [int(row["ordinal"]) for row in repeated]
        ordinal = int(source["ordinal"])
        atlas_expected.append({
            **{field: source[field] for field in ("target_occurrence_id", "raw_occurrence_id", "surface", "page",
               "physical_folio", "locus", "line_number", "section", "language", "hand", "ordinal", "token_index",
               "line_token_count", "line_position", "normalized_line_position", "paragraph_start_line",
               "paragraph_end_line", "true_paragraph_opener", "true_paragraph_closer", "reader_exact",
               "written_line_eva", "direct_signatures")},
            "direct_signature_channels": join(str(value) for value in channels), "any_direct_signature": int(bool(channels)),
            "amount_transfer_signal": int(edge is not None), "amount_relation": str(edge["relation"]) if edge else "NONE",
            "amount_raw_excluded": int(key in amount_any and key not in amount_selected),
            "process_right_signal": int(process_right), "process_left_signal": int(process_left),
            "close_left_signal": int(close_left), "close_right_signal": int(close_right),
            "f14_medial_two_sided": int(key in f14), "f15_state_transition_bridge": int(key in f15),
            "ol_count_in_locus": len(repeated), "ol_index_in_locus": ordinals.index(ordinal) + 1,
            "adjacent_ol_repeat": int(any(abs(ordinal - other) == 1 for other in ordinals if other != ordinal)),
            "calibration_case_id": locked["case_id"] if locked else "NONE",
            "calibration_default_de": locked["selected_default_de"] if locked else "NONE",
            "automatic_rule_id": rule, "automatic_branch": BRANCH[rule],
            "automatic_function": spec["selected_function"], "automatic_default_de": spec["default_de"],
            "automatic_confidence": spec["base_confidence"], "automatic_contextual": int(spec["default_de"] != FALLBACK),
            "hybrid_rule_id": hybrid_rule, "hybrid_branch": BRANCH[hybrid_rule],
            "hybrid_function": hybrid_function, "hybrid_default_de": hybrid_default,
            "hybrid_confidence": hybrid_confidence, "hybrid_contextual": int(hybrid_default != FALLBACK),
            "legacy_gdt683_default_de": legacy[key]["working_translation_de"],
            "legacy_gdt683_semantic_decision": legacy[key]["semantic_decision"],
            "legacy_gdt683_evidence_type": legacy[key]["evidence_type"],
            "legacy_gdt683_reader_support": legacy[key]["reader_support"],
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "semantic_identity_credit": 0, "component_export_credit": 0,
        })
    atlas_actual = read_tsv(artifacts / "OL_376_TRANSFER_ATLAS.tsv")
    compare(check, atlas_actual, atlas_expected, ("target_occurrence_id",), tuple(atlas_expected[0]), "transfer atlas")
    atlas = {(str(row["locus"]), int(row["ordinal"])): row for row in atlas_expected}
    auto_branches = Counter(str(row["automatic_rule_id"]) for row in atlas_expected)
    hybrid_branches = Counter(str(row["hybrid_rule_id"]) for row in atlas_expected)
    auto_outputs = Counter(str(row["automatic_default_de"]) for row in atlas_expected)
    hybrid_outputs = Counter(str(row["hybrid_default_de"]) for row in atlas_expected)
    check(dict(auto_branches) == AUTO_BRANCH and dict(hybrid_branches) == HYBRID_BRANCH, "branch census differs")
    check(dict(auto_outputs) == AUTO_OUTPUT and dict(hybrid_outputs) == HYBRID_OUTPUT, "renderer output census differs")
    check({key for key in f15 if atlas[key]["automatic_rule_id"] != "G774-D06"} ==
          {("f76v.39", 7), ("f78r.12", 6), ("f79v.25", 2), ("f81r.12", 3)},
          "F15 precedence exclusions differ")

    # Recalculate branch/count summaries from the independently dispatched atlas.
    branch_expected: list[dict[str, object]] = []
    for renderer in ("AUTOMATIC", "HYBRID"):
        prefix = renderer.lower()
        groups: defaultdict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
        for row in atlas_expected:
            groups[(str(row[f"{prefix}_rule_id"]), str(row[f"{prefix}_branch"]),
                    str(row[f"{prefix}_default_de"]))].append(row)
        for (rule_id, branch, output), rows in sorted(groups.items()):
            contextual = output != FALLBACK
            branch_expected.append({"row_type": "BRANCH", "renderer": renderer, "rule_id": rule_id,
                                    "branch": branch, "output_de": output, **census(rows),
                                    "contextual_occurrences": len(rows) if contextual else 0})
        branch_expected.append({"row_type": "TOTAL", "renderer": renderer, "rule_id": "ALL", "branch": "ALL",
                                "output_de": "ALL", **census(atlas_expected),
                                "contextual_occurrences": sum(int(row[f"{prefix}_contextual"]) for row in atlas_expected)})
    compare(check, read_tsv(artifacts / "TRANSFER_BRANCH_SUMMARY.tsv"), branch_expected,
            ("row_type", "renderer", "rule_id", "output_de"), tuple(branch_expected[0]), "branch summary")

    calibration_expected = []
    for source in calibrations:
        row = atlas[(source["locus"], int(source["ordinal"]))]
        exact = row["automatic_default_de"] == source["selected_default_de"]
        calibration_expected.append({
            "case_id": source["case_id"], "page": row["page"], "physical_folio": row["physical_folio"],
            "locus": row["locus"], "ordinal": row["ordinal"], "context_eva": source["context_eva"],
            "gdt773_dispatch_rule_id": source["dispatch_rule_id"], "gdt773_selected_function": source["selected_function"],
            "gdt773_default_de": source["selected_default_de"], "automatic_rule_id": row["automatic_rule_id"],
            "automatic_branch": row["automatic_branch"], "automatic_default_de": row["automatic_default_de"],
            "automatic_exact_match": int(exact), "miss_reason": "NONE" if exact else
            ("NO_OCCURRENCE_ID_FREE_TRANSFER_TRIGGER" if row["automatic_rule_id"] == "G774-D07"
             else "PORTABLE_RULE_SELECTS_DIFFERENT_OUTPUT"),
            "hybrid_rule_id": row["hybrid_rule_id"], "hybrid_default_de": row["hybrid_default_de"],
            "hybrid_exact_match": int(row["hybrid_default_de"] == source["selected_default_de"]),
            **{field: row[field] for field in ("amount_transfer_signal", "process_right_signal", "close_left_signal",
                                               "close_right_signal", "f15_state_transition_bridge")},
            "score_credit": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    compare(check, read_tsv(artifacts / "CALIBRATION_REPLAY_AUDIT.tsv"), calibration_expected,
            ("case_id",), tuple(calibration_expected[0]), "calibration audit")
    check(sum(int(row["automatic_exact_match"]) for row in calibration_expected) == 9 and
          sum(int(row["hybrid_exact_match"]) for row in calibration_expected) == 15,
          "automatic/hybrid calibration replay differs")

    direct_specs: list[tuple[str, str, Callable[[Mapping[str, object]], bool]]] = [
        ("ANY_DIRECT_SIGNATURE", "ANY", lambda row: bool(row["any_direct_signature"])),
        ("G769_AMOUNT", "ANY", lambda row: "AMOUNT" in str(row["direct_signature_channels"]).split("|")),
        ("PROCESS_OR_OLY", "RIGHT", lambda row: bool(row["process_right_signal"])),
        ("PROCESS_OR_OLY", "LEFT", lambda row: bool(row["process_left_signal"])),
        ("CLOSE", "LEFT", lambda row: bool(row["close_left_signal"])),
        ("CLOSE", "RIGHT", lambda row: bool(row["close_right_signal"])),
        ("STATE_DRY", "ANY", lambda row: "STATE_DRY" in str(row["direct_signature_channels"]).split("|")),
        ("STATE_MOIST", "ANY", lambda row: "STATE_MOIST" in str(row["direct_signature_channels"]).split("|")),
        ("NO_DIRECT_SIGNATURE", "NONE", lambda row: not bool(row["any_direct_signature"])),
    ]
    direct_actual = {(row["signal"], row["direction"]): row
                     for row in read_tsv(artifacts / "DIRECT_SIGNATURE_DIRECTION_SUMMARY.tsv")}
    check(set(direct_actual) == {(signal, direction) for signal, direction, _ in direct_specs},
          "direct-signature summary row universe differs")
    for signal, direction, predicate in direct_specs:
        rows = [row for row in atlas_expected if predicate(row)]
        expected = {**census(rows),
                    "automatic_selected_occurrences": sum(int(row["automatic_contextual"]) for row in rows),
                    "automatic_outputs_de": join(str(row["automatic_default_de"]) for row in rows),
                    "semantic_identity_credit": 0, "component_export_credit": 0}
        for field, value in expected.items():
            check(direct_actual.get((signal, direction), {}).get(field) == str(value),
                  f"direct-signature summary differs: {signal}/{direction}/{field}")

    f15_actual = {row["target_occurrence_id"]: row
                  for row in read_tsv(artifacts / "F15_STATE_BRIDGE_AUDIT.tsv")}
    check(len(f15_actual) == 31 and set(f15_actual) == {row["target_occurrence_id"] for row in f15.values()},
          "F15 audit occurrence universe differs")
    for key, frame in f15.items():
        row, actual = atlas[key], f15_actual.get(frame["target_occurrence_id"], {})
        detail = json.loads(frame["detail"])
        expected = {
            "page": frame["page"], "physical_folio": row["physical_folio"], "locus": frame["locus"],
            "ordinal": frame["ordinal"],
            "transition_directions": join(str(value) for value in detail.get("direction_labels", [])),
            "transition_count": len(detail.get("transitions", [])), "frame_detail": frame["detail"],
            "f14_medial_two_sided": row["f14_medial_two_sided"],
            "amount_priority_overlap": row["amount_transfer_signal"],
            "process_right_priority_overlap": row["process_right_signal"],
            "close_left_priority_overlap": row["close_left_signal"],
            "close_right_nominal_veto_overlap": row["close_right_signal"],
            "automatic_rule_id": row["automatic_rule_id"], "automatic_default_de": row["automatic_default_de"],
            "hybrid_rule_id": row["hybrid_rule_id"], "hybrid_default_de": row["hybrid_default_de"],
            "relation_is_translation": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        }
        for field, value in expected.items():
            check(actual.get(field) == str(value), f"F15 audit differs: {frame['target_occurrence_id']}/{field}")

    line_specs: list[tuple[str, Callable[[Mapping[str, object]], bool]]] = [
        ("ALL", lambda row: True), ("LINE_FIRST", lambda row: row["line_position"] == "FIRST"),
        ("LINE_MIDDLE", lambda row: row["line_position"] == "MIDDLE"),
        ("LINE_LAST", lambda row: row["line_position"] == "LAST"),
        ("PARAGRAPH_START_LINE", lambda row: row["paragraph_start_line"] == "1"),
        ("PARAGRAPH_END_LINE", lambda row: row["paragraph_end_line"] == "1"),
        ("TRUE_PARAGRAPH_OPENER", lambda row: row["true_paragraph_opener"] == "1"),
        ("TRUE_PARAGRAPH_CLOSER", lambda row: row["true_paragraph_closer"] == "1"),
        ("MULTI_OL_LINE_TOKEN", lambda row: int(row["ol_count_in_locus"]) > 1),
        ("ADJACENT_OL_REPEAT_TOKEN", lambda row: int(row["adjacent_ol_repeat"]) == 1),
        ("F14_MEDIAL_TWO_SIDED", lambda row: int(row["f14_medial_two_sided"]) == 1),
        ("F15_STATE_TRANSITION", lambda row: int(row["f15_state_transition_bridge"]) == 1),
        ("NO_DIRECT_SIGNATURE", lambda row: int(row["any_direct_signature"]) == 0),
    ]
    line_actual = {row["category"]: row for row in read_tsv(artifacts / "LINE_POSITION_REPEAT_AUDIT.tsv")}
    check(set(line_actual) == {name for name, _ in line_specs}, "line/repetition summary categories differ")
    for name, predicate in line_specs:
        selected = [row for row in atlas_expected if predicate(row)]
        expected = {**census(selected), "automatic_contextual": sum(int(row["automatic_contextual"]) for row in selected),
                    "automatic_nominal": sum(not bool(row["automatic_contextual"]) for row in selected),
                    "hybrid_contextual": sum(int(row["hybrid_contextual"]) for row in selected)}
        for field, value in expected.items():
            check(line_actual.get(name, {}).get(field) == str(value), f"line/repetition summary differs: {name}/{field}")

    register_actual = {(row["group_type"], row["group_value"]): row
                       for row in read_tsv(artifacts / "REGISTER_DISPATCH_SUMMARY.tsv")}
    register_specs: list[tuple[str, str, Callable[[Mapping[str, object]], bool]]] = [
        ("ALL", "ALL", lambda row: True), ("SECTION", "B", lambda row: row["section"] == "B"),
        ("SECTION", "NON_B", lambda row: row["section"] != "B"), ("HAND", "2", lambda row: row["hand"] == "2"),
        ("HAND", "NON_2", lambda row: row["hand"] != "2")]
    register_specs += [("SECTION_VALUE", value, lambda row, value=value: row["section"] == value)
                       for value in sorted({str(row["section"]) for row in atlas_expected} - {"B"})]
    register_specs += [("HAND_VALUE", value, lambda row, value=value: row["hand"] == value)
                       for value in sorted({str(row["hand"]) for row in atlas_expected})]
    check(set(register_actual) == {(a, b) for a, b, _ in register_specs}, "register summary groups differ")
    for axis, value, predicate in register_specs:
        rows = [row for row in atlas_expected if predicate(row)]
        expected = {**census(rows), "line_first": sum(row["line_position"] == "FIRST" for row in rows),
                    "line_middle": sum(row["line_position"] == "MIDDLE" for row in rows),
                    "line_last": sum(row["line_position"] == "LAST" for row in rows),
                    "multi_ol_line_tokens": sum(int(row["ol_count_in_locus"]) > 1 for row in rows),
                    "adjacent_repeat_tokens": sum(int(row["adjacent_ol_repeat"]) for row in rows),
                    "any_direct_signature": sum(int(row["any_direct_signature"]) for row in rows),
                    "automatic_contextual": sum(int(row["automatic_contextual"]) for row in rows),
                    "automatic_nominal": sum(not bool(row["automatic_contextual"]) for row in rows),
                    "hybrid_contextual": sum(int(row["hybrid_contextual"]) for row in rows),
                    "hybrid_nominal": sum(not bool(row["hybrid_contextual"]) for row in rows)}
        for field, expected_value in expected.items():
            check(register_actual.get((axis, value), {}).get(field) == str(expected_value),
                  f"register summary differs: {axis}/{value}/{field}")

    folio_actual = {row["physical_folio"]: row
                    for row in read_tsv(artifacts / "PHYSICAL_FOLIO_TRANSFER_SUMMARY.tsv")}
    folio_groups: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in atlas_expected:
        folio_groups[str(row["physical_folio"])].append(row)
    check(set(folio_actual) == set(folio_groups) and len(folio_actual) == 61, "physical-folio summary universe differs")
    for folio, rows in folio_groups.items():
        expected = {**census(rows), "sections": join(str(row["section"]) for row in rows),
                    "hands": join(str(row["hand"]) for row in rows),
                    "line_first": sum(row["line_position"] == "FIRST" for row in rows),
                    "line_middle": sum(row["line_position"] == "MIDDLE" for row in rows),
                    "line_last": sum(row["line_position"] == "LAST" for row in rows),
                    "any_direct_signature": sum(int(row["any_direct_signature"]) for row in rows),
                    "automatic_contextual": sum(int(row["automatic_contextual"]) for row in rows),
                    "automatic_nominal": sum(not bool(row["automatic_contextual"]) for row in rows),
                    "hybrid_contextual": sum(int(row["hybrid_contextual"]) for row in rows),
                    "hybrid_nominal": sum(not bool(row["hybrid_contextual"]) for row in rows)}
        for field, value in expected.items():
            check(folio_actual.get(folio, {}).get(field) == str(value),
                  f"physical-folio summary differs: {folio}/{field}")

    # Repetition pairs must remain visible, separate, and nominal.
    pair_columns = ("page", "locus", "left_ordinal", "right_ordinal", "working_render_de", "selected_scope", "rule", "zl3b_line")
    legacy_pairs = {(row["locus"], int(row["left_ordinal"]), int(row["right_ordinal"])): row
                    for row in guarded(G683 / "ADJACENT_OL_PAIRS.tsv", pages, pair_columns)}
    pair_actual = read_tsv(artifacts / "ADJACENT_OL_PAIR_AUDIT.tsv")
    expected_pair_keys = set()
    for locus, rows in by_locus.items():
        ordinals = sorted(int(row["ordinal"]) for row in rows)
        expected_pair_keys |= {(locus, left, right) for left, right in zip(ordinals, ordinals[1:]) if right == left + 1}
    check(len(expected_pair_keys) == len(pair_actual) == 7 and expected_pair_keys.issubset(legacy_pairs), "adjacent pair universe differs")
    check(all(row["left_automatic_rule_id"] == row["right_automatic_rule_id"] == "G774-D07"
              and row["separator_evidence"] == row["confirmed_lexeme"] == row["component_export_credit"] == "0"
              for row in pair_actual), "adjacent pair receives invented separator/context/credit")
    pair_by_key = {(row["locus"], int(row["left_ordinal"]), int(row["right_ordinal"])): row for row in pair_actual}
    for key in expected_pair_keys:
        locus, left, right = key
        actual, legacy_pair = pair_by_key.get(key, {}), legacy_pairs[key]
        left_row, right_row = atlas[(locus, left)], atlas[(locus, right)]
        expected = {"page": left_row["page"], "physical_folio": left_row["physical_folio"],
                    "left_direct_signature": left_row["direct_signature_channels"],
                    "right_direct_signature": right_row["direct_signature_channels"],
                    "left_automatic_default_de": left_row["automatic_default_de"],
                    "right_automatic_default_de": right_row["automatic_default_de"],
                    "legacy_selected_scope": legacy_pair["selected_scope"],
                    "legacy_working_render_de": legacy_pair["working_render_de"],
                    "written_line_eva": left_row["written_line_eva"]}
        for field, value in expected.items():
            check(actual.get(field) == str(value), f"adjacent-pair audit differs: {key}/{field}")

    legacy_actual = {(row["renderer"], row["class"]): row
                     for row in read_tsv(artifacts / "LEGACY_GRUNDANSATZ_COMPARISON.tsv")}
    expected_legacy_groups: dict[tuple[str, str], tuple[list[Mapping[str, object]], str, int, int]] = {}
    selected_legacy = [legacy[(str(row["locus"]), int(row["ordinal"]))] for row in atlas_expected]
    for decision in {row["semantic_decision"] for row in selected_legacy}:
        keys = {(row["locus"], int(row["ordinal"])) for row in selected_legacy if row["semantic_decision"] == decision}
        rows = [row for row in atlas_expected if (str(row["locus"]), int(row["ordinal"])) in keys]
        expected_legacy_groups[("LEGACY_GDT683", decision)] = (rows, "Grundansatz", 0, len(rows))
    for renderer, output_field, context_field in (("AUTOMATIC_GDT774", "automatic_default_de", "automatic_contextual"),
                                                   ("HYBRID_GDT774", "hybrid_default_de", "hybrid_contextual")):
        contextual = [row for row in atlas_expected if int(row[context_field])]
        nominal = [row for row in atlas_expected if not int(row[context_field])]
        expected_legacy_groups[(renderer, "CONTEXTUAL")] = (contextual, join(str(row[output_field]) for row in contextual), len(contextual), 0)
        expected_legacy_groups[(renderer, "NOMINAL_FALLBACK")] = (nominal, FALLBACK, 0, len(nominal))
    check(set(legacy_actual) == set(expected_legacy_groups), "legacy-comparison row universe differs")
    for key, (rows, output, contextual, nominal) in expected_legacy_groups.items():
        expected = {**census(rows), "output_de": output, "contextual_occurrences": contextual,
                    "nominal_occurrences": nominal}
        for field, value in expected.items():
            check(legacy_actual.get(key, {}).get(field) == str(value),
                  f"legacy comparison differs: {key}/{field}")

    manual_specs = read_tsv(SRC / "MANUAL_24_CONTEXT_AUDIT_SPECS.tsv")
    manual_actual = {row["sample_id"]: row for row in read_tsv(artifacts / "MANUAL_24_CONTEXT_AUDIT.tsv")}
    check(len(manual_specs) == len(manual_actual) == 24, "manual-24 count differs")
    for spec in manual_specs:
        row = atlas.get((spec["locus"], int(spec["ordinal"])))
        actual = manual_actual.get(spec["sample_id"], {})
        check(row is not None, f"manual spec outside atlas: {spec['sample_id']}")
        if row:
            check(actual.get("automatic_default_de") == row["automatic_default_de"] and
                  actual.get("hybrid_default_de") == row["hybrid_default_de"], f"manual dispatch differs: {spec['sample_id']}")
            check(actual.get("automatic_preferred_match") == str(int(row["automatic_default_de"] == spec["preferred_output"]))
                  and actual.get("hybrid_preferred_match") == str(int(row["hybrid_default_de"] == spec["preferred_output"])),
                  f"manual match flag differs: {spec['sample_id']}")
    check(sum(row["automatic_preferred_match"] == "1" for row in manual_actual.values()) == 24 and
          sum(row["hybrid_preferred_match"] == "1" for row in manual_actual.values()) == 24,
          "manual preferred-match total differs")

    dictionary = {row["entry_id"]: row for row in read_tsv(artifacts / "GDT774_WORKING_DICTIONARY.tsv")}
    expected_dictionary = {
        "G774-W01": ("NOMINAL_FALLBACK", FALLBACK, 327, 321, "COMPLETE_EVA_WHOLE_ONLY__NO_COMPONENT_EXPORT"),
        "G774-W02": ("CONTENT_FIELD_HEAD", "Ansatz:", 10, 10, "OCCURRENCE_CONTEXT_ONLY"),
        "G774-W03": ("MEASURE_FIELD_HEAD", "Menge:", 5, 5, "OCCURRENCE_CONTEXT_ONLY"),
        "G774-W04": ("SEQUENCE", "und dann", 4, 4, "OCCURRENCE_CONTEXT_ONLY"),
        "G774-W05": ("FIELD_BOUNDARY", ";", 3, 3, "OCCURRENCE_CONTEXT_ONLY"),
        "G774-W06": ("COORDINATION", "und", 27, 27, "OCCURRENCE_CONTEXT_ONLY"),
        "G774-W07": ("LOCKED_LOCAL_FIELD_OUTPUT", "Ansatz: | : | ;", 0, 6, "FIFTEEN_CASE_CALIBRATION_ONLY"),
    }
    check(set(dictionary) == set(expected_dictionary), "dictionary universe differs")
    for entry, expected in expected_dictionary.items():
        row = dictionary.get(entry, {})
        observed = (row.get("structural_role"), row.get("working_default_de"),
                    int(row.get("automatic_occurrences", -1)), int(row.get("hybrid_occurrences", -1)), row.get("scope"))
        check(observed == expected, f"dictionary row differs: {entry}")
        check(all(row.get(field) == "0" for field in ("default_is_translation", "confirmed_lexeme",
              "confirmed_plaintext", "semantic_identity_credit", "component_export_credit")),
              f"dictionary grants credit: {entry}")
    check(sum(int(row["automatic_occurrences"]) for row in dictionary.values()) == 376 and
          sum(int(row["hybrid_occurrences"]) for row in dictionary.values()) == 376,
          "dictionary contexts are not disjoint/exhaustive")

    structural = json.loads((artifacts / "structural_audit/STRUCTURAL_AUDIT_RESULT.json").read_text(encoding="utf-8"))
    check(structural.get("status") == "PASS__376_OL__STRUCTURAL_AUDIT__NO_NEW_PAGE", "structural audit status differs")
    check(structural.get("corpus", {}).get("occurrences") == 376 and structural.get("corpus", {}).get("loci") == 340,
          "structural audit corpus differs")
    check(structural.get("repetition") == {"adjacent_pairs": 7, "adjacent_tokens_with_any_direct_signature": 0,
          "double_lines": 28, "repeated_lines": 32, "repeated_occurrences": 68,
          "same_line_unordered_pairs": 40, "triple_lines": 4}, "structural repetition result differs")
    check(structural.get("direct_signatures", {}).get("any_signature_occurrences") == 35 and
          structural.get("direct_signatures", {}).get("no_signature_occurrences") == 341,
          "structural direct-signature result differs")
    structural_position = read_tsv(artifacts / "structural_audit/OL_376_STRUCTURAL_POSITION_ATLAS.tsv")
    check(len(structural_position) == 376 and {row["target_occurrence_id"] for row in structural_position} ==
          {row["target_occurrence_id"] for row in targets}, "structural position atlas coverage differs")
    check(len(read_tsv(artifacts / "structural_audit/OL_SELF_REPEAT_ATLAS.tsv")) == 32 and
          len(read_tsv(artifacts / "structural_audit/OL_REPEATED_NEIGHBOR_FRAMES.tsv")) == 7 and
          len(read_tsv(artifacts / "structural_audit/OL_REGISTER_SUMMARY.tsv")) == 18 and
          len(read_tsv(artifacts / "structural_audit/OL_FOLIO_HOLDOUT.tsv")) == 61 and
          len(read_tsv(artifacts / "structural_audit/OL_POSITION_MATCHED_NULL.tsv")) == 12,
          "structural summary row counts differ")

    result = json.loads((artifacts / "RESULT.json").read_text(encoding="utf-8"))
    check(result.get("experiment_id") == "GDT774" and result.get("status") == "PASS__PARTIAL_CONTEXT_TRANSFER__NO_PLAINTEXT",
          "result id/status differs")
    check(result.get("source_hashes") == actual_hashes, "result source hashes differ")
    check(result.get("automatic_renderer", {}).get("output_counts") == AUTO_OUTPUT and
          result.get("automatic_renderer", {}).get("contextual_occurrences") == 49 and
          result.get("automatic_renderer", {}).get("nominal_occurrences") == 327, "result automatic block differs")
    check(result.get("hybrid_renderer", {}).get("output_counts") == HYBRID_OUTPUT and
          result.get("hybrid_renderer", {}).get("contextual_occurrences") == 55 and
          result.get("hybrid_renderer", {}).get("nominal_occurrences") == 321 and
          result.get("hybrid_renderer", {}).get("calibration_copy_occurrences") == 15, "result hybrid block differs")
    check(result.get("calibration_replay") == {"cases": 15, "automatic_exact_matches": 9,
          "automatic_misses": 6, "hybrid_exact_matches": 15}, "result calibration block differs")
    check(result.get("amount_transfer") == {"contact_rows": 16, "raw_edges": 17, "selected_edges": 15,
          "line_final_exclusions": 2, "ol_left_of_amount": 5, "ol_right_of_amount": 12,
          "bilateral_edges": 2, "phrase_licensed_selected_edges": 8,
          "directional_c0_selected_edges": 7}, "result amount block differs")
    check(result.get("manual_context_audit") == {"cases": 24, "automatic_preferred_matches": 24,
          "hybrid_preferred_matches": 24, "independent_semantic_score_credit": 0}, "result manual block differs")
    check(result.get("legacy_crosswalk") == {"matched_occurrences": 376, "grundansatz_outputs": 376,
          "gdt664_inherited_evidence": 376}, "result legacy block differs")
    check(result.get("structural_audit") == structural, "embedded structural result differs")
    ceiling = {"new_pages_opened": 0, "new_images_opened": 0, "new_ocr": 0, "new_transcription": 0,
               "f84_accessed": 0, "f84r_accessed": 0, "confirmed_lexemes": 0,
               "confirmed_plaintext_clauses": 0, "component_exports": 0,
               "specific_medium_selected": 0, "translation_claimed": 0}
    check(result.get("claim_ceiling") == ceiling, "result claim ceiling differs")

    # Every machine-readable semantic, translation, plaintext, and component-credit flag remains zero.
    zero_fields = {"default_is_translation", "relation_is_translation", "translation_credit",
                   "confirmed_lexeme", "confirmed_plaintext", "semantic_identity_credit",
                   "component_export_credit", "score_credit", "audit_is_independent_semantic_test"}
    forbidden_credit_found = False
    translation_flag_found = False
    for name in outputs:
        if name.endswith(".tsv"):
            for number, row in enumerate(read_tsv(artifacts / name), 1):
                for field in zero_fields & set(row):
                    forbidden_credit_found |= row[field] != "0"
                    if field in {"default_is_translation", "relation_is_translation", "translation_credit",
                                 "confirmed_lexeme", "confirmed_plaintext"}:
                        translation_flag_found |= row[field] != "0"
                    check(row[field] == "0", f"{name} row {number} grants {field}")
    medium_output_found = False
    for row in atlas_actual:
        output_text = f"{row['automatic_default_de']} {row['hybrid_default_de']}".casefold()
        has_medium = any(word in output_text for word in ("öl", "oil", "wasser", "water", "wein", "wine"))
        medium_output_found |= has_medium
        check(not has_medium,
              f"specific medium output at {row['target_occurrence_id']}")
    medium_output_found |= result.get("claim_ceiling", {}).get("specific_medium_selected") != 0
    translation_flag_found |= result.get("claim_ceiling", {}).get("translation_claimed") != 0
    report_text = REPORT.read_text(encoding="utf-8")
    check("Öl, Wasser und Wein bleiben ununterscheidbar" in report_text, "report omits medium non-identification")
    check("kein" in structural.get("claim_ceiling", "").casefold() or " no " in structural.get("claim_ceiling", "").casefold(),
          "structural claim ceiling is not negative")

    local_marker, key_marker, access_marker = "/" + "home/", "PRIVATE" + " KEY", "AK" + "IA"
    scan = [*(artifacts / name for name in outputs), REPORT, *sorted(SRC.glob("*.tsv")), RUN,
            SRC / "structural_audit.py", Path(__file__).resolve()]
    for path in scan:
        text = path.read_text(encoding="utf-8", errors="replace")
        check(local_marker not in text, f"absolute local path leaked: {path.name}")
        check(key_marker not in text and access_marker not in text, f"credential-like text leaked: {path.name}")

    hashes, report_hash = {}, ""
    with tempfile.TemporaryDirectory(prefix="gdt774_validate_") as temporary:
        temporary_path = Path(temporary)
        replay_artifacts, replay_report = temporary_path / "artifacts", temporary_path / "REPORT.md"
        done = subprocess.run(["python3", str(RUN), "--output-dir", str(replay_artifacts),
                               "--report-path", str(replay_report)], cwd=ROOT, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        check(done.returncode == 0, f"runner replay failed: {done.stderr}")
        if done.returncode == 0:
            for name in outputs:
                replay, published = replay_artifacts / name, artifacts / name
                check(replay.is_file(), f"replay output missing: {name}")
                if replay.is_file() and published.is_file():
                    check(replay.read_bytes() == published.read_bytes(), f"byte replay differs: {name}")
                    hashes[name] = sha256(published)
            check(replay_report.is_file() and replay_report.read_bytes() == REPORT.read_bytes(), "report byte replay differs")
            if replay_report.is_file():
                report_hash = sha256(REPORT)

    status = "PASS" if not failures else "FAIL"
    payload = {
        "experiment_id": "GDT774", "status": status, "checks": checks, "failures": failures,
        "source_hash_locks_verified": len(actual_hashes), "reader_exact_occurrences": len(atlas_expected),
        "independent_dispatch_reconstruction": True, "independent_amount_edge_reconstruction": True,
        "automatic_branch_counts": dict(auto_branches), "hybrid_branch_counts": dict(hybrid_branches),
        "automatic_output_counts": dict(auto_outputs), "hybrid_output_counts": dict(hybrid_outputs),
        "amount_edges": len(amount_edges), "amount_line_final_exclusions": len(excluded),
        "calibration_automatic_matches": sum(int(row["automatic_exact_match"]) for row in calibration_expected),
        "calibration_hybrid_matches": sum(int(row["hybrid_exact_match"]) for row in calibration_expected),
        "adjacent_ol_pairs": len(expected_pair_keys), "f15_bridges": len(f15),
        "semantic_and_component_credit_zero": not forbidden_credit_found,
        "specific_medium_selected": medium_output_found,
        "confirmed_translation_claimed": translation_flag_found,
        "byte_replay_outputs": len(hashes), "artifact_sha256": hashes, "report_sha256": report_hash,
        "f84_accessed": False, "f84r_accessed": False,
    }
    validation.parent.mkdir(parents=True, exist_ok=True)
    validation.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
