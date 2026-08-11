#!/usr/bin/env python3
"""Build a cross-folio analogue index for the consensus record packet."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "consensus_structural_record_interlinear_v1.tsv"
SOURCE_VALIDATION = RESULTS / "consensus_structural_record_interlinear_v1_validation.json"
SPEC = BASE / "CONSENSUS_STRUCTURAL_RECORD_ANALOG_INDEX_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_TSV = RESULTS / "consensus_structural_record_analog_index_v1.tsv"
OUT_PACKET = RESULTS / "consensus_structural_record_analog_packet_v1.tsv"
OUT_JSON = RESULTS / "consensus_structural_record_analog_index_v1.json"
OUT_REPORT = RESULTS / "consensus_structural_record_analog_index_v1_report.md"

FROZEN = {
    SOURCE: "7c375a9336588096e657917548eb3f2038828d9d6d42b75da2d24b57ccd3f387",
    SOURCE_VALIDATION: "368d1be6a70c403f77abb5f87e3c0635bea1cf084c6b7408530cbf857c2e1533",
}
EXPRESSION = re.compile(
    r"^([SFCL]):([^{}]+)\{adj=([^;]+);fl=([^;]+);ec=([^;]+);"
    r"o=([0-9]+);c=([0-9]+);p=([^{};]+)\}$"
)
FOLIO = re.compile(r"^f([0-9]+)")
FIELDS = [
    "pair_order", "target_record_order", "target_segment_id", "target_page",
    "target_section", "target_currier", "target_hand", "target_group_count",
    "target_family_expression", "target_sta_expression", "target_basic_eva_lossy",
    "target_formal_expression", "candidate_rank", "candidate_pool_size",
    "candidate_record_order", "candidate_segment_id", "candidate_page",
    "candidate_section", "candidate_currier", "candidate_hand", "same_section",
    "candidate_family_expression", "candidate_sta_expression",
    "candidate_basic_eva_lossy", "candidate_formal_expression",
    "structure_distance", "adjacency_distance", "first_last_mismatches",
    "edge_core_mismatches", "opening_count_distance", "closing_count_distance",
    "family_distance", "sta_member_distance", "favored_path_distance",
    "exact_structure_match",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def levenshtein(left: list[str] | str, right: list[str] | str) -> int:
    previous = list(range(len(right) + 1))
    for i, left_item in enumerate(left, 1):
        current = [i]
        for j, right_item in enumerate(right, 1):
            current.append(min(
                current[-1] + 1,
                previous[j] + 1,
                previous[j - 1] + int(left_item != right_item),
            ))
        previous = current
    return previous[-1]


def physical_folio(page: str) -> int:
    match = FOLIO.match(page)
    if not match:
        raise ValueError(f"unrecognized physical folio: {page}")
    return int(match.group(1))


def parse_expression(row: dict[str, str]) -> list[tuple[str, str, str, str, str, int, int, str]]:
    parsed = []
    for item in row["formal_expression"].split(" | "):
        match = EXPRESSION.match(item)
        if not match:
            raise ValueError(f"bad formal expression: {item}")
        position, surface, adjacency, first_last, edge_core, opening, closing, path = match.groups()
        parsed.append((position, surface, adjacency, first_last, edge_core,
                       int(opening), int(closing), path))
    if len(parsed) != int(row["group_count"]):
        raise ValueError("formal expression group-count drift")
    if [item[1] for item in parsed] != row["family_expression"].split(" "):
        raise ValueError("formal expression surface drift")
    return parsed


def member_groups(row: dict[str, str]) -> list[list[str]]:
    groups = [group.split(" ") for group in row["zl_sta_expression"].split(" | ")]
    if len(groups) != int(row["group_count"]):
        raise ValueError("STA expression group-count drift")
    if row["zl_sta_expression"] != row["it_sta_expression"] or row["zl_sta_expression"] != row["rf_sta_expression"]:
        raise ValueError("eligible record is not all-reading member-stable")
    return groups


def distances(target: dict[str, str], candidate: dict[str, str]) -> dict[str, int]:
    target_groups, candidate_groups = parse_expression(target), parse_expression(candidate)
    target_members, candidate_members = member_groups(target), member_groups(candidate)
    if len(target_groups) != len(candidate_groups):
        raise ValueError("unaligned group counts")
    adjacency = sum(levenshtein(a[2], b[2]) for a, b in zip(target_groups, candidate_groups))
    first_last = sum(a[3] != b[3] for a, b in zip(target_groups, candidate_groups))
    edge_core = sum(a[4] != b[4] for a, b in zip(target_groups, candidate_groups))
    opening = sum(abs(a[5] - b[5]) for a, b in zip(target_groups, candidate_groups))
    closing = sum(abs(a[6] - b[6]) for a, b in zip(target_groups, candidate_groups))
    family = sum(levenshtein(a[1], b[1]) for a, b in zip(target_groups, candidate_groups))
    member = sum(levenshtein(a, b) for a, b in zip(target_members, candidate_members))
    path = sum(levenshtein("" if a[7] == "-" else a[7], "" if b[7] == "-" else b[7])
               for a, b in zip(target_groups, candidate_groups))
    structure = adjacency + first_last + edge_core + opening + closing
    return {
        "structure_distance": structure, "adjacency_distance": adjacency,
        "first_last_mismatches": first_last, "edge_core_mismatches": edge_core,
        "opening_count_distance": opening, "closing_count_distance": closing,
        "family_distance": family, "sta_member_distance": member,
        "favored_path_distance": path, "exact_structure_match": int(structure == 0),
    }


def rank_key(item: tuple[dict[str, int], dict[str, str]], target: dict[str, str]) -> tuple[object, ...]:
    distance, candidate = item
    return (
        distance["structure_distance"], distance["family_distance"],
        distance["sta_member_distance"], distance["favored_path_distance"],
        -int(candidate["section"] == target["section"]),
        candidate["segment_id"].encode("utf-8"),
    )


def build_row(pair_order: int, target: dict[str, str], candidate: dict[str, str],
              candidate_rank: int, candidate_pool_size: int,
              distance: dict[str, int]) -> dict[str, object]:
    row: dict[str, object] = {
        "pair_order": pair_order, "target_record_order": int(target["record_order"]),
        "target_segment_id": target["segment_id"], "target_page": target["page"],
        "target_section": target["section"], "target_currier": target["currier"],
        "target_hand": target["hand"], "target_group_count": int(target["group_count"]),
        "target_family_expression": target["family_expression"],
        "target_sta_expression": target["zl_sta_expression"],
        "target_basic_eva_lossy": target["zl_basic_eva_lossy_expression"],
        "target_formal_expression": target["formal_expression"],
        "candidate_rank": candidate_rank, "candidate_pool_size": candidate_pool_size,
        "candidate_record_order": int(candidate["record_order"]),
        "candidate_segment_id": candidate["segment_id"], "candidate_page": candidate["page"],
        "candidate_section": candidate["section"], "candidate_currier": candidate["currier"],
        "candidate_hand": candidate["hand"],
        "same_section": int(candidate["section"] == target["section"]),
        "candidate_family_expression": candidate["family_expression"],
        "candidate_sta_expression": candidate["zl_sta_expression"],
        "candidate_basic_eva_lossy": candidate["zl_basic_eva_lossy_expression"],
        "candidate_formal_expression": candidate["formal_expression"],
    }
    row.update(distance)
    return row


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_report(result: dict[str, object]) -> str:
    counts = result["counts"]
    return f"""# Consensus structural record analogue index v1

