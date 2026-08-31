#!/usr/bin/env python3
"""Independent validator for the GDT676 V50 external-line reader.

This module intentionally does not import the builder.  It reconstructs every
derived row from the published GDT675 overlays and the explicit GDT676 source
specifications, validates the compact result and its hashes, then executes the
builder and requires a byte-identical replay of every builder-owned artifact.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt676_v50_external_line_renderer"
ART = EXP / "artifacts"
GDT675 = ROOT / "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan"

TOUCHED_PATH = GDT675 / "artifacts/TOUCHED_LINE_OVERLAY.tsv"
OCCURRENCES_PATH = GDT675 / "artifacts/EXTERNAL_TRANSFERABLE_OCCURRENCES.tsv"
GDT675_RESULT_PATH = GDT675 / "artifacts/RESULT.json"
GDT675_MANIFEST_PATH = GDT675 / "experiment.json"
GDT676_MANIFEST_PATH = EXP / "experiment.json"
MODE_PATH = EXP / "src/LINE_MODE_SPECS.tsv"
READER_PATH = EXP / "src/LINE_READER_SPECS.tsv"
VALUE_PATH = EXP / "src/VALUE_ATTACHMENT_SPECS.tsv"
TEMPLATE_PATH = EXP / "src/SYNTAX_TEMPLATES.tsv"
PASSAGE_PATH = EXP / "src/PASSAGE_SELECTIONS.tsv"
BUILDER_PATH = EXP / "src/run.py"
VALIDATION_PATH = ART / "VALIDATION.json"

# These screens are independently re-declared rather than imported from run.py.
NARROW_CARRIER = re.compile(
    r"\b(?:\w*Ansatz\w*|\w*Kompositum\w*|\w*Species\w*|Drogenstoff|"
    r"Trockengut|Feuchtmaterial|Materialmaß|Grundauszug)\b",
    re.IGNORECASE,
)
GENERIC_FILLER = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|"
    r"Arbeitsstelle|Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|"
    r"Arbeitsschritt|Stationsansatz|Stationsposten|Stationswert|Stationsanteil|"
    r"Stationseinheit|Aktiver Posten|laufender Eintrag|work item|working material|"
    r"worksite|work cycle|source vessel|destination place|destination vessel)\b",
    re.IGNORECASE,
)
EXTENDED_CLASS_CARRIER = re.compile(
    r"(?:gut|stoff|droge|material|ansatz|kompositum|species|klasse|grad|maß|menge|"
    r"posten|charge|zubereitung|teil|eintrag|feld|form|einheit|portion|fraktion|"
    r"qualität|rahmen)",
    re.IGNORECASE,
)
WORKING_UNKNOWN = re.compile(r"⟦([^:⟧]+):\?⟧")
TOKEN_UNKNOWN = re.compile(r"^\[([^:\]]+):\?\]$")

EXPECTED_STATUS = (
    "PASS_51_LINE_READER__479_TOKENS__136_OPEN__1_DCHEY_OVERRIDE__ZERO_HARD_GENERIC"
)
EXPECTED_GDT675_STATUS = (
    "PASS_51_EXTERNAL_POSITIONS__12_CARDS_HOLD__9_RENDER_SPLITS__11_SOURCE_ONLY"
)
EXPECTED_CLAIM_CEILING = (
    "A token-preserving practical reader for 51 already touched V50 lines. It renders all 479 positions, "
    "but 136 remain explicitly unknown, 113 working-reader positions match the narrow carrier screen, and "
    "311 of 343 assigned literal values match an explicitly broad extended class sensitivity screen. Only "
    "two lines are complete. This is not plaintext, a historical codebook, or proof of manuscript-wide language, lexemes, "
    "substances, procedures, plants, diseases, patients or cures."
)

TOKEN_FIELDS = [
    "page", "locus", "section", "language", "hand", "ordinal", "surface",
    "before_v50_gloss_de", "v50_gloss_de", "information_category", "licensed_action",
    "literal_narrow_carrier", "literal_narrow_match_count", "assigned_extended_class_carrier",
    "working_chunk_de", "working_narrow_carrier", "working_narrow_match_count",
    "literal_hard_generic_hits", "working_hard_generic_hits", "new_card_surface",
    "new_card_render_mode", "new_card_reader_support",
]
LINE_FIELDS = [
    "page", "locus", "section", "language", "hand", "token_count", "new_v50_positions",
    "residual_unknown_positions", "inherited_narrow_carrier_positions",
    "inherited_other_assigned_positions", "literal_narrow_carrier_positions",
    "literal_narrow_carrier_matches", "working_narrow_carrier_positions",
    "working_narrow_carrier_matches", "assigned_fraction", "complete", "action_positions",
    "action_ordinals", "action_surfaces", "line_mode", "source_action_mode",
    "gdt675_render_correction", "new_surface", "new_reader_support",
    "remaining_unknown_surfaces", "zl3b_line", "literal_token_glosses_de",
    "working_line_de", "review_note",
]


class Audit:
    def __init__(self) -> None:
        self.checks = 0

    def check(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(f"check {self.checks} failed: {message}")


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_ordinals(raw: str) -> list[int]:
    return [] if raw == "NONE" else [int(value) for value in raw.split("|")]


def parse_action_specs(raw: str) -> list[tuple[int, str]]:
    if raw == "NONE":
        return []
    result: list[tuple[int, str]] = []
    for item in raw.split("|"):
        ordinal, label = item.split(":", 1)
        result.append((int(ordinal), label))
    return result


def normalized_row(row: Mapping[str, object], fields: Sequence[str]) -> dict[str, str]:
    return {field: str(row[field]) for field in fields}


def compare_rows(
    audit: Audit,
    label: str,
    path: Path,
    fields: Sequence[str],
    expected: Sequence[Mapping[str, object]],
) -> list[dict[str, str]]:
    actual_fields, actual = read_tsv(path)
    audit.check(actual_fields == list(fields), f"{label}: header")
    audit.check(len(actual) == len(expected), f"{label}: row count")
    for number, (found, wanted) in enumerate(zip(actual, expected), start=1):
        audit.check(list(found) == list(fields), f"{label} row {number}: field order")
        wanted_text = normalized_row(wanted, fields)
        for field in fields:
            audit.check(
                found[field] == wanted_text[field],
                f"{label} row {number} field {field}: {found[field]!r} != {wanted_text[field]!r}",
            )
    return actual


def validate_optional_manifest_hashes(manifest: Mapping[str, object]) -> None:
    """Check a populated GDT676 manifest without changing stable audit totals.

    The first validator run precedes manifest finalization.  Not counting these
    optional checks keeps VALIDATION.json byte-stable when the finalized manifest
    is later checked.  Only experiment-local and published GDT675 paths are ever
    opened here; no transcription source is admitted.
    """

    safe_prefixes = (
        "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan/",
        "experiments/yolo/gdt676_v50_external_line_renderer/",
    )
    gathered: list[tuple[str, object]] = []
    for collection in ("inputs", "outputs"):
        entries = manifest.get(collection, [])
        if not isinstance(entries, list):
            raise AssertionError(f"manifest {collection} is not a list")
        for entry in entries:
            if not isinstance(entry, dict):
                raise AssertionError(f"manifest {collection} has a non-object entry")
            relative = entry.get("path")
            expected = entry.get("sha256")
            if not isinstance(relative, str) or not relative.startswith(safe_prefixes):
                raise AssertionError(f"unsafe or unrelated manifest path: {relative!r}")
            gathered.append((relative, expected))
    # `tools/new_yolo_experiment.py` registers null hash slots before the
    # final manifest-sealing pass.  Accept that all-null draft, but never a
    # partially sealed mixture; once populated, verify every byte.
    if gathered and all(expected is None for _, expected in gathered):
        return
    if any(expected is None for _, expected in gathered):
        raise AssertionError("partially populated GDT676 manifest hashes")
    self_referential = {
        "experiments/yolo/gdt676_v50_external_line_renderer/src/validate.py",
        "experiments/yolo/gdt676_v50_external_line_renderer/artifacts/VALIDATION.json",
    }
    for relative, expected in gathered:
        if not isinstance(expected, str) or len(expected) != 64:
            raise AssertionError(f"invalid manifest SHA-256: {relative}")
        # A validator cannot require its previously sealed own hash before an
        # authorized validator update has had its first run.  The repository's
        # external manifest gate reseals these two self-referential files after
        # this run; every non-self input/output remains checked here.
        if relative in self_referential:
            continue
        target = ROOT / relative
        if not target.is_file() or sha256(target) != expected:
            raise AssertionError(f"manifest hash mismatch: {relative}")


def main() -> int:
    audit = Audit()

    touched_fields, touched = read_tsv(TOUCHED_PATH)
    occurrence_fields, occurrences = read_tsv(OCCURRENCES_PATH)
    mode_fields, mode_specs = read_tsv(MODE_PATH)
    reader_fields, reader_specs = read_tsv(READER_PATH)
    value_fields, value_specs = read_tsv(VALUE_PATH)
    template_fields, templates = read_tsv(TEMPLATE_PATH)
    passage_fields, passage_specs = read_tsv(PASSAGE_PATH)

    audit.check(touched_fields == [
        "page", "locus", "section", "language", "hand", "zl3b_line",
        "unknown_after_gdt673", "unknown_after_gdt674", "applied_ordinals",
        "applied_surfaces", "unknown_after_gdt675", "remaining_unknown_ordinals",
        "remaining_unknown_surfaces", "before_overlay_glosses_de", "gdt675_overlay_glosses_de",
    ], "GDT675 touched-line schema")
    audit.check(occurrence_fields == [
        "surface", "card_class", "composition", "working_meaning_de",
        "external_working_meaning_de", "applied_meaning_de", "render_mode",
        "strongest_rival_de", "confidence", "page", "locus", "section", "language",
        "hand", "ordinal", "line_token_count", "line_position", "source_f81r",
        "was_v48_unknown", "was_v49_unknown", "was_gdt674_unknown", "target_v49_gloss_de",
        "target_v49_source", "target_v49_scope_state", "left_surface", "left_v49_gloss_de",
        "right_surface", "right_v49_gloss_de", "it2a_operation", "it2a_render",
        "rf1b_operation", "rf1b_render", "reader_support", "zl3b_line", "decision",
        "promote_external", "review_note",
    ], "GDT675 occurrence schema")
    audit.check(mode_fields == ["locus", "action_ordinals", "line_mode", "gdt675_render_correction"], "mode schema")
    audit.check(reader_fields == ["locus", "line_mode", "action_ordinals", "working_line_de", "review_note"], "reader schema")
    audit.check(value_fields == [
        "locus", "head_ordinals", "value_ordinals", "close_ordinal", "decision",
        "contextual_reading_de", "note",
    ], "value schema")
    audit.check(template_fields == ["template_id", "visible_pattern", "renderer_rule"], "template schema")
    audit.check(passage_fields == ["selection_id", "loci", "selection_class", "purpose"], "passage schema")
    audit.check(len(touched) == 51, "51 touched lines")
    audit.check(len(occurrences) == 51, "51 external positions")
    audit.check(len(mode_specs) == 51, "51 mode specs")
    audit.check(len(reader_specs) == 51, "51 line readers")
    audit.check(len(value_specs) == 17, "17 value decisions")
    audit.check(len(templates) == 8, "8 templates")
    audit.check(len(passage_specs) == 4, "4 passage selections")

    gdt675_result = read_json(GDT675_RESULT_PATH)
    gdt675_manifest = read_json(GDT675_MANIFEST_PATH)
    gdt676_manifest = read_json(GDT676_MANIFEST_PATH)
    audit.check(isinstance(gdt675_result, dict), "GDT675 RESULT object")
    audit.check(isinstance(gdt675_manifest, dict), "GDT675 manifest object")
    audit.check(isinstance(gdt676_manifest, dict), "GDT676 manifest object")
    assert isinstance(gdt675_result, dict)
    assert isinstance(gdt675_manifest, dict)
    assert isinstance(gdt676_manifest, dict)
    audit.check(gdt675_result["status"] == EXPECTED_GDT675_STATUS, "GDT675 status")
    audit.check(gdt675_result["occurrences"]["external_lines"] == 51, "GDT675 external lines")
    audit.check(gdt675_result["occurrences"]["external_positions"] == 51, "GDT675 external positions")
    audit.check(gdt675_result["occurrences"]["external_pages"] == 36, "GDT675 external pages")
    audit.check(gdt675_manifest["experiment_id"] == "GDT675", "GDT675 manifest ID")
    audit.check(gdt675_manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "GDT675 seals")
    gdt675_hashes = {
        item["path"]: item["sha256"] for item in gdt675_manifest["outputs"]
        if isinstance(item, dict) and "path" in item and "sha256" in item
    }
    for path in (TOUCHED_PATH, OCCURRENCES_PATH, GDT675_RESULT_PATH):
        relative = path.relative_to(ROOT).as_posix()
        audit.check(relative in gdt675_hashes, f"GDT675 owns {relative}")
        audit.check(sha256(path) == gdt675_hashes[relative], f"GDT675 hash {relative}")

    audit.check(gdt676_manifest["experiment_id"] == "GDT676", "GDT676 manifest ID")
    audit.check(gdt676_manifest["slug"] == "v50_external_line_renderer", "GDT676 slug")
    audit.check(gdt676_manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "GDT676 seals")
    audit.check(gdt676_manifest["commands"]["run"] == "python3 experiments/yolo/gdt676_v50_external_line_renderer/src/run.py", "GDT676 run command")
    audit.check(gdt676_manifest["commands"]["validate"] == "python3 experiments/yolo/gdt676_v50_external_line_renderer/src/validate.py", "GDT676 validate command")
    if gdt676_manifest.get("dependencies") and "GDT675" not in gdt676_manifest["dependencies"]:
        raise AssertionError("populated GDT676 manifest must depend on GDT675")
    validate_optional_manifest_hashes(gdt676_manifest)

    loci = [row["locus"] for row in touched]
    audit.check(len(set(loci)) == 51, "unique touched loci")
    audit.check(len({row["page"] for row in touched}) == 36, "36 pages")
    mode_by_locus = {row["locus"]: row for row in mode_specs}
    reader_by_locus = {row["locus"]: row for row in reader_specs}
    audit.check(len(mode_by_locus) == 51, "unique mode loci")
    audit.check(len(reader_by_locus) == 51, "unique reader loci")
    audit.check(set(mode_by_locus) == set(loci), "mode coverage")
    audit.check(set(reader_by_locus) == set(loci), "reader coverage")

    occurrence_by_key: dict[tuple[str, int], dict[str, str]] = {}
    for occurrence in occurrences:
        key = (occurrence["locus"], int(occurrence["ordinal"]))
        audit.check(key not in occurrence_by_key, f"unique occurrence {key}")
        occurrence_by_key[key] = occurrence
    audit.check(len(occurrence_by_key) == 51, "51 unique occurrence keys")

    token_rows: list[dict[str, object]] = []
    line_rows: list[dict[str, object]] = []
    line_by_locus: dict[str, dict[str, object]] = {}
    totals: Counter[str] = Counter()
    distribution: Counter[int] = Counter()
    reader_support: Counter[str] = Counter()
    new_surfaces: set[str] = set()
    literal_narrow_positions = 0
    literal_narrow_matches = 0
    working_narrow_positions = 0
    working_narrow_matches = 0
    assigned_extended_positions = 0
    literal_generic_matches = 0
    working_generic_matches = 0

    for line in touched:
        locus = line["locus"]
        tokens = line["zl3b_line"].split()
        before = line["before_overlay_glosses_de"].split(" | ")
        after = line["gdt675_overlay_glosses_de"].split(" | ")
        applied = parse_ordinals(line["applied_ordinals"])
        remaining = parse_ordinals(line["remaining_unknown_ordinals"])
        applied_surfaces = [] if line["applied_surfaces"] == "NONE" else line["applied_surfaces"].split("|")
        remaining_surfaces = [] if line["remaining_unknown_surfaces"] == "NONE" else line["remaining_unknown_surfaces"].split("|")

        audit.check(len(tokens) == len(before) == len(after), f"{locus}: aligned vectors")
        audit.check(bool(tokens), f"{locus}: nonempty line")
        audit.check(len(applied) == 1, f"{locus}: one V50 application")
        audit.check(len(set(remaining)) == len(remaining), f"{locus}: unique residual ordinals")
        audit.check(all(1 <= ordinal <= len(tokens) for ordinal in applied + remaining), f"{locus}: ordinal range")
        audit.check(not set(applied) & set(remaining), f"{locus}: disjoint applied/residual")
        audit.check(applied_surfaces == [tokens[ordinal - 1] for ordinal in applied], f"{locus}: applied surfaces")
        audit.check(remaining_surfaces == [tokens[ordinal - 1] for ordinal in remaining], f"{locus}: residual surfaces")
        audit.check(int(line["unknown_after_gdt673"]) == sum(
            gloss == f"[{surface}:?]" for surface, gloss in zip(tokens, before)
        ), f"{locus}: GDT673 unknown count")
        audit.check(int(line["unknown_after_gdt674"]) == int(line["unknown_after_gdt673"]), f"{locus}: GDT674 unchanged")
        audit.check(int(line["unknown_after_gdt675"]) == len(remaining), f"{locus}: GDT675 unknown count")
        after_unknowns = {
            ordinal for ordinal, (surface, gloss) in enumerate(zip(tokens, after), start=1)
            if gloss == f"[{surface}:?]"
        }
        audit.check(after_unknowns == set(remaining), f"{locus}: residual placeholder positions")
        changed = {ordinal for ordinal, pair in enumerate(zip(before, after), start=1) if pair[0] != pair[1]}
        audit.check(changed == set(applied), f"{locus}: exactly one changed position")
        for ordinal in remaining:
            match = TOKEN_UNKNOWN.fullmatch(after[ordinal - 1])
            audit.check(match is not None and match.group(1) == tokens[ordinal - 1], f"{locus}: named residual {ordinal}")

        applied_ordinal = applied[0]
        audit.check(before[applied_ordinal - 1] == f"[{tokens[applied_ordinal - 1]}:?]", f"{locus}: applied position open")
        occurrence = occurrence_by_key[(locus, applied_ordinal)]
        for field in ("page", "locus", "section", "language", "hand", "zl3b_line"):
            audit.check(occurrence[field] == line[field], f"{locus}: occurrence {field}")
        audit.check(int(occurrence["line_token_count"]) == len(tokens), f"{locus}: occurrence length")
        audit.check(occurrence["surface"] == tokens[applied_ordinal - 1], f"{locus}: occurrence surface")
        audit.check(occurrence["target_v49_gloss_de"] == before[applied_ordinal - 1], f"{locus}: old occurrence gloss")
        audit.check(occurrence["applied_meaning_de"] == after[applied_ordinal - 1], f"{locus}: applied occurrence gloss")
        audit.check(occurrence["source_f81r"] == "0", f"{locus}: external occurrence")
        audit.check(occurrence["was_v48_unknown"] == "1", f"{locus}: V48-open")
        audit.check(occurrence["was_v49_unknown"] == "1", f"{locus}: V49-open")
        audit.check(occurrence["was_gdt674_unknown"] == "1", f"{locus}: GDT674-open")
        audit.check(occurrence["decision"] == "EXTERNAL_TRANSFER_HOLD", f"{locus}: transfer hold")
        audit.check(occurrence["promote_external"] == "1", f"{locus}: promoted external")
        reader_support[occurrence["reader_support"]] += 1
        new_surfaces.add(occurrence["surface"])

        mode = mode_by_locus[locus]
        reader = reader_by_locus[locus]
        working_chunks = reader["working_line_de"].rstrip(".").split(" · ")
        audit.check(len(working_chunks) == len(tokens), f"{locus}: one working chunk per token")
        action_specs = parse_action_specs(mode["action_ordinals"])
        action_ordinals = {ordinal for ordinal, _ in action_specs}
        audit.check(len(action_specs) == len(action_ordinals), f"{locus}: unique actions")
        audit.check(action_ordinals == set(parse_ordinals(reader["action_ordinals"])), f"{locus}: action agreement")
        for ordinal, label in action_specs:
            audit.check(1 <= ordinal <= len(tokens), f"{locus}: action range")
            if "<" in label:
                audit.check(label.endswith(">"), f"{locus}: fused-action syntax")
                subspan, owner = label[:-1].split("<", 1)
                audit.check(owner == tokens[ordinal - 1], f"{locus}: fused-action owner")
                audit.check(owner.startswith(subspan), f"{locus}: fused-action subspan")
            else:
                audit.check(label == tokens[ordinal - 1], f"{locus}: action surface")
        final_mode = reader["line_mode"]
        audit.check(final_mode in {"ACTION_SEQUENCE", "MIXED_RECORD", "NOMINAL_REGISTER", "QUANTITY_LABEL"}, f"{locus}: valid final mode")
        if final_mode in {"NOMINAL_REGISTER", "QUANTITY_LABEL"}:
            audit.check(not action_ordinals, f"{locus}: nominal mode has no action")
        else:
            audit.check(bool(action_ordinals), f"{locus}: active mode has action")

        unknown_markers = Counter(WORKING_UNKNOWN.findall(reader["working_line_de"]))
        expected_markers = Counter(tokens[ordinal - 1] for ordinal in remaining)
        audit.check(unknown_markers == expected_markers, f"{locus}: visible working unknowns")
        line_working_positions = sum(bool(NARROW_CARRIER.search(chunk)) for chunk in working_chunks)
        line_working_matches = sum(len(NARROW_CARRIER.findall(chunk)) for chunk in working_chunks)
        line_working_generic = sum(len(GENERIC_FILLER.findall(chunk)) for chunk in working_chunks)
        audit.check(line_working_generic == 0, f"{locus}: no working generic filler")
        working_narrow_positions += line_working_positions
        working_narrow_matches += line_working_matches
        working_generic_matches += line_working_generic

        categories: Counter[str] = Counter()
        line_literal_positions = 0
        line_literal_matches = 0
        for ordinal, (surface, old_gloss, new_gloss, working_chunk) in enumerate(
            zip(tokens, before, after, working_chunks), start=1
        ):
            if ordinal in remaining:
                audit.check(
                    working_chunk == f"⟦{surface}:?⟧",
                    f"{locus}: residual chunk {ordinal} is the exact named marker",
                )
            else:
                audit.check(
                    WORKING_UNKNOWN.search(working_chunk) is None,
                    f"{locus}: assigned chunk {ordinal} contains no unknown marker",
                )
            if ordinal in applied:
                category = "NEW_V50"
            elif ordinal in remaining:
                category = "RESIDUAL_UNKNOWN"
            elif NARROW_CARRIER.search(new_gloss):
                category = "INHERITED_NARROW_CARRIER"
            else:
                category = "INHERITED_OTHER_ASSIGNED"
            literal_hits = len(NARROW_CARRIER.findall(new_gloss))
            working_hits = len(NARROW_CARRIER.findall(working_chunk))
            extended_hit = ordinal not in remaining and bool(EXTENDED_CLASS_CARRIER.search(new_gloss))
            literal_generic = len(GENERIC_FILLER.findall(new_gloss))
            working_generic = len(GENERIC_FILLER.findall(working_chunk))
            categories[category] += 1
            totals[category] += 1
            if literal_hits:
                line_literal_positions += 1
                literal_narrow_positions += 1
            line_literal_matches += literal_hits
            literal_narrow_matches += literal_hits
            assigned_extended_positions += int(extended_hit)
            literal_generic_matches += literal_generic
            at_position = occurrence_by_key.get((locus, ordinal))
            token_rows.append({
                "page": line["page"], "locus": locus, "section": line["section"],
                "language": line["language"], "hand": line["hand"], "ordinal": ordinal,
                "surface": surface, "before_v50_gloss_de": old_gloss, "v50_gloss_de": new_gloss,
                "information_category": category,
                "licensed_action": "1" if ordinal in action_ordinals else "0",
                "literal_narrow_carrier": "1" if literal_hits else "0",
                "literal_narrow_match_count": literal_hits,
                "assigned_extended_class_carrier": "1" if extended_hit else "0",
                "working_chunk_de": working_chunk,
                "working_narrow_carrier": "1" if working_hits else "0",
                "working_narrow_match_count": working_hits,
                "literal_hard_generic_hits": literal_generic,
                "working_hard_generic_hits": working_generic,
                "new_card_surface": at_position["surface"] if at_position else "NONE",
                "new_card_render_mode": at_position["render_mode"] if at_position else "NONE",
                "new_card_reader_support": at_position["reader_support"] if at_position else "NONE",
            })

        token_count = len(tokens)
        residual = categories["RESIDUAL_UNKNOWN"]
        assigned = token_count - residual
        distribution[residual] += 1
        line_row: dict[str, object] = {
            "page": line["page"], "locus": locus, "section": line["section"],
            "language": line["language"], "hand": line["hand"], "token_count": token_count,
            "new_v50_positions": categories["NEW_V50"],
            "residual_unknown_positions": residual,
            "inherited_narrow_carrier_positions": categories["INHERITED_NARROW_CARRIER"],
            "inherited_other_assigned_positions": categories["INHERITED_OTHER_ASSIGNED"],
            "literal_narrow_carrier_positions": line_literal_positions,
            "literal_narrow_carrier_matches": line_literal_matches,
            "working_narrow_carrier_positions": line_working_positions,
            "working_narrow_carrier_matches": line_working_matches,
            "assigned_fraction": f"{assigned / token_count:.6f}",
            "complete": "1" if residual == 0 else "0", "action_positions": len(action_ordinals),
            "action_ordinals": "|".join(map(str, sorted(action_ordinals))) or "NONE",
            "action_surfaces": "|".join(tokens[ordinal - 1] for ordinal in sorted(action_ordinals)) or "NONE",
            "line_mode": final_mode, "source_action_mode": mode["line_mode"],
            "gdt675_render_correction": mode["gdt675_render_correction"],
            "new_surface": tokens[applied_ordinal - 1], "new_reader_support": occurrence["reader_support"],
            "remaining_unknown_surfaces": line["remaining_unknown_surfaces"],
            "zl3b_line": line["zl3b_line"], "literal_token_glosses_de": line["gdt675_overlay_glosses_de"],
            "working_line_de": reader["working_line_de"], "review_note": reader["review_note"],
        }
        line_rows.append(line_row)
        line_by_locus[locus] = line_row

    audit.check(len(token_rows) == 479, "479 token rows")
    audit.check(sum(totals.values()) == 479, "category partition spans 479")
    audit.check(totals == Counter({
        "NEW_V50": 51, "RESIDUAL_UNKNOWN": 136,
        "INHERITED_NARROW_CARRIER": 77, "INHERITED_OTHER_ASSIGNED": 215,
    }), "51/136/77/215 category partition")
    audit.check(literal_narrow_positions == 105, "105 literal narrow positions")
    audit.check(literal_narrow_matches == 106, "106 literal narrow matches")
    audit.check(working_narrow_positions == 113, "113 working narrow positions")
    audit.check(working_narrow_matches == 114, "114 working narrow matches")
    audit.check(assigned_extended_positions == 311, "311 assigned extended-class positions")
    audit.check(f"{assigned_extended_positions / 343:.6f}" == "0.906706", "extended-class sensitivity fraction")
    audit.check(literal_generic_matches == 0, "zero literal generic filler")
    audit.check(working_generic_matches == 0, "zero working generic filler")
    audit.check(reader_support == Counter({"BOTH_EXACT": 42, "ONE_EXACT": 7, "NEITHER_EXACT": 2}), "reader support profile")
    audit.check(len(new_surfaces) == 12, "12 transferred surfaces")
    audit.check(479 - totals["RESIDUAL_UNKNOWN"] - totals["NEW_V50"] == 292, "292 assigned before V50")
    audit.check(479 - totals["RESIDUAL_UNKNOWN"] == 343, "343 assigned after V50")
    audit.check(distribution == Counter({0: 2, 1: 9, 2: 17, 3: 8, 4: 8, 5: 6, 7: 1}), "residual distribution")
    audit.check(Counter(str(row["line_mode"]) for row in line_rows) == Counter({
        "ACTION_SEQUENCE": 11, "MIXED_RECORD": 18,
        "NOMINAL_REGISTER": 14, "QUANTITY_LABEL": 8,
    }), "line-mode profile")
    audit.check(sum(int(row["action_positions"]) for row in line_rows) == 48, "48 actions")
    audit.check(sum(int(row["action_positions"]) > 0 for row in line_rows) == 29, "29 action lines")
    audit.check(sum(row["complete"] == "1" for row in line_rows) == 2, "2 complete lines")
    audit.check(sum(int(row["residual_unknown_positions"]) <= 1 for row in line_rows) == 11, "11 lines at most one gap")
    audit.check(sum(int(row["residual_unknown_positions"]) <= 2 for row in line_rows) == 28, "28 lines at most two gaps")

    f26_mode = mode_by_locus["f26r.2"]
    f26_reader = reader_by_locus["f26r.2"]
    audit.check(f26_mode["action_ordinals"] == "NONE", "f26r.2 action removed")
    audit.check(f26_mode["line_mode"] == "CATALOGUE", "f26r.2 catalogue source mode")
    audit.check(f26_mode["gdt675_render_correction"] == "OVERRIDE_INITIAL_DCHEY_TO_NOMINAL;BIND_AIIN_VALUE_III_TO_NOMINAL_DCHEY", "f26r.2 correction")
    audit.check(f26_reader["line_mode"] == "NOMINAL_REGISTER", "f26r.2 nominal final mode")
    audit.check(f26_reader["working_line_de"].startswith("Abgemessene Trockendroge der Mittelstufe, abgeschlossen · Menge III"), "f26r.2 nominal rendering")
    line_scale_override_loci = sorted(
        row["locus"] for row in mode_specs
        if row["gdt675_render_correction"].startswith("OVERRIDE_")
    )
    audit.check(line_scale_override_loci == ["f26r.2"], "derived line-scale override set")
    audit.check(51 - len(line_scale_override_loci) == 50, "50 line-scale holds derived from override set")
    audit.check("unless an immediately bound value makes it a nominal measured result" in templates[0]["renderer_rule"], "T01 names value exception")
    audit.check("Leser-Rivale olkor/ar" in reader_by_locus["f85r2.5"]["working_line_de"], "f85r2.5 rival visible")
    audit.check("IT2a/RF1b: oltar" in reader_by_locus["f95v1.7"]["working_line_de"], "f95v1.7 rival visible")

    compare_rows(audit, "token reader", ART / "V50_EXTERNAL_TOKEN_READER.tsv", TOKEN_FIELDS, token_rows)
    compare_rows(audit, "line reader", ART / "V50_EXTERNAL_LINE_READER.tsv", LINE_FIELDS, line_rows)

    value_rows: list[dict[str, object]] = []
    value_decisions: Counter[str] = Counter()
    for number, spec in enumerate(value_specs, start=1):
        audit.check(spec["locus"] in line_by_locus, f"value {number}: locus")
        tokens = str(line_by_locus[spec["locus"]]["zl3b_line"]).split()
        heads = parse_ordinals(spec["head_ordinals"])
        values = parse_ordinals(spec["value_ordinals"])
        close = parse_ordinals(spec["close_ordinal"])
        audit.check(bool(heads) and bool(values), f"value {number}: head/value")
        audit.check(len(set(heads + values + close)) == len(heads + values + close), f"value {number}: distinct ordinals")
        audit.check(all(1 <= ordinal <= len(tokens) for ordinal in heads + values + close), f"value {number}: range")
        audit.check(spec["decision"] in {"BIND", "BIND_NOMINAL", "PROVISIONAL", "REJECT_JUMP"}, f"value {number}: decision")
        if spec["decision"] in {"BIND", "BIND_NOMINAL", "PROVISIONAL"}:
            audit.check(min(abs(head - value) for head in heads for value in values) == 1, f"value {number}: local")
        if close:
            audit.check(close == [max(values) + 1], f"value {number}: closing slot")
        value_decisions[spec["decision"]] += 1
        value_rows.append({
            "attachment_id": f"GDT676-V{number:02d}", "locus": spec["locus"],
            "head_ordinals": spec["head_ordinals"],
            "head_surfaces": "|".join(tokens[ordinal - 1] for ordinal in heads),
            "value_ordinals": spec["value_ordinals"],
            "value_surfaces": "|".join(tokens[ordinal - 1] for ordinal in values),
            "close_ordinal": spec["close_ordinal"],
            "close_surface": "|".join(tokens[ordinal - 1] for ordinal in close) or "NONE",
            "decision": spec["decision"], "contextual_reading_de": spec["contextual_reading_de"],
            "note": spec["note"],
        })
    audit.check(value_decisions == Counter({"BIND": 9, "BIND_NOMINAL": 1, "PROVISIONAL": 3, "REJECT_JUMP": 4}), "value decision profile")
    f26_values = [row for row in value_rows if row["locus"] == "f26r.2"]
    audit.check(len(f26_values) == 1, "one f26r.2 value card")
    audit.check(f26_values[0]["head_surfaces"] == "dchey" and f26_values[0]["value_surfaces"] == "aiin", "f26r.2 dchey-aiin")
    audit.check(f26_values[0]["decision"] == "BIND_NOMINAL", "f26r.2 nominal bind")
    value_output_fields = [
        "attachment_id", "locus", "head_ordinals", "head_surfaces", "value_ordinals",
        "value_surfaces", "close_ordinal", "close_surface", "decision",
        "contextual_reading_de", "note",
    ]
    compare_rows(audit, "value audit", ART / "VALUE_ATTACHMENT_AUDIT.tsv", value_output_fields, value_rows)

    ranked = sorted(line_rows, key=lambda row: (
        int(row["residual_unknown_positions"]),
        -int(row["inherited_other_assigned_positions"]),
        int(row["inherited_narrow_carrier_positions"]),
        -int(row["token_count"]), str(row["locus"]),
    ))
    ranking_rows = [{"rank": rank, **row} for rank, row in enumerate(ranked, start=1)]
    low_residual_rows = [row for row in ranking_rows if int(row["residual_unknown_positions"]) <= 2]
    ranking_fields = ["rank", *LINE_FIELDS]
    compare_rows(audit, "line ranking", ART / "LINE_INFORMATION_RANKING.tsv", ranking_fields, ranking_rows)
    compare_rows(audit, "low-residual frontier", ART / "LOW_RESIDUAL_FRONTIER.tsv", ranking_fields, low_residual_rows)
    audit.check([row["locus"] for row in ranked[:10]] == [
        "f112v.10", "f102v2.3", "f80v.27", "f86v6.5", "f106r.23",
        "f86v5.2", "f56r.6", "f77r.38", "f86v5.24", "f107r.40",
    ], "top-ten line ranking")

    page_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in line_rows:
        page_groups[str(row["page"])].append(row)
    page_rows: list[dict[str, object]] = []
    for page, rows in page_groups.items():
        if len(rows) < 2:
            continue
        tokens = sum(int(row["token_count"]) for row in rows)
        residual = sum(int(row["residual_unknown_positions"]) for row in rows)
        surfaces = {str(row["new_surface"]) for row in rows}
        page_rows.append({
            "page": page, "touched_lines": len(rows), "tokens": tokens,
            "residual_unknown": residual, "assigned_fraction": f"{(tokens - residual) / tokens:.6f}",
            "inherited_other_assigned": sum(int(row["inherited_other_assigned_positions"]) for row in rows),
            "inherited_narrow_carrier": sum(int(row["inherited_narrow_carrier_positions"]) for row in rows),
            "distinct_v50_surfaces": len(surfaces), "v50_surfaces": "|".join(sorted(surfaces)),
            "loci": "|".join(str(row["locus"]) for row in rows),
        })
    page_rows.sort(key=lambda row: (
        -float(row["assigned_fraction"]), -int(row["distinct_v50_surfaces"]),
        -int(row["touched_lines"]), -int(row["inherited_other_assigned"]),
        int(row["inherited_narrow_carrier"]), str(row["page"]),
    ))
    page_rows = [{"rank": rank, **row} for rank, row in enumerate(page_rows, start=1)]
    page_output_fields = [
        "rank", "page", "touched_lines", "tokens", "residual_unknown", "assigned_fraction",
        "inherited_other_assigned", "inherited_narrow_carrier", "distinct_v50_surfaces",
        "v50_surfaces", "loci",
    ]
    compare_rows(audit, "page ranking", ART / "PAGE_TRANSFER_RANKING.tsv", page_output_fields, page_rows)
    audit.check(len(page_rows) == 10, "10 multi-contact pages")
    audit.check([row["page"] for row in page_rows[:5]] == ["f80v", "f107r", "f86v5", "f86v6", "f86v3"], "top-five pages")

    passage_rows: list[dict[str, object]] = []
    for spec in passage_specs:
        selected_loci = spec["loci"].split("|")
        audit.check(all(locus in line_by_locus for locus in selected_loci), f"{spec['selection_id']}: loci")
        rows = [line_by_locus[locus] for locus in selected_loci]
        tokens = sum(int(row["token_count"]) for row in rows)
        residual = sum(int(row["residual_unknown_positions"]) for row in rows)
        passage_rows.append({
            "selection_id": spec["selection_id"], "loci": spec["loci"],
            "selection_class": spec["selection_class"], "purpose": spec["purpose"],
            "lines": len(rows), "tokens": tokens, "residual_unknown": residual,
            "assigned_fraction": f"{(tokens - residual) / tokens:.6f}",
            "inherited_other_assigned": sum(int(row["inherited_other_assigned_positions"]) for row in rows),
            "inherited_narrow_carrier": sum(int(row["inherited_narrow_carrier_positions"]) for row in rows),
            "new_v50_positions": sum(int(row["new_v50_positions"]) for row in rows),
            "working_passage_de": " || ".join(str(row["working_line_de"]) for row in rows),
        })
    passage_output_fields = [
        "selection_id", "loci", "selection_class", "purpose", "lines", "tokens",
        "residual_unknown", "assigned_fraction", "inherited_other_assigned",
        "inherited_narrow_carrier", "new_v50_positions", "working_passage_de",
    ]
    compare_rows(audit, "passage deck", ART / "PASSAGE_TEST_DECK.tsv", passage_output_fields, passage_rows)
    audit.check([row["selection_id"] for row in passage_rows] == ["GDT676-S01", "GDT676-S02", "GDT676-S03", "GDT676-S04"], "passage IDs")
    audit.check(passage_rows[0]["loci"] == "f112v.10" and passage_rows[0]["residual_unknown"] == 0, "complete multitoken passage")
    audit.check(passage_rows[2]["loci"] == "f86v6.4|f86v6.5" and passage_rows[2]["tokens"] == 25 and passage_rows[2]["residual_unknown"] == 3, "consecutive OLKAR passage")
    audit.check(passage_rows[3]["loci"] == "f86v3.18|f86v3.19" and passage_rows[3]["tokens"] == 17 and passage_rows[3]["residual_unknown"] == 4, "action-contrast passage")

    profile_rows: list[dict[str, object]] = []
    for axis, field in (("register", "section"), ("language", "language"), ("hand", "hand")):
        groups: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in line_rows:
            groups[str(row[field])].append(row)
        for value, rows in sorted(groups.items()):
            tokens = sum(int(row["token_count"]) for row in rows)
            residual = sum(int(row["residual_unknown_positions"]) for row in rows)
            profile_rows.append({
                "axis": axis, "value": value, "lines": len(rows), "tokens": tokens,
                "new_v50": sum(int(row["new_v50_positions"]) for row in rows),
                "residual_unknown": residual,
                "inherited_narrow_carrier": sum(int(row["inherited_narrow_carrier_positions"]) for row in rows),
                "inherited_other_assigned": sum(int(row["inherited_other_assigned_positions"]) for row in rows),
                "complete_lines": sum(row["complete"] == "1" for row in rows),
                "assigned_fraction": f"{(tokens - residual) / tokens:.6f}",
            })
    profile_output_fields = [
        "axis", "value", "lines", "tokens", "new_v50", "residual_unknown",
        "inherited_narrow_carrier", "inherited_other_assigned", "complete_lines", "assigned_fraction",
    ]
    compare_rows(audit, "register/language/hand profile", ART / "REGISTER_HAND_PROFILE.tsv", profile_output_fields, profile_rows)
    audit.check(len(profile_rows) == 12, "12 aggregate profiles")

    action_expected = [{"locus": row["locus"], **row} for row in mode_specs]
    compare_rows(audit, "action scope", ART / "ACTION_SCOPE_AUDIT.tsv", mode_fields, action_expected)
    compare_rows(audit, "syntax templates", ART / "SYNTAX_TEMPLATE_CARDS.tsv", template_fields, templates)
    audit.check([row["template_id"] for row in templates] == [f"GDT676-T{number:02d}" for number in range(1, 9)], "template IDs")
    rule_rows = [
        {"priority": 0, "rule_id": "HARD_GENERIC_PREFLIGHT_VETO", "predicate": GENERIC_FILLER.pattern, "output": "REJECT_RENDER"},
        {"priority": 1, "rule_id": "NEW_V50", "predicate": "ordinal in applied_ordinals", "output": "NEW_V50"},
        {"priority": 2, "rule_id": "RESIDUAL_UNKNOWN", "predicate": "ordinal in remaining_unknown_ordinals", "output": "RESIDUAL_UNKNOWN"},
        {"priority": 3, "rule_id": "INHERITED_NARROW_CARRIER", "predicate": NARROW_CARRIER.pattern, "output": "INHERITED_NARROW_CARRIER"},
        {"priority": 4, "rule_id": "INHERITED_OTHER_ASSIGNED", "predicate": "otherwise", "output": "INHERITED_OTHER_ASSIGNED"},
    ]
    compare_rows(audit, "renderer rules", ART / "RENDERER_RULE_CARDS.tsv", ["priority", "rule_id", "predicate", "output"], rule_rows)
    category_rows: list[dict[str, object]] = [
        {"category": category, "positions": totals[category], "denominator": 479,
         "share": f"{totals[category] / 479:.6f}"}
        for category in ("NEW_V50", "RESIDUAL_UNKNOWN", "INHERITED_NARROW_CARRIER", "INHERITED_OTHER_ASSIGNED")
    ]
    category_rows.extend([
        {"category": "LITERAL_NARROW_CARRIER_POSITIONS", "positions": 105, "denominator": 479, "share": "0.219207"},
        {"category": "LITERAL_NARROW_CARRIER_MATCHES", "positions": 106, "denominator": 479, "share": "0.221294"},
        {"category": "WORKING_NARROW_CARRIER_POSITIONS", "positions": 113, "denominator": 479, "share": "0.235908"},
        {"category": "WORKING_NARROW_CARRIER_MATCHES", "positions": 114, "denominator": 479, "share": "0.237996"},
        {"category": "ASSIGNED_EXTENDED_CLASS_CARRIER_POSITIONS", "positions": 311, "denominator": 343, "share": "0.906706"},
        {"category": "LITERAL_HARD_GENERIC_MATCHES", "positions": 0, "denominator": 479, "share": "0.000000"},
        {"category": "WORKING_HARD_GENERIC_MATCHES", "positions": 0, "denominator": 479, "share": "0.000000"},
    ])
    compare_rows(audit, "information counts", ART / "INFORMATION_CATEGORY_COUNTS.tsv", ["category", "positions", "denominator", "share"], category_rows)

    document_lines = [
        "# GDT676 — V50 external 51-line working reader", "",
        "Every source token remains visible. `⟦surface:?⟧` is an unresolved position; broad carriers remain named rather than silently concretized.", "",
    ]
    for row in line_rows:
        document_lines.extend([
            f"## {row['locus']} · {row['line_mode']}", "",
            f"**ZL3b:** `{row['zl3b_line']}`", "",
            f"**Tokenwerte:** {row['literal_token_glosses_de']}", "",
            f"**Arbeitslesung:** {row['working_line_de']}", "",
            f"**Aktionen:** {row['action_ordinals']} ({row['action_surfaces']})", "",
            f"**Rest:** {row['residual_unknown_positions']} offen; {row['remaining_unknown_surfaces']}", "",
            f"**Audit:** {row['review_note']}", "",
        ])
    expected_document = "\n".join(document_lines).rstrip() + "\n"
    audit.check((ART / "GDT676_V50_EXTERNAL_WORKING_READER.md").read_text(encoding="utf-8") == expected_document, "working-reader document")

    builder_artifacts = [
        "ACTION_SCOPE_AUDIT.tsv", "GDT676_V50_EXTERNAL_WORKING_READER.md",
        "INFORMATION_CATEGORY_COUNTS.tsv", "LINE_INFORMATION_RANKING.tsv",
        "LOW_RESIDUAL_FRONTIER.tsv", "PAGE_TRANSFER_RANKING.tsv", "PASSAGE_TEST_DECK.tsv",
        "REGISTER_HAND_PROFILE.tsv", "RENDERER_RULE_CARDS.tsv", "SYNTAX_TEMPLATE_CARDS.tsv",
        "V50_EXTERNAL_LINE_READER.tsv", "V50_EXTERNAL_TOKEN_READER.tsv", "VALUE_ATTACHMENT_AUDIT.tsv",
    ]
    file_hashes = {name: sha256(ART / name) for name in sorted(builder_artifacts)}
    expected_result = {
        "status": EXPECTED_STATUS,
        "basis": {
            "touched_lines": 51, "tokens": 479, "pages": 36, "new_pages_opened": 0,
            "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "gdt675_status": EXPECTED_GDT675_STATUS,
        },
        "information": {
            "unknown_before_v50": 187, "unknown_after_v50": 136,
            "assigned_before_v50": 292, "assigned_after_v50": 343,
            "assigned_fraction_before": "0.609603", "assigned_fraction_after": "0.716075",
            "new_v50_positions": 51, "inherited_narrow_carrier_positions": 77,
            "inherited_other_assigned_positions": 215,
            "literal_narrow_carrier_positions": 105, "literal_narrow_carrier_matches": 106,
            "working_narrow_carrier_positions": 113, "working_narrow_carrier_matches": 114,
            "assigned_extended_class_carrier_positions": 311,
            "assigned_extended_class_carrier_fraction": "0.906706",
            "literal_hard_generic_matches": 0, "working_hard_generic_matches": 0,
        },
        "lines": {
            "complete": 2, "with_residual_unknown": 49, "at_most_one_unknown": 11,
            "at_most_two_unknown": 28,
            "unknown_distribution": {"0": 2, "1": 9, "2": 17, "3": 8, "4": 8, "5": 6, "7": 1},
            "modes": {"ACTION_SEQUENCE": 11, "MIXED_RECORD": 18, "NOMINAL_REGISTER": 14, "QUANTITY_LABEL": 8},
            "licensed_action_positions": 48, "lines_with_licensed_action": 29,
        },
        "renderer": {
            "gdt675_applications_hold_at_line_scale": 50, "named_line_scale_overrides": 1,
            "override_locus": "f26r.2",
            "override": "initial dchey becomes a nominal measured dry result before adjacent quantity III",
            "value_bindings": 10, "provisional_value_bindings": 3,
            "rejected_value_jumps": 4, "syntax_templates": 8,
        },
        "next_frontier": {
            "low_residual_lines": 28, "best_complete_multitoken": "f112v.10",
            "best_consecutive_passage": "f86v6.4|f86v6.5",
            "best_action_contrast_passage": "f86v3.18|f86v3.19",
        },
        "files": file_hashes, "claim_ceiling": EXPECTED_CLAIM_CEILING,
    }
    actual_result = read_json(ART / "RESULT.json")
    audit.check(isinstance(actual_result, dict), "GDT676 RESULT object")
    audit.check(actual_result == expected_result, "full RESULT reconstruction")
    assert isinstance(actual_result, dict)
    audit.check(set(actual_result["files"]) == set(builder_artifacts), "RESULT file set")
    for name in builder_artifacts:
        audit.check(actual_result["files"][name] == sha256(ART / name), f"RESULT hash {name}")

    replay_names = [*builder_artifacts, "RESULT.json"]
    before_replay = {name: (ART / name).read_bytes() for name in replay_names}
    replay = subprocess.run(
        [sys.executable, str(BUILDER_PATH)], cwd=ROOT, text=True,
        capture_output=True, timeout=120, check=False,
    )
    audit.check(replay.returncode == 0, f"builder replay exit: {replay.stderr.strip()}")
    replay_lines = [line for line in replay.stdout.splitlines() if line.strip()]
    audit.check(len(replay_lines) == 1, "builder emits one summary line")
    replay_summary = json.loads(replay_lines[0])
    audit.check(replay_summary["status"] == EXPECTED_STATUS, "builder replay status")
    for name in replay_names:
        audit.check((ART / name).read_bytes() == before_replay[name], f"byte-identical replay {name}")
    audit.check(read_json(ART / "RESULT.json") == expected_result, "RESULT unchanged after replay")

    validation = {
        "status": "PASS", "experiment_id": "GDT676", "passed_checks": audit.checks,
        "independent_reconstruction": {
            "lines": 51, "tokens": 479, "pages": 36,
            "information_categories": {
                "NEW_V50": 51, "RESIDUAL_UNKNOWN": 136,
                "INHERITED_NARROW_CARRIER": 77, "INHERITED_OTHER_ASSIGNED": 215,
            },
            "assigned_before": 292, "assigned_after": 343,
            "literal_narrow_carrier_positions": 105, "literal_narrow_carrier_matches": 106,
            "working_narrow_carrier_positions": 113, "working_narrow_carrier_matches": 114,
            "assigned_extended_class_carrier_positions": 311,
            "assigned_extended_class_carrier_fraction": "0.906706",
            "literal_hard_generic_matches": 0, "working_hard_generic_matches": 0,
            "complete_lines": 2, "licensed_action_positions": 48,
            "lines_with_licensed_action": 29,
            "line_modes": {
                "ACTION_SEQUENCE": 11, "MIXED_RECORD": 18,
                "NOMINAL_REGISTER": 14, "QUANTITY_LABEL": 8,
            },
            "f26r2_override": "NOMINAL_DCHEY_PLUS_AIIN_VALUE_III",
            "value_decisions": {
                "BIND": 9, "BIND_NOMINAL": 1, "PROVISIONAL": 3, "REJECT_JUMP": 4,
            },
            "low_residual_lines": 28,
        },
        "builder_replay": {
            "status": "BYTE_IDENTICAL", "files": len(replay_names),
            "builder_status": EXPECTED_STATUS,
        },
        "validated_artifact_sha256": file_hashes,
    }
    VALIDATION_PATH.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "PASS", "checks": audit.checks, "lines": 51, "tokens": 479,
        "assigned_after": 343, "open": 136, "builder_replay": "BYTE_IDENTICAL",
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
