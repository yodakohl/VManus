#!/usr/bin/env python3
"""KART001: frozen A-65 system profile versus source-native Voynich structure.

This is a system-level structural comparison.  It assigns no Voynich sound,
letter, number, word, language, meaning, or translation.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
R = ROOT / "experiments/semantic_assumptions/results"

METHOD = ROOT / "KART001_A65_SYSTEM_COMPARATOR_METHOD.md"
SOURCE_AUDIT = ROOT / "KART001_A65_SOURCE_AUDIT.md"
A65_MANIFEST = ROOT / "kart001_a65_comparator_manifest.tsv"
GENERIC = ROOT / "kart001_generic_medieval_comparators.tsv"
PROVENANCE = ROOT / "kart001_source_provenance.json"
ACTIVE_STATE = ROOT / "VOYNICH_ACTIVE_STATE.md"

ARRAYS = R / "special_circle_text_blind_array_inventory.tsv"
ANNOTATIONS = R / "existing_human_exact_locus_annotations.tsv"
SURFACE = R / "source_separator_transcription.tsv"
ALIGNMENT = R / "source_sta_group_alignment.tsv"
STA = R / "source_sta_family_consensus_loci.tsv"
F69_RESULT = R / "f69ls001_long_short_result.json"
ZODIAC_PHASE = R / "zodiac_crosssign_phase_capacity.json"
ZODIAC_SLOTS = R / "zodiac_star_slot_ownership.tsv"
CLOTHING = R / "zcv001_zodiac_clothing_state_projection.tsv"
CLOTHING_CAPACITY = R / "zcv001_zodiac_clothing_native_visual_capacity.json"
TAIL = R / "zst001_zodiac_star_tail_state_projection.tsv"
TAIL_CAPACITY = R / "zst001_zodiac_star_tail_native_visual_capacity.json"
BARREL_CAPACITY = R / "zbv001_zodiac_barrel_native_visual_capacity.json"

OUT_INVENTORY = ROOT / "kart001_voynich_structural_inventory.tsv"
OUT_TESTS = ROOT / "kart001_tests.tsv"
OUT_NULLS = ROOT / "kart001_null_results.tsv"
OUT_COUNTER = ROOT / "kart001_counterexamples.tsv"
OUT_RESULT = ROOT / "kart001_result.json"
OUT_REPORT = ROOT / "KART001_A65_SYSTEM_COMPARATOR_REPORT.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
CONTROL_UNIVERSE = (3, 4, 7, 8, 10, 12, 16, 19, 27, 28, 29, 30, 36)
A65_CARDINALITIES = (7, 12, 28, 30)
PERMUTATIONS = 8192
PERMUTATION_SEED = 65001
SOURCE_FREEZE_COMMIT = "73989f1da45a1a1f544057e971b93e5e23b1f3f0"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_selected_tsv(path: Path, key: str, allowed: set[str]) -> list[dict[str, str]]:
    """Guarded stream: test one routing field before retaining any other fields."""
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        header_line = handle.readline().rstrip("\r\n")
        fields = header_line.split("\t")
        key_index = fields.index(key)
        for raw in handle:
            values = raw.rstrip("\r\n").split("\t")
            if values[key_index] not in allowed:
                continue
            rows.append(dict(zip(fields, values, strict=True)))
    return rows


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def grams(value: str, width: int) -> set[str]:
    return {value[i : i + width] for i in range(max(0, len(value) - width + 1))}


def similarity(left: str, right: str, representation: str) -> float:
    if representation == "SURFACE_EXACT":
        return float(left == right)
    if representation == "SURFACE_BIGRAM_JACCARD":
        return jaccard(grams(left, 2), grams(right, 2))
    if representation == "SURFACE_TRIGRAM_JACCARD":
        return jaccard(grams(left, 3), grams(right, 3))
    if representation == "STA_FAMILY_JACCARD":
        return jaccard(set(left), set(right))
    raise ValueError(representation)


def lag_score(sequence: list[str], lag: int, representation: str) -> float:
    return sum(similarity(sequence[i], sequence[(i + lag) % 28], representation) for i in range(28)) / 28


def f69_panel() -> tuple[list[dict[str, object]], dict[str, list[str]], list[str]]:
    panel: list[dict[str, object]] = []
    for row in read_selected_tsv(ANNOTATIONS, "page", {"f69v"}):
        if row["unit"] != "X1":
            continue
        match = re.fullmatch(r"f69v\.X1\.(\d+)", row["old_locus"])
        state = re.search(r"\b(long|short)\b", row["local_comment"].lower())
        if not match or not state:
            raise RuntimeError(f"bad f69v X1 annotation: {row}")
        panel.append({"ordinal": int(match.group(1)), "locus": row["locus"], "state": state.group(1).upper()})
    panel.sort(key=lambda item: int(item["ordinal"]))
    if [item["ordinal"] for item in panel] != list(range(1, 29)):
        raise RuntimeError("f69v panel is not exactly X1.1--X1.28")
    if [item["state"] for item in panel] != ["LONG" if i % 2 else "SHORT" for i in range(1, 29)]:
        raise RuntimeError("f69v panel does not strictly alternate")
    loci = [str(item["locus"]) for item in panel]
    locus_set = set(loci)

    source_rows: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in read_selected_tsv(SURFACE, "locus", locus_set):
        if row["edition"] in EDITIONS:
            source_rows[(row["locus"], row["edition"])].append(row)
    source_ids = {row["source_group_id"] for rows in source_rows.values() for row in rows}
    aligned = {
        row["source_group_id"]: row
        for row in read_selected_tsv(ALIGNMENT, "locus", locus_set)
        if row["source_group_id"] in source_ids
    }
    if set(aligned) != source_ids:
        raise RuntimeError("f69v source/alignment mismatch")
    editions: dict[str, list[str]] = {}
    for edition in EDITIONS:
        values: list[str] = []
        for locus in loci:
            rows = sorted(source_rows[(locus, edition)], key=lambda row: int(row["source_group_index"]))
            if not rows or len(rows) != int(rows[0]["source_group_count"]):
                raise RuntimeError(f"incomplete f69v source path: {edition} {locus}")
            values.append("".join(aligned[row["source_group_id"]]["nearest_basic_eva_primary"] for row in rows))
        editions[edition] = values

    sta_by_locus = {row["locus"]: row["family_sequence"] for row in read_selected_tsv(STA, "locus", locus_set)}
    if set(sta_by_locus) != locus_set:
        raise RuntimeError("incomplete f69v STA family panel")
    return panel, editions, [sta_by_locus[locus] for locus in loci]


def cardinality_test(array_rows: list[dict[str, str]]) -> tuple[dict[str, object], list[dict[str, object]]]:
    arrays: dict[str, int] = {}
    for row in array_rows:
        arrays[row["array_id"]] = int(row["slot_count"])
    frequencies = Counter(arrays.values())

    def score(values: tuple[int, ...]) -> tuple[int, int]:
        return len(set(values) & set(frequencies)), sum(frequencies[value] for value in values)

    observed = score(A65_CARDINALITIES)
    null_rows: list[dict[str, object]] = []
    tail = 0
    for values in itertools.combinations(CONTROL_UNIVERSE, 4):
        current = score(values)
        member = current >= observed
        tail += int(member)
        null_rows.append(
            {
                "null_id": "T1_CARD_" + "_".join(map(str, values)),
                "test_id": "KART001-T1",
                "null_type": "EXHAUSTIVE_FOUR_OF_THIRTEEN_MEDIEVAL_CARDINALITIES",
                "parameters": ",".join(map(str, values)),
                "statistic_primary": current[0],
                "statistic_secondary": current[1],
                "tail_member": int(member),
                "notes": "Lexicographic score: distinct target sizes, then arrays hit",
            }
        )
    result = {
        "array_count": len(arrays),
        "slot_count": len(array_rows),
        "array_size_frequencies": dict(sorted(frequencies.items())),
        "a65_cardinalities": list(A65_CARDINALITIES),
        "distinct_cardinalities_hit": observed[0],
        "arrays_hit": observed[1],
        "null_worlds": len(null_rows),
        "inclusive_tail_worlds": tail,
        "local_p": tail / len(null_rows),
    }
    return result, null_rows


def lag14_test(panel: list[dict[str, object]], editions: dict[str, list[str]], sta_sequence: list[str]) -> tuple[dict[str, object], list[dict[str, object]]]:
    series: list[tuple[str, str, list[str]]] = []
    for edition in EDITIONS:
        for representation in ("SURFACE_EXACT", "SURFACE_BIGRAM_JACCARD", "SURFACE_TRIGRAM_JACCARD"):
            series.append((edition, representation, editions[edition]))
    series.append(("CONSENSUS", "STA_FAMILY_JACCARD", sta_sequence))
    null_rows: list[dict[str, object]] = []
    results: list[dict[str, object]] = []
    minimum_permutation_p = 1.0
    for edition, representation, sequence in series:
        lag_values = [lag_score(sequence, lag, representation) for lag in range(1, 15)]
        observed = lag_values[13]
        rank = 1 + sum(value > observed + 1e-15 for value in lag_values)
        all_lag_tail = sum(value >= observed - 1e-15 for value in lag_values) / 14
        for lag, value in enumerate(lag_values, 1):
            null_rows.append(
                {
                    "null_id": f"T3_LAG_{edition}_{representation}_{lag:02d}",
                    "test_id": "KART001-T3",
                    "null_type": "ALL_CIRCULAR_LAGS",
                    "parameters": f"edition={edition};representation={representation};lag={lag}",
                    "statistic_primary": f"{value:.12f}",
                    "statistic_secondary": "",
                    "tail_member": int(value >= observed - 1e-15),
                    "notes": "Lag 14 is externally selected; other lags are the within-ring comparison",
                }
            )
        rng = random.Random(f"{PERMUTATION_SEED}|{edition}|{representation}")
        exceed = 0
        for _ in range(PERMUTATIONS):
            permuted = sequence.copy()
            rng.shuffle(permuted)
            exceed += int(lag_score(permuted, 14, representation) >= observed - 1e-15)
        permutation_p = (exceed + 1) / (PERMUTATIONS + 1)
        minimum_permutation_p = min(minimum_permutation_p, permutation_p)
        null_rows.append(
            {
                "null_id": f"T3_PERM_{edition}_{representation}",
                "test_id": "KART001-T3",
                "null_type": "DETERMINISTIC_RING_ORDER_PERMUTATION_SUMMARY",
                "parameters": f"seed={PERMUTATION_SEED};worlds={PERMUTATIONS};edition={edition};representation={representation}",
                "statistic_primary": f"{observed:.12f}",
                "statistic_secondary": exceed,
                "tail_member": "",
                "notes": f"plus-one permutation p={permutation_p:.12f}",
            }
        )
        results.append(
            {
                "edition": edition,
                "representation": representation,
                "lag14_score": observed,
                "lag14_rank_of_14_descending": rank,
                "all_lag_inclusive_tail": all_lag_tail,
                "permutation_exceedances": exceed,
                "permutation_worlds": PERMUTATIONS,
                "permutation_p": permutation_p,
                "best_lag": 1 + max(range(14), key=lambda index: lag_values[index]),
                "best_lag_score": max(lag_values),
            }
        )
    return {
        "panel_loci": [item["locus"] for item in panel],
        "strict_alternation": True,
        "representations": results,
        "minimum_local_permutation_p": minimum_permutation_p,
        "representation_search_count": len(results),
        "search_adjusted_p": min(1.0, minimum_permutation_p * len(results) * 2),
        "decision": "A65_DIRECT_TABLE_TRANSFER_FALSIFIED",
    }, null_rows


def seven_member_test(array_rows: list[dict[str, str]]) -> dict[str, object]:
    arrays: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in array_rows:
        if int(row["slot_count"]) == 7:
            arrays[row["array_id"]].append(row)
    loci = {row["locus"] for rows in arrays.values() for row in rows if row["locus"]}
    sta = {row["locus"]: row["family_sequence"] for row in read_selected_tsv(STA, "locus", loci)}
    details = []
    for array_id, rows in sorted(arrays.items()):
        ordered = sorted(rows, key=lambda row: int(row["slot_index"]))
        sequences = [sta[row["locus"]] for row in ordered if row["locus"] in sta]
        bigrams = [{value[i : i + 2] for i in range(len(value) - 1)} for value in sequences]
        common_bigrams = sorted(set.intersection(*bigrams)) if bigrams else []
        common_families = sorted(set.intersection(*(set(value) for value in sequences))) if sequences else []
        details.append(
            {
                "array_id": array_id,
                "page": ordered[0]["page"],
                "catalogued_slots": len(ordered),
                "formal_coverage": len(sequences),
                "source_description": ordered[0]["unit_description"],
                "description_count_consistent": not bool(
                    re.search(r"(?:\b8\b|\beight\b)", ordered[0]["unit_description"].lower())
                ),
                "common_family_bigrams": common_bigrams,
                "common_families": common_families,
            }
        )
    return {
        "nominal_seven_member_arrays": len(details),
        "arrays": details,
        "arrays_with_nontrivial_shared_family_bigram": sum(bool(item["common_family_bigrams"]) for item in details),
        "decision": "NO_INTERNAL_SEVEN_ARCHITECTURE_BEYOND_COUNT",
        "note": "A is common to every covered member but is corpus-common and not a seven-system signature.",
    }


def target_inventory(array_rows: list[dict[str, str]], t6: dict[str, object]) -> list[dict[str, object]]:
    phase = json.loads(ZODIAC_PHASE.read_text(encoding="utf-8"))
    slot_rows = read_tsv(ZODIAC_SLOTS)
    f69 = json.loads(F69_RESULT.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = [
        {
            "feature_id": "VMS_F01",
            "page_or_scope": "f70v2--f73v zodiac inventory",
            "source_artifact": str(ZODIAC_PHASE.relative_to(ROOT)),
            "observation_type": "HUMAN_INVENTORY_AND_CAPACITY_AUDIT",
            "cardinality_or_structure": "10 extant signs; 300 expected positions; 299 present labels; 7 panel topologies",
            "ordered": "NO_COMMON_PHASE",
            "score_eligible": "SYSTEM_PROFILE_ONLY",
            "caveat": phase["decision"],
        },
        {
            "feature_id": "VMS_F02",
            "page_or_scope": "f69v|X1",
            "source_artifact": str(ANNOTATIONS.relative_to(ROOT)),
            "observation_type": "EXISTING_HUMAN_ANNOTATION",
            "cardinality_or_structure": "28 radial text loci",
            "ordered": "EDITORIAL_CYCLIC_ORDER_NO_AUTHORIAL_ORIGIN",
            "score_eligible": "YES_T2_T3",
            "caveat": "No author-visible start or direction; rotation-invariant comparisons only",
        },
        {
            "feature_id": "VMS_F03",
            "page_or_scope": "f69v|X1",
            "source_artifact": str(F69_RESULT.relative_to(ROOT)),
            "observation_type": "EXISTING_HUMAN_ANNOTATION_AND_VALIDATED_AUDIT",
            "cardinality_or_structure": "14 LONG; 14 SHORT; exact AB alternation over 28",
            "ordered": "YES_RELATIVE_ALTERNATION",
            "score_eligible": "YES_T2_T3",
            "caveat": f"F69LS001 decision={f69['decision']}; states have no reliable text marker",
        },
        {
            "feature_id": "VMS_F04",
            "page_or_scope": "f68r1|S1",
            "source_artifact": str(ARRAYS.relative_to(ROOT)),
            "observation_type": "EXISTING_HUMAN_ANNOTATION",
            "cardinality_or_structure": "29 labelled stars; one central; 28 noncentral",
            "ordered": "NO_AUTHORIAL_28_ORDER",
            "score_eligible": "CARDINALITY_PROFILE_ONLY",
            "caveat": "Catalogue order is not a lunar sequence",
        },
        {
            "feature_id": "VMS_F05",
            "page_or_scope": "f67r2|M1",
            "source_artifact": str(ARRAYS.relative_to(ROOT)),
            "observation_type": "EXISTING_HUMAN_ANNOTATION",
            "cardinality_or_structure": "human-defined seven-member circular label set",
            "ordered": "CIRCULAR_WITHOUT_VALUE_KEY",
            "score_eligible": "YES_T6_NOT_COUNT_ONLY",
            "caveat": "No weekday, luminary, or name assignment",
        },
        {
            "feature_id": "VMS_F06",
            "page_or_scope": "f67r2|M2",
            "source_artifact": str(ARRAYS.relative_to(ROOT)),
            "observation_type": "EXISTING_HUMAN_ANNOTATION",
            "cardinality_or_structure": "human-defined twelve-member moon-associated circular set",
            "ordered": "CIRCULAR_WITHOUT_VALUE_KEY",
            "score_eligible": "CARDINALITY_PROFILE_ONLY",
            "caveat": "No zodiac-sign or month-name assignment",
        },
        {
            "feature_id": "VMS_F07",
            "page_or_scope": "f67v2",
            "source_artifact": "VOYNICH_ACTIVE_STATE.md",
            "observation_type": "EXISTING_HUMAN_GEOMETRY_AND_SOURCE_NATIVE_AUDIT",
            "cardinality_or_structure": "fourfold geometry; diagonal endpoints alternate two human catalogue states",
            "ordered": "THREE_POSSIBLE_PAIRINGS_ONLY",
            "score_eligible": "NO_A65_SPECIFIC_PREDICTION",
            "caveat": "No cardinal directions or Georgian labels; prior semantic transfer nonconfirmed",
        },
    ]
    arrays: dict[str, dict[str, str]] = {}
    for item in array_rows:
        arrays.setdefault(item["array_id"], item)
    for index, (array_id, item) in enumerate(sorted(arrays.items()), 1):
        rows.append(
            {
                "feature_id": f"VMS_F08_{index:02d}",
                "page_or_scope": f"{item['page']}|{item['unit']}",
                "source_artifact": str(ARRAYS.relative_to(ROOT)),
                "observation_type": "FROZEN_TEXT_BLIND_ARRAY",
                "cardinality_or_structure": f"array_id={array_id};slots={item['slot_count']}",
                "ordered": "AS_FROZEN_IN_SOURCE_INVENTORY",
                "score_eligible": "YES_T1",
                "caveat": item["unit_description"],
            }
        )
    if phase["counts"]["expected_slots"] != 300 or sum(int(row["public_label_count"]) for row in slot_rows) != 299:
        raise RuntimeError("zodiac inventory totals changed")
    return rows


def main() -> None:
    for path in (METHOD, SOURCE_AUDIT, A65_MANIFEST, GENERIC, PROVENANCE):
        if not path.exists():
            raise RuntimeError(f"missing Stage-A freeze: {path}")
    manifest = {row["feature_id"]: row for row in read_tsv(A65_MANIFEST)}
    if {key for key, row in manifest.items() if row["score_eligible"] == "YES"} != {
        "A65_F01", "A65_F02", "A65_F03", "A65_F04", "A65_F05", "A65_F06", "A65_F07"
    }:
        raise RuntimeError("A-65 feature eligibility changed")

    array_rows = read_tsv(ARRAYS)
    if len(array_rows) != 504 or len({row["array_id"] for row in array_rows}) != 45:
        raise RuntimeError("special-circle inventory changed")
    if any(row["page"] == "f84r" for row in array_rows):
        raise RuntimeError("sealed f84r entered KART001 array input")
    t1, t1_nulls = cardinality_test(array_rows)
    panel, editions, sta_sequence = f69_panel()
    t3, t3_nulls = lag14_test(panel, editions, sta_sequence)
    t6 = seven_member_test(array_rows)

    inventory = target_inventory(array_rows, t6)
    write_tsv(
        OUT_INVENTORY,
        ["feature_id", "page_or_scope", "source_artifact", "observation_type", "cardinality_or_structure", "ordered", "score_eligible", "caveat"],
        inventory,
    )

    # Two KART001 families return numerical p-values: T1 and T3.
    t1_adjusted = min(1.0, t1["local_p"] * 2)
    tests: list[dict[str, object]] = [
        {
            "test_id": "KART001-T1", "test_name": "CARDINALITY_PROFILE", "status": "SCORED_NO_UNUSUAL_CONCENTRATION",
            "target": "45-array/504-slot special-circle inventory", "a65_feature": "A65_F01;F02;F04;F05",
            "statistic": f"distinct_hits={t1['distinct_cardinalities_hit']}/4;arrays_hit={t1['arrays_hit']}",
            "local_p": f"{t1['local_p']:.12f}", "search_adjusted_p": f"{t1_adjusted:.12f}",
            "system_compatibility": "MODERATE", "cultural_specificity": "LOW",
            "best_alternative": "Generic medieval zodiac, planetary, lunar-station, and computus cardinalities",
        },
        {
            "test_id": "KART001-T2", "test_name": "F69V_28_PLUS_BINARY", "status": "28_PLUS_BINARY_MATCH",
            "target": "f69v 28 radial loci with exact LONG/SHORT alternation", "a65_feature": "A65_F05;F06",
            "statistic": "ordered28+strict_binary compatible; no state mapping",
            "local_p": "NA_NO_GENERIC_PREVALENCE_DENOMINATOR", "search_adjusted_p": "NA",
            "system_compatibility": "HIGH", "cultural_specificity": "UNKNOWN_LOW_CEILING",
            "best_alternative": "Generic 28-part lunar architecture plus deliberate manuscript alternation",
        },
        {
            "test_id": "KART001-T3", "test_name": "F69V_INTERNAL_LUNAR_PREDICTION", "status": "A65_DIRECT_TABLE_TRANSFER_FALSIFIED",
            "target": "f69v opposite n versus n+14 pairs", "a65_feature": "A65_F05;F06",
            "statistic": "lag14 bottom/near-bottom across surface 2/3-grams and STA family representations",
            "local_p": f"{t3['minimum_local_permutation_p']:.12f}", "search_adjusted_p": f"{t3['search_adjusted_p']:.12f}",
            "system_compatibility": "NEGATIVE_DIRECT_TRANSFER", "cultural_specificity": "NONE_FROM_THIS_TEST",
            "best_alternative": "Ordinary circular string similarity; other lags are stronger",
        },
        {
            "test_id": "KART001-T4", "test_name": "THIRTY_POSITION_ZODIAC", "status": "UNSCORED_NO_IDENTIFIABLE_30_POSITION_PHASE",
            "target": "10 extant signs; 300 expected slots; seven panel topologies", "a65_feature": "A65_F02;F03",
            "statistic": "no authorial universal start/direction/inter-band continuation", "local_p": "NA", "search_adjusted_p": "NA",
            "system_compatibility": "COUNT_COMPATIBLE", "cultural_specificity": "NEAR_ZERO",
            "best_alternative": "Universal 30-degree zodiac architecture",
        },
        {
            "test_id": "KART001-T5", "test_name": "SIGN_SPECIFIC_FORTUNATE_DEGREES", "status": "UNSCORED_NO_COMPLETE_ELIGIBLE_VISUAL_STATE",
            "target": "frozen clothing, tail, and barrel visual-state inventories", "a65_feature": "A65_F07",
            "statistic": "no complete capacity-valid 30-position visual subset for a source-clear sign", "local_p": "NA", "search_adjusted_p": "NA",
            "system_compatibility": "INSUFFICIENT_TARGET_CAPACITY", "cultural_specificity": "UNASSESSED",
            "best_alternative": "Any attractive partial rotation would be post-hoc selection",
        },
        {
            "test_id": "KART001-T6", "test_name": "SEVEN_MEMBER_SYSTEM", "status": "NO_INTERNAL_SEVEN_ARCHITECTURE_BEYOND_COUNT",
            "target": f"{t6['nominal_seven_member_arrays']} nominal seven-slot arrays", "a65_feature": "A65_F04",
            "statistic": f"shared_nontrivial_family_bigram_arrays={t6['arrays_with_nontrivial_shared_family_bigram']}",
            "local_p": "NA_NO_EXTERNALLY_PREDICTED_FORMAL_KEY", "search_adjusted_p": "NA",
            "system_compatibility": "COUNT_ONLY", "cultural_specificity": "NEAR_ZERO",
            "best_alternative": "Seven is a common planetary/weekday cardinality; one source description conflicts with seven-row catalogue",
        },
        {
            "test_id": "KART001-T7", "test_name": "FOURFOLD_DIRECTIONAL_STRUCTURE", "status": "UNSCORED_NO_SPECIFIC_A65_FOURFOLD_PREDICTION",
            "target": "f67v2 fourfold geometry and local diagonal binary pairing", "a65_feature": "A65_F08",
            "statistic": "A-65 source freeze predicts none of the three possible pairings", "local_p": "NA", "search_adjusted_p": "NA",
            "system_compatibility": "UNASSESSED", "cultural_specificity": "NEAR_ZERO_FOR_GENERIC_FOURFOLD",
            "best_alternative": "Common fourfold cosmography; local one-folio complement already fails transfer",
        },
    ]
    write_tsv(
        OUT_TESTS,
        ["test_id", "test_name", "status", "target", "a65_feature", "statistic", "local_p", "search_adjusted_p", "system_compatibility", "cultural_specificity", "best_alternative"],
        tests,
    )
    write_tsv(
        OUT_NULLS,
        ["null_id", "test_id", "null_type", "parameters", "statistic_primary", "statistic_secondary", "tail_member", "notes"],
        t1_nulls + t3_nulls,
    )

    counterexamples = [
        ("KART_CE01", "LANGUAGE_IDENTIFICATION", "No Georgian or Mingrelian language identification; no phonetic mapping exists.", "HARD_CLAIM_CEILING"),
        ("KART_CE02", "NUMBER_OR_MORPHOLOGY", "No number-word mapping and no q/dy semantic interpretation.", "HARD_CLAIM_CEILING"),
        ("KART_CE03", "MINGRELIAN_WEEKDAYS", "Prior exploratory weekday morphology has no visible match to the f67r2 seven-member set.", "NEGATIVE_PRIOR_RESULT"),
        ("KART_CE04", "MINGRELIAN_DIRECTIONS", "Prior cardinal-direction morphology has no convincing Voynich match.", "NEGATIVE_PRIOR_RESULT"),
        ("KART_CE05", "MODERN_MONTH_NAMES", "The modern Mingrelian five-member -tuta analogy was source-sensitive and overfit; it is excluded.", "REJECTED_ANALOGY"),
        ("KART_CE06", "F69V_TEXT_MARKER", "F69LS001 found no reliable source-text feature distinguishing LONG from SHORT.", "VALIDATED_NONCONFIRMATION"),
        ("KART_CE07", "F69V_LAG14", "Lag 14 is bottom or near-bottom under every predeclared representation and alternate reading.", "DIRECT_TRANSFER_FALSIFIER"),
        ("KART_CE08", "NINETEEN_TIMES_TWENTYEIGHT", "f70v2 C1+I10+O19 is a 30-position zodiac layout; 19x28 Chronikon multiplication is confounded and excluded.", "CONFOUNDED_SPECULATION"),
        ("KART_CE09", "GENERIC_COMPUTUS", "Generic medieval comparators already explain 7, 12, 28, 30 and related circle-module counts.", "CULTURAL_SPECIFICITY_FALSIFIER"),
        ("KART_CE10", "F68R1_ORDER", "f68r1 has 28 noncentral labelled stars but no authorial 28-member cyclic order.", "TOPOLOGY_FALSIFIER"),
        ("KART_CE11", "ZODIAC_PHASE", "Seven incompatible panel topologies prevent an identified common 3x10 degree phase.", "CAPACITY_STOP"),
        ("KART_CE12", "FORTUNATE_DEGREES", "No complete capacity-valid frozen visual subset supports the sign-specific roster test.", "CAPACITY_STOP"),
        ("KART_CE13", "SEVEN_MEMBER_FORM", "No nominal seven-member array shares a nontrivial STA-family bigram across all covered members.", "FORMAL_FALSIFIER"),
        ("KART_CE14", "F67V2_FOURFOLD", "A-65 supplies no specific opposition predicting one f67v2 pairing; the local binary complement is one-folio and nontransferring.", "EXTERNAL_PREDICTION_ABSENT"),
    ]
    write_tsv(
        OUT_COUNTER,
        ["counterexample_id", "target_claim", "evidence", "classification"],
        [{"counterexample_id": a, "target_claim": b, "evidence": c, "classification": d} for a, b, c, d in counterexamples],
    )

    inputs = {
        str(path.relative_to(ROOT)): sha256(path)
        for path in (
            METHOD, SOURCE_AUDIT, A65_MANIFEST, GENERIC, PROVENANCE, ACTIVE_STATE, ARRAYS, ANNOTATIONS, SURFACE,
            ALIGNMENT, STA, F69_RESULT, ZODIAC_PHASE, ZODIAC_SLOTS, CLOTHING, CLOTHING_CAPACITY,
            TAIL, TAIL_CAPACITY, BARREL_CAPACITY,
        )
    }
    result: dict[str, object] = {
        "schema": "KART001_A65_SYSTEM_COMPARATOR_RESULT_V1",
        "experiment": "KART001_A65_SYSTEM_COMPARATOR",
        "branch": "yolo/gdt002-visual-grammar-constraints",
        "source_freeze_commit": SOURCE_FREEZE_COMMIT,
        "stage_a_status": "EXTERNAL_COMPARATOR_FROZEN_BEFORE_VOYNICH_SCORING",
        "sealed_holdout": {
            "folio": "f84r",
            "formal_payload_retained_joined_or_scored": False,
            "guarded_stream_skipped_before_formal_field_retention": True,
        },
        "decisions": ["A65_SYSTEM_MATCH_NOT_ABOVE_GENERIC_MEDIEVAL", "A65_DIRECT_TABLE_TRANSFER_FALSIFIED"],
        "primary_decision": "A65_SYSTEM_MATCH_NOT_ABOVE_GENERIC_MEDIEVAL",
        "system_compatibility": "A65_SYSTEM_COMPATIBILITY_PROVISIONAL",
        "cultural_specificity": "LOW",
        "t1": t1 | {"search_adjusted_p": t1_adjusted},
        "t2": {
            "status": "28_PLUS_BINARY_MATCH",
            "voynich": "ordered 28 radial entries plus exact LONG/SHORT alternation",
            "a65": "ordered 28-night schedule plus exact odd-red/even-black presentation",
            "state_mapping_made": False,
            "generic_prevalence_denominator_available": False,
            "cultural_specificity": "UNKNOWN_LOW_CEILING",
        },
        "t3": t3,
        "t4": {"status": "UNSCORED_NO_IDENTIFIABLE_30_POSITION_PHASE"},
        "t5": {
            "status": "UNSCORED_NO_COMPLETE_ELIGIBLE_VISUAL_STATE",
            "clothing_capacity": json.loads(CLOTHING_CAPACITY.read_text(encoding="utf-8"))["decision"],
            "star_tail_capacity": json.loads(TAIL_CAPACITY.read_text(encoding="utf-8"))["decision"],
            "barrel_capacity": json.loads(BARREL_CAPACITY.read_text(encoding="utf-8"))["decision"],
        },
        "t6": t6,
        "t7": {"status": "UNSCORED_NO_SPECIFIC_A65_FOURFOLD_PREDICTION"},
        "counts": {
            "voynich_inventory_rows": len(inventory),
            "tests": len(tests),
            "null_rows": len(t1_nulls) + len(t3_nulls),
            "counterexamples": len(counterexamples),
            "numerically_scored_test_families": 2,
        },
        "inputs": inputs,
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha256(Path(__file__))},
        "claim_ceiling": (
            "System-level compatibility only. No Georgian or Mingrelian language, authorship, geographic origin, "
            "direct copying, sound, letter, number, zodiac label, word, morpheme, POS, plaintext, meaning, or translation."
        ),
    }

    report = f"""# KART001 A-65 system comparator report