Status: **{result['status']}**

The full index compares **{counts['targets']}** packet records with
**{counts['candidate_pairs']:,}** same-Currier, same-group-count records on
other physical folios.  Every target has at least
**{counts['minimum_candidate_pool']}** candidates on at least
**{counts['minimum_candidate_folios']}** other folios.  The compact packet
retains the first three transparent neighbors per target (**{counts['packet_rows']}** rows).

No candidate exactly matches a target's complete surface-blind formal
signature (**{counts['exact_structure_matches']}** exact matches).  This is a
capacity description: the listed neighbors are approximate formal analogues,
not repeated sentences or parallel passages.  Family, exact STA-member, path,
and formal-component distances remain separate in every row.

The index fits no model, tests no meaning, and assigns no word, part of speech,
morpheme, sound, language, cipher operation, plaintext, meaning, or
translation.  Basic EVA is an explicitly lossy display convenience.
"""


def main() -> None:
    outputs = (OUT_TSV, OUT_PACKET, OUT_JSON, OUT_REPORT)
    if any(path.exists() for path in outputs):
        raise SystemExit("refusing to overwrite analogue-index artifacts")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    validation = json.loads(SOURCE_VALIDATION.read_text(encoding="utf-8"))
    if validation.get("status") != "PASS_INDEPENDENT_RECORD_LEVEL_CONSENSUS_RECONSTRUCTION":
        raise SystemExit("source validation status mismatch")

    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    targets = [row for row in source_rows if row["packet_selected"] == "1"]
    stable = [row for row in source_rows if row["grammar_scope"] == "CONFIRMED_PROSE"
              and row["transcription_consensus_status"] == "ALL_MEMBER_AND_BOUNDARY_STABLE"]
    if len(targets) != 26 or any(row not in stable for row in targets):
        raise ValueError("target packet drift")

    rows: list[dict[str, object]] = []
    pool_counts: list[int] = []
    folio_counts: list[int] = []
    pair_order = 0
    for target in targets:
        candidates = [row for row in stable
                      if row["currier"] == target["currier"]
                      and row["group_count"] == target["group_count"]
                      and physical_folio(row["page"]) != physical_folio(target["page"])]
        scored = [(distances(target, candidate), candidate) for candidate in candidates]
        scored.sort(key=lambda item: rank_key(item, target))
        pool_counts.append(len(scored))
        folio_counts.append(len({physical_folio(candidate["page"]) for _, candidate in scored}))
        for candidate_rank, (distance, candidate) in enumerate(scored, 1):
            pair_order += 1
            rows.append(build_row(pair_order, target, candidate, candidate_rank,
                                  len(scored), distance))

    packet = [row for row in rows if int(row["candidate_rank"]) <= 3]
    write_tsv(OUT_TSV, rows)
    write_tsv(OUT_PACKET, packet)
    result = {
        "experiment": "CONSENSUS_STRUCTURAL_RECORD_ANALOG_INDEX_V1",
        "status": "PASS_DESCRIPTIVE_CROSS_FOLIO_ANALOG_INDEX",
        "decision": "RETAIN_TRANSPARENT_FORMAL_NEIGHBORS_FOR_HUMAN_INSPECTION_ONLY",
        "counts": {
            "source_records": len(source_rows), "stable_prose_candidates": len(stable),
            "targets": len(targets), "candidate_pairs": len(rows), "packet_rows": len(packet),
            "minimum_candidate_pool": min(pool_counts), "maximum_candidate_pool": max(pool_counts),
            "minimum_candidate_folios": min(folio_counts),
            "maximum_candidate_folios": max(folio_counts),
            "same_section_pairs": sum(int(row["same_section"]) for row in rows),
            "exact_structure_matches": sum(int(row["exact_structure_match"]) for row in rows),
            "top_candidate_sections": dict(sorted(Counter(
                row["candidate_section"] for row in packet if int(row["candidate_rank"]) == 1
            ).items())),
        },
        "metric": {
            "candidate_pool": "same Currier + exact group count + different physical folio",
            "ranking": ["structure_distance", "family_distance", "sta_member_distance",
                        "favored_path_distance", "same_section_desc", "segment_id_utf8"],
            "top_neighbors_per_target": 3,
        },
        "inputs": {path.name: sha(path) for path in FROZEN} | {
            SPEC.name: sha(SPEC), BUILDER.name: sha(BUILDER),
        },
        "outputs": {OUT_TSV.name: sha(OUT_TSV), OUT_PACKET.name: sha(OUT_PACKET)},
        "english_glosses": 0,
        "claim_ceiling": (
            "Deterministic cross-folio formal-neighbor concordance only; no repeated sentence, "
            "parallel passage, referent, word, POS, morphology, sound, language, cipher, "
            "plaintext, meaning, or translation follows."
        ),
    }
    report = make_report(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
