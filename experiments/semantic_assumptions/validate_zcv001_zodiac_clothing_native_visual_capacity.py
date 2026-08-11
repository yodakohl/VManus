#!/usr/bin/env python3
"""Independent reconstruction of the score-blind ZCV001 capacity artifact."""

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
SOURCE_RESULT = RESULTS / "zcv001_zodiac_clothing_native_visual_capacity.json"
SOURCE_REPORT = RESULTS / "zcv001_zodiac_clothing_native_visual_capacity_report.md"
PRODUCER = BASE / "audit_zcv001_zodiac_clothing_native_visual_capacity.py"
OUT = RESULTS / "zcv001_zodiac_clothing_native_visual_capacity_validation.json"
REPORT = RESULTS / "zcv001_zodiac_clothing_native_visual_capacity_validation.md"

HASHES = {
    PROJECTION: "d1f74428e16e0674aad9e997df884067f8b778f31927d061b1def0a715c9ad68",
    CROSSWALK: "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    PRODUCER: "2ab8e11e547fb45fc6787f5ba0a84e47e66a52c01d53da2e76aabe261a5fd78c",
    SOURCE_RESULT: "a55b532b57e3c582a5da55ec782bb7f5f6df1eaa7e6b5204b67111dc6c887455",
    SOURCE_REPORT: "e979a0490e1cf55241bbf25c201acb0f1ee44b3f0053fe549f0b8da65cccd376",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def terms(row: dict[str, str]) -> set[str]:
    found: set[str] = set()
    surface = row["family_surface"]
    for width in (1, 2, 3):
        for start in range(0, len(surface) - width + 1):
            found.add(f"F:N:{width}:{surface[start:start+width]}")
        if len(surface) >= width:
            found.add(f"F:P:{width}:{surface[:width]}")
            found.add(f"F:S:{width}:{surface[-width:]}")
    found.add("F:W:" + surface)
    seqs = tuple(tuple(row[name].split()) for name in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes"))
    if seqs[0] == seqs[1] == seqs[2]:
        seq = seqs[0]
        for width in (1, 2, 3):
            for start in range(0, len(seq) - width + 1):
                found.add(f"M:N:{width}:{' '.join(seq[start:start+width])}")
            if len(seq) >= width:
                found.add(f"M:P:{width}:{' '.join(seq[:width])}")
                found.add(f"M:S:{width}:{' '.join(seq[-width:])}")
        found.add("M:W:" + " ".join(seq))
    return found


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    checks: dict[str, bool] = {f"hash_{path.name}": digest(path) == expected for path, expected in HASHES.items()}
    if not all(checks.values()):
        raise SystemExit("hash preflight failed")

    states = table(PROJECTION)
    cross = {row["source_record_id"]: row for row in table(CROSSWALK)}
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in table(GROUPS):
        grouped[row["locus"]].append(row)

    checks.update(
        {
            "projection_has_35_rows": len(states) == 35,
            "projection_ids_unique": len({row["source_record_id"] for row in states}) == 35,
            "states_are_closed_inventory": {row["clothing_state"] for row in states}
            == {"DRESSED", "UNDRESSED", "UNCERTAIN"},
            "provenance_is_closed_inventory": {row["state_provenance"] for row in states}
            == {"HUMAN_STOLFI_GROVE_UNIT_COMMENT", "SOURCE_BOUND_NATIVE_VISUAL"},
            "native_rows_bind_one_canvas": all(
                row["canvas_id"] == "1006203"
                and row["image_sha256"]
                == "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269"
                for row in states
                if row["state_provenance"] == "SOURCE_BOUND_NATIVE_VISUAL"
            ),
            "human_rows_do_not_claim_image_provenance": all(
                row["canvas_id"] == row["image_url"] == row["image_sha256"] == "NONE"
                for row in states
                if row["state_provenance"] == "HUMAN_STOLFI_GROVE_UNIT_COMMENT"
            ),
            "projection_contains_no_voynich_surface_field": not any(
                key.lower() in {"surface", "text", "family_surface", "zl3b_text", "it2a_text", "rf1b_text"}
                for key in states[0]
            ),
        }
    )

    strict: list[dict[str, str]] = []
    excluded: dict[str, str] = {}
    feature_map: dict[str, set[str]] = {}
    for state in states:
        link = cross.get(state["source_record_id"])
        if link is None or link["primary_eligible"] != "1" or not link["current_locus"]:
            excluded[state["source_record_id"]] = "CROSSWALK_NOT_STRICT"
            continue
        if link["current_page"] != state["page"] or link["position_key"] != f"{state['ring']}:GROVE_{state['grove_number']}":
            excluded[state["source_record_id"]] = "CROSSWALK_NOT_STRICT"
            continue
        rows = sorted(grouped.get(link["current_locus"], ()), key=lambda row: int(row["consensus_group_index"]))
        if not rows:
            excluded[state["source_record_id"]] = "NO_CONSENSUS"
            continue
        complete = (
            all(
                row["page"] == state["page"]
                and row["kind"] == "L"
                and row["grammar_scope"] == "DIAGNOSTIC_NONPROSE"
                and row["strict_zero_alternative"] == "1"
                and row["family_surface"]
                for row in rows
            )
            and [int(row["consensus_group_index"]) for row in rows] == list(range(1, len(rows) + 1))
            and {int(row["consensus_group_count"]) for row in rows} == {len(rows)}
        )
        if not complete:
            excluded[state["source_record_id"]] = "NONSTRICT_CONSENSUS"
            continue
        strict.append(state)
        feature_map[state["source_record_id"]] = set().union(*(terms(row) for row in rows))

    strata: dict[str, list[dict[str, str]]] = defaultdict(list)
    for state in strict:
        strata[f"{state['page']}|{state['ring']}"].append(state)
    for values in strata.values():
        values.sort(key=lambda row: int(row["grove_number"]))
    universe = sorted(set().union(*feature_map.values()), key=lambda item: item.encode())
    retained = []
    for term in universe:
        if sum(term in values for values in feature_map.values()) < 4:
            continue
        if all(0 < sum(term in feature_map[row["source_record_id"]] for row in rows) < len(rows) for rows in strata.values()):
            retained.append(term)
    retained_sha = hashlib.sha256("".join(term + "\n" for term in retained).encode()).hexdigest()
    state_counts = Counter(row["clothing_state"] for row in strict)
    per_stratum = {
        key: dict(sorted(Counter(row["clothing_state"] for row in rows).items()))
        for key, rows in sorted(strata.items())
    }
    per_folio = {
        folio: dict(sorted(Counter(row["clothing_state"] for row in strict if row["physical_folio"] == folio).items()))
        for folio in sorted({row["physical_folio"] for row in strict})
    }
    mixed = [key for key, counts in per_stratum.items() if counts.get("DRESSED") and counts.get("UNDRESSED")]
    worlds = math.prod(len(rows) for rows in strata.values())
    gates = {
        "exactly_35_projected_records": len(states) == 35,
        "exactly_33_strict_labels": len(strict) == 33,
        "expected_two_nonstrict_records": set(excluded) == {"STOLFI_BEST_0599", "STOLFI_BEST_0601"},
        "exactly_four_mixed_page_ring_strata": len(strata) == 4 and len(mixed) == 4,
        "both_states_on_each_physical_folio": len(per_folio) == 2
        and all(value.get("DRESSED") and value.get("UNDRESSED") for value in per_folio.values()),
        "at_least_24_target_blind_features": len(retained) >= 24,
        "target_blind_feature_contract": len(universe) == 398
        and len(retained) == 37
        and retained_sha == "e395dd0228fb8ad018dce53a5089892cec02af0267ce5751be556e03c269f05e",
        "at_least_1000_cyclic_worlds": worlds >= 1000,
    }
    expected = {
        "experiment": "ZCV001_ZODIAC_CLOTHING_NATIVE_VISUAL_CAPACITY",
        "status": "PASS_UNSCORED_CLOTHING_CONTRAST_CAPACITY",
        "decision": "PASS_UNSCORED_CLOTHING_CONTRAST_CAPACITY",
        "inputs": {
            "results/zcv001_zodiac_clothing_state_projection.tsv": HASHES[PROJECTION],
            "results/existing_human_current_locus_crosswalk.tsv": HASHES[CROSSWALK],
            "results/source_sta_family_consensus_groups.tsv": HASHES[GROUPS],
        },
        "source_bindings": {
            "yale_manifest_sha256": "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309",
            "yale_canvas_1006203_full_image_sha256": "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269",
        },
        "counts": {
            "projected_records": len(states),
            "strict_labels": len(strict),
            "strict_states": dict(sorted(state_counts.items())),
            "strict_by_stratum": per_stratum,
            "strict_by_physical_folio": per_folio,
            "nonstrict_records": dict(sorted(excluded.items())),
            "unfiltered_features": len(universe),
            "filtered_features": len(retained),
            "filtered_feature_sha256": retained_sha,
            "cyclic_worlds": worlds,
        },
        "mixed_strata": mixed,
        "gates": gates,
        "claim_ceiling": (
            "Capacity only: a separately frozen experiment may test an anonymous formal-feature association. "
            "No clothing word, zodiac name, sound, language, cipher, plaintext, meaning, or translation follows."
        ),
    }
    source = json.loads(SOURCE_RESULT.read_text(encoding="utf-8"))
    expected_bytes = json.dumps(expected, indent=2, sort_keys=True) + "\n"
    checks.update(
        {
            "strict_count_reconstructed": len(strict) == 33,
            "strict_state_counts_reconstructed": state_counts == Counter({"UNDRESSED": 15, "DRESSED": 14, "UNCERTAIN": 4}),
            "exact_exclusions_reconstructed": excluded
            == {"STOLFI_BEST_0599": "NO_CONSENSUS", "STOLFI_BEST_0601": "NO_CONSENSUS"},
            "four_strata_reconstructed": len(strata) == 4,
            "feature_universe_reconstructed": len(universe) == 398,
            "feature_filter_reconstructed": len(retained) == 37,
            "feature_hash_reconstructed": retained_sha == "e395dd0228fb8ad018dce53a5089892cec02af0267ce5751be556e03c269f05e",
            "cyclic_orbit_reconstructed": worlds == 3250,
            "all_capacity_gates_pass": all(gates.values()),
            "source_result_object_equal": source == expected,
            "source_result_bytes_equal": SOURCE_RESULT.read_text(encoding="utf-8") == expected_bytes,
            "no_candidate_or_score_serialized": "winning_feature" not in expected_bytes and "exact_p" not in expected_bytes,
        }
    )
    expected_report = (
        "# ZCV001 zodiac clothing-state capacity\n\n"
        "Status: **PASS_UNSCORED_CLOTHING_CONTRAST_CAPACITY**\n\n"
        "The frozen projection contains **35** records and **33** strict labels. "
        "Strict states are {'DRESSED': 14, 'UNCERTAIN': 4, 'UNDRESSED': 15}. All four page-by-ring strata are mixed, "
        "both physical folios contain both scored states, and the target-blind filter retains "
        "**37** formal features. The complete cyclic orbit has **3250** worlds.\n\n"
        "No clothing association was scored. A target run requires a separately published preregistration and freeze.\n\n"
        f"Claim ceiling: {expected['claim_ceiling']}\n"
    )
    checks["source_report_bytes_equal"] = SOURCE_REPORT.read_text(encoding="utf-8") == expected_report
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise SystemExit("validation failure: " + ", ".join(failed))
    validation = {
        "experiment": "ZCV001_ZODIAC_CLOTHING_NATIVE_VISUAL_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_SCORE_BLIND_CAPACITY_RECONSTRUCTION",
        "validated_decision": expected["decision"],
        "source_result_sha256": HASHES[SOURCE_RESULT],
        "source_report_sha256": HASHES[SOURCE_REPORT],
        "producer_sha256": HASHES[PRODUCER],
        "checks": checks,
        "check_count": len(checks),
        "reconstructed_counts": expected["counts"],
        "claim_ceiling": expected["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# ZCV001 clothing-state capacity validation\n\n"
        "Status: **PASS_INDEPENDENT_SCORE_BLIND_CAPACITY_RECONSTRUCTION**\n\n"
        f"A nonimporting reconstruction passed all **{len(checks)}** checks, including the 35-row projection, "
        "33 strict labels, four mixed strata, 37 target-blind features, 3,250 cyclic worlds, canonical result, "
        "and exact report. No clothing association or candidate feature was scored.\n\n"
        f"Claim ceiling: {expected['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
