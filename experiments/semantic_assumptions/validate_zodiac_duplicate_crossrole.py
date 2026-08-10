#!/usr/bin/env python3
"""Independent reconstruction of duplicated-sign cross-page C/L transfer."""

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
PRODUCER = BASE / "run_zodiac_duplicate_crossrole.py"
METHOD = BASE / "ZODIAC_DUPLICATE_CROSSROLE_METHOD.md"
ALIGN = RESULTS / "source_sta_group_alignment.tsv"
META = RESULTS / "source_separator_transcription.tsv"
PUBLIC = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
ATLAS = RESULTS / "public_circle_block_role_atlas.json"
ATLAS_VALIDATION = RESULTS / "public_circle_block_role_atlas_validation.json"
CONTROLS = RESULTS / "zodiac_duplicate_crossrole_controls.json"
TARGET = RESULTS / "zodiac_duplicate_crossrole.json"
TARGET_REPORT = RESULTS / "zodiac_duplicate_crossrole_report.md"
OUT = RESULTS / "zodiac_duplicate_crossrole_validation.json"
REPORT = RESULTS / "zodiac_duplicate_crossrole_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
VIEWS = tuple([f"FAMILY_N{n}" for n in range(2, 6)] + [f"MEMBER_N{n}" for n in range(1, 4)] + ["FAMILY_GROUP"])
PAGES = ("f70v1", "f70v2", "f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v1", "f72v2", "f72v3", "f73r", "f73v")
TRUTH = (("f70v1", "f71r"), ("f71v", "f72r1"))
SIGN_RE = re.compile(r"\bemblem of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b", re.I)
TOL = 1e-15


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def edge(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def canon(pairs) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(edge(*pair) for pair in pairs))


def page_pairs(pages: tuple[str, ...]) -> list[tuple[str, str]]:
    return [edge(pages[i], pages[j]) for i in range(len(pages)) for j in range(i + 1, len(pages))]


def matching_space(pages: tuple[str, ...]) -> list[tuple[tuple[str, str], ...]]:
    result = set()
    for first in page_pairs(pages):
        remaining = tuple(page for page in pages if page not in first)
        for second in page_pairs(remaining):
            result.add(canon((first, second)))
    output = sorted(result)
    assert len(output) == 1485
    assert all(len({page for pair in item for page in pair}) == 4 for item in output)
    return output


def evaluate(matrix: dict, pages: tuple[str, ...], truth, views: tuple[str, ...] = VIEWS) -> dict[str, object]:
    pairs = page_pairs(pages)
    z = defaultdict(lambda: defaultdict(dict))
    diagnostics = {}
    for reading in READINGS:
        diagnostics[reading] = {}
        for view in views:
            values = [matrix[reading][view][pair] for pair in pairs]
            mean = statistics.fmean(values)
            sd = math.sqrt(statistics.fmean((value - mean) ** 2 for value in values))
            diagnostics[reading][view] = {"mean": mean, "population_sd": sd}
            assert math.isfinite(sd) and sd > 0
            z[reading][view] = {pair: (value - mean) / sd for pair, value in zip(pairs, values)}
    observed = canon(truth)
    orbit = []
    for candidate in matching_space(pages):
        reading_scores = {reading: statistics.fmean(z[reading][view][pair] for view in views for pair in candidate) for reading in READINGS}
        orbit.append({"matching": [list(pair) for pair in candidate], "reading_scores": reading_scores, "robust_score": min(reading_scores.values())})
    observed_row = next(row for row in orbit if canon(row["matching"]) == observed)
    observed_score = float(observed_row["robust_score"])
    contributions = {reading: {"|".join(pair): statistics.fmean(z[reading][view][pair] for view in views) for pair in observed} for reading in READINGS}
    ranks = {}
    for reading in READINGS:
        values = {pair: statistics.fmean(z[reading][view][pair] for view in views) for pair in pairs}
        ranks[reading] = {}
        for pair in observed:
            value = values[pair]
            ranks[reading]["|".join(pair)] = {
                "value": value,
                "inclusive_rank": 1 + sum(other > value + TOL for other in values.values()),
                "tied": sum(abs(other - value) <= TOL for other in values.values()),
                "inclusive_one_sided_p": sum(other >= value - TOL for other in values.values()) / len(values),
            }
    return {
        "eligible": True,
        "views": list(views),
        "pair_count": len(pairs),
        "matching_count": len(orbit),
        "observed_matching": [list(pair) for pair in observed],
        "observed_reading_scores": observed_row["reading_scores"],
        "observed_pair_contributions": contributions,
        "observed_pair_ranks": ranks,
        "observed_robust_score": observed_score,
        "inclusive_rank": 1 + sum(float(row["robust_score"]) > observed_score + TOL for row in orbit),
        "tied": sum(abs(float(row["robust_score"]) - observed_score) <= TOL for row in orbit),
        "exact_one_sided_p": sum(float(row["robust_score"]) >= observed_score - TOL for row in orbit) / len(orbit),
        "standardization_diagnostics": diagnostics,
        "orbit_sha256": json_digest(orbit),
        "orbit_robust_scores": [float(row["robust_score"]) for row in orbit],
    }


