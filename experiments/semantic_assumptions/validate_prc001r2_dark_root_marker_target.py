#!/usr/bin/env python3
"""Independent nonimporting reconstruction of the PRC001R2 target."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "PRC001R2_SOURCE_CONTRACT_CORRECTED_TARGET_SPEC.md"
RUNNER = BASE / "run_prc001r2_dark_root_marker_target.py"
PANEL = RESULTS / "pharma_root_color_native_visual_ownership.tsv"
PANEL_VALIDATION = RESULTS / "pharma_root_color_native_visual_ownership_validation.json"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
GROUPS_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
PRIOR_STOP = RESULTS / "prc001_dark_root_marker_target.json"
PRIOR_VALIDATION = RESULTS / "prc001_dark_root_marker_target_validation.json"
PRODUCTION = RESULTS / "prc001r2_dark_root_marker_target.json"
PRODUCTION_REPORT = RESULTS / "prc001r2_dark_root_marker_target_report.md"
OUT = RESULTS / "prc001r2_dark_root_marker_target_validation.json"
REPORT = RESULTS / "prc001r2_dark_root_marker_target_validation.md"

HASHES = {
    SPEC: "9236bb8fc45501249e13c711e470db4c3d6f552c8e09a11e3ae69aea97c10862",
    RUNNER: "a30929575aa36ddc318451726cd26f23151a9e9cf6e7bd55338ace519869f3df",
    PANEL: "eb1b5563fa0d775a662f27b566d9c1acd75eba59fdf690e3fc8ac9ab9e225a7b",
    PANEL_VALIDATION: "2eb90320045ac0742294f649f73ec4beff00028ca7e94523490af3535d6da03c",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    GROUPS_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    PRIOR_STOP: "d0b6b0e12bbe4175ce8ba70fcab58f73b5f51bf3a067046cd2cbd9e22a8e5f6b",
    PRIOR_VALIDATION: "52055cee342d2cfaa5bed548c64000d3adbf6eed1243d8c7c4ec268cd6c0eeb0",
}

EXCLUDED = {
    "STOLFI_BEST_1163": "NONSTRICT_ZERO_ALTERNATIVE",
    "STOLFI_BEST_1267": "MISSING_CONSENSUS_LOCUS",
}
FEATURE_SHA = "1691d552609b5651f6f0505795a747bc15c3206486252d8b9f9c134e85dfd65a"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def list_sha(items: list[str]) -> str:
    return hashlib.sha256(("\n".join(items) + "\n").encode()).hexdigest()


def features_for_group(group: dict[str, str]) -> set[str]:
    output: set[str] = set()
    family = group["family_surface"]
    for width in (1, 2, 3):
        if width > len(family):
            continue
        output.add(f"F:P:{width}:{family[:width]}")
        output.add(f"F:S:{width}:{family[-width:]}")
        for left in range(len(family) - width + 1):
            output.add(f"F:N:{width}:{family[left:left+width]}")
    output.add("F:W:" + family)
    code_sequences = tuple(tuple(group[name].split()) for name in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes"))
    if code_sequences[0] == code_sequences[1] == code_sequences[2]:
        sequence = code_sequences[0]
        for width in (1, 2, 3):
            if width > len(sequence):
                continue
            output.add(f"M:P:{width}:" + " ".join(sequence[:width]))
            output.add(f"M:S:{width}:" + " ".join(sequence[-width:]))
            for left in range(len(sequence) - width + 1):
                output.add(f"M:N:{width}:" + " ".join(sequence[left:left+width]))
        output.add("M:W:" + " ".join(sequence))
    return output


def source_groups(
    item: dict[str, str], lookup: dict[str, list[dict[str, str]]]
) -> tuple[list[dict[str, str]], str | None]:
    locus = item["mapped_locus"]
    found = sorted(lookup.get(locus, []), key=lambda group: int(group["consensus_group_index"]))
    if not found:
        return [], "MISSING_LOCUS"
    good = {group["locus"] for group in found} == {locus}
    good &= {group["page"] for group in found} == {item["source_page"]}
    good &= all(group["kind"] == "L" for group in found)
    good &= all(group["grammar_scope"] == "DIAGNOSTIC_NONPROSE" for group in found)
    good &= all(group["strict_zero_alternative"] == "1" for group in found)
    good &= [int(group["consensus_group_index"]) for group in found] == list(range(1, len(found) + 1))
    good &= {int(group["consensus_group_count"]) for group in found} == {len(found)}
    if not good:
        return [], "STRUCTURE"
    for group in found:
        family = group["family_surface"]
        code_sequences = [group[name].split() for name in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
        if not family or any(not sequence or "".join(code[0] for code in sequence) != family for sequence in code_sequences):
            return [], "CODE_FAMILY"
    return found, None


def reconstruct(
    panel: list[dict[str, str]], lookup: dict[str, list[dict[str, str]]]
) -> tuple[dict[str, set[str]], list[str]]:
    output: dict[str, set[str]] = {}
    failures: list[str] = []
    for item in panel:
        found, problem = source_groups(item, lookup)
        if problem:
            failures.append(item["source_record_id"] + ":" + problem)
            continue
        combined: set[str] = set()
        for group in found:
            combined |= features_for_group(group)
        if not combined:
            failures.append(item["source_record_id"] + ":NO_FEATURES")
        else:
            output[item["source_record_id"]] = combined
    return output, failures


def contrast(
    term: str,
    panel: list[dict[str, str]],
    feature_sets: dict[str, set[str]],
    dark: set[str],
) -> float:
    dark_numerator = sum(term in feature_sets[item["source_record_id"]] for item in panel if item["source_record_id"] in dark)
    dark_denominator = sum(item["source_record_id"] in dark for item in panel)
    light_numerator = sum(term in feature_sets[item["source_record_id"]] for item in panel if item["source_record_id"] not in dark)
    light_denominator = sum(item["source_record_id"] not in dark for item in panel)
    if not dark_denominator or not light_denominator:
        raise AssertionError("empty state partition")
    return dark_numerator / dark_denominator - light_numerator / light_denominator


def best(
    vocabulary: list[str],
    by_folio: dict[str, list[dict[str, str]]],
    feature_sets: dict[str, set[str]],
    dark: set[str],
) -> tuple[float, float, str, float, float]:
    scored = []
    for term in vocabulary:
        left = contrast(term, by_folio["f89"], feature_sets, dark)
        right = contrast(term, by_folio["f100"], feature_sets, dark)
        scored.append((min(left, right), (left + right) / 2, term, left, right))
    return min(scored, key=lambda row: (-row[0], -row[1], row[2].encode()))


def production_report(result: dict[str, object]) -> str:
    decision = str(result["decision"])
    if decision == "STOP_UNPOWERED_BEFORE_STATE_SCORE":
        return (
            "# PRC001R2 source-contract-corrected dark-root marker target\n\n"
            "Status: **STOP_UNPOWERED_BEFORE_STATE_SCORE**\n\n"
            "The corrected exact source or capacity contract did not pass. No formal-state association was scored.\n"
        )
    target = result["target"]
    assert isinstance(target, dict)
    presence = json.dumps(target["transfer_presence"], sort_keys=True)
    return (
        "# PRC001R2 source-contract-corrected dark-root marker target\n\n"
        f"Status: **{decision}**\n\n"
        f"The target-blind filter retained **{result['capacity']['filtered_features']}** formal features. "
        f"The frozen winner is `{target['winning_feature']}` with minimum cross-folio delta "
        f"**{target['winning_score']:.6f}** (f89={target['discovery_folio_deltas']['f89']:.6f}, "
        f"f100={target['discovery_folio_deltas']['f100']:.6f}); its inclusive exact max-feature "
        f"p-value is **{target['exact_p']:.6f}** "
        f"({target['inclusive_tail_count']}/1008).\n\n"
        f"Transfer presence on the two untouched f102 DARK labels is `{presence}`.\n\n"
        f"Decision: **{decision}**.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n"
    )


def write_new(path: Path, text: str) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        handle.write(text)


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite of validation outputs")
    checks: list[str] = []
    for path, expected in HASHES.items():
        if sha(path) != expected:
            raise AssertionError("hash mismatch: " + str(path))
        checks.append("hash_" + path.name)
    if not PRODUCTION.exists() or not PRODUCTION_REPORT.exists():
        raise SystemExit("production outputs absent")

    prior = json.loads(PRIOR_STOP.read_text(encoding="utf-8"))
    prior_validation = json.loads(PRIOR_VALIDATION.read_text(encoding="utf-8"))
    if (
        prior.get("decision") != "STOP_UNPOWERED_BEFORE_STATE_SCORE"
        or prior.get("capacity", {}).get("filtered_features") != 0
        or "target" in prior
        or prior_validation.get("validated_decision") != "STOP_UNPOWERED_BEFORE_STATE_SCORE"
    ):
        raise AssertionError("prior zero-score stop")
    checks.append("prior_zero_feature_zero_world_stop_bound")

    ownership = [item for item in tsv(PANEL) if item["eligible"] == "1"]
    lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for group in tsv(GROUPS):
        lookup[group["locus"]].append(group)
    by_id = {item["source_record_id"]: item for item in ownership}
    exclusion_contract = {
        "STOLFI_BEST_1163": bool(lookup.get(by_id["STOLFI_BEST_1163"]["mapped_locus"]))
        and any(group["strict_zero_alternative"] == "0" for group in lookup[by_id["STOLFI_BEST_1163"]["mapped_locus"]]),
        "STOLFI_BEST_1267": not lookup.get(by_id["STOLFI_BEST_1267"]["mapped_locus"]),
    }
    complete = [item for item in ownership if item["source_record_id"] not in EXCLUDED]
    discovery = [item for item in complete if item["physical_folio"] in ("f89", "f100")]
    transfer = [item for item in complete if item["physical_folio"] == "f102"]
    by_folio = {folio: [item for item in discovery if item["physical_folio"] == folio] for folio in ("f89", "f100")}
    margins = {folio: Counter(item["root_state"] for item in panel) for folio, panel in by_folio.items()}

    feature_sets, failures = reconstruct(discovery, lookup)
    transfer_structure_failures = []
    for item in transfer:
        _, problem = source_groups(item, lookup)
        if problem:
            transfer_structure_failures.append(item["source_record_id"] + ":" + problem)
    universe = sorted(set().union(*feature_sets.values()), key=lambda term: term.encode()) if feature_sets else []
    vocabulary = []
    for term in universe:
        total = sum(term in feature_sets[item["source_record_id"]] for item in discovery)
        variable = all(
            0 < sum(term in feature_sets[item["source_record_id"]] for item in by_folio[folio]) < len(by_folio[folio])
            for folio in ("f89", "f100")
        )
        if total >= 3 and variable:
            vocabulary.append(term)
    orbit = len(tuple(itertools.combinations(range(9), 2))) * len(tuple(itertools.combinations(range(8), 2)))
    capacity = {
        "ownership_eligible_labels": len(ownership),
        "exclusions": EXCLUDED,
        "exclusion_contract_pass": exclusion_contract,
        "complete_labels": len(complete),
        "discovery_labels": len(discovery),
        "transfer_labels": len(transfer),
        "discovery_margins": {folio: dict(sorted(counts.items())) for folio, counts in margins.items()},
        "transfer_states": dict(sorted(Counter(item["root_state"] for item in transfer).items())),
        "reconstruction_problems": failures,
        "transfer_structure_problems": transfer_structure_failures,
        "unfiltered_features": len(universe),
        "filtered_features": len(vocabulary),
        "filtered_feature_sha256": list_sha(vocabulary) if vocabulary else None,
        "exact_worlds": orbit,
    }
    capacity_pass = (
        len(ownership) == 21
        and set(by_id) >= set(EXCLUDED)
        and all(exclusion_contract.values())
        and len(complete) == 19
        and len(discovery) == 17
        and len(transfer) == 2
        and margins == {"f89": Counter({"LIGHT": 7, "DARK": 2}), "f100": Counter({"LIGHT": 6, "DARK": 2})}
        and Counter(item["root_state"] for item in transfer) == {"DARK": 2}
        and not failures
        and not transfer_structure_failures
        and len(feature_sets) == 17
        and len(universe) == 306
        and len(vocabulary) == 48
        and list_sha(vocabulary) == FEATURE_SHA
        and orbit == 1008
    )
    common = {
        "experiment": "PRC001R2_SOURCE_CONTRACT_CORRECTED_TARGET",
        "inputs": {
            str(path.relative_to(BASE)): expected
            for path, expected in HASHES.items()
            if path != RUNNER
        },
        "capacity": capacity,
    }
    if not capacity_pass:
        expected_result = {
            **common,
            "status": "STOP_UNPOWERED_BEFORE_STATE_SCORE",
            "decision": "STOP_UNPOWERED_BEFORE_STATE_SCORE",
            "gates": {"capacity": False},
            "claim_ceiling": "No formal marker or semantic result was scored.",
        }
    else:
        checks.extend(["exact_two_exclusions_reconstructed", "corrected_capacity_reconstructed", "feature_universe_reconstructed"])
        observed_dark = {item["source_record_id"] for item in discovery if item["root_state"] == "DARK"}
        winning_score, winning_mean, winning_term, d89, d100 = best(vocabulary, by_folio, feature_sets, observed_dark)
        ids89 = [item["source_record_id"] for item in by_folio["f89"]]
        ids100 = [item["source_record_id"] for item in by_folio["f100"]]
        maxima = []
        for left in itertools.combinations(ids89, 2):
            for right in itertools.combinations(ids100, 2):
                maxima.append(best(vocabulary, by_folio, feature_sets, set(left) | set(right))[0])
        if len(maxima) != 1008:
            raise AssertionError("null orbit")
        tail = sum(value >= winning_score for value in maxima)
        exact_p = tail / 1008
        transfer_sets, transfer_failures = reconstruct(transfer, lookup)
        presence = {
            item["source_record_id"]: winning_term in transfer_sets.get(item["source_record_id"], set())
            for item in transfer
        }
        deletions = {}
        for removed in sorted(observed_dark):
            remaining_dark = observed_dark - {removed}
            reduced = {
                folio: [item for item in panel if item["source_record_id"] != removed]
                for folio, panel in by_folio.items()
            }
            deletions[removed] = {
                "f89_delta": contrast(winning_term, reduced["f89"], feature_sets, remaining_dark),
                "f100_delta": contrast(winning_term, reduced["f100"], feature_sets, remaining_dark),
            }
        gates = {
            "capacity": True,
            "exact_max_feature_p_at_most_0_01": exact_p <= 0.01,
            "winning_score_at_least_0_50": winning_score >= 0.50,
            "both_discovery_folio_deltas_at_least_0_50": min(d89, d100) >= 0.50,
            "winner_present_in_both_f102_dark_labels": not transfer_failures and all(presence.values()),
            "all_discovery_dark_deletions_retain_both_deltas_at_least_0_50": all(
                min(values.values()) >= 0.50 for values in deletions.values()
            ),
            "all_reading_consensus_reconstruction": not failures and not transfer_failures,
        }
        decision = (
            "PASS_RECURRENT_FORMAL_FEATURE_ASSOCIATED_WITH_HUMAN_DARK_ROOT_STATE"
            if all(gates.values())
            else "FINAL_NONCONFIRMATION_NO_RECURRENT_DARK_ASSOCIATED_FORMAL_MARKER"
        )
        claim = (
            "A pass establishes only that one frozen source-native formal feature is associated "
            "with the inherited human DARK-root drawing state in this small panel. It does not "
            "establish the word DARK or ROOT, a plant name, sound, language, cipher, plaintext, "
            "meaning, or translation."
        )
        expected_result = {
            **common,
            "status": decision,
            "decision": decision,
            "target": {
                "winning_feature": winning_term,
                "winning_score": winning_score,
                "winning_mean_delta": winning_mean,
                "discovery_folio_deltas": {"f89": d89, "f100": d100},
                "exact_p": exact_p,
                "inclusive_tail_count": tail,
                "null_worlds": len(maxima),
                "null_maxima": maxima,
                "null_maxima_sha256": hashlib.sha256(json.dumps(maxima, separators=(",", ":")).encode()).hexdigest(),
                "transfer_presence": presence,
                "transfer_reconstruction_problems": transfer_failures,
                "dark_deletion_deltas": deletions,
            },
            "gates": gates,
            "claim_ceiling": claim,
        }
        checks.extend(["observed_winner_reconstructed", "all_1008_null_worlds_reconstructed", "transfer_and_deletions_reconstructed"])

    production_bytes = PRODUCTION.read_bytes()
    production = json.loads(production_bytes)
    canonical = (json.dumps(production, indent=2, sort_keys=True) + "\n").encode()
    if production_bytes != canonical or production != expected_result:
        raise AssertionError("production result mismatch")
    if PRODUCTION_REPORT.read_text(encoding="utf-8") != production_report(expected_result):
        raise AssertionError("production report mismatch")
    checks.extend(["canonical_production_result_exact", "production_report_exact"])
    validation = {
        "experiment": "PRC001R2_SOURCE_CONTRACT_CORRECTED_TARGET_VALIDATION",
        "status": "PASS_INDEPENDENT_EXACT_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "inputs": {
            "runner_sha256": HASHES[RUNNER],
            "production_sha256": sha(PRODUCTION),
            "production_report_sha256": sha(PRODUCTION_REPORT),
        },
        "validated_decision": production["decision"],
        "claim_ceiling": production["claim_ceiling"],
    }
    write_new(OUT, json.dumps(validation, indent=2, sort_keys=True) + "\n")
    write_new(
        REPORT,
        "# PRC001R2 target validation\n\n"
        f"Status: **{validation['status']}**\n\n"
        "A nonimporting implementation independently reconstructed the exact two-row source correction, "
        "the 17-label discovery panel, all 48 frozen features, all 1,008 conditional worlds, the held "
        "f102 transfer, deletion checks, canonical artifacts, and final decision.\n\n"
        f"Validated decision: **{production['decision']}**.\n",
    )


if __name__ == "__main__":
    main()
