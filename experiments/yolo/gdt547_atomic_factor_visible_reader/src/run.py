#!/usr/bin/env python3
"""Build exact visible routes for the final 24 atom/factor-only cards."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt547_atomic_factor_visible_reader"
OUT = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G516 = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
G517 = ROOT / "experiments/yolo/gdt517_thirty_page_surface_recipe_intake_compiler/artifacts"
G519 = ROOT / "experiments/yolo/gdt519_visible_stem_anchor_transducer/artifacts"
G535 = ROOT / "experiments/yolo/gdt535_same_statement_q_null_qef_closure/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G540 = ROOT / "experiments/yolo/gdt540_target_surface_context_requirement_contract/artifacts"
G542 = ROOT / "experiments/yolo/gdt542_full_old_tile_context_bridge/artifacts"

TIER_IN = G542 / "gdt542_145_final_support_tiers.tsv"
ALIAS_IN = G519 / "gdt519_anchor_alias_lexicon.tsv"
CURRENT_MAP_IN = G517 / "gdt517_current30_chunk_mapping_lexicon.tsv"
OLD_EVENTS_IN = G407 / "gdt407_4576_running_event_edition.tsv"
CURRENT_EVENTS_IN = G539 / "gdt539_546_contextual_prose_events.tsv"
CONTEXT_IN = G540 / "gdt540_145_surface_context_contract.tsv"
FAMILY_IN = G516 / "gdt516_159_new_surface_family_atlas.tsv"
QEF_CERT_IN = G535 / "gdt535_qef_resolution_certificate.tsv"
G446_SOURCE = (
    ROOT
    / "experiments/yolo/gdt446_identity_execution_intake_split/src"
    / "intake_certificate_v2.py"
)

CARD_OUT = OUT / "gdt547_24_atomic_factor_reader_cards.tsv"
COVER_OUT = OUT / "gdt547_44_old26_exact_cover_paths.tsv"
SEAM_OUT = OUT / "gdt547_52_atomic_pair_interfaces.tsv"
SPECIAL_OUT = OUT / "gdt547_3_special_visible_routes.tsv"
AIIS_OUT = OUT / "gdt547_4_aiis_prefix_conditioning_cards.tsv"
SUMMARY_OUT = OUT / "gdt547_atomic_factor_reader_summary.tsv"
BOOK_OUT = OUT / "GDT547_24_ATOMIC_FACTOR_READER.md"
RESULT_OUT = OUT / "gdt547_result.json"

STATUS = "PASS_24_ATOM_FACTOR_CARDS_VISIBLE__21_OLD_DECK_COVERS__3_SPECIAL_ROUTES"
NONE = "NONE"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def key_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result = {row[field]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"Duplicate {field}")
    return result


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G446 = load_module("gdt446_certificate_for_gdt547", G446_SOURCE)


@dataclass(frozen=True)
class Segment:
    alias: str
    atom_sequence: tuple[str, ...]
    canonical_anchor: str
    source: str
    support: int
    share: float
    penalty: float

    @property
    def canonical(self) -> bool:
        return (
            self.alias == self.canonical_anchor
            and self.source in {"CANONICAL_AND_LEARNED", "CANONICAL_STEM"}
        )

    @property
    def recipe(self) -> str:
        return "+".join(self.atom_sequence)


def enumerate_exact_covers(
    surface: str,
    recipe: tuple[str, ...],
    options: dict[tuple[str, ...], list[Segment]],
) -> list[tuple[Segment, ...]]:
    states: dict[tuple[int, int], list[tuple[Segment, ...]]] = {(0, 0): [tuple()]}
    for atom_index in range(len(recipe) + 1):
        for char_index in range(len(surface) + 1):
            paths = states.get((atom_index, char_index), [])
            if not paths:
                continue
            for width in range(1, 4):
                sequence = recipe[atom_index : atom_index + width]
                if len(sequence) != width:
                    continue
                for segment in options.get(sequence, []):
                    if not surface.startswith(segment.alias, char_index):
                        continue
                    destination = (atom_index + width, char_index + len(segment.alias))
                    states.setdefault(destination, []).extend(path + (segment,) for path in paths)
    paths = states.get((len(recipe), len(surface)), [])
    unique = {tuple((part.alias, part.atom_sequence) for part in path): path for path in paths}
    return sorted(
        unique.values(),
        key=lambda path: (
            sum(not part.canonical for part in path),
            sum(part.penalty for part in path),
            -len(path),
            tuple((part.alias, part.recipe) for part in path),
        ),
    )


def segment_trace(path: tuple[Segment, ...]) -> str:
    return " | ".join(f"{part.alias}→{part.recipe}" for part in path)


def evidence_trace(path: tuple[Segment, ...]) -> str:
    return " | ".join(
        f"{part.alias}:{part.source}:n{part.support}:share{part.share:.6f}"
        for part in path
    )


def one_value(value: str, label: str) -> str:
    if value == NONE:
        return NONE
    parts = value.split("|")
    if len(parts) != 1:
        raise RuntimeError(f"Expected one observed {label}, got {value}")
    return parts[0]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tiers = [
        row
        for row in read_tsv(TIER_IN)
        if row["final_support_tier"] == "ATOMS_AND_FACTORS_ONLY"
    ]
    aliases = [row for row in read_tsv(ALIAS_IN) if row["model"] == "FULL_OLD26"]
    current_map = read_tsv(CURRENT_MAP_IN)
    old_events = read_tsv(OLD_EVENTS_IN)
    current_events = read_tsv(CURRENT_EVENTS_IN)
    contexts = key_by(read_tsv(CONTEXT_IN), "surface")
    families = key_by(read_tsv(FAMILY_IN), "surface")
    qef_cert = read_tsv(QEF_CERT_IN)
    if len(tiers) != 24:
        raise RuntimeError(f"Expected 24 atom/factor cards, got {len(tiers)}")

    options: dict[tuple[str, ...], list[Segment]] = defaultdict(list)
    for row in aliases:
        sequence = tuple(row["atom_sequence"].split("+"))
        options[sequence].append(
            Segment(
                alias=row["surface_alias"],
                atom_sequence=sequence,
                canonical_anchor=row["canonical_anchor"],
                source=row["alias_source"],
                support=int(row["support"]),
                share=float(row["support_share"]),
                penalty=float(row["alias_penalty"]),
            )
        )

    selected_cover: dict[str, tuple[Segment, ...]] = {}
    cover_rows: list[dict[str, object]] = []
    cover_count_by_surface: Counter[str] = Counter()
    for tier in sorted(tiers, key=lambda row: int(row["target_ordinal"])):
        surface = tier["surface"]
        recipe = tuple(tier["final_recipe"].split("+"))
        covers = enumerate_exact_covers(surface, recipe, options)
        cover_count_by_surface[surface] = len(covers)
        if covers:
            selected_cover[surface] = covers[0]
        for rank, path in enumerate(covers, 1):
            cover_rows.append(
                {
                    "target_ordinal": tier["target_ordinal"],
                    "surface": surface,
                    "final_recipe": tier["final_recipe"],
                    "cover_rank": rank,
                    "selected_cover": "YES" if rank == 1 else "NO",
                    "segment_count": len(path),
                    "canonical_segment_count": sum(part.canonical for part in path),
                    "learned_segment_count": sum(not part.canonical for part in path),
                    "alias_penalty_total": f"{sum(part.penalty for part in path):.9f}",
                    "visible_trace": segment_trace(path),
                    "evidence_trace": evidence_trace(path),
                    "guard": "EXACT_MONOTONE_FULL_SURFACE_COVER__OLD26_ALIAS_DECK_ONLY",
                }
            )

    expected_old_missing = {"chedaiir", "faiis", "qef"}
    if set(row["surface"] for row in tiers) - set(selected_cover) != expected_old_missing:
        raise RuntimeError("Unexpected old-deck visible-cover inventory")

    aiir_rows = [
        row
        for row in current_map
        if row["surface_chunk"] == "aiir" and row["recipe"] == "IIN+R"
    ]
    if len(aiir_rows) != 1:
        raise RuntimeError("Missing unique aiir→IIN+R mapping")
    aiir = aiir_rows[0]
    if (aiir["support"], aiir["total_surface_support"], aiir["high_confidence_top_mapping"]) != (
        "17",
        "20",
        "YES",
    ):
        raise RuntimeError("aiir channel drift")

    old_event_by_surface = {row["surface"]: row for row in old_events}
    current_event_by_surface = {row["surface"]: row for row in current_events}
    aiis_specs = [
        ("OLD26", "qoaiis", "CARRIER_Q+O+IIN+S", "qo", "", "IIN+S", "QO_PREFIX"),
        ("CURRENT4", "faiis", "LOCAL_CHAR_F+IIN+S", "f", "", "IIN+S", "F_PREFIX"),
        ("OLD26", "saiisol", "S+A_ADDR+IIN+S+OL", "s", "ol", "A_ADDR+IIN+S", "S_PREFIX"),
        ("CURRENT4", "saiis", "S+A_ADDR+IIN+S", "s", "", "A_ADDR+IIN+S", "S_PREFIX"),
    ]
    aiis_rows: list[dict[str, object]] = []
    for source, surface, expected_recipe, prefix, suffix, channel, prefix_class in aiis_specs:
        event = old_event_by_surface[surface] if source == "OLD26" else current_event_by_surface[surface]
        recipe_field = "component_recipe" if source == "OLD26" else "final_context_recipe"
        if event[recipe_field] != expected_recipe or surface != prefix + "aiis" + suffix:
            raise RuntimeError(f"aiis conditioning drift at {surface}")
        aiis_rows.append(
            {
                "source_deck": source,
                "surface": surface,
                "full_recipe": expected_recipe,
                "visible_prefix": prefix,
                "visible_suffix": suffix or NONE,
                "aiis_channel_recipe": channel,
                "prefix_class": prefix_class,
                "channel_class": (
                    "IIN_PLUS_S_AFTER_F_OR_QO"
                    if channel == "IIN+S"
                    else "A_ADDR_PLUS_IIN_PLUS_S_AFTER_S"
                ),
                "guard": "PREFIX_CONDITIONED_AIIS_CHANNEL__NOT_GLOBAL_AIIS_VALUE",
            }
        )
    if Counter(row["aiis_channel_recipe"] for row in aiis_rows) != Counter(
        {"IIN+S": 2, "A_ADDR+IIN+S": 2}
    ):
        raise RuntimeError("aiis prefix split drift")

    qef_evidence = {row["evidence_layer"]: row for row in qef_cert}
    if (
        qef_evidence["CURRENT_SAME_STATEMENT_NEIGHBOURS"]["support"],
        qef_evidence["CURRENT_SAME_STATEMENT_NEIGHBOURS"]["total"],
        qef_evidence["CURRENT_SAME_STATEMENT_NEIGHBOURS"]["value"],
    ) != ("6", "6", "NONCARRIER_Q"):
        raise RuntimeError("qef local q-null evidence drift")

    special_rows = [
        {
            "target_ordinal": "11",
            "surface": "chedaiir",
            "final_recipe": "CHD+IIN+R",
            "route_class": "CURRENT30_DOMINANT_SHORT_RENDERER",
            "visible_trace": "ched→CHD | aiir→IIN+R",
            "surface_reconstruction": "ched+aiir",
            "support": "aiir 17/20 (0.850000), high-confidence top mapping",
            "residual_caution": "AIIN+R remains 3/20; full known card retains final recipe",
            "guard": "CURRENT30_DOMINANT_CHANNEL__NO_GLOBAL_AIIR_WORD_VALUE",
        },
        {
            "target_ordinal": "51",
            "surface": "faiis",
            "final_recipe": "LOCAL_CHAR_F+IIN+S",
            "route_class": "PREFIX_CONDITIONED_CURRENT_AIIS_CHANNEL",
            "visible_trace": "f→LOCAL_CHAR_F | aiis→IIN+S",
            "surface_reconstruction": "f+aiis",
            "support": "F/QO prefixes select IIN+S in 2 cards; S selects A_ADDR+IIN+S in 2",
            "residual_caution": "aiis is prefix-conditioned and has no global recipe value",
            "guard": "FOUR_CARD_PREFIX_SPLIT__TARGET_CARD_RETAINED",
        },
        {
            "target_ordinal": "86",
            "surface": "qef",
            "final_recipe": "E+LOCAL_CHAR_F",
            "route_class": "GDT535_LOCAL_Q_NULL_PLUS_CANONICAL_ATOMS",
            "visible_trace": "q→NULL_Q | e→E | f→LOCAL_CHAR_F",
            "surface_reconstruction": "q+e+f",
            "support": "same-statement q vote 6/6 noncarrier; old visible q-null 75/84",
            "residual_caution": "q-null is locally selected, not a universal q deletion",
            "guard": "GDT535_LOCAL_SELECTOR__NO_GLOBAL_Q_NULL_RULE",
        },
    ]
    special_by_surface = key_by(special_rows, "surface")

    pair_events: Counter[tuple[str, str]] = Counter()
    pair_surfaces: dict[tuple[str, str], set[str]] = defaultdict(set)
    for event in old_events:
        atoms = event["component_recipe"].split("+")
        for pair in set(zip(atoms, atoms[1:])):
            pair_events[pair] += 1
            pair_surfaces[pair].add(event["surface"])
    seam_rows: list[dict[str, object]] = []
    seams_by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for tier in sorted(tiers, key=lambda row: int(row["target_ordinal"])):
        atoms = tier["final_recipe"].split("+")
        for pair_ordinal, pair in enumerate(zip(atoms, atoms[1:]), 1):
            count = pair_events[pair]
            row = {
                "target_ordinal": tier["target_ordinal"],
                "surface": tier["surface"],
                "final_recipe": tier["final_recipe"],
                "pair_ordinal": pair_ordinal,
                "ordered_pair": ">".join(pair),
                "old_event_count": count,
                "old_example_surfaces": "|".join(sorted(pair_surfaces[pair])) if count else NONE,
                "interface_status": "OLD26_DIRECT_INTERFACE" if count else "NEW_DIRECT_INTERFACE",
                "guard": "ADJACENT_ATOM_PAIR_ONLY__NOT_WHOLE_RECIPE_SUPPORT",
            }
            seam_rows.append(row)
            seams_by_surface[tier["surface"]].append(row)

    card_rows: list[dict[str, object]] = []
    for tier in sorted(tiers, key=lambda row: int(row["target_ordinal"])):
        surface = tier["surface"]
        context = contexts[surface]
        if context["final_recipe"] != tier["final_recipe"]:
            raise RuntimeError(f"Context recipe drift for {surface}")
        incoming_action = one_value(context["observed_incoming_action_roots"], "action")
        incoming_argument = one_value(context["observed_incoming_argument_roots"], "argument")
        certificate = G446.issue_split_certificate(
            tier["final_recipe"],
            incoming_action,
            incoming_argument,
            incoming_action if incoming_action != NONE else None,
        )

        if surface in selected_cover:
            path = selected_cover[surface]
            learned = sum(not part.canonical for part in path)
            route_class = (
                "OLD26_ALL_CANONICAL_VISIBLE_ATOMS"
                if not learned
                else "OLD26_MIXED_CANONICAL_AND_LEARNED_RENDERERS"
            )
            visible_trace = segment_trace(path)
            visible_evidence = evidence_trace(path)
            segment_count = len(path)
            canonical_count = len(path) - learned
            learned_count = learned
            route_caution = NONE
        else:
            special = special_by_surface[surface]
            route_class = special["route_class"]
            visible_trace = special["visible_trace"]
            visible_evidence = special["support"]
            segment_count = len(special["visible_trace"].split(" | "))
            canonical_count = 2 if surface == "qef" else 1
            learned_count = 1
            route_caution = special["residual_caution"]

        if surface in {"axor", "chxar"}:
            if families[surface]["context_policy"] != "F66R_LOCAL_X_UNIFICATION":
                raise RuntimeError(f"Missing local-X overlay for {surface}")
            current_execution = "READ_CURRENT_LOCAL_X_OVERLAY"
            execution_caution = "GDT446_PRE_LOCAL_X_DECK_STOP__GDT516_F66R_LOCAL_X_OVERLAY"
        elif surface == "shso":
            current_execution = "READ_EXPLICIT_OBSERVED_PAIR_DEFAULT"
            execution_caution = "NEW_DIRECT_ACTION_PAIR_SH>S__OBSERVED_SINGLETON"
        elif certificate["execution_decision"] == "READ_AMBER":
            current_execution = "READ_FACTOR_AMBER_LOCAL_APPENDIX"
            execution_caution = certificate["amber_factor_rules"]
        elif certificate["execution_decision"] == "READ":
            current_execution = "READ_FACTOR_GREEN"
            execution_caution = NONE
        else:
            raise RuntimeError(f"Unexpected unresolved factor stop for {surface}")

        surface_seams = seams_by_surface[surface]
        new_pairs = [row["ordered_pair"] for row in surface_seams if row["interface_status"] == "NEW_DIRECT_INTERFACE"]
        card_rows.append(
            {
                "target_ordinal": tier["target_ordinal"],
                "surface": surface,
                "reader_decision": "READ_KNOWN_ATOMIC_FACTOR_WORKING_CARD",
                "final_recipe": tier["final_recipe"],
                "atom_count": tier["final_recipe_atom_count"],
                "visible_route_class": route_class,
                "visible_trace": visible_trace,
                "visible_evidence": visible_evidence,
                "exact_surface_reconstruction": "YES",
                "renderer_segment_count": segment_count,
                "canonical_segment_count": canonical_count,
                "learned_or_special_segment_count": learned_count,
                "old26_exact_cover_path_count": cover_count_by_surface[surface],
                "direct_interface_count": len(surface_seams),
                "old26_direct_interface_count": sum(
                    row["interface_status"] == "OLD26_DIRECT_INTERFACE" for row in surface_seams
                ),
                "new_direct_interfaces": "|".join(new_pairs) if new_pairs else NONE,
                "observed_requirement_modes": context["observed_requirement_modes"],
                "observed_incoming_action_roots": context["observed_incoming_action_roots"],
                "observed_incoming_argument_roots": context["observed_incoming_argument_roots"],
                "future_action_contract": context["future_action_contract"],
                "future_argument_contract": context["future_argument_contract"],
                "neutral_component_reading_de": context["neutral_surface_phrase_de"],
                "known_contextual_readings_de": context["known_contextual_readings_de"],
                "gdt446_identity_status": certificate["identity_status"],
                "gdt446_factor_status_in_observed_context": certificate["factor_gate_status"],
                "gdt446_execution_decision": certificate["execution_decision"],
                "gdt446_portable_factor_rules": certificate["portable_factor_rules"],
                "gdt446_amber_factor_rules": certificate["amber_factor_rules"],
                "gdt446_blocked_factor_rules": certificate["blocked_factor_rules"],
                "current_execution_route": current_execution,
                "visible_route_caution": route_caution,
                "execution_caution": execution_caution,
                "reading_scope": "GERMAN_WORKING_READING__NOT_PLAINTEXT",
                "guard": "EXACT_KNOWN_SURFACE_ONLY__NO_UNKNOWN_SURFACE_OR_NEW_MEANING",
            }
        )

    result = {
        "status": STATUS,
        "target_card_count": len(card_rows),
        "exact_surface_reconstruction_count": sum(
            row["exact_surface_reconstruction"] == "YES" for row in card_rows
        ),
        "old26_exact_cover_target_count": len(selected_cover),
        "old26_exact_cover_path_count": len(cover_rows),
        "old26_all_canonical_target_count": sum(
            row["visible_route_class"] == "OLD26_ALL_CANONICAL_VISIBLE_ATOMS"
            for row in card_rows
        ),
        "old26_mixed_learned_renderer_target_count": sum(
            row["visible_route_class"] == "OLD26_MIXED_CANONICAL_AND_LEARNED_RENDERERS"
            for row in card_rows
        ),
        "bounded_special_route_count": len(special_rows),
        "current30_dominant_aiir_route_count": 1,
        "prefix_conditioned_aiis_route_count": 1,
        "local_q_null_route_count": 1,
        "direct_interface_count": len(seam_rows),
        "old26_direct_interface_count": sum(
            row["interface_status"] == "OLD26_DIRECT_INTERFACE" for row in seam_rows
        ),
        "new_direct_interface_count": sum(
            row["interface_status"] == "NEW_DIRECT_INTERFACE" for row in seam_rows
        ),
        "target_with_new_direct_interface_count": len(
            {row["surface"] for row in seam_rows if row["interface_status"] == "NEW_DIRECT_INTERFACE"}
        ),
        "gdt446_factor_green_count": sum(
            row["gdt446_execution_decision"] == "READ" for row in card_rows
        ),
        "gdt446_factor_amber_count": sum(
            row["gdt446_execution_decision"] == "READ_AMBER" for row in card_rows
        ),
        "gdt446_factor_stop_count": sum(
            row["gdt446_execution_decision"] == "STOP" for row in card_rows
        ),
        "current_local_x_overlay_count": sum(
            row["current_execution_route"] == "READ_CURRENT_LOCAL_X_OVERLAY"
            for row in card_rows
        ),
        "current_explicit_pair_default_count": sum(
            row["current_execution_route"] == "READ_EXPLICIT_OBSERVED_PAIR_DEFAULT"
            for row in card_rows
        ),
        "current_readable_card_count": len(card_rows),
        "self_contained_card_count": sum(
            row["observed_requirement_modes"] == "SELF_CONTAINED" for row in card_rows
        ),
        "active_action_card_count": sum(
            row["observed_requirement_modes"] == "REQUIRES_ACTIVE_ACTION" for row in card_rows
        ),
        "active_argument_card_count": sum(
            row["observed_requirement_modes"] == "REQUIRES_ACTIVE_ARGUMENT" for row in card_rows
        ),
        "active_action_and_argument_card_count": sum(
            row["observed_requirement_modes"] == "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
            for row in card_rows
        ),
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    expected = {
        "target_card_count": 24,
        "exact_surface_reconstruction_count": 24,
        "old26_exact_cover_target_count": 21,
        "old26_exact_cover_path_count": 44,
        "old26_all_canonical_target_count": 16,
        "old26_mixed_learned_renderer_target_count": 5,
        "bounded_special_route_count": 3,
        "current30_dominant_aiir_route_count": 1,
        "prefix_conditioned_aiis_route_count": 1,
        "local_q_null_route_count": 1,
        "direct_interface_count": 52,
        "old26_direct_interface_count": 40,
        "new_direct_interface_count": 12,
        "target_with_new_direct_interface_count": 9,
        "gdt446_factor_green_count": 20,
        "gdt446_factor_amber_count": 1,
        "gdt446_factor_stop_count": 3,
        "current_local_x_overlay_count": 2,
        "current_explicit_pair_default_count": 1,
        "current_readable_card_count": 24,
        "self_contained_card_count": 11,
        "active_action_card_count": 1,
        "active_argument_card_count": 8,
        "active_action_and_argument_card_count": 4,
    }
    drift = {key: (result[key], value) for key, value in expected.items() if result[key] != value}
    if drift:
        raise RuntimeError(f"Atomic reader inventory drift: {drift}")

    write_tsv(CARD_OUT, card_rows)
    write_tsv(COVER_OUT, cover_rows)
    write_tsv(SEAM_OUT, seam_rows)
    write_tsv(SPECIAL_OUT, special_rows)
    write_tsv(AIIS_OUT, aiis_rows)
    write_tsv(
        SUMMARY_OUT,
        [{"metric": key, "value": value} for key, value in result.items() if key != "status"],
    )

    route_sections = []
    route_order = [
        "OLD26_ALL_CANONICAL_VISIBLE_ATOMS",
        "OLD26_MIXED_CANONICAL_AND_LEARNED_RENDERERS",
        "CURRENT30_DOMINANT_SHORT_RENDERER",
        "PREFIX_CONDITIONED_CURRENT_AIIS_CHANNEL",
        "GDT535_LOCAL_Q_NULL_PLUS_CANONICAL_ATOMS",
    ]
    for route in route_order:
        rows = [row for row in card_rows if row["visible_route_class"] == route]
        lines = [
            f"| `{row['surface']}` | `{row['visible_trace']}` | "
            f"{row['neutral_component_reading_de']} | `{row['current_execution_route']}` |"
            for row in rows
        ]
        route_sections.append(
            f"### `{route}` ({len(rows)})\n\n"
            "| Oberfläche | sichtbare Route | Arbeitslesung | Ausführung |\n"
            "| --- | --- | --- | --- |\n"
            + "\n".join(lines)
        )
    new_seam_cards = ", ".join(
        f"`{surface}`"
        for surface in sorted(
            {row["surface"] for row in seam_rows if row["interface_status"] == "NEW_DIRECT_INTERFACE"},
            key=lambda value: int(next(card["target_ordinal"] for card in card_rows if card["surface"] == value)),
        )
    )
    BOOK_OUT.write_text(
        f"""# GDT547 — 24 atomare und faktorielle Restkarten

