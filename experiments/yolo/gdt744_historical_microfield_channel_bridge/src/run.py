#!/usr/bin/env python3
"""Build boundary-clipped historical microfield channel readings for 202 targets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
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
BASE_REL = Path("experiments/yolo/gdt744_historical_microfield_channel_bridge")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

G735_RESULT_REL = Path(
    "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/RESULT.json"
)
G735_SLOT_REL = Path(
    "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_SLOT_CENSUS.tsv"
)
G739_WINDOW_REL = Path(
    "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/artifacts/"
    "WINDOW_202_TOKEN_AUDIT.tsv"
)
G743_PATCH_REL = Path(
    "experiments/yolo/gdt743_r2_run_intersection_adjudication/artifacts/"
    "TARGET_202_RENDERER_PATCH_V5.tsv"
)

QUALITY = {"HOT", "COLD", "DRY", "MOIST"}
CARRIERS = {"INGREDIENT", "MATERIAL", "PREPARATION", "PART"}
STRONG_W23 = {"W2_PROVISIONAL_WORKING", "W3_SOLID_WORKING_THEORY"}
STRONG_W3 = {"W3_SOLID_WORKING_THEORY"}
CHANNEL_ORDER = (
    "PRESCRIPTIVE_RECIPE",
    "PRESCRIPTIVE_PROCESS",
    "DESCRIPTIVE_MATERIA",
    "DESCRIPTIVE_QUALITY",
    "QUANTITY_OR_PART",
    "MATERIA_OR_INGREDIENT",
    "OPEN",
)
STATUS = (
    "PARTIAL__16_COMPLETE_RECURRENT_EXACT_WHOLE_CHANNEL_TEMPLATES__"
    "80_TEMPLATE_BACKED_FIELDS__47_COMPLETE_PLUS_33_RADIUS_CENSORED__"
    "69_OF_80_W3_TEMPLATE_RETAINED__67_SAME_CHANNEL__"
    "42_UNRESOLVED_CONTENT_SLOT_CELLS__"
    "TARGET_WHOLES_REMAIN_LEVEL_OR_STATE_FIELDS__ZERO_LEXEMES__NO_NEW_PAGE"
)
OUTPUT_NAMES = (
    "MICROFIELD_202_CHANNEL_DISPATCH.tsv",
    "FORM_CHANNEL_RECURRENCE_CENSUS.tsv",
    "UNRESOLVED_CONTENT_SLOT_CANDIDATES.tsv",
    "PASSAGE_20_MICROFIELD_READER.tsv",
    "GDT744_GDT388_MICROFIELD_EDGE_PACKET.tsv",
    "GDT744_GDT388_EDGE_INTAKE.json",
    "GDT744_HISTORICAL_MICROFIELD_READER.md",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=names,
            delimiter="\t",
            lineterminator="\n",
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


def values(value: object) -> set[str]:
    text = str(value)
    if text in {"", "NONE", "NA", "OPEN", "NOT_APPLICABLE"}:
        return set()
    return set(text.split("|"))


def joined(items: Iterable[str], order: Iterable[str] | None = None) -> str:
    members = set(items)
    selected = sorted(members) if order is None else [item for item in order if item in members]
    return "|".join(selected) or "NONE"


def load_channel_rules() -> list[dict[str, str]]:
    rules = read_tsv(SRC / "FIELD_CHANNEL_RULES.tsv")
    if [int(row["precedence"]) for row in rules] != list(range(1, 8)):
        raise AssertionError("channel rule precedence must be exactly 1..7")
    if tuple(row["channel"] for row in rules) != CHANNEL_ORDER:
        raise AssertionError("channel rule order changed")
    return rules


def load_whole_supplements() -> dict[str, dict[str, str]]:
    rows = read_tsv(SRC / "WHOLE_HISTORICAL_ROLE_SUPPLEMENTS.tsv")
    supplements = {row["surface"]: row for row in rows}
    if set(supplements) != {"olor", "qoly"} or len(rows) != 2:
        raise AssertionError("whole-role supplement deck changed")
    if any(row["lexeme_credit"] != "0" for row in rows):
        raise AssertionError("whole-role supplement grants lexeme credit")
    return supplements


def effective_tags(
    row: dict[str, str], supplements: dict[str, dict[str, str]]
) -> set[str]:
    tags = values(row["axis_tags"])
    spec = supplements.get(row["neighbor_surface"])
    if spec is None:
        return tags
    if (
        row["neighbor_semantic_value_de"] != spec["expected_semantic_value_de"]
        or row["neighbor_confidence_level"] != spec["expected_confidence_level"]
    ):
        raise AssertionError(f"whole-role supplement input drift: {row['neighbor_surface']}")
    return tags | values(spec["added_field_tags"])


def channel_for(tags: set[str], rules: list[dict[str, str]]) -> str:
    for rule in rules:
        all_required = values(rule["required_all"])
        any_one = values(rule["required_any_1"])
        any_two = values(rule["required_any_2"])
        if not all_required <= tags:
            continue
        if any_one and not any_one & tags:
            continue
        if any_two and not any_two & tags:
            continue
        return rule["channel"]
    raise AssertionError("OPEN default rule missing")


def strong_anchor(row: dict[str, str], confidence: set[str]) -> bool:
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


def unresolved_candidate(row: dict[str, str]) -> bool:
    return bool(
        row["neighbor_unknown_v99r7"] == "1"
        and row["neighbor_reader_exact"] == "1"
        and row["strict_initial_head_neighbor"] == "0"
        and row["another_gdt738_target"] == "0"
        and row["retired_patient_words"] == "NONE"
        and row["head_or_body_lexeme_credit"] == "0"
        and row["component_export_credit"] == "0"
    )


def side_span(
    window: dict[tuple[str, int], dict[str, str]], side: str, radius: int = 5
) -> tuple[list[dict[str, str]], str]:
    output: list[dict[str, str]] = []
    for distance in range(1, radius + 1):
        row = window.get((side, distance))
        if row is None:
            return output, f"LINE_EDGE_AFTER_R{distance - 1}"
        tags = values(row["axis_tags"])
        if row["another_gdt738_target"] == "1":
            return output, f"NEXT_TARGET_BEFORE_R{distance}"
        if row["strict_initial_head_neighbor"] == "1":
            return output, f"STRICT_INITIAL_BEFORE_R{distance}"
        if side == "L" and "CLOSE" in tags:
            return output, f"PRIOR_CLOSE_BEFORE_R{distance}"
        output.append(row)
        if side == "R" and "CLOSE" in tags:
            return output, f"CURRENT_CLOSE_INCLUDED_R{distance}"
    return output, f"RADIUS{radius}_CENSORED"


def clipped_span(
    window: dict[tuple[str, int], dict[str, str]], radius: int = 5
) -> tuple[list[dict[str, str]], str, str]:
    left, left_reason = side_span(window, "L", radius)
    right, right_reason = side_span(window, "R", radius)
    return left + right, left_reason, right_reason


def unclipped_span(
    window: dict[tuple[str, int], dict[str, str]], radius: int = 5
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for side in ("L", "R"):
        for distance in range(1, radius + 1):
            row = window.get((side, distance))
            if row is None:
                break
            output.append(row)
    return output


def anchor_bundle(
    span: list[dict[str, str]], confidence: set[str],
    supplements: dict[str, dict[str, str]],
) -> tuple[list[dict[str, str]], set[str], str, str]:
    anchors = [row for row in span if strong_anchor(row, confidence)]
    tags: set[str] = set()
    for row in anchors:
        tags.update(effective_tags(row, supplements))
    ordered = sorted(anchors, key=lambda row: int(row["neighbor_ordinal"]))
    signature = "|".join(
        f"{row['side']}{row['distance']}@{row['neighbor_ordinal']}:"
        f"{row['neighbor_surface']}:{joined(effective_tags(row, supplements))}"
        for row in ordered
    ) or "NONE"
    evidence = " || ".join(
        f"{row['side']}{row['distance']} {row['neighbor_surface']}="
        f"{row['neighbor_semantic_value_de']} [{joined(effective_tags(row, supplements))};"
        f"{row['neighbor_confidence_level']}]"
        for row in ordered
    ) or "NONE"
    return anchors, tags, signature, evidence


def complete_boundary(left_reason: str, right_reason: str) -> bool:
    return not left_reason.startswith("RADIUS") and not right_reason.startswith("RADIUS")


def recurrence_classes(
    rows: list[dict[str, object]], channel_field: str, signature_field: str,
    complete_only: bool,
) -> tuple[dict[tuple[str, str], list[dict[str, object]]], set[tuple[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if complete_only and not int(row["boundary_complete"]):
            continue
        grouped[(str(row["surface"]), str(row[channel_field]))].append(row)
    licensed: set[tuple[str, str]] = set()
    for key, members in grouped.items():
        pages = {str(row["page"]) for row in members}
        signatures = {str(row[signature_field]) for row in members}
        if key[1] != "OPEN" and len(pages) >= 2 and len(signatures) >= 2:
            licensed.add(key)
    return grouped, licensed


def tag_de(tags: set[str], domain: str) -> str:
    if domain == "quality":
        mapping = {"HOT": "heiß", "COLD": "kalt", "DRY": "trocken", "MOIST": "feucht/eingeweicht"}
        order = ("HOT", "COLD", "DRY", "MOIST")
    elif domain == "carrier":
        mapping = {
            "INGREDIENT": "Zutatrolle", "MATERIAL": "Stoff",
            "PREPARATION": "Zubereitung", "PART": "Teil/Portion",
        }
        order = ("INGREDIENT", "MATERIAL", "PREPARATION", "PART")
    else:
        raise AssertionError(domain)
    selected = [mapping[tag] for tag in order if tag in tags]
    rendered = "+".join(selected) or "offen"
    if domain == "quality" and (
        {"HOT", "COLD"} <= tags or {"DRY", "MOIST"} <= tags
    ):
        rendered += " (konkurrierende Anker)"
    return rendered


def target_scale(row: dict[str, object]) -> str:
    family = str(row["family"])
    level = str(row["level"])
    if family == "SCALAR":
        return f"Skala/Stufe {level}"
    if family == "STATE_RESULT":
        return f"Zustands-/Resultatstufe {level}"
    return "Statusfeld"


def content_slot_class(channel: str, tags: set[str] | None = None) -> str:
    active_tags = tags or set()
    if channel in {"PRESCRIPTIVE_RECIPE", "PRESCRIPTIVE_PROCESS"}:
        if "PASS" in active_tags and "PROCESS" not in active_tags:
            return "INGREDIENT_OR_PROCESS_PASS_CONTENT"
    return {
        "DESCRIPTIVE_MATERIA": "LEMMA_OR_DESCRIPTIVE_CONTENT",
        "DESCRIPTIVE_QUALITY": "LEMMA_OR_DESCRIPTIVE_CONTENT",
        "PRESCRIPTIVE_RECIPE": "INGREDIENT_OR_COMMAND_CONTENT",
        "PRESCRIPTIVE_PROCESS": "INGREDIENT_OR_PROCESS_COMPLEMENT",
        "QUANTITY_OR_PART": "QUANTITY_REFERENT_OR_PART_NAME",
        "MATERIA_OR_INGREDIENT": "LEMMA_OR_INGREDIENT",
        "OPEN": "UNASSIGNED",
    }[channel]


def slot_label_de(channel: str, tags: set[str] | None = None) -> str:
    active_tags = tags or set()
    if channel in {"PRESCRIPTIVE_RECIPE", "PRESCRIPTIVE_PROCESS"}:
        if "PASS" in active_tags and "PROCESS" not in active_tags:
            return "Zutat-/Verarbeitungsinhalt offen"
    return {
        "DESCRIPTIVE_MATERIA": "Lemma-/Beschreibungsinhalt offen",
        "DESCRIPTIVE_QUALITY": "Lemma-/Beschreibungsinhalt offen",
        "PRESCRIPTIVE_RECIPE": "Zutat-/Anweisungsinhalt offen",
        "PRESCRIPTIVE_PROCESS": "Stoff-/Prozessergänzung offen",
        "QUANTITY_OR_PART": "Mengenbezug-/Teilname offen",
        "MATERIA_OR_INGREDIENT": "Lemma-/Zutatinhalt offen",
        "OPEN": "Inhaltsrolle offen",
    }[channel]


def field_card(row: dict[str, object]) -> str:
    channel = str(row["raw_field_channel"])
    tags = values(row["strong_anchor_tags"])
    quality = tag_de(tags, "quality")
    carrier = tag_de(tags, "carrier")
    scale = target_scale(row)
    amount = "vorhanden" if "AMOUNT" in tags else "nicht belegt"
    amount_note = "; Mengenmarker=vorhanden" if "AMOUNT" in tags else ""
    if channel == "DESCRIPTIVE_MATERIA":
        body = (
            f"Materia-medica-Beschreibung: Lemma offen; Träger={carrier}; "
            f"Qualität={quality}{amount_note}; {scale}"
        )
    elif channel == "DESCRIPTIVE_QUALITY":
        body = (
            f"Materia-medica-Beschreibung: Lemma und Träger offen; "
            f"Qualität={quality}{amount_note}; {scale}"
        )
    elif channel == "PRESCRIPTIVE_RECIPE":
        if "PROCESS" in tags:
            body = (
                f"Rezeptanweisung: Zutat offen; Vorgang belegt; Träger={carrier}; "
                f"Mengenmarker={amount}; Bedingung={quality}; Ziel={scale}"
            )
        else:
            body = (
                f"Rezept-/Verarbeitungsfeld: Zutat offen; Verarbeitungsabschnitt belegt; "
                f"Träger={carrier}; Mengenmarker={amount}; Bedingung={quality}; Ziel={scale}"
            )
    elif channel == "PRESCRIPTIVE_PROCESS":
        if "PROCESS" in tags:
            body = (
                f"Rezeptanweisung: Stoff offen; Vorgang belegt; "
                f"Bedingung={quality}; Ziel={scale}"
            )
        else:
            body = (
                f"Verarbeitungsfeld: Stoff offen; Prozessabschnitt belegt; "
                f"Bedingung={quality}; Ziel={scale}"
            )
    elif channel == "QUANTITY_OR_PART":
        markers = "+".join(
            label for tag, label in (("AMOUNT", "Menge"), ("PART", "Teil/Portion"))
            if tag in tags
        ) or "offen"
        body = (
            f"Mengen-/Teilfeld: Bezugsstoff offen; Marker={markers}; "
            f"Träger={carrier}; Wert={scale}"
        )
    elif channel == "MATERIA_OR_INGREDIENT":
        body = (
            f"Stoff-/Zutatfeld: Beschreibungs- oder Rezeptkanal offen; "
            f"Träger={carrier}; {scale}"
        )
    else:
        return "Mikrofeld: Kanal offen; keine starken historischen Feldanker"

    tier = str(row["field_confidence_tier"])
    evidence = {
        "F3_RECURRENT_COMPLETE_CONTEXT": "voll begrenzt und auf mehreren Seiten wiederholt",
        "F2_RECURRENT_TEMPLATE_PARTIAL_CONTEXT": "voll begrenzte Vorlage wiederholt; dieser Feldrand >R5 offen",
        "F1_RECURRENT_WINDOW_ONLY": "nur im Radius-5-Fenster wiederholt",
        "F1_SINGLE_CONTEXT": "Einzelkontext",
    }[tier]
    prefix = "" if tier.startswith(("F2", "F3")) else "VORLÄUFIG: "
    return f"{prefix}{body}; Evidenz={evidence}"


def physical_folio(page: str) -> str:
    if page.startswith("fRos"):
        return "fRos"
    match = re.match(r"^(f\d+)", page)
    if not match:
        raise AssertionError(f"invalid page: {page}")
    return match.group(1)


def build_initial_fields(
    patches: list[dict[str, str]], windows: list[dict[str, str]],
    rules: list[dict[str, str]], supplements: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    by_patch: dict[str, dict[tuple[str, int], dict[str, str]]] = defaultdict(dict)
    for window_row in windows:
        coordinate = (window_row["side"], int(window_row["distance"]))
        if coordinate in by_patch[window_row["patch_id"]]:
            raise AssertionError("duplicate target-window coordinate")
        by_patch[window_row["patch_id"]][coordinate] = window_row

    output: list[dict[str, object]] = []
    for number, patch in enumerate(patches, start=1):
        window = by_patch[patch["patch_id"]]
        span, left_reason, right_reason = clipped_span(window, 5)
        r2_span, _, _ = clipped_span(window, 2)
        raw_span = unclipped_span(window, 5)
        anchors, tags, signature, evidence = anchor_bundle(span, STRONG_W23, supplements)
        w3_anchors, w3_tags, w3_signature, _ = anchor_bundle(span, STRONG_W3, supplements)
        r2_anchors, r2_tags, _, _ = anchor_bundle(r2_span, STRONG_W23, supplements)
        raw_anchors, raw_tags, _, _ = anchor_bundle(raw_span, STRONG_W23, supplements)
        supplement_anchors = [
            item for item in anchors if item["neighbor_surface"] in supplements
        ]
        left_extent = max(
            (int(item["distance"]) for item in span if item["side"] == "L"), default=0
        )
        right_extent = max(
            (int(item["distance"]) for item in span if item["side"] == "R"), default=0
        )
        candidate_neighbors = [item for item in span if unresolved_candidate(item)]
        row: dict[str, object] = {
            "gdt744_field_id": f"G744-F{number:04d}",
            "gdt743_patch_id": patch["gdt743_patch_id"],
            "gdt739_dispatch_id": patch["gdt739_dispatch_id"],
            "patch_id": patch["patch_id"],
            "occurrence_id": patch["occurrence_id"],
            "page": patch["page"],
            "locus": patch["locus"],
            "target_ordinal": patch["token_ordinal"],
            "surface": patch["surface"],
            "body": patch["body"],
            "opaque_head_id": patch["opaque_head_id"],
            "line_position": patch["line_position"],
            "family": patch["family"],
            "level": patch["level"],
            "left_extent": left_extent,
            "right_extent": right_extent,
            "bounded_span_tokens": len(span),
            "left_boundary_reason": left_reason,
            "right_boundary_reason": right_reason,
            "boundary_complete": int(complete_boundary(left_reason, right_reason)),
            "strong_anchor_count": len(anchors),
            "strong_anchor_surfaces": joined(item["neighbor_surface"] for item in anchors),
            "strong_anchor_tags": joined(tags),
            "thermal_quality_conflict": int({"HOT", "COLD"} <= tags),
            "moisture_quality_conflict": int({"DRY", "MOIST"} <= tags),
            "quality_conflict": int(
                {"HOT", "COLD"} <= tags or {"DRY", "MOIST"} <= tags
            ),
            "strong_anchor_signature": signature,
            "strong_anchor_evidence": evidence,
            "supplemental_whole_role_anchor_count": len(supplement_anchors),
            "supplemental_whole_role_surfaces": joined(
                item["neighbor_surface"] for item in supplement_anchors
            ),
            "raw_field_channel": channel_for(tags, rules),
            "w3_only_anchor_count": len(w3_anchors),
            "w3_only_anchor_signature": w3_signature,
            "w3_only_field_channel": channel_for(w3_tags, rules),
            "r2_anchor_count": len(r2_anchors),
            "r2_field_channel": channel_for(r2_tags, rules),
            "unclipped_anchor_count": len(raw_anchors),
            "unclipped_field_channel": channel_for(raw_tags, rules),
            "unresolved_candidate_count": len(candidate_neighbors),
            "unresolved_candidate_surfaces": joined(
                item["neighbor_surface"] for item in candidate_neighbors
            ),
            "gdt743_dimension_dispatch": patch["gdt743_dimension_dispatch"],
            "gdt743_carrier_dispatch": patch["gdt743_carrier_dispatch"],
            "gdt743_working_render_de": patch["gdt743_working_render_de"],
            "gdt743_specific_local_dispatch": patch["specific_local_dispatch_gdt743"],
            "field_scope": "EXACT_COMPLETE_TARGET_WHOLE_AT_ENUMERATED_CACHED_OCCURRENCE",
            "literal_lexeme_claimed": 0,
            "plaintext_clause_claimed": 0,
            "head_or_body_lexeme_credit": 0,
            "component_export_credit": 0,
            "unseen_form_export": 0,
            "_span": span,
            "_anchors": anchors,
        }
        output.append(row)
    return output


def decorate_fields(
    rows: list[dict[str, object]], rules: list[dict[str, str]]
) -> tuple[list[dict[str, object]], set[tuple[str, str]], set[tuple[str, str]], set[tuple[str, str]]]:
    all_groups, all_classes = recurrence_classes(
        rows, "raw_field_channel", "strong_anchor_signature", False
    )
    complete_groups, complete_classes = recurrence_classes(
        rows, "raw_field_channel", "strong_anchor_signature", True
    )
    _, w3_classes = recurrence_classes(
        rows, "w3_only_field_channel", "w3_only_anchor_signature", True
    )
    rule_map = {rule["channel"]: rule for rule in rules}
    for row in rows:
        key = (str(row["surface"]), str(row["raw_field_channel"]))
        all_members = all_groups[key]
        complete_members = complete_groups.get(key, [])
        if key in complete_classes:
            tier = (
                "F3_RECURRENT_COMPLETE_CONTEXT"
                if int(row["boundary_complete"])
                else "F2_RECURRENT_TEMPLATE_PARTIAL_CONTEXT"
            )
        elif key in all_classes:
            tier = "F1_RECURRENT_WINDOW_ONLY"
        elif row["raw_field_channel"] != "OPEN":
            tier = "F1_SINGLE_CONTEXT"
        else:
            tier = "F0_OPEN"
        w3_key = (str(row["surface"]), str(row["w3_only_field_channel"]))
        row.update({
            "surface_channel_occurrences": len(all_members),
            "surface_channel_pages": len({str(member["page"]) for member in all_members}),
            "surface_channel_anchor_signatures": len({str(member["strong_anchor_signature"]) for member in all_members}),
            "complete_surface_channel_occurrences": len(complete_members),
            "complete_surface_channel_pages": len({str(member["page"]) for member in complete_members}),
            "complete_surface_channel_anchor_signatures": len({str(member["strong_anchor_signature"]) for member in complete_members}),
            "window_recurrence_gate": int(key in all_classes),
            "complete_template_gate": int(key in complete_classes),
            "field_confidence_tier": tier,
            "template_backed_field_reading": int(key in complete_classes),
            "exploratory_field_candidate": int(row["raw_field_channel"] != "OPEN" and key not in complete_classes),
            "w3_only_complete_template_gate": int(w3_key in w3_classes),
            "w3_only_same_channel": int(row["raw_field_channel"] == row["w3_only_field_channel"]),
            "w3_only_template_reading_retained": int(w3_key in w3_classes),
            "historical_mode": rule_map[str(row["raw_field_channel"])]["historical_mode"],
            "unresolved_content_slot_class": content_slot_class(
                str(row["raw_field_channel"]), values(row["strong_anchor_tags"])
            ),
            "unresolved_slot_label_de": slot_label_de(
                str(row["raw_field_channel"]), values(row["strong_anchor_tags"])
            ),
        })
        row["field_render_de"] = field_card(row)
        row["combined_target_field_render_de"] = (
            f"{row['gdt743_working_render_de']} ⟦{row['field_render_de']}⟧"
        )
        row["combined_specific_dispatch"] = int(
            int(row["gdt743_specific_local_dispatch"])
            or int(row["template_backed_field_reading"])
        )
    return rows, all_classes, complete_classes, w3_classes


def recurrence_census(
    rows: list[dict[str, object]], rules: list[dict[str, str]],
    all_classes: set[tuple[str, str]], complete_classes: set[tuple[str, str]],
    w3_classes: set[tuple[str, str]],
) -> list[dict[str, object]]:
    forms = sorted({str(row["surface"]) for row in rows})
    rule_map = {rule["channel"]: rule for rule in rules}
    output: list[dict[str, object]] = []
    for surface in forms:
        first = next(row for row in rows if row["surface"] == surface)
        for channel in CHANNEL_ORDER:
            members = [
                row for row in rows
                if row["surface"] == surface and row["raw_field_channel"] == channel
            ]
            complete = [row for row in members if int(row["boundary_complete"])]
            w3_members = [
                row for row in rows
                if row["surface"] == surface and row["w3_only_field_channel"] == channel
                and int(row["boundary_complete"])
            ]
            key = (surface, channel)
            output.append({
                "census_id": f"G744-C{len(output) + 1:03d}",
                "surface": surface,
                "family": first["family"],
                "level": first["level"],
                "channel": channel,
                "historical_mode": rule_map[channel]["historical_mode"],
                "observed_occurrences": len(members),
                "observed_pages": len({str(row["page"]) for row in members}),
                "observed_anchor_signatures": len({str(row["strong_anchor_signature"]) for row in members}),
                "complete_occurrences": len(complete),
                "complete_pages": len({str(row["page"]) for row in complete}),
                "complete_anchor_signatures": len({str(row["strong_anchor_signature"]) for row in complete}),
                "window_recurrence_gate": int(key in all_classes),
                "complete_template_gate": int(key in complete_classes),
                "template_backed_total_occurrences": len(members) if key in complete_classes else 0,
                "w3_only_complete_occurrences": len(w3_members),
                "w3_only_complete_pages": len({str(row["page"]) for row in w3_members}),
                "w3_only_complete_anchor_signatures": len({str(row["w3_only_anchor_signature"]) for row in w3_members}),
                "w3_only_complete_template_gate": int(key in w3_classes),
                "unresolved_slot_class": rule_map[channel]["unresolved_slot_class"],
                "historical_basis": rule_map[channel]["historical_basis"],
                "lexeme_or_plaintext_credit": 0,
            })
    return output


def candidate_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    provisional: list[dict[str, object]] = []
    for field in rows:
        if not int(field["template_backed_field_reading"]):
            continue
        for neighbor in field["_span"]:  # type: ignore[index]
            if not unresolved_candidate(neighbor):
                continue
            provisional.append({
                "candidate_id": f"G744-U{len(provisional) + 1:03d}",
                "gdt744_field_id": field["gdt744_field_id"],
                "patch_id": field["patch_id"],
                "page": field["page"],
                "locus": field["locus"],
                "target_surface": field["surface"],
                "target_ordinal": field["target_ordinal"],
                "field_channel": field["raw_field_channel"],
                "field_confidence_tier": field["field_confidence_tier"],
                "candidate_ordinal": neighbor["neighbor_ordinal"],
                "side": neighbor["side"],
                "distance": neighbor["distance"],
                "candidate_surface": neighbor["neighbor_surface"],
                "candidate_slot_class": field["unresolved_content_slot_class"],
                "default_role_de": field["unresolved_slot_label_de"],
                "positive_evidence": (
                    "exact-reader V99R7 unknown inside a boundary-clipped, "
                    "complete-template-backed historical field"
                ),
                "counterevidence": (
                    "cell identity and exact slot ownership remain unresolved; "
                    "field membership does not identify a word"
                ),
                "literal_identity": "OPEN",
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
    counts = Counter(str(row["candidate_surface"]) for row in provisional)
    pages: dict[str, set[str]] = defaultdict(set)
    for row in provisional:
        pages[str(row["candidate_surface"])].add(str(row["page"]))
    for row in provisional:
        surface = str(row["candidate_surface"])
        row["candidate_deck_occurrences"] = counts[surface]
        row["candidate_deck_pages"] = len(pages[surface])
        row["cross_page_content_identity_gate"] = int(len(pages[surface]) >= 2)
    return provisional


def safe_microfield_render(field: dict[str, object]) -> tuple[str, str]:
    ordered = sorted(field["_span"], key=lambda row: int(row["neighbor_ordinal"]))  # type: ignore[index]
    surfaces: list[str] = []
    renders: list[str] = []
    target_ordinal = int(field["target_ordinal"])
    inserted = False
    for neighbor in ordered:
        ordinal = int(neighbor["neighbor_ordinal"])
        if not inserted and target_ordinal < ordinal:
            surfaces.append(f"⟦{field['surface']}⟧")
            renders.append(f"⟦{field['gdt743_working_render_de']}⟧")
            inserted = True
        surfaces.append(neighbor["neighbor_surface"])
        if strong_anchor(neighbor, STRONG_W23):
            renders.append(neighbor["neighbor_semantic_value_de"])
        elif unresolved_candidate(neighbor):
            renders.append(
                f"[{neighbor['neighbor_surface']}: {field['unresolved_slot_label_de']}]"
            )
        else:
            renders.append(f"[{neighbor['neighbor_surface']}:?]")
    if not inserted:
        surfaces.append(f"⟦{field['surface']}⟧")
        renders.append(f"⟦{field['gdt743_working_render_de']}⟧")
    return " ".join(surfaces), "; ".join(renders)


def passage_rows(
    rows: list[dict[str, object]], complete_classes: set[tuple[str, str]]
) -> list[dict[str, object]]:
    selected: list[tuple[str, dict[str, object]]] = []
    used_loci: set[str] = set()

    for key in sorted(complete_classes):
        candidates = [
            row for row in rows
            if (row["surface"], row["raw_field_channel"]) == key
            and int(row["boundary_complete"])
        ]
        candidates.sort(key=lambda row: (-int(row["strong_anchor_count"]), str(row["patch_id"])))
        choice = next(
            (row for row in candidates if str(row["locus"]) not in used_loci), candidates[0]
        )
        selected.append(("COMPLETE_TEMPLATE_CLASS_EXEMPLAR", choice))
        used_loci.add(str(choice["locus"]))

    def add_controls(status: str, count: int, label: str) -> None:
        candidates = [row for row in rows if row["field_confidence_tier"] == status]
        candidates.sort(key=lambda row: (-int(row["strong_anchor_count"]), str(row["patch_id"])))
        used_channels: set[str] = set()
        for _ in range(count):
            pool = [
                row for row in candidates
                if str(row["locus"]) not in used_loci
                and str(row["raw_field_channel"]) not in used_channels
            ]
            if not pool:
                pool = [row for row in candidates if str(row["locus"]) not in used_loci]
            if not pool:
                raise AssertionError(f"not enough {status} passage controls")
            choice = pool[0]
            selected.append((label, choice))
            used_loci.add(str(choice["locus"]))
            used_channels.add(str(choice["raw_field_channel"]))

    add_controls("F2_RECURRENT_TEMPLATE_PARTIAL_CONTEXT", 1, "CENSORED_TEMPLATE_EXEMPLAR")
    add_controls("F1_RECURRENT_WINDOW_ONLY", 2, "WINDOW_ONLY_COUNTERCASE")
    add_controls("F0_OPEN", 1, "OPEN_COUNTERCASE")
    if len(selected) != 20:
        raise AssertionError("passage deck must contain 20 rows")

    output: list[dict[str, object]] = []
    for number, (selection_role, field) in enumerate(selected, start=1):
        eva, safe = safe_microfield_render(field)
        if int(field["template_backed_field_reading"]):
            information = (
                f"adds recurrent {field['raw_field_channel']} record channel and locates "
                f"the unresolved {field['unresolved_content_slot_class']} slot"
            )
        elif field["raw_field_channel"] != "OPEN":
            information = (
                f"shows provisional {field['raw_field_channel']} channel without renderer licence"
            )
        else:
            information = "adds no channel; preserves the open countercase"
        output.append({
            "reader_id": f"G744-R{number:02d}",
            "selection_role": selection_role,
            "gdt744_field_id": field["gdt744_field_id"],
            "page": field["page"],
            "locus": field["locus"],
            "target_surface": field["surface"],
            "target_ordinal": field["target_ordinal"],
            "field_channel": field["raw_field_channel"],
            "field_confidence_tier": field["field_confidence_tier"],
            "boundary_state": (
                f"L={field['left_boundary_reason']}|R={field['right_boundary_reason']}"
            ),
            "eva_microfield": eva,
            "gdt743_target_render_de": field["gdt743_working_render_de"],
            "safe_microfield_render_de": safe,
            "gdt744_field_card_de": field["field_render_de"],
            "combined_target_field_render_de": field["combined_target_field_render_de"],
            "unresolved_candidate_surfaces": field["unresolved_candidate_surfaces"],
            "information_added": information,
            "reader_ceiling": "FIELD_ROLE_ONLY__NO_LITERAL_CONTENT_IDENTITY_OR_PLAINTEXT",
        })
    return output


def attach_manual_passage_assessments(
    passages: list[dict[str, object]],
) -> list[dict[str, object]]:
    assessments = read_tsv(SRC / "MANUAL_PASSAGE_ASSESSMENTS.tsv")
    by_id = {row["reader_id"]: row for row in assessments}
    if len(assessments) != 20 or len(by_id) != 20:
        raise AssertionError("manual passage assessment deck must contain 20 unique rows")
    if set(by_id) != {str(row["reader_id"]) for row in passages}:
        raise AssertionError("manual passage assessment IDs changed")
    for passage in passages:
        assessment = by_id[str(passage["reader_id"])]
        if assessment["gdt744_field_id"] != passage["gdt744_field_id"]:
            raise AssertionError(f"manual passage field drift: {passage['reader_id']}")
        passage.update({
            "manual_coherence": assessment["manual_coherence"],
            "manual_information_gain": assessment["manual_information_gain"],
            "manual_note": assessment["manual_note"],
        })
    return passages


def write_reader(
    path: Path, fields: list[dict[str, object]], census: list[dict[str, object]],
    passages: list[dict[str, object]], candidates: list[dict[str, object]],
) -> None:
    licensed = [row for row in fields if int(row["template_backed_field_reading"])]
    complete_templates = [row for row in census if int(row["complete_template_gate"])]
    lines = [
        "# GDT744 historical microfield reader", "",
        "This reader adds a recurrent historical **record channel** around an inherited exact",
        "whole. It does not turn the target or a neighbor into a decoded word. Literal content",
        "names remain open and are printed as role-bearing unknown slots.", "",
        "## Result", "",
        f"- 202 cached target occurrences; {sum(int(row['boundary_complete']) for row in fields)} are fully bounded inside radius five.",
        f"- {len(complete_templates)} exact-whole/channel templates recur across at least two fully bounded pages.",
        f"- Those templates cover {len(licensed)} occurrences: {sum(str(row['field_confidence_tier']).startswith('F3') for row in licensed)} fully bounded and {sum(str(row['field_confidence_tier']).startswith('F2') for row in licensed)} radius-censored.",
        f"- {len(candidates)} unresolved content-slot cells remain; none receives a substance identity.", "",
        "## Recurrent templates", "",
        "| exact whole | field channel | complete examples | pages | total covered | W3-only gate |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in complete_templates:
        lines.append(
            f"| `{row['surface']}` | {row['channel']} | {row['complete_occurrences']} | "
            f"{row['complete_pages']} | {row['template_backed_total_occurrences']} | "
            f"{row['w3_only_complete_template_gate']} |"
        )
    lines.extend(["", "## Twenty microfield readings", ""])
    for row in passages:
        lines.extend([
            f"### {row['reader_id']} — {row['locus']} / `{row['target_surface']}`", "",
            f"- Selection: {row['selection_role']}; {row['field_confidence_tier']}",
            f"- EVA microfield: `{row['eva_microfield']}`",
            f"- Safe local render: {row['safe_microfield_render_de']}",
            f"- Field card: **{row['gdt744_field_card_de']}**",
            f"- What changed: {row['information_added']}", "",
            f"- Manual audit: {row['manual_coherence']} — {row['manual_note']}", "",
        ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def edge_packet(output_dir: Path, fields: list[dict[str, object]]) -> dict[str, object]:
    eligible = [
        row for row in fields
        if row["field_confidence_tier"] == "F3_RECURRENT_COMPLETE_CONTEXT"
        and int(row["strong_anchor_count"]) > 0
    ]
    source = sorted(eligible, key=lambda row: str(row["patch_id"]))[0]
    anchor = sorted(
        source["_anchors"], key=lambda row: (int(row["distance"]), row["side"])
    )[0]  # type: ignore[index]
    packet = [{
        "edge_id": "G744E001",
        "batch_id": "GDT744_HISTORICAL_MICROFIELD_CHANNEL",
        "page": source["page"],
        "physical_folio": physical_folio(str(source["page"])),
        "diagram_unit_id": "CACHED_TEXT_MICROFIELD",
        "pivot_visual_id": f"TARGET_{source['patch_id']}",
        "pivot_locus": f"{source['locus']}@{source['target_ordinal']}",
        "target_visual_id": f"ANCHOR_{anchor['window_id']}",
        "target_locus": f"{source['locus']}@{anchor['neighbor_ordinal']}",
        "relation_type": "HISTORICAL_MICROFIELD_CHANNEL_COLOCATION",
        "direction_basis": "BOUNDARY_CLIPPED_TEXT_ORDER",
        "ownership_basis": "MULTIPLE_CONTEXTUAL_ANCHORS",
        "geometry_only_selection": "FALSE",
        "source_manifest_id": "GDT744",
        "page_crop_sha256": "NONE",
        "pivot_crop_sha256": "NONE",
        "target_crop_sha256": "NONE",
        "source_aware_localizer": "GDT744_BUILDER",
        "relation_reviewer": "PENDING_EXTERNAL",
        "relation_confidence": "F3_RECURRENT_COMPLETE_CONTEXT",
        "ambiguity_state": "FIELD_CHANNEL_ONLY_LEXEME_OPEN",
        "formal_access_state": "FORMAL_ACCESSED",
        "fold_assignment": "NONE",
        "eligibility_status": "INELIGIBLE_FORMAL_CONTEXT_RELATION",
    }]
    packet_path = output_dir / "GDT744_GDT388_MICROFIELD_EDGE_PACKET.tsv"
    write_tsv(packet_path, packet, list(packet[0]))
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode not in {0, 1} or not completed.stdout:
        raise AssertionError(f"edge intake failed: {completed.stderr}")
    intake = json.loads(completed.stdout)
    if intake["status"] != "INVALID_PACKET" or intake["score_ready"]:
        raise AssertionError("formal-context relation packet unexpectedly score-ready")
    (output_dir / "GDT744_GDT388_EDGE_INTAKE.json").write_text(
        json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return intake


def public_field(row: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in row.items() if not key.startswith("_")}


def verify_historical_inputs() -> dict[str, object]:
    result = json.loads((ROOT / G735_RESULT_REL).read_text(encoding="utf-8"))
    if result["historical"]["direct_two_channel_sources"] != ["HSR010"]:
        raise AssertionError("GDT735 direct two-channel witness changed")
    slots = {row["slot"]: row for row in read_tsv(ROOT / G735_SLOT_REL)}
    for slot in ("DEGREE", "HOT", "DRY", "PLANT_PART"):
        if int(slots[slot]["descriptive_rows"]) < 1:
            raise AssertionError(f"missing descriptive historical slot: {slot}")
    for slot in ("INGREDIENT", "RECIPE_COMMAND", "NUMBER", "UNIT"):
        if int(slots[slot]["prescriptive_rows"]) < 1:
            raise AssertionError(f"missing prescriptive historical slot: {slot}")
    return result


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    historical = verify_historical_inputs()
    rules = load_channel_rules()
    supplements = load_whole_supplements()
    windows = read_tsv(ROOT / G739_WINDOW_REL)
    patches = read_tsv(ROOT / G743_PATCH_REL)
    patches.sort(key=lambda row: row["gdt743_patch_id"])
    if len(windows) != 1373 or len(patches) != 202:
        raise AssertionError("inherited 1373-window/202-target boundary changed")
    if any(row["page"].startswith("f84") for row in windows + patches):
        raise AssertionError("sealed page entered GDT744")
    if len({row["patch_id"] for row in patches}) != 202:
        raise AssertionError("duplicate target patch")

    fields = build_initial_fields(patches, windows, rules, supplements)
    fields, all_classes, complete_classes, w3_classes = decorate_fields(fields, rules)
    census = recurrence_census(fields, rules, all_classes, complete_classes, w3_classes)
    candidates = candidate_rows(fields)
    passages = passage_rows(fields, complete_classes)
    passages = attach_manual_passage_assessments(passages)

    public_fields = [public_field(row) for row in fields]
    write_tsv(
        output_dir / "MICROFIELD_202_CHANNEL_DISPATCH.tsv",
        public_fields, list(public_fields[0]),
    )
    write_tsv(
        output_dir / "FORM_CHANNEL_RECURRENCE_CENSUS.tsv",
        census, list(census[0]),
    )
    write_tsv(
        output_dir / "UNRESOLVED_CONTENT_SLOT_CANDIDATES.tsv",
        candidates, list(candidates[0]),
    )
    write_tsv(
        output_dir / "PASSAGE_20_MICROFIELD_READER.tsv",
        passages, list(passages[0]),
    )
    write_reader(
        output_dir / "GDT744_HISTORICAL_MICROFIELD_READER.md",
        fields, census, passages, candidates,
    )
    intake = edge_packet(output_dir, fields)

    tiers = Counter(str(row["field_confidence_tier"]) for row in fields)
    channels = Counter(str(row["raw_field_channel"]) for row in fields)
    licensed = [row for row in fields if int(row["template_backed_field_reading"])]
    target_specific = {
        str(row["patch_id"]) for row in fields if int(row["gdt743_specific_local_dispatch"])
    }
    field_specific = {str(row["patch_id"]) for row in licensed}
    multi_channel_forms = sorted(
        surface for surface in {str(row["surface"]) for row in fields}
        if sum(1 for key in complete_classes if key[0] == surface) >= 2
    )
    result: dict[str, object] = {
        "schema": "GDT744_HISTORICAL_MICROFIELD_CHANNEL_BRIDGE_RESULT_V1",
        "status": STATUS,
        "scope": {
            "inherited_target_occurrences": len(fields),
            "target_forms": len({str(row["surface"]) for row in fields}),
            "target_pages": len({str(row["page"]) for row in fields}),
            "cached_window_rows": len(windows),
            "new_pages_used": 0,
            "new_images_used": 0,
            "new_transcriptions_used": 0,
            "f84_used": False,
            "f84r_used": False,
        },
        "boundary": {
            "fully_bounded_microfields": sum(int(row["boundary_complete"]) for row in fields),
            "radius5_censored_microfields": sum(not int(row["boundary_complete"]) for row in fields),
            "left_reason_counts": dict(sorted(Counter(str(row["left_boundary_reason"]).split("_R")[0] for row in fields).items())),
            "right_reason_counts": dict(sorted(Counter(str(row["right_boundary_reason"]).split("_R")[0] for row in fields).items())),
        },
        "channel": {
            "raw_counts": dict(sorted(channels.items())),
            "complete_recurrent_exact_whole_channel_templates": len(complete_classes),
            "window_recurrent_exact_whole_channel_templates": len(all_classes),
            "template_backed_occurrences": len(licensed),
            "confidence_tiers": dict(sorted(tiers.items())),
            "template_channels": dict(sorted(Counter(str(row["raw_field_channel"]) for row in licensed).items())),
            "forms_with_multiple_complete_templates": multi_channel_forms,
            "template_backed_quality_conflicts": sum(
                int(row["quality_conflict"]) for row in licensed
            ),
        },
        "sensitivity": {
            "w3_only_template_backed_occurrences": sum(
                int(row["w3_only_template_reading_retained"]) for row in licensed
            ),
            "w3_only_same_channel_and_template": sum(
                int(row["w3_only_template_reading_retained"])
                and int(row["w3_only_same_channel"]) for row in licensed
            ),
            "main_vs_unclipped_channel_matches": sum(
                row["raw_field_channel"] == row["unclipped_field_channel"] for row in fields
            ),
            "main_vs_r2_channel_matches": sum(
                row["raw_field_channel"] == row["r2_field_channel"] for row in fields
            ),
        },
        "renderer": {
            "gdt743_target_specific_occurrences": len(target_specific),
            "template_field_specific_occurrences": len(field_specific),
            "combined_specific_occurrences": len(target_specific | field_specific),
            "newly_specific_from_field_channel": len(field_specific - target_specific),
            "remaining_without_target_or_template_specificity": len(fields) - len(target_specific | field_specific),
            "passage_examples": len(passages),
            "manual_information_gain_examples": sum(
                int(row["manual_information_gain"]) for row in passages
            ),
        },
        "content_slots": {
            "candidate_cells": len(candidates),
            "candidate_fields": len({str(row["gdt744_field_id"]) for row in candidates}),
            "candidate_surfaces": len({str(row["candidate_surface"]) for row in candidates}),
            "cross_page_identity_gates": sum(
                int(row["cross_page_content_identity_gate"]) for row in candidates
            ),
        },
        "historical_bridge": {
            "direct_two_channel_source": historical["historical"]["direct_two_channel_sources"],
            "architecture_only": True,
            "target_reading": "bound level/state field across descriptive, prescriptive and ambiguous quantity/part channels",
            "content_identity": "open learned whole/name or ingredient slots",
            "inherited_exact_whole_role_supplement_contacts": sum(
                int(row["supplemental_whole_role_anchor_count"]) for row in fields
            ),
        },
        "relation_edge_intake": intake,
        "claims": {
            "confirmed_lexemes": 0,
            "plaintext_translations": 0,
            "literal_substances_or_species": 0,
            "head_or_body_lexeme_credit": 0,
            "component_export_credit": 0,
            "unseen_form_predictions": 0,
        },
        "artifact_rows": {
            "MICROFIELD_202_CHANNEL_DISPATCH.tsv": len(fields),
            "FORM_CHANNEL_RECURRENCE_CENSUS.tsv": len(census),
            "UNRESOLVED_CONTENT_SLOT_CANDIDATES.tsv": len(candidates),
            "PASSAGE_20_MICROFIELD_READER.tsv": len(passages),
            "GDT744_GDT388_MICROFIELD_EDGE_PACKET.tsv": 1,
            "GDT744_GDT388_EDGE_INTAKE.json": 1,
            "GDT744_HISTORICAL_MICROFIELD_READER.md": len(passages),
        },
        "artifact_hashes": {
            str(BASE_REL / "artifacts" / name): sha256(output_dir / name)
            for name in OUTPUT_NAMES
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
    result = build(parser.parse_args().output_dir)
    print(json.dumps({
        "schema": result["schema"],
        "status": result["status"],
        "boundary": result["boundary"],
        "channel": result["channel"],
        "sensitivity": result["sensitivity"],
        "renderer": result["renderer"],
        "content_slots": result["content_slots"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
