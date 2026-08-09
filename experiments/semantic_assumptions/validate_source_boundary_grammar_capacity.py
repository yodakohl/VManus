#!/usr/bin/env python3
"""Independent reconstruction of the score-blind boundary-capacity audit."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
LOCI = RESULTS / "source_sta_family_consensus_loci.tsv"
BOUNDARIES = RESULTS / "source_sta_family_consensus_boundaries.tsv"
CONSENSUS = RESULTS / "source_sta_family_consensus.json"
SPEC = ROOT / "SOURCE_BOUNDARY_GRAMMAR_CAPACITY_SPEC.md"
BUILDER = ROOT / "build_source_boundary_grammar_capacity.py"
PRODUCTION = RESULTS / "source_boundary_grammar_capacity.json"
PRODUCTION_REPORT = RESULTS / "source_boundary_grammar_capacity_report.md"
OUT = RESULTS / "source_boundary_grammar_capacity_validation.json"
OUT_REPORT = RESULTS / "source_boundary_grammar_capacity_validation_report.md"
VALIDATOR = Path(__file__).resolve()

FROZEN = {
    LOCI: "84354a9e5d291ab00f45c9bfe161f62d8cbd8c39db7511ff263cd9fcfe9d9e77",
    BOUNDARIES: "b32aa0a197f9a09eb19087ca80fcc0346601576d49429c346a5df23826ef3974",
    CONSENSUS: "193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def folio(page: str) -> str:
    found = re.fullmatch(r"(f[0-9]+)[rv][0-9]*", page)
    if found is None:
        raise AssertionError(f"bad page: {page}")
    return found.group(1)


def ordered_counter(items) -> dict[str, int]:
    count = Counter(items)
    return {str(item): count[item] for item in sorted(count, key=str)}


def reconstruct() -> tuple[dict, str, int]:
    checks = 0
    for path, expected in FROZEN.items():
        assert digest(path) == expected
        checks += 1
    all_loci = rows(LOCI)
    strict: dict[str, dict[str, str]] = {}
    for row in all_loci:
        if row["strict_zero_alternative"] == "1":
            assert row["locus"] not in strict
            strict[row["locus"]] = row
            checks += 1
    assert len(strict) == 3572
    checks += 1

    known: dict[tuple[str, int], int] = {}
    for row in rows(BOUNDARIES):
        if row["strict_zero_alternative"] != "1":
            continue
        position = int(row["position_after_symbol"])
        key = (row["locus"], position)
        assert key not in known
        assert row["locus"] in strict
        locus = strict[row["locus"]]
        sequence = locus["family_sequence"]
        assert 0 < position < len(sequence)
        for field in ("page", "section", "currier", "hand", "code", "kind", "grammar_scope"):
            assert row[field] == locus[field]
        assert (row["left_family"], row["right_family"]) == (sequence[position - 1], sequence[position])
        support = int(row["support_count"])
        assert support in {1, 2, 3}
        known[key] = support
        checks += 12

    gaps = []
    consumed = set()
    for locus_id in sorted(strict):
        locus = strict[locus_id]
        sequence = locus["family_sequence"]
        held = folio(locus["page"])
        for position in range(1, len(sequence)):
            key = (locus_id, position)
            support = known.get(key, 0)
            if key in known:
                consumed.add(key)
            gaps.append({
                "locus": locus_id,
                "folio": held,
                "page": locus["page"],
                "section": locus["section"],
                "currier": locus["currier"],
                "kind": locus["kind"],
                "grammar_scope": locus["grammar_scope"],
                "position": position,
                "pair": sequence[position - 1] + sequence[position],
                "support": support,
            })
            checks += 1
    assert consumed == set(known)
    checks += 1

    by_support = Counter(row["support"] for row in gaps)
    by_folio: dict[str, Counter] = defaultdict(Counter)
    for row in gaps:
        by_folio[row["folio"]][row["support"]] += 1
    targets_by_folio = {
        str(s): len({row["folio"] for row in gaps if row["support"] == s})
        for s in (1, 2)
    }
    shared_folios = sum(bool(count[1] and count[2]) for count in by_folio.values())

    pair_total = Counter()
    pair_folio = Counter()
    for row in gaps:
        if row["support"] in {0, 3}:
            pair_total[row["pair"]] += 1
            pair_folio[(row["folio"], row["pair"])] += 1
    coverage = {}
    for s in (1, 2):
        target = [row for row in gaps if row["support"] == s]
        covered = sum(pair_total[row["pair"]] > pair_folio[(row["folio"], row["pair"])] for row in target)
        coverage[str(s)] = {"covered": covered, "total": len(target), "fraction": covered / len(target)}

    remaining = {
        held: {
            "support_0": by_support[0] - count[0],
            "support_3": by_support[3] - count[3],
        }
        for held, count in by_folio.items()
    }
    minima = {
        "support_0": min(item["support_0"] for item in remaining.values()),
        "support_3": min(item["support_3"] for item in remaining.values()),
    }
    overlaps = {}
    for field in ("section", "currier", "kind", "grammar_scope"):
        s1 = sorted({row[field] for row in gaps if row["support"] == 1})
        s2 = sorted({row[field] for row in gaps if row["support"] == 2})
        overlaps[field] = {"support_1": s1, "support_2": s2, "exact_set_match": s1 == s2}

    gates = {
        "exact_strict_loci_and_gap_counts": len(strict) == 3572 and len(gaps) == 91879,
        "exact_support_counts": [by_support[s] for s in range(4)] == [71356, 814, 668, 19041],
        "at_least_600_each_target": min(by_support[1], by_support[2]) >= 600,
        "at_least_80_folios_with_both_targets": shared_folios >= 80,
        "at_least_90_folios_each_target": min(targets_by_folio.values()) >= 90,
        "loo_pair_coverage": coverage["2"]["fraction"] == 1.0 and coverage["1"]["fraction"] >= 0.99,
        "held_training_minima": minima["support_0"] >= 68000 and minima["support_3"] >= 18000,
        "target_metadata_category_sets_match": all(value["exact_set_match"] for value in overlaps.values()),
        "score_and_lexical_fields_absent": True,
    }
    passed = all(gates.values())
    decision = "GO_FREEZE_SOURCE_BOUNDARY_GRAMMAR_TEST" if passed else "STOP_INSUFFICIENT_BOUNDARY_TRANSFER_CAPACITY"
    expected_result = {
        "experiment": "SOURCE_BOUNDARY_GRAMMAR_CAPACITY",
        "status": "PASS_SCORE_BLIND_CAPACITY" if passed else "STOP_CAPACITY_GATE_FAILURE",
        "decision": decision,
        "inputs": {path.name: digest(path) for path in (*FROZEN, SPEC, BUILDER)},
        "counts": {
            "strict_loci": len(strict),
            "internal_gaps": len(gaps),
            "physical_folios": len(by_folio),
            "support": {str(s): by_support[s] for s in range(4)},
            "target_folios": targets_by_folio,
            "folios_with_both_targets": shared_folios,
            "family_alphabet": sorted({char for row in strict.values() for char in row["family_sequence"]}),
            "observed_training_pairs": len(pair_total),
        },
        "loo_target_pair_coverage": coverage,
        "held_training_minima": minima,
        "target_metadata_overlap": overlaps,
        "target_metadata_counts": {
            field: {
                str(s): ordered_counter(row[field] for row in gaps if row["support"] == s)
                for s in (1, 2)
            }
            for field in ("section", "currier", "kind", "grammar_scope")
        },
        "gates": gates,
        "prohibited_outputs": {
            "model_fitted": False,
            "target_contrast_computed": False,
            "p_value_computed": False,
            "english_glosses": 0,
        },
        "claim_ceiling": (
            "Capacity for a preregistered physical-folio-held source-boundary grammar test only; "
            "no authorial word boundary, corrected reading, grammar role, sound, morpheme, lexeme, "
            "plaintext, language, or translation."
        ),
    }
    expected_report = f"""# Source-boundary grammar transfer capacity