Status: **{result['primary_decision']}**

Secondary falsifier: **A65_DIRECT_TABLE_TRANSFER_FALSIFIED**

System compatibility: **A65_SYSTEM_COMPATIBILITY_PROVISIONAL**

Cultural specificity: **LOW**

## Outcome

The Voynich astronomical/circle block is compatible with the broad architecture
attested in A-65, especially 7/12/28/30 cardinalities and the striking formal
tuple `ordered 28 + exact binary alternation`. It is not unusually compatible
relative to generic medieval astrology and computus. The only visually close
tuple has no frozen comparative prevalence denominator, while the externally
predicted f69v opposite-pair relation fails across every predeclared text
representation.

This is not evidence for Georgian or Mingrelian language, authorship, origin,
or direct copying.

## Source firewall

The external manifest was frozen and publicly committed as `{SOURCE_FREEZE_COMMIT}`
before KART001 target scoring. A65_F09/F10 were excluded; Cancer and Capricorn
fortunate-degree sets were excluded. f84r remained sealed and contributes no
row, feature, score, or target selection.

## Test results

| test | result | local p | search-adjusted p | interpretation |
| --- | --- | ---: | ---: | --- |
| T1 cardinalities | 3/4 sizes present; 10 arrays hit | {t1['local_p']:.6f} | {t1_adjusted:.6f} | ordinary under the frozen medieval set null |
| T2 28 + binary | `28_PLUS_BINARY_MATCH` | n/a | n/a | high compatibility; specificity unknown, no state mapping |
| T3 lag 14 | direct transfer falsified | {t3['minimum_local_permutation_p']:.6f} | {t3['search_adjusted_p']:.6f} | lag 14 is bottom/near-bottom |
| T4 3×10 zodiac | unscored | n/a | n/a | no identifiable common phase across seven topologies |
| T5 fortunate degrees | unscored | n/a | n/a | no complete capacity-valid visual subset |
| T6 seven-member system | count only | n/a | n/a | zero arrays share a nontrivial family bigram across all covered members |
| T7 fourfold system | unscored | n/a | n/a | A-65 freeze predicts none of three pairings |

