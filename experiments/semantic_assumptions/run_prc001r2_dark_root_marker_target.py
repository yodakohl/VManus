#!/usr/bin/env python3
"""Run the frozen PRC001R2 source-contract-corrected target once."""

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
PANEL = RESULTS / "pharma_root_color_native_visual_ownership.tsv"
PANEL_VALIDATION = RESULTS / "pharma_root_color_native_visual_ownership_validation.json"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
GROUPS_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
PRIOR_STOP = RESULTS / "prc001_dark_root_marker_target.json"
PRIOR_VALIDATION = RESULTS / "prc001_dark_root_marker_target_validation.json"
OUT = RESULTS / "prc001r2_dark_root_marker_target.json"
REPORT = RESULTS / "prc001r2_dark_root_marker_target_report.md"

EXPECTED = {
    SPEC: "9236bb8fc45501249e13c711e470db4c3d6f552c8e09a11e3ae69aea97c10862",
    PANEL: "eb1b5563fa0d775a662f27b566d9c1acd75eba59fdf690e3fc8ac9ab9e225a7b",
    PANEL_VALIDATION: "2eb90320045ac0742294f649f73ec4beff00028ca7e94523490af3535d6da03c",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    GROUPS_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    PRIOR_STOP: "d0b6b0e12bbe4175ce8ba70fcab58f73b5f51bf3a067046cd2cbd9e22a8e5f6b",
    PRIOR_VALIDATION: "52055cee342d2cfaa5bed548c64000d3adbf6eed1243d8c7c4ec268cd6c0eeb0",
}

EXCLUSIONS = {
    "STOLFI_BEST_1163": "NONSTRICT_ZERO_ALTERNATIVE",
    "STOLFI_BEST_1267": "MISSING_CONSENSUS_LOCUS",
}
EXPECTED_FEATURE_HASH = "1691d552609b5651f6f0505795a747bc15c3206486252d8b9f9c134e85dfd65a"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def feature_hash(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(values) + "\n").encode()).hexdigest()


