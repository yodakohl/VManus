#!/usr/bin/env python3
"""Build the bilateral amount/content attachment atlas for GDT760."""

from __future__ import annotations

import argparse
import csv
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
BASE_REL = Path("experiments/yolo/gdt760_quantity_bilateral_content_attachment")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G759_RUN_REL = Path(
    "experiments/yolo/gdt759_quantity_part_state_construction_atlas/src/run.py"
)
G759_DICT_REL = Path(
    "experiments/yolo/gdt759_quantity_part_state_construction_atlas/"
    "artifacts/GDT759_EXACT_CONSTRUCTION_DICTIONARY.tsv"
)
G759_BRIDGES_REL = Path(
    "experiments/yolo/gdt759_quantity_part_state_construction_atlas/"
    "artifacts/QUANTITY_7_EXACT_BOUNDARY_BRIDGES.tsv"
)
G758_PRIORS_REL = Path(
    "experiments/yolo/gdt758_ychor_follower_global_content_census/"
    "src/FOLLOWER_CANDIDATE_PRIORS.tsv"
)
G754_SIEVE_REL = Path(
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
    "artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
)
OUTPUT_NAMES = (
    "QUANTITY_281_EXPRESSION_ATLAS.tsv",
    "BILATERAL_POSITION_ROLE_SUMMARY.tsv",
    "CONTENT_45_ATTACHMENT_ATLAS.tsv",
    "CONTENT_44_AMOUNT_PHRASE_READER.tsv",
    "CONTENT_ANCHOR_35_CANDIDATE_DECK.tsv",
    "AMOUNT_FORM_17_POSITION_CENSUS.tsv",
    "FUSED_S_145_CONTEXT_REVISION.tsv",
    "LINE_INITIAL_S_15_SEQUENCE_TRANSITIONS.tsv",
    "STATE_CONTRAST_AMOUNT_FAMILIES.tsv",
    "TARGET_IDENTITY_COMPETITION.tsv",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__281_AMOUNT_EXPRESSIONS__45_CLEAN_CONTENT_ATTACHMENTS__"
    "44_PHRASE_POSITIONS__35_CONTENT_WHOLES__NO_UNIVERSAL_LEFT_SLOT__"
    "POSITION_CONDITIONED_ORIENTATION__CHEOR_SHEOR_DRY_MOIST_PART_LEAD__"
    "FUSED_S_GLOBAL_DRACHM_OVERLAY_NARROWED__ZERO_CONFIRMED_LEXEMES__"
    "NO_NEW_PAGE"
)
HEADS = ("s", "or", "ar")
VALUES = ("an", "ain", "aiin", "aiiin")
VALUE_LABEL = {"an": "I", "ain": "II", "aiin": "III", "aiiin": "IV"}
VALUE_NUMBER = {"an": 1, "ain": 2, "aiin": 3, "aiiin": 4}
FUSED = {head + value: (head, value) for head in HEADS for value in VALUES}
CONTENT_AXES = {"MATERIAL", "PREPARATION"}
AMOUNT_AXES = {"AMOUNT", "PART"}
QUALITY_AXES = {
    "HOT", "COLD", "DRY", "MOIST", "BEGIN_STAGE", "MIDDLE_STAGE",
    "END_STAGE", "LEVEL_I", "LEVEL_II", "LEVEL_III",
}
PROCESS_AXES = {"PROCESS", "CLOSE"}
AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "CLOSE", "PASS", "BEGIN_STAGE",
    "MIDDLE_STAGE", "END_STAGE", "LEVEL_I", "LEVEL_II", "LEVEL_III",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g759 = load_module("gdt759_builder_for_gdt760", ROOT / G759_RUN_REL)
clean_cell = g759.g758.g756.g755.g753.g752.clean_cell
physical_folio = (
    g759.g758.g756.g755.g753.g752.g751.g750.g749.g746.g745.physical_folio
)


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


def fixed(number: float) -> str:
    return f"{number:.6f}"


def joined(values: Iterable[str]) -> str:
    selected = set(values)
    return "|".join(axis for axis in AXIS_ORDER if axis in selected) or "NONE"


