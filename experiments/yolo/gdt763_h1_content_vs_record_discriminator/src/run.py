#!/usr/bin/env python3
"""Discriminate a field-bearing H1 head from source/result, and type ol slots."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
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
BASE_REL = Path("experiments/yolo/gdt763_h1_content_vs_record_discriminator")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G762_RUN_REL = Path("experiments/yolo/gdt762_moist_medium_candidate_discrimination/src/run.py")
G736_GRID_REL = Path("experiments/yolo/gdt736_opaque_head_record_role_bridge/artifacts/OPAQUE_96_CONCRETE_ROLE_GRID.tsv")
G737_FORM_REL = Path("experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_273_FORM_ROLE_BRIDGE.tsv")
G760_QUANTITY_REL = Path("experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts/QUANTITY_281_EXPRESSION_ATLAS.tsv")
G760_CONTENT_REL = Path("experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts/CONTENT_45_ATTACHMENT_ATLAS.tsv")
G760_DECK_REL = Path("experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts/CONTENT_ANCHOR_35_CANDIDATE_DECK.tsv")
G762_OL_REL = Path("experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/OL_AMOUNT_EXPRESSION_CONTACT_ATLAS.tsv")
G735_HISTORY_REL = Path("experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_ENTRY_ATLAS.tsv")
G755_HISTORY_REL = Path("experiments/yolo/gdt755_top24_historical_register_crosswalk/src/HISTORICAL_EXPRESSION_BANK.tsv")

OUTPUT_NAMES = (
    "H1_199_OCCURRENCE_SEQUENCE_ATLAS.tsv",
    "H1_PARAGRAPH_MEDIAL_R1_R3_PROFILE.tsv",
    "H1_CLASS_STATE_PREDECESSOR_PROFILE.tsv",
    "PCHEEY_3_FIELD_FRAME.tsv",
    "GAPPED_DAIIN_FRAME_COHORT.tsv",
    "GAPPED_DAIIN_FRAME_HITS.tsv",
    "STRICT_N3_PARAGRAPH_MEDIAL_CONTROL.tsv",
    "PCHEEY_HYPOTHESIS_SCORECARD.tsv",
    "OL_16_SLOT_FUNCTION_ATLAS.tsv",
    "OL_18_MATCHED_CONTENT_COMPARATORS.tsv",
    "OL_CONTENT_CLASS_PLACEMENT_COMPARISON.tsv",
    "OL_AMOUNT_FORMULA_RECURRENCE.tsv",
    "HISTORICAL_FIELD_FUNCTION_COMPARISON.tsv",
    "TWO_WHOLE_RENDERER_REVISION.tsv",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__199_H1_OCCURRENCES__52_PARAGRAPH_START_MEDIAL_H1__"
    "PCHEEY_3_OF_3_POST_SHO_SHEO__2_OF_3_PCHEEY_X_DAIIN_VS_3_OF_196_OTHER_H1__"
    "SELECT_FIELD_BEARING_FORM_II_RECORD_CONTENT_HEAD__C1_SOURCE_RIVAL__"
    "RESULT_DOWNGRADED_ZERO_PROCESS_CLOSE_WITHIN_PLUS_MINUS3__"
    "OL_16_AMOUNT_POSITIONS_HEAD9_OBJECT1_CONTEXT5_BILATERAL1__"
    "OL_PREPARATION_LIKE_NOT_FIXED_SUBSTANCE__ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
)
HEAD_IDS = ("H1", "H2", "H3", "H4")
ROLE_ORDER = (
    "QUALITY_STAGE", "SCALAR_VALUE", "AMOUNT_VALUE", "CONTENT_PREPARATION",
    "PROCESS_PASS", "CLOSE", "H1_RECORD_FORM", "H2_RECORD_FORM",
    "H3_RECORD_FORM", "H4_RECORD_FORM", "KNOWN_OTHER", "OPEN",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g762 = load_module("gdt762_builder_for_gdt763", ROOT / G762_RUN_REL)
physical_folio = g762.physical_folio
line_position = g762.line_position
fixed = g762.fixed


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def compact(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def ordered_roles(values: Iterable[str]) -> str:
    chosen = set(values)
    return "|".join(role for role in ROLE_ORDER if role in chosen) or "OPEN"


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    row1, row2, col1 = a + b, c + d, a + c
    total = row1 + row2

    def probability(x: int) -> float:
        return math.comb(col1, x) * math.comb(total - col1, row1 - x) / math.comb(total, row1)

    low, high = max(0, row1 - (total - col1)), min(row1, col1)
    observed = probability(a)
    return min(1.0, sum(probability(x) for x in range(low, high + 1) if probability(x) <= observed + 1e-15))


def odds_ratio(a: int, b: int, c: int, d: int) -> str:
    if b * c == 0:
        return "INF" if a * d else "NA"
    return fixed((a * d) / (b * c))


def build_head_registry(training: list[dict[str, str]], held: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    registry: dict[str, dict[str, str]] = {}
    for source, rows in (("GDT736_TRAINING", training), ("GDT737_HELD", held)):
        for row in rows:
            surface = row["form"]
            if surface in registry:
                raise AssertionError(f"duplicate head form: {surface}")
            registry[surface] = {
                "head_id": row["opaque_head_id"], "body": row["body"], "registry_source": source,
                "record_role": row.get("selected_formal_role", row.get("gdt736_training_record_role", "OPEN")),
                "body_role_de": row.get("revised_body_role_de", row.get("exploratory_body_candidate_de", "offen")),
            }
    return registry


def amount_position_map(rows: list[dict[str, str]]) -> dict[tuple[str, int], dict[str, str]]:
    output: dict[tuple[str, int], dict[str, str]] = {}
    for row in rows:
        for ordinal in range(int(row["start_ordinal"]), int(row["end_ordinal"]) + 1):
            key = (row["locus"], ordinal)
            if key in output:
                raise AssertionError(f"overlapping amount expressions: {key}")
            output[key] = row
    return output


def roles_from_axes(axes: set[str]) -> set[str]:
    roles: set[str] = set()
    if axes & {"HOT", "COLD", "DRY", "MOIST", "BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE", "LEVEL_I", "LEVEL_II", "LEVEL_III"}:
        roles.add("QUALITY_STAGE")
    if axes & {"AMOUNT", "PART"}:
        roles.add("AMOUNT_VALUE")
    if axes & {"MATERIAL", "PREPARATION"}:
        roles.add("CONTENT_PREPARATION")
    if axes & {"PROCESS", "PASS"}:
        roles.add("PROCESS_PASS")
    if "CLOSE" in axes:
        roles.add("CLOSE")
    return roles


def slot_record(
    context: object, locus: str, ordinal: int,
    head_registry: dict[str, dict[str, str]], amount_positions: dict[tuple[str, int], dict[str, str]],
    state_map: dict[str, dict[str, str]], content_map: dict[str, dict[str, str]],
    manual: dict[str, dict[str, str]], suspect: set[str], meanings: dict[str, str], sources: dict[str, str],
) -> dict[str, object]:
    line = context.by_line[locus]
    if ordinal < 1 or ordinal > len(line):
        return {"ordinal": 0, "surface": "LINE_EDGE", "reader_exact": 0, "clean": 0, "status": "EDGE", "axes": "NONE", "roles": "OPEN", "semantic_candidate_de": "NONE", "semantic_source": "LINE_EDGE"}
    token, cell, axes = g762.g761.clean_cell(context, locus, ordinal)
    surface = str(token["eva"])
    exact = bool(context.exact[(locus, int(token["token_index"]))])
    status = "CLEAN"
    if not exact:
        status, axes = "NONEXACT", set()
    elif surface in suspect:
        status, axes = "QUARANTINED", set()
    roles: set[str] = set()
    if status == "CLEAN":
        if surface in head_registry:
            roles.add(head_registry[surface]["head_id"] + "_RECORD_FORM")
        if (locus, ordinal) in amount_positions:
            roles.add("AMOUNT_VALUE")
        if surface in manual:
            manual_role = manual[surface]["field_role"]
            if manual_role == "MATERIAL_AMOUNT":
                roles.update(("CONTENT_PREPARATION", "AMOUNT_VALUE"))
            else:
                roles.add(manual_role)
        if surface in state_map:
            roles.update(("QUALITY_STAGE", "CONTENT_PREPARATION"))
        if surface in content_map:
            roles.add("CONTENT_PREPARATION")
        roles.update(roles_from_axes(set(axes)))
        if not roles and surface in meanings:
            roles.add("KNOWN_OTHER")
    if not roles:
        roles.add("OPEN")
    semantic = meanings.get(surface, str(cell["v99r7_semantic_value_de"]))
    semantic_source = sources.get(surface, "GDT734_CELL")
    if surface in manual:
        semantic = manual[surface]["working_candidate_de"]
        semantic_source = manual[surface]["source"] + "_GDT763_FIELD_PRIOR"
    if status == "NONEXACT":
        semantic, semantic_source = "NONEXACT_UNSCORED", "READER_EXACT_GATE"
    elif status == "QUARANTINED":
        semantic, semantic_source = "QUARANTINED_SOURCE_COMPOSITION", "GDT762_COMBINED_QUARANTINE"
    elif any(term in semantic.lower() for term in ("pulver", "samen", "saat", "wurzel", "holz")):
        semantic = "KNOWN_WHOLE_ROLE__RETIRED_LITERAL_MATERIAL_SUPPRESSED"
        semantic_source += "|GDT763_LOCAL_DISPLAY_GUARD"
    return {
        "ordinal": ordinal, "surface": surface, "reader_exact": int(exact), "clean": int(status == "CLEAN"),
        "status": status, "axes": g762.joined(axes), "roles": ordered_roles(roles),
        "semantic_candidate_de": semantic, "semantic_source": semantic_source,
    }


def has_role(slot: dict[str, object], roles: set[str]) -> bool:
    return bool(set(str(slot["roles"]).split("|")) & roles)


def build_h1_occurrences(
    context: object, line_meta: dict[str, dict[str, str]], head_registry: dict[str, dict[str, str]],
    amount_positions: dict[tuple[str, int], dict[str, str]], state_map: dict[str, dict[str, str]],
    content_map: dict[str, dict[str, str]], manual: dict[str, dict[str, str]], suspect: set[str],
    meanings: dict[str, str], sources: dict[str, str],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    substantive = {"QUALITY_STAGE", "SCALAR_VALUE", "AMOUNT_VALUE", "CONTENT_PREPARATION"}
    for locus, line in context.by_line.items():
        h1_ordinals = [
            i + 1 for i, token in enumerate(line)
            if token["eva"] in head_registry and head_registry[str(token["eva"])]["head_id"] == "H1"
            and context.exact[(locus, int(token["token_index"]))]
        ]
        for ordinal in h1_ordinals:
            token = line[ordinal - 1]
            surface = str(token["eva"])
            form = head_registry[surface]
            slots = {delta: slot_record(context, locus, ordinal + delta, head_registry, amount_positions, state_map, content_map, manual, suspect, meanings, sources) for delta in range(-3, 6) if delta != 0}
            right3 = [slots[d] for d in (1, 2, 3)]
            around3 = [slots[d] for d in (-3, -2, -1, 1, 2, 3)]
            previous = [value for value in h1_ordinals if value < ordinal]
            following = [value for value in h1_ordinals if value > ordinal]
            prior_state = state_map.get(str(slots[-1]["surface"]))
            row: dict[str, object] = {
                "h1_occurrence_id": "", "surface": surface, "body": form["body"], "registry_source": form["registry_source"],
                "record_role": form["record_role"], "body_role_de": form["body_role_de"], "page": token["page"],
                "physical_folio": physical_folio(str(token["page"])), "locus": locus, "section": token["section"],
                "language": token["language"], "hand": token["hand"], "ordinal": ordinal, "line_token_count": len(line),
                "line_position": line_position(ordinal, len(line)), "paragraph_start_line": line_meta[locus]["paragraph_start"],
                "paragraph_end_line": line_meta[locus]["paragraph_end"], "remaining_tokens_right": len(line) - ordinal,
                "h1_count_on_line": len(h1_ordinals), "h1_surfaces_on_line": "|".join(str(line[v - 1]["eva"]) for v in h1_ordinals),
                "previous_h1_distance": ordinal - previous[-1] if previous else 0,
                "next_h1_distance": following[0] - ordinal if following else 0,
                "after_sho_or_sheo": int(slots[-1]["surface"] in {"sho", "sheo"}),
                "after_any_moist_state": int(bool(prior_state and prior_state["polarity"] == "MOIST")),
                "after_any_dry_state": int(bool(prior_state and prior_state["polarity"] == "DRY")),
                "right3_any_substantive_field": int(any(has_role(slot, substantive) for slot in right3)),
                "right3_any_quality": int(any(has_role(slot, {"QUALITY_STAGE"}) for slot in right3)),
                "right3_any_scalar": int(any(has_role(slot, {"SCALAR_VALUE", "AMOUNT_VALUE"}) for slot in right3)),
                "right3_any_content": int(any(has_role(slot, {"CONTENT_PREPARATION"}) for slot in right3)),
                "right3_any_h_head": int(any(any(role.endswith("_RECORD_FORM") for role in str(slot["roles"]).split("|")) for slot in right3)),
                "right3_any_process_pass": int(any(has_role(slot, {"PROCESS_PASS"}) for slot in right3)),
                "right3_any_close": int(any(has_role(slot, {"CLOSE"}) for slot in right3)),
                "plusminus3_any_process_pass_close": int(any(has_role(slot, {"PROCESS_PASS", "CLOSE"}) for slot in around3)),
                "gapped_x_daiin": int(slots[1]["clean"] == 1 and slots[2]["clean"] == 1 and slots[2]["surface"] == "daiin"),
                "written_line_eva": " ".join(str(item["eva"]) for item in line), "component_export_credit": 0,
            }
            for delta, label in ((-3, "l3"), (-2, "l2"), (-1, "l1"), (1, "r1"), (2, "r2"), (3, "r3"), (4, "r4"), (5, "r5")):
                for field in ("surface", "reader_exact", "clean", "status", "axes", "roles", "semantic_candidate_de", "semantic_source"):
                    row[f"{label}_{field}"] = slots[delta][field]
            output.append(row)
    output.sort(key=lambda row: (str(row["page"]), str(row["locus"]), int(row["ordinal"])))
    for number, row in enumerate(output, start=1):
        row["h1_occurrence_id"] = f"G763-H1-{number:03d}"
    return output


def build_paragraph_medial_profile(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    matched = [row for row in occurrences if row["paragraph_start_line"] == "1" and row["line_position"] == "MIDDLE"]
    cohorts = (
        ("PCHEEY_TARGET", [row for row in matched if row["surface"] == "pcheey"]),
        ("OTHER_H1_POSITION_MATCHED", [row for row in matched if row["surface"] != "pcheey"]),
        ("ALL_H1_POSITION_MATCHED", matched),
        ("OTHER_H1_ALL", [row for row in occurrences if row["surface"] != "pcheey"]),
    )
    features = (
        "right3_any_substantive_field", "right3_any_quality", "right3_any_scalar", "right3_any_content",
        "right3_any_h_head", "right3_any_process_pass", "right3_any_close",
        "plusminus3_any_process_pass_close", "gapped_x_daiin",
    )
    output: list[dict[str, object]] = []
    for cohort_id, rows in cohorts:
        record: dict[str, object] = {
            "cohort_id": cohort_id, "occurrences": len(rows), "surfaces": len({str(item["surface"]) for item in rows}),
            "pages": len({str(item["page"]) for item in rows}), "loci": len({str(item["locus"]) for item in rows}),
            "multi_h1_line_occurrences": sum(int(item["h1_count_on_line"]) >= 2 for item in rows),
            "line_final_occurrences": sum(item["line_position"] == "LAST" for item in rows),
            "paragraph_end_line_occurrences": sum(item["paragraph_end_line"] == "1" for item in rows),
            "remaining_tokens_right_counts": compact(str(item["remaining_tokens_right"]) for item in rows),
        }
        for feature in features:
            record[feature + "_occurrences"] = sum(int(item[feature]) for item in rows)
        record["cohort_definition"] = (
            "reader-exact pcheey; paragraph_start_line=1; line_position=MIDDLE"
            if cohort_id == "PCHEEY_TARGET" else
            "reader-exact H1; paragraph_start_line=1; line_position=MIDDLE"
            if "POSITION_MATCHED" in cohort_id else "reader-exact H1 outside target"
        )
        record["overlap_caveat"] = "DESCRIPTIVE_OVERLAPPING_COHORTS_NOT_INDEPENDENT"
        output.append(record)
    return output


def build_head_state_profile(
    context: object, head_registry: dict[str, dict[str, str]], state_map: dict[str, dict[str, str]],
    exposure: list[dict[str, str]],
) -> list[dict[str, object]]:
    contacts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    occurrences: Counter[str] = Counter()
    for locus, line in context.by_line.items():
        for index, token in enumerate(line):
            surface = str(token["eva"])
            if surface not in head_registry or not context.exact[(locus, int(token["token_index"]))]:
                continue
            head = head_registry[surface]["head_id"]
            occurrences[head] += 1
            if index:
                left = line[index - 1]
                if context.exact[(locus, int(left["token_index"]))] and str(left["eva"]) in state_map:
                    contacts[head][state_map[str(left["eva"])]["polarity"]] += 1
    dry_opp = sum(int(row["reader_exact_right_neighbor_opportunities"]) for row in exposure if row["polarity"] == "DRY")
    moist_opp = sum(int(row["reader_exact_right_neighbor_opportunities"]) for row in exposure if row["polarity"] == "MOIST")
    output: list[dict[str, object]] = []
    for head in HEAD_IDS:
        dry, moist = contacts[head]["DRY"], contacts[head]["MOIST"]
        dry_rate, moist_rate = dry / dry_opp, moist / moist_opp
        output.append({
            "opaque_head_id": head, "reader_exact_occurrences": occurrences[head],
            "immediately_after_dry_state": dry, "immediately_after_moist_state": moist,
            "dry_state_right_opportunities": dry_opp, "moist_state_right_opportunities": moist_opp,
            "dry_contact_rate": fixed(dry_rate), "moist_contact_rate": fixed(moist_rate),
            "normalized_moist_to_dry_rate_ratio": fixed(moist_rate / dry_rate) if dry_rate else "INF",
            "interpretation": "H1_RELATIVE_POST_MOIST_ENRICHMENT__ROLE_NOT_IDENTITY" if head == "H1" else "CONTROL_HEAD_CLASS_DRY_LEANING",
            "component_export_credit": 0,
        })
    return output


def build_pcheey_frames(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for number, source in enumerate((row for row in occurrences if row["surface"] == "pcheey"), start=1):
        if source["r2_surface"] == "daiin":
            neutral = f"Feuchtzubereitung — Trockenzubereitung/Form II: {source['r1_semantic_candidate_de']}; Wert III"
        else:
            neutral = f"Feuchtzubereitung — Trockenzubereitung/Form II; Folgefeld {source['r1_semantic_candidate_de']}"
        output.append({
            "frame_id": f"G763-P{number:02d}", "h1_occurrence_id": source["h1_occurrence_id"],
            "page": source["page"], "physical_folio": source["physical_folio"], "locus": source["locus"],
            "predecessor_surface": source["l1_surface"], "predecessor_semantic_de": source["l1_semantic_candidate_de"],
            "pcheey_surface": "pcheey", "pcheey_portable_default_de": "gebundenes Trockenzubereitungs-/Form-II-Feld mit Wertfeld-Affinität; Stoffidentität offen",
            "r1_surface": source["r1_surface"], "r1_roles": source["r1_roles"], "r1_semantic_candidate_de": source["r1_semantic_candidate_de"],
            "r2_surface": source["r2_surface"], "r2_roles": source["r2_roles"], "r2_semantic_candidate_de": source["r2_semantic_candidate_de"],
            "r3_surface": source["r3_surface"], "r3_roles": source["r3_roles"], "r3_semantic_candidate_de": source["r3_semantic_candidate_de"],
            "gapped_pcheey_x_daiin": source["gapped_x_daiin"], "neutral_record_renderer_de": neutral,
            "aggressive_source_renderer_de": "Feuchtzubereitung aus Trockengut, Form II",
            "result_renderer_de": "NOT_LICENSED__NO_PROCESS_CLOSE_SIGNAL", "written_line_eva": source["written_line_eva"],
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    return output


def build_gapped_daiin_audit(
    context: object, line_meta: dict[str, dict[str, str]], occurrences: list[dict[str, object]],
    head_registry: dict[str, dict[str, str]], suspect: set[str],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    exact_positions: defaultdict[str, list[tuple[str, int]]] = defaultdict(list)
    for locus, line in context.by_line.items():
        for index, token in enumerate(line):
            if context.exact[(locus, int(token["token_index"]))]:
                exact_positions[str(token["eva"])].append((locus, index))
    strict_controls: list[dict[str, object]] = []
    for surface, positions in exact_positions.items():
        if surface in head_registry or surface in suspect or len(positions) != 3:
            continue
        pages = {str(context.by_line[locus][index]["page"]) for locus, index in positions}
        if len(pages) != 3 or not all(
            line_position(index + 1, len(context.by_line[locus])) == "MIDDLE" and line_meta[locus]["paragraph_start"] == "1"
            for locus, index in positions
        ):
            continue
        hit_loci: list[str] = []
        for locus, index in positions:
            line = context.by_line[locus]
            if index + 2 < len(line):
                x, value = line[index + 1], line[index + 2]
                if context.exact[(locus, int(x["token_index"]))] and context.exact[(locus, int(value["token_index"]))] and value["eva"] == "daiin":
                    hit_loci.append(locus)
        strict_controls.append({
            "surface": surface, "reader_exact_occurrences": 3, "reader_exact_pages": 3,
            "all_middle": 1, "all_paragraph_start_line": 1, "surface_occurrences_with_x_daiin": len(hit_loci),
            "has_any_x_daiin": int(bool(hit_loci)), "hit_loci": "|".join(hit_loci) or "NONE",
            "selection_relation": "NON_H1_N3_PAGES3_ALL_MIDDLE_ALL_PARAGRAPH_START_NOT_SUSPECT",
            "component_export_credit": 0,
        })
    strict_controls.sort(key=lambda row: str(row["surface"]))

    hits: list[dict[str, object]] = []
    for row in occurrences:
        if int(row["gapped_x_daiin"]):
            hits.append({
                "cohort": "PCHEEY" if row["surface"] == "pcheey" else "OTHER_H1", "surface": row["surface"],
                "page": row["page"], "locus": row["locus"], "target_ordinal": row["ordinal"],
                "intervening_surface": row["r1_surface"], "intervening_roles": row["r1_roles"],
                "intervening_semantic_candidate_de": row["r1_semantic_candidate_de"], "value_surface": row["r2_surface"],
                "value_role": row["r2_roles"], "written_pattern_eva": f"{row['surface']} {row['r1_surface']} daiin",
                "written_line_eva": row["written_line_eva"], "component_export_credit": 0,
            })
    for control in strict_controls:
        if not int(control["has_any_x_daiin"]):
            continue
        surface = str(control["surface"])
        for locus, index in exact_positions[surface]:
            line = context.by_line[locus]
            if index + 2 < len(line):
                x, value = line[index + 1], line[index + 2]
                if context.exact[(locus, int(x["token_index"]))] and context.exact[(locus, int(value["token_index"]))] and value["eva"] == "daiin":
                    hits.append({
                        "cohort": "STRICT_NON_H1_CONTROL", "surface": surface, "page": line[index]["page"], "locus": locus,
                        "target_ordinal": index + 1, "intervening_surface": x["eva"], "intervening_roles": "UNCLASSIFIED_CONTROL",
                        "intervening_semantic_candidate_de": "CONTROL_ONLY", "value_surface": "daiin", "value_role": "SCALAR_VALUE",
                        "written_pattern_eva": f"{surface} {x['eva']} daiin", "written_line_eva": " ".join(str(t["eva"]) for t in line),
                        "component_export_credit": 0,
                    })
    hits.sort(key=lambda row: (str(row["cohort"]), str(row["page"]), str(row["locus"])))
    target = [row for row in occurrences if row["surface"] == "pcheey"]
    other = [row for row in occurrences if row["surface"] != "pcheey"]
    cohorts = [
        {"cohort": "PCHEEY", "candidate_surfaces": 1, "occurrences": len(target), "x_daiin_hits": sum(int(row["gapped_x_daiin"]) for row in target), "surfaces_with_any_hit": 1, "rate_or_surface_fraction": fixed(sum(int(row["gapped_x_daiin"]) for row in target) / len(target)), "comparison_unit": "OCCURRENCE", "selection": "TARGET"},
        {"cohort": "OTHER_H1", "candidate_surfaces": len({str(row["surface"]) for row in other}), "occurrences": len(other), "x_daiin_hits": sum(int(row["gapped_x_daiin"]) for row in other), "surfaces_with_any_hit": len({str(row["surface"]) for row in other if int(row["gapped_x_daiin"])}), "rate_or_surface_fraction": fixed(sum(int(row["gapped_x_daiin"]) for row in other) / len(other)), "comparison_unit": "OCCURRENCE", "selection": "ALL_OTHER_READER_EXACT_H1"},
        {"cohort": "STRICT_NON_H1_CONTROL", "candidate_surfaces": len(strict_controls), "occurrences": sum(int(row["reader_exact_occurrences"]) for row in strict_controls), "x_daiin_hits": sum(int(row["surface_occurrences_with_x_daiin"]) for row in strict_controls), "surfaces_with_any_hit": sum(int(row["has_any_x_daiin"]) for row in strict_controls), "rate_or_surface_fraction": fixed(sum(int(row["has_any_x_daiin"]) for row in strict_controls) / len(strict_controls)), "comparison_unit": "SURFACE", "selection": "N3_PAGES3_ALL_MIDDLE_ALL_PARAGRAPH_START_NOT_H1_OR_SUSPECT"},
    ]
    for row in cohorts:
        row["confirmed_syntax"], row["component_export_credit"] = 0, 0
    return cohorts, hits, strict_controls


def build_pcheey_scorecard(specs: list[dict[str, str]], occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    evidence = {
        "FIELD_BEARING_DRY_PREPARATION_HEAD": ("3/3 Inhaltsfeld in R3; 2/3 pcheey X daiin; trockene Form-II-Karte", "SELECT_COMPOSITE_WITH_RECORD_ROLE", 1),
        "PARALLEL_RECORD_FIELD": ("3/3 H1, medial auf Absatzanfangszeile und mit mehreren H1-Formen; rechte Rollen in Kontrollen üblich", "SELECT_PORTABLE_STRUCTURAL_CORE", 1),
        "DRY_SOURCE_OR_COMPLEMENT": ("3/3 unmittelbar nach sho|sheo; kein unabhängiger Relationsmarker", "RETAIN_C1_EXACT_SPAN_RIVAL", 2),
        "POST_MOIST_RESULT": ("0/3 PROCESS|PASS|CLOSE innerhalb ±3; 0/3 zeilenfinal; 0/3 Absatzende", "DOWNGRADE_WEAKEST_RIVAL", 4),
    }
    output: list[dict[str, object]] = []
    for row in (item for item in specs if item["target"] == "pcheey"):
        observed, decision, rank = evidence[row["hypothesis_role"]]
        output.append({
            "hypothesis_id": row["hypothesis_id"], "hypothesis_role": row["hypothesis_role"],
            "working_realization_de": row["working_realization_de"], "rank": rank, "observed_evidence": observed,
            "predicted_positive_signature": row["positive_signature"], "predicted_negative_signature": row["negative_signature"],
            "decision": decision, "renderer_policy": row["claim_policy"], "target_occurrences": 3,
            "specific_substance_selected": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    return sorted(output, key=lambda row: (int(row["rank"]), str(row["hypothesis_id"])))


def build_ol_slots(ol_rows: list[dict[str, str]], quantity_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    quantity = {row["expression_id"]: row for row in quantity_rows}
    output: list[dict[str, object]] = []
    for row in ol_rows:
        qrow = quantity[row["expression_id"]]
        sides = row["ol_sides_relative_to_amount"].split("|")
        competitor_surface = "NONE"
        if sides == ["L", "R"]:
            selected, basis = "BILATERAL_AMBIGUOUS", "ol steht auf beiden Seiten derselben Mengenexpression"
            competitor_exact, outside_surface, outside_exact, outside_class = 0, "AMBIGUOUS", 0, "AMBIGUOUS"
        else:
            side = sides[0]
            if side == "R":
                competitor_exact, competitor_surface, competitor_class = int(qrow["left_reader_exact"]), qrow["left_surface"], qrow["left_axis_class"]
            else:
                competitor_exact, competitor_surface, competitor_class = int(qrow["right_reader_exact"]), qrow["right_surface"], qrow["right_axis_class"]
            if side == "L":
                outside_surface, outside_exact, outside_class = qrow["right_surface"], int(qrow["right_reader_exact"]), qrow["right_axis_class"]
            else:
                outside_surface, outside_exact, outside_class = "SEE_OL_OCCURRENCE_R1", 0, "NOT_REQUIRED_BY_SELECTED_DISPATCH"
            if row["decision"] == "CONTACT_SUPPORT_ONLY_NONPREFERRED_SIDE" and side == "R" and competitor_exact == 1:
                selected = "CONTEXT_SECOND_FIELD"
                basis = f"positionsbevorzugter linker Gegenkandidat {competitor_surface} ist reader-exakt ({competitor_class})"
            elif row["decision"] == "EXACT_AMOUNT_CONTENT_PHRASE_LICENSE" and outside_exact == 1 and outside_class == "PROCESS_CLOSE":
                selected = "OBJECT_PATIENT"
                basis = f"zulässiger Mengenkopf mit folgendem exaktem Prozessfeld {outside_surface}"
            else:
                selected = "HEAD"
                basis = "ol besetzt allein die positionsbevorzugte Inhaltsseite" if row["decision"] == "EXACT_AMOUNT_CONTENT_PHRASE_LICENSE" else f"nichtbevorzugte Seite, aber Gegenkandidat {competitor_surface} ist nicht reader-exakt"
        output.append({
            "ol_slot_id": row["ol_amount_contact_id"].replace("G762-", "G763-"), "source_contact_id": row["ol_amount_contact_id"],
            "expression_id": row["expression_id"], "page": row["page"], "physical_folio": row["physical_folio"], "locus": row["locus"],
            "amount_expression_eva": row["amount_expression_eva"], "amount_candidate_de": row["amount_candidate_de"], "amount_mode": row["amount_mode"],
            "expression_line_position": row["expression_line_position"], "ol_sides_relative_to_amount": row["ol_sides_relative_to_amount"],
            "position_expected_side": row["position_expected_side"], "gdt762_decision": row["decision"], "selected_slot_function": selected,
            "dispatch_basis": basis, "preferred_competitor_surface": competitor_surface,
            "preferred_competitor_reader_exact": competitor_exact, "outside_span_surface": outside_surface,
            "outside_span_reader_exact": outside_exact, "outside_span_axis_class": outside_class,
            "working_phrase_de": "drei Drachmen Ansatz/Zubereitung; abseihen" if selected == "OBJECT_PATIENT" else row["working_phrase_de"],
            "source_relation_marker": "NONE", "specific_oil_identity": 0, "written_line_eva": row["written_line_eva"],
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    return output


def build_ol_comparators(ol_rows: list[dict[str, str]], content_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    keys = {
        (row["amount_expression_eva"], row["expression_line_position"], side)
        for row in ol_rows for side in row["ol_sides_relative_to_amount"].split("|")
    }
    output: list[dict[str, object]] = []
    for row in content_rows:
        key = (row["amount_expression_eva"], row["expression_line_position"], row["content_side"])
        if key not in keys:
            continue
        output.append({
            "attachment_id": row["attachment_id"], "page": row["page"], "locus": row["locus"], "match_key": "|".join(key),
            "amount_expression_eva": row["amount_expression_eva"], "expression_line_position": row["expression_line_position"],
            "content_side": row["content_side"], "content_surface": row["content_surface"], "content_axes": row["content_axes"],
            "content_role_label_de": row["content_role_label_de"], "content_candidate_de": row["content_candidate_de"],
            "content_semantic_confidence": row["content_semantic_confidence"], "position_condition_agreement": row["position_condition_agreement"],
            "comparison_interpretation": "NONPREFERRED_MIDDLE_RIGHT_SLOT_ATTESTED_AS_PREPARATION" if row["expression_line_position"] == "MIDDLE" else "PREFERRED_FIRST_RIGHT_SLOT_MIXES_MATERIAL_AND_PREPARATION",
            "written_line_eva": row["written_line_eva"], "component_export_credit": 0,
        })
    return output


def build_ol_placement_comparison(ol_slots: list[dict[str, object]], content_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    groups: list[tuple[str, int, int]] = []
    for label in ("Stoff", "Zubereitung", "Stoff/Zubereitung"):
        rows = [row for row in content_rows if row["content_role_label_de"] == label]
        groups.append((label, sum(int(row["position_condition_agreement"]) for row in rows), len(rows)))
    unambiguous = [row for row in ol_slots if row["selected_slot_function"] != "BILATERAL_AMBIGUOUS"]
    ol_expected = sum(row["ol_sides_relative_to_amount"] == row["position_expected_side"] for row in unambiguous)
    output: list[dict[str, object]] = []
    for label, expected, total in groups:
        other, ol_other = total - expected, len(unambiguous) - ol_expected
        output.append({
            "comparison_class": label, "expected_side_contacts": expected, "nonexpected_side_contacts": other,
            "total_contacts": total, "expected_side_fraction": fixed(expected / total),
            "ol_expected_side_contacts": ol_expected, "ol_nonexpected_side_contacts": ol_other,
            "ol_unambiguous_contacts": len(unambiguous), "ol_expected_side_fraction": fixed(ol_expected / len(unambiguous)),
            "ol_vs_class_odds_ratio": odds_ratio(ol_expected, ol_other, expected, other),
            "ol_vs_class_fisher_two_sided": fixed(fisher_two_sided(ol_expected, ol_other, expected, other)),
            "interpretation": "OL_PLACEMENT_CLOSE_TO_PREPARATION_CLASS" if label == "Zubereitung" else "OL_LESS_DIRECTIONAL_THAN_MATERIAL_CLASS" if label == "Stoff" else "SMALL_MIXED_CONTROL",
            "dependence_caveat": "DESCRIPTIVE_CONTACT_DIAGNOSTIC_NOT_INDEPENDENT_LEXEME_TEST",
        })
    return output


def build_ol_formula_recurrence(ol_rows: list[dict[str, str]], context: object) -> list[dict[str, object]]:
    patterns = (
        ("ol s aiin", lambda row: "L" in row["ol_sides_relative_to_amount"].split("|") and row["amount_expression_eva"] == "s aiin", "Ansatz/Zubereitung: drei Drachmen"),
        ("sain ol", lambda row: row["ol_sides_relative_to_amount"] == "R" and row["amount_expression_eva"] == "sain", "zwei Drachmen Ansatz/Zubereitung"),
        ("saiin ol", lambda row: row["ol_sides_relative_to_amount"] == "R" and row["amount_expression_eva"] == "saiin", "drei Drachmen Ansatz/Zubereitung"),
        ("or aiin ol", lambda row: row["ol_sides_relative_to_amount"] == "R" and row["amount_expression_eva"] == "or aiin", "drei Portionen Ansatz/Zubereitung"),
    )
    output: list[dict[str, object]] = []
    for pattern, predicate, renderer in patterns:
        rows = [row for row in ol_rows if predicate(row)]
        output.append({
            "pattern_eva": pattern, "reader_exact_amount_contact_positions": len(rows), "pages": len({row["page"] for row in rows}),
            "loci": "|".join(sorted(row["locus"] for row in rows)), "working_role": "CONTENT_PLUS_AMOUNT_ORDER_VARIANT",
            "working_renderer_de": renderer, "counterevidence": "Mengenwert, Einheit und Syntaxrichtung bleiben austauschbar",
            "component_export_credit": 0,
        })
    positions: list[tuple[str, int]] = []
    for locus, line in context.by_line.items():
        for index, token in enumerate(line):
            if token["eva"] == "ols" and context.exact[(locus, int(token["token_index"]))]:
                positions.append((locus, index))
    value_hits = [
        (locus, index) for locus, index in positions
        if index + 1 < len(context.by_line[locus]) and context.by_line[locus][index + 1]["eva"] in {"aiin", "aiiin"}
        and context.exact[(locus, int(context.by_line[locus][index + 1]["token_index"]))]
    ]
    output.append({
        "pattern_eva": "ols + aiin|aiiin", "reader_exact_amount_contact_positions": len(value_hits),
        "pages": len({str(context.by_line[locus][index]["page"]) for locus, index in value_hits}),
        "loci": "|".join(sorted(locus for locus, _ in value_hits)), "working_role": "RELATED_WHOLE_PREPARATION_FAMILY_CONTROL",
        "working_renderer_de": "ols: Zubereitungsfamilie mit rechtem Wertfeld",
        "counterevidence": f"ols hat {len(positions)} exakte Vorkommen; whole-Vergleich gibt ol null Komponentenrecht",
        "component_export_credit": 0,
    })
    return output


def build_history() -> list[dict[str, object]]:
    entries = {row["observation_id"]: row for row in read_tsv(ROOT / G735_HISTORY_REL)}
    expressions = {row["candidate_id"]: row for row in read_tsv(ROOT / G755_HISTORY_REL)}
    specs = (
        ("HEO005", "ENTRY_HEAD_QUALITY_DEGREE", "PCHEEY_RECORD_HEAD", "ROLE_ANALOGY"),
        ("HEO006", "ENTRY_HEAD_QUALITY_DEGREE", "PCHEEY_RECORD_HEAD", "ROLE_ANALOGY"),
        ("HEO011", "PRODUCT_HEAD_OR_SOURCE", "PCHEEY_SOURCE_RIVAL", "RELATION_EXPLICIT_IN_HISTORY_ONLY"),
        ("E020", "PROCESS_TO_RESULT", "PCHEEY_RESULT_RIVAL", "TARGET_LACKS_PROCESS_CLOSE"),
        ("E022", "PROCESS_TO_RESULT", "PCHEEY_RESULT_RIVAL", "TARGET_LACKS_PROCESS_CLOSE"),
        ("E028", "NAMED_OIL_CONTENT", "OL_OIL_RIVAL", "TARGET_LACKS_LIQUID_OIL_SLOT"),
        ("E036", "NAMED_DRY_PREPARATION", "PCHEEY_POWDER_RIVAL", "NO_POWDER_SPECIFIC_TARGET_SLOT"),
        ("E043", "DRY_PROCESS", "PCHEEY_RESULT_RIVAL", "TARGET_LACKS_PROCESS_CLOSE"),
    )
    output: list[dict[str, object]] = []
    for source_id, analogy, target, decision in specs:
        if source_id.startswith("HEO"):
            row = entries[source_id]
            expression, locator, source_record, channel = row["headword_or_rubric"], row["locator"], row["source_id"], row["record_mode"]
        else:
            row = expressions[source_id]
            expression, locator, source_record, channel = row["attested_form"], row["locator"], row["source_ids"], row["historical_register_family"]
        output.append({
            "historical_item_id": source_id, "historical_expression": expression, "historical_locator": locator,
            "historical_source_ids": source_record, "historical_channel": channel, "analogy_class": analogy,
            "target_hypothesis": target, "decision": decision, "target_assignment_credit": 0, "eva_spelling_credit": 0,
            "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    return output


def build_revisions() -> list[dict[str, object]]:
    return [
        {
            "surface": "pcheey", "old_working_default_de": "Trockenzubereitungs-/Form-II-Eintrag; Identität offen",
            "new_working_default_de": "gebundenes Trockenzubereitungs-/Form-II-Feld mit Wertfeld-Affinität; Stoffidentität offen",
            "role": "FIELD_BEARING_RECORD_CONTENT_HEAD", "confidence": "C2_EXACT_CONSTRUCTION_STRONG_SMALL_N",
            "evidence": "3/3 nach sho|sheo; 3/3 Inhaltsfeld in R3; 2/3 X daiin gegen 3/196 andere H1; 3/3 mehrere H1 auf Zeile",
            "counterevidence": "nur drei Vorkommen; Recordkopf, Quelle und Inhaltskomplement nicht syntaktisch getrennt",
            "exact_span_renderer_de": "Feuchtzubereitung — Trockenzubereitung/Form II: folgendes Feld",
            "aggressive_c1_renderer_de": "Feuchtzubereitung aus Trockengut, Form II",
            "global_identity_selected": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        },
        {
            "surface": "ol", "old_working_default_de": "mengenfähiger Zubereitungs-/Stoffträger; genaue Basis offen",
            "new_working_default_de": "mengenfähiger Zubereitungs-/Inhaltskopf mit kontextuellen Nebenverwendungen",
            "role": "QUANTIFIABLE_PREPARATION_CONTENT_HEAD_WITH_CONTEXT_USES", "confidence": "C2_RELATIONAL_ROLE_C0_IDENTITY",
            "evidence": "16 Mengenpositionen/17 Kanten/13 Seiten; HEAD9 OBJECT1 CONTEXT5 BILATERAL1",
            "counterevidence": "nur 8/15 eindeutige Kontakte in bevorzugter Orientierung; hohe Gesamtfrequenz; Öl ohne Flüssigkeitssignal",
            "exact_span_renderer_de": "Menge + Ansatz/Zubereitung oder Ansatz/Zubereitung + Menge, positionsgebunden",
            "aggressive_c1_renderer_de": "Ansatz/Zubereitung; konkrete Substanz offen",
            "global_identity_selected": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        },
    ]


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    training = read_tsv(ROOT / G736_GRID_REL)
    held = read_tsv(ROOT / G737_FORM_REL)
    quantity_rows = read_tsv(ROOT / G760_QUANTITY_REL)
    content_rows = read_tsv(ROOT / G760_CONTENT_REL)
    content_deck = read_tsv(ROOT / G760_DECK_REL)
    ol_rows = read_tsv(ROOT / G762_OL_REL)
    manual_rows = read_tsv(SRC / "EXACT_WHOLE_FIELD_PRIORS.tsv")
    hypothesis_specs = read_tsv(SRC / "ROLE_HYPOTHESIS_SPECS.tsv")
    state_rows = read_tsv(g762.SRC / "STATE_PAIR_PRIORS.tsv")
    candidate_rows = read_tsv(g762.SRC / "CANDIDATE_PRIORS.tsv")
    exposure = read_tsv(g762.DEFAULT_ARTIFACTS / "STATE_PAIR_EXPOSURE.tsv")
    if len(training) != 96 or len(held) != 273 or len(quantity_rows) != 281:
        raise AssertionError("fixed predecessor universes changed")
    if len(content_rows) != 45 or len(content_deck) != 35 or len(ol_rows) != 16:
        raise AssertionError("fixed content/ol universes changed")
    head_registry = build_head_registry(training, held)
    amount_positions = amount_position_map(quantity_rows)
    state_map, _, _ = g762.state_maps(state_rows)
    meanings, sources, suspect, _, quarantine = g762.semantic_inputs(state_rows, candidate_rows)
    content_map = {row["content_surface"]: row for row in content_deck}
    manual = {row["surface"]: row for row in manual_rows}
    context, line_meta, guard = g762.g761.g760.g759.g758.g756.g755.g753.g752.g751.load_context()

    h1_occurrences = build_h1_occurrences(
        context, line_meta, head_registry, amount_positions, state_map, content_map,
        manual, suspect, meanings, sources,
    )
    h1_profile = build_paragraph_medial_profile(h1_occurrences)
    head_state = build_head_state_profile(context, head_registry, state_map, exposure)
    pcheey_frames = build_pcheey_frames(h1_occurrences)
    gapped_cohorts, gapped_hits, strict_controls = build_gapped_daiin_audit(
        context, line_meta, h1_occurrences, head_registry, suspect,
    )
    pcheey_scorecard = build_pcheey_scorecard(hypothesis_specs, h1_occurrences)
    ol_slots = build_ol_slots(ol_rows, quantity_rows)
    ol_comparators = build_ol_comparators(ol_rows, content_rows)
    ol_placement = build_ol_placement_comparison(ol_slots, content_rows)
    ol_formulas = build_ol_formula_recurrence(ol_rows, context)
    history = build_history()
    revisions = build_revisions()

    expected_registry = Counter({"H1": 89, "H2": 95, "H3": 75, "H4": 110})
    if len(head_registry) != 369 or Counter(row["head_id"] for row in head_registry.values()) != expected_registry:
        raise AssertionError("head registry changed")
    if len(h1_occurrences) != 199 or len({row["page"] for row in h1_occurrences}) != 82 or len({row["locus"] for row in h1_occurrences}) != 183:
        raise AssertionError("H1 occurrence universe changed")
    if Counter(row["line_position"] for row in h1_occurrences) != Counter({"FIRST": 125, "MIDDLE": 71, "LAST": 3}):
        raise AssertionError("H1 position profile changed")
    if sum(row["paragraph_start_line"] == "1" for row in h1_occurrences) != 157:
        raise AssertionError("H1 paragraph-start profile changed")
    target = [row for row in h1_occurrences if row["surface"] == "pcheey"]
    if len(target) != 3 or not all(int(row["after_sho_or_sheo"]) for row in target):
        raise AssertionError("pcheey target frame changed")
    matched = [row for row in h1_occurrences if row["paragraph_start_line"] == "1" and row["line_position"] == "MIDDLE"]
    if len(matched) != 52 or sum(row["surface"] == "pcheey" for row in matched) != 3:
        raise AssertionError("position-matched H1 cohort changed")
    if sum(int(row["gapped_x_daiin"]) for row in target) != 2:
        raise AssertionError("pcheey X daiin frame changed")
    if sum(int(row["gapped_x_daiin"]) for row in h1_occurrences if row["surface"] != "pcheey") != 3:
        raise AssertionError("other H1 X daiin control changed")
    if len(strict_controls) != 11 or sum(int(row["has_any_x_daiin"]) for row in strict_controls) != 1 or len(gapped_hits) != 6:
        raise AssertionError("strict non-H1 control changed")
    if any(int(row["plusminus3_any_process_pass_close"]) for row in target):
        raise AssertionError("pcheey gained a result signature")
    expected_head_state = {"H1": (6, 12), "H2": (19, 7), "H3": (18, 3), "H4": (61, 20)}
    if {row["opaque_head_id"]: (row["immediately_after_dry_state"], row["immediately_after_moist_state"]) for row in head_state} != expected_head_state:
        raise AssertionError("head/state predecessor profile changed")
    if Counter(row["selected_slot_function"] for row in ol_slots) != Counter({"HEAD": 9, "OBJECT_PATIENT": 1, "CONTEXT_SECOND_FIELD": 5, "BILATERAL_AMBIGUOUS": 1}):
        raise AssertionError("ol slot dispatch changed")
    expected_dispatch = {
        "HEAD": {"G762-A01", "G762-A02", "G762-A03", "G762-A04", "G762-A06", "G762-A10", "G762-A11", "G762-A13", "G762-A15"},
        "OBJECT_PATIENT": {"G762-A16"},
        "CONTEXT_SECOND_FIELD": {"G762-A05", "G762-A07", "G762-A08", "G762-A09", "G762-A14"},
        "BILATERAL_AMBIGUOUS": {"G762-A12"},
    }
    for role, identifiers in expected_dispatch.items():
        if {row["source_contact_id"] for row in ol_slots if row["selected_slot_function"] == role} != identifiers:
            raise AssertionError(f"ol {role} identity set changed")
    expected_comparators = Counter({("MIDDLE", "R", "Zubereitung"): 9, ("FIRST", "R", "Stoff"): 5, ("FIRST", "R", "Zubereitung"): 4})
    if len(ol_comparators) != 18 or Counter((row["expression_line_position"], row["content_side"], row["content_role_label_de"]) for row in ol_comparators) != expected_comparators:
        raise AssertionError("ol matched content controls changed")
    if [(row["pattern_eva"], row["reader_exact_amount_contact_positions"]) for row in ol_formulas] != [
        ("ol s aiin", 4), ("sain ol", 4), ("saiin ol", 2), ("or aiin ol", 2), ("ols + aiin|aiiin", 3),
    ]:
        raise AssertionError("ol formula recurrence changed")
    if any(str(row["page"]).startswith("f84") for row in h1_occurrences + ol_slots):
        raise AssertionError("sealed page entered GDT763")

    tables = (
        h1_occurrences, h1_profile, head_state, pcheey_frames, gapped_cohorts,
        gapped_hits, strict_controls, pcheey_scorecard, ol_slots, ol_comparators,
        ol_placement, ol_formulas, history, revisions,
    )
    for name, rows in zip(OUTPUT_NAMES[:-1], tables):
        if not rows:
            raise AssertionError(f"empty output: {name}")
        write_tsv(output_dir / name, rows, list(rows[0]))

    result = {
        "schema": "GDT763_RESULT_V1", "status": STATUS,
        "scope": {
            "registered_head_forms": len(head_registry), "registered_h1_forms": 89,
            "observed_h1_surfaces": len({str(row["surface"]) for row in h1_occurrences}),
            "h1_reader_exact_occurrences": len(h1_occurrences), "h1_pages": len({str(row["page"]) for row in h1_occurrences}),
            "h1_loci": len({str(row["locus"]) for row in h1_occurrences}), "paragraph_start_medial_h1_occurrences": len(matched),
            "pcheey_occurrences": len(target), "strict_non_h1_control_surfaces": len(strict_controls),
            "ol_amount_positions": len(ol_slots), "ol_directed_edges": sum(len(str(row["ol_sides_relative_to_amount"]).split("|")) for row in ol_slots),
            "ol_matched_content_comparators": len(ol_comparators), "historical_role_comparators": len(history),
        },
        "pcheey_result": {
            "immediately_after_sho_or_sheo": 3, "right3_content_field_occurrences": sum(int(row["right3_any_content"]) for row in target),
            "pcheey_x_daiin_occurrences": sum(int(row["gapped_x_daiin"]) for row in target),
            "other_h1_x_daiin_occurrences": sum(int(row["gapped_x_daiin"]) for row in h1_occurrences if row["surface"] != "pcheey"),
            "strict_control_surfaces_with_x_daiin": sum(int(row["has_any_x_daiin"]) for row in strict_controls),
            "strict_control_surfaces": len(strict_controls), "plusminus3_process_pass_close": sum(int(row["plusminus3_any_process_pass_close"]) for row in target),
            "line_final": sum(row["line_position"] == "LAST" for row in target), "paragraph_end": sum(row["paragraph_end_line"] == "1" for row in target),
            "selected_role": "FIELD_BEARING_FORM_II_RECORD_CONTENT_HEAD", "portable_working_default_de": revisions[0]["new_working_default_de"],
            "source_relation": "C1_EXACT_SPAN_RIVAL_ONLY", "result_relation": "DOWNGRADED_WEAKEST_RIVAL",
        },
        "head_state_result": {row["opaque_head_id"]: {"dry": row["immediately_after_dry_state"], "moist": row["immediately_after_moist_state"], "normalized_moist_to_dry": row["normalized_moist_to_dry_rate_ratio"]} for row in head_state},
        "ol_result": {
            "slot_dispatch": dict(Counter(str(row["selected_slot_function"]) for row in ol_slots)),
            "head_or_object_positions": sum(row["selected_slot_function"] in {"HEAD", "OBJECT_PATIENT"} for row in ol_slots),
            "source_markers": 0, "portable_working_default_de": revisions[1]["new_working_default_de"],
            "strongest_span_eva": "ol s aiin oly", "strongest_span_working_de": "drei Drachmen Ansatz/Zubereitung; abseihen",
            "oil_identity": "UNSELECTED_C0_WHOLE_RIVAL",
        },
        "guard": {"inherited_token_query": guard}, "semantic_quarantine": quarantine,
        "claim_boundary": {
            "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "confirmed_substances": 0, "confirmed_units": 0,
            "confirmed_syntax_relations": 0, "component_values": 0, "new_pages": 0, "new_images": 0,
            "f84_accessed": False, "f84r_accessed": False,
        },
    }
    (output_dir / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
