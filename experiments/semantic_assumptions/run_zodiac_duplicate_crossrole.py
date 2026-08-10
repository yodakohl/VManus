#!/usr/bin/env python3
"""Controls and target for duplicated-sign cross-page C/L profile transfer."""

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

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
METHOD = BASE / "ZODIAC_DUPLICATE_CROSSROLE_METHOD.md"
ALIGN = RESULTS / "source_sta_group_alignment.tsv"
META = RESULTS / "source_separator_transcription.tsv"
PUBLIC = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
ROLE_ATLAS = RESULTS / "public_circle_block_role_atlas.json"
ROLE_ATLAS_VALIDATION = RESULTS / "public_circle_block_role_atlas_validation.json"
CONTROLS = RESULTS / "zodiac_duplicate_crossrole_controls.json"
CONTROL_REPORT = RESULTS / "zodiac_duplicate_crossrole_controls_report.md"
OUT = RESULTS / "zodiac_duplicate_crossrole.json"
REPORT = RESULTS / "zodiac_duplicate_crossrole_report.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
VIEWS = tuple([f"FAMILY_N{n}" for n in range(2, 6)] + [f"MEMBER_N{n}" for n in range(1, 4)] + ["FAMILY_GROUP"])
PAGES = ("f70v1", "f70v2", "f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v1", "f72v2", "f72v3", "f73r", "f73v")
OBSERVED = (("f70v1", "f71r"), ("f71v", "f72r1"))
SIGN_RE = re.compile(r"\bemblem of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b", re.I)
TOL = 1e-15


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def edge(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))


def matching_key(pairs) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(edge(*pair) for pair in pairs))


def two_pair_matchings(pages: tuple[str, ...]) -> list[tuple[tuple[str, str], ...]]:
    rows = set()
    for a in range(len(pages)):
        for b in range(a + 1, len(pages)):
            first = edge(pages[a], pages[b])
            remaining = [page for page in pages if page not in first]
            for c in range(len(remaining)):
                for d in range(c + 1, len(remaining)):
                    rows.add(matching_key((first, edge(remaining[c], remaining[d]))))
    output = sorted(rows)
    if any(len({page for pair in item for page in pair}) != 4 for item in output):
        raise AssertionError("matching is not page-disjoint")
    return output


def all_pairs(pages: tuple[str, ...]) -> list[tuple[str, str]]:
    return [edge(pages[i], pages[j]) for i in range(len(pages)) for j in range(i + 1, len(pages))]


