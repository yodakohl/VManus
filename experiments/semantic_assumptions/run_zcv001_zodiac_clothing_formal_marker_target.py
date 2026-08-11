#!/usr/bin/env python3
"""Run the frozen ZCV001 clothing-state formal-marker target once."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "ZCV001_ZODIAC_CLOTHING_FORMAL_MARKER_TARGET_SPEC.md"
PANEL = RESULTS / "zcv001_zodiac_clothing_state_projection.tsv"
CAPACITY = RESULTS / "zcv001_zodiac_clothing_native_visual_capacity.json"
CAPACITY_VALIDATION = RESULTS / "zcv001_zodiac_clothing_native_visual_capacity_validation.json"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
GROUP_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
OUT = RESULTS / "zcv001_zodiac_clothing_formal_marker_target.json"
REPORT = RESULTS / "zcv001_zodiac_clothing_formal_marker_target_report.md"

EXPECTED = {
    SPEC: "89046a228a15a6aa4e9c8050c9915f42395a014d2aa004df6d0d0e041deb7079",
    PANEL: "d1f74428e16e0674aad9e997df884067f8b778f31927d061b1def0a715c9ad68",
    CAPACITY: "a55b532b57e3c582a5da55ec782bb7f5f6df1eaa7e6b5204b67111dc6c887455",
    CAPACITY_VALIDATION: "b2ce7bc0e1391142fb92954d58423bb573083660322ccc5d04b9c9395b2cbd76",
    CROSSWALK: "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    GROUP_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
}
FEATURE_SHA = "e395dd0228fb8ad018dce53a5089892cec02af0267ce5751be556e03c269f05e"
STRATUM_ORDER = ("f71r|INNER", "f71v|OUTER", "f72r1|INNER", "f72r2|OUTER")
EXPECTED_NONSTRICT = {"STOLFI_BEST_0599", "STOLFI_BEST_0601"}
MEDIUM_NATIVE = {"STOLFI_BEST_0536", "STOLFI_BEST_0597"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def feature_hash(values: list[str]) -> str:
    return hashlib.sha256("".join(value + "\n" for value in values).encode()).hexdigest()


def group_features(row: dict[str, str]) -> set[str]:
    result: set[str] = set()
    family = row["family_surface"]
    for n in (1, 2, 3):
        result.update(f"F:N:{n}:{family[i:i+n]}" for i in range(len(family) - n + 1))
        if len(family) >= n:
            result.update((f"F:P:{n}:{family[:n]}", f"F:S:{n}:{family[-n:]}"))
    result.add("F:W:" + family)
    sequences = [row[key].split() for key in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
    if sequences[0] == sequences[1] == sequences[2]:
        sequence = sequences[0]
        for n in (1, 2, 3):
            result.update(
                f"M:N:{n}:{' '.join(sequence[i:i+n])}" for i in range(len(sequence) - n + 1)
            )
            if len(sequence) >= n:
                result.update(
                    (
                        f"M:P:{n}:{' '.join(sequence[:n])}",
                        f"M:S:{n}:{' '.join(sequence[-n:])}",
                    )
                )
        result.add("M:W:" + " ".join(sequence))
    return result


def reconstruct() -> tuple[
    list[dict[str, str]],
    dict[str, list[dict[str, str]]],
    dict[str, set[str]],
    list[str],
    dict[str, str],
]:
    panel = rows(PANEL)
    cross = {row["source_record_id"]: row for row in rows(CROSSWALK)}
    lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows(GROUPS):
        lookup[row["locus"]].append(row)
    strict: list[dict[str, str]] = []
    features: dict[str, set[str]] = {}
    excluded: dict[str, str] = {}
    for state in panel:
        link = cross.get(state["source_record_id"])
        if (
            link is None
            or link["primary_eligible"] != "1"
            or not link["current_locus"]
            or link["current_page"] != state["page"]
            or link["position_key"] != f"{state['ring']}:GROVE_{state['grove_number']}"
        ):
            excluded[state["source_record_id"]] = "CROSSWALK_NOT_STRICT"
            continue
        groups = sorted(
            lookup.get(link["current_locus"], ()), key=lambda row: int(row["consensus_group_index"])
        )
        if not groups:
            excluded[state["source_record_id"]] = "NO_CONSENSUS"
            continue
        valid = (
            all(
                group["page"] == state["page"]
                and group["kind"] == "L"
                and group["grammar_scope"] == "DIAGNOSTIC_NONPROSE"
                and group["strict_zero_alternative"] == "1"
                and group["family_surface"]
                for group in groups
            )
            and [int(group["consensus_group_index"]) for group in groups]
            == list(range(1, len(groups) + 1))
            and {int(group["consensus_group_count"]) for group in groups} == {len(groups)}
        )
        if not valid:
            excluded[state["source_record_id"]] = "NONSTRICT_CONSENSUS"
            continue
        strict.append(state)
        features[state["source_record_id"]] = set().union(*(group_features(group) for group in groups))
    strata: dict[str, list[dict[str, str]]] = defaultdict(list)
    for state in strict:
        strata[f"{state['page']}|{state['ring']}"].append(state)
    for values in strata.values():
        values.sort(key=lambda row: int(row["grove_number"]))
    universe = sorted(set().union(*features.values()), key=lambda term: term.encode())
    vocabulary = [
        term
        for term in universe
        if sum(term in item for item in features.values()) >= 4
        and all(
            0 < sum(term in features[state["source_record_id"]] for state in strata[key]) < len(strata[key])
            for key in STRATUM_ORDER
        )
    ]
    return strict, strata, features, vocabulary, excluded


def rotate_assignments(strata: dict[str, list[dict[str, str]]], shifts: tuple[int, ...]) -> dict[str, str]:
    assigned: dict[str, str] = {}
    for key, shift in zip(STRATUM_ORDER, shifts, strict=True):
        values = strata[key]
        original = [row["clothing_state"] for row in values]
        for index, row in enumerate(values):
            assigned[row["source_record_id"]] = original[(index - shift) % len(values)]
    return assigned


def delta(
    feature: str,
    values: list[dict[str, str]],
    features: dict[str, set[str]],
    assignments: dict[str, str],
    excluded_ids: set[str] | None = None,
) -> float:
    excluded_ids = excluded_ids or set()
    dressed = [
        int(feature in features[row["source_record_id"]])
        for row in values
        if row["source_record_id"] not in excluded_ids
        and assignments[row["source_record_id"]] == "DRESSED"
    ]
    undressed = [
        int(feature in features[row["source_record_id"]])
        for row in values
        if row["source_record_id"] not in excluded_ids
        and assignments[row["source_record_id"]] == "UNDRESSED"
    ]
    if not dressed or not undressed:
        raise AssertionError("empty state margin")
    return sum(dressed) / len(dressed) - sum(undressed) / len(undressed)


def score_feature(
    feature: str,
    strata: dict[str, list[dict[str, str]]],
    features: dict[str, set[str]],
    assignments: dict[str, str],
) -> tuple[float, float, dict[str, float], dict[str, float]]:
    per_stratum = {key: delta(feature, strata[key], features, assignments) for key in STRATUM_ORDER}
    per_folio = {
        "f71": (per_stratum["f71r|INNER"] + per_stratum["f71v|OUTER"]) / 2,
        "f72": (per_stratum["f72r1|INNER"] + per_stratum["f72r2|OUTER"]) / 2,
    }
    return min(per_folio.values()), sum(per_folio.values()) / 2, per_folio, per_stratum


def select(
    vocabulary: list[str],
    strata: dict[str, list[dict[str, str]]],
    features: dict[str, set[str]],
    assignments: dict[str, str],
) -> tuple[float, float, str, dict[str, float], dict[str, float]]:
    scored = []
    for feature in vocabulary:
        score, mean_score, folio, stratum = score_feature(feature, strata, features, assignments)
        scored.append((score, mean_score, feature, folio, stratum))
    return min(scored, key=lambda value: (-value[0], -value[1], value[2].encode()))


def report(result: dict[str, object]) -> str:
    if result["decision"] == "STOP_UNPOWERED_BEFORE_CLOTHING_ASSOCIATION_SCORE":
        return (
            "# ZCV001 zodiac clothing-state formal-marker target\n\n"
            "Status: **STOP_UNPOWERED_BEFORE_CLOTHING_ASSOCIATION_SCORE**\n\n"
            "The frozen source or capacity contract failed. No clothing-state association was scored.\n"
        )
    target = result["target"]
    assert isinstance(target, dict)
    return (
        "# ZCV001 zodiac clothing-state formal-marker target\n\n"
        f"Status: **{result['decision']}**\n\n"
        f"The frozen winner is `{target['winning_feature']}` with physical-folio effects "
        f"f71={target['folio_effects']['f71']:.6f} and f72={target['folio_effects']['f72']:.6f}; "
        f"its minimum score is **{target['winning_score']:.6f}**. The inclusive exact cyclic "
        f"max-feature p-value is **{target['exact_p']:.6f}** "
        f"({target['inclusive_tail_count']}/3250).\n\n"
        f"Decision: **{result['decision']}**.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n"
    )


def write_once(path: Path, content: str) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        handle.write(content)


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"input hash mismatch: {path}")
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    capacity_validation = json.loads(CAPACITY_VALIDATION.read_text(encoding="utf-8"))
    group_validation = json.loads(GROUP_VALIDATION.read_text(encoding="utf-8"))
    strict, strata, features, vocabulary, excluded = reconstruct()
    state_counts = Counter(row["clothing_state"] for row in strict)
    stratum_counts = {
        key: Counter(row["clothing_state"] for row in strata[key]) for key in STRATUM_ORDER
    }
    cyclic_worlds = math.prod(len(strata[key]) for key in STRATUM_ORDER)
    capacity_pass = (
        capacity.get("decision") == "PASS_UNSCORED_CLOTHING_CONTRAST_CAPACITY"
        and capacity_validation.get("status") == "PASS_INDEPENDENT_SCORE_BLIND_CAPACITY_RECONSTRUCTION"
        and str(group_validation.get("status", "")).startswith("PASS")
        and len(strict) == 33
        and set(excluded) == EXPECTED_NONSTRICT
        and tuple(strata) == STRATUM_ORDER
        and [len(strata[key]) for key in STRATUM_ORDER] == [5, 10, 5, 13]
        and state_counts == Counter({"UNDRESSED": 15, "DRESSED": 14, "UNCERTAIN": 4})
        and stratum_counts
        == {
            "f71r|INNER": Counter({"DRESSED": 4, "UNDRESSED": 1}),
            "f71v|OUTER": Counter({"DRESSED": 7, "UNDRESSED": 2, "UNCERTAIN": 1}),
            "f72r1|INNER": Counter({"UNDRESSED": 3, "DRESSED": 1, "UNCERTAIN": 1}),
            "f72r2|OUTER": Counter({"UNDRESSED": 9, "DRESSED": 2, "UNCERTAIN": 2}),
        }
        and len(set().union(*features.values())) == 398
        and len(vocabulary) == 37
        and feature_hash(vocabulary) == FEATURE_SHA
        and cyclic_worlds == 3250
    )
    common = {
        "experiment": "ZCV001_ZODIAC_CLOTHING_FORMAL_MARKER_TARGET",
        "inputs": {str(path.relative_to(BASE)): expected for path, expected in EXPECTED.items()},
        "capacity": {
            "strict_labels": len(strict),
            "strict_state_counts": dict(sorted(state_counts.items())),
            "stratum_sizes": {key: len(strata[key]) for key in STRATUM_ORDER},
            "filtered_features": len(vocabulary),
            "filtered_feature_sha256": feature_hash(vocabulary) if vocabulary else None,
            "cyclic_worlds": cyclic_worlds,
            "excluded_records": dict(sorted(excluded.items())),
        },
    }
    if not capacity_pass:
        result = {
            **common,
            "status": "STOP_UNPOWERED_BEFORE_CLOTHING_ASSOCIATION_SCORE",
            "decision": "STOP_UNPOWERED_BEFORE_CLOTHING_ASSOCIATION_SCORE",
            "gates": {"capacity": False},
            "claim_ceiling": "No clothing-state association or semantic result was scored.",
        }
        write_once(OUT, json.dumps(result, indent=2, sort_keys=True) + "\n")
        write_once(REPORT, report(result))
        return

    observed = rotate_assignments(strata, (0, 0, 0, 0))
    winning_score, winning_mean, winner, folio_effects, stratum_effects = select(
        vocabulary, strata, features, observed
    )
    null_maxima = []
    for shifts in itertools.product(*(range(len(strata[key])) for key in STRATUM_ORDER)):
        assignments = rotate_assignments(strata, shifts)
        null_maxima.append(select(vocabulary, strata, features, assignments)[0])
    if len(null_maxima) != 3250:
        raise AssertionError("cyclic orbit mismatch")
    tail = sum(value >= winning_score for value in null_maxima)
    exact_p = tail / len(null_maxima)
    dressed_support = {
        folio: sum(
            winner in features[row["source_record_id"]]
            for row in strict
            if row["physical_folio"] == folio and row["clothing_state"] == "DRESSED"
        )
        for folio in ("f71", "f72")
    }
    robust_f72_strata = {
        key: delta(winner, strata[key], features, observed, MEDIUM_NATIVE)
        for key in ("f72r1|INNER", "f72r2|OUTER")
    }
    robust_f72 = sum(robust_f72_strata.values()) / 2
    gates = {
        "capacity": True,
        "exact_max_feature_p_at_most_0_01": exact_p <= 0.01,
        "winning_score_at_least_0_50": winning_score >= 0.50,
        "both_folio_effects_at_least_0_50": all(value >= 0.50 for value in folio_effects.values()),
        "all_stratum_deltas_at_least_0_25": all(value >= 0.25 for value in stratum_effects.values()),
        "dressed_support_not_concentrated": dressed_support["f71"] >= 4 and dressed_support["f72"] >= 2,
        "medium_grade_deleted_f72_effect_at_least_0_40": robust_f72 >= 0.40,
    }
    decision = (
        "PASS_RECURRENT_FORMAL_FEATURE_ASSOCIATED_WITH_CLOTHING_STATE"
        if all(gates.values())
        else "FINAL_NONCONFIRMATION_NO_RECURRENT_CLOTHING_ASSOCIATED_FORMAL_MARKER"
    )
    result = {
        **common,
        "status": decision,
        "decision": decision,
        "target": {
            "winning_feature": winner,
            "winning_score": winning_score,
            "winning_mean_folio_effect": winning_mean,
            "folio_effects": folio_effects,
            "stratum_effects": stratum_effects,
            "inclusive_tail_count": tail,
            "exact_p": exact_p,
            "dressed_feature_support": dressed_support,
            "medium_confidence_deleted_f72_stratum_effects": robust_f72_strata,
            "medium_confidence_deleted_f72_effect": robust_f72,
        },
        "gates": gates,
        "claim_ceiling": (
            "At most, one frozen formal feature is associated with this source-bound clothing-state panel. "
            "No clothing gloss, zodiac name, sound, language, cipher, plaintext, meaning, or translation follows."
        ),
    }
    write_once(OUT, json.dumps(result, indent=2, sort_keys=True) + "\n")
    write_once(REPORT, report(result))


if __name__ == "__main__":
    main()
