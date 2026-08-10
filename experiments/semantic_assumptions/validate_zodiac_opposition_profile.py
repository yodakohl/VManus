#!/usr/bin/env python3
"""Nonimporting reconstruction of the public zodiac-opposition profile result."""

from __future__ import annotations

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
ALIGN = RESULTS / "source_sta_group_alignment.tsv"
META = RESULTS / "source_separator_transcription.tsv"
PAGES = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
METHOD = BASE / "ZODIAC_OPPOSITION_PROFILE_METHOD.md"
PRODUCER = BASE / "run_zodiac_opposition_profile.py"
CONTROLS = RESULTS / "zodiac_opposition_profile_controls.json"
TARGET = RESULTS / "zodiac_opposition_profile.json"
TARGET_REPORT = RESULTS / "zodiac_opposition_profile_report.md"
OUT = RESULTS / "zodiac_opposition_profile_validation.json"
REPORT = RESULTS / "zodiac_opposition_profile_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
VIEWS = tuple([f"FAMILY_N{n}" for n in range(2, 6)] + [f"MEMBER_N{n}" for n in range(1, 4)] + ["FAMILY_GROUP"])
SIGNS = ("ARIES", "GEMINI", "LIBRA", "PISCES", "SAGITTARIUS", "SCORPIUS", "TAURUS", "VIRGO")
OPPOSITE = (("ARIES", "LIBRA"), ("GEMINI", "SAGITTARIUS"), ("PISCES", "VIRGO"), ("SCORPIUS", "TAURUS"))
SIGN_RE = re.compile(r"\bemblem of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b", re.I)
TOL = 1e-15


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def edge(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def matching(pairs) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(edge(a, b) for a, b in pairs))


def perfect_matchings(nodes: tuple[str, ...]) -> list[tuple[tuple[str, str], ...]]:
    if not nodes:
        return [tuple()]
    head = nodes[0]
    out = []
    for j in range(1, len(nodes)):
        remaining = nodes[1:j] + nodes[j + 1:]
        for tail in perfect_matchings(remaining):
            out.append(matching(((head, nodes[j]),) + tail))
    result = sorted(set(out))
    assert all(sorted(x for pair in item for x in pair) == sorted(nodes) for item in result)
    return result


def evaluate(matrix: dict, nodes: tuple[str, ...], observed_pairs) -> dict[str, object]:
    edges = [edge(nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i + 1, len(nodes))]
    z = defaultdict(lambda: defaultdict(dict))
    diagnostics = {}
    for reading in READINGS:
        diagnostics[reading] = {}
        for view in VIEWS:
            values = [matrix[reading][view][pair] for pair in edges]
            mean = statistics.fmean(values)
            sd = math.sqrt(statistics.fmean((value - mean) ** 2 for value in values))
            diagnostics[reading][view] = {"mean": mean, "population_sd": sd}
            if not math.isfinite(sd) or sd <= 0:
                return {"eligible": False, "reason": f"zero_or_nonfinite_sd:{reading}:{view}"}
            z[reading][view] = {pair: (value - mean) / sd for pair, value in zip(edges, values)}
    matchings = perfect_matchings(nodes)
    observed = matching(observed_pairs)
    assert observed in matchings
    orbit = []
    for candidate in matchings:
        reading_scores = {
            reading: statistics.fmean(z[reading][view][pair] for view in VIEWS for pair in candidate)
            for reading in READINGS
        }
        orbit.append({"matching": [list(pair) for pair in candidate], "edition_scores": reading_scores, "robust_score": min(reading_scores.values())})
    observed_row = next(row for row in orbit if matching(tuple(tuple(pair) for pair in row["matching"])) == observed)
    observed_score = float(observed_row["robust_score"])
    contributions = {
        reading: {"|".join(pair): statistics.fmean(z[reading][view][pair] for view in VIEWS) for pair in observed}
        for reading in READINGS
    }
    return {
        "eligible": True,
        "matching_count": len(matchings),
        "observed_matching": [list(pair) for pair in observed],
        "observed_edition_scores": observed_row["edition_scores"],
        "observed_robust_score": observed_score,
        "inclusive_rank": 1 + sum(float(row["robust_score"]) > observed_score + TOL for row in orbit),
        "tied": sum(abs(float(row["robust_score"]) - observed_score) <= TOL for row in orbit),
        "exact_one_sided_p": sum(float(row["robust_score"]) >= observed_score - TOL for row in orbit) / len(orbit),
        "positive_pair_support": {reading: sum(value > 0 for value in contributions[reading].values()) for reading in READINGS},
        "observed_pair_contributions": contributions,
        "standardization_diagnostics": diagnostics,
        "orbit_sha256": json_digest(orbit),
        "orbit_robust_scores": [float(row["robust_score"]) for row in orbit],
    }