def evaluate(matrices: dict, pages: tuple[str, ...], observed_pairs, views: tuple[str, ...] = VIEWS) -> dict[str, object]:
    pairs = all_pairs(pages)
    standardized = defaultdict(lambda: defaultdict(dict))
    diagnostics = {}
    for reading in READINGS:
        diagnostics[reading] = {}
        for view in views:
            values = [matrices[reading][view][pair] for pair in pairs]
            center = statistics.fmean(values)
            scale = math.sqrt(statistics.fmean((value - center) ** 2 for value in values))
            diagnostics[reading][view] = {"mean": center, "population_sd": scale}
            if not math.isfinite(scale) or scale <= 0:
                return {"eligible": False, "reason": f"zero_or_nonfinite_sd:{reading}:{view}"}
            standardized[reading][view] = {pair: (value - center) / scale for pair, value in zip(pairs, values)}
    matchings = two_pair_matchings(pages)
    observed = matching_key(observed_pairs)
    if observed not in matchings:
        raise AssertionError("observed relation absent from matching space")
    orbit = []
    for item in matchings:
        reading_scores = {
            reading: statistics.fmean(standardized[reading][view][pair] for view in views for pair in item)
            for reading in READINGS
        }
        orbit.append({"matching": [list(pair) for pair in item], "reading_scores": reading_scores, "robust_score": min(reading_scores.values())})
    observed_row = next(row for row in orbit if matching_key(row["matching"]) == observed)
    observed_score = float(observed_row["robust_score"])
    contributions = {
        reading: {"|".join(pair): statistics.fmean(standardized[reading][view][pair] for view in views) for pair in observed}
        for reading in READINGS
    }
    pair_rank = {}
    for reading in READINGS:
        pair_values = {
            pair: statistics.fmean(standardized[reading][view][pair] for view in views)
            for pair in pairs
        }
        pair_rank[reading] = {}
        for pair in observed:
            value = pair_values[pair]
            pair_rank[reading]["|".join(pair)] = {
                "value": value,
                "inclusive_rank": 1 + sum(other > value + TOL for other in pair_values.values()),
                "tied": sum(abs(other - value) <= TOL for other in pair_values.values()),
                "inclusive_one_sided_p": sum(other >= value - TOL for other in pair_values.values()) / len(pair_values),
            }
    return {
        "eligible": True,
        "views": list(views),
        "pair_count": len(pairs),
        "matching_count": len(matchings),
        "observed_matching": [list(pair) for pair in observed],
        "observed_reading_scores": observed_row["reading_scores"],
        "observed_pair_contributions": contributions,
        "observed_pair_ranks": pair_rank,
        "observed_robust_score": observed_score,
        "inclusive_rank": 1 + sum(float(row["robust_score"]) > observed_score + TOL for row in orbit),
        "tied": sum(abs(float(row["robust_score"]) - observed_score) <= TOL for row in orbit),
        "exact_one_sided_p": sum(float(row["robust_score"]) >= observed_score - TOL for row in orbit) / len(orbit),
        "standardization_diagnostics": diagnostics,
        "orbit_sha256": object_sha(orbit),
        "orbit_robust_scores": [float(row["robust_score"]) for row in orbit],
    }


def synthetic_matrices(pages: tuple[str, ...], favored_pairs, low: float = .1, high: float = .9) -> dict:
    favored = set(matching_key(favored_pairs))
    pairs = all_pairs(pages)
    return {
        reading: {view: {pair: high if pair in favored else low for pair in pairs} for view in VIEWS}
        for reading in READINGS
    }


def target_pass(item: dict[str, object], joint_alpha: float = .01) -> bool:
    return (
        item.get("eligible") is True
        and item.get("exact_one_sided_p", 1.0) <= joint_alpha
        and all(value > 0 for value in item.get("observed_reading_scores", {}).values())
        and all(value > 0 for row in item.get("observed_pair_contributions", {}).values() for value in row.values())
        and all(cell.get("inclusive_one_sided_p", 1.0) <= .10 for row in item.get("observed_pair_ranks", {}).values() for cell in row.values())
    )


