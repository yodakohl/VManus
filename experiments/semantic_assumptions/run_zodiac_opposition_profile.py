#!/usr/bin/env python3
"""Exact opposition-matching controls and target for public zodiac circular text."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

B = Path(__file__).resolve().parent
R = B / "results"
METHOD = B / "ZODIAC_OPPOSITION_PROFILE_METHOD.md"
ALIGN = R / "source_sta_group_alignment.tsv"
META = R / "source_separator_transcription.tsv"
PAGES = R / "public_voynich_nu_page_annotations_v2.tsv"
CONTROLS = R / "zodiac_opposition_profile_controls.json"
CONTROL_REPORT = R / "zodiac_opposition_profile_controls_report.md"
OUT = R / "zodiac_opposition_profile.json"
REPORT = R / "zodiac_opposition_profile_report.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
VIEWS = tuple([f"FAMILY_N{n}" for n in range(2, 6)] + [f"MEMBER_N{n}" for n in range(1, 4)] + ["FAMILY_GROUP"])
TOL = 1e-15
SIGN_RE = re.compile(r"\bemblem of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b", re.I)
TARGET_SIGNS = ("ARIES", "GEMINI", "LIBRA", "PISCES", "SAGITTARIUS", "SCORPIUS", "TAURUS", "VIRGO")
OPPOSITIONS = (("ARIES", "LIBRA"), ("GEMINI", "SAGITTARIUS"), ("PISCES", "VIRGO"), ("SCORPIUS", "TAURUS"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def pair_key(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))


def matching_key(pairs: tuple[tuple[str, str], ...] | list[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(pair_key(*pair) for pair in pairs))


def all_matchings(nodes: tuple[str, ...]) -> list[tuple[tuple[str, str], ...]]:
    if not nodes:
        return [tuple()]
    first = nodes[0]
    output = []
    for index in range(1, len(nodes)):
        second = nodes[index]
        remainder = nodes[1:index] + nodes[index+1:]
        for rest in all_matchings(remainder):
            output.append(matching_key(((first, second),) + rest))
    return sorted(set(output))


def evaluate(matrices: dict[str, dict[str, dict[tuple[str, str], float]]], nodes: tuple[str, ...], observed_pairs: tuple[tuple[str, str], ...]) -> dict[str, object]:
    pairs = [pair_key(nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i + 1, len(nodes))]
    standardized: dict[str, dict[str, dict[tuple[str, str], float]]] = defaultdict(lambda: defaultdict(dict))
    diagnostics = {}
    for edition in EDITIONS:
        diagnostics[edition] = {}
        for view in VIEWS:
            values = [matrices[edition][view][pair] for pair in pairs]
            mean = statistics.fmean(values)
            sd = math.sqrt(statistics.fmean((value - mean) ** 2 for value in values))
            diagnostics[edition][view] = {"mean": mean, "population_sd": sd}
            if not math.isfinite(sd) or sd <= 0:
                return {"eligible": False, "reason": f"zero_or_nonfinite_sd:{edition}:{view}"}
            for pair, value in zip(pairs, values):
                standardized[edition][view][pair] = (value - mean) / sd
    matchings = all_matchings(nodes)
    observed = matching_key(observed_pairs)
    if observed not in matchings:
        raise AssertionError("observed relation is not a perfect matching")
    orbit = []
    for matching in matchings:
        edition_scores = {
            edition: statistics.fmean(standardized[edition][view][pair] for view in VIEWS for pair in matching)
            for edition in EDITIONS
        }
        orbit.append({"matching": [list(pair) for pair in matching], "edition_scores": edition_scores, "robust_score": min(edition_scores.values())})
    observed_row = next(row for row in orbit if matching_key([tuple(pair) for pair in row["matching"]]) == observed)
    observed_score = float(observed_row["robust_score"])
    inclusive_rank = 1 + sum(float(row["robust_score"]) > observed_score + TOL for row in orbit)
    tied = sum(abs(float(row["robust_score"]) - observed_score) <= TOL for row in orbit)
    pair_contributions = {
        edition: {"|".join(pair): statistics.fmean(standardized[edition][view][pair] for view in VIEWS) for pair in observed}
        for edition in EDITIONS
    }
    positive_support = {edition: sum(value > 0 for value in pair_contributions[edition].values()) for edition in EDITIONS}
    return {
        "eligible": True,
        "matching_count": len(matchings),
        "observed_matching": [list(pair) for pair in observed],
        "observed_edition_scores": observed_row["edition_scores"],
        "observed_robust_score": observed_score,
        "inclusive_rank": inclusive_rank,
        "tied": tied,
        "exact_one_sided_p": sum(float(row["robust_score"]) >= observed_score - TOL for row in orbit) / len(orbit),
        "positive_pair_support": positive_support,
        "observed_pair_contributions": pair_contributions,
        "standardization_diagnostics": diagnostics,
        "orbit_sha256": json_sha(orbit),
        "orbit_robust_scores": [float(row["robust_score"]) for row in orbit],
    }


def synthetic_matrices(nodes: tuple[str, ...], favored: tuple[tuple[str, str], ...], background: float = 0.1, foreground: float = 0.9) -> dict[str, dict[str, dict[tuple[str, str], float]]]:
    favored_set = set(matching_key(favored))
    pairs = [pair_key(nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i + 1, len(nodes))]
    return {
        edition: {
            view: {pair: (foreground if pair in favored_set else background) for pair in pairs}
            for view in VIEWS
        }
        for edition in EDITIONS
    }


def run_controls() -> None:
    if CONTROLS.exists() or CONTROL_REPORT.exists():
        raise SystemExit("refusing overwrite")
    nodes = tuple(f"S{index}" for index in range(8))
    truth = (("S0", "S1"), ("S2", "S3"), ("S4", "S5"), ("S6", "S7"))
    alternative = (("S0", "S2"), ("S1", "S3"), ("S4", "S6"), ("S5", "S7"))
    planted_matrices = synthetic_matrices(nodes, truth)
    planted = evaluate(planted_matrices, nodes, truth)

    constant_matrices = synthetic_matrices(nodes, truth, background=0.5, foreground=0.5)
    constant = evaluate(constant_matrices, nodes, truth)

    one_pair_matrices = synthetic_matrices(nodes, (("S0", "S1"),))
    one_pair = evaluate(one_pair_matrices, nodes, truth)

    disagreement_matrices = synthetic_matrices(nodes, truth)
    alternative_rf = synthetic_matrices(nodes, alternative)["RF1b"]
    disagreement_matrices["RF1b"] = alternative_rf
    disagreement = evaluate(disagreement_matrices, nodes, truth)

    affine_matrices = {
        edition: {
            view: {pair: value * (1.3 + .1 * view_index) + (edition_index - 2.0) for pair, value in planted_matrices[edition][view].items()}
            for view_index, view in enumerate(VIEWS)
        }
        for edition_index, edition in enumerate(EDITIONS)
    }
    affine = evaluate(affine_matrices, nodes, truth)

    mapping = {node: nodes[-index - 1] for index, node in enumerate(nodes)}
    relabeled_matrices = {
        edition: {
            view: {pair_key(mapping[pair[0]], mapping[pair[1]]): value for pair, value in planted_matrices[edition][view].items()}
            for view in VIEWS
        }
        for edition in EDITIONS
    }
    relabeled_truth = tuple(pair_key(mapping[left], mapping[right]) for left, right in truth)
    relabeled = evaluate(relabeled_matrices, tuple(sorted(mapping.values())), relabeled_truth)

    checks = {
        "exact_105_matchings": planted.get("matching_count") == 105,
        "distributed_plant_unique_rank_one": planted.get("inclusive_rank") == planted.get("tied") == 1,
        "distributed_plant_all_pairs_positive": all(value == 4 for value in planted.get("positive_pair_support", {}).values()),
        "constant_null_ineligible": constant == {"eligible": False, "reason": "zero_or_nonfinite_sd:ZL3b:FAMILY_N2"},
        "one_pair_rejected_by_support": any(value < 3 for value in one_pair.get("positive_pair_support", {}).values()),
        "reading_disagreement_rejected": disagreement.get("exact_one_sided_p", 1.0) > .05 or any(value <= 0 for value in disagreement.get("observed_edition_scores", {}).values()),
        "positive_affine_rank_invariant": affine.get("inclusive_rank") == planted.get("inclusive_rank") and affine.get("tied") == planted.get("tied") and abs(float(affine.get("exact_one_sided_p", 1)) - float(planted.get("exact_one_sided_p", 0))) <= TOL,
        "sign_relabeling_invariant": relabeled.get("inclusive_rank") == planted.get("inclusive_rank") and relabeled.get("tied") == planted.get("tied") and abs(float(relabeled.get("observed_robust_score", 0)) - float(planted.get("observed_robust_score", 1))) <= 1e-12,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {
        "experiment": "ZODIAC_OPPOSITION_PROFILE_CONTROLS", "status": status,
        "inputs": {path.name: sha(path) for path in (METHOD, Path(__file__))},
        "checks": checks,
        "summaries": {name: value for name, value in (("planted", planted), ("constant", constant), ("one_pair", one_pair), ("reading_disagreement", disagreement), ("affine", affine), ("relabeled", relabeled))},
        "target_accessed": False,
        "claim_ceiling": "Synthetic scorer validation only; no manuscript opposition result or meaning.",
    }
    CONTROLS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CONTROL_REPORT.write_text(
        "# Zodiac-opposition profile controls\n\n"
        f"Status: **{status}**\n\n"
        "The exact 105-matching scorer recovers the distributed plant, rejects constant, one-pair, and reading-disagreement controls, and is invariant to positive affine transforms and sign relabeling. No manuscript source was opened.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "checks": checks}, sort_keys=True))


def feature_values(row: dict[str, str]) -> dict[str, list[str]]:
    families = list(row["primary_sta_families"])
    members = row["primary_sta_codes"].split()
    result = {}
    for size in range(2, 6):
        result[f"FAMILY_N{size}"] = ["".join(families[start:start+size]) for start in range(len(families)-size+1)]
    for size in range(1, 4):
        result[f"MEMBER_N{size}"] = ["-".join(members[start:start+size]) for start in range(len(members)-size+1)]
    result["FAMILY_GROUP"] = [row["primary_sta_families"]]
    return result


def weighted_jaccard(left: Counter[str], right: Counter[str]) -> float:
    inventory = sorted(set(left).union(right))
    denominator = sum(max(left[item], right[item]) for item in inventory)
    return sum(min(left[item], right[item]) for item in inventory) / denominator if denominator else 0.0


def profile_matrices(counters: dict[tuple[str, str, str, str], Counter[str]], role: str, mask: str, sign_pages: dict[str, list[str]]) -> tuple[dict[str, dict[str, dict[tuple[str, str], float]]], dict[str, dict[str, int]]]:
    sign_counters = {}
    counts = {}
    for sign in TARGET_SIGNS:
        counts[sign] = {}
        for edition in EDITIONS:
            counts[sign][edition] = sum(sum(counters[(role, mask, page, edition, "FAMILY_GROUP")].values()) for page in sign_pages[sign])
            for view in VIEWS:
                combined: Counter[str] = Counter()
                for page in sign_pages[sign]:
                    combined.update(counters[(role, mask, page, edition, view)])
                sign_counters[(sign, edition, view)] = combined
    matrices = {
        edition: {
            view: {
                pair_key(TARGET_SIGNS[i], TARGET_SIGNS[j]): weighted_jaccard(sign_counters[(TARGET_SIGNS[i], edition, view)], sign_counters[(TARGET_SIGNS[j], edition, view)])
                for i in range(len(TARGET_SIGNS)) for j in range(i + 1, len(TARGET_SIGNS))
            }
            for view in VIEWS
        }
        for edition in EDITIONS
    }
    return matrices, counts


def run_target() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    if not CONTROLS.exists():
        raise SystemExit("controls absent")
    controls = json.loads(CONTROLS.read_text())
    expected_control_inputs = {path.name: sha(path) for path in (METHOD, Path(__file__))}
    if controls.get("status") != "PASS" or controls.get("inputs") != expected_control_inputs or controls.get("target_accessed") is not False:
        raise SystemExit("control binding failed")

    public_rows = read_tsv(PAGES)
    page_signs = {}
    for row in public_rows:
        match = SIGN_RE.search(row["illustrations"])
        if match:
            page_signs[row["page"]] = match.group(1).upper()
    if len(page_signs) != 12 or any(row["tentative_identifications_are_role_evidence"] != "0" for row in public_rows):
        raise AssertionError("public zodiac source gate changed")
    sign_pages = {sign: sorted(page for page, value in page_signs.items() if value == sign) for sign in TARGET_SIGNS}
    expected_counts = {"ARIES": 2, "TAURUS": 2, "GEMINI": 1, "LIBRA": 1, "PISCES": 1, "SAGITTARIUS": 1, "SCORPIUS": 1, "VIRGO": 1}
    if {sign: len(pages) for sign, pages in sign_pages.items()} != expected_counts:
        raise AssertionError("target sign-page panel changed")

    meta_rows = read_tsv(META)
    metadata = {row["source_group_id"]: row for row in meta_rows}
    if len(metadata) != len(meta_rows):
        raise AssertionError("duplicate metadata group ID")
    counters: dict[tuple[str, str, str, str, str], Counter[str]] = defaultdict(Counter)
    target_groups = 0
    alternative_groups = 0
    for row in read_tsv(ALIGN):
        info = metadata.get(row["source_group_id"])
        if info is None:
            raise AssertionError("alignment group missing metadata")
        page = info["page"]
        if page not in page_signs or page_signs[page] not in TARGET_SIGNS or info["kind"] not in {"C", "L"}:
            continue
        target_groups += 1
        if int(row["alternative_site_count"]):
            alternative_groups += 1
            continue
        values = feature_values(row)
        for role in (info["kind"],):
            for mask in ("FULL", "NO_BABA"):
                if mask == "NO_BABA" and row["primary_sta_families"].endswith("BABA"):
                    continue
                for view, features in values.items():
                    counters[(role, mask, page, row["edition"], view)].update(features)

    evaluations = {}
    matrices_by_key = {}
    sign_group_counts = {}
    for role in ("C", "L"):
        evaluations[role] = {}
        sign_group_counts[role] = {}
        for mask in ("FULL", "NO_BABA"):
            matrices, counts = profile_matrices(counters, role, mask, sign_pages)
            matrices_by_key[(role, mask)] = matrices
            sign_group_counts[role][mask] = counts
            evaluations[role][mask] = evaluate(matrices, TARGET_SIGNS, OPPOSITIONS)

    deletions = {mask: {} for mask in ("FULL", "NO_BABA")}
    for mask in deletions:
        matrices = matrices_by_key[("C", mask)]
        for deleted in OPPOSITIONS:
            remaining_nodes = tuple(node for node in TARGET_SIGNS if node not in deleted)
            remaining_pairs = tuple(pair for pair in OPPOSITIONS if pair != deleted)
            deletions[mask]["|".join(pair_key(*deleted))] = evaluate(matrices, remaining_nodes, remaining_pairs)

    full = evaluations["C"]["FULL"]
    masked = evaluations["C"]["NO_BABA"]
    gates = {
        "controls_bound_and_pass": True,
        "exact_105_matchings": full.get("matching_count") == masked.get("matching_count") == 105,
        "full_exact_p_at_most_005": full.get("exact_one_sided_p", 1.0) <= .05,
        "full_all_readings_positive": all(value > 0 for value in full.get("observed_edition_scores", {}).values()),
        "full_three_of_four_pair_support_every_reading": all(value >= 3 for value in full.get("positive_pair_support", {}).values()),
        "masked_exact_p_at_most_005": masked.get("exact_one_sided_p", 1.0) <= .05,
        "masked_all_readings_positive": all(value > 0 for value in masked.get("observed_edition_scores", {}).values()),
        "masked_three_of_four_pair_support_every_reading": all(value >= 3 for value in masked.get("positive_pair_support", {}).values()),
        "all_full_pair_deletions_rank_at_most_2": all(item.get("inclusive_rank", 99) <= 2 for item in deletions["FULL"].values()),
        "all_full_pair_deletions_readings_positive": all(all(value > 0 for value in item.get("observed_edition_scores", {}).values()) for item in deletions["FULL"].values()),
        "all_masked_pair_deletions_rank_at_most_2": all(item.get("inclusive_rank", 99) <= 2 for item in deletions["NO_BABA"].values()),
        "all_masked_pair_deletions_readings_positive": all(all(value > 0 for value in item.get("observed_edition_scores", {}).values()) for item in deletions["NO_BABA"].values()),
        "zero_english_glosses": True,
    }
    confirmed = all(gates.values())
    status = "CONFIRMED_AGGREGATE_ZODIAC_OPPOSITION_PROFILE" if confirmed else "FINAL_NONCONFIRMATION_ZODIAC_OPPOSITION_PROFILE"
    decision = "RETAIN_AGGREGATE_OPPOSITION_ALIGNMENT_NO_LEXICAL_GLOSS" if confirmed else "CLOSE_FIXED_WHOLE_PROFILE_OPPOSITION_ROUTE"
    result = {
        "experiment": "ZODIAC_OPPOSITION_PROFILE", "status": status, "decision": decision,
        "inputs": {path.name: sha(path) for path in (ALIGN, META, PAGES, METHOD, Path(__file__), CONTROLS)},
        "source_scope": {"public_page_signs": {page: page_signs[page] for page in sorted(page_signs)}, "target_sign_pages": sign_pages, "target_groups_C_or_L": target_groups, "excluded_alternative_groups": alternative_groups},
        "opposition_matching": [list(pair_key(*pair)) for pair in OPPOSITIONS],
        "sign_group_counts": sign_group_counts,
        "evaluations": evaluations,
        "pair_deletions": deletions,
        "gates": gates,
        "claim_ceiling": "Aggregate source-native circular-profile alignment with public zodiac opposition only; no individual sign, opposition word, sign name, month, day, doctrine, sound, language, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Zodiac-opposition circular profile\n\n"
        f"Status: **{status}**\n\n"
        f"The complete circular profile ranks {full.get('inclusive_rank')} of 105 exact matchings (p={full.get('exact_one_sided_p'):.6f}); after deleting every `BABA`-ending group it ranks {masked.get('inclusive_rank')} of 105 (p={masked.get('exact_one_sided_p'):.6f}). Full positive-pair support is {full.get('positive_pair_support')}; masked support is {masked.get('positive_pair_support')}.\n\n"
        f"Decision: **{decision}**. Label-role results are diagnostic only. No individual sign, sign name, word, meaning, plaintext, or translation follows.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "full_rank": full.get("inclusive_rank"), "full_p": full.get("exact_one_sided_p"), "masked_rank": masked.get("inclusive_rank"), "masked_p": masked.get("exact_one_sided_p")}, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--controls", action="store_true")
    group.add_argument("--target", action="store_true")
    args = parser.parse_args()
    run_controls() if args.controls else run_target()


if __name__ == "__main__":
    main()