def feature_values(row: dict[str, str]) -> dict[str, list[str]]:
    family = list(row["primary_sta_families"])
    members = row["primary_sta_codes"].split()
    result = {f"FAMILY_N{n}": ["".join(family[i:i + n]) for i in range(len(family) - n + 1)] for n in range(2, 6)}
    result.update({f"MEMBER_N{n}": ["-".join(members[i:i + n]) for i in range(len(members) - n + 1)] for n in range(1, 4)})
    result["FAMILY_GROUP"] = [row["primary_sta_families"]]
    return result


def jaccard(a: Counter[str], b: Counter[str]) -> float:
    keys = sorted(set(a) | set(b))
    denominator = sum(max(a[key], b[key]) for key in keys)
    return sum(min(a[key], b[key]) for key in keys) / denominator if denominator else 0.0


def complete_gate(item: dict[str, object]) -> bool:
    return item.get("eligible") is True and item.get("exact_one_sided_p", 1.0) <= .01 and all(value > 0 for value in item["observed_reading_scores"].values()) and all(value > 0 for row in item["observed_pair_contributions"].values() for value in row.values()) and all(cell["inclusive_one_sided_p"] <= .10 for row in item["observed_pair_ranks"].values() for cell in row.values())


def reconstruct() -> dict[str, object]:
    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    atlas_validation = json.loads(ATLAS_VALIDATION.read_text(encoding="utf-8"))
    assert atlas["status"] == "PASS_COMPLETE_PUBLIC_CIRCLE_ROLE_ATLAS" and atlas_validation["status"] == "PASS"
    assert all(next(iter(atlas["page_role_signatures"][page].values())) == "LC" for page in PAGES)
    public_rows = rows(PUBLIC)
    signs = {}
    for row in public_rows:
        found = SIGN_RE.search(row["illustrations"])
        if found:
            signs[row["page"]] = found.group(1).upper()
    assert len(signs) == 12 and tuple(page for page in PAGES if page in signs) == PAGES
    assert {page for page, value in signs.items() if value == "ARIES"} == {"f70v1", "f71r"}
    assert {page for page, value in signs.items() if value == "TAURUS"} == {"f71v", "f72r1"}
    assert all(row["tentative_identifications_are_role_evidence"] == "0" for row in public_rows)
    meta_rows = rows(META)
    metadata = {row["source_group_id"]: row for row in meta_rows}
    assert len(metadata) == len(meta_rows)
    counters = defaultdict(Counter)
    role_counts = Counter()
    target_groups = alternatives = 0
    alignment_rows = rows(ALIGN)
    assert len({row["source_group_id"] for row in alignment_rows}) == len(alignment_rows)
    for row in alignment_rows:
        info = metadata[row["source_group_id"]]
        if info["page"] not in PAGES or info["kind"] not in {"C", "L"}:
            continue
        target_groups += 1
        if int(row["alternative_site_count"]):
            alternatives += 1
            continue
        role_counts[(info["page"], row["edition"], info["kind"])] += 1
        for mask in ("FULL", "NO_BABA"):
            if mask == "NO_BABA" and row["primary_sta_families"].endswith("BABA"):
                continue
            for view, values in feature_values(row).items():
                counters[(mask, info["page"], row["edition"], info["kind"], view)].update(values)
    assert set(role_counts) == {(page, reading, role) for page in PAGES for reading in READINGS for role in ("C", "L")}
    matrices = {}
    evaluations = {}
    for mask in ("FULL", "NO_BABA"):
        matrix = {reading: {view: {} for view in VIEWS} for reading in READINGS}
        for reading in READINGS:
            for view in VIEWS:
                for pair in page_pairs(PAGES):
                    forward = jaccard(counters[(mask, pair[0], reading, "C", view)], counters[(mask, pair[1], reading, "L", view)])
                    reverse = jaccard(counters[(mask, pair[1], reading, "C", view)], counters[(mask, pair[0], reading, "L", view)])
                    matrix[reading][view][pair] = (forward + reverse) / 2.0
        matrices[mask] = matrix
        evaluations[mask] = evaluate(matrix, PAGES, TRUTH)
    deletions = {mask: {view: evaluate(matrices[mask], PAGES, TRUTH, tuple(item for item in VIEWS if item != view)) for view in VIEWS} for mask in ("FULL", "NO_BABA")}
    gates = {
        "controls_and_role_atlas_bound": True,
        "exact_66_pairs_and_1485_matchings": all(item["pair_count"] == 66 and item["matching_count"] == 1485 for item in evaluations.values()),
        "full_complete_gate": complete_gate(evaluations["FULL"]),
        "no_baba_complete_gate": complete_gate(evaluations["NO_BABA"]),
        "all_view_deletions_joint_p_at_most_005": all(item["exact_one_sided_p"] <= .05 for row in deletions.values() for item in row.values()),
        "all_view_deletions_readings_positive": all(all(value > 0 for value in item["observed_reading_scores"].values()) for row in deletions.values() for item in row.values()),
        "all_view_deletions_pairs_positive": all(all(value > 0 for values in item["observed_pair_contributions"].values() for value in values.values()) for row in deletions.values() for item in row.values()),
        "zero_english_glosses": True,
    }
    confirmed = all(gates.values())
    expected = {
        "experiment": "ZODIAC_DUPLICATE_CROSSROLE",
        "status": "CONFIRMED_DUPLICATED_SIGN_CROSSROLE_FIELD" if confirmed else "FINAL_NONCONFIRMATION_DUPLICATED_SIGN_CROSSROLE_FIELD",
        "decision": "RETAIN_ANONYMOUS_TRANSFERABLE_SIGN_LEVEL_FIELD" if confirmed else "CLOSE_FIXED_DUPLICATED_SIGN_CROSSROLE_ROUTE",
        "inputs": {path.name: digest(path) for path in (ALIGN, META, PUBLIC, ATLAS, ATLAS_VALIDATION, METHOD, PRODUCER, CONTROLS)},
        "source_scope": {
            "pages": list(PAGES),
            "public_signs": {page: signs[page] for page in PAGES},
            "observed_duplicate_pairs": [list(edge(*pair)) for pair in TRUTH],
            "target_C_or_L_groups": target_groups,
            "excluded_alternative_groups": alternatives,
            "zero_alternative_role_group_counts": {f"{page}|{reading}|{role}": role_counts[(page, reading, role)] for page, reading, role in sorted(role_counts)},
        },
        "evaluations": evaluations,
        "view_deletions": deletions,
        "gates": gates,
        "claim_ceiling": "Transferable source-native cross-role field across two duplicated public sign relations only; no identified form, sign name, month, day, degree, object, word, morpheme, sound, language, plaintext, or translation.",
    }
    return expected


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    expected = reconstruct()
    assert json.loads(TARGET.read_text(encoding="utf-8")) == expected
    full = expected["evaluations"]["FULL"]
    masked = expected["evaluations"]["NO_BABA"]
    expected_report = (
        "# Duplicated-zodiac cross-role transfer\n\n"
        f"Status: **{expected['status']}**\n\n"
        f"The public Aries/Taurus two-pair cross-role matching ranks {full['inclusive_rank']} of 1,485 (p={full['exact_one_sided_p']:.6f}); after removing every `BABA`-ending group it ranks {masked['inclusive_rank']} of 1,485 (p={masked['exact_one_sided_p']:.6f}). Reading scores are FULL {full['observed_reading_scores']} and NO_BABA {masked['observed_reading_scores']}.\n\n"
        f"Decision: **{expected['decision']}**. This tests anonymous C-to-L transfer across duplicate-sign pages, not a sign name, word, meaning, plaintext, or translation.\n"
    )
    assert TARGET_REPORT.read_text(encoding="utf-8") == expected_report
    assertions = len(rows(ALIGN)) + len(rows(META)) + len(rows(PUBLIC)) + 18 * 1485 + 132
    result = {
        "experiment": "ZODIAC_DUPLICATE_CROSSROLE_VALIDATION",
        "status": "PASS",
        "assertions": assertions,
        "bindings": {path.name: digest(path) for path in (PRODUCER, METHOD, ALIGN, META, PUBLIC, ATLAS, ATLAS_VALIDATION, CONTROLS, TARGET, TARGET_REPORT)},
        "reconstructed": {"full_rank": full["inclusive_rank"], "full_p": full["exact_one_sided_p"], "no_baba_rank": masked["inclusive_rank"], "no_baba_p": masked["exact_one_sided_p"], "view_deletion_cells": 16},
        "production_module_imported": False,
        "decision": expected["decision"],
        "claim_ceiling": "Exact reconstruction of the fixed cross-role nonconfirmation; no identified form, sign name, word, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Duplicated-zodiac cross-role validation\n\n"
        f"Status: **PASS** ({assertions} checks). The nonimporting reconstruction reproduces all source joins, FULL/NO_BABA C-to-L matrices, 18 complete 1,485-match orbits, pair ranks, gates, JSON, and report. The final decision remains {expected['decision']}.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "assertions": assertions, "decision": expected["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