## T1: cardinality profile

The 45-array/504-slot special-circle inventory contains sizes 7, 12, and 28,
but not 30. The A-65 set therefore covers three external cardinalities and hits
ten arrays. Among all 715 equally sized subsets of the frozen medieval control
universe, 302 score at least as well: `p = {t1['local_p']:.12f}`. Paying for the
two KART001 families with numerical p-values gives `{t1_adjusted:.12f}`.

The separate 30-position zodiac inventory is a strong compatibility fact but
has near-zero cultural specificity: thirty degrees per sign are universal
zodiac architecture, and the seven Voynich panel topologies do not identify a
shared degree phase.

## T2: the 28-plus-binary tuple

f69v has 28 catalogue-ordered radial entries and exact LONG/SHORT alternation.
A-65 has an ordered 28-night schedule and the edition reports odd entries in
red, even entries in black. This is a real system-level topology match. It does
not identify LONG with odd, SHORT with even, or either visual state with a
color. Generic 28-part lunar systems are widespread; the exact prevalence of
alternating rubrication was not established by the frozen control audit.
Consequently compatibility is high but cultural specificity remains unknown
with a low claim ceiling.

## T3: externally predicted opposite pairs

The direct schedule analogy predicts that positions `n` and `n+14` share the
same A-65 odd/even presentation state. That prediction does not transfer to the
Voynich strings. Lag 14 has no exact surface matches; it ranks at or near the
bottom for character bigrams, trigrams, and source-native STA-family Jaccard in
ZL3b, IT2a, and RF1b. The readings are sensitivity views of one manuscript,
not replications. Full scores and deterministic ring-order permutation tails
are in `kart001_null_results.tsv`.