def group_features(row: dict[str, str]) -> set[str]:
    family = row["family_surface"]
    result: set[str] = {f"F:W:{family}"}
    for n in range(1, min(3, len(family)) + 1):
        result.update(
            f"F:N:{n}:{family[start:start+n]}"
            for start in range(len(family) - n + 1)
        )
        result.add(f"F:P:{n}:{family[:n]}")
        result.add(f"F:S:{n}:{family[-n:]}")
    versions = [row[field].split() for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
    if versions[0] == versions[1] == versions[2]:
        member = versions[0]
        result.add("M:W:" + " ".join(member))
        for n in range(1, min(3, len(member)) + 1):
            result.update(
                f"M:N:{n}:" + " ".join(member[start:start+n])
                for start in range(len(member) - n + 1)
            )
            result.add(f"M:P:{n}:" + " ".join(member[:n]))
            result.add(f"M:S:{n}:" + " ".join(member[-n:]))
    return result


def validated_groups(
    item: dict[str, str], lookup: dict[str, list[dict[str, str]]]
) -> tuple[list[dict[str, str]], str | None]:
    locus = item["mapped_locus"]
    current = sorted(lookup.get(locus, ()), key=lambda row: int(row["consensus_group_index"]))
    if not current:
        return [], "MISSING_LOCUS"
    if (
        {row["locus"] for row in current} != {locus}
        or {row["page"] for row in current} != {item["source_page"]}
        or any(row["kind"] != "L" or row["grammar_scope"] != "DIAGNOSTIC_NONPROSE" for row in current)
        or any(row["strict_zero_alternative"] != "1" for row in current)
        or [int(row["consensus_group_index"]) for row in current] != list(range(1, len(current) + 1))
        or {int(row["consensus_group_count"]) for row in current} != {len(current)}
    ):
        return [], "STRUCTURE"
    for row in current:
        family = row["family_surface"]
        versions = [row[field].split() for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
        if not family or any(not version or "".join(code[0] for code in version) != family for version in versions):
            return [], "CODE_FAMILY"
    return current, None


def build_features(
    panel: list[dict[str, str]], lookup: dict[str, list[dict[str, str]]]
) -> tuple[dict[str, set[str]], list[str]]:
    output: dict[str, set[str]] = {}
    problems: list[str] = []
    for item in panel:
        current, problem = validated_groups(item, lookup)
        if problem:
            problems.append(f"{item['source_record_id']}:{problem}")
            continue
        feature_set: set[str] = set()
        for group in current:
            feature_set.update(group_features(group))
        if not feature_set:
            problems.append(f"{item['source_record_id']}:NO_FEATURES")
        else:
            output[item["source_record_id"]] = feature_set
    return output, problems


def effect(
    feature: str,
    panel: list[dict[str, str]],
    features: dict[str, set[str]],
    dark_ids: set[str],
) -> float:
    dark = [int(feature in features[item["source_record_id"]]) for item in panel if item["source_record_id"] in dark_ids]
    light = [int(feature in features[item["source_record_id"]]) for item in panel if item["source_record_id"] not in dark_ids]
    if not dark or not light:
        raise AssertionError("empty state partition")
    return sum(dark) / len(dark) - sum(light) / len(light)


def select(
    vocabulary: list[str],
    split: dict[str, list[dict[str, str]]],
    features: dict[str, set[str]],
    dark_ids: set[str],
) -> tuple[float, float, str, float, float]:
    scored = []
    for term in vocabulary:
        d89 = effect(term, split["f89"], features, dark_ids)
        d100 = effect(term, split["f100"], features, dark_ids)
        scored.append((min(d89, d100), (d89 + d100) / 2, term, d89, d100))
    return min(scored, key=lambda value: (-value[0], -value[1], value[2].encode()))


def render_report(result: dict[str, object]) -> str:
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


def write_once(path: Path, data: str) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        handle.write(data)


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite of target outputs")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"input hash mismatch: {path}")
    panel_validation = json.loads(PANEL_VALIDATION.read_text(encoding="utf-8"))
    group_validation = json.loads(GROUPS_VALIDATION.read_text(encoding="utf-8"))
    prior_stop = json.loads(PRIOR_STOP.read_text(encoding="utf-8"))
    prior_validation = json.loads(PRIOR_VALIDATION.read_text(encoding="utf-8"))
    if panel_validation.get("status") != "PASS_SOURCE_IMAGE_BINDINGS_AND_GATE_RECONSTRUCTION":
        raise SystemExit("ownership validation not passed")
    if not str(group_validation.get("status", "")).startswith("PASS"):
        raise SystemExit("consensus validation not passed")
    if prior_stop.get("decision") != "STOP_UNPOWERED_BEFORE_STATE_SCORE":
        raise SystemExit("prior capacity stop not bound")
    if prior_validation.get("validated_decision") != "STOP_UNPOWERED_BEFORE_STATE_SCORE":
        raise SystemExit("prior stop validation not bound")

    ownership = [item for item in rows(PANEL) if item["eligible"] == "1"]
    lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for group in rows(GROUPS):
        lookup[group["locus"]].append(group)
    by_id = {item["source_record_id"]: item for item in ownership}
    exclusion_checks = {
        "STOLFI_BEST_1163": bool(lookup.get(by_id["STOLFI_BEST_1163"]["mapped_locus"]))
        and any(row["strict_zero_alternative"] == "0" for row in lookup[by_id["STOLFI_BEST_1163"]["mapped_locus"]]),
        "STOLFI_BEST_1267": not lookup.get(by_id["STOLFI_BEST_1267"]["mapped_locus"]),
    }
    complete = [item for item in ownership if item["source_record_id"] not in EXCLUSIONS]
    discovery = [item for item in complete if item["physical_folio"] in ("f89", "f100")]
    transfer = [item for item in complete if item["physical_folio"] == "f102"]
    split = {folio: [item for item in discovery if item["physical_folio"] == folio] for folio in ("f89", "f100")}
    margins = {folio: Counter(item["root_state"] for item in panel) for folio, panel in split.items()}

    discovery_features, problems = build_features(discovery, lookup)
    transfer_structure_problems = []
    for item in transfer:
        _, problem = validated_groups(item, lookup)
        if problem:
            transfer_structure_problems.append(f"{item['source_record_id']}:{problem}")
    universe = sorted(set().union(*discovery_features.values()), key=lambda term: term.encode()) if discovery_features else []
    vocabulary = []
    for term in universe:
        if sum(term in discovery_features[item["source_record_id"]] for item in discovery) < 3:
            continue
        if all(
            0 < sum(term in discovery_features[item["source_record_id"]] for item in split[folio]) < len(split[folio])
            for folio in ("f89", "f100")
        ):
            vocabulary.append(term)
    orbit = len(list(itertools.combinations(range(9), 2))) * len(list(itertools.combinations(range(8), 2)))
    capacity = {
        "ownership_eligible_labels": len(ownership),
        "exclusions": EXCLUSIONS,
        "exclusion_contract_pass": exclusion_checks,
        "complete_labels": len(complete),
        "discovery_labels": len(discovery),
        "transfer_labels": len(transfer),
        "discovery_margins": {folio: dict(sorted(counts.items())) for folio, counts in margins.items()},
        "transfer_states": dict(sorted(Counter(item["root_state"] for item in transfer).items())),
        "reconstruction_problems": problems,
        "transfer_structure_problems": transfer_structure_problems,
        "unfiltered_features": len(universe),
        "filtered_features": len(vocabulary),
        "filtered_feature_sha256": feature_hash(vocabulary) if vocabulary else None,
        "exact_worlds": orbit,
    }
    capacity_pass = (
        len(ownership) == 21
        and set(by_id) >= set(EXCLUSIONS)
        and all(exclusion_checks.values())
        and len(complete) == 19
        and len(discovery) == 17
        and len(transfer) == 2
        and margins == {"f89": Counter({"LIGHT": 7, "DARK": 2}), "f100": Counter({"LIGHT": 6, "DARK": 2})}
        and Counter(item["root_state"] for item in transfer) == {"DARK": 2}
        and not problems
        and not transfer_structure_problems
        and len(discovery_features) == 17
        and len(universe) == 306
        and len(vocabulary) == 48
        and feature_hash(vocabulary) == EXPECTED_FEATURE_HASH
        and orbit == 1008
    )
    common = {
        "experiment": "PRC001R2_SOURCE_CONTRACT_CORRECTED_TARGET",
        "inputs": {str(path.relative_to(BASE)): expected for path, expected in EXPECTED.items()},
        "capacity": capacity,
    }
    if not capacity_pass:
        result = {
            **common,
            "status": "STOP_UNPOWERED_BEFORE_STATE_SCORE",
            "decision": "STOP_UNPOWERED_BEFORE_STATE_SCORE",
            "gates": {"capacity": False},
            "claim_ceiling": "No formal marker or semantic result was scored.",
        }
        write_once(OUT, json.dumps(result, indent=2, sort_keys=True) + "\n")
        write_once(REPORT, render_report(result))
        return

    observed_dark = {item["source_record_id"] for item in discovery if item["root_state"] == "DARK"}
    winning_score, winning_mean, winning_term, d89, d100 = select(vocabulary, split, discovery_features, observed_dark)
    ids89 = [item["source_record_id"] for item in split["f89"]]
    ids100 = [item["source_record_id"] for item in split["f100"]]
    maxima = []
    for dark89 in itertools.combinations(ids89, 2):
        for dark100 in itertools.combinations(ids100, 2):
            maxima.append(select(vocabulary, split, discovery_features, set(dark89) | set(dark100))[0])
    if len(maxima) != 1008:
        raise AssertionError("null orbit changed")
    tail = sum(value >= winning_score for value in maxima)
    exact_p = tail / len(maxima)

    # The discovery winner is fixed before f102 feature presence is constructed.
    transfer_features, transfer_problems = build_features(transfer, lookup)
    presence = {
        item["source_record_id"]: winning_term in transfer_features.get(item["source_record_id"], set())
        for item in transfer
    }
    deletions = {}
    for removed in sorted(observed_dark):
        reduced_dark = observed_dark - {removed}
        reduced_split = {
            folio: [item for item in panel if item["source_record_id"] != removed]
            for folio, panel in split.items()
        }
        deletions[removed] = {
            "f89_delta": effect(winning_term, reduced_split["f89"], discovery_features, reduced_dark),
            "f100_delta": effect(winning_term, reduced_split["f100"], discovery_features, reduced_dark),
        }
    gates = {
        "capacity": True,
        "exact_max_feature_p_at_most_0_01": exact_p <= 0.01,
        "winning_score_at_least_0_50": winning_score >= 0.50,
        "both_discovery_folio_deltas_at_least_0_50": min(d89, d100) >= 0.50,
        "winner_present_in_both_f102_dark_labels": not transfer_problems and all(presence.values()),
        "all_discovery_dark_deletions_retain_both_deltas_at_least_0_50": all(
            min(values.values()) >= 0.50 for values in deletions.values()
        ),
        "all_reading_consensus_reconstruction": not problems and not transfer_problems,
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
    result = {
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
            "transfer_reconstruction_problems": transfer_problems,
            "dark_deletion_deltas": deletions,
        },
        "gates": gates,
        "claim_ceiling": claim,
    }
    write_once(OUT, json.dumps(result, indent=2, sort_keys=True) + "\n")
    write_once(REPORT, render_report(result))


if __name__ == "__main__":
    main()
