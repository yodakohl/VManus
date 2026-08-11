#!/usr/bin/env python3
"""Independently rebuild the consensus structural record analogue index."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SOURCE = RESULTS / "consensus_structural_record_interlinear_v1.tsv"
SOURCE_VALIDATION = RESULTS / "consensus_structural_record_interlinear_v1_validation.json"
SPEC = ROOT / "CONSENSUS_STRUCTURAL_RECORD_ANALOG_INDEX_SPEC.md"
BUILDER = ROOT / "build_consensus_structural_record_analog_index.py"
PRODUCER_TSV = RESULTS / "consensus_structural_record_analog_index_v1.tsv"
PRODUCER_PACKET = RESULTS / "consensus_structural_record_analog_packet_v1.tsv"
PRODUCER_JSON = RESULTS / "consensus_structural_record_analog_index_v1.json"
PRODUCER_REPORT = RESULTS / "consensus_structural_record_analog_index_v1_report.md"
OUT_JSON = RESULTS / "consensus_structural_record_analog_index_v1_validation.json"
OUT_REPORT = RESULTS / "consensus_structural_record_analog_index_v1_validation_report.md"

FROZEN = {
    SOURCE: "7c375a9336588096e657917548eb3f2038828d9d6d42b75da2d24b57ccd3f387",
    SOURCE_VALIDATION: "368d1be6a70c403f77abb5f87e3c0635bea1cf084c6b7408530cbf857c2e1533",
    SPEC: "c159e350b855cec24c2b52c43bc59d4120030eb8ccec1cf98744fd13bb9984b2",
    BUILDER: "f6905e0e4bcee67869e97037fdbc77762236091ea72761fe2b016617c9beb4a0",
    PRODUCER_TSV: "98bda36e420025bdcb2be72de7c800cd271537f0df187fb8e19ba0c71c7a968c",
    PRODUCER_PACKET: "f759a06297bfed0e91e7170f08387db2b74a3887dfddcb177db3a0b3c5881a2d",
    PRODUCER_JSON: "89a126c333fcb05ff46092d7499685283ef4ae84de0719467a276b537871b041",
    PRODUCER_REPORT: "76bb22302ee7a6fa142bba0128838b238e3a673be19804d411a64792b3eeb934",
}
FORM = re.compile(
    r"^([SFCL]):([^{}]+)\{adj=([^;]+);fl=([^;]+);ec=([^;]+);"
    r"o=([0-9]+);c=([0-9]+);p=([^{};]+)\}$"
)
PAGE = re.compile(r"^f([0-9]+)")
COLUMNS = [
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edit_distance(a: list[str] | str, b: list[str] | str) -> int:
    row = list(range(len(b) + 1))
    for index_a, value_a in enumerate(a, 1):
        next_row = [index_a]
        for index_b, value_b in enumerate(b, 1):
            delete = row[index_b] + 1
            insert = next_row[-1] + 1
            replace = row[index_b - 1] + (value_a != value_b)
            next_row.append(min(delete, insert, replace))
        row = next_row
    return row[-1]


def folio(page: str) -> int:
    found = PAGE.match(page)
    assert found is not None
    return int(found.group(1))


def decode_form(record: dict[str, str]) -> list[dict[str, object]]:
    decoded = []
    for group in record["formal_expression"].split(" | "):
        found = FORM.fullmatch(group)
        assert found is not None
        position, surface, adjacency, first_last, edge_core, opening, closing, path = found.groups()
        decoded.append({
            "position": position, "surface": surface, "adjacency": adjacency,
            "first_last": first_last, "edge_core": edge_core, "opening": int(opening),
            "closing": int(closing), "path": path,
        })
    assert len(decoded) == int(record["group_count"])
    assert [group["surface"] for group in decoded] == record["family_expression"].split()
    return decoded


def decode_members(record: dict[str, str]) -> list[list[str]]:
    assert record["zl_sta_expression"] == record["it_sta_expression"]
    assert record["zl_sta_expression"] == record["rf_sta_expression"]
    decoded = [part.split() for part in record["zl_sta_expression"].split(" | ")]
    assert len(decoded) == int(record["group_count"])
    return decoded


def compare(target: dict[str, str], candidate: dict[str, str]) -> dict[str, int]:
    left, right = decode_form(target), decode_form(candidate)
    left_members, right_members = decode_members(target), decode_members(candidate)
    assert len(left) == len(right)
    adjacency = sum(edit_distance(a["adjacency"], b["adjacency"]) for a, b in zip(left, right))
    first_last = sum(a["first_last"] != b["first_last"] for a, b in zip(left, right))
    edge_core = sum(a["edge_core"] != b["edge_core"] for a, b in zip(left, right))
    opening = sum(abs(int(a["opening"]) - int(b["opening"])) for a, b in zip(left, right))
    closing = sum(abs(int(a["closing"]) - int(b["closing"])) for a, b in zip(left, right))
    family = sum(edit_distance(str(a["surface"]), str(b["surface"])) for a, b in zip(left, right))
    member = sum(edit_distance(a, b) for a, b in zip(left_members, right_members))
    path = sum(edit_distance("" if a["path"] == "-" else str(a["path"]),
                             "" if b["path"] == "-" else str(b["path"]))
               for a, b in zip(left, right))
    structure = adjacency + first_last + edge_core + opening + closing
    return {
        "structure_distance": structure, "adjacency_distance": adjacency,
        "first_last_mismatches": first_last, "edge_core_mismatches": edge_core,
        "opening_count_distance": opening, "closing_count_distance": closing,
        "family_distance": family, "sta_member_distance": member,
        "favored_path_distance": path, "exact_structure_match": int(structure == 0),
    }


def ordering(scored: tuple[dict[str, int], dict[str, str]], target: dict[str, str]) -> tuple[object, ...]:
    distances, candidate = scored
    return (
        distances["structure_distance"], distances["family_distance"],
        distances["sta_member_distance"], distances["favored_path_distance"],
        0 if candidate["section"] == target["section"] else 1,
        candidate["segment_id"].encode("utf-8"),
    )


def output_row(serial: int, target: dict[str, str], candidate: dict[str, str],
               rank: int, pool: int, distances: dict[str, int]) -> dict[str, object]:
    result: dict[str, object] = {
        "pair_order": serial, "target_record_order": int(target["record_order"]),
        "target_segment_id": target["segment_id"], "target_page": target["page"],
        "target_section": target["section"], "target_currier": target["currier"],
        "target_hand": target["hand"], "target_group_count": int(target["group_count"]),
        "target_family_expression": target["family_expression"],
        "target_sta_expression": target["zl_sta_expression"],
        "target_basic_eva_lossy": target["zl_basic_eva_lossy_expression"],
        "target_formal_expression": target["formal_expression"],
        "candidate_rank": rank, "candidate_pool_size": pool,
        "candidate_record_order": int(candidate["record_order"]),
        "candidate_segment_id": candidate["segment_id"], "candidate_page": candidate["page"],
        "candidate_section": candidate["section"], "candidate_currier": candidate["currier"],
        "candidate_hand": candidate["hand"],
        "same_section": int(target["section"] == candidate["section"]),
        "candidate_family_expression": candidate["family_expression"],
        "candidate_sta_expression": candidate["zl_sta_expression"],
        "candidate_basic_eva_lossy": candidate["zl_basic_eva_lossy_expression"],
        "candidate_formal_expression": candidate["formal_expression"],
    }
    result.update(distances)
    return result


def tsv_bytes(rows: list[dict[str, object]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def report(result: dict[str, object]) -> str:
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
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite analogue validation")
    for path, expected in FROZEN.items():
        assert digest(path) == expected, path
    source_validation = json.loads(SOURCE_VALIDATION.read_text(encoding="utf-8"))
    assert source_validation["status"] == "PASS_INDEPENDENT_RECORD_LEVEL_CONSENSUS_RECONSTRUCTION"
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle, delimiter="\t"))
    targets = [record for record in records if record["packet_selected"] == "1"]
    eligible = [record for record in records
                if record["grammar_scope"] == "CONFIRMED_PROSE"
                and record["transcription_consensus_status"] == "ALL_MEMBER_AND_BOUNDARY_STABLE"]
    assert len(records) == 4012 and len(targets) == 26 and len(eligible) == 1240

    rebuilt: list[dict[str, object]] = []
    pools, folios = [], []
    serial = 0
    for target in targets:
        candidates = [candidate for candidate in eligible
                      if candidate["currier"] == target["currier"]
                      and int(candidate["group_count"]) == int(target["group_count"])
                      and folio(candidate["page"]) != folio(target["page"])]
        scored = [(compare(target, candidate), candidate) for candidate in candidates]
        scored = sorted(scored, key=lambda item: ordering(item, target))
        pools.append(len(scored))
        folios.append(len({folio(candidate["page"]) for _, candidate in scored}))
        for rank, (distances, candidate) in enumerate(scored, 1):
            serial += 1
            rebuilt.append(output_row(serial, target, candidate, rank, len(scored), distances))
    compact = [row for row in rebuilt if int(row["candidate_rank"]) <= 3]
    assert tsv_bytes(rebuilt) == PRODUCER_TSV.read_bytes()
    assert tsv_bytes(compact) == PRODUCER_PACKET.read_bytes()

    expected_result = {
        "experiment": "CONSENSUS_STRUCTURAL_RECORD_ANALOG_INDEX_V1",
        "status": "PASS_DESCRIPTIVE_CROSS_FOLIO_ANALOG_INDEX",
        "decision": "RETAIN_TRANSPARENT_FORMAL_NEIGHBORS_FOR_HUMAN_INSPECTION_ONLY",
        "counts": {
            "source_records": len(records), "stable_prose_candidates": len(eligible),
            "targets": len(targets), "candidate_pairs": len(rebuilt), "packet_rows": len(compact),
            "minimum_candidate_pool": min(pools), "maximum_candidate_pool": max(pools),
            "minimum_candidate_folios": min(folios), "maximum_candidate_folios": max(folios),
            "same_section_pairs": sum(int(row["same_section"]) for row in rebuilt),
            "exact_structure_matches": sum(int(row["exact_structure_match"]) for row in rebuilt),
            "top_candidate_sections": dict(sorted(Counter(
                row["candidate_section"] for row in compact if int(row["candidate_rank"]) == 1
            ).items())),
        },
        "metric": {
            "candidate_pool": "same Currier + exact group count + different physical folio",
            "ranking": ["structure_distance", "family_distance", "sta_member_distance",
                        "favored_path_distance", "same_section_desc", "segment_id_utf8"],
            "top_neighbors_per_target": 3,
        },
        "inputs": {path.name: digest(path) for path in (SOURCE, SOURCE_VALIDATION, SPEC, BUILDER)},
        "outputs": {PRODUCER_TSV.name: digest(PRODUCER_TSV),
                    PRODUCER_PACKET.name: digest(PRODUCER_PACKET)},
        "english_glosses": 0,
        "claim_ceiling": (
            "Deterministic cross-folio formal-neighbor concordance only; no repeated sentence, "
            "parallel passage, referent, word, POS, morphology, sound, language, cipher, "
            "plaintext, meaning, or translation follows."
        ),
    }
    assert (json.dumps(expected_result, indent=2, sort_keys=True) + "\n").encode() == PRODUCER_JSON.read_bytes()
    assert report(expected_result).encode() == PRODUCER_REPORT.read_bytes()
    assert len(rebuilt) == 1078 and len(compact) == 78
    assert min(pools) == 10 and min(folios) == 8
    assert not any(int(row["exact_structure_match"]) for row in rebuilt)
    assert all(1 <= int(row["candidate_rank"]) <= int(row["candidate_pool_size"]) for row in rebuilt)
    assert all(folio(str(row["target_page"])) != folio(str(row["candidate_page"])) for row in rebuilt)
    assert all(row["target_currier"] == row["candidate_currier"] for row in rebuilt)
    assert all(row["target_group_count"] == int(records[int(row["candidate_record_order"]) - 1]["group_count"])
               for row in rebuilt)

    check_count = 10 + len(FROZEN) + len(records) + len(rebuilt) * len(COLUMNS) + len(compact)
    validation = {
        "experiment": "CONSENSUS_STRUCTURAL_RECORD_ANALOG_INDEX_V1_VALIDATION",
        "status": "PASS_INDEPENDENT_ANALOG_INDEX_RECONSTRUCTION",
        "validated_experiment": expected_result["experiment"],
        "check_count": check_count,
        "checks": [
            "frozen_source_and_producer_hashes", "source_validation_status",
            "independent_expression_parser", "independent_levenshtein_implementation",
            "exact_candidate_pool_and_folio_exclusion", "exact_rank_tuple",
            "full_tsv_byte_identity", "packet_tsv_byte_identity",
            "result_json_byte_identity", "report_byte_identity",
            "zero_exact_structure_matches", "zero_english_glosses",
        ],
        "discrepancies": [],
        "reconstructed_counts": expected_result["counts"],
        "source_result_sha256": digest(PRODUCER_JSON),
        "source_report_sha256": digest(PRODUCER_REPORT),
        "inputs": {path.name: digest(path) for path in FROZEN},
        "english_glosses": 0,
        "claim_ceiling": expected_result["claim_ceiling"],
    }
    validation_report = f"""# Consensus structural record analogue index validation

Status: **{validation['status']}**

An implementation that imports no production module independently rebuilt all
**{len(rebuilt):,}** target-candidate rows and the **{len(compact)}**-row
compact packet.  It reproduces both TSV files, the canonical result JSON, and
the report byte-for-byte in **{check_count:,}** checks.  Every candidate remains
on another physical folio with the target's exact Currier state and group
count; all **{len(targets)}** target rankings are reconstructed from the frozen
component distances.

The reconstruction confirms **0** exact surface-blind formal matches.  This is
an inspection concordance, not evidence of a parallel passage, referent, word,
part of speech, sound, language, cipher, plaintext, meaning, or translation.
"""
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(validation_report, encoding="utf-8")
    print(json.dumps(validation, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
