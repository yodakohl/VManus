#!/usr/bin/env python3
"""Discriminate medium, carrier, and post-moist complement roles."""

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
BASE_REL = Path("experiments/yolo/gdt762_moist_medium_candidate_discrimination")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G761_RUN_REL = Path(
    "experiments/yolo/gdt761_state_pair_outer_carrier_bridge/src/run.py"
)
G760_QUANTITY_REL = Path(
    "experiments/yolo/gdt760_quantity_bilateral_content_attachment/"
    "artifacts/QUANTITY_281_EXPRESSION_ATLAS.tsv"
)
G736_GRID_REL = Path(
    "experiments/yolo/gdt736_opaque_head_record_role_bridge/"
    "artifacts/OPAQUE_96_CONCRETE_ROLE_GRID.tsv"
)
G737_FORM_REL = Path(
    "experiments/yolo/gdt737_held_body_record_role_transfer/"
    "artifacts/HELD_273_FORM_ROLE_BRIDGE.tsv"
)
G755_HISTORICAL_REL = Path(
    "experiments/yolo/gdt755_top24_historical_register_crosswalk/"
    "src/HISTORICAL_EXPRESSION_BANK.tsv"
)
CANDIDATES = ("ckhy", "pcheey", "ol")
CONFOUNDERS = ("ckhy", "pcheey", "ol", "shor", "chor", "daiin", "oraiin")
HEADS = (("H1", "p"), ("H2", "s"), ("H3", "r"), ("H4", "l"))
BODY_CONTROLS = ("cheey", "chey", "chy")
OUTPUT_NAMES = (
    "CANDIDATE_OCCURRENCE_ATLAS.tsv",
    "STATE_PAIR_EXPOSURE.tsv",
    "DIRECT_STATE_CONTACT_ATLAS.tsv",
    "RADIUS2_STATE_RELAY_ATLAS.tsv",
    "CANDIDATE_PAIR_CONTACT_MATRIX.tsv",
    "CANDIDATE_POLARITY_SUMMARY.tsv",
    "PCHEEY_EXACT_CONTEXT_ATLAS.tsv",
    "CANDIDATE_DIRECT_NEIGHBOR_DECK.tsv",
    "REPEATED_CANDIDATE_CONSTRUCTION_ATLAS.tsv",
    "OL_AMOUNT_EXPRESSION_CONTACT_ATLAS.tsv",
    "DIRECTED_PATTERN_NULL_CENSUS.tsv",
    "BODY_FAMILY_CONTEXT_CONTROL.tsv",
    "H1_POST_MOIST_SPECIFICITY_AUDIT.tsv",
    "BOUNDARY_SHELL_RIVAL_AUDIT.tsv",
    "CONFOUNDER_AND_FORM_OVERLAP_AUDIT.tsv",
    "SEMANTIC_PRECEDENCE_REPAIR_AUDIT.tsv",
    "HISTORICAL_ROLE_RIVAL_AUDIT.tsv",
    "ROLE_HYPOTHESIS_SCORECARD.tsv",
    "THREE_PCHEEY_WORKING_SPANS.tsv",
    "THREE_CANDIDATE_WORKING_REVISION.tsv",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__404_CANDIDATE_OCCURRENCES__11_DRY_MOIST_WHOLE_PAIRS__"
    "98_DIRECT_STATE_EDGES__66_RADIUS2_STATE_RELAYS__"
    "PCHEEY_3_OF_3_IMMEDIATELY_AFTER_SHO_OR_SHEO__"
    "SELECT_POST_MOIST_FORM_II_RECORD_FIELD__C1_DRY_SOURCE_RIVAL__"
    "CKHY_OPEN_RELAY_ONLY__OL_QUANTITY_BEARING_CONTENT_CARRIER__"
    "ZERO_SPECIFIC_MEDIUM_IDENTITY__ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g761 = load_module("gdt761_builder_for_gdt762", ROOT / G761_RUN_REL)
physical_folio = g761.physical_folio
clean_cell = g761.clean_cell
line_position = g761.line_position
fixed = g761.fixed
compact_counts = g761.compact_counts


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
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


def joined(values: Iterable[str]) -> str:
    selected = set(values)
    return "|".join(axis for axis in g761.AXIS_ORDER if axis in selected) or "NONE"


def ratio(numerator: float, denominator: float) -> str:
    if denominator == 0.0:
        return "INF" if numerator > 0.0 else "NA"
    return fixed(numerator / denominator)


def state_maps(
    rows: list[dict[str, str]],
) -> tuple[dict[str, dict[str, str]], set[str], set[str]]:
    mapping: dict[str, dict[str, str]] = {}
    dry: set[str] = set()
    moist: set[str] = set()
    for row in rows:
        for polarity, field, meaning_field in (
            ("DRY", "dry_surface", "dry_working_candidate_de"),
            ("MOIST", "moist_surface", "moist_working_candidate_de"),
        ):
            surface = row[field]
            mapping[surface] = {
                "pair_id": row["pair_id"], "pair_role": row["pair_role"],
                "role_stratum": row["role_stratum"], "polarity": polarity,
                "working_candidate_de": row[meaning_field],
                "working_confidence": row["working_confidence"], "basis": row["basis"],
            }
            (dry if polarity == "DRY" else moist).add(surface)
    return mapping, dry, moist


def semantic_inputs(
    state_rows: list[dict[str, str]], candidate_rows: list[dict[str, str]]
) -> tuple[
    dict[str, str], dict[str, str], set[str], list[dict[str, object]], dict[str, int]
]:
    target_rows = read_tsv(g761.SRC / "TARGET_WHOLE_PRIORS.tsv")
    carrier_rows = read_tsv(g761.SRC / "CARRIER_CANDIDATE_PRIORS.tsv")
    override_rows = read_tsv(ROOT / g761.CURRENT_OVERRIDES_REL)
    sieve_rows = read_tsv(ROOT / g761.G754_SIEVE_REL)
    quarantine_rows = read_tsv(ROOT / g761.G737_QUARANTINE_REL)
    hold_rows = read_tsv(ROOT / g761.G738_HOLD_REL)
    follower_rows = read_tsv(ROOT / g761.G758_PRIORS_REL)
    dictionary_rows = read_tsv(ROOT / g761.G734_DICT_REL)
    training_rows = read_tsv(ROOT / G736_GRID_REL)
    targets = {row["target_surface"]: row for row in target_rows}
    carriers = {row["surface"]: row for row in carrier_rows}
    overrides = {row["surface"]: row for row in override_rows}
    meanings, sources = g761.semantic_map(
        targets, carriers, overrides, follower_rows, dictionary_rows
    )
    protected_later_wholes = (
        set(g761.g760.FUSED) | set(targets) | set(carriers) | set(overrides)
        | {row["surface"] for row in follower_rows}
        | {row["dry_surface"] for row in state_rows}
        | {row["moist_surface"] for row in state_rows}
        | {row["surface"] for row in candidate_rows}
    )
    training_neutral_repairs = 0
    repair_rows: list[dict[str, object]] = []
    for row in training_rows:
        surface = row["form"]
        if surface in protected_later_wholes:
            continue
        inherited = meanings.get(surface, "NO_INHERITED_WHOLE_VALUE")
        repaired = (
            f"{row['opaque_head_id']}-Ganzform im Feld „{row['revised_body_role_de']}“; "
            "genaue Bedeutung offen"
        )
        meanings[surface] = repaired
        sources[surface] = "GDT736_FORMAL_ROLE_REPAIR_NO_HEAD_NOUN"
        repair_rows.append({
            "surface": surface,
            "opaque_head_class": row["opaque_head_id"],
            "eva_transcription_label": row["eva_transcription_label"],
            "body_surface": row["body"],
            "inherited_gdt734_candidate_de": inherited,
            "repaired_structural_candidate_de": repaired,
            "old_literal_head_noun_detected": int(any(
                term in inherited.lower()
                for term in ("pulver", "samen", "saat", "wurzel", "holz")
            )),
            "decision": "GDT736_STRUCTURAL_FORM_OVERRIDES_GDT734_RETIRED_HEAD_NOUN",
            "eva_initial_semantic_credit": 0,
            "component_export_credit": 0,
        })
        training_neutral_repairs += 1
    for row in state_rows:
        meanings[row["dry_surface"]] = row["dry_working_candidate_de"]
        meanings[row["moist_surface"]] = row["moist_working_candidate_de"]
        sources[row["dry_surface"]] = "GDT762_STATE_PAIR_PRIOR"
        sources[row["moist_surface"]] = "GDT762_STATE_PAIR_PRIOR"
    for row in candidate_rows:
        meanings[row["surface"]] = row["prior_working_candidate_de"]
        sources[row["surface"]] = row["basis"] + "_CANDIDATE_PRIOR"
    retired = {
        row["surface"] for row in quarantine_rows
        if row["gdt737_decision"] == "QUARANTINE_RETIRED_HEAD_NOUN_DERIVATION"
    }
    retired_salt = {
        row["surface"] for row in hold_rows
        if row["decision"] == "HOLD_RETIRED_LITERAL_MATERIAL"
    }
    repaired = protected_later_wholes | {row["form"] for row in training_rows}
    suspect = ({row["surface"] for row in sieve_rows} | retired | retired_salt) - repaired
    audit = {
        "gdt754_source_composed_surfaces": len(sieve_rows),
        "gdt737_retired_head_surfaces": len(retired),
        "gdt738_retired_salt_surfaces": len(retired_salt),
        "later_repaired_surface_exemptions": len(repaired),
        "active_suspect_surface_union": len(suspect),
        "gdt736_training_form_neutral_repairs": training_neutral_repairs,
    }
    repair_rows.sort(key=lambda item: str(item["surface"]))
    return meanings, sources, suspect, repair_rows, audit


def slot_record(
    context: object,
    locus: str,
    ordinal: int,
    state_map: dict[str, dict[str, str]],
    candidate_map: dict[str, dict[str, str]],
    suspect: set[str],
    meanings: dict[str, str],
    sources: dict[str, str],
) -> dict[str, object]:
    line = context.by_line[locus]
    if ordinal < 1 or ordinal > len(line):
        return {
            "ordinal": 0, "surface": "LINE_EDGE", "status": "EDGE",
            "axes": "NONE", "semantic_candidate_de": "NONE",
            "semantic_source": "LINE_EDGE", "unknown_cell": 1,
        }
    token, cell, axes = clean_cell(context, locus, ordinal)
    surface = str(token["eva"])
    exact = bool(context.exact[(locus, int(token["token_index"]))])
    if not exact:
        status = "NONEXACT"
    elif surface in state_map:
        status = "STATE"
    elif surface in candidate_map:
        status = "CANDIDATE"
    elif surface in suspect:
        status = "SUSPECT"
        axes = set()
    else:
        status = "ELIGIBLE"
    semantic = meanings.get(surface, str(cell["v99r7_semantic_value_de"]))
    source = sources.get(surface, "GDT734_CELL")
    if status == "SUSPECT":
        semantic = "QUARANTINED_SOURCE_COMPOSITION"
        source = "GDT754_GDT737_GDT738_COMBINED_QUARANTINE"
    return {
        "ordinal": ordinal, "surface": surface, "status": status,
        "axes": joined(axes), "semantic_candidate_de": semantic,
        "semantic_source": source, "unknown_cell": int(cell["unknown_v99r7"]),
    }


def build_occurrences(
    context: object,
    line_meta: dict[str, dict[str, str]],
    state_map: dict[str, dict[str, str]],
    candidate_map: dict[str, dict[str, str]],
    suspect: set[str],
    meanings: dict[str, str],
    sources: dict[str, str],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for locus, line in context.by_line.items():
        for index, token in enumerate(line):
            surface = str(token["eva"])
            if surface not in candidate_map:
                continue
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            ordinal = index + 1
            slots = {
                key: slot_record(
                    context, locus, ordinal + delta, state_map, candidate_map,
                    suspect, meanings, sources,
                )
                for key, delta in (("l2", -2), ("l1", -1), ("r1", 1), ("r2", 2))
            }
            meta = line_meta[locus]
            prior = candidate_map[surface]
            row: dict[str, object] = {
                "candidate_occurrence_id": "", "page": token["page"],
                "physical_folio": physical_folio(str(token["page"])),
                "locus": locus, "line_number": meta["line_number"],
                "section": token["section"], "language": token["language"],
                "hand": token["hand"], "paragraph_start_line": meta["paragraph_start"],
                "paragraph_end_line": meta["paragraph_end"],
                "candidate_surface": surface, "candidate_ordinal": ordinal,
                "line_token_count": len(line),
                "candidate_line_position": line_position(ordinal, len(line)),
                "prior_working_candidate_de": prior["prior_working_candidate_de"],
                "prior_role": prior["prior_role"], "prior_confidence": prior["prior_confidence"],
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
            }
            for key in ("l2", "l1", "r1", "r2"):
                for field in (
                    "ordinal", "surface", "status", "axes",
                    "semantic_candidate_de", "semantic_source", "unknown_cell",
                ):
                    row[f"{key}_{field}"] = slots[key][field]
            output.append(row)
    output.sort(key=lambda row: (
        str(row["page"]), int(row["line_number"]), int(row["candidate_ordinal"]),
    ))
    counters: Counter[str] = Counter()
    for row in output:
        surface = str(row["candidate_surface"])
        counters[surface] += 1
        row["candidate_occurrence_id"] = f"G762-{surface.upper()}-{counters[surface]:03d}"
    return output


def build_state_exposure(
    context: object, state_rows: list[dict[str, str]], state_map: dict[str, dict[str, str]]
) -> list[dict[str, object]]:
    positions: defaultdict[str, list[tuple[str, dict[str, object], int, int]]] = defaultdict(list)
    for locus, line in context.by_line.items():
        for index, token in enumerate(line):
            surface = str(token["eva"])
            if surface in state_map and context.exact[(locus, int(token["token_index"]))]:
                positions[surface].append((locus, token, index + 1, len(line)))
    output: list[dict[str, object]] = []
    for pair in state_rows:
        for polarity, field in (("DRY", "dry_surface"), ("MOIST", "moist_surface")):
            surface = pair[field]
            rows = positions[surface]
            left_opportunities = 0
            right_opportunities = 0
            for locus, _, ordinal, line_count in rows:
                line = context.by_line[locus]
                if ordinal > 1:
                    left_token = line[ordinal - 2]
                    left_opportunities += int(
                        context.exact[(locus, int(left_token["token_index"]))]
                    )
                if ordinal < line_count:
                    right_token = line[ordinal]
                    right_opportunities += int(
                        context.exact[(locus, int(right_token["token_index"]))]
                    )
            output.append({
                "pair_id": pair["pair_id"], "pair_role": pair["pair_role"],
                "role_stratum": pair["role_stratum"], "polarity": polarity,
                "pair_side": "DRY_SIDE" if polarity == "DRY" else "MOIST_SIDE",
                "pair_side_epistemic_status": "WORKING_PAIR_SIDE_NOT_CONFIRMED_LEXEME",
                "surface": surface, "working_candidate_de": state_map[surface]["working_candidate_de"],
                "working_confidence": pair["working_confidence"], "basis": pair["basis"],
                "reader_exact_occurrences": len(rows),
                "reader_exact_pages": len({str(token["page"]) for _, token, _, _ in rows}),
                "reader_exact_loci": len({locus for locus, _, _, _ in rows}),
                "reader_exact_left_neighbor_opportunities": left_opportunities,
                "reader_exact_right_neighbor_opportunities": right_opportunities,
                "line_position_counts": compact_counts(
                    line_position(ordinal, count) for _, _, ordinal, count in rows
                ),
                "pair_asymmetry_caveat": (
                    "SHO_LINE_INITIAL_BIASED_27_OF_93_VS_CHO_1_OF_45"
                    if pair["pair_id"] == "SP01" else "NONE"
                ),
                "counterevidence": pair["counterevidence"], "component_export_credit": 0,
            })
    return output


def build_state_contacts(
    occurrences: list[dict[str, object]],
    state_map: dict[str, dict[str, str]],
    distance: int,
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    keys = (("L", "l1"), ("R", "r1")) if distance == 1 else (("L", "l2"), ("R", "r2"))
    for occurrence in occurrences:
        for side, key in keys:
            surface = str(occurrence[f"{key}_surface"])
            if occurrence[f"{key}_status"] != "STATE":
                continue
            state = state_map[surface]
            inner_key = "l1" if side == "L" else "r1"
            output.append({
                "contact_id": "", "candidate_occurrence_id": occurrence["candidate_occurrence_id"],
                "page": occurrence["page"], "physical_folio": occurrence["physical_folio"],
                "locus": occurrence["locus"], "candidate_surface": occurrence["candidate_surface"],
                "candidate_ordinal": occurrence["candidate_ordinal"], "state_side": side,
                "state_distance": distance, "state_surface": surface,
                "state_ordinal": occurrence[f"{key}_ordinal"], "state_pair_id": state["pair_id"],
                "state_pair_role": state["pair_role"], "role_stratum": state["role_stratum"],
                "state_polarity": state["polarity"],
                "state_working_candidate_de": state["working_candidate_de"],
                "intervening_surface": occurrence[f"{inner_key}_surface"] if distance == 2 else "NONE",
                "intervening_status": occurrence[f"{inner_key}_status"] if distance == 2 else "NONE",
                "written_line_eva": occurrence["written_line_eva"],
                "reader_exact_candidate_and_state": 1,
                "specific_medium_identity_credit": 0, "component_export_credit": 0,
            })
    prefix = "D" if distance == 1 else "R"
    for number, row in enumerate(output, start=1):
        row["contact_id"] = f"G762-{prefix}{number:03d}"
    return output


def exact_index(
    context: object,
) -> tuple[dict[str, list[tuple[str, int]]], Counter[str], defaultdict[str, set[str]]]:
    positions: defaultdict[str, list[tuple[str, int]]] = defaultdict(list)
    counts: Counter[str] = Counter()
    pages: defaultdict[str, set[str]] = defaultdict(set)
    for locus, line in context.by_line.items():
        for index, token in enumerate(line):
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            surface = str(token["eva"])
            positions[surface].append((locus, index))
            counts[surface] += 1
            pages[surface].add(str(token["page"]))
    return dict(positions), counts, pages


def position_features(
    context: object, positions: list[tuple[str, int]], dry: set[str], moist: set[str]
) -> dict[str, object]:
    values: Counter[str] = Counter()
    loci: set[str] = set()
    line_positions: Counter[str] = Counter()
    for locus, index in positions:
        line = context.by_line[locus]
        loci.add(locus)
        line_positions[line_position(index + 1, len(line))] += 1
        left = None
        right = None
        if index > 0:
            token = line[index - 1]
            if context.exact[(locus, int(token["token_index"]))]:
                left = str(token["eva"])
        if index + 1 < len(line):
            token = line[index + 1]
            if context.exact[(locus, int(token["token_index"]))]:
                right = str(token["eva"])
        values["left_moist"] += int(left in moist)
        values["right_moist"] += int(right in moist)
        values["left_dry"] += int(left in dry)
        values["right_dry"] += int(right in dry)
        values["left_sho_sheo"] += int(left in {"sho", "sheo"})
        values["left_sheo"] += int(left == "sheo")
        values["left_sho"] += int(left == "sho")
        values["direct_moist_occurrence"] += int(left in moist or right in moist)
        values["direct_dry_occurrence"] += int(left in dry or right in dry)
        exact_line = {
            str(token["eva"])
            for token in line
            if context.exact[(locus, int(token["token_index"]))]
        }
        values["same_line_moist"] += int(bool(exact_line & moist))
        values["same_line_dry"] += int(bool(exact_line & dry))
    return {
        **values, "loci": len(loci), "line_position_counts": compact_counts(
            position for position, count in line_positions.items() for _ in range(count)
        ),
    }


def build_candidate_summary(
    occurrences: list[dict[str, object]],
    direct: list[dict[str, object]],
    radius2: list[dict[str, object]],
    exposure_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    exposure = Counter()
    outer_exposure = Counter()
    right_opportunities = Counter()
    for row in exposure_rows:
        polarity = str(row["polarity"])
        count = int(row["reader_exact_occurrences"])
        exposure[polarity] += count
        right_opportunities[polarity] += int(row["reader_exact_right_neighbor_opportunities"])
        if str(row["role_stratum"]).startswith("OUTER_CONTROL"):
            outer_exposure[polarity] += count
    output: list[dict[str, object]] = []
    for candidate in CANDIDATES:
        occ = [row for row in occurrences if row["candidate_surface"] == candidate]
        edges = [row for row in direct if row["candidate_surface"] == candidate]
        relays = [row for row in radius2 if row["candidate_surface"] == candidate]
        polarity = Counter(str(row["state_polarity"]) for row in edges)
        relay_polarity = Counter(str(row["state_polarity"]) for row in relays)
        outer = Counter(
            str(row["state_polarity"]) for row in edges
            if str(row["role_stratum"]).startswith("OUTER_CONTROL")
        )
        strata = defaultdict(set)
        for row in edges:
            strata[str(row["state_polarity"])].add(str(row["role_stratum"]))
        dry_rate = 1000.0 * polarity["DRY"] / exposure["DRY"]
        moist_rate = 1000.0 * polarity["MOIST"] / exposure["MOIST"]
        outer_dry_rate = 1000.0 * outer["DRY"] / outer_exposure["DRY"]
        outer_moist_rate = 1000.0 * outer["MOIST"] / outer_exposure["MOIST"]
        if candidate == "pcheey":
            revised = "Trockenzubereitungs-/Form-II-Eintrag; Identität offen"
            decision = "SELECT_POST_MOIST_FORM_II_RECORD_FIELD__C1_SOURCE_RIVAL"
        elif candidate == "ckhy":
            revised = "Zubereitung/Kompositum, Anfangsstufe; Mischung als Rivale"
            decision = "OPEN_RELAY_ONLY__KEEP_NOMINAL_PREPARATION_BEGIN_PRIOR"
        else:
            revised = "mengenfähiger Zubereitungs-/Stoffträger; genaue Basis offen"
            decision = "PROMOTE_QUANTITY_BEARING_CONTENT_CARRIER__SPECIFIC_MEDIA_UNSELECTED"
        output.append({
            "candidate_surface": candidate, "reader_exact_occurrences": len(occ),
            "reader_exact_pages": len({str(row["page"]) for row in occ}),
            "reader_exact_loci": len({str(row["locus"]) for row in occ}),
            "line_position_counts": compact_counts(str(row["candidate_line_position"]) for row in occ),
            "direct_state_edges": len(edges), "direct_dry_edges": polarity["DRY"],
            "direct_moist_edges": polarity["MOIST"], "outer_direct_dry_edges": outer["DRY"],
            "outer_direct_moist_edges": outer["MOIST"],
            "radius2_dry_relays": relay_polarity["DRY"],
            "radius2_moist_relays": relay_polarity["MOIST"],
            "left_moist_edges_candidate_after_state": sum(
                row["state_polarity"] == "MOIST" and row["state_side"] == "L" for row in edges
            ),
            "left_dry_edges_candidate_after_state": sum(
                row["state_polarity"] == "DRY" and row["state_side"] == "L" for row in edges
            ),
            "right_moist_edges_candidate_before_state": sum(
                row["state_polarity"] == "MOIST" and row["state_side"] == "R" for row in edges
            ),
            "dry_role_strata": len(strata["DRY"]), "moist_role_strata": len(strata["MOIST"]),
            "dry_state_exposure": exposure["DRY"], "moist_state_exposure": exposure["MOIST"],
            "dry_state_right_neighbor_opportunities": right_opportunities["DRY"],
            "moist_state_right_neighbor_opportunities": right_opportunities["MOIST"],
            "after_dry_state_hits_per_1000_right_opportunities": fixed(
                1000.0 * sum(
                    row["state_polarity"] == "DRY" and row["state_side"] == "L" for row in edges
                ) / right_opportunities["DRY"]
            ),
            "after_moist_state_hits_per_1000_right_opportunities": fixed(
                1000.0 * sum(
                    row["state_polarity"] == "MOIST" and row["state_side"] == "L" for row in edges
                ) / right_opportunities["MOIST"]
            ),
            "dry_edges_per_1000_state_occurrences": fixed(dry_rate),
            "moist_edges_per_1000_state_occurrences": fixed(moist_rate),
            "moist_to_dry_normalized_rate_ratio": ratio(moist_rate, dry_rate),
            "outer_dry_edges_per_1000": fixed(outer_dry_rate),
            "outer_moist_edges_per_1000": fixed(outer_moist_rate),
            "outer_moist_to_dry_rate_ratio": ratio(outer_moist_rate, outer_dry_rate),
            "revised_working_candidate_de": revised, "decision": decision,
            "specific_water_selected": 0, "specific_wine_selected": 0,
            "specific_oil_selected": 0, "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def build_pcheey_contexts(
    context: object,
    occurrences: list[dict[str, object]],
    moist: set[str],
    h1_surfaces: set[str],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in occurrences:
        if row["candidate_surface"] != "pcheey":
            continue
        left = str(row["l1_surface"])
        phrase = (
            "Feuchtzubereitung; [Eintrag:] Trockenform II"
            if left == "sheo" else "feuchter Ansatz; [Eintrag:] Trockenform II"
        )
        source_rival = (
            "Mazerat/Feuchtzubereitung aus Trockengut, Form II"
            if left == "sheo" else "Feuchtansatz aus Trockengut, Form II"
        )
        line = context.by_line[str(row["locus"])]
        exact_h1 = [
            str(token["eva"])
            for token in line
            if str(token["eva"]) in h1_surfaces
            and context.exact[(str(row["locus"]), int(token["token_index"]))]
        ]
        output.append({
            "pcheey_context_id": "", "candidate_occurrence_id": row["candidate_occurrence_id"],
            "page": row["page"], "physical_folio": row["physical_folio"],
            "locus": row["locus"], "section": row["section"], "language": row["language"],
            "hand": row["hand"], "paragraph_start_line": row["paragraph_start_line"],
            "paragraph_end_line": row["paragraph_end_line"],
            "candidate_ordinal": row["candidate_ordinal"], "line_position": row["candidate_line_position"],
            "l2_surface": row["l2_surface"], "l1_surface": left,
            "r1_surface": row["r1_surface"], "r2_surface": row["r2_surface"],
            "immediately_after_any_current_moist_whole": int(left in moist),
            "immediately_after_sho_or_sheo": int(left in {"sho", "sheo"}),
            "gdt761_discovery_contact": int(left == "sheo"),
            "new_outer_control_contact": int(left == "sho"),
            "dense_related_form_list_context": int(row["locus"] == "f8r.9"),
            "exact_h1_record_forms_on_line": "|".join(exact_h1),
            "exact_h1_record_form_count_on_line": len(exact_h1),
            "multiple_h1_record_forms_on_line": int(len(exact_h1) >= 2),
            "portable_whole_default_de": "Trockenzubereitungs-/Form-II-Eintrag; Identität offen",
            "working_phrase_relation": "POST_MOIST_FORM_II_RECORD_FIELD",
            "working_phrase_de": phrase,
            "aggressive_source_rival_de": source_rival,
            "result_rival_de": "Feuchtzubereitung, danach Trockenmasse/Rückstand II",
            "record_rival_de": "Feuchtfeld mit nachfolgendem Form-II-Listeneintrag",
            "boundary_rival_de": "getrennt geschriebene Variante einer CH/SH/O-Präparatsschale",
            "medium_rival_de": "Wasser/Wein/Öl; ohne eigene Flüssigkeitsevidenz",
            "written_line_eva": row["written_line_eva"],
            "conditional_working_phrase_license": 1, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    for number, row in enumerate(output, start=1):
        row["pcheey_context_id"] = f"G762-P{number:02d}"
    return output


def build_neighbor_deck(
    occurrences: list[dict[str, object]], counts: Counter[str], pages: defaultdict[str, set[str]]
) -> list[dict[str, object]]:
    groups: defaultdict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        for side, key in (("L", "l1"), ("R", "r1")):
            if row[f"{key}_status"] not in {"ELIGIBLE", "STATE", "CANDIDATE"}:
                continue
            groups[(str(row["candidate_surface"]), str(row[f"{key}_surface"]))].append({
                "side": side, "page": row["page"], "locus": row["locus"],
                "semantic": row[f"{key}_semantic_candidate_de"],
                "source": row[f"{key}_semantic_source"], "status": row[f"{key}_status"],
            })
    output: list[dict[str, object]] = []
    for (candidate, neighbor), rows in groups.items():
        output.append({
            "candidate_surface": candidate, "neighbor_surface": neighbor,
            "direct_contacts": len(rows), "contact_pages": len({str(row["page"]) for row in rows}),
            "contact_loci": len({str(row["locus"]) for row in rows}),
            "side_counts": compact_counts(str(row["side"]) for row in rows),
            "neighbor_status_counts": compact_counts(str(row["status"]) for row in rows),
            "global_reader_exact_occurrences": counts[neighbor],
            "global_reader_exact_pages": len(pages[neighbor]),
            "current_semantic_candidate_de": " || ".join(sorted({str(row["semantic"]) for row in rows})),
            "semantic_sources": "|".join(sorted({str(row["source"]) for row in rows})),
            "relation_identity": "DIRECT_EXACT_COMPLETE_WHOLE_NEIGHBOR",
            "component_export_credit": 0,
        })
    output.sort(key=lambda row: (
        str(row["candidate_surface"]), -int(row["direct_contacts"]), str(row["neighbor_surface"]),
    ))
    return output


def build_pair_matrix(
    direct: list[dict[str, object]],
    radius2: list[dict[str, object]],
    state_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for candidate in CANDIDATES:
        for pair in state_rows:
            drows = [
                row for row in direct
                if row["candidate_surface"] == candidate and row["state_pair_id"] == pair["pair_id"]
            ]
            rrows = [
                row for row in radius2
                if row["candidate_surface"] == candidate and row["state_pair_id"] == pair["pair_id"]
            ]
            output.append({
                "candidate_surface": candidate, "pair_id": pair["pair_id"],
                "pair_role": pair["pair_role"], "role_stratum": pair["role_stratum"],
                "dry_surface": pair["dry_surface"], "moist_surface": pair["moist_surface"],
                "direct_dry_edges": sum(row["state_polarity"] == "DRY" for row in drows),
                "direct_moist_edges": sum(row["state_polarity"] == "MOIST" for row in drows),
                "direct_side_counts": compact_counts(str(row["state_side"]) for row in drows),
                "radius2_dry_relays": sum(row["state_polarity"] == "DRY" for row in rrows),
                "radius2_moist_relays": sum(row["state_polarity"] == "MOIST" for row in rrows),
                "radius2_side_counts": compact_counts(str(row["state_side"]) for row in rrows),
                "specific_medium_identity_credit": 0, "component_export_credit": 0,
            })
    return output


def build_null_census(
    context: object,
    positions: dict[str, list[tuple[str, int]]],
    counts: Counter[str],
    pages: defaultdict[str, set[str]],
    suspect: set[str],
    dry: set[str],
    moist: set[str],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for surface in sorted(counts):
        count = counts[surface]
        if count < 2 or surface in suspect:
            continue
        features = position_features(context, positions[surface], dry, moist)
        pos_counts = str(features["line_position_counts"])
        all_middle = int(pos_counts == f"MIDDLE:{count}")
        left_core = int(features.get("left_sho_sheo", 0))
        output.append({
            "surface": surface, "reader_exact_occurrences": count,
            "reader_exact_pages": len(pages[surface]), "reader_exact_loci": features["loci"],
            "line_position_counts": pos_counts, "all_occurrences_middle": all_middle,
            "left_sheo_contacts_discovery_channel": features.get("left_sheo", 0),
            "left_sho_contacts_outer_channel": features.get("left_sho", 0),
            "left_sho_or_sheo_contacts": left_core,
            "left_sho_or_sheo_fraction": fixed(left_core / count),
            "all_occurrences_after_sho_or_sheo": int(left_core == count),
            "left_any_moist_contacts": features.get("left_moist", 0),
            "right_any_moist_contacts": features.get("right_moist", 0),
            "left_any_dry_contacts": features.get("left_dry", 0),
            "right_any_dry_contacts": features.get("right_dry", 0),
            "occurrences_with_same_line_moist": features.get("same_line_moist", 0),
            "occurrences_with_same_line_dry": features.get("same_line_dry", 0),
            "exact_n3_cohort": int(count == 3),
            "n3_pages3_all_middle_selection_matched": int(
                count == 3 and len(pages[surface]) == 3 and all_middle
            ),
            "n2_to_n4_cohort": int(2 <= count <= 4),
            "gdt761_selected_candidate": int(surface == "pcheey"),
            "component_export_credit": 0,
        })
    output.sort(key=lambda row: (-int(row["all_occurrences_after_sho_or_sheo"]), str(row["surface"])))
    return output


def build_body_controls(
    context: object,
    positions: dict[str, list[tuple[str, int]]],
    counts: Counter[str],
    pages: defaultdict[str, set[str]],
    dry: set[str],
    moist: set[str],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for body in BODY_CONTROLS:
        for head_class, head in HEADS:
            surface = head + body
            features = position_features(context, positions.get(surface, []), dry, moist)
            output.append({
                "body_surface": body, "opaque_head_class": head_class,
                "eva_head_label": head, "whole_surface": surface,
                "reader_exact_occurrences": counts[surface], "reader_exact_pages": len(pages[surface]),
                "left_sho_or_sheo_contacts": features.get("left_sho_sheo", 0),
                "left_any_moist_contacts": features.get("left_moist", 0),
                "right_any_moist_contacts": features.get("right_moist", 0),
                "direct_moist_occurrences": features.get("direct_moist_occurrence", 0),
                "direct_dry_occurrences": features.get("direct_dry_occurrence", 0),
                "selected_target": int(surface == "pcheey"),
                "head_letter_semantic_credit": 0, "body_component_export_credit": 0,
                "interpretation": (
                    "TARGET_POST_MOIST_CONSTRUCTION" if surface == "pcheey"
                    else "WITHIN_BODY_OR_WITHIN_HEAD_CONTROL"
                ),
            })
    return output


def build_h1_specificity_audit(
    context: object,
    training_rows: list[dict[str, str]],
    held_rows: list[dict[str, str]],
    positions: dict[str, list[tuple[str, int]]],
    counts: Counter[str],
    pages: defaultdict[str, set[str]],
    dry: set[str],
    moist: set[str],
) -> list[dict[str, object]]:
    provenance: dict[str, str] = {}
    body_by_surface: dict[str, str] = {}
    for row in training_rows:
        if row["opaque_head_id"] != "H1":
            continue
        provenance[row["form"]] = "GDT736_TRAINING_24_BODY_GRID"
        body_by_surface[row["form"]] = row["body"]
    for row in held_rows:
        if row["opaque_head_id"] != "H1":
            continue
        provenance[row["form"]] = "GDT737_HELD_120_BODY_TRANSFER"
        body_by_surface[row["form"]] = row["body"]
    output: list[dict[str, object]] = []
    for surface in sorted(provenance):
        features = position_features(context, positions.get(surface, []), dry, moist)
        output.append({
            "surface": surface, "body_surface": body_by_surface[surface],
            "opaque_head_class": "H1", "eva_transcription_label": "p",
            "source_universe": provenance[surface],
            "reader_exact_occurrences": counts[surface],
            "reader_exact_pages": len(pages[surface]),
            "line_position_counts": features["line_position_counts"],
            "left_sho_contacts": features.get("left_sho", 0),
            "left_sheo_contacts": features.get("left_sheo", 0),
            "left_sho_or_sheo_contacts": features.get("left_sho_sheo", 0),
            "selected_pcheey": int(surface == "pcheey"),
            "head_class_is_analyst_variable": 1,
            "eva_p_letter_or_semantic_credit": 0,
            "component_export_credit": 0,
            "interpretation": (
                "TARGET_ACCOUNTS_FOR_ALL_3_READER_EXACT_H1_POST_MOIST_CONTACTS"
                if surface == "pcheey" else "H1_ECOLOGY_CONTROL"
            ),
        })
    output.sort(key=lambda row: (0 if row["selected_pcheey"] else 1, str(row["surface"])))
    return output


def exact_ngram_counts(
    context: object, patterns: dict[str, tuple[str, ...]]
) -> dict[str, tuple[int, int, str]]:
    found: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
    for locus, line in context.by_line.items():
        surfaces = [str(token["eva"]) for token in line]
        exact = [bool(context.exact[(locus, int(token["token_index"]))]) for token in line]
        for key, pattern in patterns.items():
            width = len(pattern)
            for start in range(0, len(line) - width + 1):
                if tuple(surfaces[start:start + width]) == pattern and all(exact[start:start + width]):
                    found[key].append((str(line[start]["page"]), locus))
    return {
        key: (
            len(found[key]), len({page for page, _ in found[key]}),
            "|".join(locus for _, locus in found[key]) or "NONE",
        )
        for key in patterns
    }


def build_repeated_constructions(context: object) -> list[dict[str, object]]:
    patterns = {
        "daiin ckhy": ("daiin", "ckhy"),
        "sheo pcheey": ("sheo", "pcheey"),
        "sho pcheey": ("sho", "pcheey"),
        "ol s aiin": ("ol", "s", "aiin"),
    }
    counted = exact_ngram_counts(context, patterns)
    interpretations = {
        "daiin ckhy": "REPEATED_AMOUNT_OR_VALUE_CONDITIONED_CKHY_FRAME",
        "sheo pcheey": "GDT761_DISCOVERY_PREPARATION_TO_FORM_II_FRAME",
        "sho pcheey": "OUTER_CONTROL_REPLICATION_OF_DIRECTED_FORM_II_FRAME",
        "ol s aiin": "REPEATED_OL_PLUS_AMOUNT_FORMULA_ECOLOGY",
    }
    output: list[dict[str, object]] = []
    for pattern in patterns:
        occurrences, page_count, loci = counted[pattern]
        output.append({
            "construction_id": "", "construction_type": "CONTIGUOUS_EXACT_NGRAM",
            "written_pattern_eva": pattern, "reader_exact_occurrences": occurrences,
            "reader_exact_pages": page_count, "loci": loci, "intervening_counts": "NONE",
            "interpretation": interpretations[pattern],
            "exact_working_relation_license": int(pattern in {"sheo pcheey", "sho pcheey"}),
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    gapped: list[tuple[str, str]] = []
    for locus, line in context.by_line.items():
        surfaces = [str(token["eva"]) for token in line]
        exact = [bool(context.exact[(locus, int(token["token_index"]))]) for token in line]
        for start in range(0, len(line) - 3):
            if (
                surfaces[start] == "sheo" and surfaces[start + 1] == "pcheey"
                and surfaces[start + 3] == "daiin" and all(exact[start:start + 4])
            ):
                gapped.append((locus, surfaces[start + 2]))
    output.append({
        "construction_id": "", "construction_type": "GAPPED_EXACT_FOUR_TOKEN_FRAME",
        "written_pattern_eva": "sheo pcheey X daiin",
        "reader_exact_occurrences": len(gapped),
        "reader_exact_pages": len({context.by_line[locus][0]["page"] for locus, _ in gapped}),
        "loci": "|".join(locus for locus, _ in gapped) or "NONE",
        "intervening_counts": compact_counts(value for _, value in gapped),
        "interpretation": "FORM_II_FIELD_FOLLOWED_BY_VALUE_OR_AMOUNT_FRAME",
        "exact_working_relation_license": 0, "confirmed_plaintext": 0,
        "component_export_credit": 0,
    })
    for number, row in enumerate(output, start=1):
        row["construction_id"] = f"G762-C{number:02d}"
    return output


def build_ol_amount_contacts(
    quantity_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in quantity_rows:
        ol_sides: list[str] = []
        if (
            row["left_surface"] == "ol" and row["left_reader_exact"] == "1"
            and row["left_source_composed_quarantined"] == "0"
        ):
            ol_sides.append("L")
        if (
            row["right_surface"] == "ol" and row["right_reader_exact"] == "1"
            and row["right_source_composed_quarantined"] == "0"
        ):
            ol_sides.append("R")
        if not ol_sides:
            continue
        preferred = "R" if row["expression_line_position"] == "FIRST" else "L"
        if len(ol_sides) == 2:
            decision = "BILATERAL_AMBIGUOUS_CONTACT"
            license_value = 0
        elif preferred in ol_sides:
            decision = "EXACT_AMOUNT_CONTENT_PHRASE_LICENSE"
            license_value = 1
        else:
            decision = "CONTACT_SUPPORT_ONLY_NONPREFERRED_SIDE"
            license_value = 0
        opposite_surface = (
            row["right_surface"] if "L" in ol_sides and "R" not in ol_sides
            else row["left_surface"] if "R" in ol_sides and "L" not in ol_sides
            else "NONE"
        )
        opposite_semantic = (
            row["right_semantic_candidate_de"] if "L" in ol_sides and "R" not in ol_sides
            else row["left_semantic_candidate_de"] if "R" in ol_sides and "L" not in ol_sides
            else "NONE"
        )
        base_phrase = f"Ansatzstoff: {row['amount_candidate_de']}"
        extended = (
            base_phrase + "; abseihen"
            if opposite_surface == "oly" and opposite_semantic == "abseihen" else base_phrase
        )
        output.append({
            "ol_amount_contact_id": "", "expression_id": row["expression_id"],
            "page": row["page"], "physical_folio": row["physical_folio"],
            "locus": row["locus"], "section": row["section"],
            "language": row["language"], "hand": row["hand"],
            "expression_line_position": row["expression_line_position"],
            "amount_mode": row["mode"], "amount_expression_eva": row["source_expression_eva"],
            "amount_candidate_de": row["amount_candidate_de"],
            "amount_rivals_de": row["amount_rivals_de"],
            "amount_working_confidence": row["amount_working_confidence"],
            "ol_sides_relative_to_amount": "|".join(ol_sides),
            "ol_directed_edges": len(ol_sides), "position_expected_side": preferred,
            "position_expected_side_present": int(preferred in ol_sides),
            "opposite_neighbor_surface": opposite_surface,
            "opposite_neighbor_semantic_candidate_de": opposite_semantic,
            "working_phrase_de": base_phrase,
            "extended_working_phrase_de": extended,
            "ol_identity_rivals_de": "Grundansatz|Stoff/Basis|Öl oder ölige Grundlage",
            "decision": decision, "conditional_phrase_license": license_value,
            "written_line_eva": row["written_line_eva"],
            "specific_medium_selected": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    output.sort(key=lambda row: (str(row["page"]), str(row["locus"]), str(row["expression_id"])))
    for number, row in enumerate(output, start=1):
        row["ol_amount_contact_id"] = f"G762-A{number:02d}"
    return output


def build_boundary_audit(
    context: object, counts: Counter[str], pages: defaultdict[str, set[str]]
) -> list[dict[str, object]]:
    patterns = {
        "sho pcheey": ("sho", "pcheey"), "sheo pcheey": ("sheo", "pcheey"),
        "cho pcheey": ("cho", "pcheey"), "cheo pcheey": ("cheo", "pcheey"),
    }
    ngrams = exact_ngram_counts(context, patterns)
    output: list[dict[str, object]] = []
    for pattern in patterns:
        occurrences, page_count, loci = ngrams[pattern]
        output.append({
            "audit_kind": "SPACED_EXACT_BIGRAM", "surface_or_span": pattern,
            "reader_exact_occurrences": occurrences, "reader_exact_pages": page_count,
            "loci": loci, "body_relation": "PCHEEY_EXACT_BODY",
            "polarity_or_shell": "MOIST" if pattern.startswith(("sho ", "sheo ")) else "DRY",
            "interpretation": "OBSERVED_DIRECT_CONSTRUCTION" if occurrences else "UNOBSERVED_POLARITY_CONTROL",
            "component_export_credit": 0,
        })
    fused = (
        ("shopcheey", "MOIST_EXACT_BODY"), ("sheopcheey", "MOIST_EXACT_BODY"),
        ("chopcheey", "DRY_EXACT_BODY"), ("cheopcheey", "DRY_EXACT_BODY"),
        ("shopchey", "MOIST_NEAR_BODY"), ("sheopchey", "MOIST_NEAR_BODY"),
        ("chopchey", "DRY_NEAR_BODY"), ("cheopchey", "DRY_NEAR_BODY"),
        ("opcheey", "O_SHELL_EXACT_BODY"), ("qopcheey", "QO_SHELL_EXACT_BODY"),
        ("pchedy", "H1_DRY_NEAR_BODY"), ("tcheey", "T_DRY_NEAR_BODY"),
    )
    for surface, shell in fused:
        output.append({
            "audit_kind": "FUSED_WHOLE_OR_FORM_NEAR_CONTROL", "surface_or_span": surface,
            "reader_exact_occurrences": counts[surface], "reader_exact_pages": len(pages[surface]),
            "loci": "MULTIPLE_OR_SEE_CACHE" if counts[surface] else "NONE",
            "body_relation": "CHEEY_OR_CHEY_NEIGHBORHOOD", "polarity_or_shell": shell,
            "interpretation": "BOUNDARY_SHELL_RIVAL_NOT_COMPONENT_LICENSE",
            "component_export_credit": 0,
        })
    return output


def direct_state_counts_for_surface(
    context: object,
    positions: list[tuple[str, int]],
    state_map: dict[str, dict[str, str]],
) -> tuple[Counter[str], Counter[str], Counter[str]]:
    polarity: Counter[str] = Counter()
    outer: Counter[str] = Counter()
    strata: Counter[str] = Counter()
    for locus, index in positions:
        line = context.by_line[locus]
        for neighbor_index in (index - 1, index + 1):
            if neighbor_index < 0 or neighbor_index >= len(line):
                continue
            token = line[neighbor_index]
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            state = state_map.get(str(token["eva"]))
            if not state:
                continue
            polarity[state["polarity"]] += 1
            strata[state["role_stratum"]] += 1
            if state["role_stratum"].startswith("OUTER_CONTROL"):
                outer[state["polarity"]] += 1
    return polarity, outer, strata


def build_confounders(
    context: object,
    positions: dict[str, list[tuple[str, int]]],
    counts: Counter[str],
    pages: defaultdict[str, set[str]],
    state_map: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    roles = {
        "ckhy": ("TARGET_OPEN_RELAY", "NONE"),
        "pcheey": ("TARGET_PREPARATION_COMPLEMENT", "H1_PLUS_DRY_BODY_FAMILY"),
        "ol": ("TARGET_GENERIC_CARRIER", "CONTAINED_IN_CHOL_SHOL_CHEOL_SHEOL"),
        "shor": ("MOIST_PSEUDOPOSITIVE", "SH_BASE_AND_REPRODUCTIVE_PART_FAMILY"),
        "chor": ("DRY_PSEUDOPOSITIVE", "CH_BASE_AND_REPRODUCTIVE_PART_FAMILY"),
        "daiin": ("AMOUNT_VALUE_CONTROL", "AMOUNT_OR_VALUE_ROLE"),
        "oraiin": ("AMOUNT_FORMULA_CONTROL", "AMOUNT_OR_VALUE_ROLE"),
    }
    output: list[dict[str, object]] = []
    for surface in CONFOUNDERS:
        polarity, outer, strata = direct_state_counts_for_surface(
            context, positions.get(surface, []), state_map
        )
        output.append({
            "surface": surface, "control_role": roles[surface][0],
            "reader_exact_occurrences": counts[surface], "reader_exact_pages": len(pages[surface]),
            "direct_dry_edges_all11": polarity["DRY"],
            "direct_moist_edges_all11": polarity["MOIST"],
            "outer_direct_dry_edges_p01_p09": outer["DRY"],
            "outer_direct_moist_edges_p01_p09": outer["MOIST"],
            "role_stratum_contacts": "|".join(f"{key}:{strata[key]}" for key in sorted(strata)) or "NONE",
            "form_or_role_confound": roles[surface][1],
            "naive_moist_selectivity_pseudopositive": int(
                surface == "shor" and polarity["MOIST"] > polarity["DRY"]
            ),
            "specific_medium_selected": 0,
            "interpretation": (
                "FORM_OVERLAP_AND_BROAD_POLARITY_NEUTRAL_HOST"
                if surface == "ol" else "CONTROL_PREVENTS_NAIVE_MEDIUM_PROMOTION"
            ),
            "component_export_credit": 0,
        })
    return output


def build_historical_rival_audit(
    rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    """Compare period role vocabulary without matching it to EVA spelling."""
    selected_ids = {
        "E015", "E018", "E022", "E023", "E025",
        "E028", "E029", "E030", "E037",
    }
    selected = {
        row["candidate_id"]: row
        for row in rows
        if row["candidate_id"] in selected_ids
    }
    if set(selected) != selected_ids:
        raise AssertionError("historical rival deck changed")
    signatures = {
        "ckhy": (
            "NOMINAL_PREPARATION_OR_COMPOSITUM_BEGIN; no independent PROCESS, "
            "LIQUID, or VESSEL axis"
        ),
        "pcheey": (
            "POST_MOIST_FORM_II_RECORD_FIELD; C1 dry-source rival; no independent "
            "PROCESS, LIQUID, or VESSEL axis"
        ),
        "ol": (
            "QUANTITY_BEARING_CONTENT_CARRIER; no independent LIQUID, OIL, "
            "WATER, WINE, or VESSEL axis"
        ),
    }
    decisions: dict[tuple[str, str], str] = {}
    for surface in CANDIDATES:
        for candidate_id in selected_ids:
            decisions[(surface, candidate_id)] = (
                "HISTORICAL_CATEGORY_OR_RIVAL_ONLY__NO_TARGET_ASSIGNMENT"
            )
    decisions[("ckhy", "E025")] = "ROLE_COMPATIBLE_PREPARATION_NOUN_CATEGORY_ONLY"
    decisions[("pcheey", "E015")] = (
        "DRY_STATE_CATEGORY_COMPATIBLE__SOURCE_RELATION_UNSPOKEN"
    )
    decisions[("pcheey", "E023")] = (
        "POST_MOIST_ECOLOGY_COMPATIBLE__PROCESS_NOT_ASSIGNED"
    )
    decisions[("pcheey", "E025")] = "RECORD_PREPARATION_CATEGORY_COMPATIBLE_ONLY"
    decisions[("ol", "E025")] = "GENERAL_PREPARATION_CARRIER_COMPATIBLE_ONLY"
    for candidate_id in ("E028", "E029", "E030"):
        decisions[("ol", candidate_id)] = (
            "LIVE_SPECIFIC_MEDIUM_RIVAL__LIQUID_AXIS_MISSING"
        )
    decisions[("ol", "E022")] = (
        "PROCESS_NEIGHBOR_COMPATIBLE_AT_F94V9__NOT_OL_IDENTITY"
    )
    output: list[dict[str, object]] = []
    for surface in CANDIDATES:
        for candidate_id in sorted(selected):
            row = selected[candidate_id]
            output.append({
                "surface": surface,
                "historical_candidate_id": candidate_id,
                "historical_expression": row["normalized_expression"],
                "historical_working_gloss_de": row["working_gloss_de"],
                "historical_candidate_kind": row["candidate_kind"],
                "historical_required_axes": row["required_all_axes"],
                "historical_content_slot_axis": row["content_slot_axis"],
                "historical_source_ids": row["source_ids"],
                "historical_attested_form": row["attested_form"],
                "historical_locator": row["locator"],
                "target_observed_signature": signatures[surface],
                "decision": decisions[(surface, candidate_id)],
                "eva_spelling_match_credit": 0,
                "target_assignment_credit": 0,
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
    return output


def build_role_scorecard(
    rows: list[dict[str, str]], summaries: list[dict[str, object]]
) -> list[dict[str, object]]:
    by_candidate = {str(row["candidate_surface"]): row for row in summaries}
    outcomes = {
        ("ckhy", "AQUEOUS_OR_WINE_MEDIUM"): (3, "REJECT_SPECIFIC_MEDIUM"),
        ("ckhy", "OIL_OR_OLEAGINOUS_BASE"): (4, "UNSUPPORTED_SPECIFIC_MEDIUM"),
        ("ckhy", "NOMINAL_PREPARATION_OR_COMPOSITUM_BEGIN"): (1, "SELECT_WORKING_WHOLE_ROLE"),
        ("ckhy", "OPEN_RELAY_OR_OTHER"): (2, "SELECT_RELATIONAL_DISPOSITION"),
        ("pcheey", "AQUEOUS_WINE_OR_OIL_MEDIUM"): (5, "REJECT_SPECIFIC_MEDIUM"),
        ("pcheey", "DRY_SOURCE_OR_COMPLEMENT"): (2, "LIVE_C1_EXACT_SPAN_SEMANTIC"),
        ("pcheey", "POST_MOIST_RESULT"): (3, "LIVE_CREATIVE_RIVAL"),
        ("pcheey", "RECORD_FORM_FIELD"): (1, "SELECT_PORTABLE_WHOLE_AND_CONSTRUCTION_ROLE"),
        ("pcheey", "OPAQUE_OR_BOUND_SHELL"): (4, "LIVE_BOUNDARY_RIVAL"),
        ("ol", "AQUEOUS_OR_WINE_MEDIUM"): (5, "REJECT_SPECIFIC_MEDIUM"),
        ("ol", "OIL_OR_OLEAGINOUS_BASE"): (3, "LIVE_C0_WHOLE_RIVAL_UNSELECTED"),
        ("ol", "GENERAL_PREPARATION_OR_CARRIER"): (1, "SELECT_GENERAL_ROLE"),
        ("ol", "MATERIAL_OR_PROPERTY_HEAD"): (2, "LIVE_RIVAL"),
        ("ol", "OPAQUE_OR_OTHER"): (4, "WEAK_RIVAL"),
    }
    output: list[dict[str, object]] = []
    for row in rows:
        summary = by_candidate[row["surface"]]
        rank, decision = outcomes[(row["surface"], row["hypothesis_role"])]
        evidence = (
            f"D1 dry={summary['direct_dry_edges']}, moist={summary['direct_moist_edges']}; "
            f"outer dry={summary['outer_direct_dry_edges']}, moist={summary['outer_direct_moist_edges']}; "
            f"R2 dry={summary['radius2_dry_relays']}, moist={summary['radius2_moist_relays']}"
        )
        if row["surface"] == "pcheey":
            evidence += (
                "; 3/3 direkt nach sho|sheo, sämtliche anderen reader-exakten "
                "H1-Fälle 0/196; alle drei Zeilen enthalten mehrere H1-Recordformen"
            )
        if row["surface"] == "ol" and row["hypothesis_role"] == "GENERAL_PREPARATION_OR_CARRIER":
            evidence += "; 16 Mengenexpressionsstellen/17 Kanten auf 13 Seiten, 8 gerichtete Phrasenlizenzen"
        output.append({
            "hypothesis_id": row["hypothesis_id"], "surface": row["surface"],
            "hypothesis_role": row["hypothesis_role"],
            "working_realization_de": row["working_realization_de"],
            "rank_within_candidate": rank,
            "evidence": evidence,
            "positive_signature": row["positive_signature"],
            "negative_signature": row["negative_signature"], "decision": decision,
            "specific_medium_identity_selected": 0, "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    output.sort(key=lambda row: (str(row["surface"]), int(row["rank_within_candidate"])))
    return output


def build_revisions(
    priors: list[dict[str, str]], summaries: list[dict[str, object]]
) -> list[dict[str, object]]:
    by_summary = {str(row["candidate_surface"]): row for row in summaries}
    output: list[dict[str, object]] = []
    for prior in priors:
        surface = prior["surface"]
        summary = by_summary[surface]
        if surface == "pcheey":
            confidence = "C2_POST_MOIST_FORM_FIELD__C1_DRY_SOURCE_READING"
            evidence = (
                "3/3 nach sho|sheo auf 3 Seiten; einzige clean recurrent whole mit "
                "vollständiger gerichteter Deckung; pchey/pchy 0/7; jede Zeile hat "
                "mehrere H1-Recordformen"
            )
            counter = "Zwei Stellen waren Auswahlgrund in GDT761; nur sho pcheey ist Außenreplikation; fused shell und Record-Feld bleiben Rivalen"
        elif surface == "ckhy":
            confidence = "C1_NOMINAL_PREPARATION_BEGIN__C0_MEDIUM__R2_RELAY_ONLY"
            evidence = "25 Vorkommen; direkt 1 trocken/2 feucht, außen nur ckhy chol; Radius-zwei 1 trocken/3 feucht"
            counter = "Mischungsidentität bleibt Gegenhypothese; keine Flüssigkeits-, Gefäß- oder Mischhandlung"
        else:
            confidence = "C2_GENERAL_CARRIER__C1_QUANTITY_BEARING_CONTENT__C0_WATER_WINE_OIL"
            evidence = "376 Vorkommen; 58/34 direkte und 37/25 Radius-zwei Trocken/Feuchtkontakte; 16 Mengenexpressionsstellen/17 Kanten auf 13 Seiten, davon 8 gerichtete Phrasenlizenzen"
            counter = "Formüberlappung mit chol/shol/cheol/sheol; Öl bleibt ungestützter Ganzwortrivale"
        new_role = {
            "ckhy": "NOMINAL_PREPARATION_OR_COMPOSITUM_BEGIN__OPEN_RELAY",
            "pcheey": "POST_MOIST_FORM_II_RECORD_FIELD__C1_DRY_SOURCE_RIVAL",
            "ol": "QUANTITY_BEARING_PREPARATION_OR_CONTENT_CARRIER",
        }[surface]
        output.append({
            "surface": surface, "old_working_candidate_de": prior["prior_working_candidate_de"],
            "new_portable_working_candidate_de": summary["revised_working_candidate_de"],
            "old_role": prior["prior_role"], "new_role": new_role,
            "new_confidence": confidence,
            "evidence": evidence, "counterevidence": counter, "decision": summary["decision"],
            "conditional_exact_span_licenses": 3 if surface == "pcheey" else 8 if surface == "ol" else 0,
            "specific_medium_selected": 0, "global_component_export_allowed": 0,
            "confirmed_lexeme": 0,
        })
    return output


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    state_rows = read_tsv(SRC / "STATE_PAIR_PRIORS.tsv")
    candidate_rows = read_tsv(SRC / "CANDIDATE_PRIORS.tsv")
    hypothesis_rows = read_tsv(SRC / "ROLE_HYPOTHESES.tsv")
    quantity_rows = read_tsv(ROOT / G760_QUANTITY_REL)
    historical_rows = read_tsv(ROOT / G755_HISTORICAL_REL)
    training_rows = read_tsv(ROOT / G736_GRID_REL)
    held_rows = read_tsv(ROOT / G737_FORM_REL)
    if len(state_rows) != 11 or len(candidate_rows) != 3 or len(hypothesis_rows) != 14:
        raise AssertionError("fixed source decks required")
    candidate_map = {row["surface"]: row for row in candidate_rows}
    state_map, dry, moist = state_maps(state_rows)
    if tuple(candidate_map) != CANDIDATES or len(state_map) != 22:
        raise AssertionError("candidate or state universe changed")
    meanings, sources, suspect, semantic_repairs, quarantine = semantic_inputs(
        state_rows, candidate_rows
    )
    context, line_meta, inherited_guard = (
        g761.g760.g759.g758.g756.g755.g753.g752.g751.load_context()
    )
    occurrences = build_occurrences(
        context, line_meta, state_map, candidate_map, suspect, meanings, sources
    )
    exposure = build_state_exposure(context, state_rows, state_map)
    direct = build_state_contacts(occurrences, state_map, 1)
    radius2 = build_state_contacts(occurrences, state_map, 2)
    pair_matrix = build_pair_matrix(direct, radius2, state_rows)
    positions, counts, pages = exact_index(context)
    summaries = build_candidate_summary(occurrences, direct, radius2, exposure)
    h1_surfaces = {
        row["form"]
        for row in (*training_rows, *held_rows)
        if row["opaque_head_id"] == "H1"
    }
    pcheey_contexts = build_pcheey_contexts(
        context, occurrences, moist, h1_surfaces
    )
    neighbors = build_neighbor_deck(occurrences, counts, pages)
    repeated = build_repeated_constructions(context)
    ol_amount = build_ol_amount_contacts(quantity_rows)
    null_census = build_null_census(context, positions, counts, pages, suspect, dry, moist)
    body_controls = build_body_controls(context, positions, counts, pages, dry, moist)
    h1_audit = build_h1_specificity_audit(
        context, training_rows, held_rows, positions, counts, pages, dry, moist
    )
    boundary = build_boundary_audit(context, counts, pages)
    confounders = build_confounders(context, positions, counts, pages, state_map)
    historical = build_historical_rival_audit(historical_rows)
    scorecard = build_role_scorecard(hypothesis_rows, summaries)
    revisions = build_revisions(candidate_rows, summaries)

    expected_exposure = {
        "cho": 45, "sho": 93, "chy": 114, "shy": 67, "chey": 282,
        "shey": 179, "cheey": 137, "sheey": 105, "chdy": 89, "shdy": 25,
        "chedy": 296, "shedy": 219, "cheedy": 39, "sheedy": 41,
        "chol": 303, "shol": 146, "cheol": 118, "sheol": 71,
        "cheor": 56, "sheor": 31, "cheo": 36, "sheo": 28,
    }
    if {str(row["surface"]): int(row["reader_exact_occurrences"]) for row in exposure} != expected_exposure:
        raise AssertionError("11-pair exposure universe changed")
    if Counter(str(row["candidate_surface"]) for row in occurrences) != Counter({
        "ol": 376, "ckhy": 25, "pcheey": 3,
    }):
        raise AssertionError("candidate occurrence universe changed")
    if len(occurrences) != 404 or len(direct) != 98 or len(radius2) != 66:
        raise AssertionError("occurrence or relation universe changed")
    if len(pair_matrix) != 33:
        raise AssertionError("candidate pair matrix changed")
    summary_map = {str(row["candidate_surface"]): row for row in summaries}
    expected_contacts = {"ckhy": (1, 2, 1, 3), "pcheey": (0, 3, 0, 0), "ol": (58, 34, 37, 25)}
    for surface, expected in expected_contacts.items():
        row = summary_map[surface]
        actual = tuple(int(row[field]) for field in (
            "direct_dry_edges", "direct_moist_edges", "radius2_dry_relays", "radius2_moist_relays",
        ))
        if actual != expected:
            raise AssertionError(f"{surface} contact profile changed: {actual}")
    if len(pcheey_contexts) != 3 or Counter(
        str(row["l1_surface"]) for row in pcheey_contexts
    ) != Counter({"sheo": 2, "sho": 1}):
        raise AssertionError("pcheey directed construction changed")
    if any(
        int(row["exact_h1_record_form_count_on_line"]) < 2
        for row in pcheey_contexts
    ):
        raise AssertionError("pcheey multi-H1 line context changed")
    body_map = {str(row["whole_surface"]): row for row in body_controls}
    if (int(body_map["pchey"]["reader_exact_occurrences"]), int(body_map["pchy"]["reader_exact_occurrences"])) != (6, 1):
        raise AssertionError("H1 dry control recurrence changed")
    if sum(int(body_map[surface]["left_sho_or_sheo_contacts"]) for surface in ("pchey", "pchy")):
        raise AssertionError("H1 dry controls gained sho or sheo predecessor")
    fully_directed = [row for row in null_census if row["all_occurrences_after_sho_or_sheo"] == 1]
    if [row["surface"] for row in fully_directed] != ["pcheey"]:
        raise AssertionError(f"directed recurrent null changed: {fully_directed}")
    if sum(int(row["exact_n3_cohort"]) for row in null_census) != 235:
        raise AssertionError("exact recurrence-three control cohort changed")
    if sum(int(row["n3_pages3_all_middle_selection_matched"]) for row in null_census) != 91:
        raise AssertionError("selection-matched control cohort changed")
    if sum(int(row["n2_to_n4_cohort"]) for row in null_census) != 929:
        raise AssertionError("N2-N4 control cohort changed")
    if sum(int(row["reader_exact_occurrences"]) for row in h1_audit) != 199:
        raise AssertionError("full H1 reader-exact universe changed")
    if sum(int(row["left_sho_or_sheo_contacts"]) for row in h1_audit) != 3:
        raise AssertionError("full H1 post-moist contact universe changed")
    if sum(
        int(row["left_sho_or_sheo_contacts"]) for row in h1_audit
        if row["surface"] != "pcheey"
    ) != 0:
        raise AssertionError("non-pcheey H1 post-moist controls changed")
    if sum(int(row["reader_exact_right_neighbor_opportunities"]) for row in exposure if row["polarity"] == "DRY") != 1158:
        raise AssertionError("dry-side right-neighbor opportunities changed")
    if sum(int(row["reader_exact_right_neighbor_opportunities"]) for row in exposure if row["polarity"] == "MOIST") != 788:
        raise AssertionError("moist-side right-neighbor opportunities changed")
    if any(int(row["specific_medium_identity_selected"]) for row in scorecard):
        raise AssertionError("specific medium may not be selected")
    if len(ol_amount) != 16 or sum(int(row["ol_directed_edges"]) for row in ol_amount) != 17:
        raise AssertionError("ol amount-expression contact universe changed")
    if len({str(row["page"]) for row in ol_amount}) != 13:
        raise AssertionError("ol amount-expression pages changed")
    if Counter(str(row["decision"]) for row in ol_amount) != Counter({
        "EXACT_AMOUNT_CONTENT_PHRASE_LICENSE": 8,
        "BILATERAL_AMBIGUOUS_CONTACT": 1,
        "CONTACT_SUPPORT_ONLY_NONPREFERRED_SIDE": 7,
    }):
        raise AssertionError("ol amount-expression position dispatch changed")
    if any(str(row["page"]).startswith("f84") for row in occurrences):
        raise AssertionError("sealed page entered candidate atlas")

    tables = (
        occurrences, exposure, direct, radius2, pair_matrix, summaries, pcheey_contexts,
        neighbors, repeated, ol_amount, null_census, body_controls, h1_audit,
        boundary, confounders, semantic_repairs, historical, scorecard,
        pcheey_contexts, revisions,
    )
    for name, rows in zip(OUTPUT_NAMES[:-1], tables):
        write_tsv(output_dir / name, rows, list(rows[0]))

    result = {
        "schema": "GDT762_RESULT_V1", "status": STATUS,
        "scope": {
            "candidate_occurrences": len(occurrences),
            "candidate_pages": len({str(row["page"]) for row in occurrences}),
            "candidate_loci": len({str(row["locus"]) for row in occurrences}),
            "state_pairs": 11, "state_surfaces": 22,
            "state_reader_exact_occurrences": sum(int(row["reader_exact_occurrences"]) for row in exposure),
            "dry_state_exposure": sum(int(row["reader_exact_occurrences"]) for row in exposure if row["polarity"] == "DRY"),
            "moist_state_exposure": sum(int(row["reader_exact_occurrences"]) for row in exposure if row["polarity"] == "MOIST"),
            "direct_candidate_state_edges": len(direct), "radius2_state_relays": len(radius2),
            "candidate_pair_matrix_rows": len(pair_matrix),
            "candidate_direct_neighbor_types": len(neighbors),
            "repeated_candidate_constructions": len(repeated),
            "ol_amount_expression_positions": len(ol_amount),
            "ol_amount_directed_edges": sum(int(row["ol_directed_edges"]) for row in ol_amount),
            "ol_amount_phrase_licenses": sum(int(row["conditional_phrase_license"]) for row in ol_amount),
            "clean_recurrent_null_surfaces": len(null_census),
            "body_family_control_rows": len(body_controls), "boundary_shell_audit_rows": len(boundary),
            "h1_specificity_audit_rows": len(h1_audit),
            "confounder_rows": len(confounders),
            "semantic_precedence_repairs": len(semantic_repairs),
            "historical_role_rival_rows": len(historical),
            "role_hypotheses": len(scorecard),
            "conditional_pcheey_working_span_licenses": len(pcheey_contexts),
        },
        "pcheey_result": {
            "reader_exact_occurrences": 3, "immediately_after_sho_or_sheo": 3,
            "left_neighbor_counts": "sheo:2|sho:1", "gdt761_discovery_contacts": 2,
            "new_outer_control_contacts": 1,
            "other_h1_dry_forms_occurrences": 7,
            "other_h1_dry_forms_after_sho_or_sheo": 0,
            "clean_n3_control_cohort": 235,
            "selection_matched_n3_pages3_all_middle_cohort": 91,
            "clean_n2_to_n4_control_cohort": 929,
            "all_clean_recurrent_surfaces_with_full_sho_sheo_predecessor_coverage": 1,
            "all_h1_reader_exact_occurrences": 199,
            "other_h1_reader_exact_occurrences": 196,
            "all_h1_after_reader_exact_sho_or_sheo": 3,
            "other_h1_after_reader_exact_sho_or_sheo": 0,
            "dry_side_right_neighbor_opportunities": 1158,
            "moist_side_right_neighbor_opportunities": 788,
            "all_three_lines_have_multiple_h1_record_forms": True,
            "portable_whole_default_de": "Trockenzubereitungs-/Form-II-Eintrag; Identität offen",
            "minimal_directed_renderer_sheo_pcheey_de": "Feuchtzubereitung; [Eintrag:] Trockenform II",
            "minimal_directed_renderer_sho_pcheey_de": "feuchter Ansatz; [Eintrag:] Trockenform II",
            "best_aggressive_phrase_sheo_pcheey_de": "Mazerat/Feuchtzubereitung aus Trockengut, Form II",
            "best_aggressive_phrase_sho_pcheey_de": "Feuchtansatz aus Trockengut, Form II",
            "selected_construction_role": "POST_MOIST_FORM_II_RECORD_FIELD",
            "dry_source_relation": "C1_AGGRESSIVE_WORKING_RIVAL",
            "result_rival": "TROCKENMASSE_OR_RESIDUE_II_AFTER_MOIST_PREPARATION",
            "boundary_rival": "SPACED_VARIANT_OF_STATE_PREPARATION_SHELL_ARCHITECTURE",
            "powder_default": "RETIRED_NO_CURRENT_EVIDENCE__MAY_RETURN_ONLY_AS_INDEPENDENT_WHOLE_RIVAL",
        },
        "ckhy_result": {
            "reader_exact_occurrences": 25, "direct_dry_edges": 1, "direct_moist_edges": 2,
            "radius2_dry_relays": 1, "radius2_moist_relays": 3,
            "decision": summary_map["ckhy"]["decision"],
            "portable_working_candidate_de": summary_map["ckhy"]["revised_working_candidate_de"],
        },
        "ol_result": {
            "reader_exact_occurrences": 376, "direct_dry_edges": 58, "direct_moist_edges": 34,
            "radius2_dry_relays": 37, "radius2_moist_relays": 25,
            "normalized_direct_moist_to_dry_ratio": summary_map["ol"]["moist_to_dry_normalized_rate_ratio"],
            "decision": summary_map["ol"]["decision"],
            "quantity_expression_positions": 16,
            "quantity_expression_directed_edges": 17,
            "exact_amount_content_phrase_licenses": 8,
            "portable_working_candidate_de": summary_map["ol"]["revised_working_candidate_de"],
            "repeated_example": "ol s aiin = Ansatzstoff: drei Drachmen",
            "oil_rival": "LIVE_C0_WHOLE_RIVAL_UNSELECTED_NOT_FALSIFIED_BY_DRY_CONTACTS",
        },
        "medium_result": {
            "specific_medium_selected": 0, "water": "NOT_IDENTIFIED",
            "wine": "NOT_IDENTIFIED", "oil": "NOT_IDENTIFIED_LIVE_C0_RIVAL_FOR_OL",
            "strongest_new_relation": "PCHEEY_POST_MOIST_FORM_II_RECORD_FIELD",
        },
        "guard": {"inherited_token_query": inherited_guard},
        "neighbor_slot_status": {
            "direct": compact_counts(
                str(row[f"{key}_status"])
                for row in occurrences for key in ("l1", "r1")
            ),
            "radius2_only": compact_counts(
                str(row[f"{key}_status"])
                for row in occurrences for key in ("l2", "r2")
            ),
            "direct_clean_exact_including_candidate_targets": 585,
            "direct_score_eligible_excluding_candidate_targets": 571,
            "radius2_clean_exact_including_candidate_targets": 490,
            "radius2_score_eligible_excluding_candidate_targets": 474,
            "candidate_target_edges_direct_all_ol_to_ol": 14,
            "candidate_target_edges_radius2_all_ol_to_ol": 16,
        },
        "semantic_quarantine": quarantine,
        "claim_boundary": {
            "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
            "confirmed_solvents": 0, "confirmed_material_identities": 0,
            "component_values": 0, "new_pages": 0, "new_images": 0,
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