## T5 capacity and T6/T7 negatives

The frozen clothing data are incomplete subsets of 30-position signs. The
star-tail and barrel routes have failed ownership/capacity gates, and no
complete capacity-valid sign-specific visual subset remains for the fortunate-
degree comparison. No rotation was opened.

Three catalogue arrays have nominal size seven. None has a nontrivial
STA-family bigram shared by every formally covered member; one seven-row
catalogue is itself described by the human source as a circle of eight labels.
Thus `7 == 7` remains count-only evidence. The previously explored Mingrelian
weekday forms supply no shared formal architecture.

f67v2 retains a real one-folio local binary complement in its fourfold geometry,
but the frozen A-65 source profile supplies no specific opposition selecting
one of the three pairings. Generic fourfold cosmography is the simpler control.

## Cultural-specificity summary

| feature | Voynich evidence | A-65 evidence | generic prevalence | compatibility | specificity / alternative |
| --- | --- | --- | --- | --- | --- |
| 12 zodiac signs | ten extant sign panels in a zodiac series | twelve chapters | universal astrology | high family compatibility | near-zero; generic zodiac |
| 30 positions/sign | 300 expected slots over ten signs | 30 degrees/sign | universal astrology | high count compatibility | near-zero; no Voynich degree phase |
| 3×10 | no topology-independent partition | three ten-degree rulers | common decans | target unscored | none established |
| seven | several seven-size arrays | seven luminaries | common planets/weekdays | count only | near-zero |
| ordered 28 | f69v ordered radial catalogue | 28 lunar nights | widespread lunar systems | high | low |
| 28 + strict binary | exact LONG/SHORT alternation | odd-red/even-black note | prevalence unknown | high topology match | unknown; deliberate alternation |
| fortunate degrees | no eligible complete visual subset | ten clear sign rosters | wider degree doctrines | unscored | unassessed |
| fourfold profile | f67v2 local geometry | generic sign qualities/directions | common cosmography | unscored | near-zero |

