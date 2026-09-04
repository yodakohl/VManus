#!/usr/bin/env python3
"""Build GDT805's discovery-subtracted whole-context discriminator."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt805_eleven_whole_context_role_discriminator"
SRC = EXP / "src"
ART = EXP / "artifacts"

G800_OCCURRENCES = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
G802_CONTEXTS = ROOT / "experiments/yolo/gdt802_masked_lm_neighbour_context_transfer/artifacts/GDT802_4137_MASKED_NEIGHBOUR_ATLAS.tsv"
G803_BRACKETS = ROOT / "experiments/yolo/gdt803_recurrent_context_rarity_discriminator/artifacts/GDT803_12_BIDIRECTIONAL_BRACKETS.tsv"
G804_CENSUS = ROOT / "experiments/yolo/gdt804_bracket_middle_independent_field_bridge/artifacts/GDT804_11_MIDDLE_CENSUS.tsv"
G804_CONTROLS = ROOT / "experiments/yolo/gdt804_bracket_middle_independent_field_bridge/artifacts/GDT804_NEAREST_CONTROL_POOLS.tsv"
G804_UNION = ROOT / "experiments/yolo/gdt804_bracket_middle_independent_field_bridge/artifacts/GDT804_30_TARGET_UNION_CELLS.tsv"
G804_RESULT = ROOT / "experiments/yolo/gdt804_bracket_middle_independent_field_bridge/artifacts/RESULT.json"
G739_WINDOWS = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/artifacts/WINDOW_202_TOKEN_AUDIT.tsv"
G739_AXES = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/ANCHOR_AXIS_SPECS.tsv"
G754_DECISIONS = ROOT / "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
G738_HOLDS = ROOT / "experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/artifacts/MANUAL_HOLD_AUDIT.tsv"
G734_LINES = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
G734_CELLS = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv"
G631_ALLOWLIST = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
G634_RUN = ROOT / "experiments/yolo/gdt634_known_core_terminal_semantics/src/run.py"
TOKENS_RAW = ROOT / "transcription/voynich_zl3b_tokens.tsv"
CROSS_RAW = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
TARGET_MODELS = SRC / "TARGET_CANDIDATE_MODELS.tsv"
VMANUS_EXP = ROOT / "vmanus-exp"
GUARDED_QUERY_TOOL = ROOT / "tools/guarded_tsv_query.py"
EXPERIMENT_TOOL = ROOT / "tools/vmanus_experiment.py"
EDGE_VALIDATOR = ROOT / "tools/relation_edge_intake.py"

AXIS_GERMAN = {
    "HOT": "Wärme-/Heißfeld",
    "COLD": "Kältefeld",
    "DRY": "Trockenfeld",
    "MOIST": "Feuchtefeld",
    "AMOUNT": "Mengen-/Maßfeld",
    "VALUE": "Wert-/Gradfeld",
    "PART": "Teil-/Fraktionsfeld",
    "MATERIAL": "Stoff-/Materialfeld",
    "PREPARATION": "Zubereitungsfeld",
    "PROCESS": "Vorgangs-/Prozessfeld",
    "CLOSE": "Abschluss-/Ergebnisfeld",
    "PASS": "Durchgangs-/Fortsetzungsfeld",
}

OUTPUT_NAMES = (
    "SOURCE_LOCK.tsv",
    "GDT805_GUARDED_QUERY_STATS.tsv",
    "GDT805_131_GDT739_SURFACE_PROJECTION_AUDIT.tsv",
    "GDT805_1086_EXTERNAL_CONTEXT_ATLAS.tsv",
    "GDT805_11_CONTEXT_CAPACITY.tsv",
    "GDT805_NEIGHBOUR_IDENTITY_PROFILE.tsv",
    "GDT805_ROLE_CONTACT_PROFILE.tsv",
    "GDT805_K12_ROLE_COMPARISON.tsv",
    "GDT805_ROLE_LEADS.tsv",
    "GDT805_13_REPEATED_FRAME_TYPES.tsv",
    "GDT805_CANDIDATE_SCORECARD.tsv",
    "GDT805_11_CANDIDATE_ADJUDICATION.tsv",
    "GDT805_45_PASSAGE_CARDS.tsv",
    "GDT805_GDT388_CONTEXT_EDGE_PACKET.tsv",
    "GDT805_GDT388_EDGE_INTAKE.json",
    "GDT805_STRUCTURAL_CARD.tsv",
    "RESULT.json",
)

EDGE_FIELDS = (
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
    "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
    "relation_type", "direction_basis", "ownership_basis",
    "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
    "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer",
    "relation_reviewer", "relation_confidence", "ambiguity_state",
    "formal_access_state", "fold_assignment", "eligibility_status",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def f12(value: float) -> str:
    return f"{value:.12g}"


def assert_unsealed(rows: Iterable[dict[str, Any]]) -> None:
    for row in rows:
        for field in ("page", "source_selector", "locus", "physical_folio"):
            value = str(row.get(field, ""))
            if value.startswith("f84"):
                raise AssertionError(f"sealed selector reached GDT805: {field}={value}")


def guarded_query(
    path: Path, pages: set[str], columns: Sequence[str], label: str,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    command = [str(VMANUS_EXP), "query-tsv", relative(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend((
        "--columns", ",".join(columns),
        "--forbid-prefix", "f84", "--forbid-prefix", "f84r",
    ))
    completed = subprocess.run(
        command, cwd=ROOT, check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr or f"guarded {label} query failed")
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError(f"guard statistics missing for {label}")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    assert_unsealed(rows)
    stats = json.loads(stats_lines[0][12:])
    return rows, {
        "query_id": label,
        "source_path": relative(path),
        "selector": "page",
        "allowed_values": len(pages),
        "output_columns": ",".join(columns),
        "forbidden_prefixes": "f84|f84r",
        "selected_rows": stats["selected"],
        "skipped_forbidden_rows": stats["skipped_forbidden"],
        "skipped_not_allowed_rows": stats["skipped_not_allowed"],
    }


def source_lock() -> list[dict[str, str]]:
    inputs = (
        G800_OCCURRENCES, G802_CONTEXTS, G803_BRACKETS, G804_CENSUS,
        G804_CONTROLS, G804_UNION, G804_RESULT, G739_WINDOWS, G739_AXES,
        G754_DECISIONS, G738_HOLDS,
        G734_LINES, G734_CELLS, G631_ALLOWLIST, G634_RUN, TOKENS_RAW,
        CROSS_RAW, TARGET_MODELS, VMANUS_EXP, GUARDED_QUERY_TOOL,
        EXPERIMENT_TOOL, EDGE_VALIDATOR,
    )
    purposes = {
        G800_OCCURRENCES: "exact paired-terminal occurrence identity and metadata",
        G802_CONTEXTS: "4137 masked exact L1 and R1 context joins",
        G803_BRACKETS: "twelve exact discovery occurrence IDs to subtract",
        G804_CENSUS: "fixed eleven-target cohort and field/amount context candidates",
        G804_CONTROLS: "fixed outcome-blind K12 control pools",
        G804_UNION: "occurrence-local field proximity and positional amount candidates",
        G804_RESULT: "published GDT804 marginal and scope checks",
        G739_WINDOWS: "position-scoped GDT739 neighbour roles audited for a new projection",
        G739_AXES: "fixed broad axis tag definitions",
        G754_DECISIONS: "later quarantine of source-composed whole readings",
        G738_HOLDS: "manual hold inventory for retired literal readings",
        G734_LINES: "cached complete ZL3b lines for exact passage parity",
        G734_CELLS: "32339 cached ordinal-surface parity cells",
        G631_ALLOWLIST: "inherited 179-page selector allow-list",
        G634_RUN: "published token-rank stability definition",
        TOKENS_RAW: "guarded ZL3b tokens for exact context stability",
        CROSS_RAW: "guarded alternate-reader lines for sequence stability",
        TARGET_MODELS: "replaceable concrete whole-form rival deck",
        VMANUS_EXP: "guarded query and edge-packet dispatcher",
        GUARDED_QUERY_TOOL: "selector-before-materialization implementation",
        EXPERIMENT_TOOL: "sealed-selector and manifest implementation",
        EDGE_VALIDATOR: "GDT388 relation-packet intake validator",
    }
    return [
        {"path": relative(path), "sha256": sha256(path), "purpose": purposes[path]}
        for path in inputs
    ]


def build_anchor_deck(
    targets: set[str],
) -> tuple[
    list[dict[str, Any]],
    dict[str, tuple[str, ...]],
    dict[tuple[str, str, int, str], tuple[str, ...]],
]:
    """Audit GDT739 neighbours and expose only an explicit GDT805 projection.

    GDT739 licensed roles at enumerated positions, not a global surface
    dictionary.  The surface lookup below is therefore an exploratory GDT805
    covariate with zero renderer/semantic credit.  Exact active-radius source
    cells are retained separately so passage cards can distinguish inherited
    local evidence from the new projection.
    """
    windows = read_tsv(G739_WINDOWS)
    selected = [row for row in windows if row["eligible_local_anchor"] == "1"]
    if len(selected) != 230:
        raise AssertionError("GDT739 eligible neighbour-contact capacity drift")
    g754_quarantine = {row["surface"] for row in read_tsv(G754_DECISIONS)}
    g738_holds = {row["surface"] for row in read_tsv(G738_HOLDS)}
    if len(g754_quarantine) != 172 or len(g738_holds) != 14:
        raise AssertionError("later whole-reading quarantine capacity drift")
    grouped: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected:
        required = (
            row["neighbor_reader_exact"] == "1",
            row["neighbor_unknown_v99r7"] == "0",
            row["neighbor_composition_semantic_credit"] == "0",
            row["strict_initial_head_neighbor"] == "0",
            row["another_gdt738_target"] == "0",
            row["retired_patient_words"] == "NONE",
            row["axis_tags"] != "NONE",
            row["neighbor_confidence_level"].startswith(("W2", "W3")),
            row["head_or_body_lexeme_credit"] == "0",
            row["component_export_credit"] == "0",
        )
        if not all(required):
            raise AssertionError(f"eligible GDT739 neighbour violates source gate: {row['window_id']}")
        grouped[row["neighbor_surface"]].append(row)
    if len(grouped) != 131:
        raise AssertionError("GDT739 deduplicated neighbour-surface capacity drift")
    if sum(int(row["distance"]) <= 2 for row in selected) != 124:
        raise AssertionError("GDT739 active-radius contact capacity drift")
    if sum(any(int(row["distance"]) <= 2 for row in rows) for rows in grouped.values()) != 87:
        raise AssertionError("GDT739 active-radius surface capacity drift")
    if len(set(grouped) & g754_quarantine) != 14:
        raise AssertionError("GDT754/GDT739 quarantine overlap drift")

    output: list[dict[str, Any]] = []
    projection_lookup: dict[str, tuple[str, ...]] = {}
    exact_active_cells: dict[tuple[str, str, int, str], tuple[str, ...]] = {}
    for index, (surface, rows) in enumerate(sorted(grouped.items()), start=1):
        tag_sets = {tuple(row["axis_tags"].split("|")) for row in rows}
        if len(tag_sets) != 1:
            raise AssertionError(f"inconsistent GDT739 tags for {surface}")
        tags = next(iter(tag_sets))
        active_rows = [row for row in rows if int(row["distance"]) <= 2]
        blocked = []
        if not active_rows:
            blocked.append("GDT739_DISCOVERY_RADIUS_ONLY")
        if surface in g754_quarantine:
            blocked.append("GDT754_SOURCE_COMPOSITION_QUARANTINE")
        if surface in g738_holds:
            blocked.append("GDT738_MANUAL_HOLD")
        if surface in targets:
            blocked.append("GDT805_TARGET_MASK")
        allowed = not blocked
        if allowed:
            projection_lookup[surface] = tags
            for row in active_rows:
                key = (row["page"], row["locus"], int(row["neighbor_ordinal"]), surface)
                previous = exact_active_cells.setdefault(key, tags)
                if previous != tags:
                    raise AssertionError(f"conflicting exact GDT739 cell tags: {key}")
        output.append({
            "projection_audit_id": f"G805-A{index:03d}",
            "surface": surface,
            "axis_tags": "|".join(tags),
            "axis_displays_de": "|".join(AXIS_GERMAN[tag] for tag in tags),
            "gdt739_all_radius_contacts": len(rows),
            "gdt739_active_radius_contacts": len(active_rows),
            "gdt739_active_radius_pages": len({row["page"] for row in active_rows}),
            "gdt739_active_radius_loci": len({row["locus"] for row in active_rows}),
            "source_radius_tier": "ACTIVE_RADIUS_SOURCE" if active_rows else "DISCOVERY_RADIUS_ONLY",
            "confidence_levels": "|".join(sorted({row["neighbor_confidence_level"] for row in rows})),
            "gdt754_quarantined": int(surface in g754_quarantine),
            "gdt738_hold": int(surface in g738_holds),
            "is_gdt805_target": int(surface in targets),
            "primary_surface_projection_allowed": int(allowed),
            "projection_exclusion_reason": "|".join(blocked) or "NONE",
            "german_working_string_imported": 0,
            "axis_tags_derived_from_german_working_prose": 1,
            "renderer_license": 0,
            "semantic_credit": 0,
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output, projection_lookup, exact_active_cells


def contiguous_count(tokens: Sequence[str], gram: tuple[str, ...]) -> int:
    width = len(gram)
    return sum(tuple(tokens[index:index + width]) == gram for index in range(len(tokens) - width + 1))


class ReaderContext:
    def __init__(self) -> None:
        pages = {row["page"] for row in read_tsv(G631_ALLOWLIST)}
        if len(pages) != 179 or any(page.startswith("f84") for page in pages):
            raise AssertionError("inherited allow-list drift")
        token_columns = ("page", "locus", "token_index", "eva", "section", "language", "hand")
        cross_columns = (
            "page", "locus", "all_three_present", "all_present_exact",
            "zl3b_clean", "it2a_clean", "rf1b_clean",
        )
        tokens, token_stats = guarded_query(TOKENS_RAW, pages, token_columns, "ZL3B_TOKENS")
        cross, cross_stats = guarded_query(CROSS_RAW, pages, cross_columns, "CROSS_READER_LINES")
        if len(tokens) != 32339 or len(cross) != 4137:
            raise AssertionError("guarded reader capacity drift")
        self.stats = [token_stats, cross_stats]
        self.by_locus: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
        for row in tokens:
            self.by_locus[row["locus"]].append(row)
        for rows in self.by_locus.values():
            rows.sort(key=lambda row: int(row["token_index"]))
        self.cross = {row["locus"]: row for row in cross}
        if len(self.cross) != len(cross):
            raise AssertionError("cross-reader locus duplication")
        self.reader_tokens = {
            locus: {
                name: tuple(row[name].split())
                for name in ("zl3b_clean", "it2a_clean", "rf1b_clean")
            }
            for locus, row in self.cross.items()
        }
        self.token_stable: dict[tuple[str, int], int] = {}
        for locus, rows in self.by_locus.items():
            ranks: Counter[str] = Counter()
            reader = self.reader_tokens[locus]
            for row in rows:
                surface = row["eva"]
                ranks[surface] += 1
                caps = [reader[name].count(surface) for name in reader]
                self.token_stable[(locus, int(row["token_index"]))] = int(ranks[surface] <= min(caps))
        self._sequence_cache: dict[tuple[str, int, int], int] = {}
        self._boundary_cache: dict[tuple[str, int, int, int, int], int] = {}
        self._verify_cached_parity(tokens)

    def _verify_cached_parity(self, tokens: list[dict[str, str]]) -> None:
        cells = read_tsv(G734_CELLS)
        if len(cells) != 32339:
            raise AssertionError("GDT734 cell capacity drift")
        cell_map = {(row["locus"], int(row["token_ordinal"])): row["surface"] for row in cells}
        if len(cell_map) != 32339:
            raise AssertionError("GDT734 cell key duplication")
        for row in tokens:
            if cell_map[(row["locus"], int(row["token_index"]))] != row["eva"]:
                raise AssertionError("guarded/GDT734 token parity drift")
        lines = read_tsv(G734_LINES)
        if len(lines) != 4128:
            raise AssertionError("GDT734 line capacity drift")
        line_map = {row["locus"]: row["zl3b_line"] for row in lines}
        if len(line_map) != 4128:
            raise AssertionError("GDT734 line key duplication")
        for locus, rows in self.by_locus.items():
            if " ".join(row["eva"] for row in rows) != line_map[locus]:
                raise AssertionError("guarded/GDT734 line parity drift")

    def sequence_stable(self, locus: str, start: int, width: int) -> int:
        """Rank-identical contiguous n-gram capacity in all three readers."""
        key = (locus, start, width)
        if key in self._sequence_cache:
            return self._sequence_cache[key]
        zl = self.reader_tokens[locus]["zl3b_clean"]
        gram = tuple(zl[start:start + width])
        rank = sum(tuple(zl[index:index + width]) == gram for index in range(start + 1))
        caps = [contiguous_count(self.reader_tokens[locus][name], gram) for name in self.reader_tokens[locus]]
        value = int(rank <= min(caps))
        self._sequence_cache[key] = value
        return value

    def boundary_span_stable(
        self, locus: str, start: int, width: int, bol: int, eol: int,
    ) -> int:
        key = (locus, start, width, bol, eol)
        if key in self._boundary_cache:
            return self._boundary_cache[key]
        zl = self.reader_tokens[locus]["zl3b_clean"]
        gram = tuple(zl[start:start + width])
        hits = []
        for reader in self.reader_tokens[locus].values():
            ok = True
            if bol:
                ok = ok and tuple(reader[:width]) == gram
            if eol:
                ok = ok and tuple(reader[-width:]) == gram
            if not bol and not eol:
                ok = contiguous_count(reader, gram) > 0
            hits.append(ok)
        value = int(all(hits))
        self._boundary_cache[key] = value
        return value


def axis_fields(
    surface: str, page: str, locus: str, ordinal: int,
    targets: set[str], projections: dict[str, tuple[str, ...]],
    exact_active_cells: dict[tuple[str, str, int, str], tuple[str, ...]],
) -> tuple[str, str, str]:
    if surface == "NONE":
        return "BOUNDARY", "BOUNDARY", "Zeilenrand"
    if surface in targets:
        return "TARGET_WHOLE", "TARGET_WHOLE_NO_SEMANTIC_CREDIT", f"{surface}-Zielganzform"
    tags = projections.get(surface)
    if tags is None:
        return "UNMAPPED", "NONE", f"[{surface}:?]"
    display = "/".join(AXIS_GERMAN[tag] for tag in tags)
    key = (page, locus, ordinal, surface)
    if exact_active_cells.get(key) == tags:
        return "GDT739_EXACT_ACTIVE_CELL", "|".join(tags), display
    return "GDT805_EXPLORATORY_SURFACE_AXIS_PROJECTION", "|".join(tags), f"[Kandidat: {display}]"


def build_context_event(
    row: dict[str, str], base: dict[str, str], reader: ReaderContext,
    targets: set[str], projections: dict[str, tuple[str, ...]],
    exact_active_cells: dict[tuple[str, str, int, str], tuple[str, ...]],
    union: dict[tuple[str, str, int, str], dict[str, str]],
) -> dict[str, Any]:
    locus = row["locus"]
    index1 = int(row["token_index"])
    index0 = index1 - 1
    line_rows = reader.by_locus[locus]
    line_tokens = [item["eva"] for item in line_rows]
    surface = base["surface"]
    if line_tokens[index0] != surface:
        raise AssertionError(f"occurrence/token join drift: {row['occurrence_id']}")
    l1 = line_tokens[index0 - 1] if index0 >= 1 else "NONE"
    l2 = line_tokens[index0 - 2] if index0 >= 2 else "NONE"
    r1 = line_tokens[index0 + 1] if index0 + 1 < len(line_tokens) else "NONE"
    r2 = line_tokens[index0 + 2] if index0 + 2 < len(line_tokens) else "NONE"
    if l1 != row["left_context"] or r1 != row["right_context"]:
        raise AssertionError(f"GDT802 immediate-context drift: {row['occurrence_id']}")
    left_kind, left_tags, left_default = axis_fields(
        l1, base["page"], locus, index1 - 1, targets, projections, exact_active_cells,
    )
    right_kind, right_tags, right_default = axis_fields(
        r1, base["page"], locus, index1 + 1, targets, projections, exact_active_cells,
    )
    left_pair = reader.sequence_stable(locus, index0 - 1, 2) if l1 != "NONE" else 0
    right_pair = reader.sequence_stable(locus, index0, 2) if r1 != "NONE" else 0
    left_l2 = reader.sequence_stable(locus, index0 - 2, 3) if l2 != "NONE" else 0
    right_r2 = reader.sequence_stable(locus, index0, 3) if r2 != "NONE" else 0
    frame = reader.sequence_stable(locus, index0 - 1, 3) if l1 != "NONE" and r1 != "NONE" else 0
    full5 = reader.sequence_stable(locus, index0 - 2, 5) if l2 != "NONE" and r2 != "NONE" else 0
    bol_stable = reader.boundary_span_stable(locus, 0, min(2, len(line_tokens)), 1, int(len(line_tokens) <= 2)) if index0 == 0 else 0
    eol_start = max(0, len(line_tokens) - 2)
    eol_stable = reader.boundary_span_stable(locus, eol_start, len(line_tokens) - eol_start, int(len(line_tokens) <= 2), 1) if index0 == len(line_tokens) - 1 else 0
    local = union.get((base["page"], locus, index1, surface), {})
    return {
        "occurrence_id": row["occurrence_id"],
        "source_selector": base["page"],
        "physical_folio": row["physical_folio"],
        "locus": locus,
        "section": base["section"],
        "language": base["language"],
        "hand": base["hand"],
        "token_index": index1,
        "token_count": len(line_tokens),
        "position_class": base["position_class"],
        "surface": surface,
        "l2_surface": l2,
        "l1_surface": l1,
        "r1_surface": r1,
        "r2_surface": r2,
        "exact_five_window": " ".join(token for token in (l2, l1, surface, r1, r2) if token != "NONE"),
        "target_token_stable_all_three": reader.token_stable[(locus, index1)],
        "l1_token_stable_all_three": reader.token_stable.get((locus, index1 - 1), 0),
        "r1_token_stable_all_three": reader.token_stable.get((locus, index1 + 1), 0),
        "l1_pair_sequence_stable_all_three": left_pair,
        "r1_pair_sequence_stable_all_three": right_pair,
        "l2_chain_sequence_stable_all_three": left_l2,
        "r2_chain_sequence_stable_all_three": right_r2,
        "l1_target_r1_sequence_stable_all_three": frame,
        "l2_to_r2_sequence_stable_all_three": full5,
        "bol_target_stable_all_three": bol_stable,
        "target_eol_stable_all_three": eol_stable,
        "l1_anchor_kind": left_kind,
        "l1_axis_tags": left_tags,
        "l1_axis_default_de": left_default,
        "r1_anchor_kind": right_kind,
        "r1_axis_tags": right_tags,
        "r1_axis_default_de": right_default,
        "gdt804_common_mask_field_hit": local.get("common_mask_field_hit", "0"),
        "gdt804_positioned_amount_neighbour_hit": local.get("positioned_amount_neighbour_hit", "0"),
        "gdt804_clean_content_contact": local.get("gdt760_clean_content_contact", "0"),
        "full_zl3b_line": " ".join(line_tokens),
        "semantic_credit": "SURFACE_AXIS_PROJECTION_ZERO_SEMANTIC_CREDIT",
        "confirmed_plaintext": 0,
        "confirmed_lexeme": 0,
        "component_export_credit": 0,
    }


def entropy_profile(values: Sequence[str]) -> tuple[int, int, str, str, str]:
    counts = Counter(value for value in values if value != "NONE")
    total = sum(counts.values())
    if not counts:
        return 0, 0, "0", "0", "0"
    entropy = -sum((count / total) * math.log(count / total) for count in counts.values())
    normalized = entropy / math.log(len(counts)) if len(counts) > 1 else 0.0
    top = sorted(counts.values(), reverse=True)
    return len(counts), total, f12(normalized), f12(top[0] / total), f12(sum(top[:5]) / total)


def axes_for_event(row: dict[str, Any], side: str) -> tuple[str, ...]:
    value = str(row[f"{side}_axis_tags"])
    if value in {"NONE", "BOUNDARY", "TARGET_WHOLE_NO_SEMANTIC_CREDIT"}:
        return ()
    return tuple(value.split("|"))


def profile_axis(events: Sequence[dict[str, Any]], side: str, axis: str) -> dict[str, Any]:
    stable_field = f"{side}_pair_sequence_stable_all_three"
    contacts = [row for row in events if axis in axes_for_event(row, side)]
    stable_opportunities = [row for row in events if int(row[stable_field])]
    stable_contacts = [row for row in contacts if int(row[stable_field])]
    return {
        "opportunities": len(events),
        "stable_opportunities": len(stable_opportunities),
        "contacts": len(contacts),
        "pages": len({row["physical_folio"] for row in contacts}),
        "stable_contacts": len(stable_contacts),
        "stable_pages": len({row["physical_folio"] for row in stable_contacts}),
        "rate": len(contacts) / len(events) if events else 0.0,
        "stable_rate": len(stable_contacts) / len(stable_opportunities) if stable_opportunities else 0.0,
    }


def build_identity_profiles(events: Sequence[dict[str, Any]], targets: Sequence[str]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    grouped: defaultdict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in events:
        for side in ("l1", "r1"):
            grouped[(str(row["surface"]), side, str(row[f"{side}_surface"]))].append(row)
    for index, ((surface, side, neighbor), rows) in enumerate(sorted(grouped.items()), start=1):
        output.append({
            "identity_profile_id": f"G805-I{index:04d}",
            "surface": surface,
            "side": side.upper(),
            "neighbour_surface": neighbor,
            "anchor_kind": rows[0][f"{side}_anchor_kind"],
            "axis_tags": rows[0][f"{side}_axis_tags"],
            "external_occurrences": len(rows),
            "physical_folios": len({row["physical_folio"] for row in rows}),
            "target_token_stable_occurrences": sum(int(row["target_token_stable_all_three"]) for row in rows),
            "neighbour_token_stable_occurrences": sum(int(row[f"{side}_token_stable_all_three"]) for row in rows),
            "pair_sequence_stable_occurrences": sum(int(row[f"{side}_pair_sequence_stable_all_three"]) for row in rows),
            "pair_sequence_stable_folios": len({row["physical_folio"] for row in rows if int(row[f"{side}_pair_sequence_stable_all_three"])}),
            "semantic_credit": "0",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    if {row["surface"] for row in output} != set(targets) - {"okail"}:
        raise AssertionError("identity profile target coverage drift")
    return output


def build_capacity(
    all_target: Sequence[dict[str, Any]], external: Sequence[dict[str, Any]], targets: Sequence[str],
) -> list[dict[str, Any]]:
    by_all: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    by_ext: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_target:
        by_all[str(row["surface"])].append(row)
    for row in external:
        by_ext[str(row["surface"])].append(row)
    output: list[dict[str, Any]] = []
    for surface in targets:
        rows, ext = by_all[surface], by_ext[surface]
        lu, ln, le, lt1, lt5 = entropy_profile([str(row["l1_surface"]) for row in ext])
        ru, rn, re_, rt1, rt5 = entropy_profile([str(row["r1_surface"]) for row in ext])
        axes = {axis for row in ext for side in ("l1", "r1") for axis in axes_for_event(row, side)}
        output.append({
            "surface": surface,
            "total_l_occurrences": len(rows),
            "discovery_occurrences_subtracted": len(rows) - len(ext),
            "external_occurrences": len(ext),
            "external_source_selectors": len({row["source_selector"] for row in ext}),
            "external_physical_folios": len({row["physical_folio"] for row in ext}),
            "target_token_stable_external": sum(int(row["target_token_stable_all_three"]) for row in ext),
            "l1_pair_sequence_stable_external": sum(int(row["l1_pair_sequence_stable_all_three"]) for row in ext),
            "r1_pair_sequence_stable_external": sum(int(row["r1_pair_sequence_stable_all_three"]) for row in ext),
            "l2_chain_sequence_stable_external": sum(int(row["l2_chain_sequence_stable_all_three"]) for row in ext),
            "r2_chain_sequence_stable_external": sum(int(row["r2_chain_sequence_stable_all_three"]) for row in ext),
            "two_sided_frame_sequence_stable_external": sum(int(row["l1_target_r1_sequence_stable_all_three"]) for row in ext),
            "five_window_sequence_stable_external": sum(int(row["l2_to_r2_sequence_stable_all_three"]) for row in ext),
            "left_unique_neighbours": lu,
            "left_nonboundary_opportunities": ln,
            "left_normalized_identity_entropy": le,
            "left_top1_identity_rate": lt1,
            "left_top5_identity_rate": lt5,
            "right_unique_neighbours": ru,
            "right_nonboundary_opportunities": rn,
            "right_normalized_identity_entropy": re_,
            "right_top1_identity_rate": rt1,
            "right_top5_identity_rate": rt5,
            "mapped_axis_breadth": len(axes),
            "capacity_decision": "CONTEXT_SCOREABLE" if len({row["physical_folio"] for row in ext}) >= 3 else "NO_EXTERNAL_CAPACITY",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def build_role_profiles(
    events: Sequence[dict[str, Any]], targets: Sequence[str], axes: Sequence[str],
) -> list[dict[str, Any]]:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in events:
        grouped[str(row["surface"])].append(row)
    output: list[dict[str, Any]] = []
    for surface in targets:
        for side in ("l1", "r1"):
            for axis in axes:
                result = profile_axis(grouped[surface], side, axis)
                output.append({
                    "surface": surface,
                    "side": side.upper(),
                    "axis": axis,
                    "external_opportunities": result["opportunities"],
                    "axis_contact_occurrences": result["contacts"],
                    "axis_contact_physical_folios": result["pages"],
                    "raw_axis_contact_rate": f12(result["rate"]),
                    "pair_stable_opportunities": result["stable_opportunities"],
                    "pair_stable_axis_contacts": result["stable_contacts"],
                    "pair_stable_axis_contact_folios": result["stable_pages"],
                    "pair_stable_axis_contact_rate": f12(result["stable_rate"]),
                    "role_source": "GDT805_EXPLORATORY_SURFACE_AXIS_PROJECTION",
                    "semantic_credit": "0",
                    "confirmed_lexeme": 0,
                    "component_export_credit": 0,
                })
    return output


def build_control_comparisons(
    target_events: Sequence[dict[str, Any]], all_l_events: dict[str, list[dict[str, Any]]],
    targets: Sequence[str], axes: Sequence[str], control_rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_target: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in target_events:
        by_target[str(row["surface"])].append(row)
    pools: defaultdict[str, list[str]] = defaultdict(list)
    for row in control_rows:
        if row["pool_variant"] == "PRIMARY_K12":
            pools[row["target_surface"]].append(row["control_surface"])
    if any(len(pools[target]) != 12 for target in targets):
        raise AssertionError("GDT804 K12 control-pool drift")
    output: list[dict[str, Any]] = []
    leads: list[dict[str, Any]] = []
    for surface in targets:
        for side in ("l1", "r1"):
            for axis in axes:
                target = profile_axis(by_target[surface], side, axis)
                controls = [(control, profile_axis(all_l_events[control], side, axis)) for control in pools[surface]]
                raw_rates = [item[1]["rate"] for item in controls]
                stable_rates = [item[1]["stable_rate"] for item in controls]
                raw_median = statistics.median(raw_rates)
                stable_median = statistics.median(stable_rates)
                raw_equal_or_exceed = sum(rate >= target["rate"] for rate in raw_rates)
                stable_equal_or_exceed = sum(rate >= target["stable_rate"] for rate in stable_rates)
                raw_rank = 1 + raw_equal_or_exceed
                stable_rank = 1 + stable_equal_or_exceed
                raw_above_max = target["rate"] > max(raw_rates)
                stable_above_max = target["stable_rate"] > max(stable_rates)
                dominates_all = raw_above_max and stable_above_max
                pass_gate = (
                    target["pages"] >= 3 and target["stable_pages"] >= 3
                    and raw_rank <= 3 and stable_rank <= 3
                    and target["rate"] > raw_median
                    and target["stable_rate"] > stable_median
                )
                row = {
                    "comparison_id": f"G805-K{len(output) + 1:03d}",
                    "surface": surface,
                    "side": side.upper(),
                    "axis": axis,
                    "target_contacts": target["contacts"],
                    "target_contact_folios": target["pages"],
                    "target_raw_rate": f12(target["rate"]),
                    "target_pair_stable_contacts": target["stable_contacts"],
                    "target_pair_stable_folios": target["stable_pages"],
                    "target_pair_stable_rate": f12(target["stable_rate"]),
                    "raw_rank_of_13": raw_rank,
                    "pair_stable_rank_of_13": stable_rank,
                    "raw_controls_equal_or_exceed": raw_equal_or_exceed,
                    "pair_stable_controls_equal_or_exceed": stable_equal_or_exceed,
                    "control_raw_median": f12(raw_median),
                    "control_raw_max": f12(max(raw_rates)),
                    "control_pair_stable_median": f12(stable_median),
                    "control_pair_stable_max": f12(max(stable_rates)),
                    "raw_above_all_controls": int(raw_above_max),
                    "pair_stable_above_all_controls": int(stable_above_max),
                    "dominates_all_controls_both_views": int(dominates_all),
                    "control_rates": "|".join(f"{name}:{f12(data['rate'])}" for name, data in controls),
                    "control_pair_stable_rates": "|".join(f"{name}:{f12(data['stable_rate'])}" for name, data in controls),
                    "decision": "ROLE_LEAD" if pass_gate else "NO_ROLE_LEAD",
                    "semantic_credit": 0,
                    "confirmed_lexeme": 0,
                    "component_export_credit": 0,
                }
                output.append(row)
                if pass_gate:
                    leads.append({
                        "lead_id": f"G805-L{len(leads) + 1:02d}",
                        **{key: row[key] for key in (
                            "surface", "side", "axis", "target_contacts",
                            "target_contact_folios", "target_raw_rate",
                            "target_pair_stable_contacts", "target_pair_stable_folios",
                            "target_pair_stable_rate", "raw_rank_of_13",
                            "pair_stable_rank_of_13", "raw_controls_equal_or_exceed",
                            "pair_stable_controls_equal_or_exceed", "control_raw_median",
                            "control_pair_stable_median", "raw_above_all_controls",
                            "pair_stable_above_all_controls",
                            "dominates_all_controls_both_views",
                        )},
                        "interpretation_de": f"projizierter {side.upper()}-Kontext ist für {AXIS_GERMAN[axis]} gegenüber K12 angereichert",
                        "role_source": "GDT805_EXPLORATORY_SURFACE_AXIS_PROJECTION",
                        "semantic_credit": 0,
                        "renderer_license": 0,
                        "meaning_ceiling": "ROLE_DISTRIBUTION_NOT_WORD_IDENTITY",
                        "confirmed_lexeme": 0,
                        "component_export_credit": 0,
                    })
    return output, leads


def build_repeated_frames(events: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: defaultdict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in events:
        left, right = str(row["l1_surface"]), str(row["r1_surface"])
        if left != "NONE" and right != "NONE":
            kind = "REAL_TWO_SIDED_FRAME"
        elif (left == "NONE") ^ (right == "NONE"):
            kind = "BOUNDARY_ANCHORED_ONE_SIDED_FRAME"
        else:
            continue
        grouped[(str(row["surface"]), left, right, kind)].append(row)
    output: list[dict[str, Any]] = []
    for surface, left, right, kind in sorted(grouped):
        rows = grouped[(surface, left, right, kind)]
        pages = {row["physical_folio"] for row in rows}
        if len(pages) < 2:
            continue
        output.append({
            "frame_id": f"G805-F{len(output) + 1:02d}",
            "surface": surface,
            "frame_class": kind,
            "left_surface": left,
            "right_surface": right,
            "exact_frame": " ".join(value for value in (left, surface, right) if value != "NONE"),
            "occurrences": len(rows),
            "physical_folios": len(pages),
            "stable_sequence_occurrences": sum(int(row["l1_target_r1_sequence_stable_all_three"]) for row in rows) if kind == "REAL_TWO_SIDED_FRAME" else sum(int(row["bol_target_stable_all_three"]) or int(row["target_eol_stable_all_three"]) for row in rows),
            "loci": "|".join(sorted({str(row["locus"]) for row in rows})),
            "left_axis_tags": rows[0]["l1_axis_tags"],
            "right_axis_tags": rows[0]["r1_axis_tags"],
            "meaning_ceiling": "EXACT_REPEATED_FRAME_NOT_PLAINTEXT",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    real = sum(row["frame_class"] == "REAL_TWO_SIDED_FRAME" for row in output)
    boundary = sum(row["frame_class"] == "BOUNDARY_ANCHORED_ONE_SIDED_FRAME" for row in output)
    if (real, boundary) != (7, 6):
        raise AssertionError(f"repeated frame capacity drift: {(real, boundary)}")
    return output


def context_bridge_result(census: dict[str, str], bridge: str) -> tuple[int, str]:
    channels = {part.split(":", 1)[0] for part in census["common_mask_channel_counts"].split("|") if part != "NONE"}
    field_hits = int(census["common_mask_licensed_hits"])
    amount_hits = int(census["positioned_amount_neighbour_hits"])
    direct_content_hits = int(census["gdt760_clean_content_contact_hits"])
    mapping = {
        "FIELD_OR_AMOUNT": field_hits > 0 or amount_hits > 0,
        "QUALITY_FIELD": "DESCRIPTIVE_QUALITY" in channels,
        "MATERIA_FIELD": "DESCRIPTIVE_MATERIA" in channels,
        "MATERIA_FIELD_OR_AMOUNT": "DESCRIPTIVE_MATERIA" in channels or amount_hits > 0,
        "FIELD_AND_AMOUNT": field_hits > 0 and amount_hits > 0,
        "PRESCRIPTIVE_FIELD": any(channel.startswith("PRESCRIPTIVE") for channel in channels),
        "LIQUID_SPECIFIC_BRIDGE": False,
        "OPAQUE_PRIOR": census["preferred_role_class"].startswith("OPAQUE"),
        "GDT793_OPAQUE_PRIOR": census["preferred_role_class"] == "OPAQUE_SYSTEM_ENTRY",
    }
    if bridge not in mapping:
        raise AssertionError(f"unknown context bridge {bridge}")
    detail = (
        f"channels={census['common_mask_channel_counts']};field_hits={field_hits};"
        f"positional_amount_candidates={amount_hits};direct_clean_content_hits={direct_content_hits};"
        f"prior={census['preferred_role_class']};independent_semantic_credit=0"
    )
    return int(mapping[bridge]), detail


def build_candidate_scores(
    models: Sequence[dict[str, str]], comparisons: Sequence[dict[str, Any]],
    leads: Sequence[dict[str, Any]], census_rows: Sequence[dict[str, str]],
    capacity_rows: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    comp = {(row["surface"], row["side"], row["axis"]): row for row in comparisons}
    lead_keys = {(row["surface"], row["side"], row["axis"]) for row in leads}
    census = {row["surface"]: row for row in census_rows}
    capacity = {row["surface"]: row for row in capacity_rows}
    scores: list[dict[str, Any]] = []
    for model in models:
        surface = model["surface"]
        expected = []
        for side, column in (("L1", "left_support_axes"), ("R1", "right_support_axes")):
            for axis in model[column].split("|"):
                if axis != "NONE":
                    expected.append((side, axis))
        lead_matches = [(side, axis) for side, axis in expected if (surface, side, axis) in lead_keys]
        dominant_matches = [
            (side, axis) for side, axis in lead_matches
            if int(comp[(surface, side, axis)]["dominates_all_controls_both_views"])
        ]
        near_matches = []
        for side, axis in expected:
            row = comp[(surface, side, axis)]
            if (
                (surface, side, axis) not in lead_keys
                and
                int(row["target_contact_folios"]) >= 3
                and int(row["raw_rank_of_13"]) <= 3
                and int(row["pair_stable_rank_of_13"]) <= 3
                and float(row["target_raw_rate"]) > float(row["control_raw_median"])
                and float(row["target_pair_stable_rate"]) > float(row["control_pair_stable_median"])
            ):
                near_matches.append((side, axis))
        bridge_flag, bridge_detail = context_bridge_result(
            census[surface], model["context_bridge_hypothesis"],
        )
        breadth = int(capacity[surface]["mapped_axis_breadth"])
        nondominant_full = [item for item in lead_matches if item not in dominant_matches]
        score = 5 * len(dominant_matches) + 2 * len(nondominant_full) + len(near_matches)
        density = score / len(expected) if expected else 0.0
        scores.append({
            **model,
            "external_physical_folios": capacity[surface]["external_physical_folios"],
            "mapped_axis_breadth": breadth,
            "expected_signature_count": len(expected),
            "dominant_role_lead_count": len(dominant_matches),
            "dominant_role_leads": "|".join(f"{side}:{axis}" for side, axis in dominant_matches) or "NONE",
            "full_role_lead_count": len(lead_matches),
            "full_role_leads": "|".join(f"{side}:{axis}" for side, axis in lead_matches) or "NONE",
            "near_only_lead_count": len(near_matches),
            "near_only_leads": "|".join(f"{side}:{axis}" for side, axis in near_matches) or "NONE",
            "context_bridge_flag": bridge_flag,
            "context_bridge_detail": bridge_detail,
            "context_bridge_is_independent_semantics": 0,
            "direct_content_bridge_pass": int(int(census[surface]["gdt760_clean_content_contact_hits"]) > 0),
            "candidate_score": score,
            "candidate_score_density": f12(density),
            "score_is_probability": 0,
            "semantic_status": "WIDTH_SCALED_AXIS_CORRELATED_RIVAL_DIAGNOSTIC_ONLY__NO_SELECTION",
            "confirmed_lexeme": 0,
        })
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scores:
        grouped[row["surface"]].append(row)
    adjudication: list[dict[str, Any]] = []
    decisions = {
        "chal": "PROJECTED_MATERIAL_OR_QUALITY_CONTEXT_PROFILE__NO_DIRECT_SLOT",
        "chedal": "MATERIAL_OR_AMOUNT_RIVALS_UNRESOLVED__NO_DIRECT_SLOT",
        "cheol": "DRY_VALUE_CONTEXT_PROFILE__MATERIAL_OR_QUALITY_UNRESOLVED__NO_DIRECT_SLOT",
        "okail": "NO_EXTERNAL_CAPACITY",
        "okal": "RETAIN_GDT793_OPAQUE_ENTRY_PRIOR__MATERIAL_CONTEXT_RIVAL",
        "ol": "RETAIN_GDT762_GENERAL_CARRIER_PRIOR__SPECIFIC_MEDIUM_UNSUPPORTED",
        "otal": "PREPARATION_OR_QUALITY_CONTEXT_PROFILE__NO_DIRECT_SLOT",
        "qokeol": "HOT_VALUE_CONTEXT_FIELD__PROCESS_PREPARATION_QUALITY_UNRESOLVED",
        "qokol": "VALUE_CONTEXT_FIELD__PROCESS_PREPARATION_UNRESOLVED",
        "qotal": "MATERIAL_OR_QUALITY_RIVALS_UNRESOLVED__NO_ROLE_LEAD",
        "sail": "NO_EXTERNAL_CAPACITY",
    }
    retained_prior_ids = {"okal": "OKAL-OPAQUE", "ol": "OL-CARRIER"}
    for surface in [row["surface"] for row in census_rows]:
        ranked = sorted(
            grouped[surface],
            key=lambda row: (
                -float(row["candidate_score_density"]),
                -int(row["dominant_role_lead_count"]),
                -int(row["full_role_lead_count"]),
                row["candidate_id"],
            ),
        )
        diagnostic_top = ranked[0]
        retained_id = retained_prior_ids.get(surface, "NONE")
        top = next((row for row in ranked if row["candidate_id"] == retained_id), diagnostic_top)
        runner = next((row for row in ranked if row["candidate_id"] != top["candidate_id"]), None)
        margin = int(top["candidate_score"]) - int(runner["candidate_score"]) if runner else int(top["candidate_score"])
        folios = int(top["external_physical_folios"])
        decision = decisions[surface]
        if (folios < 3) != (decision == "NO_EXTERNAL_CAPACITY"):
            raise AssertionError(f"capacity/adjudication drift for {surface}")
        surface_leads = [row for row in leads if row["surface"] == surface]
        dominant = [row for row in surface_leads if int(row["dominates_all_controls_both_views"])]
        adjudication.append({
            "surface": surface,
            "decision": decision,
            "diagnostic_top_candidate_id": diagnostic_top["candidate_id"],
            "diagnostic_top_score_density": diagnostic_top["candidate_score_density"],
            "leading_candidate_id": top["candidate_id"],
            "leading_candidate_class": top["candidate_class"],
            "leading_concrete_working_reading_de": top["concrete_working_reading_de"],
            "leading_score": top["candidate_score"],
            "runner_up_candidate_id": runner["candidate_id"] if runner else "NONE",
            "runner_up_working_reading_de": runner["concrete_working_reading_de"] if runner else top["countercandidate_de"],
            "runner_up_score": runner["candidate_score"] if runner else 0,
            "score_margin": margin,
            "context_role_leads": "|".join(f"{row['side']}:{row['axis']}" for row in surface_leads) or "NONE",
            "dominant_role_leads": "|".join(f"{row['side']}:{row['axis']}" for row in dominant) or "NONE",
            "context_bridge_hypothesis": top["context_bridge_hypothesis"],
            "context_bridge_flag": top["context_bridge_flag"],
            "context_bridge_is_independent_semantics": 0,
            "direct_content_bridge_pass": top["direct_content_bridge_pass"],
            "safe_gdt804_default_de": census[surface]["conservative_working_default_de"],
            "new_role_selected": 0,
            "prior_role_retained": int(decision.startswith("RETAIN_")),
            "confidence": "PRIOR_RETAINED" if decision.startswith("RETAIN_") else "C0_RIVAL",
            "literal_identity": "OPEN",
            "confirmed_plaintext": 0,
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    if sum(int(row["new_role_selected"]) for row in adjudication) != 0:
        raise AssertionError("GDT805 must not install a new role from projected covariates")
    return scores, adjudication


def choose_passages(
    events: Sequence[dict[str, Any]], adjudication: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_surface: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in events:
        by_surface[str(row["surface"])].append(row)
    decisions = {row["surface"]: row for row in adjudication}
    output: list[dict[str, Any]] = []

    def safe_flank(row: dict[str, Any], side: str) -> str:
        if row[f"{side}_anchor_kind"] == "GDT739_EXACT_ACTIVE_CELL":
            return str(row[f"{side}_axis_default_de"])
        surface = row[f"{side}_surface"]
        return "Zeilenrand" if surface == "NONE" else f"[{surface}:?]"

    for surface, decision in decisions.items():
        if decision["decision"] == "NO_EXTERNAL_CAPACITY":
            continue
        candidates = []
        for row in by_surface[surface]:
            mapped_kinds = {
                "GDT739_EXACT_ACTIVE_CELL",
                "GDT805_EXPLORATORY_SURFACE_AXIS_PROJECTION",
            }
            mapped = int(row["l1_anchor_kind"] in mapped_kinds) + int(row["r1_anchor_kind"] in mapped_kinds)
            stable = int(row["l1_pair_sequence_stable_all_three"]) + int(row["r1_pair_sequence_stable_all_three"])
            field_context = int(row["gdt804_common_mask_field_hit"]) + int(row["gdt804_positioned_amount_neighbour_hit"])
            candidates.append((5 * mapped + 2 * stable + field_context, row))
        candidates.sort(key=lambda item: (-item[0], str(item[1]["physical_folio"]), str(item[1]["locus"]), int(item[1]["token_index"])))
        chosen: list[tuple[int, dict[str, Any]]] = []
        used_folios: set[str] = set()
        for score, row in candidates:
            if str(row["physical_folio"]) in used_folios:
                continue
            chosen.append((score, row))
            used_folios.add(str(row["physical_folio"]))
            if len(chosen) == 5:
                break
        if len(chosen) != 5:
            raise AssertionError(f"passage capacity drift for {surface}")
        for score, row in chosen:
            output.append({
                "passage_id": f"G805-P{len(output) + 1:02d}",
                "surface": surface,
                "source_selector": row["source_selector"],
                "physical_folio": row["physical_folio"],
                "locus": row["locus"],
                "token_index": row["token_index"],
                "exact_five_window": row["exact_five_window"],
                "full_zl3b_line": row["full_zl3b_line"],
                "left_complete_surface": row["l1_surface"],
                "left_axis_evidence_kind": row["l1_anchor_kind"],
                "left_broad_axis": row["l1_axis_tags"],
                "target_safe_role_de": decision["safe_gdt804_default_de"],
                "leading_concrete_candidate_de": decision["leading_concrete_working_reading_de"],
                "right_complete_surface": row["r1_surface"],
                "right_axis_evidence_kind": row["r1_anchor_kind"],
                "right_broad_axis": row["r1_axis_tags"],
                "safe_role_skeleton_de": f"{safe_flank(row, 'l1')} | {decision['safe_gdt804_default_de']} | {safe_flank(row, 'r1')}",
                "projected_axis_skeleton_de": f"{row['l1_axis_default_de']} | {decision['safe_gdt804_default_de']} | {row['r1_axis_default_de']}",
                "concrete_candidate_display_de": f"{row['l1_axis_default_de']} | {decision['leading_concrete_working_reading_de']} | {row['r1_axis_default_de']}",
                "strongest_rival_de": decision["runner_up_working_reading_de"],
                "adjudication": decision["decision"],
                "selection_score": score,
                "target_token_stable_all_three": row["target_token_stable_all_three"],
                "left_pair_stable_all_three": row["l1_pair_sequence_stable_all_three"],
                "right_pair_stable_all_three": row["r1_pair_sequence_stable_all_three"],
                "renderer_scope": "EXPLORATORY_PASSAGE_CARD__SURFACE_PROJECTION_NOT_RENDERER_LICENSE",
                "confirmed_plaintext": 0,
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
    if len(output) != 45:
        raise AssertionError("passage-card capacity drift")
    return output


def build_edge_packet(events: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in events:
        target_index = int(row["token_index"])
        for side, offset in (("l1", -1), ("r1", 1)):
            if row[f"{side}_anchor_kind"] not in {
                "GDT739_EXACT_ACTIVE_CELL",
                "GDT805_EXPLORATORY_SURFACE_AXIS_PROJECTION",
            }:
                continue
            neighbour = row[f"{side}_surface"]
            neighbour_index = target_index + offset
            page = str(row["source_selector"])
            match = re.match(r"^(f\d+)", page)
            if match is None:
                raise AssertionError(f"cannot normalize physical folio {page}")
            output.append({
                "edge_id": f"G805E{len(output) + 1:04d}",
                "batch_id": "GDT805_COMPLETE_WHOLE_CONTEXT",
                "page": page,
                "physical_folio": match.group(1),
                "diagram_unit_id": "CACHED_TEXT_LINE",
                "pivot_visual_id": f"TOKEN_{row['surface']}_{target_index}",
                "pivot_locus": f"{row['locus']}@{target_index}",
                "target_visual_id": f"TOKEN_{neighbour}_{neighbour_index}",
                "target_locus": f"{row['locus']}@{neighbour_index}",
                "relation_type": f"EXACT_COMPLETE_WHOLE_{side.upper()}_CONTEXT",
                "direction_basis": "WRITTEN_TOKEN_ADJACENCY",
                "ownership_basis": "SAME_CACHED_TEXT_LINE",
                "geometry_only_selection": "FALSE",
                "source_manifest_id": "GDT805",
                "page_crop_sha256": "NONE",
                "pivot_crop_sha256": "NONE",
                "target_crop_sha256": "NONE",
                "source_aware_localizer": "GDT805_BUILDER",
                "relation_reviewer": "PENDING_EXTERNAL",
                "relation_confidence": "EXACT_TRANSCRIPTION_ADJACENCY",
                "ambiguity_state": "PROJECTED_BROAD_AXIS_ZERO_SEMANTIC_CREDIT",
                "formal_access_state": "FORMAL_ACCESSED",
                "fold_assignment": "NONE",
                "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
            })
    return output


def run_edge_intake(packet_path: Path, intake_path: Path, packet_rows: int) -> dict[str, Any]:
    completed = subprocess.run(
        [str(VMANUS_EXP), "check-edge-packet", str(packet_path)], cwd=ROOT,
        check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    expected = {
        "status": "INVALID_PACKET", "packet_rows": packet_rows,
        "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0,
        "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False,
        "errors": [f"edge row {number}: formal access is not sealed" for number in range(2, packet_rows + 2)],
    }
    if completed.returncode != 1 or completed.stderr or json.loads(completed.stdout) != expected:
        raise AssertionError("GDT388 context-edge intake drift")
    intake_path.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return expected


def report_text(
    status: str, capacity: Sequence[dict[str, Any]], leads: Sequence[dict[str, Any]],
    frames: Sequence[dict[str, Any]], adjudication: Sequence[dict[str, Any]],
    passages: Sequence[dict[str, Any]], audited_projection_count: int,
    primary_projection_count: int, exact_context_matches: int,
) -> str:
    cap = {row["surface"]: row for row in capacity}
    dominant = [row for row in leads if int(row["dominates_all_controls_both_views"])]
    retained = [row for row in adjudication if int(row["prior_role_retained"])]
    lines = [
        "# GDT805 — discovery-bereinigte Ganzwortkontexte", "",
        f"Status: `{status}`", "", "## Ergebnis", "",
        "Die zwölf GDT803-Entdeckungsstellen sind über ihre exakten occurrence IDs",
        "abgezogen. Übrig bleiben 1.086 Außenstellen der elf Mittelganzformen; 916",
        "Zieltoken sind in allen drei alternativen Lesungen oberflächenstabil. `okail`",
        "hat keine und `sail` nur eine Außenstelle. Für beide wird keine Bedeutung",
        "erzwungen.", "",
        f"GDT805 auditiert {audited_projection_count} deduplizierte GDT739-Nachbaroberflächen.",
        f"Nach aktivem Radius, GDT754-/GDT738-Quarantäne und Zielmaskierung bleiben {primary_projection_count}",
        "Oberflächen für eine ausdrücklich neue Surface-Achsenprojektion. Der deutsche",
        "Quellstring wird nicht ausgegeben; die Tags sind aber aus früherer deutscher",
        "Arbeitsprosa abgeleitet. Sie sind keine unabhängige Semantik und keine",
        f"Renderer-Lizenz. Nur {exact_context_matches} Flankenzellen im Außenatlas sind zugleich",
        "dieselben lokal aktiven GDT739-Quellzellen; alle anderen Tags erscheinen nur als",
        "markierte Kandidaten.", "",
        "## K12-Projektionsleads", "",
        "Ein Lead braucht mindestens drei rohe und drei paarstabile Folios, Rang 1–3",
        "von 13 gegen dieselben GDT804-K12-Kontrollen und eine Rate über beiden",
        "Kontrollmedianen. Gleichstände werden gegen das Ziel gezählt.",
        f"{len(leads)} Seiten-/Achsen-Kombinationen erfüllen diese Profilregel; {len(dominant)}",
        "schlagen alle zwölf Kontrollen in beiden Ansichten:", "",
        "| Form | Seite | breite Achse | Kontakte/Folios | stabil | Ränge roh/stabil | dominant |", "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in leads:
        lines.append(
            f"| `{row['surface']}` | {row['side']} | {row['axis']} | {row['target_contacts']}/{row['target_contact_folios']} | "
            f"{row['target_pair_stable_contacts']}/{row['target_pair_stable_folios']} | {row['raw_rank_of_13']}/{row['pair_stable_rank_of_13']} | "
            f"{row['dominates_all_controls_both_views']} |"
        )
    lines.extend(["", "## Korrektur des Kandidatenwählers", "",
        "Der erste Diagnoselauf bevorzugte breite Materialmodelle, zählte volle Leads",
        "nochmals als Near-Leads und wertete Feldnähe beziehungsweise eine offene",
        "Mengenposition als direkten Inhaltsbeleg. Das war falsch. Der korrigierte Lauf",
        "macht Full und Near disjunkt, skaliert den Diagnosescore durch die deklarierte",
        "Modellbreite und vergibt keinen",
        "Breiten- oder Feldbonus und installiert aus den Projektionen null neue Rollen.",
        "Mehrere korrelierte Achsentags derselben Kontaktzelle können weiter einzeln",
        "zählen; deshalb ist der Score ausdrücklich kein vollständig normalisierter Beleg.",
        "GDT804s direkter sauberer CONTENT_PREP-Kontakt bleibt für alle elf Formen null.",
        "Die konkreten Rivalen bleiben sichtbar, damit die nächste Runde sie tatsächlich",
        "prüfen kann.", "", "## Rollenstand statt Scheinübersetzung", "",
        "| Form | Außenstellen/Folios | führender konkreter Rivale | Gegenrivale | Entscheidung |", "|---|---:|---|---|---|",
    ])
    for row in adjudication:
        lines.append(
            f"| `{row['surface']}` | {cap[row['surface']]['external_occurrences']}/{cap[row['surface']]['external_physical_folios']} | "
            f"{row['leading_concrete_working_reading_de']} | {row['runner_up_working_reading_de']} | `{row['decision']}` |"
        )
    lines.extend(["", "Neu ausgewählt wird keine Rolle. Beibehalten werden nur zwei ältere",
        "Basismodelle: `okal` als Kennstellen-/Systemeintrag mit Materialkontext-Rivale",
        "und `ol` als allgemeiner mengenfähiger Inhaltsträger. Insbesondere bleibt offen,",
        "ob `ol` Öl, Wasser, Wein oder überhaupt ein konkretes Medium bezeichnet.", "",
        "## Wiederholte vollständige Rahmen", "",
        f"Es gibt {sum(row['frame_class'] == 'REAL_TWO_SIDED_FRAME' for row in frames)} echte beidseitige Mehrseitenrahmen und",
        f"{sum(row['frame_class'] == 'BOUNDARY_ANCHORED_ONE_SIDED_FRAME' for row in frames)} Zeilenrand-gebundene einseitige Rahmen. `NONE` zählt dabei nie",
        "als Token. Die Rahmen sind nützliche Passagen, aber zu dünn als allgemeiner",
        "Decoder.", "", "## Konkrete Passagekarten", "",
    ])
    for target in ("chal", "chedal", "cheol", "okal", "ol", "otal", "qokeol", "qokol", "qotal"):
        row = next(item for item in passages if item["surface"] == target)
        lines.extend([
            f"- `{row['locus']}` — `{row['exact_five_window']}`",
            f"  - zellgebunden: {row['safe_role_skeleton_de']}",
            f"  - projizierte Achsen: {row['projected_axis_skeleton_de']}",
            f"  - konkreter Rivale: {row['concrete_candidate_display_de']}",
        ])
    lines.extend(["", "Alle 45 Passagekarten stehen im Artefakt; hier wird je auswertbarer Form",
        "nur eine gezeigt. Das ist erstmals eine vollständige, reale Kontextausgabe mit",
        "konkretem Rivalen, nicht der alte Nulltext ‘Arbeitsgut bearbeiten’. Trotzdem",
        "bleiben bestätigte Lexeme und Klartextsätze null.", "", "## Nächste Route", "",
        "Die produktivste nächste Runde soll die tatsächlich gewonnenen Rollenleads",
        "in drei getrennten Kanälen replizieren: exakte Quellzellen, ein quarantänebereinigtes",
        "enges GDT739-Deck und ein breiteres GDT734-Deck. Dabei zählt jede Kontaktstelle",
        "pro disjunkter Makroklasse nur einmal. Erst danach werden die sieben exakten",
        "Mehrseitenrahmen gegen konkrete Stoff-, Qualitäts- und Prozessrivalen gespielt.",
        "Keine neue Seite ist dafür nötig.", "", "## Grenze und Reproduktion", "",
        f"Neue Rollen: 0; beibehaltene Vorrollen: {len(retained)}.",
        "Der GDT388-Einlass wird auf jede gemappte Kontextkante angewandt und bleibt",
        "wegen nachträglichem Formalzugriff nicht score-ready. Keine neue Seite, kein Bild",
        "und keine Transkription wurden geöffnet; f84/f84r blieben ausgeschlossen.", "",
    ])
    return "\n".join(lines)


def build(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    census_rows = read_tsv(G804_CENSUS)
    targets = [row["surface"] for row in census_rows]
    target_set = set(targets)
    if targets != ["chal", "chedal", "cheol", "okail", "okal", "ol", "otal", "qokeol", "qokol", "qotal", "sail"]:
        raise AssertionError("GDT804 target cohort drift")
    discovery = {row["occurrence_id"] for row in read_tsv(G803_BRACKETS)}
    if len(discovery) != 12:
        raise AssertionError("GDT803 discovery set drift")
    projection_audit, projection_lookup, exact_active_cells = build_anchor_deck(target_set)
    reader = ReaderContext()
    base_rows = {row["occurrence_id"]: row for row in read_tsv(G800_OCCURRENCES)}
    context_rows = read_tsv(G802_CONTEXTS)
    if len(base_rows) != 4137 or len(context_rows) != 4137:
        raise AssertionError("paired occurrence capacity drift")
    union = {
        (row["page"], row["locus"], int(row["token_ordinal"]), row["surface"]): row
        for row in read_tsv(G804_UNION)
    }
    controls = read_tsv(G804_CONTROLS)
    control_surfaces = {row["control_surface"] for row in controls if row["pool_variant"] == "PRIMARY_K12"}
    if control_surfaces & target_set:
        raise AssertionError("K12 controls overlap target cohort")
    needed = target_set | control_surfaces
    all_l_events: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    all_target: list[dict[str, Any]] = []
    for row in context_rows:
        base = base_rows[row["occurrence_id"]]
        surface = base["surface"]
        if row["terminal"] != "l" or surface not in needed:
            continue
        event = build_context_event(
            row, base, reader, target_set, projection_lookup, exact_active_cells, union,
        )
        all_l_events[surface].append(event)
        if surface in target_set:
            all_target.append(event)
    if len(all_target) != 1098:
        raise AssertionError("target occurrence capacity drift")
    external = [row for row in all_target if row["occurrence_id"] not in discovery]
    if len(external) != 1086:
        raise AssertionError("external target capacity drift")
    for index, row in enumerate(sorted(external, key=lambda item: (targets.index(str(item["surface"])), str(item["source_selector"]), str(item["locus"]), int(item["token_index"]))), start=1):
        row["context_id"] = f"G805-C{index:04d}"
    axes = [row["axis_id"] for row in read_tsv(G739_AXES)]
    if axes != list(AXIS_GERMAN):
        raise AssertionError("GDT739 axis definition drift")
    capacity = build_capacity(all_target, external, targets)
    expected_stable = {"chal": 34, "chedal": 14, "cheol": 117, "okail": 0, "okal": 101, "ol": 376, "otal": 107, "qokeol": 33, "qokol": 81, "qotal": 53, "sail": 0}
    if {row["surface"]: int(row["target_token_stable_external"]) for row in capacity} != expected_stable:
        raise AssertionError("target token-stability capacity drift")
    sequence_totals = (
        sum(int(row["l1_pair_sequence_stable_all_three"]) for row in external),
        sum(int(row["r1_pair_sequence_stable_all_three"]) for row in external),
        sum(int(row["l2_chain_sequence_stable_all_three"]) for row in external),
        sum(int(row["r2_chain_sequence_stable_all_three"]) for row in external),
        sum(int(row["l1_target_r1_sequence_stable_all_three"]) for row in external),
        sum(int(row["l2_to_r2_sequence_stable_all_three"]) for row in external),
    )
    if sequence_totals != (677, 663, 475, 461, 495, 228):
        raise AssertionError(f"context sequence-stability capacity drift: {sequence_totals}")
    identities = build_identity_profiles(external, targets)
    role_profiles = build_role_profiles(external, targets, axes)
    comparisons, leads = build_control_comparisons(external, all_l_events, targets, axes, controls)
    frames = build_repeated_frames(external)
    scores, adjudication = build_candidate_scores(
        read_tsv(TARGET_MODELS), comparisons, leads, census_rows, capacity,
    )
    passages = choose_passages(external, adjudication)
    edge_packet = build_edge_packet(external)
    if len(edge_packet) < 50:
        raise AssertionError("context edge packet lacks descriptive capacity")
    primary_projection_count = sum(int(row["primary_surface_projection_allowed"]) for row in projection_audit)
    exact_context_matches = sum(
        row[f"{side}_anchor_kind"] == "GDT739_EXACT_ACTIVE_CELL"
        for row in external for side in ("l1", "r1")
    )
    projected_context_contacts = sum(
        row[f"{side}_anchor_kind"] == "GDT805_EXPLORATORY_SURFACE_AXIS_PROJECTION"
        for row in external for side in ("l1", "r1")
    )
    dominant_leads = sum(int(row["dominates_all_controls_both_views"]) for row in leads)

    write_tsv(output_dir / "SOURCE_LOCK.tsv", source_lock(), ("path", "sha256", "purpose"))
    write_tsv(output_dir / "GDT805_GUARDED_QUERY_STATS.tsv", reader.stats, tuple(reader.stats[0]))
    write_tsv(
        output_dir / "GDT805_131_GDT739_SURFACE_PROJECTION_AUDIT.tsv",
        projection_audit, tuple(projection_audit[0]),
    )
    external_fields = ("context_id",) + tuple(key for key in external[0] if key != "context_id")
    write_tsv(output_dir / "GDT805_1086_EXTERNAL_CONTEXT_ATLAS.tsv", external, external_fields)
    write_tsv(output_dir / "GDT805_11_CONTEXT_CAPACITY.tsv", capacity, tuple(capacity[0]))
    write_tsv(output_dir / "GDT805_NEIGHBOUR_IDENTITY_PROFILE.tsv", identities, tuple(identities[0]))
    write_tsv(output_dir / "GDT805_ROLE_CONTACT_PROFILE.tsv", role_profiles, tuple(role_profiles[0]))
    write_tsv(output_dir / "GDT805_K12_ROLE_COMPARISON.tsv", comparisons, tuple(comparisons[0]))
    write_tsv(output_dir / "GDT805_ROLE_LEADS.tsv", leads, tuple(leads[0]))
    write_tsv(output_dir / "GDT805_13_REPEATED_FRAME_TYPES.tsv", frames, tuple(frames[0]))
    write_tsv(output_dir / "GDT805_CANDIDATE_SCORECARD.tsv", scores, tuple(scores[0]))
    write_tsv(output_dir / "GDT805_11_CANDIDATE_ADJUDICATION.tsv", adjudication, tuple(adjudication[0]))
    write_tsv(output_dir / "GDT805_45_PASSAGE_CARDS.tsv", passages, tuple(passages[0]))
    write_tsv(output_dir / "GDT805_GDT388_CONTEXT_EDGE_PACKET.tsv", edge_packet, EDGE_FIELDS)
    intake = run_edge_intake(
        output_dir / "GDT805_GDT388_CONTEXT_EDGE_PACKET.tsv",
        output_dir / "GDT805_GDT388_EDGE_INTAKE.json", len(edge_packet),
    )
    new_role_selections = sum(int(row["new_role_selected"]) for row in adjudication)
    retained_priors = sum(int(row["prior_role_retained"]) for row in adjudication)
    if new_role_selections != 0 or retained_priors != 2:
        raise AssertionError("GDT805 corrected role-retention count drift")
    status = (
        f"PARTIAL__1086_EXTERNAL_EVENTS__916_TARGET_TOKEN_STABLE__131_GDT739_SURFACES_AUDITED__"
        f"{primary_projection_count}_PRIMARY_SURFACE_PROJECTIONS__{len(leads)}_K12_PROFILE_LEADS__"
        f"{dominant_leads}_DOMINATE_ALL_K12__7_REAL_TWO_SIDED_MULTIFOLIO_FRAMES__"
        "0_NEW_ROLE_SELECTIONS__2_PRIORS_RETAINED__ZERO_LEXEMES"
    )
    structural = [{
        "experiment": "GDT805", "status": status,
        "selected_structure": "DISCOVERY_SUBTRACTED_EXACT_WHOLE_CONTEXT_ROLE_DISCRIMINATOR",
        "external_events": 1086, "target_token_stable": 916,
        "gdt739_surfaces_audited": 131,
        "primary_surface_projection_wholes": primary_projection_count,
        "exact_gdt739_context_cells": exact_context_matches,
        "projected_context_contacts": projected_context_contacts,
        "k12_profile_leads": len(leads),
        "dominant_k12_profile_leads": dominant_leads,
        "real_two_sided_multifolio_frames": 7,
        "boundary_anchored_one_sided_frames": 6,
        "new_role_selections": new_role_selections,
        "retained_prior_roles": retained_priors,
        "meaning_ceiling": "WHOLE_ROLE_RIVALS_ONLY__NO_WORD_OR_COMPONENT_IDENTITY",
        "confirmed_lexemes": 0, "confirmed_plaintext": 0,
        "component_export_credit": 0, "new_pages_images_or_transcriptions": 0,
    }]
    write_tsv(output_dir / "GDT805_STRUCTURAL_CARD.tsv", structural, tuple(structural[0]))
    result: dict[str, Any] = {
        "experiment_id": "GDT805", "status": status,
        "target_surfaces": targets, "total_target_l_occurrences": 1098,
        "discovery_occurrences_subtracted": 12, "external_context_events": 1086,
        "external_physical_folios": len({row["physical_folio"] for row in external}),
        "target_token_stable_external": 916,
        "sequence_stability_totals": {
            "l1_pairs": sequence_totals[0], "r1_pairs": sequence_totals[1],
            "l2_chains": sequence_totals[2], "r2_chains": sequence_totals[3],
            "two_sided_frames": sequence_totals[4], "five_windows": sequence_totals[5],
        },
        "gdt739_source_contacts_audited": 230,
        "gdt739_surfaces_audited": 131,
        "primary_surface_projection_wholes": primary_projection_count,
        "exact_gdt739_context_cells": exact_context_matches,
        "projected_context_contacts": projected_context_contacts,
        "k12_profile_leads": len(leads),
        "dominant_k12_profile_leads": dominant_leads,
        "projected_axis_profile_leads": [f"{row['surface']}:{row['side']}:{row['axis']}" for row in leads],
        "real_two_sided_multifolio_frames": 7,
        "boundary_anchored_one_sided_frames": 6,
        "candidate_decisions": {row["surface"]: row["decision"] for row in adjudication},
        "displayed_rival_candidates_de": {row["surface"]: row["leading_concrete_working_reading_de"] for row in adjudication},
        "new_role_selections": new_role_selections,
        "retained_prior_roles": retained_priors,
        "passage_cards": len(passages), "gdt388_context_edges": len(edge_packet),
        "gdt388_intake": intake, "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0, "component_export_credit": 0,
        "new_pages_images_or_transcriptions": 0, "f84_or_f84r_rows": 0,
    }
    result["output_sha256"] = {
        name: sha256(output_dir / name)
        for name in OUTPUT_NAMES if name != "RESULT.json"
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if output_dir.resolve() == ART.resolve():
        (EXP / "REPORT.md").write_text(
            report_text(
                status, capacity, leads, frames, adjudication, passages,
                len(projection_audit), primary_projection_count, exact_context_matches,
            ),
            encoding="utf-8",
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ART)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
