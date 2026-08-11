#!/usr/bin/env python3
"""Independent nonimporting reconstruction of the PRC001 target."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "PRC001_DARK_ROOT_MARKER_TARGET_SPEC.md"
RUNNER = BASE / "run_prc001_dark_root_marker_target.py"
PANEL = RESULTS / "pharma_root_color_native_visual_ownership.tsv"
PANEL_VALIDATION = RESULTS / "pharma_root_color_native_visual_ownership_validation.json"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
GROUPS_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
PRODUCTION = RESULTS / "prc001_dark_root_marker_target.json"
PRODUCTION_REPORT = RESULTS / "prc001_dark_root_marker_target_report.md"
OUT = RESULTS / "prc001_dark_root_marker_target_validation.json"
REPORT = RESULTS / "prc001_dark_root_marker_target_validation.md"

HASHES = {
    SPEC: "ebb43c0f45fefa91f01400ab646de409741e64d34f1c7b763f708bae9952253e",
    RUNNER: "9d791f339e9d1454265aa5d4f1c81c033d93959a19983b8b7b1f02773e9aa9c0",
    PANEL: "eb1b5563fa0d775a662f27b566d9c1acd75eba59fdf690e3fc8ac9ab9e225a7b",
    PANEL_VALIDATION: "2eb90320045ac0742294f649f73ec4beff00028ca7e94523490af3535d6da03c",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    GROUPS_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def feature_hash(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(values) + "\n").encode()).hexdigest()


def one_group(row: dict[str, str]) -> set[str]:
    family = row["family_surface"]
    result: set[str] = {f"F:W:{family}"}
    for n in (1, 2, 3):
        if n > len(family):
            continue
        result.add(f"F:P:{n}:{family[:n]}")
        result.add(f"F:S:{n}:{family[-n:]}")
        for start in range(0, len(family) - n + 1):
            result.add(f"F:N:{n}:{family[start:start+n]}")
    versions = tuple(tuple(row[field].split()) for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes"))
    if versions[0] == versions[1] == versions[2]:
        member = versions[0]
        result.add("M:W:" + " ".join(member))
        for n in (1, 2, 3):
            if n > len(member):
                continue
            result.add(f"M:P:{n}:" + " ".join(member[:n]))
            result.add(f"M:S:{n}:" + " ".join(member[-n:]))
            for start in range(0, len(member) - n + 1):
                result.add(f"M:N:{n}:" + " ".join(member[start:start+n]))
    return result


def reconstruct(
    panel: list[dict[str, str]], index: dict[str, list[dict[str, str]]]
) -> tuple[dict[str, set[str]], list[str]]:
    output: dict[str, set[str]] = {}
    failures: list[str] = []
    for item in panel:
        source_id, locus = item["source_record_id"], item["mapped_locus"]
        current = sorted(index.get(locus, ()), key=lambda value: int(value["consensus_group_index"]))
        structural = bool(current)
        structural &= {value["page"] for value in current} == {item["source_page"]}
        structural &= all(value["kind"] == "L" and value["grammar_scope"] == "LABEL" for value in current)
        structural &= all(value["strict_zero_alternative"] == "1" for value in current)
        structural &= [int(value["consensus_group_index"]) for value in current] == list(range(1, len(current) + 1))
        structural &= {int(value["consensus_group_count"]) for value in current} == {len(current)}
        if not structural:
            failures.append(source_id + (":MISSING_LOCUS" if not current else ":STRUCTURE"))
            continue
        feature_set: set[str] = set()
        valid = True
        for group in current:
            family = group["family_surface"]
            for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes"):
                code_list = group[field].split()
                if not code_list or "".join(code[0] for code in code_list) != family:
                    valid = False
            feature_set |= one_group(group)
        if not valid or not feature_set:
            failures.append(source_id + ":CODE_FAMILY")
        else:
            output[source_id] = feature_set
    return output, failures


def effect(feature: str, items: list[dict[str, str]], feature_sets: dict[str, set[str]], dark: set[str]) -> float:
    dark_values, light_values = [], []
    for item in items:
        value = int(feature in feature_sets[item["source_record_id"]])
        (dark_values if item["source_record_id"] in dark else light_values).append(value)
    if not dark_values or not light_values:
        raise AssertionError("empty state")
    return sum(dark_values) / len(dark_values) - sum(light_values) / len(light_values)


def select(
    vocabulary: list[str], split: dict[str, list[dict[str, str]]],
    feature_sets: dict[str, set[str]], dark: set[str],
) -> tuple[float, float, str, float, float]:
    candidates = []
    for term in vocabulary:
        d89 = effect(term, split["f89"], feature_sets, dark)
        d100 = effect(term, split["f100"], feature_sets, dark)
        candidates.append((min(d89, d100), (d89 + d100) / 2, term, d89, d100))
    return min(candidates, key=lambda value: (-value[0], -value[1], value[2].encode()))


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    checks: list[str] = []
    for path, expected in HASHES.items():
        if sha(path) != expected:
            raise AssertionError(f"hash:{path}")
        checks.append("hash_" + path.name)
    if not PRODUCTION.exists() or not PRODUCTION_REPORT.exists():
        raise SystemExit("target outputs absent")

    panel = [item for item in rows(PANEL) if item["eligible"] == "1"]
    discovery = [item for item in panel if item["physical_folio"] in ("f89", "f100")]
    transfer = [item for item in panel if item["physical_folio"] == "f102"]
    split = {folio: [item for item in discovery if item["physical_folio"] == folio] for folio in ("f89", "f100")}

    lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for group in rows(GROUPS):
        lookup[group["locus"]].append(group)
    feature_sets, failures = reconstruct(discovery, lookup)
    universe = sorted(set().union(*feature_sets.values()), key=lambda item: item.encode()) if feature_sets else []
    vocabulary = []
    for term in universe:
        if sum(term in feature_sets[item["source_record_id"]] for item in discovery) < 3:
            continue
        if all(
            0 < sum(term in feature_sets[item["source_record_id"]] for item in split[folio]) < len(split[folio])
            for folio in ("f89", "f100")
        ):
            vocabulary.append(term)

    margins = {folio: Counter(item["root_state"] for item in split[folio]) for folio in split}
    capacity = {
        "eligible_labels": len(panel), "discovery_labels": len(discovery),
        "transfer_labels": len(transfer),
        "discovery_margins": {folio: dict(sorted(value.items())) for folio, value in margins.items()},
        "transfer_states": dict(sorted(Counter(item["root_state"] for item in transfer).items())),
        "reconstruction_problems": failures,
        "unfiltered_features": len(universe), "filtered_features": len(vocabulary),
        "filtered_feature_sha256": feature_hash(vocabulary) if vocabulary else None,
        "exact_worlds": 1540,
    }
    capacity_pass = (
        len(panel) == 21 and len(discovery) == 19 and len(transfer) == 2
        and margins == {"f89": Counter({"LIGHT": 9, "DARK": 2}), "f100": Counter({"LIGHT": 6, "DARK": 2})}
        and Counter(item["root_state"] for item in transfer) == {"DARK": 2}
        and not failures and len(feature_sets) == 19 and len(vocabulary) >= 4
    )
    production = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    if not capacity_pass:
        expected = {
            "experiment": "PRC001_DARK_ROOT_MARKER_TARGET",
            "status": "STOP_UNPOWERED_BEFORE_STATE_SCORE",
            "decision": "STOP_UNPOWERED_BEFORE_STATE_SCORE",
            "inputs": {str(path.relative_to(BASE)): value for path, value in HASHES.items() if path != RUNNER},
            "capacity": capacity,
            "gates": {"capacity": False},
            "claim_ceiling": "No formal marker or semantic result was scored.",
        }
        if production != expected:
            raise AssertionError("capacity stop mismatch")
        checks.append("capacity_stop_exact")
    else:
        dark = {item["source_record_id"] for item in discovery if item["root_state"] == "DARK"}
        observed = select(vocabulary, split, feature_sets, dark)
        winning_score, winning_mean, winning_term, d89, d100 = observed
        ids89 = [item["source_record_id"] for item in split["f89"]]
        ids100 = [item["source_record_id"] for item in split["f100"]]
        maxima = []
        for left in itertools.combinations(ids89, 2):
            for right in itertools.combinations(ids100, 2):
                maxima.append(select(vocabulary, split, feature_sets, set(left) | set(right))[0])
        tail = sum(value >= winning_score for value in maxima)
        exact_p = tail / 1540

        transfer_sets, transfer_failures = reconstruct(transfer, lookup)
        presence = {
            item["source_record_id"]: winning_term in transfer_sets.get(item["source_record_id"], set())
            for item in transfer
        }
        deletions = {}
        for removed in sorted(dark):
            reduced = {folio: [item for item in items if item["source_record_id"] != removed] for folio, items in split.items()}
            remaining_dark = dark - {removed}
            deletions[removed] = {
                "f89_delta": effect(winning_term, reduced["f89"], feature_sets, remaining_dark),
                "f100_delta": effect(winning_term, reduced["f100"], feature_sets, remaining_dark),
            }
        gates = {
            "capacity": True,
            "exact_max_feature_p_at_most_0_01": exact_p <= .01,
            "winning_score_at_least_0_50": winning_score >= .50,
            "both_discovery_folio_deltas_at_least_0_50": min(d89, d100) >= .50,
            "winner_present_in_both_f102_dark_labels": not transfer_failures and all(presence.values()),
            "all_discovery_dark_deletions_retain_both_deltas_at_least_0_50": all(min(value.values()) >= .50 for value in deletions.values()),
            "all_reading_consensus_reconstruction": not failures and not transfer_failures,
        }
        decision = (
            "PASS_RECURRENT_FORMAL_FEATURE_ASSOCIATED_WITH_HUMAN_DARK_ROOT_STATE"
            if all(gates.values()) else
            "FINAL_NONCONFIRMATION_NO_RECURRENT_DARK_ASSOCIATED_FORMAL_MARKER"
        )
        expected_target = {
            "winning_feature": winning_term,
            "winning_score": winning_score,
            "winning_mean_delta": winning_mean,
            "discovery_folio_deltas": {"f89": d89, "f100": d100},
            "exact_p": exact_p,
            "inclusive_tail_count": tail,
            "null_worlds": 1540,
            "null_maxima": maxima,
            "null_maxima_sha256": hashlib.sha256(json.dumps(maxima, separators=(",", ":")).encode()).hexdigest(),
            "transfer_presence": presence,
            "transfer_reconstruction_problems": transfer_failures,
            "dark_deletion_deltas": deletions,
        }
        checks.extend([
            "capacity_reconstructed", "feature_universe_reconstructed", "observed_winner_reconstructed",
            "all_1540_null_worlds_reconstructed", "transfer_reconstructed", "deletions_reconstructed",
        ])
        if production["capacity"] != capacity or production["target"] != expected_target or production["gates"] != gates:
            raise AssertionError("numeric reconstruction mismatch")
        if production["status"] != decision or production["decision"] != decision:
            raise AssertionError("decision mismatch")
        checks.append("production_numeric_and_decision_exact")

    report = PRODUCTION_REPORT.read_text(encoding="utf-8")
    if production["status"] not in report or production["decision"] not in report:
        raise AssertionError("report status")
    checks.append("report_status_and_decision")
    result = {
        "experiment": "PRC001_DARK_ROOT_MARKER_TARGET_VALIDATION",
        "status": "PASS_INDEPENDENT_EXACT_RECONSTRUCTION",
        "check_count": len(checks), "checks": checks,
        "inputs": {
            "runner_sha256": HASHES[RUNNER],
            "production_sha256": sha(PRODUCTION),
            "production_report_sha256": sha(PRODUCTION_REPORT),
        },
        "validated_decision": production["decision"],
        "claim_ceiling": production["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    detail = (
        "The independent implementation reconstructed the exact capacity stop before any "
        "feature or conditional world was scored."
        if production["decision"] == "STOP_UNPOWERED_BEFORE_STATE_SCORE" else
        "The independent implementation reconstructed the frozen feature universe, all 1,540 "
        "conditional worlds, transfer panel, robustness gates, and decision."
    )
    REPORT.write_text(
        "# PRC001 target validation\n\n"
        f"Status: **{result['status']}**\n\n"
        f"{detail} Validated decision: **{production['decision']}**.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
