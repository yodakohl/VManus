#!/usr/bin/env python3
"""Resolve ofchy and schor as concrete, replaceable content-field defaults."""

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
BASE_REL = Path("experiments/yolo/gdt765_ofchy_schor_content_field_discriminator")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

G764_RUN_REL = Path("experiments/yolo/gdt764_bounded_value_field_dispatch/src/run.py")
G737_FORM_REL = Path("experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_273_FORM_ROLE_BRIDGE.tsv")
G738_FORM_REL = Path("experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/artifacts/FORM_273_ADJUDICATION.tsv")
G738_ANCHOR_REL = Path("experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/artifacts/NONHEAD_NEIGHBOR_AXIS_ANCHORS.tsv")
G761_CHOR_REL = Path("experiments/yolo/gdt761_state_pair_outer_carrier_bridge/artifacts/CHOR_5_CARRIER_AND_SHOR_SHEOR_2_RIVAL_SPAN_ATLAS.tsv")
G723_CORE_REL = Path("experiments/yolo/gdt723_v96_twelve_preparation_bound_core_context_repair/artifacts/V96_12_PREPARATION_CORE_CONTEXT_DELTA.tsv")
G735_HISTORY_REL = Path("experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_ENTRY_ATLAS.tsv")

TARGETS = ("ofchy", "schor")
CHOR_VALUE_HEADS = ("chor", "cthor", "dshor", "schor", "shor", "sor", "tchor", "qotor", "or")
VALUE_WHOLES = ("aiin", "dain", "daiin", "qodaiin")
F22_LOCI = ("f22r.4", "f22r.5", "f22r.6")
OUTPUT_NAMES = (
    "TARGET_6_EXACT_OCCURRENCE_ATLAS.tsv",
    "TARGET_RAW_EXACT_AUDIT.tsv",
    "OFCH_25_EXACT_FAMILY_ATLAS.tsv",
    "FCHY_13_EXACT_FAMILY_ATLAS.tsv",
    "FORMAL_FAMILY_21_WHOLE_PROFILE.tsv",
    "CHOR_VALUE_67_PAIR_ATLAS.tsv",
    "H_HEAD_X_DAIIN_12_ATLAS.tsv",
    "F22R_4_VALUE_GRID.tsv",
    "TARGET_HYPOTHESIS_SCORECARD.tsv",
    "TARGET_WORKING_DICTIONARY_REVISION.tsv",
    "TARGET_6_CONCRETE_RENDERER.tsv",
    "F22R4_9_TOKEN_WORKING_READER.tsv",
    "CFHY_6_EXACT_TRANSITION_AUDIT.tsv",
    "HISTORICAL_CONTENT_FIELD_COMPARATORS.tsv",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__6_TARGET_OCCURRENCES__OFCHY_3_OF3_NOMINAL_SPECIFICATION_HEAD__"
    "SELECT_BLUETENMASSE_C0__SCHOR_3_ITEM_HEADS__SELECT_BLUETENSTAND_C1__"
    "25_OFCH_PREFIX__13_FCHY_SUFFIX__67_CHOR_VALUE_PAIRS__12_H_X_DAIIN__"
    "F22R_TWO_PARALLEL_TARGET_FIELDS__CFHY_TRANSITION_C1__ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g764 = load_module("gdt764_builder_for_gdt765", ROOT / G764_RUN_REL)


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


def line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def build_target_occurrences(
    env: dict[str, object],
    defaults: dict[str, dict[str, str]],
    render_specs: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, object]]:
    context = env["context"]
    line_meta = env["line_meta"]
    output: list[dict[str, object]] = []
    for locus, line in sorted(context.by_line.items()):
        for index, token in enumerate(line):
            surface = str(token["eva"])
            ordinal = index + 1
            if surface not in defaults or not context.exact[(locus, int(token["token_index"]))]:
                continue
            spec = render_specs[(surface, locus)]
            span_start = int(spec["span_start"])
            span_end = int(spec["span_end"])
            if span_start != ordinal:
                raise AssertionError(f"render start mismatch: {surface} {locus}")
            span = line[span_start - 1:span_end]
            if not span or not all(context.exact[(locus, int(item["token_index"]))] for item in span):
                raise AssertionError(f"render span is not wholly exact: {surface} {locus}")
            current = g764.slot(env, locus, ordinal)
            left = g764.slot(env, locus, ordinal - 1)
            right = g764.slot(env, locus, ordinal + 1)
            tail = [g764.slot(env, locus, pos) for pos in range(ordinal + 1, span_end + 1)]
            default = defaults[surface]
            output.append({
                "target_occurrence_id": f"G765-T{len(output)+1:02d}",
                "surface": surface,
                "page": str(token["page"]),
                "physical_folio": g764.g763.physical_folio(str(token["page"])),
                "locus": locus,
                "section": str(token["section"]),
                "language": str(token["language"]),
                "hand": str(token["hand"]),
                "ordinal": ordinal,
                "line_token_count": len(line),
                "line_position": line_position(ordinal, len(line)),
                "paragraph_start_line": line_meta[locus]["paragraph_start"],
                "paragraph_end_line": line_meta[locus]["paragraph_end"],
                "current_structural_roles": current["roles"],
                "current_semantic_candidate_de": current["semantic_candidate_de"],
                "left_surface": left["surface"],
                "left_roles": left["roles"],
                "right_surface": right["surface"],
                "right_roles": right["roles"],
                "render_channel": spec["channel"],
                "exact_span_eva": " ".join(str(item["eva"]) for item in span),
                "tail_surfaces": "|".join(str(item["surface"]) for item in tail) or "NONE",
                "tail_roles": "|".join(str(item["roles"]) for item in tail) or "NONE",
                "tail_candidates_de": " || ".join(str(item["semantic_candidate_de"]) for item in tail) or "NONE",
                "selected_role_de": default["selected_role_de"],
                "portable_default_de": default["portable_default_de"],
                "bold_concrete_default_de": default["bold_concrete_default_de"],
                "role_confidence": default["role_confidence"],
                "identity_confidence": default["identity_confidence"],
                "portable_renderer_de": spec["portable_renderer_de"],
                "bold_renderer_de": spec["bold_renderer_de"],
                "render_basis": spec["basis"],
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
                "confirmed_plaintext": 0,
                "component_export_credit": 0,
            })
    return output