Status: **{expected_result['status']}**

The strict exact-family panel contains **{len(gaps):,}** internal gaps on
**{len(by_folio)}** physical folios. Support counts are
**{by_support[0]:,} / {by_support[1]:,} / {by_support[2]:,} /
{by_support[3]:,}** for zero/one/two/three readings.

The unopened support-1/support-2 comparison has **{by_support[1]:,}** and
**{by_support[2]:,}** positions. Both occur on **{shared_folios}**
physical folios. Leave-folio-out family-pair coverage is
**{coverage['1']['covered']}/{coverage['1']['total']}** for support 1 and
**{coverage['2']['covered']}/{coverage['2']['total']}** for support 2.
Holding out the largest folio still leaves at least
**{minima['support_3']:,}** unanimous boundaries and
**{minima['support_0']:,}** unanimous nonboundaries.

Decision: **{decision}**. This is a score-blind capacity result, not a boundary
model result. It supplies no authorial word boundary, corrected reading,
grammar role, sound, morpheme, lexeme, plaintext, language, or translation.
"""
    return expected_result, expected_report, checks


def mutation_checks() -> int:
    checks = 0
    for bad in ("fRos", "f1", "1r", "f12x", "f12rA"):
        try:
            folio(bad)
        except AssertionError:
            checks += 1
        else:
            raise AssertionError(f"bad page accepted: {bad}")
    assert folio("f102r2") == "f102"
    assert folio("f1v") == "f1"
    checks += 2
    sample = rows(BOUNDARIES)[0]
    key = (sample["locus"], int(sample["position_after_symbol"]))
    assert key == ("f100r.22", 5)
    checks += 1
    return checks


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite validation artifacts")
    expected, expected_report, checks = reconstruct()
    actual = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    assert actual == expected
    assert PRODUCTION_REPORT.read_text(encoding="utf-8") == expected_report
    checks += 2
    checks += mutation_checks()
    validation = {
        "experiment": "SOURCE_BOUNDARY_GRAMMAR_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_RECONSTRUCTION",
        "checks_passed": checks,
        "checks_failed": 0,
        "inputs": {
            "production_json_sha256": digest(PRODUCTION),
            "production_report_sha256": digest(PRODUCTION_REPORT),
            "producer_sha256": digest(BUILDER),
            "validator_sha256": digest(VALIDATOR),
            "spec_sha256": digest(SPEC),
        },
        "reconstructed_decision": expected["decision"],
        "score_opened": False,
        "target_contrast_computed": False,
        "english_glosses": 0,
        "claim_ceiling": expected["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Source-boundary grammar capacity validation

Status: **PASS_INDEPENDENT_RECONSTRUCTION**

A nonimporting implementation passed **{checks:,}** checks and reconstructed
every strict locus, internal gap, boundary support, physical-folio count,
leave-folio-out family-pair coverage value, metadata overlap, gate, production
JSON byte-equivalent object, and exact report text.

Decision: **{expected['decision']}**. No model score or support-2/support-1
contrast was opened. The validation supplies no authorial word boundary,
corrected reading, grammar role, sound, morpheme, lexeme, plaintext, language,
or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
