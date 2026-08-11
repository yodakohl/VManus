#!/usr/bin/env python3
"""Independent nonimporting reconstruction of the ZCV001 target."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "ZCV001_ZODIAC_CLOTHING_FORMAL_MARKER_TARGET_SPEC.md"
RUNNER = BASE / "run_zcv001_zodiac_clothing_formal_marker_target.py"
PANEL = RESULTS / "zcv001_zodiac_clothing_state_projection.tsv"
CAPACITY = RESULTS / "zcv001_zodiac_clothing_native_visual_capacity.json"
CAPACITY_VALIDATION = RESULTS / "zcv001_zodiac_clothing_native_visual_capacity_validation.json"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
GROUP_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
PRODUCTION = RESULTS / "zcv001_zodiac_clothing_formal_marker_target.json"
PRODUCTION_REPORT = RESULTS / "zcv001_zodiac_clothing_formal_marker_target_report.md"
OUT = RESULTS / "zcv001_zodiac_clothing_formal_marker_target_validation.json"
REPORT = RESULTS / "zcv001_zodiac_clothing_formal_marker_target_validation.md"

HASHES = {
    SPEC: "89046a228a15a6aa4e9c8050c9915f42395a014d2aa004df6d0d0e041deb7079",
    RUNNER: "d078c8a18d483324701a3227df1e356664c8355dc2185267d38b1f10c997154f",
    PANEL: "d1f74428e16e0674aad9e997df884067f8b778f31927d061b1def0a715c9ad68",
    CAPACITY: "a55b532b57e3c582a5da55ec782bb7f5f6df1eaa7e6b5204b67111dc6c887455",
    CAPACITY_VALIDATION: "b2ce7bc0e1391142fb92954d58423bb573083660322ccc5d04b9c9395b2cbd76",
    CROSSWALK: "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    GROUP_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
}
ORDER = ("f71r|INNER", "f71v|OUTER", "f72r1|INNER", "f72r2|OUTER")
FEATURE_SHA = "e395dd0228fb8ad018dce53a5089892cec02af0267ce5751be556e03c269f05e"
MEDIUM = {"STOLFI_BEST_0536", "STOLFI_BEST_0597"}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def formal_features(group: dict[str, str]) -> set[str]:
    found: set[str] = set()
    surface = group["family_surface"]
    for width in (1, 2, 3):
        if width <= len(surface):
            found.add(f"F:P:{width}:{surface[:width]}")
            found.add(f"F:S:{width}:{surface[-width:]}")
            for index in range(len(surface) - width + 1):
                found.add(f"F:N:{width}:{surface[index:index+width]}")
    found.add("F:W:" + surface)
    readings = tuple(tuple(group[key].split()) for key in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes"))
    if readings[0] == readings[1] == readings[2]:
        sequence = readings[0]
        for width in (1, 2, 3):
            if width <= len(sequence):
                found.add(f"M:P:{width}:" + " ".join(sequence[:width]))
                found.add(f"M:S:{width}:" + " ".join(sequence[-width:]))
                for index in range(len(sequence) - width + 1):
                    found.add(f"M:N:{width}:" + " ".join(sequence[index:index+width]))
        found.add("M:W:" + " ".join(sequence))
    return found


def build_panel() -> tuple[
    list[dict[str, str]], dict[str, list[dict[str, str]]], dict[str, set[str]], list[str], dict[str, str]
]:
    projected = load_tsv(PANEL)
    links = {row["source_record_id"]: row for row in load_tsv(CROSSWALK)}
    groups_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for group in load_tsv(GROUPS):
        groups_by_locus[group["locus"]].append(group)
    strict = []
    excluded = {}
    per_label = {}
    for state in projected:
        link = links.get(state["source_record_id"])
        expected_position = f"{state['ring']}:GROVE_{state['grove_number']}"
        if (
            link is None
            or link["primary_eligible"] != "1"
            or not link["current_locus"]
            or link["current_page"] != state["page"]
            or link["position_key"] != expected_position
        ):
            excluded[state["source_record_id"]] = "CROSSWALK_NOT_STRICT"
            continue
        groups = sorted(
            groups_by_locus.get(link["current_locus"], ()),
            key=lambda group: int(group["consensus_group_index"]),
        )
        if not groups:
            excluded[state["source_record_id"]] = "NO_CONSENSUS"
            continue
        indices = [int(group["consensus_group_index"]) for group in groups]
        counts = {int(group["consensus_group_count"]) for group in groups}
        if (
            indices != list(range(1, len(groups) + 1))
            or counts != {len(groups)}
            or any(
                group["page"] != state["page"]
                or group["kind"] != "L"
                or group["grammar_scope"] != "DIAGNOSTIC_NONPROSE"
                or group["strict_zero_alternative"] != "1"
                or not group["family_surface"]
                for group in groups
            )
        ):
            excluded[state["source_record_id"]] = "NONSTRICT_CONSENSUS"
            continue
        strict.append(state)
        per_label[state["source_record_id"]] = set().union(*(formal_features(group) for group in groups))
    strata: dict[str, list[dict[str, str]]] = defaultdict(list)
    for state in strict:
        strata[state["page"] + "|" + state["ring"]].append(state)
    for values in strata.values():
        values.sort(key=lambda state: int(state["grove_number"]))
    universe = sorted(set().union(*per_label.values()), key=lambda value: value.encode())
    retained = []
    for term in universe:
        if sum(term in values for values in per_label.values()) < 4:
            continue
        if all(0 < sum(term in per_label[row["source_record_id"]] for row in strata[key]) < len(strata[key]) for key in ORDER):
            retained.append(term)
    return strict, strata, per_label, retained, excluded


def assignments_for(
    strata: dict[str, list[dict[str, str]]], shifts: tuple[int, ...]
) -> dict[str, str]:
    output: dict[str, str] = {}
    for position, key in enumerate(ORDER):
        values = strata[key]
        states = tuple(row["clothing_state"] for row in values)
        shift = shifts[position]
        for index, row in enumerate(values):
            output[row["source_record_id"]] = states[(index - shift) % len(states)]
    return output


def contrast(
    term: str,
    values: list[dict[str, str]],
    per_label: dict[str, set[str]],
    assigned: dict[str, str],
    remove: set[str] = frozenset(),
) -> float:
    positive = []
    negative = []
    for row in values:
        record_id = row["source_record_id"]
        if record_id in remove:
            continue
        present = int(term in per_label[record_id])
        if assigned[record_id] == "DRESSED":
            positive.append(present)
        elif assigned[record_id] == "UNDRESSED":
            negative.append(present)
    if not positive or not negative:
        raise AssertionError("invalid state partition")
    return sum(positive) / len(positive) - sum(negative) / len(negative)


def evaluate(
    term: str,
    strata: dict[str, list[dict[str, str]]],
    per_label: dict[str, set[str]],
    assigned: dict[str, str],
) -> tuple[float, float, dict[str, float], dict[str, float]]:
    by_stratum = {key: contrast(term, strata[key], per_label, assigned) for key in ORDER}
    by_folio = {
        "f71": (by_stratum["f71r|INNER"] + by_stratum["f71v|OUTER"]) / 2,
        "f72": (by_stratum["f72r1|INNER"] + by_stratum["f72r2|OUTER"]) / 2,
    }
    return min(by_folio.values()), (by_folio["f71"] + by_folio["f72"]) / 2, by_folio, by_stratum


def winner_for(
    retained: list[str],
    strata: dict[str, list[dict[str, str]]],
    per_label: dict[str, set[str]],
    assigned: dict[str, str],
) -> tuple[float, float, str, dict[str, float], dict[str, float]]:
    candidates = []
    for term in retained:
        score, average, folio, stratum = evaluate(term, strata, per_label, assigned)
        candidates.append((score, average, term, folio, stratum))
    return min(candidates, key=lambda item: (-item[0], -item[1], item[2].encode()))


def make_report(result: dict[str, object]) -> str:
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


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    if not PRODUCTION.exists() or not PRODUCTION_REPORT.exists():
        raise SystemExit("production outputs absent")
    for path, expected in HASHES.items():
        if file_sha(path) != expected:
            raise SystemExit(f"hash mismatch: {path}")
    checks: dict[str, bool] = {
        f"hash_{path.name}": file_sha(path) == expected for path, expected in HASHES.items()
    }
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    capacity_validation = json.loads(CAPACITY_VALIDATION.read_text(encoding="utf-8"))
    group_validation = json.loads(GROUP_VALIDATION.read_text(encoding="utf-8"))
    strict, strata, per_label, retained, excluded = build_panel()
    checks.update(
        {
            "capacity_source_passed": capacity.get("decision") == "PASS_UNSCORED_CLOTHING_CONTRAST_CAPACITY",
            "capacity_validation_passed": capacity_validation.get("status")
            == "PASS_INDEPENDENT_SCORE_BLIND_CAPACITY_RECONSTRUCTION",
            "group_validation_passed": str(group_validation.get("status", "")).startswith("PASS"),
            "strict_count_33": len(strict) == 33,
            "only_expected_nonstrict": excluded
            == {"STOLFI_BEST_0599": "NO_CONSENSUS", "STOLFI_BEST_0601": "NO_CONSENSUS"},
            "stratum_order_exact": tuple(strata) == ORDER,
            "stratum_sizes_exact": [len(strata[key]) for key in ORDER] == [5, 10, 5, 13],
            "strict_states_exact": Counter(row["clothing_state"] for row in strict)
            == Counter({"UNDRESSED": 15, "DRESSED": 14, "UNCERTAIN": 4}),
            "feature_count_37": len(retained) == 37,
            "feature_sha_exact": hashlib.sha256("".join(term + "\n" for term in retained).encode()).hexdigest()
            == FEATURE_SHA,
        }
    )
    observed = assignments_for(strata, (0, 0, 0, 0))
    winning_score, winning_mean, term, folio_effects, stratum_effects = winner_for(
        retained, strata, per_label, observed
    )
    maxima = []
    for shifts in itertools.product(*(range(len(strata[key])) for key in ORDER)):
        maxima.append(winner_for(retained, strata, per_label, assignments_for(strata, shifts))[0])
    tail = sum(value >= winning_score for value in maxima)
    exact_p = tail / len(maxima)
    dressed_support = {
        folio: sum(
            term in per_label[row["source_record_id"]]
            for row in strict
            if row["physical_folio"] == folio and row["clothing_state"] == "DRESSED"
        )
        for folio in ("f71", "f72")
    }
    robust_strata = {
        key: contrast(term, strata[key], per_label, observed, MEDIUM)
        for key in ("f72r1|INNER", "f72r2|OUTER")
    }
    robust_f72 = sum(robust_strata.values()) / 2
    gates = {
        "capacity": all(checks.values()),
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
    inputs = {str(path.relative_to(BASE)): expected for path, expected in HASHES.items() if path != RUNNER}
    expected_result = {
        "experiment": "ZCV001_ZODIAC_CLOTHING_FORMAL_MARKER_TARGET",
        "inputs": inputs,
        "capacity": {
            "strict_labels": len(strict),
            "strict_state_counts": dict(sorted(Counter(row["clothing_state"] for row in strict).items())),
            "stratum_sizes": {key: len(strata[key]) for key in ORDER},
            "filtered_features": len(retained),
            "filtered_feature_sha256": FEATURE_SHA,
            "cyclic_worlds": len(maxima),
            "excluded_records": dict(sorted(excluded.items())),
        },
        "status": decision,
        "decision": decision,
        "target": {
            "winning_feature": term,
            "winning_score": winning_score,
            "winning_mean_folio_effect": winning_mean,
            "folio_effects": folio_effects,
            "stratum_effects": stratum_effects,
            "inclusive_tail_count": tail,
            "exact_p": exact_p,
            "dressed_feature_support": dressed_support,
            "medium_confidence_deleted_f72_stratum_effects": robust_strata,
            "medium_confidence_deleted_f72_effect": robust_f72,
        },
        "gates": gates,
        "claim_ceiling": (
            "At most, one frozen formal feature is associated with this source-bound clothing-state panel. "
            "No clothing gloss, zodiac name, sound, language, cipher, plaintext, meaning, or translation follows."
        ),
    }
    production = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    expected_bytes = json.dumps(expected_result, indent=2, sort_keys=True) + "\n"
    checks.update(
        {
            "exact_3250_worlds": len(maxima) == 3250,
            "observed_world_in_orbit": assignments_for(strata, (0, 0, 0, 0)) == observed,
            "production_object_exact": production == expected_result,
            "production_bytes_exact": PRODUCTION.read_text(encoding="utf-8") == expected_bytes,
            "production_report_exact": PRODUCTION_REPORT.read_text(encoding="utf-8")
            == make_report(expected_result),
        }
    )
    if not all(checks.values()):
        raise SystemExit("validation failed: " + ", ".join(name for name, value in checks.items() if not value))
    validation = {
        "experiment": "ZCV001_ZODIAC_CLOTHING_FORMAL_MARKER_TARGET_VALIDATION",
        "status": "PASS_INDEPENDENT_EXACT_TARGET_RECONSTRUCTION",
        "validated_decision": decision,
        "source_result_sha256": file_sha(PRODUCTION),
        "source_report_sha256": file_sha(PRODUCTION_REPORT),
        "checks": checks,
        "check_count": len(checks),
        "reconstructed_target": expected_result["target"],
        "reconstructed_gates": gates,
        "claim_ceiling": expected_result["claim_ceiling"],
    }
    with OUT.open("x", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    with REPORT.open("x", encoding="utf-8", newline="") as handle:
        handle.write(
            "# ZCV001 clothing-state formal-marker target validation\n\n"
            "Status: **PASS_INDEPENDENT_EXACT_TARGET_RECONSTRUCTION**\n\n"
            f"A nonimporting implementation reproduced all 3,250 cyclic worlds, the winner, exact p-value, "
            f"robustness checks, canonical result, and exact report in **{len(checks)}** checks.\n\n"
            f"Validated decision: **{decision}**.\n\n"
            f"Claim ceiling: {expected_result['claim_ceiling']}\n"
        )


if __name__ == "__main__":
    main()
