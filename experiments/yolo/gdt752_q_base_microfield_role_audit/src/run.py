#!/usr/bin/env python3
"""Audit q/base and non-q direct pairs with independent outer microfields."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import subprocess
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
BASE_REL = Path("experiments/yolo/gdt752_q_base_microfield_role_audit")
EXP = ROOT / BASE_REL
DEFAULT_ARTIFACTS = EXP / "artifacts"
G751_RUN_REL = Path("experiments/yolo/gdt751_q_base_carrier_shell_audit/src/run.py")
G751_Q_CONTACT_REL = Path(
    "experiments/yolo/gdt751_q_base_carrier_shell_audit/artifacts/"
    "DIRECT_Q_BASE_CONTACTS.tsv"
)
G751_CONTROL_REL = Path(
    "experiments/yolo/gdt751_q_base_carrier_shell_audit/artifacts/"
    "NONQ_PREFIX_160_CONTROL_DECK.tsv"
)
G751_ENRICHED_REL = Path(
    "experiments/yolo/gdt751_q_base_carrier_shell_audit/artifacts/"
    "OKEEY_10_CARRIER_ENRICHED_CARDS.tsv"
)
G744_RUN_REL = Path(
    "experiments/yolo/gdt744_historical_microfield_channel_bridge/src/run.py"
)
OUTPUT_NAMES = (
    "Q_44_OUTER_MICROFIELD_AUDIT.tsv",
    "CONTROL_42_OUTER_MICROFIELD_AUDIT.tsv",
    "SIDE_ROLE_GROUP_COMPARISON.tsv",
    "Q_PAIR_TYPE_ROLE_CENSUS.tsv",
    "OKEEY_13_LOCAL_CARRIER_REVIEW.tsv",
    "GDT752_Q_BASE_MICROFIELD_READER.md",
    "GDT752_GDT388_SIDE_ROLE_EDGE_PACKET.tsv",
    "GDT752_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__44_Q_CONTACTS_12_PAIRS__42_NONQ_CONTROLS_26_PAIRS__"
    "27_Q_28_CONTROL_COMPLETE_FIELDS__ZERO_Q_EXACT_ROLE_SPLITS__"
    "ONE_CONTROL_REVERSE__ONE_Q_SYMMETRIC_AMBIGUOUS_FIELD__"
    "TEN_OKEEY_PREPARATION_CARDS_HYPOTHESIS_ONLY__HOT_END_RETAINED__"
    "ZERO_Q_COMPONENT_EXPORT__NO_NEW_PAGE"
)
QUALITY_STAGE = {
    "HOT", "COLD", "DRY", "MOIST", "BEGIN_STAGE", "MIDDLE_STAGE",
    "END_STAGE", "LEVEL_II", "LEVEL_III",
}
CARRIERS = {"INGREDIENT", "MATERIAL", "PREPARATION", "PART"}
AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "CLOSE", "PASS", "BEGIN_STAGE",
    "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g751 = load_module("gdt751_builder_for_gdt752", ROOT / G751_RUN_REL)
g744 = load_module("gdt744_builder_for_gdt752", ROOT / G744_RUN_REL)


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def joined(values: Iterable[str]) -> str:
    chosen = set(values)
    return "|".join(axis for axis in AXIS_ORDER if axis in chosen) or "NONE"


def clean_cell(
    context: object, locus: str, ordinal: int
) -> tuple[dict[str, str], dict[str, str], set[str]]:
    line = context.by_line[locus]
    token = line[ordinal - 1]
    cell = context.cells[(locus, ordinal)]
    if token["eva"] != cell["surface"]:
        raise AssertionError(f"raw/cache mismatch at {locus}:{ordinal}")
    exact = context.exact[(locus, int(token["token_index"]))]
    axes = set(g751.g750.g749.g746.clean_axes(cell, exact, context.patterns))
    return token, cell, axes


def outer_field(
    context: object,
    rules: list[dict[str, str]],
    locus: str,
    target_ordinal: int,
    partner_ordinal: int,
    pair_surfaces: set[str],
) -> dict[str, object]:
    line = context.by_line[locus]
    direction = -1 if partner_ordinal > target_ordinal else 1
    side = "L" if direction == -1 else "R"
    span: list[dict[str, object]] = []
    boundary = "RADIUS5_CENSORED"
    for distance in range(1, 6):
        ordinal = target_ordinal + direction * distance
        if not 1 <= ordinal <= len(line):
            boundary = f"LINE_EDGE_AFTER_R{distance - 1}"
            break
        token, cell, axes = clean_cell(context, locus, ordinal)
        surface = token["eva"]
        if surface in pair_surfaces:
            boundary = f"PAIR_SURFACE_BEFORE_R{distance}"
            break
        if g751.g750.g749.g746.g745.g739.strict_initial_head(surface):
            boundary = f"STRICT_INITIAL_BEFORE_R{distance}"
            break
        if direction == -1 and "CLOSE" in axes:
            boundary = f"PRIOR_CLOSE_BEFORE_R{distance}"
            break
        span.append({
            "ordinal": ordinal,
            "distance": distance,
            "surface": surface,
            "semantic": cell["v99r7_semantic_value_de"],
            "axes": axes,
            "reader_exact": int(
                context.exact[(locus, int(token["token_index"]))]
            ),
            "unknown": int(cell["unknown_v99r7"]),
            "confidence": cell["gdt734_confidence_level"],
        })
        if direction == 1 and "CLOSE" in axes:
            boundary = f"CURRENT_CLOSE_INCLUDED_R{distance}"
            break

    anchors = [item for item in span if item["axes"]]
    tags = {axis for item in anchors for axis in item["axes"]}
    channel = g744.channel_for(tags, rules)
    evidence = " || ".join(
        f"{side}{item['distance']} {item['surface']}={item['semantic']}"
        f" [{joined(item['axes'])};{item['confidence']}]"
        for item in anchors
    ) or "NONE"
    return {
        "outer_side": side,
        "outer_extent": len(span),
        "outer_boundary_reason": boundary,
        "outer_boundary_complete": int(not boundary.startswith("RADIUS5")),
        "outer_anchor_count": len(anchors),
        "outer_anchor_surfaces": "|".join(
            str(item["surface"]) for item in anchors
        ) or "NONE",
        "outer_anchor_tags": joined(tags),
        "outer_anchor_evidence": evidence,
        "outer_field_channel": channel,
        "outer_slot_class": g744.content_slot_class(channel, tags),
        "outer_slot_label_de": g744.slot_label_de(channel, tags),
        "outer_quality_stage_support": int(bool(tags & QUALITY_STAGE)),
        "outer_preparation_support": int("PREPARATION" in tags),
        "outer_carrier_support": int(bool(tags & CARRIERS)),
        "outer_unknown_count": sum(int(item["unknown"]) for item in span),
    }


def evidence_status(
    prefix_field: dict[str, object], base_field: dict[str, object]
) -> str:
    hypothesis = bool(
        prefix_field["outer_quality_stage_support"]
        and base_field["outer_preparation_support"]
    )
    reverse = bool(
        base_field["outer_quality_stage_support"]
        and prefix_field["outer_preparation_support"]
    )
    if hypothesis and reverse:
        return "AMBIGUOUS_BOTH_EXACT_SPLITS"
    if hypothesis:
        return "SUPPORT_PREFIX_QUALITY_BASE_PREPARATION"
    if reverse:
        return "REVERSE_PREFIX_PREPARATION_BASE_QUALITY"
    partial_h = bool(
        prefix_field["outer_quality_stage_support"]
        or base_field["outer_preparation_support"]
    )
    partial_r = bool(
        base_field["outer_quality_stage_support"]
        or prefix_field["outer_preparation_support"]
    )
    if partial_h and partial_r:
        return "MIXED_PARTIAL"
    if partial_h:
        return "PARTIAL_HYPOTHESIS_SIDE"
    if partial_r:
        return "PARTIAL_REVERSE_SIDE"
    return "NO_INDEPENDENT_SIDE_SIGNAL"


def audit_contact(
    contact_id: str,
    group: str,
    pair_id: str,
    prefix_character: str,
    prefix_surface: str,
    base_surface: str,
    locus: str,
    prefix_ordinal: int,
    base_ordinal: int,
    page: str,
    physical_folio: str,
    written_line: str,
    context: object,
    rules: list[dict[str, str]],
) -> dict[str, object]:
    pair_surfaces = {prefix_surface, base_surface}
    prefix_field = outer_field(
        context, rules, locus, prefix_ordinal, base_ordinal, pair_surfaces
    )
    base_field = outer_field(
        context, rules, locus, base_ordinal, prefix_ordinal, pair_surfaces
    )
    status = evidence_status(prefix_field, base_field)
    complete = int(
        prefix_field["outer_boundary_complete"]
        and base_field["outer_boundary_complete"]
    )
    raw_exact_support = int(status == "SUPPORT_PREFIX_QUALITY_BASE_PREPARATION")
    raw_exact_reverse = int(status == "REVERSE_PREFIX_PREPARATION_BASE_QUALITY")
    raw_broad_support = int(
        prefix_field["outer_quality_stage_support"]
        and base_field["outer_carrier_support"]
    )
    raw_broad_reverse = int(
        base_field["outer_quality_stage_support"]
        and prefix_field["outer_carrier_support"]
    )
    row: dict[str, object] = {
        "gdt752_contact_id": contact_id,
        "comparison_group": group,
        "pair_id": pair_id,
        "prefix_character": prefix_character,
        "prefix_surface": prefix_surface,
        "base_surface": base_surface,
        "page": page,
        "physical_folio": physical_folio,
        "locus": locus,
        "prefix_ordinal": prefix_ordinal,
        "base_ordinal": base_ordinal,
        "written_order": (
            "PREFIX_THEN_BASE" if prefix_ordinal < base_ordinal
            else "BASE_THEN_PREFIX"
        ),
        "written_line_eva": written_line,
    }
    for label, field in (("prefix", prefix_field), ("base", base_field)):
        row.update({f"{label}_{key}": value for key, value in field.items()})
    row.update({
        "both_outer_boundaries_complete": complete,
        "raw_exact_role_split_support": raw_exact_support,
        "raw_exact_role_split_reverse": raw_exact_reverse,
        "raw_broad_role_split_support": raw_broad_support,
        "raw_broad_role_split_reverse": raw_broad_reverse,
        "exact_role_split_support": complete * raw_exact_support,
        "exact_role_split_reverse": complete * raw_exact_reverse,
        "broad_role_split_support": complete * raw_broad_support,
        "broad_role_split_reverse": complete * raw_broad_reverse,
        "independent_side_evidence_status": status,
        "complete_field_decision": (
            status if complete else f"CENSORED__{status}"
        ),
        "working_pair_render_de": (
            f"{prefix_surface}: äußeres Feld {prefix_field['outer_field_channel']}; "
            f"{base_surface}: äußeres Feld {base_field['outer_field_channel']}"
        ),
        "literal_identity": "OPEN",
        "confirmed_lexeme": 0,
        "component_export_credit": 0,
    })
    return row


def contact_fields() -> list[str]:
    fields = [
        "gdt752_contact_id", "comparison_group", "pair_id",
        "prefix_character", "prefix_surface", "base_surface", "page",
        "physical_folio", "locus", "prefix_ordinal", "base_ordinal",
        "written_order", "written_line_eva",
    ]
    side_fields = [
        "outer_side", "outer_extent", "outer_boundary_reason",
        "outer_boundary_complete", "outer_anchor_count",
        "outer_anchor_surfaces", "outer_anchor_tags",
        "outer_anchor_evidence", "outer_field_channel", "outer_slot_class",
        "outer_slot_label_de", "outer_quality_stage_support",
        "outer_preparation_support", "outer_carrier_support",
        "outer_unknown_count",
    ]
    for label in ("prefix", "base"):
        fields.extend(f"{label}_{name}" for name in side_fields)
    fields.extend([
        "both_outer_boundaries_complete", "raw_exact_role_split_support",
        "raw_exact_role_split_reverse", "raw_broad_role_split_support",
        "raw_broad_role_split_reverse", "exact_role_split_support",
        "exact_role_split_reverse", "broad_role_split_support",
        "broad_role_split_reverse", "independent_side_evidence_status",
        "complete_field_decision", "working_pair_render_de", "literal_identity", "confirmed_lexeme",
        "component_export_credit",
    ])
    return fields


def group_summary(group: str, rows: list[dict[str, object]]) -> dict[str, object]:
    complete = [row for row in rows if int(row["both_outer_boundaries_complete"])]
    return {
        "comparison_group": group,
        "contacts": len(rows),
        "pair_types": len({str(row["pair_id"]) for row in rows}),
        "pages": len({str(row["page"]) for row in rows}),
        "both_outer_boundaries_complete": len(complete),
        "prefix_outer_anchor_present": sum(int(row["prefix_outer_anchor_count"]) > 0 for row in rows),
        "base_outer_anchor_present": sum(int(row["base_outer_anchor_count"]) > 0 for row in rows),
        "both_outer_anchors_present": sum(
            int(row["prefix_outer_anchor_count"]) > 0
            and int(row["base_outer_anchor_count"]) > 0 for row in rows
        ),
        "raw_exact_role_split_support": sum(int(row["raw_exact_role_split_support"]) for row in rows),
        "raw_exact_role_split_reverse": sum(int(row["raw_exact_role_split_reverse"]) for row in rows),
        "raw_broad_role_split_support": sum(int(row["raw_broad_role_split_support"]) for row in rows),
        "raw_broad_role_split_reverse": sum(int(row["raw_broad_role_split_reverse"]) for row in rows),
        "exact_role_split_support": sum(int(row["exact_role_split_support"]) for row in rows),
        "exact_role_split_reverse": sum(int(row["exact_role_split_reverse"]) for row in rows),
        "broad_role_split_support": sum(int(row["broad_role_split_support"]) for row in rows),
        "broad_role_split_reverse": sum(int(row["broad_role_split_reverse"]) for row in rows),
        "status_counts": "|".join(
            f"{key}:{count}" for key, count in sorted(
                Counter(str(row["independent_side_evidence_status"]) for row in rows).items()
            )
        ),
        "prefix_channel_counts": "|".join(
            f"{key}:{count}" for key, count in sorted(
                Counter(str(row["prefix_outer_field_channel"]) for row in rows).items()
            )
        ),
        "base_channel_counts": "|".join(
            f"{key}:{count}" for key, count in sorted(
                Counter(str(row["base_outer_field_channel"]) for row in rows).items()
            )
        ),
        "literal_identity_credit": 0,
        "component_export_credit": 0,
    }


def pair_type_census(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["pair_id"])].append(row)
    output: list[dict[str, object]] = []
    for pair_id, members in sorted(grouped.items()):
        first = members[0]
        output.append({
            "pair_id": pair_id,
            "q_surface": first["prefix_surface"],
            "base_surface": first["base_surface"],
            "contacts": len(members),
            "pages": len({str(row["page"]) for row in members}),
            "written_q_then_base": sum(row["written_order"] == "PREFIX_THEN_BASE" for row in members),
            "written_base_then_q": sum(row["written_order"] == "BASE_THEN_PREFIX" for row in members),
            "raw_exact_support": sum(int(row["raw_exact_role_split_support"]) for row in members),
            "raw_exact_reverse": sum(int(row["raw_exact_role_split_reverse"]) for row in members),
            "exact_support": sum(int(row["exact_role_split_support"]) for row in members),
            "exact_reverse": sum(int(row["exact_role_split_reverse"]) for row in members),
            "broad_support": sum(int(row["broad_role_split_support"]) for row in members),
            "broad_reverse": sum(int(row["broad_role_split_reverse"]) for row in members),
            "independent_side_result": (
                "SUPPORT" if any(int(row["exact_role_split_support"]) for row in members)
                and not any(int(row["exact_role_split_reverse"]) for row in members)
                else "REVERSE" if any(int(row["exact_role_split_reverse"]) for row in members)
                and not any(int(row["exact_role_split_support"]) for row in members)
                else "MIXED" if any(
                    int(row["exact_role_split_support"]) or int(row["exact_role_split_reverse"])
                    for row in members
                ) else "NO_EXACT_SPLIT"
            ),
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def okeey_review(
    q_rows: list[dict[str, object]], enriched: list[dict[str, str]]
) -> list[dict[str, object]]:
    enriched_keys = {
        (row["locus"], int(row["token_ordinal"])): row for row in enriched
    }
    output: list[dict[str, object]] = []
    selected = [
        row for row in q_rows
        if row["prefix_surface"] == "qokeey" and row["base_surface"] == "okeey"
    ]
    for number, row in enumerate(selected, start=1):
        key = (str(row["locus"]), int(row["base_ordinal"]))
        inherited = enriched_keys.get(key)
        independent = bool(row["exact_role_split_support"])
        status = (
            "RETAIN_WITH_INDEPENDENT_OUTER_SUPPORT" if inherited and independent
            else "HOLD_MODEL_INTERNAL_NO_OUTER_SUPPORT" if inherited
            else "NO_GDT751_CARD"
        )
        output.append({
            "gdt752_okeey_review_id": f"G752-O{number:02d}",
            "gdt752_contact_id": row["gdt752_contact_id"],
            "page": row["page"],
            "locus": row["locus"],
            "okeey_ordinal": row["base_ordinal"],
            "qokeey_ordinal": row["prefix_ordinal"],
            "gdt751_card_id": inherited["gdt751_carrier_card_id"] if inherited else "NONE",
            "gdt751_working_render_de": inherited["working_render_de"] if inherited else "NONE",
            "q_outer_tags": row["prefix_outer_anchor_tags"],
            "okeey_outer_tags": row["base_outer_anchor_tags"],
            "q_outer_channel": row["prefix_outer_field_channel"],
            "okeey_outer_channel": row["base_outer_field_channel"],
            "independent_exact_role_split_support": int(independent),
            "review_decision": status,
            "current_safe_render_de": (
                inherited["working_render_de"] if inherited and independent
                else "heiß an der End-/Vollstufe; Trägerrolle offen"
                if inherited else "keine zusätzliche lokale Karte"
            ),
            "scope": "THIS_OCCURRENCE_ONLY",
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def write_reader(
    path: Path,
    groups: list[dict[str, object]],
    pair_types: list[dict[str, object]],
    okeey: list[dict[str, object]],
) -> None:
    q = next(row for row in groups if row["comparison_group"] == "Q_PREFIX")
    c = next(row for row in groups if row["comparison_group"] == "NONQ_PREFIX_CONTROL")
    lines = [
        "# GDT752 q/base outer-microfield reader", "",
        "## Fixed comparison", "",
        "| group | contacts | pair types | exact support/reverse | broad support/reverse |",
        "|---|---:|---:|---:|---:|",
        f"| q/base | {q['contacts']} | {q['pair_types']} | {q['exact_role_split_support']}/{q['exact_role_split_reverse']} | {q['broad_role_split_support']}/{q['broad_role_split_reverse']} |",
        f"| non-q control | {c['contacts']} | {c['pair_types']} | {c['exact_role_split_support']}/{c['exact_role_split_reverse']} | {c['broad_role_split_support']}/{c['broad_role_split_reverse']} |",
        "",
        "Each member is clipped away from its adjacent partner. Only exact W2/W3 complete-whole anchors on that outer side can type the local field. Pair members never anchor one another.",
        "",
        "## q/base pair types", "",
        "| q form | base | contacts | exact support | exact reverse | result |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in pair_types:
        lines.append(
            f"| `{row['q_surface']}` | `{row['base_surface']}` | {row['contacts']} | "
            f"{row['exact_support']} | {row['exact_reverse']} | {row['independent_side_result']} |"
        )
    lines.extend(["", "## `okeey` cards", ""])
    for row in okeey:
        lines.append(
            f"- `{row['locus']}:{row['okeey_ordinal']}` — {row['review_decision']}: "
            f"{row['current_safe_render_de']}"
        )
    lines.extend([
        "",
        "The one fully bounded q/base field with preparation on both outer sides is `qokeey/okeey` at `f99r.50`; both sides carry the same HOT|PREPARATION|LEVEL_II evidence, so it is symmetric rather than directional.",
        "",
        "The ten prior `okeey` preparation cards receive no independent directional outer-field support. Their HOT|END_STAGE axes remain licensed; PREPARATION stays as a background hypothesis and is no longer spoken by the current renderer.",
        "",
        "No value is assigned to EVA q or any substring. Field labels are occurrence-local working roles, not plaintext or lexemes.",
    ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def edge_packet(
    output_dir: Path, q_rows: list[dict[str, object]]
) -> dict[str, object]:
    selected = [
        row for row in q_rows
        if int(row["both_outer_boundaries_complete"])
        and row["independent_side_evidence_status"] in {
            "SUPPORT_PREFIX_QUALITY_BASE_PREPARATION",
            "REVERSE_PREFIX_PREPARATION_BASE_QUALITY",
            "AMBIGUOUS_BOTH_EXACT_SPLITS",
        }
    ]
    packet: list[dict[str, object]] = []
    for number, row in enumerate(selected, start=1):
        packet.append({
            "edge_id": f"G752E{number:03d}",
            "batch_id": "GDT752_OUTER_MICROFIELD_ROLE_SPLIT",
            "page": row["page"],
            "physical_folio": row["physical_folio"],
            "diagram_unit_id": "CACHED_TEXT_OUTER_MICROFIELD_PAIR",
            "pivot_visual_id": f"PREFIX_WHOLE_{row['prefix_surface']}",
            "pivot_locus": f"{row['locus']}@{row['prefix_ordinal']}",
            "target_visual_id": f"BASE_WHOLE_{row['base_surface']}",
            "target_locus": f"{row['locus']}@{row['base_ordinal']}",
            "relation_type": row["independent_side_evidence_status"],
            "direction_basis": "SURFACE_ROLE_NOT_WRITTEN_ORDER",
            "ownership_basis": "PAIR_PARTNER_EXCLUDED_OUTER_W2_W3_FIELDS",
            "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT752",
            "page_crop_sha256": "NONE",
            "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT752_BUILDER",
            "relation_reviewer": "PENDING_EXTERNAL",
            "relation_confidence": "EXPLORATORY_COMPLETE_PAIR_SIDE_ROLE",
            "ambiguity_state": "Q_COMPONENT_VALUE_OPEN_COMPLETE_WHOLES_ONLY",
            "formal_access_state": "FORMAL_ACCESSED",
            "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_FORMAL_CONTEXT_RELATION",
        })
    packet_path = output_dir / "GDT752_GDT388_SIDE_ROLE_EDGE_PACKET.tsv"
    fields = list(packet[0]) if packet else [
        "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
        "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
        "relation_type", "direction_basis", "ownership_basis",
        "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
        "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer",
        "relation_reviewer", "relation_confidence", "ambiguity_state",
        "formal_access_state", "fold_assignment", "eligibility_status",
    ]
    write_tsv(packet_path, packet, fields)
    command = [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    intake = json.loads(completed.stdout)
    if intake["status"] not in {"INVALID_PACKET", "NOT_SCORE_READY"}:
        raise AssertionError("unexpected score-ready side-role packet")
    (output_dir / "GDT752_GDT388_EDGE_INTAKE.json").write_text(
        json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return intake


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    context, _, line_guard = g751.load_context()
    q_source = read_tsv(ROOT / G751_Q_CONTACT_REL)
    controls = read_tsv(ROOT / G751_CONTROL_REL)
    enriched = read_tsv(ROOT / G751_ENRICHED_REL)
    rules = g744.load_channel_rules()

    q_rows: list[dict[str, object]] = []
    for number, source in enumerate(q_source, start=1):
        q_rows.append(audit_contact(
            f"G752-Q{number:03d}", "Q_PREFIX", source["pair_id"], "q",
            source["q_surface"], source["base_surface"], source["locus"],
            int(source["q_ordinal"]), int(source["base_ordinal"]), source["page"],
            source["physical_folio"], source["written_line_eva"], context, rules,
        ))

    # Materialize all and only the 42 direct contacts already counted by GDT751.
    occurrence_map: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for locus, line in context.by_line.items():
        written = " ".join(token["eva"] for token in line)
        for ordinal, token in enumerate(line, start=1):
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            occurrence_map[token["eva"]].append({
                "page": token["page"],
                "physical_folio": g751.g750.g749.g746.g745.physical_folio(token["page"]),
                "locus": locus,
                "token_ordinal": ordinal,
                "written_line_eva": written,
            })
    control_rows: list[dict[str, object]] = []
    control_number = 0
    for pair in controls:
        contacts = g751.direct_contacts(
            pair["prefix_surface"], pair["base_surface"], occurrence_map, context
        )
        if len(contacts) != int(pair["direct_contacts"]):
            raise AssertionError(f"control contact drift: {pair['pair_id']}")
        for contact in contacts:
            control_number += 1
            control_rows.append(audit_contact(
                f"G752-C{control_number:03d}", "NONQ_PREFIX_CONTROL", pair["pair_id"],
                pair["prefix_character"], pair["prefix_surface"], pair["base_surface"],
                str(contact["locus"]), int(contact["prefix_ordinal"]),
                int(contact["base_ordinal"]), str(contact["page"]),
                str(contact["physical_folio"]), str(contact["written_line_eva"]),
                context, rules,
            ))
    if len(q_rows) != 44 or len(control_rows) != 42:
        raise AssertionError("fixed 44/42 contact deck changed")

    groups = [
        group_summary("Q_PREFIX", q_rows),
        group_summary("NONQ_PREFIX_CONTROL", control_rows),
    ]
    pair_types = pair_type_census(q_rows)
    okeey = okeey_review(q_rows, enriched)
    write_tsv(output_dir / OUTPUT_NAMES[0], q_rows, contact_fields())
    write_tsv(output_dir / OUTPUT_NAMES[1], control_rows, contact_fields())
    write_tsv(output_dir / OUTPUT_NAMES[2], groups, list(groups[0]))
    write_tsv(output_dir / OUTPUT_NAMES[3], pair_types, list(pair_types[0]))
    write_tsv(output_dir / OUTPUT_NAMES[4], okeey, list(okeey[0]))
    write_reader(output_dir / OUTPUT_NAMES[5], groups, pair_types, okeey)
    intake = edge_packet(output_dir, q_rows)

    q_group, c_group = groups
    retained_okeey = sum(
        row["review_decision"] == "RETAIN_WITH_INDEPENDENT_OUTER_SUPPORT"
        for row in okeey
    )
    result = {
        "schema": "GDT752_RESULT_V1",
        "status": STATUS,
        "scope": {
            "q_contacts": len(q_rows),
            "q_pair_types": len(pair_types),
            "q_pages": len({str(row['page']) for row in q_rows}),
            "control_contacts": len(control_rows),
            "control_pair_types": len({str(row['pair_id']) for row in control_rows}),
            "control_pages": len({str(row['page']) for row in control_rows}),
            "okeey_pair_contacts": len(okeey),
            "gdt751_okeey_cards_reviewed": len(enriched),
        },
        "independent_outer_microfield_result": {
            "q_exact_support": q_group["exact_role_split_support"],
            "q_exact_reverse": q_group["exact_role_split_reverse"],
            "control_exact_support": c_group["exact_role_split_support"],
            "control_exact_reverse": c_group["exact_role_split_reverse"],
            "q_raw_exact_support": q_group["raw_exact_role_split_support"],
            "q_raw_exact_reverse": q_group["raw_exact_role_split_reverse"],
            "control_raw_exact_support": c_group["raw_exact_role_split_support"],
            "control_raw_exact_reverse": c_group["raw_exact_role_split_reverse"],
            "q_broad_support": q_group["broad_role_split_support"],
            "q_broad_reverse": q_group["broad_role_split_reverse"],
            "control_broad_support": c_group["broad_role_split_support"],
            "control_broad_reverse": c_group["broad_role_split_reverse"],
            "okeey_cards_with_independent_outer_support": retained_okeey,
            "q_specific_quality_vs_base_preparation_split_supported": False,
            "only_complete_q_exact_pattern": "SYMMETRIC_BOTH_SIDES_AT_f99r.50_NOT_DIRECTIONAL",
            "censored_directional_lead": "qokeol_okeol_f99v.22_HOLD_ONLY",
        },
        "renderer_decision": {
            "gdt751_okeey_preparation_cards_retained_as_spoken": 0,
            "gdt751_okeey_preparation_cards_demoted_to_hypothesis_only": len(enriched),
            "gdt750_hot_end_occurrence_cards_retained": len(enriched),
            "current_render_de": "heiß an der End-/Vollstufe; Trägerrolle offen",
            "weak_complete_pair_relation_retained": True,
            "q_component_value_exported": False,
        },
        "edge_intake": intake,
        "guard": line_guard,
        "claim_boundary": {
            "q_component_export_credit": 0,
            "confirmed_lexemes": 0,
            "plaintext_clauses": 0,
            "literal_preparations": 0,
            "new_pages": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps({
        "status": result["status"],
        "scope": result["scope"],
        "result": result["independent_outer_microfield_result"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