Status: `{STATUS}`

Alle24 Oberflächen besitzen jetzt eine vollständige sichtbare Route und eine
vollständige deutsche Arbeitslesung.21 werden vom alten GDT519-Renderer-Deck
buchstabengetreu abgedeckt:16 rein kanonisch, fünf mit mindestens einem alten
gelernten Kurzrenderer. Die drei übrigen benutzen je einen bereits begrenzten
Mechanismus (`aiir`, präfixbedingtes `aiis`, lokales q-null).

{chr(10).join(route_sections)}

## Offene Nähte

Von52 direkten Atompaaren kommen40 schon innerhalb alter vollständiger Karten
vor. Zwölf Nähte auf neun Karten sind neu: {new_seam_cards}. Das nimmt den
Karten nicht ihre Defaultbedeutung. Es sagt nur, an welcher Stelle der heutige
Reader auf Faktor-/Kontextlogik oder eine beobachtete Einzelkarte statt auf
eine alte direkte Naht angewiesen ist.

Der ältere GDT446-Faktorleser gibt im beobachteten Kontext20 grüne, eine
gelbe und drei Stopentscheidungen. Zwei Stopps (`axor`, `chxar`) entstehen nur,
weil sein eingefrorenes Deck dem späteren f66r-`LOCAL_X`-Overlay vorausgeht.
Der verbleibende Stopp `shso` ist der ehrliche Einzeldefault für das neue
Direktpaar `SH>S`. `shtchy` bleibt wegen des lokalen `SH>T`-Paares gelb.

Keine Oberfläche bleibt bedeutungslos, aber diese Unterschiede bleiben in
jeder Karte sichtbar.
""",
        encoding="utf-8",
    )
    RESULT_OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
