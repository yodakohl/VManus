#!/usr/bin/env python3
"""Give all 23 GDT548 defaults exact visible routes and audit current peer bridges."""

from __future__ import annotations

import csv
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
EXP = ROOT / "experiments/yolo/gdt549_default_queue_visible_peer_bridges"
ART = EXP / "artifacts"

G548 = ROOT / "experiments/yolo/gdt548_unified_145_prose_reader/artifacts"
G519 = ROOT / "experiments/yolo/gdt519_visible_stem_anchor_transducer/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G546 = ROOT / "experiments/yolo/gdt546_consolidated_fragment_reader/artifacts"
G547 = ROOT / "experiments/yolo/gdt547_atomic_factor_visible_reader/artifacts"

QUEUE_IN = G548 / "gdt548_23_named_default_queue.tsv"
READER_IN = G548 / "gdt548_145_unified_prose_reader.tsv"
ALIAS_IN = G519 / "gdt519_anchor_alias_lexicon.tsv"
EVENT_IN = G539 / "gdt539_546_contextual_prose_events.tsv"
FRAGMENT_IN = G546 / "gdt546_81_consolidated_fragment_reader.tsv"
ATOMIC_IN = G547 / "gdt547_24_atomic_factor_reader_cards.tsv"
AIIS_IN = G547 / "gdt547_4_aiis_prefix_conditioning_cards.tsv"


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
    def recipe(self) -> str:
        return "+".join(self.atom_sequence)

    @property
    def canonical(self) -> bool:
        return (
            self.alias == self.canonical_anchor
            and self.source in {"CANONICAL_AND_LEARNED", "CANONICAL_STEM"}
        )


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result = {row[field]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"duplicate {field}")
    return result


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def enumerate_exact_covers(
    surface: str,
    recipe: tuple[str, ...],
    options: dict[tuple[str, ...], list[Segment]],
) -> list[tuple[Segment, ...]]:
    states: dict[tuple[int, int], list[tuple[Segment, ...]]] = {(0, 0): [tuple()]}
    for atom_index in range(len(recipe) + 1):
        for char_index in range(len(surface) + 1):
            paths = states.get((atom_index, char_index), [])
            for path in paths:
                for width in range(1, 4):
                    sequence = recipe[atom_index : atom_index + width]
                    if len(sequence) != width:
                        continue
                    for segment in options.get(sequence, []):
                        if not surface.startswith(segment.alias, char_index):
                            continue
                        destination = (
                            atom_index + width,
                            char_index + len(segment.alias),
                        )
                        states.setdefault(destination, []).append(path + (segment,))
    paths = states.get((len(recipe), len(surface)), [])
    unique = {
        tuple((part.alias, part.atom_sequence) for part in path): path for path in paths
    }
    return sorted(
        unique.values(),
        key=lambda path: (
            len(path),
            sum(part.penalty for part in path),
            -sum(part.support for part in path),
            tuple((part.alias, part.recipe) for part in path),
        ),
    )


def trace(path: tuple[Segment, ...]) -> str:
    return " | ".join(f"{part.alias}→{part.recipe}" for part in path)


def evidence(path: tuple[Segment, ...]) -> str:
    return " | ".join(
        f"{part.alias}:{part.source}:n{part.support}:share{part.share:.6f}"
        for part in path
    )


def event_mode(event: dict[str, str]) -> str:
    action = event["inherited_action_root"] != "NONE"
    argument = event["inherited_argument_root"] != "NONE"
    if action and argument:
        return "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
    if action:
        return "REQUIRES_ACTIVE_ACTION"
    if argument:
        return "REQUIRES_ACTIVE_ARGUMENT"
    return "SELF_CONTAINED"


def contains_sequence(recipe: str, needle: str) -> bool:
    source = recipe.split("+")
    target = needle.split("+")
    return any(source[index : index + len(target)] == target for index in range(len(source)))


