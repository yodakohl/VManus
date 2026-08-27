#!/usr/bin/env python3
"""Bridge the ten GDT549 sequence cautions with recurrent visible recipe frames."""

from __future__ import annotations

import csv
import itertools
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
EXP = ROOT / "experiments/yolo/gdt550_recurrent_sequence_frame_bridges"
ART = EXP / "artifacts"
G519 = ROOT / "experiments/yolo/gdt519_visible_stem_anchor_transducer/artifacts"
G548 = ROOT / "experiments/yolo/gdt548_unified_145_prose_reader/artifacts"
G549 = ROOT / "experiments/yolo/gdt549_default_queue_visible_peer_bridges/artifacts"

ALIAS_IN = G519 / "gdt519_anchor_alias_lexicon.tsv"
READER_IN = G548 / "gdt548_145_unified_prose_reader.tsv"
VISIBLE_IN = G549 / "gdt549_23_exact_visible_default_cards.tsv"
RESIDUAL_IN = G549 / "gdt549_19_residual_support_queue.tsv"


@dataclass(frozen=True)
class Segment:
    alias: str
    atom_sequence: tuple[str, ...]
    source: str
    support: int
    share: float
    penalty: float

    @property
    def recipe(self) -> str:
        return "+".join(self.atom_sequence)


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
            for path in states.get((atom_index, char_index), []):
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


def segment_trace(path: tuple[Segment, ...]) -> str:
    return " | ".join(f"{part.alias}→{part.recipe}" for part in path)


def evidence_trace(path: tuple[Segment, ...]) -> str:
    return " | ".join(
        f"{part.alias}:{part.source}:n{part.support}:share{part.share:.6f}"
        for part in path
    )


def modes(row: dict[str, str]) -> set[str]:
    return set(row["observed_requirement_modes"].split("|"))


def position(start: int, end: int, length: int) -> str:
    if start == 0 and end == length:
        return "FULL"
    if start == 0:
        return "START"
    if end == length:
        return "END"
    return "INTERNAL"


def joined(values: set[str]) -> str:
    return "|".join(sorted(values)) if values else "NONE"


