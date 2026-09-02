#!/usr/bin/env python3
"""Independent recomputation and byte replay for GDT744."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
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
BASE = Path("experiments/yolo/gdt744_historical_microfield_channel_bridge")
EXP = ROOT / BASE
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
MANIFEST = EXP / "experiment.json"
G735_RESULT = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/RESULT.json"
G735_SLOTS = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_SLOT_CENSUS.tsv"
G739_WINDOWS = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/artifacts/WINDOW_202_TOKEN_AUDIT.tsv"
G743_PATCHES = ROOT / "experiments/yolo/gdt743_r2_run_intersection_adjudication/artifacts/TARGET_202_RENDERER_PATCH_V5.tsv"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "PARTIAL__16_COMPLETE_RECURRENT_EXACT_WHOLE_CHANNEL_TEMPLATES__"
    "80_TEMPLATE_BACKED_FIELDS__47_COMPLETE_PLUS_33_RADIUS_CENSORED__"
    "69_OF_80_W3_TEMPLATE_RETAINED__67_SAME_CHANNEL__"
    "42_UNRESOLVED_CONTENT_SLOT_CELLS__"
    "TARGET_WHOLES_REMAIN_LEVEL_OR_STATE_FIELDS__ZERO_LEXEMES__NO_NEW_PAGE"
)
GENERATED = (
    "MICROFIELD_202_CHANNEL_DISPATCH.tsv",
    "FORM_CHANNEL_RECURRENCE_CENSUS.tsv",
    "UNRESOLVED_CONTENT_SLOT_CANDIDATES.tsv",
    "PASSAGE_20_MICROFIELD_READER.tsv",
    "GDT744_GDT388_MICROFIELD_EDGE_PACKET.tsv",
    "GDT744_GDT388_EDGE_INTAKE.json",
    "GDT744_HISTORICAL_MICROFIELD_READER.md",
    "RESULT.json",
)
QUALITY = {"HOT", "COLD", "DRY", "MOIST"}
OBJECTS = {"AMOUNT", "INGREDIENT", "MATERIAL", "PART", "PREPARATION"}
W23 = {"W2_PROVISIONAL_WORKING", "W3_SOLID_WORKING_THEORY"}
W3 = {"W3_SOLID_WORKING_THEORY"}
EXPECTED_COMPLETE_CLASSES = {
    ("lcheol", "DESCRIPTIVE_QUALITY"),
    ("lkaiin", "PRESCRIPTIVE_RECIPE"),
    ("lkaiin", "DESCRIPTIVE_MATERIA"),
    ("lkaiin", "DESCRIPTIVE_QUALITY"),
    ("lkain", "PRESCRIPTIVE_RECIPE"),
    ("lkain", "PRESCRIPTIVE_PROCESS"),
    ("lkain", "DESCRIPTIVE_MATERIA"),
    ("lkain", "QUANTITY_OR_PART"),
    ("lkar", "DESCRIPTIVE_MATERIA"),
    ("lkar", "DESCRIPTIVE_QUALITY"),
    ("lkar", "QUANTITY_OR_PART"),
    ("pcheol", "QUANTITY_OR_PART"),
    ("rain", "DESCRIPTIVE_MATERIA"),
    ("sain", "DESCRIPTIVE_MATERIA"),
    ("sain", "DESCRIPTIVE_QUALITY"),
    ("sain", "QUANTITY_OR_PART"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def values(value: str) -> set[str]:
    if value in {"", "NONE", "NA", "OPEN", "NOT_APPLICABLE"}:
        return set()
    return set(value.split("|"))


def joined(items: set[str]) -> str:
    return "|".join(sorted(items)) or "NONE"


def strong(row: dict[str, str], confidence: set[str]) -> bool:
    return bool(
        row["neighbor_confidence_level"] in confidence
        and row["neighbor_reader_exact"] == "1"
        and row["neighbor_unknown_v99r7"] == "0"
        and row["neighbor_composition_semantic_credit"] == "0"
        and row["strict_initial_head_neighbor"] == "0"
        and row["another_gdt738_target"] == "0"
        and row["retired_patient_words"] == "NONE"
        and row["head_or_body_lexeme_credit"] == "0"
        and row["component_export_credit"] == "0"
    )


def candidate(row: dict[str, str]) -> bool:
    return bool(
        row["neighbor_unknown_v99r7"] == "1"
        and row["neighbor_reader_exact"] == "1"
        and row["strict_initial_head_neighbor"] == "0"
        and row["another_gdt738_target"] == "0"
        and row["retired_patient_words"] == "NONE"
        and row["head_or_body_lexeme_credit"] == "0"
        and row["component_export_credit"] == "0"
    )


def independent_channel(tags: set[str]) -> str:
    if tags & {"PASS", "PROCESS"} and tags & OBJECTS:
        return "PRESCRIPTIVE_RECIPE"
    if tags & {"PASS", "PROCESS"}:
        return "PRESCRIPTIVE_PROCESS"
    if tags & QUALITY and tags & {"MATERIAL", "PART", "PREPARATION"}:
        return "DESCRIPTIVE_MATERIA"
    if tags & QUALITY:
        return "DESCRIPTIVE_QUALITY"
    if tags & {"AMOUNT", "PART"}:
        return "QUANTITY_OR_PART"
    if tags & {"INGREDIENT", "MATERIAL", "PREPARATION"}:
        return "MATERIA_OR_INGREDIENT"
    return "OPEN"


def effective_tags(
    row: dict[str, str], supplements: dict[str, dict[str, str]]
) -> set[str]:
    tags = values(row["axis_tags"])
    spec = supplements.get(row["neighbor_surface"])
    if spec is None:
        return tags
    if row["neighbor_semantic_value_de"] != spec["expected_semantic_value_de"]:
        raise AssertionError("supplement semantic input drift")
    if row["neighbor_confidence_level"] != spec["expected_confidence_level"]:
        raise AssertionError("supplement confidence input drift")
    return tags | values(spec["added_field_tags"])


def side_span(
    window: dict[tuple[str, int], dict[str, str]], side: str, radius: int = 5
) -> tuple[list[dict[str, str]], str]:
    rows: list[dict[str, str]] = []
    for distance in range(1, radius + 1):
        row = window.get((side, distance))
        if row is None:
            return rows, f"LINE_EDGE_AFTER_R{distance - 1}"
        tags = values(row["axis_tags"])
        if row["another_gdt738_target"] == "1":
            return rows, f"NEXT_TARGET_BEFORE_R{distance}"
        if row["strict_initial_head_neighbor"] == "1":
            return rows, f"STRICT_INITIAL_BEFORE_R{distance}"
        if side == "L" and "CLOSE" in tags:
            return rows, f"PRIOR_CLOSE_BEFORE_R{distance}"
        rows.append(row)
        if side == "R" and "CLOSE" in tags:
            return rows, f"CURRENT_CLOSE_INCLUDED_R{distance}"
    return rows, f"RADIUS{radius}_CENSORED"


def clipped(
    window: dict[tuple[str, int], dict[str, str]], radius: int = 5
) -> tuple[list[dict[str, str]], str, str]:
    left, left_reason = side_span(window, "L", radius)
    right, right_reason = side_span(window, "R", radius)
    return left + right, left_reason, right_reason


def unclipped(
    window: dict[tuple[str, int], dict[str, str]], radius: int = 5
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for side in ("L", "R"):
        for distance in range(1, radius + 1):
            row = window.get((side, distance))
            if row is None:
                break
            rows.append(row)
    return rows


def bundle(
    span: list[dict[str, str]], confidence: set[str],
    supplements: dict[str, dict[str, str]],
) -> tuple[list[dict[str, str]], set[str], str]:
    anchors = [row for row in span if strong(row, confidence)]
    tags: set[str] = set()
    for row in anchors:
        tags |= effective_tags(row, supplements)
    signature = "|".join(
        f"{row['side']}{row['distance']}@{row['neighbor_ordinal']}:"
        f"{row['neighbor_surface']}:{joined(effective_tags(row, supplements))}"
        for row in sorted(anchors, key=lambda item: int(item["neighbor_ordinal"]))
    ) or "NONE"
    return anchors, tags, signature


def derive(
    patches: list[dict[str, str]], windows: list[dict[str, str]],
    supplements: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    by_patch: dict[str, dict[tuple[str, int], dict[str, str]]] = defaultdict(dict)
    for row in windows:
        by_patch[row["patch_id"]][(row["side"], int(row["distance"]))] = row
    output: list[dict[str, object]] = []
    for patch in patches:
        window = by_patch[patch["patch_id"]]
        span, left_reason, right_reason = clipped(window)
        r2_span, _, _ = clipped(window, 2)
        anchors, tags, signature = bundle(span, W23, supplements)
        w3_anchors, w3_tags, w3_signature = bundle(span, W3, supplements)
        r2_anchors, r2_tags, _ = bundle(r2_span, W23, supplements)
        raw_anchors, raw_tags, _ = bundle(unclipped(window), W23, supplements)
        complete = not left_reason.startswith("RADIUS") and not right_reason.startswith("RADIUS")
        output.append({
            "patch": patch,
            "patch_id": patch["patch_id"],
            "surface": patch["surface"],
            "page": patch["page"],
            "span": span,
            "left_reason": left_reason,
            "right_reason": right_reason,
            "complete": complete,
            "anchors": anchors,
            "tags": tags,
            "signature": signature,
            "channel": independent_channel(tags),
            "w3_anchors": w3_anchors,
            "w3_signature": w3_signature,
            "w3_channel": independent_channel(w3_tags),
            "r2_channel": independent_channel(r2_tags),
            "raw_channel": independent_channel(raw_tags),
            "supplement_contacts": sum(row["neighbor_surface"] in supplements for row in anchors),
        })
    return output


def classes(
    rows: list[dict[str, object]], channel: str, signature: str,
    complete_only: bool,
) -> tuple[dict[tuple[str, str], list[dict[str, object]]], set[tuple[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if complete_only and not row["complete"]:
            continue
        grouped[(str(row["surface"]), str(row[channel]))].append(row)
    recurrent = {
        key for key, members in grouped.items()
        if key[1] != "OPEN"
        and len({str(row["page"]) for row in members}) >= 2
        and len({str(row[signature]) for row in members}) >= 2
    }
    return grouped, recurrent


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

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT744", "manifest experiment id")
    check(manifest["slug"] == "historical_microfield_channel_bridge", "manifest slug")
    check(manifest["status"] == STATUS, "manifest status")
    check(manifest["dependencies"] == ["GDT735", "GDT739", "GDT743"], "manifest dependencies")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed selectors forbidden")
    check(bool(manifest["question"]) and bool(manifest["claim_ceiling"]), "manifest question and ceiling")
    check(manifest["validation"] == {"artifact": str(VALIDATION_REL), "status": "PASS"}, "manifest validation contract")
    expected_inputs = {str(path.relative_to(ROOT)) for path in (G735_RESULT, G735_SLOTS, G739_WINDOWS, G743_PATCHES)}
    check({row["path"] for row in manifest["inputs"]} == expected_inputs, "manifest exact four inputs")
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file() and sha256(path) == binding["sha256"], f"input hash {binding['path']}")

    rules = read_tsv(SRC / "FIELD_CHANNEL_RULES.tsv")
    check(len(rules) == 7 and [int(row["precedence"]) for row in rules] == list(range(1, 8)), "seven ordered channel rules")
    check(rules[0]["required_any_1"] == "PASS|PROCESS" and "INGREDIENT" in rules[0]["required_any_2"], "PASS and ingredient rule wiring")
    supplements_list = read_tsv(SRC / "WHOLE_HISTORICAL_ROLE_SUPPLEMENTS.tsv")
    supplements = {row["surface"]: row for row in supplements_list}
    check(set(supplements) == {"olor", "qoly"} and len(supplements_list) == 2, "two exact-whole role supplements")
    check(supplements["olor"]["added_field_tags"] == "INGREDIENT", "olor ingredient-role supplement")
    check(values(supplements["qoly"]["added_field_tags"]) == {"CLOSE", "PROCESS"}, "qoly process-close role supplement")
    check(all(row["lexeme_credit"] == "0" for row in supplements_list), "supplements grant zero lexeme credit")

    historical = json.loads(G735_RESULT.read_text(encoding="utf-8"))
    check(historical["historical"]["direct_two_channel_sources"] == ["HSR010"], "GDT735 direct two-channel witness")
    slot_map = {row["slot"]: row for row in read_tsv(G735_SLOTS)}
    check(all(int(slot_map[key]["descriptive_rows"]) for key in ("DEGREE", "HOT", "DRY", "PLANT_PART")), "historical descriptive slots")
    check(all(int(slot_map[key]["prescriptive_rows"]) for key in ("INGREDIENT", "RECIPE_COMMAND", "NUMBER", "UNIT")), "historical prescriptive slots")

    window_rows = read_tsv(G739_WINDOWS)
    patch_rows = sorted(read_tsv(G743_PATCHES), key=lambda row: row["gdt743_patch_id"])
    check(len(window_rows) == 1373 and len(patch_rows) == 202, "inherited 1373 windows and 202 targets")
    check(len({row["patch_id"] for row in patch_rows}) == 202, "unique inherited target patches")
    check(not any(row["page"].startswith("f84") for row in window_rows + patch_rows), "no sealed selector in inputs")
    derived = derive(patch_rows, window_rows, supplements)
    by_patch = {str(row["patch_id"]): row for row in derived}
    check(len(by_patch) == 202, "independent 202-field derivation")

    all_groups, all_classes = classes(derived, "channel", "signature", False)
    complete_groups, complete_classes = classes(derived, "channel", "signature", True)
    _, w3_classes = classes(derived, "w3_channel", "w3_signature", True)
    check(complete_classes == EXPECTED_COMPLETE_CLASSES, "exact sixteen complete recurrent classes")
    check(len(all_classes) == 19 and complete_classes <= all_classes, "nineteen window classes contain sixteen complete classes")
    check(sum(bool(row["complete"]) for row in derived) == 140, "140 fully bounded microfields")
    check(sum(not bool(row["complete"]) for row in derived) == 62, "62 radius-censored microfields")
    raw_counts = Counter(str(row["channel"]) for row in derived)
    check(raw_counts == Counter({
        "OPEN": 93, "DESCRIPTIVE_MATERIA": 45, "DESCRIPTIVE_QUALITY": 23,
        "PRESCRIPTIVE_RECIPE": 19, "QUANTITY_OR_PART": 11,
        "MATERIA_OR_INGREDIENT": 6, "PRESCRIPTIVE_PROCESS": 5,
    }), "independent raw channel counts")

    def tier(row: dict[str, object]) -> str:
        key = (str(row["surface"]), str(row["channel"]))
        if key in complete_classes:
            return "F3_RECURRENT_COMPLETE_CONTEXT" if row["complete"] else "F2_RECURRENT_TEMPLATE_PARTIAL_CONTEXT"
        if key in all_classes:
            return "F1_RECURRENT_WINDOW_ONLY"
        if row["channel"] != "OPEN":
            return "F1_SINGLE_CONTEXT"
        return "F0_OPEN"

    tier_counts = Counter(tier(row) for row in derived)
    check(tier_counts == Counter({
        "F0_OPEN": 93, "F1_SINGLE_CONTEXT": 22,
        "F1_RECURRENT_WINDOW_ONLY": 7,
        "F2_RECURRENT_TEMPLATE_PARTIAL_CONTEXT": 33,
        "F3_RECURRENT_COMPLETE_CONTEXT": 47,
    }), "independent confidence tier counts")
    licensed = [row for row in derived if (str(row["surface"]), str(row["channel"])) in complete_classes]
    check(len(licensed) == 80, "eighty complete-template-backed fields")
    check(Counter(str(row["channel"]) for row in licensed) == Counter({
        "DESCRIPTIVE_MATERIA": 40, "DESCRIPTIVE_QUALITY": 17,
        "PRESCRIPTIVE_RECIPE": 11, "QUANTITY_OR_PART": 9,
        "PRESCRIPTIVE_PROCESS": 3,
    }), "template channel counts")
    quality_conflicts = sum(
        {"HOT", "COLD"} <= row["tags"] or {"DRY", "MOIST"} <= row["tags"]
        for row in licensed
    )
    check(quality_conflicts == 7, "seven licensed quality conflicts")
    check(sum(int(row["supplement_contacts"]) for row in derived) == 1, "one in-bound exact-whole supplement contact")
    check(by_patch["G738-P0056"]["channel"] == "MATERIA_OR_INGREDIENT", "olor changes field to ambiguous material/ingredient")
    check(by_patch["G738-P0057"]["channel"] == "OPEN", "qoly remains beyond included close boundary")

    w3_retained = sum(
        (str(row["surface"]), str(row["w3_channel"])) in w3_classes for row in licensed
    )
    w3_same = sum(
        (str(row["surface"]), str(row["w3_channel"])) in w3_classes
        and row["channel"] == row["w3_channel"] for row in licensed
    )
    check((w3_retained, w3_same) == (69, 67), "W3-only 69 retained and 67 same-channel")
    check(sum(row["channel"] == row["raw_channel"] for row in derived) == 152, "unclipped sensitivity 152 matches")
    check(sum(row["channel"] == row["r2_channel"] for row in derived) == 172, "radius-two sensitivity 172 matches")

    field_rows = read_tsv(art / "MICROFIELD_202_CHANNEL_DISPATCH.tsv")
    census_rows = read_tsv(art / "FORM_CHANNEL_RECURRENCE_CENSUS.tsv")
    candidate_rows = read_tsv(art / "UNRESOLVED_CONTENT_SLOT_CANDIDATES.tsv")
    passage_rows = read_tsv(art / "PASSAGE_20_MICROFIELD_READER.tsv")
    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(len(field_rows) == 202 and len({row["gdt744_field_id"] for row in field_rows}) == 202, "artifact 202 unique fields")
    check(len(census_rows) == 84, "artifact full twelve-by-seven census")
    check(len(candidate_rows) == 42, "artifact 42 unresolved candidate cells")
    check(len(passage_rows) == 20 and len({row["locus"] for row in passage_rows}) == 20, "artifact twenty distinct passages")
    artifact_by_patch = {row["patch_id"]: row for row in field_rows}
    check(set(artifact_by_patch) == set(by_patch), "artifact and independent patch sets equal")
    for patch_id, source in by_patch.items():
        row = artifact_by_patch[patch_id]
        check(row["left_boundary_reason"] == source["left_reason"], f"left boundary {patch_id}")
        check(row["right_boundary_reason"] == source["right_reason"], f"right boundary {patch_id}")
        check(row["boundary_complete"] == str(int(bool(source["complete"]))), f"boundary complete {patch_id}")
        check(row["strong_anchor_tags"] == joined(source["tags"]), f"anchor tags {patch_id}")
        check(row["strong_anchor_signature"] == source["signature"], f"anchor signature {patch_id}")
        check(row["raw_field_channel"] == source["channel"], f"channel {patch_id}")
        check(row["field_confidence_tier"] == tier(source), f"tier {patch_id}")
        key = (str(source["surface"]), str(source["channel"]))
        check(row["template_backed_field_reading"] == str(int(key in complete_classes)), f"template gate {patch_id}")
        check(row["w3_only_field_channel"] == source["w3_channel"], f"W3 channel {patch_id}")
        check(row["r2_field_channel"] == source["r2_channel"], f"R2 channel {patch_id}")
        check(row["unclipped_field_channel"] == source["raw_channel"], f"unclipped channel {patch_id}")
        check(row["literal_lexeme_claimed"] == "0" and row["plaintext_clause_claimed"] == "0", f"zero literal claims {patch_id}")
        if row["quality_conflict"] == "1":
            check("konkurrierende Anker" in row["field_render_de"], f"quality conflict rendered {patch_id}")
    check(True, "all 202 field rows independently match")

    census_map = {(row["surface"], row["channel"]): row for row in census_rows}
    check(len(census_map) == 84, "census keys unique")
    for key, row in census_map.items():
        members = all_groups.get(key, [])
        complete_members = complete_groups.get(key, [])
        check(int(row["observed_occurrences"]) == len(members), f"census observations {key}")
        check(int(row["complete_occurrences"]) == len(complete_members), f"census complete {key}")
        check(int(row["window_recurrence_gate"]) == int(key in all_classes), f"census window gate {key}")
        check(int(row["complete_template_gate"]) == int(key in complete_classes), f"census complete gate {key}")
    check(True, "all 84 census cells independently match")

    independent_candidates: set[tuple[str, str, str]] = set()
    for row in licensed:
        for neighbor in row["span"]:
            if candidate(neighbor):
                independent_candidates.add((
                    str(row["patch_id"]), neighbor["neighbor_ordinal"], neighbor["neighbor_surface"]
                ))
    artifact_candidates = {
        (row["patch_id"], row["candidate_ordinal"], row["candidate_surface"])
        for row in candidate_rows
    }
    check(independent_candidates == artifact_candidates and len(independent_candidates) == 42, "independent candidate slot set")
    check(len({row["candidate_surface"] for row in candidate_rows}) == 41, "41 candidate surfaces")
    check(len({row["gdt744_field_id"] for row in candidate_rows}) == 28, "28 fields contain candidates")
    check(sum(int(row["cross_page_content_identity_gate"]) for row in candidate_rows) == 0, "zero cross-page candidate identities")
    check(all(row["literal_identity"] == "OPEN" and row["confirmed_lexeme"] == "0" for row in candidate_rows), "candidate identities remain open")

    target_specific = {row["patch_id"] for row in patch_rows if row["specific_local_dispatch_gdt743"] == "1"}
    field_specific = {str(row["patch_id"]) for row in licensed}
    check((len(target_specific), len(field_specific), len(target_specific | field_specific)) == (59, 80, 95), "renderer union 59 plus 80 gives 95")
    check(len(field_specific - target_specific) == 36, "36 newly field-specific occurrences")
    check(all(row["combined_target_field_render_de"] and row["field_render_de"] for row in field_rows), "all field cards nonempty")
    banned = ("Arbeitsgut", "Arbeitsschritt", "Arbeitszyklus", "work item")
    check(not any(term in row["combined_target_field_render_de"] for term in banned for row in field_rows), "generic work-item prose absent")

    assessment_rows = read_tsv(SRC / "MANUAL_PASSAGE_ASSESSMENTS.tsv")
    assessment_map = {row["reader_id"]: row for row in assessment_rows}
    check(len(assessment_rows) == len(assessment_map) == 20, "twenty manual assessments")
    check(sum(int(row["manual_information_gain"]) for row in assessment_rows) == 17, "seventeen manually useful examples")
    check(Counter(row["selection_role"] for row in passage_rows) == Counter({
        "COMPLETE_TEMPLATE_CLASS_EXEMPLAR": 16,
        "CENSORED_TEMPLATE_EXEMPLAR": 1,
        "WINDOW_ONLY_COUNTERCASE": 2,
        "OPEN_COUNTERCASE": 1,
    }), "passage selection strata")
    for row in passage_rows:
        assessment = assessment_map[row["reader_id"]]
        check(row["gdt744_field_id"] == assessment["gdt744_field_id"], f"manual field join {row['reader_id']}")
        check(row["manual_coherence"] == assessment["manual_coherence"], f"manual judgment join {row['reader_id']}")
        check(row["manual_information_gain"] == assessment["manual_information_gain"], f"manual information join {row['reader_id']}")
    check(True, "all manual passage joins match")

    check(result["status"] == STATUS and result["schema"] == "GDT744_HISTORICAL_MICROFIELD_CHANNEL_BRIDGE_RESULT_V1", "result status and schema")
    check(result["scope"]["new_pages_used"] == result["scope"]["new_images_used"] == result["scope"]["new_transcriptions_used"] == 0, "result no new source access")
    check(result["scope"]["f84_used"] is False and result["scope"]["f84r_used"] is False, "result sealed pages unused")
    check(result["channel"]["complete_recurrent_exact_whole_channel_templates"] == 16, "result sixteen templates")
    check(result["channel"]["template_backed_occurrences"] == 80, "result eighty fields")
    check(result["renderer"]["combined_specific_occurrences"] == 95, "result combined renderer count")
    check(result["renderer"]["manual_information_gain_examples"] == 17, "result manual information count")
    check(result["content_slots"] == {
        "candidate_cells": 42, "candidate_fields": 28,
        "candidate_surfaces": 41, "cross_page_identity_gates": 0,
    }, "result candidate slot summary")
    check(result["historical_bridge"]["inherited_exact_whole_role_supplement_contacts"] == 1, "result supplement contact count")
    check(all(value == 0 for value in result["claims"].values()), "result claim counters all zero")
    for name in GENERATED[:-1]:
        rel = str(BASE / "artifacts" / name)
        check(result["artifact_hashes"][rel] == sha256(art / name), f"result artifact hash {name}")

    intake_run = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(art / "GDT744_GDT388_MICROFIELD_EDGE_PACKET.tsv")],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    intake = json.loads(intake_run.stdout)
    expected_intake = {
        "capacity_gate_50_edges_5_folios": False,
        "discovery_edges": 0,
        "eligible_edges": 0,
        "eligible_folios": 0,
        "errors": ["edge row 2: formal access is not sealed"],
        "holdout_edges": 0,
        "holdout_gate": False,
        "mobile_edges": 0,
        "mobile_null_gate": False,
        "packet_rows": 1,
        "score_ready": False,
        "status": "INVALID_PACKET",
    }
    check(intake == expected_intake, "edge intake remains invalid and not score-ready")
    check(json.loads((art / "GDT744_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8")) == intake, "stored edge intake matches executable")

    with tempfile.TemporaryDirectory(prefix=".gdt744_replay_", dir=EXP) as temp_name:
        replay_dir = Path(temp_name)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay_dir)],
            cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay exits zero")
        for name in GENERATED:
            check((replay_dir / name).read_bytes() == (art / name).read_bytes(), f"byte replay {name}")
    check(True, "all generated artifacts byte-identical")

    payload = {
        "schema": "GDT744_VALIDATION_V1",
        "status": "PASS",
        "check_count": len(checks),
        "checks": checks,
        "byte_replay": "PASS",
        "edge_intake": intake,
        "independent_summary": {
            "fields": 202,
            "fully_bounded": 140,
            "complete_templates": 16,
            "template_backed_fields": 80,
            "combined_specific": 95,
            "candidate_cells": 42,
            "manual_information_gain": 17,
        },
    }
    if not args.no_write:
        (art / "VALIDATION.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "schema": payload["schema"], "status": payload["status"],
        "check_count": payload["check_count"], "byte_replay": payload["byte_replay"],
        "independent_summary": payload["independent_summary"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