def build_raw_exact_audit(env: dict[str, object]) -> list[dict[str, object]]:
    context = env["context"]
    output: list[dict[str, object]] = []
    for surface in TARGETS:
        hits: list[tuple[str, int, int]] = []
        for locus, line in sorted(context.by_line.items()):
            for index, token in enumerate(line, 1):
                if str(token["eva"]) == surface:
                    hits.append((locus, index, int(context.exact[(locus, int(token["token_index"]))])))
        exact = [item for item in hits if item[2] == 1]
        excluded = [item for item in hits if item[2] == 0]
        output.append({
            "surface": surface,
            "raw_occurrences": len(hits),
            "reader_exact_occurrences": len(exact),
            "reader_exact_pages": len({str(context.by_line[locus][ordinal - 1]["page"]) for locus, ordinal, _ in exact}),
            "exact_loci_and_ordinals": "|".join(f"{locus}:{ordinal}" for locus, ordinal, _ in exact),
            "excluded_loci_and_ordinals": "|".join(f"{locus}:{ordinal}" for locus, ordinal, _ in excluded) or "NONE",
            "exclusion_rule": "TARGET_TOKEN_MUST_BE_READER_EXACT",
            "component_export_credit": 0,
        })
    return output


def build_family_atlas(env: dict[str, object], family: str) -> list[dict[str, object]]:
    context = env["context"]
    line_meta = env["line_meta"]
    if family == "OFCH_PREFIX":
        predicate = lambda value: value.startswith("ofch")
    elif family == "FCHY_SUFFIX":
        predicate = lambda value: value.endswith("fchy")
    else:
        raise AssertionError(family)
    output: list[dict[str, object]] = []
    for locus, line in sorted(context.by_line.items()):
        for index, token in enumerate(line, 1):
            surface = str(token["eva"])
            if not predicate(surface) or not context.exact[(locus, int(token["token_index"]))]:
                continue
            left = g764.slot(env, locus, index - 1)
            right = g764.slot(env, locus, index + 1)
            output.append({
                "family_occurrence_id": f"G765-{family[:2]}{len(output)+1:03d}",
                "family": family,
                "surface": surface,
                "page": str(token["page"]),
                "locus": locus,
                "section": str(token["section"]),
                "hand": str(token["hand"]),
                "ordinal": index,
                "line_token_count": len(line),
                "line_position": line_position(index, len(line)),
                "paragraph_start_line": line_meta[locus]["paragraph_start"],
                "paragraph_end_line": line_meta[locus]["paragraph_end"],
                "left_surface": left["surface"],
                "left_roles": left["roles"],
                "left_candidate_de": left["semantic_candidate_de"],
                "right_surface": right["surface"],
                "right_roles": right["roles"],
                "right_candidate_de": right["semantic_candidate_de"],
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
                "family_analogy_only": 1,
                "component_export_credit": 0,
            })
    return output