def build_book(
    selected_frames: list[dict[str, object]],
    promoted: list[dict[str, object]],
    residual: list[dict[str, object]],
    metrics: dict[str, object],
) -> str:
    lines = [
        "# GDT550 — fünf sichtbare Frames schließen zehn Sequenzkarten",
        "",
        f"Status: `{metrics['status']}`",
        "",
        "Die fünf ausgewählten Frames bilden eine kleinste vollständige Abdeckung",
        "der zehn GDT549-Sequenzkarten. Jeder Frame erscheint außerdem in mindestens",
        "einer stärkeren Karte mit passendem beobachtetem Kontextmodus.",
        "",
        "## Frames",
        "",
    ]
    for row in selected_frames:
        lines.extend(
            [
                f"### `{row['visible_frame']}→{row['recipe_frame']}`",
                "",
                f"- Restkarten: `{row['sequence_targets']}`",
                f"- Stärkere Peers: `{row['strong_peers']}`",
                f"- Alte sichtbare Realisierung: `{row['frame_realization_trace']}`",
                f"- Passende Ziel/Peer-Kontextkontakte: {row['same_mode_peer_contact_count']}",
            ]
        )
    lines.extend(["", "## Zehn Arbeits-Promotionen", ""])
    for row in promoted:
        lines.extend(
            [
                f"### `{row['surface']}`",
                "",
                f"- Vollroute: `{row['exact_visible_route']}`",
                f"- Brückenframe: `{row['visible_frame']}→{row['recipe_frame']}`",
                f"- Gleichmodus-Peers: `{row['same_mode_peer_surfaces']}`",
                f"- Default: {row['neutral_component_reading_de']}",
                f"- Bekannter Kontext: {row['known_contextual_readings_de']}",
            ]
        )
    lines.extend(
        [
            "",
            f"Danach verbleiben {len(residual)} getrennte Karten: vier Kontext- und",
            "fünf direkte Interfacefragen. Alle Bedeutungen und Zerlegungen bleiben",
            "erhalten; ein Frame ist keine neue Ganzwortübersetzung.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    reader_rows = read_tsv(READER_IN)
    readers = keyed(reader_rows, "surface")
    visible = keyed(read_tsv(VISIBLE_IN), "surface")
    residual_source = read_tsv(RESIDUAL_IN)
    sequence_targets = {
        row["surface"]
        for row in residual_source
        if row["residual_dimension"] == "HIGHER_ORDER_SEQUENCE_CONTEXT"
    }
    if len(sequence_targets) != 10:
        raise RuntimeError("expected ten sequence targets")

    aliases = [row for row in read_tsv(ALIAS_IN) if row["model"] == "FULL_OLD26"]
    options: dict[tuple[str, ...], list[Segment]] = defaultdict(list)
    direct_alias: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in aliases:
        sequence = tuple(row["atom_sequence"].split("+"))
        options[sequence].append(
            Segment(
                alias=row["surface_alias"],
                atom_sequence=sequence,
                source=row["alias_source"],
                support=int(row["support"]),
                share=float(row["support_share"]),
                penalty=float(row["alias_penalty"]),
            )
        )
        direct_alias[(row["surface_alias"], row["atom_sequence"])].append(row)

    paths_by_surface: dict[str, list[tuple[Segment, ...]]] = {}
    for row in reader_rows:
        paths_by_surface[row["surface"]] = enumerate_exact_covers(
            row["surface"], tuple(row["final_recipe"].split("+")), options
        )
    if not all(paths_by_surface[surface] for surface in sequence_targets):
        raise RuntimeError("sequence target without old exact cover")

    occurrence_options: dict[
        tuple[str, str], dict[str, list[dict[str, object]]]
    ] = defaultdict(lambda: defaultdict(list))
    for row in reader_rows:
        surface = row["surface"]
        for path in paths_by_surface[surface]:
            char_offsets = [0]
            atom_offsets = [0]
            for segment in path:
                char_offsets.append(char_offsets[-1] + len(segment.alias))
                atom_offsets.append(atom_offsets[-1] + len(segment.atom_sequence))
            for start in range(len(path)):
                for end in range(start + 1, min(len(path), start + 3) + 1):
                    chain = path[start:end]
                    visible_frame = "".join(part.alias for part in chain)
                    recipe_atoms = sum((part.atom_sequence for part in chain), tuple())
                    if len(visible_frame) < 2 or len(recipe_atoms) < 2:
                        continue
                    recipe_frame = "+".join(recipe_atoms)
                    occurrence_options[(visible_frame, recipe_frame)][surface].append(
                        {
                            "segment_count": len(chain),
                            "penalty": sum(part.penalty for part in chain),
                            "frame_realization_trace": segment_trace(chain),
                            "frame_evidence_trace": evidence_trace(chain),
                            "position": position(
                                char_offsets[start], char_offsets[end], len(surface)
                            ),
                        }
                    )

    best_occurrence: dict[tuple[str, str], dict[str, dict[str, object]]] = {}
    for frame, by_surface in occurrence_options.items():
        best_occurrence[frame] = {}
        for surface, occurrences in by_surface.items():
            best_occurrence[frame][surface] = sorted(
                occurrences,
                key=lambda row: (
                    int(row["segment_count"]),
                    float(row["penalty"]),
                    str(row["frame_realization_trace"]),
                ),
            )[0]

    candidates_raw: list[dict[str, object]] = []
    candidate_payload: dict[tuple[str, str], dict[str, object]] = {}
    for frame, occurrences in best_occurrence.items():
        visible_frame, recipe_frame = frame
        targets = set(occurrences) & sequence_targets
        strong_peers = {
            surface
            for surface in set(occurrences) - sequence_targets
            if readers[surface]["weak_queue_candidate"] == "NO"
        }
        if not targets or not strong_peers:
            continue
        peer_map = {
            target: {
                peer
                for peer in strong_peers
                if modes(readers[target]) & modes(readers[peer])
            }
            for target in targets
        }
        covered_targets = {target for target, peers in peer_map.items() if peers}
        best_realization = min(
            (occurrences[surface] for surface in set(occurrences)),
            key=lambda row: (
                int(row["segment_count"]),
                float(row["penalty"]),
                str(row["frame_realization_trace"]),
            ),
        )
        direct = direct_alias.get(frame, [])
        if direct:
            direct_best = min(
                direct,
                key=lambda row: (float(row["alias_penalty"]), -int(row["support"])),
            )
            realization_class = "SINGLE_OLD_LEARNED_OR_CANONICAL_ALIAS"
            old_evidence = (
                f"{visible_frame}:{direct_best['alias_source']}:"
                f"n{direct_best['support']}:share{direct_best['support_share']}"
            )
        else:
            realization_class = "COALESCED_ADJACENT_OLD_ALIAS_SEGMENTS"
            old_evidence = str(best_realization["frame_evidence_trace"])
        payload = {
            "visible_frame": visible_frame,
            "recipe_frame": recipe_frame,
            "recipe_atom_count": len(recipe_frame.split("+")),
            "frame_realization_class": realization_class,
            "frame_realization_trace": best_realization["frame_realization_trace"],
            "old_alias_evidence": old_evidence,
            "sequence_target_count": len(targets),
            "sequence_targets": joined(targets),
            "strong_peer_count": len(strong_peers),
            "strong_peers": joined(strong_peers),
            "target_mode_coverage_count": len(covered_targets),
            "same_mode_peer_contact_count": sum(len(peers) for peers in peer_map.values()),
            "same_mode_peer_map": " ; ".join(
                f"{target}:{joined(peers)}" for target, peers in sorted(peer_map.items())
            ),
            "target_positions": "|".join(
                f"{surface}:{occurrences[surface]['position']}" for surface in sorted(targets)
            ),
            "peer_positions": "|".join(
                f"{surface}:{occurrences[surface]['position']}"
                for surface in sorted(strong_peers)
            ),
            "all_targets_have_same_mode_peer": (
                "YES" if covered_targets == targets else "NO"
            ),
            "guard": "EXACT_FRAME_INSIDE_FULL_OLD_ALIAS_COVERS__CURRENT_STRONG_PEERS_ONLY",
            "_targets": targets,
            "_strong_peers": strong_peers,
            "_peer_map": peer_map,
        }
        candidate_payload[frame] = payload
        candidates_raw.append(payload)

    candidates_raw.sort(
        key=lambda row: (
            -int(row["sequence_target_count"]),
            -int(row["strong_peer_count"]),
            -int(row["recipe_atom_count"]),
            -len(str(row["visible_frame"])),
            str(row["visible_frame"]),
            str(row["recipe_frame"]),
        )
    )
    candidate_rows: list[dict[str, object]] = []
    frame_id: dict[tuple[str, str], str] = {}
    for index, payload in enumerate(candidates_raw, 1):
        frame = (str(payload["visible_frame"]), str(payload["recipe_frame"]))
        identifier = f"F{index:03d}"
        frame_id[frame] = identifier
        candidate_rows.append(
            {
                "frame_id": identifier,
                **{key: value for key, value in payload.items() if not key.startswith("_")},
            }
        )
    if len(candidate_rows) != 23:
        raise RuntimeError(f"expected 23 candidate frames, got {len(candidate_rows)}")

    eligible_frames = [
        frame
        for frame, payload in candidate_payload.items()
        if payload["all_targets_have_same_mode_peer"] == "YES"
    ]
    solutions: list[tuple[tuple[str, str], ...]] = []
    for width in range(1, len(eligible_frames) + 1):
        for combination in itertools.combinations(eligible_frames, width):
            covered = set().union(
                *(candidate_payload[frame]["_targets"] for frame in combination)
            )
            if covered == sequence_targets:
                solutions.append(combination)
        if solutions:
            break
    if len(solutions) != 6 or len(solutions[0]) != 5:
        raise RuntimeError("minimum frame-cover solution drift")

    def solution_key(solution: tuple[tuple[str, str], ...]) -> tuple[object, ...]:
        return (
            -sum(len(frame[1].split("+")) for frame in solution),
            -sum(len(frame[0]) for frame in solution),
            -sum(
                int(candidate_payload[frame]["same_mode_peer_contact_count"])
                for frame in solution
            ),
            tuple(sorted(solution)),
        )

    solutions.sort(key=solution_key)
    selected_solution = solutions[0]
    expected_selected = {
        ("chor", "CH+OR"),
        ("ko", "K+O"),
        ("she", "SH+E"),
        ("shy", "SH+Y"),
        ("ches", "CH+E+S"),
    }
    if set(selected_solution) != expected_selected:
        raise RuntimeError(f"selected frame set drift: {selected_solution}")

    solution_rows: list[dict[str, object]] = []
    for index, solution in enumerate(solutions, 1):
        covered = set().union(
            *(candidate_payload[frame]["_targets"] for frame in solution)
        )
        solution_rows.append(
            {
                "solution_rank": index,
                "selected_solution": "YES" if index == 1 else "NO",
                "frame_count": len(solution),
                "frame_ids": "|".join(sorted(frame_id[frame] for frame in solution)),
                "frame_traces": " | ".join(
                    f"{frame[0]}→{frame[1]}" for frame in sorted(solution)
                ),
                "covered_target_count": len(covered),
                "covered_targets": joined(covered),
                "total_mapped_atom_count": sum(
                    len(frame[1].split("+")) for frame in solution
                ),
                "total_same_mode_peer_contacts": sum(
                    int(candidate_payload[frame]["same_mode_peer_contact_count"])
                    for frame in solution
                ),
                "selection_priority": (
                    "MINIMUM_FRAME_COUNT__THEN_MAX_MAPPED_ATOMS_VISIBLE_LENGTH_AND_PEERS"
                ),
                "guard": "FINITE_EXACT_SET_COVER_OVER_CONTEXT_COMPATIBLE_CANDIDATE_FRAMES",
            }
        )

    selected_frame_rows: list[dict[str, object]] = []
    for frame in sorted(selected_solution):
        payload = candidate_payload[frame]
        selected_frame_rows.append(
            {
                "frame_id": frame_id[frame],
                **{key: value for key, value in payload.items() if not key.startswith("_")},
                "bridge_decision": "SELECTED_RECURRENT_SEQUENCE_FRAME",
            }
        )

    occurrence_rows: list[dict[str, object]] = []
    selected_strong_peers: set[str] = set()
    for frame in sorted(selected_solution):
        payload = candidate_payload[frame]
        targets = set(payload["_targets"])
        peers = set(payload["_strong_peers"])
        selected_strong_peers.update(peers)
        occurrences = best_occurrence[frame]
        for surface in sorted(targets | peers):
            role = "SEQUENCE_TARGET" if surface in targets else "STRONG_PEER"
            if role == "SEQUENCE_TARGET":
                matched = set(payload["_peer_map"][surface])
            else:
                matched = {
                    target
                    for target in targets
                    if modes(readers[target]) & modes(readers[surface])
                }
            occurrence_rows.append(
                {
                    "frame_id": frame_id[frame],
                    "visible_frame": frame[0],
                    "recipe_frame": frame[1],
                    "surface": surface,
                    "occurrence_role": role,
                    "full_recipe": readers[surface]["final_recipe"],
                    "support_tier": readers[surface]["support_tier"],
                    "observed_requirement_modes": readers[surface][
                        "observed_requirement_modes"
                    ],
                    "frame_position": occurrences[surface]["position"],
                    "frame_realization_trace": occurrences[surface][
                        "frame_realization_trace"
                    ],
                    "same_mode_bridge_contacts": joined(matched),
                    "guard": "EXACT_FRAME_OCCURRENCE_INSIDE_FULL_OLD_ALIAS_COVER",
                }
            )

    promoted_rows: list[dict[str, object]] = []
    for surface in sorted(sequence_targets):
        matching_frames = [
            frame
            for frame in selected_solution
            if surface in candidate_payload[frame]["_targets"]
        ]
        if len(matching_frames) != 1:
            raise RuntimeError(f"expected one selected frame for {surface}")
        frame = matching_frames[0]
        payload = candidate_payload[frame]
        peers = set(payload["_peer_map"][surface])
        occurrence = best_occurrence[frame][surface]
        source = readers[surface]
        promoted_rows.append(
            {
                "surface": surface,
                "final_recipe": source["final_recipe"],
                "exact_visible_route": visible[surface]["selected_visible_trace"],
                "frame_id": frame_id[frame],
                "visible_frame": frame[0],
                "recipe_frame": frame[1],
                "frame_position": occurrence["position"],
                "frame_realization_trace": occurrence["frame_realization_trace"],
                "target_modes": source["observed_requirement_modes"],
                "same_mode_peer_count": len(peers),
                "same_mode_peer_surfaces": joined(peers),
                "old_tile_and_seam_evidence": source["tier_evidence"],
                "neutral_component_reading_de": source[
                    "neutral_component_reading_de"
                ],
                "known_contextual_readings_de": source[
                    "known_contextual_readings_de"
                ],
                "promotion_status": "PROMOTED_BY_RECURRENT_VISIBLE_FRAME_AND_SAME_MODE_PEER",
                "retained_caution": (
                    "NO_COMPLETE_OLD_WHOLE_RECIPE_OR_ORDERED_STATEMENT_PATH__"
                    "WORKING_FRAME_BRIDGE_ACCEPTED"
                ),
                "guard": "CURRENT_WORKING_PROMOTION__NO_NEW_RECIPE_FRAME_OR_MEANING",
            }
        )

    residual_rows: list[dict[str, object]] = []
    for index, row in enumerate(
        [
            row
            for row in residual_source
            if row["residual_dimension"] != "HIGHER_ORDER_SEQUENCE_CONTEXT"
        ],
        1,
    ):
        residual_rows.append(
            {
                "queue_ordinal": index,
                **row,
                "post_gdt550_status": "UNCHANGED_CONTEXT_OR_INTERFACE_SUPPORT_REST",
            }
        )
    if len(promoted_rows) != 10 or len(residual_rows) != 9:
        raise RuntimeError("promotion/residual count drift")

    residual_counts = Counter(row["residual_dimension"] for row in residual_rows)
    selected_contacts = sum(
        int(candidate_payload[frame]["same_mode_peer_contact_count"])
        for frame in selected_solution
    )
    metrics: dict[str, object] = {
        "status": "PASS_FIVE_RECURRENT_FRAMES_BRIDGE_ALL_10_SEQUENCE_DEFAULTS__NINE_SUPPORT_RESTS",
        "source_sequence_card_count": 10,
        "source_sequence_exact_old_cover_count": sum(
            bool(paths_by_surface[surface]) for surface in sequence_targets
        ),
        "candidate_recurrent_frame_count": len(candidate_rows),
        "all_target_modes_peer_compatible_frame_count": sum(
            row["all_targets_have_same_mode_peer"] == "YES" for row in candidate_rows
        ),
        "minimum_frame_cover_size": len(selected_solution),
        "minimum_frame_cover_solution_count": len(solutions),
        "selected_frame_count": len(selected_frame_rows),
        "selected_frame_target_count": len(
            set().union(
                *(candidate_payload[frame]["_targets"] for frame in selected_solution)
            )
        ),
        "selected_frame_strong_peer_count": len(selected_strong_peers),
        "selected_same_mode_peer_contact_count": selected_contacts,
        "selected_frame_occurrence_count": len(occurrence_rows),
        "promoted_sequence_card_count": len(promoted_rows),
        "residual_support_card_count": len(residual_rows),
        "residual_anchor_context_count": residual_counts["ANCHOR_CONTEXT"],
        "residual_direct_interface_count": residual_counts["DIRECT_INTERFACE"],
        "complete_neutral_meaning_count": sum(
            bool(row["neutral_component_reading_de"]) for row in promoted_rows
        ),
        "complete_context_meaning_count": sum(
            bool(row["known_contextual_readings_de"]) for row in promoted_rows
        ),
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }

    write_tsv(
        ART / "gdt550_23_candidate_recurrent_frames.tsv",
        candidate_rows,
        list(candidate_rows[0]),
    )
    write_tsv(
        ART / "gdt550_6_minimum_five_frame_covers.tsv",
        solution_rows,
        list(solution_rows[0]),
    )
    write_tsv(
        ART / "gdt550_5_selected_bridge_frames.tsv",
        selected_frame_rows,
        list(selected_frame_rows[0]),
    )
    write_tsv(
        ART / "gdt550_31_selected_frame_occurrences.tsv",
        occurrence_rows,
        list(occurrence_rows[0]),
    )
    write_tsv(
        ART / "gdt550_10_promoted_sequence_cards.tsv",
        promoted_rows,
        list(promoted_rows[0]),
    )
    write_tsv(
        ART / "gdt550_9_residual_support_queue.tsv",
        residual_rows,
        list(residual_rows[0]),
    )
    write_tsv(
        ART / "gdt550_recurrent_frame_summary.tsv",
        [
            {"metric": key, "value": str(value), "guard": "GDT550_REPLAYED_METRIC"}
            for key, value in metrics.items()
        ],
        ["metric", "value", "guard"],
    )
    (ART / "GDT550_RECURRENT_SEQUENCE_FRAME_BOOK.md").write_text(
        build_book(selected_frame_rows, promoted_rows, residual_rows, metrics),
        encoding="utf-8",
    )
    (ART / "gdt550_result.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