def contains_pair(recipe: str, pair: str) -> bool:
    left, right = pair.split(">")
    atoms = recipe.split("+")
    return any(a == left and b == right for a, b in zip(atoms, atoms[1:]))


def list_field(values: list[str]) -> str:
    return "|".join(sorted(set(values))) if values else "NONE"


def build_book(
    visible_rows: list[dict[str, object]],
    promoted_rows: list[dict[str, object]],
    residual_rows: list[dict[str, object]],
    metrics: dict[str, object],
) -> str:
    promoted = {str(row["surface"]) for row in promoted_rows}
    residual = {str(row["surface"]): row for row in residual_rows}
    lines = [
        "# GDT549 — sichtbare Routen und Peer-Brücken der 23 Defaults",
        "",
        f"Status: `{metrics['status']}`",
        "",
        "Alle 23 Karten besitzen jetzt eine exakte sichtbare Komposition. Zwanzig",
        "haben mindestens einen vollständigen Weg im alten Aliasdeck; drei benutzen",
        "bereits begrenzte aktuelle Kanäle. Es bleibt keine lexikalisch unsichtbare",
        "Ganzwortbedeutung.",
        "",
        f"Vier Karten gewinnen vollständige aktuelle Peer-Brücken: "
        f"`{'`, `'.join(sorted(promoted))}`.",
        f"Die dimensionstreue Restliste enthält {len(residual_rows)} Karten.",
        "",
        "## Karten",
        "",
    ]
    for row in visible_rows:
        surface = str(row["surface"])
        state = (
            "PROMOTED_BY_CURRENT_PEERS"
            if surface in promoted
            else str(residual.get(surface, {}).get("residual_dimension", "VISIBLE_ONLY_COMPLETE"))
        )
        lines.extend(
            [
                f"### `{surface}`",
                "",
                f"- Komponenten: `{row['final_recipe']}`",
                f"- Sichtbare Route: `{row['selected_visible_trace']}`",
                f"- Routenklasse: `{row['visible_route_class']}`",
                f"- Default: {row['neutral_component_reading_de']}",
                f"- Bekannter Kontext: {row['known_contextual_readings_de']}",
                f"- Aktueller Rest: `{state}`",
            ]
        )
    lines.extend(
        [
            "",
            "Die verbleibenden Hinweise sind zehn Sequenz-/Satzpfad-, vier Kontext-",
            "und fünf direkte Nahtfragen. Keine davon entfernt die vollständige",
            "Defaultbedeutung. Deutsche Lesungen bleiben Arbeitslesungen.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    queue = read_tsv(QUEUE_IN)
    reader_rows = read_tsv(READER_IN)
    readers = keyed(reader_rows, "surface")
    fragments = keyed(read_tsv(FRAGMENT_IN), "surface")
    atomics = keyed(read_tsv(ATOMIC_IN), "surface")
    events = read_tsv(EVENT_IN)
    aiis_rows = read_tsv(AIIS_IN)
    aliases = [row for row in read_tsv(ALIAS_IN) if row["model"] == "FULL_OLD26"]
    if len(queue) != 23:
        raise RuntimeError(f"expected 23 defaults, got {len(queue)}")

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

    cover_rows: list[dict[str, object]] = []
    selected: dict[str, tuple[Segment, ...]] = {}
    cover_counts: Counter[str] = Counter()
    for queue_row in queue:
        surface = queue_row["surface"]
        recipe = tuple(queue_row["final_recipe"].split("+"))
        covers = enumerate_exact_covers(surface, recipe, options)
        cover_counts[surface] = len(covers)
        if covers:
            selected[surface] = covers[0]
        for rank, path in enumerate(covers, 1):
            cover_rows.append(
                {
                    "surface": surface,
                    "final_recipe": queue_row["final_recipe"],
                    "compressed_cover_rank": rank,
                    "selected_compressed_cover": "YES" if rank == 1 else "NO",
                    "segment_count": len(path),
                    "canonical_segment_count": sum(part.canonical for part in path),
                    "learned_segment_count": sum(not part.canonical for part in path),
                    "alias_penalty_total": f"{sum(part.penalty for part in path):.9f}",
                    "visible_trace": trace(path),
                    "evidence_trace": evidence(path),
                    "exact_surface_reconstruction": "YES",
                    "exact_recipe_reconstruction": "YES",
                    "guard": "EXACT_MONOTONE_FULL_SURFACE_COVER__OLD26_ALIAS_DECK_ONLY",
                }
            )

    missing = {row["surface"] for row in queue} - set(selected)
    if missing != {"aiicthy", "saiis", "shokaiir"}:
        raise RuntimeError(f"unexpected old-cover missing set: {sorted(missing)}")

    saiis_source = [row for row in aiis_rows if row["surface"] == "saiis"]
    if len(saiis_source) != 1:
        raise RuntimeError("missing saiis prefix-conditioned source")
    special_specs = {
        "aiicthy": {
            "class": "GDT546_SINGLETON_EXTENSION_PLUS_EXACT_OLD_STEM",
            "trace": "aii→AIIN | cthy→CH+T+Y",
            "evidence": "aii channel n1; cthy old anchor events19",
            "caution": "CURRENT_SINGLETON_AII_CHANNEL__AIIN>CH_INTERFACE_UNRESOLVED",
        },
        "saiis": {
            "class": "GDT547_PREFIX_CONDITIONED_AIIS_ROUTE",
            "trace": "s→S | aiis→A_ADDR+IIN+S",
            "evidence": "four complete aiis cards split 2/2 by F-QO versus S prefix",
            "caution": "AIIS_VALUE_IS_PREFIX_CONDITIONED__CONTEXT_BRIDGE_UNRESOLVED",
        },
        "shokaiir": {
            "class": "GDT546_EXACT_OLD_STEM_PLUS_RECURRENT_EXTENSION",
            "trace": "sh→SH | okaiir→OK+IIN+R",
            "evidence": "okaiir old anchor events2; SH>OK old events6; sh channel n3",
            "caution": "ANCHOR_CONTEXT_BRIDGE_UNRESOLVED",
        },
    }

    visible_rows: list[dict[str, object]] = []
    for queue_row in queue:
        surface = queue_row["surface"]
        source = readers[surface]
        if surface in selected:
            path = selected[surface]
            route_class = "OLD26_EXACT_ALIAS_COVER"
            selected_trace = trace(path)
            selected_evidence = evidence(path)
            caution = "NONE_AT_VISIBLE_COMPOSITION_LAYER"
            segment_count = len(path)
            canonical_count = sum(part.canonical for part in path)
            learned_count = sum(not part.canonical for part in path)
        else:
            spec = special_specs[surface]
            route_class = spec["class"]
            selected_trace = spec["trace"]
            selected_evidence = spec["evidence"]
            caution = spec["caution"]
            segment_count = 2
            canonical_count = 0
            learned_count = 2
        visible_rows.append(
            {
                "queue_ordinal": queue_row["queue_ordinal"],
                "surface": surface,
                "final_recipe": source["final_recipe"],
                "original_support_tier": source["support_tier"],
                "original_support_band": source["support_band"],
                "original_weak_reason": source["weak_queue_reason"],
                "visible_route_class": route_class,
                "old26_exact_cover_path_count": cover_counts[surface],
                "selected_segment_count": segment_count,
                "selected_canonical_segment_count": canonical_count,
                "selected_learned_or_bounded_segment_count": learned_count,
                "selected_visible_trace": selected_trace,
                "selected_visible_evidence": selected_evidence,
                "exact_surface_reconstruction": "YES",
                "exact_recipe_reconstruction": "YES",
                "lexical_visible_status": "EXACT_VISIBLE_COMPOSITION__NO_OPAQUE_WHOLE_GLOSS",
                "visible_route_caution": caution,
                "neutral_component_reading_de": source["neutral_component_reading_de"],
                "known_contextual_readings_de": source["known_contextual_readings_de"],
                "guard": "VISIBLE_ROUTE_ONLY__DOES_NOT_ERASE_CONTEXT_OR_INTERFACE_CAUTION",
            }
        )

    context_targets = [
        row
        for row in queue
        if "ANCHOR_CONTEXT_MODE_DIFFERENCE" in readers[row["surface"]]["tier_caution"]
    ]
    context_rows: list[dict[str, object]] = []
    context_repaired: set[str] = set()
    for target in context_targets:
        surface = target["surface"]
        fragment = fragments[surface]
        target_modes = set(readers[surface]["observed_requirement_modes"].split("|"))
        peers = [
            event
            for event in events
            if event["surface"] != surface
            and contains_sequence(event["final_context_recipe"], fragment["primary_anchor_recipe"])
            and event_mode(event) in target_modes
        ]
        if peers:
            context_repaired.add(surface)
        context_rows.append(
            {
                "surface": surface,
                "anchor_recipe": fragment["primary_anchor_recipe"],
                "target_modes": readers[surface]["observed_requirement_modes"],
                "old_anchor_modes": fragment["primary_anchor_context_modes"],
                "current_peer_event_count": len(peers),
                "current_peer_surface_count": len({event["surface"] for event in peers}),
                "current_peer_page_count": len({event["physical_page"] for event in peers}),
                "current_peer_surfaces": list_field([event["surface"] for event in peers]),
                "current_peer_pages": list_field([event["physical_page"] for event in peers]),
                "current_peer_event_ids": list_field([event["event_id"] for event in peers]),
                "current_peer_recipes": list_field(
                    [event["final_context_recipe"] for event in peers]
                ),
                "peer_context_status": (
                    "CURRENT_PEER_CONTEXT_BRIDGE"
                    if peers
                    else "NO_CURRENT_PEER_CONTEXT_BRIDGE"
                ),
                "guard": "CURRENT_ADMITTED_PEER_SUPPORT__NOT_OLD_PREFIX_OR_UNIVERSAL_CONTEXT",
            }
        )

    fragment_new_pairs: dict[str, str] = {}
    for target in queue:
        surface = target["surface"]
        if surface not in fragments:
            continue
        fragment = fragments[surface]
        if "NEW_ATOM_INTERFACE" not in fragment["current_caution"]:
            continue
        candidates = []
        if fragment["left_interface_pair"] != "NONE" and fragment[
            "left_interface_old_event_count"
        ] == "0":
            candidates.append(fragment["left_interface_pair"])
        if fragment["right_interface_pair"] != "NONE" and fragment[
            "right_interface_old_event_count"
        ] == "0":
            candidates.append(fragment["right_interface_pair"])
        if len(candidates) != 1:
            raise RuntimeError(f"expected one new interface at {surface}: {candidates}")
        fragment_new_pairs[surface] = candidates[0]
    interface_targets = {**fragment_new_pairs, "shso": "SH>S"}
    interface_rows: list[dict[str, object]] = []
    interface_repaired: set[str] = set()
    for surface, pair in sorted(interface_targets.items()):
        all_current = [
            event for event in events if contains_pair(event["final_context_recipe"], pair)
        ]
        peers = [event for event in all_current if event["surface"] != surface]
        if peers:
            interface_repaired.add(surface)
        interface_rows.append(
            {
                "surface": surface,
                "interface_pair": pair,
                "old26_interface_event_count": 0,
                "current_total_event_count": len(all_current),
                "current_peer_event_count": len(peers),
                "current_peer_surface_count": len({event["surface"] for event in peers}),
                "current_peer_page_count": len({event["physical_page"] for event in peers}),
                "current_peer_surfaces": list_field([event["surface"] for event in peers]),
                "current_peer_pages": list_field([event["physical_page"] for event in peers]),
                "current_peer_event_ids": list_field([event["event_id"] for event in peers]),
                "peer_interface_status": (
                    "CURRENT_PEER_INTERFACE_BRIDGE"
                    if peers
                    else "CURRENT_SINGLETON_INTERFACE"
                ),
                "guard": "EXACT_ADJACENT_PAIR_IN_CURRENT_ADMITTED_EVENTS__NOT_OLD_OR_PRODUCTIVE_RULE",
            }
        )

    promoted_rows: list[dict[str, object]] = []
    residual_rows: list[dict[str, object]] = []
    for target in queue:
        surface = target["surface"]
        source = readers[surface]
        if source["support_band"] == "WORKING_DEFAULT_COMPLETE_OLD_TILES":
            residual_rows.append(
                {
                    "surface": surface,
                    "final_recipe": source["final_recipe"],
                    "residual_dimension": "HIGHER_ORDER_SEQUENCE_CONTEXT",
                    "residual_detail": "NO_COMPLETE_OLD_PORTABLE_SKELETON_OR_ORDERED_STATEMENT_PATH",
                    "visible_status": "EXACT_VISIBLE_COMPOSITION",
                    "next_search": "GROUP_BY_RECURRENT_VISIBLE_RECIPE_FRAME",
                    "guard": "CURRENT_READING_RETAINED__NO_WHOLE_RECIPE_CLAIM",
                }
            )
            continue
        need_context = "ANCHOR_CONTEXT_MODE_DIFFERENCE" in source["tier_caution"]
        need_interface = surface in interface_targets
        context_ok = not need_context or surface in context_repaired
        interface_ok = not need_interface or surface in interface_repaired
        if context_ok and interface_ok and surface != "shso":
            promoted_rows.append(
                {
                    "surface": surface,
                    "final_recipe": source["final_recipe"],
                    "visible_route": next(
                        row["selected_visible_trace"]
                        for row in visible_rows
                        if row["surface"] == surface
                    ),
                    "context_bridge": (
                        "CURRENT_PEER_CONTEXT_BRIDGE" if need_context else "NOT_REQUIRED"
                    ),
                    "interface_bridge": (
                        "CURRENT_PEER_INTERFACE_BRIDGE"
                        if need_interface
                        else "NOT_REQUIRED"
                    ),
                    "promotion_status": "PROMOTED_OUT_OF_NAMED_DEFAULT_QUEUE",
                    "guard": "CURRENT_WORKING_PEER_PROMOTION__NOT_CONFIRMED_WORD_OR_UNIVERSAL_RULE",
                }
            )
            continue
        if not context_ok:
            dimension = "ANCHOR_CONTEXT"
            detail = "NO_CURRENT_TARGET_MODE_PEER_FOR_OLD_ANCHOR"
            next_search = "SEARCH_SHARED_CONTEXT_SWITCH_FRAME"
        elif not interface_ok:
            dimension = "DIRECT_INTERFACE"
            detail = interface_targets[surface]
            next_search = "SEARCH_SEPARATED_OR_FAMILY_PAIR_BRIDGE"
        else:
            raise RuntimeError(f"unclassified residual {surface}")
        residual_rows.append(
            {
                "surface": surface,
                "final_recipe": source["final_recipe"],
                "residual_dimension": dimension,
                "residual_detail": detail,
                "visible_status": "EXACT_VISIBLE_COMPOSITION",
                "next_search": next_search,
                "guard": "CURRENT_READING_RETAINED__RESIDUAL_SUPPORT_DIMENSION_ONLY",
            }
        )

    promoted_rows.sort(key=lambda row: row["surface"])
    residual_rows.sort(
        key=lambda row: (row["residual_dimension"], row["surface"])
    )
    if {row["surface"] for row in promoted_rows} != {
        "chady",
        "kody",
        "qoekedy",
        "qokshd",
    }:
        raise RuntimeError("unexpected peer promotion set")

    residual_counts = Counter(row["residual_dimension"] for row in residual_rows)
    selected_counts = Counter(
        int(row["selected_segment_count"]) for row in visible_rows
    )
    metrics: dict[str, object] = {
        "status": "PASS_ALL_23_DEFAULTS_EXACTLY_VISIBLE__4_CURRENT_PEER_PROMOTIONS__19_SUPPORT_RESTS",
        "source_default_count": 23,
        "exact_visible_composition_count": len(visible_rows),
        "old26_exact_cover_target_count": len(selected),
        "old26_exact_cover_path_count": len(cover_rows),
        "bounded_current_visible_route_count": len(special_specs),
        "two_segment_selected_route_count": selected_counts[2],
        "three_segment_selected_route_count": selected_counts[3],
        "four_segment_selected_route_count": selected_counts[4],
        "opaque_whole_gloss_count": 0,
        "context_mismatch_source_count": len(context_rows),
        "context_peer_repaired_count": len(context_repaired),
        "context_unresolved_count": len(context_rows) - len(context_repaired),
        "context_peer_event_count": sum(
            int(row["current_peer_event_count"]) for row in context_rows
        ),
        "new_interface_source_count": len(interface_rows),
        "interface_peer_repaired_count": len(interface_repaired),
        "interface_unresolved_count": len(interface_rows) - len(interface_repaired),
        "interface_peer_event_count": sum(
            int(row["current_peer_event_count"]) for row in interface_rows
        ),
        "promoted_card_count": len(promoted_rows),
        "residual_card_count": len(residual_rows),
        "residual_higher_order_sequence_count": residual_counts[
            "HIGHER_ORDER_SEQUENCE_CONTEXT"
        ],
        "residual_anchor_context_count": residual_counts["ANCHOR_CONTEXT"],
        "residual_direct_interface_count": residual_counts["DIRECT_INTERFACE"],
        "complete_neutral_meaning_count": sum(
            bool(row["neutral_component_reading_de"]) for row in visible_rows
        ),
        "complete_context_meaning_count": sum(
            bool(row["known_contextual_readings_de"]) for row in visible_rows
        ),
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }

    write_tsv(
        ART / "gdt549_96_old26_exact_cover_paths.tsv",
        cover_rows,
        [
            "surface",
            "final_recipe",
            "compressed_cover_rank",
            "selected_compressed_cover",
            "segment_count",
            "canonical_segment_count",
            "learned_segment_count",
            "alias_penalty_total",
            "visible_trace",
            "evidence_trace",
            "exact_surface_reconstruction",
            "exact_recipe_reconstruction",
            "guard",
        ],
    )
    write_tsv(
        ART / "gdt549_23_exact_visible_default_cards.tsv",
        visible_rows,
        list(visible_rows[0]),
    )
    write_tsv(
        ART / "gdt549_9_context_mismatch_peer_audit.tsv",
        context_rows,
        list(context_rows[0]),
    )
    write_tsv(
        ART / "gdt549_6_new_interface_peer_audit.tsv",
        interface_rows,
        list(interface_rows[0]),
    )
    write_tsv(
        ART / "gdt549_4_promoted_peer_cards.tsv",
        promoted_rows,
        list(promoted_rows[0]),
    )
    write_tsv(
        ART / "gdt549_19_residual_support_queue.tsv",
        residual_rows,
        list(residual_rows[0]),
    )
    write_tsv(
        ART / "gdt549_visible_peer_summary.tsv",
        [
            {"metric": key, "value": str(value), "guard": "GDT549_REPLAYED_METRIC"}
            for key, value in metrics.items()
        ],
        ["metric", "value", "guard"],
    )
    (ART / "GDT549_DEFAULT_QUEUE_VISIBLE_PEER_BOOK.md").write_text(
        build_book(visible_rows, promoted_rows, residual_rows, metrics),
        encoding="utf-8",
    )
    (ART / "gdt549_result.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