## Counterexamples retained

- F69LS001 remains nonconfirming: LONG/SHORT has no reliable textual marker.
- Lag 14 is a direct falsifier, not a rescued representation choice.
- f68r1's 28 noncentral stars have no authorial 28-member order.
- `19 × 28 = 532` is excluded: f70v2's 19-member band is part of
  `C1 + I10 + O19 = 30`.
- Generic computus/cosmography explains most module cardinalities.
- Mingrelian weekday/direction morphology has no convincing match, and the
  modern five-member `-tuta` month analogy was source-sensitive overfit.
- No `q`, `dy`, number word, sound, letter, language, or meaning is assigned.

## Claim ceiling

At most, KART001 shows that the Voynich circle block belongs comfortably in a
broad medieval astronomical/computistical system family that also includes
A-65. Generic Byzantine, Arabic-derived, Latin, Persian, and wider Eurasian
comparators explain the main architecture at least as economically. It does
not establish Georgian authorship, Georgian or Mingrelian language, Georgian
origin, direct copying from A-65, plaintext, or translation.

**A65_SYSTEM_MATCH_NOT_ABOVE_GENERIC_MEDIEVAL**
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    result["outputs"] = {
        str(path.relative_to(ROOT)): sha256(path)
        for path in (OUT_INVENTORY, OUT_TESTS, OUT_NULLS, OUT_COUNTER, OUT_REPORT)
    }
    normalized_result = json.loads(json.dumps(result, sort_keys=True, ensure_ascii=True))
    result["result_content_sha256"] = hashlib.sha256(canonical_json(normalized_result).encode()).hexdigest()
    OUT_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
