#!/usr/bin/env python3
"""Build the score-blind ZCV001 clothing-state capacity artifact."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PROJECTION = RESULTS / "zcv001_zodiac_clothing_state_projection.tsv"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
OUT = RESULTS / "zcv001_zodiac_clothing_native_visual_capacity.json"
REPORT = RESULTS / "zcv001_zodiac_clothing_native_visual_capacity_report.md"

EXPECTED = {
    PROJECTION: "d1f74428e16e0674aad9e997df884067f8b778f31927d061b1def0a715c9ad68",
    CROSSWALK: "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
}
EXPECTED_FEATURE_SHA = "e395dd0228fb8ad018dce53a5089892cec02af0267ce5751be556e03c269f05e"
EXPECTED_NONSTRICT = {"STOLFI_BEST_0599", "STOLFI_BEST_0601"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def feature_sha(features: list[str]) -> str:
    return hashlib.sha256("".join(term + "\n" for term in features).encode()).hexdigest()


def group_features(row: dict[str, str]) -> set[str]:
    output: set[str] = set()
    family = row["family_surface"]
    for n in (1, 2, 3):
        output.update(f"F:N:{n}:{family[i:i+n]}" for i in range(len(family) - n + 1))
        if len(family) >= n:
            output.update((f"F:P:{n}:{family[:n]}", f"F:S:{n}:{family[-n:]}"))
    output.add("F:W:" + family)
    readings = [row[key].split() for key in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
    if readings[0] == readings[1] == readings[2]:
        codes = readings[0]
        for n in (1, 2, 3):
            output.update(
                f"M:N:{n}:{' '.join(codes[i:i+n])}" for i in range(len(codes) - n + 1)
            )
            if len(codes) >= n:
                output.update(
                    (f"M:P:{n}:{' '.join(codes[:n])}", f"M:S:{n}:{' '.join(codes[-n:])}")
                )
        output.add("M:W:" + " ".join(codes))
    return output


def strict_groups(
    state: dict[str, str],
    crosswalk: dict[str, str] | None,
    lookup: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, str]], str]:
    if crosswalk is None:
        return [], "NO_CROSSWALK"
    expected_key = f"{state['ring']}:GROVE_{state['grove_number']}"
    if (
        crosswalk["primary_eligible"] != "1"
        or not crosswalk["current_locus"]
        or crosswalk["current_page"] != state["page"]
        or crosswalk["position_key"] != expected_key
    ):
        return [], "CROSSWALK_NOT_STRICT"
    groups = sorted(
        lookup.get(crosswalk["current_locus"], ()), key=lambda row: int(row["consensus_group_index"])
    )
    if not groups:
        return [], "NO_CONSENSUS"
    if (
        any(
            row["page"] != state["page"]
            or row["kind"] != "L"
            or row["grammar_scope"] != "DIAGNOSTIC_NONPROSE"
            or row["strict_zero_alternative"] != "1"
            or not row["family_surface"]
            for row in groups
        )
        or [int(row["consensus_group_index"]) for row in groups]
        != list(range(1, len(groups) + 1))
        or {int(row["consensus_group_count"]) for row in groups} != {len(groups)}
    ):
        return [], "NONSTRICT_CONSENSUS"
    return groups, "NONE"


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"input hash mismatch: {path}")

    states = read_rows(PROJECTION)
    crosswalk = {row["source_record_id"]: row for row in read_rows(CROSSWALK)}
    group_lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_rows(GROUPS):
        group_lookup[row["locus"]].append(row)

    if len(states) != len({row["source_record_id"] for row in states}):
        raise SystemExit("duplicate state id")
    features: dict[str, set[str]] = {}
    exclusions: dict[str, str] = {}
    strict_states: list[dict[str, str]] = []
    for state in states:
        groups, reason = strict_groups(state, crosswalk.get(state["source_record_id"]), group_lookup)
        if reason != "NONE":
            exclusions[state["source_record_id"]] = reason
            continue
        strict_states.append(state)
        features[state["source_record_id"]] = set().union(*(group_features(row) for row in groups))

    strata: dict[str, list[dict[str, str]]] = defaultdict(list)
    for state in strict_states:
        strata[f"{state['page']}|{state['ring']}"].append(state)
    for values in strata.values():
        values.sort(key=lambda row: int(row["grove_number"]))

    universe = sorted(set().union(*features.values()), key=lambda term: term.encode())
    vocabulary = [
        term
        for term in universe
        if sum(term in values for values in features.values()) >= 4
        and all(
            0 < sum(term in features[row["source_record_id"]] for row in values) < len(values)
            for values in strata.values()
        )
    ]
    strict_counts = Counter(row["clothing_state"] for row in strict_states)
    by_stratum = {
        key: dict(sorted(Counter(row["clothing_state"] for row in values).items()))
        for key, values in sorted(strata.items())
    }
    by_folio = {
        folio: dict(
            sorted(Counter(row["clothing_state"] for row in strict_states if row["physical_folio"] == folio).items())
        )
        for folio in sorted({row["physical_folio"] for row in strict_states})
    }
    mixed = [
        key
        for key, counts in by_stratum.items()
        if counts.get("DRESSED", 0) and counts.get("UNDRESSED", 0)
    ]
    cyclic_worlds = math.prod(len(values) for values in strata.values())

    gates = {
        "exactly_35_projected_records": len(states) == 35,
        "exactly_33_strict_labels": len(strict_states) == 33,
        "expected_two_nonstrict_records": set(exclusions) == EXPECTED_NONSTRICT,
        "exactly_four_mixed_page_ring_strata": len(strata) == 4 and len(mixed) == 4,
        "both_states_on_each_physical_folio": len(by_folio) == 2
        and all(counts.get("DRESSED", 0) and counts.get("UNDRESSED", 0) for counts in by_folio.values()),
        "at_least_24_target_blind_features": len(vocabulary) >= 24,
        "target_blind_feature_contract": len(universe) == 398
        and len(vocabulary) == 37
        and feature_sha(vocabulary) == EXPECTED_FEATURE_SHA,
        "at_least_1000_cyclic_worlds": cyclic_worlds >= 1000,
    }
    decision = (
        "PASS_UNSCORED_CLOTHING_CONTRAST_CAPACITY"
        if all(gates.values())
        else "STOP_UNSCORED_CLOTHING_CONTRAST_CAPACITY"
    )
    result = {
        "experiment": "ZCV001_ZODIAC_CLOTHING_NATIVE_VISUAL_CAPACITY",
        "status": decision,
        "decision": decision,
        "inputs": {str(path.relative_to(BASE)): expected for path, expected in EXPECTED.items()},
        "source_bindings": {
            "yale_manifest_sha256": "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309",
            "yale_canvas_1006203_full_image_sha256": "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269",
        },
        "counts": {
            "projected_records": len(states),
            "strict_labels": len(strict_states),
            "strict_states": dict(sorted(strict_counts.items())),
            "strict_by_stratum": by_stratum,
            "strict_by_physical_folio": by_folio,
            "nonstrict_records": dict(sorted(exclusions.items())),
            "unfiltered_features": len(universe),
            "filtered_features": len(vocabulary),
            "filtered_feature_sha256": feature_sha(vocabulary),
            "cyclic_worlds": cyclic_worlds,
        },
        "mixed_strata": mixed,
        "gates": gates,
        "claim_ceiling": (
            "Capacity only: a separately frozen experiment may test an anonymous formal-feature association. "
            "No clothing word, zodiac name, sound, language, cipher, plaintext, meaning, or translation follows."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# ZCV001 zodiac clothing-state capacity\n\n"
        f"Status: **{decision}**\n\n"
        f"The frozen projection contains **{len(states)}** records and **{len(strict_states)}** strict labels. "
        f"Strict states are {dict(sorted(strict_counts.items()))}. All four page-by-ring strata are mixed, "
        f"both physical folios contain both scored states, and the target-blind filter retains "
        f"**{len(vocabulary)}** formal features. The complete cyclic orbit has **{cyclic_worlds}** worlds.\n\n"
        "No clothing association was scored. A target run requires a separately published preregistration and freeze.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