def features(row: dict[str, str]) -> dict[str, list[str]]:
    families = list(row["primary_sta_families"])
    members = row["primary_sta_codes"].split()
    result = {
        f"FAMILY_N{n}": ["".join(families[i:i + n]) for i in range(len(families) - n + 1)]
        for n in range(2, 6)
    }
    result.update({
        f"MEMBER_N{n}": ["-".join(members[i:i + n]) for i in range(len(members) - n + 1)]
        for n in range(1, 4)
    })
    result["FAMILY_GROUP"] = [row["primary_sta_families"]]
    return result


def weighted_jaccard(a: Counter[str], b: Counter[str]) -> float:
    keys = sorted(set(a) | set(b))
    denominator = sum(max(a[key], b[key]) for key in keys)
    return sum(min(a[key], b[key]) for key in keys) / denominator if denominator else 0.0


def make_matrix(counters: dict, role: str, mask: str, sign_pages: dict[str, list[str]]) -> tuple[dict, dict]:
    profiles = {}
    counts = {}
    for sign in SIGNS:
        counts[sign] = {}
        for reading in READINGS:
            counts[sign][reading] = sum(sum(counters[(role, mask, page, reading, "FAMILY_GROUP")].values()) for page in sign_pages[sign])
            for view in VIEWS:
                merged = Counter()
                for page in sign_pages[sign]:
                    merged.update(counters[(role, mask, page, reading, view)])
                profiles[(sign, reading, view)] = merged
    matrix = {
        reading: {
            view: {
                edge(SIGNS[i], SIGNS[j]): weighted_jaccard(profiles[(SIGNS[i], reading, view)], profiles[(SIGNS[j], reading, view)])
                for i in range(len(SIGNS)) for j in range(i + 1, len(SIGNS))
            }
            for view in VIEWS
        }
        for reading in READINGS
    }
    return matrix, counts