def build_family_profile(*atlases: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for rows in atlases:
        grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
        for row in rows:
            grouped[str(row["surface"])].append(row)
        family = str(rows[0]["family"])
        for surface in sorted(grouped):
            selected = grouped[surface]
            output.append({
                "family": family,
                "surface": surface,
                "exact_occurrences": len(selected),
                "pages": len({str(row["page"]) for row in selected}),
                "sections": compact(str(row["section"]) for row in selected),
                "line_positions": compact(str(row["line_position"]) for row in selected),
                "paragraph_start_occurrences": sum(str(row["paragraph_start_line"]) == "1" for row in selected),
                "paragraph_end_occurrences": sum(str(row["paragraph_end_line"]) == "1" for row in selected),
                "right_role_profile": compact(str(row["right_roles"]) for row in selected),
                "semantic_transfer": "WHOLE_FORM_ANALOGY_ONLY",
                "component_export_credit": 0,
            })
    return output


def build_chor_value_pairs(env: dict[str, object]) -> list[dict[str, object]]:
    context = env["context"]
    output: list[dict[str, object]] = []
    for locus, line in sorted(context.by_line.items()):
        for index in range(0, len(line) - 1):
            head, value = line[index:index + 2]
            head_surface = str(head["eva"])
            value_surface = str(value["eva"])
            if head_surface not in CHOR_VALUE_HEADS or value_surface not in VALUE_WHOLES:
                continue
            if not context.exact[(locus, int(head["token_index"]))] or not context.exact[(locus, int(value["token_index"]))]:
                continue
            value_slot = g764.slot(env, locus, index + 2)
            output.append({
                "pair_id": f"G765-CV{len(output)+1:03d}",
                "head_surface": head_surface,
                "value_surface": value_surface,
                "page": str(head["page"]),
                "locus": locus,
                "section": str(head["section"]),
                "hand": str(head["hand"]),
                "head_ordinal": index + 1,
                "line_position": line_position(index + 1, len(line)),
                "exact_span_eva": f"{head_surface} {value_surface}",
                "value_roles": value_slot["roles"],
                "value_candidate_de": value_slot["semantic_candidate_de"],
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
                "head_family_value_contact": 1,
                "component_export_credit": 0,
            })
    return output


def build_h_head_x_daiin(env: dict[str, object]) -> list[dict[str, object]]:
    context = env["context"]
    heads = env["head_registry"]
    output: list[dict[str, object]] = []
    for locus, line in sorted(context.by_line.items()):
        for index in range(0, len(line) - 2):
            head, field, value = line[index:index + 3]
            head_surface = str(head["eva"])
            if head_surface not in heads or str(value["eva"]) != "daiin":
                continue
            if not all(context.exact[(locus, int(item["token_index"]))] for item in (head, field, value)):
                continue
            registry = heads[head_surface]
            field_slot = g764.slot(env, locus, index + 2)
            output.append({
                "triple_id": f"G765-HD{len(output)+1:02d}",
                "page": str(head["page"]),
                "locus": locus,
                "section": str(head["section"]),
                "hand": str(head["hand"]),
                "head_ordinal": index + 1,
                "head_surface": head_surface,
                "head_id": registry["head_id"],
                "head_record_role": registry["record_role"],
                "head_body_role_de": registry["body_role_de"],
                "x_surface": str(field["eva"]),
                "x_roles": field_slot["roles"],
                "x_candidate_de": field_slot["semantic_candidate_de"],
                "daiin_value": "III",
                "exact_span_eva": f"{head_surface} {field['eva']} daiin",
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
                "component_export_credit": 0,
            })
    return output


def build_f22_value_grid(env: dict[str, object], defaults: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    context = env["context"]
    bold = {
        "ofchy": "drei Einheiten Blütenmasse",
        "schor": "drei Einheiten Blütenstand",
        "ol": "drei Einheiten Ansatz oder Zubereitung",
        "dar": "abgemessener Anteil I, Wert III",
    }
    output: list[dict[str, object]] = []
    for locus in F22_LOCI:
        line = context.by_line[locus]
        for index in range(0, len(line) - 1):
            head, value = line[index:index + 2]
            if str(value["eva"]) != "daiin" or not all(context.exact[(locus, int(item["token_index"]))] for item in (head, value)):
                continue
            head_surface = str(head["eva"])
            head_slot = g764.slot(env, locus, index + 1)
            output.append({
                "grid_field_id": f"G765-FG{len(output)+1:02d}",
                "locus": locus,
                "head_ordinal": index + 1,
                "field_head_surface": head_surface,
                "current_roles": head_slot["roles"],
                "current_candidate_de": head_slot["semantic_candidate_de"],
                "gdt765_target": int(head_surface in defaults),
                "gdt765_role_de": defaults[head_surface]["selected_role_de"] if head_surface in defaults else head_slot["semantic_candidate_de"],
                "value": "III",
                "bold_working_renderer_de": bold[head_surface],
                "written_span_eva": f"{head_surface} daiin",
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
                "component_export_credit": 0,
            })
    return output


def build_hypothesis_scorecard(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        score = (
            2 * int(row["bounded_tail_fit"])
            + 2 * int(row["parallel_field_fit"])
            + int(row["family_support"])
            - 2 * int(row["stacking_or_redundancy_penalty"])
            - int(row["unsupported_identity_penalty"])
        )
        output.append({
            **row,
            "working_score": score,
            "score_rule": "2*tail+2*parallel+family-2*redundancy-unsupported_identity",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def build_dictionary_revision(
    target_rows: list[dict[str, object]],
    defaults: list[dict[str, str]],
    ofch: list[dict[str, object]],
    chor_pairs: list[dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for spec in defaults:
        surface = spec["surface"]
        selected = [row for row in target_rows if row["surface"] == surface]
        family_members = (
            sorted({str(row["surface"]) for row in ofch})
            if surface == "ofchy"
            else sorted({str(row["head_surface"]) for row in chor_pairs})
        )
        output.append({
            "surface": surface,
            "previous_gdt764_default_de": "ofchy-Feld; Bedeutung offen" if surface == "ofchy" else "trockener Teil-/Portionsträger; unentschieden",
            "selected_role_de": spec["selected_role_de"],
            "portable_default_de": spec["portable_default_de"],
            "bold_concrete_default_de": spec["bold_concrete_default_de"],
            "role_confidence": spec["role_confidence"],
            "identity_confidence": spec["identity_confidence"],
            "identity_score_100": spec["identity_score_100"],
            "exact_occurrences": len(selected),
            "exact_pages": len({str(row["page"]) for row in selected}),
            "direct_value_contacts": sum(str(row["render_channel"]) == "VALUE_FIELD" for row in selected),
            "formal_analogy_members": "|".join(family_members),
            "strongest_evidence": spec["strongest_evidence"],
            "strongest_counterevidence": spec["strongest_counterevidence"],
            "primary_rival_de": spec["primary_rival_de"],
            "secondary_rival_de": spec["secondary_rival_de"],
            "specific_identity_is_replaceable": 1,
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def build_concrete_renderer(target_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{
        "renderer_id": f"G765-R{index:02d}",
        "surface": row["surface"],
        "page": row["page"],
        "locus": row["locus"],
        "exact_span_eva": row["exact_span_eva"],
        "portable_renderer_de": row["portable_renderer_de"],
        "bold_renderer_de": row["bold_renderer_de"],
        "role_confidence": row["role_confidence"],
        "identity_confidence": row["identity_confidence"],
        "evidence": row["render_basis"],
        "scope": "THIS_EXACT_OBSERVED_SPAN",
        "confirmed_plaintext": 0,
        "component_export_credit": 0,
    } for index, row in enumerate(target_rows, 1)]


def build_f22_reader(env: dict[str, object], specs: list[dict[str, str]]) -> list[dict[str, object]]:
    locus = "f22r.4"
    context = env["context"]
    line = context.by_line[locus]
    if len(specs) != len(line):
        raise AssertionError("f22r.4 token default length")
    bold_line = (
        "Haupteintrag, Trockenklasse III: drei Einheiten Blütenmasse; "
        "abgemessene Drogenportion Form III mit dazugehörigem Trockenmaterial; "
        "Unterposten: drei Einheiten Blütenstand."
    )
    portable_line = (
        "Haupteintrag, Trockenklasse III: benannte Arzneidroge in Grundform, Wert III; "
        "interner Stoff-, Mess- und Trockenmaterialblock; Unterposten: Pflanzenteilposten, Wert III."
    )
    output: list[dict[str, object]] = []
    for spec, token in zip(specs, line):
        ordinal = int(spec["ordinal"])
        if ordinal != len(output) + 1 or spec["surface"] != str(token["eva"]):
            raise AssertionError(f"f22r.4 token spec mismatch at {ordinal}")
        if not context.exact[(locus, int(token["token_index"]))]:
            raise AssertionError(f"nonexact token entered f22 reader: {ordinal}")
        output.append({
            "page": str(token["page"]),
            "locus": locus,
            "ordinal": ordinal,
            "surface": spec["surface"],
            "local_default_de": spec["local_default_de"],
            "confidence": spec["confidence"],
            "evidence": spec["evidence"],
            "global_export": spec["global_export"],
            "written_line_eva": " ".join(str(item["eva"]) for item in line),
            "portable_line_renderer_de": portable_line,
            "bold_line_renderer_de": bold_line,
            "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    return output


def build_historical_comparators(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    selected_ids = {"HEO001", "HEO004", "HEO005", "HEO006", "HEO008", "HEO009", "HEO010"}
    use = {
        "HEO001": "learned drug name followed by compact qualities and degree",
        "HEO004": "part-class header above learned simples",
        "HEO005": "named drug plus plant part plus qualities and degree",
        "HEO006": "named drug plus root plus qualities and degree",
        "HEO008": "ingredient list plus separate amount fields",
        "HEO009": "amount marker, unit and value occupy distinct slots",
        "HEO010": "number and ingredient are separate written fields",
    }
    output: list[dict[str, object]] = []
    for row in rows:
        if row["observation_id"] not in selected_ids:
            continue
        output.append({
            "historical_item_id": row["observation_id"],
            "record_mode": row["record_mode"],
            "headword_or_rubric": row["headword_or_rubric"],
            "observed_slots": row["observed_slots"],
            "layout_relation": row["layout_relation"],
            "gdt765_architecture_use": use[row["observation_id"]],
            "evidence_summary": row["evidence_summary"],
            "caveat": row["caveat"],
            "target_spelling_credit": 0,
            "target_identity_credit": 0,
            "component_export_credit": 0,
        })
    return output


def build_cfhy_audit(env: dict[str, object]) -> list[dict[str, object]]:
    context = env["context"]
    line_meta = env["line_meta"]
    raw: list[tuple[str, int, int]] = []
    for locus, line in sorted(context.by_line.items()):
        for index, token in enumerate(line, 1):
            if str(token["eva"]) == "cfhy":
                raw.append((locus, index, int(context.exact[(locus, int(token["token_index"]))])))
    excluded = "|".join(f"{locus}:{ordinal}" for locus, ordinal, exact in raw if not exact) or "NONE"
    output: list[dict[str, object]] = []
    for locus, ordinal, exact in raw:
        if not exact:
            continue
        line = context.by_line[locus]
        token = line[ordinal - 1]
        left = g764.slot(env, locus, ordinal - 1)
        right = g764.slot(env, locus, ordinal + 1)
        output.append({
            "audit_id": f"G765-CF{len(output)+1:02d}",
            "page": str(token["page"]),
            "locus": locus,
            "section": str(token["section"]),
            "hand": str(token["hand"]),
            "ordinal": ordinal,
            "line_token_count": len(line),
            "line_position": line_position(ordinal, len(line)),
            "paragraph_start_line": line_meta[locus]["paragraph_start"],
            "paragraph_end_line": line_meta[locus]["paragraph_end"],
            "left_surface": left["surface"],
            "left_roles": left["roles"],
            "right_surface": right["surface"],
            "right_roles": right["roles"],
            "right_is_daiin": int(right["surface"] == "daiin"),
            "raw_occurrences": len(raw),
            "reader_exact_occurrences": sum(item[2] for item in raw),
            "excluded_loci_and_ordinals": excluded,
            "selected_local_role": "FIELD_TRANSITION_OR_CONTINUATION",
            "local_renderer_de": ";",
            "retired_specific_actions": "NEHMEN|AUSWRINGEN",
            "confidence": "C1_LOCAL_STRUCTURE",
            "global_export": 0,
            "written_line_eva": " ".join(str(item["eva"]) for item in line),
            "component_export_credit": 0,
        })
    return output


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    default_specs = read_tsv(SRC / "TARGET_DEFAULT_SPECS.tsv")
    render_spec_rows = read_tsv(SRC / "OCCURRENCE_RENDER_SPECS.tsv")
    hypothesis_specs = read_tsv(SRC / "TARGET_HYPOTHESIS_SPECS.tsv")
    token_specs = read_tsv(SRC / "F22R4_TOKEN_DEFAULT_SPECS.tsv")
    defaults = {row["surface"]: row for row in default_specs}
    render_specs = {(row["surface"], row["locus"]): row for row in render_spec_rows}
    if tuple(defaults) != TARGETS or len(render_specs) != 6:
        raise AssertionError("target spec universe changed")

    env = g764.semantic_environment()
    targets = build_target_occurrences(env, defaults, render_specs)
    audit = build_raw_exact_audit(env)
    ofch = build_family_atlas(env, "OFCH_PREFIX")
    fchy = build_family_atlas(env, "FCHY_SUFFIX")
    profiles = build_family_profile(ofch, fchy)
    chor_pairs = build_chor_value_pairs(env)
    h_triples = build_h_head_x_daiin(env)
    value_grid = build_f22_value_grid(env, defaults)
    hypotheses = build_hypothesis_scorecard(hypothesis_specs)
    dictionary = build_dictionary_revision(targets, default_specs, ofch, chor_pairs)
    renderers = build_concrete_renderer(targets)
    reader = build_f22_reader(env, token_specs)
    cfhy = build_cfhy_audit(env)
    history = build_historical_comparators(read_tsv(ROOT / G735_HISTORY_REL))

    held_forms = read_tsv(ROOT / G737_FORM_REL)
    adjudication = read_tsv(ROOT / G738_FORM_REL)
    anchors = read_tsv(ROOT / G738_ANCHOR_REL)
    chor_spans = read_tsv(ROOT / G761_CHOR_REL)
    core_rows = read_tsv(ROOT / G723_CORE_REL)
    schor_held = [row for row in held_forms if row["form"] == "schor"]
    schor_adjudication = [row for row in adjudication if row["form"] == "schor"]
    schor_anchors = [row for row in anchors if row["form"] == "schor"]
    exact_chor_phrases = [row for row in chor_spans if row["carrier_surface"] == "chor" and row["exact_phrase_translation_license"] == "1"]
    ofchedy = [row for row in core_rows if row["surface"] == "ofchedy"]

    if Counter(str(row["surface"]) for row in targets) != Counter({"ofchy": 3, "schor": 3}):
        raise AssertionError("target occurrence census changed")
    if [(row["surface"], row["raw_occurrences"], row["reader_exact_occurrences"]) for row in audit] != [("ofchy", 4, 3), ("schor", 3, 3)]:
        raise AssertionError("raw/exact audit changed")
    if len(ofch) != 25 or len({row["surface"] for row in ofch}) != 13:
        raise AssertionError("ofch family census changed")
    if len(fchy) != 13 or len({row["surface"] for row in fchy}) != 8:
        raise AssertionError("fchy family census changed")
    if len(profiles) != 21:
        raise AssertionError("family profile count")
    expected_chor = Counter({"or": 38, "chor": 12, "cthor": 5, "shor": 4, "sor": 4, "schor": 1, "dshor": 1, "qotor": 1, "tchor": 1})
    if len(chor_pairs) != 67 or Counter(str(row["head_surface"]) for row in chor_pairs) != expected_chor:
        raise AssertionError("chor value-pair census changed")
    if len(h_triples) != 12 or Counter(str(row["head_id"]) for row in h_triples) != Counter({"H1": 5, "H2": 5, "H4": 2}):
        raise AssertionError("H-head X-daiin census changed")
    if [(row["locus"], row["field_head_surface"]) for row in value_grid] != [("f22r.4", "ofchy"), ("f22r.4", "schor"), ("f22r.5", "ol"), ("f22r.5", "dar")]:
        raise AssertionError("f22 value grid changed")
    if len(schor_held) != 1 or len(schor_adjudication) != 1 or len(schor_anchors) != 2:
        raise AssertionError("schor provenance rows changed")
    if schor_adjudication[0]["w23_body_decision"] != "CONTRADICTED_FAMILY_TRANSFER":
        raise AssertionError("schor failed transfer not preserved")
    if len(exact_chor_phrases) != 5 or len(ofchedy) != 1:
        raise AssertionError("whole-analogy provenance changed")
    if len(cfhy) != 6 or Counter(str(row["line_position"]) for row in cfhy) != Counter({"MIDDLE": 5, "LAST": 1}):
        raise AssertionError("cfhy exact geometry changed")
    if any(int(row["right_is_daiin"]) or str(row["paragraph_end_line"]) == "1" for row in cfhy):
        raise AssertionError("cfhy transition evidence changed")
    if env["guard"] != {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}:
        raise AssertionError("guarded context changed")
    if any(str(row["page"]).startswith("f84") for row in targets + ofch + fchy + chor_pairs + h_triples + reader + cfhy):
        raise AssertionError("sealed page entered GDT765")

    tables: tuple[list[dict[str, object]], ...] = (
        targets, audit, ofch, fchy, profiles, chor_pairs, h_triples, value_grid,
        hypotheses, dictionary, renderers, reader, cfhy, history,
    )
    for name, rows in zip(OUTPUT_NAMES[:-1], tables):
        if not rows:
            raise AssertionError(f"empty output: {name}")
        write_tsv(output_dir / name, rows, list(rows[0]))

    result = {
        "schema": "GDT765_RESULT_V1",
        "status": STATUS,
        "scope": {
            "target_exact_occurrences": len(targets),
            "target_pages": len({str(row["page"]) for row in targets}),
            "ofch_prefix_exact_occurrences": len(ofch),
            "fchy_suffix_exact_occurrences": len(fchy),
            "chor_value_pairs": len(chor_pairs),
            "h_head_x_daiin_triples": len(h_triples),
            "f22r_value_grid_fields": len(value_grid),
            "cfhy_transition_occurrences": len(cfhy),
            "historical_comparators": len(history),
        },
        "ofchy_result": {
            "selected_role": "LEARNED_DRUG_OR_PREPARATION_HEAD",
            "portable_default_de": defaults["ofchy"]["portable_default_de"],
            "bold_concrete_default_de": defaults["ofchy"]["bold_concrete_default_de"],
            "role_confidence": defaults["ofchy"]["role_confidence"],
            "identity_confidence": defaults["ofchy"]["identity_confidence"],
            "exact_specification_frames": 3,
            "quality_index_rival": "DOWNRANKED_BY_TWO_STACKED_OR_REDUNDANT_TAILS",
        },
        "schor_result": {
            "selected_role": "DRUG_OR_PLANT_PART_ITEM_HEAD",
            "portable_default_de": defaults["schor"]["portable_default_de"],
            "bold_concrete_default_de": defaults["schor"]["bold_concrete_default_de"],
            "role_confidence": defaults["schor"]["role_confidence"],
            "identity_confidence": defaults["schor"]["identity_confidence"],
            "failed_generic_body_transfer_preserved": True,
            "specific_flower_head_basis": "CHOR_REPRODUCTIVE_PART_C1_NOT_S_INITIAL",
        },
        "f22r4_bold_working_translation_de": reader[0]["bold_line_renderer_de"],
        "guard": {"inherited_token_query": env["guard"]},
        "claim_boundary": {
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
            "confirmed_substances": 0,
            "confirmed_units": 0,
            "component_values": 0,
            "new_pages": 0,
            "new_images": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
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