def compact_counts(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def expression_position(start: int, end: int, count: int) -> str:
    if start == 1 and end == count:
        return "SINGLE"
    if start == 1:
        return "FIRST"
    if end == count:
        return "LAST"
    return "MIDDLE"


def amount_candidate(head: str, value: str) -> tuple[str, str]:
    number = VALUE_NUMBER[value]
    cardinal_f = ["null", "eine", "zwei", "drei", "vier"][number]
    cardinal_m = ["null", "ein", "zwei", "drei", "vier"][number]
    if head == "s":
        noun = "Drachme" if number == 1 else "Drachmen"
        rival_noun = "Unze" if number == 1 else "Unzen"
        equal_rival = "ein gleicher Teil" if number == 1 else f"{cardinal_m} gleiche Teile"
        return (
            f"{cardinal_f} {noun}",
            f"{equal_rival} || {cardinal_f} {rival_noun}",
        )
    if head == "or":
        noun = "Portion" if number == 1 else "Portionen"
        return f"{cardinal_f} {noun}", "Dosis/Dosen || Teil/Teile"
    noun = "Anteil" if number == 1 else "Anteile"
    return f"{cardinal_m} {noun}", "Portion/Portionen || Fraktion/Fraktionen"


def paragraph_ids(
    context: object, line_meta: dict[str, dict[str, str]]
) -> dict[str, str]:
    by_page: defaultdict[str, list[str]] = defaultdict(list)
    for locus, row in line_meta.items():
        by_page[row["page"]].append(locus)
    output: dict[str, str] = {}
    for page in sorted(by_page):
        paragraph = 0
        for locus in sorted(
            by_page[page], key=lambda item: (
                int(line_meta[item]["line_number"]), item
            )
        ):
            if paragraph == 0 or line_meta[locus]["paragraph_start"] == "1":
                paragraph += 1
            output[locus] = f"{page}-P{paragraph:03d}"
    return output


def neighbor_record(
    context: object,
    locus: str,
    ordinal: int,
    suspect_surfaces: set[str],
    overrides: dict[str, dict[str, str]],
) -> dict[str, object]:
    line = context.by_line[locus]
    if ordinal < 1 or ordinal > len(line):
        return {
            "surface": "LINE_EDGE", "ordinal": 0, "reader_exact": 0,
            "source_composed_quarantined": 0, "axes": "NONE",
            "axis_class": "EDGE_OR_NONEXACT", "semantic_candidate_de": "NONE",
            "semantic_confidence": "NONE", "semantic_source": "LINE_EDGE",
        }
    token, cell, axes = clean_cell(context, locus, ordinal)
    exact = int(context.exact[(locus, int(token["token_index"]))])
    suspect = int(str(token["eva"]) in suspect_surfaces)
    if suspect:
        axes = set()
    if not exact:
        axis_class = "EDGE_OR_NONEXACT"
    elif axes & CONTENT_AXES:
        axis_class = "CONTENT_PREP"
    elif axes & AMOUNT_AXES:
        axis_class = "AMOUNT_PART"
    elif axes & QUALITY_AXES:
        axis_class = "QUALITY_VALUE"
    elif axes & PROCESS_AXES:
        axis_class = "PROCESS_CLOSE"
    else:
        axis_class = "OPEN"
    surface = str(token["eva"])
    if suspect:
        semantic = "QUARANTINED_SOURCE_COMPOSITION"
        confidence = "HOLD"
        source = "GDT754_PROVENANCE_SIEVE"
    elif surface in overrides:
        semantic = overrides[surface]["renderer_value_de"]
        confidence = overrides[surface]["working_confidence"]
        source = "GDT758_COMPLETE_WHOLE_OVERRIDE"
    else:
        semantic = str(cell["v99r7_semantic_value_de"])
        confidence = str(cell["gdt734_confidence_level"])
        source = "GDT734_CLEAN_EXACT_WHOLE_CELL"
    return {
        "surface": surface, "ordinal": ordinal, "reader_exact": exact,
        "source_composed_quarantined": suspect, "axes": joined(axes),
        "axis_class": axis_class, "semantic_candidate_de": semantic,
        "semantic_confidence": confidence, "semantic_source": source,
    }


def content_label(axes_text: str) -> str:
    axes = set(axes_text.split("|"))
    if {"MATERIAL", "PREPARATION"} <= axes:
        return "Stoff/Zubereitung"
    return "Stoff" if "MATERIAL" in axes else "Zubereitung"


def identity_rivals(axes_text: str) -> str:
    axes = set(axes_text.split("|"))
    if {"MOIST", "MATERIAL"} <= axes:
        return "frischer Drogenteil || eingeweichter Pflanzenteil || feuchte Droge"
    if {"DRY", "MATERIAL"} <= axes:
        return "getrocknete Droge || trockener Pflanzenteil || Pulver"
    if {"MOIST", "PREPARATION"} <= axes:
        return "Mazerat || Feuchtansatz || Wasser-/Weinansatz"
    if {"COLD", "PREPARATION"} <= axes:
        return "Kaltansatz || Mazerat || gekühlte Zubereitung"
    if {"HOT", "PREPARATION"} <= axes:
        return "Dekokt || erhitzter Ansatz || warme Zubereitung"
    if "MATERIAL" in axes:
        return "Drogenstoff || Pflanzenteil || gelernter Stoffname"
    return "Ansatz || Arzneizubereitung || gelernter Zubereitungsname"


def build_expressions(
    context: object,
    line_meta: dict[str, dict[str, str]],
    suspect_surfaces: set[str],
    overrides: dict[str, dict[str, str]],
    amount_confidence: dict[tuple[str, str], str],
    bridge_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    paragraph_by_locus = paragraph_ids(context, line_meta)
    bridge_keys = {
        (row["page"], row["locus"], row["head_surface"], row["value_surface"])
        for row in bridge_rows
    }
    bridge_types = Counter(
        (row["head_surface"], row["value_surface"]) for row in bridge_rows
    )
    output: list[dict[str, object]] = []
    for locus, line in context.by_line.items():
        for index, token in enumerate(line):
            surface = str(token["eva"])
            start = index + 1
            end = start
            if surface in FUSED and context.exact[(locus, int(token["token_index"]))]:
                head, value = FUSED[surface]
                mode = "FUSED"
            elif (
                index + 1 < len(line) and surface in HEADS
                and str(line[index + 1]["eva"]) in VALUES
                and context.exact[(locus, int(token["token_index"]))]
                and context.exact[(locus, int(line[index + 1]["token_index"]))]
            ):
                head = surface
                value = str(line[index + 1]["eva"])
                end = start + 1
                mode = "SEPARATED"
            else:
                continue
            left = neighbor_record(context, locus, start - 1, suspect_surfaces, overrides)
            right = neighbor_record(context, locus, end + 1, suspect_surfaces, overrides)
            content_sides = [
                side for side, neighbor in (("L", left), ("R", right))
                if neighbor["axis_class"] == "CONTENT_PREP"
            ]
            primary, rivals = amount_candidate(head, value)
            if len(content_sides) == 1:
                neighbor = left if content_sides[0] == "L" else right
                rendered = (
                    f"Menge: {primary}; {content_label(str(neighbor['axes']))}: "
                    f"{neighbor['semantic_candidate_de']}"
                )
                render_scope = "EXACT_AMOUNT_PLUS_ONE_CLEAN_CONTENT_CONTACT"
            elif len(content_sides) == 2:
                rendered = (
                    f"links {left['semantic_candidate_de']}; Menge: {primary}; "
                    f"rechts {right['semantic_candidate_de']}; Anbindung offen"
                )
                render_scope = "EXACT_BILATERAL_CONTENT_CONTACT_AMBIGUOUS"
            elif mode == "SEPARATED":
                rendered = primary
                render_scope = "EXACT_SEPARATED_AMOUNT_SPAN"
            else:
                rendered = (
                    f"Mengenform {VALUE_LABEL[value]}; Leitkandidat {primary}; "
                    f"Rivalen {rivals}"
                )
                render_scope = "FUSED_AMOUNT_CANDIDATE_REFERENCE_OPEN"
            position = expression_position(start, end, len(line))
            meta = line_meta[locus]
            output.append({
                "expression_id": "", "page": token["page"],
                "physical_folio": physical_folio(str(token["page"])),
                "locus": locus, "line_number": meta["line_number"],
                "section": token["section"], "language": token["language"],
                "hand": token["hand"], "paragraph_id": paragraph_by_locus[locus],
                "paragraph_start_line": meta["paragraph_start"],
                "paragraph_end_line": meta["paragraph_end"], "mode": mode,
                "head_surface": head, "value_surface": value,
                "value_label": VALUE_LABEL[value], "value_number": VALUE_NUMBER[value],
                "source_expression_eva": surface if mode == "FUSED" else f"{head} {value}",
                "start_ordinal": start, "end_ordinal": end,
                "line_token_count": len(line), "expression_line_position": position,
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
                "left_surface": left["surface"], "left_ordinal": left["ordinal"],
                "left_reader_exact": left["reader_exact"],
                "left_source_composed_quarantined": left["source_composed_quarantined"],
                "left_axes": left["axes"], "left_axis_class": left["axis_class"],
                "left_semantic_candidate_de": left["semantic_candidate_de"],
                "left_semantic_confidence": left["semantic_confidence"],
                "left_semantic_source": left["semantic_source"],
                "right_surface": right["surface"], "right_ordinal": right["ordinal"],
                "right_reader_exact": right["reader_exact"],
                "right_source_composed_quarantined": right["source_composed_quarantined"],
                "right_axes": right["axes"], "right_axis_class": right["axis_class"],
                "right_semantic_candidate_de": right["semantic_candidate_de"],
                "right_semantic_confidence": right["semantic_confidence"],
                "right_semantic_source": right["semantic_source"],
                "content_attachment_sides": "|".join(content_sides) or "NONE",
                "clean_content_attachment_count": len(content_sides),
                "amount_candidate_de": primary, "amount_rivals_de": rivals,
                "amount_working_confidence": amount_confidence.get(
                    (head, value), "C0_BOUNDARY_FAMILY_EXPLORATORY"
                ),
                "exact_normalized_boundary_bridges_for_type": bridge_types[(head, value)],
                "this_zl3b_locus_is_exact_boundary_bridge": int(
                    (str(token["page"]), locus, head, value) in bridge_keys
                ),
                "gdt760_render_de": rendered, "renderer_scope": render_scope,
                "global_unit_identity_confirmed": 0, "confirmed_plaintext": 0,
                "component_export_credit": 0,
            })
    output.sort(key=lambda row: (
        str(row["page"]), int(row["line_number"]), int(row["start_ordinal"]),
        str(row["mode"]),
    ))
    for number, row in enumerate(output, start=1):
        row["expression_id"] = f"G760-E{number:04d}"
    return output


def selected_rows(
    expressions: list[dict[str, object]], dimension: str, level: str
) -> list[dict[str, object]]:
    if dimension == "ALL":
        return expressions
    field = {"POSITION": "expression_line_position", "MODE": "mode", "HEAD": "head_surface"}[dimension]
    return [row for row in expressions if row[field] == level]


def build_bilateral_summary(
    expressions: list[dict[str, object]]
) -> list[dict[str, object]]:
    groups = [
        ("ALL", "ALL"),
        *(("POSITION", value) for value in ("FIRST", "MIDDLE", "LAST")),
        *(("MODE", value) for value in ("FUSED", "SEPARATED")),
        *(("HEAD", value) for value in HEADS),
    ]
    output: list[dict[str, object]] = []
    for number, (dimension, level) in enumerate(groups, start=1):
        rows = selected_rows(expressions, dimension, level)
        left_eligible = sum(row["left_axis_class"] != "EDGE_OR_NONEXACT" for row in rows)
        right_eligible = sum(row["right_axis_class"] != "EDGE_OR_NONEXACT" for row in rows)
        left_content = sum(row["left_axis_class"] == "CONTENT_PREP" for row in rows)
        right_content = sum(row["right_axis_class"] == "CONTENT_PREP" for row in rows)
        left_rate = left_content / left_eligible if left_eligible else 0.0
        right_rate = right_content / right_eligible if right_eligible else 0.0
        if dimension == "ALL":
            decision = "NO_GLOBAL_DIRECTION_LEFT_AND_RIGHT_RATES_EQUAL"
        elif dimension == "POSITION" and level == "FIRST":
            decision = "AMOUNT_FIRST_RIGHT_CONTENT_LEAD"
        elif dimension == "POSITION" and level == "MIDDLE":
            decision = "INTERNAL_AMOUNT_LEFT_CONTENT_LEAD"
        elif dimension == "POSITION" and level == "LAST":
            decision = "AMOUNT_FINAL_LEFT_ONLY_LOW_YIELD"
        else:
            decision = "DESCRIPTIVE_SUBGROUP_NO_UNIVERSAL_RULE"
        if left_rate > right_rate + 0.02:
            preferred = "LEFT"
        elif right_rate > left_rate + 0.02:
            preferred = "RIGHT"
        else:
            preferred = "NONE_OR_TIE"
        output.append({
            "comparison_id": f"G760-D{number:02d}", "dimension": dimension,
            "level": level, "expressions": len(rows),
            "left_eligible_exact_neighbors": left_eligible,
            "left_content_preparation_neighbors": left_content,
            "left_content_rate": fixed(left_rate),
            "right_eligible_exact_neighbors": right_eligible,
            "right_content_preparation_neighbors": right_content,
            "right_content_rate": fixed(right_rate),
            "preferred_side_descriptive": preferred, "decision": decision,
            "causal_or_language_order_claim": 0,
        })
    return output


def build_attachments(
    expressions: list[dict[str, object]]
) -> list[dict[str, object]]:
    raw: list[tuple[dict[str, object], str]] = []
    for row in expressions:
        for side in ("L", "R"):
            prefix = "left" if side == "L" else "right"
            if row[f"{prefix}_axis_class"] == "CONTENT_PREP":
                raw.append((row, side))
    surface_counts = Counter(
        str(row["left_surface"] if side == "L" else row["right_surface"])
        for row, side in raw
    )
    output: list[dict[str, object]] = []
    for number, (row, side) in enumerate(raw, start=1):
        prefix = "left" if side == "L" else "right"
        surface = str(row[f"{prefix}_surface"])
        axes = str(row[f"{prefix}_axes"])
        semantic = str(row[f"{prefix}_semantic_candidate_de"])
        confidence = (
            "C2_RECURRENT_EXACT_AMOUNT_CONTACT" if surface_counts[surface] >= 3
            else "C1_REPEATED_EXACT_AMOUNT_CONTACT" if surface_counts[surface] == 2
            else "C0_SINGLE_EXACT_AMOUNT_CONTACT"
        )
        expected_side = (
            "R" if row["expression_line_position"] == "FIRST"
            else "L" if row["expression_line_position"] in {"MIDDLE", "LAST"}
            else "NONE"
        )
        output.append({
            "attachment_id": f"G760-A{number:03d}",
            "expression_id": row["expression_id"], "page": row["page"],
            "physical_folio": row["physical_folio"], "locus": row["locus"],
            "expression_line_position": row["expression_line_position"],
            "amount_mode": row["mode"], "amount_expression_eva": row["source_expression_eva"],
            "amount_head_surface": row["head_surface"],
            "amount_value_surface": row["value_surface"],
            "amount_candidate_de": row["amount_candidate_de"], "content_side": side,
            "content_surface": surface, "content_ordinal": row[f"{prefix}_ordinal"],
            "content_axes": axes, "content_role_label_de": content_label(axes),
            "content_candidate_de": semantic,
            "content_semantic_confidence": row[f"{prefix}_semantic_confidence"],
            "content_semantic_source": row[f"{prefix}_semantic_source"],
            "surface_amount_attachment_occurrences": surface_counts[surface],
            "attachment_confidence": confidence,
            "position_condition_expected_side": expected_side,
            "position_condition_agreement": int(side == expected_side),
            "candidate_phrase_de": (
                f"Menge: {row['amount_candidate_de']}; {content_label(axes)}: {semantic}"
            ),
            "identity_rivals_de": identity_rivals(axes),
            "written_line_eva": row["written_line_eva"],
            "scope": "THIS_EXACT_AMOUNT_CONTENT_CONTACT_ONLY",
            "literal_identity_confirmed": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    return output


def build_phrase_reader(
    expressions: list[dict[str, object]], attachments: list[dict[str, object]]
) -> list[dict[str, object]]:
    by_expression: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in attachments:
        by_expression[str(row["expression_id"])].append(row)
    expression_by_id = {str(row["expression_id"]): row for row in expressions}
    output: list[dict[str, object]] = []
    for expression_id in sorted(by_expression):
        group = by_expression[expression_id]
        source = expression_by_id[expression_id]
        if len(group) == 1:
            item = group[0]
            attachment = str(item["content_side"])
            candidate = str(item["candidate_phrase_de"])
            confidence = str(item["attachment_confidence"])
            decision = "ONE_CLEAN_CONTENT_CONTACT"
            content_map = f"{item['content_surface']}={item['content_candidate_de']}"
        else:
            attachment = "AMBIGUOUS_BILATERAL"
            left = next(item for item in group if item["content_side"] == "L")
            right = next(item for item in group if item["content_side"] == "R")
            candidate = (
                f"links {left['content_candidate_de']}; Menge: {source['amount_candidate_de']}; "
                f"rechts {right['content_candidate_de']}"
            )
            confidence = "C0_BILATERAL_ATTACHMENT_AMBIGUOUS"
            decision = "DO_NOT_FORCE_LEFT_OR_RIGHT_ATTACHMENT"
            content_map = (
                f"{left['content_surface']}={left['content_candidate_de']} || "
                f"{right['content_surface']}={right['content_candidate_de']}"
            )
        output.append({
            "phrase_id": f"G760-P{len(output) + 1:03d}",
            "expression_id": expression_id, "page": source["page"],
            "locus": source["locus"], "amount_expression_eva": source["source_expression_eva"],
            "amount_candidate_de": source["amount_candidate_de"],
            "content_attachment": attachment, "content_candidate_map_de": content_map,
            "working_phrase_de": candidate, "working_confidence": confidence,
            "attachment_decision": decision, "written_line_eva": source["written_line_eva"],
            "candidate_not_plaintext": 1, "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def global_candidate_stats(
    context: object, surfaces: set[str]
) -> tuple[Counter[str], defaultdict[str, set[str]]]:
    counts: Counter[str] = Counter()
    pages: defaultdict[str, set[str]] = defaultdict(set)
    for locus, line in context.by_line.items():
        for token in line:
            surface = str(token["eva"])
            if surface in surfaces and context.exact[(locus, int(token["token_index"]))]:
                counts[surface] += 1
                pages[surface].add(str(token["page"]))
    return counts, pages


def build_candidate_deck(
    context: object, attachments: list[dict[str, object]]
) -> list[dict[str, object]]:
    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in attachments:
        by_surface[str(row["content_surface"])].append(row)
    global_counts, global_pages = global_candidate_stats(context, set(by_surface))
    output: list[dict[str, object]] = []
    for surface, rows in by_surface.items():
        hits = len(rows)
        pages = {str(row["page"]) for row in rows}
        priority = (
            "A2_RECURRENT_AMOUNT_CONTENT_WHOLE" if hits >= 3 and len(pages) >= 2
            else "A1_REPEATED_AMOUNT_CONTENT_WHOLE" if hits >= 2
            else "A0_SINGLE_AMOUNT_CONTACT"
        )
        output.append({
            "content_surface": surface, "amount_attachment_occurrences": hits,
            "amount_attachment_pages": len(pages),
            "amount_attachment_loci": len({str(row["locus"]) for row in rows}),
            "left_attachments": sum(row["content_side"] == "L" for row in rows),
            "right_attachments": sum(row["content_side"] == "R" for row in rows),
            "amount_mode_counts": compact_counts(str(row["amount_mode"]) for row in rows),
            "amount_head_counts": compact_counts(str(row["amount_head_surface"]) for row in rows),
            "amount_value_counts": compact_counts(str(row["amount_value_surface"]) for row in rows),
            "line_position_counts": compact_counts(str(row["expression_line_position"]) for row in rows),
            "global_reader_exact_occurrences": global_counts[surface],
            "global_reader_exact_pages": len(global_pages[surface]),
            "amount_attachment_per_global_occurrence": fixed(
                hits / global_counts[surface] if global_counts[surface] else 0.0
            ),
            "current_content_axes": " || ".join(sorted({str(row["content_axes"]) for row in rows})),
            "current_working_whole_candidate_de": " || ".join(sorted({str(row["content_candidate_de"]) for row in rows})),
            "current_semantic_confidence": " || ".join(sorted({str(row["content_semantic_confidence"]) for row in rows})),
            "amount_attachment_priority": priority,
            "identity_rivals_de": " || ".join(sorted({str(row["identity_rivals_de"]) for row in rows})),
            "evidence": (
                f"{hits} reader-exakte unmittelbare Mengenkontakte auf {len(pages)} Seiten; "
                f"{global_counts[surface]} reader-exakte Ganzwortvorkommen im zugelassenen Cache"
            ),
            "semantic_identity_status": "REPLACEABLE_WHOLE_CANDIDATE",
            "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    rank = {"A2_RECURRENT_AMOUNT_CONTENT_WHOLE": 0,
            "A1_REPEATED_AMOUNT_CONTENT_WHOLE": 1,
            "A0_SINGLE_AMOUNT_CONTACT": 2}
    output.sort(key=lambda row: (
        rank[str(row["amount_attachment_priority"])],
        -int(row["amount_attachment_occurrences"]),
        -int(row["global_reader_exact_occurrences"]), str(row["content_surface"]),
    ))
    return output


def build_form_census(
    expressions: list[dict[str, object]]
) -> list[dict[str, object]]:
    groups: defaultdict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in expressions:
        groups[(str(row["mode"]), str(row["source_expression_eva"]))].append(row)
    output: list[dict[str, object]] = []
    for number, ((mode, surface), rows) in enumerate(sorted(groups.items()), start=1):
        sample = rows[0]
        output.append({
            "form_census_id": f"G760-F{number:02d}", "mode": mode,
            "source_expression_eva": surface, "head_surface": sample["head_surface"],
            "value_surface": sample["value_surface"],
            "amount_candidate_de": sample["amount_candidate_de"], "occurrences": len(rows),
            "pages": len({str(row["page"]) for row in rows}),
            "line_first": sum(row["expression_line_position"] == "FIRST" for row in rows),
            "line_middle": sum(row["expression_line_position"] == "MIDDLE" for row in rows),
            "line_last": sum(row["expression_line_position"] == "LAST" for row in rows),
            "paragraph_first": sum(
                row["expression_line_position"] == "FIRST"
                and str(row["paragraph_start_line"]) == "1" for row in rows
            ),
            "left_content_attachments": sum(row["left_axis_class"] == "CONTENT_PREP" for row in rows),
            "right_content_attachments": sum(row["right_axis_class"] == "CONTENT_PREP" for row in rows),
            "exact_boundary_bridges_for_type": sample["exact_normalized_boundary_bridges_for_type"],
            "unit_identity_confirmed": 0,
        })
    return output


def build_fused_s_revision(
    expressions: list[dict[str, object]]
) -> list[dict[str, object]]:
    rows = [row for row in expressions if row["mode"] == "FUSED" and row["head_surface"] == "s"]
    output: list[dict[str, object]] = []
    for number, row in enumerate(rows, start=1):
        attached = int(row["clean_content_attachment_count"]) > 0
        if attached:
            decision = "OCCURRENCE_AMOUNT_PLUS_CONTENT_PHRASE_LICENSED"
            rendered = row["gdt760_render_de"]
        elif row["expression_line_position"] == "FIRST":
            decision = "AMOUNT_FIRST_FORMULA_REFERENCE_NOT_DIRECTLY_ATTACHED"
            rendered = (
                f"Mengenform {row['value_label']} am Zeilenanfang; "
                f"{row['amount_candidate_de']} bleibt Leitkandidat"
            )
        else:
            decision = "FUSED_AMOUNT_FORMULA_REFERENCE_OPEN"
            rendered = row["gdt760_render_de"]
        output.append({
            "fused_s_revision_id": f"G760-S{number:03d}",
            "expression_id": row["expression_id"], "page": row["page"],
            "locus": row["locus"], "surface": row["source_expression_eva"],
            "value_surface": row["value_surface"], "value_label": row["value_label"],
            "line_position": row["expression_line_position"],
            "paragraph_start_line": row["paragraph_start_line"],
            "left_surface": row["left_surface"], "right_surface": row["right_surface"],
            "clean_content_attachment_sides": row["content_attachment_sides"],
            "gdt759_global_candidate_de": row["amount_candidate_de"],
            "gdt760_context_render_de": rendered, "context_decision": decision,
            "exact_content_phrase_license": int(attached),
            "working_drachm_candidate_retained": 1,
            "unconditional_global_spoken_drachm_overlay_allowed": 0,
            "simple_ordinal_entry_default_allowed": 0,
            "old_seed_reading_quarantined": 1, "confirmed_unit": 0,
            "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    return output


def build_s_sequence_transitions(
    expressions: list[dict[str, object]]
) -> list[dict[str, object]]:
    groups: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in expressions:
        if row["mode"] == "FUSED" and row["head_surface"] == "s" and row["expression_line_position"] == "FIRST":
            groups[str(row["paragraph_id"])].append(row)
    output: list[dict[str, object]] = []
    for paragraph_id in sorted(groups):
        group = sorted(groups[paragraph_id], key=lambda row: (int(row["line_number"]), int(row["start_ordinal"])))
        if len(group) < 2:
            continue
        for previous, current in zip(group, group[1:]):
            left = int(previous["value_number"])
            right = int(current["value_number"])
            direction = "INCREASE" if right > left else "DECREASE" if right < left else "EQUAL"
            output.append({
                "transition_id": f"G760-T{len(output) + 1:02d}",
                "paragraph_id": paragraph_id, "page": current["page"],
                "previous_locus": previous["locus"], "previous_surface": previous["source_expression_eva"],
                "previous_value_number": left, "current_locus": current["locus"],
                "current_surface": current["source_expression_eva"],
                "current_value_number": right, "transition_direction": direction,
                "strict_ordinal_progression_compatible": int(direction == "INCREASE"),
                "simple_entry_ordinal_default_supported": 0,
            })
    return output


def build_contrasts(
    priors: list[dict[str, str]],
    attachments: list[dict[str, object]],
    candidate_deck: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in attachments:
        by_surface[str(row["content_surface"])].append(row)
    deck = {str(row["content_surface"]): row for row in candidate_deck}
    output: list[dict[str, object]] = []
    for prior in priors:
        dry = prior["dry_surface"]
        moist = prior["moist_surface"]
        dry_rows = by_surface[dry]
        moist_rows = by_surface[moist]
        output.append({
            "contrast_id": prior["contrast_id"], "shared_role": prior["shared_role"],
            "dry_surface": dry, "dry_working_candidate_de": prior["dry_working_candidate_de"],
            "dry_amount_attachments": len(dry_rows),
            "dry_global_exact_occurrences": deck[dry]["global_reader_exact_occurrences"] if dry in deck else 0,
            "moist_surface": moist, "moist_working_candidate_de": prior["moist_working_candidate_de"],
            "moist_amount_attachments": len(moist_rows),
            "moist_global_exact_occurrences": deck[moist]["global_reader_exact_occurrences"] if moist in deck else 0,
            "amount_head_counts": compact_counts(str(row["amount_head_surface"]) for row in dry_rows + moist_rows),
            "amount_value_counts": compact_counts(str(row["amount_value_surface"]) for row in dry_rows + moist_rows),
            "observed_exact_amount_phrases": len(dry_rows) + len(moist_rows),
            "disposition": "BOTH_WHOLES_OCCUPY_EXACT_AMOUNT_CONTENT_SLOT" if dry_rows and moist_rows else "PAIR_NOT_COMPLETELY_OBSERVED",
            "interpretation": prior["interpretation"],
            "component_contrast_export_allowed": 0, "confirmed_lexeme": 0,
        })
    return output


def build_identity_competition(
    priors: list[dict[str, str]], attachments: list[dict[str, object]]
) -> list[dict[str, object]]:
    by_surface = Counter(str(row["content_surface"]) for row in attachments)
    pages_by_surface: defaultdict[str, set[str]] = defaultdict(set)
    for row in attachments:
        pages_by_surface[str(row["content_surface"])].add(str(row["page"]))
    output: list[dict[str, object]] = []
    for prior in priors:
        surfaces = [item for item in prior["candidate_surfaces"].split("|") if item]
        hit_counts = {surface: by_surface[surface] for surface in surfaces if by_surface[surface]}
        pages = set().union(*(pages_by_surface[surface] for surface in surfaces)) if surfaces else set()
        output.append({
            "candidate_id": prior["candidate_id"], "target_identity_de": prior["target_identity_de"],
            "candidate_surfaces": prior["candidate_surfaces"],
            "current_amount_attachment_hits": sum(hit_counts.values()),
            "current_amount_attachment_pages": len(pages),
            "supporting_surface_counts": "|".join(
                f"{surface}:{hit_counts[surface]}" for surface in sorted(hit_counts)
            ) or "NONE",
            "other_predecessor_span_evidence": prior["other_predecessor_span_evidence"],
            "strongest_current_lead": prior["strongest_current_lead"],
            "counterevidence": prior["counterevidence"],
            "disposition": prior["disposition"],
            "specific_identity_selected": prior["specific_identity_selected"],
            "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    return output


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    g759_dictionary = read_tsv(ROOT / G759_DICT_REL)
    bridge_rows = read_tsv(ROOT / G759_BRIDGES_REL)
    override_rows = read_tsv(ROOT / G758_PRIORS_REL)
    sieve_rows = read_tsv(ROOT / G754_SIEVE_REL)
    contrast_priors = read_tsv(SRC / "STATE_CONTRAST_PRIORS.tsv")
    identity_priors = read_tsv(SRC / "TARGET_IDENTITY_PRIORS.tsv")
    if len(bridge_rows) != 7 or len(sieve_rows) != 172:
        raise AssertionError("fixed GDT759 bridge and GDT754 quarantine universes required")
    if len(contrast_priors) != 2 or len(identity_priors) != 8:
        raise AssertionError("fixed contrast and target-identity decks required")
    overrides = {row["surface"]: row for row in override_rows}
    overrides["ols"] = dict(overrides["ols"])
    overrides["ols"]["renderer_value_de"] = "abgeseihte Zubereitung"
    suspect_surfaces = {row["surface"] for row in sieve_rows}
    amount_confidence = {
        tuple(row["exact_expression_eva"].split()): row["working_confidence"]
        for row in g759_dictionary if row["family"] == "QUANTITY_VALUE"
    }
    context, line_meta, inherited_guard = g759.g758.g756.g755.g753.g752.g751.load_context()
    expressions = build_expressions(
        context, line_meta, suspect_surfaces, overrides, amount_confidence, bridge_rows
    )
    bilateral = build_bilateral_summary(expressions)
    attachments = build_attachments(expressions)
    phrases = build_phrase_reader(expressions, attachments)
    candidate_deck = build_candidate_deck(context, attachments)
    form_census = build_form_census(expressions)
    fused_s = build_fused_s_revision(expressions)
    transitions = build_s_sequence_transitions(expressions)
    contrasts = build_contrasts(contrast_priors, attachments, candidate_deck)
    identities = build_identity_competition(identity_priors, attachments)

    position_counts = Counter(str(row["expression_line_position"]) for row in expressions)
    left_classes = Counter(str(row["left_axis_class"]) for row in expressions)
    right_classes = Counter(str(row["right_axis_class"]) for row in expressions)
    mode_counts = Counter(str(row["mode"]) for row in expressions)
    if mode_counts != Counter({"FUSED": 185, "SEPARATED": 96}):
        raise AssertionError(f"amount mode universe changed: {mode_counts}")
    if position_counts != Counter({"FIRST": 87, "MIDDLE": 169, "LAST": 25}):
        raise AssertionError(f"amount position universe changed: {position_counts}")
    if left_classes != Counter({
        "EDGE_OR_NONEXACT": 118, "OPEN": 130, "CONTENT_PREP": 20,
        "QUALITY_VALUE": 10, "AMOUNT_PART": 3,
    }):
        raise AssertionError(f"left neighbor universe changed: {left_classes}")
    if right_classes != Counter({
        "EDGE_OR_NONEXACT": 77, "OPEN": 162, "CONTENT_PREP": 25,
        "QUALITY_VALUE": 12, "AMOUNT_PART": 3, "PROCESS_CLOSE": 2,
    }):
        raise AssertionError(f"right neighbor universe changed: {right_classes}")
    if len(expressions) != 281 or len(attachments) != 45 or len(phrases) != 44:
        raise AssertionError("expected 281 expressions, 45 attachments and 44 phrases")
    if len(candidate_deck) != 35 or len(form_census) != 17 or len(fused_s) != 145:
        raise AssertionError("candidate, form or fused-s census changed")
    if len(transitions) != 15 or len({row["paragraph_id"] for row in transitions}) != 11:
        raise AssertionError("line-initial s transition universe changed")
    if Counter(row["transition_direction"] for row in transitions) != Counter({
        "EQUAL": 10, "DECREASE": 2, "INCREASE": 3,
    }):
        raise AssertionError("line-initial s transition directions changed")
    if sum(int(row["exact_content_phrase_license"]) for row in fused_s) != 22:
        raise AssertionError("expected 22 fused-s content phrase licenses")

    tables = (
        expressions, bilateral, attachments, phrases, candidate_deck, form_census,
        fused_s, transitions, contrasts, identities,
    )
    for name, rows in zip(OUTPUT_NAMES[:-1], tables):
        write_tsv(output_dir / name, rows, list(rows[0]))

    all_summary = next(row for row in bilateral if row["dimension"] == "ALL")
    first_summary = next(row for row in bilateral if row["dimension"] == "POSITION" and row["level"] == "FIRST")
    middle_summary = next(row for row in bilateral if row["dimension"] == "POSITION" and row["level"] == "MIDDLE")
    last_summary = next(row for row in bilateral if row["dimension"] == "POSITION" and row["level"] == "LAST")
    result = {
        "schema": "GDT760_RESULT_V1", "status": STATUS,
        "scope": {
            "amount_expressions": len(expressions), "fused_expressions": mode_counts["FUSED"],
            "separated_expressions": mode_counts["SEPARATED"],
            "clean_content_attachments": len(attachments),
            "amount_expressions_with_content": len(phrases),
            "distinct_content_surfaces": len(candidate_deck), "amount_form_types": len(form_census),
            "fused_s_occurrences_revised": len(fused_s),
            "fused_s_content_phrase_licenses": sum(int(row["exact_content_phrase_license"]) for row in fused_s),
            "line_initial_s_transitions": len(transitions),
            "line_initial_s_multi_entry_paragraphs": len({row["paragraph_id"] for row in transitions}),
            "state_contrast_families": len(contrasts),
            "target_identity_competitors": len(identities),
            "cached_pages_in_guarded_context": len({str(row["page"]) for row in expressions}),
        },
        "bilateral_result": {
            "global_left_content": f"{all_summary['left_content_preparation_neighbors']}/{all_summary['left_eligible_exact_neighbors']}",
            "global_left_rate": all_summary["left_content_rate"],
            "global_right_content": f"{all_summary['right_content_preparation_neighbors']}/{all_summary['right_eligible_exact_neighbors']}",
            "global_right_rate": all_summary["right_content_rate"],
            "global_direction": "NONE_RATES_EFFECTIVELY_EQUAL",
            "line_first_right_content": f"{first_summary['right_content_preparation_neighbors']}/{first_summary['right_eligible_exact_neighbors']}",
            "line_middle_left_content": f"{middle_summary['left_content_preparation_neighbors']}/{middle_summary['left_eligible_exact_neighbors']}",
            "line_middle_right_content": f"{middle_summary['right_content_preparation_neighbors']}/{middle_summary['right_eligible_exact_neighbors']}",
            "line_final_left_content": f"{last_summary['left_content_preparation_neighbors']}/{last_summary['left_eligible_exact_neighbors']}",
            "selected_working_rule": "line-first amount looks right; internal amount looks left first; line-final amount has no automatic content default",
        },
        "content_result": {
            "recurrent_three_hit_surfaces": sorted(
                row["content_surface"] for row in candidate_deck if int(row["amount_attachment_occurrences"]) >= 3
            ),
            "dry_moist_part_pair": "cheor/sheor: 3+3 exact amount contacts",
            "dry_moist_preparation_pair": "cheo/sheo: 2+1 exact amount contacts",
            "leaf_lead": "cthy: one direct amount attachment; GDT758 Blattgut whole candidate retained",
            "water_wine_oil_salt": "NO_SPECIFIC_IDENTITY_SELECTED",
        },
        "fused_s_correction": {
            "fused_s_occurrences": len(fused_s),
            "line_first_fused_s": sum(row["line_position"] == "FIRST" for row in fused_s),
            "separated_s_occurrences": sum(row["mode"] == "SEPARATED" and row["head_surface"] == "s" for row in expressions),
            "line_first_separated_s": sum(
                row["mode"] == "SEPARATED" and row["head_surface"] == "s"
                and row["expression_line_position"] == "FIRST" for row in expressions
            ),
            "strictly_increasing_initial_transitions": sum(row["transition_direction"] == "INCREASE" for row in transitions),
            "nonincreasing_initial_transitions": sum(row["transition_direction"] != "INCREASE" for row in transitions),
            "simple_entry_ordinal_default": "REJECTED",
            "drachm_candidate": "RETAINED_AS_CONTEXTUAL_LEAD",
            "unconditional_fused_exact_whole_spoken_overlay": "REMOVED",
            "fused_content_attached_phrase_licenses": sum(int(row["exact_content_phrase_license"]) for row in fused_s),
        },
        "guard": {"inherited_token_query": inherited_guard},
        "claim_boundary": {
            "confirmed_lexemes": 0, "confirmed_units": 0,
            "confirmed_plaintext_clauses": 0, "component_values": 0,
            "specific_liquid_identities": 0, "new_pages": 0, "new_images": 0,
            "f84_accessed": False, "f84r_accessed": False,
        },
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
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
