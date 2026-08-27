#!/usr/bin/env python3
"""Build bounded old boundary/family bridges for five interface rests."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt552_interface_boundary_family_bridges"
ART = EXP / "artifacts"

G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G444 = ROOT / "experiments/yolo/gdt444_focus_separated_action_pair_atlas/artifacts"
G526 = ROOT / "experiments/yolo/gdt526_cha_intermediate_stem_extension/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G549 = ROOT / "experiments/yolo/gdt549_default_queue_visible_peer_bridges/artifacts"
G551 = ROOT / "experiments/yolo/gdt551_context_contract_normalization/artifacts"

OLD_IN = G407 / "gdt407_4576_running_event_edition.tsv"
FOCUS_IN = G444 / "gdt444_28_observed_separated_pair_occurrences.tsv"
CHA_IN = G526 / "gdt526_cha_route_atlas.tsv"
CURRENT_IN = G539 / "gdt539_546_contextual_prose_events.tsv"
VISIBLE_IN = G549 / "gdt549_23_exact_visible_default_cards.tsv"
RESIDUAL_IN = G551 / "gdt551_5_residual_interface_queue.tsv"

CENSUS_OUT = ART / "gdt552_5_interface_pair_census.tsv"
GAP_OUT = ART / "gdt552_11_old_one_gap_witnesses.tsv"
BOUNDARY_OUT = ART / "gdt552_76_old_card_boundary_witnesses.tsv"
CURRENT_OUT = ART / "gdt552_10_current_reinforcement_witnesses.tsv"
BRIDGE_OUT = ART / "gdt552_5_selected_interface_bridges.tsv"
QUEUE_OUT = ART / "gdt552_support_queue_status.tsv"
SUMMARY_OUT = ART / "gdt552_interface_bridge_summary.tsv"
BOOK_OUT = ART / "GDT552_INTERFACE_BRIDGE_BOOK.md"
RESULT_OUT = ART / "gdt552_result.json"

STATUS = "PASS_FIVE_BOUNDED_INTERFACE_BRIDGES__ZERO_SUPPORT_RESTS"

TARGET_META = {
    "aiicthy": {
        "left": "AIIN",
        "right": "CH",
        "visible_left": "aii",
        "visible_right": "ch",
        "bridge_class": "EXACT_TARGET_TILES_AT_OLD_CARD_BOUNDARY",
    },
    "chap": {
        "left": "A_ADDR",
        "right": "P",
        "visible_left": "a",
        "visible_right": "p",
        "bridge_class": "LEARNED_CHA_SUFFIX_PLUS_TWO_ONE_GAP_CARRIERS",
    },
    "ofaram": {
        "left": "AR",
        "right": "AM_ADDR",
        "visible_left": "ar",
        "visible_right": "am",
        "bridge_class": "VISIBLE_OLD_CARD_BOUNDARY_PLUS_ONE_GAP_CARRIER",
    },
    "rotaiin": {
        "left": "R",
        "right": "OT",
        "visible_left": "r",
        "visible_right": "ot",
        "bridge_class": "VISIBLE_OLD_CARD_BOUNDARY_PLUS_ONE_GAP_CARRIER",
    },
    "shso": {
        "left": "SH",
        "right": "S",
        "visible_left": "sh",
        "visible_right": "s",
        "bridge_class": "VISIBLE_OLD_CARD_BOUNDARY_PLUS_RECURRENT_SEPARATED_CHAIN",
    },
}
TARGET_ORDER = list(TARGET_META)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result = {row[field]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"Duplicate {field}")
    return result


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(part for part in recipe.split("+") if part)


def join(values: Iterable[str]) -> str:
    material = sorted({str(value) for value in values if str(value) and str(value) != "NONE"})
    return "|".join(material) if material else "NONE"


def count_direct(
    rows: list[dict[str, str]], recipe_field: str, excluded: set[str]
) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["surface"] in excluded:
            continue
        recipe = atoms(row[recipe_field])
        pairs = set(zip(recipe, recipe[1:]))
        for surface, meta in TARGET_META.items():
            if (meta["left"], meta["right"]) in pairs:
                result[surface].append(row)
    return result


def one_gap_witnesses(
    rows: list[dict[str, str]],
    *,
    recipe_field: str,
    event_field: str,
    statement_field: str,
    source: str,
    excluded: set[str],
) -> list[dict[str, object]]:
    material: list[dict[str, object]] = []
    for row in rows:
        if row["surface"] in excluded:
            continue
        recipe = atoms(row[recipe_field])
        for surface, meta in TARGET_META.items():
            for start in range(len(recipe) - 2):
                if recipe[start] != meta["left"] or recipe[start + 2] != meta["right"]:
                    continue
                material.append(
                    {
                        "target_surface": surface,
                        "ordered_pair": f"{meta['left']}>{meta['right']}",
                        "source_deck": source,
                        "event_id": row[event_field],
                        "physical_page": row["physical_page"],
                        "register": row["register"],
                        "statement_id": row[statement_field],
                        "surface": row["surface"],
                        "full_recipe": row[recipe_field],
                        "pair_start_atom_ordinal": start + 1,
                        "separator_atom": recipe[start + 1],
                        "observed_sequence": "+".join(recipe[start : start + 3]),
                        "gdt444_observed_focus_witness": "PENDING",
                        "guard": "EXACT_ORDERED_ROOTS_WITH_ONE_VISIBLE_RECIPE_ATOM_BETWEEN",
                    }
                )
    return material


def card_boundary_witnesses(
    rows: list[dict[str, str]],
    *,
    recipe_field: str,
    event_field: str,
    statement_field: str,
    order_field: str,
    source: str,
    excluded: set[str],
) -> list[dict[str, object]]:
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_statement[row[statement_field]].append(row)
    material: list[dict[str, object]] = []
    for statement_id, events in by_statement.items():
        ordered = sorted(events, key=lambda row: int(row[order_field]))
        for left_event, right_event in zip(ordered, ordered[1:]):
            if left_event["surface"] in excluded or right_event["surface"] in excluded:
                continue
            left_recipe = atoms(left_event[recipe_field])
            right_recipe = atoms(right_event[recipe_field])
            for surface, meta in TARGET_META.items():
                if left_recipe[-1] != meta["left"] or right_recipe[0] != meta["right"]:
                    continue
                visible_exact = left_event["surface"].endswith(meta["visible_left"]) and right_event[
                    "surface"
                ].startswith(meta["visible_right"])
                exact_target_tiles = (
                    surface == "aiicthy"
                    and left_event[recipe_field] == "AIIN"
                    and right_event[recipe_field] == "CH+T+Y"
                )
                material.append(
                    {
                        "target_surface": surface,
                        "ordered_pair": f"{meta['left']}>{meta['right']}",
                        "source_deck": source,
                        "statement_id": statement_id,
                        "physical_page": left_event["physical_page"],
                        "register": left_event["register"],
                        "left_event_id": left_event[event_field],
                        "right_event_id": right_event[event_field],
                        "left_surface": left_event["surface"],
                        "right_surface": right_event["surface"],
                        "left_recipe": left_event[recipe_field],
                        "right_recipe": right_event[recipe_field],
                        "visible_left_seam": meta["visible_left"],
                        "visible_right_seam": meta["visible_right"],
                        "visible_target_seam_exact": "YES" if visible_exact else "NO",
                        "exact_aiicthy_target_tile_path": "YES" if exact_target_tiles else "NO",
                        "guard": "CONSECUTIVE_CARDS_SAME_STATEMENT__LAST_TO_FIRST_ROOT_BOUNDARY",
                    }
                )
    return material


def build_book(
    census: list[dict[str, object]],
    bridges: list[dict[str, object]],
    metrics: dict[str, object],
) -> str:
    lines = [
        "# GDT552 interface bridge book",
        "",
        "## Ergebnis",
        "",
        "Keines der fünf Paare besitzt im alten 26-Seiten-Deck eine direkte "
        "Binnenkarten-Nachbarschaft. Trotzdem ist keines strukturell isoliert: zusammen "
        f"stehen {metrics['old_statement_boundary_witness_count']} exakte alte "
        "Satzkartengrenzen und "
        f"{metrics['old_one_gap_witness_count']} alte Ein-Zwischenstück-Ketten bereit. "
        "Die Brücken stützen nur die fünf bereits beobachteten Karten; die direkten "
        "Paare werden nicht zu einem freien Wörterbuchgesetz.",
        "",
        "## Fünferzensus",
        "",
        "| Karte | Paar | alt direkt | alt +1 | alte Kartengrenze | sichtbare Grenze |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in census:
        lines.append(
            f"| `{row['surface']}` | `{row['ordered_pair']}` | "
            f"{row['old_direct_event_count']} | {row['old_one_gap_witness_count']} | "
            f"{row['old_card_boundary_witness_count']} | "
            f"{row['old_visible_seam_boundary_count']} |"
        )
    lines.extend(["", "## Ausgewählte Brücken", ""])
    explanations = {
        "aiicthy": (
            "70 alte `AIIN|CH`-Kartengrenzen; darunter einmal die exakten "
            "Zielteile `AIIN` gefolgt von `CH+T+Y`."
        ),
        "chap": (
            "Zwei alte `A_ADDR+LOCAL_CHAR_I+P`-Ketten plus die bereits "
            "eingefrorene GDT526-Regel `cha=CH+A_ADDR` + `p→P` (2/2)."
        ),
        "ofaram": (
            "Vier alte `...ar|am...`-Kartengrenzen reproduzieren die sichtbare "
            "Zielnaht; `AR+O+AM_ADDR` liefert zusätzlich eine Binnenkarte."
        ),
        "rotaiin": (
            "Eine alte `...r|ot...`-Kartengrenze reproduziert die sichtbare "
            "Zielnaht; `R+OL+OT` hält dieselbe Ordnung in einer Binnenkarte."
        ),
        "shso": (
            "Eine alte `sh|s`-Kartengrenze, sieben alte `SH+X+S`-Ketten und die "
            "fünf unabhängig publizierten GDT444-Fokusketten stützen die Ordnung."
        ),
    }
    for row in bridges:
        lines.extend(
            [
                f"### `{row['surface']}` — `{row['ordered_pair']}`",
                "",
                explanations[str(row["surface"])],
                "",
                f"- sichtbar: `{row['selected_visible_trace']}`",
                f"- Rezept: `{row['final_recipe']}`",
                f"- neutral: {row['neutral_component_reading_de']}",
                f"- bekannter Satz: {row['known_contextual_readings_de']}",
                f"- Brückenklasse: `{row['bridge_class']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Grenze",
            "",
            "Die aktive Verbesserungswarteschlange ist damit leer, nicht das Manuskript "
            "übersetzt. Jede Zielkarte bleibt ein exakter Arbeitsleser-Schlüssel. Keine "
            "Brücke erzeugt neue Oberflächen oder bestätigt historische Lexeme.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    old_rows = read_tsv(OLD_IN)
    focus_rows = read_tsv(FOCUS_IN)
    cha_rows = read_tsv(CHA_IN)
    current_rows = read_tsv(CURRENT_IN)
    visible = keyed(read_tsv(VISIBLE_IN), "surface")
    residual = read_tsv(RESIDUAL_IN)
    if (len(old_rows), len(focus_rows), len(current_rows), len(visible), len(residual)) != (
        4576,
        28,
        546,
        23,
        5,
    ):
        raise RuntimeError("Input inventory drift")
    residual_by_surface = keyed(residual, "surface")
    if set(residual_by_surface) != set(TARGET_META):
        raise RuntimeError("Five-target surface drift")
    for surface, row in residual_by_surface.items():
        meta = TARGET_META[surface]
        if row["residual_detail"] != f"{meta['left']}>{meta['right']}":
            raise RuntimeError(f"Pair drift for {surface}")

    target_surfaces = set(TARGET_META)
    old_direct = count_direct(old_rows, "component_recipe", set())
    current_direct = count_direct(current_rows, "final_context_recipe", target_surfaces)

    old_gaps = one_gap_witnesses(
        old_rows,
        recipe_field="component_recipe",
        event_field="global_running_event_id",
        statement_field="source_statement_id",
        source="GDT407_OLD26",
        excluded=set(),
    )
    current_gaps = one_gap_witnesses(
        current_rows,
        recipe_field="final_context_recipe",
        event_field="event_id",
        statement_field="statement_id",
        source="GDT539_CURRENT4_NON_TARGET",
        excluded=target_surfaces,
    )
    old_boundaries = card_boundary_witnesses(
        old_rows,
        recipe_field="component_recipe",
        event_field="global_running_event_id",
        statement_field="source_statement_id",
        order_field="source_order",
        source="GDT407_OLD26",
        excluded=set(),
    )
    current_boundaries = card_boundary_witnesses(
        current_rows,
        recipe_field="final_context_recipe",
        event_field="event_id",
        statement_field="statement_id",
        order_field="card_ordinal_in_statement",
        source="GDT539_CURRENT4_NON_TARGET",
        excluded=target_surfaces,
    )

    focus_shs = {
        row["event_id"]
        for row in focus_rows
        if row["direct_red_pair"] == "SH>S"
    }
    for row in old_gaps:
        row["gdt444_observed_focus_witness"] = (
            "YES" if row["event_id"] in focus_shs else "NO"
        )
    for row in current_gaps:
        row["gdt444_observed_focus_witness"] = "NOT_OLD_GDT444_SOURCE"

    old_gap_by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    old_boundary_by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    current_gap_by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    current_boundary_by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in old_gaps:
        old_gap_by_target[str(row["target_surface"])].append(row)
    for row in old_boundaries:
        old_boundary_by_target[str(row["target_surface"])].append(row)
    for row in current_gaps:
        current_gap_by_target[str(row["target_surface"])].append(row)
    for row in current_boundaries:
        current_boundary_by_target[str(row["target_surface"])].append(row)

    chap_routes = [
        row
        for row in cha_rows
        if row["surface"] == "chap" and row["candidate_recipe"] == "CH+A_ADDR+P"
    ]
    if len(chap_routes) != 1:
        raise RuntimeError("GDT526 chap route drift")
    chap_route = chap_routes[0]
    chap_family_ok = (
        chap_route["candidate_is_truth"] == "YES"
        and chap_route["gdt526_rank"] == "1"
        and chap_route["base_surface"] == "cha"
        and chap_route["base_recipe"] == "CH+A_ADDR"
        and chap_route["suffix"] == "p"
        and chap_route["atom_insert"] == "P"
        and chap_route["signature_support"] == "2"
        and chap_route["visible_condition_total"] == "2"
    )

    census_rows: list[dict[str, object]] = []
    bridge_rows: list[dict[str, object]] = []
    for ordinal, surface in enumerate(TARGET_ORDER, 1):
        meta = TARGET_META[surface]
        gaps = old_gap_by_target[surface]
        boundaries = old_boundary_by_target[surface]
        current_reinforcement = current_gap_by_target[surface] + current_boundary_by_target[surface]
        visible_boundaries = [
            row for row in boundaries if row["visible_target_seam_exact"] == "YES"
        ]
        tile_boundaries = [
            row
            for row in boundaries
            if row["exact_aiicthy_target_tile_path"] == "YES"
        ]
        gdt444_count = sum(
            row["gdt444_observed_focus_witness"] == "YES" for row in gaps
        )
        if surface == "aiicthy":
            qualified = len(boundaries) >= 1 and len(tile_boundaries) >= 1
            gate_trace = (
                f"old_boundaries={len(boundaries)};exact_AIIN_then_CH+T+Y="
                f"{len(tile_boundaries)}"
            )
        elif surface == "chap":
            qualified = chap_family_ok and len(gaps) >= 2
            gate_trace = (
                f"old_one_gap={len(gaps)};cha_plus_p_rank1="
                f"{'YES' if chap_family_ok else 'NO'};suffix_license=2/2"
            )
        elif surface in {"ofaram", "rotaiin"}:
            qualified = len(gaps) >= 1 and len(visible_boundaries) >= 1
            gate_trace = (
                f"old_one_gap={len(gaps)};old_boundaries={len(boundaries)};"
                f"visible_seam_boundaries={len(visible_boundaries)}"
            )
        else:
            qualified = (
                len(gaps) >= 5
                and len(visible_boundaries) >= 1
                and gdt444_count >= 5
            )
            gate_trace = (
                f"old_one_gap={len(gaps)};visible_seam_boundaries="
                f"{len(visible_boundaries)};gdt444_focus={gdt444_count}"
            )
        census_rows.append(
            {
                "pair_ordinal": ordinal,
                "surface": surface,
                "final_recipe": residual_by_surface[surface]["final_recipe"],
                "ordered_pair": f"{meta['left']}>{meta['right']}",
                "old_direct_event_count": len(old_direct[surface]),
                "old_one_gap_witness_count": len(gaps),
                "old_one_gap_page_count": len({str(row["physical_page"]) for row in gaps}),
                "old_one_gap_separators": join(str(row["separator_atom"]) for row in gaps),
                "old_card_boundary_witness_count": len(boundaries),
                "old_card_boundary_page_count": len({str(row["physical_page"]) for row in boundaries}),
                "old_card_boundary_statement_count": len({str(row["statement_id"]) for row in boundaries}),
                "old_visible_seam_boundary_count": len(visible_boundaries),
                "old_exact_target_tile_boundary_count": len(tile_boundaries),
                "current_non_target_direct_event_count": len(current_direct[surface]),
                "current_non_target_one_gap_count": len(current_gap_by_target[surface]),
                "current_non_target_card_boundary_count": len(current_boundary_by_target[surface]),
                "gdt444_focus_witness_count": gdt444_count,
                "gdt526_chap_family_license": (
                    "YES" if surface == "chap" and chap_family_ok else "NOT_APPLICABLE"
                ),
                "finite_gate_pass": "YES" if qualified else "NO",
                "gate_trace": gate_trace,
                "guard": "PAIR_SUPPORT_CENSUS__DIRECT_OLD_PAIR_REMAINS_DISTINCT",
            }
        )
        source = visible[surface]
        bridge_rows.append(
            {
                "bridge_ordinal": ordinal,
                "surface": surface,
                "final_recipe": source["final_recipe"],
                "ordered_pair": f"{meta['left']}>{meta['right']}",
                "selected_visible_trace": source["selected_visible_trace"],
                "visible_route_class": source["visible_route_class"],
                "exact_surface_reconstruction": source["exact_surface_reconstruction"],
                "exact_recipe_reconstruction": source["exact_recipe_reconstruction"],
                "bridge_class": meta["bridge_class"],
                "gate_trace": gate_trace,
                "old_one_gap_event_ids": join(str(row["event_id"]) for row in gaps),
                "old_boundary_event_pairs": join(
                    f"{row['left_event_id']}>{row['right_event_id']}" for row in boundaries
                ),
                "current_reinforcement_count": len(current_reinforcement),
                "direct_old_within_card_pair_status": "ABSENT_AND_RETAINED_AS_ABSENT",
                "neutral_component_reading_de": source["neutral_component_reading_de"],
                "known_contextual_readings_de": source["known_contextual_readings_de"],
                "promotion_status": (
                    "PROMOTED_BY_BOUNDED_ORDERED_BRIDGE__NO_UNIVERSAL_PAIR_LICENSE"
                    if qualified
                    else "REMAINS_INTERFACE_SUPPORT_REST"
                ),
                "guard": "ALREADY_OBSERVED_EXACT_CARD_ONLY__NO_NEW_SURFACE_OR_PAIR_RULE",
            }
        )

    if not all(row["finite_gate_pass"] == "YES" for row in census_rows):
        failed = [row["surface"] for row in census_rows if row["finite_gate_pass"] != "YES"]
        raise RuntimeError(f"Finite interface gates failed: {failed}")

    for ordinal, row in enumerate(old_gaps, 1):
        row = {"witness_ordinal": ordinal, **row}
        old_gaps[ordinal - 1] = row
    for ordinal, row in enumerate(old_boundaries, 1):
        row = {"witness_ordinal": ordinal, **row}
        old_boundaries[ordinal - 1] = row
    current_combined: list[dict[str, object]] = []
    for row in current_gaps:
        current_combined.append(
            {
                "target_surface": row["target_surface"],
                "ordered_pair": row["ordered_pair"],
                "reinforcement_class": "CURRENT_NON_TARGET_ONE_GAP_CARD",
                "event_or_pair_id": row["event_id"],
                "physical_page": row["physical_page"],
                "statement_id": row["statement_id"],
                "surface_trace": row["surface"],
                "recipe_trace": row["full_recipe"],
                "guard": "CURRENT_ADMITTED_REINFORCEMENT__NOT_TARGET_SELF_SUPPORT",
            }
        )
    for row in current_boundaries:
        current_combined.append(
            {
                "target_surface": row["target_surface"],
                "ordered_pair": row["ordered_pair"],
                "reinforcement_class": "CURRENT_NON_TARGET_CARD_BOUNDARY",
                "event_or_pair_id": f"{row['left_event_id']}>{row['right_event_id']}",
                "physical_page": row["physical_page"],
                "statement_id": row["statement_id"],
                "surface_trace": f"{row['left_surface']}|{row['right_surface']}",
                "recipe_trace": f"{row['left_recipe']}|{row['right_recipe']}",
                "guard": "CURRENT_ADMITTED_REINFORCEMENT__NOT_TARGET_SELF_SUPPORT",
            }
        )
    current_combined.sort(
        key=lambda row: (
            TARGET_ORDER.index(str(row["target_surface"])),
            str(row["physical_page"]),
            str(row["event_or_pair_id"]),
        )
    )
    for ordinal, row in enumerate(current_combined, 1):
        current_combined[ordinal - 1] = {"witness_ordinal": ordinal, **row}

    promoted_count = sum(
        row["promotion_status"].startswith("PROMOTED_") for row in bridge_rows
    )
    queue_rows = [
        {
            "source_support_rest_count": len(residual),
            "promoted_interface_card_count": promoted_count,
            "residual_support_rest_count": len(residual) - promoted_count,
            "residual_surfaces": "NONE",
            "next_route": "CONSOLIDATE_ZERO_REST_145_CARD_WORKING_EDITION",
            "guard": "EMPTY_SUPPORT_QUEUE_DOES_NOT_MEAN_DECIPHERMENT",
        }
    ]
    metrics: dict[str, object] = {
        "status": STATUS,
        "source_interface_card_count": len(residual),
        "old_direct_target_pair_event_count": sum(len(old_direct[s]) for s in TARGET_ORDER),
        "old_one_gap_witness_count": len(old_gaps),
        "old_one_gap_supported_target_count": sum(bool(old_gap_by_target[s]) for s in TARGET_ORDER),
        "old_statement_boundary_witness_count": len(old_boundaries),
        "old_statement_boundary_supported_target_count": sum(bool(old_boundary_by_target[s]) for s in TARGET_ORDER),
        "old_visible_target_seam_boundary_count": sum(row["visible_target_seam_exact"] == "YES" for row in old_boundaries),
        "old_exact_aiicthy_tile_path_count": sum(row["exact_aiicthy_target_tile_path"] == "YES" for row in old_boundaries),
        "gdt444_shs_focus_witness_count": len(focus_shs),
        "gdt526_chap_family_license_count": int(chap_family_ok),
        "current_non_target_reinforcement_count": len(current_combined),
        "finite_gate_pass_count": sum(row["finite_gate_pass"] == "YES" for row in census_rows),
        "selected_bridge_class_count": len({row["bridge_class"] for row in bridge_rows}),
        "promoted_interface_card_count": promoted_count,
        "promoted_exact_visible_route_count": sum(
            row["exact_surface_reconstruction"] == "YES"
            and row["exact_recipe_reconstruction"] == "YES"
            for row in bridge_rows
        ),
        "promoted_complete_neutral_meaning_count": sum(bool(row["neutral_component_reading_de"]) for row in bridge_rows),
        "promoted_complete_context_meaning_count": sum(bool(row["known_contextual_readings_de"]) for row in bridge_rows),
        "residual_support_rest_count": len(residual) - promoted_count,
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }

    write_tsv(CENSUS_OUT, census_rows)
    write_tsv(GAP_OUT, old_gaps)
    write_tsv(BOUNDARY_OUT, old_boundaries)
    write_tsv(CURRENT_OUT, current_combined)
    write_tsv(BRIDGE_OUT, bridge_rows)
    write_tsv(QUEUE_OUT, queue_rows)
    write_tsv(
        SUMMARY_OUT,
        [
            {"metric": key, "value": str(value), "guard": "GDT552_REPLAYED_METRIC"}
            for key, value in metrics.items()
        ],
    )
    BOOK_OUT.write_text(build_book(census_rows, bridge_rows, metrics), encoding="utf-8")
    RESULT_OUT.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