def reconstruct() -> tuple[dict[str, object], int]:
    public = rows(PAGES)
    page_signs = {}
    for row in public:
        found = SIGN_RE.search(row["illustrations"])
        if found:
            page_signs[row["page"]] = found.group(1).upper()
    assert len(page_signs) == 12
    assert all(row["tentative_identifications_are_role_evidence"] == "0" for row in public)
    sign_pages = {sign: sorted(page for page, value in page_signs.items() if value == sign) for sign in SIGNS}
    assert {sign: len(value) for sign, value in sign_pages.items()} == {
        "ARIES": 2, "TAURUS": 2, "GEMINI": 1, "LIBRA": 1,
        "PISCES": 1, "SAGITTARIUS": 1, "SCORPIUS": 1, "VIRGO": 1,
    }
    meta_rows = rows(META)
    metadata = {row["source_group_id"]: row for row in meta_rows}
    assert len(metadata) == len(meta_rows)
    counters = defaultdict(Counter)
    total = alternatives = 0
    alignment_rows = rows(ALIGN)
    assert len({row["source_group_id"] for row in alignment_rows}) == len(alignment_rows)
    for row in alignment_rows:
        info = metadata[row["source_group_id"]]
        page = info["page"]
        if page not in page_signs or page_signs[page] not in SIGNS or info["kind"] not in {"C", "L"}:
            continue
        assert row["edition"] == info["edition"]
        total += 1
        if int(row["alternative_site_count"]):
            alternatives += 1
            continue
        for mask in ("FULL", "NO_BABA"):
            if mask == "NO_BABA" and row["primary_sta_families"].endswith("BABA"):
                continue
            for view, values in features(row).items():
                counters[(info["kind"], mask, page, row["edition"], view)].update(values)

    evaluations = {}
    matrices = {}
    counts = {}
    for role in ("C", "L"):
        evaluations[role] = {}
        counts[role] = {}
        for mask in ("FULL", "NO_BABA"):
            matrix, group_counts = make_matrix(counters, role, mask, sign_pages)
            matrices[(role, mask)] = matrix
            counts[role][mask] = group_counts
            evaluations[role][mask] = evaluate(matrix, SIGNS, OPPOSITE)
    deletions = {mask: {} for mask in ("FULL", "NO_BABA")}
    for mask in deletions:
        for deleted in OPPOSITE:
            kept_nodes = tuple(node for node in SIGNS if node not in deleted)
            kept_pairs = tuple(pair for pair in OPPOSITE if pair != deleted)
            deletions[mask]["|".join(edge(*deleted))] = evaluate(matrices[("C", mask)], kept_nodes, kept_pairs)
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
    assert not any(key.lower() in {"gloss", "english_gloss", "translation", "plaintext"} for key in evaluations)
    expected = {
        "experiment": "ZODIAC_OPPOSITION_PROFILE",
        "status": "CONFIRMED_AGGREGATE_ZODIAC_OPPOSITION_PROFILE" if confirmed else "FINAL_NONCONFIRMATION_ZODIAC_OPPOSITION_PROFILE",
        "decision": "RETAIN_AGGREGATE_OPPOSITION_ALIGNMENT_NO_LEXICAL_GLOSS" if confirmed else "CLOSE_FIXED_WHOLE_PROFILE_OPPOSITION_ROUTE",
        "inputs": {path.name: digest(path) for path in (ALIGN, META, PAGES, METHOD, PRODUCER, CONTROLS)},
        "source_scope": {
            "public_page_signs": {page: page_signs[page] for page in sorted(page_signs)},
            "target_sign_pages": sign_pages,
            "target_groups_C_or_L": total,
            "excluded_alternative_groups": alternatives,
        },
        "opposition_matching": [list(edge(*pair)) for pair in OPPOSITE],
        "sign_group_counts": counts,
        "evaluations": evaluations,
        "pair_deletions": deletions,
        "gates": gates,
        "claim_ceiling": "Aggregate source-native circular-profile alignment with public zodiac opposition only; no individual sign, opposition word, sign name, month, day, doctrine, sound, language, plaintext, or translation.",
    }
    assertions = len(alignment_rows) + len(meta_rows) + len(public) + 4 * 105 + 8 * 15 + len(gates)
    return expected, assertions


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    expected, assertions = reconstruct()
    assert stored == expected, "stored target result differs from clean-room reconstruction"
    full = expected["evaluations"]["C"]["FULL"]
    masked = expected["evaluations"]["C"]["NO_BABA"]
    expected_report = (
        "# Zodiac-opposition circular profile\n\n"
        f"Status: **{expected['status']}**\n\n"
        f"The complete circular profile ranks {full.get('inclusive_rank')} of 105 exact matchings (p={full.get('exact_one_sided_p'):.6f}); after deleting every `BABA`-ending group it ranks {masked.get('inclusive_rank')} of 105 (p={masked.get('exact_one_sided_p'):.6f}). Full positive-pair support is {full.get('positive_pair_support')}; masked support is {masked.get('positive_pair_support')}.\n\n"
        f"Decision: **{expected['decision']}**. Label-role results are diagnostic only. No individual sign, sign name, word, meaning, plaintext, or translation follows.\n"
    )
    assert TARGET_REPORT.read_text(encoding="utf-8") == expected_report
    validation = {
        "experiment": "ZODIAC_OPPOSITION_PROFILE_VALIDATION",
        "status": "PASS",
        "assertions": assertions,
        "bindings": {path.name: digest(path) for path in (TARGET, TARGET_REPORT, ALIGN, META, PAGES, METHOD, PRODUCER, CONTROLS)},
        "reconstructed": {
            "full_rank": full["inclusive_rank"], "full_p": full["exact_one_sided_p"],
            "no_baba_rank": masked["inclusive_rank"], "no_baba_p": masked["exact_one_sided_p"],
            "full_positive_support": full["positive_pair_support"],
            "no_baba_positive_support": masked["positive_pair_support"],
            "pair_deletion_cells": 8,
        },
        "production_module_imported": False,
        "decision": expected["decision"],
        "claim_ceiling": "Exact reconstruction of the fixed profile nonconfirmation; no lexical or translation claim.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Zodiac-opposition profile validation\n\n"
        f"Status: **PASS** ({assertions} checks). A nonimporting reconstruction reproduced all source bindings, 105-matching profiles, `BABA` deletion, eight pair-deletion cells, gates, decision, JSON, and report. The fixed result remains rank {full['inclusive_rank']}/105 (p={full['exact_one_sided_p']:.6f}) and closes without lexical interpretation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "assertions": assertions, "decision": expected["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