def run_controls() -> None:
    if CONTROLS.exists() or CONTROL_REPORT.exists():
        raise SystemExit("refusing overwrite")
    pages = tuple(f"S{i:02d}" for i in range(12))
    truth = (("S00", "S01"), ("S02", "S03"))
    alternative = (("S04", "S05"), ("S06", "S07"))
    planted_matrix = synthetic_matrices(pages, truth)
    planted = evaluate(planted_matrix, pages, truth)
    constant = evaluate(synthetic_matrices(pages, truth, .5, .5), pages, truth)
    one_pair = evaluate(synthetic_matrices(pages, (truth[0],)), pages, truth)
    hub = evaluate(synthetic_matrices(pages, tuple(("S00", page) for page in pages if page != "S00")), pages, truth)
    disagreement_matrix = synthetic_matrices(pages, truth)
    disagreement_matrix["RF1b"] = synthetic_matrices(pages, alternative)["RF1b"]
    disagreement = evaluate(disagreement_matrix, pages, truth)
    affine_matrix = {
        reading: {
            view: {pair: value * (1.2 + .1 * vi) + ri for pair, value in planted_matrix[reading][view].items()}
            for vi, view in enumerate(VIEWS)
        }
        for ri, reading in enumerate(READINGS)
    }
    affine = evaluate(affine_matrix, pages, truth)
    rename = {page: pages[-index - 1] for index, page in enumerate(pages)}
    relabeled_matrix = {
        reading: {
            view: {edge(rename[pair[0]], rename[pair[1]]): value for pair, value in planted_matrix[reading][view].items()}
            for view in VIEWS
        }
        for reading in READINGS
    }
    relabeled_truth = tuple(edge(rename[a], rename[b]) for a, b in truth)
    relabeled = evaluate(relabeled_matrix, tuple(sorted(rename.values())), relabeled_truth)
    affine_delta = max(abs(a - b) for a, b in zip(affine.get("orbit_robust_scores", []), planted.get("orbit_robust_scores", [])))
    checks = {
        "exact_66_page_pairs": planted.get("pair_count") == 66,
        "exact_1485_disjoint_two_pair_matchings": planted.get("matching_count") == 1485,
        "distributed_plant_unique_rank_one": planted.get("inclusive_rank") == planted.get("tied") == 1,
        "distributed_plant_passes_complete_gate": target_pass(planted),
        "constant_null_ineligible": constant == {"eligible": False, "reason": "zero_or_nonfinite_sd:ZL3b:FAMILY_N2"},
        "one_pair_plant_rejected": not target_pass(one_pair),
        "one_page_hub_rejected": not target_pass(hub),
        "third_reading_disagreement_rejected": not target_pass(disagreement),
        "positive_affine_invariant": affine.get("inclusive_rank") == planted.get("inclusive_rank") and affine.get("tied") == planted.get("tied") and affine.get("exact_one_sided_p") == planted.get("exact_one_sided_p") and affine_delta <= 1e-12,
        "page_relabeling_invariant": relabeled.get("inclusive_rank") == planted.get("inclusive_rank") and relabeled.get("tied") == planted.get("tied") and relabeled.get("exact_one_sided_p") == planted.get("exact_one_sided_p") and abs(float(relabeled.get("observed_robust_score", 0)) - float(planted.get("observed_robust_score", 1))) <= 1e-12,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {
        "experiment": "ZODIAC_DUPLICATE_CROSSROLE_CONTROLS",
        "status": status,
        "inputs": {path.name: sha(path) for path in (METHOD, Path(__file__))},
        "checks": checks,
        "affine_max_abs_orbit_delta": affine_delta,
        "summaries": {
            "planted": planted,
            "constant": constant,
            "one_pair": one_pair,
            "hub": hub,
            "reading_disagreement": disagreement,
            "affine": affine,
            "relabeled": relabeled,
        },
        "target_accessed": False,
        "claim_ceiling": "Synthetic cross-role scorer validation only; no manuscript relation, sign field, word, meaning, or translation.",
    }
    CONTROLS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CONTROL_REPORT.write_text(
        "# Zodiac duplicate cross-role controls\n\n"
        f"Status: **{status}**\n\n"
        "The 1,485-matching scorer recovers a distributed two-pair plant, rejects constant, one-pair, hub, and reading-disagreement controls, and preserves affine and page-relabeling invariance. No manuscript target source was opened.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "checks": checks, "affine_delta": affine_delta}, sort_keys=True))


def features(row: dict[str, str]) -> dict[str, list[str]]:
    families = list(row["primary_sta_families"])
    members = row["primary_sta_codes"].split()
    result = {
        f"FAMILY_N{size}": ["".join(families[start:start + size]) for start in range(len(families) - size + 1)]
        for size in range(2, 6)
    }
    result.update({
        f"MEMBER_N{size}": ["-".join(members[start:start + size]) for start in range(len(members) - size + 1)]
        for size in range(1, 4)
    })
    result["FAMILY_GROUP"] = [row["primary_sta_families"]]
    return result


def weighted_jaccard(left: Counter[str], right: Counter[str]) -> float:
    keys = sorted(set(left) | set(right))
    denominator = sum(max(left[key], right[key]) for key in keys)
    return sum(min(left[key], right[key]) for key in keys) / denominator if denominator else 0.0


def run_target() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    controls = json.loads(CONTROLS.read_text(encoding="utf-8"))
    expected_control_inputs = {path.name: sha(path) for path in (METHOD, Path(__file__))}
    if controls.get("status") != "PASS" or controls.get("inputs") != expected_control_inputs or controls.get("target_accessed") is not False:
        raise SystemExit("control binding failed")
    atlas = json.loads(ROLE_ATLAS.read_text(encoding="utf-8"))
    atlas_validation = json.loads(ROLE_ATLAS_VALIDATION.read_text(encoding="utf-8"))
    if atlas.get("status") != "PASS_COMPLETE_PUBLIC_CIRCLE_ROLE_ATLAS" or atlas_validation.get("status") != "PASS":
        raise SystemExit("role atlas binding failed")
    if any(next(iter(atlas["page_role_signatures"][page].values())) != "LC" for page in PAGES):
        raise AssertionError("zodiac LC role panel changed")

    public_rows = read_tsv(PUBLIC)
    signs = {}
    for row in public_rows:
        match = SIGN_RE.search(row["illustrations"])
        if match:
            signs[row["page"]] = match.group(1).upper()
    if tuple(page for page in PAGES if page in signs) != PAGES or len(signs) != 12:
        raise AssertionError("public zodiac panel changed")
    if {page for page, sign in signs.items() if sign == "ARIES"} != {"f70v1", "f71r"} or {page for page, sign in signs.items() if sign == "TAURUS"} != {"f71v", "f72r1"}:
        raise AssertionError("duplicate sign identities changed")
    if any(row["tentative_identifications_are_role_evidence"] != "0" for row in public_rows):
        raise AssertionError("tentative identity gate changed")

    meta_rows = read_tsv(META)
    metadata = {row["source_group_id"]: row for row in meta_rows}
    if len(metadata) != len(meta_rows):
        raise AssertionError("duplicate metadata group ID")
    counters = defaultdict(Counter)
    target_groups = alternatives = 0
    role_counts = Counter()
    for row in read_tsv(ALIGN):
        info = metadata[row["source_group_id"]]
        page = info["page"]
        role = info["kind"]
        if page not in PAGES or role not in {"C", "L"}:
            continue
        target_groups += 1
        if int(row["alternative_site_count"]):
            alternatives += 1
            continue
        role_counts[(page, row["edition"], role)] += 1
        values = features(row)
        for mask in ("FULL", "NO_BABA"):
            if mask == "NO_BABA" and row["primary_sta_families"].endswith("BABA"):
                continue
            for view, items in values.items():
                counters[(mask, page, row["edition"], role, view)].update(items)
    expected_role_keys = {(page, reading, role) for page in PAGES for reading in READINGS for role in ("C", "L")}
    if set(role_counts) != expected_role_keys or min(role_counts.values()) <= 0:
        raise AssertionError("incomplete page-reading-role panel")

    evaluations = {}
    matrices_by_mask = {}
    for mask in ("FULL", "NO_BABA"):
        matrices = {reading: {view: {} for view in VIEWS} for reading in READINGS}
        for reading in READINGS:
            for view in VIEWS:
                for pair in all_pairs(PAGES):
                    forward = weighted_jaccard(counters[(mask, pair[0], reading, "C", view)], counters[(mask, pair[1], reading, "L", view)])
                    reverse = weighted_jaccard(counters[(mask, pair[1], reading, "C", view)], counters[(mask, pair[0], reading, "L", view)])
                    matrices[reading][view][pair] = (forward + reverse) / 2.0
        matrices_by_mask[mask] = matrices
        evaluations[mask] = evaluate(matrices, PAGES, OBSERVED)
    deletions = {
        mask: {
            view: evaluate(matrices_by_mask[mask], PAGES, OBSERVED, tuple(item for item in VIEWS if item != view))
            for view in VIEWS
        }
        for mask in ("FULL", "NO_BABA")
    }
    gates = {
        "controls_and_role_atlas_bound": True,
        "exact_66_pairs_and_1485_matchings": all(item.get("pair_count") == 66 and item.get("matching_count") == 1485 for item in evaluations.values()),
        "full_complete_gate": target_pass(evaluations["FULL"]),
        "no_baba_complete_gate": target_pass(evaluations["NO_BABA"]),
        "all_view_deletions_joint_p_at_most_005": all(item.get("exact_one_sided_p", 1.0) <= .05 for rows in deletions.values() for item in rows.values()),
        "all_view_deletions_readings_positive": all(all(value > 0 for value in item.get("observed_reading_scores", {}).values()) for rows in deletions.values() for item in rows.values()),
        "all_view_deletions_pairs_positive": all(all(value > 0 for row in item.get("observed_pair_contributions", {}).values() for value in row.values()) for rows in deletions.values() for item in rows.values()),
        "zero_english_glosses": True,
    }
    confirmed = all(gates.values())
    status = "CONFIRMED_DUPLICATED_SIGN_CROSSROLE_FIELD" if confirmed else "FINAL_NONCONFIRMATION_DUPLICATED_SIGN_CROSSROLE_FIELD"
    decision = "RETAIN_ANONYMOUS_TRANSFERABLE_SIGN_LEVEL_FIELD" if confirmed else "CLOSE_FIXED_DUPLICATED_SIGN_CROSSROLE_ROUTE"
    result = {
        "experiment": "ZODIAC_DUPLICATE_CROSSROLE",
        "status": status,
        "decision": decision,
        "inputs": {path.name: sha(path) for path in (ALIGN, META, PUBLIC, ROLE_ATLAS, ROLE_ATLAS_VALIDATION, METHOD, Path(__file__), CONTROLS)},
        "source_scope": {
            "pages": list(PAGES),
            "public_signs": {page: signs[page] for page in PAGES},
            "observed_duplicate_pairs": [list(edge(*pair)) for pair in OBSERVED],
            "target_C_or_L_groups": target_groups,
            "excluded_alternative_groups": alternatives,
            "zero_alternative_role_group_counts": {f"{page}|{reading}|{role}": role_counts[(page, reading, role)] for page, reading, role in sorted(role_counts)},
        },
        "evaluations": evaluations,
        "view_deletions": deletions,
        "gates": gates,
        "claim_ceiling": "Transferable source-native cross-role field across two duplicated public sign relations only; no identified form, sign name, month, day, degree, object, word, morpheme, sound, language, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Duplicated-zodiac cross-role transfer\n\n"
        f"Status: **{status}**\n\n"
        f"The public Aries/Taurus two-pair cross-role matching ranks {evaluations['FULL'].get('inclusive_rank')} of 1,485 (p={evaluations['FULL'].get('exact_one_sided_p'):.6f}); after removing every `BABA`-ending group it ranks {evaluations['NO_BABA'].get('inclusive_rank')} of 1,485 (p={evaluations['NO_BABA'].get('exact_one_sided_p'):.6f}). Reading scores are FULL {evaluations['FULL'].get('observed_reading_scores')} and NO_BABA {evaluations['NO_BABA'].get('observed_reading_scores')}.\n\n"
        f"Decision: **{decision}**. This tests anonymous C-to-L transfer across duplicate-sign pages, not a sign name, word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "decision": decision, "full_rank": evaluations["FULL"].get("inclusive_rank"), "full_p": evaluations["FULL"].get("exact_one_sided_p"), "no_baba_rank": evaluations["NO_BABA"].get("inclusive_rank"), "no_baba_p": evaluations["NO_BABA"].get("exact_one_sided_p")}, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--controls", action="store_true")
    group.add_argument("--target", action="store_true")
    args = parser.parse_args()
    run_controls() if args.controls else run_target()


if __name__ == "__main__":
    main()
